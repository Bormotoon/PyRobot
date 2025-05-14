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
    expected_output = "42"
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

def test_2d_table_operations():
    """
    Тестирует объявление двумерной таблицы, присваивание значений элементам
    и вывод этих элементов.
    """
    code = """
    алг Тест2DТаблицы
    нач
      целтаб Т[1:2, 0:1]
      Т[1,0] := 10
      Т[1,1] := 11
      Т[2,0] := 20
      Т[2,1] := 21
      вывод Т[1,0], " ", Т[1,1], нс
      вывод Т[2,0], " ", Т[2,1], нс
    кон
    """
    expected_output = "10 11\n20 21\n" # Важно: КуМир обычно не добавляет \n в конце, если нет явного нс. Но наш interpret_kumir может добавлять.
                                      # Однако, команды вывод с нс должны каждая завершаться \n.
                                      # И последняя команда вывод с нс тоже должна дать \n.
                                      # Исходя из AI_notes.md (09.08.2024) по финальному \n, interpret_kumir больше не должен добавлять лишний \n.
                                      # Значит, "10 11\n20 21\n" - это верный ожидаемый вывод.

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
        pytest.fail(f"Тест упал с ошибкой: {e}\nКод:\n{code}")
    # finally:
        # sys.stderr = old_stderr # Восстанавливаем stderr в любом случае
        # pass

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