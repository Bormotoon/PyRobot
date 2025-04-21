import sys
import os
import unittest
import io

# Добавляем путь к директории 'generated' в sys.path
# Определяем абсолютный путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(__file__))
# Формируем путь к директории 'generated' относительно текущего файла
generated_path = os.path.join(current_dir, 'pyrobot', 'backend', 'kumir_interpreter', 'generated')
# Добавляем путь в sys.path, если его там еще нет
if generated_path not in sys.path:
    sys.path.insert(0, generated_path)

# Добавляем также путь к директории 'kumir_interpreter', чтобы найти другие модули, если они понадобятся
interpreter_path = os.path.dirname(generated_path)
if interpreter_path not in sys.path:
    sys.path.insert(0, interpreter_path)

from antlr4 import *
# Удаляем импорты парсера/лексера, они теперь внутри interpret_kumir
# from generated.KumirLexer import KumirLexer
# from generated.KumirParser import KumirParser
# from antlr4.error.ErrorListener import ErrorListener

# Импортируем новую функцию и Visitor (если понадобится ErrorListener)
from pyrobot.backend.kumir_interpreter.interpreter import interpret_kumir, KumirInterpreterVisitor
# from antlr4.error.ErrorListener import ErrorListener # Понадобится, если будем проверять ошибки парсинга

# Глобальная переменная для ошибок больше не нужна здесь,
# обработка ошибок будет внутри interpret_kumir или тестов
# last_syntax_error = None

# MyErrorListener больше не нужен здесь (или его нужно передавать в interpret_kumir)
# class MyErrorListener(ErrorListener): ...

# Функция parse_kumir_string больше не нужна
# def parse_kumir_string(input_string): ...

class TestKumirParserAndInterpreter(unittest.TestCase):
    """Тесты для парсера и базового Visitor'а Кумира."""

    # Устанавливаем флаг для вывода stderr от interpret_kumir
    # Но пока interpret_kumir сам печатает ошибки, это не нужно
    # def setUp(self):
    #     self._stderr_capture = io.StringIO()
    #     sys.stderr = self._stderr_capture

    # def tearDown(self):
    #     sys.stderr = sys.__stderr__
    #     # Можно распечатать stderr, если нужно
    #     # print("Captured stderr:\n", self._stderr_capture.getvalue())

    def assertParsesAndInterprets(self, code, should_succeed=True, msg=""):
        """Проверяет, что код парсится и обходится Visitor'ом без исключений."""
        # print(f"Тестируем код:\n{code}") # Отладка
        result = interpret_kumir(code)
        if should_succeed:
            self.assertTrue(result, msg + " (Интерпретация должна быть успешной)")
        else:
            # TODO: Если нужно проверять конкретные ошибки парсинга/интерпретации
            self.assertFalse(result, msg + " (Интерпретация должна завершиться неудачей)")

    def test_01_with_declarations(self):
        """Тест парсинга и обхода корректного кода с многословными объявлениями."""
        kumir_code = """
алг Тест С Объявлением
лит Моя Строка
нач
кон
"""
        print("\n--- Тест 1: С многословными объявлениями (Интерпретация) ---")
        self.assertParsesAndInterprets(kumir_code)

    def test_02_without_declarations(self):
        """Тест парсинга и обхода корректного кода без объявлений (многословное имя алг)."""
        kumir_code = """
алг Тест Без Объявления
нач
кон
"""
        print("\n--- Тест 2: Без объявлений (многословное имя алг) (Интерпретация) ---")
        self.assertParsesAndInterprets(kumir_code)

    def test_03_invalid_missing_kon(self):
        """Тест парсинга неверного кода (отсутствует 'кон'). Ожидаем ошибку парсинга."""
        kumir_code = """
алг Тест Ошибка
нач
    # нет кон
"""
        print("\n--- Тест 3: Ошибка (нет 'кон') (Интерпретация) ---")
        # interpret_kumir выведет ошибку ANTLR, и вернет False
        self.assertParsesAndInterprets(kumir_code, should_succeed=False)

    def test_04_invalid_extra_token(self):
        """Тест парсинга неверного кода (лишний токен перед 'нач'). Ожидаем ошибку парсинга."""
        kumir_code = """
алг Тест Ошибка 2
лит Моя Строка
; тут ошибка
нач
кон
"""
        print("\n--- Тест 4: Ошибка (лишний ';') (Интерпретация) ---")
        self.assertParsesAndInterprets(kumir_code, should_succeed=False)

    def test_05_multiword_assignment_and_expr(self):
        """Тест присваивания, вычисления выражения и использования многословной переменной."""
        kumir_code = """
алг Тест Выражения
цел результат
цел а, b
нач
  а := 5
  b := 10
  результат := (а + b * 2) - 3 
  вывод результат 
кон
"""
        print("\n--- Тест 5: Присваивание и простое выражение (Интерпретация) ---")
        self.assertParsesAndInterprets(kumir_code)
        # TODO: Добавить проверку конечного значения 'результат' (когда будет доступ к state)

    def test_06_multiword_in_loop(self):
        """Тест использования многословной переменной в цикле for (Обход)."""
        kumir_code = """
алг Тест Цикла
цел индекс цикла
нач
  нц для индекс цикла от 1 до 5
    вывод индекс цикла
  кц
кон
"""
        print("\n--- Тест 6: Многословная переменная в цикле (Интерпретация) ---")
        self.assertParsesAndInterprets(kumir_code)

    def test_07_logical_operations(self):
        """Тест логических операций и присваивания."""
        kumir_code = """
алг Тест Логики
лог флаг А, флаг Б, результат
нач
  флаг А := да
  флаг Б := нет
  результат := флаг А и (не флаг Б)
  вывод результат 
  результат := (флаг А или флаг Б) и флаг Б
  вывод результат 
кон
"""
        print("\n--- Тест 7: Логические операции (Интерпретация) ---")
        self.assertParsesAndInterprets(kumir_code)
        # TODO: Проверить конечные значения переменных

    def test_08_type_conversion_and_error(self):
        """Тест неявного преобразования типов и ошибки типа при присваивании."""
        # Успешное присваивание цел -> вещ
        kumir_code_success = """
алг Тест Типов Успех
вещ моя вещ переменная
цел моя цел переменная
нач
  моя цел переменная := 10
  моя вещ переменная := моя цел переменная + 5.5
  вывод моя вещ переменная
кон
"""
        print("\n--- Тест 8a: Преобразование типов (успех) ---")
        self.assertParsesAndInterprets(kumir_code_success)

        # Ошибка присваивания вещ -> цел
        kumir_code_fail = """
алг Тест Типов Ошибка
вещ моя вещ переменная
цел моя цел переменная
нач
  моя вещ переменная := 10.5
  моя цел переменная := моя вещ переменная 
кон
"""
        print("\n--- Тест 8b: Преобразование типов (ошибка) ---")
        # Ожидаем ошибку AssignmentError внутри interpret_kumir
        self.assertParsesAndInterprets(kumir_code_fail, should_succeed=False)

# Добавляем стандартный запуск unittest
if __name__ == '__main__':
    unittest.main() 