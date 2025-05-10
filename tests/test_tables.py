import pytest
from pyrobot.backend.kumir_interpreter.interpreter import interpret_kumir
from pyrobot.backend.kumir_interpreter.kumir_exceptions import KumirEvalError, KumirSyntaxError

def test_simple_1d_table_declaration_assignment_output():
    """
    Тестирует объявление одномерной таблицы, присваивание значения элементу
    и вывод этого элемента.
    """
    code = """
    алг ТестПростойТаблицы1
    нач
      целтаб МояТаблица[1:3]
      МояТаблица[2] := 42
      вывод МояТаблица[2]
    кон
    """
    expected_output = "42\n"
    # Захватываем stderr, чтобы видеть отладочные сообщения интерпретатора, если тест упадет
    # import sys
    # from io import StringIO
    # old_stderr = sys.stderr
    # sys.stderr = captured_stderr = StringIO()
    
    try:
        output = interpret_kumir(code)
        assert output == expected_output
    except Exception as e:
        # sys.stderr = old_stderr
        # print(f"Stderr_capture:\n{captured_stderr.getvalue()}", file=sys.stderr)
        pytest.fail(f"Тест упал с ошибкой: {e}\n{code}")
    # finally:
        # sys.stderr = old_stderr # Восстанавливаем stderr в любом случае
        # pass # Убрали вывод captured_stderr, если тест прошел

# TODO: Добавить больше тестов:
# - Разные типы данных (вещтаб, логтаб, симтаб, литтаб)
# - Многомерные таблицы (2D, 3D)
# - Граничные условия для индексов (первый, последний)
# - Ошибки: выход за границы массива
# - Ошибки: неправильный тип индекса
# - Ошибки: неправильный тип присваиваемого значения
# - Присваивание одной таблицы другой
# - Передача таблиц в процедуры/функции (арг, рез, арг рез)
# - Использование таблиц в выражениях
# - Инициализация таблиц при объявлении (если будет поддержана)
# - Пустые таблицы или таблицы с "перевернутыми" границами (например, [5:1]) 