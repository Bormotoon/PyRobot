"""
Модуль execution.py
@description Реализует функции для выполнения управляющих конструкций
языка KUMIR (циклы, условия) и диспетчеризацию отдельных команд.
"""
import logging
# Import RobotError if robot commands can raise specific errors
import re

from .declarations import process_declaration, process_assignment, process_output, process_input, ALLOWED_TYPES
from .robot_commands import process_robot_command  # Handles robot actions
from .safe_eval import safe_eval, get_eval_env, KumirEvalError  # For evaluating expressions

logger = logging.getLogger('KumirExecution')


# Define a specific exception for execution logic issues
class KumirExecutionError(Exception):
	pass


def process_control_command(line, env):
	"""
	Обрабатывает команды управления: утв, дано, надо.
	Вычисляет логическое выражение и генерирует исключение, если оно ложно.

	Args:
		line (str): Строка команды управления.
		env (dict): Окружение переменных.

	Returns:
		bool: True, если команда успешно обработана (условие истинно).

	Raises:
		KumirExecutionError: Если выражение не вычисляется или его результат ложен.
		KumirEvalError: Если ошибка при вычислении выражения.
	"""
	lower_line = line.lower().strip()
	keyword = None
	for kw in ["утв", "дано", "надо"]:
		if lower_line.startswith(kw):
			keyword = kw
			break

	if keyword:
		expr = line[len(keyword):].strip()
		if not expr:
			raise KumirExecutionError(f"Команда '{keyword}' требует логического выражения.")

		eval_env = get_eval_env(env)
		try:
			# safe_eval handles potential errors during evaluation itself
			result = safe_eval(expr, eval_env)
			logger.debug(f"Control command '{keyword}' evaluated '{expr}' -> {result}")
		except Exception as e:
			# Catch exceptions from safe_eval (like NameError, TypeError etc.)
			raise KumirEvalError(f"Ошибка вычисления выражения '{expr}' в команде '{keyword}': {e}")

		# Check the condition based on Kumir's boolean logic (да/нет or bool)
		condition = result if isinstance(result, bool) else (str(result).strip().lower() == "да")

		if not condition:
			logger.warning(f"Control command failed: '{keyword} {expr}' result is False.")
			raise KumirExecutionError(
				f"Отказ: условие '{expr}' в команде '{keyword}' не выполнено (результат: {result}).")

		logger.info(f"Control command '{keyword} {expr}' successful.")
		return True  # Indicate command was processed and condition met

	return False  # Line didn't match any control command


def process_if_block(lines, start_index, env, robot, interpreter):
	"""
	Обрабатывает блок условного оператора "если-то-[иначе]-все".

	Args:
		lines (list): Список всех строк кода блока (включая 'если').
		start_index (int): Индекс строки 'если'.
		env (dict): Окружение переменных.
		robot (SimulatedRobot): Объект робота.
		interpreter (KumirLanguageInterpreter): Контекст интерпретатора.

	Returns:
		int: Индекс строки, следующей за 'все'.

	Raises:
		KumirExecutionError: При синтаксических ошибках или ошибках выполнения.
		KumirEvalError: При ошибках вычисления условия.
	"""
	n = len(lines)
	header_line = lines[start_index].strip()
	if not header_line.lower().startswith("если"):
		# This should not happen if called correctly, but safeguard
		raise KumirExecutionError("Internal Error: process_if_block called without 'если'.")

	condition_expr = header_line[len("если"):].strip()
	i = start_index + 1
	series1_lines = []  # Lines for the 'то' branch
	series2_lines = []  # Lines for the 'иначе' branch
	current_series = None  # Track which branch we are appending lines to
	found_then = False
	found_else = False
	end_if_index = -1

	# --- Parsing the structure ---
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()

		if lower_line == "все":
			end_if_index = i
			break
		elif lower_line.startswith("то") and not found_then:
			found_then = True
			current_series = series1_lines
			content_after_then = line[len("то"):].strip()
			if content_after_then:
				current_series.append(content_after_then)  # Add content on the same line as 'то'
		elif lower_line.startswith("иначе") and found_then and not found_else:
			found_else = True
			current_series = series2_lines
			content_after_else = line[len("иначе"):].strip()
			if content_after_else:
				current_series.append(content_after_else)  # Add content on the same line as 'иначе'
		else:
			if current_series is not None:
				current_series.append(line)  # Append line to the current branch
			elif not found_then:
				# Still part of the condition (multi-line condition)
				condition_expr += " " + line
			else:
				# This case should ideally not be reached if structure is то/иначе/все
				raise KumirExecutionError(
					f"Неожиданная строка в блоке 'если': '{line}'. Ожидалось 'то', 'иначе' или 'все'.")
				i += 1

	# --- Validation ---
	if end_if_index == -1:
		raise KumirExecutionError("Отсутствует 'все' для завершения конструкции 'если'.")
	if not found_then:
		raise KumirExecutionError("Отсутствует 'то' в конструкции 'если'.")
	if not condition_expr:
		raise KumirExecutionError("Отсутствует условие после 'если'.")

	# --- Evaluation and Execution ---
	logger.debug(f"Evaluating 'если' condition: {condition_expr}")
	eval_env = get_eval_env(env)
	try:
		cond_value = safe_eval(condition_expr, eval_env)
	except Exception as e:
		raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'если': {e}")

	# Convert to boolean based on Kumir rules
	cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
	logger.info(f"'Если {condition_expr}' evaluated to {cond_bool}.")

	if cond_bool:
		logger.debug("Executing 'то' branch...")
		execute_lines(series1_lines, env, robot, interpreter)  # Recursively execute the branch
	elif found_else:
		logger.debug("Executing 'иначе' branch...")
		execute_lines(series2_lines, env, robot, interpreter)  # Recursively execute the branch
	else:
		logger.debug("Condition false, no 'иначе' branch.")

	return end_if_index + 1  # Return the index after 'все'


def process_select_block(lines, start_index, env, robot, interpreter):
	"""
	Обрабатывает блок оператора выбора "выбор-при-[иначе]-все".

	Args: See process_if_block
	Returns: See process_if_block
	Raises: See process_if_block
	"""
	n = len(lines)
	if not lines[start_index].strip().lower() == "выбор":
		raise KumirExecutionError("Internal Error: process_select_block called without 'выбор'.")

	i = start_index + 1
	branches = []  # List of tuples: (condition_expr, series_lines)
	else_series = []
	found_else = False
	end_select_index = -1

	# --- Parsing the structure ---
	current_branch_lines = None
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()

		if lower_line == "все":
			end_select_index = i
			break
		elif lower_line.startswith("при"):
			if found_else:
				raise KumirExecutionError("Ветка 'при' не может следовать после 'иначе' в 'выбор'.")
			parts = line.split(":", 1)
			if len(parts) != 2:
				raise KumirExecutionError(f"Неверный синтаксис ветки 'при': отсутствует ':' в строке '{line}'")

			cond_part = parts[0].strip()
			condition_expr = cond_part[len("при"):].strip()
			if not condition_expr:
				raise KumirExecutionError(f"Отсутствует условие после 'при' в строке '{line}'")

			series_line = parts[1].strip()
			current_branch_lines = [series_line] if series_line else []
			branches.append((condition_expr, current_branch_lines))

		elif lower_line.startswith("иначе"):
			if found_else:
				raise KumirExecutionError("Повторное использование 'иначе' в 'выбор'.")
			found_else = True
			current_branch_lines = else_series  # Switch context to else_series
			content_after_else = line[len("иначе"):].strip()
			if content_after_else:
				current_branch_lines.append(content_after_else)
		else:
			# Line belongs to the body of the current 'при' or 'иначе' branch
			if current_branch_lines is not None:
				current_branch_lines.append(line)
			else:
				raise KumirExecutionError(
					f"Неожиданная строка в блоке 'выбор': '{line}'. Ожидалось 'при', 'иначе' или 'все'.")
		i += 1

	# --- Validation ---
	if end_select_index == -1:
		raise KumirExecutionError("Отсутствует 'все' для завершения конструкции 'выбор'.")
	if not branches and not found_else:
		logger.warning("Конструкция 'выбор' не содержит веток 'при' или 'иначе'.")

	# --- Evaluation and Execution ---
	eval_env = get_eval_env(env)
	executed_branch = False

	# Evaluate 'при' branches
	for idx, (condition_expr, series) in enumerate(branches):
		logger.debug(f"Evaluating 'при' condition #{idx + 1}: {condition_expr}")
		try:
			cond_value = safe_eval(condition_expr, eval_env)
		except Exception as e:
			raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'выбор': {e}")

		cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
		logger.info(f"'При {condition_expr}' evaluated to {cond_bool}.")

		if cond_bool:
			logger.debug(f"Executing 'при' branch #{idx + 1}...")
			execute_lines(series, env, robot, interpreter)
			executed_branch = True
			break  # Execute only the first matching branch

	# Execute 'иначе' if no 'при' matched and 'иначе' exists
	if not executed_branch and found_else:
		logger.debug("Executing 'иначе' branch...")
		execute_lines(else_series, env, robot, interpreter)

	return end_select_index + 1  # Return index after 'все'


def process_loop_for(lines, start_index, env, robot, interpreter):
	"""Обрабатывает цикл 'нц для ... кц'."""
	n = len(lines)
	header_line = lines[start_index].strip()
	# Example: нц для i от 1 до 10 шаг 2
	match = re.match(r"нц\s+для\s+([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)\s+от\s+(.+)\s+до\s+(.+?)(?:\s+шаг\s+(.+))?$",
					 header_line.lower())
	if not match:
		raise KumirExecutionError(f"Неверный синтаксис цикла 'нц для': {header_line}")

	var_name, start_expr, end_expr, step_expr = match.groups()
	step_expr = step_expr if step_expr else "1"  # Default step is 1

	# --- Find loop body and 'кц' ---
	i = start_index + 1
	loop_body = []
	end_loop_index = -1
	nesting_level = 0  # Handle nested loops correctly
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()
		# Check for nested loop start/end
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i
				break
			else:
				nesting_level -= 1
		loop_body.append(line)  # Append line regardless of nesting for now
		i += 1

	if end_loop_index == -1:
		raise KumirExecutionError("Отсутствует 'кц' для завершения цикла 'нц для'.")

	# --- Evaluate loop parameters ---
	logger.debug(f"Evaluating 'нц для' params: start='{start_expr}', end='{end_expr}', step='{step_expr}'")
	eval_env = get_eval_env(env)
	try:
		start_val = int(safe_eval(start_expr, eval_env))
		end_val = int(safe_eval(end_expr, eval_env))
		step_val = int(safe_eval(step_expr, eval_env))
	except Exception as e:
		raise KumirEvalError(
			f"Ошибка вычисления параметров цикла 'для' ('{start_expr}', '{end_expr}', '{step_expr}'): {e}")

	if step_val == 0:
		raise KumirExecutionError("Шаг в цикле 'для' не может быть равен нулю.")

	# --- Execute Loop ---
	# Check if variable exists, create if not (Kumir allows implicit local loop variables)
	# Note: Proper scoping might require more complex environment handling
	original_value = None
	was_declared = var_name in env
	if was_declared:
		original_value = env[var_name]['value']  # Save original value if overwriting global/outer scope
		if env[var_name]['type'] != 'цел':
			logger.warning(f"Loop variable '{var_name}' has type '{env[var_name]['type']}', expected 'цел'.")
	else:
		# Implicitly declare as local integer for the loop duration
		env[var_name] = {"type": "цел", "value": None, "kind": "local", "is_table": False}
		logger.debug(f"Implicitly declared loop variable '{var_name}' as local 'цел'.")

	current = start_val
	logger.info(f"Starting 'нц для {var_name}' from {start_val} to {end_val} step {step_val}.")
	iteration_count = 0
	try:
		# Loop condition depends on step direction
		condition_met = (step_val > 0 and current <= end_val) or \
						(step_val < 0 and current >= end_val)

		while condition_met:
			iteration_count += 1
			env[var_name]["value"] = current  # Update loop variable
			logger.debug(f"Loop 'для {var_name}' iteration {iteration_count}, value = {current}")

			try:
				# Execute the loop body
				execute_lines(loop_body, env, robot, interpreter)
			except KumirExecutionError as e:
				if str(e).startswith("Выход"):  # Check if it's an 'выход' command exception
					logger.info("Команда 'выход' прервала цикл 'для'.")
					break  # Exit the while loop
				else:
					raise e  # Re-raise other execution errors

			current += step_val
			# Update condition for next iteration
			condition_met = (step_val > 0 and current <= end_val) or \
							(step_val < 0 and current >= end_val)
	finally:
		# Restore original variable value or remove implicit local variable
		if was_declared:
			env[var_name]['value'] = original_value
			logger.debug(f"Restored original value for variable '{var_name}'.")
		elif var_name in env:  # Only delete if implicitly created by this loop
			del env[var_name]
			logger.debug(f"Removed implicitly declared loop variable '{var_name}'.")

	logger.info(f"Finished 'нц для {var_name}' after {iteration_count} iterations.")
	return end_loop_index + 1  # Return index after 'кц'


def process_loop_while(lines, start_index, env, robot, interpreter):
	"""Обрабатывает цикл 'нц пока ... кц'."""
	n = len(lines)
	header_line = lines[start_index].strip()
	match = re.match(r"нц\s+пока\s+(.+)", header_line.lower())
	if not match:
		raise KumirExecutionError(f"Неверный синтаксис цикла 'нц пока': {header_line}")

	condition_expr = match.group(1).strip()
	if not condition_expr:
		raise KumirExecutionError("Отсутствует условие после 'нц пока'.")

	# --- Find loop body and 'кц' ---
	i = start_index + 1
	loop_body = []
	end_loop_index = -1
	nesting_level = 0
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i
				break
			else:
				nesting_level -= 1
		loop_body.append(line)
		i += 1

	if end_loop_index == -1:
		raise KumirExecutionError("Отсутствует 'кц' для завершения цикла 'нц пока'.")

	# --- Execute Loop ---
	logger.info(f"Starting 'нц пока {condition_expr}'.")
	iteration_count = 0
	while True:  # Loop indefinitely until condition is false or 'выход'
		iteration_count += 1
		eval_env = get_eval_env(env)
		try:
			cond_value = safe_eval(condition_expr, eval_env)
		except Exception as e:
			raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в цикле 'пока': {e}")

		cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
		logger.debug(f"Loop 'пока' condition '{condition_expr}' -> {cond_bool} (Iteration {iteration_count})")

		if not cond_bool:
			logger.debug("Condition false, exiting 'нц пока'.")
			break  # Exit loop if condition is false

		# Execute loop body
		try:
			execute_lines(loop_body, env, robot, interpreter)
		except KumirExecutionError as e:
			if str(e).startswith("Выход"):
				logger.info("Команда 'выход' прервала цикл 'пока'.")
				break  # Exit the while loop
			else:
				raise e  # Re-raise other execution errors

	logger.info(f"Finished 'нц пока {condition_expr}' after {iteration_count - 1} successful iterations.")
	return end_loop_index + 1  # Return index after 'кц'


def process_loop_n_times(lines, start_index, env, robot, interpreter):
	"""Обрабатывает цикл 'нц <N> раз ... кц'."""
	n = len(lines)
	header_line = lines[start_index].strip()
	match = re.match(r"нц\s+(\d+)\s+раз", header_line.lower())
	if not match:
		raise KumirExecutionError(f"Неверный синтаксис цикла 'N раз': {header_line}")

	try:
		count = int(match.group(1))
	except ValueError:
		raise KumirExecutionError(f"Неверное число повторений в цикле 'N раз': {match.group(1)}")

	if count < 0:
		raise KumirExecutionError(f"Число повторений в цикле 'N раз' не может быть отрицательным: {count}")

	# --- Find loop body and 'кц' ---
	i = start_index + 1
	loop_body = []
	end_loop_index = -1
	nesting_level = 0
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i
				break
			else:
				nesting_level -= 1
		loop_body.append(line)
		i += 1

	if end_loop_index == -1:
		raise KumirExecutionError("Отсутствует 'кц' для завершения цикла 'N раз'.")

	# --- Execute Loop ---
	logger.info(f"Starting 'нц {count} раз'.")
	for iteration in range(count):
		logger.debug(f"Loop 'N раз' iteration {iteration + 1}/{count}")
		try:
			execute_lines(loop_body, env, robot, interpreter)
		except KumirExecutionError as e:
			if str(e).startswith("Выход"):
				logger.info(f"Команда 'выход' прервала цикл 'N раз' на итерации {iteration + 1}.")
				break  # Exit the for loop
			else:
				raise e  # Re-raise other execution errors

	logger.info(f"Finished 'нц {count} раз'.")
	return end_loop_index + 1


def process_loop_infinite(lines, start_index, env, robot, interpreter):
	"""Обрабатывает бесконечный цикл 'нц ... кц'."""
	n = len(lines)
	if not lines[start_index].strip().lower() == "нц":
		raise KumirExecutionError("Internal Error: process_loop_infinite called without 'нц'.")

	# --- Find loop body and 'кц' ---
	i = start_index + 1
	loop_body = []
	end_loop_index = -1
	nesting_level = 0
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i
				break
			else:
				nesting_level -= 1
		loop_body.append(line)
		i += 1

	if end_loop_index == -1:
		raise KumirExecutionError("Отсутствует 'кц' для завершения бесконечного цикла 'нц'.")

	# --- Execute Loop ---
	logger.info("Starting infinite 'нц' loop (requires 'выход').")
	iteration_count = 0
	while True:  # Runs forever until 'выход'
		iteration_count += 1
		logger.debug(f"Infinite loop 'нц' iteration {iteration_count}")
		try:
			execute_lines(loop_body, env, robot, interpreter)
		except KumirExecutionError as e:
			if str(e).startswith("Выход"):
				logger.info(f"Команда 'выход' прервала бесконечный цикл 'нц' на итерации {iteration_count}.")
				break  # Exit the while loop
			else:
				raise e  # Re-raise other execution errors
	# Add a safeguard against true infinite loops in practice?
	# Maybe limit iterations in testing environments?
	# if iteration_count > 10000: # Example safeguard
	#     raise KumirExecutionError("Превышен лимит итераций для бесконечного цикла 'нц'.")

	logger.info(f"Finished infinite 'нц' loop.")
	return end_loop_index + 1


def process_algorithm_call(line, env, robot, interpreter):
	"""
	Обрабатывает вызов другого алгоритма (процедуры).
	Простая реализация: ищет имя алгоритма и выполняет его тело.
	Не обрабатывает параметры.

	Args: See execute_line
	Returns:
		bool: True if an algorithm call was processed, False otherwise.
	"""
	line_strip = line.strip()
	# Simple check: does the line match a defined algorithm name?
	# Improve: handle calls with parameters like 'алгоритм(a, b)' later
	call_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)(?:\(.*\))?$", line_strip)

	if call_match:
		algo_name = call_match.group(1)
		if algo_name in interpreter.algorithms:
			logger.info(f"Executing algorithm call: {algo_name}")
			alg_to_run = interpreter.algorithms[algo_name]
			# Execute the called algorithm's body
			# Note: This needs proper handling of scope (local vs global) and parameters
			execute_lines(alg_to_run["body"], env, robot, interpreter)  # Pass current env, robot, interpreter
			logger.info(f"Finished algorithm call: {algo_name}")
			return True
	return False


def execute_lines(lines, env, robot, interpreter=None):
	"""
	Выполняет список строк кода (например, тело алгоритма или ветку).

	Args:
		lines (list): Список строк кода для выполнения.
		env (dict): Окружение переменных.
		robot (SimulatedRobot): Объект робота.
		interpreter (KumirLanguageInterpreter, optional): Контекст интерпретатора.

	Raises:
		KumirExecutionError, KumirEvalError, RobotError: При ошибках выполнения.
		Propagates exceptions from called functions.
	"""
	i = 0
	n = len(lines)
	while i < n:
		line = lines[i].strip()
		if not line:  # Skip empty lines
			i += 1
			continue

		lower_line = line.lower()
		processed = False  # Flag to check if the line was handled by a block structure

		# --- Block Structures ---
		if lower_line.startswith("если"):
			i = process_if_block(lines, i, env, robot, interpreter)
			processed = True
		elif lower_line == "выбор":  # Only startswith 'выбор' might be too broad
			i = process_select_block(lines, i, env, robot, interpreter)
			processed = True
		elif lower_line.startswith("нц"):
			# Determine loop type
			if lower_line.startswith("нц для"):
				i = process_loop_for(lines, i, env, robot, interpreter)
			elif lower_line.startswith("нц пока"):
				i = process_loop_while(lines, i, env, robot, interpreter)
			elif re.match(r"нц\s+\d+\s+раз", lower_line):
				i = process_loop_n_times(lines, i, env, robot, interpreter)
			elif lower_line == "нц":  # Simple 'нц' means infinite loop
				i = process_loop_infinite(lines, i, env, robot, interpreter)
			else:
				raise KumirExecutionError(f"Неизвестный тип цикла 'нц': {line}")
			processed = True

		# --- Single Line Commands ---
		if not processed:
			execute_line(line, env, robot, interpreter)
			i += 1  # Move to the next line


def execute_line(line, env, robot, interpreter=None):
	"""
	Выполняет одну строку кода.

	Args: See execute_lines
	Raises: Propagates exceptions from processors.
	"""
	logger.debug(f"Executing line: '{line}'")
	line_strip = line.strip()
	lower_line = line_strip.lower()

	# Check different command types in order
	# 1. Declaration
	for type_keyword in ALLOWED_TYPES:
		if lower_line.startswith(type_keyword + " ") or lower_line == type_keyword:
			# Check avoids matching keywords like 'целый' if only 'цел' is allowed
			if re.match(rf"^{type_keyword}(?:\s+.*|$)", lower_line):
				process_declaration(line_strip, env)
				return

	# 2. Assignment
	if ":=" in line_strip:
		process_assignment(line_strip, env)
		return

	# 3. Output
	if lower_line.startswith("вывод"):
		# Pass interpreter context to buffer output
		process_output(line_strip, env, interpreter)
		return

	# 4. Input (Not fully implemented for web server context)
	if lower_line.startswith("ввод"):
		process_input(line_strip, env)  # Needs proper async handling
		logger.warning("Команда 'ввод' используется, но может не работать корректно в веб-окружении.")
		return

	# 5. Control Commands (утв, дано, надо)
	if lower_line.startswith(("утв", "дано", "надо")):
		if process_control_command(line_strip, env):
			return  # Command processed (condition was true)
	# If False, process_control_command already raised error if needed

	# 6. Flow Control (стоп, выход, пауза)
	if lower_line == "стоп":
		logger.info("Команда 'стоп' обнаружена.")
		raise KumirExecutionError("Выполнение прервано командой 'стоп'.")
	if lower_line == "выход":
		logger.info("Команда 'выход' обнаружена.")
		raise KumirExecutionError("Выход")  # Special exception caught by loops/algorithms

	if lower_line == "пауза":
		logger.info("Команда 'пауза' обнаружена (проигнорирована в неинтерактивном режиме).")
		# Removed blocking input() call
		# In a full implementation, this should signal the frontend.
		return

	# 7. Robot Commands
	if process_robot_command(line_strip, robot):  # Pass robot object
		return  # Robot command was handled

	# 8. Algorithm Call (if interpreter context provided)
	if interpreter and process_algorithm_call(line_strip, env, robot, interpreter):
		return

	# If none of the above matched
	logger.error(f"Неизвестная команда или синтаксическая ошибка: {line_strip}")
	raise KumirExecutionError(f"Неизвестная команда: {line_strip}")
