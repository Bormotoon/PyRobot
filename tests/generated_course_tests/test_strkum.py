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

# Автогенерированные тесты для курса: strkum
# Сгенерировано: 2025-06-09 11:49:00

def test_strkum_Nayti_pervyy_simvol_stroki_10(tmp_path):
    """
    Тест для задачи: Найти первый символ строки (ID: 10)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг сим __Решение__(лит s)
нач
знач:= s[1]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_10.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_pervyy_simvol_stroki_10 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_pervyy_simvol_stroki_10: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_pervyy_simvol_stroki_10: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_pervyy_simvol_stroki_10: {e}")


def test_strkum_Zamenit_pervyy_simvol_stroki_na_tsifru_0_11(tmp_path):
    """
    Тест для задачи: Заменить первый символ строки на цифру 0 (ID: 11)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
s[1]:="0"
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_11.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_pervyy_simvol_stroki_na_tsifru_0_11 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_pervyy_simvol_stroki_na_tsifru_0_11: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_pervyy_simvol_stroki_na_tsifru_0_11: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_pervyy_simvol_stroki_na_tsifru_0_11: {e}")


def test_strkum_Zamenit_pervye_dva_simvola_stroki_na_bukvy_Zh_12(tmp_path):
    """
    Тест для задачи: Заменить первые два символа строки на буквы Ж (ID: 12)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
s[1]:="Ж"
s[2]:="Ж"
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_12.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_pervye_dva_simvola_stroki_na_bukvy_Zh_12 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_pervye_dva_simvola_stroki_na_bukvy_Zh_12: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_pervye_dva_simvola_stroki_na_bukvy_Zh_12: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_pervye_dva_simvola_stroki_na_bukvy_Zh_12: {e}")


def test_strkum_Vychislit_dlinu_stroki_13(tmp_path):
    """
    Тест для задачи: Вычислить длину строки (ID: 13)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
знач:=длин(s)
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_13.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vychislit_dlinu_stroki_13 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vychislit_dlinu_stroki_13: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vychislit_dlinu_stroki_13: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vychislit_dlinu_stroki_13: {e}")


def test_strkum_Nayti_posledniy_simvol_stroki_14(tmp_path):
    """
    Тест для задачи: Найти последний символ строки (ID: 14)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг сим __Решение__(лит s)
нач
знач:= s[длин(s)]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_14.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_posledniy_simvol_stroki_14 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_posledniy_simvol_stroki_14: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_posledniy_simvol_stroki_14: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_posledniy_simvol_stroki_14: {e}")


def test_strkum_Vyyasnit_verno_li_chto_dlina_stroki_chyotnoe_chislo_15(tmp_path):
    """
    Тест для задачи: Выяснить, верно ли, что длина строки - чётное число (ID: 15)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(лит s)
нач
знач:= mod(длин(s),2) = 0
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_15.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vyyasnit_verno_li_chto_dlina_stroki_chyotnoe_chislo_15 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vyyasnit_verno_li_chto_dlina_stroki_chyotnoe_chislo_15: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vyyasnit_verno_li_chto_dlina_stroki_chyotnoe_chislo_15: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vyyasnit_verno_li_chto_dlina_stroki_chyotnoe_chislo_15: {e}")


def test_strkum_Zamenit_poslednie_dva_simvola_na_bukvy_Y_16(tmp_path):
    """
    Тест для задачи: Заменить последние два символа на буквы Ы (ID: 16)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел Len
Len:=длин(s)
s[Len]:="Ы"
s[Len-1]:="Ы"
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_16.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_poslednie_dva_simvola_na_bukvy_Y_16 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_poslednie_dva_simvola_na_bukvy_Y_16: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_poslednie_dva_simvola_na_bukvy_Y_16: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_poslednie_dva_simvola_na_bukvy_Y_16: {e}")


def test_strkum_Opredelit_verno_li_chto_pervyy_i_posledniy_simvoly_stroki_so_17(tmp_path):
    """
    Тест для задачи: Определить, верно ли, что первый и последний символы строки совпадают (ID: 17)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(лит s)
нач
знач:= s[1] = s[длин(s)]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_17.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Opredelit_verno_li_chto_pervyy_i_posledniy_simvoly_stroki_so_17 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Opredelit_verno_li_chto_pervyy_i_posledniy_simvoly_stroki_so_17: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Opredelit_verno_li_chto_pervyy_i_posledniy_simvoly_stroki_so_17: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Opredelit_verno_li_chto_pervyy_i_posledniy_simvoly_stroki_so_17: {e}")


def test_strkum_Nayti_sredniy_simvol_stroki_18(tmp_path):
    """
    Тест для задачи: Найти средний символ строки (ID: 18)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг сим __Решение__(лит s)
нач
знач:= s[div(длин(s),2)+1]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_18.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_sredniy_simvol_stroki_18 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_sredniy_simvol_stroki_18: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_sredniy_simvol_stroki_18: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_sredniy_simvol_stroki_18: {e}")


def test_strkum_Opredelit_verno_li_chto_pervyy_sredniy_i_posledniy_simvoly_s_19(tmp_path):
    """
    Тест для задачи: Определить, верно ли, что первый, средний и последний символы строки совпадают (ID: 19)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(лит s)
нач
знач:= (s[1] = s[длин(s)]) и (s[1] = s[div(длин(s),2)+1])
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_19.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Opredelit_verno_li_chto_pervyy_sredniy_i_posledniy_simvoly_s_19 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Opredelit_verno_li_chto_pervyy_sredniy_i_posledniy_simvoly_s_19: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Opredelit_verno_li_chto_pervyy_sredniy_i_posledniy_simvoly_s_19: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Opredelit_verno_li_chto_pervyy_sredniy_i_posledniy_simvoly_s_19: {e}")


def test_strkum_Pomenyat_mestami_pervyy_i_vtoroy_simvoly_stroki_110(tmp_path):
    """
    Тест для задачи: Поменять местами первый и второй символы строки (ID: 110)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
сим temp
temp:=s[1]; s[1]:=s[2]; s[2]:=temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_110.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Pomenyat_mestami_pervyy_i_vtoroy_simvoly_stroki_110 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Pomenyat_mestami_pervyy_i_vtoroy_simvoly_stroki_110: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Pomenyat_mestami_pervyy_i_vtoroy_simvoly_stroki_110: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Pomenyat_mestami_pervyy_i_vtoroy_simvoly_stroki_110: {e}")


def test_strkum_Pomenyat_mestami_pervyy_i_posledniy_simvoly_stroki_111(tmp_path):
    """
    Тест для задачи: Поменять местами первый и последний символы строки (ID: 111)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел L
сим temp
L:=длин(s)
temp:=s[1]; s[1]:=s[L]; s[L]:=temp
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_111.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Pomenyat_mestami_pervyy_i_posledniy_simvoly_stroki_111 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Pomenyat_mestami_pervyy_i_posledniy_simvoly_stroki_111: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Pomenyat_mestami_pervyy_i_posledniy_simvoly_stroki_111: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Pomenyat_mestami_pervyy_i_posledniy_simvoly_stroki_111: {e}")


def test_strkum_Zamenit_vse_simvoly_stroki_na_tsifry_5_20(tmp_path):
    """
    Тест для задачи: Заменить все символы строки на цифры 5 (ID: 20)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до длин(s)
s[i]:="5"
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_20.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_vse_simvoly_stroki_na_tsifry_5_20 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_vse_simvoly_stroki_na_tsifry_5_20: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_vse_simvoly_stroki_na_tsifry_5_20: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_vse_simvoly_stroki_na_tsifry_5_20: {e}")


def test_strkum_Zamenit_vse_simvoly_stroki_krome_pervogo_i_poslednego_na_tsi_21(tmp_path):
    """
    Тест для задачи: Заменить все символы строки, кроме первого и последнего, на цифры 6 (ID: 21)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 2 до длин(s)-1
s[i]:="6"
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_21.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_vse_simvoly_stroki_krome_pervogo_i_poslednego_na_tsi_21 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_vse_simvoly_stroki_krome_pervogo_i_poslednego_na_tsi_21: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_vse_simvoly_stroki_krome_pervogo_i_poslednego_na_tsi_21: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_vse_simvoly_stroki_krome_pervogo_i_poslednego_na_tsi_21: {e}")


def test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_22(tmp_path):
    """
    Тест для задачи: Заменить в строке все цифры 1 на цифры 0 (ID: 22)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до длин(s)
если s[i] = "1" то
s[i]:="0"
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_22.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_22 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_22: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_22: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_22: {e}")


def test_strkum_Zamenit_v_stroke_vse_simvoly_s_chyotnymi_nomerami_na_tochki_23(tmp_path):
    """
    Тест для задачи: Заменить в строке все символы с чётными номерами на точки (ID: 23)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 2 до длин(s) шаг 2
s[i]:="."
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_23.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_v_stroke_vse_simvoly_s_chyotnymi_nomerami_na_tochki_23 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_v_stroke_vse_simvoly_s_chyotnymi_nomerami_na_tochki_23: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_v_stroke_vse_simvoly_s_chyotnymi_nomerami_na_tochki_23: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_v_stroke_vse_simvoly_s_chyotnymi_nomerami_na_tochki_23: {e}")


def test_strkum_Zamenit_v_stroke_vse_tsifry_1_24(tmp_path):
    """
    Тест для задачи: Заменить в строке все цифры 1 (ID: 24)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до длин(s)
если "1" <= s[i] и s[i] <= "9" то
s[i]:="0"
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_24.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_v_stroke_vse_tsifry_1_24 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_v_stroke_vse_tsifry_1_24: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_v_stroke_vse_tsifry_1_24: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_v_stroke_vse_tsifry_1_24: {e}")


def test_strkum_Zamenit_vse_simvoly_pervoy_poloviny_stroki_na_tsifry_9_25(tmp_path):
    """
    Тест для задачи: Заменить все символы первой половины строки на цифры 9 (ID: 25)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до div(длин(s),2)
s[i]:="9"
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_25.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_vse_simvoly_pervoy_poloviny_stroki_na_tsifry_9_25 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_vse_simvoly_pervoy_poloviny_stroki_na_tsifry_9_25: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_vse_simvoly_pervoy_poloviny_stroki_na_tsifry_9_25: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_vse_simvoly_pervoy_poloviny_stroki_na_tsifry_9_25: {e}")


def test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_i_naoborot_vse_tsi_26(tmp_path):
    """
    Тест для задачи: Заменить в строке все цифры 1 на цифры 0 и наоборот (все цифры 0 на цифры 1) (ID: 26)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до длин(s)
если s[i] = "1" то
s[i]:="0"
иначе
если s[i] = "0" то
s[i]:="1"
все
все
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s0, sBad, sOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s0, нс
вывод "Получена строка:  ", sBad, нс
вывод "Правильный ответ: ", sOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_26.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_i_naoborot_vse_tsi_26 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_i_naoborot_vse_tsi_26: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_i_naoborot_vse_tsi_26: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_i_naoborot_vse_tsi_26: {e}")


def test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_t_27(tmp_path):
    """
    Тест для задачи: Заменить в строке все русские буквы А на буквы Б, и наоборот (только заглавные) (ID: 27)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до длин(s)
если s[i] = "А" то
s[i]:="Б"
иначе
если s[i] = "Б" то
s[i]:="А"
все
все
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s0, sBad, sOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s0, нс
вывод "Получена строка:  ", sBad, нс
вывод "Правильный ответ: ", sOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_27.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_t_27 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_t_27: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_t_27: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_t_27: {e}")


def test_strkum_Zamenit_v_pervoy_polovine_stroki_vse_tochki_na_znaki_voprosa_28(tmp_path):
    """
    Тест для задачи: Заменить в первой половине строки все точки на знаки вопроса и наоборот (ID: 28)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до div(длин(s),2)
если s[i] = "." то
s[i]:="?"
иначе
если s[i] = "?" то
s[i]:="."
все
все
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s0, sBad, sOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s0, нс
вывод "Получена строка:  ", sBad, нс
вывод "Правильный ответ: ", sOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_28.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_v_pervoy_polovine_stroki_vse_tochki_na_znaki_voprosa_28 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_v_pervoy_polovine_stroki_vse_tochki_na_znaki_voprosa_28: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_v_pervoy_polovine_stroki_vse_tochki_na_znaki_voprosa_28: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_v_pervoy_polovine_stroki_vse_tochki_na_znaki_voprosa_28: {e}")


def test_strkum_Zamenit_vse_simvoly_vtoroy_poloviny_stroki_na_tsifry_8_29(tmp_path):
    """
    Тест для задачи: Заменить все символы второй половины строки на цифры 8 (ID: 29)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от div(длин(s),2)+1 до длин(s) 
s[i]:="8"
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_29.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_vse_simvoly_vtoroy_poloviny_stroki_na_tsifry_8_29 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_vse_simvoly_vtoroy_poloviny_stroki_na_tsifry_8_29: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_vse_simvoly_vtoroy_poloviny_stroki_na_tsifry_8_29: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_vse_simvoly_vtoroy_poloviny_stroki_na_tsifry_8_29: {e}")


def test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_s_210(tmp_path):
    """
    Тест для задачи: Заменить в строке все русские буквы А на буквы Б, и наоборот (строчные на строчные, заглавные на заглавные) (ID: 210)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от 1 до длин(s)
если s[i] = "а" то
s[i]:="б"
иначе
если s[i] = "б" то
s[i]:="а"
все
все
если s[i] = "А" то
s[i]:="Б"
иначе
если s[i] = "Б" то
s[i]:="А"
все
все
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s0, sBad, sOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s0, нс
вывод "Получена строка:  ", sBad, нс
вывод "Правильный ответ: ", sOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_210.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_s_210 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_s_210: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_s_210: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_s_210: {e}")


def test_strkum_Zamenit_vo_vtoroy_polovine_stroki_vse_tochki_na_znaki_vopros_211(tmp_path):
    """
    Тест для задачи: Заменить во второй половине строки все точки на знаки вопроса и наоборот (ID: 211)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  лит s
  s := "тест"
  __Решение__(s)
  вывод "Процедура __Решение__ выполнена", нс
кон

алг __Решение__(аргрез лит s)
нач
цел i
нц для i от div(длин(s),2)+1 до длин(s)
если s[i] = "." то
s[i]:="?"
иначе
если s[i] = "?" то
s[i]:="."
все
все
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s0, sBad, sOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s0, нс
вывод "Получена строка:  ", sBad, нс
вывод "Правильный ответ: ", sOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_211.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Zamenit_vo_vtoroy_polovine_stroki_vse_tochki_na_znaki_vopros_211 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Zamenit_vo_vtoroy_polovine_stroki_vse_tochki_na_znaki_vopros_211: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Zamenit_vo_vtoroy_polovine_stroki_vse_tochki_na_znaki_vopros_211: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Zamenit_vo_vtoroy_polovine_stroki_vse_tochki_na_znaki_vopros_211: {e}")


def test_strkum_Podschitat_kolichestvo_tsifr_0_v_simvolnoy_stroke_30(tmp_path):
    """
    Тест для задачи: Подсчитать количество цифр 0 в символьной строке (ID: 30)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, count=0
нц для i от 1 до длин(s)
если s[i] = "0" то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_30.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_kolichestvo_tsifr_0_v_simvolnoy_stroke_30 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_kolichestvo_tsifr_0_v_simvolnoy_stroke_30: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_kolichestvo_tsifr_0_v_simvolnoy_stroke_30: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_kolichestvo_tsifr_0_v_simvolnoy_stroke_30: {e}")


def test_strkum_Podschitat_obschee_kolichestvo_tsifr_0_31(tmp_path):
    """
    Тест для задачи: Подсчитать общее количество цифр 0 (ID: 31)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, count=0
нц для i от 1 до длин(s)
если "0" <= s[i] и s[i] <= "9" то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_31.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_obschee_kolichestvo_tsifr_0_31 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_obschee_kolichestvo_tsifr_0_31: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_obschee_kolichestvo_tsifr_0_31: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_obschee_kolichestvo_tsifr_0_31: {e}")


def test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_zaglavnyh_v_pe_32(tmp_path):
    """
    Тест для задачи: Подсчитать общее количество латинских букв (заглавных) в первой половине символьной строки (ID: 32)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, count=0
нц для i от 1 до div(длин(s),2)
если "A" <= s[i] и s[i] <= "Z" то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_32.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_zaglavnyh_v_pe_32 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_zaglavnyh_v_pe_32: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_zaglavnyh_v_pe_32: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_zaglavnyh_v_pe_32: {e}")


def test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_33(tmp_path):
    """
    Тест для задачи: Подсчитать общее количество латинских букв A (ID: 33)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, count=0
нц для i от 1 до div(длин(s),2)
если "A" <= s[i] и s[i] <= "Z" или "0" <= s[i] и s[i] <= "9" то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_33.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_33 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_33: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_33: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_33: {e}")


def test_strkum_Podschitat_kolichestvo_par_odinakovyh_simvolov_stoyaschih_ry_34(tmp_path):
    """
    Тест для задачи: Подсчитать количество пар одинаковых символов, стоящих рядом (ID: 34)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, count=0
нц для i от 2 до длин(s)
если s[i-1] = s[i] то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_34.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_kolichestvo_par_odinakovyh_simvolov_stoyaschih_ry_34 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_kolichestvo_par_odinakovyh_simvolov_stoyaschih_ry_34: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_kolichestvo_par_odinakovyh_simvolov_stoyaschih_ry_34: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_kolichestvo_par_odinakovyh_simvolov_stoyaschih_ry_34: {e}")


def test_strkum_Podschitat_obschee_kolichestvo_bukv_A_i_B_tolko_zaglavnyh_vo_35(tmp_path):
    """
    Тест для задачи: Подсчитать общее количество букв А и Б (только заглавных) во второй половине символьной строки (ID: 35)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, count=0
нц для i от div(длин(s),2)+1 до длин(s)
если s[i] = "А" или s[i] = "Б" то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_35.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_obschee_kolichestvo_bukv_A_i_B_tolko_zaglavnyh_vo_35 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_obschee_kolichestvo_bukv_A_i_B_tolko_zaglavnyh_vo_35: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_obschee_kolichestvo_bukv_A_i_B_tolko_zaglavnyh_vo_35: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_obschee_kolichestvo_bukv_A_i_B_tolko_zaglavnyh_vo_35: {e}")


def test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_36(tmp_path):
    """
    Тест для задачи: Подсчитать общее количество латинских букв A (ID: 36)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел i, count=0
нц для i от div(длин(s),2)+1 до длин(s)
если "A" <= s[i] и s[i] <= "Z" или "a" <= s[i] и s[i] <= "z" то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_36.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_36 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_36: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_36: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_36: {e}")


def test_strkum_Vydelit_imya_iz_stroki_v_kotoroy_zapisany_imya_familiya_i_ot_40(tmp_path):
    """
    Тест для задачи: Выделить имя из строки, в которой записаны имя, фамилия и отчество, разделённые одиночными пробелами (ID: 40)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s)
нач
цел p 
p:=позиция(' ', s)
знач:=s[1:p-1]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_40.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vydelit_imya_iz_stroki_v_kotoroy_zapisany_imya_familiya_i_ot_40 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vydelit_imya_iz_stroki_v_kotoroy_zapisany_imya_familiya_i_ot_40: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vydelit_imya_iz_stroki_v_kotoroy_zapisany_imya_familiya_i_ot_40: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vydelit_imya_iz_stroki_v_kotoroy_zapisany_imya_familiya_i_ot_40: {e}")


def test_strkum_Vydelit_otchestvo_iz_stroki_v_kotoroy_zapisany_imya_familiya_41(tmp_path):
    """
    Тест для задачи: Выделить отчество из строки, в которой записаны имя, фамилия и отчество, разделённые одиночными пробелами (ID: 41)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s
s:=s0
p:=позиция(' ', s)
удалить(s, 1, p)
p:=позиция(' ', s)
знач:=s[1:p-1]
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_41.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vydelit_otchestvo_iz_stroki_v_kotoroy_zapisany_imya_familiya_41 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vydelit_otchestvo_iz_stroki_v_kotoroy_zapisany_imya_familiya_41: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vydelit_otchestvo_iz_stroki_v_kotoroy_zapisany_imya_familiya_41: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vydelit_otchestvo_iz_stroki_v_kotoroy_zapisany_imya_familiya_41: {e}")


def test_strkum_Vydelit_familiyu_iz_stroki_v_kotoroy_zapisany_imya_familiya_42(tmp_path):
    """
    Тест для задачи: Выделить фамилию из строки, в которой записаны имя, фамилия и отчество, разделённые одиночными пробелами (ID: 42)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s
s:=s0
p:=позиция(' ', s)
удалить(s, 1, p)
p:=позиция(' ', s)
удалить(s, 1, p)
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_42.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vydelit_familiyu_iz_stroki_v_kotoroy_zapisany_imya_familiya_42 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vydelit_familiyu_iz_stroki_v_kotoroy_zapisany_imya_familiya_42: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vydelit_familiyu_iz_stroki_v_kotoroy_zapisany_imya_familiya_42: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vydelit_familiyu_iz_stroki_v_kotoroy_zapisany_imya_familiya_42: {e}")


def test_strkum_Vydelit_god_rozhdeniya_iz_stroki_v_kotoroy_zapisany_imya_fam_43(tmp_path):
    """
    Тест для задачи: Выделить год рождения из строки, в которой записаны имя, фамилия, отчество и год рождения, разделённые одиночными пробелами (ID: 43)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s
s:=s0
p:=позиция(' ', s)
удалить(s, 1, p)
p:=позиция(' ', s)
удалить(s, 1, p)
p:=позиция(' ', s)
удалить(s, 1, p)
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_43.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vydelit_god_rozhdeniya_iz_stroki_v_kotoroy_zapisany_imya_fam_43 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vydelit_god_rozhdeniya_iz_stroki_v_kotoroy_zapisany_imya_fam_43: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vydelit_god_rozhdeniya_iz_stroki_v_kotoroy_zapisany_imya_fam_43: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vydelit_god_rozhdeniya_iz_stroki_v_kotoroy_zapisany_imya_fam_43: {e}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_44(tmp_path):
    """
    Тест для задачи: В строке записаны имя, фамилия и отчество, разделённые одиночными пробелами (ID: 44)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s, имя, отчество
s:=s0
p:=позиция(' ', s)
имя:=s[1:p-1]
удалить(s, 1, p)
p:=позиция(' ', s)
отчество:=s[1:p-1]
удалить(s, 1, p)
знач:=имя + " " + s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_44.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_44 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_44: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_44: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_44: {e}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_45(tmp_path):
    """
    Тест для задачи: В строке записаны имя, фамилия и отчество, разделённые одиночными пробелами (ID: 45)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s, имя, отчество
s:=s0
p:=позиция(' ', s)
имя:=s[1:p-1]
удалить(s, 1, p)
p:=позиция(' ', s)
отчество:=s[1:p-1]
удалить(s, 1, p)
знач:=s + " " + имя
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_45.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_45 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_45: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_45: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_45: {e}")


def test_strkum_V_stroke_zapisany_imya_familiya_otchestvo_i_god_rozhdeniya_r_46(tmp_path):
    """
    Тест для задачи: В строке записаны имя, фамилия, отчество и год рождения, разделённые одиночными пробелами (ID: 46)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s, имя, фамилия, год
s:=s0
p:=позиция(' ', s)
имя:=s[1:p-1]
удалить(s, 1, p)
p:=позиция(' ', s)
удалить(s, 1, p)
p:=позиция(' ', s)
фамилия:=s[1:p-1]
удалить(s, 1, p)
знач:=фамилия + " " + имя + " (" + s + ")"
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_46.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_V_stroke_zapisany_imya_familiya_otchestvo_i_god_rozhdeniya_r_46 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_V_stroke_zapisany_imya_familiya_otchestvo_i_god_rozhdeniya_r_46: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_V_stroke_zapisany_imya_familiya_otchestvo_i_god_rozhdeniya_r_46: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_V_stroke_zapisany_imya_familiya_otchestvo_i_god_rozhdeniya_r_46: {e}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_47(tmp_path):
    """
    Тест для задачи: В строке записаны имя, фамилия и отчество, разделённые одиночными пробелами (ID: 47)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s, имя, отчество
s:=s0
p:=позиция(' ', s)
имя:=s[1:p-1]
удалить(s, 1, p)
p:=позиция(' ', s)
отчество:=s[1:p-1]
удалить(s, 1, p)
знач:=s + " " + имя[1] + "." + отчество[1] + "."
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_47.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_47 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_47: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_47: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_47: {e}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_48(tmp_path):
    """
    Тест для задачи: В строке записаны имя, фамилия и отчество, разделённые одиночными пробелами (ID: 48)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p 
лит s, имя, отчество
s:=s0
p:=позиция(' ', s)
имя:=s[1:p-1]
удалить(s, 1, p)
p:=позиция(' ', s)
отчество:=s[1:p-1]
удалить(s, 1, p)
знач:=имя[1] + "." + отчество[1] + ". " + s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_48.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_48 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_48: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_48: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_48: {e}")


def test_strkum_Udalit_lishnie_probely_v_nachale_stroki_50(tmp_path):
    """
    Тест для задачи: Удалить лишние пробелы в начале строки (ID: 50)
    Курс: strkum
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
удалить(s,1,1)
кц
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_50.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Udalit_lishnie_probely_v_nachale_stroki_50 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Udalit_lishnie_probely_v_nachale_stroki_50: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Udalit_lishnie_probely_v_nachale_stroki_50: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Udalit_lishnie_probely_v_nachale_stroki_50: {e}")


def test_strkum_Udalit_lishnie_probely_v_kontse_stroki_51(tmp_path):
    """
    Тест для задачи: Удалить лишние пробелы в конце строки (ID: 51)
    Курс: strkum
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
удалить(s,длин(s),1)
кц
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_51.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Udalit_lishnie_probely_v_kontse_stroki_51 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Udalit_lishnie_probely_v_kontse_stroki_51: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Udalit_lishnie_probely_v_kontse_stroki_51: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Udalit_lishnie_probely_v_kontse_stroki_51: {e}")


def test_strkum_Udalit_lishnie_probely_v_nachale_i_v_kontse_stroki_52(tmp_path):
    """
    Тест для задачи: Удалить лишние пробелы в начале и в конце строки (ID: 52)
    Курс: strkum
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
удалить(s,1,1)
кц
нц пока длин(s) > 0 и s[длин(s)] = " "
удалить(s,длин(s),1)
кц
знач:=s
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_52.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Udalit_lishnie_probely_v_nachale_i_v_kontse_stroki_52 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Udalit_lishnie_probely_v_nachale_i_v_kontse_stroki_52: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Udalit_lishnie_probely_v_nachale_i_v_kontse_stroki_52: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Udalit_lishnie_probely_v_nachale_i_v_kontse_stroki_52: {e}")


def test_strkum_Udalit_vse_mnozhestvennye_probely_mezhdu_slovami_53(tmp_path):
    """
    Тест для задачи: Удалить все множественные пробелы между словами (ID: 53)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p
лит s
s:= s0
нц
p:=позиция("  ",s)
если p < 1 то выход все
удалить(s,p,1)
кц
если s = " " то s:= "" все
знач:=s
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
    test_file = tmp_path / "test_53.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Udalit_vse_mnozhestvennye_probely_mezhdu_slovami_53 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Udalit_vse_mnozhestvennye_probely_mezhdu_slovami_53: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Udalit_vse_mnozhestvennye_probely_mezhdu_slovami_53: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Udalit_vse_mnozhestvennye_probely_mezhdu_slovami_53: {e}")


def test_strkum_Udalit_vse_lishnie_probely_v_nachale_i_v_kontse_stroki_a_tak_54(tmp_path):
    """
    Тест для задачи: Удалить все лишние пробелы в начале и в конце строки, а также сдвоенные пробелы между словами (ID: 54)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел p
лит s
s:= s0
нц пока длин(s) > 0 и s[1] = " "
удалить(s,1,1)
кц
нц пока длин(s) > 0 и s[длин(s)] = " "
удалить(s,длин(s),1)
кц
нц
p:=позиция("  ",s)
если p < 1 то выход все
удалить(s,p,1)
кц
знач:=s
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
    test_file = tmp_path / "test_54.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Udalit_vse_lishnie_probely_v_nachale_i_v_kontse_stroki_a_tak_54 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Udalit_vse_lishnie_probely_v_nachale_i_v_kontse_stroki_a_tak_54: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Udalit_vse_lishnie_probely_v_nachale_i_v_kontse_stroki_a_tak_54: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Udalit_vse_lishnie_probely_v_nachale_i_v_kontse_stroki_a_tak_54: {e}")


def test_strkum_Podschitat_kolichestvo_simvolov_stroki_okruzhennyh_probelami_55(tmp_path):
    """
    Тест для задачи: Подсчитать количество символов строки, окруженных пробелами слева и справа (ID: 55)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s0)
нач
цел i, count=0
лит s
|s:=" " + s0 + " "
s:=s0
нц для i от 2 до длин(s)-1
если s[i-1]=" " и s[i]<>" " и s[i+1]=" " то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_55.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_kolichestvo_simvolov_stroki_okruzhennyh_probelami_55 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_kolichestvo_simvolov_stroki_okruzhennyh_probelami_55: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_kolichestvo_simvolov_stroki_okruzhennyh_probelami_55: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_kolichestvo_simvolov_stroki_okruzhennyh_probelami_55: {e}")


def test_strkum_Podschitat_kolichestvo_slov_v_simvolnoy_stroke_56(tmp_path):
    """
    Тест для задачи: Подсчитать количество слов в символьной строке (ID: 56)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s0)
нач
цел i, count=0
лит s
s:=" " + s0
нц для i от 2 до длин(s)
если s[i-1]=" " и s[i]<>" " то
count:=count+1
все
кц
знач:=count
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_56.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_kolichestvo_slov_v_simvolnoy_stroke_56 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_kolichestvo_slov_v_simvolnoy_stroke_56: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_kolichestvo_slov_v_simvolnoy_stroke_56: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_kolichestvo_slov_v_simvolnoy_stroke_56: {e}")


def test_strkum_Podschitat_kolichestvo_slov_kotoryy_nachinayutsya_s_russkoy_57(tmp_path):
    """
    Тест для задачи: Подсчитать количество слов, который начинаются с русской буквы "ю" (заглавной или строчной) (ID: 57)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s0)
нач
цел i, count=0
лит s
s:=" " + s0
нц для i от 2 до длин(s)
если s[i-1]=" " и (s[i]="ю" или s[i]="Ю")то
count:=count+1
все
кц
знач:=count
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, цел ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  '", s, "'", нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_57.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Podschitat_kolichestvo_slov_kotoryy_nachinayutsya_s_russkoy_57 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Podschitat_kolichestvo_slov_kotoryy_nachinayutsya_s_russkoy_57: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Podschitat_kolichestvo_slov_kotoryy_nachinayutsya_s_russkoy_57: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Podschitat_kolichestvo_slov_kotoryy_nachinayutsya_s_russkoy_57: {e}")


def test_strkum_Nayti_pervoe_slovo_v_simvolnoy_stroke_58(tmp_path):
    """
    Тест для задачи: Найти первое слово в символьной строке (ID: 58)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел i 
лит s
s:= " " + s0
i:=1
знач:= ""
нц пока s[i] = " "; i:=i+1 кц
нц пока i <= длин(s) и s[i] <> " "
знач:= знач + s[i]
i:=i+1
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  '", s, "'", нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_58.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_pervoe_slovo_v_simvolnoy_stroke_58 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_pervoe_slovo_v_simvolnoy_stroke_58: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_pervoe_slovo_v_simvolnoy_stroke_58: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_pervoe_slovo_v_simvolnoy_stroke_58: {e}")


def test_strkum_Nayti_poslednee_slovo_v_simvolnoy_stroke_59(tmp_path):
    """
    Тест для задачи: Найти последнее слово в символьной строке (ID: 59)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лит __Решение__(лит s0)
нач
цел i 
лит s
s:= s0 + " "
i:=длин(s)
знач:= ""
нц пока s[i] = " "; i:=i-1 кц
нц пока i > 0 и s[i] <> " "
знач:= s[i] + знач
i:=i-1
кц
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, лит ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  '", s, "'", нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_59.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_poslednee_slovo_v_simvolnoy_stroke_59 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_poslednee_slovo_v_simvolnoy_stroke_59: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_poslednee_slovo_v_simvolnoy_stroke_59: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_poslednee_slovo_v_simvolnoy_stroke_59: {e}")


def test_strkum_Opredelit_verno_li_chto_stroka_predstavlyaet_soboy_palindrom_510(tmp_path):
    """
    Тест для задачи: Определить, верно ли, что строка представляет собой палиндром (то есть, читается одинаково слева направо и справа налево) (ID: 510)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(лит s)
нач
цел i, len
len:=длин(s)
знач:=да
нц для i от 1 до div(len,2)
если s[i] <> s[len-i+1] то
знач:=нет
выход
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
        print(f"Test test_strkum_Opredelit_verno_li_chto_stroka_predstavlyaet_soboy_palindrom_510 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Opredelit_verno_li_chto_stroka_predstavlyaet_soboy_palindrom_510: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Opredelit_verno_li_chto_stroka_predstavlyaet_soboy_palindrom_510: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Opredelit_verno_li_chto_stroka_predstavlyaet_soboy_palindrom_510: {e}")


def test_strkum_Opredelit_verno_li_chto_obe_poloviny_stroki_predstavlyayut_s_511(tmp_path):
    """
    Тест для задачи: Определить, верно ли, что обе половины строки представляют собой палиндромы (то есть, читаются одинаково слева направо и справа налево) (ID: 511)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг лог __Решение__(лит s)
нач
цел i, len
len:=div(длин(s),2)
знач:=да
нц для i от 1 до div(len,2)
если s[i] <> s[len-i+1] то
знач:=нет
выход
все
кц
нц для i от 1 до div(len,2)
если s[len+i] <> s[len+len-i+1] то
знач:=нет
выход
все
кц
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_511.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Opredelit_verno_li_chto_obe_poloviny_stroki_predstavlyayut_s_511 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Opredelit_verno_li_chto_obe_poloviny_stroki_predstavlyayut_s_511: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Opredelit_verno_li_chto_obe_poloviny_stroki_predstavlyayut_s_511: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Opredelit_verno_li_chto_obe_poloviny_stroki_predstavlyayut_s_511: {e}")


def test_strkum_Nayti_summu_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_60(tmp_path):
    """
    Тест для задачи: Найти сумму двух чисел, записанную в виде символьной строки (ID: 60)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2
лог ОК
p:=позиция("+",s)
n1:=лит_в_цел(s[1:p-1], ОК)
n2:=лит_в_цел(s[p+1:длин(s)], ОК)
знач:=n1+n2
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_60.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_summu_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_60 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_summu_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_60: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_summu_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_60: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_summu_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_60: {e}")


def test_strkum_Nayti_raznost_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_strok_61(tmp_path):
    """
    Тест для задачи: Найти разность двух чисел, записанную в виде символьной строки (ID: 61)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2
лог ОК
p:=позиция("-",s)
n1:=лит_в_цел(s[1:p-1], ОК)
n2:=лит_в_цел(s[p+1:длин(s)], ОК)
знач:=n1-n2
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_61.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_raznost_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_strok_61 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_raznost_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_strok_61: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_raznost_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_strok_61: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_raznost_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_strok_61: {e}")


def test_strkum_Nayti_proizvedenie_dvuh_chisel_zapisannoe_v_vide_simvolnoy_s_62(tmp_path):
    """
    Тест для задачи: Найти произведение двух чисел, записанное в виде символьной строки (ID: 62)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2
лог ОК
p:=позиция("*",s)
n1:=лит_в_цел(s[1:p-1], ОК)
n2:=лит_в_цел(s[p+1:длин(s)], ОК)
знач:=n1*n2
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_62.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_proizvedenie_dvuh_chisel_zapisannoe_v_vide_simvolnoy_s_62 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_proizvedenie_dvuh_chisel_zapisannoe_v_vide_simvolnoy_s_62: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_proizvedenie_dvuh_chisel_zapisannoe_v_vide_simvolnoy_s_62: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_proizvedenie_dvuh_chisel_zapisannoe_v_vide_simvolnoy_s_62: {e}")


def test_strkum_Nayti_summu_tryoh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_63(tmp_path):
    """
    Тест для задачи: Найти сумму трёх чисел, записанную в виде символьной строки (ID: 63)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2, n3
лит s1
лог ОК
p:=позиция("+",s)
n1:=лит_в_цел(s[1:p-1], ОК)
s1:=s[p+1:длин(s)];
p:=позиция("+",s1)
n2:=лит_в_цел(s1[1:p-1], ОК)
n3:=лит_в_цел(s1[p+1:длин(s1)], ОК)
знач:=n1+n2+n3
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_63.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Nayti_summu_tryoh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_63 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Nayti_summu_tryoh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_63: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Nayti_summu_tryoh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_63: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Nayti_summu_tryoh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_63: {e}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_64(tmp_path):
    """
    Тест для задачи: Вычислить выражение с тремя числами, первая операция - «+», вторая - «-» (ID: 64)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2, n3
лит s1
лог ОК
p:=позиция("+",s)
n1:=лит_в_цел(s[1:p-1], ОК)
s1:=s[p+1:длин(s)];
p:=позиция("-",s1)
n2:=лит_в_цел(s1[1:p-1], ОК)
n3:=лит_в_цел(s1[p+1:длин(s1)], ОК)
знач:=n1+n2-n3
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_64.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_64 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_64: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_64: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_64: {e}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_65(tmp_path):
    """
    Тест для задачи: Вычислить выражение с тремя числами, первая операция - «-», вторая - «+» (ID: 65)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2, n3
лит s1
лог ОК
p:=позиция("-",s)
n1:=лит_в_цел(s[1:p-1], ОК)
s1:=s[p+1:длин(s)];
p:=позиция("+",s1)
n2:=лит_в_цел(s1[1:p-1], ОК)
n3:=лит_в_цел(s1[p+1:длин(s1)], ОК)
знач:=n1-n2+n3
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_65.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_65 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_65: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_65: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_65: {e}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_odna_iz_operatsiy_dru_66(tmp_path):
    """
    Тест для задачи: Вычислить выражение с тремя числами, одна из операций - «+», другая - «-» (ID: 66)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2, n3
лит s1
сим op1, op2
лог ОК
p:=1;
нц пока s[p]<>"+"  и  s[p]<>"-"
p:=p+1
кц
op1:=s[p]
n1:=лит_в_цел(s[1:p-1], ОК)
s1:=s[p+1:длин(s)];
p:=1;
нц пока s1[p]<>"+"  и  s1[p]<>"-"
p:=p+1
кц
op2:=s1[p]
n2:=лит_в_цел(s1[1:p-1], ОК)
n3:=лит_в_цел(s1[p+1:длин(s1)], ОК)
если op1 = "+" то
знач:=n1+n2-n3
иначе
знач:=n1-n2+n3
все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, цел ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_66.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_odna_iz_operatsiy_dru_66 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_odna_iz_operatsiy_dru_66: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_odna_iz_operatsiy_dru_66: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_odna_iz_operatsiy_dru_66: {e}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_67(tmp_path):
    """
    Тест для задачи: Вычислить выражение с тремя числами, используются операции «+» и «-» (ID: 67)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2, n3
лит s1
сим op1, op2
лог ОК
p:=1;
нц пока s[p]<>"+"  и  s[p]<>"-"
p:=p+1
кц
op1:=s[p]
n1:=лит_в_цел(s[1:p-1], ОК)
s1:=s[p+1:длин(s)];
p:=1;
нц пока s1[p]<>"+"  и  s1[p]<>"-"
p:=p+1
кц
op2:=s1[p]
n2:=лит_в_цел(s1[1:p-1], ОК)
n3:=лит_в_цел(s1[p+1:длин(s1)], ОК)
если op1 = "+" то
знач:=n1+n2
иначе
знач:=n1-n2
все
если op2 = "+" то
знач:=знач+n3
иначе
знач:=знач-n3
все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, цел ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_67.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_67 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_67: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_67: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_67: {e}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_68(tmp_path):
    """
    Тест для задачи: Вычислить выражение с тремя числами, используются операции «*», «+» и «-» (ID: 68)
    Курс: strkum
    """
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг цел __Решение__(лит s)
нач
цел p, n1, n2, n3
лит s1
сим op1, op2
лог ОК
p:=1;
нц пока s[p]<>"+"  и  s[p]<>"-"  и  s[p]<>"*"
p:=p+1
кц
op1:=s[p]
n1:=лит_в_цел(s[1:p-1], ОК)
s1:=s[p+1:длин(s)];
p:=1;
нц пока s1[p]<>"+"  и  s1[p]<>"-"  и  s1[p]<>"*"
p:=p+1
кц
op2:=s1[p]
n2:=лит_в_цел(s1[1:p-1], ОК)
n3:=лит_в_цел(s1[p+1:длин(s1)], ОК)
если op2 = "*" то
знач:=__Calc__(n1,__Calc__(n2,n3,op2),op1)
иначе
знач:=__Calc__(__Calc__(n1,n2,op1),n3,op2)
все
кон
|-------------------------------------------------------
| Вывод сообщения об ошибке
|-------------------------------------------------------
алг __Ошибка__(лит s, цел ansBad, ansOK)
нач
вывод "Программа работает неверно!", нс
вывод "Исходная строка:  ", s, нс
вывод "Получен ответ:    ", ansBad, нс
вывод "Правильный ответ: ", ansOK, нс
кон'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_68.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор через существующую функцию
    try:
        output = run_kumir_program(str(test_file))
        print(f"Test test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_68 completed successfully. Output: {output[:100]}")
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_68: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_68: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_68: {e}")

