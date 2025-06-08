import pytest  # type: ignore
import os
import sys
from io import StringIO

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir
from pyrobot.backend.kumir_interpreter.kumir_exceptions import KumirSyntaxError, KumirEvalError

# Определяем директорию с примерами КуМир относительно текущего файла
current_dir = os.path.dirname(os.path.abspath(__file__))
# Исправляем путь на tests/polyakov_kum
PROGRAMS_DIR = os.path.join(current_dir, "polyakov_kum")

from typing import List, Tuple, Optional

TEST_CASES: List[Tuple[str, Optional[str], Optional[str]]] = [
    ('1-empty.kum', None, ''),
    ('2-2+2.kum', None, '2+2=?\nОтвет: 4\n'),
    ('3-a+b.kum', '2\n3\n', '2 3\n5\n'),
    ('4-a+b.kum', '10\n20\n', 'Введите два целых числа: 10 20\n10+20=30\n'),
    ('6-format.kum', None, '>  123<\n1.2345678\n>  1.235<\n'),
    ('7-rand.kum', None, None),
    ('8-if.kum', '5\n7\n', 'Введите два целых числа: 5 7\nМаксимальное число:\n7\n7\n7\n7\n'),
    ('9-if.kum', '-3\n5\n', 'Введите возраст Андрея и Бориса: -3 5\nБорис старше\n'),
    ('10-and.kum', '27\n', "Введите возраст: 27\nподходит\n"),
    ('11-switch.kum', '2\n', 'Введите номер месяца: 2\nфевраль\n'),
    ('12-switch.kum', '7\n', '7\n1\n'),
    ('13-loopN.kum', '5\n', 'Сколько раз сделать? 5\nпривет\nпривет\nпривет\nпривет\nпривет\n'),
    ('14-while.kum', '5\n', 'Сколько раз сделать? 5\nпривет\nпривет\nпривет\nпривет\nпривет\n'),
    ('15-while.kum', '12345\n', "Введите целое число: 12345\nЦифр в числе: 5\n"),
    ('16-repeat.kum', '-1\n0\n2\n', 'Введите целое положительное число: -1\n0\n2\nВведено число 2\n  и до него 2 ошибочных значений(я)\n'),
    ('17-for.kum', '5\n', '5\n2 4 8 16 32 \n'),
    ('18-downto.kum', '5\n', '5\n32 16 8 4 2 \n'),
    ('19-prime.kum', '17\n', 'Введите максимальное число: 17\nПростые числа: 2 3 5 7 11 13 17 \n'),
    ('20-proc-err.kum', '-1\n', '-1\nОшибка программы\n'),
    ('21-proc-bin.kum', '13\n', 'Введите натуральное число: 13\nДвоичный код: 00001101\n'),
    ('1-primes.kum', '100\n', 'Введите максимальное число: 100\nПростые числа от 2 до 100:\n2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97 \n'),
    ('2-longnum.kum', None, 'Факториал числа 100:\n93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000\n'),
    ('22-swap.kum', '2\n3\n', 'Введите два целых числа: 2 3\nПосле обмена: x=3 y=2\n'),
    ('23-func-sumdig.kum', '12345\n', 'Введите целое число: 12345\nСумма цифр 15\n'),
    ('24-func-prime.kum', '15\n', 'Введите максимальное число: 15\nПростые числа: 2 3 5 7 11 13 \n'),
    ('25-func-prime.kum', '5\n7\n12\n', 'Введите число: 5\n5 - простое число\nВведите число: 7\n7 - простое число\nВведите число: 12\n'),
    ('26-rec-hanoi.kum', None, '1 -> 3\n1 -> 2\n3 -> 2\n1 -> 3\n2 -> 1\n2 -> 3\n1 -> 3\n'),
    ('27-rec-bin.kum', '99\n', 'Введите натуральное число: 99\nДвоичный код 1100011\n'),
    ('28-rec-sumdig.kum', '12345\n', 'Введите натуральное число: 12345\nСумма цифр 15\n'),
    ('29-rec-nod.kum', '14\n21\n', 'Введите два натуральных числа: 14 21\nНОД(14,21)=7\n'),
    ('30-rec-fact.kum', '4\n', 'Введите натуральное число: 4\n-> N=4\n-> N=3\n-> N=2\n-> N=1\n<- N=1\n<- N=2\n<- N=3\n<- N=4\n24\n'),
    ('31-arr-empty.kum', None, ''),
    ('32-arr-kvad.kum', '9\n', 'Введите размер массива: 9\n1 4 9 16 25 36 49 64 81 \n'),
    ('33-arr-input.kum', '4\n9\n-2\n0\n1\n', 'Введите размер массива: 4\nВведите элементы массива:\nA[1]=9\nA[2]=-2\nA[3]=0\nA[4]=1\nМассив задом наперёд: \n1 0 -2 9 \n'),
    ('34-arr-rand.kum', '8\n', None),
    ('35-arr-sum.kum', '7\n180\n185\n100\n200\n170\n188\n190\n', 'Введите размер массива:\n7\nВведите элементы массива:\n180\n185\n100\n200\n170\n188\n190\nЭлементы 180 < x < 190:\nКоличество: 2\nСумма:      373\nСреднее:    186.5\n'),
    ('36-arr-search.kum', '6\n-3\n3\n0\n2\n12\n-45\n0\n', 'Введите размер массива: 6\nВведите элементы массива: \n-3\n3\n0\n2\n12\n-45\nЧто ищем? 0\nA[3]=0\n'),
    ('37-arr-search.kum', '7\n-3\n-2\n-1\n0\n1\n2\n3\n1\n', 'Введите размер массива: 7\nВведите элементы массива: \n-3\n-2\n-1\n0\n1\n2\n3\nЧто ищем? 1\nA[5]=1\n'),
    ('39-arr-rev.kum', '7\n-2\n-1\n0\n1\n2\n3\n4\n', 'Введите размер массива: 7\nВведите элементы массива: \n-2\n-1\n0\n1\n2\n3\n4\nПосле реверса:\n4 3 2 1 0 -1 -2 \n'),
    ('40-arr-shift.kum', '5\n-3\n-2\n0\n2\n3\n', 'Введите размер массива: 5\nВведите элементы массива: \n-3\n-2\n0\n2\n3\nПосле сдвига влево:\n-2 0 2 3 -3 \n'),
    ('42-arr-bsort.kum', '4\n-12\n0\n3\n1\n', 'Введите размер массива: 4\nВведите элементы массива:\n-12\n0\n3\n1\nПосле сортировки:\n-12 0 1 3 \n'),
    ('42a-arr-bsort.kum', '6\n-12\n43\n11\n0\n-3\n-5412\n', 'Введите размер массива: 6\nВведите элементы массива:\n-12\n43\n11\n0\n-3\n-5412\nПосле сортировки:\n-5412 -12 -3 0 11 43 \n'),
    ('43-arr-msort.kum', '5\n-1\n8\n4\n5\n-21\n', 'Введите размер массива: 5\nВведите элементы массива: \n-1\n8\n4\n5\n-21\nПосле сортировки:\n-21 -1 4 5 8 \n'),
    ('44-arr-qsort.kum', None, 'До сортировки:\n78 6 82 67 55 44 34 \nПосле сортировки:\n6 34 44 55 67 78 82 \n'),
    ('46-str-ab.kum', 'ааабббвввгггдддееежжж\n', 'ааабббвввгггдддееежжж\nббббббвввгггдддееежжж\n'),
    ('47-str-ops.kum', None, 'Привет, Вася!\n34567\n129\n12ABC3456789\n'),
    ('48-str-search.kum', None, 'Номер символа 4\n'),
    ('49-str-complex.kum', 'Николай Ильич Щитфаков\n', 'Введите имя, отчество и фамилию:Николай Ильич Щитфаков\nЩитфаков Н. И.\n'),
    ('50-str-num.kum', None, '246\n246.912\n123\n123.456\n'),
    ('51-str-proc.kum', None, 'A12B.A12B.A12B\n'),
    ('52-str-func.kum', None, 'A12B.A12B.A12B\n'),
    ('53-str-rec.kum', None, 'ЫЫЫ\nЫЫШ\nЫЫЧ\nЫЫО\nЫШЫ\nЫШШ\nЫШЧ\nЫШО\nЫЧЫ\nЫЧШ\nЫЧЧ\nЫЧО\nЫОЫ\nЫОШ\nЫОЧ\nЫОО\nШЫЫ\nШЫШ\nШЫЧ\nШЫО\nШШЫ\nШШШ\nШШЧ\nШШО\nШЧЫ\nШЧШ\nШЧЧ\nШЧО\nШОЫ\nШОШ\nШОЧ\nШОО\nЧЫЫ\nЧЫШ\nЧЫЧ\nЧЫО\nЧШЫ\nЧШШ\nЧШЧ\nЧШО\nЧЧЫ\nЧЧШ\nЧЧЧ\nЧЧО\nЧОЫ\nЧОШ\nЧОЧ\nЧОО\nОЫЫ\nОЫШ\nОЫЧ\nОЫО\nОШЫ\nОШШ\nОШЧ\nОШО\nОЧЫ\nОЧШ\nОЧЧ\nОЧО\nООЫ\nООШ\nООЧ\nООО\n'),
    ('54-str-sort.kum', '5\nпароход\nпаровоз\nпар\nПар\nпАр\n', 'Введите количество строк: 5\nВведите строки: \nпароход\nпаровоз\nпар\nПар\nпАр\nПосле сортировки: \nПар\nпАр\nпар\nпаровоз\nпароход\n'),
    ('55-matr-declare.kum', None, ''),
    ('56-matr-rand.kum', None, None),
    ('57-matr-sum.kum', None, 'Матрица: \n2 3 4 5 \n3 4 5 6 \n4 5 6 7 \nСумма элементов 54\n'),
]


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
    original_stderr = sys.stderr  # Сохраняем оригинальный stderr

    input_buffer = StringIO(input_data if input_data else "")
    # output_buffer больше не нужен здесь для redirect_stdout
    # output_buffer = StringIO()

    # print(f"[DEBUG_RUN_KUMIR_PROGRAM] BEFORE (no redirect). output_buffer concept removed", file=original_stderr)

    actual_output_value = ""  # Переименуем, чтобы не путать с переменной теста

    try:
        with open(program_path, 'r', encoding='utf-8') as f:
            code = f.read()
            code = code.replace('\r\n', '\n').replace('\r', '\n')        # Устанавливаем stdin
        sys.stdin = input_buffer

        # interpret_kumir сам захватывает stdout и возвращает его.
        # Внешнее перенаправление через redirect_stdout(output_buffer) не нужно
        # и приводило к тому, что output_buffer оставался пустым.
        actual_output_value = interpret_kumir(code, input_data)        # DEBUG PRINT ПОСЛЕ ВЫЗОВА INTERPRET_KUMIR
        print(f"[DEBUG_RUN_KUMIR_PROGRAM] interpret_kumir returned:\n>>>\n{actual_output_value}\n<<<", file=original_stderr)
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError for {program_path}: {e}")
    except KumirEvalError as e:
        actual_output_value += f"\nОШИБКА ВЫПОЛНЕНИЯ: {e}\n"
        pytest.fail(f"KumirEvalError for {program_path}: {e}")
    except Exception as e:
        print(f"--- НЕПРЕДВИДЕННАЯ ОШИБКА {os.path.basename(program_path)} ---", file=original_stderr)
        import traceback
        traceback.print_exc(file=original_stderr)
        pytest.fail(f"Unexpected exception for {program_path}: {e}")
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    # --- DEBUG PRINT ПОСЛЕ try/finally ---
    # print(f"[DEBUG_RUN_KUMIR_PROGRAM] AFTER try/finally. actual_output_value is: ({len(actual_output_value)} chars)\n>>>\n{actual_output_value}\n<<<", file=original_stderr)

    # actual_output теперь это то, что вернул interpret_kumir
    # actual_output = output_buffer.getvalue() # Эта строка больше не нужна

    # DEBUG PRINT ДЛЯ ACTUAL_OUTPUT (который теперь actual_output_value)
    # print(f"[DEBUG_RUN_KUMIR_PROGRAM] actual_output (from interpret_kumir) is ({len(actual_output_value)} chars):\n>>>\n{actual_output_value}\n<<<", file=original_stderr)

    # Нормализация конца строки, если нужно (оставляем эту логику)
    if actual_output_value and not actual_output_value.endswith('\n'):
        actual_output_value += '\n'
    return actual_output_value


@pytest.mark.parametrize("program,input_data,expected_output", TEST_CASES)
def test_kumir_program(
    program: str,
    input_data: str | None,
    expected_output: str | None
) -> None:
    """
    Тестирует выполнение программы на КуМире.

    Args:
        program (str): Имя файла программы
        input_data (str): Входные данные (если нужны)
        expected_output (str): Ожидаемый вывод
    """
    program_path = os.path.join(PROGRAMS_DIR, program)
    assert os.path.exists(program_path), f"Файл программы не найден: {program}"

    actual_output = ""  # Инициализируем actual_output
    try:
        actual_output = run_kumir_program(program_path, input_data)
        if expected_output is not None:
            assert actual_output == expected_output, \
                f"Неверный вывод для {program}:\nОжидалось:\n{expected_output}\nПолучено:\n{actual_output}"
    except KumirSyntaxError as e:
        pytest.fail(f"KumirSyntaxError for {program_path}: {e}")
    except KumirEvalError as e:
        pytest.fail(f"KumirEvalError for {program_path}: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected exception for {program_path}: {e}")
    if expected_output is not None and "ОШИБКА ВЫПОЛНЕНИЯ" not in actual_output:
        assert actual_output == expected_output, \
            f"Неверный вывод для {program}:\nОжидалось:\n{expected_output}\nПолучено:\n{actual_output}"

# Автогенерированные тесты для курса: strkum
# Сгенерировано: 2025-06-08 22:42:30

def test_strkum_Nayti_pervyy_simvol_stroki_10(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_pervyy_simvol_stroki_10 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_pervyy_simvol_stroki_na_tsifru_0_11(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_pervyy_simvol_stroki_na_tsifru_0_11 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_pervye_dva_simvola_stroki_na_bukvy_Zh_12(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_pervye_dva_simvola_stroki_na_bukvy_Zh_12 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vychislit_dlinu_stroki_13(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vychislit_dlinu_stroki_13 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_posledniy_simvol_stroki_14(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_posledniy_simvol_stroki_14 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vyyasnit_verno_li_chto_dlina_stroki_chyotnoe_chislo_15(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vyyasnit_verno_li_chto_dlina_stroki_chyotnoe_chislo_15 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_poslednie_dva_simvola_na_bukvy_Y_16(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_poslednie_dva_simvola_na_bukvy_Y_16 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Opredelit_verno_li_chto_pervyy_i_posledniy_simvoly_stroki_so_17(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Opredelit_verno_li_chto_pervyy_i_posledniy_simvoly_stroki_so_17 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_sredniy_simvol_stroki_18(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_sredniy_simvol_stroki_18 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Opredelit_verno_li_chto_pervyy_sredniy_i_posledniy_simvoly_s_19(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Opredelit_verno_li_chto_pervyy_sredniy_i_posledniy_simvoly_s_19 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Pomenyat_mestami_pervyy_i_vtoroy_simvoly_stroki_110(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Pomenyat_mestami_pervyy_i_vtoroy_simvoly_stroki_110 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Pomenyat_mestami_pervyy_i_posledniy_simvoly_stroki_111(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Pomenyat_mestami_pervyy_i_posledniy_simvoly_stroki_111 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_vse_simvoly_stroki_na_tsifry_5_20(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_vse_simvoly_stroki_na_tsifry_5_20 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_vse_simvoly_stroki_krome_pervogo_i_poslednego_na_tsi_21(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_vse_simvoly_stroki_krome_pervogo_i_poslednego_na_tsi_21 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_22(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_22 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_v_stroke_vse_simvoly_s_chyotnymi_nomerami_na_tochki_23(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_v_stroke_vse_simvoly_s_chyotnymi_nomerami_na_tochki_23 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_v_stroke_vse_tsifry_1_24(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_v_stroke_vse_tsifry_1_24 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_vse_simvoly_pervoy_poloviny_stroki_na_tsifry_9_25(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_vse_simvoly_pervoy_poloviny_stroki_na_tsifry_9_25 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_i_naoborot_vse_tsi_26(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_v_stroke_vse_tsifry_1_na_tsifry_0_i_naoborot_vse_tsi_26 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_t_27(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_t_27 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_v_pervoy_polovine_stroki_vse_tochki_na_znaki_voprosa_28(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_v_pervoy_polovine_stroki_vse_tochki_na_znaki_voprosa_28 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_vse_simvoly_vtoroy_poloviny_stroki_na_tsifry_8_29(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_vse_simvoly_vtoroy_poloviny_stroki_na_tsifry_8_29 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_s_210(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_v_stroke_vse_russkie_bukvy_A_na_bukvy_B_i_naoborot_s_210 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Zamenit_vo_vtoroy_polovine_stroki_vse_tochki_na_znaki_vopros_211(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Zamenit_vo_vtoroy_polovine_stroki_vse_tochki_na_znaki_vopros_211 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_kolichestvo_tsifr_0_v_simvolnoy_stroke_30(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_kolichestvo_tsifr_0_v_simvolnoy_stroke_30 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_obschee_kolichestvo_tsifr_0_31(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_obschee_kolichestvo_tsifr_0_31 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_zaglavnyh_v_pe_32(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_zaglavnyh_v_pe_32 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_33(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_33 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_kolichestvo_par_odinakovyh_simvolov_stoyaschih_ry_34(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_kolichestvo_par_odinakovyh_simvolov_stoyaschih_ry_34 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_obschee_kolichestvo_bukv_A_i_B_tolko_zaglavnyh_vo_35(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_obschee_kolichestvo_bukv_A_i_B_tolko_zaglavnyh_vo_35 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_36(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_obschee_kolichestvo_latinskih_bukv_A_36 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vydelit_imya_iz_stroki_v_kotoroy_zapisany_imya_familiya_i_ot_40(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vydelit_imya_iz_stroki_v_kotoroy_zapisany_imya_familiya_i_ot_40 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vydelit_otchestvo_iz_stroki_v_kotoroy_zapisany_imya_familiya_41(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vydelit_otchestvo_iz_stroki_v_kotoroy_zapisany_imya_familiya_41 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vydelit_familiyu_iz_stroki_v_kotoroy_zapisany_imya_familiya_42(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vydelit_familiyu_iz_stroki_v_kotoroy_zapisany_imya_familiya_42 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vydelit_god_rozhdeniya_iz_stroki_v_kotoroy_zapisany_imya_fam_43(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vydelit_god_rozhdeniya_iz_stroki_v_kotoroy_zapisany_imya_fam_43 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_44(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_44 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_45(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_45 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_V_stroke_zapisany_imya_familiya_otchestvo_i_god_rozhdeniya_r_46(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_V_stroke_zapisany_imya_familiya_otchestvo_i_god_rozhdeniya_r_46 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_47(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_47 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_48(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_V_stroke_zapisany_imya_familiya_i_otchestvo_razdelyonnye_odi_48 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Udalit_lishnie_probely_v_nachale_stroki_50(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Udalit_lishnie_probely_v_nachale_stroki_50 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Udalit_lishnie_probely_v_kontse_stroki_51(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Udalit_lishnie_probely_v_kontse_stroki_51 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Udalit_lishnie_probely_v_nachale_i_v_kontse_stroki_52(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Udalit_lishnie_probely_v_nachale_i_v_kontse_stroki_52 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Udalit_vse_mnozhestvennye_probely_mezhdu_slovami_53(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Udalit_vse_mnozhestvennye_probely_mezhdu_slovami_53 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Udalit_vse_lishnie_probely_v_nachale_i_v_kontse_stroki_a_tak_54(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Udalit_vse_lishnie_probely_v_nachale_i_v_kontse_stroki_a_tak_54 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_kolichestvo_simvolov_stroki_okruzhennyh_probelami_55(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_kolichestvo_simvolov_stroki_okruzhennyh_probelami_55 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_kolichestvo_slov_v_simvolnoy_stroke_56(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_kolichestvo_slov_v_simvolnoy_stroke_56 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Podschitat_kolichestvo_slov_kotoryy_nachinayutsya_s_russkoy_57(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Podschitat_kolichestvo_slov_kotoryy_nachinayutsya_s_russkoy_57 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_pervoe_slovo_v_simvolnoy_stroke_58(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_pervoe_slovo_v_simvolnoy_stroke_58 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_poslednee_slovo_v_simvolnoy_stroke_59(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_poslednee_slovo_v_simvolnoy_stroke_59 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Opredelit_verno_li_chto_stroka_predstavlyaet_soboy_palindrom_510(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Opredelit_verno_li_chto_stroka_predstavlyaet_soboy_palindrom_510 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Opredelit_verno_li_chto_obe_poloviny_stroki_predstavlyayut_s_511(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Opredelit_verno_li_chto_obe_poloviny_stroki_predstavlyayut_s_511 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_summu_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_60(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_summu_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_60 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_raznost_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_strok_61(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_raznost_dvuh_chisel_zapisannuyu_v_vide_simvolnoy_strok_61 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_proizvedenie_dvuh_chisel_zapisannoe_v_vide_simvolnoy_s_62(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_proizvedenie_dvuh_chisel_zapisannoe_v_vide_simvolnoy_s_62 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Nayti_summu_tryoh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_63(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Nayti_summu_tryoh_chisel_zapisannuyu_v_vide_simvolnoy_stroki_63 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_64(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_64 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_65(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_pervaya_operatsiya_vt_65 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_odna_iz_operatsiy_dru_66(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_odna_iz_operatsiy_dru_66 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_67(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_67 выполнен. Вывод: {result.stdout_output[:100]}")


def test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_68(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_strkum_Vychislit_vyrazhenie_s_tremya_chislami_ispolzuyutsya_operats_68 выполнен. Вывод: {result.stdout_output[:100]}")

