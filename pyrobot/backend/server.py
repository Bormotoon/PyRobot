# FILE START: server.py
import logging

import eventlet

eventlet.monkey_patch()
import redis
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, join_room, emit

# Импорты вашего интерпретатора
from .kumir_interpreter.interpreter import KumirLanguageInterpreter, KumirExecutionError, KumirEvalError
from .kumir_interpreter.robot_state import RobotError

import os
from pathlib import Path

app = Flask(__name__)
# Настройте origins для вашего production окружения
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# --- Конфигурация сессии ---
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your-default-secret-key-please-change')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(
	host=os.environ.get('REDIS_HOST', 'localhost'),
	port=int(os.environ.get('REDIS_PORT', 6379)),
	db=int(os.environ.get('REDIS_DB', 0))
)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

Session(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", manage_session=False, async_mode='eventlet')

# --- Настройка логирования ---
logger = logging.getLogger('FlaskServer')
if not logger.handlers:
	handler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logger.setLevel(getattr(logging, log_level, logging.DEBUG))

# --- Создание каталога песочницы ---
try:
	backend_dir = Path(__file__).parent.absolute()
	SANDBOX_DIR = backend_dir / "kumir_sandbox"
	SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
	logger.info(f"Ensured sandbox directory exists at: {SANDBOX_DIR}")
except Exception as e:
	logger.exception(f"CRITICAL: Failed to create/ensure sandbox directory at {SANDBOX_DIR}: {e}")
# В production можно прервать запуск: raise RuntimeError("Sandbox directory creation failed.")


# --- Вспомогательные функции ---
def get_field_state_from_session():
	"""Получает состояние поля из сессии, если оно валидно."""
	s = session.get('field_state')
	if s and isinstance(s, dict):
		# Добавим проверку типов для большей надежности
		width_ok = isinstance(s.get('width'), int) and s['width'] > 0
		height_ok = isinstance(s.get('height'), int) and s['height'] > 0
		pos_ok = isinstance(s.get('robotPos'), dict) and 'x' in s['robotPos'] and 'y' in s['robotPos']

		if width_ok and height_ok and pos_ok:
			logger.debug("Valid field state found in session.")
			return s
		else:
			logger.warning(
				f"Invalid field state found in session: width_ok={width_ok}, height_ok={height_ok}, pos_ok={pos_ok}. State: {s}")
			session.pop('field_state', None)
			session.modified = True
			return None
	elif s is not None:
		logger.warning(f"Invalid type for field_state in session: {type(s)}. Clearing.")
		session.pop('field_state', None)
		session.modified = True
	return None  # Возвращаем None, если состояния нет или оно невалидно


# --- Ручки Flask ---
@app.route('/updateField', methods=['POST'])
def update_field():
	"""Обновляет состояние поля, сохраненное в сессии."""
	if not request.is_json:
		return jsonify({'success': False, 'message': 'Invalid content type, expected JSON.'}), 415
	d = request.json
	# Базовая валидация
	if not isinstance(d, dict) or not isinstance(d.get('width'), int) or not isinstance(d.get('height'), int):
		logger.warning(f"Invalid data received in /updateField: {d}")
		return jsonify({'success': False, 'message': 'Invalid or incomplete field data.'}), 400

	logger.info("Updating field state in session.")
	# Логируем только ключи и типы для краткости
	logged_state = {k: type(v).__name__ for k, v in d.items()}
	logger.debug(f"State update request keys/types: {logged_state}")
	# TODO: Добавить более глубокую валидацию состояния (типы стен, маркеров и т.д.) перед сохранением
	session['field_state'] = d
	session.modified = True
	return jsonify({'success': True, 'message': 'Field state updated in session.'}), 200


@app.route('/execute', methods=['POST'])
def execute_code():
	"""Выполняет код Кумира и возвращает результат или запрос на ввод."""
	session_id_for_log = session.get('sid', 'None')
	logger.debug(f"Session @ /execute start: {dict(session.items())}")
	logger.info(f"Execute code request received (Session SID: {session_id_for_log})")

	if not request.is_json:
		logger.warning("Invalid content type for /execute. Expected JSON.")
		return jsonify({'success': False, 'message': 'Invalid request content type (expected JSON).'}), 415

	data = request.get_json()
	code = data.get('code', '').strip()
	client_state = data.get('fieldState')  # Состояние поля, присланное клиентом

	if not code:
		logger.warning("Empty code received for execution.")
		return jsonify({'success': False,
						'message': 'Код для выполнения пуст.'}), 200  # 200 OK, т.к. это валидный запрос, но делать нечего

	# Определяем начальное состояние: приоритет у состояния от клиента, затем из сессии, затем по умолчанию
	initial_state = client_state or get_field_state_from_session()
	state_source = 'Request' if client_state else ('Session' if session.get('field_state') else 'Default')
	logger.debug(f"Using initial field state from: {state_source}")

	interpreter = None
	trace_data = []  # Инициализируем трассировку как пустой список

	try:
		# Создаем интерпретатор с начальным состоянием
		interpreter = KumirLanguageInterpreter(code, initial_field_state=initial_state)
		logger.debug("Kumir interpreter initialized successfully.")

		# Функция обратного вызова для прогресса выполнения (отправка через WebSocket)
		def progress_callback(progress_data):
			current_sid = session.get('sid')  # Получаем SID из ТЕКУЩЕЙ сессии Flask
			if not current_sid:
				if not hasattr(progress_callback, 'warned_no_sid'):
					logger.warning("Cannot emit progress via WebSocket: No SID found in session.")
					progress_callback.warned_no_sid = True
				return

			# Добавляем актуальную позицию робота и вывод
			if interpreter and hasattr(interpreter, 'robot'):
				progress_data['robotPos'] = interpreter.robot.robot_pos.copy()
			progress_data['output'] = interpreter.output if interpreter else ""

			try:
				# Используем eventlet.sleep для неблокирующей паузы
				eventlet.sleep(0)
				logger.debug(f"Emitting execution_progress to SID {current_sid}: Keys={list(progress_data.keys())}")
				# Используем `to=current_sid` вместо `room=current_sid` для большей ясности
				socketio.emit('execution_progress', progress_data, to=current_sid)
			except Exception as emit_err:
				# Логируем ошибку отправки, но не прерываем выполнение
				logger.error(f"Error emitting progress to SID {current_sid}: {emit_err}")

		# Запускаем интерпретацию кода
		result = interpreter.interpret(progress_callback=progress_callback)

		# Проверяем, требует ли результат ввода от пользователя
		if result.get('input_required'):
			logger.info(f"Execution requires input for variable '{result.get('var_name')}'.")
			# Добавляем трассировку в ответ, если она есть
			result['trace'] = result.get('trace', [])
			# Возвращаем специальный ответ для фронтенда
			return jsonify(result), 200  # 200 OK, ожидание ввода - штатная ситуация

		# Если ввод не требуется, обрабатываем результат (успех или ошибка)
		trace_data = result.get('trace', [])  # Получаем трассировку

		# Формируем основной ответ
		response_data = {
			'success': result.get('success', False),
			'message': result.get('message', 'OK' if result.get('success') else 'Unknown Error'),
			'finalState': result.get('finalState'),  # Включаем полное финальное состояние
			'trace': trace_data
		}
		# Добавляем индекс ошибки, если выполнение не успешно
		if not response_data['success']:
			response_data['errorIndex'] = result.get('errorIndex')
			logger.warning(
				f"Execution finished with error: {response_data['message']} (Index: {response_data.get('errorIndex')})")
		else:
			logger.info("Execution completed successfully.")
			# Сохраняем финальное состояние поля в сессию при успехе
			try:
				if interpreter and response_data.get('finalState'):
					# Сохраняем только данные поля, а не все finalState (где есть env, output)
					final_field_state = {
						'width': interpreter.width, 'height': interpreter.height,
						'robotPos': response_data['finalState'].get('robot'),
						'walls': response_data['finalState'].get('walls', []),  # Уже должны быть list
						'markers': response_data['finalState'].get('markers', {}),
						'coloredCells': response_data['finalState'].get('coloredCells', []),  # Уже должны быть list
						'symbols': response_data['finalState'].get('symbols', {}),
						'radiation': response_data['finalState'].get('radiation', {}),
						'temperature': response_data['finalState'].get('temperature', {})
					}
					session['field_state'] = final_field_state
					session.modified = True
					logger.debug("Saved final field state to session after successful execution.")
				else:
					logger.warning("Could not save final state to session: interpreter or finalState missing.")
			except Exception as save_err:
				logger.error(f"Error saving final state to session: {save_err}", exc_info=True)

		return jsonify(response_data), 200

	# Обработка ожидаемых ошибок интерпретатора
	except (KumirExecutionError, KumirEvalError, RobotError) as e:
		err_msg = f"Ошибка выполнения Кумир: {str(e)}"
		logger.error(err_msg, exc_info=False)  # Логируем без полного traceback
		# Формируем ответ с ошибкой
		output_on_error = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
		state_on_error = {}
		try:
			state_on_error = interpreter.get_state() if interpreter and hasattr(interpreter, 'get_state') else {}
			state_on_error["output"] = output_on_error
			# Явно добавляем отсутствующие ключи, если get_state неполный
			for key in ['radiation', 'temperature', 'robot', 'coloredCells', 'walls', 'markers', 'symbols', 'env']:
				if key not in state_on_error: state_on_error[key] = None  # Или {}/[] в зависимости от типа
		except Exception as getStateErr:
			logger.error(f"Error getting state after Kumir error: {getStateErr}")
			state_on_error = {"output": output_on_error}  # Минимальное состояние

		return jsonify({
			'success': False,
			'message': err_msg,
			'finalState': state_on_error,  # Состояние на момент ошибки
			'trace': trace_data  # Трассировка до ошибки
		}), 200  # 200 OK, т.к. это ошибка кода Кумир

	# Обработка непредвиденных серверных ошибок
	except Exception as e:
		logger.exception("Unexpected server error during code execution.")  # Логируем с полным traceback
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
			'message': f'Внутренняя ошибка сервера: {str(e)}',
			'finalState': state_on_error,
			'trace': trace_data
		}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator_session():
	"""Сбрасывает состояние поля в сессии."""
	session_id_for_log = session.get('sid', 'None')
	logger.info(f"Reset field state request received (Session SID: {session_id_for_log}).")
	session.pop('field_state', None)  # Удаляем состояние поля из сессии
	session.modified = True
	logger.info("Field state cleared from session.")
	return jsonify({'success': True, 'message': 'Состояние поля сброшено в сессии.'}), 200


# --- Обработчики SocketIO ---
@socketio.on('connect')
def handle_connect():
	"""Обрабатывает подключение нового WebSocket клиента."""
	logger.info(f"WebSocket client connected: SID={request.sid}")
	session['sid'] = request.sid  # Сохраняем SID в сессию Flask для использования в HTTP запросах
	session.modified = True
	join_room(request.sid)  # Присоединяем клиента к его персональной комнате
	emit('connection_ack', {'sid': request.sid})  # Отправляем подтверждение с SID клиенту
	logger.debug(f"SID '{request.sid}' saved to session. Session keys: {list(session.keys())}")


@socketio.on('disconnect')
def handle_disconnect(*args):
	"""Обрабатывает отключение WebSocket клиента."""
	# args может содержать причину отключения, но нам важен SID
	sid = request.sid  # SID отключающегося клиента
	logger.info(f"WebSocket client disconnected: SID={sid}")


# Очищать SID из сессии здесь не обязательно, он перезапишется при следующем connect

@socketio.on_error_default
def default_error_handler(e):
	"""Обрабатывает ошибки SocketIO."""
	logger.error(f"SocketIO error: {e}", exc_info=True)


# --- Запуск сервера ---
if __name__ == '__main__':
	host = os.environ.get('HOST', '0.0.0.0')
	port = int(os.environ.get('PORT', 5000))
	debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
	use_reloader = debug_mode  # Включаем перезагрузчик только в debug режиме

	logger.info(f"Starting Flask-SocketIO server on {host}:{port} (Debug: {debug_mode}, Reloader: {use_reloader})...")
	# Используем eventlet в качестве WSGI сервера
	socketio.run(app,
				 host=host,
				 port=port,
				 debug=debug_mode,
				 use_reloader=use_reloader
				 )

# FILE END: server.py
