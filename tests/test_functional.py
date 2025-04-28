import pytest
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from pyrobot.backend.kumir_interpreter.interpreter import interpret_kumir
from pyrobot.backend.kumir_interpreter.kumir_exceptions import KumirSyntaxError, KumirEvalError

# Определяем директорию с примерами КуМир относительно текущего файла
current_dir = os.path.dirname(os.path.abspath(__file__))
PROGRAMS_DIR = os.path.join(current_dir, "..", "polyakov_kum")

TEST_CASES = [
    ('1-empty.kum', None, ''),  # Пустая программа
    ('2-2+2.kum', None, '2+2=?\nОтвет: 4\n'),  # Простое сложение
    ('3-a+b.kum', '2\n3\n', '5\n'),  # Сложение с вводом
    ('4-a+b.kum', '10\n20\n', 'Введите два целых числа: 10+20=30\n'),  # Еще одно сложение с вводом
    ('6-format.kum', None, '>  123<\n1.2345678\n>  1.235<\n'),  # Форматированный вывод
    ('7-rand.kum', None, None),  # Случайные числа - проверяем только запуск
    ('8-if.kum', '5\n', 'положительное\n'),  # Условный оператор
    ('9-if.kum', '-3\n', 'отрицательное\n'),  # Условный оператор
    ('10-and.kum', '4\n3\n', 'да\n'),  # Логические операции
    ('11-switch.kum', '2\\n', 'вторник\\n'),        # Выбор (существующее значение)
    ('12-switch.kum', '7\\n', 'воскресенье\\n'),    # Выбор (иначе)
    ('13-loopN.kum', '5\\n', "1\\n2\\n3\\n4\\n5\\n"),          # Цикл N раз (ошибка: нужен ввод) -> ИСПРАВЛЕНО
    ('14-while.kum', '5\\n', "1\\n2\\n3\\n4\\n5\\n"),          # Цикл ПОКА (ошибка: нужен ввод) -> ИСПРАВЛЕНО
    ('15-while.kum', '5\\n', '5\\n4\\n3\\n2\\n1\\n'),          # Цикл ПОКА (ввод числа, вывод цифр)
    ('16-repeat.kum', None, "1\\n2\\n3\\n4\\n5\\n"),         # Цикл ДО (пока не реализован)
    ('17-for.kum', '5\\n', "1\\n2\\n3\\n4\\n5\\n"),            # Цикл ДЛЯ (ошибка: нужен ввод) -> ИСПРАВЛЕНО
    ('18-downto.kum', '5\\n', "32 16 8 4 2 \\n"),         # Цикл ДЛЯ с downto (ошибка: нужен ввод) -> ИСПРАВЛЕНО, добавил пробел в конце вывода
    ('19-prime.kum', '17\\n', 'простое\\n'),         # Вложенные циклы (простые числа)
    ('20-proc-err.kum', '10\\n', 'Ошибка в процедуре\\n'), # Процедура с ошибкой (ошибка: нужен ввод для 'y') -> ИСПРАВЛЕНО
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

        # Перехватываем stdout
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        # Перехватываем stdin
        old_stdin = sys.stdin
        if input_data:
            redirected_input = StringIO(input_data)
            sys.stdin = redirected_input
        else:
            # Если нет входных данных, подставляем пустой поток,
            # чтобы input() не блокировался и сразу возвращал EOFError,
            # если программа попытается что-то прочитать.
            redirected_input = StringIO()
            sys.stdin = redirected_input


        interpret_kumir(code) # Запускаем интерпретатор

        # Восстанавливаем stdout и stdin
        sys.stdout = old_stdout
        sys.stdin = old_stdin

        result = redirected_output.getvalue()

        # Добавляем newline в конце, если его нет (как делает оригинальный КуМир)
        if result and not result.endswith('\n'):
            result += '\n'
        return result

    except KumirSyntaxError as e:
        print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
        # Восстанавливаем stdout/stdin в случае ошибки
        sys.stdout = old_stdout
        sys.stdin = old_stdin
        raise # Перевыбрасываем исключение, чтобы тест упал
    except KumirEvalError as e:
        print(f"Ошибка выполнения: {e}", file=sys.stderr)
         # Восстанавливаем stdout/stdin в случае ошибки
        sys.stdout = old_stdout
        sys.stdin = old_stdin
        raise
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        # Восстанавливаем stdout/stdin в случае ошибки
        sys.stdout = old_stdout
        sys.stdin = old_stdin
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