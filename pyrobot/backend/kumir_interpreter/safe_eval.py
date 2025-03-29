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
from .robot_state import SimulatedRobot, RobotError  # Import Robot stuff

logger = logging.getLogger('KumirSafeEval')


class KumirEvalError(Exception): pass


SAFE_GLOBALS = {  # Base safe functions, sensors added dynamically
    "__builtins__": None, "sin": sin_val, "cos": cos_val, "tan": tan_val, "cot": cot, "arcsin": arcsin_val,
    "arccos": arccos_val,
    "arctan": arctan_val, "arccot": arccot, "sqrt": sqrt, "ln": ln, "lg": lg, "exp": exp_val, "abs": abs_val,
    "iabs": iabs,
    "sign": sign, "int": int_part, "min": min_val, "max": max_val, "imin": imin, "imax": imax, "div": div, "mod": mod,
    "rnd": rnd,
    "rand": rand, "irnd": irnd, "irand": irand, "МАКСЦЕЛ": max_int(), "MAX_INT": max_int(), "MAX_FLOAT": max_float(),
    "int_to_str": int_to_str, "float_to_str": float_to_str, "str_to_int": str_to_int, "str_to_float": str_to_float,
    "Int": Int, "Float": Float, "Bool": Bool, "да": True, "нет": False, "length": length, "char_code": char_code,
    "unicode_code": unicode_code, "char": char, "unicode_char": unicode_char, "to_upper": to_upper,
    "to_lower": to_lower,
    "position": position, "pos": pos, "position_after": position_after, "pos_after": pos_after, "insert": insert,
    "replace_str": replace_str, "delete_str": delete_str, "open_for_reading": open_for_reading,
    "open_for_writing": open_for_writing, "open_for_append": open_for_append, "close_file": close_file,
    "reset_reading": reset_reading, "eof": eof, "has_data": has_data, "set_encoding": set_encoding,
    "can_open_for_reading": can_open_for_reading, "can_open_for_writing": can_open_for_writing, "exists": exists,
    "is_directory": is_directory, "create_directory": create_directory, "delete_file": delete_file,
    "delete_directory": delete_directory, "full_path": full_path, "WORKING_DIRECTORY": WORKING_DIRECTORY,
    "PROGRAM_DIRECTORY": PROGRAM_DIRECTORY, "set_input": set_input, "set_output": set_output,
    "console_file": console_file,
    "sleep_ms": sleep_ms, "current_time": current_time,
}


def safe_eval(expr, eval_env):
    """ Безопасно вычисляет выражение KUMIR. """
    try:
        processed_expr = convert_hex_constants(expr)
    except Exception as e:
        raise KumirEvalError(f"Hex err '{expr}': {e}")
    try:
        return eval(processed_expr, SAFE_GLOBALS, eval_env)  # Pass sensors via eval_env
    except NameError as e:
        raise KumirEvalError(f"Неизв. имя: {e}")
    except TypeError as e:
        raise KumirEvalError(f"Ошибка типа: {e}")
    except SyntaxError as e:
        raise KumirEvalError(f"Синтаксис: {e}")
    except ZeroDivisionError:
        raise KumirEvalError("Деление на 0.")
    except RobotError as e:
        raise KumirEvalError(f"Ошибка робота: {e}")  # Pass RobotError up
    except Exception as e:
        logger.error(f"Unexpected eval error '{processed_expr}': {e}", exc_info=True); raise KumirEvalError(
            f"Ошибка выч.: {e}")


def get_eval_env(env, robot=None):
    """ Создает окружение для safe_eval (переменные + сенсоры робота). """
    eval_env = {}
    for var, info in env.items():
        if isinstance(info, dict) and 'value' in info:
            eval_env[var] = info.get("value")
        else:
            logger.warning(f"Неверная структура env['{var}']"); eval_env[var] = None
    if robot and isinstance(robot, SimulatedRobot):
        # Sensor wrappers (closures capturing 'robot')
        def _sf():
            return robot.check_direction("left", "free"); eval_env["слева_свободно"] = _sf

        def _spr():
            return robot.check_direction("right", "free"); eval_env["справа_свободно"] = _spr

        def _sv():
            return robot.check_direction("up", "free"); eval_env["сверху_свободно"] = _sv

        def _sn():
            return robot.check_direction("down", "free"); eval_env["снизу_свободно"] = _sn

        def _stl():
            return robot.check_direction("left", "wall"); eval_env["слева_стена"] = _stl

        def _stpr():
            return robot.check_direction("right", "wall"); eval_env["справа_стена"] = _stpr

        def _stv():
            return robot.check_direction("up", "wall"); eval_env["сверху_стена"] = _stv

        def _stn():
            return robot.check_direction("down", "wall"); eval_env["снизу_стена"] = _stn

        def _kzakr():
            return robot.check_cell("painted"); eval_env["клетка_закрашена"] = _kzakr

        def _kchis():
            return robot.check_cell("clear"); eval_env["клетка_чистая"] = _kchis

        # --- NEW: Add wrappers for radiation/temperature ---
        def _rad():
            return robot.do_measurement("radiation"); eval_env["радиация"] = _rad

        def _temp():
            return robot.do_measurement("temperature"); eval_env["температура"] = _temp
        # ----------------------------------------------------
    elif robot:
        logger.error("get_eval_env: robot obj invalid.")
    return eval_env