# FILE START: preprocessing.py
"""
Модуль preprocessing.py
@description Выполняет предварительную обработку исходного кода программы на языке KUMIR.
Удаляет комментарии, пустые строки, обрабатывает точки с запятой и разделяет код на секции.
"""
import logging
import re

# Импортируем типы для валидации
from .declarations import ALLOWED_TYPES  # Используем ALLOWED_TYPES для проверки типов параметров
from .identifiers import is_valid_identifier  # Для проверки имен параметров

logger = logging.getLogger('KumirPreprocessing')


# Функция preprocess_code остается без изменений
def preprocess_code(code):
	"""
	Выполняет предварительную обработку кода KUMIR:
	- Удаляет комментарии (| или # до конца строки).
	- Удаляет пустые строки и лишние пробелы.
	- Обрабатывает точки с запятой (;) как разделители команд.
	- Пропускает строку "использовать робот".

	Args:
		code (str): Исходный код программы.

	Returns:
		list: Список строк кода, готовых к дальнейшему разбору.
	"""
	# ... (код без изменений) ...
	lines = []
	logger.debug("Starting code preprocessing...")
	line_number = 0
	for original_line in code.splitlines():
		line_number += 1
		line = re.sub(r"[|#].*", "", original_line).strip()
		if not line: continue
		if line.lower() == "использовать робот":
			logger.debug(f"Skipping 'использовать робот' on line {line_number}")
			continue
		parts = []
		current_part = ''
		in_quotes = False
		quote_char = ''
		for char in line:
			if char in ('"', "'") and (not in_quotes or char == quote_char):
				in_quotes = not in_quotes
				quote_char = char if in_quotes else ''
			if char == ';' and not in_quotes:
				stripped_part = current_part.strip()
				if stripped_part: parts.append(stripped_part)
				current_part = ''
			else:
				current_part += char
		stripped_part = current_part.strip()
		if stripped_part: parts.append(stripped_part)
		if not parts: continue
		lines.extend(parts)
		logger.debug(f"Line {line_number} processed into: {parts}")
	logger.info(f"Preprocessing finished. Total lines for parsing: {len(lines)}")
	return lines


# Функция separate_sections остается без изменений
def separate_sections(lines):
	"""
	Разделяет предварительно обработанные строки кода на:
	- Вступительную часть (до первого 'алг').
	- Список секций алгоритмов (каждая с заголовком и телом).

	Args:
		lines (list): Список строк кода после preprocess_code.

	Returns:
		tuple: (introduction: list, algorithms: list)
		       algorithms - список словарей {'header': str, 'body': list}

	Raises:
		SyntaxError: При структурных ошибках ('нач' без 'алг', 'кон' без 'нач').
	"""
	# ... (код без изменений) ...
	introduction = []
	algorithms = []
	current_algo_dict = None
	in_algo_body = False
	current_line_index = 0
	logger.debug("Separating code into introduction and algorithms...")
	for line in lines:
		current_line_index += 1
		lower_line = line.lower()
		if lower_line.startswith("алг"):
			if current_algo_dict is not None:
				if in_algo_body:
					raise SyntaxError(
						f"Структурная ошибка: отсутствует 'кон' для алгоритма, начинающегося с '{current_algo_dict['header']}' перед строкой {current_line_index}.")
				logger.debug(
					f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
				algorithms.append(current_algo_dict)
			current_algo_dict = {"header": line, "body": []}
			in_algo_body = False
			logger.debug(f"Detected algorithm start at line {current_line_index}: '{line}'")
		elif lower_line == "нач":
			if current_algo_dict is None: raise SyntaxError(
				f"Структурная ошибка: 'нач' найден вне блока 'алг' (строка {current_line_index}).")
			if in_algo_body: raise SyntaxError(
				f"Структурная ошибка: повторный 'нач' внутри блока алгоритма (строка {current_line_index}).")
			in_algo_body = True
			logger.debug(
				f"Entering algorithm body ('нач') for '{current_algo_dict.get('header', '')}' at line {current_line_index}.")
		elif lower_line == "кон":
			if current_algo_dict is None or not in_algo_body: raise SyntaxError(
				f"Структурная ошибка: 'кон' найден без соответствующего 'нач' или вне блока 'алг' (строка {current_line_index}).")
			in_algo_body = False
			logger.debug(
				f"Exiting algorithm body ('кон') for '{current_algo_dict.get('header', '')}' at line {current_line_index}.")
			logger.debug(
				f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
			algorithms.append(current_algo_dict)
			current_algo_dict = None
		else:
			if current_algo_dict is None:
				introduction.append(line)
			else:
				if in_algo_body:
					current_algo_dict["body"].append(line)
				else:
					# Склеиваем строки заголовка до 'нач'
					current_algo_dict["header"] += " " + line
					logger.debug(f"Appending to header: '{line}'")

	if current_algo_dict is not None:
		if in_algo_body: raise SyntaxError(
			f"Структурная ошибка: отсутствует 'кон' для последнего алгоритма, начинающегося с '{current_algo_dict['header']}'.")
		logger.warning(f"Последний блок 'алг' ('{current_algo_dict['header']}') не содержит 'нач'/'кон'.")
		algorithms.append(current_algo_dict)
	logger.info(
		f"Section separation complete. Introduction lines: {len(introduction)}, Algorithms found: {len(algorithms)}")
	return introduction, algorithms


# --- НОВАЯ, УЛУЧШЕННАЯ ВЕРСИЯ parse_algorithm_header ---
def parse_algorithm_header(header_line):
	"""
	Разбирает строку заголовка алгоритма ('алг тип имя (параметры)')
	на имя, тип возвращаемого значения (если есть) и список параметров.

	Args:
		header_line (str): Полная строка заголовка (включая 'алг').

	Returns:
		dict: Словарь с ключами:
			  'raw' (str): Исходная строка заголовка (без 'алг').
			  'name' (str | None): Имя алгоритма или None.
			  'return_type' (str | None): Тип возвращаемого значения (цел, вещ...) или None.
			  'params' (list): Список словарей параметров:
							   [{'mode': str, 'type': str, 'name': str, 'is_table': bool}]
							   mode: 'арг', 'рез', 'аргрез', 'знач'
	Raises:
		ValueError: при синтаксических ошибках в заголовке.
	"""
	logger.debug(f"Parsing algorithm header: '{header_line}'")
	header_strip = header_line.strip()
	if not header_strip.lower().startswith("алг"):
		raise ValueError(f"Заголовок '{header_line}' не начинается с 'алг'.")

	content = header_strip[len("алг"):].strip()
	raw_header_content = content

	return_type = None
	name_part = content
	params_part_str = None
	params = []

	# 1. Проверка на наличие типа возвращаемого значения перед именем
	potential_type_match = re.match(r"^(\w+)\s+(.*)", content)
	if potential_type_match:
		potential_type = potential_type_match.group(1).lower()
		if potential_type in ALLOWED_TYPES:
			return_type = potential_type
			content = potential_type_match.group(2).strip()  # Оставшаяся часть для имени и параметров
			name_part = content  # Переопределяем часть с именем
			logger.debug(f"Detected return type: '{return_type}'")

	# 2. Разделение на имя и параметры в скобках
	params_match = re.match(r"^(.*?)\s*\((.*)\)\s*$", content)
	if params_match:
		name_part = params_match.group(1).strip()
		params_part_str = params_match.group(2).strip()
	elif "(" in content or ")" in content:
		# Непарные скобки или не в конце
		raise ValueError(f"Некорректный формат скобок в заголовке: '{content}'")
	else:
		# Нет скобок, значит нет параметров
		name_part = content.strip()
		params_part_str = None

	# 3. Получение имени алгоритма
	# Имя может отсутствовать, если это основной блок `алг нач кон`
	algo_name = name_part if name_part else None
	if algo_name and not is_valid_identifier(algo_name, ""):  # Проверяем валидность имени
		raise ValueError(f"Недопустимое имя алгоритма: '{algo_name}'")

	logger.debug(f"Algorithm name: '{algo_name}'")

	# 4. Парсинг параметров, если они есть
	if params_part_str:
		logger.debug(f"Parsing parameters string: '{params_part_str}'")
		# Разделяем параметры по ';' (точка с запятой)
		param_sections = [p.strip() for p in params_part_str.split(';') if p.strip()]

		for section in param_sections:
			parts = section.split()
			if not parts: continue

			mode = parts[0].lower()
			if mode not in ["арг", "рез", "аргрез", "знач"]:
				# Если первое слово не режим, считаем, что это тип (режим по умолчанию 'арг')
				mode = "арг"
				current_index = 0
			else:
				# Первое слово - режим, сдвигаем индекс
				current_index = 1

			if current_index >= len(parts):
				raise ValueError(f"Неполное определение параметра в секции: '{section}' (отсутствует тип/имя)")

			# Следующее слово - тип или 'таб'
			type_part = parts[current_index].lower()
			current_index += 1
			is_table = False

			if type_part == "таб":
				is_table = True
				if current_index >= len(parts):
					raise ValueError(
						f"Неполное определение параметра в секции: '{section}' (отсутствует тип после 'таб')")
				type_part = parts[current_index].lower()  # Берем тип после 'таб'
				current_index += 1

			# Проверяем тип
			if type_part not in ALLOWED_TYPES:
				raise ValueError(f"Неизвестный тип параметра '{type_part}' в секции: '{section}'")
			param_type = type_part

			# Остальные слова в секции - имена переменных через запятую
			if current_index >= len(parts):
				raise ValueError(f"Отсутствуют имена параметров после типа '{param_type}' в секции: '{section}'")

			# Собираем имена, удаляя запятые
			names_str = " ".join(parts[current_index:])
			param_names = [name.strip() for name in names_str.split(',') if name.strip()]

			if not param_names:
				raise ValueError(f"Не найдены имена параметров в секции: '{section}'")

			# Добавляем каждый параметр в список
			for p_name in param_names:
				if not is_valid_identifier(p_name, param_type):
					raise ValueError(f"Недопустимое имя параметра '{p_name}' в секции: '{section}'")
				params.append({
					"mode": mode,
					"type": param_type,
					"name": p_name,
					"is_table": is_table
				})
				logger.debug(f"Parsed param: mode={mode}, type={param_type}, name={p_name}, is_table={is_table}")

	header_info = {
		"raw": raw_header_content,
		"name": algo_name,
		"return_type": return_type,
		"params": params
	}
	logger.debug(f"Header parsed successfully: {header_info}")
	return header_info

# FILE END: preprocessing.py
