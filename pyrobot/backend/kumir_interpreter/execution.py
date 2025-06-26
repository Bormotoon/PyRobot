# FILE START: execution.py
"""
Модуль execution.py
@description Реализует функции для выполнения управляющих конструкций
языка KUMIR (циклы, условия) и диспетчеризацию отдельных команд, включая вызовы алгоритмов.
Обновлен для работы с механизмом ссылок через interpreter и использует
исключения из kumir_exceptions.
"""
import logging
import re
import time

# Импортируем все нужные исключения
from .kumir_exceptions import (KumirExecutionError, DeclarationError, AssignmentError,
                               InputOutputError, KumirInputRequiredError, KumirEvalError,
                               RobotError)
from .constants import ALLOWED_TYPES
# Импортируем только нужные функции process_* из declarations
from .declarations import (process_declaration, process_assignment, process_output,
                           process_input)
from .robot_commands import process_robot_command
from .safe_eval import safe_eval  # KumirEvalError импортирован выше

logger = logging.getLogger('KumirExecution')

MAX_INFINITE_LOOP_DURATION_S = 10


# --- Функции обработки управляющих конструкций ---
# Теперь принимают 'interpreter' для передачи его в safe_eval и execute_lines

def process_control_command(line, interpreter):
	"""Обрабатывает команды утв/дано/надо."""
	env = interpreter.get_env_by_index(interpreter.get_current_env_index())
	robot = interpreter.robot
	lower_line = line.lower().strip();
	keyword = None;
	expr = None
	for kw in ["утв", "дано", "надо"]:
		if lower_line.startswith(kw + " "):
			keyword = kw;
			expr = line[len(keyword):].strip();
			break
	if not keyword:
		if lower_line in ["утв", "дано", "надо"]: raise KumirExecutionError(
			f"Команда '{lower_line}' требует логическое выражение после себя.")
		return False
	if not expr: raise KumirExecutionError(f"Команда '{keyword}' требует логическое выражение после себя.")
	try:
		result = safe_eval(expr, env, robot, interpreter)
		logger.debug(f"Control '{keyword}' evaluated '{expr}' -> {result} (type: {type(result)})")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления выражения '{expr}' в команде '{keyword}': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating control expr '{expr}': {e}", exc_info=True); raise KumirEvalError(
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
		failure_reason = result if isinstance(result, (str, bool, int, float)) else type(result).__name__
		logger.warning(f"Control command failure: '{keyword} {expr}' evaluated to {failure_reason} (False)")
		raise KumirExecutionError(f"Отказ: условие '{expr}' в команде '{keyword}' ложно (результат: {failure_reason}).")
	else:
		logger.info(f"Control command success: '{keyword} {expr}' is True.")
		return True


def process_if_block(lines, start_index, interpreter, trace, progress_callback, phase_name, original_indices):
	"""Обрабатывает блок если-то-иначе-все."""
	env = interpreter.get_env_by_index(interpreter.get_current_env_index())
	robot = interpreter.robot
	n = len(lines);
	header_line_index = original_indices[start_index];
	header_line = lines[start_index].strip()
	if not header_line.lower().startswith("если"): raise KumirExecutionError(
		"Внутренняя ошибка: process_if_block вызван не для строки 'если'.", header_line_index, header_line)
	condition_expr = header_line[len("если"):].strip()
	if not condition_expr:
		if start_index + 1 < n and not lines[start_index + 1].lower().strip().startswith(("то", "иначе", "все")):
			logger.debug(
				f"Condition for 'если' seems to be on the next line. Reading line {original_indices[start_index + 1] + 1}")
			condition_expr = lines[start_index + 1].strip();
			start_index += 1
		else:
			raise KumirExecutionError(f"Отсутствует условие после 'если' на строке {header_line_index + 1}.",
			                          header_line_index, header_line)
	i = start_index + 1;
	series1_lines, series2_lines = [], [];
	series1_indices, series2_indices = [], []
	current_series = None
	current_indices = None
	found_then, found_else, end_if_index = False, False, -1
	while i < n:
		line_raw = lines[i];
		line = line_raw.strip();
		lower_line = line.lower();
		original_index_for_line = original_indices[i]
		if lower_line == "все":
			end_if_index = i; logger.debug(
				f"Found 'все' for 'если' at index {original_index_for_line + 1} (local index {i})"); break
		elif lower_line.startswith("то") and not found_then:
			found_then = True;
			current_series, current_indices = series1_lines, series1_indices
			content_after_then = line[len("то"):].strip()
			if content_after_then: 
				current_series.append(content_after_then); current_indices.append(original_index_for_line)
			logger.debug(f"Found 'то' at index {original_index_for_line + 1}. Content after: '{content_after_then}'")
		elif lower_line.startswith("иначе") and found_then and not found_else:
			found_else = True;
			current_series, current_indices = series2_lines, series2_indices
			content_after_else = line[len("иначе"):].strip()
			if content_after_else: 
				current_series.append(content_after_else); current_indices.append(original_index_for_line)
			logger.debug(f"Found 'иначе' at index {original_index_for_line + 1}. Content after: '{content_after_else}'")
		elif lower_line.startswith("иначе если") and found_then and not found_else:
			logger.warning(
				f"Detected 'иначе если' at line {original_index_for_line + 1}. Treating as start of 'иначе'.")
			found_else = True;
			current_series, current_indices = series2_lines, series2_indices
			current_series.append(line_raw);
			current_indices.append(original_index_for_line)
		else:
			if current_series is not None and current_indices is not None:
				current_series.append(line_raw); current_indices.append(original_index_for_line)
			elif not found_then:
				logger.debug(f"Line '{line}' appended to 'если' condition."); condition_expr += "\n" + line_raw
			else:
				logger.error(
					f"Unexpected line '{line}' at index {original_index_for_line + 1} during 'если' parsing."); raise KumirExecutionError(
					f"Неожиданная строка '{line}' при разборе блока 'если'.", original_index_for_line, line)
		i += 1
	if end_if_index == -1: raise KumirExecutionError(
		f"Не найден 'все' для блока 'если', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	if not found_then: raise KumirExecutionError(
		f"Не найдено 'то' в блоке 'если', начавшемся на строке {header_line_index + 1}.", header_line_index,
		header_line)
	logger.debug(f"Evaluating 'если' condition: '{condition_expr}'")
	try:
		cond_value = safe_eval(condition_expr, env, robot, interpreter)
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
		if series1_lines:
			logger.debug(f"Executing 'то' block (lines {len(series1_lines)})."); execute_lines(series1_lines, env,
			                                                                                   robot, interpreter,
			                                                                                   trace, progress_callback,
			                                                                                   phase_name,
			                                                                                   series1_indices)
		else:
			logger.debug("Executing 'то' block (empty).")
	elif found_else:
		if series2_lines:
			logger.debug(f"Executing 'иначе' block (lines {len(series2_lines)})."); execute_lines(series2_lines, env,
			                                                                                      robot, interpreter,
			                                                                                      trace,
			                                                                                      progress_callback,
			                                                                                      phase_name,
			                                                                                      series2_indices)
		else:
			logger.debug("Executing 'иначе' block (empty).")
	else:
		logger.debug("Condition is false, no 'иначе' block to execute.")
	return end_if_index + 1


# --->>> ВОЗВРАЩАЕМ ОПРЕДЕЛЕНИЯ ФУНКЦИЙ ОБРАБОТКИ БЛОКОВ <<<---

def process_select_block(lines, start_index, interpreter, trace, progress_callback, phase_name, original_indices):
	"""Обрабатывает блок выбор-при-иначе-все."""
	env = interpreter.get_env_by_index(interpreter.get_current_env_index())
	robot = interpreter.robot
	n = len(lines);
	header_line_index = original_indices[start_index];
	header_line = lines[start_index].strip()
	if not header_line.lower() == "выбор": raise KumirExecutionError(
		"Внутренняя ошибка: process_select_block вызван не для 'выбор'.", header_line_index, header_line)
	i = start_index + 1;
	branches = [];
	else_series, else_indices = [], [];
	found_else = False;
	end_select_index = -1
	current_branch_dict = None
	current_branch_lines = None
	current_branch_indices = None
	while i < n:
		line_raw = lines[i];
		line = line_raw.strip();
		lower_line = line.lower();
		original_index_for_line = original_indices[i]
		if lower_line == "все":
			end_select_index = i; logger.debug(f"Found 'все' for 'выбор' at index {original_index_for_line + 1}"); break
		elif lower_line.startswith("при"):
			if found_else: raise KumirExecutionError("Обнаружена ветка 'при' после 'иначе' в блоке 'выбор'.",
			                                         original_index_for_line, line)
			parts = line.split(":", 1);
			if len(parts) != 2: raise KumirExecutionError(f"Отсутствует ':' после условия в ветке 'при': '{line}'",
			                                              original_index_for_line, line)
			cond_part = parts[0].strip();
			condition_expr = cond_part[len("при"):].strip()
			if not condition_expr: raise KumirExecutionError(f"Отсутствует условие после 'при' в строке: '{line}'",
			                                                 original_index_for_line, line)
			first_command = parts[1].strip();
			current_branch_dict = {"condition": condition_expr, "body": [], "indices": []}
			current_branch_lines, current_branch_indices = current_branch_dict["body"], current_branch_dict["indices"]
			if first_command: 
				current_branch_lines.append(first_command); current_branch_indices.append(original_index_for_line)
			branches.append(current_branch_dict)
			logger.debug(
				f"Found 'при' branch (idx {len(branches) - 1}) with condition '{condition_expr}'. First command: '{first_command}'")
		elif lower_line.startswith("иначе"):
			if found_else: raise KumirExecutionError("Обнаружено повторное 'иначе' в блоке 'выбор'.",
			                                         original_index_for_line, line)
			if not branches: logger.warning("Блок 'иначе' найден до каких-либо веток 'при' в 'выбор'.")
			found_else = True;
			current_branch_dict = None;
			current_branch_lines, current_branch_indices = else_series, else_indices
			content_after_else = line[len("иначе"):].strip()
			if content_after_else: 
				current_branch_lines.append(content_after_else); current_branch_indices.append(original_index_for_line)
			logger.debug(f"Found 'иначе' block. Content after: '{content_after_else}'")
		else:
			if current_branch_lines is not None and current_branch_indices is not None:
				current_branch_lines.append(line_raw); current_branch_indices.append(original_index_for_line)
			else:
				raise KumirExecutionError(f"Неожиданная строка '{line}' внутри 'выбор' до начала веток 'при'/'иначе'.",
				                          original_index_for_line, line)
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
			cond_value = safe_eval(condition_expr, env, robot, interpreter)
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
			execute_lines(series, env, robot, interpreter, trace, progress_callback, phase_name, indices)
			executed = True;
			break
	if not executed and found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(else_series)}).")
		execute_lines(else_series, env, robot, interpreter, trace, progress_callback, phase_name, else_indices)
	elif not executed:
		logger.debug("No 'при' branch matched and no 'иначе' block found.")
	return end_select_index + 1


def process_loop_for(lines, start_index, interpreter, trace, progress_callback, phase_name, original_indices):
	"""Обрабатывает цикл нц-для-от-до-шаг-кц."""
	env = interpreter.get_env_by_index(interpreter.get_current_env_index())
	robot = interpreter.robot
	n = len(lines);
	header_line_index = original_indices[start_index];
	header_line = lines[start_index].strip()
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
		line_raw = lines[i];
		line = line_raw.strip();
		lower_line = line.lower();
		original_index_for_line = original_indices[i]
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; break
			else:
				nesting_level -= 1
		loop_body.append(line_raw);
		body_indices.append(original_index_for_line);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц для', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	try:
		start_val_raw = safe_eval(start_expr, env, robot, interpreter);
		end_val_raw = safe_eval(end_expr, env, robot, interpreter);
		step_val_raw = safe_eval(step_expr, env, robot, interpreter)
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

	# --- Управление переменной цикла ---
	original_value, was_declared = None, False
	var_info = interpreter.get_variable_info(var_name)  # Ищем в текущем и глобальном
	if var_info:
		was_declared = True
		if var_info.get("is_table"): raise KumirExecutionError(f"Переменная цикла '{var_name}' не может быть таблицей.",
		                                                       header_line_index, header_line)
		if var_info["type"] != "цел": logger.warning(
			f"Переменная цикла '{var_name}' имеет тип '{var_info['type']}', но будет использоваться как 'цел'.")
		original_value = interpreter.resolve_variable_value(var_name)  # Сохраняем текущее значение
		logger.debug(f"Loop variable '{var_name}' exists. Original value: {original_value}")
	else:
		# Если не объявлена, создаем временно в *текущем* окружении
		current_env = interpreter.get_env_by_index(interpreter.get_current_env_index())
		current_env[var_name] = {"kind": "value", "type": "цел", "value": None, "is_table": False, "dimensions": None,
		                         "_loop_temp": True}
		logger.debug(f"Loop variable '{var_name}' created temporarily for the loop.")

	current = start_val;
	logger.info(f"Starting 'нц для {var_name}' from {start_val} to {end_val} step {step_val}.");
	iteration_count = 0
	try:
		while True:
			if (step_val > 0 and current > end_val) or (step_val < 0 and current < end_val): break
			iteration_count += 1;
			# Обновляем значение переменной цикла через метод интерпретатора
			try:
				interpreter.update_variable_value(var_name, current)
			except KumirExecutionError as update_err:
				logger.error(
					f"Failed to update loop variable '{var_name}': {update_err}"); break  # Прерываем цикл при ошибке обновления
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
		# Восстанавливаем или удаляем переменную цикла
		var_info_final = interpreter.get_variable_info(var_name)
		if was_declared:
			if var_info_final:  # Если переменная все еще существует
				try:
					interpreter.update_variable_value(var_name, original_value); logger.debug(
						f"Restored original value for '{var_name}'.")
				except KumirExecutionError as restore_err:
					logger.error(f"Failed to restore original value for loop variable '{var_name}': {restore_err}")
			else:
				logger.warning(f"Loop variable '{var_name}' disappeared during loop execution.")
		elif var_info_final and var_info_final.get("_loop_temp"):
			# Удаляем временную переменную из текущего окружения
			current_env = interpreter.get_env_by_index(interpreter.get_current_env_index())
			if var_name in current_env:
				del current_env[var_name];
				logger.debug(f"Removed temporary loop variable '{var_name}'.")

	logger.info(f"Finished 'нц для {var_name}' after {iteration_count} iterations.")
	return end_loop_index + 1


def process_loop_while(lines, start_index, interpreter, trace, progress_callback, phase_name, original_indices):
	"""Обрабатывает цикл нц-пока-кц."""
	env = interpreter.get_env_by_index(interpreter.get_current_env_index())
	robot = interpreter.robot
	n = len(lines);
	header_line_index = original_indices[start_index];
	header_line = lines[start_index].strip()
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
		line_raw = lines[i];
		line = line_raw.strip();
		lower_line = line.lower();
		original_index_for_line = original_indices[i]
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; break
			else:
				nesting_level -= 1
		loop_body.append(line_raw);
		body_indices.append(original_index_for_line);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц пока', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	logger.info(f"Starting 'нц пока {condition_expr}'.");
	iteration_count = 0
	while True:
		iteration_count += 1
		try:
			cond_value = safe_eval(condition_expr, env, robot, interpreter)
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


def process_loop_n_times(lines, start_index, interpreter, trace, progress_callback, phase_name, original_indices):
	"""Обрабатывает цикл нц-N-раз-кц."""
	env = interpreter.get_env_by_index(interpreter.get_current_env_index())
	robot = interpreter.robot
	n = len(lines);
	header_line_index = original_indices[start_index];
	header_line = lines[start_index].strip()
	match = re.match(r"нц\s+(.+?)\s+раз", header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц N раз': {header_line}",
	                                        header_line_index, header_line)
	count_expr = match.group(1).strip();
	logger.debug(f"Parsing 'нц N раз': count_expr='{count_expr}'")
	try:
		count_raw = safe_eval(count_expr, env, robot, interpreter)
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
		line_raw = lines[i];
		line = line_raw.strip();
		lower_line = line.lower();
		original_index_for_line = original_indices[i]
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; break
			else:
				nesting_level -= 1
		loop_body.append(line_raw);
		body_indices.append(original_index_for_line);
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


def process_loop_infinite(lines, start_index, interpreter, trace, progress_callback, phase_name, original_indices):
	"""Обрабатывает бесконечный цикл нц-кц."""
	env = interpreter.get_env_by_index(interpreter.get_current_env_index())
	robot = interpreter.robot
	n = len(lines);
	header_line_index = original_indices[start_index];
	header_line = lines[start_index].strip()
	if not header_line.lower() == "нц": raise KumirExecutionError(
		"Внутренняя ошибка: process_loop_infinite вызван не для 'нц'.", header_line_index, header_line)
	logger.debug("Parsing infinite 'нц' loop.")
	i = start_index + 1;
	loop_body, body_indices = [], [];
	end_loop_index, nesting_level = -1, 0
	while i < n:
		line_raw = lines[i];
		line = line_raw.strip();
		lower_line = line.lower();
		original_index_for_line = original_indices[i]
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; break
			else:
				nesting_level -= 1
		loop_body.append(line_raw);
		body_indices.append(original_index_for_line);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц', начавшегося на строке {header_line_index + 1}.", header_line_index,
		header_line)
	logger.info("Starting infinite 'нц' loop.");
	iteration_count = 0;
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


# --- execute_lines и execute_line ---
# Теперь принимают 'interpreter' и передают его дальше

def execute_lines(lines, current_env_for_exec, robot, interpreter, trace, progress_callback, phase_name,
                  original_indices=None):
	""" Выполняет список строк кода Кумира. """
	n = len(lines);
	i = 0
	while i < n:
		line_content_raw = lines[i];
		line_content = line_content_raw.strip()
		current_original_index = original_indices[i] if original_indices and i < len(original_indices) else i
		if not line_content: i += 1; continue
		logger.debug(f"Preparing to execute line index {current_original_index + 1} ({phase_name}): '{line_content}'")
		state_before = None;
		output_before = interpreter.output;
		error_occurred = None
		processed_by_block = False;
		next_i_in_lines = i + 1
		try:
			lower_line = line_content.lower()
			is_if_block = lower_line.startswith("если");
			is_select_block = lower_line == "выбор";
			is_loop_block = lower_line.startswith("нц")
			if is_if_block or is_select_block or is_loop_block:
				processed_by_block = True;
				logger.debug(f"Processing block starting at line {current_original_index + 1}")
				state_before = interpreter.get_state()
				block_processor = None
				if is_if_block:
					block_processor = process_if_block
				elif is_select_block:
					block_processor = process_select_block
				elif is_loop_block:
					if re.match(r"нц\s+для", lower_line):
						loop_func = process_loop_for
					elif re.match(r"нц\s+пока", lower_line):
						loop_func = process_loop_while
					elif re.match(r"нц\s+.+?\s+раз", lower_line):
						loop_func = process_loop_n_times
					elif lower_line == "нц":
						loop_func = process_loop_infinite
					else:
						raise KumirExecutionError(f"Неизвестный синтаксис цикла 'нц'", current_original_index,
						                          line_content)
					block_processor = loop_func
				else:
					raise KumirExecutionError("Внутренняя ошибка: не найден обработчик блока", current_original_index,
					                          line_content)
				next_line_index_in_lines = block_processor(lines, i, interpreter, trace, progress_callback, phase_name,
				                                           original_indices)
				next_i_in_lines = next_line_index_in_lines
			else:
				processed_by_block = False;
				state_before = interpreter.get_state()
				# Передаем оригинальную строку с отступами
				execute_line(line_content_raw, interpreter, current_original_index)
		except KumirInputRequiredError as e:
			if not hasattr(e, 'line_index') or e.line_index is None: e.line_index = current_original_index
			if not hasattr(e, 'line_content') or e.line_content is None: e.line_content = line_content_raw
			error_occurred = e;
			raise e
		except (
		KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError, InputOutputError) as e:
			logger.error(
				f"Error executing line index {current_original_index + 1} ({phase_name}: '{line_content_raw}'): {e}",
				exc_info=False)
			error_occurred = e
			if not hasattr(e, 'line_index') or e.line_index is None: e.line_index = current_original_index
			if not hasattr(e, 'line_content') or e.line_content is None: e.line_content = line_content_raw
			raise e
		except Exception as e:
			logger.exception(
				f"Unexpected error executing line index {current_original_index + 1} ({phase_name}: '{line_content_raw}')")
			error_occurred = e;
			new_e = KumirExecutionError(f"Неожиданная внутренняя ошибка: {type(e).__name__}", current_original_index,
			                            line_content_raw);
			raise new_e from e
		finally:
			if not processed_by_block and state_before is not None:
				state_after = interpreter.get_state();
				output_after = interpreter.output
				trace_entry = {"phase": phase_name, "commandIndex": current_original_index, "command": line_content_raw,
				               "stateBefore": state_before, "stateAfter": state_after,
				               "outputDelta": output_after[len(output_before):]}
				if error_occurred: trace_entry["error"] = str(error_occurred)
				trace.append(trace_entry)
				if progress_callback:
					callback_data = {"phase": phase_name, "commandIndex": current_original_index,
					                 "output": output_after,
					                 "robotPos": state_after.get("robot") if state_after else None}
					if error_occurred: callback_data["error"] = str(error_occurred)
					try:
						progress_callback(callback_data)
					except Exception as cb_err:
						logger.error(f"Error in progress callback: {cb_err}", exc_info=True)
			i = next_i_in_lines


def execute_line(line_raw, interpreter, current_original_index):
	""" Выполняет одну строку кода Кумира. """
	line = line_raw.strip();
	logger.debug(f"Executing single line index {current_original_index + 1}: '{line}'");
	# ROBOT_DEBUG: отладка execute_line
	with open('/tmp/robot_debug.log', 'a') as f:
		f.write(f"execute_line: processing '{line}'\n")
	lower_line = line.lower()
	env = interpreter.get_env_by_index(interpreter.get_current_env_index());
	robot = interpreter.robot
	try:
		type_match = None
		for type_kw in ALLOWED_TYPES:
			if re.match(rf"^{type_kw}(\s+.*|$)", lower_line): type_match = type_kw; break
		if type_match:
			if process_declaration(line_raw, env): return
		if lower_line == "использовать робот": logger.info(
			"Ignoring 'использовать Робот' command in backend execution."); return
		if ":=" in line: process_assignment(line_raw, interpreter); return
		if lower_line.startswith("вывод"): process_output(line_raw, interpreter); return
		if lower_line.startswith("ввод"): process_input(line_raw, interpreter); return
		if lower_line.startswith(("утв ", "дано ", "надо ")):
			if process_control_command(line_raw, interpreter): return
		if lower_line == "стоп": logger.info("Execution stopped by 'стоп' command."); raise KumirExecutionError(
			"Выполнение прервано командой 'стоп'.")
		if lower_line == "выход": logger.info("Raising 'Выход' exception."); raise KumirExecutionError("Выход")
		if lower_line == "пауза" or lower_line.startswith("ждать "):
			logger.info(f"Command '{lower_line}' ignored by backend (handled by frontend animation).")
			if interpreter.progress_callback:
				try:
					interpreter.progress_callback({'phase': 'pause', 'commandIndex': current_original_index})
				except Exception as cb_err:
					logger.error(f"Error in pause progress callback: {cb_err}")
			return
		if process_robot_command(line, robot): return
		# TODO: Implement algorithm calls
		# if process_algorithm_call(line_raw, interpreter, current_original_index): return
		logger.error(f"Unknown command or syntax error: '{line}'")
		raise KumirExecutionError(f"Неизвестная команда или синтаксическая ошибка.")
	except (KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError, InputOutputError,
	        KumirInputRequiredError) as e:
		if hasattr(e, 'line_index') and e.line_index is None: e.line_index = current_original_index
		if hasattr(e, 'line_content') and e.line_content is None: e.line_content = line_raw
		raise e
	except Exception as e:
		logger.exception(f"Unexpected error processing line index {current_original_index + 1}: '{line_raw}'")
		raise KumirExecutionError(f"Неожиданная ошибка: {e}", current_original_index, line_raw) from e

# FILE END: execution.py