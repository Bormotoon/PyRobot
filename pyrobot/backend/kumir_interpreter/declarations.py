# FILE START: declarations.py
"""
Модуль declarations.py
@description Обработка объявлений переменных, присваиваний, ввода/вывода.
"""
import logging
import math
import re
import sys

from .constants import ALLOWED_TYPES, MAX_INT
from .file_functions import get_default_output
from .identifiers import is_valid_identifier
from .safe_eval import safe_eval, KumirEvalError

logger = logging.getLogger('KumirDeclarations')


class DeclarationError(Exception): pass


class AssignmentError(Exception): pass


class InputOutputError(Exception): pass


class KumirInputRequiredError(Exception):
	def __init__(self, var_name, prompt, target_type):
		self.var_name = var_name;
		self.prompt = prompt;
		self.target_type = target_type
		message = f"Требуется ввод для переменной '{var_name}' (тип: {target_type}). Подсказка: {prompt}"
		super().__init__(message)


# --->>> НОВАЯ ФУНКЦИЯ <<<---
def get_default_value(kumir_type):
	"""Возвращает значение по умолчанию для заданного типа Кумира."""
	base_type = kumir_type.replace('таб', '')  # Убираем суффикс таблицы
	if base_type == "цел": return 0
	if base_type == "вещ": return 0.0
	if base_type == "лог": return False  # "нет"
	if base_type == "сим": return ""  # Или может быть пробел? Кумир неявно может инициализировать
	if base_type == "лит": return ""
	# Для таблиц возвращаем пустой словарь (их значение по умолчанию)
	if kumir_type.endswith("таб"): return {}
	logger.warning(f"Requesting default value for unknown type '{kumir_type}'. Returning None.")
	return None


# --- <<< КОНЕЦ НОВОЙ ФУНКЦИИ >>> ---

def _validate_and_convert_value(value, target_type, var_name_for_error):
	"""Проверяет и конвертирует значение к целевому типу KUMIR."""
	# Добавляем обработку для табличных типов - конвертируем в словарь, если это возможно
	is_target_table = target_type.endswith("таб")
	base_target_type = target_type[:-3] if is_target_table else target_type

	if base_target_type not in ALLOWED_TYPES:
		raise TypeError(f"Неподдерживаемый целевой тип: {target_type}")

	# Если целевой тип - таблица
	if is_target_table:
		if not isinstance(value, dict):
			# Попытка присвоить не-словарь таблице - ошибка
			# (кроме случая присваивания элемента, который обрабатывается отдельно)
			raise AssignmentError(
				f"Попытка присвоить значение типа '{type(value).__name__}' таблице '{var_name_for_error}'. Ожидался словарь.")
		# TODO: Можно добавить проверку типов элементов словаря, но это сложно
		return value  # Возвращаем словарь как есть

	# Если целевой тип - не таблица
	try:
		if base_target_type == "цел":
			converted_value = int(value)
			if not (-MAX_INT - 1 <= converted_value <= MAX_INT): raise ValueError(
				f"Значение {converted_value} выходит за допустимый диапазон для типа 'цел'.")
		elif base_target_type == "вещ":
			converted_value = float(value)
			if not math.isfinite(converted_value): raise ValueError(
				f"Значение {converted_value} не является конечным числом для типа 'вещ'.")
		elif base_target_type == "лог":
			if isinstance(value, bool):
				converted_value = value
			elif isinstance(value, str):
				low_val = value.lower().strip()
				if low_val == "да":
					converted_value = True
				elif low_val == "нет":
					converted_value = False
				else:
					try:
						num_val = float(value); converted_value = (num_val != 0)
					except ValueError:
						raise ValueError(
							f"Недопустимое логическое значение: '{value}'. Ожидалось 'да', 'нет' или число.")
			elif isinstance(value, (int, float)):
				converted_value = (value != 0)
			else:
				converted_value = bool(value)
		elif base_target_type == "сим":
			converted_value = str(value)
			if len(converted_value) != 1: raise ValueError("Значение для типа 'сим' должно быть ровно одним символом.")
		elif base_target_type == "лит":
			converted_value = str(value)
		else:  # Не должно достигаться из-за проверки в начале
			raise TypeError(f"Неожиданный базовый тип: {base_target_type}")
		return converted_value
	except (ValueError, TypeError) as e:
		raise AssignmentError(
			f"Ошибка преобразования значения '{value}' к типу '{target_type}' для переменной '{var_name_for_error}': {e}")
	except Exception as e:
		raise AssignmentError(f"Неожиданная ошибка при преобразовании значения для '{var_name_for_error}': {e}")


def parse_dimensions(dim_spec_str):
	"""Парсит строку размерностей таблицы вида "нач1:кон1, нач2:кон2, ..."."""
	dimensions = []
	if not dim_spec_str: return dimensions
	dim_parts = [part.strip() for part in dim_spec_str.split(',') if part.strip()]
	for i, part in enumerate(dim_parts):
		match = re.match(r"^(-?\d+):(-?\d+)$", part)
		if not match: raise DeclarationError(
			f"Некорректный формат размерности #{i + 1}: '{part}'. Ожидался формат 'начало:конец'.")
		try:
			start_bound = int(match.group(1));
			end_bound = int(match.group(2))
			dimensions.append((start_bound, end_bound))
		except ValueError:
			raise DeclarationError(f"Границы размерности #{i + 1} ('{part}') не являются целыми числами.")
	return dimensions


def process_declaration(line, env):
	"""Обрабатывает строку объявления переменной или таблицы."""
	logger.debug(f"Processing declaration: '{line}'")
	tokens = line.split()
	if not tokens: raise DeclarationError("Пустая строка объявления.")
	decl_type_raw = tokens[0].lower()
	if decl_type_raw not in ALLOWED_TYPES: raise DeclarationError(f"Неизвестный тип переменной: '{tokens[0]}'")
	idx = 1;
	is_table = False;
	table_type_suffix = ""
	if idx < len(tokens) and tokens[idx].lower() == "таб":
		is_table = True;
		table_type_suffix = "таб";
		idx += 1
		logger.debug(f"Declaration is for a table (Type: {decl_type_raw}).")
	full_type = decl_type_raw + table_type_suffix
	rest_of_line = " ".join(tokens[idx:])
	if not rest_of_line: raise DeclarationError(f"Отсутствуют имена переменных после типа '{tokens[0]}'.")
	identifiers_raw = [ident.strip() for ident in rest_of_line.split(",") if ident.strip()]
	if not identifiers_raw: raise DeclarationError(f"Не найдены имена переменных в строке объявления: '{line}'")
	for ident_raw in identifiers_raw:
		var_name = ident_raw;
		dimension_bounds = None
		if is_table:
			dim_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", ident_raw)
			if dim_match:
				var_name = dim_match.group(1).strip();
				dim_spec_str = dim_match.group(2).strip()
				try:
					dimension_bounds = parse_dimensions(dim_spec_str); logger.debug(
						f"Parsed dimensions for table '{var_name}': {dimension_bounds}")
				except DeclarationError as dim_err:
					raise DeclarationError(f"Ошибка в размерностях таблицы '{var_name}': {dim_err}")
			else:
				raise DeclarationError(f"Для таблицы '{ident_raw}' не указаны размерности в квадратных скобках.")
		elif "[" in ident_raw or "]" in ident_raw:
			raise DeclarationError(f"Неожиданные скобки '[]' в объявлении переменной (не таблицы): '{ident_raw}'")
		if not is_valid_identifier(var_name, decl_type_raw): raise DeclarationError(
			f"Недопустимое имя переменной/таблицы: '{var_name}'")
		if var_name in env: raise DeclarationError(f"Переменная или таблица '{var_name}' уже объявлена.")
		env[var_name] = {"type": decl_type_raw,  # Базовый тип хранится здесь
			"value": {} if is_table else get_default_value(decl_type_raw),  # Используем default value
			"kind": "global", "is_table": is_table, "dimensions": dimension_bounds}
		kind_str = "таблица" if is_table else "переменная";
		logger.info(
			f"Declared {kind_str} '{var_name}' base type '{decl_type_raw}'{f' with dimensions {dimension_bounds}' if dimension_bounds else ''}.")
	return True


def process_assignment(line, env, robot=None):
	"""Обрабатывает строку присваивания (:=)."""
	logger.debug(f"Processing assignment: '{line}'")
	parts = line.split(":=", 1);
	if len(parts) != 2: raise AssignmentError(f"Неверный синтаксис присваивания: {line}")
	left_raw, right_expr = parts[0].strip(), parts[1].strip()
	if not left_raw: raise AssignmentError("Отсутствует переменная слева от ':='.")
	if not right_expr: raise AssignmentError("Отсутствует выражение справа от ':='.")
	try:
		rhs_value = safe_eval(right_expr, env, robot); logger.debug(f"Evaluated RHS '{right_expr}' -> {rhs_value}")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления RHS '{right_expr}': {e}")
	except Exception as e:
		logger.error(f"Unexpected error eval RHS '{right_expr}': {e}", exc_info=True); raise KumirEvalError(
			f"Неожиданная ошибка вычисления '{right_expr}': {e}")

	table_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", left_raw)
	if table_match:  # Присваивание элементу таблицы
		var_name = table_match.group(1).strip();
		indices_expr_str = table_match.group(2).strip()
		logger.debug(f"Table element assignment: '{var_name}', indices expr: '{indices_expr_str}'")
		if var_name not in env: raise DeclarationError(f"Таблица '{var_name}' не объявлена.")
		var_info = env[var_name]
		if not var_info.get("is_table"): raise AssignmentError(f"Переменная '{var_name}' не таблица.")
		index_tokens = [t.strip() for t in indices_expr_str.split(',') if t.strip()]
		if not index_tokens: raise AssignmentError(f"Нет индексов для таблицы '{var_name}'.")
		try:
			indices = []
			for token in index_tokens:
				idx_val = safe_eval(token, env, robot)
				try:
					indices.append(int(idx_val))
				except (ValueError, TypeError):
					raise KumirEvalError(f"Индекс '{token}'='{idx_val}' не целое число.")
			indices = tuple(indices);
			logger.debug(f"Evaluated indices: {indices}")
			# Проверка границ
			dims = var_info.get("dimensions")
			if dims:
				if len(indices) != len(dims): raise AssignmentError(
					f"Неверное число индексов ({len(indices)}) для '{var_name}', ожидалось {len(dims)}.")
				for d_idx, idx_val in enumerate(indices):
					start, end = dims[d_idx]
					if not (start <= idx_val <= end): raise AssignmentError(
						f"Индекс #{d_idx + 1} ({idx_val}) вне диапазона [{start}:{end}] для '{var_name}'.")
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления индексов '{indices_expr_str}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error eval indices '{indices_expr_str}': {e}",
						 exc_info=True); raise KumirEvalError(f"Неожиданная ошибка вычисления индексов: {e}")

		target_type = var_info["type"]  # Базовый тип таблицы
		try:
			converted_value = _validate_and_convert_value(rhs_value, target_type, f"{var_name}[...]")
		except AssignmentError as e:
			raise AssignmentError(f"Ошибка присваивания элементу {var_name}{list(indices)}: {e}")
		if not isinstance(var_info.get("value"), dict): var_info["value"] = {}  # Инициализация, если нужно
		var_info["value"][indices] = converted_value
		logger.info(f"Assigned {converted_value} to table element {var_name}{list(indices)}.")
	else:  # Присваивание простой переменной
		var_name = left_raw;
		logger.debug(f"Simple variable assignment: '{var_name}'")
		if var_name not in env: raise DeclarationError(f"Переменная '{var_name}' не объявлена.")
		var_info = env[var_name]
		if var_info.get("is_table"): raise AssignmentError(f"Попытка присвоить значение всей таблице '{var_name}'.")
		target_type = var_info["type"]  # Тип переменной
		converted_value = _validate_and_convert_value(rhs_value, target_type, var_name)
		var_info["value"] = converted_value;
		logger.info(f"Assigned {converted_value} to variable '{var_name}'.")


# Функция split_respecting_quotes остается здесь или выносится в utils
def split_respecting_quotes(text, delimiter=',', quote_char='"'):
	parts = [];
	current_part = "";
	in_quotes = False;
	escape = False
	for char in text:
		if char == quote_char and not escape:
			in_quotes = not in_quotes; current_part += char
		elif char == delimiter and not in_quotes:
			parts.append(current_part);
			current_part = ""
		else:
			current_part += char
		escape = (char == '\\' and not escape)
	parts.append(current_part)
	# Убираем пустые строки и пробелы по краям после разделения
	return [part.strip() for part in parts if part or not part.isspace()]


def process_output(line, env, robot=None, interpreter=None):
	"""Обрабатывает команду 'вывод'."""
	logger.debug(f"Processing output: '{line}'")
	content_part = line[len("вывод"):].strip();
	append_newline = True
	if content_part.lower().endswith(" нс"):
		content_part = content_part[:-len(" нс")].strip(); append_newline = False
	elif content_part.lower() == "нс":
		content_part = ""; append_newline = False
	output_str_parts = []
	if content_part:
		parts_to_eval = split_respecting_quotes(content_part, delimiter=',', quote_char='"')
		if not parts_to_eval and content_part: logger.warning(
			f"Output args split failed: '{content_part}'. Treating as single arg."); parts_to_eval = [content_part]
		for part_expr in parts_to_eval:
			part_expr_strip = part_expr.strip();
			if not part_expr_strip: continue
			try:
				value = safe_eval(part_expr_strip, env, robot)
				if isinstance(value, bool):
					output_str_parts.append("да" if value else "нет")
				else:
					output_str_parts.append(str(value))
				logger.debug(f"Evaluated output part '{part_expr_strip}' -> '{output_str_parts[-1]}'")
			except KumirEvalError as e:
				logger.error(f"Error eval output part '{part_expr_strip}': {e}"); raise InputOutputError(
					f"Ошибка вычисления '{part_expr_strip}' в 'вывод': {e}")
			except Exception as e:
				logger.error(f"Unexpected error eval output part '{part_expr_strip}': {e}",
							 exc_info=True); raise InputOutputError(
					f"Неожиданная ошибка в 'вывод' для '{part_expr_strip}': {e}")
	output_str = "".join(output_str_parts)
	if append_newline: output_str += "\n"
	if interpreter:
		if not hasattr(interpreter, 'output') or interpreter.output is None: interpreter.output = ""
		interpreter.output += output_str;
		output_str_escaped = output_str.replace('\n', '\\n').replace('\r', '\\r')
		logger.info(f"Appended to output buffer: '{output_str_escaped}'")
	else:
		output_stream = get_default_output() or sys.stdout
		try:
			print(output_str, end="", file=output_stream, flush=True); logger.warning(
				"Interpreter context missing for 'вывод', printed to default output.")
		except Exception as e:
			logger.error(f"Error writing to default output stream: {e}")


def process_input(line, env):
	"""Обрабатывает команду 'ввод'."""
	logger.debug(f"Processing 'ввод': '{line}'. Raising InputRequiredError.")
	var_name_raw = line[len("ввод"):].strip()
	if not var_name_raw: raise InputOutputError("Отсутствует имя переменной после 'ввод'.")

	# TODO: Добавить парсинг для `ввод Таблица[индекс]`
	# Пока поддерживаем только простые переменные
	var_name = var_name_raw
	if '[' in var_name: raise InputOutputError(
		f"Команда 'ввод' для элементов таблицы пока не поддерживается: '{var_name_raw}'")

	if not is_valid_identifier(var_name, ""): raise InputOutputError(
		f"Недопустимое имя переменной для ввода: '{var_name}'")
	if var_name not in env: raise DeclarationError(
		f"Переменная '{var_name}' не объявлена перед использованием в 'ввод'.")
	var_info = env[var_name]
	if var_info.get("is_table"): raise InputOutputError(
		f"Команда 'ввод' не поддерживается для целых таблиц ('{var_name}').")

	target_type = var_info["type"];
	prompt = f"Введите значение для '{var_name}' (тип: {target_type}): "
	logger.info(f"Input required for variable '{var_name}' (type: {target_type}). Raising exception.")
	raise KumirInputRequiredError(var_name=var_name, prompt=prompt, target_type=target_type)

# FILE END: declarations.py
