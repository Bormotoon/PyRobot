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

# Автогенерированные тесты для курса: arrkum
# Сгенерировано: 2025-06-08 22:42:30

def test_arrkum_Zapolnite_massiv_A_nulyami_10(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnite_massiv_A_nulyami_10 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_11(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_11 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_12(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnite_massiv_A_pervymi_N_naturalnymi_chislami_nachinaya_12 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnite_massiv_naturalnymi_chislami_tak_chto_pervyy_elemen_13(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnite_massiv_naturalnymi_chislami_tak_chto_pervyy_elemen_13 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnit_massiv_A_pervymi_N_chislami_Fibonachchi_14(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnit_massiv_A_pervymi_N_chislami_Fibonachchi_14 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnite_massiv_stepenyami_chisla_2_tak_chtoby_posledniy_el_15(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnite_massiv_stepenyami_chisla_2_tak_chtoby_posledniy_el_15 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnite_massiv_tselymi_chislami_tak_chtoby_sredniy_element_16(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnite_massiv_tselymi_chislami_tak_chtoby_sredniy_element_16 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Uvelichit_vse_elementy_massiva_A_na_1_20(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Uvelichit_vse_elementy_massiva_A_na_1_20 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Umnozhit_vse_elementy_massiva_A_na_2_21(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Umnozhit_vse_elementy_massiva_A_na_2_21 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vozvesti_v_kvadrat_vse_elementy_massiva_A_22(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vozvesti_v_kvadrat_vse_elementy_massiva_A_22 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Uvelichit_na_4_vse_elementy_v_pervoy_polovine_massiva_A_schi_23(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Uvelichit_na_4_vse_elementy_v_pervoy_polovine_massiva_A_schi_23 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Razdelit_na_2_vse_elementy_massiva_A_krome_pervogo_i_posledn_24(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Razdelit_na_2_vse_elementy_massiva_A_krome_pervogo_i_posledn_24 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Umnozhit_na_3_vse_elementy_vo_vtoroy_polovine_massiva_A_schi_25(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Umnozhit_na_3_vse_elementy_vo_vtoroy_polovine_massiva_A_schi_25 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_srednee_arifmeticheskoe_vseh_elementov_massiva_A_26(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_srednee_arifmeticheskoe_vseh_elementov_massiva_A_26 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_maksimalnoe_znachenie_sredi_vseh_elementov_massiva_30(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_maksimalnoe_znachenie_sredi_vseh_elementov_massiva_30 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_minimalnoe_znachenie_sredi_vseh_elementov_massiva_31(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_minimalnoe_znachenie_sredi_vseh_elementov_massiva_31 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_minimalnoe_i_maksimalnoe_znacheniya_sredi_vseh_element_32(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_minimalnoe_i_maksimalnoe_znacheniya_sredi_vseh_element_32 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_nomer_minimalnogo_elementa_massiva_33(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_nomer_minimalnogo_elementa_massiva_33 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_nomera_minimalnogo_i_maksimalnogo_elementov_massiva_34(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_nomera_minimalnogo_i_maksimalnogo_elementov_massiva_34 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_dva_maksimalnyh_elementa_massiva_35(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_dva_maksimalnyh_elementa_massiva_35 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_nomera_dvuh_minimalnyh_elementov_massiva_36(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_nomera_dvuh_minimalnyh_elementov_massiva_36 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_1_40(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_1_40 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_zadannomu_znache_41(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_skolko_elementov_massiva_A_ravny_zadannomu_znache_41 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_kolichestvo_polozhitelnyh_elementov_massiva_A_42(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_kolichestvo_polozhitelnyh_elementov_massiva_A_42 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_kolichestvo_chyotnyh_i_nechyotnyh_elementov_massi_43(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_kolichestvo_chyotnyh_i_nechyotnyh_elementov_massi_43 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_kolichestvo_chyotnyh_polozhitelnyh_elementov_mass_44(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_kolichestvo_chyotnyh_polozhitelnyh_elementov_mass_44 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_45(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_45 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_46(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_kolichestvo_elementov_massiva_v_desyatichnoy_zapisi_ko_46 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_50(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_50 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vychislit_summu_otritsatelnyh_elementov_massiva_A_51(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vychislit_summu_otritsatelnyh_elementov_massiva_A_51 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_kotorye_delyatsya_n_52(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vychislit_summu_vseh_elementov_massiva_A_kotorye_delyatsya_n_52 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vychislit_srednee_arifmeticheskoe_vseh_elementov_massiva_A_k_53(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vychislit_srednee_arifmeticheskoe_vseh_elementov_massiva_A_k_53 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vychislit_proizvedenie_vseh_chyotnyh_polozhitelnyh_elementov_54(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vychislit_proizvedenie_vseh_chyotnyh_polozhitelnyh_elementov_54 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_summu_vseh_elementov_massiva_A_u_kotoryh_chislo_desyat_55(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_summu_vseh_elementov_massiva_A_u_kotoryh_chislo_desyat_55 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vse_elementy_massiva_A_tryohznachnye_chisla_56(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vse_elementy_massiva_A_tryohznachnye_chisla_56 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_v_massive_A_nomer_pervogo_elementa_ravnogo_X_60(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_v_massive_A_nomer_pervogo_elementa_ravnogo_X_60 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_v_pervoy_polovin_61(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_v_pervoy_polovin_61 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_vo_vtoroy_polovi_62(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_nomer_pervogo_elementa_ravnogo_X_vo_vtoroy_polovi_62 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_nomer_poslednego_elementa_ravnogo_X_vo_vtoroy_pol_63(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_nomer_poslednego_elementa_ravnogo_X_vo_vtoroy_pol_63 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_skolko_est_elementov_ravnyh_X_v_pervoy_polovine_m_64(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_skolko_est_elementov_ravnyh_X_v_pervoy_polovine_m_64 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Opredelite_skolko_v_massive_A_par_sosednih_elementov_znachen_65(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Opredelite_skolko_v_massive_A_par_sosednih_elementov_znachen_65 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Gorka_eto_tri_stoyaschih_podryad_elementa_massiva_A_iz_kotor_66(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Gorka_eto_tri_stoyaschih_podryad_elementa_massiva_A_iz_kotor_66 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Elementy_massiva_A_proizvolnye_naturalnye_chisla_71(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Elementy_massiva_A_proizvolnye_naturalnye_chisla_71 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Naydite_v_massive_A_samuyu_dlinnuyu_tsepochku_raspolozhennyh_72(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Naydite_v_massive_A_samuyu_dlinnuyu_tsepochku_raspolozhennyh_72 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Vse_elementy_massiva_A_nahodyatsya_v_diapazone_ot_2_do_1000_73(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Vse_elementy_massiva_A_nahodyatsya_v_diapazone_ot_2_do_1000_73 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnit_massiv_A_pervymi_N_prostymi_chislami_nachinaya_c_2_74(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnit_massiv_A_pervymi_N_prostymi_chislami_nachinaya_c_2_74 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Nayti_v_massive_A_vse_chisla_perevertyshi_kotorye_chitayutsy_75(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Nayti_v_massive_A_vse_chisla_perevertyshi_kotorye_chitayutsy_75 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum_Zapolnit_massiv_A_pervymi_N_giperprostymi_chislami_76(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum_Zapolnit_massiv_A_pervymi_N_giperprostymi_chislami_76 выполнен. Вывод: {result.stdout_output[:100]}")

