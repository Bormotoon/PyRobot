"""
Модуль server.py
@description Серверная часть приложения для интерпретации кода на языке KUMIR.
Реализован с использованием Flask и Flask-CORS для обеспечения взаимодействия с фронтендом.
Принимает POST-запросы на маршрутах /execute для выполнения кода и /reset для сброса состояния симулятора.
"""

import logging

from flask import Flask, request, jsonify
from flask_cors import CORS

# Импортируем класс интерпретатора языка KUMIR из соответствующего модуля проекта.
from pyrobot.backend.kumir_interpreter.interpreter import KumirLanguageInterpreter

# Создаем экземпляр приложения Flask
app = Flask(__name__)
# Настраиваем CORS для приложения, разрешая запросы с фронтенд-домена (укажите ваш домен, если отличается)
CORS(app,
     resources={r"/execute": {"origins": "http://localhost:3000"}, r"/reset": {"origins": "http://localhost:3000"}})

# Настройка логирования: уровень DEBUG для подробной отладки
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('FlaskServer')


@app.route('/execute', methods=['POST'])
def execute_code():
    """
    Обрабатывает запрос на выполнение кода.

    Ожидается JSON с полем "code", содержащим исходный код программы на языке KUMIR.
    Если код пустой, возвращается ошибка с кодом 400.
    При успешном выполнении создается новый экземпляр интерпретатора, выполняется интерпретация кода,
    и возвращается JSON с результатом, содержащим success, message, а также обновленное окружение,
    позицию робота и другие данные (если есть).

    Возвращаемое значение:
      JSON-ответ с результатом выполнения или сообщением об ошибке.
    """
    data = request.json
    # Извлекаем исходный код из JSON-запроса; если поле отсутствует, используем пустую строку
    code = data.get('code', '')
    logger.info("Получен код для выполнения.")
    logger.debug(f"Код:\n{code}")

    # Если код пустой, возвращаем ошибку
    if not code.strip():
        logger.warning("Получен пустой код.")
        return jsonify({'success': False, 'message': 'Код не предоставлен.'}), 400

    try:
        # Для каждого запроса создается новый экземпляр интерпретатора,
        # чтобы избежать влияния предыдущих состояний.
        interpreter = KumirLanguageInterpreter(code)
        result = interpreter.interpret()
        logger.info("Код выполнен успешно.")
        logger.debug(f"Результат: {result}")
        # Возвращаем успешный JSON-ответ. Распаковываем словарь result, который содержит данные окружения,
        # позицию робота и другие параметры (например, output, если используется).
        return jsonify({'success': True, 'message': 'Код выполнен успешно.', **result}), 200

    except Exception as e:
        # Логируем исключение и возвращаем ответ с кодом 500, сообщая о неизвестной ошибке.
        logger.exception("Неизвестная ошибка при выполнении кода.")
        return jsonify({'success': False, 'message': f'Неизвестная ошибка: {str(e)}'}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    """
    Обрабатывает запрос на сброс симулятора.

    В новой архитектуре состояние интерпретатора не хранится глобально,
    поэтому достаточно вернуть сообщение о сбросе.

    Возвращаемое значение:
      JSON-ответ с успешным сообщением о сбросе симулятора.
    """
    logger.info("Запрос на сброс симулятора получен. (Глобальное состояние не сохраняется.)")
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


if __name__ == '__main__':
    # Запускаем сервер Flask в режиме отладки на порту 5000.
    app.run(debug=True, port=5000)
