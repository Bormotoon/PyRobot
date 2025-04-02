# FILE START: declarations.py
"""
Модуль declarations.py
@description Обработка объявлений переменных, присваиваний, ввода/вывода.
"""
import logging
import math
import re

from .identifiers import is_valid_identifier
from .safe_eval import safe_eval, KumirEvalError

logger = logging.getLogger('KumirDeclarations')

ALLOWED_TYPES = {"цел", "вещ", "лог", "сим", "лит"}
MAX_INT = 2147483647


class DeclarationError(Exception): pass


class AssignmentError(Exception): pass


class InputOutputError(Exception): pass


# _validate_and_convert_value без изменений
def _validate_and_convert_value(value, target_type, var_name_for_error):
	# ... (код без изменений) ...
	try:
		if target_type == "цел":
			converted_value = int(value);
			if not (-MAX_INT - 1 <= converted_value <= MAX_INT): raise ValueError(
				f"Значение {converted_value} выходит за допустимый диапазон для типа 'цел'.")
		elif target_type == "вещ":
			converted_value = float(value);
			if not math.isfinite(converted_value): raise ValueError(
				f"Значение {converted_value} не является конечным числом для типа 'вещ'.")
		elif target_type == "лог":
			if isinstance(value, bool):
				converted_value = value
			elif isinstance(value, str):
				low_val = value.lower().strip();
				if low_val == "да":
					converted_value = True
				elif low_val == "нет":
					converted_value = False
				else:
					try:
						num_val = float(value);
						converted_value = (num_val != 0)
					except ValueError:
						raise ValueError(
							f"Недопустимое логическое значение: '{value}'. Ожидалось 'да', 'нет' или число.")
			elif isinstance(value, (int, float)):
				converted_value = (value != 0)
			else:
				converted_value = bool(value)
		elif target_type == "сим":
			converted_value = str(value);
			if len(converted_value) != 1: raise ValueError("Значение для типа 'сим' должно быть ровно одним символом.")
		elif target_type == "лит":
			converted_value = str(value)
		else:
			raise TypeError(f"Неподдерживаемый целевой тип: {target_type}")
		return converted_value
	except (ValueError, TypeError) as e:
		raise AssignmentError(
			f"Ошибка преобразования значения '{value}' к типу '{target_type}' для переменной '{var_name_for_error}': {e}")
	except Exception as e:
		raise AssignmentError(f"Неожиданная ошибка при преобразовании значения для '{var_name_for_error}': {e}")


# process_declaration - добавляем 'kind'
def process_declaration(line, env):
	"""
	Обрабатывает строку объявления переменной или таблицы в текущем окружении.
	"""
	logger.debug(f"Processing declaration: '{line}'")
	tokens = line.split()
	if not tokens: raise DeclarationError("Пустая строка объявления.")

	decl_type_raw = tokens[0].lower()
	if decl_type_raw not in ALLOWED_TYPES:
		raise DeclarationError(f"Неизвестный тип переменной: '{tokens[0]}'")

	idx = 1;
	is_table = False
	if idx < len(tokens) and tokens[idx].lower().startswith("таб"):
		is_table = True;
		idx += 1
		logger.debug(f"Declaration is for a table (Type: {decl_type_raw}).")

	rest_of_line = " ".join(tokens[idx:])
	if not rest_of_line: raise DeclarationError(f"Отсутствуют имена переменных после типа '{tokens[0]}'.")

	identifiers_raw = [ident.strip() for ident in rest_of_line.split(",") if ident.strip()]

	for ident_raw in identifiers_raw:
		var_name = ident_raw;
		dimensions = None
		if is_table and "[" in ident_raw and ident_raw.endswith("]"):
			match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", ident_raw)
			if match:
				var_name = match.group(1).strip()
				dim_spec = match.group(2).strip()
				dimensions = dim_spec  # TODO: Parse dimensions
				logger.debug(f"Table '{var_name}' dimensions specified: [{dimensions}]")
			else:
				raise DeclarationError(f"Некорректный синтаксис объявления таблицы: '{ident_raw}'")
		elif is_table:
			logger.warning(f"Объявлена таблица '{var_name}', но размеры не указаны (динамические?).")
		elif "[" in ident_raw:
			raise DeclarationError(f"Неожиданные скобки '[]' в объявлении переменной (не таблицы): '{ident_raw}'")

		if not is_valid_identifier(var_name, decl_type_raw):
			raise DeclarationError(f"Недопустимое имя переменной: '{var_name}'")
		if var_name in env:
			# TODO: Уточнить правила Кумира о переопределении в том же scope. Пока запрещаем.
			raise DeclarationError(f"Переменная '{var_name}' уже объявлена в текущем окружении.")

		# Определяем "kind" в зависимости от того, глобальное ли это окружение
		# (Пока просто считаем, что если не параметр, то local/global)
		# Правильное определение kind будет зависеть от контекста вызова process_declaration
		var_kind = "local"  # По умолчанию локальная для текущего scope
		# Если бы мы знали, что это глобальный scope, поставили бы 'global'
		# var_kind = "global" if is_global_scope else "local"

		env[var_name] = {
			"type": decl_type_raw,
			"value": {} if is_table else None,
			"kind": var_kind,  # Добавляем kind
			"is_table": is_table,
			"dimensions": dimensions
		}
		table_str = "таблица" if is_table else "переменная"
		logger.info(f"Объявлена {var_kind} {table_str} '{var_name}' типа '{decl_type_raw}'.")

	return True


# process_assignment без изменений
def process_assignment(line, env, robot=None):
	# ... (код без изменений) ...
	logger.debug(f"Processing assignment: '{line}'")
	parts = line.split(":=", 1)
	if len(parts) != 2: raise AssignmentError(
		f"Неверный синтаксис присваивания (отсутствует или несколько ':='): {line}")
	left_raw, right_expr = parts[0].strip(), parts[1].strip()
	if not left_raw: raise AssignmentError("Отсутствует переменная слева от ':='.")
	if not right_expr: raise AssignmentError("Отсутствует выражение справа от ':='.")
	try:
		rhs_value = safe_eval(right_expr, env, robot)
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления выражения '{right_expr}' в правой части присваивания: {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating RHS '{right_expr}': {e}", exc_info=True);
		raise KumirEvalError(
			f"Неожиданная ошибка вычисления '{right_expr}': {e}")
	table_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", left_raw)
	if table_match:
		var_name = table_match.group(1).strip();
		indices_expr_str = table_match.group(2).strip()
		logger.debug(f"Assignment target is table '{var_name}' with indices expr '{indices_expr_str}'")
		if var_name not in env: raise DeclarationError(f"Таблица '{var_name}' не объявлена.")
		var_info = env[var_name]
		if not var_info.get("is_table"): raise AssignmentError(
			f"Переменная '{var_name}' не является таблицей, но используется с индексами.")
		index_tokens = [token.strip() for token in indices_expr_str.split(",") if token.strip()]
		if not index_tokens: raise AssignmentError(f"Отсутствуют индексы для таблицы '{var_name}'.")
		try:
			indices = []
			for token in index_tokens:
				index_val = safe_eval(token, env, robot)
				try:
					indices.append(int(index_val))
				except (ValueError, TypeError):
					raise KumirEvalError(
						f"Индекс '{token}' вычислен в '{index_val}', но не может быть преобразован в целое число.")
			indices = tuple(indices)
			logger.debug(f"Evaluated indices -> {indices}")
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления индексов '{indices_expr_str}' для таблицы '{var_name}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating indices '{indices_expr_str}': {e}",
						 exc_info=True);
			raise KumirEvalError(
				f"Неожиданная ошибка вычисления индексов '{indices_expr_str}': {e}")
		target_type = var_info["type"];
		converted_value = _validate_and_convert_value(rhs_value, target_type, f"{var_name}[{indices_expr_str}]")
		if var_info["value"] is None or not isinstance(var_info["value"], dict): var_info["value"] = {}
		var_info["value"][indices] = converted_value
		logger.info(f"Присвоено значение {converted_value} элементу {var_name}{list(indices)}.")
	else:
		var_name = left_raw;
		logger.debug(f"Assignment target is variable '{var_name}'")
		if var_name not in env: raise DeclarationError(f"Переменная '{var_name}' не объявлена.")
		var_info = env[var_name]
		if var_info.get("is_table"): raise AssignmentError(
			f"Попытка присвоить значение таблице '{var_name}' без указания индексов.")
		target_type = var_info["type"];
		converted_value = _validate_and_convert_value(rhs_value, target_type, var_name)
		var_info["value"] = converted_value
		logger.info(f"Присвоено значение {converted_value} переменной '{var_name}'.")


# process_output без изменений
def process_output(line, env, robot=None, interpreter=None):
	# ... (код без изменений) ...
	logger.debug(f"Processing output: '{line}'")
	content_part = line[len("вывод"):].strip();
	append_newline = True
	if content_part.lower().endswith(" нс"):
		content_part = content_part[:-len(" нс")].strip();
		append_newline = False
	elif content_part.lower() == "нс":
		content_part = "";
		append_newline = False
	if not content_part:
		output_str = "\n" if append_newline and interpreter and hasattr(interpreter, 'output') else ""
	else:
		parts_to_eval = [part.strip() for part in content_part.split(",") if part.strip()]  # TODO: Handle quoted commas
		output_segments = []
		for part in parts_to_eval:
			if not part: continue
			try:
				value = safe_eval(part, env, robot)  # Передаем env, robot
				if isinstance(value, bool):
					output_segments.append("да" if value else "нет")
				else:
					output_segments.append(str(value))
				logger.debug(f"Evaluated output part '{part}' -> '{output_segments[-1]}'")
			except KumirEvalError as e:
				logger.error(f"Ошибка вычисления части '{part}' в команде 'вывод': {e}");
				raise InputOutputError(
					f"Ошибка вычисления выражения '{part}' в команде 'вывод': {e}")
			except Exception as e:
				logger.error(f"Unexpected error evaluating output part '{part}': {e}",
							 exc_info=True);
				raise InputOutputError(f"Неожиданная ошибка в 'вывод' для '{part}': {e}")
		output_str = "".join(output_segments)
		if append_newline: output_str += "\n"
	if interpreter:
		if not hasattr(interpreter, 'output'): interpreter.output = ""
		interpreter.output += output_str
		output_str_escaped = output_str.replace('\n', '\\n')
		logger.info(f"Output buffer appended: '{output_str_escaped}'")
	else:
		print(output_str, end="");
		logger.warning("Interpreter context not provided for 'вывод', printing to console.")


# process_input без изменений
def process_input(line, env):
	# ... (код без изменений) ...
	logger.warning(f"Processing 'ввод': '{line}'. This is blocking and unsuitable for web servers.")
	var_name = line[len("ввод"):].strip()
	if not var_name: raise InputOutputError("Отсутствует имя переменной после 'ввод'.")
	if not is_valid_identifier(var_name, ""): raise InputOutputError(
		f"Недопустимое имя переменной для ввода: '{var_name}'")
	if var_name not in env: raise DeclarationError(
		f"Переменная '{var_name}' не объявлена перед использованием в 'ввод'.")
	var_info = env[var_name]
	if var_info.get("is_table"): raise InputOutputError(
		f"Нельзя использовать 'ввод' для всей таблицы '{var_name}'. Укажите элемент.")
	target_type = var_info["type"];
	prompt = f"Введите значение для '{var_name}' (тип {target_type}): "
	try:
		user_input = input(prompt)  # Блокирует!
		logger.info(f"Получен ввод для '{var_name}': '{user_input}'")
		converted_value = _validate_and_convert_value(user_input, target_type, var_name)
		env[var_name]["value"] = converted_value
		logger.info(f"Переменной '{var_name}' присвоено введенное значение {converted_value}.")
	except EOFError:
		logger.error("EOF encountered during 'ввод'.");
		raise InputOutputError(
			"Неожиданный конец файла при ожидании ввода.")
	except (AssignmentError, ValueError, TypeError) as e:
		logger.error(f"Ошибка обработки ввода для '{var_name}': {e}");
		raise InputOutputError(
			f"Ошибка обработки ввода для '{var_name}': {e}")
	except Exception as e:
		logger.exception(f"Неожиданная ошибка при выполнении 'ввод' для '{var_name}': {e}");
		raise InputOutputError(
			f"Неожиданная ошибка при вводе для '{var_name}': {e}")

# FILE END: declarations.py
