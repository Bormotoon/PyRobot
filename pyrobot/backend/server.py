# backend/server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import sys
import logging
from kumir_interpreter import KumirInterpreter, KumirInterpreterError

app = Flask(__name__)
CORS(app, resources={
    r"/execute": {"origins": "http://localhost:3000"},  # Замените на ваш фронтенд-домен
    r"/reset": {"origins": "http://localhost:3000"}
})

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('FlaskServer')

# Инициализация интерпретатора
interpreter = KumirInterpreter()


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
        # Интерпретация кода на языке КУМИР
        result = interpreter.interpret(code)

        if result['success']:
            logger.info("Код выполнен успешно.")
            logger.debug(f"Результат: {result['result']}")
            return jsonify({
                'success': True,
                'message': 'Код выполнен успешно.',
                'robotPos': interpreter.robot_pos,
                'walls': list(interpreter.walls),
                'markers': interpreter.markers,
                'coloredCells': list(interpreter.colored_cells)
            }), 200
        else:
            logger.error(f"Ошибка интерпретации: {result['message']}")
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400

    except KumirInterpreterError as e:
        logger.error(f"Ошибка интерпретатора: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        logger.exception("Неизвестная ошибка при выполнении кода.")
        return jsonify({'success': False, 'message': f'Неизвестная ошибка: {str(e)}'}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    interpreter.reset()
    logger.info("Состояние симулятора сброшено.")
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
