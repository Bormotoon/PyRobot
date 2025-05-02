import pytest
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from pyrobot.backend.kumir_interpreter.interpreter import interpret_kumir
from pyrobot.backend.kumir_interpreter.kumir_exceptions import KumirSyntaxError, KumirEvalError

# Определяем директорию с примерами КуМир относительно текущего файла
current_dir = os.path.dirname(os.path.abspath(__file__))
# Нормализуем путь, чтобы избежать проблем с '..' - УДАЛЕНО, ТАК КАК ПУТЬ НЕПРАВИЛЬНЫЙ
# PROGRAMS_DIR = os.path.abspath(os.path.join(current_dir, "..", "polyakov_kum"))
# Исправляем путь на tests/polyakov_kum
PROGRAMS_DIR = os.path.join(current_dir, "polyakov_kum")

TEST_CASES = [
    ('1-empty.kum', None, ''),  # Пустая программа
    ('2-2+2.kum', None, '2+2=?\nОтвет: 4\n'),  # Простое сложение - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с финальным \n)
    ('3-a+b.kum', '2\n3\n', '2 3\n5\n'),  # Сложение с вводом - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('4-a+b.kum', '10\n20\n', 'Введите два целых числа: 10 20\n10+20=30\n'),  # Сложение с вводом - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('6-format.kum', None, '>  123<\n1.2345678\n>  1.235<\n'),  # Форматированный вывод
    ('7-rand.kum', None, None),  # Случайные числа - проверяем только запуск
    ('8-if.kum', '5\n7\n', 'Введите два целых числа: 5 7\nМаксимальное число:\n7\n7\n7\n7\n'), # Условный оператор - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('9-if.kum', '-3\n5\n', 'Введите возраст Андрея и Бориса: -3 5\nБорис старше\n'), # Условный оператор, ветвление - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('10-and.kum', '27\n', "Введите возраст: 27\nподходит\n"),  # Логическое И - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('11-switch.kum', '2\n', 'Введите номер месяца: 2\nфевраль\n'), # Выбор (месяц) - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('12-switch.kum', '7\n', '7\n1\n'),                # Выбор (знак числа) - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('13-loopN.kum', '5\n', 'Сколько раз сделать? 5\nпривет\nпривет\nпривет\nпривет\nпривет\n'), # Цикл НЦ раз - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('14-while.kum', '5\n', 'Сколько раз сделать? 5\nпривет\nпривет\nпривет\nпривет\nпривет\n'), # Цикл ПОКА - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('15-while.kum', '12345\n', "Введите целое число: 12345\nЦифр в числе: 5\n"), # Цикл ПОКА (подсчет цифр) - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('16-repeat.kum', '-1\n0\n2\n', 'Введите целое положительное число: -1\n0\n2\nВведено число 2\n  и до него 2 ошибочных значений(я)\n'), # Цикл ДО - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('17-for.kum', '5\n', '5\n2 4 8 16 32 \n'),            # Цикл ДЛЯ (степени двойки) - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('18-downto.kum', '5\n', '5\n32 16 8 4 2 \n'),         # Цикл ДЛЯ с downto - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('19-prime.kum', '17\n', 'Введите максимальное число: 17\nПростые числа: 2 3 5 7 11 13 17 \n'),  # Проверка простоты числа - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('20-proc-err.kum', '-1\n', '-1\nОшибка программы\n'), # Вызов процедуры по условию - ОБНОВЛЕНО ПО ОРИГИНАЛУ (вход -1, с эхом)
    ('21-proc-bin.kum', '13\n', 'Введите натуральное число: 13\nДвоичный код: 00001101\n'), # Процедура перевода в двоичную - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('1-primes.kum', '100\n', 'Введите максимальное число: 100\nПростые числа от 2 до 100:\n2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97 \n'), # Решето Эратосфена - ОБНОВЛЕНО ПО ОРИГИНАЛУ (с эхом ввода)
    ('2-longnum.kum', None, 'Факториал числа 100:\n93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000\n'), # Длинные числа (факториал) - ДОБАВЛЕНО ПО ОРИГИНАЛУ
    ('22-swap.kum', '2\n3\n', 'Введите два целых числа: 2 3\nПосле обмена: x=3 y=2\n'), # Процедура с аргрез (обмен) - ДОБАВЛЕНО ПО ОРИГИНАЛУ
    ('23-func-sumdig.kum', '12345\n', 'Введите целое число: 12345\nСумма цифр 15\n'), # Функция (сумма цифр) - ДОБАВЛЕНО ПО ОРИГИНАЛУ
    ('24-func-prime.kum', '15\n', 'Введите максимальное число: 15\nПростые числа: 2 3 5 7 11 13 \n'), # Логическая функция (проверка простоты) - ДОБАВЛЕНО ПО ОРИГИНАЛУ
    ('25-func-prime.kum', '5\n7\n12\n', 'Введите число: 5\n5 - простое число\nВведите число: 7\n7 - простое число\nВведите число: 12\n'), # Цикл ПОКА с логической функцией - ДОБАВЛЕНО ПО ОРИГИНАЛУ
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
    try:
        with open(program_path, 'r', encoding='utf-8') as f:
            code = f.read()
            # --- Добавляем нормализацию переносов строк ---
            code = code.replace('\r\n', '\n').replace('\r', '\n')

        # Создаем буферы для перехвата вывода и ввода
        output_buffer = StringIO()
        input_buffer = StringIO(input_data if input_data else '')

        # Используем контекстные менеджеры для безопасного перехвата stdout и stdin
        with redirect_stdout(output_buffer), redirect_stderr(StringIO()):
            # Временно заменяем stdin
            old_stdin = sys.stdin
            sys.stdin = input_buffer
            try:
                interpret_kumir(code)  # Запускаем интерпретатор
            finally:
                # Восстанавливаем stdin в любом случае
                sys.stdin = old_stdin

        # Получаем результат
        result = output_buffer.getvalue()
        # --- ИСПРАВЛЕНИЕ: Убираем пробельные символы в конце результата --- 
        result = result.rstrip()

        # Добавляем newline в конце, если его нет (как делает оригинальный КуМир)
        if result:
            result += '\n'
        return result

    except KumirSyntaxError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        raise  # Перевыбрасываем исключение, чтобы тест упал
    except KumirEvalError as e:
        print(f"Ошибка выполнения: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


@pytest.mark.parametrize("program,input_data,expected_output", TEST_CASES)
def test_kumir_program(program, input_data, expected_output):
    """
    Тестирует выполнение программы на КуМире.
    
    Args:
        program (str): Имя файла программы
        input_data (str): Входные данные (если нужны)
        expected_output (str): Ожидаемый вывод
    """
    program_path = os.path.join(PROGRAMS_DIR, program)
    assert os.path.exists(program_path), f"Файл программы не найден: {program}"
    
    actual_output = run_kumir_program(program_path, input_data)
    if expected_output is not None:  # Пропускаем проверку для программ с недетерминированным выводом
        assert actual_output == expected_output, \
            f"Неверный вывод для {program}:\nОжидалось:\n{expected_output}\nПолучено:\n{actual_output}" 