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

# Автогенерированные тесты для курса: funkum
# Сгенерировано: 2025-06-08 22:42:30

def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kvadrat_chisla_10(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kvadrat_chisla_10 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kub_chisla_11(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kub_chisla_11 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_poslednyuyu_tsifru_v_12(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_poslednyuyu_tsifru_v_12 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_desyatkov_pre_13(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_desyatkov_pre_13 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_soten_tretyu_14(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_soten_tretyu_14 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_rezultat_okrugleniya_15(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_rezultat_okrugleniya_15 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vypolnyaet_okruglenie_vverh_to_es_16(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vypolnyaet_okruglenie_vverh_to_es_16 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_vseh_naturalny_17(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_vseh_naturalny_17 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zadannuyu_stepen_chi_18(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zadannuyu_stepen_chi_18 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_faktorial_chisla_X_p_20(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_faktorial_chisla_X_p_20 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervuyu_tsifru_v_des_21(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervuyu_tsifru_v_des_21 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_tsifr_ch_22(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_tsifr_ch_22 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_tsifr_chisla_23(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_tsifr_chisla_23 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_edinits_24(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_edinits_24 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_nuley_v_25(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_nuley_v_25 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_Fibonachchi_s_26(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_chislo_Fibonachchi_s_26 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervoe_chislo_Fibona_27(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_pervoe_chislo_Fibona_27 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_stepen_v_kotoruyu_nu_28(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_stepen_v_kotoruyu_nu_28 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_30(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_30 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_31(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_srednee_arifmetiches_31 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_dvuh_c_32(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_dvuh_c_32 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_dvuh_c_33(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_dvuh_c_33 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_tryoh_34(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_iz_tryoh_34 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_tryoh_35(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshee_iz_tryoh_35 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvodit_X_v_stepen_Y_ispolzuya_p_36(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvodit_X_v_stepen_Y_ispolzuya_p_36 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshiy_obschiy_d_37(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naibolshiy_obschiy_d_37 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_obschee_k_38(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_naimenshee_obschee_k_38 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_neizvestnyy_pokazatel_39(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_neizvestnyy_pokazatel_39 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_naibolshiy_pokazatel_310(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_naibolshiy_pokazatel_310 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_40(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_40 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_41(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_41 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_42(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_imya_42 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_43(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_razbiraet_URL_i_vozvraschaet_nazv_43 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_44(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_44 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_45(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_45 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_st_46(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_st_46 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_kontse_str_47(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_kontse_str_47 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_i_48(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_udalyaet_vse_probely_v_nachale_i_48 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_49(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_49 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_izmenyaet_rasshirenie_imeni_fayla_50(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_izmenyaet_rasshirenie_imeni_fayla_50 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_poluchaet_put_k_faylu_izmenyaet_r_51(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_poluchaet_put_k_faylu_izmenyaet_r_51 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_dvoichnoy_zap_52(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_dvoichnoy_zap_52 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_vosmerichnoy_53(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_vosmerichnoy_53 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_shestnadtsate_54(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_perevodit_chislo_iz_shestnadtsate_54 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_55(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_55 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_56(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_zapis_peredannogo_ey_56 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_perevodit_zapis_chisla_v_sisteme_57(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_perevodit_zapis_chisla_v_sisteme_57 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_zakanchivaetsya_li_pe_60(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_zakanchivaetsya_li_pe_60 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_delitsya_li_peredanno_61(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_delitsya_li_peredanno_61 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_62(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_62 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_63(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_63 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_64(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_64 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_65(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_65 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_66(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_66 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_67(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_67 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_68(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_68 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_69(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_69 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_610(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_610 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_611(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_611 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_612(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_612 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_613(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_opredelyaet_verno_li_chto_peredan_613 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_70(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_70 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_71(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_elemento_71 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_polozhit_72(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_polozhit_72 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_chyotnyh_73(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_kolichestvo_chyotnyh_73 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_maksimalnyy_element_74(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_maksimalnyy_element_74 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_minimalnyy_element_m_75(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_minimalnyy_element_m_75 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_maksimalnogo_e_76(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_maksimalnogo_e_76 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_minimalnogo_el_77(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_minimalnogo_el_77 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_elementov_mass_78(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_summu_elementov_mass_78 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_pervogo_elemen_79(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_funktsiyu_kotoraya_vozvraschaet_nomer_pervogo_elemen_79 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_faktori_80(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_faktori_80 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_chislo_81(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_chislo_81 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zadannu_82(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zadannu_82 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_v_83(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_v_83 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_koliche_84(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_koliche_84 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_t_85(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_summu_t_85 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_pervuyu_86(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_pervuyu_86 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_naibols_87(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_naibols_87 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_88(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_88 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_89(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_vozvraschaet_zapis_p_89 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_verno_li_810(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_verno_li_810 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_preobrazuet_dvoichnu_811(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_preobrazuet_dvoichnu_811 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_skolko_r_812(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_opredelyaet_skolko_r_812 выполнен. Вывод: {result.stdout_output[:100]}")


def test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_zamenyaet_vo_vsey_st_813(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_funkum_Napisat_rekursivnuyu_funktsiyu_kotoraya_zamenyaet_vo_vsey_st_813 выполнен. Вывод: {result.stdout_output[:100]}")

