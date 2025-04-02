# FILE START: execution.py
"""
Модуль execution.py
@description Реализует функции для выполнения управляющих конструкций
языка KUMIR (циклы, условия) и диспетчеризацию отдельных команд.
"""
import logging
import re
import time  # Добавим для возможной паузы (хотя на сервере не рекомендуется)

# Импорты из нашего проекта
from .declarations import process_declaration, process_assignment, process_output, ALLOWED_TYPES, \
	DeclarationError, AssignmentError, InputOutputError
from .robot_commands import process_robot_command
from .robot_state import RobotError
# Используем новый safe_eval и его исключение
from .safe_eval import safe_eval, KumirEvalError

logger = logging.getLogger('KumirExecution')


class KumirExecutionError(Exception):
	"""Основное исключение для ошибок выполнения (не вычисления)."""
	pass


def process_control_command(line, env, robot=None):  # Добавляем robot
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
			# Используем новый safe_eval
			result = safe_eval(expr, env, robot)
			logger.debug(f"Control '{keyword}' evaluated '{expr}' -> {result} (type: {type(result)})")
		except KumirEvalError as e:
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
			raise KumirExecutionError(
				f"Отказ: условие '{expr}' в команде '{keyword}' ложно (результат: {failure_reason}).")
		else:
			logger.info(f"Control command success: '{keyword} {expr}' is True.")
			return True  # Команда обработана

	return False  # Это была не команда утв/дано/надо


def process_if_block(lines, start_index, env, robot, interpreter):
	""" Обрабатывает блок "если-то-[иначе]-все". """
	n = len(lines)
	header_line = lines[start_index].strip()
	# Проверка, что мы действительно начинаем с "если", хотя она избыточна, если вызывается правильно
	if not header_line.lower().startswith("если"):
		raise KumirExecutionError("Внутренняя ошибка: process_if_block вызван не для строки 'если'.")

	condition_expr = header_line[len("если"):].strip()
	i = start_index + 1
	series1_lines = []  # Блок "то"
	series2_lines = []  # Блок "иначе"
	current_series = None
	found_then = False
	found_else = False
	end_if_index = -1

	# --- Парсинг блока ---
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()

		if lower_line == "все":
			# Нашли конец блока "если"
			end_if_index = i
			logger.debug(f"Found 'все' for 'если' at index {i}")
			break
		elif lower_line.startswith("то") and not found_then:
			# Начало блока "то"
			found_then = True
			current_series = series1_lines
			# Добавляем остаток строки после "то", если он есть
			content_after_then = line[len("то"):].strip()
			if content_after_then:
				current_series.append(content_after_then)
			logger.debug(f"Found 'то' at index {i}. Content after: '{content_after_then}'")
		elif lower_line.startswith("иначе") and found_then and not found_else:
			# Начало блока "иначе"
			found_else = True
			current_series = series2_lines
			# Добавляем остаток строки после "иначе", если он есть
			content_after_else = line[len("иначе"):].strip()
			if content_after_else:
				current_series.append(content_after_else)
			logger.debug(f"Found 'иначе' at index {i}. Content after: '{content_after_else}'")
		else:
			# Обычная строка внутри блока "то" или "иначе"
			if current_series is not None:
				current_series.append(line)
			elif not found_then:
				# Если 'то' еще не было, это продолжение условия 'если' (многострочное?)
				# В стандартном Кумире условие обычно однострочное. Обработаем как ошибку или объединим?
				# Будем считать ошибкой для строгости.
				logger.warning(f"Unexpected line '{line}' inside 'если' before 'то'. Assuming part of condition.")
				condition_expr += " " + line  # Попытаемся объединить, но это может быть неверно  # raise KumirExecutionError(f"Неожиданная строка '{line}' внутри 'если' до 'то'.")
			else:
				# Строка после 'то'/'иначе', но не 'все'.
				# Это должно быть тело блока
				logger.error(f"Internal logic error: Line '{line}' encountered unexpectedly in 'если' parsing.")
				raise KumirExecutionError(f"Неожиданная строка '{line}' при разборе блока 'если'.")
		i += 1

	# --- Валидация структуры ---
	if end_if_index == -1:
		raise KumirExecutionError(f"Не найден 'все' для блока 'если', начавшегося на строке {start_index + 1}.")
	if not found_then:
		raise KumirExecutionError(f"Не найдено 'то' в блоке 'если', начавшемся на строке {start_index + 1}.")
	if not condition_expr:
		raise KumirExecutionError(f"Отсутствует условие после 'если' на строке {start_index + 1}.")

	# --- Вычисление условия ---
	logger.debug(f"Evaluating 'если' condition: '{condition_expr}'")
	try:
		# Используем новый safe_eval
		cond_value = safe_eval(condition_expr, env, robot)
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'если': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating 'если' condition '{condition_expr}': {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка в условии 'если': {e}")

	# Преобразуем результат к булевому типу
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
		execute_lines(series1_lines, env, robot, interpreter)
	elif found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(series2_lines)}).")
		execute_lines(series2_lines, env, robot, interpreter)
	else:
		logger.debug("Condition is false, no 'иначе' block to execute.")

	# Возвращаем индекс строки, следующей за 'все'
	return end_if_index + 1


def process_select_block(lines, start_index, env, robot, interpreter):
	""" Обрабатывает блок "выбор-при-[иначе]-все". """
	n = len(lines)
	if not lines[start_index].strip().lower() == "выбор":
		raise KumirExecutionError("Внутренняя ошибка: process_select_block вызван не для строки 'выбор'.")

	i = start_index + 1
	branches = []  # Список кортежей: (condition_expr, series_lines)
	else_series = []
	found_else = False
	end_select_index = -1
	current_branch_lines = None  # Куда добавлять строки: в текущую ветку 'при' или в 'иначе'

	# --- Парсинг блока ---
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()

		if lower_line == "все":
			end_select_index = i
			logger.debug(f"Found 'все' for 'выбор' at index {i}")
			break
		elif lower_line.startswith("при"):
			if found_else:
				raise KumirExecutionError("Обнаружена ветка 'при' после 'иначе' в блоке 'выбор'.")

			# Ищем двоеточие, разделяющее условие и первую команду ветки
			parts = line.split(":", 1)
			if len(parts) != 2:
				raise KumirExecutionError(f"Отсутствует ':' после условия в ветке 'при': '{line}'")

			cond_part = parts[0].strip()
			condition_expr = cond_part[len("при"):].strip()
			if not condition_expr:
				raise KumirExecutionError(f"Отсутствует условие после 'при' в строке: '{line}'")

			# Первая команда ветки (может быть пустой)
			first_command = parts[1].strip()
			current_branch_lines = [first_command] if first_command else []
			branches.append({"condition": condition_expr, "body": current_branch_lines})
			logger.debug(f"Found 'при' branch with condition '{condition_expr}'. First command: '{first_command}'")

		elif lower_line.startswith("иначе"):
			if found_else:
				raise KumirExecutionError("Обнаружено повторное 'иначе' в блоке 'выбор'.")
			if not branches:
				logger.warning(
					"Блок 'иначе' найден до каких-либо веток 'при' в 'выбор'.")  # Это синтаксически допустимо, но странно

			found_else = True
			current_branch_lines = else_series  # Теперь строки добавляются в блок 'иначе'
			# Добавляем остаток строки после "иначе", если он есть
			content_after_else = line[len("иначе"):].strip()
			if content_after_else:
				current_branch_lines.append(content_after_else)
			logger.debug(f"Found 'иначе' block. Content after: '{content_after_else}'")

		else:
			# Обычная строка внутри ветки 'при' или 'иначе'
			if current_branch_lines is not None:
				current_branch_lines.append(line)
			else:
				# Строка до первого 'при' или 'иначе' (после 'выбор') - ошибка
				raise KumirExecutionError(f"Неожиданная строка '{line}' внутри 'выбор' до начала веток 'при'/'иначе'.")
		i += 1

	# --- Валидация ---
	if end_select_index == -1:
		raise KumirExecutionError(f"Не найден 'все' для блока 'выбор', начавшегося на строке {start_index + 1}.")
	if not branches and not found_else:
		logger.warning("Конструкция 'выбор-все' не содержит веток 'при' или блока 'иначе'. Блок пуст.")

	# --- Выполнение ---
	executed = False
	for idx, branch in enumerate(branches):
		condition_expr = branch["condition"]
		series = branch["body"]
		logger.debug(f"Evaluating 'при' condition #{idx + 1}: {condition_expr}")
		try:
			# Используем новый safe_eval
			cond_value = safe_eval(condition_expr, env, robot)
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в ветке 'при' блока 'выбор': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating 'при' condition '{condition_expr}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка в условии 'при': {e}")

		# Преобразуем к bool
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
			execute_lines(series, env, robot, interpreter)
			executed = True
			break  # Выполняется только первая подошедшая ветка 'при'

	if not executed and found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(else_series)}).")
		execute_lines(else_series, env, robot, interpreter)
	elif not executed:
		logger.debug("No 'при' branch matched and no 'иначе' block found.")

	return end_select_index + 1


def process_loop_for(lines, start_index, env, robot, interpreter):
	""" Обрабатывает цикл 'нц для ... кц'. """
	n = len(lines)
	header_line = lines[start_index].strip()
	# Паттерн для разбора 'нц для <вар> от <нач> до <кон> [шаг <шаг>]'
	# Используем нежадный поиск '(.+?)' для 'до', чтобы 'шаг' не попал в конец
	match = re.match(
		r"нц\s+для\s+([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)\s+от\s+(.+?)\s+до\s+(.+?)(?:\s+шаг\s+(.+))?$",
		header_line, re.IGNORECASE)
	if not match:
		raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц для': {header_line}")

	var_name, start_expr, end_expr, step_expr = match.groups()
	# Шаг по умолчанию 1, если не указан
	step_expr = step_expr.strip() if step_expr else "1"

	logger.debug(f"Parsing 'нц для': var='{var_name}', from='{start_expr}', to='{end_expr}', step='{step_expr}'")

	# --- Поиск тела цикла и 'кц' ---
	i = start_index + 1
	loop_body = []
	end_loop_index = -1
	nesting_level = 0  # Для обработки вложенных циклов
	while i < n:
		line = lines[i].strip()
		lower_line = line.lower()

		# Проверяем на начало/конец вложенных циклов 'нц'/'кц'
		if lower_line.startswith("нц"):
			nesting_level += 1
			logger.debug(f"Nested 'нц' found at index {i}, nesting level: {nesting_level}")
		elif lower_line == "кц":
			if nesting_level == 0:
				# Нашли 'кц' для нашего цикла
				end_loop_index = i
				logger.debug(f"Found matching 'кц' for 'нц для' at index {i}")
				break
			else:
				# Это 'кц' для вложенного цикла
				nesting_level -= 1
				logger.debug(f"Nested 'кц' found at index {i}, nesting level: {nesting_level}")

		# Добавляем строку в тело текущего цикла
		loop_body.append(line)
		i += 1

	if end_loop_index == -1:
		raise KumirExecutionError(f"Не найден 'кц' для цикла 'нц для', начавшегося на строке {start_index + 1}.")

	# --- Вычисление параметров цикла ---
	try:
		# Используем новый safe_eval
		start_val_raw = safe_eval(start_expr, env, robot)
		end_val_raw = safe_eval(end_expr, env, robot)
		step_val_raw = safe_eval(step_expr, env, robot)

		# Преобразуем к целым числам, как требует Кумир
		try:
			start_val = int(start_val_raw)
			end_val = int(end_val_raw)
			step_val = int(step_val_raw)
		except (ValueError, TypeError) as conv_e:
			raise KumirEvalError(
				f"Параметры цикла 'для' (начало, конец, шаг) должны быть целыми числами. Ошибка преобразования: {conv_e}")

	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления параметров цикла 'нц для': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating 'нц для' params: {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка в параметрах 'нц для': {e}")

	if step_val == 0:
		raise KumirExecutionError("Шаг в цикле 'нц для' не может быть равен нулю.")

	# --- Выполнение цикла ---
	original_value = None
	was_declared = var_name in env

	# Сохраняем оригинальное значение переменной, если она была объявлена
	if was_declared:
		if env[var_name].get("is_table"):
			raise KumirExecutionError(f"Переменная цикла '{var_name}' не может быть таблицей.")
		if env[var_name]["type"] != "цел":
			logger.warning(
				f"Переменная цикла '{var_name}' имеет тип '{env[var_name]['type']}', но будет использоваться как 'цел'.")  # Можно либо выдать ошибку, либо разрешить, Кумир часто прощает это. Разрешим с предупреждением.
		original_value = env[var_name].get('value')
		logger.debug(f"Loop variable '{var_name}' exists. Original value: {original_value}")
	else:
		# Если переменная не была объявлена, создаем ее локально на время цикла
		env[var_name] = {"type": "цел", "value": None, "kind": "local_loop", "is_table": False}
		logger.debug(f"Loop variable '{var_name}' created locally for the loop.")

	current = start_val
	logger.info(f"Starting 'нц для {var_name}' from {start_val} to {end_val} step {step_val}.")
	iteration_count = 0

	try:
		while True:
			# Проверяем условие входа/продолжения
			if step_val > 0:
				if current > end_val: break
			else:  # step_val < 0
				if current < end_val: break

			iteration_count += 1
			# Устанавливаем текущее значение переменной цикла
			env[var_name]["value"] = current
			logger.debug(f"'для {var_name}' iteration {iteration_count}, value = {current}")

			# Выполняем тело цикла
			try:
				execute_lines(loop_body, env, robot, interpreter)
			except KumirExecutionError as exit_e:
				# Обрабатываем команду 'выход'
				if str(exit_e) == "Выход":
					logger.info(f"Команда 'выход' прервала цикл 'нц для {var_name}' на итерации {iteration_count}.")
					break  # Выходим из while True
				else:
					raise exit_e  # Пробрасываем другие ошибки выполнения
			except Exception as body_e:
				# Ловим ошибки из тела цикла
				logger.error(f"Error inside 'нц для {var_name}' body (iteration {iteration_count}): {body_e}",
							 exc_info=True)
				# Пробрасываем как ошибку выполнения
				raise KumirExecutionError(f"Ошибка в теле цикла 'для {var_name}': {body_e}")

			# Переходим к следующему значению
			current += step_val

		# Добавим защиту от слишком длинных циклов (опционально)  # if iteration_count > 100000: # Примерный лимит  #     raise KumirExecutionError(f"Превышен лимит итераций ({iteration_count}) для цикла 'нц для {var_name}'.")


	finally:
		# Восстанавливаем/удаляем переменную цикла после завершения
		if was_declared:
			env[var_name]['value'] = original_value
			logger.debug(f"Restored original value for '{var_name}'.")
		elif var_name in env and env[var_name].get("kind") == "local_loop":
			# Удаляем переменную, если она была создана локально для цикла
			del env[var_name]
			logger.debug(f"Removed temporary loop variable '{var_name}'.")  # else: непредвиденная ситуация

	logger.info(f"Finished 'нц для {var_name}' after {iteration_count} iterations.")
	return end_loop_index + 1


def process_loop_while(lines, start_index, env, robot, interpreter):
	""" Обрабатывает цикл 'нц пока ... кц'. """
	n = len(lines)
	header_line = lines[start_index].strip()
	match = re.match(r"нц\s+пока\s+(.+)", header_line, re.IGNORECASE)
	if not match:
		raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц пока': {header_line}")

	condition_expr = match.group(1).strip()
	if not condition_expr:
		raise KumirExecutionError("Отсутствует условие после 'нц пока'.")

	logger.debug(f"Parsing 'нц пока': condition='{condition_expr}'")

	# --- Поиск тела цикла и 'кц' ---
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
		raise KumirExecutionError(f"Не найден 'кц' для цикла 'нц пока', начавшегося на строке {start_index + 1}.")

	# --- Выполнение цикла ---
	logger.info(f"Starting 'нц пока {condition_expr}'.")
	iteration_count = 0
	while True:
		iteration_count += 1
		# --- Вычисление условия ---
		try:
			# Используем новый safe_eval
			cond_value = safe_eval(condition_expr, env, robot)
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в цикле 'нц пока': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating 'нц пока' condition '{condition_expr}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка в условии 'нц пока': {e}")

		# Преобразуем к bool
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

		# Если условие ложно, выходим из цикла
		if not cond_bool:
			logger.debug("Condition is false, exiting 'нц пока'.")
			break

		# Выполняем тело цикла
		try:
			execute_lines(loop_body, env, robot, interpreter)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала цикл 'нц пока' на итерации {iteration_count}.")
				break  # Выходим из while True
			else:
				raise exit_e
		except Exception as body_e:
			logger.error(f"Error inside 'нц пока' body (iteration {iteration_count}): {body_e}", exc_info=True)
			raise KumirExecutionError(f"Ошибка в теле цикла 'пока': {body_e}")

	# Защита от бесконечных циклов  # if iteration_count > 100000: # Примерный лимит  #      raise KumirExecutionError(f"Превышен лимит итераций ({iteration_count}) для цикла 'нц пока {condition_expr}'.")

	logger.info(f"Finished 'нц пока {condition_expr}' after {iteration_count - 1} successful iterations.")
	return end_loop_index + 1


def process_loop_n_times(lines, start_index, env, robot, interpreter):
	""" Обрабатывает цикл 'нц <N> раз ... кц'. """
	n = len(lines)
	header_line = lines[start_index].strip()
	# Используем (.+) для выражения N, чтобы потом вычислить его
	match = re.match(r"нц\s+(.+?)\s+раз", header_line, re.IGNORECASE)
	if not match:
		raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц N раз': {header_line}")

	count_expr = match.group(1).strip()
	logger.debug(f"Parsing 'нц N раз': count_expr='{count_expr}'")

	# --- Вычисляем количество повторений N ---
	try:
		# Используем новый safe_eval
		count_raw = safe_eval(count_expr, env, robot)
		try:
			count = int(count_raw)
		except (ValueError, TypeError):
			raise KumirEvalError(
				f"Количество повторений '{count_expr}' (вычислено как '{count_raw}') не является целым числом.")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления количества повторений '{count_expr}' в цикле 'нц N раз': {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating 'N раз' count '{count_expr}': {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка в количестве повторений 'нц N раз': {e}")

	if count < 0:
		# В Кумире цикл с отрицательным числом раз просто не выполняется
		logger.warning(f"Число повторений в 'нц {count} раз' отрицательное. Цикл не будет выполнен.")
		count = 0  # Не выполняем ни разу

	# --- Поиск тела цикла и 'кц' ---
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
		raise KumirExecutionError(f"Не найден 'кц' для цикла 'нц N раз', начавшегося на строке {start_index + 1}.")

	# --- Выполнение цикла ---
	logger.info(f"Starting 'нц {count} раз'.")
	for iteration in range(count):
		current_iteration = iteration + 1
		logger.debug(f"'нц N раз' iteration {current_iteration}/{count}")

		try:
			execute_lines(loop_body, env, robot, interpreter)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала цикл 'нц N раз' на итерации {current_iteration}.")
				break  # Выходим из for
			else:
				raise exit_e
		except Exception as body_e:
			logger.error(f"Error inside 'нц N раз' body (iteration {current_iteration}): {body_e}", exc_info=True)
			raise KumirExecutionError(f"Ошибка в теле цикла 'N раз': {body_e}")

	logger.info(f"Finished 'нц {count} раз'.")
	return end_loop_index + 1


def process_loop_infinite(lines, start_index, env, robot, interpreter):
	""" Обрабатывает 'бесконечный' цикл 'нц ... кц'. """
	n = len(lines)
	# Простая проверка, что это действительно 'нц' без условий
	header_line = lines[start_index].strip()
	if not header_line.lower() == "нц":
		raise KumirExecutionError("Внутренняя ошибка: process_loop_infinite вызван не для 'нц'.")

	logger.debug("Parsing infinite 'нц' loop.")

	# --- Поиск тела цикла и 'кц' ---
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
		raise KumirExecutionError(f"Не найден 'кц' для цикла 'нц', начавшегося на строке {start_index + 1}.")

	# --- Выполнение цикла ---
	logger.info("Starting infinite 'нц' loop.")
	iteration_count = 0
	# Нужна защита от реального бесконечного цикла на сервере!
	# MAX_ITERATIONS = 100000 # Определить константу где-то выше
	MAX_DURATION_S = 10  # Максимальное время выполнения цикла в секундах

	start_time = time.time()

	while True:
		iteration_count += 1
		logger.debug(f"Infinite 'нц' loop iteration {iteration_count}")

		# Проверка максимального времени выполнения
		current_time_exec = time.time()
		if current_time_exec - start_time > MAX_DURATION_S:
			logger.error(
				f"Infinite loop 'нц' exceeded max duration ({MAX_DURATION_S}s) after {iteration_count} iterations.")
			raise KumirExecutionError(f"Превышено максимальное время выполнения ({MAX_DURATION_S}с) для цикла 'нц'.")

		# Проверка максимального числа итераций (если используется)
		# if iteration_count > MAX_ITERATIONS:
		#     logger.error(f"Infinite loop 'нц' exceeded max iterations ({MAX_ITERATIONS}).")
		#     raise KumirExecutionError(f"Превышен лимит итераций ({MAX_ITERATIONS}) для цикла 'нц'.")

		try:
			execute_lines(loop_body, env, robot, interpreter)
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала бесконечный цикл 'нц' на итерации {iteration_count}.")
				break  # Выходим из while True
			else:
				raise exit_e
		except Exception as body_e:
			logger.error(f"Error inside infinite 'нц' body (iteration {iteration_count}): {body_e}", exc_info=True)
			raise KumirExecutionError(f"Ошибка в теле цикла 'нц': {body_e}")

	logger.info(f"Finished infinite 'нц' loop after {iteration_count} iterations.")
	return end_loop_index + 1


def process_algorithm_call(line, env, robot, interpreter):
	"""
    Обрабатывает вызов другого алгоритма.
    ВНИМАНИЕ: Текущая реализация ПРОСТАЯ и НЕКОРРЕКТНАЯ с точки зрения
    области видимости и передачи параметров Кумира. Требует ПЕРЕРАБОТКИ.
    """
	line_strip = line.strip()
	# Упрощенный паттерн для вызова вида: имя_алгоритма [(аргументы)]
	call_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)(?:\s*\((.*)\))?$", line_strip)

	if call_match:
		algo_name = call_match.group(1)
		args_str = call_match.group(2)  # Строка с аргументами или None

		if algo_name in interpreter.algorithms:
			alg_to_run = interpreter.algorithms[algo_name]
			header_info = alg_to_run.get("header_info", {})
			params_def = header_info.get("params", [])

			logger.info(f"Attempting to call algorithm: '{algo_name}' with args_str='{args_str}'")
			logger.warning("Algorithm call implementation is basic and needs proper parameter handling and scoping.")

			# TODO: Реализовать сложную логику:
			# 1. Парсинг строки аргументов `args_str` (если есть).
			# 2. Вычисление значений переданных аргументов в ТЕКУЩЕМ окружении `env`.
			# 3. Создание НОВОГО окружения (локального scope) для вызываемого алгоритма.
			# 4. Сопоставление вычисленных аргументов с параметрами `params_def` из заголовка.
			# 5. Копирование/передача значений в новое окружение согласно режиму (арг/рез/аргрез/знач).
			# 6. Выполнение тела `alg_to_run["body"]` с НОВЫМ окружением.
			# 7. Обработка возвращаемых значений (`рез`, `аргрез`) и копирование их обратно в `env`.
			# 8. Восстановление старого окружения (если используется стек вызовов).

			# --- ВРЕМЕННАЯ ЗАГЛУШКА: выполняем тело в текущем env ---
			try:
				logger.debug(
					f"Executing body of '{algo_name}' in current environment (scoping/params NOT IMPLEMENTED).")
				execute_lines(alg_to_run["body"], env, robot, interpreter)  # Неправильно!
				logger.info(f"Finished placeholder call to '{algo_name}'.")
				return True  # Сигнализируем, что это был распознанный вызов
			except Exception as call_e:
				logger.error(f"Error during execution of algorithm '{algo_name}': {call_e}", exc_info=True)
				# Оборачиваем ошибку
				raise KumirExecutionError(
					f"Ошибка при выполнении алгоритма '{algo_name}': {call_e}")  # --- КОНЕЦ ЗАГЛУШКИ ---

	return False  # Не похоже на вызов известного алгоритма


def execute_lines(lines, env, robot, interpreter=None):
	""" Выполняет список строк кода Кумира. """
	i = 0
	n = len(lines)
	while i < n:
		line_raw = lines[i]
		line_strip = line_raw.strip()

		# Пропускаем пустые строки
		if not line_strip:
			i += 1
			continue

		logger.debug(f"Executing line {i + 1}/{n}: '{line_strip}'")

		lower_line = line_strip.lower()
		processed_by_block = False  # Флаг, что строка обработана как начало блока

		try:
			# --- Обработка блочных структур ---
			if lower_line.startswith("если"):
				i = process_if_block(lines, i, env, robot, interpreter)
				processed_by_block = True
			elif lower_line == "выбор":
				i = process_select_block(lines, i, env, robot, interpreter)
				processed_by_block = True
			elif lower_line.startswith("нц"):
				# Определяем тип цикла 'нц'
				if re.match(r"нц\s+для", lower_line):
					i = process_loop_for(lines, i, env, robot, interpreter)
				elif re.match(r"нц\s+пока", lower_line):
					i = process_loop_while(lines, i, env, robot, interpreter)
				elif re.match(r"нц\s+.+?\s+раз", lower_line):
					i = process_loop_n_times(lines, i, env, robot, interpreter)
				elif lower_line == "нц":  # Простой 'нц' (бесконечный)
					i = process_loop_infinite(lines, i, env, robot, interpreter)
				else:
					# Неизвестный вариант 'нц'
					raise KumirExecutionError(f"Неизвестный или некорректный синтаксис цикла 'нц': '{line_strip}'")
				processed_by_block = True
			# --- Обработка однострочных команд ---
			# Если строка не была обработана как начало блока, выполняем ее как отдельную команду
			if not processed_by_block:
				# Передаем оригинальную строку с пробелами по краям
				# и передаем robot во все функции, где он может понадобиться
				execute_line(line_strip, env, robot, interpreter)
				i += 1  # Переходим к следующей строке

		# --- Обработка исключений на уровне строки/блока ---
		except KumirExecutionError as e:
			# Ловим ошибки выполнения (включая 'Выход', 'стоп')
			# Команда 'выход' обрабатывается внутри циклов, здесь ловим ее, если она вне цикла
			if str(e) == "Выход":
				logger.error("Команда 'выход' использована вне цикла.")
				raise KumirExecutionError("Команда 'выход' может использоваться только внутри циклов ('нц'... 'кц').")
			else:
				# Пробрасываем остальные ошибки выполнения (включая 'стоп')
				logger.error(f"Execution error on line {i + 1} ('{line_strip}'): {e}")
				raise e
		except KumirEvalError as e:
			# Ловим ошибки вычисления выражений
			logger.error(f"Evaluation error on line {i + 1} ('{line_strip}'): {e}")
			# Оборачиваем в KumirExecutionError для единообразия
			raise KumirExecutionError(f"Ошибка вычисления на строке {i + 1}: {e}")
		except RobotError as e:
			# Ловим ошибки робота
			logger.error(f"Robot error on line {i + 1} ('{line_strip}'): {e}")
			raise KumirExecutionError(f"Ошибка робота на строке {i + 1}: {e}")
		except (DeclarationError, AssignmentError, InputOutputError) as e:
			# Ловим ошибки объявления, присваивания, ввода/вывода
			logger.error(f"Error on line {i + 1} ('{line_strip}'): {e}")
			raise KumirExecutionError(f"Ошибка на строке {i + 1}: {e}")
		except Exception as e:
			# Ловим все остальные непредвиденные ошибки
			logger.exception(f"Unexpected error on line {i + 1} ('{line_strip}'): {e}")
			raise KumirExecutionError(f"Неожиданная ошибка на строке {i + 1}: {e}")


def execute_line(line, env, robot, interpreter=None):
	"""
    Выполняет одну строку кода Кумира. Предполагается, что это не начало блочной конструкции.
    """
	logger.debug(f"Executing single line: '{line}'")
	lower_line = line.lower()

	# 1. Объявление переменных (проверяем по начальным словам)
	# Используем ALLOWED_TYPES из declarations
	for type_kw in ALLOWED_TYPES:
		# Проверяем, что строка начинается с типа и за ним идет пробел или конец строки
		if re.match(rf"^{type_kw}(?:\s+.*|$)", lower_line):
			process_declaration(line, env)
			return  # Выполнено

	# 2. Присваивание
	if ":=" in line:
		process_assignment(line, env, robot)  # Передаем robot
		return  # Выполнено

	# 3. Вывод
	if lower_line.startswith("вывод"):
		process_output(line, env, robot, interpreter)  # Передаем robot
		return  # Выполнено

	# 4. Ввод (Блокирующий!)
	if lower_line.startswith("ввод"):
		# process_input(line, env) # Выполняет input(), блокирует сервер!
		logger.warning("Команда 'ввод' обнаружена, но игнорируется в серверном режиме.")
		# Можно сгенерировать ошибку или просто пропустить
		# raise KumirExecutionError("Команда 'ввод' не поддерживается в данном режиме.")
		return  # Условно выполнено (проигнорировано)

	# 5. Команды управления (утв, дано, надо)
	if lower_line.startswith(("утв", "дано", "надо")):
		if process_control_command(line, env, robot):  # Передаем robot
			return  # Выполнено (или ошибка была брошена внутри)

	# 6. Команды потока управления (стоп, выход, пауза)
	if lower_line == "стоп":
		logger.info("Execution stopped by 'стоп' command.")
		raise KumirExecutionError("Выполнение прервано командой 'стоп'.")  # Бросаем исключение для остановки

	if lower_line == "выход":
		# 'выход' должен обрабатываться внутри циклов. Если дошли сюда - ошибка.
		logger.error("'выход' command used outside of a loop.")
		raise KumirExecutionError("Выход")  # Бросаем исключение, которое поймает execute_lines

	if lower_line == "пауза":  # или 'ждать'
		logger.info("Command 'пауза' ignored in server execution mode.")
		# На сервере паузу не делаем, чтобы не блокировать.
		# time.sleep(1) # Не делать так на сервере!
		return  # Условно выполнено (проигнорировано)

	# 7. Команды робота
	# process_robot_command может бросить RobotError, который будет пойман выше
	if process_robot_command(line, robot):
		return  # Команда робота распознана и (попытка) выполнена

	# 8. Вызов другого алгоритма (Заглушка!)
	if interpreter and process_algorithm_call(line, env, robot, interpreter):
		return  # Вызов алгоритма обработан (или ошибка брошена внутри)

	# 9. Неизвестная команда
	logger.error(f"Unknown command or syntax error: '{line}'")
	raise KumirExecutionError(f"Неизвестная команда или синтаксическая ошибка: '{line}'")

# FILE END: execution.py
