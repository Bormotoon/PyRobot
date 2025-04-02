# FILE START: kumir_globals.py
"""
Модуль для определения глобально доступных функций и констант
в безопасном окружении вычисления выражений Кумира.
"""
import logging  # Добавим логгер и сюда, если нужно
import math

logger = logging.getLogger('KumirGlobals')

# Импорты функций из других модулей проекта
from .builtins import int_to_str, float_to_str, str_to_float, str_to_int, Int, Float, Bool
from .file_functions import (
	open_for_reading, open_for_writing, open_for_append, close_file, reset_reading, eof,
	has_data, set_encoding, can_open_for_reading, can_open_for_writing, exists, is_directory,
	create_directory, delete_file, delete_directory, full_path, WORKING_DIRECTORY,
	PROGRAM_DIRECTORY, set_input, set_output, console_file
)
from .math_functions import (sqrt, abs_val, iabs, sign, sin_val, cos_val, tan_val, cot, arcsin_val, arccos_val,
							 arctan_val, arccot, ln, lg, exp_val, min_val, max_val, imin, imax, div, mod, int_part, rnd,
							 rand, irnd, irand, max_int, max_float)
from .string_utils import (to_upper, to_lower, position, position_after, insert, replace_str,
						   delete_str)
from .system_functions import current_time  # , sleep_ms # sleep_ms все еще не рекомендуется
from .text_functions import length, char_code, unicode_code, char, unicode_char

# --->>> УДАЛЯЕМ ЭТУ СТРОКУ ИМПОРТА <<<---
# from .kumir_interpreter.interpreter import KumirLanguageInterpreter, KumirExecutionError, KumirEvalError # НЕ НУЖНО ЗДЕСЬ

# Глобальные переменные и функции, разрешенные для использования в выражениях Кумира.
SAFE_GLOBALS = {
	"__builtins__": None,  # Запрещаем встроенные функции Python по умолчанию
	# Математика
	"sin": sin_val, "cos": cos_val, "tan": tan_val, "cot": cot, "arcsin": arcsin_val, "arccos": arccos_val,
	"arctan": arctan_val, "arccot": arccot, "sqrt": sqrt, "ln": ln, "lg": lg, "exp": exp_val, "abs": abs_val,
	"iabs": iabs, "sign": sign, "int": int_part,  # 'int' теперь это KUMIR'овский int_part
	"min": min_val, "max": max_val, "imin": imin, "imax": imax, "div": div, "mod": mod,
	"rnd": rnd, "rand": rand, "irnd": irnd, "irand": irand,
	"МАКСЦЕЛ": max_int(), "MAX_INT": max_int(), "MAX_FLOAT": max_float(),
	"pi": math.pi, "e": math.e,
	# Встроенные Кумир (преобразования типов и т.д.)
	"цел_в_лит": int_to_str, "вещ_в_лит": float_to_str, "лит_в_цел": str_to_int, "лит_в_вещ": str_to_float,
	"Цел": Int, "Вещ": Float, "Лог": Bool,
	"да": True, "нет": False,
	# Строки
	"длин": length, "симв": char_code, "код": char_code, "юникод": unicode_code,
	"символ": char, "юнисимвол": unicode_char,
	"в_верхний_регистр": to_upper, "в_нижний_регистр": to_lower,
	"поз": position, "поз_после": position_after,
	"вставить": insert, "заменить": replace_str, "удалить": delete_str,
	# Система
	# "ждать": sleep_ms,
	"время": current_time,
	# Файловые функции (теперь безопасные внутри песочницы)
	"откр_для_чт": open_for_reading, "откр_для_зап": open_for_writing, "откр_для_доб": open_for_append,
	"закр": close_file, "сброс_чт": reset_reading, "eof": eof, "есть_данные": has_data,
	"уст_кодировку": set_encoding, "можно_откр_для_чт": can_open_for_reading,
	"можно_откр_для_зап": can_open_for_writing, "сущ": exists, "папка": is_directory,
	"создать_папку": create_directory, "удалить_файл": delete_file, "удалить_папку": delete_directory,
	"полный_путь": full_path, "РАБ_ПАПКА": WORKING_DIRECTORY, "ПАПКА_ПРОГРАММЫ": PROGRAM_DIRECTORY,
	"уст_ввод": set_input, "уст_вывод": set_output, "консоль": console_file,

	# Добавим базовые Python функции, которые могут быть полезны и безопасны
	"float": float,  # Для преобразования внутри выражений
	"int": int,  # Для преобразования внутри выражений (стандартный Python int)
	"str": str,  # Для преобразования в строку
}

logger.debug(f"SAFE_GLOBALS initialized with {len(SAFE_GLOBALS)} entries.")

# FILE END: kumir_globals.py
