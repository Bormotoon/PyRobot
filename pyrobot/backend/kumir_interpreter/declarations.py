# FILE START: declarations.py
"""
Модуль declarations.py
@description Обработка объявлений переменных, присваиваний, ввода/вывода.
             Работает с новой структурой env и использует методы интерпретатора
             для разрешения ссылок и обновления значений.
"""
import logging
import math
import re
import sys

# Импортируем нужные исключения из нового файла
from .kumir_exceptions import (DeclarationError, AssignmentError, InputOutputError,
                               KumirInputRequiredError, KumirExecutionError, KumirEvalError)
from .constants import ALLOWED_TYPES, MAX_INT
from .file_functions import get_default_output
from .identifiers import is_valid_identifier
# Импортируем safe_eval только для использования, а не для исключений
from .safe_eval import safe_eval

logger = logging.getLogger('KumirDeclarations')


# Определения классов исключений УДАЛЕНЫ отсюда

# Функции get_default_value, _validate_and_convert_value, parse_dimensions остаются без изменений

def get_default_value(kumir_type):
	"""Возвращает значение по умолчанию для заданного типа Кумира."""
	base_type = kumir_type.replace('таб', '')
	if base_type == "цел": return 0
	if base_type == "вещ": return 0.0
	if base_type == "лог": return False
	if base_type == "сим": return ""
	if base_type == "лит": return ""
	if kumir_type.endswith("таб"): return {}
	logger.warning(f"Requesting default value for unknown type '{kumir_type}'. Returning None.")
	return None


def _validate_and_convert_value(value, target_type, var_name_for_error):
	"""
	Проверяет и конвертирует значение к целевому типу KUMIR.
	"""
	is_target_table = target_type.endswith("таб")
	base_target_type = target_type[:-3] if is_target_table else target_type

	if base_target_type not in ALLOWED_TYPES:
		raise TypeError(f"Неподдерживаемый целевой тип '{target_type}' для '{var_name_for_error}'")

	if value is None:
		raise AssignmentError(f"Попытка присвоить неопределенное значение (None) переменной '{var_name_for_error}'.")

	if is_target_table:
		if not isinstance(value, dict):
			raise AssignmentError(
				f"Попытка присвоить значение типа '{type(value).__name__}' таблице '{var_name_for_error}'. Ожидался словарь (dict)."
			)
		return value

	try:
		if base_target_type == "цел":
			try:
				f_val = float(value)
				if f_val != int(f_val):
					raise ValueError("Дробное число нельзя присвоить целой переменной")
				converted_value = int(f_val)
			except ValueError:
				converted_value = int(value)
			if not (-MAX_INT - 1 <= converted_value <= MAX_INT):
				raise ValueError(f"Значение {converted_value} выходит за допустимый диапазон для типа 'цел'.")
		elif base_target_type == "вещ":
			converted_value = float(value)
			if not math.isfinite(converted_value):
				raise ValueError(f"Значение {converted_value} не является конечным числом для типа 'вещ'.")
		elif base_target_type == "лог":
			if isinstance(value, bool):
				converted_value = value
			elif isinstance(value, str):
				low_val = value.lower().strip()
				if low_val in ["да", "true", "1"]:
					converted_value = True
				elif low_val in ["нет", "false", "0"]:
					converted_value = False
				else:
					try:
						converted_value = (float(value) != 0)
					except ValueError:
						raise ValueError(f"Недопустимое логическое значение: '{value}'. Ожидалось да/нет или число.")
			elif isinstance(value, (int, float)):
				converted_value = (value != 0)
			else:
				converted_value = bool(value)
		elif base_target_type == "сим":
			converted_value = str(value)
			if len(converted_value) != 1:
				raise ValueError("Значение для типа 'сим' должно быть ровно одним символом.")
		elif base_target_type == "лит":
			converted_value = str(value)
		else:
			raise TypeError(f"Неожиданный базовый тип: {base_target_type}")
		return converted_value
	except (ValueError, TypeError) as e:
		raise AssignmentError(
			f"Ошибка преобразования значения '{value}' ({type(value).__name__}) к типу '{target_type}' для '{var_name_for_error}': {e}"
		)
	except Exception as e:
		logger.exception(f"Неожиданная ошибка при конвертации значения для '{var_name_for_error}'")
		raise AssignmentError(f"Неожиданная ошибка при преобразовании значения для '{var_name_for_error}': {e}")


def parse_dimensions(dim_spec_str):
	"""Парсит строку размерностей таблицы вида "нач1:кон1, нач2:кон2, ..."."""
	dimensions = []
	if not dim_spec_str: return dimensions
	parts = re.split(r'\s*,\s*', dim_spec_str.strip())
	for i, part in enumerate(parts):
		if not part: continue
		match = re.match(r"^\s*(-?\d+)\s*:\s*(-?\d+)\s*$", part)
		if not match: raise DeclarationError(
			f"Некорректный формат размерности #{i + 1}: '{part}'. Ожидался формат 'целое:целое'.")
		try:
			start_bound = int(match.group(1));
			end_bound = int(match.group(2))
			if start_bound > end_bound:
				raise DeclarationError(
					f"Начальная граница ({start_bound}) размерности #{i + 1} больше конечной ({end_bound}).")
			dimensions.append((start_bound, end_bound))
		except ValueError:
			raise DeclarationError(f"Границы размерности #{i + 1} ('{part}') не являются целыми числами.")
	return dimensions


# process_declaration, process_assignment, split_respecting_quotes, process_output, process_input
# остаются без изменений в своей логике, но теперь используют импортированные исключения.

def process_declaration(line, env):
	"""
	Обрабатывает строку объявления переменной или таблицы.
	Создает запись в env с новой структурой ('kind', 'type', 'value', ...).
	"""
	logger.debug(f"Processing declaration: '{line}'")
	match = re.match(r"^\s*(\S+)(?:\s+(таб))?(?:\s+(.*))?$", line.strip(), re.IGNORECASE)
	if not match: raise DeclarationError(f"Некорректный синтаксис объявления: '{line}'")
	type_kw_raw, is_table_kw, rest_of_line = match.groups()
	type_kw = type_kw_raw.lower()
	is_table = bool(is_table_kw)
	if type_kw not in ALLOWED_TYPES: raise DeclarationError(f"Неизвестный тип переменной: '{type_kw_raw}'")
	if not rest_of_line: raise DeclarationError(f"Отсутствуют имена переменных после типа '{type_kw_raw}'.")
	identifiers_raw = [ident.strip() for ident in rest_of_line.split(",") if ident.strip()]
	if not identifiers_raw: raise DeclarationError(f"Не найдены имена переменных в строке объявления: '{line}'")
	declared_count = 0
	for ident_raw in identifiers_raw:
		var_name = ident_raw
		dimension_bounds = None
		if is_table:
			dim_match = re.match(r"^\s*(\S.*?)\s*\[\s*(.+?)\s*\]\s*$", ident_raw)
			if dim_match:
				var_name = dim_match.group(1).strip()
				dim_spec_str = dim_match.group(2).strip()
				try:
					dimension_bounds = parse_dimensions(dim_spec_str)
					if not dimension_bounds: raise DeclarationError(
						f"Не указаны корректные размерности для таблицы '{var_name}'.")
					logger.debug(f"Parsed dimensions for table '{var_name}': {dimension_bounds}")
				except DeclarationError as dim_err:
					raise DeclarationError(f"Ошибка в размерностях таблицы '{var_name}': {dim_err}")
			else:
				raise DeclarationError(f"Для таблицы '{ident_raw}' не указаны размерности в квадратных скобках.")
		elif "[" in ident_raw or "]" in ident_raw:
			raise DeclarationError(f"Неожиданные скобки '[]' в объявлении переменной (не таблицы): '{ident_raw}'")
		if not is_valid_identifier(var_name, ""): raise DeclarationError(
			f"Недопустимое имя переменной/таблицы: '{var_name}'")
		if var_name in env: raise DeclarationError(f"Переменная или таблица '{var_name}' уже объявлена.")
		env[var_name] = {"kind": "value", "type": type_kw, "is_table": is_table,
		                 "dimensions": dimension_bounds if is_table else None,
		                 "value": {} if is_table else get_default_value(type_kw)}
		declared_count += 1
		kind_str = "таблица" if is_table else "переменная";
		dim_str = f" с размерностями {dimension_bounds}" if is_table else ""
		logger.info(f"Declared {kind_str} '{var_name}' (base type '{type_kw}'{dim_str}).")
	return declared_count > 0


def process_assignment(line, interpreter):
	"""
	Обрабатывает строку присваивания (:=).
	Использует interpreter.update_variable_value для записи значения.
	"""
	logger.debug(f"Processing assignment: '{line}'")
	parts = line.split(":=", 1);
	if len(parts) != 2: raise AssignmentError(f"Неверный синтаксис присваивания (ожидалось :=): {line}")
	left_raw = parts[0].strip()
	right_expr = parts[1].strip()
	if not left_raw: raise AssignmentError("Отсутствует переменная слева от ':='.")
	if not right_expr: raise AssignmentError("Отсутствует выражение справа от ':='.")
	try:
		# Передаем текущее окружение и интерпретатор в safe_eval
		current_env = interpreter.get_env_by_index(interpreter.get_current_env_index())
		rhs_value = safe_eval(right_expr, current_env, interpreter.robot, interpreter)
		logger.debug(f"Evaluated RHS '{right_expr}' -> {rhs_value} (type: {type(rhs_value)})")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления правой части присваивания ('{right_expr}'): {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating RHS '{right_expr}': {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка при вычислении '{right_expr}': {e}")

	target_var_name = left_raw
	indices = None
	table_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", left_raw)
	if table_match:
		target_var_name = table_match.group(1).strip()
		indices_expr_str = table_match.group(2).strip()
		logger.debug(f"Assignment target is table element: '{target_var_name}', indices expr: '{indices_expr_str}'")
		index_tokens = split_respecting_quotes(indices_expr_str, delimiter=',', quote_char='"')
		if not index_tokens: raise AssignmentError(f"Не указаны индексы для таблицы '{target_var_name}'.")
		evaluated_indices = []
		try:
			current_env = interpreter.get_env_by_index(interpreter.get_current_env_index())
			for token in index_tokens:
				idx_val = safe_eval(token.strip(), current_env, interpreter.robot, interpreter)
				try:
					evaluated_indices.append(int(idx_val))
				except (ValueError, TypeError):
					raise KumirEvalError(f"Индекс '{token}' (= {idx_val}) не является целым числом.")
			indices = tuple(evaluated_indices)
			logger.debug(f"Evaluated indices: {indices}")
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления индексов '{indices_expr_str}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating indices '{indices_expr_str}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка при вычислении индексов: {e}")
	else:
		logger.debug(f"Assignment target is simple variable: '{target_var_name}'")
		if not is_valid_identifier(target_var_name, ""): raise AssignmentError(
			f"Недопустимое имя переменной слева от ':=': '{target_var_name}'")

	try:
		interpreter.update_variable_value(target_var_name, rhs_value, indices)
		logger.info(
			f"Assigned value {rhs_value} to '{target_var_name}'{f' with indices {indices}' if indices else ''}.")
	except (KumirExecutionError, AssignmentError, DeclarationError) as e:
		raise e
	except Exception as e:
		logger.exception(f"Unexpected error during variable update for '{target_var_name}'")
		raise KumirExecutionError(f"Неожиданная ошибка присваивания переменной '{target_var_name}': {e}")


def split_respecting_quotes(text, delimiter=',', quote_char='"'):
	"""Разделяет строку по разделителю, игнорируя разделители внутри кавычек."""
	parts = [];
	current_part = "";
	in_quotes = False;
	escape = False
	for char in text:
		if char == quote_char and not escape:
			in_quotes = not in_quotes;
			current_part += char
		elif char == delimiter and not in_quotes:
			parts.append(current_part.strip());
			current_part = ""
		else:
			current_part += char
		escape = (char == '\\' and not escape)
	parts.append(current_part.strip())
	return parts


def process_output(line, interpreter):
	""" Обрабатывает команду 'вывод'. """
	logger.debug(f"Processing output: '{line}'")
	content_part = line[len("вывод"):].strip();
	append_newline = True
	if content_part.lower().endswith(" нс"):
		content_part = content_part[:-len(" нс")].rstrip();
		append_newline = False
	elif content_part.lower() == "нс":
		content_part = ""; append_newline = False
	output_str_parts = []
	if content_part:
		parts_to_eval = split_respecting_quotes(content_part, delimiter=',', quote_char='"')
		logger.debug(f"Output parts to evaluate: {parts_to_eval}")
		for part_expr in parts_to_eval:
			part_expr_strip = part_expr
			try:
				current_env = interpreter.get_env_by_index(interpreter.get_current_env_index())
				value = safe_eval(part_expr_strip, current_env, interpreter.robot, interpreter)
				if isinstance(value, bool):
					output_str_parts.append("да" if value else "нет")
				elif value is None:
					output_str_parts.append("")
				else:
					output_str_parts.append(str(value))
				logger.debug(f"Evaluated output part '{part_expr_strip}' -> '{output_str_parts[-1]}'")
			except KumirEvalError as e:
				logger.error(f"Error evaluating output part '{part_expr_strip}': {e}")
				raise InputOutputError(f"Ошибка вычисления '{part_expr_strip}' в 'вывод': {e}")
			except Exception as e:
				logger.exception(f"Unexpected error evaluating output part '{part_expr_strip}'")
				raise InputOutputError(f"Неожиданная ошибка в 'вывод' для '{part_expr_strip}': {e}")
	output_str = "".join(output_str_parts)
	if append_newline: output_str += "\n"
	if not hasattr(interpreter, 'output') or interpreter.output is None: interpreter.output = ""
	interpreter.output += output_str;
	output_str_escaped = output_str.replace('\n', '\\n').replace('\r', '\\r')
	logger.info(f"Appended to output buffer: '{output_str_escaped}'")


def process_input(line, interpreter):
	""" Обрабатывает команду 'ввод'. """
	logger.debug(f"Processing 'ввод': '{line}'.")
	var_name_raw = line[len("ввод"):].strip()
	if not var_name_raw: raise InputOutputError("Отсутствует имя переменной после 'ввод'.")
	var_name = var_name_raw;
	indices = None
	if '[' in var_name_raw:
		table_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", var_name_raw)
		if table_match:
			var_name = table_match.group(1).strip()
			indices_expr_str = table_match.group(2).strip()
			logger.warning(
				f"Input for table element '{var_name}[{indices_expr_str}]' requested, but not fully supported yet. Evaluating indices...")
			index_tokens = split_respecting_quotes(indices_expr_str, delimiter=',', quote_char='"')
			if not index_tokens: raise AssignmentError(f"Не указаны индексы для таблицы '{var_name}'.")
			evaluated_indices = []
			try:
				current_env = interpreter.get_env_by_index(interpreter.get_current_env_index())
				for token in index_tokens:
					idx_val = safe_eval(token.strip(), current_env, interpreter.robot, interpreter)
					try:
						evaluated_indices.append(int(idx_val))
					except (ValueError, TypeError):
						raise KumirEvalError(f"Индекс '{token}' (= {idx_val}) не является целым числом.")
				indices = tuple(evaluated_indices)
				logger.debug(f"Evaluated indices for input: {indices}")
			except KumirEvalError as e:
				raise InputOutputError(f"Ошибка вычисления индексов '{indices_expr_str}' в 'ввод': {e}")
			except Exception as e:
				raise InputOutputError(f"Неожиданная ошибка при вычислении индексов в 'ввод': {e}")
		else:
			raise InputOutputError(f"Некорректный синтаксис для ввода элемента таблицы: '{var_name_raw}'")
	if not is_valid_identifier(var_name, ""): raise InputOutputError(
		f"Недопустимое имя переменной для ввода: '{var_name}'")
	var_info = interpreter.get_variable_info(var_name)
	if var_info is None: raise DeclarationError(f"Переменная '{var_name}' не объявлена перед использованием в 'ввод'.")
	if var_info.get("is_table") and indices is None: raise InputOutputError(
		f"Команда 'ввод' не поддерживается для целых таблиц ('{var_name}'). Введите элемент таблицы.")
	target_type = var_info["type"]
	prompt = f"Введите значение для '{var_name_raw}' (тип: {target_type}): "
	logger.info(f"Input required for variable '{var_name_raw}' (type: {target_type}). Raising exception.")
	raise KumirInputRequiredError(var_name=var_name, prompt=prompt, target_type=target_type)

# FILE END: declarations.py