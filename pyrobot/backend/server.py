from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import redis
import logging

# Инициализация приложения Flask
app = Flask(__name__)
CORS(app,
     supports_credentials=True,
     resources={
         r"/execute": {"origins": "http://localhost:3000"},
         r"/reset": {"origins": "http://localhost:3000"},
         r"/updateField": {"origins": "http://localhost:3000"}
     })

# Настройка секретного ключа и конфигурации сессии
app.config['SECRET_KEY'] = 'your-secret-key'  # Замените на надежное значение
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
# Для локальной разработки используем 'Lax', чтобы cookie сохранялись при HTTP-соединениях
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_DOMAIN'] = 'localhost'  # если потребуется

# Инициализация Flask-Session
Session(app)

# Настройка логгирования
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

    try:
        field_state = session.get('field_state')
        from pyrobot.backend.kumir_interpreter.interpreter import KumirLanguageInterpreter
        interpreter = KumirLanguageInterpreter(code)
        interpreter.parse()
        trace = []
        interpreter.execute_introduction(trace, step_delay=0, step_by_step=False)
        if field_state is not None and 'robotPos' in field_state:
            interpreter.robot.robot_pos = field_state['robotPos']
            logger.debug(f"Начальная позиция робота переустановлена в: {field_state['robotPos']}")
        interpreter.execute_algorithm(interpreter.main_algorithm, trace, step_delay=0, step_by_step=False)
        final_state = {
            "env": interpreter.env,
            "robot": interpreter.robot.robot_pos,
            "coloredCells": list(interpreter.robot.colored_cells),
            "output": interpreter.output
        }
        result = {"trace": trace, "finalState": final_state}
        logger.info("Код выполнен успешно.")
        logger.debug(f"Результат: {result}")
        if field_state is not None:
            final_state['field'] = field_state
        response = {
            'success': True,
            'message': 'Код выполнен успешно.',
            **final_state,
            'trace': trace
        }
        return jsonify(response), 200

    except Exception as e:
        logger.exception("Неизвестная ошибка при выполнении кода.")
        return jsonify({'success': False, 'message': f'Неизвестная ошибка: {str(e)}'}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    logger.info("Запрос на сброс симулятора получен. (Состояние сессии будет очищено.)")
    session.pop('field_state', None)
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
