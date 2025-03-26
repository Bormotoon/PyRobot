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

logger = logging.getLogger('KumirSafeEval')


# --- Define Custom Exception ---
class KumirEvalError(Exception):
	"""Custom exception for errors occurring during safe_eval."""
	pass


# -----------------------------

# Global variable scope for eval (builtins are explicitly limited)
# Combine all imported functions and constants into one dictionary
SAFE_GLOBALS = {"__builtins__": None,  # Disable standard builtins for security

				# --- Math Functions ---
				"sin": sin_val, "cos": cos_val, "tan": tan_val, "cot": cot, "arcsin": arcsin_val, "arccos": arccos_val,
				"arctan": arctan_val, "arccot": arccot, "sqrt": sqrt, "ln": ln, "lg": lg, "exp": exp_val,
				"abs": abs_val,
				"iabs": iabs, "sign": sign, "int": int_part,  # 'int' maps to int_part
				"min": min_val, "max": max_val, "imin": imin, "imax": imax, "div": div, "mod": mod, "rnd": rnd,
				"rand": rand,
				"irnd": irnd, "irand": irand, "МАКСЦЕЛ": max_int(),  # Use function call to get value
				"MAX_INT": max_int(),  # Alias
				"MAX_FLOAT": max_float(),

				# --- Type Conversion Functions ---
				"int_to_str": int_to_str, "float_to_str": float_to_str, "str_to_int": str_to_int,
				"str_to_float": str_to_float,
				"Int": Int, "Float": Float, "Bool": Bool,
				# Basic python types (use with caution, consider wrapping if needed)
				# 'float': float, - Let's rely on explicit conversion functions for now

				# --- Boolean Constants ---
				"да": True, "нет": False,

				# --- Text/String Functions ---
				"length": length, "char_code": char_code, "unicode_code": unicode_code, "char": char,
				"unicode_char": unicode_char,
				"to_upper": to_upper, "to_lower": to_lower, "position": position, "pos": pos,
				"position_after": position_after,
				"pos_after": pos_after, "insert": insert, "replace_str": replace_str, "delete_str": delete_str,

				# --- File Functions ---
				"open_for_reading": open_for_reading, "open_for_writing": open_for_writing,
				"open_for_append": open_for_append,
				"close_file": close_file, "reset_reading": reset_reading, "eof": eof, "has_data": has_data,
				"set_encoding": set_encoding, "can_open_for_reading": can_open_for_reading,
				"can_open_for_writing": can_open_for_writing, "exists": exists, "is_directory": is_directory,
				"create_directory": create_directory, "delete_file": delete_file, "delete_directory": delete_directory,
				"full_path": full_path, "WORKING_DIRECTORY": WORKING_DIRECTORY, "PROGRAM_DIRECTORY": PROGRAM_DIRECTORY,
				"set_input": set_input, "set_output": set_output, "console_file": console_file,

				# --- System Functions ---
				"sleep_ms": sleep_ms, "current_time": current_time, }


def safe_eval(expr, eval_env):
	"""
    Безопасно вычисляет выражение KUMIR.

    Преобразует hex константы, затем использует eval() с ограниченным
    глобальным окружением (SAFE_GLOBALS) и предоставленным локальным
    окружением (eval_env).

    Args:
        expr (str): Выражение для вычисления.
        eval_env (dict): Словарь локальных переменных (имя: значение).

    Returns:
        Результат вычисления выражения.

    Raises:
        KumirEvalError: Если происходит ошибка во время вычисления (NameError, TypeError, etc.)
                        или при преобразовании шестнадцатеричных констант.
    """
	try:
		# Преобразуем шестнадцатеричные константы ('$FF' -> '0xFF')
		processed_expr = convert_hex_constants(expr)
	except Exception as e:
		logger.error(f"Error converting hex constants in expression '{expr}': {e}", exc_info=True)
		raise KumirEvalError(f"Ошибка преобразования шестнадцатеричных констант в '{expr}': {e}")

	try:
		logger.debug(f"Safely evaluating: '{processed_expr}' with env keys: {list(eval_env.keys())}")
		# Выполняем eval с ограниченными globals и переданным locals
		result = eval(processed_expr, SAFE_GLOBALS, eval_env)
		logger.debug(f"Evaluation result: {result}")
		return result
	except NameError as e:
		logger.warning(f"Evaluation failed: NameError - {e} in expression '{processed_expr}'")
		raise KumirEvalError(f"Неизвестное имя (переменная или функция) в выражении: {e}")
	except TypeError as e:
		logger.warning(f"Evaluation failed: TypeError - {e} in expression '{processed_expr}'")
		raise KumirEvalError(f"Ошибка типа при вычислении выражения: {e}")
	except SyntaxError as e:
		logger.error(f"Evaluation failed: SyntaxError - {e} in expression '{processed_expr}'")
		raise KumirEvalError(f"Синтаксическая ошибка в выражении: {e}")
	except ZeroDivisionError:
		logger.error(f"Evaluation failed: ZeroDivisionError in expression '{processed_expr}'")
		raise KumirEvalError("Деление на ноль.")
	except Exception as e:
		# Перехватываем другие возможные ошибки во время eval
		logger.error(f"Unexpected evaluation error for '{processed_expr}': {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка при вычислении выражения '{processed_expr}': {e}")


def get_eval_env(env):
	"""
    Преобразует полное окружение переменных интерпретатора в словарь
    "имя: значение" для использования в safe_eval.

    Args:
        env (dict): Полное окружение переменных ({ var: {'type':..., 'value':...} }).

    Returns:
        dict: Словарь только с именами и значениями переменных.
    """
	eval_env = {}
	# Перебираем все переменные в окружении и извлекаем их значения
	for var, info in env.items():
		# Проверяем, что info - это словарь и содержит 'value'
		if isinstance(info, dict) and 'value' in info:
			eval_env[var] = info.get("value")
		else:
			# Логируем предупреждение, если структура env неожиданная
			logger.warning(f"Некорректная структура для переменной '{var}' в окружении при создании eval_env.")
			eval_env[var] = None  # Или пропустить эту переменную?
	return eval_env

# Import math only where needed within functions to avoid potential patching issues?
# Example for _validate_and_convert_value (already used above)
# Note: It's generally safe to import standard libraries like math at the top
# AFTER eventlet.monkey_patch() has run.

# Placeholder for the conversion function needed by declarations.py
# (This is redundant if declarations.py imports this module, better keep it separate)
# def _validate_and_convert_value(value, target_type, var_name_for_error):
#     # ... implementation as provided previously ...
#     # Ensure 'math' is imported if needed for math.isfinite etc.
#     import math
#     try:
#        # ... (rest of the validation/conversion logic)
#     except (ValueError, TypeError) as e:
#          raise KumirEvalError(...) # Raise specific error if needed
