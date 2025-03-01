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


@app.route('/updateField', methods=['POST'])
def update_field():
    data = request.json
    logger.info("Получено обновление состояния поля.")
    logger.debug(f"Field state: {data}")
    session['field_state'] = data
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
        field_state = session.get('field_state')
        from pyrobot.backend.kumir_interpreter.interpreter import KumirLanguageInterpreter
        interpreter = KumirLanguageInterpreter(code)
        interpreter.parse()
        trace = []
        interpreter.execute_introduction(trace, step_delay=0, step_by_step=False)
        interpreter.robot.robot_pos = {'x': 0, 'y': 0}
        interpreter.robot.colored_cells = set()
        if field_state is not None and 'walls' in field_state:
            interpreter.robot.walls = set(field_state['walls'])
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
        response = {
            'success': True,
            'steps': steps
        }
        return jsonify(response), 200

    except Exception as e:
        logger.exception("Ошибка при выполнении кода.")
        output = interpreter.output if interpreter is not None else ""
        return jsonify({
            'success': False,
            'message': f'Ошибка: {str(e)}',
            'output': output
        }), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    logger.info("Запрос на сброс симулятора получен. (Состояние сессии будет очищено.)")
    session.pop('field_state', None)
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)