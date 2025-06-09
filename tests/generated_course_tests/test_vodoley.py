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

# Автогенерированные тесты для курса: vodoley
# Сгенерировано: 2025-06-09 11:49:00

def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_101(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 101)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом 5 и 3 литра
надо | Получить 1 литр воды в любом из сосудов
нач
наполни B
перелей из B в A
наполни B
перелей из B в A
кон

|#%%
алг цел @тестирование
нач
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_101.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_101 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_101: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_101: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_101: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_102(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 102)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Три пустых сосуда объемом 6, 10, 15 литров
надо | Получить 1 литр воды в любом из сосудов
нач
наполни B
перелей из B в C
наполни A
перелей из A в C
кон

алг цел @тестирование
нач
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_102.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_102 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_102: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_102: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_102: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_103(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 103)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два сосуда объемом 6 и 10 литров, в первом налито 3 литра
надо | Получить 1 литр воды в любом из сосудов
нач
наполни B
перелей из B в A
вылей A
перелей из B в A
кон

алг цел @тестирование
нач
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_103.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_103 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_103: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_103: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_103: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_104(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 104)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом 8 и 5 литров
надо | Получить 1 литр воды в любом из сосудов
нач
наполни A
перелей из A в B
вылей B
перелей из A в B
наполни A
перелей из A в B
вылей B
перелей из A в B
кон
алг цел @тестирование
нач
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_104.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_104 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_104: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_104: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_104: {e}")


def test_vodoley_Naberite_4_litra_vody_v_lyubom_iz_sosudov_105(tmp_path):
    """
    Тест для задачи: Наберите 4 литра воды в любом из сосудов (ID: 105)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 4 литра
дано | Два пустых сосуда объемом 8 и 5 литров
надо | Получить 4 литра воды в любом из сосудов
нач
наполни B
перелей из B в A
наполни B
перелей из B в A
вылей A
перелей из B в A
наполни B
перелей из B в A
наполни B
перелей из B в A
кон
алг цел @тестирование
нач
Отмерить 4 литра
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_105.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_4_litra_vody_v_lyubom_iz_sosudov_105 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_4_litra_vody_v_lyubom_iz_sosudov_105: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_4_litra_vody_v_lyubom_iz_sosudov_105: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_4_litra_vody_v_lyubom_iz_sosudov_105: {e}")


def test_vodoley_Naberite_7_litrov_vody_v_lyubom_iz_sosudov_106(tmp_path):
    """
    Тест для задачи: Наберите 7 литров воды в любом из сосудов (ID: 106)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 7 литров
дано | Три пустых сосуда объемом 6, 10, 15 литров
надо | Получить 7 литров воды в любом из сосудов
нач
наполни B
перелей из B в C
наполни A
перелей из A в C
перелей из A в B
наполни A
перелей из A в B
кон

алг цел @тестирование
нач
Отмерить 7 литров
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_106.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_7_litrov_vody_v_lyubom_iz_sosudov_106 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_7_litrov_vody_v_lyubom_iz_sosudov_106: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_7_litrov_vody_v_lyubom_iz_sosudov_106: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_7_litrov_vody_v_lyubom_iz_sosudov_106: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_201(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 201)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей
алг Отмерить 1 литр
дано | Два пустых сосуда объемом 7 и 2 литра.
надо | Получить 1 литр воды в любом 
       | из сосудов.
       | Используйте цикл "N раз" 
нач
наполни A
нц 3 раз
перелей из A в B
вылей B
кц
кон
алг цел @тестирование
нач
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_201.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_201 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_201: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_201: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_201: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_202(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 202)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом 5 и 2 литра
надо | Получить 1 литр воды в любом из сосудов
нач
наполни A
нц 2 раз
перелей из A в B
вылей B
кц
кон

алг цел @тестирование
нач
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_202.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_202 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_202: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_202: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_202: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_203(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 203)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом 11 и 2 литра
надо | Получить 1 литр воды в любом из сосудов
нач
наполни A
нц 5 раз
перелей из A в B
вылей B
кц
кон

алг цел @тестирование
нач
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно"
иначе
вывод "Задание не выполнено"
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_203.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_203 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_203: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_203: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_203: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_204(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 204)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и 2 литра, n - нечетное
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц ... раз
нач
наполни A
нц div(размер A, 2) раз
вылей B
перелей из A в B
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_204.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_204 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_204: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_204: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_204: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_205(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 205)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и 3 литра, 
       | где n=3*k+1.
надо | Получить 1 литр воды в любом из сосудов.
       | Используйте цикл "N раз".
нач
наполни A
нц div(размер A, 3) раз
вылей B
перелей из A в B
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_205.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_205 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_205: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_205: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_205: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_206(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 206)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и m литров, 
       | где n=m*k+1.
надо | Получить 1 литр воды в любом из сосудов.
       | Используйте цикл "N раз".
нач
наполни A
нц div(размер A, размер B) раз
вылей B
перелей из A в B
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_206.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_206 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_206: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_206: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_206: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_207(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 207)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и m литров, n=m*k-1 (k>0)
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц ... раз
нач
нц div(размер A, размер B)+1 раз
наполни B
перелей из B в A
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_207.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_207 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_207: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_207: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_207: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_208(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 208)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и m литров, 
       | где n=m*k-1 (k>0).
надо | Получить 1 литр воды в любом из сосудов.
       | Используйте цикл "N раз".
нач
нц div(размер A, размер B)+1 раз
наполни B
перелей из B в A
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_208.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_208 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_208: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_208: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_208: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_301(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 301)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и 2 литра, n - нечетное
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц пока
нач
наполни A
нц пока в сосуде A <> 1
перелей из A в B
вылей B
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_301.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_301 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_301: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_301: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_301: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_302(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 302)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом 3 литра и n литров, n=3*k+1
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц пока
нач
наполни B
нц пока в сосуде B <> 1
перелей из B в A
вылей A
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_302.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_302 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_302: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_302: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_302: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_303(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 303)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и 3 литра, n=3*k+2
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц пока
нач
нц пока в сосуде B <> 1
наполни B
перелей из B в A
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_303.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_303 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_303: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_303: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_303: {e}")


def test_vodoley_Naberite_10_litrov_vody_304(tmp_path):
    """
    Тест для задачи: Наберите 10 литров воды (ID: 304)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 10 литров
дано | Два сосуда объемом 4 и n литров (n=4*k, k>2), 
| в первый налито 2 литра воды, а во второй - 1 литр.
надо | Отмерить 10 литров воды.
| Используйте цикл "пока".
нач
вылей B
нц пока в сосуде B <> 10
перелей из A в B
наполни A
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 10 литров
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_304.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_10_litrov_vody_304 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_10_litrov_vody_304: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_10_litrov_vody_304: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_10_litrov_vody_304: {e}")


def test_vodoley_Naberite_9_litrov_vody_305(tmp_path):
    """
    Тест для задачи: Наберите 9 литров воды (ID: 305)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 9 литров
дано | Два сосуда объемом n и 4 литра (n=4*k, k>2), 
| в первый налит 2 литра воды, а во второй - 1 литр.
надо | Отмерить 9 литров воды.
| Используйте цикл "пока".
нач
вылей A
нц пока в сосуде A <> 9
перелей из B в A
наполни B
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 9 литров
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_305.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_9_litrov_vody_305 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_9_litrov_vody_305: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_9_litrov_vody_305: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_9_litrov_vody_305: {e}")


def test_vodoley_Naberite_11_litrov_vody_306(tmp_path):
    """
    Тест для задачи: Наберите 11 литров воды (ID: 306)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 11 литров
дано | Два сосуда объемом n и 4 литра (n=4*k, k>2), 
| в первый налит 2 литра воды, а во второй - 1 литр.
надо | Отмерить 11 литров воды.
| Используйте цикл "пока".
нач
нц пока в сосуде A <> 11
перелей из B в A
наполни B
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 11 литров
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_306.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_11_litrov_vody_306 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_11_litrov_vody_306: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_11_litrov_vody_306: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_11_litrov_vody_306: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_401(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 401)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и 2 литра, n - нечетное
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц пока
| Команды "в сосуде X" использовать не разрешается.
нач
цел N
наполни A
N := размер A
нц пока N <> 1
перелей из A в B
вылей B
N := N - 2
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_401.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_401 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_401: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_401: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_401: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_402(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 402)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом 2 литра и n литров, 
| где n - нечетное число.
надо | Получить 1 литр воды в любом из сосудов.
| Используйте цикл "пока".
| Команды "в сосуде X" использовать 
| не разрешается.
нач
цел N
наполни B
N := размер B
нц пока N <> 1
перелей из B в A
вылей A
N := N - 2
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_402.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_402 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_402: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_402: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_402: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_403(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 403)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом 3 литра и n литров, n=3*k+1
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц пока
| Команды "в сосуде X" использовать не разрешается.
нач
цел N
наполни B
N := размер B
нц пока N <> 1
перелей из B в A
вылей A
N := N - 3
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_403.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_403 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_403: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_403: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_403: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_404(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 404)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и 3 литра, n=3*k+2
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл нц пока
| Команды "в сосуде X" использовать не разрешается. 
нач
цел N
N := размер A
нц пока N > 0
наполни B
перелей из B в A
N := N - 3
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_404.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_404 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_404: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_404: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_404: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_405(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 405)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и m литрво, n=m*k+1
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл "пока".
| Команды "в сосуде X" использовать не разрешается.
нач
цел N
наполни A
N := размер A
нц пока N <> 1
перелей из A в B
вылей B
N := N - размер B
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_405.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_405 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_405: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_405: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_405: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_406(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 406)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и m литров, n=m*k-1 (k>0)
надо | Получить 1 литр воды в любом из сосудов
| Используйте цикл "пока".
| Команды "в сосуде X" использовать не разрешается.
нач
цел N
N := размер A
нц пока N > 0
наполни B
перелей из B в A
N := N - размер B
кц
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_406.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_406 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_406: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_406: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_406: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_501(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 501)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, один из которых (незвестно какой) 
       | имеет объем 1 литр 
надо | Получить 1 литр воды в любом из сосудов
нач 
если размер A = 1
то
наполни A
иначе
наполни B
все
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_501.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_501 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_501: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_501: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_501: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_502(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 502)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, один из которых имеет объем 2 литра,
       | а объем второго - нечетное число  
надо | Получить 1 литр воды в любом из сосудов
нач 
если размер A = 2
то
наполни B
перелей из B в A
иначе 
наполни A
перелей из A в B
все
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_502.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_502 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_502: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_502: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_502: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_503(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 503)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, один из которых (незвестно какой) 
| имеет объем 2 литра, а второй - 11 литров 
надо | Получить 1 литр воды в любом из сосудов
нач 
если размер A = 2
то
наполни B
нц 5 раз
перелей из B в A
вылей A
кц
иначе 
наполни A
нц 5 раз
перелей из A в B
вылей B
кц
все
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_503.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_503 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_503: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_503: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_503: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_504(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 504)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, один из которых имеет объем 2 литра,
| а объем второго - нечетное число  
надо | Получить 1 литр воды в любом из сосудов
     | используйте цикл "пока"
нач 
если размер A = 4
то
нц пока в сосуде A <> 1
наполни A
перелей из A в B
кц
иначе 
нц пока в сосуде B <> 1
наполни B
перелей из B в A
кц
все
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_504.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_504 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_504: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_504: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_504: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_505(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 505)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, один из которых имеет объем 2 литра,
       | а объем второго - нечетное число  
надо | Получить 1 литр воды в любом из сосудов
нач 
если размер A = 2
то
наполни B
нц div(размер B,2) раз
перелей из B в A
если в сосуде A <> 1 
то
вылей A
все
кц
иначе 
наполни A
нц div(размер A,2) раз
перелей из A в B
если в сосуде B <> 1 
то
вылей B
все
кц
все
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_505.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_505 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_505: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_505: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_505: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_506(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 506)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, один из которых 
       | (неизвестно какой) имеет объем 2 литра,
       | а объем второго - нечетное число.  
надо | Получить 1 литр воды в любом из сосудов.
       | Используйте цикл "N раз".
нач 
если размер A = 2
то
наполни B
нц пока в сосуде B <> 1
перелей из B в A
вылей A
кц
иначе 
наполни A
нц пока в сосуде A <> 1
перелей из A в B
вылей B
кц
все
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_506.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_506 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_506: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_506: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_506: {e}")


def test_vodoley_Dany_dva_sosuda_507(tmp_path):
    """
    Тест для задачи: Даны два сосуда (ID: 507)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 ИЛИ 4 литра
дано | Два сосуда, первый имеет объем 2 литра,
| а объем второго неизвестен, но не менее 3 литров.  
надо | Если это возможно, наберите 1 литр воды 
       | в любом из сосудов. Если нельзя - наберите
       | 4 литра воды во втором сосуде.
       | Подсказка: mod(A,B) обозначает остаток от
       | деления A на B.
нач 
если mod(размер B,2) = 1
то
наполни B
нц пока в сосуде B <> 1
перелей из B в A
вылей A
кц
иначе
нц 2 раз
наполни A
перелей из A в B
кц
все
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 ИЛИ 4 литра 
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_507.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Dany_dva_sosuda_507 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Dany_dva_sosuda_507: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Dany_dva_sosuda_507: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Dany_dva_sosuda_507: {e}")


def test_vodoley_Dany_dva_sosuda_508(tmp_path):
    """
    Тест для задачи: Даны два сосуда (ID: 508)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 ИЛИ 4 литра
дано | Два сосуда, один из которых (неизвестно какой)
       | имеет объем 2 литра, а объем другого 
       | неизвестен, но не менее 3 литров.  
надо | Если это возможно, наберите 1 литр воды 
       | в любом из сосудов. Если невозможно - наберите
       | 4 литра воды.
       | Подсказка: mod(A,B) обозначает остаток от
       | деления A на B.
нач 
если размер A = 2
то
если mod(размер B,2) = 1
то
наполни B
нц пока в сосуде B <> 1
перелей из B в A
вылей A
кц
иначе
нц 2 раз
наполни A
перелей из A в B
кц
все
иначе
если mod(размер A,2) = 1
то
наполни A
нц пока в сосуде A <> 1
перелей из A в B
вылей B
кц
иначе
нц 2 раз
наполни B
перелей из B в A
кц
все
все
кон
алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 ИЛИ 4 литра 
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_508.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Dany_dva_sosuda_508 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Dany_dva_sosuda_508: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Dany_dva_sosuda_508: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Dany_dva_sosuda_508: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_601(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 601)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда объемом n и 3 литра, n не делится на 3
надо | Получить 1 литр воды в любом из сосудов
нач 
если размер A = 1
то
наполни A
иначе
если размер A = 2
то
наполни B
перелей из B в A
иначе
нц пока в сосуде B <> 1
наполни B
перелей из B в A
если в сосуде A = размер A
то
вылей A
все
кц
все
все
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то 
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_601.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_601 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_601: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_601: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_601: {e}")


def test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_602(tmp_path):
    """
    Тест для задачи: Наберите 1 литр воды в любом из сосудов (ID: 602)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, объемы сосудов - взаимно простые числа
надо | Получить 1 литр воды в любом из сосудов
нач 
наполни A
нц пока в сосуде A <> 1
перелей из A в B
если в сосуде B = размер B то 
вылей B
все
если в сосуде A = 0 то 
наполни A
все
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_602.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_602 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_602: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_602: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Naberite_1_litr_vody_v_lyubom_iz_sosudov_602: {e}")


def test_vodoley_Dopolnite_reshenie_predyduschey_zadachi_tak_chtoby_ono_rabot_603(tmp_path):
    """
    Тест для задачи: Дополните решение предыдущей задачи так, чтобы оно работало и в том случае, когда размеры сосудов могут быть равны 1 (ID: 603)
    Курс: vodoley
    """
    kumir_code = '''использовать Водолей

алг Отмерить 1 литр
дано | Два пустых сосуда, объемы сосудов - взаимно простые числа
надо | Получить 1 литр воды в любом из сосудов
нач 
наполни A
нц пока в сосуде A <> 1
перелей из A в B
если в сосуде B = размер B то 
вылей B
все
если в сосуде A = 0 то 
наполни A
все
кц
кон

алг цел @тестирование
нач
вывод "Начинаем проверку на сосудах объемом ", размер A, " и ", размер B, " литров", нс
Отмерить 1 литр
если @решено то
знач:=10
вывод "Задание выполнено успешно", нс
иначе
вывод "Задание выполнено неверно", нс
знач:=0
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_603.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_vodoley_Dopolnite_reshenie_predyduschey_zadachi_tak_chtoby_ono_rabot_603 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_vodoley_Dopolnite_reshenie_predyduschey_zadachi_tak_chtoby_ono_rabot_603: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_vodoley_Dopolnite_reshenie_predyduschey_zadachi_tak_chtoby_ono_rabot_603: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_vodoley_Dopolnite_reshenie_predyduschey_zadachi_tak_chtoby_ono_rabot_603: {e}")

