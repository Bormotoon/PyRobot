\
import os
import sys

# Добавляем корень проекта в sys.path, чтобы можно было импортировать pyrobot
# __file__ это tests/test_task_1_0.py
# os.path.dirname(__file__) это tests/
# os.path.join(os.path.dirname(__file__), '..') это ../ (корень проекта)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

# Путь к файлу программы КуМир для тестирования
# Файл 1-0.kum находится в корне проекта
PROGRAM_FILE_PATH = os.path.join(project_root, "1-0.kum")

# Старое имя: def test_task_1_0_solution():
def test_task_1_0_identifies_naado_syntax_error(): # НОВОЕ ИМЯ ТЕСТА
    """
    Тестирует, что PyRobot корректно определяет синтаксическую ошибку
    в файле 1-0.kum, связанную с ключевым словом 'надо'.
    """
    assert os.path.exists(PROGRAM_FILE_PATH), f"Файл программы не найден: {PROGRAM_FILE_PATH}"

    with open(PROGRAM_FILE_PATH, 'r', encoding='utf-8') as f:
        code = f.read().replace('\\r\\n', '\\n').replace('\\r', '\\n')

    # Вызываем interpret_kumir напрямую - он теперь возвращает строку с ошибкой вместо исключения
    result = interpret_kumir(code, None)

    # Проверяем, что результат содержит маркер синтаксической ошибки
    assert result.startswith("SYNTAX_ERROR:"), f"Ожидался результат, начинающийся с 'SYNTAX_ERROR:', но получено: {result}"
    
    # Проверяем, что ошибка связана с ключевым словом 'надо'
    assert "mismatched input 'надо'" in result, f"Ожидалось сообщение об ошибке, содержащее 'mismatched input \\'надо\\'', но получено: {result}"
    
    # Проверяем, что указана правильная строка (строка 3)
    assert "строка 3" in result, f"Ожидалось упоминание 'строка 3' в результате, но получено: {result}"

    print(f"Тест для {os.path.basename(PROGRAM_FILE_PATH)} успешно подтвердил наличие ожидаемой синтаксической ошибки (ключевое слово 'надо' на строке 3).")

