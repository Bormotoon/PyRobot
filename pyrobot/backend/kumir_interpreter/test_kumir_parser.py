import sys
from antlr4 import *
from .generated.KumirLexer import KumirLexer
from .generated.KumirParser import KumirParser
from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    """Кастомный обработчик ошибок для вывода в stderr."""
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"Ошибка синтаксиса в строке {line}:{column} - {msg}", file=sys.stderr)
        # Можно раскомментировать, чтобы остановить парсинг при первой ошибке
        # raise Exception(f"Ошибка синтаксиса в строке {line}:{column} - {msg}")

def parse_kumir(input_string, test_name):
    """Функция для парсинга строки с кодом Кумира."""
    print(f"--- Запуск теста: {test_name} ---")
    print(f"Парсинг ввода:\n---\n{input_string}\n---")
    input_stream = InputStream(input_string)
    lexer = KumirLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = KumirParser(stream)

    # Удаляем стандартный обработчик ошибок и добавляем свой
    parser.removeErrorListeners()
    parser.addErrorListener(MyErrorListener())

    success = False
    try:
        # Начинаем разбор с правила 'start'
        tree = parser.start()
        print("Парсинг успешен!")
        success = True
    except Exception as e:
        print(f"Парсинг завершился с исключением: {e}", file=sys.stderr)
        success = False
    finally:
        print("--- Тест завершен ---\n")
        return success

if __name__ == '__main__':
    # Тест 1: С объявлениями и присваиванием
    kumir_code_1 = """алг Тест1
лит МояСтрока
цел i
нач
i := 5
МояСтрока := "Привет"
кон
"""
    parse_kumir(kumir_code_1, "Объявления и присваивание")

    # Тест 2: Без объявлений, вывод
    kumir_code_2 = """алг Тест2
нач
вывод "Мир", нс, 123
кон
"""
    parse_kumir(kumir_code_2, "Вывод и нс")

    # Тест 3: Условие ЕСЛИ-ТО-ИНАЧЕ-ВСЕ
    kumir_code_3 = """алг Тест3
лог флаг
цел x
нач
x := -10
флаг := x > 0
если флаг то
  вывод "Положительное"
иначе
  вывод "Неположительное"
все
кон
"""
    parse_kumir(kumir_code_3, "Условие Если")

    # Тест 4: Цикл ДЛЯ
    kumir_code_4 = """алг Тест4
цел i
нач
нц для i от 1 до 5 шаг 2
  вывод i
кц
кон
"""
    parse_kumir(kumir_code_4, "Цикл Для")

    # Тест 5: Цикл ПОКА
    kumir_code_5 = """алг Тест5
цел счетчик
нач
счетчик := 0
нц пока счетчик < 3
  счетчик := счетчик + 1
  вывод счетчик
кц
кон
"""
    parse_kumir(kumir_code_5, "Цикл Пока")

    # Тест 6: Выражения
    kumir_code_6 = """алг ТестВыражения
цел а, b, c
вещ x, y
лог усл
нач
a := 5
b := 10
c := (a + b) * 2 - a div 2
x := 3.14 * (b**2)
y := -x + 5.0e-1
усл := (a < b) и (не (c = 24) или (x > 100.0))
вывод a, b, c, x, y, усл
кон
"""
    parse_kumir(kumir_code_6, "Сложные выражения")

    # Тест 7: Таблицы (объявление и доступ)
    kumir_code_7 = """алг ТестТаблицы
таб цел числа[1:5]
цел i, сумма
нач
нц для i от 1 до 5
  числа[i] := i * 10
кц
сумма := числа[2] + числа[4]
вывод сумма
кон
"""
    parse_kumir(kumir_code_7, "Таблицы")

    # Тест 8: Функция
    kumir_code_8 = """алг вещ Квадрат(арг вещ x)
нач
знач := x * x
кон

алг Главный
вещ y
нач
y := Квадрат(5.0)
вывод y
кон
"""
    parse_kumir(kumir_code_8, "Функция")

    # Тест 9: Ошибка - нет кон
    kumir_code_err_1 = """алг Ошибка1
нач
вывод """
    parse_kumir(kumir_code_err_1, "Ошибка - нет кон")

    # Тест 10: Ошибка - несоответствие типов (проверяется позже)
    # kumir_code_err_2 = """алг Ошибка2
    # цел n
    # нач
    # n := "привет"
    # кон
    # """
    # parse_kumir(kumir_code_err_2, "Ошибка - типы") 