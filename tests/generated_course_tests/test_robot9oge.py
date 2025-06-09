import pytest  # type: ignore
import os
import sys
from io import StringIO

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir
from pyrobot.backend.kumir_interpreter.kumir_exceptions import KumirSyntaxError, KumirEvalError


def run_kumir_program(program_path: str, input_data: str | None = None) -> str:
    """
    Запускает программу КуМир и возвращает её стандартный вывод.

    Args:
        program_path (str): Путь к файлу программы .kum
        input_data (str, optional): Строка с входными данными. Defaults to None.

    Returns:
        str: Стандартный вывод программы.
    """
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    input_buffer = StringIO(input_data if input_data else "")
    actual_output_value = ""

    try:
        with open(program_path, 'r', encoding='utf-8') as f:
            code = f.read()
            code = code.replace('\r\n', '\n').replace('\r', '\n')
        sys.stdin = input_buffer

        actual_output_value = interpret_kumir(code, input_data)
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError for {program_path}: {e}")
    except KumirEvalError as e:
        actual_output_value += f"\nОШИБКА ВЫПОЛНЕНИЯ: {e}\n"
        pytest.fail(f"KumirEvalError for {program_path}: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc(file=original_stderr)
        pytest.fail(f"Unexpected exception for {program_path}: {e}")
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    if actual_output_value and not actual_output_value.endswith('\n'):
        actual_output_value += '\n'
    return actual_output_value

# Автогенерированные тесты для курса: robot9oge
# Сгенерировано: 2025-06-09 11:49:00

def test_robot9oge_1_A_101(tmp_path):
    """
    Тест для задачи: 1-А (ID: 101)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот находится в верхней клетке узкого 
     | вертикального коридора. Ширина коридора - 
     | одна клетка, длина коридора может быть 
     | произвольной.
надо | Закрасить все клетки в коридоре
нач
закрасить
нц пока снизу свободно
вниз
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_101.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_1_A_101 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_1_A_101: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_1_A_101: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_1_A_101: {e}")


def test_robot9oge_1_B_102(tmp_path):
    """
    Тест для задачи: 1-B (ID: 102)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот находится в нижней клетке узкого 
     | вертикального коридора. Ширина коридора - 
     | одна клетка, длина коридора может быть 
     | произвольной.
надо | Закрасить все клетки в коридоре
нач
закрасить
нц пока сверху свободно
вверх
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_102.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_1_B_102 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_1_B_102: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_1_B_102: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_1_B_102: {e}")


def test_robot9oge_1_C_103(tmp_path):
    """
    Тест для задачи: 1-C (ID: 103)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот находится в одной из клеток узкого 
     | вертикального коридора. Ширина коридора - 
     | одна клетка, длина коридора может быть 
     | произвольной.
надо | Закрасить все клетки в коридоре
нач
нц пока сверху свободно
вверх
кц
закрасить
нц пока снизу свободно
вниз
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_103.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_1_C_103 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_1_C_103: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_1_C_103: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_1_C_103: {e}")


def test_robot9oge_1_D_104(tmp_path):
    """
    Тест для задачи: 1-D (ID: 104)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот находится в левой клетке узкого 
     | горизонтального коридора. Ширина коридора - 
     | одна клетка, длина коридора может быть 
     | произвольной.
надо | Закрасить все клетки в коридоре
нач
закрасить
нц пока справа свободно
вправо
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_104.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_1_D_104 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_1_D_104: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_1_D_104: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_1_D_104: {e}")


def test_robot9oge_1_E_105(tmp_path):
    """
    Тест для задачи: 1-E (ID: 105)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот находится в правой клетке узкого 
     | горизонтального коридора. Ширина коридора - 
     | одна клетка, длина коридора может быть 
     | произвольной.
надо | Закрасить все клетки в коридоре
нач
закрасить
нц пока слева свободно
влево
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_105.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_1_E_105 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_1_E_105: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_1_E_105: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_1_E_105: {e}")


def test_robot9oge_1_F_106(tmp_path):
    """
    Тест для задачи: 1-F (ID: 106)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот находится в одной из клеток узкого 
     | горизонтального коридора. Ширина коридора - 
     | одна клетка, длина коридора может быть 
     | произвольной.
надо | Закрасить все клетки в коридоре
нач
нц пока справа свободно
вправо
кц
закрасить
нц пока слева свободно
влево
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_106.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_1_F_106 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_1_F_106: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_1_F_106: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_1_F_106: {e}")


def test_robot9oge_2_A_201(tmp_path):
    """
    Тест для задачи: 2-A (ID: 201)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть одна горизонтальная 
     | стена неизвестной длины. Робот находится в 
     | одной из клеток над стеной.
надо | Закрасить все клетки, расположенные выше 
     | стены непосредственно над ней.
нач
нц пока снизу свободно
вниз
кц
нц пока не снизу свободно
вправо
кц
влево
нц пока не снизу свободно
закрасить
влево
кц 
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_201.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_2_A_201 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_2_A_201: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_2_A_201: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_2_A_201: {e}")


def test_robot9oge_2_B_202(tmp_path):
    """
    Тест для задачи: 2-B (ID: 202)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть одна горизонтальная 
     | стена неизвестной длины. Робот находится в 
     | одной из клеток над стеной.
надо | Закрасить все клетки, расположенные ниже 
     | стены непосредственно под ней.
нач
нц пока снизу свободно
вниз
кц
нц пока не снизу свободно
вправо
кц
вниз
влево
нц пока не сверху свободно
закрасить
влево
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_202.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_2_B_202 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_2_B_202: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_2_B_202: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_2_B_202: {e}")


def test_robot9oge_2_C_203(tmp_path):
    """
    Тест для задачи: 2-C (ID: 203)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть одна горизонтальная 
     | стена неизвестной длины. Робот находится в 
     | одной из клеток над стеной.
надо | Закрасить все клетки, расположенные ниже 
     | стены непосредственно под ней.
нач
нц пока сверху свободно
вверх
кц
нц пока не сверху свободно
вправо
кц
вверх
влево
нц пока не снизу свободно
закрасить
влево
кц 
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_203.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_2_C_203 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_2_C_203: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_2_C_203: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_2_C_203: {e}")


def test_robot9oge_2_D_204(tmp_path):
    """
    Тест для задачи: 2-D (ID: 204)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть одна горизонтальная 
     | стена неизвестной длины. Робот находится в 
     | одной из клеток под стеной.
надо | Закрасить все клетки, расположенные ниже 
     | стены непосредственно под ней.
нач
нц пока сверху свободно
вверх
кц
нц пока не сверху свободно
вправо
кц
влево
нц пока не сверху свободно
закрасить
влево
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_204.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_2_D_204 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_2_D_204: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_2_D_204: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_2_D_204: {e}")


def test_robot9oge_2_E_205(tmp_path):
    """
    Тест для задачи: 2-E (ID: 205)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть одна вертикальная 
     | стена неизвестной длины. Робот находится в 
     | одной из клеток справа от стены.
надо | Закрасить все клетки, расположенные с двух сторон 
     | рядом со стеной.
нач
нц пока слева свободно
влево
кц
нц пока не слева свободно
вниз
кц
вверх
нц пока не слева свободно
закрасить 
вверх
кц
влево
вниз
нц пока не справа свободно
закрасить
вниз
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_205.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_2_E_205 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_2_E_205: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_2_E_205: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_2_E_205: {e}")


def test_robot9oge_2_F_206(tmp_path):
    """
    Тест для задачи: 2-F (ID: 206)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть одна вертикальная 
     | стена неизвестной длины. Робот находится в 
     | одной из клеток слева от стены.
надо | Закрасить все клетки, расположенные с двух сторон 
     | рядом со стеной.
нач
нц пока справа свободно
вправо
кц
нц пока не справа свободно
вниз
кц
вверх
нц пока не справа свободно
закрасить 
вверх
кц
вправо
вниз
нц пока не слева свободно
закрасить
вниз
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_206.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_2_F_206 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_2_F_206: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_2_F_206: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_2_F_206: {e}")


def test_robot9oge_2_G_207(tmp_path):
    """
    Тест для задачи: 2-G (ID: 207)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть одна горизонтальная 
     | стена неизвестной длины. Робот находится в 
     | одной из клеток прямо над стеной.
надо | Закрасить все клетки, расположенные выше стены
     | на расстоянии одной пустой клетки.
нач
нц пока не снизу свободно
влево
кц
вправо
нц пока не снизу свободно
вверх
закрасить
вниз
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_207.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_2_G_207 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_2_G_207: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_2_G_207: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_2_G_207: {e}")


def test_robot9oge_3_A_301(tmp_path):
    """
    Тест для задачи: 3-A (ID: 301)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются две вертикальные стены 
     | одинаковой длины, расположенные точно одна напротив 
     | другой, и одна горизонтальная, соединяющая верхние
     | концы стен. Длина стен неизвестна. Расстояние между 
     | стенами неизвестно. Робот находится справа от 
     | первой стены в клетке, расположенной у её нижнего края.
надо | Закрасить все клетки самого верхнего ряда, 
     | расположенные между стенами.
нач
нц пока сверху свободно
вверх
кц
закрасить
нц пока справа свободно
вправо
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_301.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_3_A_301 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_3_A_301: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_3_A_301: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_3_A_301: {e}")


def test_robot9oge_3_B_302(tmp_path):
    """
    Тест для задачи: 3-B (ID: 302)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются две вертикальные стены 
     | одинаковой длины, расположенные точно одна напротив 
     | другой, и одна горизонтальная, соединяющая нижние концы
     | стен. Длина стен неизвестна. Расстояние между 
     | стенами неизвестно. Робот находится в одной из
     | клеток, расположенных между верхними концами
     | вертикальных стен. 
надо | Закрасить все клетки ниже горизонтальной стены, 
     | расположенные непосредственно под ней.
нач
нц пока справа свободно
вправо
кц
вверх
вправо
вниз
нц пока не слева свободно
вниз
кц
влево
нц пока не сверху свободно
закрасить
влево
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_302.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_3_B_302 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_3_B_302: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_3_B_302: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_3_B_302: {e}")


def test_robot9oge_3_C_303(tmp_path):
    """
    Тест для задачи: 3-C (ID: 303)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется горизонтальная стена. 
     | Длина стены неизвестна. От правого конца стены 
     | вниз отходит вертикальная стена также неизвестной 
     | длины. От нижнего конца этой стены отходит влево 
     | вторая горизонтальная стена неизвестной длины. 
     | Робот находится в клетке, расположенной снизу
     | от левого края первой горизонтальной стены. 
надо | Закрасить клетку, на которой находится Робот 
     | первоначально, и клетки, расположенные сверху 
     | от второй горизонтальной стены.
нач
закрасить
нц пока справа свободно
вправо
кц
нц пока снизу свободно
вниз
кц
нц пока не снизу свободно
закрасить
влево
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_303.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_3_C_303 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_3_C_303: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_3_C_303: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_3_C_303: {e}")


def test_robot9oge_3_D_304(tmp_path):
    """
    Тест для задачи: 3-D (ID: 304)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется горизонтальная стена. 
     | Длина стены неизвестна. От левого конца стены 
     | вниз отходит вертикальная стена также неизвестной
     | длины. От нижнего конца этой стены отходит вправо 
     | вторая горизонтальная стена неизвестной длины. 
     | Робот находится в клетке, расположенной сверху
     | от левого края второй горизонтальной стены. 

надо | Закрасить клетки, расположенные ниже первой 
     | горизонтальной стены, и угловую клетку, 
     | расположенную на пересечении вертикальной и 
     | первой горизонтальной стен.
нач
нц пока слева свободно
влево
кц
закрасить
нц пока сверху свободно
вверх
кц
нц пока не сверху свободно
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_304.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_3_D_304 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_3_D_304: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_3_D_304: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_3_D_304: {e}")


def test_robot9oge_3_E_305(tmp_path):
    """
    Тест для задачи: 3-E (ID: 305)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется горизонтальная стена. 
     | Длина стены неизвестна. От левого конца стены 
     | вниз отходит вертикальная стена также неизвестной
     | длины. От нижнего конца этой стены отходит вправо 
     | вторая горизонтальная стена неизвестной длины. 
     | Робот находится в клетке, расположенной сверху
     | от левого края второй горизонтальной стены. 

надо | Закрасить клетки, расположенные ниже первой 
     | горизонтальной стены, и угловую клетку, 
     | расположенную на пересечении вертикальной и 
     | первой горизонтальной стен.
нач
нц пока снизу свободно
вниз
кц
нц пока справа свободно
вправо
кц
нц пока не справа свободно
вверх
кц
вправо
нц пока снизу свободно
вниз
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_305.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_3_E_305 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_3_E_305: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_3_E_305: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_3_E_305: {e}")


def test_robot9oge_3_F_306(tmp_path):
    """
    Тест для задачи: 3-F (ID: 306)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется стена, длины отрезков 
     | cтены неизвестны. Стена состоит из одного 
     | вертикального и трёх горизонтальных отрезков 
     | (отрезки стены расположены буквой "Е"). Все отрезки 
     | неизвестной длины. Робот находится в клетке, расположенной 
     | непосредственно снизу от правого конца нижнего 
     | горизонтального отрезка. 
надо | Закрасить все клетки, расположенные непосредственно 
     | сверху от верхнего горизонтального отрезка.
нач
нц пока не сверху свободно
влево
кц
вверх
нц пока не справа свободно
вверх
кц
вправо
нц пока не снизу свободно
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_306.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_3_F_306 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_3_F_306: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_3_F_306: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_3_F_306: {e}")


def test_robot9oge_4_A_401(tmp_path):
    """
    Тест для задачи: 4-A (ID: 401)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются 4 стены, расположенные 
     | в форме прямоугольника. Длины вертикальных и 
     | горизонтальных стен неизвестны. Робот находится в 
     | клетке, расположенной в левом верхнем углу 
     | прямоугольника. 
надо | Закрасить все клетки расположенные с внутренней 
     | стороны верхней и нижней стен. 
нач
закрасить
нц пока справа свободно
вправо
закрасить
кц
нц пока снизу свободно
вниз
кц
закрасить
нц пока слева свободно
влево
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_401.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_4_A_401 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_4_A_401: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_4_A_401: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_4_A_401: {e}")


def test_robot9oge_4_B_402(tmp_path):
    """
    Тест для задачи: 4-B (ID: 402)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются 4 стены, расположенные 
     | в форме прямоугольника. Длины вертикальных и 
     | горизонтальных стен неизвестны. Робот находится в 
     | клетке, расположенной в правом верхнем углу 
     | прямоугольника. 
надо | Закрасить все клетки расположенные с внутренней 
     | стороны верхней и левой стен. 
нач
нц пока снизу свободно
вниз
кц
закрасить
нц пока слева свободно
влево
закрасить
кц
нц пока сверху свободно
вверх
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_402.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_4_B_402 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_4_B_402: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_4_B_402: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_4_B_402: {e}")


def test_robot9oge_4_C_403(tmp_path):
    """
    Тест для задачи: 4-C (ID: 403)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется вертикальная стена. 
     | Длина стены неизвестна. От верхнего конца стены 
     | вправо отходит горизонтальная стена также неизвестной 
     | длины. Робот находится в клетке, расположенной слева 
     | от нижнего края вертикальной стены. 
надо | Закрасить все клетки расположенные левее вертикальной 
     | стены и выше горизонтальной стены и прилегающие к ним. 
нач
нц пока не справа свободно
закрасить
вверх
кц
закрасить
вправо
нц пока не снизу свободно
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_403.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_4_C_403 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_4_C_403: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_4_C_403: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_4_C_403: {e}")


def test_robot9oge_4_D_404(tmp_path):
    """
    Тест для задачи: 4-D (ID: 404)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется стена. Стена состоит 
     | из трёх последовательных отрезков: вправо, вниз, 
     | вправо, все отрезки неизвестной длины. Робот находится 
     | в клетке, расположенной непосредственно сверху 
     | левого конца первого отрезка. 
надо | Закрасить все клетки расположенные непосредственно 
     | правее второго отрезка и над третьим. 
нач
нц пока не снизу свободно
вправо
кц
нц пока снизу свободно
вниз
закрасить
кц
вправо
нц пока не снизу свободно
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_404.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_4_D_404 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_4_D_404: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_4_D_404: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_4_D_404: {e}")


def test_robot9oge_4_E_405(tmp_path):
    """
    Тест для задачи: 4-E (ID: 405)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется стена. Стена состоит 
     | из трёх последовательных отрезков: вправо, вниз, 
     | вправо, все отрезки неизвестной длины. Робот находится 
     | в клетке, расположенной непосредственно сверху 
     | левого конца первого отрезка. 
надо | Закрасить все клетки расположенные непосредственно 
     | правее второго отрезка и над третьим. 
нач
нц пока не сверху свободно
вправо
кц
влево
нц пока не сверху свободно
закрасить
влево
кц
вправо
нц пока снизу свободно
вниз
кц
влево
вниз
вправо
нц пока не сверху свободно
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_405.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_4_E_405 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_4_E_405: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_4_E_405: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_4_E_405: {e}")


def test_robot9oge_4_F_406(tmp_path):
    """
    Тест для задачи: 4-F (ID: 406)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется вертикальная стена. 
     | Длина стены неизвестна. От нижнего конца стены вправо 
     | отходит горизонтальная стена также неизвестной длины. 
     | Робот находится в клетке, расположенной слева от 
     | вертикальной стены и выше горизонтальной стены.
надо | Закрасить все клетки, расположенные правее 
     | вертикальной стены, выше горизонтальной стены и 
     | примыкающие к ним, кроме угловой клетки. 
нач
нц пока справа свободно
вправо
кц
нц пока не справа свободно
вверх
кц
вправо
вниз
нц пока снизу свободно
закрасить
вниз
кц
вправо
нц пока не снизу свободно
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_406.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_4_F_406 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_4_F_406: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_4_F_406: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_4_F_406: {e}")


def test_robot9oge_5_A_501(tmp_path):
    """
    Тест для задачи: 5-A (ID: 501)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть горизонтальная и вертикальная стены. 
     | Правый конец горизонтальной стены соединён с нижним 
     | концом вертикальной стены. Длины стен неизвестны. 
     | В каждой стене есть ровно один проход, точное место 
     | прохода и его ширина неизвестны. Робот находится 
     | в клетке, расположенной непосредственно слева от 
     | горизонтальной стены у её верхнего конца.
надо | Закрасить все клетки, расположенные 
     | непосредственно слева от вертикальной стены и выше 
     | горизонтальной стены. Проходы должны остаться 
     | незакрашенными. 
нач
нц пока не справа свободно
закрасить
вниз
кц
нц пока справа свободно
вниз
кц
закрасить
нц пока снизу свободно
вниз
закрасить
кц
влево
нц пока не снизу свободно
закрасить
влево
кц
нц пока снизу свободно
влево
кц
нц пока не снизу свободно
закрасить
влево
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_501.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_5_A_501 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_5_A_501: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_5_A_501: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_5_A_501: {e}")


def test_robot9oge_5_B_502(tmp_path):
    """
    Тест для задачи: 5-B (ID: 502)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть горизонтальная и вертикальная стены. 
     | Правый конец горизонтальной стены соединён с верхним 
     | концом вертикальной стены. Длины стен неизвестны. 
     | В каждой стене есть ровно один проход, точное место 
     | прохода и его ширина неизвестны. Робот находится 
     | в угловой клетке.
надо | Закрасить все клетки, расположенные 
     | непосредственно сверху от горизонтальной стены и справа 
     | от вертикальной стены. Проходы должны остаться 
     | незакрашенными. 
нач
нц пока не сверху свободно
влево
кц
нц пока сверху свободно
влево
кц
нц пока не сверху свободно
влево
кц
вверх
вправо
нц пока не снизу свободно
закрасить
вправо
кц
нц пока снизу свободно
вправо
кц
нц пока не снизу свободно
закрасить
вправо
кц
вниз
нц пока не слева свободно
закрасить
вниз
кц
нц пока слева свободно
вниз
кц
нц пока не слева свободно
закрасить
вниз
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_502.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_5_B_502 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_5_B_502: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_5_B_502: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_5_B_502: {e}")


def test_robot9oge_5_C_503(tmp_path):
    """
    Тест для задачи: 5-C (ID: 503)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть горизонтальная и вертикальная стены. 
     | Левый конец горизонтальной стены соединён с нижним 
     | концом вертикальной стены. Длины стен неизвестны. 
     | В вертикальной стене есть ровно один проход, точное место 
     | прохода и его ширина неизвестны. Робот находится 
     | в клетке, расположенной непосредственно под 
     | горизонтальной стеной у её правого конца.
надо | Закрасить все клетки, расположенные 
     | непосредственно слева и справа от вертикальной стены.
     | Проход должен остаться незакрашенным. 
нач
нц пока не сверху свободно
влево
кц
вверх
нц пока не справа свободно
закрасить
вверх
кц
нц пока справа свободно
вверх
кц
нц пока не справа свободно
закрасить
вверх
кц
вправо
вниз
нц пока не слева свободно
закрасить
вниз
кц
нц пока слева свободно
вниз
кц
вверх
нц пока снизу свободно
вниз
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_503.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_5_C_503 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_5_C_503: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_5_C_503: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_5_C_503: {e}")


def test_robot9oge_5_D_504(tmp_path):
    """
    Тест для задачи: 5-D (ID: 504)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле есть горизонтальная и вертикальная стены. 
     | Левый конец горизонтальной стены соединён с верхним 
     | концом вертикальной стены. Длины стен неизвестны. 
     | В горизонтальной стене есть ровно один проход, точное место 
     | прохода и его ширина неизвестны. Робот находится 
     | в клетке, расположенной непосредственно справа 
     | от вертикальной стены у её нижнего конца.
надо | Закрасить все клетки, расположенные 
     | непосредственно сверху и снизу от горизонтальной стены.
     | Проход должен остаться незакрашенным. 
нач
нц пока сверху свободно
вверх
кц
нц пока не сверху свободно
закрасить
вправо
кц
нц пока сверху свободно
вправо
кц
нц пока не сверху свободно
закрасить
вправо
кц
вверх
влево
нц пока не снизу свободно
закрасить
влево
кц
нц пока снизу свободно
влево
кц
нц пока не снизу свободно
закрасить
влево
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_504.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_5_D_504 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_5_D_504: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_5_D_504: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_5_D_504: {e}")


def test_robot9oge_5_E_505(tmp_path):
    """
    Тест для задачи: 5-E (ID: 505)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется стена, длины отрезков 
     | стены неизвестны. Стена состоит из двух вертикальных 
     | и соединяющего их горизонтального отрезков (отрезки 
     | стены расположены "буквой П"). В горизонтальном участке 
     | есть ровно один проход, место и длина прохода 
     | неизвестны. Робот находится в клетке, расположенной 
     | над левым концом горизонтального отрезка стены.
надо | Закрасить все клетки, расположенные 
     | над горизонтальным отрезком стены справа от прохода, 
     | и все клетки, расположенные с внешней стороны от 
     | правого вертикального участка стены. 
нач
нц пока не снизу свободно
вправо
кц
нц пока снизу свободно
вправо
кц
нц пока не снизу свободно
закрасить
вправо
кц
вниз
нц пока не слева свободно
закрасить
вниз
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_505.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_5_E_505 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_5_E_505: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_5_E_505: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_5_E_505: {e}")


def test_robot9oge_5_F_506(tmp_path):
    """
    Тест для задачи: 5-F (ID: 506)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются четыре стены, 
     | соединённые между собой, которые образуют прямоугольник. 
     | Длины стен неизвестны. В левой вертикальной стене есть 
     | ровно один проход, в нижней горизонтальной стене также 
     | есть ровно один проход. Проход не может примыкать к углу 
     | прямоугольника. Точные места проходов и ширина проходов 
     | неизвестны. Робот находится около нижнего конца левой 
     | вертикальной стены, снаружи прямоугольника и выше нижней стены.
надо | Закрасить все клетки, расположенные вдоль стен прямоугольника 
     | с внутренней стороны. Проходы должны остаться незакрашенными. 
нач
нц пока не справа свободно
вверх
кц
вправо
нц пока слева свободно
вверх
кц
нц пока сверху свободно
закрасить
вверх
кц
нц пока справа свободно
закрасить
вправо
кц
нц пока снизу свободно
закрасить
вниз
кц
нц пока не снизу свободно
закрасить
влево
кц
нц пока снизу свободно
влево
кц
нц пока слева свободно
закрасить
влево
кц
нц пока не слева свободно
закрасить
вверх 
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_506.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_5_F_506 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_5_F_506: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_5_F_506: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_5_F_506: {e}")


def test_robot9oge_6_A_601(tmp_path):
    """
    Тест для задачи: 6-A (ID: 601)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется лестница. Сначала лестница 
     | слева направо спускается вниз, затем поднимается вверх. 
     | Высота каждой ступени - одна клетка, ширина - две клетки. 
     | Робот находится на первой ступеньке лестницы, в левой клетке. 
     | Количество ступеней, ведущих вниз, и количество ступеней, 
     | ведущих вверх, неизвестно.
надо | Закрасить все клетки, расположенные непосредственно над 
     | ступенями лестницы. 
нач
нц пока справа свободно
закрасить
вправо
закрасить
если справа свободно
то
вправо
вниз
все
кц 
нц пока не справа свободно
вверх
вправо
закрасить
вправо
закрасить
кц
кон
|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_601.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_6_A_601 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_6_A_601: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_6_A_601: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_6_A_601: {e}")


def test_robot9oge_6_B_602(tmp_path):
    """
    Тест для задачи: 6-B (ID: 602)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется лестница. Сначала лестница 
     | слева направо спускается вниз, затем поднимается вверх. 
     | Высота каждой ступени - одна клетка, ширина - две клетки. 
     | Робот находится над самой правой ступенькой лестницы, 
     | в правой клетке. Количество ступеней, ведущих вниз, 
     | и количество ступеней, ведущих вверх, неизвестно.
надо | Закрасить все клетки, расположенные непосредственно под 
     | ступенями лестницы. 
нач
вправо
вниз
влево
закрасить
влево
закрасить
нц пока не слева свободно
вниз
влево
закрасить
влево
закрасить
кц
влево
вверх
нц пока не справа свободно
закрасить
влево 
закрасить
влево
вверх
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_602.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_6_B_602 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_6_B_602: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_6_B_602: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_6_B_602: {e}")


def test_robot9oge_6_C_603(tmp_path):
    """
    Тест для задачи: 6-C (ID: 603)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется лестница. Сначала лестница 
     | слева направо спускается вниз, затем поднимается вверх. 
     | Высота каждой ступени - одна клетка, ширина - две клетки. 
     | Робот находится над самой правой ступенькой лестницы, 
     | в правой клетке. Количество ступеней, ведущих вниз, 
     | и количество ступеней, ведущих вверх, неизвестно.
надо | Закрасить все клетки, расположенные непосредственно под 
     | ступенями лестницы. 
нач
нц пока снизу свободно
вниз
влево
влево
кц
нц пока не слева свободно
закрасить
вправо
закрасить
вправо
вниз
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_603.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_6_C_603 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_6_C_603: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_6_C_603: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_6_C_603: {e}")


def test_robot9oge_6_D_604(tmp_path):
    """
    Тест для задачи: 6-D (ID: 604)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется лестница. Сначала лестница 
     | спускается вниз сплева направо, затем спускается вниз 
     | справа налево. Высота каждой ступени - одна клетка, 
     | ширина - две клетки. Робот находится слева от верхней 
     | ступени лестницы. Количество ступенек, ведущих вправо, 
     | и количество ступенек, ведущих влево, неизвестно.
надо | Закрасить все клетки, расположенные непосредственно под 
     | ступенями лестницы, спускающейся справа налево. 
нач
вверх
вправо
вниз
нц пока не снизу свободно
вправо
вправо
вниз
кц
нц пока не слева свободно
вниз
влево
закрасить
влево
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_604.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_6_D_604 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_6_D_604: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_6_D_604: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_6_D_604: {e}")


def test_robot9oge_6_E_605(tmp_path):
    """
    Тест для задачи: 6-E (ID: 605)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется лестница. Сначала лестница 
     | поднимается вверх слева направо, потом опускается вниз 
     | также слева направо. Правее спуска лестница переходит в 
     | горизонтальную стену. Высота каждой ступени — 1 клетка, 
     | ширина — 1 клетка. Количество ступенек, ведущих вверх, 
     | и количество ступенек, ведущих вниз, неизвестно. Между 
     | спуском и подъемом ширина площадки — 1 клетка. Робот 
     | находится в клетке, расположенной в начале подъёма.
надо | Закрасить все клетки, расположенные непосредственно над 
     | лестницей, и клетки, которые касаются углов лестницы. 
нач
нц пока не справа свободно
закрасить
вверх
закрасить
вправо
кц
закрасить
вправо
нц пока снизу свободно
закрасить
вниз
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_605.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_6_E_605 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_6_E_605: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_6_E_605: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_6_E_605: {e}")


def test_robot9oge_6_F_606(tmp_path):
    """
    Тест для задачи: 6-F (ID: 606)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется лестница. Сначала лестница 
     | спускается вниз слева направо, потом поднимается вверх 
     | также слева направо. Левее спуска и правее подъёма лестница  
     | переходит в горизонтальную стену. Высота каждой ступени — 1 клетка, 
     | ширина — 1 клетка. Количество ступенек, ведущих вверх, 
     | и количество ступенек, ведущих вниз, неизвестно. Между 
     | спуском и подъемом ширина площадки — 1 клетка. Робот 
     | находится в клетке, расположенной в конце подъёма.
надо | Закрасить все клетки, расположенные непосредственно над 
     | лестницей, и клетки, которые касаются углов лестницы. 
нач
нц пока слева свободно
влево
закрасить
вниз
закрасить
кц
вверх
влево
нц пока не слева свободно
закрасить
вверх
закрасить
влево
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_606.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_6_F_606 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_6_F_606: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_6_F_606: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_6_F_606: {e}")


def test_robot9oge_7_A_701(tmp_path):
    """
    Тест для задачи: 7-A (ID: 701)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются четыре стены, соединённые между 
     | собой, которые образуют прямоугольник. Длины стен неизвестны. 
     | В левой вертикальной стене есть ровно один проход. Проход 
     | не может примыкать к углу прямоугольника. Точное место 
     | и ширина прохода неизвестны. Робот находится около 
     | нижнего конца левой вертикальной стены, снаружи 
     | прямоугольника и выше нижней стены.
надо | Закрасить все клетки, расположенные внутри прямоугольника 
     | рядом со стенами и строки, которые примыкают к проходу. 
нач
нц пока не справа свободно
вверх
кц
вправо
вниз
нц пока справа свободно
вправо
закрасить
кц
нц пока слева свободно
влево
кц
нц пока снизу свободно
закрасить
вниз
кц
нц пока справа свободно
закрасить
вправо
кц
нц пока сверху свободно
закрасить
вверх
кц
нц пока слева свободно
закрасить
влево
кц
нц пока не слева свободно
закрасить
вниз
кц
вверх
нц пока справа свободно
вправо
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_701.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_7_A_701 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_7_A_701: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_7_A_701: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_7_A_701: {e}")


def test_robot9oge_7_B_702(tmp_path):
    """
    Тест для задачи: 7-B (ID: 702)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются четыре стены, соединённые между 
     | собой, которые образуют прямоугольник. Длины стен неизвестны. 
     | В правой вертикальной стене есть ровно один проход, в верхней 
     | горизонтальной стене также есть ровно один проход. Проход 
     | не может примыкать к углу прямоугольника. Точные места 
     | проходов и ширина проходов неизвестны. Робот находится около 
     | нижнего конца левой вертикальной стены, снаружи 
     | прямоугольника и выше нижней стены.
надо | Закрасить все клетки, расположенные вдоль стен прямоугольника 
     | с внешней стороны, включая угловые клетки. Проходы должны остаться незакрашенными. 
нач
нц пока не справа свободно
вниз
кц
вверх
нц пока не справа свободно
закрасить
вверх
кц
закрасить
вправо
нц пока не снизу свободно
закрасить
вправо
кц
нц пока снизу свободно
вправо
кц
нц пока не снизу свободно
закрасить
вправо
кц
закрасить
вниз
нц пока не слева свободно
закрасить
вниз
кц
нц пока слева свободно
вниз
кц
нц пока не слева свободно
закрасить
вниз
кц
закрасить
влево
нц пока не сверху свободно
закрасить
влево
кц
закрасить
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_702.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_7_B_702 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_7_B_702: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_7_B_702: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_7_B_702: {e}")


def test_robot9oge_7_C_703(tmp_path):
    """
    Тест для задачи: 7-C (ID: 703)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеются четыре стены, соединённые между 
     | собой, которые образуют прямоугольник. Длины стен неизвестны. 
     | В правой вертикальной стене есть ровно один проход, в верхней 
     | горизонтальной стене также есть ровно один проход. Проход 
     | не может примыкать к углу прямоугольника. Точные места 
     | проходов и ширина проходов неизвестны. Робот находится около 
     | нижнего конца левой вертикальной стены, снаружи 
     | прямоугольника и выше нижней стены.
надо | Закрасить все клетки, расположенные вдоль стен прямоугольника 
     | с внешней стороны, включая угловые клетки. Проходы должны остаться незакрашенными. 
нач
нц пока справа свободно
закрасить
вправо
кц
нц пока снизу свободно
закрасить
вниз
кц
закрасить
нц пока не снизу свободно
влево
кц
вниз
нц пока не справа свободно
закрасить
вниз
кц
закрасить
вправо
нц пока не сверху свободно
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_703.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_7_C_703 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_7_C_703: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_7_C_703: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_7_C_703: {e}")


def test_robot9oge_7_D_704(tmp_path):
    """
    Тест для задачи: 7-D (ID: 704)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется стена, состоящая из 5 последовательных 
     | отрезков, расположенных змейкой: вниз, вправо, вверх, вправо, 
     | вниз, все отрезки неизвестной длины. Робот находится в самой 
     | нижней клетке непосредственно справа от правой горизонтальной стены.
надо | Закрасить все клетки, расположенные справ от первого и выше 
     | второго отрезков стены и ниже четвёртого и слева от пятого 
     | отрезков стены. 
нач
вниз
влево
нц пока сверху свободно
вверх
закрасить
кц
нц пока слева свободно
влево
закрасить
кц
нц пока не слева свободно
вниз
кц
влево
нц пока не сверху свободно
влево
кц
вверх
нц пока не справа свободно
вверх
кц
вправо
нц пока снизу свободно
вниз
закрасить
кц
нц пока справа свободно
вправо
закрасить
кц 
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_704.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_7_D_704 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_7_D_704: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_7_D_704: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_7_D_704: {e}")


def test_robot9oge_7_E_705(tmp_path):
    """
    Тест для задачи: 7-E (ID: 705)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется две горизонтальные стены,
     | которные соединяются вертикальной стеной.
     | Робот находится в одной из клеток под нижней горизнтальной
     | стеной. Длины всех стен неизвестны.
надо | Закрасить все клетки, расположенные слева и справа от 
     | вертикальной стенки, над верхней горизонтальной стеной и 
     | под нижней горизонтальной стеной. 
нач
нц пока не сверху свободно
влево
кц
вправо
нц пока не сверху свободно
закрасить
вправо
кц
вверх
нц пока слева свободно
влево
кц
закрасить
нц пока сверху свободно
вверх
закрасить
кц
нц пока не сверху свободно
вправо
кц
вверх
влево
нц пока не снизу свободно
закрасить
влево
кц
вниз
нц пока справа свободно
вправо
кц
закрасить
нц пока снизу свободно
вниз
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_705.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_7_E_705 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_7_E_705: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_7_E_705: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_7_E_705: {e}")


def test_robot9oge_7_F_706(tmp_path):
    """
    Тест для задачи: 7-F (ID: 706)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | На бесконечном поле имеется две вертикальные стены,
     | которные соединяются горизонтальной стеной.
     | Робот находится в одной из клеток под вертикальной
     | стеной. Длины всех стен неизвестны.
надо | Закрасить все клетки, расположенные слева и справа от 
     | вертикальных стен. 
нач
нц пока слева свободно
влево
кц
нц пока не слева свободно
закрасить
вниз
кц
влево
вверх
нц пока не справа свободно
закрасить
вверх
кц
вправо
нц пока снизу свободно
вниз
закрасить
кц
нц пока справа свободно
вправо
кц
нц пока не справа свободно
закрасить
вверх
кц
вправо
вниз
нц пока не слева свободно
закрасить
вниз
кц
влево
нц пока сверху свободно
вверх
закрасить
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_706.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_7_F_706 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_7_F_706: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_7_F_706: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_7_F_706: {e}")


def test_robot9oge_7_G_707(tmp_path):
    """
    Тест для задачи: 7-G (ID: 707)
    Курс: robot9oge
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | (Н.Е. Леко) На бесконечном поле есть две горизонтальные стены,
     | расположенные друг под другом и отстоящие на расстояние,
     | равное одной клетке, и две вертикальные стены.
     | Левый конец верхней горизонтальной стены соединен с нижним
     | концом одной из вертикальных стен.
     | Правый конец нижней горизонтальной стены соединён с верхним
     | концом второй вертикальной стены. Длины стен неизвестны.
     | Робот находится в клетке, расположенной непосредственно слева
     | от верхнего края левой вертикальной стены.
надо | Закрасить все клетки, расположенные между 
     | двумя горизонтальными стенами (точно известно, что хотя бы
     | одна такая клетка есть). 
нач
нц пока справа стена
вниз
кц
вправо
нц пока снизу свободно
вправо
кц
нц пока сверху стена
закрасить
вправо
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
@@размер поля(ширина, высота)
нц для x от 1 до ширина
нц для y от 1 до высота
если @@метка(x, y) и не @@закрашена(x, y)
то
вывод "Задание не выполнено: не закрашена помеченная клетка.", нс
знач := 0
выход
все
если @@закрашена(x, y) и не @@метка(x, y)
то
вывод "Задание не выполнено: закрашена непомеченная клетка.", нс
знач := 0
выход
все
кц
если знач = 0
то
выход
все
кц
если знач = 10 то
вывод "Задание выполнено успешно."
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_707.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robot9oge_7_G_707 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robot9oge_7_G_707: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robot9oge_7_G_707: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robot9oge_7_G_707: {e}")

