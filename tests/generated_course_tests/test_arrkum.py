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

# Автогенерированные тесты для курса: arrkum
# Сгенерировано: 2025-06-09 11:48:59

def test_arrkum_Zapolnite_massiv_A_nulyami_10(tmp_path):
    """
    Тест для задачи: Заполните массив A нулями (ID: 10)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_10.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnite_massiv_A_nulyami_10 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnite_massiv_A_nulyami_10: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnite_massiv_A_nulyami_10: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnite_massiv_A_nulyami_10: {e}")


def test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_11(tmp_path):
    """
    Тест для задачи: Заполните массив A первыми N натуральными числами, начиная с 1 (ID: 11)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_11.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_11 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_11: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_11: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_11: {e}")


def test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_12(tmp_path):
    """
    Тест для задачи: Заполните массив A первыми N натуральными числами, начиная с X (ID: 12)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_12.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_12 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_12: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_12: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_12: {e}")


def test_arrkum_Zapolnite_massiv_naturalnymi_chislami_tak_chto_pervyy_elemen_13(tmp_path):
    """
    Тест для задачи: Заполните массив натуральными числами, так что первый элемент массива должен быть равен X, а каждый следующий элемент должен быть на 5 больше предыдущего (ID: 13)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_13.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnite_massiv_naturalnymi_chislami_tak_chto_pervyy_elemen_13 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnite_massiv_naturalnymi_chislami_tak_chto_pervyy_elemen_13: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnite_massiv_naturalnymi_chislami_tak_chto_pervyy_elemen_13: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnite_massiv_naturalnymi_chislami_tak_chto_pervyy_elemen_13: {e}")


def test_arrkum_Zapolnit_massiv_A_pervymi_N_chislami_Fibonachchi_14(tmp_path):
    """
    Тест для задачи: Заполнить массив A первыми N числами Фибоначчи (ID: 14)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_14.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnit_massiv_A_pervymi_N_chislami_Fibonachchi_14 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnit_massiv_A_pervymi_N_chislami_Fibonachchi_14: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnit_massiv_A_pervymi_N_chislami_Fibonachchi_14: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnit_massiv_A_pervymi_N_chislami_Fibonachchi_14: {e}")


def test_arrkum_Zapolnite_massiv_stepenyami_chisla_2_tak_chtoby_posledniy_el_15(tmp_path):
    """
    Тест для задачи: Заполните массив степенями числа 2, так чтобы последний элемент массива был равен 1, а каждый предыдущий был в 2 раза больше следующего (ID: 15)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_15.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnite_massiv_stepenyami_chisla_2_tak_chtoby_posledniy_el_15 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnite_massiv_stepenyami_chisla_2_tak_chtoby_posledniy_el_15: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnite_massiv_stepenyami_chisla_2_tak_chtoby_posledniy_el_15: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnite_massiv_stepenyami_chisla_2_tak_chtoby_posledniy_el_15: {e}")


def test_arrkum_Zapolnite_massiv_tselymi_chislami_tak_chtoby_sredniy_element_16(tmp_path):
    """
    Тест для задачи: Заполните массив целыми числами, так чтобы  средний элемент массива был равен X, слева от него элементы стоят по возрастанию, а справа - по убыванию (ID: 16)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_16.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnite_massiv_tselymi_chislami_tak_chtoby_sredniy_element_16 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnite_massiv_tselymi_chislami_tak_chtoby_sredniy_element_16: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnite_massiv_tselymi_chislami_tak_chtoby_sredniy_element_16: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnite_massiv_tselymi_chislami_tak_chtoby_sredniy_element_16: {e}")


def test_arrkum_Uvelichit_vse_elementy_massiva_A_na_1_20(tmp_path):
    """
    Тест для задачи: Увеличить все элементы массива A на 1 (ID: 20)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i
нц для i от 1 до N 
A[i]:=A[i]+1 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_20.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Uvelichit_vse_elementy_massiva_A_na_1_20 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Uvelichit_vse_elementy_massiva_A_na_1_20: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Uvelichit_vse_elementy_massiva_A_na_1_20: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Uvelichit_vse_elementy_massiva_A_na_1_20: {e}")


def test_arrkum_Umnozhit_vse_elementy_massiva_A_na_2_21(tmp_path):
    """
    Тест для задачи: Умножить все элементы массива A на 2 (ID: 21)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i
нц для i от 1 до N 
A[i]:=A[i]*2 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_21.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Umnozhit_vse_elementy_massiva_A_na_2_21 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Umnozhit_vse_elementy_massiva_A_na_2_21: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Umnozhit_vse_elementy_massiva_A_na_2_21: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Umnozhit_vse_elementy_massiva_A_na_2_21: {e}")


def test_arrkum_Vozvesti_v_kvadrat_vse_elementy_massiva_A_22(tmp_path):
    """
    Тест для задачи: Возвести в квадрат все элементы массива A (ID: 22)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i
нц для i от 1 до N 
A[i]:=A[i]*A[i] 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_22.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vozvesti_v_kvadrat_vse_elementy_massiva_A_22 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vozvesti_v_kvadrat_vse_elementy_massiva_A_22: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vozvesti_v_kvadrat_vse_elementy_massiva_A_22: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vozvesti_v_kvadrat_vse_elementy_massiva_A_22: {e}")


def test_arrkum_Uvelichit_na_4_vse_elementy_v_pervoy_polovine_massiva_A_schi_23(tmp_path):
    """
    Тест для задачи: Увеличить на 4 все элементы в первой половине массива A (считать, что в массиве чётное число элементов) (ID: 23)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i
нц для i от 1 до div(N,2) 
A[i]:=A[i]+4 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_23.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Uvelichit_na_4_vse_elementy_v_pervoy_polovine_massiva_A_schi_23 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Uvelichit_na_4_vse_elementy_v_pervoy_polovine_massiva_A_schi_23: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Uvelichit_na_4_vse_elementy_v_pervoy_polovine_massiva_A_schi_23: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Uvelichit_na_4_vse_elementy_v_pervoy_polovine_massiva_A_schi_23: {e}")


def test_arrkum_Razdelit_na_2_vse_elementy_massiva_A_krome_pervogo_i_posledn_24(tmp_path):
    """
    Тест для задачи: Разделить на 2 все элементы массива A, кроме первого и последнего (считать, что в массиве есть, по крайней мере, два элемента и все элементы чётные) (ID: 24)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i
нц для i от 2 до N-1 
A[i]:=div(A[i],2) 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_24.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Razdelit_na_2_vse_elementy_massiva_A_krome_pervogo_i_posledn_24 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Razdelit_na_2_vse_elementy_massiva_A_krome_pervogo_i_posledn_24: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Razdelit_na_2_vse_elementy_massiva_A_krome_pervogo_i_posledn_24: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Razdelit_na_2_vse_elementy_massiva_A_krome_pervogo_i_posledn_24: {e}")


def test_arrkum_Umnozhit_na_3_vse_elementy_vo_vtoroy_polovine_massiva_A_schi_25(tmp_path):
    """
    Тест для задачи: Умножить на 3 все элементы во второй половине массива A (считать, что в массиве чётное число элементов) (ID: 25)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i
нц для i от div(N,2)+1 до N 
A[i]:=A[i]*3 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_25.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Umnozhit_na_3_vse_elementy_vo_vtoroy_polovine_massiva_A_schi_25 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Umnozhit_na_3_vse_elementy_vo_vtoroy_polovine_massiva_A_schi_25: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Umnozhit_na_3_vse_elementy_vo_vtoroy_polovine_massiva_A_schi_25: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Umnozhit_na_3_vse_elementy_vo_vtoroy_polovine_massiva_A_schi_25: {e}")


def test_arrkum_Nayti_srednee_arifmeticheskoe_vseh_elementov_massiva_A_26(tmp_path):
    """
    Тест для задачи: Найти среднее арифметическое всех элементов массива A (ID: 26)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг вещ __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum = 0
нц для i от 1 до N 
sum:=sum+A[i]
кц
знач:=sum/N
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_26.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_srednee_arifmeticheskoe_vseh_elementov_massiva_A_26 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_srednee_arifmeticheskoe_vseh_elementov_massiva_A_26: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_srednee_arifmeticheskoe_vseh_elementov_massiva_A_26: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_srednee_arifmeticheskoe_vseh_elementov_massiva_A_26: {e}")


def test_arrkum_Nayti_maksimalnoe_znachenie_sredi_vseh_elementov_massiva_30(tmp_path):
    """
    Тест для задачи: Найти максимальное значение среди всех элементов массива (ID: 30)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, aMax
aMax:=A[1]
нц для i от 2 до N 
если A[i] > aMax то
aMax:=A[i]
все
кц
знач:=aMax
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_30.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_maksimalnoe_znachenie_sredi_vseh_elementov_massiva_30 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_maksimalnoe_znachenie_sredi_vseh_elementov_massiva_30: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_maksimalnoe_znachenie_sredi_vseh_elementov_massiva_30: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_maksimalnoe_znachenie_sredi_vseh_elementov_massiva_30: {e}")


def test_arrkum_Nayti_minimalnoe_znachenie_sredi_vseh_elementov_massiva_31(tmp_path):
    """
    Тест для задачи: Найти минимальное значение среди всех элементов массива (ID: 31)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, aMin
aMin:=A[1]
нц для i от 2 до N 
если A[i] < aMin то
aMin:=A[i]
все
кц
знач:=aMin
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_31.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_minimalnoe_znachenie_sredi_vseh_elementov_massiva_31 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_minimalnoe_znachenie_sredi_vseh_elementov_massiva_31: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_minimalnoe_znachenie_sredi_vseh_elementov_massiva_31: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_minimalnoe_znachenie_sredi_vseh_elementov_massiva_31: {e}")


def test_arrkum_Nayti_minimalnoe_i_maksimalnoe_znacheniya_sredi_vseh_element_32(tmp_path):
    """
    Тест для задачи: Найти минимальное и максимальное значения среди всех элементов массива (ID: 32)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез цел
  N := 5
  A[1:N] := 0
  цел := 0
  __Решение__(N, A[1:N], цел)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел Min, Max)
нач
цел i
Min:=A[1]
Max:=A[1]
нц для i от 2 до N 
если A[i] < Min то
Min:=A[i]
все
если A[i] > Max то
Max:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_32.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_minimalnoe_i_maksimalnoe_znacheniya_sredi_vseh_element_32 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_minimalnoe_i_maksimalnoe_znacheniya_sredi_vseh_element_32: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_minimalnoe_i_maksimalnoe_znacheniya_sredi_vseh_element_32: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_minimalnoe_i_maksimalnoe_znacheniya_sredi_vseh_element_32: {e}")


def test_arrkum_Nayti_nomer_minimalnogo_elementa_massiva_33(tmp_path):
    """
    Тест для задачи: Найти номер минимального элемента массива (ID: 33)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, nMin
nMin:=1
нц для i от 2 до N 
если A[i] < A[nMin] то
nMin:=i
все
кц
знач:=nMin
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_33.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_nomer_minimalnogo_elementa_massiva_33 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_nomer_minimalnogo_elementa_massiva_33: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_nomer_minimalnogo_elementa_massiva_33: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_nomer_minimalnogo_elementa_massiva_33: {e}")


def test_arrkum_Nayti_nomera_minimalnogo_i_maksimalnogo_elementov_massiva_34(tmp_path):
    """
    Тест для задачи: Найти номера минимального и максимального элементов массива (ID: 34)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез цел
  N := 5
  A[1:N] := 0
  цел := 0
  __Решение__(N, A[1:N], цел)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел nMin, nMax)
нач
цел i
nMin:=1
nMax:=1
нц для i от 2 до N 
если A[i] < A[nMin] то
nMin:=i
все
если A[i] > A[nMax] то
nMax:=i
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_34.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_nomera_minimalnogo_i_maksimalnogo_elementov_massiva_34 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_nomera_minimalnogo_i_maksimalnogo_elementov_massiva_34: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_nomera_minimalnogo_i_maksimalnogo_elementov_massiva_34: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_nomera_minimalnogo_i_maksimalnogo_elementov_massiva_34: {e}")


def test_arrkum_Nayti_dva_maksimalnyh_elementa_massiva_35(tmp_path):
    """
    Тест для задачи: Найти два максимальных элемента массива (ID: 35)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез цел
  N := 5
  A[1:N] := 0
  цел := 0
  __Решение__(N, A[1:N], цел)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел Max, Max2)
нач
цел i
Max:=imax(A[1],A[2])
Max2:=imin(A[1],A[2])
нц для i от 3 до N 
если A[i] > Max то
Max2:=Max
Max:=A[i]
иначе
если A[i] > Max2 то
Max2:=A[i]
все
все
кц
кон
|-------------------------------------------------------
| Вывод массива 
|-------------------------------------------------------
алг __Вывод массива__(цел N, целтаб A[1:N]) 
нач
цел i
нц для i от 1 до N 
вывод A[i]," "
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел N, целтаб A[1:N], цел R, R0, Q, Q0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Получены ответы:    max = ", R, "  max2 = ", Q
вывод нс, "Правильныые ответы: max = ", R0, "  max2 = ", Q0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_35.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_dva_maksimalnyh_elementa_massiva_35 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_dva_maksimalnyh_elementa_massiva_35: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_dva_maksimalnyh_elementa_massiva_35: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_dva_maksimalnyh_elementa_massiva_35: {e}")


def test_arrkum_Nayti_nomera_dvuh_minimalnyh_elementov_massiva_36(tmp_path):
    """
    Тест для задачи: Найти номера двух минимальных элементов массива (ID: 36)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез цел
  N := 5
  A[1:N] := 0
  цел := 0
  __Решение__(N, A[1:N], цел)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел nMin, nMin2)
нач
цел i
если A[1] <= A[2] то
nMin:=1; nMin2:=2
иначе
nMin:=2; nMin2:=1
все
нц для i от 3 до N 
если A[i] < A[nMin] то
nMin2:=nMin
nMin:=i
иначе
если A[i] < A[nMin2] то
nMin2:=i
все
все
кц
кон
|-------------------------------------------------------
| Вывод массива 
|-------------------------------------------------------
алг __Вывод массива__(цел N, целтаб A[1:N]) 
нач
цел i
нц для i от 1 до N 
вывод A[i]," "
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел N, целтаб A[1:N], цел R, R0, Q, Q0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Получены ответы:    min=A[", R, "]=", A[R], "   min2=A[", Q, "]=", A[Q]
вывод нс, "Правильныые ответы: min=A[", R0, "]=", A[R0], "   min2=A[", Q0, "]=", A[Q0]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_36.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_nomera_dvuh_minimalnyh_elementov_massiva_36 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_nomera_dvuh_minimalnyh_elementov_massiva_36: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_nomera_dvuh_minimalnyh_elementov_massiva_36: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_nomera_dvuh_minimalnyh_elementov_massiva_36: {e}")


def test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_1_40(tmp_path):
    """
    Тест для задачи: Определите, сколько элементов массива A равны 1 (ID: 40)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, count
count:=0
нц для i от 1 до N 
если A[i] = 1 то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_40.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_1_40 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_1_40: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_1_40: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_1_40: {e}")


def test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_zadannomu_znache_41(tmp_path):
    """
    Тест для задачи: Определите, сколько элементов массива A равны заданному значению X (ID: 41)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, count
count:=0
нц для i от 1 до N 
если A[i] = X то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_41.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_zadannomu_znache_41 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_zadannomu_znache_41: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_zadannomu_znache_41: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_zadannomu_znache_41: {e}")


def test_arrkum_Opredelite_kolichestvo_polozhitelnyh_elementov_massiva_A_42(tmp_path):
    """
    Тест для задачи: Определите количество положительных элементов массива А (ID: 42)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, count
count:=0
нц для i от 1 до N 
если A[i] > 0 то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_42.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_kolichestvo_polozhitelnyh_elementov_massiva_A_42 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_kolichestvo_polozhitelnyh_elementov_massiva_A_42: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_kolichestvo_polozhitelnyh_elementov_massiva_A_42: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_kolichestvo_polozhitelnyh_elementov_massiva_A_42: {e}")


def test_arrkum_Opredelite_kolichestvo_chyotnyh_i_nechyotnyh_elementov_massi_43(tmp_path):
    """
    Тест для задачи: Определите количество чётных и нечётных элементов массива А (ID: 43)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез цел
  N := 5
  A[1:N] := 0
  цел := 0
  __Решение__(N, A[1:N], цел)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел R, Q)
нач
цел i
R:=0; Q:=0
нц для i от 1 до N 
если mod(A[i],2) = 0 то
R:=R+1
иначе
Q:=Q+1
все
кц
кон
|-------------------------------------------------------
| Вывод массива 
|-------------------------------------------------------
алг __Вывод массива__(цел N, целтаб A[1:N]) 
нач
цел i
нц для i от 1 до N 
вывод A[i]," "
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел N, целтаб A[1:N], цел R, R0, Q, Q0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Получен ответ:    чётных ", R, ", нечётных ", Q
вывод нс, "Правильный ответ: чётных ", R0, ", нечётных ", Q0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_43.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_kolichestvo_chyotnyh_i_nechyotnyh_elementov_massi_43 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_kolichestvo_chyotnyh_i_nechyotnyh_elementov_massi_43: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_kolichestvo_chyotnyh_i_nechyotnyh_elementov_massi_43: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_kolichestvo_chyotnyh_i_nechyotnyh_elementov_massi_43: {e}")


def test_arrkum_Opredelite_kolichestvo_chyotnyh_polozhitelnyh_elementov_mass_44(tmp_path):
    """
    Тест для задачи: Определите, количество чётных положительных элементов массива А (ID: 44)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, count
count:=0
нц для i от 1 до N 
если mod(A[i],2) = 0 и A[i] > 0 то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_44.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_kolichestvo_chyotnyh_polozhitelnyh_elementov_mass_44 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_kolichestvo_chyotnyh_polozhitelnyh_elementov_mass_44: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_kolichestvo_chyotnyh_polozhitelnyh_elementov_mass_44: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_kolichestvo_chyotnyh_polozhitelnyh_elementov_mass_44: {e}")


def test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_45(tmp_path):
    """
    Тест для задачи: Найти количество элементов массива, в десятичной записи которых предпоследняя цифра (число десятков) - 5 (ID: 45)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, count
count:=0
нц для i от 1 до N 
если mod(div(A[i],10),10) = 5 то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_45.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_45 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_45: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_45: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_45: {e}")


def test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_46(tmp_path):
    """
    Тест для задачи: Найти количество элементов массива, в десятичной записи которых последняя и предпоследняя цифры одинаковые (ID: 46)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, count
count:=0
нц для i от 1 до N 
если mod(div(A[i],10),10) = mod(A[i],10) то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_46.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_46 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_46: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_46: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_46: {e}")


def test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_50(tmp_path):
    """
    Тест для задачи: Вычислить сумму всех элементов массива A (ID: 50)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum
sum:=0
нц для i от 1 до N 
sum:=sum+A[i]
кц
знач:=sum
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_50.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_50 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_50: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_50: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_50: {e}")


def test_arrkum_Vychislit_summu_otritsatelnyh_elementov_massiva_A_51(tmp_path):
    """
    Тест для задачи: Вычислить сумму отрицательных элементов массива A (ID: 51)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum
sum:=0
нц для i от 1 до N 
если A[i] < 0 то
sum:=sum+A[i]
все
кц
знач:=sum
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_51.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vychislit_summu_otritsatelnyh_elementov_massiva_A_51 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vychislit_summu_otritsatelnyh_elementov_massiva_A_51: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vychislit_summu_otritsatelnyh_elementov_massiva_A_51: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vychislit_summu_otritsatelnyh_elementov_massiva_A_51: {e}")


def test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_kotorye_delyatsya_n_52(tmp_path):
    """
    Тест для задачи: Вычислить сумму всех элементов массива A, которые делятся на 3 (ID: 52)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum
sum:=0
нц для i от 1 до N 
если mod(A[i],3) = 0 то
sum:=sum+A[i]
все
кц
знач:=sum
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_52.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_kotorye_delyatsya_n_52 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_kotorye_delyatsya_n_52: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_kotorye_delyatsya_n_52: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_kotorye_delyatsya_n_52: {e}")


def test_arrkum_Vychislit_srednee_arifmeticheskoe_vseh_elementov_massiva_A_k_53(tmp_path):
    """
    Тест для задачи: Вычислить среднее арифметическое всех элементов массива A, которые меньше, чем 50 (ID: 53)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг вещ __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum=0, count=0
нц для i от 1 до N 
если A[i] < 50 то
sum:=sum+A[i]
count:=count+1
все
кц
знач:=sum/count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_53.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vychislit_srednee_arifmeticheskoe_vseh_elementov_massiva_A_k_53 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vychislit_srednee_arifmeticheskoe_vseh_elementov_massiva_A_k_53: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vychislit_srednee_arifmeticheskoe_vseh_elementov_massiva_A_k_53: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vychislit_srednee_arifmeticheskoe_vseh_elementov_massiva_A_k_53: {e}")


def test_arrkum_Vychislit_proizvedenie_vseh_chyotnyh_polozhitelnyh_elementov_54(tmp_path):
    """
    Тест для задачи: Вычислить произведение всех чётных положительных элементов массива A (ID: 54)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, prod = 1
нц для i от 1 до N 
если A[i] > 0 и mod(A[i],2) = 0 то
prod:=prod*A[i]
все
кц
знач:=prod
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_54.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vychislit_proizvedenie_vseh_chyotnyh_polozhitelnyh_elementov_54 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vychislit_proizvedenie_vseh_chyotnyh_polozhitelnyh_elementov_54: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vychislit_proizvedenie_vseh_chyotnyh_polozhitelnyh_elementov_54: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vychislit_proizvedenie_vseh_chyotnyh_polozhitelnyh_elementov_54: {e}")


def test_arrkum_Nayti_summu_vseh_elementov_massiva_A_u_kotoryh_chislo_desyat_55(tmp_path):
    """
    Тест для задачи: Найти сумму всех элементов массива A, у которых число десятков (вторая с конца цифра десятичной записи) больше, чем число единиц (ID: 55)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum=0
нц для i от 1 до N 
если mod(div(A[i],10),10) > mod(A[i],10) то
sum:=sum+A[i]
все
кц
знач:=sum
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_55.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_summu_vseh_elementov_massiva_A_u_kotoryh_chislo_desyat_55 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_summu_vseh_elementov_massiva_A_u_kotoryh_chislo_desyat_55: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_summu_vseh_elementov_massiva_A_u_kotoryh_chislo_desyat_55: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_summu_vseh_elementov_massiva_A_u_kotoryh_chislo_desyat_55: {e}")


def test_arrkum_Vse_elementy_massiva_A_tryohznachnye_chisla_56(tmp_path):
    """
    Тест для задачи: Все элементы массива A - трёхзначные числа (ID: 56)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum=0
нц для i от 1 до N 
если mod(div(A[i],10),10) = mod(A[i],10) и div(A[i],100) = mod(A[i],10) то
sum:=sum+A[i]
все
кц
знач:=sum
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_56.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vse_elementy_massiva_A_tryohznachnye_chisla_56 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vse_elementy_massiva_A_tryohznachnye_chisla_56: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vse_elementy_massiva_A_tryohznachnye_chisla_56: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vse_elementy_massiva_A_tryohznachnye_chisla_56: {e}")


def test_arrkum_Opredelite_v_massive_A_nomer_pervogo_elementa_ravnogo_X_60(tmp_path):
    """
    Тест для задачи: Определите в массиве A номер первого элемента, равного X (ID: 60)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, nomerX=-1
нц для i от 1 до N
если A[i] = X то
nomerX:=i
выход
все
кц
знач:=nomerX
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_60.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_v_massive_A_nomer_pervogo_elementa_ravnogo_X_60 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_v_massive_A_nomer_pervogo_elementa_ravnogo_X_60: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_v_massive_A_nomer_pervogo_elementa_ravnogo_X_60: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_v_massive_A_nomer_pervogo_elementa_ravnogo_X_60: {e}")


def test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_v_pervoy_polovin_61(tmp_path):
    """
    Тест для задачи: Определите номер первого элемента, равного X, в первой половине массива A (массив имеет чётное число элементов) (ID: 61)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, nomerX=-1
нц для i от 1 до div(N,2)
если A[i] = X то
nomerX:=i
выход
все
кц
знач:=nomerX
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_61.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_v_pervoy_polovin_61 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_v_pervoy_polovin_61: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_v_pervoy_polovin_61: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_v_pervoy_polovin_61: {e}")


def test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_vo_vtoroy_polovi_62(tmp_path):
    """
    Тест для задачи: Определите номер первого элемента, равного X, во второй половине массива A (массив имеет чётное число элементов) (ID: 62)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, nomerX=-1
нц для i от div(N,2)+1 до N
если A[i] = X то
nomerX:=i
выход
все
кц
знач:=nomerX
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_62.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_vo_vtoroy_polovi_62 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_vo_vtoroy_polovi_62: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_vo_vtoroy_polovi_62: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_vo_vtoroy_polovi_62: {e}")


def test_arrkum_Opredelite_nomer_poslednego_elementa_ravnogo_X_vo_vtoroy_pol_63(tmp_path):
    """
    Тест для задачи: Определите номер последнего элемента, равного X, во второй половине массива A (массив имеет чётное число элементов) (ID: 63)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, nomerX=-1
нц для i от div(N,2) до N
если A[i] = X то
nomerX:=i
все
кц
знач:=nomerX
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_63.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_nomer_poslednego_elementa_ravnogo_X_vo_vtoroy_pol_63 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_nomer_poslednego_elementa_ravnogo_X_vo_vtoroy_pol_63: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_nomer_poslednego_elementa_ravnogo_X_vo_vtoroy_pol_63: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_nomer_poslednego_elementa_ravnogo_X_vo_vtoroy_pol_63: {e}")


def test_arrkum_Opredelite_skolko_est_elementov_ravnyh_X_v_pervoy_polovine_m_64(tmp_path):
    """
    Тест для задачи: Определите, сколько есть элементов, равных X, в первой половине массива A (массив имеет чётное число элементов) (ID: 64)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, countX = 0
нц для i от 1 до div(N,2)
если A[i] = X то
countX:=countX + 1
все
кц
знач:=countX
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_64.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_skolko_est_elementov_ravnyh_X_v_pervoy_polovine_m_64 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_skolko_est_elementov_ravnyh_X_v_pervoy_polovine_m_64: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_skolko_est_elementov_ravnyh_X_v_pervoy_polovine_m_64: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_skolko_est_elementov_ravnyh_X_v_pervoy_polovine_m_64: {e}")


def test_arrkum_Opredelite_skolko_v_massive_A_par_sosednih_elementov_znachen_65(tmp_path):
    """
    Тест для задачи: Определите, сколько в массиве A пар соседних элементов, значения которых одинаковы и равны заданному X (ID: 65)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, count = 0
нц для i от 1 до N-1
если A[i]=X и A[i+1]=X то
count:=count + 1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_65.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Opredelite_skolko_v_massive_A_par_sosednih_elementov_znachen_65 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Opredelite_skolko_v_massive_A_par_sosednih_elementov_znachen_65: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Opredelite_skolko_v_massive_A_par_sosednih_elementov_znachen_65: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Opredelite_skolko_v_massive_A_par_sosednih_elementov_znachen_65: {e}")


def test_arrkum_Gorka_eto_tri_stoyaschih_podryad_elementa_massiva_A_iz_kotor_66(tmp_path):
    """
    Тест для задачи: Горка - это три стоящих подряд элемента массива A, из которых средний ("вершина") имеет наибольшее значение, а два крайних - меньше него (ID: 66)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N], арг цел X)
нач
цел i, count = 0
нц для i от 1 до N-2
если A[i]<X и A[i+1]=X и A[i+2]<X то
count:=count + 1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_66.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Gorka_eto_tri_stoyaschih_podryad_elementa_massiva_A_iz_kotor_66 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Gorka_eto_tri_stoyaschih_podryad_elementa_massiva_A_iz_kotor_66: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Gorka_eto_tri_stoyaschih_podryad_elementa_massiva_A_iz_kotor_66: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Gorka_eto_tri_stoyaschih_podryad_elementa_massiva_A_iz_kotor_66: {e}")


def test_arrkum_Elementy_massiva_A_proizvolnye_naturalnye_chisla_71(tmp_path):
    """
    Тест для задачи: Элементы массива A - произвольные натуральные числа (ID: 71)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, count, digit, elem
лог OK
count:=0
нц для i от 1 до N
elem:=A[i]
digit:=mod(elem,10)
elem:=div(elem,10)
OK:=да
нц пока elem > 0
если mod(elem,10)<>digit то
OK:=нет
выход
все
elem:=div(elem,10)
кц
если OK то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_71.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Elementy_massiva_A_proizvolnye_naturalnye_chisla_71 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Elementy_massiva_A_proizvolnye_naturalnye_chisla_71: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Elementy_massiva_A_proizvolnye_naturalnye_chisla_71: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Elementy_massiva_A_proizvolnye_naturalnye_chisla_71: {e}")


def test_arrkum_Naydite_v_massive_A_samuyu_dlinnuyu_tsepochku_raspolozhennyh_72(tmp_path):
    """
    Тест для задачи: Найдите в массиве A самую длинную цепочку расположенных друг за другом одинаковых значений и вычислите её длину (ID: 72)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, Lmax = 0, L = 1
нц для i от 2 до N
если A[i-1] = A[i] то
L:=L + 1
если L > Lmax то Lmax:=L все
иначе
L:=1
все
кц
знач:=Lmax
кон
|-------------------------------------------------------
| Вывод массива 
|-------------------------------------------------------
алг __Вывод массива__(цел N, целтаб A[1:N]) 
нач
цел i
нц для i от 1 до N 
вывод A[i]," "
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел N, целтаб A[1:N], цел R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Получен ответ:    ", R
вывод нс, "Правильный ответ: ", R0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_72.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Naydite_v_massive_A_samuyu_dlinnuyu_tsepochku_raspolozhennyh_72 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Naydite_v_massive_A_samuyu_dlinnuyu_tsepochku_raspolozhennyh_72: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Naydite_v_massive_A_samuyu_dlinnuyu_tsepochku_raspolozhennyh_72: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Naydite_v_massive_A_samuyu_dlinnuyu_tsepochku_raspolozhennyh_72: {e}")


def test_arrkum_Vse_elementy_massiva_A_nahodyatsya_v_diapazone_ot_2_do_1000_73(tmp_path):
    """
    Тест для задачи: Все элементы массива A находятся в диапазоне от 2 до 1000 (ID: 73)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, k, count=0
нц для i от 1 до N
нц для k от 1 до __NP__
если A[i] = __Primes__[k]  то
count:=count+1
выход
все
кц
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_73.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Vse_elementy_massiva_A_nahodyatsya_v_diapazone_ot_2_do_1000_73 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Vse_elementy_massiva_A_nahodyatsya_v_diapazone_ot_2_do_1000_73: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Vse_elementy_massiva_A_nahodyatsya_v_diapazone_ot_2_do_1000_73: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Vse_elementy_massiva_A_nahodyatsya_v_diapazone_ot_2_do_1000_73: {e}")


def test_arrkum_Zapolnit_massiv_A_pervymi_N_prostymi_chislami_nachinaya_c_2_74(tmp_path):
    """
    Тест для задачи: Заполнить массив A первыми N простыми числами (начиная c 2) (ID: 74)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_74.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnit_massiv_A_pervymi_N_prostymi_chislami_nachinaya_c_2_74 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnit_massiv_A_pervymi_N_prostymi_chislami_nachinaya_c_2_74: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnit_massiv_A_pervymi_N_prostymi_chislami_nachinaya_c_2_74: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnit_massiv_A_pervymi_N_prostymi_chislami_nachinaya_c_2_74: {e}")


def test_arrkum_Nayti_v_massive_A_vse_chisla_perevertyshi_kotorye_chitayutsy_75(tmp_path):
    """
    Тест для задачи: Найти в массиве A все числа-перевертыши, которые читаются одинаково слева направо и справа налево (например, 5, 44, 717, 1221), и вычислить их сумму (ID: 75)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, sum, d, elem
лог OK 
sum:=0
нц для i от 1 до N 
elem:=A[i]
d:=1
нц пока d < elem
d:=d*10
кц
d:=div(d,10);
OK:=да
нц пока d > 1
если mod(elem,10) <> div(elem,d) то
OK:=нет
выход
все
elem:=div(mod(elem,d),10)
d:=div(d,100)
кц
если OK то
sum:=sum+A[i]
все
кц
знач:=sum
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_75.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Nayti_v_massive_A_vse_chisla_perevertyshi_kotorye_chitayutsy_75 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Nayti_v_massive_A_vse_chisla_perevertyshi_kotorye_chitayutsy_75: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Nayti_v_massive_A_vse_chisla_perevertyshi_kotorye_chitayutsy_75: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Nayti_v_massive_A_vse_chisla_perevertyshi_kotorye_chitayutsy_75: {e}")


def test_arrkum_Zapolnit_massiv_A_pervymi_N_giperprostymi_chislami_76(tmp_path):
    """
    Тест для задачи: Заполнить массив A первыми N гиперпростыми числами (ID: 76)
    Курс: arrkum
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  N := 5
  A[1:N] := 0
  __Решение__(N, A[1:N])
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, аргрез целтаб A[1:N])
нач
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_76.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum_Zapolnit_massiv_A_pervymi_N_giperprostymi_chislami_76 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum_Zapolnit_massiv_A_pervymi_N_giperprostymi_chislami_76: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum_Zapolnit_massiv_A_pervymi_N_giperprostymi_chislami_76: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum_Zapolnit_massiv_A_pervymi_N_giperprostymi_chislami_76: {e}")

