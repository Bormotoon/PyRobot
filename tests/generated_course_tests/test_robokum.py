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

# Автогенерированные тесты для курса: robokum
# Сгенерировано: 2025-06-09 11:49:00

def test_robokum_1_A_101(tmp_path):
    """
    Тест для задачи: 1-A (ID: 101)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
нач
вверх
вверх
вверх
влево
влево
закрасить
влево
закрасить
влево
закрасить
влево
вниз
вправо
закрасить
вправо
закрасить
вправо
закрасить
влево
влево
влево
вверх
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_1_A_101 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_1_A_101: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_1_A_101: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_1_A_101: {e}")


def test_robokum_1_B_102(tmp_path):
    """
    Тест для задачи: 1-B (ID: 102)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
нач
вниз
вниз
вправо
вправо
вправо
вниз
влево
влево
закрасить
влево
закрасить
влево
закрасить
вправо
вниз
вниз
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_1_B_102 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_1_B_102: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_1_B_102: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_1_B_102: {e}")


def test_robokum_1_C_103(tmp_path):
    """
    Тест для задачи: 1-C (ID: 103)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
нач
вверх
вверх
вверх
влево
закрасить
вниз
закрасить
вверх
вправо
вправо
вниз
закрасить
вверх
закрасить
влево
вниз
вниз
влево
влево
вверх
вверх
вверх
закрасить
вправо
вправо
закрасить
вправо
вправо
закрасить
вниз
вниз

кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_1_C_103 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_1_C_103: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_1_C_103: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_1_C_103: {e}")


def test_robokum_1_D_104(tmp_path):
    """
    Тест для задачи: 1-D (ID: 104)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
нач
вниз
влево
влево
вниз
вниз
вниз
вправо
вправо
вправо
закрасить
вверх
вверх
закрасить
влево
влево
закрасить
вниз
вправо
закрасить
влево
вверх
вправо
вправо
вниз
вниз
влево
влево
влево
вниз
вниз
вниз
вниз
вправо
вправо
вправо
вправо
вверх
вверх
вверх
влево
влево
влево
закрасить
вниз
вниз
закрасить
вправо
вправо
закрасить
вверх
влево
закрасить
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_1_D_104 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_1_D_104: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_1_D_104: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_1_D_104: {e}")


def test_robokum_2_A_201(tmp_path):
    """
    Тест для задачи: 2-A (ID: 201)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
влево
нц 6 раз
влево
закрасить
кц
вниз
вниз
нц 5 раз
закрасить
вправо
кц
вниз
влево
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_2_A_201 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_2_A_201: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_2_A_201: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_2_A_201: {e}")


def test_robokum_2_B_202(tmp_path):
    """
    Тест для задачи: 2-B (ID: 202)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
нц 7 раз
влево
закрасить
кц
нц 6 раз
вправо
кц
нц 5 раз
вниз
закрасить
кц
нц 6 раз
влево
закрасить
кц
нц 7 раз
вправо
кц
вниз
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_2_B_202 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_2_B_202: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_2_B_202: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_2_B_202: {e}")


def test_robokum_2_C_203(tmp_path):
    """
    Тест для задачи: 2-C (ID: 203)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
нц 3 раз
вправо
кц
нц 3 раз
вниз
закрасить
влево
кц
вниз
вниз
нц 5 раз
вправо
закрасить
вверх
кц
вправо
вправо
нц 7 раз
вниз
закрасить
влево
кц
вниз
вниз
нц 9 раз
вправо
закрасить
вверх
кц
нц 9 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_2_C_203 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_2_C_203: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_2_C_203: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_2_C_203: {e}")


def test_robokum_2_D_204(tmp_path):
    """
    Тест для задачи: 2-D (ID: 204)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
нц 8 раз
вниз
влево
вверх
закрасить
кц
влево
закрасить
нц 8 раз
вправо
вниз
влево
закрасить
кц
вниз
закрасить
нц 8 раз
вверх
вправо
вниз
закрасить
кц
вправо
закрасить
нц 8 раз
влево
вверх
вправо
закрасить
кц
вверх
закрасить
вниз
влево
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_2_D_204 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_2_D_204: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_2_D_204: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_2_D_204: {e}")


def test_robokum_3_A_301(tmp_path):
    """
    Тест для задачи: 3-A (ID: 301)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
нц 3 раз
вверх
кц
нц 6 раз
вправо
закрасить
влево
вниз
кц
нц 3 раз
вправо
кц
нц 3 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_3_A_301 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_3_A_301: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_3_A_301: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_3_A_301: {e}")


def test_robokum_3_B_302(tmp_path):
    """
    Тест для задачи: 3-B (ID: 302)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
нц 6 раз
влево
вниз
закрасить
кц
влево
вниз
нц 7 раз
вправо
кц
нц 6 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_3_B_302 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_3_B_302: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_3_B_302: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_3_B_302: {e}")


def test_robokum_3_C_303(tmp_path):
    """
    Тест для задачи: 3-C (ID: 303)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
вправо
нц 6 раз
вниз
закрасить
вверх
вправо
вниз
кц
нц 2 раз
вниз
кц
влево
нц 6 раз
вверх
закрасить
вниз
влево
вверх
кц
вверх
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_3_C_303 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_3_C_303: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_3_C_303: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_3_C_303: {e}")


def test_robokum_3_D_304(tmp_path):
    """
    Тест для задачи: 3-D (ID: 304)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте цикл "N раз"
нач
вниз
нц 4 раз
вправо
закрасить
вправо
закрасить
вниз
закрасить
влево
закрасить
вправо
вверх
влево
влево
вниз
вниз
вправо
кц
нц 3 раз
вправо
кц
нц 4 раз
вверх
закрасить
влево
закрасить
вверх
закрасить
вправо
закрасить
влево
кц
вверх
нц 3 раз
влево
кц
вниз
вниз
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_3_D_304 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_3_D_304: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_3_D_304: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_3_D_304: {e}")


def test_robokum_4_A_401(tmp_path):
    """
    Тест для задачи: 4-A (ID: 401)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте вложенный цикл "N раз"
нач
влево
нц 4 раз
вверх
нц 7 раз
вправо
закрасить
кц
нц 7 раз
влево
кц
вверх
кц
вниз
нц 8 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_4_A_401 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_4_A_401: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_4_A_401: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_4_A_401: {e}")


def test_robokum_4_B_402(tmp_path):
    """
    Тест для задачи: 4-B (ID: 402)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте вложенный цикл "N раз"
нач
вправо
нц 4 раз
нц 6 раз
закрасить
вниз
кц
нц 5 раз
вверх
кц
вправо
кц
нц 4 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_4_B_402 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_4_B_402: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_4_B_402: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_4_B_402: {e}")


def test_robokum_4_C_403(tmp_path):
    """
    Тест для задачи: 4-C (ID: 403)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте вложенный цикл "N раз"
нач
вниз
вправо
нц 3 раз
вверх
нц 3 раз
влево
влево
закрасить
влево
закрасить
вверх
закрасить
вниз
кц
вверх
вверх
нц 9 раз
вправо
кц
кц
нц 10 раз
влево
кц
вниз
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_4_C_403 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_4_C_403: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_4_C_403: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_4_C_403: {e}")


def test_robokum_4_D_404(tmp_path):
    """
    Тест для задачи: 4-D (ID: 404)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести робота на Базу.
| Используйте вложенный цикл "N раз"
нач
нц 9 раз
влево
кц
нц 3 раз
нц 8 раз
вниз
закрасить
вниз
закрасить
вверх
вверх
вправо
кц
нц 3 раз
вниз
кц
нц 8 раз
влево
кц
кц
нц 8 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_4_D_404 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_4_D_404: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_4_D_404: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_4_D_404: {e}")


def test_robokum_5_A_501(tmp_path):
    """
    Тест для задачи: 5-A (ID: 501)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у левой стенки ограды.
| Длины стенок неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока снизу свободно
вниз
кц
закрасить
нц пока справа свободно
вправо
кц
закрасить
нц пока справа стена
вверх
кц
вниз
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_5_A_501 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_5_A_501: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_5_A_501: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_5_A_501: {e}")


def test_robokum_5_B_502(tmp_path):
    """
    Тест для задачи: 5-B (ID: 502)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у левой стенки поля.
| Длины стенок неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока сверху свободно
вверх
кц
закрасить
нц пока снизу свободно
вниз
кц
закрасить
нц пока справа свободно
вправо
кц
закрасить
нц пока сверху свободно
вверх
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_5_B_502 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_5_B_502: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_5_B_502: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_5_B_502: {e}")


def test_robokum_5_C_503(tmp_path):
    """
    Тест для задачи: 5-C (ID: 503)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот где-то на поле.
| Размеры поля неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока снизу свободно
вниз
кц
нц пока справа свободно
вправо
кц
нц пока сверху свободно
вверх
закрасить
кц
нц пока слева свободно
влево
закрасить
кц
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_5_C_503 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_5_C_503: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_5_C_503: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_5_C_503: {e}")


def test_robokum_5_D_504(tmp_path):
    """
    Тест для задачи: 5-D (ID: 504)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит под прямоугольной оградой.
| Длины стенок неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока сверху свободно
вверх
кц
нц пока сверху стена
вправо
кц
закрасить
влево
нц пока сверху стена
закрасить
влево
кц
закрасить
вверх
нц пока справа стена
закрасить
вверх
кц
закрасить
вправо
нц пока снизу стена
закрасить
вправо
кц
закрасить
вниз
нц пока слева стена
закрасить
вниз
кц
нц пока снизу свободно
вниз
кц
нц пока справа свободно
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_5_D_504 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_5_D_504: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_5_D_504: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_5_D_504: {e}")


def test_robokum_6_A_601(tmp_path):
    """
    Тест для задачи: 6-A (ID: 601)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у левого края поля.
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока сверху свободно
вверх
кц
нц пока справа свободно
если сверху стена
то
закрасить
иначе
нц 2 раз
вверх
закрасить
кц
нц 2 раз
вниз
кц
все
вправо
кц
закрасить
вниз
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_6_A_601 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_6_A_601: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_6_A_601: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_6_A_601: {e}")


def test_robokum_6_B_602(tmp_path):
    """
    Тест для задачи: 6-B (ID: 602)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у входа в коридопр..
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока справа свободно
вправо
закрасить
если сверху свободно
то
вверх
закрасить
вниз
все
если снизу свободно
то
вниз
закрасить
вверх
все
кц
нц пока слева свободно
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_6_B_602 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_6_B_602: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_6_B_602: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_6_B_602: {e}")


def test_robokum_6_C_603(tmp_path):
    """
    Тест для задачи: 6-C (ID: 603)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у входа в коридопр..
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока справа свободно
вправо
закрасить
если сверху свободно
то
нц 2 раз
вверх
закрасить
кц
вниз
вниз
все
если снизу свободно
то
вниз
закрасить
вверх
все
кц
нц пока слева свободно
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_6_C_603 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_6_C_603: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_6_C_603: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_6_C_603: {e}")


def test_robokum_6_D_604(tmp_path):
    """
    Тест для задачи: 6-D (ID: 604)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у входа в коридопр..
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока".
нач
нц пока справа свободно
вправо
закрасить
если сверху свободно
то
вверх
закрасить
если сверху свободно
то
вверх
закрасить
вниз
все
вниз
все
если снизу свободно
то
вниз
закрасить
если снизу свободно
то
вниз
закрасить
вверх
все
вверх
все
кц
нц пока слева свободно
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_6_D_604 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_6_D_604: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_6_D_604: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_6_D_604: {e}")


def test_robokum_7_A_701(tmp_path):
    """
    Тест для задачи: 7-A (ID: 701)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у входа в коридор.
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока" и сложные условия.
нач
вверх
влево
нц пока сверху стена или снизу стена
закрасить
влево
кц
вверх
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_7_A_701 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_7_A_701: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_7_A_701: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_7_A_701: {e}")


def test_robokum_7_B_702(tmp_path):
    """
    Тест для задачи: 7-B (ID: 702)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у входа в коридор.
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока" и 
| сложные условия.
нач
вверх
влево
нц пока сверху стена или снизу стена
если сверху стена и снизу стена
то
закрасить
все
влево
кц
вверх
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_7_B_702 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_7_B_702: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_7_B_702: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_7_B_702: {e}")


def test_robokum_7_C_703(tmp_path):
    """
    Тест для задачи: 7-C (ID: 703)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у входа в коридор.
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока" и 
| сложные условия.
нач
вниз
вправо
нц пока справа свободно
если сверху стена и снизу стена
то
закрасить
все
если сверху свободно
то
вверх
закрасить
вниз
все
вправо
кц
нц пока справа стена или слева стена
если слева стена и справа стена
то
закрасить
все
если справа свободно
то
вправо
закрасить
влево
все
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_7_C_703 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_7_C_703: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_7_C_703: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_7_C_703: {e}")


def test_robokum_7_D_704(tmp_path):
    """
    Тест для задачи: 7-D (ID: 704)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот стоит у входа в коридор.
| Длины стенок и число проходов 
| неизвестны.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл "пока" и 
| сложные условия.
нач
вниз
вправо
нц пока сверху стена или снизу стена
если сверху стена и снизу стена
то
закрасить
все
если сверху свободно
то
вверх
закрасить
вниз
все
вправо
кц
вниз
нц пока справа стена или слева стена
если слева стена и справа стена
то
закрасить
все
если справа свободно
то
вправо
закрасить
влево
все
вниз
кц
влево
нц пока сверху стена или снизу стена
если сверху стена и снизу стена
то
закрасить
все
если снизу свободно
то
вниз
закрасить
вверх
все
влево
кц
вверх
нц пока справа стена или слева стена
если слева стена и справа стена
то
закрасить
все
если слева свободно
то
влево
закрасить
вправо
все
вверх
кц
влево
вверх
вверх
вправо
вправо
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
        print(f"Test test_robokum_7_D_704 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_7_D_704: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_7_D_704: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_7_D_704: {e}")


def test_robokum_8_A_801(tmp_path):
    """
    Тест для задачи: 8-A (ID: 801)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте вспомогательный алгоритм
| "Ряд".
нач
вправо
вниз
Ряд
вверх
вправо
Ряд
вправо
вправо
Ряд
вправо
вниз
Ряд
кон
| вспомогательный алгоритм
алг Ряд
нач
нц 6 раз
вниз
закрасить
кц
нц 6 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_801.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_8_A_801 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_8_A_801: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_8_A_801: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_8_A_801: {e}")


def test_robokum_8_B_802(tmp_path):
    """
    Тест для задачи: 8-B (ID: 802)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте вспомогательный алгоритм
| "Сапог".
нач
Сапог
вправо
вправо
вверх
вверх
Сапог
вверх
вверх
влево
влево
Сапог
кон
| вспомогательный алгоритм
алг Сапог
нач
влево
закрасить
вверх
нц 4 раз
закрасить
влево
кц
нц 5 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_802.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_8_B_802 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_8_B_802: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_8_B_802: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_8_B_802: {e}")


def test_robokum_8_C_803(tmp_path):
    """
    Тест для задачи: 8-C (ID: 803)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте вспомогательный алгоритм.
нач
Крест
нц 5 раз
вниз
кц
влево
Крест
нц 3 раз
вверх
кц
влево
Крест
кон
| вспомогательный алгоритм
алг Крест
нач
вправо
закрасить
вверх
вверх
закрасить
влево
вниз
нц 3 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_803.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_8_C_803 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_8_C_803: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_8_C_803: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_8_C_803: {e}")


def test_robokum_8_D_804(tmp_path):
    """
    Тест для задачи: 8-D (ID: 804)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте вспомогательный алгоритм,
| который вызывается 4 раза.
нач
вправо
Т
Т
нц 4 раз
вниз
кц
Т
нц 4 раз
вниз
кц
нц 4 раз
влево
кц
Т
влево
влево
вверх
вверх
кон
| вспомогательный алгоритм
алг Т
нач
вверх
закрасить
вверх
влево
нц 3 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_804.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_8_D_804 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_8_D_804: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_8_D_804: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_8_D_804: {e}")


def test_robokum_9_A_901(tmp_path):
    """
    Тест для задачи: 9-A (ID: 901)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот у нижней стенки прямоугольной ограды.
надо | Привести Робота на Базу, расположенную у верхней
| стенки ограды на таком же расстояниии от 
| левой стенки этой ограды.
| Используйте переменные.
нач
цел n
n := 0
нц пока сверху стена
влево
n:=n+1
кц
вверх
нц пока справа стена
вверх
кц
нц n раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_901.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_9_A_901 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_9_A_901: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_9_A_901: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_9_A_901: {e}")


def test_robokum_9_B_902(tmp_path):
    """
    Тест для задачи: 9-B (ID: 902)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Ниже Робота расположена стенка.
надо | Привести Робота на Базу, расположенную симметрично
| начальной точке относительно стенки. Закрасить все 
| клетки под стенкой слева от линии Робот-база.
| Используйте переменные.
нач
цел a, b
a:=0; b:=0
нц пока снизу свободно
вниз
a:=a+1
кц
нц пока снизу стена
влево
b:=b+1
кц
вниз
нц b раз
вправо
закрасить
кц
нц a раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_902.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_9_B_902 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_9_B_902: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_9_B_902: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_9_B_902: {e}")


def test_robokum_9_C_903(tmp_path):
    """
    Тест для задачи: 9-C (ID: 903)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить клетки в углах поля и привести 
| Робота в начальную точку.
| Используйте переменные.
нач
цел a, b
a:=0; b:=0
нц пока сверху свободно
вверх
a:=a+1
кц
нц пока слева свободно
влево
b:=b+1
кц
закрасить
нц пока снизу свободно
вниз
кц
закрасить
нц пока справа свободно
вправо
кц
закрасить
нц пока сверху свободно
вверх
кц
закрасить
нц пока слева свободно
влево
кц
закрасить
нц b раз
вправо
кц
нц a раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_903.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_9_C_903 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_9_C_903: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_9_C_903: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_9_C_903: {e}")


def test_robokum_9_D_904(tmp_path):
    """
    Тест для задачи: 9-D (ID: 904)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле, разделенном на две части
| горизонтальной стенкой. В стенке есть проход.
надо | Закрасить клетки в углах обеих частей 
| поля и привести Робота в начальную точку.
| Используйте переменные.
нач
цел a, b
a:=0; b:=0
нц пока сверху свободно
вверх
a:=a+1
кц
нц пока слева свободно
влево
b:=b+1
кц
закрасить
нц пока снизу свободно
вниз
кц
закрасить
нц пока снизу стена
вправо
кц
вниз
нц пока слева свободно
влево
кц
закрасить
нц пока снизу свободно
вниз
кц
закрасить
нц пока справа свободно
вправо
кц
закрасить
нц пока сверху свободно
вверх
кц
закрасить
нц пока сверху стена
влево
кц
вверх
нц пока справа свободно
вправо
кц
закрасить
нц пока сверху свободно
вверх
кц
закрасить
нц пока слева свободно
влево
кц
закрасить
нц b раз
вправо
кц
нц a раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_904.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_9_D_904 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_9_D_904: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_9_D_904: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_9_D_904: {e}")


def test_robokum_10_A_1001(tmp_path):
    """
    Тест для задачи: 10-A (ID: 1001)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Ниже Робота расположена стенка.
надо | Закрасить все отмеченные клетки и привести 
| Робота на Базу, расположенную у правого
| края стенки.
| Используйте вспомогательный алгоритм, который
| вычисляет длину стенки.
нач
цел д
д := Длина стенки
вывод "Длина стенки ", д
кон
| вспомогательный алгоритм с результатом
алг цел Длина стенки
нач
цел a
нц пока снизу свободно
вниз
кц
нц пока снизу стена
влево
кц
вниз
a:=0
вправо
нц пока сверху стена
закрасить
вправо
a:=a+1
кц
знач:=a
кон

|#%%
алг цел @тестирование
нач
цел x, y, ширина, высота, длина
длина := Длина стенки
если длина <> int(@@температура(1,1))то
вывод "Задание не выполнено: неверно определена длина стенки"
знач:=0
выход
все
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1001.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_10_A_1001 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_10_A_1001: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_10_A_1001: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_10_A_1001: {e}")


def test_robokum_10_B_1002(tmp_path):
    """
    Тест для задачи: 10-B (ID: 1002)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на пустом поле.
надо | Закрасить отмеченные клетки в углах поля
| и привести Робота на Базу рядом в правом
| нижнем углу поля.
| Используйте вспомогательный алгоритм, который
| вычисляет площадь поля.
нач
цел пл
пл := Площадь поля
вывод "Площадь поля ", пл
кон
| вспомогательный алгоритм с результатом
алг цел Площадь поля
нач
цел a, b
нц пока справа свободно
вправо
кц
нц пока сверху свободно
вверх
кц
a:=1
закрасить
нц пока слева свободно
влево
a:=a+1
кц
b:=1
закрасить
нц пока снизу свободно
вниз
b:=b+1
кц
закрасить
нц пока справа свободно
вправо
кц
закрасить
знач:=a*b
кон

|#%%
алг цел @тестирование
нач
цел x, y, ширина, высота, длина
длина := Площадь поля
если длина <> int(@@температура(1,1))то
вывод "Задание не выполнено: неверно определена площадь поля"
знач:=0
выход
все
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1002.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_10_B_1002 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_10_B_1002: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_10_B_1002: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_10_B_1002: {e}")


def test_robokum_10_C_1003(tmp_path):
    """
    Тест для задачи: 10-C (ID: 1003)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на пустом поле.
надо | Закрасить отмеченные клетки по краям поля
| и привести Робота в начальную клетку.
| Используйте вспомогательный алгоритм, который
| вычисляет площадь поля.
нач
цел пл
пл := Площадь поля
вывод "Площадь поля ", пл
кон
| вспомогательный алгоритм с результатом
алг цел Площадь поля
нач
цел a, b, m, n
m:=0
нц пока справа свободно
вправо
m:=m+1
кц
n:=0
нц пока сверху свободно
вверх
n:=n+1
кц
a:=1
нц пока слева свободно
влево
закрасить
a:=a+1
кц
b:=1
нц пока снизу свободно
вниз
закрасить
b:=b+1
кц
нц пока справа свободно
вправо
закрасить
кц
нц пока сверху свободно
вверх
закрасить
кц
нц n раз
вниз
кц
нц m раз
влево
кц
знач:=a*b
кон

|#%%
алг цел @тестирование
нач
цел x, y, ширина, высота, длина
длина := Площадь поля
если длина <> int(@@температура(1,1))то
вывод "Задание не выполнено: неверно определена площадь поля"
знач:=0
выход
все
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1003.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_10_C_1003 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_10_C_1003: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_10_C_1003: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_10_C_1003: {e}")


def test_robokum_10_D_1004(tmp_path):
    """
    Тест для задачи: 10-D (ID: 1004)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Поле состоит из двух прямоугольников,
| правые границы которых находятся
| на одной линии. Робот стоит где-то в 
| нижнем (большом) прямоугольнике.
надо | Закрасить отмеченные клетки по 
| контуру поля и привести Робота  
| в начальную клетку.
| Используйте вспомогательный алгоритм, 
| который выполняет это задание и 
| вычисляет количество закрашенных клеток.
нач
цел клетки
клетки := Закрашенных клеток
вывод "Закрашено клеток: ", клетки
кон
| вспомогательный алгоритм с результатом
алг цел Закрашенных клеток
нач
цел n=0
нц пока снизу свободно; вниз; кц
нц пока справа свободно; вправо; кц
нц пока слева свободно; влево; закрасить; n:=n+1; кц
нц пока сверху свободно; вверх; закрасить; n:=n+1; кц
нц пока сверху стена; вправо; закрасить; n:=n+1; кц
нц пока сверху свободно; вверх; закрасить; n:=n+1; кц
нц пока справа свободно; вправо; закрасить; n:=n+1; кц
нц пока снизу свободно; вниз; закрасить; n:=n+1; кц
знач:=n
кон

|#%%
алг цел @тестирование
нач
цел x, y, ширина, высота, длина
длина := Закрашенных клеток
если длина <> int(@@температура(1,1))то
вывод "Задание не выполнено: неверно определен периметр поля"
знач:=0
выход
все
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1004.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_10_D_1004 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_10_D_1004: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_10_D_1004: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_10_D_1004: {e}")


def test_robokum_10_E_1005(tmp_path):
    """
    Тест для задачи: 10-E (ID: 1005)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле, которое разделено на две части 
| фигурной стенкой, причем нижняя граница поля
| свободна и все клетки, доступные Роботу,
| просматриваются с нижней границы.
надо | Закрасить все клетки, доступные Роботу,
| и привести Робота в правый нижний угол поля.
| Используйте вспомогательный алгоритм, который
| вычисляет площадь доступной части поля.
нач
цел пл
пл := Площадь поля
вывод "Площадь поля ", пл
кон
| вспомогательный алгоритм с результатом
алг цел Площадь поля
нач
цел a
нц пока снизу свободно
вниз
кц
нц пока слева свободно
влево
кц
a:=0
нц пока справа свободно
a:=a+Ряд
вправо
кц
знач:=a + Ряд
кон
| Обработка вертикального рядя клеток
алг цел Ряд
нач 
цел a = 1
закрасить
нц пока сверху свободно
вверх
закрасить
a:=a+1
кц
нц пока снизу свободно
вниз
кц
знач:=a
кон

|#%%
алг цел @тестирование
нач
цел x, y, ширина, высота, длина
длина := Площадь поля
если длина <> int(@@температура(1,1))то
вывод "Задание не выполнено: неверно определена площадь поля"
знач:=0
выход
все
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1005.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_10_E_1005 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_10_E_1005: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_10_E_1005: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_10_E_1005: {e}")


def test_robokum_11_A_1101(tmp_path):
    """
    Тест для задачи: 11-A (ID: 1101)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл с переменной.
нач
цел i
нц для i от 1 до 7
нц i раз
влево
закрасить
кц
нц i раз
вправо
кц
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1101.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_11_A_1101 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_11_A_1101: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_11_A_1101: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_11_A_1101: {e}")


def test_robokum_11_B_1102(tmp_path):
    """
    Тест для задачи: 11-B (ID: 1102)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл с переменной.
нач
цел i
нц 5 раз
вправо
кц
нц для i от 1 до 5
нц i раз
влево
закрасить
кц
нц i раз
вправо
кц
вниз
кц
влево
нц для i от 5 до 1 шаг -1
нц i раз
вправо
закрасить
кц
нц i раз
влево
кц
вниз
кц
вправо
нц 6 раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1102.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_11_B_1102 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_11_B_1102: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_11_B_1102: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_11_B_1102: {e}")


def test_robokum_11_C_1103(tmp_path):
    """
    Тест для задачи: 11-C (ID: 1103)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл с переменной.
нач
цел i
нц для i от 9 до 1 шаг -2
вверх
нц i раз
закрасить
вправо
кц
нц i-1 раз
влево
кц
кц
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1103.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_11_C_1103 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_11_C_1103: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_11_C_1103: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_11_C_1103: {e}")


def test_robokum_11_D_1104(tmp_path):
    """
    Тест для задачи: 11-D (ID: 1104)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте цикл с переменной.
нач
цел i
влево
вверх
вверх
нц для i от 8 до 2 шаг -2
нц i раз
вправо
вниз
закрасить
кц
нц i раз
вверх
влево
кц
вправо
вправо
кц
вниз
кон

|#%%
алг цел @тестирование
нач
Миссия
цел x, y, ширина, высота
знач := 10
@@робот(x, y)
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1104.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_11_D_1104 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_11_D_1104: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_11_D_1104: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_11_D_1104: {e}")


def test_robokum_12_A_1201(tmp_path):
    """
    Тест для задачи: 12-A (ID: 1201)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте алгоритм с параметром.
нач
цел i
вниз
вниз
вправо
нц для i от 5 до 1 шаг -2
Ряд(i)
вправо
вправо
вверх
кц
вниз
вниз
Ряд(3)
вправо
вправо
вниз
Ряд(5)
вправо
нц 5 раз
вверх
кц
кон
алг Ряд (цел длина)
нач
нц длина раз
вверх
закрасить
кц
нц длина раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1201.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_12_A_1201 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_12_A_1201: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_12_A_1201: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_12_A_1201: {e}")


def test_robokum_12_B_1202(tmp_path):
    """
    Тест для задачи: 12-B (ID: 1202)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте алгоритм с параметром.
нач
вниз
вправо
цел д
нц для д от 3 до 6
Сапог(д)
вправо
кц
нц 6 раз
вверх
кц
кон
алг Сапог (цел длина)
нач
нц длина раз
вверх
закрасить
кц
вправо
закрасить
нц длина раз
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1202.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_12_B_1202 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_12_B_1202: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_12_B_1202: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_12_B_1202: {e}")


def test_robokum_12_C_1203(tmp_path):
    """
    Тест для задачи: 12-C (ID: 1203)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте алгоритм с параметром.
нач
Квадрат(3)
вниз
вправо
Квадрат(2)
нц 3 раз
вправо
кц
нц 4 раз
вверх
кц
Квадрат(4)
нц 5 раз
вправо
кц
вверх
кон
алг Квадрат (цел сторона)
нач
нц сторона раз
нц сторона раз
вправо
закрасить
кц
нц сторона раз
влево
кц
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1203.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_12_C_1203 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_12_C_1203: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_12_C_1203: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_12_C_1203: {e}")


def test_robokum_12_D_1204(tmp_path):
    """
    Тест для задачи: 12-D (ID: 1204)
    Курс: robokum
    """
    kumir_code = '''использовать Робот
алг Миссия 
дано | Робот на поле.
надо | Закрасить все отмеченные клетки
| и привести Робота на Базу.
| Используйте алгоритм с параметром.
нач
Птичка(4)
влево
нц 6 раз
вверх
кц
Птичка(3)
влево
влево
нц 6 раз
вверх
кц
Птичка(5)
вправо
нц 5 раз
вверх
кц
кон
алг Птичка(цел размер)
нач
цел i
нц для i от размер до 1 шаг -1
нц i раз
вправо
закрасить
кц
нц i-1 раз
влево
кц
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
если @@нижняя буква (x,y) <> 'Б' то 
вывод "Задание не выполнено: Робот не пришёл на Базу.", нс
знач := 0
выход
все
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
    test_file = tmp_path / "test_1204.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_robokum_12_D_1204 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_robokum_12_D_1204: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_robokum_12_D_1204: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_robokum_12_D_1204: {e}")

