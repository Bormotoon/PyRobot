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

# Автогенерированные тесты для курса: arrkum2
# Сгенерировано: 2025-06-09 11:48:59

def test_arrkum2_Perestavit_vse_elementy_massiva_v_obratnom_poryadke_10(tmp_path):
    """
    Тест для задачи: Переставить все элементы массива в обратном порядке (ID: 10)
    Курс: arrkum2
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
цел i, k, temp
нц для i от 1 до div(N,2)
k:= N - i + 1
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_10.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_vse_elementy_massiva_v_obratnom_poryadke_10 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_vse_elementy_massiva_v_obratnom_poryadke_10: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_vse_elementy_massiva_v_obratnom_poryadke_10: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_vse_elementy_massiva_v_obratnom_poryadke_10: {e}")


def test_arrkum2_Perestavit_vse_elementy_massiva_krome_poslednego_v_obratnom_11(tmp_path):
    """
    Тест для задачи: Переставить все элементы массива, кроме последнего, в обратном порядке (ID: 11)
    Курс: arrkum2
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
цел i, k, temp
нц для i от 1 до div(N-1,2)
k:= N - i
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_11.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_vse_elementy_massiva_krome_poslednego_v_obratnom_11 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_vse_elementy_massiva_krome_poslednego_v_obratnom_11: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_vse_elementy_massiva_krome_poslednego_v_obratnom_11: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_vse_elementy_massiva_krome_poslednego_v_obratnom_11: {e}")


def test_arrkum2_Perestavit_vse_elementy_massiva_krome_pervogo_v_obratnom_por_12(tmp_path):
    """
    Тест для задачи: Переставить все элементы массива, кроме первого, в обратном порядке (ID: 12)
    Курс: arrkum2
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
цел i, k, temp
нц для i от 2 до div(N-1,2)+1
k:= N - i + 2
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_12.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_vse_elementy_massiva_krome_pervogo_v_obratnom_por_12 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_vse_elementy_massiva_krome_pervogo_v_obratnom_por_12: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_vse_elementy_massiva_krome_pervogo_v_obratnom_por_12: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_vse_elementy_massiva_krome_pervogo_v_obratnom_por_12: {e}")


def test_arrkum2_Perestavit_vse_elementy_v_pervoy_polovine_massiva_v_obratnom_13(tmp_path):
    """
    Тест для задачи: Переставить все элементы в первой половине массива в обратном порядке (ID: 13)
    Курс: arrkum2
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
цел i, k, temp
нц для i от 1 до div(N,4)
k:= div(N,2) - i + 1
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_13.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_vse_elementy_v_pervoy_polovine_massiva_v_obratnom_13 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_vse_elementy_v_pervoy_polovine_massiva_v_obratnom_13: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_vse_elementy_v_pervoy_polovine_massiva_v_obratnom_13: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_vse_elementy_v_pervoy_polovine_massiva_v_obratnom_13: {e}")


def test_arrkum2_Perestavit_elementy_v_kazhdoy_pare_1_yy_so_2_m_3_y_s_4_m_i_t_14(tmp_path):
    """
    Тест для задачи: Переставить элементы в каждой паре: 1-ый со 2-м, 3-й с 4-м и т (ID: 14)
    Курс: arrkum2
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
цел i, temp
нц для i от 1 до N-1 шаг 2
temp:=A[i]; A[i]:=A[i+1]; A[i+1]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_14.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_elementy_v_kazhdoy_pare_1_yy_so_2_m_3_y_s_4_m_i_t_14 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_elementy_v_kazhdoy_pare_1_yy_so_2_m_3_y_s_4_m_i_t_14: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_elementy_v_kazhdoy_pare_1_yy_so_2_m_3_y_s_4_m_i_t_14: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_elementy_v_kazhdoy_pare_1_yy_so_2_m_3_y_s_4_m_i_t_14: {e}")


def test_arrkum2_Perestavit_vse_elementy_vo_vtoroy_polovine_massiva_v_obratno_15(tmp_path):
    """
    Тест для задачи: Переставить все элементы во второй половине массива в обратном порядке (ID: 15)
    Курс: arrkum2
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
цел i, k, temp, H
H:= div(N,2)
нц для i от H+1 до div(3*N,4)
k:= N + H + 1 - i
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_15.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_vse_elementy_vo_vtoroy_polovine_massiva_v_obratno_15 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_vse_elementy_vo_vtoroy_polovine_massiva_v_obratno_15: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_vse_elementy_vo_vtoroy_polovine_massiva_v_obratno_15: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_vse_elementy_vo_vtoroy_polovine_massiva_v_obratno_15: {e}")


def test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_polovine_massiva_v_obratno_16(tmp_path):
    """
    Тест для задачи: Переставить все элементы в каждой половине массива в обратном порядке (ID: 16)
    Курс: arrkum2
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
цел i, k, temp, H
H:= div(N,2)
нц для i от 1 до div(H,2)
k:= H + 1 - i
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
нц для i от H+1 до div(3*N,4)
k:= N + H + 1 - i
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_16.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_polovine_massiva_v_obratno_16 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_polovine_massiva_v_obratno_16: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_polovine_massiva_v_obratno_16: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_polovine_massiva_v_obratno_16: {e}")


def test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_treti_massiva_v_obratnom_p_17(tmp_path):
    """
    Тест для задачи: Переставить все элементы в каждой трети массива в обратном порядке (ID: 17)
    Курс: arrkum2
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
цел i, k, temp, H, M
H:= div(N,3)
M:= 2*H
нц для i от 1 до div(H,2)
k:= H + 1 - i
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
нц для i от H+1 до div(N,2)
k:= M + H + 1 - i
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
нц для i от M+1 до div(5*N,6)
k:= N + M + 1 - i
temp:=A[i]; A[i]:=A[k]; A[k]:=temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_17.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_treti_massiva_v_obratnom_p_17 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_treti_massiva_v_obratnom_p_17: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_treti_massiva_v_obratnom_p_17: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_treti_massiva_v_obratnom_p_17: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_1_pozitsiyu_20(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг массива влево на 1 позицию (ID: 20)
    Курс: arrkum2
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
цел i, temp
temp:= A[1]
нц для i от 1 до N-1
A[i]:=A[i+1]
кц
A[N]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_20.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_1_pozitsiyu_20 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_1_pozitsiyu_20: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_1_pozitsiyu_20: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_1_pozitsiyu_20: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_vl_21(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг всех элементов, кроме первого, влево на 1 позицию (ID: 21)
    Курс: arrkum2
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
цел i, temp
temp:= A[2]
нц для i от 2 до N-1
A[i]:=A[i+1]
кц
A[N]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_21.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_vl_21 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_vl_21: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_vl_21: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_vl_21: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_poslednego_22(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг всех элементов, кроме последнего, влево на 1 позицию (ID: 22)
    Курс: arrkum2
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
цел i, temp
temp:= A[1]
нц для i от 1 до N-2
A[i]:=A[i+1]
кц
A[N-1]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_22.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_poslednego_22 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_poslednego_22: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_poslednego_22: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_poslednego_22: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_23(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг всех элементов, кроме первого и последнего, влево на 1 позицию (ID: 23)
    Курс: arrkum2
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
цел i, temp
temp:= A[2]
нц для i от 2 до N-2
A[i]:=A[i+1]
кц
A[N-1]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_23.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_23 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_23: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_23: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_23: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_1_pozitsiyu_24(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг массива вправо на 1 позицию (ID: 24)
    Курс: arrkum2
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
цел i, temp
temp:= A[N]
нц для i от N-1 до 1 шаг -1
A[i+1]:=A[i]
кц
A[1]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_24.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_1_pozitsiyu_24 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_1_pozitsiyu_24: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_1_pozitsiyu_24: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_1_pozitsiyu_24: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_pervoy_po_25(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг вправо на 1 позицию первой половины массива (ID: 25)
    Курс: arrkum2
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
цел i, temp, H
H:= div(N,2)
temp:= A[H]
нц для i от H до 2 шаг -1
A[i]:=A[i-1]
кц
A[1]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_25.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_pervoy_po_25 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_pervoy_po_25: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_pervoy_po_25: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_pervoy_po_25: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_vtoroy_po_26(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг вправо на 1 позицию второй половины массива (ID: 26)
    Курс: arrkum2
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
цел i, temp, H
H:= div(N,2)+1
temp:= A[N]
нц для i от N до H+1 шаг -1
A[i]:=A[i-1]
кц
A[H]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_26.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_vtoroy_po_26 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_vtoroy_po_26: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_vtoroy_po_26: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_vtoroy_po_26: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_27(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг всех элементов, кроме первого и последнего, вправо на 1 позицию (ID: 27)
    Курс: arrkum2
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
цел i, temp
temp:= A[N-1]
нц для i от N-2 до 2 шаг -1
A[i+1]:=A[i]
кц
A[2]:= temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_27.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_27 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_27: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_27: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_27: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_4_pozitsii_28(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг массива влево на 4 позиции (ID: 28)
    Курс: arrkum2
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
цел i, temp, k
нц для k от 1 до 4
temp:= A[1]
нц для i от 1 до N-1
A[i]:=A[i+1]
кц
A[N]:= temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_28.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_4_pozitsii_28 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_4_pozitsii_28: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_4_pozitsii_28: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_4_pozitsii_28: {e}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_4_pozitsii_29(tmp_path):
    """
    Тест для задачи: Выполнить циклический сдвиг массива вправо на 4 позиции (ID: 29)
    Курс: arrkum2
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
цел i, temp, k
нц для k от 1 до 4
temp:= A[N]
нц для i от N-1 до 1 шаг -1
A[i+1]:=A[i]
кц
A[1]:= temp
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_29.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_4_pozitsii_29 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_4_pozitsii_29: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_4_pozitsii_29: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_4_pozitsii_29: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_i_za_30(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все положительные элементы массива A и записать их количество 
в переменную count (ID: 30)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если A[i]>0 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_30.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_i_za_30 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_i_za_30: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_i_za_30: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_i_za_30: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_otritsatelnye_elementy_massiva_A_i_za_31(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все отрицательные элементы массива A и 
   записать их количество в переменную count (ID: 31)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если A[i]<0 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_31.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_otritsatelnye_elementy_massiva_A_i_za_31 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_otritsatelnye_elementy_massiva_A_i_za_31: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_otritsatelnye_elementy_massiva_A_i_za_31: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_otritsatelnye_elementy_massiva_A_i_za_31: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_elementy_massiva_A_i_zapisat_32(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все чётные элементы массива A и 
   записать их количество в переменную count (ID: 32)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если mod(A[i],2) = 0 то
count:=count+1
B[count]:=A[i]
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
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_elementy_massiva_A_i_zapisat_32 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_elementy_massiva_A_i_zapisat_32: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_elementy_massiva_A_i_zapisat_32: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_elementy_massiva_A_i_zapisat_32: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_elementy_massiva_A_i_zapis_33(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все нечётные элементы массива A и 
   записать их количество в переменную count (ID: 33)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если mod(A[i],2) <> 0 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_33.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_elementy_massiva_A_i_zapis_33 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_elementy_massiva_A_i_zapis_33: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_elementy_massiva_A_i_zapis_33: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_elementy_massiva_A_i_zapis_33: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_polozhitelnye_elementy_mas_34(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все нечётные положительные элементы массива A и 
   записать их количество в переменную count (ID: 34)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если mod(A[i],2) <> 0 и A[i] > 0 то
count:=count+1
B[count]:=A[i]
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
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_polozhitelnye_elementy_mas_34 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_polozhitelnye_elementy_mas_34: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_polozhitelnye_elementy_mas_34: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_polozhitelnye_elementy_mas_34: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_otritsatelnye_elementy_massi_35(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все чётные отрицательные элементы массива A и 
   записать их количество в переменную count (ID: 35)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если mod(A[i],2) = 0 и A[i] < 0 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_35.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_otritsatelnye_elementy_massi_35 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_otritsatelnye_elementy_massi_35: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_otritsatelnye_elementy_massi_35: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_otritsatelnye_elementy_massi_35: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_koto_36(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все положительные элементы массива A, которые делятся на 10, и 
   записать их количество в переменную count (ID: 36)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если mod(A[i],10) = 0 и A[i] > 0 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_36.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_koto_36 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_koto_36: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_koto_36: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_koto_36: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_desy_37(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все положительные элементы массива A, десятичная запись которых оканчивается на 6, и 
   записать их количество в переменную count (ID: 37)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если mod(A[i],10) = 6 и A[i] > 0 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_37.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_desy_37 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_desy_37: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_desy_37: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_desy_37: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_v_de_38(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все положительные элементы массива A, в десятичной записи которых 
   вторая цифра (число десятков) равна 6, и 
   записать их количество в переменную count (ID: 38)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если mod(div(A[i],10),10) = 6 и A[i] > 0 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_38.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_v_de_38 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_v_de_38: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_v_de_38: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_v_de_38: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_predstavly_39(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все элементы массива A, которые представляют собой простые числа, и
записать их количество в переменную count (ID: 39)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если __Простое__(A[i]) то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_39.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_predstavly_39 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_predstavly_39: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_predstavly_39: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_predstavly_39: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_u_kotoryh_summa_ts_310(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все элементы массива A, у которых сумма цифр равна 10, и
 записать их количество в переменную count (ID: 310)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i
count:=0
нц для i от 1 до N
если __Сумма цифр__(A[i]) = 10 то
count:=count+1
B[count]:=A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_310.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_u_kotoryh_summa_ts_310 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_u_kotoryh_summa_ts_310: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_u_kotoryh_summa_ts_310: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_u_kotoryh_summa_ts_310: {e}")


def test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_vstrechayu_311(tmp_path):
    """
    Тест для задачи: Отобрать в массив B все элементы массива A, которые встречаются в массива более одного 
раза, и записать их количество в переменную count (ID: 311)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  цел N
  целтаб A[1:N]
  рез целтаб
  цел count
  N := 5
  A[1:N] := 0
  целтаб := 0
  count := 5
  __Решение__(N, A[1:N], целтаб, count)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__ (цел N, целтаб A[1:N], рез целтаб B[1:N], цел count)
нач
цел i, k, j
лог уже
count:= 0
нц для i от 1 до N
уже:=нет
нц для j от 1 до count
если B[j] = A[i] то
уже:=да
выход
все
кц
если не уже то
k:= 1
нц для j от i+1 до N
если A[j] = A[i] то
k:= k+1
выход
все
кц
если k > 1 то
count:=count+1
B[count]:=A[i]
все
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_311.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_vstrechayu_311 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_vstrechayu_311: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_vstrechayu_311: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_vstrechayu_311: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_40(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию (ID: 40)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 1 до N-1
нц для j от 1 до N-i
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_40.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_40 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_40: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_40: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_40: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_41(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по убыванию (ID: 41)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 1 до N-1
нц для j от 1 до N-i
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_41.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_41 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_41: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_41: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_41: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_42(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива, кроме последнего, по убыванию (ID: 42)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 1 до N-2
нц для j от 1 до N-2
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_42.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_42 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_42: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_42: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_42: {e}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_43(tmp_path):
    """
    Тест для задачи: Выполнить сортировку первой половины массива по возрастанию (ID: 43)
    Курс: arrkum2
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
цел i, j, temp, H
H:=div(N,2)
нц для i от 1 до H-1
нц для j от 1 до H-i
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_43.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_43 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_43: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_43: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_43: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_44(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива, кроме первого, по убыванию (ID: 44)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 2 до N-1
нц для j от 2 до N-i+1
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_44.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_44 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_44: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_44: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_44: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_45(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива, кроме первого и последнего, по возрастанию (ID: 45)
    Курс: arrkum2
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
цел i, j, temp, H
H:=N-1
нц для i от 2 до H-1
нц для j от 2 до H-i+1
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_45.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_45 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_45: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_45: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_45: {e}")


def test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_46(tmp_path):
    """
    Тест для задачи: Выполнить сортировку второй половины массива по убыванию (ID: 46)
    Курс: arrkum2
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
цел i, j, temp, H
H:=div(N,2)+1
нц для i от H до N-1
нц для j от H до N-1
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_46.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_46 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_46: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_46: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_46: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_47(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию последней цифры в десятичной 
записи числа (ID: 47)
    Курс: arrkum2
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
цел i, j, temp, m1, m2
нц для i от 1 до N-1
нц для j от 1 до N-i
m1:=mod(A[j],10)
m2:=mod(A[j+1],10)
если m1>m2 или m1=m2 и A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все

кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_47.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_47 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_47: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_47: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_47: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_48(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию и записать число перестановок
в переменную count (ID: 48)
    Курс: arrkum2
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

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел R)
нач
цел i, j, temp
R:=0
нц для i от 1 до N-1
нц для j от 1 до N-i
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
R:=R+1
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_48.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_48 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_48: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_48: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_48: {e}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_49(tmp_path):
    """
    Тест для задачи: Выполнить сортировку первой половины массива - по возрастанию, а второй половины -
по убыванию (ID: 49)
    Курс: arrkum2
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
цел i, j, temp, H
H:=div(N,2)
нц для i от 1 до H-1
нц для j от 1 до H-1
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
H:=H+1
нц для i от H до N-1
нц для j от H до N-1
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_49.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_49 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_49: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_49: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_49: {e}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_410(tmp_path):
    """
    Тест для задачи: Выполнить сортировку первой половины массива - по возрастанию, а второй половины -
по убыванию (ID: 410)
    Курс: arrkum2
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

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел R)
нач
цел i, j, temp, H
R:=0
H:=div(N,2)
нц для i от 1 до H-1
нц для j от 1 до H-1
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
R:=R+1
все
кц
кц
H:=H+1
нц для i от H до N-1
нц для j от H до N-1
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
R:=R+1
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_410.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_410 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_410: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_410: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_410: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_411(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию суммы цифр в десятичной 
записи числа (ID: 411)
    Курс: arrkum2
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
цел i, j, temp, m1, m2
целтаб S[1:N]
нц для i от 1 до N
S[i]:=__Сумма цифр__(A[i])
кц
нц для i от 1 до N-1
нц для j от N-1 до i шаг -1
m1:=S[j]
m2:=S[j+1]
если m1>m2 или m1=m2 и A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
temp:=S[j]; S[j]:=S[j+1]; S[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_411.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_411 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_411: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_411: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_411: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_50(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию (ID: 50)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 1 до N-1
нц для j от 1 до N-i
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_50.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_50 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_50: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_50: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_50: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_51(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по убыванию (ID: 51)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 1 до N-1
нц для j от 1 до N-i
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_51.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_51 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_51: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_51: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_51: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_52(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива, кроме последнего, по убыванию (ID: 52)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 1 до N-2
нц для j от 1 до N-2
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_52.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_52 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_52: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_52: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_52: {e}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_53(tmp_path):
    """
    Тест для задачи: Выполнить сортировку первой половины массива по возрастанию (ID: 53)
    Курс: arrkum2
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
цел i, j, temp, H
H:=div(N,2)
нц для i от 1 до H-1
нц для j от 1 до H-i
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_53.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_53 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_53: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_53: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_53: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_54(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива, кроме первого, по убыванию (ID: 54)
    Курс: arrkum2
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
цел i, j, temp
нц для i от 2 до N-1
нц для j от 2 до N-i+1
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_54.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_54 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_54: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_54: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_54: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_55(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива, кроме первого и последнего, по возрастанию (ID: 55)
    Курс: arrkum2
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
цел i, j, temp, H
H:=N-1
нц для i от 2 до H-1
нц для j от 2 до H-i+1
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_55.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_55 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_55: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_55: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_55: {e}")


def test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_56(tmp_path):
    """
    Тест для задачи: Выполнить сортировку второй половины массива по убыванию (ID: 56)
    Курс: arrkum2
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
цел i, j, temp, H
H:=div(N,2)+1
нц для i от H до N-1
нц для j от H до N-1
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_56.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_56 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_56: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_56: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_56: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_57(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию последней цифры в десятичной 
записи числа (ID: 57)
    Курс: arrkum2
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
цел i, j, temp, m1, m2
нц для i от 1 до N-1
нц для j от 1 до N-i
m1:=mod(A[j],10)
m2:=mod(A[j+1],10)
если m1>m2 или m1=m2 и A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все

кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_57.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_57 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_57: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_57: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_57: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_58(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию и записать число перестановок
в переменную count (ID: 58)
    Курс: arrkum2
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

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел R)
нач
цел i, j, kMin, temp
R:=0
нц для i от 1 до N-1
kMin:=i
нц для j от i+1 до N
если A[j] < A[kMin] то
kMin:= j
все
кц
если kMin <> i то
temp:=A[kMin]; A[kMin]:=A[i]; A[i]:=temp
R:=R+1
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_58.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_58 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_58: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_58: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_58: {e}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_59(tmp_path):
    """
    Тест для задачи: Выполнить сортировку первой половины массива - по возрастанию, а второй половины -
по убыванию (ID: 59)
    Курс: arrkum2
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
цел i, j, temp, H
H:=div(N,2)
нц для i от 1 до H-1
нц для j от 1 до H-1
если A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
H:=H+1
нц для i от H до N-1
нц для j от H до N-1
если A[j]<A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_59.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_59 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_59: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_59: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_59: {e}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_510(tmp_path):
    """
    Тест для задачи: Выполнить сортировку первой половины массива - по возрастанию, а второй половины -
по убыванию (ID: 510)
    Курс: arrkum2
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

алг __Решение__ (цел N, аргрез целтаб A[1:N], рез цел R)
нач
цел i, j, temp, kMin, H
R:=0
H:=div(N,2)
нц для i от 1 до H-1
kMin:= i
нц для j от i+1 до H
если A[j] < A[kMin] то
kMin:= j
все
кц
если kMin <> i то
temp:=A[kMin]; A[kMin]:=A[i]; A[i]:=temp
R:=R+1
все
кц
H:=H+1
нц для i от H до N-1
kMin:= i
нц для j от i+1 до N
если A[j] > A[kMin] то
kMin:= j
все
кц
если kMin <> i то
temp:=A[kMin]; A[kMin]:=A[i]; A[i]:=temp
R:=R+1
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_510.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_510 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_510: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_510: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_510: {e}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_511(tmp_path):
    """
    Тест для задачи: Выполнить сортировку элементов массива по возрастанию суммы цифр в десятичной 
записи числа (ID: 511)
    Курс: arrkum2
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
цел i, j, temp, m1, m2
целтаб S[1:N]
нц для i от 1 до N
S[i]:=__Сумма цифр__(A[i])
кц
нц для i от 1 до N-1
нц для j от 1 до N-i
m1:=S[j]
m2:=S[j+1]
если m1>m2 или m1=m2 и A[j]>A[j+1] то
temp:=A[j]; A[j]:=A[j+1]; A[j+1]:=temp
temp:=S[j]; S[j]:=S[j+1]; S[j+1]:=temp
все

кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_511.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_511 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_511: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_511: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_511: {e}")


def test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_60(tmp_path):
    """
    Тест для задачи: Массив отсортирован по возрастанию (неубыванию) (ID: 60)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 5)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, целтаб A[1:N], цел X)
нач
цел L, R, nX, c
L:= 1; R:= N; nX:= -1 
нц пока R >= L
c:= div(R+L, 2);
если X = A[c]
то nX:= c; выход
все
если X < A[c] то R:= c - 1 все 
если X > A[c] то L:= c + 1 все 
кц
знач:=nX
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
алг __Ошибка__(цел N, целтаб A[1:N], цел X, R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Ищем значение:    ", X
вывод нс, "Получен ответ:    ", R
если 1 <= R <= N то
вывод "  (A[", R, "] = ", A[R], ")"
иначе
вывод " (нет элемента)" 
все
вывод нс, "Правильный ответ: ", R0
если 1 <= R0 <= N то
вывод "  (A[", R0, "] = ", A[R0], ")"
иначе
вывод " (нет элемента)" 
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_60.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_60 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_60: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_60: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_60: {e}")


def test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_61(tmp_path):
    """
    Тест для задачи: Массив отсортирован по убыванию (невозрастанию) (ID: 61)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 5)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, целтаб A[1:N], цел X)
нач
цел L, R, nX, c
L:= 1; R:= N; nX:= -1 
нц пока R >= L
c:= div(R+L, 2);
если X = A[c]
то nX:= c; выход
все
если X > A[c] то R:= c - 1 все 
если X < A[c] то L:= c + 1 все 
кц
знач:=nX
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
алг __Ошибка__(цел N, целтаб A[1:N], цел X, R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Ищем значение:    ", X
вывод нс, "Получен ответ:    ", R
если 1 <= R <= N то
вывод "  (A[", R, "] = ", A[R], ")"
иначе
вывод " (нет элемента)" 
все
вывод нс, "Правильный ответ: ", R0
если 1 <= R0 <= N то
вывод "  (A[", R0, "] = ", A[R0], ")"
иначе
вывод " (нет элемента)" 
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_61.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_61 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_61: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_61: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_61: {e}")


def test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_62(tmp_path):
    """
    Тест для задачи: Массив отсортирован по возрастанию (неубыванию) (ID: 62)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 5)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, целтаб A[1:N], цел X)
нач
цел L, R, nX, c
L:= 1; R:= N; nX:= -1 
знач:=0
нц пока R >= L
знач:=знач+1
c:= div(R+L, 2);
если X = A[c]
то nX:= c; выход
все
если X < A[c] то R:= c - 1 все 
если X > A[c] то L:= c + 1 все 
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
алг __Ошибка__(цел N, целтаб A[1:N], цел X, nX, nX0, R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Ищем значение:    ", X
вывод нс, "Получен ответ:    номер = ", nX
если 1 <= nX <= N то
вывод "  (A[", nX, "] = ", A[nX], ")"
иначе
вывод " (нет элемента)" 
все
вывод " шагов: ", R
вывод нс, "Правильный ответ: номер = ", nX0
если 1 <= nX0 <= N то
вывод "  (A[", nX0, "] = ", A[nX0], ")"
иначе
вывод " (нет элемента)" 
все
вывод " шагов: ", R0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_62.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_62 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_62: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_62: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_62: {e}")


def test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_63(tmp_path):
    """
    Тест для задачи: Массив отсортирован по убыванию (невозрастанию) (ID: 63)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0, 5)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, целтаб A[1:N], цел X)
нач
цел L, R, nX, c
L:= 1; R:= N; nX:= -1 
знач:=0
нц пока R >= L
знач:=знач+1
c:= div(R+L, 2);
если X = A[c]
то nX:= c; выход
все
если X > A[c] то R:= c - 1 все 
если X < A[c] то L:= c + 1 все 
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
алг __Ошибка__(цел N, целтаб A[1:N], цел X, nX, nX0, R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__(N, A)
вывод нс, "Ищем значение:    ", X
вывод нс, "Получен ответ:    номер = ", nX
если 1 <= nX <= N то
вывод "  (A[", nX, "] = ", A[nX], ")"
иначе
вывод " (нет элемента)" 
все
вывод " шагов: ", R
вывод нс, "Правильный ответ: номер = ", nX0
если 1 <= nX0 <= N то
вывод "  (A[", nX0, "] = ", A[nX0], ")"
иначе
вывод " (нет элемента)" 
все
вывод " шагов: ", R0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_63.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_63 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_63: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_63: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_63: {e}")


def test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_64(tmp_path):
    """
    Тест для задачи: Используя двоичный поиск, найти число X, куб которого равен заданному
   значению N (ID: 64)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  результат := Найти(5)
  вывод результат, нс
кон

алг цел Найти кубический корень (цел N)
дано | Натуральное число N, которое равно кубу
       | (третьей степени) некоторого натурального 
       | числа X, которое не больше 1000.
надо | Используя двоичный поиск, найти число X, 
       | куб которого равен N. Записать результат
       | в переменную X.
нач
цел X
цел L, R, c, c3
L:= 1; R:= imin(N,1000)
X:= 0
нц пока R >= L
c:= div(R+L, 2);
c3:= c*c*c
если N = c*c*c
то X := c; выход
все
если N < c3 то R:= c - 1 все 
если N > c3 то L:= c + 1 все 
кц
знач:=X
кон

алг цел @тестирование
нач
цел i, N=10
цел R, X3
целтаб R0[1:N] = {1, 3, 5, 9, 75, 178, 290, 350, 463, 512}
нц для i от 1 до N
X3:= R0[i]**3;
R := Найти кубический корень (X3)
знач:=__Сравнить__(R, R0[i])
если знач = 0 то 
__Ошибка__(X3, R, R0[i]); 
выход
все
кц
если знач = 10 то
вывод "Задание зачтено."
все
кон
|-------------------------------------------------------
| Функция возвращает 10, если результаты совпадают,
| и 0, если различаются
|-------------------------------------------------------
алг цел __Сравнить__ (цел R, R0)
нач
знач:=10
если R <> R0 то знач:=0; все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел X3, цел R, R0)
нач
вывод "Программа работает неверно!", нс
вывод "Куб числа:        ", X3, нс
вывод "Получен ответ:    ", R, нс
вывод "Правильный ответ: ", R0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_64.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_64 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_64: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_64: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_64: {e}")


def test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_65(tmp_path):
    """
    Тест для задачи: Используя двоичный поиск, найти число X, куб которого равен заданному значению
   N (ID: 65)
    Курс: arrkum2
    """
    kumir_code = '''алг
нач
  результат := Шаги(5, 0)
  вывод результат, нс
кон

алг цел Шаги кубический корень (цел N, рез цел X)
дано | Натуральное число N, которое равно кубу
       | (третьей степени) некоторого натурального 
       | числа X, которое не больше 1000.
надо | Используя двоичный поиск, найти число X, 
       | куб которого равен N. Записать в переменную 
       | X результат поиска, а в перемпенную "шаги"
       | количество шагов цикла  (сколько раз вычислялась
       | середина интервала поиска).
нач
цел шаги
цел L, R, c, c3
L:= 1; R:= imin(N,1000)
X:= 0
шаги:= 0
нц пока R >= L
c:= div(R+L, 2);
шаги:= шаги + 1
c3:= c*c*c
если N = c*c*c
то X := c; выход
все
если N < c3 то R:= c - 1 все 
если N > c3 то L:= c + 1 все 
кц
знач:=шаги
кон

алг цел @тестирование
нач
цел i, N=10
цел R, X3, X1
целтаб XX[1:N] = {1, 3, 5, 9, 75, 178, 290, 350, 463, 512}
целтаб R0[1:N] = {1, 3, 6, 9, 9,  10,  9,   10,  10,  10}
нц для i от 1 до N
X3:= XX[i]**3;
R := Шаги кубический корень (X3, X1)
знач:=__Сравнить__(X1, XX[i], R, R0[i])
если знач = 0 то 
__Ошибка__(X3, R, R0[i]); 
выход
все
кц
если знач = 10 то
вывод "Задание зачтено."
все
кон
|-------------------------------------------------------
| Функция возвращает 10, если результаты совпадают,
| и 0, если различаются
|-------------------------------------------------------
алг цел __Сравнить__ (цел X, X0, R, R0)
нач
знач:=10
если X <> X0 или R <> R0 то знач:=0; все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел X3, цел R, R0)
нач
вывод "Программа работает неверно!", нс
вывод "Куб числа:        ", X3, нс
вывод "Получен ответ:    ", R, " шагов", нс
вывод "Правильный ответ: ", R0, " шагов"
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_65.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_65 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_65: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_65: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_65: {e}")

