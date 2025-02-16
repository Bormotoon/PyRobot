"""
Модуль server.py
@description Серверная часть приложения для интерпретации кода на языке KUMIR.
Реализован с использованием Flask и Flask-CORS для взаимодействия с фронтендом.
"""

import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from pyrobot.backend.kumir_interpreter.interpreter import KumirLanguageInterpreter

app = Flask(__name__)
CORS(app, resources={r"/execute": {"origins": "http://localhost:3000"},
                     r"/reset": {"origins": "http://localhost:3000"},
                     r"/updateField": {"origins": "http://localhost:3000"}})

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('FlaskServer')

global_field_state = None


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
        interpreter = KumirLanguageInterpreter(code)
        # Выполнение в batch-режиме: все шаги выполняются сразу, без задержек
        result = interpreter.interpret(step_by_step=False, step_delay=0)
        logger.info("Код выполнен успешно.")
        logger.debug(f"Результат: {result}")
        # Извлекаем finalState и trace, формируя плоский объект ответа
        final_state = result.get("finalState", {})
        trace = result.get("trace", [])
        if global_field_state is not None:
            final_state['field'] = global_field_state
        response = {'success': True, 'message': 'Код выполнен успешно.', **final_state, 'trace': trace}
        return jsonify(response), 200

    except Exception as e:
        logger.exception("Неизвестная ошибка при выполнении кода.")
        return jsonify({'success': False, 'message': f'Неизвестная ошибка: {str(e)}'}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    logger.info("Запрос на сброс симулятора получен. (Глобальное состояние не сохраняется.)")
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


@app.route('/updateField', methods=['POST'])
def update_field():
    global global_field_state
    data = request.json
    logger.info("Получено обновление состояния поля.")
    logger.debug(f"Field state: {data}")
    global_field_state = data
    return jsonify({'success': True, 'message': 'Поле обновлено на сервере.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
