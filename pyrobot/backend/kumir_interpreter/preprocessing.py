"""
Модуль preprocessing.py
@description Выполняет предварительную обработку исходного кода программы на языке KUMIR.
Удаляет комментарии, пустые строки, обрабатывает точки с запятой и разделяет код на секции.
"""
import logging
import re

logger = logging.getLogger('KumirPreprocessing')


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
	lines = []
	logger.debug("Starting code preprocessing...")
	line_number = 0
	for original_line in code.splitlines():
		line_number += 1
		# Удаляем комментарии (все после | или #)
		line = re.sub(r"[|#].*", "", original_line).strip()

		# Пропускаем пустые строки
		if not line:
			continue

		# Пропускаем "использовать робот" (без учета регистра)
		if line.lower() == "использовать робот":
			logger.debug(f"Skipping 'использовать робот' on line {line_number}")
			continue

		# Разделяем строку по ';' как разделителю команд
		# Учитываем, что ; может быть внутри строкового литерала (упрощенно)
		# TODO: Более надежный парсинг с учетом строковых литералов
		parts = []
		current_part = ''
		in_quotes = False
		for char in line:
			if char == '"':
				in_quotes = not in_quotes
			if char == ';' and not in_quotes:
				stripped_part = current_part.strip()
				if stripped_part:
					parts.append(stripped_part)
				current_part = ''
			else:
				current_part += char

		# Добавляем последнюю часть, если она не пустая
		stripped_part = current_part.strip()
		if stripped_part:
			parts.append(stripped_part)

		if not parts:  # Если строка состояла только из ;
			continue

		# Добавляем обработанные части в общий список строк
		lines.extend(parts)
		logger.debug(f"Line {line_number} processed into: {parts}")

	logger.info(f"Preprocessing finished. Total lines for parsing: {len(lines)}")
	return lines


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
	introduction = []
	algorithms = []
	current_algo_dict = None  # Словарь для текущего собираемого алгоритма
	in_algo_body = False  # Флаг: находимся ли между 'нач' и 'кон'
	current_line_index = 0

	logger.debug("Separating code into introduction and algorithms...")

	for line in lines:
		current_line_index += 1
		lower_line = line.lower()

		if lower_line.startswith("алг"):
			# Завершаем предыдущий алгоритм, если он был
			if current_algo_dict is not None:
				if in_algo_body:
					# Ошибка: начался новый алг, но предыдущий не закрыт 'кон'
					raise SyntaxError(
						f"Структурная ошибка: отсутствует 'кон' для алгоритма, начинающегося с '{current_algo_dict['header']}' перед строкой {current_line_index}.")
				logger.debug(
					f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
				algorithms.append(current_algo_dict)

			# Начинаем новый алгоритм
			current_algo_dict = {"header": line, "body": []}
			in_algo_body = False
			logger.debug(f"Detected algorithm start at line {current_line_index}: '{line}'")

		elif lower_line == "нач":
			if current_algo_dict is None:
				raise SyntaxError(f"Структурная ошибка: 'нач' найден вне блока 'алг' (строка {current_line_index}).")
			if in_algo_body:
				raise SyntaxError(
					f"Структурная ошибка: повторный 'нач' внутри блока алгоритма (строка {current_line_index}).")
			in_algo_body = True
			logger.debug(
				f"Entering algorithm body ('нач') for '{current_algo_dict['header']}' at line {current_line_index}.")

		elif lower_line == "кон":
			if current_algo_dict is None or not in_algo_body:
				raise SyntaxError(
					f"Структурная ошибка: 'кон' найден без соответствующего 'нач' или вне блока 'алг' (строка {current_line_index}).")
			in_algo_body = False
			logger.debug(
				f"Exiting algorithm body ('кон') for '{current_algo_dict['header']}' at line {current_line_index}.")
			# Алгоритм полностью собран, добавим его в список и сбросим current_algo_dict
			logger.debug(
				f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
			algorithms.append(current_algo_dict)
			current_algo_dict = None  # Готовы к новому алг или к концу файла

		else:
			# Строка не является ключевым словом структуры
			if current_algo_dict is None:
				# Еще не начался ни один алгоритм - это вступление
				introduction.append(line)
			else:
				if in_algo_body:
					# Находимся внутри тела алгоритма ('нач' ... 'кон')
					current_algo_dict["body"].append(line)
				else:
					# Строка между 'алг' и 'нач' - часть заголовка (например, параметры)
					# Объединяем с предыдущей строкой заголовка через пробел
					current_algo_dict["header"] += " " + line
					logger.debug(f"Appending to header: '{line}'")

	# Проверяем, не остался ли незавершенный алгоритм в конце файла
	if current_algo_dict is not None:
		if in_algo_body:
			raise SyntaxError(
				f"Структурная ошибка: отсутствует 'кон' для последнего алгоритма, начинающегося с '{current_algo_dict['header']}'.")
		# Если был алг, но не было нач/кон - это странно, но может быть пустым?
		logger.warning(f"Последний блок 'алг' ('{current_algo_dict['header']}') не содержит 'нач'/'кон'.")
		# Решаем, добавлять ли такой "пустой" алгоритм
		algorithms.append(current_algo_dict)  # Добавим, но он, вероятно, вызовет ошибку при выполнении

	logger.info(
		f"Section separation complete. Introduction lines: {len(introduction)}, Algorithms found: {len(algorithms)}")
	return introduction, algorithms


def parse_algorithm_header(header_line):
	"""
	Разбирает строку заголовка алгоритма ('алг имя (параметры)')
	на имя и список параметров.

	Args:
		header_line (str): Полная строка заголовка (включая 'алг').

	Returns:
		dict: Словарь с ключами:
		      'raw' (str): Исходная строка заголовка (без 'алг').
		      'name' (str | None): Имя алгоритма или None, если имя отсутствует.
		      'params' (list): Список кортежей параметров (mode, type, name).
	                            mode: 'арг', 'рез', 'аргрез', 'знач' (пока только 'арг')
	                            type: 'цел', 'вещ', 'лог', 'сим', 'лит'
	                            name: имя параметра
	Raises:
	    ValueError: при синтаксических ошибках в заголовке.
	"""
	logger.debug(f"Parsing algorithm header: '{header_line}'")
	header_strip = header_line.strip()
	if not header_strip.lower().startswith("алг"):
		raise ValueError(f"Заголовок '{header_line}' не начинается с 'алг'.")

	# Удаляем 'алг' и лишние пробелы
	content = header_strip[3:].strip()
	raw_header_content = content  # Сохраняем для словаря результата

	params = []
	name_part = content  # По умолчанию всё после 'алг' - это имя
	params_part = None

	# Проверяем наличие и извлекаем параметры в скобках
	if "(" in content and content.endswith(")"):
		match = re.match(r"^(.*?)\s*\((.*)\)$", content)
		if match:
			name_part = match.group(1).strip()
			params_part = match.group(2).strip()
		else:
			# Скобки есть, но формат не совпадает - возможно, ошибка
			raise ValueError(f"Некорректный формат скобок в заголовке: '{content}'")
	elif "(" in content or ")" in content:
		# Одиночные скобки или неправильное расположение
		raise ValueError(f"Непарные или некорректно расположенные скобки в заголовке: '{content}'")

	algo_name = name_part if name_part else None  # Имя может отсутствовать у основного алгоритма

	# Парсим строку параметров, если она есть
	if params_part:
		logger.debug(f"Parsing parameters: '{params_part}'")
		# Упрощенный парсинг параметров - разделяем по запятой
		# TODO: Более сложный парсинг с учетом режимов (арг/рез/знач) и типов
		param_defs = [p.strip() for p in params_part.split(',') if p.strip()]
		current_mode = 'арг'  # Режим по умолчанию
		current_type = None

		for param_def in param_defs:
			# Очень упрощенно: считаем первое слово типом, второе именем
			parts = param_def.split(None, 1)  # Split on first whitespace
			if len(parts) == 2:
				p_type = parts[0].lower()
				p_name = parts[1]
				# TODO: Validate p_type against ALLOWED_TYPES
				# TODO: Validate p_name using is_valid_identifier
				params.append((current_mode, p_type, p_name))
				logger.debug(f"Parsed param: mode={current_mode}, type={p_type}, name={p_name}")
			elif len(parts) == 1:
				# Возможно только имя, если тип был указан ранее? Или ошибка?
				# TODO: Implement full parameter parsing logic based on Kumir spec
				logger.warning(f"Parameter definition '{param_def}' seems incomplete.")
				raise ValueError(f"Неполное определение параметра: '{param_def}'. Ожидался тип и имя.")
			else:
				raise ValueError(f"Некорректное определение параметра: '{param_def}'.")

	header_info = {"raw": raw_header_content, "name": algo_name, "params": params}
	logger.debug(f"Header parsed: Name='{algo_name}', Params={params}")
	return header_info
