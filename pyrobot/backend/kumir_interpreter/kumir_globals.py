# FILE START: kumir_globals.py
"""
Модуль для определения глобально доступных функций и констант
в безопасном окружении вычисления выражений Кумира.
"""
import math

# Импорты функций из других модулей проекта
from .builtins import int_to_str, float_to_str, str_to_float, str_to_int, Int, Float, Bool
# Файловые функции все еще опасны, оставляем их закомментированными
# from .file_functions import (...)
from .math_functions import (sqrt, abs_val, iabs, sign, sin_val, cos_val, tan_val, cot, arcsin_val, arccos_val,
							 arctan_val, arccot, ln, lg, exp_val, min_val, max_val, imin, imax, div, mod, int_part, rnd,
							 rand, irnd, irand, max_int, max_float)
from .string_utils import (to_upper, to_lower, position, position_after, insert, replace_str,
						   delete_str)
# sleep_ms - блокирующая, лучше не использовать на сервере
from .system_functions import current_time  # , sleep_ms
from .text_functions import length, char_code, unicode_code, char, unicode_char

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
	# Система (ОСТОРОЖНО: sleep_ms - блокирующая!)
	# "ждать": sleep_ms,
	"время": current_time,
	# Файлы (ЗАКОММЕНТИРОВАНО - ОПАСНО!)
	# ... (все файловые функции остаются закомментированными) ...

	# Добавим базовые Python функции, которые могут быть полезны и безопасны
	"float": float,  # Для преобразования внутри выражений
	"int": int,  # Для преобразования внутри выражений (стандартный Python int)
	"str": str,  # Для преобразования в строку
}

# FILE END: kumir_globals.py
