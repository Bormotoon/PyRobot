# FILE START: kumir_expression_translator.py
import logging
import re

# Импортируем SAFE_GLOBALS, чтобы получить список валидных Python-имен
# Это создаст зависимость, но она менее критична, чем предыдущие циклы.
# Альтернатива - передавать словарь имен как аргумент.
try:
	# Попытка импорта для получения имен
	from .kumir_globals import SAFE_GLOBALS

	# Создаем словарь трансляции ИМЕН Кумир -> Python
	# Нужно убедиться, что все нужные имена здесь есть.
	# Ключи - кумирские имена в нижнем регистре (возможно, без пробелов для удобства поиска)
	# Значения - ключи из SAFE_GLOBALS
	KUMIR_NAME_TRANSLATIONS = {
		"sin": "sin", "cos": "cos", "tan": "tan", "cot": "cot",
		"arcsin": "arcsin", "arccos": "arccos", "arctan": "arctan", "arccot": "arccot",
		"sqrt": "sqrt", "ln": "ln", "lg": "lg", "exp": "exp",
		"abs": "abs", "iabs": "iabs", "sign": "sign",
		# 'int' Кумира - это 'int_part' в Python, но в выражениях Python int() тоже может быть нужен.
		# Оставляем стандартный Python 'int'. KUMIR 'int' обычно не используется в выражениях напрямую.
		"int": "int",  # Стандартный Python int
		"цел": "int",  # Для преобразований
		"вещ": "float",  # Для преобразований
		"лог": "bool",  # Для преобразований
		"лит": "str",  # Для преобразований
		"min": "min", "max": "max", "imin": "imin", "imax": "imax",
		"div": "div",  # Уже заменяется в OPS, но можно и здесь для полноты
		"mod": "mod",  # Уже заменяется в OPS
		"rnd": "rnd", "rand": "rand", "irnd": "irnd", "irand": "irand",
		"максцел": "МАКСЦЕЛ",  # Или "max_int()"? Зависит от реализации в globals
		"максвещ": "MAX_FLOAT",  # Или "max_float()"?
		"пи": "pi", "е": "e",
		"цел_в_лит": "цел_в_лит", "вещ_в_лит": "вещ_в_лит",
		"лит_в_цел": "лит_в_цел", "лит_в_вещ": "лит_в_вещ",
		"цел": "Цел", "вещ": "Вещ", "лог": "Лог",
		# "да": "True", "нет": "False", # Уже заменяются в OPS
		"длин": "длин", "симв": "симв", "код": "код", "юникод": "юникод",
		"символ": "символ", "юнисимвол": "юнисимвол",
		"вверхнийрегистр": "в_верхний_регистр",  # Пример без пробелов
		"внижнийрегистр": "в_нижний_регистр",  # Пример без пробелов
		"в_верхний_регистр": "в_верхний_регистр",
		"в_нижний_регистр": "в_нижний_регистр",
		"поз": "поз", "позпосле": "поз_после", "поз_после": "поз_после",
		"вставить": "вставить", "заменить": "заменить", "удалить": "удалить",
		"время": "время",
		# --- Сенсоры Робота ---
		# Важно: ключи здесь должны соответствовать тому, как пользователь их пишет
		# (например, с пробелами), а значения - ключам в словаре robot_sensors
		"слева свободно": "слева_свободно",
		"справа свободно": "справа_свободно",
		"сверху свободно": "сверху_свободно",
		"снизу свободно": "снизу_свободно",
		"слева стена": "слева_стена",
		"справа стена": "справа_стена",
		"сверху стена": "сверху_стена",
		"снизу стена": "снизу_стена",
		"клетка закрашена": "клетка_закрашена",
		"клетка чистая": "клетка_чистая",
		"радиация": "радиация",
		"температура": "температура",
		# Добавляем алиасы без пробелов для сенсоров, если они поддерживаются
		"слевасвободно": "слева_свободно",
		"справасвободно": "справа_свободно",
		"сверхусвободно": "сверху_свободно",
		"снизусвободно": "снизу_свободно",
		"слевастена": "слева_стена",
		"справастена": "справа_стена",
		"сверхустена": "сверху_стена",
		"снизустена": "снизу_стена",
		"клетказакрашена": "клетка_закрашена",
		"клеткачистая": "клетка_чистая",
		# Добавляем имена файлов, если они используются как константы
		"консоль": "консоль",  # Если console_file() доступна под этим именем
		# Добавить другие функции из kumir_globals.py по мере необходимости...
	}
	# Проверим, что все значения из словаря трансляции есть в SAFE_GLOBALS (или базовых)
	missing_globals = {py_name for py_name in KUMIR_NAME_TRANSLATIONS.values()
	                   if py_name not in SAFE_GLOBALS and py_name not in ['int', 'float', 'bool', 'str']}
	if missing_globals:
		logging.warning(f"Kumir name translations map to unknown Python identifiers: {missing_globals}")

except ImportError:
	logging.error("Could not import SAFE_GLOBALS from kumir_globals.py for translator setup.")
	SAFE_GLOBALS = {}  # Определяем пустой словарь, чтобы код ниже не падал
	KUMIR_NAME_TRANSLATIONS = {}

logger = logging.getLogger('KumirExprTranslator')

# Операторы и константы (кроме имен функций/сенсоров и "не")
KUMIR_TO_PYTHON_OPS = [
	(r'<>', ' != '),
	(r'=', ' == '),
	(r'\bи\b', ' and '),
	(r'\bили\b', ' or '),
	(r'\bdiv\b', ' // '),
	(r'\bmod\b', ' % '),
	(r'\bда\b', ' True '),  # Добавляем пробелы для отделения
	(r'\bнет\b', ' False '),  # Добавляем пробелы
]

# Унарный НЕ
НЕ_PATTERN = re.compile(r"\bне\b", re.IGNORECASE)
# Шестнадцатеричные константы
HEX_PATTERN = re.compile(r'\$(?P<hex>[A-Fa-f0-9]+)')
# Строковые литералы
STRING_LITERAL_PATTERN = re.compile(r'(\"[^\"]*\"|\'[^\']*\')')


class TranslationError(Exception):
	pass


def _replace_names_outside_strings(text, name_translations):
	""" Заменяет известные имена Кумира на их Python-эквиваленты вне строк. """
	parts = STRING_LITERAL_PATTERN.split(text)
	result = []
	# Сортируем ключи по убыванию длины, чтобы сначала заменять более длинные имена
	# (например, "сверху свободно" перед "свободно")
	sorted_kumir_names = sorted(name_translations.keys(), key=len, reverse=True)

	for i, part in enumerate(parts):
		if i % 2 == 1:  # Строковый литерал
			result.append(part)
		else:  # Код вне строки
			temp_part = part
			for kumir_name in sorted_kumir_names:
				python_name = name_translations[kumir_name]
				# Используем regex с границами слова (\b) для точной замены
				# Экранируем специальные символы regex в имени Кумира (если они есть)
				pattern = r'\b' + re.escape(kumir_name) + r'\b'
				# Замена без учета регистра
				temp_part = re.sub(pattern, python_name, temp_part, flags=re.IGNORECASE)
			result.append(temp_part)
	return "".join(result)


def _replace_ops_outside_strings(text, replacements, ne_pattern):
	"""Применяет замены операторов и 'не' только вне строковых литералов."""
	parts = STRING_LITERAL_PATTERN.split(text)
	result = []
	for i, part in enumerate(parts):
		if i % 2 == 1:
			result.append(part)
		else:
			temp_part = part
			# Замена "не"
			temp_part = ne_pattern.sub(' not ', temp_part)
			temp_part = re.sub(r"(\s|^|[(])\s+not\s+", r"\1not ", temp_part)  # Убираем лишний пробел перед not

			# Применяем остальные замены операторов/констант
			for pattern, replacement in replacements:
				if isinstance(pattern, str) and r'\b' in pattern:
					temp_part = re.sub(pattern, replacement, temp_part, flags=re.IGNORECASE)
				elif isinstance(pattern, str):
					temp_part = temp_part.replace(pattern, replacement)
			result.append(temp_part)
	return "".join(result)


def kumir_expr_to_python_expr(kumir_expr):
	"""
	Преобразует строку выражения Кумира в строку выражения Python.
	"""
	logger.debug(f"Translating Kumir expr: '{kumir_expr}'")
	if not isinstance(kumir_expr, str):
		raise TranslationError(f"Expression must be a string, got {type(kumir_expr)}")

	try:
		# 1. Замена шестнадцатеричных констант
		expr_no_hex = HEX_PATTERN.sub(r' 0x\g<hex> ', kumir_expr)
		logger.debug(f"After hex replacement: '{expr_no_hex}'")

		# 2. Замена операторов, 'не', констант да/нет
		expr_ops_replaced = _replace_ops_outside_strings(expr_no_hex, KUMIR_TO_PYTHON_OPS, НЕ_PATTERN)
		logger.debug(f"After operator/const replacement: '{expr_ops_replaced}'")

		# 3. Замена имен функций/сенсоров/переменных Кумира на Python идентификаторы
		python_expr_raw = _replace_names_outside_strings(expr_ops_replaced, KUMIR_NAME_TRANSLATIONS)
		logger.debug(f"After name replacement: '{python_expr_raw}'")

		# 4. Очистка лишних пробелов
		python_expr = python_expr_raw.strip()
		python_expr = re.sub(r'\s+', ' ', python_expr)
		python_expr = python_expr.replace(' ( ', '(').replace(' ) ', ')')
		python_expr = python_expr.replace(' [ ', '[').replace(' ] ', ']')
		python_expr = python_expr.replace(' , ', ', ')
		python_expr = re.sub(r'\bnot\(', 'not (', python_expr)  # Пробел после not перед скобкой
		# Убираем пробел в начале, если остался
		if python_expr.startswith(' '):
			python_expr = python_expr[1:]
		# Убираем пробел перед запятой
		python_expr = python_expr.replace(' ,', ',')


	except Exception as e:
		logger.error(f"Error translating expression '{kumir_expr}': {e}", exc_info=True)
		raise TranslationError(f"Ошибка трансляции выражения '{kumir_expr}': {e}")

	# Проверка на потенциально опасные конструкции
	if '__' in python_expr:
		logger.warning(f"Potential dangerous construct '__' found in translated expr: '{python_expr}'")

	logger.info(f"Translation result for '{kumir_expr}': '{python_expr}'")
	return python_expr

# FILE END: kumir_expression_translator.py