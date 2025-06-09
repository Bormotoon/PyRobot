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

# Автогенерированные тесты для курса: c2kum
# Сгенерировано: 2025-06-09 11:48:59

def test_c2kum_Nayti_maksimalnyy_nechyotnyy_element_massiva_10(tmp_path):
    """
    Тест для задачи: Найти максимальный нечётный элемент массива (ID: 10)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= -1001
нц для i от 1 до N
если A[i] > знач и mod(A[i],2) <> 0 то
знач:= A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_10.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_maksimalnyy_nechyotnyy_element_massiva_10 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_maksimalnyy_nechyotnyy_element_massiva_10: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_maksimalnyy_nechyotnyy_element_massiva_10: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_maksimalnyy_nechyotnyy_element_massiva_10: {e}")


def test_c2kum_Nayti_minimalnyy_chyotnyy_element_kotoryy_ne_delitsya_na_3_11(tmp_path):
    """
    Тест для задачи: Найти минимальный чётный элемент, который не делится на 3 (ID: 11)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= 1001
нц для i от 1 до N
если A[i] < знач и mod(A[i],2) = 0 и mod(A[i],3) <> 0 то
знач:= A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_11.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_minimalnyy_chyotnyy_element_kotoryy_ne_delitsya_na_3_11 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_minimalnyy_chyotnyy_element_kotoryy_ne_delitsya_na_3_11: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_minimalnyy_chyotnyy_element_kotoryy_ne_delitsya_na_3_11: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_minimalnyy_chyotnyy_element_kotoryy_ne_delitsya_na_3_11: {e}")


def test_c2kum_Nayti_minimalnyy_nechyotnyy_element_kotoryy_delitsya_na_3_12(tmp_path):
    """
    Тест для задачи: Найти минимальный нечётный элемент, который делится на 3 (ID: 12)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= 1001
нц для i от 1 до N
если A[i] < знач и mod(A[i],2) <> 0 и mod(A[i],3) = 0 то
знач:= A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_12.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_minimalnyy_nechyotnyy_element_kotoryy_delitsya_na_3_12 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_minimalnyy_nechyotnyy_element_kotoryy_delitsya_na_3_12: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_minimalnyy_nechyotnyy_element_kotoryy_delitsya_na_3_12: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_minimalnyy_nechyotnyy_element_kotoryy_delitsya_na_3_12: {e}")


def test_c2kum_Nayti_minimalnyy_iz_elementov_znacheniya_kotoryh_bolshe_ili_13(tmp_path):
    """
    Тест для задачи: Найти минимальный из элементов, значения которых больше или равны 180 (ID: 13)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= 201
нц для i от 1 до N
если A[i] < знач и A[i] >= 180 то
знач:= A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_13.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_minimalnyy_iz_elementov_znacheniya_kotoryh_bolshe_ili_13 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_minimalnyy_iz_elementov_znacheniya_kotoryh_bolshe_ili_13: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_minimalnyy_iz_elementov_znacheniya_kotoryh_bolshe_ili_13: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_minimalnyy_iz_elementov_znacheniya_kotoryh_bolshe_ili_13: {e}")


def test_c2kum_Nayti_maksimalnyy_iz_elementov_znacheniya_kotoryh_menshe_nul_14(tmp_path):
    """
    Тест для задачи: Найти максимальный из элементов, значения которых меньше нуля (ID: 14)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= -100
нц для i от 1 до N
если A[i] > знач и A[i] < 0 то
знач:= A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_14.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_maksimalnyy_iz_elementov_znacheniya_kotoryh_menshe_nul_14 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_maksimalnyy_iz_elementov_znacheniya_kotoryh_menshe_nul_14: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_maksimalnyy_iz_elementov_znacheniya_kotoryh_menshe_nul_14: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_maksimalnyy_iz_elementov_znacheniya_kotoryh_menshe_nul_14: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_aMin_minimalnoe_polozhitelnoe_15(tmp_path):
    """
    Тест для задачи: Найти и записать в переменную aMin минимальное положительное чётное число, 
       которое есть в массиве (ID: 15)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, k
k:= 1 
нц пока A[k] <= 0  или  mod(A[k],2) = 1
k:=k+1
кц
нц для i от 1 до N
если A[i] > 0 и mod(A[i],2) = 0 и A[i] < A[k] то
k:= i
все
кц
знач:= A[k]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_15.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennuyu_aMin_minimalnoe_polozhitelnoe_15 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_aMin_minimalnoe_polozhitelnoe_15: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_aMin_minimalnoe_polozhitelnoe_15: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennuyu_aMin_minimalnoe_polozhitelnoe_15: {e}")


def test_c2kum_Nayti_minimalnoe_tryohznachnoe_chislo_kotoroe_est_v_massive_16(tmp_path):
    """
    Тест для задачи: Найти минимальное трёхзначное число, которое есть в массиве (ID: 16)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= 1000
нц для i от 1 до N
если A[i] < знач и A[i] >= 100 то
знач:= A[i]
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_16.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_minimalnoe_tryohznachnoe_chislo_kotoroe_est_v_massive_16 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_minimalnoe_tryohznachnoe_chislo_kotoroe_est_v_massive_16: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_minimalnoe_tryohznachnoe_chislo_kotoroe_est_v_massive_16: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_minimalnoe_tryohznachnoe_chislo_kotoroe_est_v_massive_16: {e}")


def test_c2kum_Nayti_nomer_elementa_imeyuschego_naibolshee_chislo_deliteley_17(tmp_path):
    """
    Тест для задачи: Найти номер элемента, имеющего наибольшее число делителей (ID: 17)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, k, count, mx
знач:= 0
mx:= 0
нц для i от 1 до N
count:= 1
нц для k от 2 до N
если mod(A[i],k) = 0 то
count:= count + 1
все
кц
если count > mx то
mx:= count
знач:= i
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_17.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_nomer_elementa_imeyuschego_naibolshee_chislo_deliteley_17 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_nomer_elementa_imeyuschego_naibolshee_chislo_deliteley_17: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_nomer_elementa_imeyuschego_naibolshee_chislo_deliteley_17: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_nomer_elementa_imeyuschego_naibolshee_chislo_deliteley_17: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_pervogo_po_schyotu_el_20(tmp_path):
    """
    Тест для задачи: Найти и записать в переменную nX номер первого по счёту элемента массива, равного X (ID: 20)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел X)
нач
цел i
знач:=-1
нц для i от 1 до N
если A[i] = X то
знач:= i
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_20.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_pervogo_po_schyotu_el_20 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_pervogo_po_schyotu_el_20: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_pervogo_po_schyotu_el_20: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_pervogo_po_schyotu_el_20: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_tretego_po_schyotu_po_21(tmp_path):
    """
    Тест для задачи: Найти и записать в переменную nX номер третьего по счёту положительного элемента массива (ID: 21)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, count=0
знач:=-1
нц для i от 1 до N
если A[i] > 0 то
count:= count + 1
если count = 3 то
знач:= i
выход
все
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_21.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_tretego_po_schyotu_po_21 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_tretego_po_schyotu_po_21: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_tretego_po_schyotu_po_21: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_tretego_po_schyotu_po_21: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_nMax2_nomer_vtorogo_maksimuma_22(tmp_path):
    """
    Тест для задачи: Найти и записать в переменную nMax2 номер «второго максимума» массива, то есть
 элемента, который стоял бы вторым в массиве, отсортированном по возрастанию (ID: 22)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, m1, m2
если A[1] > A[2] то
m1:= 1; m2:= 2
иначе
m1:= 2; m2:= 1
все
нц для i от 3 до N
если A[i] > A[m1] то
m2:= m1; m1:= i
иначе 
если A[i] > A[m2] то m2:= i все
все
кц
знач:= m2
кон
|--------------------------------
| Сообщение об ошибке
|--------------------------------
алг __Ошибка__(цел R, Q)
нач
цел i
вывод "Задание выполнено неверно!", нс
вывод "Массив:", нс
нц для i от 1 до N
вывод A[i], " "
кц
вывод нс
вывод "Получен ответ:    ", R 
если R < 1 то
вывод " (нет элемента)"
все
вывод нс, "Правильный ответ: ", Q
если Q < 1 то
вывод " (нет элемента)"
все
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_22.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennuyu_nMax2_nomer_vtorogo_maksimuma_22 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nMax2_nomer_vtorogo_maksimuma_22: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nMax2_nomer_vtorogo_maksimuma_22: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennuyu_nMax2_nomer_vtorogo_maksimuma_22: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_summa_summu_dvuh_minimalnyh_el_23(tmp_path):
    """
    Тест для задачи: Найти и записать в переменную сумма сумму двух минимальных элементов массива 
 (их значения могут быть равны) (ID: 23)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, m1, m2
если A[1] <= A[2] то
m1:= A[1]; m2:= A[2]
иначе
m1:= A[2]; m2:= A[1]
все
нц для i от 3 до N
если A[i] < m1 то
m2:= m1; m1:= A[i]
иначе 
если A[i] < m2 то m2:= A[i] все
все
кц
знач:= m1+m2
кон
|--------------------------------
| Сообщение об ошибке
|--------------------------------
алг __Ошибка__(цел R, Q)
нач
цел i
вывод "Задание выполнено неверно!", нс
вывод "Массив:", нс
нц для i от 1 до N
вывод A[i], " "
кц
вывод нс
вывод "Получен ответ:    ", R 
вывод нс, "Правильный ответ: ", Q
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_23.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennuyu_summa_summu_dvuh_minimalnyh_el_23 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_summa_summu_dvuh_minimalnyh_el_23: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_summa_summu_dvuh_minimalnyh_el_23: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennuyu_summa_summu_dvuh_minimalnyh_el_23: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennye_n1_i_n2_nomera_dvuh_elementov_m_24(tmp_path):
    """
    Тест для задачи: Найти и записать в переменные n1 и n2 номера двух элементов массива, которые
       меньше всего отличаются друг от друга (ID: 24)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  рез цел
  цел := 0
  __Решение__(цел)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(рез цел m1, m2)
нач
цел i, j
m1:= 1; m2:= 2
нц для i от 1 до N
нц для j от i+1 до N
если abs(A[i]-A[j]) < abs(A[m1]-A[m2]) то
m1:= i; m2:= j
все
кц
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_24.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennye_n1_i_n2_nomera_dvuh_elementov_m_24 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennye_n1_i_n2_nomera_dvuh_elementov_m_24: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennye_n1_i_n2_nomera_dvuh_elementov_m_24: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennye_n1_i_n2_nomera_dvuh_elementov_m_24: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_25(tmp_path):
    """
    Тест для задачи: Найти и записать в переменную count количество элементов массива, равных
       максимальному элементу (ID: 25)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, m, count
count:=1
m:=A[1]
нц для i от 2 до N
если A[i] = m то
count:=count+1
иначе 
если A[i] > m то
m:= A[i]; count:= 1
все
все
кц
знач:= count
кон
|--------------------------------
| Сообщение об ошибке
|--------------------------------
алг __Ошибка__(цел R, Q)
нач
цел i
вывод "Задание выполнено неверно!", нс
вывод "Массив:", нс
нц для i от 1 до N
вывод A[i], " "
кц
вывод нс, "Получен ответ:    ", R 
вывод нс, "Правильный ответ: ", Q

кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_25.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_25 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_25: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_25: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_25: {e}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_26(tmp_path):
    """
    Тест для задачи: Найти и записать в переменную count количество элементов массива, которые
       больше, чем среднее арифметическое всех элементов (ID: 26)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, m, count
вещ среднее = 0
нц для i от 1 до N
среднее:= среднее + A[i]
кц
среднее:= среднее / N
count:=0
нц для i от 1 до N
если A[i] > среднее то
count:=count+1
все
кц
знач:= count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_26.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_26 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_26: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_26: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_26: {e}")


def test_c2kum_Nayti_summu_elementov_massiva_kotorye_kratny_chislu_13_i_zap_30(tmp_path):
    """
    Тест для задачи: Найти сумму элементов массива, которые кратны числу 13, и записать эту сумму
   в переменную сумма (ID: 30)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= 0
нц для i от 1 до N
если mod(A[i],13) = 0 то
знач:= знач + A[i] 
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
        print(f"Test test_c2kum_Nayti_summu_elementov_massiva_kotorye_kratny_chislu_13_i_zap_30 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_summu_elementov_massiva_kotorye_kratny_chislu_13_i_zap_30: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_summu_elementov_massiva_kotorye_kratny_chislu_13_i_zap_30: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_summu_elementov_massiva_kotorye_kratny_chislu_13_i_zap_30: {e}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_elementov_massiva_kotorye_bols_31(tmp_path):
    """
    Тест для задачи: Найти среднее арифметическое элементов массива,  которые больше 20, и записать эту сумму
       в переменную среднее (ID: 31)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг вещ __Решение__
нач
цел i, count = 0
знач:= 0
нц для i от 1 до N
если A[i] > 20 то
знач:= знач + A[i] 
count:= count + 1
все
кц
знач:= знач / count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_31.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_srednee_arifmeticheskoe_elementov_massiva_kotorye_bols_31 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_srednee_arifmeticheskoe_elementov_massiva_kotorye_bols_31: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_srednee_arifmeticheskoe_elementov_massiva_kotorye_bols_31: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_srednee_arifmeticheskoe_elementov_massiva_kotorye_bols_31: {e}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_nechyotnyh_otritsatelnyh_eleme_32(tmp_path):
    """
    Тест для задачи: Найти среднее арифметическое нечётных  отрицательных элементов массива
       и записать его в переменную среднее (ID: 32)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг вещ __Решение__
нач
цел i, count = 0
знач:= 0
нц для i от 1 до N
если A[i] < 0 и mod(A[i],2) <> 0 то
знач:= знач + A[i] 
count:= count + 1
все
кц
знач:= знач / count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_32.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_srednee_arifmeticheskoe_nechyotnyh_otritsatelnyh_eleme_32 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_srednee_arifmeticheskoe_nechyotnyh_otritsatelnyh_eleme_32: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_srednee_arifmeticheskoe_nechyotnyh_otritsatelnyh_eleme_32: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_srednee_arifmeticheskoe_nechyotnyh_otritsatelnyh_eleme_32: {e}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_33(tmp_path):
    """
    Тест для задачи: Найти среднее арифметическое положительных элементов массива,
   делящихся на 5, и записать его в переменную среднее (ID: 33)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг вещ __Решение__
нач
цел i, count = 0
знач:= 0
нц для i от 1 до N
если A[i] > 0 и mod(A[i],5) = 0 то
знач:= знач + A[i] 
count:= count + 1
все
кц
знач:= знач / count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_33.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_33 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_33: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_33: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_33: {e}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_34(tmp_path):
    """
    Тест для задачи: Найти среднее арифметическое положительных элементов массива,
   кратных первому элементу, и записать его в переменную среднее (ID: 34)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг вещ __Решение__
нач
цел i, count = 0
знач:= 0
нц для i от 1 до N
если A[i] > 0 и mod(A[i],A[1]) = 0 то
знач:= знач + A[i] 
count:= count + 1
все
кц
знач:= знач / count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_34.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_34 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_34: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_34: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_34: {e}")


def test_c2kum_Nayti_nomer_elementa_blizhayshego_k_srednemu_arifmeticheskom_35(tmp_path):
    """
    Тест для задачи: Найти номер элемента, ближайшего к среднему арифметическому всех элементов массива, 
   и записать его в переменную номер (ID: 35)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, count = 0
вещ среднее, dist
среднее:= 0
нц для i от 1 до N
среднее:= среднее + A[i] 
кц
среднее:= среднее / N
знач:= 0
нц для i от 1 до N
если знач = 0 или abs(A[i]-среднее) < dist то
dist:= abs(A[i]-среднее)
знач:= i
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
        print(f"Test test_c2kum_Nayti_nomer_elementa_blizhayshego_k_srednemu_arifmeticheskom_35 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_nomer_elementa_blizhayshego_k_srednemu_arifmeticheskom_35: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_nomer_elementa_blizhayshego_k_srednemu_arifmeticheskom_35: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_nomer_elementa_blizhayshego_k_srednemu_arifmeticheskom_35: {e}")


def test_c2kum_Nayti_proizvedenie_chyotnyh_elementov_massiva_kotorye_ne_oka_36(tmp_path):
    """
    Тест для задачи: Найти произведение чётных элементов массива, которые не оканчиваются на 0, 
   и записать его в переменную произв (ID: 36)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= 1
нц для i от 1 до N
если mod(A[i],2) = 0 и  mod(A[i],10) <> 0 то
знач:= знач * A[i]
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
        print(f"Test test_c2kum_Nayti_proizvedenie_chyotnyh_elementov_massiva_kotorye_ne_oka_36 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_proizvedenie_chyotnyh_elementov_massiva_kotorye_ne_oka_36: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_proizvedenie_chyotnyh_elementov_massiva_kotorye_ne_oka_36: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_proizvedenie_chyotnyh_elementov_massiva_kotorye_ne_oka_36: {e}")


def test_c2kum_Nayti_proizvedenie_dvuznachnyh_elementov_massiva_kotorye_del_37(tmp_path):
    """
    Тест для задачи: Найти произведение двузначных элементов массива, которые делятся на 6, 
   и записать его в переменную произв (ID: 37)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i
знач:= 1
нц для i от 1 до N
если 10 <= A[i] <= 99 и  mod(A[i],6) = 0 то
знач:= знач * A[i]
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
        print(f"Test test_c2kum_Nayti_proizvedenie_dvuznachnyh_elementov_massiva_kotorye_del_37 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_proizvedenie_dvuznachnyh_elementov_massiva_kotorye_del_37: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_proizvedenie_dvuznachnyh_elementov_massiva_kotorye_del_37: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_proizvedenie_dvuznachnyh_elementov_massiva_kotorye_del_37: {e}")


def test_c2kum_Nayti_paru_sosednih_elementov_summa_kotoryh_maksimalna_i_zap_40(tmp_path):
    """
    Тест для задачи: Найти пару соседних элементов, сумма которых максимальна, и записать в переменную
       K номер первого из них (ID: 40)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, s, M
знач:= 1
M:= A[1]+A[2]
нц для i от 2 до N-1
s:= A[i]+A[i+1]
если s > M то
знач:= i
M:= s
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_40.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_paru_sosednih_elementov_summa_kotoryh_maksimalna_i_zap_40 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_paru_sosednih_elementov_summa_kotoryh_maksimalna_i_zap_40: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_paru_sosednih_elementov_summa_kotoryh_maksimalna_i_zap_40: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_paru_sosednih_elementov_summa_kotoryh_maksimalna_i_zap_40: {e}")


def test_c2kum_Nayti_tri_sosednih_elementa_summa_kotoryh_minimalna_i_zapisa_41(tmp_path):
    """
    Тест для задачи: Найти три соседних элемента, сумма которых минимальна, и записать в переменную
       K номер первого из них (ID: 41)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, s, M
знач:= 1
M:= A[1]+A[2]+A[3]
нц для i от 2 до N-2
s:= A[i]+A[i+1]+A[i+2]
если s < M то
знач:= i
M:= s
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_41.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_tri_sosednih_elementa_summa_kotoryh_minimalna_i_zapisa_41 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_tri_sosednih_elementa_summa_kotoryh_minimalna_i_zapisa_41: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_tri_sosednih_elementa_summa_kotoryh_minimalna_i_zapisa_41: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_tri_sosednih_elementa_summa_kotoryh_minimalna_i_zapisa_41: {e}")


def test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_otritsatel_42(tmp_path):
    """
    Тест для задачи: Найти длину наибольшей цепочки идущих подряд отрицательных чисел и
       записать её в переменную L (ID: 42)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, L
знач:= 0
L:=0
нц для i от 1 до N
если A[i] < 0 то
L:= L + 1
если L > знач то
знач:= L
все
иначе
L:=0
все
кц
кон
|-------------------------------------------------------
| Вывод массива 
|-------------------------------------------------------
алг __Вывод массива__
нач
цел i
нц для i от 1 до N 
вывод A[i]," "
кц
вывод нс
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__
вывод "Получен ответ:    ", R
вывод нс, "Правильный ответ: ", R0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_42.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_otritsatel_42 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_otritsatel_42: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_otritsatel_42: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_otritsatel_42: {e}")


def test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_odinakovyh_43(tmp_path):
    """
    Тест для задачи: Найти длину наибольшей цепочки идущих подряд одинаковых чисел и
       записать её в переменную L (ID: 43)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, L
знач:= 1
L:=1
нц для i от 2 до N
если A[i] = A[i-1] то
L:= L + 1
если L > знач то
знач:= L
все
иначе
L:=1
все
кц
кон
|-------------------------------------------------------
| Вывод массива 
|-------------------------------------------------------
алг __Вывод массива__
нач
цел i
нц для i от 1 до N 
вывод A[i]," "
кц
вывод нс
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__
вывод "Получен ответ:    ", R
вывод нс, "Правильный ответ: ", R0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_43.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_odinakovyh_43 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_odinakovyh_43: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_odinakovyh_43: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_odinakovyh_43: {e}")


def test_c2kum_Nayti_dlinu_naibolshey_tsepochki_chisel_elementy_kotoroy_sto_44(tmp_path):
    """
    Тест для задачи: Найти длину наибольшей цепочки чисел, элементы которой стоят в порядке возрастания
       (неубывания), и записать её в переменную L (ID: 44)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, L
знач:= 1
L:=1
нц для i от 2 до N
если A[i] >= A[i-1] то
L:= L + 1
если L > знач то
знач:= L
все
иначе
L:=1
все
кц
кон
|-------------------------------------------------------
| Вывод массива 
|-------------------------------------------------------
алг __Вывод массива__
нач
цел i
нц для i от 1 до N 
вывод A[i]," "
кц
вывод нс
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел R, R0)
нач
вывод "Программа работает неверно!", нс, "Массив: "
__Вывод массива__
вывод "Получен ответ:    ", R
вывод нс, "Правильный ответ: ", R0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_44.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_dlinu_naibolshey_tsepochki_chisel_elementy_kotoroy_sto_44 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_chisel_elementy_kotoroy_sto_44: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_chisel_elementy_kotoroy_sto_44: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_dlinu_naibolshey_tsepochki_chisel_elementy_kotoroy_sto_44: {e}")


def test_c2kum_Nayti_maksimalnyy_iz_elementov_kotorye_menshe_100_i_zapisat_50(tmp_path):
    """
    Тест для задачи: Найти максимальный из элементов, которые меньше 100, и записать его в переменную 
   максимум (ID: 50)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, M 
M:=100
нц для i от 1 до N
нц для j от 1 до N
если A[i,j] < 100 то
если M = 100 или A[i,j] > M то
M:= A[i,j]
все
все
кц
кц
знач:=M
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_50.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_maksimalnyy_iz_elementov_kotorye_menshe_100_i_zapisat_50 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_maksimalnyy_iz_elementov_kotorye_menshe_100_i_zapisat_50: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_maksimalnyy_iz_elementov_kotorye_menshe_100_i_zapisat_50: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_maksimalnyy_iz_elementov_kotorye_menshe_100_i_zapisat_50: {e}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_vseh_elementov_glavnoy_diagona_51(tmp_path):
    """
    Тест для задачи: Найти среднее арифметическое всех элементов главной диагонали матрицы и записать его 
 в переменную среднее (ID: 51)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг вещ __Решение__
нач
цел i, j 
вещ сумма = 0
нц для i от 1 до N
сумма:= сумма + A[i,i]
кц
знач:= сумма / N
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_51.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_srednee_arifmeticheskoe_vseh_elementov_glavnoy_diagona_51 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_srednee_arifmeticheskoe_vseh_elementov_glavnoy_diagona_51: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_srednee_arifmeticheskoe_vseh_elementov_glavnoy_diagona_51: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_srednee_arifmeticheskoe_vseh_elementov_glavnoy_diagona_51: {e}")


def test_c2kum_Nayti_kolichestvo_polozhitelnyh_elementov_matritsy_kotorye_b_52(tmp_path):
    """
    Тест для задачи: Найти количество положительных элементов матрицы, которые больше среднего арифметического 
   элементов её главной диагонали матрицы, и записать его в переменную count (ID: 52)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг вещ __Решение__
нач
цел i, j 
вещ сумма = 0, среднее
нц для i от 1 до N
сумма:= сумма + A[i,i]
кц
среднее:= сумма / N
знач:= 0
нц для i от 1 до N
нц для j от 1 до N
если A[i,j] > 0 и A[i,j] > среднее то
знач:= знач + 1
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
        print(f"Test test_c2kum_Nayti_kolichestvo_polozhitelnyh_elementov_matritsy_kotorye_b_52 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_kolichestvo_polozhitelnyh_elementov_matritsy_kotorye_b_52: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_kolichestvo_polozhitelnyh_elementov_matritsy_kotorye_b_52: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_kolichestvo_polozhitelnyh_elementov_matritsy_kotorye_b_52: {e}")


def test_c2kum_Nayti_kolichestvo_elementov_matritsy_kotorye_bolshe_srednego_53(tmp_path):
    """
    Тест для задачи: Найти количество элементов матрицы, которые больше среднего арифметического
 всех элементов, и записать его в переменную count (ID: 53)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j 
вещ среднее = 0
нц для i от 1 до N
нц для j от 1 до N
среднее:= среднее + A[i,j]
кц
кц
среднее:= среднее / (N*N)
знач:=0
нц для i от 1 до N
нц для j от 1 до N
если A[i,j] > среднее то
знач:=знач+1
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
        print(f"Test test_c2kum_Nayti_kolichestvo_elementov_matritsy_kotorye_bolshe_srednego_53 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_kolichestvo_elementov_matritsy_kotorye_bolshe_srednego_53: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_kolichestvo_elementov_matritsy_kotorye_bolshe_srednego_53: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_kolichestvo_elementov_matritsy_kotorye_bolshe_srednego_53: {e}")


def test_c2kum_Nayti_summu_minimalnyh_elementov_kazhdogo_stolbtsa_i_zapisat_54(tmp_path):
    """
    Тест для задачи: Найти сумму минимальных элементов каждого столбца и записать её 
 в переменную сумма (ID: 54)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, M 
знач:=0
нц для j от 1 до N
M:= A[1,j]
нц для i от 2 до N
если A[i,j] < M то
M:= A[i,j]
все
кц
знач:=знач + M 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_54.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_summu_minimalnyh_elementov_kazhdogo_stolbtsa_i_zapisat_54 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_summu_minimalnyh_elementov_kazhdogo_stolbtsa_i_zapisat_54: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_summu_minimalnyh_elementov_kazhdogo_stolbtsa_i_zapisat_54: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_summu_minimalnyh_elementov_kazhdogo_stolbtsa_i_zapisat_54: {e}")


def test_c2kum_Nayti_summu_maksimalnyh_elementov_kazhdoy_stroki_i_zapisat_e_55(tmp_path):
    """
    Тест для задачи: Найти сумму максимальных элементов каждой строки и записать её 
 в переменную сумма (ID: 55)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, M 
знач:=0
нц для i от 1 до N
M:= A[i,1]
нц для j от 2 до N
если A[i,j] > M то
M:= A[i,j]
все
кц
знач:=знач + M 
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_55.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_summu_maksimalnyh_elementov_kazhdoy_stroki_i_zapisat_e_55 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_summu_maksimalnyh_elementov_kazhdoy_stroki_i_zapisat_e_55: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_summu_maksimalnyh_elementov_kazhdoy_stroki_i_zapisat_e_55: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_summu_maksimalnyh_elementov_kazhdoy_stroki_i_zapisat_e_55: {e}")


def test_c2kum_Nayti_nomer_stolbtsa_s_maksimalnoy_summoy_elementov_i_zapisa_56(tmp_path):
    """
    Тест для задачи: Найти номер столбца с максимальной суммой элементов и записать его 
 в переменную nMаx (ID: 56)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, s, sMax, nMax 
нц для j от 1 до M
s:= 0
нц для i от 1 до N
s:= s + A[i,j]
кц
если j = 1 или s > sMax то
sMax:= s; nMax := j
все
кц
знач:=nMax
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_56.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_nomer_stolbtsa_s_maksimalnoy_summoy_elementov_i_zapisa_56 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_nomer_stolbtsa_s_maksimalnoy_summoy_elementov_i_zapisa_56: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_nomer_stolbtsa_s_maksimalnoy_summoy_elementov_i_zapisa_56: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_nomer_stolbtsa_s_maksimalnoy_summoy_elementov_i_zapisa_56: {e}")


def test_c2kum_Nayti_nomer_stroki_s_minimalnoy_summoy_elementov_i_zapisat_e_57(tmp_path):
    """
    Тест для задачи: Найти номер строки с минимальной суммой элементов и записать его 
 в переменную nMin (ID: 57)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, s, sMin, nMin 
нц для i от 1 до N
s:= 0
нц для j от 1 до M
s:= s + A[i,j]
кц
если i = 1 или s < sMin то
sMin:= s; nMin := i
все
кц
знач:=nMin
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_57.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_nomer_stroki_s_minimalnoy_summoy_elementov_i_zapisat_e_57 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_nomer_stroki_s_minimalnoy_summoy_elementov_i_zapisat_e_57: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_nomer_stroki_s_minimalnoy_summoy_elementov_i_zapisat_e_57: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_nomer_stroki_s_minimalnoy_summoy_elementov_i_zapisat_e_57: {e}")


def test_c2kum_Nayti_maksimalnyy_iz_minimalnyh_elementov_kazhdoy_stroki_i_z_58(tmp_path):
    """
    Тест для задачи: Найти максимальный из минимальных элементов каждой строки и записать его 
   в переменную maxMin (ID: 58)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, M 
нц для i от 1 до N
M:= A[i,1]
нц для j от 2 до N
если A[i,j] < M то
M:= A[i,j]
все
кц
если i = 1 или M > знач то
знач:= M 
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
        print(f"Test test_c2kum_Nayti_maksimalnyy_iz_minimalnyh_elementov_kazhdoy_stroki_i_z_58 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_maksimalnyy_iz_minimalnyh_elementov_kazhdoy_stroki_i_z_58: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_maksimalnyy_iz_minimalnyh_elementov_kazhdoy_stroki_i_z_58: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_maksimalnyy_iz_minimalnyh_elementov_kazhdoy_stroki_i_z_58: {e}")


def test_c2kum_Nayti_minimalnyy_iz_maksimalnyh_elementov_kazhdogo_stolbtsa_59(tmp_path):
    """
    Тест для задачи: Найти минимальный из максимальных элементов каждого столбца и записать его 
 в переменную minMax (ID: 59)
    Курс: c2kum
    """
    kumir_code = '''алг
нач
  результат := __Решение__()
  вывод результат, нс
кон

алг цел __Решение__
нач
цел i, j, M 
нц для j от 1 до N
M:= A[1,j]
нц для i от 2 до N
если A[i,j] > M то
M:= A[i,j]
все
кц
если j = 1 или M < знач то
знач:= M 
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_59.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_c2kum_Nayti_minimalnyy_iz_maksimalnyh_elementov_kazhdogo_stolbtsa_59 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_c2kum_Nayti_minimalnyy_iz_maksimalnyh_elementov_kazhdogo_stolbtsa_59: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_c2kum_Nayti_minimalnyy_iz_maksimalnyh_elementov_kazhdogo_stolbtsa_59: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_c2kum_Nayti_minimalnyy_iz_maksimalnyh_elementov_kazhdogo_stolbtsa_59: {e}")

