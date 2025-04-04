# FILE START: preprocessing.py
"""
Модуль preprocessing.py
@description Выполняет предварительную обработку исходного кода программы на языке KUMIR.
Удаляет комментарии, пустые строки, обрабатывает точки с запятой как разделители команд
(с учетом строковых литералов) и разделяет код на секции.
"""
import logging
import re

from .constants import ALLOWED_TYPES
from .identifiers import is_valid_identifier

logger = logging.getLogger('KumirPreprocessing')


def split_respecting_quotes(text, delimiter=';', quote_char='"'):
	"""Разделяет строку по разделителю, игнорируя разделители внутри кавычек."""
	parts = [];
	current_part = "";
	in_quotes = False;
	escape = False
	for char in text:
		if char == quote_char and not escape:
			in_quotes = not in_quotes; current_part += char
		elif char == delimiter and not in_quotes:
			stripped_part = current_part.strip();
			if stripped_part: parts.append(stripped_part)
			current_part = ""
		else:
			current_part += char
		escape = (char == '\\' and not escape)
	stripped_part = current_part.strip()
	if stripped_part: parts.append(stripped_part)
	return parts


def preprocess_code(code):
	"""Выполняет предварительную обработку кода KUMIR."""
	processed_lines = [];
	logger.debug("Starting code preprocessing...");
	line_number = 0
	for original_line in code.splitlines():
		line_number += 1;
		line_no_comments = re.sub(r"[|#].*", "", original_line).strip()
		if not line_no_comments: continue
		commands = split_respecting_quotes(line_no_comments, delimiter=';', quote_char='"')
		if len(commands) > 1:
			logger.debug(f"Line {line_number} split by ';' into: {commands}")
		elif commands:
			logger.debug(f"Line {line_number} processed into: ['{commands[0]}']")
		processed_lines.extend(commands)
	logger.info(f"Preprocessing finished. Total commands/lines for parsing: {len(processed_lines)}")
	return processed_lines


def separate_sections(lines):
	"""Разделяет предварительно обработанные строки кода на вступление и алгоритмы."""
	introduction = [];
	algorithms = [];
	current_algo_dict = None;
	in_algo_body = False;
	current_line_index = 0
	logger.debug("Separating code into introduction and algorithms...")
	for line in lines:
		current_line_index += 1;
		lower_line = line.lower()
		if lower_line.startswith("алг"):
			if current_algo_dict is not None:
				if in_algo_body: raise SyntaxError(
					f"Структурная ошибка: отсутствует 'кон' для алгоритма '{current_algo_dict['header']}' перед строкой {current_line_index}.")
				logger.debug(
					f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
				algorithms.append(current_algo_dict)
			current_algo_dict = {"header": line, "body": []};
			in_algo_body = False
			logger.debug(f"Detected algorithm start at line {current_line_index}: '{line}'")
		elif lower_line == "нач":
			if current_algo_dict is None: raise SyntaxError(
				f"Структурная ошибка: 'нач' найден вне блока 'алг' (строка {current_line_index}).")
			if in_algo_body: raise SyntaxError(
				f"Структурная ошибка: повторный 'нач' внутри блока алгоритма (строка {current_line_index}).")
			in_algo_body = True;
			logger.debug(
				f"Entering algorithm body ('нач') for '{current_algo_dict['header']}' at line {current_line_index}.")
		elif lower_line == "кон":
			if current_algo_dict is None or not in_algo_body: raise SyntaxError(
				f"Структурная ошибка: 'кон' найден без соответствующего 'нач' или вне блока 'алг' (строка {current_line_index}).")
			in_algo_body = False;
			logger.debug(
				f"Exiting algorithm body ('кон') for '{current_algo_dict['header']}' at line {current_line_index}.")
			logger.debug(
				f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
			algorithms.append(current_algo_dict);
			current_algo_dict = None
		else:
			if current_algo_dict is None:
				introduction.append(line)
			else:
				if in_algo_body:
					current_algo_dict["body"].append(line)
				else:  # Строка между 'алг' и 'нач'
					if line.strip():  # Игнорируем пустые строки
						# Считаем это частью заголовка (для многострочных сигнатур)
						logger.debug(f"Appending to header: '{line}' (at index {current_line_index}).")
						current_algo_dict["header"] += " " + line
	if current_algo_dict is not None:
		if in_algo_body: raise SyntaxError(
			f"Структурная ошибка: отсутствует 'кон' для последнего алгоритма '{current_algo_dict['header']}'.")
		logger.warning(
			f"Last 'алг' block ('{current_algo_dict['header']}') might be incomplete (missing 'нач'/'кон' or empty body).")
		algorithms.append(current_algo_dict)
	logger.info(
		f"Section separation complete. Introduction lines: {len(introduction)}, Algorithms found: {len(algorithms)}")
	return introduction, algorithms


def parse_algorithm_header(header_line):
	"""Разбирает заголовок алгоритма с параметрами."""
	logger.debug(f"Parsing algorithm header: '{header_line}'")
	header_strip = header_line.strip()
	if not header_strip.lower().startswith("алг"): raise ValueError(f"Заголовок '{header_line}' не начинается с 'алг'.")
	content = header_strip[len("алг"):].strip();
	raw_header_content = content
	params = [];
	name_part = content;
	params_part_str = None
	param_match = re.match(r"^(.*?)\s*\((.*)\)\s*$", content)
	if param_match:
		name_part = param_match.group(1).strip(); params_part_str = param_match.group(2).strip(); logger.debug(
			f"Header has name='{name_part}', params='{params_part_str}'")
	elif "(" in content or ")" in content:
		raise ValueError(f"Некорректный формат скобок в заголовке: '{content}'")
	else:
		name_part = content.strip(); logger.debug(f"Header has name='{name_part}', no parameters.")
	algo_name = name_part if name_part else None
	if algo_name and not is_valid_identifier(algo_name, ""):
		raise ValueError(f"Недопустимое имя алгоритма: '{algo_name}'")
	elif not algo_name:
		logger.debug("Algorithm is unnamed (likely main).")

	if params_part_str:
		segments = [seg.strip() for seg in params_part_str.split(';') if seg.strip()]
		if not segments: logger.warning(f"Parameter brackets empty: '({params_part_str})'")
		for segment in segments:
			logger.debug(f"Parsing parameter segment: '{segment}'")
			segment_parts = segment.split();
			if not segment_parts: continue
			current_mode = "арг";
			part_index = 0
			first_word_lower = segment_parts[0].lower()
			if first_word_lower in ["арг", "рез", "аргрез", "знач"]:
				current_mode = first_word_lower; part_index += 1; logger.debug(f"Mode detected: '{current_mode}'")
			elif first_word_lower in ALLOWED_TYPES or first_word_lower.endswith("таб"):
				logger.debug(f"Mode not specified, defaulting to 'арг'.")
			else:
				raise ValueError(f"Неожиданное начало сегмента параметра: '{segment_parts[0]}' в '{segment}'.")
			if part_index >= len(segment_parts): raise ValueError(f"Отсутствует тип параметра в сегменте: '{segment}'")
			current_type = segment_parts[part_index].lower();
			part_index += 1
			is_table_type = current_type.endswith("таб")
			base_type = current_type[:-3] if is_table_type else current_type
			# --->>> УЛУЧШЕННАЯ ВАЛИДАЦИЯ ТИПА <<<---
			valid_type = False
			if is_table_type:
				if base_type in ALLOWED_TYPES: valid_type = True
			elif current_type in ALLOWED_TYPES:
				valid_type = True
			if not valid_type: raise ValueError(
				f"Неизвестный или некорректный тип параметра: '{current_type}' в сегменте '{segment}'")
			# --- <<< КОНЕЦ УЛУЧШЕНИЯ >>> ---
			logger.debug(f"Type detected: '{current_type}' (table={is_table_type})")
			if part_index >= len(segment_parts): raise ValueError(
				f"Отсутствуют имена параметров после типа '{current_type}' в '{segment}'")
			names_str = " ".join(segment_parts[part_index:])
			param_names = [name.strip() for name in names_str.split(',') if name.strip()]
			if not param_names: raise ValueError(f"Не найдены имена параметров в сегменте: '{segment}'")
			for p_name in param_names:
				if not is_valid_identifier(p_name, base_type): raise ValueError(
					f"Недопустимое имя параметра: '{p_name}' в '{segment}'")
				params.append((current_mode, current_type, p_name))
				logger.debug(f"Parsed param: mode={current_mode}, type={current_type}, name={p_name}")

	header_info = {"raw": raw_header_content, "name": algo_name, "params": params}
	logger.debug(f"Header parsed successfully: Name='{algo_name}', Params Count={len(params)}")
	return header_info

# FILE END: preprocessing.py
