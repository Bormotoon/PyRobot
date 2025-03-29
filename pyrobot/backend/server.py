import logging
import eventlet

eventlet.monkey_patch()

import redis
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, join_room, emit

# Use RELATIVE imports
from .kumir_interpreter.interpreter import KumirLanguageInterpreter, KumirExecutionError, KumirEvalError
from .kumir_interpreter.robot_state import RobotError

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
app.config['SECRET_KEY'] = 'change-this-to-a-real-secret-key-in-production'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True for HTTPS

Session(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", manage_session=False, async_mode='eventlet')

# --- Logging Setup ---
logger = logging.getLogger('FlaskServer')
if not logger.handlers:
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
        # Check for essential keys + basic type validation
        if all(k in state for k in ('width', 'height', 'robotPos')) and \
                isinstance(state['width'], int) and state['width'] > 0 and \
                isinstance(state['height'], int) and state['height'] > 0 and \
                isinstance(state['robotPos'], dict):
            logger.debug("Retrieved valid field state from session.")
            return state
        else:
            logger.warning("Invalid field state in session, clearing.")
            session.pop('field_state', None);
            session.modified = True;
            return None
    return None


# --- Routes ---
@app.route('/updateField', methods=['POST'])
def update_field():
    """Stores received field state in session."""
    data = request.json
    if not data or not isinstance(data, dict) or 'width' not in data or 'height' not in data:
        logger.warning("Invalid field update request.");
        return jsonify({'success': False, 'message': 'Неверные данные.'}), 400
    logger.info("Received field state update.");
    logger.debug(f"State: {data}")
    session['field_state'] = data;
    session.modified = True
    return jsonify({'success': True, 'message': 'Состояние обновлено.'}), 200


@app.route('/execute', methods=['POST'])
def execute_code():
    """Executes Kumir code."""
    logger.debug(f"Session at /execute start: {dict(session.items())}")  # Log session at start
    sid = session.get('sid')
    logger.info(f"Execute request (SID in session: {sid})")

    if not request.is_json: logger.error("Request must be JSON"); return jsonify(
        {'success': False, 'message': 'Invalid request.'}), 415
    data = request.get_json();
    code = data.get('code', '').strip();
    client_field_state = data.get('fieldState')
    if not code: logger.warning("Empty code execution."); return jsonify(
        {'success': False, 'message': 'Код пуст.'}), 200

    initial_state = client_field_state or get_field_state_from_session()
    logger.debug(
        f"Using initial state: {'Request' if client_field_state else ('Session' if session.get('field_state') else 'Default')}")

    interpreter = None;
    trace_data = []
    try:
        interpreter = KumirLanguageInterpreter(code, initial_field_state=initial_state)
        logger.debug("Interpreter initialized.")

        # --- FIX: Ensure robot obj is passed to progress_callback context ---
        def progress_callback(progress_data):
            # Add robot position from the interpreter's robot to the progress data
            # Check if interpreter exists and has robot attribute first
            if interpreter and hasattr(interpreter, 'robot'):
                current_robot_pos = interpreter.robot.robot_pos.copy()  # Get current position
                progress_data['robotPos'] = current_robot_pos
            # ----------------------------------------------------------------

            if sid:
                socketio.sleep(0)
                logger.debug(f"Emit progress to {sid}: {progress_data}")
                socketio.emit('execution_progress', progress_data, room=sid)
            else:
                if not hasattr(progress_callback, 'warned'): logger.warning(
                    "Cannot send progress, no SID."); progress_callback.warned = True

        result = interpreter.interpret(progress_callback=progress_callback)
        trace_data = result.get('trace', [])

        # Prepare response data (including final symbols state)
        response_data = {
            'success': result['success'],
            'message': result.get('message', 'OK' if result['success'] else 'Error'),
            'output': result['finalState'].get('output', ''),
            'robot': result['finalState'].get('robot'),
            'coloredCells': result['finalState'].get('coloredCells', []),
            'env': result['finalState'].get('env', {}),
            'symbols': result['finalState'].get('symbols', {}),  # Use state from get_state()
            'trace': trace_data
        }

        if not result['success']:
            response_data['errorIndex'] = result.get('errorIndex')
            logger.warning(f"Execution failed: {result.get('message')}")
        else:
            logger.info("Execution successful.")
            # Store final state back to session ONLY on success
            final_field_state = {
                'width': interpreter.width, 'height': interpreter.height,
                'robotPos': response_data['robot'],
                'walls': list(interpreter.robot.walls),  # Get current walls
                'markers': interpreter.robot.markers.copy(),
                'coloredCells': response_data['coloredCells'],
                'symbols': response_data['symbols']  # Save final symbols
            }
            session['field_state'] = final_field_state;
            session.modified = True
            logger.debug("Stored final field state in session.")

        return jsonify(response_data), 200

    except (KumirExecutionError, KumirEvalError, RobotError) as e:
        error_msg = f"Ошибка: {str(e)}";
        logger.error(error_msg, exc_info=False)
        output = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
        final_state_on_error = interpreter.get_state() if interpreter else {}  # Try get state on error
        final_state_on_error["output"] = output
        return jsonify({'success': False, 'message': error_msg, **final_state_on_error, 'trace': trace_data}), 200
    except Exception as e:
        logger.exception("Неожиданная ошибка сервера.");
        output = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
        final_state_on_error = interpreter.get_state() if interpreter else {}
        final_state_on_error["output"] = output
        return jsonify({'success': False, 'message': f'Ошибка сервера: {str(e)}', **final_state_on_error,
                        'trace': trace_data}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator_session():
    """Clears simulator state from session."""
    sid = session.get('sid');
    logger.info(f"Reset request (SID: {sid}). Clearing session state.")
    session.pop('field_state', None);
    session.modified = True
    return jsonify({'success': True, 'message': 'Состояние сброшено.'}), 200


# --- SocketIO Event Handlers ---
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: SID={request.sid}")
    session['sid'] = request.sid;
    session.modified = True;
    join_room(request.sid)
    emit('connection_ack', {'message': f'Connected, SID: {request.sid}', 'sid': request.sid})
    logger.debug(f"SID {request.sid} saved, joined room. Session: {dict(session.items())}")


@socketio.on('disconnect')
def handle_disconnect(*args): sid = session.get('sid', request.sid); logger.info(f"Client disconnected: SID={sid}")


@socketio.on_error_default
def default_error_handler(e): logger.error(f"SocketIO error: {e}")


# --- Main Execution Block ---
if __name__ == '__main__':
    logger.info("Starting Flask-SocketIO server (Eventlet)...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=True)