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
        # Успешное присваивание цел -> вещ (Исправлены имена переменных)
        kumir_code_success = """
алг Тест Типов Успех
вещ моя_вещ_переменная
цел моя_цел_переменная
нач
  моя_цел_переменная := 10
  моя_вещ_переменная := моя_цел_переменная + 5.5
  вывод моя_вещ_переменная
кон
"""
        print("\n--- Тест 8a: Преобразование типов (успех) ---")
        self.assertParsesAndInterprets(kumir_code_success)

        # Ошибка присваивания вещ -> цел (Исправлены имена переменных)
        kumir_code_fail = """
алг Тест Типов Ошибка
вещ моя_вещ_переменная
цел моя_цел_переменная
нач
  моя_вещ_переменная := 10.5
  моя_цел_переменная := моя_вещ_переменная 
кон
"""
        print("\n--- Тест 8b: Преобразование типов (ошибка) ---")
        # Ожидаем ошибку AssignmentError внутри interpret_kumir
        self.assertParsesAndInterprets(kumir_code_fail, should_succeed=False)

    def test_09_while_loop(self):
        """Тесты для цикла ПОКА."""
        # 1. Простой цикл пока
        kumir_code_simple = """
алг Тест Цикла Пока
цел счетчик
нач
  счетчик := 0
  нц пока счетчик < 3
    вывод "Итерация ", счетчик, нс
    счетчик := счетчик + 1
  кц
  вывод "Конец цикла, счетчик=", счетчик
кон
"""
        print("\n--- Тест 9a: Цикл ПОКА (простой) ---")
        self.assertParsesAndInterprets(kumir_code_simple)

        # 2. Цикл пока с ложным условием
        kumir_code_false = """
алг Тест Цикла Пока Ложь
цел x
нач
  x := 5
  нц пока x < 5
    вывод "Эта строка не должна вывестись"
    x := x + 1
  кц
  вывод "Цикл завершен"
кон
"""
        print("\n--- Тест 9b: Цикл ПОКА (условие ложно) ---")
        self.assertParsesAndInterprets(kumir_code_false)

        # 3. Цикл пока с логической переменной
        kumir_code_log = """
алг Тест Цикла Пока Лог
лог продолжать
цел i
нач
  продолжать := да
  i := 0
  нц пока продолжать
    i := i + 1
    вывод i, нс
    если i >= 2 то 
      продолжать := нет
    все
  кц
кон
"""
        print("\n--- Тест 9c: Цикл ПОКА (логическая переменная) ---")
        self.assertParsesAndInterprets(kumir_code_log)
        
        # 4. Ошибка: нелогическое условие
        kumir_code_err_type = """
алг Тест Цикла Пока Ошибка Типа
цел x
нач
  x := 1
  нц пока x 
    вывод x
  кц
кон
"""
        print("\n--- Тест 9d: Цикл ПОКА (ошибка типа условия) ---")
        self.assertParsesAndInterprets(kumir_code_err_type, should_succeed=False)

    def test_10_times_loop(self):
        """Тесты для цикла РАЗ."""
        # 1. Простой цикл раз
        kumir_code_simple = """
алг Тест Цикла Раз
нач
  нц 3 раз
    вывод "Привет!"
  кц
кон
"""
        print("\n--- Тест 10a: Цикл РАЗ (простой) ---")
        self.assertParsesAndInterprets(kumir_code_simple)
        
        # 2. Цикл 0 раз
        kumir_code_zero = """
алг Тест Цикла Раз Ноль
нач
  нц 0 раз
    вывод "Эта строка не должна вывестись"
  кц
  вывод "Цикл завершен"
кон
"""
        print("\n--- Тест 10b: Цикл РАЗ (ноль итераций) ---")
        self.assertParsesAndInterprets(kumir_code_zero)
        
        # 3. Цикл с переменным числом раз
        kumir_code_var = """
алг Тест Цикла Раз Переменная
цел количество
нач
  количество := 2 + 1
  нц количество раз
    вывод количество
    количество := количество - 1
  кц
кон
"""
        print("\n--- Тест 10c: Цикл РАЗ (переменное N) ---")
        self.assertParsesAndInterprets(kumir_code_var)
        
        # 4. Ошибка: нецелое число раз
        kumir_code_err_type = """
alг Тест Цикла Раз Ошибка Типа
вещ N
нач
  N := 2.5
  нц N раз
    вывод N
  кц
кон
"""
        print("\n--- Тест 10d: Цикл РАЗ (ошибка типа N) ---")
        self.assertParsesAndInterprets(kumir_code_err_type, should_succeed=False)
        
        # 5. Ошибка: отрицательное число раз
        kumir_code_err_neg = """
алг Тест Цикла Раз Отрицательное
цел N
нач
  N := -2
  нц N раз
    вывод N
  кц
кон
"""
        print("\n--- Тест 10e: Цикл РАЗ (отрицательное N) ---")
        self.assertParsesAndInterprets(kumir_code_err_neg, should_succeed=False)

    def test_11_ne_operator_and_identifier(self):
        """Тесты для оператора НЕ и слова НЕ в идентификаторе."""
        # 1. НЕ как оператор
        kumir_code_op = """
алг Тест Оператора НЕ
лог флаг, результат
нач
  флаг := нет
  результат := не флаг
  вывод результат
кон
"""
        print("\n--- Тест 11a: Оператор НЕ ---")
        self.assertParsesAndInterprets(kumir_code_op)

        # 2. НЕ как часть идентификатора (валидный случай)
        kumir_code_id = """
алг Тест НЕ в Идентификаторе
лог файл не найден
нач
  файл не найден := да
  если файл не найден то
     вывод "Файл действительно не найден!"
  все
кон
"""
        print("\n--- Тест 11b: НЕ в идентификаторе (валидный) ---")
        self.assertParsesAndInterprets(kumir_code_id)

        # 3. Ошибка: НЕ в конце идентификатора (невалидный случай)
        kumir_code_err_end = """
алг Тест НЕ в Идентификаторе Ошибка
лог флаг не
нач
  флаг не := да
кон
"""
        print("\n--- Тест 11c: НЕ в идентификаторе (ошибка в конце) ---")
        self.assertParsesAndInterprets(kumir_code_err_end, should_succeed=False)
        
        # 4. Ошибка: Два НЕ в идентификаторе (невалидный случай)
        # Замечание: Грамматика может это разобрать как "(не (не флаг))", 
        # но семантически это не имя "не не флаг"
        kumir_code_err_double = """
алг Тест НЕ в Идентификаторе Двойное
лог не не флаг
нач
  не не флаг := да
кон
"""
        print("\n--- Тест 11d: НЕ в идентификаторе (двойное НЕ - должно быть ошибкой?) ---")
        # Ожидаем ошибку парсинга или выполнения, т.к. "не не флаг" не должно быть валидным именем
        self.assertParsesAndInterprets(kumir_code_err_double, should_succeed=False) 

    def test_12_uses_and_intro(self):
        """Тесты для директивы 'использовать' и вступления."""
        # 1. Только 'использовать'
        kumir_code_uses = """
использовать Робот
использовать Файлы
алг Пустой
нач
кон
"""
        print("\n--- Тест 12a: Только 'использовать' ---")
        # TODO: Реально 'использовать' пока ничего не делает, но парсинг должен пройти
        self.assertParsesAndInterprets(kumir_code_uses)

        # 2. Только вступление
        kumir_code_intro = """
цел глоб_перем
глоб_перем := 100
| Комментарий во вступлении
вывод "Вступление: ", глоб_перем

алг Основной
нач
  вывод "Основной: ", глоб_перем
кон
"""
        print("\n--- Тест 12b: Только вступление ---")
        self.assertParsesAndInterprets(kumir_code_intro)

        # 3. 'использовать' и вступление вместе
        kumir_code_both = """
использовать МодульОдин

лит сообщение
сообщение := "Привет из вступления!"

алг Главный
нач
  вывод сообщение
кон
"""
        print("\n--- Тест 12c: 'использовать' и вступление ---")
        self.assertParsesAndInterprets(kumir_code_both)

        # 4. Пустой файл (должен парситься без ошибок)
        kumir_code_empty = """
"""
        print("\n--- Тест 12d: Пустой файл ---")
        self.assertParsesAndInterprets(kumir_code_empty)

        # 5. Файл только с комментарием (должен парситься без ошибок)
        kumir_code_comment = """
| Это просто комментарий

"""
        print("\n--- Тест 12e: Только комментарий ---")
        self.assertParsesAndInterprets(kumir_code_comment)

# Добавляем стандартный запуск unittest
if __name__ == '__main__':
    unittest.main() 