# safe_eval.py (updated fragment)

import math
from .identifiers import convert_hex_constants
from .builtins import int_to_str, float_to_str, str_to_float, str_to_int, Int, Float, Bool
from .math_functions import (
    sqrt, abs_val, iabs, sign,
    sin_val, cos_val, tg, ctg, arcsin_val, arccos_val, arctg, arcctg,
    ln, lg, exp_val,
    min_val, max_val, imin, imax, div, mod, int_part,
    rnd, rand, irnd, irand, MAX_INT, MAX_FLOAT
)
from .text_functions import length, char_code, unicode_code, char, unicode_char

from .string_utils import (
    to_upper, to_lower,
    position, pos, position_after, pos_after,
    insert, replace_str, delete_str
)

from .file_functions import (
    open_for_reading, open_for_writing, open_for_append, close_file,
    reset_reading, eof, has_data,
    set_encoding, can_open_for_reading, can_open_for_writing,
    exists, is_directory, create_directory, delete_file, delete_directory,
    full_path, WORKING_DIRECTORY, PROGRAM_DIRECTORY,
    set_input, set_output, console_file
)
from .system_functions import sleep_ms, current_time  # новый импорт


def safe_eval(expr, eval_env):
    expr = convert_hex_constants(expr)
    safe_globals = {
        "__builtins__": None,
        # Math functions
        "sin": sin_val,
        "cos": cos_val,
        "sqrt": sqrt,
        "int": int_part,
        "float": float,
        # Number conversion functions
        "int_to_str": int_to_str,
        "float_to_str": float_to_str,
        "str_to_float": str_to_float,
        "str_to_int": str_to_int,
        "Int": Int,
        "Float": Float,
        "Bool": Bool,
        # Additional math functions
        "abs": abs_val,
        "iabs": iabs,
        "sign": sign,
        "tan": tg,  # заменяем tan_val на tg
        "cot": ctg,
        "arcsin": arcsin_val,
        "arccos": arccos_val,
        "arctan": arctg,  # заменяем arctan_val на arctg
        "arccot": arcctg,
        "ln": ln,
        "lg": lg,
        "exp": exp_val,
        "min": min_val,
        "max": max_val,
        "imin": imin,
        "imax": imax,
        "div": div,
        "mod": mod,
        "rnd": rnd,
        "rand": rand,
        "irnd": irnd,
        "irand": irand,
        "MAX_INT": MAX_INT,
        "MAX_FLOAT": MAX_FLOAT,
        # Text functions
        "length": length,
        "char_code": char_code,
        "unicode_code": unicode_code,
        "char": char,
        "unicode_char": unicode_char,
        # String processing functions
        "to_upper": to_upper,
        "to_lower": to_lower,
        "position": position,
        "pos": pos,
        "position_after": position_after,
        "pos_after": pos_after,
        "insert": insert,
        "replace_str": replace_str,
        "delete_str": delete_str,
        # File functions
        "open_for_reading": open_for_reading,
        "open_for_writing": open_for_writing,
        "open_for_append": open_for_append,
        "close_file": close_file,
        "reset_reading": reset_reading,
        "eof": eof,
        "has_data": has_data,
        "set_encoding": set_encoding,
        "can_open_for_reading": can_open_for_reading,
        "can_open_for_writing": can_open_for_writing,
        "exists": exists,
        "is_directory": is_directory,
        "create_directory": create_directory,
        "delete_file": delete_file,
        "delete_directory": delete_directory,
        "full_path": full_path,
        "WORKING_DIRECTORY": WORKING_DIRECTORY,
        "PROGRAM_DIRECTORY": PROGRAM_DIRECTORY,
        "set_input": set_input,
        "set_output": set_output,
        "console_file": console_file,
        # System functions
        "sleep_ms": sleep_ms,
        "current_time": current_time,
    }
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    result = {}
    for var, info in env.items():
        result[var] = info.get("value")
    return result
