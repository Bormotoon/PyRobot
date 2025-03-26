import logging

# 1. Import eventlet and monkey_patch VERY FIRST
import eventlet

eventlet.monkey_patch()

# 2. Import other libraries AFTER patching
import redis
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, join_room, emit

# 3. Use RELATIVE imports for modules within the backend package
from .kumir_interpreter.interpreter import KumirLanguageInterpreter, KumirExecutionError, KumirEvalError
from .kumir_interpreter.robot_state import RobotError

# --- Flask App Setup ---
app = Flask(__name__)

# CORS Configuration: Allow requests from your frontend origin
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# Session Configuration (using Redis)
# IMPORTANT: Replace 'your-secret-key' with a strong, random secret key!
app.config['SECRET_KEY'] = 'change-this-to-a-real-secret-key-in-production'  # <-- CHANGE THIS!
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False  # Sessions expire when browser closes
app.config['SESSION_USE_SIGNER'] = True  # Encrypt session cookie
# Configure Redis connection (adjust host/port/db if needed)
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
# Cookie Security Settings (adjust for production)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Recommended for most cases
app.config['SESSION_COOKIE_SECURE'] = False  # SET TO TRUE IN PRODUCTION (HTTPS required)
# app.config['SESSION_COOKIE_DOMAIN'] = 'yourdomain.com' # Set in production

# Initialize Flask-Session
Session(app)

# SocketIO Setup (manage_session=False because Flask-Session handles it)
# Ensure async_mode='eventlet' is specified for compatibility with monkey_patch
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", manage_session=False, async_mode='eventlet')

# --- Logging Setup ---
# Use Flask's logger for better integration if desired, or keep basicConfig
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FlaskServer')
if not logger.handlers:  # Avoid adding handlers multiple times if auto-reloading
	handler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# --- Helper Functions ---
def get_field_state_from_session():
	"""Retrieves and validates field state from session."""
	state = session.get('field_state')
	if state and isinstance(state, dict):
		# Basic validation (ensure essential keys exist and have roughly correct types)
		if all(k in state for k in ('width', 'height', 'robotPos')) and \
				isinstance(state['width'], int) and state['width'] > 0 and \
				isinstance(state['height'], int) and state['height'] > 0 and \
				isinstance(state['robotPos'], dict):
			logger.debug("Retrieved valid field state from session.")
			return state
		else:
			logger.warning("Invalid field state found in session, clearing.")
			session.pop('field_state', None)  # Clear invalid state
			session.modified = True  # Mark session as modified
			return None
	return None


# --- Routes ---
@app.route('/updateField', methods=['POST'])
def update_field():
	"""Stores the received field state in the user's session."""
	data = request.json
	# Basic validation of incoming data
	if not data or not isinstance(data, dict) or 'width' not in data or 'height' not in data:
		logger.warning("Received invalid field update request.")
		return jsonify({'success': False, 'message': 'Неверные данные поля.'}), 400

	logger.info("Received field state update from client.")
	logger.debug(f"Field state received: {data}")
	# Store the validated data in the session
	session['field_state'] = data
	# Ensure session is saved
	session.modified = True
	return jsonify({'success': True, 'message': 'Состояние поля обновлено на сервере.'}), 200


@app.route('/execute', methods=['POST'])
def execute_code():
	"""Executes the provided Kumir code using the interpreter."""
	# === Add logging for session contents at the START of the request ===
	logger.debug(f"Session contents at start of /execute: {dict(session.items())}")
	# =====================================================================
	sid = session.get('sid')  # Get client's SocketIO SID for progress updates
	logger.info(f"Execution request received (SID found in session: {sid})")  # Log if SID was found

	if not request.is_json:
		logger.error("Invalid request: Content-Type must be application/json")
		return jsonify({'success': False, 'message': 'Invalid request format.'}), 415

	data = request.get_json()
	code = data.get('code', '').strip()
	client_field_state = data.get('fieldState')  # Get field state sent with this request

	if not code:
		logger.warning("Execution request with empty code.")
		return jsonify({'success': False, 'message': 'Код программы пуст.'}), 200  # OK status, logical error

	# Determine initial state: use state sent with request, fallback to session, then default
	initial_state = client_field_state or get_field_state_from_session()
	logger.debug(
		f"Using initial field state: {'Provided in request' if client_field_state else ('From session' if session.get('field_state') else 'Interpreter default')}")

	# --- Interpreter Execution ---
	interpreter = None  # Initialize for potential use in except block
	trace_data = []  # Initialize trace data
	try:
		# Initialize the interpreter with the code and initial field state
		interpreter = KumirLanguageInterpreter(code, initial_field_state=initial_state)
		logger.debug("Kumir interpreter initialized.")

		# Callback for sending progress updates via WebSocket
		def progress_callback(progress_data):
			if sid:
				# Use socketio.sleep(0) to yield control briefly, allowing other greenlets (like emit) to run
				# This prevents the interpreter loop from potentially blocking the emit call for too long.
				socketio.sleep(0)
				logger.debug(f"Emitting execution_progress to SID {sid}: {progress_data}")
				# Explicitly emit to the specific room/SID
				socketio.emit('execution_progress', progress_data, room=sid)
			else:
				# Log only once if SID missing during execution?
				if not hasattr(progress_callback, 'sid_warning_logged'):
					logger.warning("Cannot send progress during execution, client SID not found in session.")
					progress_callback.sid_warning_logged = True  # Avoid flooding logs

		# Execute the code and get the result (includes trace, final state, status)
		result = interpreter.interpret(progress_callback=progress_callback)
		trace_data = result.get('trace', [])  # Store trace locally for the response

		# --- Prepare Response ---
		response_data = {
			'success': result['success'],
			'message': result.get('message', 'Выполнение завершено.' if result['success'] else 'Произошла ошибка.'),
			'output': result['finalState'].get('output', ''),
			'robot': result['finalState'].get('robot'),
			'coloredCells': result['finalState'].get('coloredCells', []),
			'env': result['finalState'].get('env', {}),
			'trace': trace_data  # Send trace back in HTTP response as well
		}

		if not result['success']:
			response_data['errorIndex'] = result.get('errorIndex')
			logger.warning(f"Execution failed: {result.get('message')}")
		else:
			logger.info("Execution successful.")

			# Store the final field state back into the session for future requests
			# Access attributes directly from the interpreter's robot object
			final_field_state = {
				'width': interpreter.width,
				'height': interpreter.height,
				'robotPos': result['finalState'].get('robot'),  # Already retrieved correctly
				'walls': list(interpreter.robot.walls),  # Use .walls attribute
				'markers': interpreter.robot.markers,  # Use .markers attribute
				'coloredCells': result['finalState'].get('coloredCells', [])  # Already retrieved correctly
			}
			session['field_state'] = final_field_state
			session.modified = True
			logger.debug("Stored final field state in session.")

		# Return JSON response (HTTP 200 OK even for logical failures)
		return jsonify(response_data), 200

	except (KumirExecutionError, KumirEvalError, RobotError) as e:
		# Handle specific errors from the interpreter/robot
		error_msg = f"Ошибка выполнения: {str(e)}"
		logger.error(error_msg, exc_info=False)  # Log error without full traceback unless needed
		output_buffer = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
		return jsonify({
			'success': False,
			'message': error_msg,
			'output': output_buffer,
			'trace': trace_data  # Send trace up to the point of error
		}), 200

	except Exception as e:
		# Handle unexpected errors during initialization or execution
		logger.exception("Неожиданная ошибка сервера при выполнении кода.")  # Log with traceback
		output_buffer = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
		return jsonify({
			'success': False,
			'message': f'Внутренняя ошибка сервера: {str(e)}',
			'output': output_buffer,
			'trace': trace_data  # Send trace up to the point of error
		}), 500  # Internal Server Error


@app.route('/reset', methods=['POST'])
def reset_simulator_session():
	"""Clears the simulator-related state from the user's session."""
	sid = session.get('sid')
	logger.info(f"Reset request received (SID: {sid}). Clearing session field state.")
	session.pop('field_state', None)
	session.modified = True
	# Optionally reset other session data related to the simulator
	return jsonify({'success': True, 'message': 'Состояние симулятора на сервере сброшено.'}), 200


# --- SocketIO Event Handlers ---
@socketio.on('connect')
def handle_connect():
	"""Handles new client WebSocket connections."""
	logger.info(f"Client connected: SID={request.sid}")
	# Store the SID in the session to associate HTTP requests with WebSocket connection
	session['sid'] = request.sid
	# Explicitly mark session as modified to ensure it's saved
	session.modified = True
	join_room(request.sid)  # Client joins a room identified by their SID
	# It's good practice to acknowledge connection or send initial state if needed
	emit('connection_ack', {'message': f'Connected to server, your SID is {request.sid}', 'sid': request.sid})
	logger.debug(f"SID {request.sid} saved in session and joined room.")
	# Log session contents *after* modification attempt for debugging
	logger.debug(f"Session contents after connect: {dict(session.items())}")


@socketio.on('disconnect')
def handle_disconnect(*args):  # <-- Accept *args to handle potential arguments
	"""Handles client WebSocket disconnections."""
	# Session should still be available here briefly
	sid = session.get('sid', request.sid)  # Get SID from session or fallback to request context
	logger.info(f"Client disconnected: SID={sid}")


# Optional: Clean up specific session keys if needed, though Flask-Session handles expiry.
# session.pop('sid', None) # Example if you want immediate cleanup


@socketio.on_error_default  # Catchall for SocketIO errors
def default_error_handler(e):
	logger.error(f"SocketIO error occurred: {e}")


# Consider emitting an error message back to the client if appropriate


# --- Main Execution Block ---
# Use this block to run the server directly with python -m pyrobot.backend.server
if __name__ == '__main__':
	logger.info("Starting Flask-SocketIO server with Eventlet...")
	# Use socketio.run, which integrates with Eventlet correctly
	# debug=True enables auto-reloading and Werkzeug debugger (DISABLE in production)
	# host='0.0.0.0' makes server accessible on your network (use '127.0.0.1' or None for local only)
	# port=5000 specified port
	socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=True)
# use_reloader=True is often the default with debug=True, but can be explicit
