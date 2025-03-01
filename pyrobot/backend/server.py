import logging
import redis
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
CORS(app, supports_credentials=True,
     resources={r"/execute": {"origins": "http://localhost:3000"},
                r"/reset": {"origins": "http://localhost:3000"},
                r"/updateField": {"origins": "http://localhost:3000"}})

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_DOMAIN'] = 'localhost'

Session(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('FlaskServer')


def setup_permanent_walls(width, height):
    walls = set()
    for x in range(width):
        walls.add(f"{x},0,{x + 1},0")
        walls.add(f"{x},{height},{x + 1},{height}")
    for y in range(height):
        walls.add(f"0,{y},0,{y + 1}")
        walls.add(f"{width},{y},{width},{y + 1}")
    return walls


@app.route('/updateField', methods=['POST'])
def update_field():
    data = request.json
    logger.info("Получено обновление состояния поля.")
    logger.debug(f"Field delta: {data}")

    field_state = session.get('field_state', {})
    base_state = session.get('base_state', {'width': 7, 'height': 7, 'cellSize': 50})

    if 'robotPos' in data:
        field_state['robotPos'] = {'x': data['robotPos'][0], 'y': data['robotPos'][1]}
    if 'walls' in data:
        field_state['walls'] = data['walls']
    if 'markers' in data:
        field_state['markers'] = data['markers']
    if 'coloredCells' in data:
        field_state['coloredCells'] = data['coloredCells']

    for key in ['width', 'height', 'cellSize']:
        if key in data:
            base_state[key] = data[key]

    session['field_state'] = field_state
    session['base_state'] = base_state
    return jsonify({'success': True, 'message': 'Поле обновлено на сервере.'}), 200


@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get('code', '')
    logger.info("Получен код для выполнения.")
    logger.debug(f"Код:\n{code}")

    if not code.strip():
        logger.warning("Получен пустой код.")
        return jsonify({'success': False, 'message': 'Код не предоставлен.'}), 400

    interpreter = None
    try:
        field_state = session.get('field_state', {})
        base_state = session.get('base_state', {'width': 7, 'height': 7, 'cellSize': 50})
        from pyrobot.backend.kumir_interpreter.interpreter import KumirLanguageInterpreter
        interpreter = KumirLanguageInterpreter(code)
        interpreter.parse()
        trace = []
        interpreter.execute_introduction(trace, step_delay=0, step_by_step=False)
        interpreter.robot.robot_pos = field_state.get('robotPos', {'x': 0, 'y': 0})
        interpreter.robot.colored_cells = set(field_state.get('coloredCells', []))
        interpreter.robot.walls = set(field_state.get('walls', [])) | setup_permanent_walls(base_state['width'],
                                                                                            base_state['height'])
        logger.debug(f"Стеновые данные обновлены: {interpreter.robot.walls}")
        interpreter.execute_algorithm(interpreter.main_algorithm, trace, step_delay=0, step_by_step=False)

        steps = [
            {
                "robot": event["stateAfter"]["robot"],
                "coloredCells": event["stateAfter"]["coloredCells"]
            }
            for event in trace if "stateAfter" in event
        ]

        logger.info("Код выполнен успешно.")
        logger.debug(f"Шаги: {steps}")
        return jsonify({'success': True, 'steps': steps}), 200

    except Exception as e:
        logger.exception("Ошибка при выполнении кода.")
        output = interpreter.output if interpreter is not None else ""
        steps = [
            {
                "robot": event["stateAfter"]["robot"],
                "coloredCells": event["stateAfter"]["coloredCells"]
            }
            for event in trace if "stateAfter" in event
        ] if 'trace' in locals() else []
        return jsonify({
            'success': False,
            'message': f'Ошибка: {str(e)}',
            'steps': steps,
            'output': output
        }), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    logger.info("Запрос на сброс симулятора получен.")
    session.pop('field_state', None)
    session.pop('base_state', None)
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)