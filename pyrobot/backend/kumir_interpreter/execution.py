# FILE START: execution.py
"""
Модуль execution.py
@description Реализует функции для выполнения управляющих конструкций
языка KUMIR (циклы, условия) и диспетчеризацию отдельных команд, включая вызовы алгоритмов.
"""
import copy  # Для глубокого копирования при передаче параметров
import logging
import re
import time

from .constants import ALLOWED_TYPES
from .declarations import (process_declaration, process_assignment, process_output, process_input, DeclarationError,
						   AssignmentError, InputOutputError, KumirInputRequiredError, get_default_value,
						   _validate_and_convert_value)  # Добавили get_default_value, _validate_and_convert_value
from .robot_commands import process_robot_command
from .robot_state import RobotError
from .safe_eval import safe_eval, KumirEvalError
from .preprocessing import split_respecting_quotes
from .identifiers import is_valid_identifier

logger = logging.getLogger('KumirExecution')

MAX_INFINITE_LOOP_DURATION_S = 10


class KumirExecutionError(Exception):
	def __init__(self, message, line_index=None, line_content=None): super().__init__(
		message); self.line_index = line_index; self.line_content = line_content

	def __str__(self):
		base_message = super().__str__()
		context = ""
		if self.line_index is not None:  # <--- Added colon here
			context += f"строка {self.line_index + 1}"
		if self.line_content is not None:
			context += f": '{self.line_content}'"
		return f"{base_message} ({context.strip()})" if context else base_message

# process_control_command, process_if_block, process_select_block,
# process_loop_for, process_loop_while, process_loop_n_times, process_loop_infinite
# остаются БЕЗ ИЗМЕНЕНИЙ с предыдущей версии (копируем полностью)
def process_control_command(line, env, robot=None):
	lower_line = line.lower().strip();
	keyword = None
	for kw in ["утв", "дано", "надо"]:
		if lower_line.startswith(kw): keyword = kw; break
	if keyword:
		expr = line[len(keyword):].strip()
		if not expr: raise KumirExecutionError(f"Команда '{keyword}' требует логическое выражение после себя.")
		try:
			result = safe_eval(expr, env, robot); logger.debug(
				f"Control '{keyword}' evaluated '{expr}' -> {result} (type: {type(result)})")
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления выражения '{expr}' в команде '{keyword}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating control expr '{expr}': {e}",
						 exc_info=True); raise KumirEvalError(
				f"Неожиданная ошибка вычисления '{expr}' в '{keyword}': {e}")
		if isinstance(result, bool):
			condition = result
		elif isinstance(result, str):
			condition = result.strip().lower() == "да"
		else:
			try:
				condition = (float(result) != 0)
			except (ValueError, TypeError):
				condition = bool(result)
		if not condition:
			failure_reason = result if isinstance(result, (str, bool, int, float)) else type(
				result).__name__; logger.warning(
				f"Control command failure: '{keyword} {expr}' evaluated to {failure_reason} (False)"); raise KumirExecutionError(
				f"Отказ: условие '{expr}' в команде '{keyword}' ложно (результат: {failure_reason}).")
		else:
			logger.info(f"Control command success: '{keyword} {expr}' is True."); return True
	return False


def process_if_block(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	if not header_line.lower().startswith("если"): raise KumirExecutionError(
		"Внутренняя ошибка: process_if_block вызван не для строки 'если'.", header_line_index, header_line)
	condition_expr = header_line[len("если"):].strip();
	i = start_index + 1
	series1_lines, series2_lines, series1_indices, series2_indices = [], [], [], []
	current_series, current_indices = None, None;
	found_then, found_else, end_if_index = False, False, -1
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower();
		original_index = i
		if lower_line == "все":
			end_if_index = original_index; logger.debug(f"Found 'все' for 'если' at index {original_index}"); break
		elif lower_line.startswith("то") and not found_then:
			found_then = True;
			current_series, current_indices = series1_lines, series1_indices;
			content_after_then = line[len("то"):].strip()
			if content_after_then: current_series.append(content_after_then); current_indices.append(original_index)
			logger.debug(f"Found 'то' at index {original_index}. Content after: '{content_after_then}'")
		elif lower_line.startswith("иначе") and found_then and not found_else:
			found_else = True;
			current_series, current_indices = series2_lines, series2_indices;
			content_after_else = line[len("иначе"):].strip()
			if content_after_else: current_series.append(content_after_else); current_indices.append(original_index)
			logger.debug(f"Found 'иначе' at index {original_index}. Content after: '{content_after_else}'")
		else:
			if current_series is not None:
				current_series.append(line); current_indices.append(original_index)
			elif not found_then:
				logger.warning(
					f"Unexpected line '{line}' inside 'если' before 'то'. Assuming part of condition."); condition_expr += " " + line
			else:
				logger.error(
					f"Internal logic error: Line '{line}' encountered unexpectedly in 'если' parsing."); raise KumirExecutionError(
					f"Неожиданная строка '{line}' при разборе блока 'если'.", original_index, line)
		i += 1
	if end_if_index == -1: raise KumirExecutionError(
		f"Не найден 'все' для блока 'если', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	if not found_then: raise KumirExecutionError(
		f"Не найдено 'то' в блоке 'если', начавшемся на строке {header_line_index + 1}.", header_line_index,
		header_line)
	if not condition_expr: raise KumirExecutionError(
		f"Отсутствует условие после 'если' на строке {header_line_index + 1}.", header_line_index, header_line)
	logger.debug(f"Evaluating 'если' condition: '{condition_expr}'")
	try:
		cond_value = safe_eval(condition_expr, env, robot)
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'если': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating 'если' condition '{condition_expr}': {e}",
					 exc_info=True); raise KumirEvalError(f"Неожиданная ошибка в условии 'если': {e}")
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
	if cond_bool:
		logger.debug(f"Executing 'то' block (lines {len(series1_lines)})."); execute_lines(series1_lines, env, robot,
																						   interpreter, trace,
																						   progress_callback,
																						   phase_name, series1_indices)
	elif found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(series2_lines)})."); execute_lines(series2_lines, env, robot,
																							  interpreter, trace,
																							  progress_callback,
																							  phase_name,
																							  series2_indices)
	else:
		logger.debug("Condition is false, no 'иначе' block to execute.")
	return end_if_index + 1


def process_select_block(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	if not header_line.lower() == "выбор": raise KumirExecutionError(
		"Внутренняя ошибка: process_select_block вызван не для 'выбор'.", header_line_index, header_line)
	i = start_index + 1;
	branches = [];
	else_series, else_indices = [], [];
	found_else = False;
	end_select_index = -1
	current_branch_dict, current_branch_lines, current_branch_indices = None, None, None
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower();
		original_index = i
		if lower_line == "все":
			end_select_index = original_index; logger.debug(f"Found 'все' for 'выбор' at index {original_index}"); break
		elif lower_line.startswith("при"):
			if found_else: raise KumirExecutionError("Обнаружена ветка 'при' после 'иначе' в блоке 'выбор'.",
													 original_index, line)
			parts = line.split(":", 1);
			if len(parts) != 2: raise KumirExecutionError(f"Отсутствует ':' после условия в ветке 'при': '{line}'",
														  original_index, line)
			cond_part = parts[0].strip();
			condition_expr = cond_part[len("при"):].strip()
			if not condition_expr: raise KumirExecutionError(f"Отсутствует условие после 'при' в строке: '{line}'",
															 original_index, line)
			first_command = parts[1].strip();
			current_branch_dict = {"condition": condition_expr, "body": [], "indices": []}
			current_branch_lines, current_branch_indices = current_branch_dict["body"], current_branch_dict["indices"]
			if first_command: current_branch_lines.append(first_command); current_branch_indices.append(original_index)
			branches.append(current_branch_dict)
			logger.debug(
				f"Found 'при' branch (idx {len(branches) - 1}) with condition '{condition_expr}'. First command: '{first_command}'")
		elif lower_line.startswith("иначе"):
			if found_else: raise KumirExecutionError("Обнаружено повторное 'иначе' в блоке 'выбор'.", original_index,
													 line)
			if not branches: logger.warning("Блок 'иначе' найден до каких-либо веток 'при' в 'выбор'.")
			found_else = True;
			current_branch_dict = None;
			current_branch_lines, current_branch_indices = else_series, else_indices
			content_after_else = line[len("иначе"):].strip()
			if content_after_else: current_branch_lines.append(content_after_else); current_branch_indices.append(
				original_index)
			logger.debug(f"Found 'иначе' block. Content after: '{content_after_else}'")
		else:
			if current_branch_lines is not None:
				current_branch_lines.append(line); current_branch_indices.append(original_index)
			else:
				raise KumirExecutionError(f"Неожиданная строка '{line}' внутри 'выбор' до начала веток 'при'/'иначе'.",
										  original_index, line)
		i += 1
	if end_select_index == -1: raise KumirExecutionError(
		f"Не найден 'все' для блока 'выбор', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	if not branches and not found_else: logger.warning(
		"Конструкция 'выбор-все' не содержит веток 'при' или блока 'иначе'. Блок пуст.")
	executed = False
	for idx, branch in enumerate(branches):
		condition_expr, series, indices = branch["condition"], branch["body"], branch["indices"]
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
		if cond_bool: logger.debug(f"Executing 'при' branch #{idx + 1} (lines {len(series)})."); execute_lines(series,
																											   env,
																											   robot,
																											   interpreter,
																											   trace,
																											   progress_callback,
																											   phase_name,
																											   indices); executed = True; break
	if not executed and found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(else_series)})."); execute_lines(else_series, env, robot,
																							interpreter, trace,
																							progress_callback,
																							phase_name, else_indices)
	elif not executed:
		logger.debug("No 'при' branch matched and no 'иначе' block found.")
	return end_select_index + 1


def process_loop_for(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	match = re.match(
		r"нц\s+для\s+([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)\s+от\s+(.+?)\s+до\s+(.+?)(?:\s+шаг\s+(.+))?$",
		header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц для': {header_line}",
											header_line_index, header_line)
	var_name, start_expr, end_expr, step_expr = match.groups();
	step_expr = step_expr.strip() if step_expr else "1"
	logger.debug(f"Parsing 'нц для': var='{var_name}', from='{start_expr}', to='{end_expr}', step='{step_expr}'")
	i = start_index + 1;
	loop_body, body_indices = [], [];
	end_loop_index, nesting_level = -1, 0
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
		loop_body.append(line);
		body_indices.append(original_index);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц для', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	try:
		start_val_raw = safe_eval(start_expr, env, robot);
		end_val_raw = safe_eval(end_expr, env, robot);
		step_val_raw = safe_eval(step_expr, env, robot)
		try:
			start_val, end_val, step_val = int(start_val_raw), int(end_val_raw), int(step_val_raw)
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
	original_value, was_declared = None, var_name in env
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
			try:
				execute_lines(loop_body, env, robot, interpreter, trace, progress_callback, phase_name, body_indices)
			except KumirExecutionError as exit_e:
				if str(exit_e) == "Выход":
					logger.info(
						f"Команда 'выход' прервала цикл 'нц для {var_name}' на итерации {iteration_count}."); break
				else:
					raise exit_e
			current += step_val
	finally:
		if was_declared:
			env[var_name]['value'] = original_value; logger.debug(f"Restored original value for '{var_name}'.")
		elif var_name in env and env[var_name].get("kind") == "local_loop":
			del env[var_name]; logger.debug(f"Removed temporary loop variable '{var_name}'.")
	logger.info(f"Finished 'нц для {var_name}' after {iteration_count} iterations.")
	return end_loop_index + 1


def process_loop_while(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
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
	i = start_index + 1;
	loop_body, body_indices = [], [];
	end_loop_index, nesting_level = -1, 0
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
		loop_body.append(line);
		body_indices.append(original_index);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц пока', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
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
		try:
			execute_lines(loop_body, env, robot, interpreter, trace, progress_callback, phase_name, body_indices)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала цикл 'нц пока' на итерации {iteration_count}."); break
			else:
				raise exit_e
	logger.info(f"Finished 'нц пока {condition_expr}' after {iteration_count - 1} successful iterations.")
	return end_loop_index + 1


def process_loop_n_times(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	match = re.match(r"нц\s+(.+?)\s+раз", header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц N раз': {header_line}",
											header_line_index, header_line)
	count_expr = match.group(1).strip();
	logger.debug(f"Parsing 'нц N раз': count_expr='{count_expr}'")
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
	i = start_index + 1;
	loop_body, body_indices = [], [];
	end_loop_index, nesting_level = -1, 0
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
		loop_body.append(line);
		body_indices.append(original_index);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц N раз', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
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
	logger.info(f"Finished 'нц {count} раз'.")
	return end_loop_index + 1


def process_loop_infinite(lines, start_index, env, robot, interpreter, trace, progress_callback, phase_name):
	n = len(lines);
	header_line_index = start_index;
	header_line = lines[header_line_index].strip()
	if not header_line.lower() == "нц": raise KumirExecutionError(
		"Внутренняя ошибка: process_loop_infinite вызван не для 'нц'.", header_line_index, header_line)
	logger.debug("Parsing infinite 'нц' loop.")
	i = start_index + 1;
	loop_body, body_indices = [], [];
	end_loop_index, nesting_level = -1, 0
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
		loop_body.append(line);
		body_indices.append(original_index);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	logger.info("Starting infinite 'нц' loop.");
	iteration_count = 0
	start_time = time.time()
	while True:
		iteration_count += 1;
		logger.debug(f"Infinite 'нц' loop iteration {iteration_count}")
		current_time_exec = time.time()
		if current_time_exec - start_time > MAX_INFINITE_LOOP_DURATION_S: logger.error(
			f"Infinite loop 'нц' exceeded max duration ({MAX_INFINITE_LOOP_DURATION_S}s) after {iteration_count} iterations."); raise KumirExecutionError(
			f"Превышено максимальное время выполнения ({MAX_INFINITE_LOOP_DURATION_S}с) для цикла 'нц'.",
			header_line_index, header_line)
		try:
			execute_lines(loop_body, env, robot, interpreter, trace, progress_callback, phase_name, body_indices)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала бесконечный цикл 'нц' на итерации {iteration_count}."); break
			else:
				raise exit_e
	logger.info(f"Finished infinite 'нц' loop after {iteration_count} iterations.")
	return end_loop_index + 1


# --->>> НОВАЯ РЕАЛИЗАЦИЯ ВЫЗОВА АЛГОРИТМОВ <<<---
def process_algorithm_call(line, caller_env, robot, interpreter, trace, progress_callback, phase_name,
						   current_line_index):
	"""
    Обрабатывает вызов другого алгоритма с параметрами и управлением scope.
    """
	line_strip = line.strip()
	# Паттерн для вызова: имя_алгоритма [(аргументы)] [тип_результата]
	# Тип результата указывается для функций, возвращающих значение (`алг тип имя(...)`)
	# Мы пока не поддерживаем функции, только процедуры.
	call_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*)(?:\s*\((.*)\))?$", line_strip)
	# TODO: Добавить парсинг возвращаемого типа для функций

	if not call_match: return False  # Не похоже на вызов

	algo_name = call_match.group(1).strip()
	args_str = call_match.group(2)  # Строка аргументов или None

	# Проверяем, существует ли такой алгоритм
	if algo_name not in interpreter.algorithms:
		return False  # Это не вызов известного алгоритма

	alg_to_run = interpreter.algorithms[algo_name]
	header_info = alg_to_run.get("header_info", {})
	params_def = header_info.get("params", [])  # [(mode, type, name), ...]

	logger.info(f"Processing call to algorithm '{algo_name}' with args: '{args_str or ''}'")

	# 1. Парсим строку аргументов вызова
	call_args_expr = []
	if args_str:
		# Используем split_respecting_quotes для разделения аргументов по запятой
		call_args_expr = split_respecting_quotes(args_str, delimiter=',', quote_char='"')
		logger.debug(f"Parsed call arguments expressions: {call_args_expr}")

	# 2. Проверяем соответствие количества аргументов и параметров
	if len(call_args_expr) != len(params_def):
		raise KumirExecutionError(
			f"Неверное число аргументов при вызове '{algo_name}'. Ожидалось {len(params_def)}, получено {len(call_args_expr)}.",
			current_line_index, line)

	# 3. Вычисляем значения аргументов в КОНТЕКСТЕ ВЫЗЫВАЮЩЕГО (caller_env)
	evaluated_args = []
	try:
		for i, arg_expr in enumerate(call_args_expr):
			arg_value = safe_eval(arg_expr, caller_env, robot)
			evaluated_args.append(arg_value)
			logger.debug(f"Evaluated argument #{i + 1} ('{arg_expr}') -> {arg_value}")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления аргумента '{arg_expr}' при вызове '{algo_name}': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating argument '{arg_expr}' for '{algo_name}': {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка при вычислении аргумента '{arg_expr}': {e}")

	# 4. Создаем НОВОЕ локальное окружение для вызываемого алгоритма
	local_env = {}
	params_to_copy_back = []  # Список (param_name_local, param_name_caller) для рез/аргрез

	# 5. Сопоставляем аргументы и параметры, заполняем local_env
	for i, (param_mode, param_type, param_name) in enumerate(params_def):
		arg_value = evaluated_args[i]
		logger.debug(f"Binding arg value {arg_value} to param {param_name} (mode: {param_mode}, type: {param_type})")

		# Создаем запись о параметре в локальном окружении
		local_env[param_name] = {"type": param_type.replace('таб', ''),  # Базовый тип
			"value": None,  # Будет установлено ниже
			"kind": "param_" + param_mode,  # Помечаем как параметр
			"is_table": param_type.endswith("таб"), "dimensions": None  # TODO: Поддержка таблиц как параметров
		}

		if local_env[param_name]["is_table"] and not isinstance(arg_value, dict) and param_mode != 'рез':
			raise KumirExecutionError(
				f"Тип аргумента #{i + 1} для параметра-таблицы '{param_name}' должен быть таблицей (словарем).",
				current_line_index, line)

		# Передача значения в зависимости от режима
		if param_mode == "арг" or param_mode == "знач":
			# Передача по значению: копируем значение аргумента
			try:
				# Глубокое копирование для словарей/списков (если будут)
				copied_value = copy.deepcopy(arg_value)
				# Валидируем и конвертируем скопированное значение к типу параметра
				validated_value = _validate_and_convert_value(copied_value, param_type, param_name)
				local_env[param_name]["value"] = validated_value
			except (AssignmentError, TypeError) as e:
				raise KumirExecutionError(f"Ошибка типа при передаче аргумента #{i + 1} параметру '{param_name}': {e}",
										  current_line_index, line)
		elif param_mode == "рез":
			# Результат: инициализируем значением по умолчанию в локальной среде
			local_env[param_name]["value"] = get_default_value(param_type)
			# Запоминаем, что нужно скопировать обратно. Аргумент должен быть именем переменной!
			caller_var_name = call_args_expr[i].strip()  # Имя переменной в вызывающем коде
			if not is_valid_identifier(caller_var_name, ""):
				raise KumirExecutionError(
					f"Аргумент #{i + 1} для параметра 'рез' ('{param_name}') должен быть именем переменной, а не выражением '{caller_var_name}'.",
					current_line_index, line)
			params_to_copy_back.append((param_name, caller_var_name))
		elif param_mode == "аргрез":
			# Аргумент-результат: копируем значение И запоминаем для копирования обратно
			try:
				copied_value = copy.deepcopy(arg_value)
				validated_value = _validate_and_convert_value(copied_value, param_type, param_name)
				local_env[param_name]["value"] = validated_value
			except (AssignmentError, TypeError) as e:
				raise KumirExecutionError(
					f"Ошибка типа при передаче аргумента #{i + 1} параметру 'аргрез' ('{param_name}'): {e}",
					current_line_index, line)
			caller_var_name = call_args_expr[i].strip()
			if not is_valid_identifier(caller_var_name, ""):
				raise KumirExecutionError(
					f"Аргумент #{i + 1} для параметра 'аргрез' ('{param_name}') должен быть именем переменной, а не выражением '{caller_var_name}'.",
					current_line_index, line)
			params_to_copy_back.append((param_name, caller_var_name))
		else:
			# Неизвестный режим (не должно случиться, если парсинг заголовка верен)
			raise KumirExecutionError(f"Неизвестный режим параметра '{param_mode}' для '{param_name}'.",
									  current_line_index, line)

	# 6. Помещаем локальное окружение в стек вызовов
	interpreter.push_call_stack(algo_name, local_env, caller_env)

	# 7. Выполняем тело алгоритма с ЛОКАЛЬНЫМ окружением
	try:
		body_lines = alg_to_run["body"]
		# Генерируем фиктивные индексы для строк тела
		body_indices = list(range(len(body_lines)))
		logger.info(f"Executing body of '{algo_name}'...")
		# Передаем local_env как текущее окружение
		execute_lines(body_lines, local_env, robot, interpreter, trace, progress_callback, f"call_{algo_name}",
					  body_indices)
		logger.info(f"Finished executing body of '{algo_name}'.")

	except Exception as call_e:
		# Если ошибка произошла внутри вызванного алгоритма, пробрасываем ее,
		# но сначала нужно вытолкнуть запись из стека
		logger.error(f"Error occurred inside algorithm '{algo_name}': {call_e}")
		interpreter.pop_call_stack()  # Убираем текущий вызов из стека
		raise  # Пробрасываем ошибку дальше
	# --- Выполнение тела завершено (успешно или через 'выход') ---

	# 8. Извлекаем локальное окружение из стека
	stack_frame = interpreter.pop_call_stack()
	if not stack_frame or stack_frame['name'] != algo_name:
		# Это серьезная внутренняя ошибка управления стеком
		logger.critical(f"Call stack corruption after executing '{algo_name}'!")
		raise KumirExecutionError("Нарушение стека вызовов.", current_line_index, line)
	executed_local_env = stack_frame['env']
	restored_caller_env = stack_frame['caller_env']

	# 9. Копируем результаты (`рез`, `аргрез`) обратно в окружение вызывающего
	logger.debug(f"Copying back results for '{algo_name}': {params_to_copy_back}")
	for local_param_name, caller_var_name in params_to_copy_back:
		if local_param_name not in executed_local_env:
			logger.warning(f"Result parameter '{local_param_name}' not found in local env after call to '{algo_name}'.")
			continue
		# Получаем финальное значение из локальной среды
		final_value = executed_local_env[local_param_name].get("value")
		logger.debug(f"Copying back: {caller_var_name} := {final_value} (from {local_param_name})")
		# Находим переменную в окружении вызывающего
		caller_var_info = interpreter.resolve_variable(caller_var_name)  # Ищем в восстановленном окружении
		if caller_var_info is None:
			# Переменная, куда должен был вернуться результат, не найдена
			raise KumirExecutionError(
				f"Переменная '{caller_var_name}' для возврата результата из '{algo_name}' не найдена в вызывающем окружении.",
				current_line_index, line)
		# Проверяем совместимость типов (базовую)
		expected_caller_type = caller_var_info.get("type")
		actual_param_type = executed_local_env[local_param_name].get("type")
		# Сравниваем базовые типы
		if expected_caller_type != actual_param_type:
			logger.warning(
				f"Type mismatch when copying back result for '{caller_var_name}'. Expected '{expected_caller_type}', got '{actual_param_type}'. Attempting conversion.")
			# Пытаемся конвертировать, но это может быть опасно или неверно
			try:
				validated_value = _validate_and_convert_value(final_value, expected_caller_type, caller_var_name)
				caller_var_info['value'] = validated_value
			except AssignmentError as e:
				raise KumirExecutionError(f"Ошибка типа при возврате результата в '{caller_var_name}': {e}",
										  current_line_index, line)
		else:
			# Типы совпадают, просто присваиваем
			caller_var_info['value'] = final_value

		logger.info(f"Updated caller variable '{caller_var_name}' with result from '{local_param_name}'.")

	# 10. Обработка возвращаемого значения функции (если это была функция)
	# TODO: Реализовать возврат значения для функций, используя stack_frame['return_target']

	logger.info(f"Call to '{algo_name}' completed.")
	return True  # Сигнализируем, что вызов обработан


# --- <<< КОНЕЦ НОВОЙ РЕАЛИЗАЦИИ >>> ---


def execute_lines(lines, env, robot, interpreter, trace, progress_callback, phase_name, original_indices=None):
	"""Выполняет список строк кода Кумира, обрабатывая блоки и трассировку."""
	n = len(lines)
	i = 0
	while i < n:
		line_content = lines[i].strip()
		current_line_index = original_indices[i] if original_indices and i < len(original_indices) else i
		if not line_content: i += 1; continue
		logger.debug(f"Preparing to execute line index {current_line_index} ({phase_name}): '{line_content}'")
		state_before = interpreter.get_state();
		output_before = interpreter.output
		error_occurred = None;
		processed_by_block = False;
		next_i_in_lines = i + 1
		try:
			lower_line = line_content.lower()
			if lower_line.startswith("если"):
				# Передаем env, т.к. блоки выполняются в текущем scope
				next_original_index = process_if_block(lines, i, env, robot, interpreter, trace, progress_callback,
													   phase_name)
				processed_lines_count = next_original_index - i;
				next_i_in_lines = i + processed_lines_count;
				processed_by_block = True
			elif lower_line == "выбор":
				next_original_index = process_select_block(lines, i, env, robot, interpreter, trace, progress_callback,
														   phase_name)
				processed_lines_count = next_original_index - i;
				next_i_in_lines = i + processed_lines_count;
				processed_by_block = True
			elif lower_line.startswith("нц"):
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
				# Передаем env, т.к. циклы выполняются в текущем scope (переменная 'для' обрабатывается внутри)
				next_original_index = loop_func(lines, i, env, robot, interpreter, trace, progress_callback, phase_name)
				processed_lines_count = next_original_index - i;
				next_i_in_lines = i + processed_lines_count;
				processed_by_block = True
			if not processed_by_block:
				# Передаем текущее окружение `env` в execute_line
				execute_line(line_content, env, robot, interpreter,
							 current_line_index)  # next_i_in_lines остается i + 1
		except KumirInputRequiredError as e:
			if not hasattr(e, 'line_index') or e.line_index is None: e.line_index = current_line_index
			if not hasattr(e, 'line_content') or e.line_content is None: e.line_content = line_content
			error_occurred = e;
			raise e
		except (KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
				InputOutputError) as e:
			logger.error(f"Error executing line index {current_line_index} ({phase_name}: '{line_content}'): {e}",
						 exc_info=False)
			error_occurred = e
			if not hasattr(e, 'line_index') or e.line_index is None: e.line_index = current_line_index
			if not hasattr(e, 'line_content') or e.line_content is None: e.line_content = line_content
			raise e
		except Exception as e:
			logger.exception(
				f"Unexpected error executing line index {current_line_index} ({phase_name}: '{line_content}'): {e}")
			error_occurred = e;
			new_e = KumirExecutionError(f"Неожиданная внутренняя ошибка: {type(e).__name__}", current_line_index,
										line_content);
			raise new_e from e
		finally:
			# Трассировка и Callback ПОСЛЕ выполнения строки (если не блок)
			if not processed_by_block:
				state_after = interpreter.get_state();
				output_after = interpreter.output
				trace_entry = {"phase": phase_name, "commandIndex": current_line_index, "command": line_content,
							   "stateAfter": state_after, "outputAfter": output_after}
				if error_occurred: trace_entry["error"] = str(error_occurred)
				trace.append(trace_entry)
				if progress_callback:
					callback_data = {"phase": phase_name, "commandIndex": current_line_index, "output": output_after,
									 "robotPos": state_after.get("robot")}
					if error_occurred: callback_data["error"] = str(error_occurred)
					try:
						progress_callback(callback_data)
					except Exception as cb_err:
						logger.error(f"Error in progress callback: {cb_err}", exc_info=True)
		i = next_i_in_lines


def execute_line(line, env, robot, interpreter, current_line_index):
	"""Выполняет одну строку кода Кумира (не начало блока)."""
	logger.debug(f"Executing single line index {current_line_index}: '{line}'")
	lower_line = line.lower()
	try:
		if lower_line == "использовать робот":
			logger.info("Ignoring 'использовать Робот' command in backend execution.")
			return
		for type_kw in ALLOWED_TYPES:
			if re.match(rf"^{type_kw}(?:\s+.*|$)", lower_line): process_declaration(line, env); return
		if ":=" in line: process_assignment(line, env, robot); return
		if lower_line.startswith("вывод"): process_output(line, env, robot, interpreter); return
		if lower_line.startswith("ввод"): process_input(line, env); return
		if lower_line.startswith(("утв", "дано", "надо")):
			if process_control_command(line, env, robot): return
		if lower_line == "стоп": logger.info("Execution stopped by 'стоп' command."); raise KumirExecutionError(
			"Выполнение прервано командой 'стоп'.")
		if lower_line == "выход": logger.error("'выход' command used outside of a loop."); raise KumirExecutionError(
			"Выход")
		if lower_line == "пауза" or lower_line == "ждать": logger.info(f"Command '{lower_line}' ignored."); return
		if process_robot_command(line, robot): return

		# --->>> ИЗМЕНЯЕМ ВЫЗОВ process_algorithm_call <<<---
		# Передаем текущее окружение `env` как окружение вызывающего
		if interpreter and process_algorithm_call(line, env, robot, interpreter, interpreter.trace,
												  interpreter.progress_callback, "call", current_line_index):
			return
		# --- <<< КОНЕЦ ИЗМЕНЕНИЯ >>> ---

		logger.error(f"Unknown command or syntax error: '{line}'")
		raise KumirExecutionError(f"Неизвестная команда или синтаксическая ошибка.")
	except (KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError, InputOutputError,
			KumirInputRequiredError) as e:
		if hasattr(e, 'line_index') and e.line_index is None: e.line_index = current_line_index
		if hasattr(e, 'line_content') and e.line_content is None: e.line_content = line
		raise e
	except Exception as e:
		logger.exception(
			f"Unexpected error processing line index {current_line_index}: '{line}'"); raise KumirExecutionError(
			f"Неожиданная ошибка: {e}", current_line_index, line)

# FILE END: execution.py
