import pytest
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from pyrobot.backend.kumir_interpreter.interpreter import interpret_kumir

# Директории с тестовыми данными
KUMIR_EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../polyakov_kum'))
TEST_CASES = [
    ('1-empty.kum', None, ''),  # Пустая программа
    ('2-2+2.kum', None, '2+2=?\nОтвет: 4\n'),  # Простое сложение
    ('3-a+b.kum', '2\n3\n', '5\n'),  # Сложение с вводом
    ('4-a+b.kum', '10\n20\n', 'Введите два целых числа: 10+20=30\n'),  # Еще одно сложение с вводом
    ('6-format.kum', None, '2.5\n2.50\n2.500\n'),  # Форматированный вывод
    ('7-rand.kum', None, None),  # Случайные числа - проверяем только запуск
    ('8-if.kum', '5\n', 'положительное\n'),  # Условный оператор
    ('9-if.kum', '-3\n', 'отрицательное\n'),  # Условный оператор
    ('10-and.kum', '4\n3\n', 'да\n'),  # Логические операции
    ('11-switch.kum', '2\n', 'вторник\n'),  # Выбор
    ('12-switch.kum', '7\n', 'воскресенье\n'),  # Выбор
    ('13-loopN.kum', None, '1\n2\n3\n4\n5\n'),  # Цикл N раз
    ('14-while.kum', None, '1\n2\n3\n4\n5\n'),  # Цикл ПОКА
    ('15-while.kum', '5\n', '5\n4\n3\n2\n1\n'),  # Цикл ПОКА с вводом
    ('16-repeat.kum', None, '1\n2\n3\n4\n5\n'),  # Цикл с постусловием
    ('17-for.kum', None, '1\n2\n3\n4\n5\n'),  # Цикл ДЛЯ
    ('18-downto.kum', None, '5\n4\n3\n2\n1\n'),  # Цикл ДЛЯ с шагом -1
    ('19-prime.kum', '17\n', 'простое\n'),  # Проверка на простое число
    ('20-proc-err.kum', None, 'Ошибка в процедуре\n'),  # Процедуры
]

def run_kumir_program(program_path, input_data=None):
    """
    Запускает программу на КуМире и возвращает её вывод.
    
    Args:
        program_path (str): Путь к файлу с программой
        input_data (str): Входные данные (если нужны)
        
    Returns:
        str: Вывод программы
    """
    # Читаем код программы
    try:
        with open(program_path, 'r', encoding='utf-8') as f:
            code = f.read().replace('\r\n', '\n')  # Нормализуем переводы строк
    except UnicodeDecodeError:
        with open(program_path, 'r', encoding='cp1251') as f:
            code = f.read().replace('\r\n', '\n')  # Нормализуем переводы строк
            
    print(f"[DEBUG] Запуск программы: {program_path}", file=sys.stderr)
    print(f"[DEBUG] Входные данные: {input_data}", file=sys.stderr)
    
    # Если есть входные данные, подготавливаем их
    if input_data:
        sys.stdin = StringIO(input_data)
    
    # Перехватываем стандартный вывод
    output = StringIO()
    stderr = StringIO()
    
    # Запускаем программу и перехватываем вывод
    with redirect_stdout(output), redirect_stderr(stderr):
        try:
            interpret_kumir(code)
        except Exception as e:
            print(f"[DEBUG] Ошибка при выполнении: {e}", file=sys.stderr)
            raise
    
    # Восстанавливаем стандартный ввод, если он был изменен
    if input_data:
        sys.stdin = sys.__stdin__
        
    # Получаем вывод программы
    result = output.getvalue()
    debug_output = stderr.getvalue()
    
    print(f"[DEBUG] Отладочный вывод:\n{debug_output}", file=sys.stderr)
    print(f"[DEBUG] Стандартный вывод:\n{result}", file=sys.stderr)
    
    return result

@pytest.mark.parametrize("program,input_data,expected_output", TEST_CASES)
def test_kumir_program(program, input_data, expected_output):
    """
    Тестирует выполнение программы на КуМире.
    
    Args:
        program (str): Имя файла программы
        input_data (str): Входные данные (если нужны)
        expected_output (str): Ожидаемый вывод
    """
    program_path = os.path.join(KUMIR_EXAMPLES_DIR, program)
    assert os.path.exists(program_path), f"Файл программы не найден: {program}"
    
    actual_output = run_kumir_program(program_path, input_data)
    if expected_output is not None:  # Пропускаем проверку для программ с недетерминированным выводом
        assert actual_output == expected_output, \
            f"Неверный вывод для {program}:\nОжидалось:\n{expected_output}\nПолучено:\n{actual_output}" 