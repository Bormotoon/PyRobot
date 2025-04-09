# FILE START: server.py
import logging
import eventlet

eventlet.monkey_patch()
import redis
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, join_room, emit
import os
from pathlib import Path

# Импортируем интерпретатор и нужные исключения из нового файла
from .kumir_interpreter.interpreter import KumirLanguageInterpreter
from .kumir_interpreter.kumir_exceptions import (KumirExecutionError, KumirEvalError,
                                                 KumirInputRequiredError, RobotError,
                                                 DeclarationError, AssignmentError, InputOutputError)

app = Flask(__name__)

# --- Настройки CORS, Сессии, Логирования, Песочницы ---
allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS', "http://localhost:3000").split(',')
CORS(app, supports_credentials=True, origins=allowed_origins)
logger = logging.getLogger('FlaskServer')
logger.info(f"CORS configured for origins: {allowed_origins}")
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-please-change-this-immediately!')
if app.config['SECRET_KEY'] == 'fallback-secret-key-change-this-immediately!': logger.warning(
	"SECURITY WARNING: Using default FLASK_SECRET_KEY.")
app.config['SESSION_TYPE'] = 'redis';
app.config['SESSION_PERMANENT'] = False;
app.config['SESSION_USE_SIGNER'] = True
redis_host = os.environ.get('REDIS_HOST', 'localhost');
redis_port = int(os.environ.get('REDIS_PORT', 6379));
redis_db = int(os.environ.get('REDIS_DB', 0))
try:
	redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, socket_timeout=5,
	                           socket_connect_timeout=5);
	redis_client.ping();
	app.config['SESSION_REDIS'] = redis_client;
	logger.info(f"Session storage configured for Redis at {redis_host}:{redis_port}, DB: {redis_db}")
except redis.exceptions.ConnectionError as redis_err:
	logger.error(f"CRITICAL: Failed to connect to Redis: {redis_err}");
	app.config['SESSION_TYPE'] = 'filesystem';
	logger.warning("Falling back to 'filesystem' session type.")
except Exception as redis_other_err:
	logger.error(f"CRITICAL: Error configuring Redis: {redis_other_err}");
	app.config['SESSION_TYPE'] = 'filesystem';
	logger.warning("Falling back to 'filesystem' session type.")

app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax');
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
logger.info(f"Session cookie Samesite: {app.config['SESSION_COOKIE_SAMESITE']}");
logger.info(f"Session cookie Secure flag: {app.config['SESSION_COOKIE_SECURE']}")
Session(app)
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, manage_session=False, async_mode='eventlet')
log_level_name = os.environ.get('LOG_LEVEL', 'DEBUG').upper();
log_level = getattr(logging, log_level_name, logging.DEBUG)
if logger.hasHandlers(): logger.handlers.clear()
log_handler = logging.StreamHandler();
log_formatter = logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s');
log_handler.setFormatter(log_formatter);
logger.addHandler(log_handler)
logger.setLevel(log_level)
logging.getLogger('werkzeug').setLevel(logging.WARNING if log_level > logging.INFO else logging.INFO)
logging.getLogger('socketio').setLevel(logging.WARNING if log_level > logging.INFO else logging.INFO)
logging.getLogger('engineio').setLevel(logging.WARNING if log_level > logging.INFO else logging.INFO)
logging.getLogger('redis').setLevel(logging.WARNING)
logger.info(f"Logger level for '{logger.name}' set to: {log_level_name}")
try:
	backend_dir = Path(__file__).parent.absolute(); SANDBOX_DIR = backend_dir / "kumir_sandbox"; SANDBOX_DIR.mkdir(
		parents=True, exist_ok=True); logger.info(f"Ensured sandbox directory exists at: {SANDBOX_DIR}")
except Exception as e:
	logger.exception(f"CRITICAL: Failed to create/ensure sandbox directory at {SANDBOX_DIR}.")


# --- Вспомогательные функции ---
def get_field_state_from_session():
	s = session.get('field_state');
	if not isinstance(s, dict):
		if s is not None: logger.warning(f"Invalid type for field_state in session: {type(s)}. Clearing."); session.pop(
			'field_state', None); session.modified = True
		return None
	width_ok = isinstance(s.get('width'), int) and s['width'] > 0;
	height_ok = isinstance(s.get('height'), int) and s['height'] > 0
	pos_ok = isinstance(s.get('robotPos'), dict) and isinstance(s['robotPos'].get('x'), int) and isinstance(
		s['robotPos'].get('y'), int)
	if width_ok and height_ok and pos_ok:
		logger.debug("Valid field state retrieved from session."); return s
	else:
		logger.warning(f"Invalid field state content in session. Clearing."); session.pop('field_state',
		                                                                                  None); session.modified = True; return None


# --- Эндпоинты Flask ---
@app.route('/updateField', methods=['POST'])
def update_field():
	if not request.is_json: logger.warning("Request to /updateField is not JSON."); return jsonify(
		{'success': False, 'message': 'Invalid content type, expected JSON.'}), 415
	d = request.json;
	if not isinstance(d, dict): return jsonify(
		{'success': False, 'message': 'Invalid data format, expected a JSON object.'}), 400

	errors = {}
	width = d.get('width');
	height = d.get('height');
	robotPos = d.get('robotPos');
	cellSize = d.get('cellSize')

	if not (isinstance(width, int) and width > 0):
		errors['width'] = "Must be a positive integer."
	if not (isinstance(height, int) and height > 0):
		errors['height'] = "Must be a positive integer."
	if not (isinstance(robotPos, dict) and isinstance(robotPos.get('x'), int) and isinstance(robotPos.get('y'), int)):
		# --->>> ИСПРАВЛЕННЫЙ ОТСТУП <<<---
		errors['robotPos'] = "Must be an object with integer 'x' and 'y'."
	if not (isinstance(cellSize, int) and cellSize > 0):
		errors['cellSize'] = "Must be a positive integer."

	# Валидация коллекций (остается без изменений)
	if not isinstance(d.get('walls'), list):
		errors['walls'] = "Must be a list."
	elif not all(isinstance(w, str) for w in d.get('walls', [])):
		errors['walls'] = "All elements must be strings."  # Добавил .get с default
	if not isinstance(d.get('markers'), dict): errors['markers'] = "Must be an object/dict."
	if not isinstance(d.get('coloredCells'), list):
		errors['coloredCells'] = "Must be a list."
	elif not all(isinstance(c, str) for c in d.get('coloredCells', [])):
		errors['coloredCells'] = "All elements must be strings."  # Добавил .get с default
	if not isinstance(d.get('symbols'), dict): errors['symbols'] = "Must be an object/dict."
	if not isinstance(d.get('radiation'), dict): errors['radiation'] = "Must be an object/dict."
	if not isinstance(d.get('temperature'), dict): errors['temperature'] = "Must be an object/dict."

	if errors: logger.warning(f"Invalid data received in /updateField: {errors}. Data: {d}"); return jsonify(
		{'success': False, 'message': 'Invalid field data.', 'errors': errors}), 400

	logger.info("Updating field state in session (data validated).");
	session['field_state'] = d;
	session.modified = True
	return jsonify({'success': True, 'message': 'Field state updated in session.'}), 200


@app.route('/execute', methods=['POST'])
def execute_code():
	# ... (Остальной код execute_code без изменений) ...
	session_id_for_log = session.get('sid', 'None');
	logger.debug(f"Session @ /execute start for SID {session_id_for_log}: {dict(session.items())}");
	logger.info(f"Execute code request received (Session SID: {session_id_for_log})")
	if not request.is_json: logger.warning("Invalid content type for /execute. Expected JSON."); return jsonify(
		{'success': False, 'message': 'Invalid request content type (expected JSON).'}), 415
	data = request.get_json();
	code = data.get('code', '').strip();
	client_state = data.get('fieldState')
	if not code: logger.warning("Empty code received for execution."); return jsonify(
		{'success': False, 'message': 'Код для выполнения пуст.'}), 200
	initial_state = client_state or get_field_state_from_session();
	state_source = 'Request' if client_state else ('Session' if session.get('field_state') else 'Default');
	logger.debug(f"Using initial field state from: {state_source}")
	if not initial_state: logger.info("No initial state provided or found in session, using interpreter defaults.")
	interpreter = None;
	trace_data = []
	try:
		interpreter = KumirLanguageInterpreter(code, initial_field_state=initial_state);
		logger.debug("Kumir interpreter initialized successfully.")

		def progress_callback(progress_data):
			current_sid = session.get('sid');
			if not current_sid:
				if not hasattr(progress_callback, 'warned_no_sid'): logger.warning(
					"Cannot emit progress via WebSocket: No SID found in Flask session."); progress_callback.warned_no_sid = True
				return
			if interpreter:
				if hasattr(interpreter, 'robot'): progress_data['robotPos'] = interpreter.robot.robot_pos.copy()
				progress_data['output'] = interpreter.output
			else:
				progress_data['output'] = ""
			try:
				eventlet.sleep(0); socketio.emit('execution_progress', progress_data, to=current_sid)
			except Exception as emit_err:
				logger.error(f"Error emitting progress to SID {current_sid}: {emit_err}")

		result = interpreter.interpret(progress_callback=progress_callback)
		if result.get('input_required'): logger.info(
			f"Execution requires input for variable '{result.get('var_name')}'. Returning input request."); result[
			'trace'] = result.get('trace', []); return jsonify(result), 200
		trace_data = result.get('trace', []);
		final_state_data = result.get('finalState')
		response_data = {'success': result.get('success', False),
		                 'message': result.get('message', 'OK' if result.get('success') else 'Unknown Error'),
		                 'finalState': final_state_data, 'trace': trace_data}
		if not response_data['success']:
			response_data['errorIndex'] = result.get('errorIndex', -1); logger.warning(
				f"Execution finished with error: {response_data['message']} (Error Index: {response_data.get('errorIndex')})")
		else:
			logger.info("Execution completed successfully.")
			try:
				if interpreter and final_state_data and final_state_data.get('robot') is not None:
					field_state_to_save = {'width': interpreter.width, 'height': interpreter.height,
					                       'robotPos': final_state_data.get('robot'),
					                       'walls': final_state_data.get('walls', []),
					                       'markers': final_state_data.get('markers', {}),
					                       'coloredCells': final_state_data.get('coloredCells', []),
					                       'symbols': final_state_data.get('symbols', {}),
					                       'radiation': final_state_data.get('radiation', {}),
					                       'temperature': final_state_data.get('temperature', {})}
					field_state_to_save = {k: v for k, v in field_state_to_save.items() if v is not None};
					session['field_state'] = field_state_to_save;
					session.modified = True;
					logger.debug("Saved final field state to session after successful execution.")
				else:
					logger.warning("Could not save final state to session: interpreter/finalState/robotPos missing.")
			except Exception as save_err:
				logger.error(f"Error saving final state to session: {save_err}", exc_info=True)
		return jsonify(response_data), 200
	except (KumirExecutionError, KumirEvalError, RobotError, KumirInputRequiredError, DeclarationError, AssignmentError,
	        InputOutputError) as e:
		err_msg = f"Ошибка выполнения: {str(e)}";
		logger.error(err_msg, exc_info=False)
		output_on_error = interpreter.output if interpreter and hasattr(interpreter, 'output') else "";
		state_on_error = {};
		error_index = -1
		try:
			state_on_error = interpreter.get_state() if interpreter and hasattr(interpreter, 'get_state') else {};
			state_on_error["output"] = output_on_error; error_index = getattr(e, 'line_index', -1)
		except Exception as getStateErr:
			logger.error(f"Error getting state after Kumir error: {getStateErr}"); state_on_error = {
				"output": output_on_error}
		return jsonify({'success': False, 'message': err_msg, 'finalState': state_on_error, 'trace': trace_data,
		                'errorIndex': error_index}), 200
	except Exception as e:
		logger.exception("Unexpected server error during code execution.")
		output_on_error = interpreter.output if interpreter and hasattr(interpreter, 'output') else "";
		state_on_error = {}
		try:
			state_on_error = interpreter.get_state() if interpreter and hasattr(interpreter, 'get_state') else {}
		except Exception:
			pass
		state_on_error["output"] = output_on_error
		return jsonify({'success': False, 'message': f'Внутренняя ошибка сервера: {type(e).__name__}',
		                'finalState': state_on_error, 'trace': trace_data}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator_session():
	session_id_for_log = session.get('sid', 'None');
	logger.info(f"Reset field state request received (Session SID: {session_id_for_log}).");
	session.pop('field_state', None);
	session.modified = True;
	logger.info("Field state cleared from session.");
	return jsonify({'success': True, 'message': 'Состояние поля сброшено в сессии.'}), 200


# --- Обработчики SocketIO ---
@socketio.on('connect')
def handle_connect(): logger.info(f"WebSocket client connected: SID={request.sid}"); session[
	'sid'] = request.sid; session.modified = True; join_room(request.sid); emit('connection_ack',
                                                                                {'sid': request.sid}); logger.debug(
	f"SID '{request.sid}' saved to Flask session. Session keys: {list(session.keys())}")


@socketio.on('disconnect')
def handle_disconnect(*args): sid = request.sid; logger.info(f"WebSocket client disconnected: SID={sid}")


@socketio.on_error_default
def default_error_handler(e): logger.error(f"SocketIO error: {e}", exc_info=True)


# --- Запуск сервера ---
if __name__ == '__main__':
	host = os.environ.get('HOST', '0.0.0.0');
	port = int(os.environ.get('PORT', 5000));
	is_development = os.environ.get('FLASK_ENV', '').lower() == 'development';
	debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' or is_development;
	use_reloader = os.environ.get('USE_RELOADER', str(is_development)).lower() == 'true'
	if not debug_mode: logging.getLogger('werkzeug').setLevel(logging.WARNING)
	logger.info(f"Starting Flask-SocketIO server...");
	logger.info(f"  Host: {host}");
	logger.info(f"  Port: {port}");
	logger.info(f"  Debug Mode: {debug_mode}");
	logger.info(f"  Reloader: {use_reloader}");
	logger.info(f"  Log Level: {log_level_name}");
	logger.info(f"  Session Secure Cookie: {app.config['SESSION_COOKIE_SECURE']}");
	logger.info(f"  Allowed CORS Origins: {allowed_origins}")
	try:
		socketio.run(app, host=host, port=port, debug=debug_mode, use_reloader=use_reloader)
	except Exception as run_err:
		logger.exception(f"Failed to start the server: {run_err}"); import sys; sys.exit(1)

# FILE END: server.py