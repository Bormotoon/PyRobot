import logging

import eventlet

eventlet.monkey_patch()
import redis
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, join_room, emit
from .kumir_interpreter.interpreter import KumirLanguageInterpreter, KumirExecutionError, KumirEvalError
from .kumir_interpreter.robot_state import RobotError

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
# Session Config ... (unchanged, ensure SECRET_KEY is set)
app.config['SECRET_KEY'] = 'your-secret-key-needs-to-be-set'  # !! CHANGE THIS !!
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

Session(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", manage_session=False, async_mode='eventlet')
logger = logging.getLogger('FlaskServer');  # Basic logging setup assumed sufficient for now
if not logger.handlers: handler = logging.StreamHandler(); handler.setFormatter(
    logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')); logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def get_field_state_from_session():
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


@app.route('/updateField', methods=['POST'])
def update_field():
    d = request.json
    if not d or not isinstance(d, dict) or 'width' not in d or 'height' not in d:
        return jsonify({'success': False, 'message': 'Invalid data.'}), 400
    logger.info("Update field.")
    logger.debug(f"State:{d}")
    session['field_state'] = d
    session.modified = True
    return jsonify({'success': True, 'message': 'State updated.'}), 200


@app.route('/execute', methods=['POST'])
def execute_code():
    logger.debug(f"Session @ /execute start: {dict(session.items())}");
    sid = session.get('sid');
    logger.info(f"Execute req (SID: {sid})")
    if not request.is_json: return jsonify({'success': False, 'message': 'Invalid request.'}), 415
    data = request.get_json();
    code = data.get('code', '').strip();
    client_state = data.get('fieldState')
    if not code: return jsonify({'success': False, 'message': 'Код пуст.'}), 200

    initial_state = client_state or get_field_state_from_session()
    logger.debug(
        f"Initial state: {'Request' if client_state else ('Session' if session.get('field_state') else 'Default')}")

    interpreter = None;
    trace_data = []
    try:
        interpreter = KumirLanguageInterpreter(code, initial_field_state=initial_state)
        logger.debug("Interpreter initialized.")

        def progress_callback(progress_data):
            if interpreter and hasattr(interpreter, 'robot'): progress_data[
                'robotPos'] = interpreter.robot.robot_pos.copy()  # Add current pos
            if sid:
                socketio.sleep(0)
                logger.debug(f"Emit progress to {sid}")
                socketio.emit('execution_progress', progress_data, room=sid)
            else:
                if not hasattr(progress_callback, 'warned'): logger.warning("No SID for progress.")
                progress_callback.warned = True

        result = interpreter.interpret(progress_callback=progress_callback)
        trace_data = result.get('trace', [])

        response_data = {  # Prepare response
            'success': result['success'], 'message': result.get('message', 'OK' if result['success'] else 'Error'),
            'output': result['finalState'].get('output', ''), 'robot': result['finalState'].get('robot'),
            'coloredCells': result['finalState'].get('coloredCells', []), 'env': result['finalState'].get('env', {}),
            'symbols': result['finalState'].get('symbols', {}),
            'radiation': interpreter.robot.radiation.copy() if interpreter else {},  # <-- Get final radiation
            'temperature': interpreter.robot.temperature.copy() if interpreter else {},  # <-- Get final temperature
            'trace': trace_data}

        if not result['success']:
            response_data['errorIndex'] = result.get('errorIndex');
            logger.warning(f"Exec fail: {result.get('message')}")
        else:
            logger.info("Exec OK.")
            final_state = {  # Save final state to session
                'width': interpreter.width, 'height': interpreter.height, 'robotPos': response_data['robot'],
                'walls': list(interpreter.robot.walls), 'markers': interpreter.robot.markers.copy(),
                'coloredCells': response_data['coloredCells'], 'symbols': response_data['symbols'],
                'radiation': response_data['radiation'],  # <-- Save rad/temp
                'temperature': response_data['temperature']}
            session['field_state'] = final_state;
            session.modified = True;
            logger.debug("Saved final state.")
        return jsonify(response_data), 200
    except (KumirExecutionError, KumirEvalError, RobotError) as e:
        err_msg = f"Ошибка:{str(e)}";
        logger.error(err_msg, exc_info=False);
        output = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
        state_on_error = interpreter.get_state() if interpreter else {};
        state_on_error["output"] = output
        # Try to get rad/temp even on error
        state_on_error['radiation'] = interpreter.robot.radiation.copy() if interpreter and hasattr(interpreter,
                                                                                                    'robot') else {}
        state_on_error['temperature'] = interpreter.robot.temperature.copy() if interpreter and hasattr(interpreter,
                                                                                                        'robot') else {}
        return jsonify({'success': False, 'message': err_msg, **state_on_error, 'trace': trace_data}), 200
    except Exception as e:
        logger.exception("Server Error.");
        output = interpreter.output if interpreter and hasattr(interpreter, 'output') else ""
        state_on_error = interpreter.get_state() if interpreter else {};
        state_on_error["output"] = output
        state_on_error['radiation'] = interpreter.robot.radiation.copy() if interpreter and hasattr(interpreter,
                                                                                                    'robot') else {}
        state_on_error['temperature'] = interpreter.robot.temperature.copy() if interpreter and hasattr(interpreter,
                                                                                                        'robot') else {}
        return jsonify(
            {'success': False, 'message': f'Server Err:{str(e)}', **state_on_error, 'trace': trace_data}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator_session():
    sid = session.get('sid');
    logger.info(f"Reset req (SID:{sid}).");
    session.pop('field_state', None);
    session.modified = True;
    return jsonify({'success': True, 'message': 'Сброшено.'}), 200


# SocketIO Handlers
@socketio.on('connect')
def handle_connect(): logger.info(f"Connect:SID={request.sid}");session[
    'sid'] = request.sid;session.modified = True;join_room(request.sid);emit('connection_ack',
                                                                             {'sid': request.sid});logger.debug(
    f"SID saved. Session:{dict(session.items())}")


@socketio.on('disconnect')
def handle_disconnect(*args): sid = session.get('sid', request.sid); logger.info(f"Disconnect:SID={sid}")


@socketio.on_error_default
def default_error_handler(e): logger.error(f"SocketIO error: {e}")


# Main Execution
if __name__ == '__main__': logger.info("Starting Server..."); socketio.run(app, debug=True, host='0.0.0.0', port=5000,
                                                                           use_reloader=True)
