from .builtins import int_to_str, float_to_str, str_to_float, str_to_int, Int, Float, Bool
from .file_functions import (open_for_reading, open_for_writing, open_for_append, close_file, reset_reading, eof,
                             has_data, set_encoding, can_open_for_reading, can_open_for_writing, exists, is_directory,
                             create_directory, delete_file, delete_directory, full_path, WORKING_DIRECTORY,
                             PROGRAM_DIRECTORY, set_input, set_output, console_file)
from .identifiers import convert_hex_constants
from .math_functions import (sqrt, abs_val, iabs, sign, sin_val, cos_val, tan_val, cot, arcsin_val, arccos_val,
                             arctan_val, arccot, ln, lg, exp_val, min_val, max_val, imin, imax, div, mod, int_part, rnd,
                             rand, irnd, irand, max_int, max_float)
from .string_utils import (to_upper, to_lower, position, pos, position_after, pos_after, insert, replace_str,
                           delete_str)
from .system_functions import sleep_ms, current_time  # новый импорт
from .text_functions import length, char_code, unicode_code, char, unicode_char


def safe_eval(expr, eval_env):
    """
    Безопасно вычисляет выражение, используя ограниченное окружение глобальных переменных.

    Функция сначала заменяет шестнадцатеричные константы (начинающиеся с '$') на формат,
    понятный Python (например, '$100' -> '0x100'), затем вызывает встроенную функцию eval()
    с заранее определенным набором безопасных глобальных функций и констант, доступных в KUMIR.

    Параметры:
      expr (str): Выражение для вычисления.
      eval_env (dict): Окружение (словарь переменных), доступное для вычисления.

    Возвращаемое значение:
      Результат вычисления выражения expr.

    Примечание:
      Использование eval() ограничено только безопасными функциями, чтобы предотвратить выполнение нежелательного кода.
    """
    # Преобразуем шестнадцатеричные константы в выражении
    expr = convert_hex_constants(expr)

    # Определяем безопасное глобальное окружение, разрешающее только вызов определённых функций и констант
    safe_globals = {"__builtins__": None,  # Отключаем доступ к стандартным встроенным функциям для безопасности
        # Математические функции
        "sin": sin_val, "cos": cos_val, "sqrt": sqrt, "int": int_part,
        # Используем int_part для получения целой части числа
        "float": float, # Функции для преобразования чисел в строки и обратно
        "int_to_str": int_to_str, "float_to_str": float_to_str, "str_to_float": str_to_float, "str_to_int": str_to_int,
        "Int": Int, "Float": Float, "Bool": Bool, # Дополнительные математические функции
        "abs": abs_val, "iabs": iabs, "sign": sign, "tan": tan_val,  # tan теперь ссылается на функцию tan_val
        "cot": cot,  # cot для вычисления котангенса
        "arcsin": arcsin_val, "arccos": arccos_val, "arctan": arctan_val, "arccot": arccot, "ln": ln, "lg": lg,
        "exp": exp_val, "min": min_val, "max": max_val, "imin": imin, "imax": imax, "div": div, "mod": mod, "rnd": rnd,
        "rand": rand, "irnd": irnd, "irand": irand, "MAX_INT": max_int(),  # Максимальное целое число для KUMIR
        "MAX_FLOAT": max_float(),  # Максимальное вещественное число
        # Функции для работы с текстом
        "length": length, "char_code": char_code, "unicode_code": unicode_code, "char": char,
        "unicode_char": unicode_char, # Функции обработки строк
        "to_upper": to_upper, "to_lower": to_lower, "position": position, "pos": pos, "position_after": position_after,
        "pos_after": pos_after, "insert": insert, "replace_str": replace_str, "delete_str": delete_str,
        # Функции работы с файлами
        "open_for_reading": open_for_reading, "open_for_writing": open_for_writing, "open_for_append": open_for_append,
        "close_file": close_file, "reset_reading": reset_reading, "eof": eof, "has_data": has_data,
        "set_encoding": set_encoding, "can_open_for_reading": can_open_for_reading,
        "can_open_for_writing": can_open_for_writing, "exists": exists, "is_directory": is_directory,
        "create_directory": create_directory, "delete_file": delete_file, "delete_directory": delete_directory,
        "full_path": full_path, "WORKING_DIRECTORY": WORKING_DIRECTORY, "PROGRAM_DIRECTORY": PROGRAM_DIRECTORY,
        "set_input": set_input, "set_output": set_output, "console_file": console_file, # Системные функции
        "sleep_ms": sleep_ms, "current_time": current_time, }
    # Вычисляем выражение с использованием eval() с безопасными глобальными переменными и переданным окружением eval_env
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    """
    Преобразует окружение переменных для использования в вычислении выражений.

    Функция создает новый словарь, где каждому имени переменной из исходного окружения
    соответствует ее текущее значение (ключ "value" в словаре информации о переменной).

    Параметры:
      env (dict): Исходное окружение переменных, где каждая переменная представлена в виде
                  ключа со значением, являющимся словарем (например, {"type": ..., "value": ...}).

    Возвращаемое значение:
      dict: Новый словарь, содержащий пары "имя переменной": "ее значение".
    """
    result = {}
    # Перебираем все переменные в окружении и извлекаем их значения
    for var, info in env.items():
        result[var] = info.get("value")
    return result
