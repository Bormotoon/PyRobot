"""
Модуль server.py
@description Серверная часть приложения для интерпретации кода на языке KUMIR.
Реализован с использованием Flask и Flask-CORS для обеспечения взаимодействия с фронтендом.
Принимает POST-запросы на маршрутах /execute для выполнения кода, /reset для сброса состояния симулятора,
а также /updateField для обновления состояния игрового поля.
"""

import logging

from flask import Flask, request, jsonify
from flask_cors import CORS

# Импортируем класс интерпретатора языка KUMIR из соответствующего модуля проекта.
from pyrobot.backend.kumir_interpreter.interpreter import KumirLanguageInterpreter

# Создаем экземпляр приложения Flask
app = Flask(__name__)
# Настраиваем CORS для приложения, разрешая запросы с фронтенд-домена
CORS(app, resources={r"/execute": {"origins": "http://localhost:3000"}, r"/reset": {"origins": "http://localhost:3000"},
                     r"/updateField": {"origins": "http://localhost:3000"}})

# Настройка логирования: уровень DEBUG для подробной отладки
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('FlaskServer')

# Глобальная переменная для хранения текущего состояния игрового поля,
# обновляемого из фронтенда при редактировании.
global_field_state = None


@app.route('/execute', methods=['POST'])
def execute_code():
    """
    Обрабатывает запрос на выполнение кода.

    Ожидается JSON с полем "code", содержащим исходный код программы на языке KUMIR.
    Если код пустой, возвращается ошибка с кодом 400.
    При успешном выполнении создается новый экземпляр интерпретатора, выполняется интерпретация кода,
    и возвращается JSON с результатом, содержащим success, message, а также обновленное окружение,
    позицию робота и (если обновлено) актуальное состояние поля из global_field_state.
    """
    data = request.json
    code = data.get('code', '')
    logger.info("Получен код для выполнения.")
    logger.debug(f"Код:\n{code}")

    if not code.strip():
        logger.warning("Получен пустой код.")
        return jsonify({'success': False, 'message': 'Код не предоставлен.'}), 400

    try:
        interpreter = KumirLanguageInterpreter(code)
        result = interpreter.interpret()
        logger.info("Код выполнен успешно.")
        logger.debug(f"Результат: {result}")
        # Если состояние поля было обновлено, включаем его в результат.
        if global_field_state is not None:
            result['field'] = global_field_state
        return jsonify({'success': True, 'message': 'Код выполнен успешно.', **result}), 200

    except Exception as e:
        logger.exception("Неизвестная ошибка при выполнении кода.")
        return jsonify({'success': False, 'message': f'Неизвестная ошибка: {str(e)}'}), 500


@app.route('/reset', methods=['POST'])
def reset_simulator():
    """
    Обрабатывает запрос на сброс симулятора.

    В новой архитектуре состояние интерпретатора не хранится глобально,
    поэтому достаточно вернуть сообщение о сбросе.
    """
    logger.info("Запрос на сброс симулятора получен. (Глобальное состояние не сохраняется.)")
    return jsonify({'success': True, 'message': 'Симулятор сброшен.'}), 200


@app.route('/updateField', methods=['POST'])
def update_field():
    """
    Обрабатывает запрос на обновление состояния игрового поля.

    Ожидается JSON с параметрами поля:
      - width, height, cellSize,
      - robotPos (объект {x, y}),
      - walls, permanentWalls (массивы строк),
      - markers (объект),
      - coloredCells (массив строк).

    Сохраняет полученное состояние в глобальной переменной global_field_state.
    """
    global global_field_state
    data = request.json
    logger.info("Получено обновление состояния поля.")
    logger.debug(f"Field state: {data}")
    global_field_state = data
    return jsonify({'success': True, 'message': 'Поле обновлено на сервере.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
