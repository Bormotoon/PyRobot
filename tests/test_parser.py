import pytest
import os

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

# Импортируем сгенерированные классы (должны найтись благодаря установке -e)
from pyrobot.backend.kumir_interpreter.generated.KumirLexer import KumirLexer
from pyrobot.backend.kumir_interpreter.generated.KumirParser import KumirParser

# Директория с примерами кода КуМир
KUMIR_EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'polyakov_kum'))

# Собираем список .kum файлов для параметризации теста
kumir_files = [
    os.path.join(KUMIR_EXAMPLES_DIR, f)
    for f in os.listdir(KUMIR_EXAMPLES_DIR)
    if f.endswith('.kum') and os.path.isfile(os.path.join(KUMIR_EXAMPLES_DIR, f))
]

# Класс для сбора ошибок парсинга
class SyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Возвращаем простой формат ошибки
        self.errors.append(f"line {line}:{column} {msg}")

        # offending_symbol_text = repr(offendingSymbol.text) if offendingSymbol else 'None'
        # exception_type = type(e).__name__ if e else 'None'
        # self.errors.append(f"line {line}:{column} MSG: {msg} | OFFENDING_SYMBOL: {offending_symbol_text} | EXCEPTION: {exception_type}")

# Функция для парсинга кода
def parse_kumir_code(code: str):
    # Нормализуем переносы строк (заменяем \r\n на \n)
    code = code.replace('\r\n', '\n')
    input_stream = InputStream(code)
    lexer = KumirLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = KumirParser(stream)

    # Удаляем стандартные слушатели ошибок и добавляем свой
    parser.removeErrorListeners()
    error_listener = SyntaxErrorListener()
    parser.addErrorListener(error_listener)

    # === Включаем трассировку парсера ===
    # parser.setTrace(True) # Отключаем трассировку
    # =====================================

    # Запускаем парсинг со стартового правила 'program'
    try:
        tree = parser.program() # Используем стартовое правило из грамматики
        return tree, error_listener.errors
    except Exception as e:
        # Ловим другие возможные исключения при парсинге
        return None, [str(e)]

# Параметризованный тест для каждого .kum файла
@pytest.mark.parametrize("kumir_file_path", kumir_files)
def test_kumir_file_parsing(kumir_file_path):
    """
    Тест проверяет, что файл .kum успешно парсится без синтаксических ошибок.
    """
    try:
        with open(kumir_file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except UnicodeDecodeError:
         with open(kumir_file_path, 'r', encoding='cp1251') as f: # Пробуем другую кодировку
            code = f.read()
    except Exception as e:
        pytest.fail(f"Не удалось прочитать файл {kumir_file_path}: {e}")
        return # Добавлено для ясности, хотя pytest.fail прервет выполнение

    # Убираем BOM, если он есть (часто встречается в Windows)
    if code.startswith('\ufeff'):
        code = code[1:]

    tree, errors = parse_kumir_code(code)

    assert not errors, f"Ошибки парсинга в файле {os.path.basename(kumir_file_path)}:\n" + "\n".join(errors)
    assert tree is not None, f"Парсер вернул None для файла {os.path.basename(kumir_file_path)}"