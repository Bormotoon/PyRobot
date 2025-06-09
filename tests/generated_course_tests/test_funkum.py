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

# Автогенерированные тесты для курса: funkum
# Сгенерировано: 2025-06-09 11:48:59

def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kvadrat_chisla_10(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает квадрат числа (ID: 10)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=x*x
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_10.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kvadrat_chisla_10 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kvadrat_chisla_10: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kvadrat_chisla_10: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kvadrat_chisla_10: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kub_chisla_11(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает куб числа (ID: 11)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=x*x*x
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_11.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kub_chisla_11 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kub_chisla_11: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kub_chisla_11: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kub_chisla_11: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_poslednyuyu_tsifru_v_12(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает последнюю цифру в десятичной записи числа (ID: 12)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=mod(x,10)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_12.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_poslednyuyu_tsifru_v_12 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_poslednyuyu_tsifru_v_12: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_poslednyuyu_tsifru_v_12: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_poslednyuyu_tsifru_v_12: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_desyatkov_pre_13(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает число десятков - предпоследнюю цифру в десятичной записи числа (ID: 13)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=mod(div(x,10),10)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_13.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_desyatkov_pre_13 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_desyatkov_pre_13: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_desyatkov_pre_13: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_desyatkov_pre_13: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_soten_tretyu_14(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает число сотен - третью с конца цифру в десятичной записи числа (ID: 14)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=mod(div(x,100),10)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_14.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_soten_tretyu_14 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_soten_tretyu_14: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_soten_tretyu_14: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_soten_tretyu_14: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_rezultat_okrugleniya_15(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает результат округления числа до ближайщего целого (ID: 15)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(3.14)
  вывод результат, нс
кон

алг цел __Решение__(вещ x)
нач
цел xR
xR:=int(x)
знач:=0
если x-xR >= 0.5 то
xR:=xR+1
все
знач:=xR
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_15.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_rezultat_okrugleniya_15 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_rezultat_okrugleniya_15: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_rezultat_okrugleniya_15: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_rezultat_okrugleniya_15: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vypolnyaet_okruglenie_vverh_to_es_16(tmp_path):
    """
    Тест для задачи: Написать функцию, которая выполняет «округление вверх», то есть возвращает первое целое число, которое больше или равно данному (ID: 16)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(3.14)
  вывод результат, нс
кон

алг цел __Решение__(вещ x)
нач
цел xR
xR:=int(x)
знач:=0
если x-xR > 0 то
xR:=xR+1
все
знач:=xR
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_16.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vypolnyaet_okruglenie_vverh_to_es_16 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vypolnyaet_okruglenie_vverh_to_es_16: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vypolnyaet_okruglenie_vverh_to_es_16: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vypolnyaet_okruglenie_vverh_to_es_16: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_vseh_naturalny_17(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает сумму всех натуральных чисел от 1 до заданного числа X (ID: 17)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел i
знач:=0
нц для i от 1 до x
знач:=знач+i
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_17.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_vseh_naturalny_17 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_vseh_naturalny_17: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_vseh_naturalny_17: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_vseh_naturalny_17: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zadannuyu_stepen_chi_18(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает заданную степень числа 2 (ID: 18)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=1
цел i
нц для i от 1 до x
знач:=2*знач
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_18.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zadannuyu_stepen_chi_18 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zadannuyu_stepen_chi_18: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zadannuyu_stepen_chi_18: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zadannuyu_stepen_chi_18: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_faktorial_chisla_X_p_20(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает факториaл числа X - произведение всех натуральных чисел от 1 до X (ID: 20)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел i
знач:=1
нц для i от 1 до x
знач:=знач*i
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_20.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_faktorial_chisla_X_p_20 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_faktorial_chisla_X_p_20: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_faktorial_chisla_X_p_20: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_faktorial_chisla_X_p_20: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervuyu_tsifru_v_des_21(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает первую цифру в десятичной записи числа (ID: 21)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=x
нц пока знач > 9
знач:=div(знач,10)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_21.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervuyu_tsifru_v_des_21 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervuyu_tsifru_v_des_21: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervuyu_tsifru_v_des_21: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervuyu_tsifru_v_des_21: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_tsifr_ch_22(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает количество цифр числа (ID: 22)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел x1
x1:=x
знач:=0
нц пока x1 > 0
знач:=знач+1
x1:=div(x1,10)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_22.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_tsifr_ch_22 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_tsifr_ch_22: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_tsifr_ch_22: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_tsifr_ch_22: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_tsifr_chisla_23(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает сумму цифр числа (ID: 23)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел x1
x1:=x
знач:=0
нц пока x1 > 0
знач:=знач+mod(x1,10)
x1:=div(x1,10)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_23.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_tsifr_chisla_23 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_tsifr_chisla_23: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_tsifr_chisla_23: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_tsifr_chisla_23: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_edinits_24(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает количество единиц в двоичной записи числа (ID: 24)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел x1
x1:=x
знач:=0
нц пока x1 > 0
знач:=знач+mod(x1,2)
x1:=div(x1,2)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_24.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_edinits_24 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_edinits_24: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_edinits_24: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_edinits_24: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_nuley_v_25(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает количество нулей в двоичной записи числа (ID: 25)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел x1
x1:=x
знач:=0
нц пока x1 > 0
если mod(x1,2) = 0 то
знач:=знач+1
все 
x1:=div(x1,2)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_25.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_nuley_v_25 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_nuley_v_25: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_nuley_v_25: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_nuley_v_25: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_Fibonachchi_s_26(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает число Фибоначчи с заданным номером (ID: 26)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=1
если x < 3 то выход все
цел i, f1 = 1, f2 = 1
нц для i от 3 до x
знач:=f1 + f2
f2:=f1
f1:=знач
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_26.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_Fibonachchi_s_26 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_Fibonachchi_s_26: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_Fibonachchi_s_26: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_Fibonachchi_s_26: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervoe_chislo_Fibona_27(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает первое число Фибоначчи, которое больше или равно заданному значению (ID: 27)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел f1 = 1, f2 = 1
знач:=1
нц пока знач < x
знач:=f1 + f2
f2:=f1
f1:=знач
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_27.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervoe_chislo_Fibona_27 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervoe_chislo_Fibona_27: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervoe_chislo_Fibona_27: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervoe_chislo_Fibona_27: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_stepen_v_kotoruyu_nu_28(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает степень, в которую нужно возвести число 2 для того, чтобы получить заданное число (ID: 28)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел x2 = 1
знач:=0
нц пока x2 < x
знач:=знач+1
x2:=x2*2
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_28.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_stepen_v_kotoruyu_nu_28 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_stepen_v_kotoruyu_nu_28: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_stepen_v_kotoruyu_nu_28: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_stepen_v_kotoruyu_nu_28: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_30(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает среднее арифметическое двух чисел (ID: 30)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг вещ __Решение__(цел x, y)
нач
знач:= (x+y) / 2
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_30.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_30 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_30: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_30: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_30: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_31(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает среднее арифметическое трёх чисел (ID: 31)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг вещ __Решение__(цел x, y, z)
нач
знач:=(x+y+z)/3
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_31.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_31 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_31: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_31: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_31: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_dvuh_c_32(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает наименьшее из двух чисел (ID: 32)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x, y)
нач
знач:=imin(x,y)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_32.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_dvuh_c_32 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_dvuh_c_32: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_dvuh_c_32: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_dvuh_c_32: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_dvuh_c_33(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает наибольшее из двух чисел (ID: 33)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x, y)
нач
знач:=imax(x,y)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_33.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_dvuh_c_33 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_dvuh_c_33: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_dvuh_c_33: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_dvuh_c_33: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_tryoh_34(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает наименьшее из трёх чисел (ID: 34)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x, y, z)
нач
знач:=imin(imin(x,y),z)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_34.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_tryoh_34 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_tryoh_34: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_tryoh_34: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_tryoh_34: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_tryoh_35(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает наибольшее из трёх чисел (ID: 35)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x, y, z)
нач
знач:=imax(imax(x,y),z)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_35.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_tryoh_35 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_tryoh_35: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_tryoh_35: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_tryoh_35: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvodit_X_v_stepen_Y_ispolzuya_p_36(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возводит X в степень Y, используя последовательное умножение (ID: 36)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x, y)
нач
знач:=x**y
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_36.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvodit_X_v_stepen_Y_ispolzuya_p_36 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvodit_X_v_stepen_Y_ispolzuya_p_36: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvodit_X_v_stepen_Y_ispolzuya_p_36: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvodit_X_v_stepen_Y_ispolzuya_p_36: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshiy_obschiy_d_37(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает наибольший общий делитель (НОД) двух натуральных чисел (ID: 37)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x0, y0)
нач
цел x, y
x:=x0; y:=y0
нц пока x <> 0 и y <> 0
если x > y то
x:= mod(x,y)
иначе
y:= mod(y,x)
все
кц
знач:=x+y
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел x, y, цел ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Заданные числа:   ", x, ", ", y, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_37.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshiy_obschiy_d_37 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshiy_obschiy_d_37: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshiy_obschiy_d_37: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshiy_obschiy_d_37: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_obschee_k_38(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает наименьшее общее кратное (НОК) двух натуральных чисел (ID: 38)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x0, y0)
нач
цел x, y
x:=x0; y:=y0
нц пока x <> 0 и y <> 0
если x > y то
x:= mod(x,y)
иначе
y:= mod(y,x)
все
кц
знач:=div(x0*y0,x+y)
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел x, y, цел ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Заданные числа:   ", x, ", ", y, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_38.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_obschee_k_38 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_obschee_k_38: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_obschee_k_38: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_obschee_k_38: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_neizvestnyy_pokazatel_39(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет неизвестный показатель степени N в уравнении «Y = X в степени N» (ID: 39)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x, y)
нач
цел y1
y1:=1
знач:=0
нц пока y1 < y
y1:=y1*x
знач:=знач+1
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_39.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_neizvestnyy_pokazatel_39 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_neizvestnyy_pokazatel_39: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_neizvestnyy_pokazatel_39: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_neizvestnyy_pokazatel_39: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_naibolshiy_pokazatel_310(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет наибольший показатель степени N, при котором «X в степени N» меньше или равно Y (ID: 310)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x, y)
нач
цел y1
y1:=1
знач:=0
нц пока y1 <= y
y1:=y1*x
знач:=знач+1
кц
знач:=знач-1
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_310.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_naibolshiy_pokazatel_310 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_naibolshiy_pokazatel_310: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_naibolshiy_pokazatel_310: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_naibolshiy_pokazatel_310: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_40(tmp_path):
    """
    Тест для задачи: Написать функцию, которая разбирает URL и возвращает название протокола (ID: 40)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s)
нач
цел p
p:=найти(":",s)
знач:=s[1:p-1]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_40.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_40 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_40: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_40: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_40: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_41(tmp_path):
    """
    Тест для задачи: Написать функцию, которая разбирает URL и возвращает имя сервера (ID: 41)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s)
нач
цел p
лит s1
p:=найти("//",s)
s1:=удалить(s,1,p+1)
p:=найти("/",s1)
если p > 0 то
знач:=s1[1:p-1]
иначе
знач:=s1
все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит x, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Задан адрес:      ", x, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_41.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_41 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_41: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_41: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_41: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_42(tmp_path):
    """
    Тест для задачи: Написать функцию, которая разбирает URL и возвращает имя файла (ID: 42)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s)
нач
цел p
p:=длин(s)
нц пока s[p] <> '/' 
p:=p-1
кц
знач:=s[p+1:длин(s)]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_42.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_42 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_42: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_42: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_42: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_43(tmp_path):
    """
    Тест для задачи: Написать функцию, которая разбирает URL и возвращает название доменной зоны (например, «com») (ID: 43)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s)
нач
цел p
лит s1
p:=найти("//",s)
s1:=удалить(s,1,p+1)
p:=найти("/",s1)
если p > 0 то
s1:=s1[1:p-1]
все
нц пока да
p:=найти(".", s1)
если p < 1 то выход все
s1:=удалить(s1,1,p)
кц
знач:=s1
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_43.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_43 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_43: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_43: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_43: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_44(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает запись переданного ей числа в двоичной системе счисления (результат - символьная строка) (ID: 44)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лит __Решение__(цел x)
нач
цел x1, osn=2
если x <= 0 то
знач:="0"
выход
все
знач:=""
x1:=x
нц пока x1 > 0
знач:=цел_в_лит(mod(x1,osn)) + знач
x1:=div(x1,osn)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_44.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_44 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_44: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_44: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_44: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_45(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает запись переданного ей числа в восьмеричной системе счисления (результат - символьная строка) (ID: 45)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лит __Решение__(цел x)
нач
цел x1, osn=8
если x <= 0 то
знач:="0"
выход
все
знач:=""
x1:=x
нц пока x1 > 0
знач:=цел_в_лит(mod(x1,osn)) + знач
x1:=div(x1,osn)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_45.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_45 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_45: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_45: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_45: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_st_46(tmp_path):
    """
    Тест для задачи: Написать функцию, которая удаляет все пробелы в начале строки и возвращает укороченную строку (ID: 46)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
лит s
s:= s0
нц пока длин(s) > 0 и s[1] = " "
s:=удалить(s,1,1)
кц
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_46.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_st_46 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_st_46: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_st_46: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_st_46: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_kontse_str_47(tmp_path):
    """
    Тест для задачи: Написать функцию, которая удаляет все пробелы в конце строки и возвращает укороченную строку (ID: 47)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
лит s
s:= s0
нц пока длин(s) > 0 и s[длин(s)] = " "
s:=удалить(s,длин(s),1)
кц
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_47.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_kontse_str_47 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_kontse_str_47: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_kontse_str_47: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_kontse_str_47: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_i_48(tmp_path):
    """
    Тест для задачи: Написать функцию, которая удаляет все пробелы в начале и в конце строки и возвращает укороченную строку (ID: 48)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
лит s
s:= s0
нц пока длин(s) > 0 и s[1] = " "
s:=удалить(s,1,1)
кц
нц пока длин(s) > 0 и s[длин(s)] = " "
s:=удалить(s,длин(s),1)
кц
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_48.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_i_48 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_i_48: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_i_48: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_i_48: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_49(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает запись переданного ей числа в шестнадцатеричной системе счисления (результат - символьная строка) (ID: 49)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лит __Решение__(цел x)
нач
цел x1, osn=16, dig
если x <= 0 то
знач:="0"
выход
все
знач:=""
x1:=x
нц пока x1 > 0
dig:=mod(x1,osn)
если dig < 10 то
знач:=цел_в_лит(dig) + знач
иначе
знач:=символ(код("A")+dig-10) + знач
все
x1:=div(x1,osn)
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел x, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Заданное число:   ", x, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_49.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_49 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_49: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_49: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_49: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_izmenyaet_rasshirenie_imeni_fayla_50(tmp_path):
    """
    Тест для задачи: Написать функцию, которая изменяет расширение имени файла на « (ID: 50)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s)
нач
цел p
p:=найти(".",s)
если p > 0 то
знач:=s[1:p] + "bak"
иначе 
знач:=s + ".bak" 
все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  '", s, "'", нс
вывод "Получен ответ:    '", ansBad, "'", нс
вывод "Правильный ответ: '", ansOK, "'", нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_50.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_izmenyaet_rasshirenie_imeni_fayla_50 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_izmenyaet_rasshirenie_imeni_fayla_50: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_izmenyaet_rasshirenie_imeni_fayla_50: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_izmenyaet_rasshirenie_imeni_fayla_50: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_poluchaet_put_k_faylu_izmenyaet_r_51(tmp_path):
    """
    Тест для задачи: Написать функцию, которая получает путь к файлу, изменяет расширение имени файла на « (ID: 51)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s)
нач
цел p
p:=длин(s)
нц пока p > 0 и s[p] <> '\' и s[p] <> '.'
p:=p-1
кц
если p = 0 или s[p] = '\' то
знач:=s + ".bak"
иначе
знач:=s[1:p] + "bak"
все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  '", s, "'", нс
вывод "Получен ответ:    '", ansBad, "'", нс
вывод "Правильный ответ: '", ansOK, "'", нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_51.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_poluchaet_put_k_faylu_izmenyaet_r_51 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_poluchaet_put_k_faylu_izmenyaet_r_51: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_poluchaet_put_k_faylu_izmenyaet_r_51: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_poluchaet_put_k_faylu_izmenyaet_r_51: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_dvoichnoy_zap_52(tmp_path):
    """
    Тест для задачи: Написать функцию, которая переводит число из двоичной записи (символьной строки) в десятичную систему (результат - целое число) (ID: 52)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, dig
знач:=0
нц для i от 1 до длин(s)
знач:=знач*2
если s[i] = "1" то
знач:=знач+1
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_52.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_dvoichnoy_zap_52 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_dvoichnoy_zap_52: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_dvoichnoy_zap_52: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_dvoichnoy_zap_52: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_vosmerichnoy_53(tmp_path):
    """
    Тест для задачи: Написать функцию, которая переводит число из восьмеричной записи (символьной строки) в десятичную систему (результат - целое число) (ID: 53)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, dig
лог OK
знач:=0
нц для i от 1 до длин(s)
знач:=знач*8 + лит_в_цел(s[i],OK)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_53.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_vosmerichnoy_53 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_vosmerichnoy_53: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_vosmerichnoy_53: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_vosmerichnoy_53: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_shestnadtsate_54(tmp_path):
    """
    Тест для задачи: Написать функцию, которая переводит число из шестнадцатеричной записи (символьной строки) в десятичную систему (результат - целое число) (ID: 54)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, dig
лит digits = "0123456789ABCDEF"
знач:=0
нц для i от 1 до длин(s)
знач:=знач*16 + найти(s[i],digits) - 1
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_54.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_shestnadtsate_54 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_shestnadtsate_54: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_shestnadtsate_54: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_shestnadtsate_54: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_55(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает запись переданного ей числа X в системе счисления с основанием Y <= 10 (результат - символьная строка) (ID: 55)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лит __Решение__(цел x, osn)
нач
цел x1, dig
если x <= 0 то
знач:="0"
выход
все
знач:=""
x1:=x
нц пока x1 > 0
dig:=mod(x1,osn)
если dig < 10 то
знач:=цел_в_лит(dig) + знач
иначе
знач:=символ(код("A")+dig-10) + знач
все
x1:=div(x1,osn)
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел x, y, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Перевести число ", x, " в систему с основанием ", y, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_55.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_55 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_55: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_55: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_55: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_56(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает запись переданного ей числа X в системе счисления с основанием Y <= 36 (результат - символьная строка) (ID: 56)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лит __Решение__(цел x, osn)
нач
цел x1, dig
если x <= 0 то
знач:="0"
выход
все
знач:=""
x1:=x
нц пока x1 > 0
dig:=mod(x1,osn)
если dig < 10 то
знач:=цел_в_лит(dig) + знач
иначе
знач:=символ(код("A")+dig-10) + знач
все
x1:=div(x1,osn)
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел x, y, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Перевести число ", x, " в систему с основанием ", y, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_56.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_56 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_56: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_56: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_56: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_zapis_chisla_v_sisteme_57(tmp_path):
    """
    Тест для задачи: Написать функцию, которая переводит запись числа в системе счисления с заданным основанием N (символьную строку) в десятичную систему (результат - целое число) (ID: 57)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест", 5)
  вывод результат, нс
кон

алг цел __Решение__(лит s, цел N)
нач
цел i, dig
лит digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
знач:=0
нц для i от 1 до длин(s)
знач:=знач*N + найти(s[i],digits) - 1
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_57.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_perevodit_zapis_chisla_v_sisteme_57 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_zapis_chisla_v_sisteme_57: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_zapis_chisla_v_sisteme_57: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_perevodit_zapis_chisla_v_sisteme_57: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_zakanchivaetsya_li_pe_60(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, заканчивается ли переданное ей число на 0 (ID: 60)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лог __Решение__(цел N)
нач
знач:=mod(N,10) = 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_60.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_zakanchivaetsya_li_pe_60 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_zakanchivaetsya_li_pe_60: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_zakanchivaetsya_li_pe_60: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_zakanchivaetsya_li_pe_60: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_delitsya_li_peredanno_61(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, делится ли переданное ей число на 7 (ID: 61)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лог __Решение__(цел N)
нач
знач:= mod(N,7) = 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_61.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_delitsya_li_peredanno_61 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_delitsya_li_peredanno_61: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_delitsya_li_peredanno_61: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_delitsya_li_peredanno_61: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_62(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданный ей символ - цифра (ID: 62)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(сим c)
нач
лит цифры = "0123456789"
знач:= найти(c, цифры) > 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_62.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_62 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_62: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_62: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_62: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_63(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданный ей символ - шестнадцатеричная цифра (ID: 63)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(сим c)
нач
лит цифры = "0123456789ABCDEFabcdef"
знач:= найти(c, цифры) > 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_63.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_63 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_63: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_63: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_63: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_64(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданный ей символ - заглавная латинская буква (ID: 64)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(сим c)
нач
лит Латинские = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
знач:= найти(c, Латинские) > 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_64.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_64 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_64: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_64: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_64: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_65(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданный ей символ - заглавная или строчная латинская буква (ID: 65)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(сим c)
нач
лит Латинские = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
знач:= найти(c, Латинские) > 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_65.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_65 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_65: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_65: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_65: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_66(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданный ей символ - заглавная русская буква (ID: 66)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(сим c)
нач
лит Русские = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
знач:= найти(c, Русские) > 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_66.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_66 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_66: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_66: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_66: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_67(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданный ей символ - заглавная или строчная русская буква (ID: 67)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(сим c)
нач
лит Русские = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
знач:= найти(c, Русские) > 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_67.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_67 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_67: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_67: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_67: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_68(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданный ей шестизначный номер - «счастливый», то есть сумма его первых трёх цифр равна сумме последних трёх (ID: 68)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лог __Решение__(цел N0)
нач
цел i, s1=0, s2=0, N
N:=N0
нц для i от 1 до 3
s1:= s1 + mod(N,10)
N:= div(N,10)
кц
нц для i от 1 до 3
s2:= s2 + mod(N,10)
N:= div(N,10)
кц
знач:= s1 = s2
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_68.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_68 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_68: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_68: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_68: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_69(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданная ей строка - палиндром, то есть читается одинаково в обе стороны, как, например, слово «казак» (ID: 69)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(лит s)
нач
цел i, L
L:= длин(s)
знач:= да
нц для i  от 1 до div(L,2)
если s[i] <> s[L-i+1] то
знач:=нет
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_69.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_69 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_69: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_69: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_69: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_610(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданное ей число - палиндром (ID: 610)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лог __Решение__(цел N)
нач
лит s
цел i, L
знач:= да
s:=цел_в_лит(N)
L:=длин(s)
нц для i от 1 до div(L,2)
если s[i] <> s[L-i+1] то
знач:=нет
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_610.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_610 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_610: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_610: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_610: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_611(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданное ей число - простое (ID: 611)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лог __Решение__(цел N)
нач
цел i, L
знач:= да
нц для i от 2 до div(N,2)
если mod(N,i) = 0 то
знач:=нет
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_611.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_611 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_611: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_611: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_611: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_612(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданные ей два числа - взаимно простые, то есть, не имеют общего делителя, кроме 1 (ID: 612)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лог __Решение__(цел N, K)
нач
цел i, L
знач:= да
нц для i от 2 до N
если mod(N,i) = 0 и mod(K,i) = 0 то
знач:=нет
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_612.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_612 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_612: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_612: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_612: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_613(tmp_path):
    """
    Тест для задачи: Написать функцию, которая определяет, верно ли, что переданное ей число - гиперпростое (ID: 613)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лог __Решение__(цел N)
нач
цел i
знач:= нет
нц для i от 1 до __NP__
если N = __Hyper__[i] то
знач:=да
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_613.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_613 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_613: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_613: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_613: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_70(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает количество элементов массива, равных 1 (ID: 70)
    Курс: funkum
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
    test_file = tmp_path / "test_70.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_70 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_70: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_70: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_70: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_71(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает количество элементов массива, равных 1 (ID: 71)
    Курс: funkum
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
    test_file = tmp_path / "test_71.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_71 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_71: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_71: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_71: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_polozhit_72(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает количество положительных элементов массива (ID: 72)
    Курс: funkum
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
    test_file = tmp_path / "test_72.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_polozhit_72 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_polozhit_72: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_polozhit_72: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_polozhit_72: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_chyotnyh_73(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает количество чётных элементов массива (ID: 73)
    Курс: funkum
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
если mod(A[i],2) = 0 то
count:=count+1
все
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
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_chyotnyh_73 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_chyotnyh_73: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_chyotnyh_73: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_chyotnyh_73: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_maksimalnyy_element_74(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает максимальный элемент массива (ID: 74)
    Курс: funkum
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
    test_file = tmp_path / "test_74.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_maksimalnyy_element_74 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_maksimalnyy_element_74: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_maksimalnyy_element_74: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_maksimalnyy_element_74: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_minimalnyy_element_m_75(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает минимальный элемент массива (ID: 75)
    Курс: funkum
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
    test_file = tmp_path / "test_75.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_minimalnyy_element_m_75 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_minimalnyy_element_m_75: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_minimalnyy_element_m_75: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_minimalnyy_element_m_75: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_maksimalnogo_e_76(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает номер максимального элемента массива (ID: 76)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5, 0)
  вывод результат, нс
кон

алг цел __Решение__ (цел N, аргрез целтаб A[1:N])
нач
цел i, nMax
nMax:=1
нц для i от 2 до N 
если A[i] > A[nMax] то
nMax:=i
все
кц
знач:=nMax
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_76.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_maksimalnogo_e_76 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_maksimalnogo_e_76: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_maksimalnogo_e_76: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_maksimalnogo_e_76: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_minimalnogo_el_77(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает номер минимального элемента массива (ID: 77)
    Курс: funkum
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
    test_file = tmp_path / "test_77.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_minimalnogo_el_77 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_minimalnogo_el_77: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_minimalnogo_el_77: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_minimalnogo_el_77: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_elementov_mass_78(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает сумму элементов массива (ID: 78)
    Курс: funkum
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
    test_file = tmp_path / "test_78.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_elementov_mass_78 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_elementov_mass_78: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_elementov_mass_78: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_elementov_mass_78: {e}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_pervogo_elemen_79(tmp_path):
    """
    Тест для задачи: Написать функцию, которая возвращает номер первого элемента массива, равного заданному значению X (ID: 79)
    Курс: funkum
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
    test_file = tmp_path / "test_79.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_pervogo_elemen_79 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_pervogo_elemen_79: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_pervogo_elemen_79: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_pervogo_elemen_79: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_faktori_80(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает факториaл числа X - произведение всех натуральных чисел от 1 до X (ID: 80)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел i
знач:=1
нц для i от 1 до x
знач:=знач*i
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_80.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_faktori_80 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_faktori_80: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_faktori_80: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_faktori_80: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_chislo_81(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает число Фибоначчи F(N) с заданным номером (ID: 81)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=1
если x < 3 то выход все
цел i, f1 = 1, f2 = 1
нц для i от 3 до x
знач:=f1 + f2
f2:=f1
f1:=знач
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_81.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_chislo_81 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_chislo_81: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_chislo_81: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_chislo_81: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zadannu_82(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает заданную степень числа 2 (ID: 82)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=1
цел i
нц для i от 1 до x
знач:=2*знач
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_82.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zadannu_82 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zadannu_82: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zadannu_82: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zadannu_82: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_v_83(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает сумму всех натуральных чисел от 1 до заданного числа X (ID: 83)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел i
знач:=0
нц для i от 1 до x
знач:=знач+i
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_83.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_v_83 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_v_83: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_v_83: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_v_83: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_koliche_84(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает количество цифр числа (ID: 84)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел x1
x1:=x
знач:=0
нц пока x1 > 0
знач:=знач+1
x1:=div(x1,10)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_84.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_koliche_84 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_koliche_84: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_koliche_84: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_koliche_84: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_t_85(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает сумму цифр числа (ID: 85)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
цел x1
x1:=x
знач:=0
нц пока x1 > 0
знач:=знач+mod(x1,10)
x1:=div(x1,10)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_85.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_t_85 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_t_85: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_t_85: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_t_85: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_pervuyu_86(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает первую цифру в десятичной записи числа (ID: 86)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x)
нач
знач:=x
нц пока знач >= 10
знач:=div(знач,10)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_86.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_pervuyu_86 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_pervuyu_86: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_pervuyu_86: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_pervuyu_86: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_naibols_87(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает наибольший общий делитель (НОД) двух натуральных чисел (ID: 87)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг цел __Решение__(цел x0, y0)
нач
цел x, y
x:=x0; y:=y0
нц пока x <> 0 и y <> 0
если x > y то
x:= mod(x,y)
иначе
y:= mod(y,x)
все
кц
знач:=x+y
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел x, y, цел ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Заданные числа:   ", x, ", ", y, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_87.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_naibols_87 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_naibols_87: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_naibols_87: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_naibols_87: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_88(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает запись переданного ей числа в двоичной системе счисления (результат - символьная строка) (ID: 88)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лит __Решение__(цел x)
нач
цел x1, osn=2
если x <= 0 то
знач:="0"
выход
все
знач:=""
x1:=x
нц пока x1 > 0
знач:=цел_в_лит(mod(x1,osn)) + знач
x1:=div(x1,osn)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_88.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_88 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_88: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_88: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_88: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_89(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая возвращает запись переданного ей числа в шестнадцатеричной системе счисления (результат - символьная строка) (ID: 89)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__(5)
  вывод результат, нс
кон

алг лит __Решение__(цел x)
нач
цел x1, osn=16, dig
если x <= 0 то
знач:="0"
выход
все
знач:=""
x1:=x
нц пока x1 > 0
dig:=mod(x1,osn)
если dig < 10 то
знач:=цел_в_лит(dig) + знач
иначе
знач:=символ(код("A")+dig-10) + знач
все
x1:=div(x1,osn)
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(цел x, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Заданное число:   ", x, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_89.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_89 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_89: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_89: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_89: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_verno_li_810(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая определяет, верно ли, что переданная ей строка - палиндром (ID: 810)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(лит s)
нач
цел i, L
L:= длин(s)
знач:= да
нц для i  от 1 до div(L,2)
если s[i] <> s[L-i+1] то
знач:=нет
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_810.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_verno_li_810 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_verno_li_810: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_verno_li_810: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_verno_li_810: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_preobrazuet_dvoichnu_811(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая преобразует двоичную запись числа (символьную строку) в число (ID: 811)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, dig
знач:=0
нц для i от 1 до длин(s)
знач:=знач*2
если s[i] = "1" то
знач:=знач+1
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_811.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_preobrazuet_dvoichnu_811 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_preobrazuet_dvoichnu_811: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_preobrazuet_dvoichnu_811: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_preobrazuet_dvoichnu_811: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_skolko_r_812(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая определяет, сколько раз встречается в строке заданное слово (ID: 812)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s, word)
нач
лит s1
цел p, L
s1:=s
L:=длин(word)
знач:=0
p:=найти(word, s1)
нц пока p > 0
знач:=знач+1
s1:=удалить(s1, 1, p+L-1)
p:=найти(word, s1)
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_812.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_skolko_r_812 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_skolko_r_812: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_skolko_r_812: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_skolko_r_812: {e}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_zamenyaet_vo_vsey_st_813(tmp_path):
    """
    Тест для задачи: Написать рекурсивную функцию, которая заменяет во всей строке одну послендовательность символов на другую и возвращает изменённую строку (ID: 813)
    Курс: funkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s, word, new)
нач
лит s1
цел p, L
s1:=s
L:=длин(word)
знач:=""
p:=найти(word, s1)
нц пока p > 0
если p > 1 то
знач:=знач + s1[1:p-1]
все
знач:=знач + new
s1:=удалить(s1, 1, p+L-1)
p:=найти(word, s1)
кц
знач:=знач+s1
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_813.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_zamenyaet_vo_vsey_st_813 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_zamenyaet_vo_vsey_st_813: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_zamenyaet_vo_vsey_st_813: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_zamenyaet_vo_vsey_st_813: {e}")

