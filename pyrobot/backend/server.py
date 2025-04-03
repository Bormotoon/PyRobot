# FILE START: server.py
import logging
import eventlet

eventlet.monkey_patch()  # Должно быть как можно раньше
import redis
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, join_room, emit
import os
from pathlib import Path

# Импорты вашего интерпретатора
from .kumir_interpreter.interpreter import KumirLanguageInterpreter, KumirExecutionError, KumirEvalError
from .kumir_interpreter.declarations import KumirInputRequiredError
from .kumir_interpreter.robot_state import RobotError

app = Flask(__name__)

# --- Настройка CORS ---
# В production замените "*" или "http://localhost:3000" на ваш реальный фронтенд-домен
allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS', "http://localhost:3000").split(',')
CORS(app, supports_credentials=True, origins=allowed_origins)
logger = logging.getLogger('FlaskServer')  # Логгер инициализируем до использования
logger.info(f"CORS configured for origins: {allowed_origins}")

# --- Конфигурация сессии через переменные окружения ---
# ВАЖНО: Установите надежный секретный ключ в переменной окружения FLASK_SECRET_KEY
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-change-this-immediately!')
if app.config['SECRET_KEY'] == 'fallback-secret-key-change-this-immediately!':
    logger.warning(
        "SECURITY WARNING: Using default FLASK_SECRET_KEY. Set a strong secret key in environment variables!")

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # Подписывать cookie сессии

# Параметры Redis
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_db = int(os.environ.get('REDIS_DB', 0))
app.config['SESSION_REDIS'] = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
logger.info(f"Session storage configured for Redis at {redis_host}:{redis_port}, DB: {redis_db}")

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 'Lax' или 'None' (требует Secure=True)
# Установите SESSION_COOKIE_SECURE=True для HTTPS в production
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
logger.info(
    f"Session cookie secure flag: {app.config['SESSION_COOKIE_SECURE']} (Set SESSION_COOKIE_SECURE=True for HTTPS)")

Session(app)
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, manage_session=False, async_mode='eventlet')

# --- Настройка логирования ---
log_level_name = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
log_level = getattr(logging, log_level_name, logging.DEBUG)

# Удаляем существующие обработчики, если они есть (чтобы избежать дублирования при перезагрузке)
# for handler in logger.handlers[:]: logger.removeHandler(handler) # Это может вызвать проблемы, если другие модули настроили логгеры

if not logger.handlers:  # Добавляем обработчик, только если его нет
    log_handler = logging.StreamHandler()
    # Более информативный форматтер
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'
    )
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)

logger.setLevel(log_level)
# Логируем и другие важные библиотеки (по желанию)
logging.getLogger('werkzeug').setLevel(logging.INFO)  # Логи запросов Flask
logging.getLogger('socketio').setLevel(logging.INFO)
logging.getLogger('engineio').setLevel(logging.INFO)
logging.getLogger('redis').setLevel(logging.INFO)

logger.info(f"Logger level set to: {log_level_name}")

# --- Создание каталога песочницы ---
try:
    backend_dir = Path(__file__).parent.absolute()
    SANDBOX_DIR = backend_dir / "kumir_sandbox"
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured sandbox directory exists at: {SANDBOX_DIR}")
except Exception as e:
    logger.exception(
        f"CRITICAL: Failed to create/ensure sandbox directory at {SANDBOX_DIR}. File operations might fail.")
# В production можно прервать запуск: raise RuntimeError("Sandbox directory creation failed.")


# --- Вспомогательные функции ---
def get_field_state_from_session():
    """Получает состояние поля из сессии, если оно валидно."""
    s = session.get('field_state')
    if not isinstance(s, dict):
        if s is not None:
            logger.warning(f"Invalid type for field_state in session: {type(s)}. Clearing.")
            session.pop('field_state', None)
            session.modified = True
        return None

    # Проверка наличия и базовых типов ключей
    width_ok = isinstance(s.get('width'), int) and s['width'] > 0
    height_ok = isinstance(s.get('height'), int) and s['height'] > 0
    pos_ok = isinstance(s.get('robotPos'), dict) and isinstance(s['robotPos'].get('x'), int) and isinstance(
        s['robotPos'].get('y'), int)

    if width_ok and height_ok and pos_ok:
        logger.debug("Valid field state retrieved from session.")
        # Дополнительно: нормализуем типы коллекций (стены, клетки) в set для консистентности
        s['walls'] = set(s.get('walls', []))
        s['coloredCells'] = set(s.get('coloredCells', []))
        return s
    else:
        logger.warning(
            f"Invalid field state content found in session. Clearing. Details: width_ok={width_ok}, height_ok={height_ok}, pos_ok={pos_ok}. State: {s}")
        session.pop('field_state', None)
        session.modified = True
        return None


# --- Ручки Flask ---
@app.route('/updateField', methods=['POST'])
def update_field():
    """Обновляет состояние поля, сохраненное в сессии."""
    if not request.is_json:
        logger.warning("Request to /updateField is not JSON.")
        return jsonify({'success': False, 'message': 'Invalid content type, expected JSON.'}), 415

    d = request.json
    # Более строгая валидация данных
    if not isinstance(d, dict):
        return jsonify({'success': False, 'message': 'Invalid data format, expected a JSON object.'}), 400
    width = d.get('width')
    height = d.get('height')
    robotPos = d.get('robotPos')
    if not (isinstance(width, int) and width > 0 and
            isinstance(height, int) and height > 0 and
            isinstance(robotPos, dict) and isinstance(robotPos.get('x'), int) and isinstance(robotPos.get('y'), int)):
        logger.warning(f"Invalid or incomplete data received in /updateField: {d}")
        return jsonify(
            {'success': False, 'message': 'Invalid or incomplete field data (width, height, robotPos).'}), 400

    # TODO: Добавить валидацию типов для walls, markers, coloredCells, symbols и т.д.

    logger.info("Updating field state in session.")
    # Логируем только ключи и типы для краткости
    logged_state = {k: type(v).__name__ for k, v in d.items()}
    logger.debug(f"State update request keys/types: {logged_state}")

    session['field_state'] = d
    session.modified = True
    return jsonify({'success': True, 'message': 'Field state updated in session.'}), 200


@app.route('/execute', methods=['POST'])
def execute_code():
    """Выполняет код Кумира и возвращает результат или запрос на ввод."""
    session_id_for_log = session.get('sid', 'None')
    logger.debug(f"Session @ /execute start for SID {session_id_for_log}: {dict(session.items())}")
    logger.info(f"Execute code request received (Session SID: {session_id_for_log})")

    if not request.is_json:
        logger.warning("Invalid content type for /execute. Expected JSON.")
        return jsonify({'success': False, 'message': 'Invalid request content type (expected JSON).'}), 415

    data = request.get_json()
    code = data.get('code', '').strip()
    client_state = data.get('fieldState')

    if not code:
        logger.warning("Empty code received for execution.")
        return jsonify({'success': False, 'message': 'Код для выполнения пуст.'}), 200

    initial_state = client_state or get_field_state_from_session()
    state_source = 'Request' if client_state else ('Session' if session.get('field_state') else 'Default')
    logger.debug(f"Using initial field state from: {state_source}")
    if not initial_state:
        logger.info("No initial state provided or found in session, using defaults.")
    # initial_state останется None, интерпретатор использует свои defaults

    interpreter = None
    trace_data = []  # Гарантированно инициализируем

    try:
        interpreter = KumirLanguageInterpreter(code, initial_field_state=initial_state)
        logger.debug("Kumir interpreter initialized successfully.")

        def progress_callback(progress_data):
            current_sid = session.get('sid')  # Берем SID из сессии Flask
            if not current_sid:
                if not hasattr(progress_callback, 'warned_no_sid'):
                    logger.warning("Cannot emit progress via WebSocket: No SID found in Flask session.")
                    progress_callback.warned_no_sid = True
                return

            # Добавляем данные в колбэк
            if interpreter:
                if hasattr(interpreter, 'robot'): progress_data['robotPos'] = interpreter.robot.robot_pos.copy()
                progress_data['output'] = interpreter.output
            else:  # Случай, если interpreter еще не создан или уже None
                progress_data['output'] = ""

            try:
                eventlet.sleep(0)  # Неблокирующая пауза
                # logger.debug(f"Emitting execution_progress to SID {current_sid}: Keys={list(progress_data.keys())}")
                socketio.emit('execution_progress', progress_data, to=current_sid)
            except Exception as emit_err:
                logger.error(f"Error emitting progress to SID {current_sid}: {emit_err}")

        # Запускаем интерпретацию
        result = interpreter.interpret(progress_callback=progress_callback)

        # Проверка на запрос ввода
        if result.get('input_required'):
            logger.info(f"Execution requires input for variable '{result.get('var_name')}'. Returning input request.")
            result['trace'] = result.get('trace', [])  # Убедимся, что trace есть
            return jsonify(result), 200

        # Обработка обычного результата (успех или ошибка)
        trace_data = result.get('trace', [])
        final_state_data = result.get('finalState')  # Получаем финальное состояние

        # Формируем ответ
        response_data = {
            'success': result.get('success', False),
            'message': result.get('message', 'OK' if result.get('success') else 'Unknown Error'),
            'finalState': final_state_data,  # Включаем полное состояние
            'trace': trace_data
        }

        if not response_data['success']:
            response_data['errorIndex'] = result.get('errorIndex', -1)  # Индекс строки ошибки
            logger.warning(
                f"Execution finished with error: {response_data['message']} (Error Index: {response_data.get('errorIndex')})")
        else:
            logger.info("Execution completed successfully.")
            # Сохраняем состояние поля в сессию
            try:
                if interpreter and final_state_data:
                    # Сохраняем только relevant field state
                    field_state_to_save = {
                        'width': interpreter.width, 'height': interpreter.height,
                        'robotPos': final_state_data.get('robot'),
                        'walls': final_state_data.get('walls', []),  # Должны быть list
                        'markers': final_state_data.get('markers', {}),
                        'coloredCells': final_state_data.get('coloredCells', []),  # Должны быть list
                        'symbols': final_state_data.get('symbols', {}),
                        'radiation': final_state_data.get('radiation', {}),
                        'temperature': final_state_data.get('temperature', {})
                    }
                    # Удаляем None значения перед сохранением
                    field_state_to_save = {k: v for k, v in field_state_to_save.items() if v is not None}
                    if field_state_to_save.get('robotPos') is None:  # Робот обязателен
                        logger.error("Cannot save session state: robotPos is missing in final state.")
                    else:
                        session['field_state'] = field_state_to_save
                        session.modified = True
                        logger.debug("Saved final field state to session after successful execution.")
                else:
                    logger.warning(
                        "Could not save final state to session: interpreter or finalState missing in result.")
            except Exception as save_err:
                logger.error(f"Error saving final state to session: {save_err}", exc_info=True)

        return jsonify(response_data), 200

    # Обработка ожидаемых ошибок Кумира
    except (KumirExecutionError, KumirEvalError, RobotError, KumirInputRequiredError) as e:
        # KumirInputRequiredError здесь ловиться не должен (обрабатывается выше), но на всякий случай
        err_msg = f"Ошибка выполнения Кумир: {str(e)}"
        logger.error(err_msg, exc_info=False)
        output_on_error = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
        state_on_error = {}
        try:
            state_on_error = interpreter.get_state() if interpreter and hasattr(interpreter, 'get_state') else {}
            state_on_error["output"] = output_on_error
        except Exception as getStateErr:
            logger.error(f"Error getting state after Kumir error: {getStateErr}")
            state_on_error = {"output": output_on_error}

        # Добавляем индекс ошибки, если он есть в исключении
        error_index = getattr(e, 'line_index', -1) if isinstance(e, KumirExecutionError) else -1

        return jsonify({
            'success': False, 'message': err_msg,
            'finalState': state_on_error,
            'trace': trace_data,
            'errorIndex': error_index
        }), 200

    # Обработка непредвиденных ошибок сервера
    except Exception as e:
        logger.exception("Unexpected server error during code execution.")
        output_on_error = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
        state_on_error = {}
        try:
            state_on_error = interpreter.get_state() if interpreter and hasattr(interpreter, 'get_state') else {}
            state_on_error["output"] = output_on_error
        except Exception as getStateErr:
            logger.error(f"Could not get interpreter state after server error: {getStateErr}")
            state_on_error = {"output": output_on_error}

        return jsonify({
            'success': False,
            'message': f'Внутренняя ошибка сервера: {type(e).__name__}',  # Не показываем детали ошибки пользователю
            'finalState': state_on_error,
            'trace': trace_data
        }), 500


@app.route('/reset', methods=['POST'])
def reset_simulator_session():
    """Сбрасывает состояние поля в сессии."""
    session_id_for_log = session.get('sid', 'None')
    logger.info(f"Reset field state request received (Session SID: {session_id_for_log}).")
    session.pop('field_state', None)
    session.modified = True
    logger.info("Field state cleared from session.")
    return jsonify({'success': True, 'message': 'Состояние поля сброшено в сессии.'}), 200


# --- Обработчики SocketIO ---
@socketio.on('connect')
def handle_connect():
    """Обрабатывает подключение нового WebSocket клиента."""
    logger.info(f"WebSocket client connected: SID={request.sid}")
    session['sid'] = request.sid
    session.modified = True
    join_room(request.sid)
    emit('connection_ack', {'sid': request.sid})
    logger.debug(f"SID '{request.sid}' saved to Flask session. Session keys: {list(session.keys())}")


@socketio.on('disconnect')
def handle_disconnect(*args):
    """Обрабатывает отключение WebSocket клиента."""
    sid = request.sid  # SID отключающегося клиента
    logger.info(f"WebSocket client disconnected: SID={sid}")


# Можно добавить логику очистки ресурсов, связанных с этим SID, если нужно

@socketio.on_error_default
def default_error_handler(e):
    """Обрабатывает ошибки SocketIO."""
    logger.error(f"SocketIO error: {e}", exc_info=True)


# --- Запуск сервера ---
if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    # Включаем debug и reloader только если FLASK_ENV=development (или явно задано)
    is_development = os.environ.get('FLASK_ENV', 'production').lower() == 'development'
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' or is_development
    use_reloader = os.environ.get('USE_RELOADER', str(is_development)).lower() == 'true'

    # Устанавливаем уровень логгера Werkzeug ниже в production
    if not debug_mode:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    logger.info(f"Starting Flask-SocketIO server...")
    logger.info(f"  Host: {host}")
    logger.info(f"  Port: {port}")
    logger.info(f"  Debug Mode: {debug_mode}")
    logger.info(f"  Reloader: {use_reloader}")
    logger.info(f"  Log Level: {log_level_name}")
    logger.info(f"  Session Secure Cookie: {app.config['SESSION_COOKIE_SECURE']}")
    logger.info(f"  Allowed CORS Origins: {allowed_origins}")

    socketio.run(app,
                 host=host,
                 port=port,
                 debug=debug_mode,
                 use_reloader=use_reloader,
                 # Доп. параметры eventlet, если нужны
                 # log_output=debug_mode # Логировать запросы eventlet в debug режиме
                 )

# FILE END: server.py