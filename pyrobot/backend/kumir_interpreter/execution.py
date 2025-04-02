# FILE START: execution.py
"""
Модуль execution.py
@description Реализует функции для выполнения управляющих конструкций
языка KUMIR (циклы, условия) и диспетчеризацию отдельных команд.
"""
import logging
import re
import time  # Для защиты от бесконечных циклов

# Импорты из нашего проекта
from .declarations import (process_declaration, process_assignment, process_output, process_input, ALLOWED_TYPES,
						   DeclarationError, AssignmentError, InputOutputError, KumirInputRequiredError)
from .robot_commands import process_robot_command
from .robot_state import RobotError, SimulatedRobot
from .safe_eval import safe_eval, KumirEvalError

logger = logging.getLogger('KumirExecution')

# Максимальное время выполнения для "бесконечных" циклов 'нц' в секундах
MAX_INFINITE_LOOP_DURATION_S = 10


# Максимальное количество итераций (альтернативная или дополнительная защита)
# MAX_LOOP_ITERATIONS = 100000 # Можно раскомментировать и использовать

class KumirExecutionError(Exception):
	"""Основное исключение для ошибок выполнения (не вычисления)."""

	def __init__(self, message, line_index=None, line_content=None):
		super().__init__(message)
		self.line_index = line_index  # Индекс строки в текущем блоке (0-based)
		self.line_content = line_content  # Содержимое строки

	def __str__(self):
		base_message = super().__str__()
		if self.line_index is not None and self.line_content is not None:
			return f"{base_message} (строка {self.line_index + 1}: '{self.line_content}')"
		elif self.line_content is not None:
			return f"{base_message} (строка: '{self.line_content}')"
		else:
			return base_message


def process_control_command(line, env, robot=None):
	""" Обрабатывает команды управления: утв, дано, надо. """
	lower_line = line.lower().strip()
	keyword = None
	for kw in ["утв", "дано", "надо"]:
		if lower_line.startswith(kw):
			keyword = kw
			break

	if keyword:
		expr = line[len(keyword):].strip()
		if not expr:
			raise KumirExecutionError(f"Команда '{keyword}' требует логическое выражение после себя.")

		try:
			result = safe_eval(expr, env, robot)
			logger.debug(f"Control '{keyword}' evaluated '{expr}' -> {result} (type: {type(result)})")
		except KumirEvalError as e:
			# Добавляем контекст к ошибке вычисления
			raise KumirEvalError(f"Ошибка вычисления выражения '{expr}' в команде '{keyword}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating control expr '{expr}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка вычисления '{expr}' в '{keyword}': {e}")

		# Преобразуем результат к булевому типу (с учетом "да"/"нет")
		if isinstance(result, bool):
			condition = result
		elif isinstance(result, str):
			condition = result.strip().lower() == "да"
		else:  # Попытка преобразовать числа (0=False, !=0=True)
			try:
				condition = (float(result) != 0)
			except (ValueError, TypeError):
				condition = bool(result)  # Fallback

		if not condition:
			failure_reason = result if isinstance(result, (str, bool, int, float)) else type(result).__name__
			logger.warning(f"Control command failure: '{keyword} {expr}' evaluated to {failure_reason} (False)")
			# Бросаем ошибку выполнения, а не вычисления
			raise KumirExecutionError(
				f"Отказ: условие '{expr}' в команде '{keyword}' ложно (результат: {failure_reason}).")
		else:
			logger.info(f"Control command success: '{keyword} {expr}' is True.")
			return True  # Команда обработана

	return False  # Это была не команда утв/дано/надо


def process_if_block(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	""" Обрабатывает блок "если-то-[иначе]-все". """
	n = len(lines)
	header_line_index = start_index  # Запоминаем индекс строки 'если'
	header_line = lines[header_line_index].strip()
	if not header_line.lower().startswith("если"):
		raise KumirExecutionError("Внутренняя ошибка: process_if_block вызван не для строки 'если'.", header_line_index,
								  header_line)

	condition_expr = header_line[len("если"):].strip()
	i = start_index + 1
	series1_lines = []  # Блок "то"
	series2_lines = []  # Блок "иначе"
	# Храним индексы строк для блоков
	series1_indices = []
	series2_indices = []
	current_series = None
	current_indices = None
	found_then = False
	found_else = False
	end_if_index = -1

	# --- Парсинг блока ---
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()
		original_index = i  # Индекс в исходном списке `lines`

		if lower_line == "все":
			end_if_index = original_index
			logger.debug(f"Found 'все' for 'если' at index {original_index}")
			break
		elif lower_line.startswith("то") and not found_then:
			found_then = True
			current_series = series1_lines
			current_indices = series1_indices
			content_after_then = line[len("то"):].strip()
			if content_after_then:
				current_series.append(content_after_then)
				current_indices.append(original_index)  # Сохраняем индекс
			logger.debug(f"Found 'то' at index {original_index}. Content after: '{content_after_then}'")
		elif lower_line.startswith("иначе") and found_then and not found_else:
			found_else = True
			current_series = series2_lines
			current_indices = series2_indices
			content_after_else = line[len("иначе"):].strip()
			if content_after_else:
				current_series.append(content_after_else)
				current_indices.append(original_index)  # Сохраняем индекс
			logger.debug(f"Found 'иначе' at index {original_index}. Content after: '{content_after_else}'")
		else:
			if current_series is not None:
				current_series.append(line)
				current_indices.append(original_index)  # Сохраняем индекс
			elif not found_then:
				logger.warning(f"Unexpected line '{line}' inside 'если' before 'то'. Assuming part of condition.")
				condition_expr += " " + line  # Попытка объединить
			else:
				logger.error(f"Internal logic error: Line '{line}' encountered unexpectedly in 'если' parsing.")
				raise KumirExecutionError(f"Неожиданная строка '{line}' при разборе блока 'если'.", original_index,
										  line)
		i += 1

	# --- Валидация структуры ---
	if end_if_index == -1:
		raise KumirExecutionError(f"Не найден 'все' для блока 'если', начавшегося на строке {header_line_index + 1}.",
								  header_line_index, header_line)
	if not found_then:
		raise KumirExecutionError(f"Не найдено 'то' в блоке 'если', начавшемся на строке {header_line_index + 1}.",
								  header_line_index, header_line)
	if not condition_expr:
		raise KumirExecutionError(f"Отсутствует условие после 'если' на строке {header_line_index + 1}.",
								  header_line_index, header_line)

	# --- Вычисление условия ---
	logger.debug(f"Evaluating 'если' condition: '{condition_expr}'")
	try:
		cond_value = safe_eval(condition_expr, env, robot)
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'если': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating 'если' condition '{condition_expr}': {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка в условии 'если': {e}")

	if isinstance(cond_value, bool):
		cond_bool = cond_value
	elif isinstance(cond_value, str):
		cond_bool = cond_value.strip().lower() == "да"
	else:
		try:
			cond_bool = (float(cond_value) != 0)
		except (ValueError, TypeError):
			cond_bool = bool(cond_value)
	logger.info(f"'Если {condition_expr}' evaluated to {cond_bool}.")

	# --- Выполнение соответствующего блока ---
	if cond_bool:
		logger.debug(f"Executing 'то' block (lines {len(series1_lines)}).")
		# Передаем строки и их оригинальные индексы
		execute_lines(series1_lines, env, robot, interpreter, trace, progress_callback, phase_name, series1_indices)
	elif found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(series2_lines)}).")
		execute_lines(series2_lines, env, robot, interpreter, trace, progress_callback, phase_name, series2_indices)
	else:
		logger.debug("Condition is false, no 'иначе' block to execute.")

	# Возвращаем индекс строки, следующей за 'все'
	return end_if_index + 1


def process_select_block(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	""" Обрабатывает блок "выбор-при-[иначе]-все". """
	n = len(lines)
	header_line_index = start_index
	header_line = lines[header_line_index].strip()
	if not header_line.lower() == "выбор":
		raise KumirExecutionError("Внутренняя ошибка: process_select_block вызван не для 'выбор'.", header_line_index,
								  header_line)

	i = start_index + 1
	branches = []  # Список словарей: {"condition": expr, "body": lines, "indices": line_indices}
	else_series = []
	else_indices = []
	found_else = False
	end_select_index = -1
	current_branch_dict = None  # Ссылка на текущий словарь ветки в `branches`
	current_branch_lines = None
	current_branch_indices = None

	# --- Парсинг блока ---
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()
		original_index = i

		if lower_line == "все":
			end_select_index = original_index
			logger.debug(f"Found 'все' for 'выбор' at index {original_index}")
			break
		elif lower_line.startswith("при"):
			if found_else: raise KumirExecutionError("Обнаружена ветка 'при' после 'иначе' в блоке 'выбор'.",
													 original_index, line)
			parts = line.split(":", 1)
			if len(parts) != 2: raise KumirExecutionError(f"Отсутствует ':' после условия в ветке 'при': '{line}'",
														  original_index, line)
			cond_part = parts[0].strip();
			condition_expr = cond_part[len("при"):].strip()
			if not condition_expr: raise KumirExecutionError(f"Отсутствует условие после 'при' в строке: '{line}'",
															 original_index, line)
			first_command = parts[1].strip()
			# Создаем новый словарь для ветки
			current_branch_dict = {"condition": condition_expr, "body": [], "indices": []}
			current_branch_lines = current_branch_dict["body"]
			current_branch_indices = current_branch_dict["indices"]
			if first_command:
				current_branch_lines.append(first_command)
				current_branch_indices.append(original_index)
			branches.append(current_branch_dict)
			logger.debug(
				f"Found 'при' branch (idx {len(branches) - 1}) with condition '{condition_expr}'. First command: '{first_command}'")

		elif lower_line.startswith("иначе"):
			if found_else: raise KumirExecutionError("Обнаружено повторное 'иначе' в блоке 'выбор'.", original_index,
													 line)
			if not branches: logger.warning("Блок 'иначе' найден до каких-либо веток 'при' в 'выбор'.")
			found_else = True
			current_branch_dict = None  # Больше не добавляем в ветки 'при'
			current_branch_lines = else_series  # Переключаемся на блок 'иначе'
			current_branch_indices = else_indices
			content_after_else = line[len("иначе"):].strip()
			if content_after_else:
				current_branch_lines.append(content_after_else)
				current_branch_indices.append(original_index)
			logger.debug(f"Found 'иначе' block. Content after: '{content_after_else}'")

		else:
			if current_branch_lines is not None:
				current_branch_lines.append(line)
				current_branch_indices.append(original_index)  # Сохраняем индекс
			else:
				raise KumirExecutionError(f"Неожиданная строка '{line}' внутри 'выбор' до начала веток 'при'/'иначе'.",
										  original_index, line)
		i += 1

	# --- Валидация ---
	if end_select_index == -1:
		raise KumirExecutionError(f"Не найден 'все' для блока 'выбор', начавшегося на строке {header_line_index + 1}.",
								  header_line_index, header_line)
	if not branches and not found_else:
		logger.warning("Конструкция 'выбор-все' не содержит веток 'при' или блока 'иначе'. Блок пуст.")

	# --- Выполнение ---
	executed = False
	for idx, branch in enumerate(branches):
		condition_expr = branch["condition"]
		series = branch["body"]
		indices = branch["indices"]  # Получаем индексы строк ветки
		logger.debug(f"Evaluating 'при' condition #{idx + 1}: {condition_expr}")
		try:
			cond_value = safe_eval(condition_expr, env, robot)
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в ветке 'при' блока 'выбор': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating 'при' condition '{condition_expr}': {e}",
						 exc_info=True); raise KumirEvalError(f"Неожиданная ошибка в условии 'при': {e}")

		if isinstance(cond_value, bool):
			cond_bool = cond_value
		elif isinstance(cond_value, str):
			cond_bool = cond_value.strip().lower() == "да"
		else:
			try:
				cond_bool = (float(cond_value) != 0)
			except (ValueError, TypeError):
				cond_bool = bool(cond_value)
		logger.info(f"'При {condition_expr}' evaluated to {cond_bool}.")

		if cond_bool:
			logger.debug(f"Executing 'при' branch #{idx + 1} (lines {len(series)}).")
			# Передаем строки ветки и их оригинальные индексы
			execute_lines(series, env, robot, interpreter, trace, progress_callback, phase_name, indices)
			executed = True
			break

	if not executed and found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(else_series)}).")
		execute_lines(else_series, env, robot, interpreter, trace, progress_callback, phase_name, else_indices)
	elif not executed:
		logger.debug("No 'при' branch matched and no 'иначе' block found.")

	return end_select_index + 1


def process_loop_for(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	""" Обрабатывает цикл 'нц для ... кц'. """
	n = len(lines)
	header_line_index = start_index
	header_line = lines[header_line_index].strip()
	match = re.match(
		r"нц\s+для\s+([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)\s+от\s+(.+?)\s+до\s+(.+?)(?:\s+шаг\s+(.+))?$",
		header_line, re.IGNORECASE)
	if not match:
		raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц для': {header_line}", header_line_index,
								  header_line)

	var_name, start_expr, end_expr, step_expr = match.groups();
	step_expr = step_expr.strip() if step_expr else "1"
	logger.debug(f"Parsing 'нц для': var='{var_name}', from='{start_expr}', to='{end_expr}', step='{step_expr}'")

	# --- Поиск тела цикла и 'кц' ---
	i = start_index + 1;
	loop_body = [];
	body_indices = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower();
		original_index = i
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = original_index; break
			else:
				nesting_level -= 1
		loop_body.append(line)
		body_indices.append(original_index)  # Сохраняем индекс строки тела
		i += 1
	if end_loop_index == -1:
		raise KumirExecutionError(f"Не найден 'кц' для цикла 'нц для', начавшегося на строке {header_line_index + 1}.",
								  header_line_index, header_line)

	# --- Вычисление параметров цикла ---
	try:
		start_val_raw = safe_eval(start_expr, env, robot);
		end_val_raw = safe_eval(end_expr, env, robot);
		step_val_raw = safe_eval(step_expr, env, robot)
		try:
			start_val = int(start_val_raw); end_val = int(end_val_raw); step_val = int(step_val_raw)
		except (ValueError, TypeError) as conv_e:
			raise KumirEvalError(
				f"Параметры цикла 'для' (начало, конец, шаг) должны быть целыми числами. Ошибка преобразования: {conv_e}")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления параметров цикла 'нц для': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating 'нц для' params: {e}", exc_info=True); raise KumirEvalError(
			f"Неожиданная ошибка в параметрах 'нц для': {e}")
	if step_val == 0: raise KumirExecutionError("Шаг в цикле 'нц для' не может быть равен нулю.", header_line_index,
												header_line)

	# --- Выполнение цикла ---
	original_value = None;
	was_declared = var_name in env
	if was_declared:
		if env[var_name].get("is_table"): raise KumirExecutionError(
			f"Переменная цикла '{var_name}' не может быть таблицей.", header_line_index, header_line)
		if env[var_name]["type"] != "цел": logger.warning(
			f"Переменная цикла '{var_name}' имеет тип '{env[var_name]['type']}', но будет использоваться как 'цел'.")
		original_value = env[var_name].get('value');
		logger.debug(f"Loop variable '{var_name}' exists. Original value: {original_value}")
	else:
		env[var_name] = {"type": "цел", "value": None, "kind": "local_loop", "is_table": False}; logger.debug(
			f"Loop variable '{var_name}' created locally for the loop.")
	current = start_val;
	logger.info(f"Starting 'нц для {var_name}' from {start_val} to {end_val} step {step_val}.");
	iteration_count = 0
	try:
		while True:
			if step_val > 0:
				if current > end_val: break
			else:
				if current < end_val: break
			iteration_count += 1;
			env[var_name]["value"] = current;
			logger.debug(f"'для {var_name}' iteration {iteration_count}, value = {current}")
			# Выполняем тело цикла, передавая строки тела и их индексы
			try:
				execute_lines(loop_body, env, robot, interpreter, trace, progress_callback, phase_name, body_indices)
			except KumirExecutionError as exit_e:
				if str(exit_e) == "Выход":
					logger.info(
						f"Команда 'выход' прервала цикл 'нц для {var_name}' на итерации {iteration_count}."); break
				else:
					raise exit_e  # Перебрасываем другие ошибки выполнения
			# Ошибки Eval, Robot и др. будут пойманы внешним обработчиком execute_lines
			current += step_val
		# if iteration_count > MAX_LOOP_ITERATIONS: raise KumirExecutionError(f"Превышен лимит итераций ({iteration_count})", header_line_index, header_line)
	finally:  # Восстановление/удаление переменной цикла
		if was_declared:
			env[var_name]['value'] = original_value; logger.debug(f"Restored original value for '{var_name}'.")
		elif var_name in env and env[var_name].get("kind") == "local_loop":
			del env[var_name]; logger.debug(f"Removed temporary loop variable '{var_name}'.")
	logger.info(f"Finished 'нц для {var_name}' after {iteration_count} iterations.")
	return end_loop_index + 1


def process_loop_while(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	""" Обрабатывает цикл 'нц пока ... кц'. """
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	match = re.match(r"нц\s+пока\s+(.+)", header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц пока': {header_line}",
											header_line_index, header_line)
	condition_expr = match.group(1).strip()
	if not condition_expr: raise KumirExecutionError("Отсутствует условие после 'нц пока'.", header_line_index,
													 header_line)
	logger.debug(f"Parsing 'нц пока': condition='{condition_expr}'")
	# --- Поиск тела цикла ---
	i = start_index + 1;
	loop_body = [];
	body_indices = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower();
		original_index = i
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = original_index; break
			else:
				nesting_level -= 1
		loop_body.append(line)
		body_indices.append(original_index)  # Сохраняем индекс
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц пока', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	# --- Выполнение ---
	logger.info(f"Starting 'нц пока {condition_expr}'.");
	iteration_count = 0
	while True:
		iteration_count += 1
		try:
			cond_value = safe_eval(condition_expr, env, robot)
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в цикле 'нц пока': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating 'нц пока' condition '{condition_expr}': {e}",
						 exc_info=True); raise KumirEvalError(f"Неожиданная ошибка в условии 'нц пока': {e}")
		if isinstance(cond_value, bool):
			cond_bool = cond_value
		elif isinstance(cond_value, str):
			cond_bool = cond_value.strip().lower() == "да"
		else:
			try:
				cond_bool = (float(cond_value) != 0)
			except (ValueError, TypeError):
				cond_bool = bool(cond_value)
		logger.debug(f"'пока {condition_expr}' (Iteration {iteration_count}) evaluated to {cond_bool}.")
		if not cond_bool: logger.debug("Condition is false, exiting 'нц пока'."); break
		# Выполняем тело
		try:
			execute_lines(loop_body, env, robot, interpreter, trace, progress_callback, phase_name, body_indices)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала цикл 'нц пока' на итерации {iteration_count}."); break
			else:
				raise exit_e
	# Ошибки Eval, Robot и др. будут пойманы внешним обработчиком execute_lines
	# if iteration_count > MAX_LOOP_ITERATIONS: raise KumirExecutionError(f"Превышен лимит итераций ({iteration_count})", header_line_index, header_line)
	logger.info(f"Finished 'нц пока {condition_expr}' after {iteration_count - 1} successful iterations.")
	return end_loop_index + 1


def process_loop_n_times(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	""" Обрабатывает цикл 'нц <N> раз ... кц'. """
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	match = re.match(r"нц\s+(.+?)\s+раз", header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц N раз': {header_line}",
											header_line_index, header_line)
	count_expr = match.group(1).strip();
	logger.debug(f"Parsing 'нц N раз': count_expr='{count_expr}'")
	# --- Вычисляем N ---
	try:
		count_raw = safe_eval(count_expr, env, robot)
		try:
			count = int(count_raw)
		except (ValueError, TypeError):
			raise KumirEvalError(
				f"Количество повторений '{count_expr}' (вычислено как '{count_raw}') не является целым числом.")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления количества повторений '{count_expr}' в цикле 'нц N раз': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating 'N раз' count '{count_expr}': {e}",
					 exc_info=True); raise KumirEvalError(f"Неожиданная ошибка в количестве повторений 'нц N раз': {e}")
	if count < 0: logger.warning(
		f"Число повторений в 'нц {count} раз' отрицательное. Цикл не будет выполнен."); count = 0
	# --- Поиск тела ---
	i = start_index + 1;
	loop_body = [];
	body_indices = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower();
		original_index = i
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = original_index; break
			else:
				nesting_level -= 1
		loop_body.append(line)
		body_indices.append(original_index)  # Сохраняем индекс
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц N раз', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	# --- Выполнение ---
	logger.info(f"Starting 'нц {count} раз'.")
	for iteration in range(count):
		current_iteration = iteration + 1;
		logger.debug(f"'нц N раз' iteration {current_iteration}/{count}")
		try:
			execute_lines(loop_body, env, robot, interpreter, trace, progress_callback, phase_name, body_indices)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала цикл 'нц N раз' на итерации {current_iteration}."); break
			else:
				raise exit_e
	# Ошибки Eval, Robot и др. будут пойманы внешним обработчиком execute_lines
	logger.info(f"Finished 'нц {count} раз'.")
	return end_loop_index + 1


def process_loop_infinite(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	""" Обрабатывает 'бесконечный' цикл 'нц ... кц'. """
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	if not header_line.lower() == "нц": raise KumirExecutionError(
		"Внутренняя ошибка: process_loop_infinite вызван не для 'нц'.", header_line_index, header_line)
	logger.debug("Parsing infinite 'нц' loop.")
	# --- Поиск тела ---
	i = start_index + 1;
	loop_body = [];
	body_indices = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower();
		original_index = i
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = original_index; break
			else:
				nesting_level -= 1
		loop_body.append(line)
		body_indices.append(original_index)  # Сохраняем индекс
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	# --- Выполнение ---
	logger.info("Starting infinite 'нц' loop.");
	iteration_count = 0
	start_time = time.time()
	while True:
		iteration_count += 1;
		logger.debug(f"Infinite 'нц' loop iteration {iteration_count}")
		# Защита от зависания
		current_time_exec = time.time()
		if current_time_exec - start_time > MAX_INFINITE_LOOP_DURATION_S:
			logger.error(
				f"Infinite loop 'нц' exceeded max duration ({MAX_INFINITE_LOOP_DURATION_S}s) after {iteration_count} iterations.")
			raise KumirExecutionError(
				f"Превышено максимальное время выполнения ({MAX_INFINITE_LOOP_DURATION_S}с) для цикла 'нц'.",
				header_line_index, header_line)
		# if iteration_count > MAX_LOOP_ITERATIONS: raise KumirExecutionError(...)
		try:
			execute_lines(loop_body, env, robot, interpreter, trace, progress_callback, phase_name, body_indices)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала бесконечный цикл 'нц' на итерации {iteration_count}."); break
			else:
				raise exit_e
	# Ошибки Eval, Robot и др. будут пойманы внешним обработчиком execute_lines
	logger.info(f"Finished infinite 'нц' loop after {iteration_count} iterations.")
	return end_loop_index + 1


def process_algorithm_call(line, env, robot, interpreter, trace, progress_callback, phase_name, current_line_index):
	"""
	Обрабатывает вызов другого алгоритма.
	ВНИМАНИЕ: Реализация все еще УПРОЩЕННАЯ (ЗАГЛУШКА).
	"""
	line_strip = line.strip()
	call_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)(?:\s*\((.*)\))?$", line_strip)

	if call_match:
		algo_name = call_match.group(1);
		args_str = call_match.group(2)
		if algo_name in interpreter.algorithms:
			alg_to_run = interpreter.algorithms[algo_name]
			# TODO: Реализовать полную логику вызова с параметрами и scope.
			logger.info(f"Placeholder call to algorithm: '{algo_name}' (Params/Scope not implemented)")
			logger.warning("Algorithm call implementation is basic and needs proper parameter handling and scoping.")
			try:
				# --- ВРЕМЕННАЯ ЗАГЛУШКА: выполняем тело в текущем env ---
				body_lines = alg_to_run["body"]
				# Генерируем фиктивные индексы для строк тела вызываемого алгоритма
				# Это неверно, т.к. индексы должны быть относительно исходного файла,
				# но пока нет механизма маппинга.
				body_indices = list(range(len(body_lines)))  # Фиктивные индексы 0, 1, 2...

				execute_lines(body_lines, env, robot, interpreter, trace, progress_callback, f"call_{algo_name}",
							  body_indices)
				logger.info(f"Finished placeholder call to '{algo_name}'.")
				return True  # Сигнализируем, что это был распознанный вызов
			except Exception as call_e:
				logger.error(f"Error during execution of algorithm '{algo_name}': {call_e}", exc_info=True)
				raise KumirExecutionError(f"Ошибка при выполнении алгоритма '{algo_name}': {call_e}",
										  current_line_index, line)
		# --- КОНЕЦ ЗАГЛУШКИ ---
	return False


def execute_lines(lines, env, robot, interpreter, trace, progress_callback, phase_name, original_indices=None):
	"""
	Выполняет список строк кода Кумира.
	Args:
		lines (list): Список строк кода для выполнения.
		env (dict): Текущее окружение переменных.
		robot (SimulatedRobot): Экземпляр робота.
		interpreter (KumirLanguageInterpreter): Экземпляр интерпретатора.
		trace (list): Список для записи шагов трассировки.
		progress_callback (function): Функция обратного вызова для отправки прогресса.
		phase_name (str): Имя текущей фазы выполнения (e.g., 'introduction', 'main', 'call_myFunc').
		original_indices (list, optional): Список оригинальных индексов строк в исходном коде
											(для корректной трассировки внутри блоков).
											Если None, используются индексы 0, 1, 2...
	"""
	n = len(lines)
	i = 0  # Индекс в текущем списке `lines`
	while i < n:
		line_content = lines[i].strip()
		# Определяем оригинальный индекс строки (если передан) или используем текущий
		current_line_index = original_indices[i] if original_indices and i < len(original_indices) else i

		if not line_content:
			i += 1
			continue

		logger.debug(f"Executing line index {current_line_index} ({phase_name}): '{line_content}'")

		# --- Трассировка и Callback ПЕРЕД выполнением ---
		state_before = interpreter.get_state()
		output_before = interpreter.output
		trace_entry_before = {
			"phase": phase_name,
			"commandIndex": current_line_index,
			"command": line_content,
			"stateBefore": state_before,  # Состояние до
			"outputBefore": output_before
		}
		# trace.append(trace_entry_before) # Можно добавить, если нужно состояние ДО

		error_occurred = None
		processed_by_block = False

		try:
			# --- Определение типа строки и выполнение ---
			lower_line = line_content.lower()

			# Блочные структуры
			if lower_line.startswith("если"):
				# Передаем дальше trace, progress_callback, phase_name
				next_i_offset = process_if_block(lines, i, env, robot, interpreter, trace, progress_callback,
												 phase_name)
				# Устанавливаем i на индекс ПОСЛЕ 'все'
				# next_i_offset - это индекс СЛЕДУЮЩЕЙ строки после блока
				# Нам нужно найти смещение относительно текущего `lines`
				# Это сложно без точного маппинга индексов. Пока упростим:
				# Найдем индекс 'все' и перейдем за него.
				block_end_line_idx = next_i_offset - 1
				# Найдем смещение в текущем lines (примерно)
				processed_lines_count = block_end_line_idx - current_line_index + 1 if original_indices else next_i_offset - i
				i += processed_lines_count  # Перескакиваем весь блок
				processed_by_block = True
			elif lower_line == "выбор":
				next_i_offset = process_select_block(lines, i, env, robot, interpreter, trace, progress_callback,
													 phase_name)
				block_end_line_idx = next_i_offset - 1
				processed_lines_count = block_end_line_idx - current_line_index + 1 if original_indices else next_i_offset - i
				i += processed_lines_count
				processed_by_block = True
			elif lower_line.startswith("нц"):
				# Определяем тип цикла
				if re.match(r"нц\s+для", lower_line):
					loop_func = process_loop_for
				elif re.match(r"нц\s+пока", lower_line):
					loop_func = process_loop_while
				elif re.match(r"нц\s+.+?\s+раз", lower_line):
					loop_func = process_loop_n_times
				elif lower_line == "нц":
					loop_func = process_loop_infinite
				else:
					raise KumirExecutionError(f"Неизвестный синтаксис цикла 'нц'", current_line_index, line_content)
				next_i_offset = loop_func(lines, i, env, robot, interpreter, trace, progress_callback, phase_name)
				block_end_line_idx = next_i_offset - 1
				processed_lines_count = block_end_line_idx - current_line_index + 1 if original_indices else next_i_offset - i
				i += processed_lines_count
				processed_by_block = True

			# Однострочные команды
			if not processed_by_block:
				# Передаем индекс и контент для возможных ошибок
				execute_line(line_content, env, robot, interpreter, current_line_index)
				i += 1  # Переходим к следующей строке в `lines`

		# --->>> Обработка исключений ВНУТРИ execute_lines <<<---
		except KumirInputRequiredError as e:
			raise e  # Пробрасываем наверх для interpret
		except (
				KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
				InputOutputError) as e:
			logger.error(f"Error executing line index {current_line_index} ({phase_name}: '{line_content}'): {e}",
						 exc_info=False)
			error_occurred = e  # Запоминаем ошибку
			# Если у ошибки нет индекса строки, добавляем его
			if hasattr(e, 'line_index') and e.line_index is None: e.line_index = current_line_index
			if hasattr(e, 'line_content') and e.line_content is None: e.line_content = line_content
			# Прерываем выполнение текущего блока строк
			# raise e # Или просто break/return? Пробрасываем наверх в interpret
			raise e
		except Exception as e:
			logger.exception(
				f"Unexpected error executing line index {current_line_index} ({phase_name}: '{line_content}'): {e}")
			error_occurred = e  # Запоминаем ошибку
			# Прерываем выполнение текущего блока строк
			# Оборачиваем в KumirExecutionError для единообразия
			raise KumirExecutionError(f"Неожиданная внутренняя ошибка: {e}", current_line_index, line_content)

		# --- Трассировка и Callback ПОСЛЕ выполнения (или при ошибке) ---
		state_after = interpreter.get_state()
		output_after = interpreter.output

		trace_entry_after = {
			"phase": phase_name,
			"commandIndex": current_line_index,
			"command": line_content,
			"stateAfter": state_after,
			"outputAfter": output_after
		}
		if error_occurred:
			trace_entry_after["error"] = str(error_occurred)

		trace.append(trace_entry_after)

		if progress_callback:
			callback_data = {
				"phase": phase_name,
				"commandIndex": current_line_index,
				"output": output_after,
				"robotPos": state_after.get("robot")  # Может быть None
			}
			if error_occurred:
				callback_data["error"] = str(error_occurred)
			progress_callback(callback_data)

	# Если произошла ошибка (кроме InputRequired), прерываем цикл while i < n
	# InputRequired обрабатывается в interpret
	# if error_occurred:
	#     break # Выходим из цикла обработки строк


def execute_line(line, env, robot, interpreter, current_line_index):
	"""
	Выполняет одну строку кода Кумира. Предполагается, что это не начало блочной конструкции.
	Добавлен current_line_index для добавления контекста к ошибкам.
	"""
	logger.debug(f"Executing single line index {current_line_index}: '{line}'")
	lower_line = line.lower()

	try:
		# 1. Объявление переменных
		for type_kw in ALLOWED_TYPES:
			if re.match(rf"^{type_kw}(?:\s+.*|$)", lower_line):
				process_declaration(line, env)
				return

		# 2. Присваивание
		if ":=" in line:
			process_assignment(line, env, robot)
			return

		# 3. Вывод
		if lower_line.startswith("вывод"):
			process_output(line, env, robot, interpreter)
			return

		# 4. Ввод
		if lower_line.startswith("ввод"):
			process_input(line, env)  # Генерирует KumirInputRequiredError
			return  # Не будет достигнуто

		# 5. Команды управления (утв, дано, надо)
		if lower_line.startswith(("утв", "дано", "надо")):
			if process_control_command(line, env, robot):
				return

		# 6. Команды потока управления (стоп, выход, пауза/ждать)
		if lower_line == "стоп":
			logger.info("Execution stopped by 'стоп' command.")
			raise KumirExecutionError("Выполнение прервано командой 'стоп'.")

		if lower_line == "выход":
			logger.error("'выход' command used outside of a loop.")
			# Бросаем исключение, которое должно быть поймано внутри process_loop_*
			raise KumirExecutionError("Выход")

		if lower_line == "пауза" or lower_line == "ждать":
			logger.info(f"Command '{lower_line}' ignored in server execution mode (handled by frontend animation).")
			# Ничего не делаем на бэкенде
			return

		# 7. Команды робота
		if process_robot_command(line, robot):
			return

		# 8. Вызов другого алгоритма (Заглушка!)
		# Передаем trace, callback, phase и индекс для возможного использования внутри
		if interpreter and process_algorithm_call(line, env, robot, interpreter, interpreter.trace,
												  interpreter.progress_callback, "call", current_line_index):
			return

		# 9. Неизвестная команда
		logger.error(f"Unknown command or syntax error: '{line}'")
		raise KumirExecutionError(f"Неизвестная команда или синтаксическая ошибка.")

	# Перехватываем ошибки и добавляем контекст строки
	except (KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError, InputOutputError,
			KumirInputRequiredError) as e:
		# Если у ошибки еще нет контекста строки, добавляем его
		if hasattr(e, 'line_index') and e.line_index is None: e.line_index = current_line_index
		if hasattr(e, 'line_content') and e.line_content is None: e.line_content = line
		raise e  # Пробрасываем дальше
	except Exception as e:
		logger.exception(f"Unexpected error processing line index {current_line_index}: '{line}'")
		# Оборачиваем в KumirExecutionError с контекстом
		raise KumirExecutionError(f"Неожиданная ошибка: {e}", current_line_index, line)

# FILE END: execution.py
