import math
import logging
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
from .system_functions import sleep_ms, current_time
from .text_functions import length, char_code, unicode_code, char, unicode_char
# --- ИМПОРТИРУЕМ КЛАСС РОБОТА ДЛЯ ПРОВЕРКИ ТИПА ---
from .robot_state import SimulatedRobot, RobotError

logger = logging.getLogger('KumirSafeEval')


class KumirEvalError(Exception):
    """Custom exception for errors occurring during safe_eval."""
    pass


# --- ОБЪЯВЛЯЕМ SAFE_GLOBALS ЗДЕСЬ, ДОБАВИМ СЕНСОРЫ РОБОТА ПОЗЖЕ В get_eval_env ---
SAFE_GLOBALS = {
    "__builtins__": None,  # Disable standard builtins

    # --- Math Functions ---
    "sin": sin_val, "cos": cos_val, "tan": tan_val, "cot": cot,
    "arcsin": arcsin_val, "arccos": arccos_val, "arctan": arctan_val, "arccot": arccot,
    "sqrt": sqrt, "ln": ln, "lg": lg, "exp": exp_val, "abs": abs_val, "iabs": iabs,
    "sign": sign, "int": int_part, "min": min_val, "max": max_val, "imin": imin,
    "imax": imax, "div": div, "mod": mod, "rnd": rnd, "rand": rand, "irnd": irnd,
    "irand": irand, "МАКСЦЕЛ": max_int(), "MAX_INT": max_int(), "MAX_FLOAT": max_float(),

    # --- Type Conversion ---
    "int_to_str": int_to_str, "float_to_str": float_to_str, "str_to_int": str_to_int,
    "str_to_float": str_to_float, "Int": Int, "Float": Float, "Bool": Bool,

    # --- Boolean Constants ---
    "да": True, "нет": False,

    # --- Text/String ---
    "length": length, "char_code": char_code, "unicode_code": unicode_code, "char": char,
    "unicode_char": unicode_char, "to_upper": to_upper, "to_lower": to_lower,
    "position": position, "pos": pos, "position_after": position_after, "pos_after": pos_after,
    "insert": insert, "replace_str": replace_str, "delete_str": delete_str,

    # --- File ---
    "open_for_reading": open_for_reading, "open_for_writing": open_for_writing,
    "open_for_append": open_for_append, "close_file": close_file, "reset_reading": reset_reading,
    "eof": eof, "has_data": has_data, "set_encoding": set_encoding,
    "can_open_for_reading": can_open_for_reading, "can_open_for_writing": can_open_for_writing,
    "exists": exists, "is_directory": is_directory, "create_directory": create_directory,
    "delete_file": delete_file, "delete_directory": delete_directory, "full_path": full_path,
    "WORKING_DIRECTORY": WORKING_DIRECTORY, "PROGRAM_DIRECTORY": PROGRAM_DIRECTORY,
    "set_input": set_input, "set_output": set_output, "console_file": console_file,

    # --- System ---
    "sleep_ms": sleep_ms, "current_time": current_time,

    # --- Робот-Сенсоры (имена КуМир будут добавлены в get_eval_env) ---
    # Эти Python функции-обертки будут добавлены динамически
}


def safe_eval(expr, eval_env):
    """
    Безопасно вычисляет выражение KUMIR.
    Использует ограниченные SAFE_GLOBALS и локальное окружение eval_env,
    которое теперь ДОЛЖНО содержать функции-сенсоры робота.

    Args:
        expr (str): Выражение для вычисления.
        eval_env (dict): Локальное окружение (переменные + функции-сенсоры робота).

    Returns:
        Результат вычисления выражения.

    Raises:
        KumirEvalError: Если происходит ошибка во время вычисления.
    """
    try:
        processed_expr = convert_hex_constants(expr)
    except Exception as e:
        logger.error(f"Ошибка конвертации hex в '{expr}': {e}", exc_info=True)
        raise KumirEvalError(f"Ошибка шестнадцатеричных констант в '{expr}': {e}")

    try:
        # logger.debug(f"Eval: '{processed_expr}' with env keys: {list(eval_env.keys())}")
        # Выполняем eval с ГЛОБАЛЬНЫМИ базовыми функциями и ЛОКАЛЬНЫМ окружением
        # Локальное окружение eval_env теперь содержит и переменные, и обертки сенсоров робота
        result = eval(processed_expr, SAFE_GLOBALS, eval_env)
        # logger.debug(f"Eval result: {result}")
        return result
    except NameError as e:
        logger.warning(f"Eval NameError: {e} in '{processed_expr}'")
        raise KumirEvalError(f"Неизвестное имя: {e}")
    except TypeError as e:
        logger.warning(f"Eval TypeError: {e} in '{processed_expr}'")
        raise KumirEvalError(f"Ошибка типа: {e}")
    except SyntaxError as e:
        logger.error(f"Eval SyntaxError: {e} in '{processed_expr}'")
        raise KumirEvalError(f"Синтаксическая ошибка: {e}")
    except ZeroDivisionError:
        logger.error(f"Eval ZeroDivisionError in '{processed_expr}'")
        raise KumirEvalError("Деление на ноль.")
    except RobotError as e:  # Перехватываем ошибки робота, если они возникли при вызове сенсора
        logger.warning(f"RobotError during eval of '{processed_expr}': {e}")
        raise KumirEvalError(f"Ошибка робота при проверке условия: {e}")
    except Exception as e:
        logger.error(f"Unexpected eval error for '{processed_expr}': {e}", exc_info=True)
        raise KumirEvalError(f"Неожиданная ошибка при вычислении '{processed_expr}': {e}")


def get_eval_env(env, robot=None):
    """
    Преобразует полное окружение и объект робота в словарь "имя: значение/функция" для safe_eval.

    Args:
        env (dict): Полное окружение переменных ({ var: {'type':..., 'value':...} }).
        robot (SimulatedRobot, optional): Экземпляр робота для вызова сенсоров.

    Returns:
        dict: Словарь с переменными и функциями-сенсорами робота.
    """
    eval_env = {}
    # 1. Добавляем значения переменных
    for var, info in env.items():
        if isinstance(info, dict) and 'value' in info:
            eval_env[var] = info.get("value")
        else:
            logger.warning(f"Некорректная структура env для '{var}' при создании eval_env.")
            eval_env[var] = None

    # 2. Добавляем функции-сенсоры робота, если робот передан
    if robot and isinstance(robot, SimulatedRobot):
        # Создаем замыкания (closures) для вызова методов робота
        def _is_left_free():
            return robot.check_direction("left", "free")

        def _is_right_free():
            return robot.check_direction("right", "free")

        def _is_up_free():
            return robot.check_direction("up", "free")

        def _is_down_free():
            return robot.check_direction("down", "free")

        def _is_left_wall():
            return robot.check_direction("left", "wall")

        def _is_right_wall():
            return robot.check_direction("right", "wall")

        def _is_up_wall():
            return robot.check_direction("up", "wall")

        def _is_down_wall():
            return robot.check_direction("down", "wall")

        def _is_cell_painted():
            return robot.check_cell("painted")

        def _is_cell_clear():
            return robot.check_cell("clear")

        # Добавляем русские имена функций в eval_env
        # Пробелы в именах КуМир должны быть заменены на `_` в Python
        eval_env["слева_свободно"] = _is_left_free
        eval_env["справа_свободно"] = _is_right_free
        eval_env["сверху_свободно"] = _is_up_free
        eval_env["снизу_свободно"] = _is_down_free
        eval_env["слева_стена"] = _is_left_wall
        eval_env["справа_стена"] = _is_right_wall
        eval_env["сверху_стена"] = _is_up_wall
        eval_env["снизу_стена"] = _is_down_wall
        eval_env["клетка_закрашена"] = _is_cell_painted
        eval_env["клетка_чистая"] = _is_cell_clear
    elif robot:
        logger.error("get_eval_env: robot object provided but is not a SimulatedRobot instance.")
    # else: logger.debug("get_eval_env: robot not provided, sensor functions not added.")

    return eval_env