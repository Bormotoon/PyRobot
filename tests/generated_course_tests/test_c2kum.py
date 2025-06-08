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

# Автогенерированные тесты для курса: c2kum
# Сгенерировано: 2025-06-08 22:42:30

def test_c2kum_Nayti_maksimalnyy_nechyotnyy_element_massiva_10(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_maksimalnyy_nechyotnyy_element_massiva_10 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_minimalnyy_chyotnyy_element_kotoryy_ne_delitsya_na_3_11(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_minimalnyy_chyotnyy_element_kotoryy_ne_delitsya_na_3_11 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_minimalnyy_nechyotnyy_element_kotoryy_delitsya_na_3_12(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_minimalnyy_nechyotnyy_element_kotoryy_delitsya_na_3_12 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_minimalnyy_iz_elementov_znacheniya_kotoryh_bolshe_ili_13(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_minimalnyy_iz_elementov_znacheniya_kotoryh_bolshe_ili_13 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_maksimalnyy_iz_elementov_znacheniya_kotoryh_menshe_nul_14(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_maksimalnyy_iz_elementov_znacheniya_kotoryh_menshe_nul_14 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_aMin_minimalnoe_polozhitelnoe_15(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennuyu_aMin_minimalnoe_polozhitelnoe_15 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_minimalnoe_tryohznachnoe_chislo_kotoroe_est_v_massive_16(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_minimalnoe_tryohznachnoe_chislo_kotoroe_est_v_massive_16 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_nomer_elementa_imeyuschego_naibolshee_chislo_deliteley_17(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_nomer_elementa_imeyuschego_naibolshee_chislo_deliteley_17 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_pervogo_po_schyotu_el_20(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_pervogo_po_schyotu_el_20 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_tretego_po_schyotu_po_21(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennuyu_nX_nomer_tretego_po_schyotu_po_21 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_nMax2_nomer_vtorogo_maksimuma_22(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennuyu_nMax2_nomer_vtorogo_maksimuma_22 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_summa_summu_dvuh_minimalnyh_el_23(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennuyu_summa_summu_dvuh_minimalnyh_el_23 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennye_n1_i_n2_nomera_dvuh_elementov_m_24(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennye_n1_i_n2_nomera_dvuh_elementov_m_24 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_25(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_25 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_26(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_i_zapisat_v_peremennuyu_count_kolichestvo_elementov_ma_26 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_summu_elementov_massiva_kotorye_kratny_chislu_13_i_zap_30(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_summu_elementov_massiva_kotorye_kratny_chislu_13_i_zap_30 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_elementov_massiva_kotorye_bols_31(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_srednee_arifmeticheskoe_elementov_massiva_kotorye_bols_31 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_nechyotnyh_otritsatelnyh_eleme_32(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_srednee_arifmeticheskoe_nechyotnyh_otritsatelnyh_eleme_32 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_33(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_33 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_34(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_srednee_arifmeticheskoe_polozhitelnyh_elementov_massiv_34 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_nomer_elementa_blizhayshego_k_srednemu_arifmeticheskom_35(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_nomer_elementa_blizhayshego_k_srednemu_arifmeticheskom_35 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_proizvedenie_chyotnyh_elementov_massiva_kotorye_ne_oka_36(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_proizvedenie_chyotnyh_elementov_massiva_kotorye_ne_oka_36 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_proizvedenie_dvuznachnyh_elementov_massiva_kotorye_del_37(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_proizvedenie_dvuznachnyh_elementov_massiva_kotorye_del_37 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_paru_sosednih_elementov_summa_kotoryh_maksimalna_i_zap_40(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_paru_sosednih_elementov_summa_kotoryh_maksimalna_i_zap_40 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_tri_sosednih_elementa_summa_kotoryh_minimalna_i_zapisa_41(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_tri_sosednih_elementa_summa_kotoryh_minimalna_i_zapisa_41 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_otritsatel_42(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_otritsatel_42 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_odinakovyh_43(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_dlinu_naibolshey_tsepochki_iduschih_podryad_odinakovyh_43 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_dlinu_naibolshey_tsepochki_chisel_elementy_kotoroy_sto_44(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_dlinu_naibolshey_tsepochki_chisel_elementy_kotoroy_sto_44 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_maksimalnyy_iz_elementov_kotorye_menshe_100_i_zapisat_50(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_maksimalnyy_iz_elementov_kotorye_menshe_100_i_zapisat_50 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_srednee_arifmeticheskoe_vseh_elementov_glavnoy_diagona_51(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_srednee_arifmeticheskoe_vseh_elementov_glavnoy_diagona_51 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_kolichestvo_polozhitelnyh_elementov_matritsy_kotorye_b_52(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_kolichestvo_polozhitelnyh_elementov_matritsy_kotorye_b_52 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_kolichestvo_elementov_matritsy_kotorye_bolshe_srednego_53(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_kolichestvo_elementov_matritsy_kotorye_bolshe_srednego_53 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_summu_minimalnyh_elementov_kazhdogo_stolbtsa_i_zapisat_54(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_summu_minimalnyh_elementov_kazhdogo_stolbtsa_i_zapisat_54 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_summu_maksimalnyh_elementov_kazhdoy_stroki_i_zapisat_e_55(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_summu_maksimalnyh_elementov_kazhdoy_stroki_i_zapisat_e_55 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_nomer_stolbtsa_s_maksimalnoy_summoy_elementov_i_zapisa_56(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_nomer_stolbtsa_s_maksimalnoy_summoy_elementov_i_zapisa_56 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_nomer_stroki_s_minimalnoy_summoy_elementov_i_zapisat_e_57(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_nomer_stroki_s_minimalnoy_summoy_elementov_i_zapisat_e_57 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_maksimalnyy_iz_minimalnyh_elementov_kazhdoy_stroki_i_z_58(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_maksimalnyy_iz_minimalnyh_elementov_kazhdoy_stroki_i_z_58 выполнен. Вывод: {result.stdout_output[:100]}")


def test_c2kum_Nayti_minimalnyy_iz_maksimalnyh_elementov_kazhdogo_stolbtsa_59(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_c2kum_Nayti_minimalnyy_iz_maksimalnyh_elementov_kazhdogo_stolbtsa_59 выполнен. Вывод: {result.stdout_output[:100]}")

