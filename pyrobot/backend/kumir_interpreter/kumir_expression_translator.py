# FILE START: kumir_expression_translator.py
import logging
import re

logger = logging.getLogger('KumirExprTranslator')

# Паттерны для поиска и замены. Порядок важен!
# Более специфичные (div, mod) должны идти перед более общими (+, -).
# Обрамляем пробелами, чтобы не заменять внутри слов.
KUMIR_TO_PYTHON_OPS = [
	# Логические и сравнения
	(r'\bи\b', ' and '),
	(r'\bили\b', ' or '),
	(r'\bне\b', ' not '),
	(r'<>', '!='),
	(r'=', '=='),  # Должно быть после <>
	# Арифметика
	(r'\bdiv\b', '//'),
	(r'\bmod\b', '%'),
	# Константы
	(r'\bда\b', 'True'),
	(r'\bнет\b', 'False'),
]

# Паттерн для шестнадцатеричных констант
HEX_PATTERN = re.compile(r'\$(?P<hex>[A-Fa-f0-9]+)')

# Паттерн для строковых литералов (упрощенный, может не обрабатывать экранирование кавычек внутри)
STRING_LITERAL_PATTERN = re.compile(r'("[^"]*"|\'[^\']*\')')


class TranslationError(Exception):
	pass


def _replace_outside_strings(text, replacements):
	"""Применяет замены только вне строковых литералов."""
	parts = STRING_LITERAL_PATTERN.split(text)
	result = []
	for i, part in enumerate(parts):
		if i % 2 == 1:  # Это строковый литерал
			result.append(part)
		else:  # Это код вне строки
			temp_part = part
			for pattern, replacement in replacements:
				# Используем re.sub для замены с учетом границ слов, где применимо
				if isinstance(pattern, str) and pattern.startswith(r'\b'):
					temp_part = re.sub(pattern, replacement, temp_part, flags=re.IGNORECASE)
				else:  # Простая замена для операторов типа <> или =
					temp_part = temp_part.replace(pattern, replacement)
			result.append(temp_part)
	return "".join(result)


def kumir_expr_to_python_expr(kumir_expr):
	"""
	Преобразует строку выражения Кумира в строку выражения Python.

	Args:
		kumir_expr (str): Выражение на языке Кумир.

	Returns:
		str: Эквивалентное выражение на языке Python.

	Raises:
		TranslationError: Если происходит ошибка во время трансляции.
	"""
	logger.debug(f"Translating Kumir expr: '{kumir_expr}'")
	if not isinstance(kumir_expr, str):
		raise TranslationError(f"Expression must be a string, got {type(kumir_expr)}")

	try:
		# 1. Замена шестнадцатеричных констант
		expr_no_hex = HEX_PATTERN.sub(r'0x\g<hex>', kumir_expr)
		logger.debug(f"After hex replacement: '{expr_no_hex}'")

		# 2. Замена операторов и констант вне строковых литералов
		python_expr = _replace_outside_strings(expr_no_hex, KUMIR_TO_PYTHON_OPS)
		logger.debug(f"After operator/const replacement: '{python_expr}'")

	# 3. Дополнительные проверки (например, на недопустимые символы) можно добавить здесь

	except Exception as e:
		logger.error(f"Error translating expression '{kumir_expr}': {e}", exc_info=True)
		raise TranslationError(f"Ошибка трансляции выражения '{kumir_expr}': {e}")

	# Проверка на потенциально опасные конструкции, не пойманные заменами
	# (Очень базовый пример, можно улучшать)
	if '__' in python_expr:
		logger.warning(f"Potential dangerous construct '__' found in translated expr: '{python_expr}'")
	# Можно либо выбросить ошибку, либо просто залогировать
	# raise TranslationError("Потенциально небезопасная конструкция '__' в выражении.")

	logger.debug(f"Translation result: '{python_expr}'")
	return python_expr

# FILE END: kumir_expression_translator.py
