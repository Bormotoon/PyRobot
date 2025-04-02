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
# --->>> ДОБАВЛЯЕМ ИМПОРТЫ ДЛЯ ПЕСОЧНИЦЫ <<<---
import os
from pathlib import Path

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# --- Конфигурация сессии ---
# ВАЖНО: Установите настоящий секретный ключ!
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your-default-secret-key-please-change')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
# TODO: Настройте параметры Redis из переменных окружения
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Установите True для HTTPS в production
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

Session(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", manage_session=False, async_mode='eventlet')

# --- Настройка логирования ---
logger = logging.getLogger('FlaskServer')
if not logger.handlers:
	handler = logging.StreamHandler()
	# Улучшенный форматтер
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
# Уровень логирования можно настроить через переменную окружения
log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logger.setLevel(getattr(logging, log_level, logging.DEBUG))

# --->>> СОЗДАНИЕ КАТАЛОГА ПЕСОЧНИЦЫ <<<---
try:
	# Путь должен совпадать с тем, что в file_functions.py
	backend_dir = Path(__file__).parent.absolute()
	SANDBOX_DIR = backend_dir / "kumir_sandbox"
	SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
	logger.info(f"Ensured sandbox directory exists at: {SANDBOX_DIR}")
except Exception as e:
	logger.exception(f"CRITICAL: Failed to create/ensure sandbox directory at {SANDBOX_DIR}: {e}")
	# Возможно, стоит остановить сервер, если песочница не создана
	# raise RuntimeError("Sandbox directory creation failed.")


# --- Остальной код сервера (без изменений) ---

# Функция get_field_state_from_session остается без изменений
def get_field_state_from_session():
	# ... (код без изменений) ...
	s = session.get('field_state');
	if s and isinstance(s, dict):
		if all(k in s for k in ('width', 'height', 'robotPos')) and isinstance(s['width'], int) and s[
			'width'] > 0 and isinstance(s['height'], int) and s['height'] > 0 and isinstance(s['robotPos'], dict):
			logger.debug("Session state OK.");
			return s;
		else:
			logger.warning("Invalid session state.");
			session.pop('field_state', None);
			session.modified = True;
			return None


# Ручка /updateField остается без изменений
@app.route('/updateField', methods=['POST'])
def update_field():
	# ... (код без изменений) ...
	d = request.json
	if not d or not isinstance(d, dict) or 'width' not in d or 'height' not in d:
		return jsonify({'success': False, 'message': 'Invalid data.'}), 400
	logger.info("Update field.")
	# Логируем только ключи и типы для краткости
	logged_state = {k: type(v).__name__ for k, v in d.items()}
	logger.debug(f"State update request: {logged_state}")
	session['field_state'] = d
	session.modified = True
	return jsonify({'success': True, 'message': 'State updated.'}), 200


# Ручка /execute остается без изменений
@app.route('/execute', methods=['POST'])
def execute_code():
	# ... (код без изменений) ...
	logger.debug(f"Session @ /execute start: {dict(session.items())}");
	sid = session.get('sid');
	logger.info(f"Execute req (SID: {sid or 'None'})")  # Добавил None
	if not request.is_json: return jsonify(
		{'success': False, 'message': 'Invalid request content type (expected JSON).'}), 415
	data = request.get_json();
	code = data.get('code', '').strip();
	client_state = data.get('fieldState')
	if not code: return jsonify({'success': False, 'message': 'Код пуст.'}), 200

	initial_state = client_state or get_field_state_from_session()
	logger.debug(
		f"Initial state source: {'Request' if client_state else ('Session' if session.get('field_state') else 'Default')}")

	interpreter = None;
	trace_data = []  # Всегда инициализируем trace_data
	try:
		interpreter = KumirLanguageInterpreter(code, initial_field_state=initial_state)
		logger.debug("Interpreter initialized successfully.")

		def progress_callback(progress_data):
			# Добавляем актуальную позицию робота в данные для callback
			if interpreter and hasattr(interpreter, 'robot'):
				progress_data['robotPos'] = interpreter.robot.robot_pos.copy()
			# Добавляем текущий вывод
			progress_data['output'] = interpreter.output if interpreter else ""

			if sid:
				# Используем eventlet.sleep для неблокирующей паузы в асинхронном контексте
				eventlet.sleep(0)  # Даем другим гринлетам шанс выполниться
				logger.debug(f"Emitting execution_progress to SID {sid}: {progress_data}")
				socketio.emit('execution_progress', progress_data, room=sid)
			else:
				# Логируем предупреждение только один раз
				if not hasattr(progress_callback, 'warned_no_sid'):
					logger.warning("Cannot emit progress: No SID found in session.")
					progress_callback.warned_no_sid = True

		# Запускаем интерпретацию с коллбэком
		result = interpreter.interpret(progress_callback=progress_callback)
		trace_data = result.get('trace', [])  # Получаем трассировку из результата

		# Подготовка ответа сервера
		response_data = {
			'success': result.get('success', False),  # Явно указываем False по умолчанию
			'message': result.get('message', 'OK' if result.get('success') else 'Unknown Error'),
			# Данные из финального состояния интерпретатора
			'output': result.get('finalState', {}).get('output', ''),
			'robot': result.get('finalState', {}).get('robot'),
			'coloredCells': result.get('finalState', {}).get('coloredCells', []),
			'env': result.get('finalState', {}).get('env', {}),
			'symbols': result.get('finalState', {}).get('symbols', {}),
			'radiation': result.get('finalState', {}).get('radiation', {}),
			'temperature': result.get('finalState', {}).get('temperature', {}),
			# Полная трассировка выполнения
			'trace': trace_data
		}

		if not response_data['success']:
			# Если выполнение не успешно, добавляем индекс ошибки, если он есть
			response_data['errorIndex'] = result.get('errorIndex')
			logger.warning(f"Execution failed: {response_data['message']} (Index: {response_data.get('errorIndex')})")
		else:
			logger.info("Execution completed successfully.")
			# Сохраняем финальное состояние поля в сессию при успехе
			try:
				# Убедимся, что interpreter существует и имеет нужные атрибуты
				if interpreter and hasattr(interpreter, 'robot'):
					final_state_to_save = {
						'width': interpreter.width,
						'height': interpreter.height,
						'robotPos': response_data['robot'],
						'walls': list(interpreter.robot.walls),
						'markers': interpreter.robot.markers.copy(),
						'coloredCells': response_data['coloredCells'],  # Уже список
						'symbols': response_data['symbols'],
						'radiation': response_data['radiation'],
						'temperature': response_data['temperature']
					}
					session['field_state'] = final_state_to_save
					session.modified = True
					logger.debug("Saved final field state to session.")
				else:
					logger.warning("Could not save final state to session: interpreter object missing or invalid.")
			except Exception as save_err:
				logger.error(f"Error saving final state to session: {save_err}", exc_info=True)

		# Отправляем ответ клиенту
		return jsonify(response_data), 200

	except (KumirExecutionError, KumirEvalError, RobotError) as e:
		# Обработка известных ошибок интерпретации/робота
		err_msg = f"Ошибка выполнения Кумир: {str(e)}"
		logger.error(err_msg, exc_info=False)  # Не логируем полный traceback для ожидаемых ошибок
		# Формируем состояние на момент ошибки
		output_on_error = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
		state_on_error = interpreter.get_state() if interpreter and hasattr(interpreter, 'get_state') else {}
		state_on_error["output"] = output_on_error
		# Добавляем радиацию/температуру, если возможно
		if interpreter and hasattr(interpreter, 'robot'):
			state_on_error['radiation'] = interpreter.robot.radiation.copy()
			state_on_error['temperature'] = interpreter.robot.temperature.copy()
		else:
			state_on_error['radiation'] = {}
			state_on_error['temperature'] = {}

		return jsonify({'success': False, 'message': err_msg, **state_on_error,
						'trace': trace_data}), 200  # Возвращаем 200 OK, т.к. это ошибка Кумир кода, а не сервера

	except Exception as e:
		# Обработка непредвиденных серверных ошибок
		logger.exception("Unexpected server error during code execution.")  # Логируем с полным traceback
		output_on_error = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
		# Пытаемся получить состояние, но может не сработать
		try:
			state_on_error = interpreter.get_state() if interpreter and hasattr(interpreter, 'get_state') else {}
		except Exception as getStateErr:
			logger.error(f"Could not get interpreter state after server error: {getStateErr}")
			state_on_error = {}
		state_on_error["output"] = output_on_error
		# Добавляем радиацию/температуру, если возможно
		if interpreter and hasattr(interpreter, 'robot'):
			state_on_error['radiation'] = interpreter.robot.radiation.copy()
			state_on_error['temperature'] = interpreter.robot.temperature.copy()
		else:
			state_on_error['radiation'] = {}
			state_on_error['temperature'] = {}

		# Возвращаем 500 Internal Server Error
		return jsonify(
			{'success': False, 'message': f'Внутренняя ошибка сервера: {str(e)}', **state_on_error, 'trace': trace_data}
		), 500


# Ручка /reset остается без изменений
@app.route('/reset', methods=['POST'])
def reset_simulator_session():
	# ... (код без изменений) ...
	sid = session.get('sid');
	logger.info(f"Reset req (SID:{sid}).");
	session.pop('field_state', None);
	session.modified = True;
	return jsonify({'success': True, 'message': 'Сброшено.'}), 200


# Обработчики SocketIO остаются без изменений
@socketio.on('connect')
def handle_connect():
	# ... (код без изменений) ...
	logger.info(f"Connect:SID={request.sid}");
	session['sid'] = request.sid;  # Сохраняем SID в сессию Flask
	session.modified = True;
	join_room(request.sid);  # Присоединяем клиента к комнате с его SID
	emit('connection_ack', {'sid': request.sid});  # Отправляем подтверждение клиенту
	logger.debug(f"SID saved. Session contents: {dict(session.items())}")


@socketio.on('disconnect')
def handle_disconnect(*args):
	# ... (код без изменений) ...
	# Получаем SID либо из сессии (если она еще жива), либо из request.sid
	sid = session.get('sid', request.sid)
	logger.info(f"Disconnect: SID={sid}")
	# Сессию здесь чистить не обязательно, она может быть использована для HTTP запросов


@socketio.on_error_default
def default_error_handler(e):
	# ... (код без изменений) ...
	logger.error(f"SocketIO error: {e}", exc_info=True)  # Логируем с traceback


# Запуск сервера
if __name__ == '__main__':
	logger.info("Starting Flask-SocketIO Server...")
	# Используем eventlet в качестве сервера
	socketio.run(app,
				 debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
				 host='0.0.0.0',
				 port=int(os.environ.get('PORT', 5000)),
				 use_reloader=True  # Автоперезагрузка при изменении кода (удобно для разработки)
				 )

# FILE END: server.py
