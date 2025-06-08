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

# Автогенерированные тесты для курса: arrkum2
# Сгенерировано: 2025-06-08 22:42:30

def test_arrkum2_Perestavit_vse_elementy_massiva_v_obratnom_poryadke_10(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_vse_elementy_massiva_v_obratnom_poryadke_10 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Perestavit_vse_elementy_massiva_krome_poslednego_v_obratnom_11(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_vse_elementy_massiva_krome_poslednego_v_obratnom_11 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Perestavit_vse_elementy_massiva_krome_pervogo_v_obratnom_por_12(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_vse_elementy_massiva_krome_pervogo_v_obratnom_por_12 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Perestavit_vse_elementy_v_pervoy_polovine_massiva_v_obratnom_13(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_vse_elementy_v_pervoy_polovine_massiva_v_obratnom_13 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Perestavit_elementy_v_kazhdoy_pare_1_yy_so_2_m_3_y_s_4_m_i_t_14(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_elementy_v_kazhdoy_pare_1_yy_so_2_m_3_y_s_4_m_i_t_14 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Perestavit_vse_elementy_vo_vtoroy_polovine_massiva_v_obratno_15(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_vse_elementy_vo_vtoroy_polovine_massiva_v_obratno_15 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_polovine_massiva_v_obratno_16(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_polovine_massiva_v_obratno_16 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_treti_massiva_v_obratnom_p_17(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Perestavit_vse_elementy_v_kazhdoy_treti_massiva_v_obratnom_p_17 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_1_pozitsiyu_20(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_1_pozitsiyu_20 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_vl_21(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_vl_21 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_poslednego_22(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_poslednego_22 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_23(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_23 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_1_pozitsiyu_24(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_1_pozitsiyu_24 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_pervoy_po_25(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_pervoy_po_25 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_vtoroy_po_26(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vpravo_na_1_pozitsiyu_vtoroy_po_26 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_27(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_vseh_elementov_krome_pervogo_i_27 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_4_pozitsii_28(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vlevo_na_4_pozitsii_28 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_4_pozitsii_29(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_tsiklicheskiy_sdvig_massiva_vpravo_na_4_pozitsii_29 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_i_za_30(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_i_za_30 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_otritsatelnye_elementy_massiva_A_i_za_31(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_otritsatelnye_elementy_massiva_A_i_za_31 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_elementy_massiva_A_i_zapisat_32(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_elementy_massiva_A_i_zapisat_32 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_elementy_massiva_A_i_zapis_33(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_elementy_massiva_A_i_zapis_33 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_polozhitelnye_elementy_mas_34(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_nechyotnye_polozhitelnye_elementy_mas_34 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_otritsatelnye_elementy_massi_35(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_chyotnye_otritsatelnye_elementy_massi_35 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_koto_36(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_koto_36 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_desy_37(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_desy_37 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_v_de_38(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_polozhitelnye_elementy_massiva_A_v_de_38 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_predstavly_39(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_predstavly_39 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_u_kotoryh_summa_ts_310(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_u_kotoryh_summa_ts_310 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_vstrechayu_311(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Otobrat_v_massiv_B_vse_elementy_massiva_A_kotorye_vstrechayu_311 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_40(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_40 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_41(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_41 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_42(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_42 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_43(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_43 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_44(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_44 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_45(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_45 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_46(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_46 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_47(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_47 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_48(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_48 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_49(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_49 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_410(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_410 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_411(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_411 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_50(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_50 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_51(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_ubyvaniyu_51 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_52(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_poslednego_po_ub_52 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_53(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_53 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_54(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_po_ubyva_54 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_55(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_krome_pervogo_i_posled_55 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_56(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_vtoroy_poloviny_massiva_po_ubyvaniyu_56 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_57(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_posled_57 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_58(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_i_zapi_58 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_59(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_59 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_510(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_pervoy_poloviny_massiva_po_vozrastaniyu_510 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_511(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Vypolnit_sortirovku_elementov_massiva_po_vozrastaniyu_summy_511 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_60(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_60 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_61(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_61 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_62(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Massiv_otsortirovan_po_vozrastaniyu_neubyvaniyu_62 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_63(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Massiv_otsortirovan_po_ubyvaniyu_nevozrastaniyu_63 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_64(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_64 выполнен. Вывод: {result.stdout_output[:100]}")


def test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_65(run_kumir_code_func, tmp_path):
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
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {result.stderr_output}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест test_arrkum2_Ispolzuya_dvoichnyy_poisk_nayti_chislo_X_kub_kotorogo_raven_65 выполнен. Вывод: {result.stdout_output[:100]}")

