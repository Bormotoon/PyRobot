# backend/server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from kumir_interpreter.interpreter import KumirLanguageInterpreter  # Импорт нового интерпретатора

app = Flask(__name__)
CORS(app, resources={
    r"/execute": {"origins": "http://localhost:3000"},  # Замените на ваш фронтенд-домен
    r"/reset": {"origins": "http://localhost:3000"}
})

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('FlaskServer')


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
        # Создаем новый экземпляр интерпретатора языка Кумир для каждого запроса
        interpreter = KumirLanguageInterpreter(code)
        result = interpreter.interpret()
        logger.info("Код выполнен успешно.")
        logger.debug(f"Результат: {result}")
        # Ожидаем, что результат содержит нужные поля, например:
        # { 'env': ..., 'robotPos': ..., 'walls': ..., 'markers': ..., 'coloredCells': ... }
        return jsonify({
            'success': True,
            'message': 'Код выполнен успешно.',
            **result
        }), 200

    except Exception as e:
        logger.exception("Неизвестная ошибка при выполнении кода.")
        return jsonify({'success': False, 'message': f'Неизвестная ошибка: {str(e)}'}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    # В новой парадигме состояние интерпретатора не хранится глобально,
    # поэтому можно просто вернуть сообщение о сбросе.
    logger.info("Запрос на сброс симулятора получен. (Глобальное состояние не сохраняется.)")
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
