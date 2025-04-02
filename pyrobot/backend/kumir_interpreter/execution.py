# FILE START: execution.py
"""
Модуль execution.py
@description Реализует функции для выполнения управляющих конструкций
языка KUMIR (циклы, условия) и диспетчеризацию отдельных команд,
включая обработку вызовов алгоритмов со стеком.
"""
import logging
import re
import time
from copy import deepcopy  # Для копирования значений аргументов

# Импорты из нашего проекта
from .declarations import (process_declaration, process_assignment, process_output,
						   _validate_and_convert_value,  # Нужна для проверки типов аргументов
						   ALLOWED_TYPES, DeclarationError, AssignmentError, InputOutputError)
# Импортируем интерпретатор для доступа к стеку и алгоритмам
from .interpreter import \
	KumirLanguageInterpreter  # или from . import KumirLanguageInterpreter? Проверить относительный импорт
from .robot_commands import process_robot_command
from .robot_state import RobotError
from .safe_eval import safe_eval, KumirEvalError  # Используем новый safe_eval

logger = logging.getLogger('KumirExecution')


class KumirExecutionError(Exception):
	"""Основное исключение для ошибок выполнения."""
	pass


# --- НОВАЯ ФУНКЦИЯ: handle_algorithm_call ---
def handle_algorithm_call(call_line, interpreter):
	"""
	Обрабатывает вызов алгоритма: парсит аргументы, создает новый фрейм стека,
	передает параметры, выполняет тело, обрабатывает результаты.

	Args:
		call_line (str): Строка с вызовом алгоритма (e.g., "ИмяАлг(арг1, 'строка', 5)").
		interpreter (KumirLanguageInterpreter): Экземпляр интерпретатора для доступа
												к списку алгоритмов и стеку вызовов.
	"""
	logger.debug(f"Attempting to handle algorithm call: '{call_line}'")

	# 1. Парсинг строки вызова (имя и строка с аргументами)
	call_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\s*(?:\((.*)\))?$", call_line)
	if not call_match:
		# Это не похоже на вызов алгоритма (например, может быть переменной)
		logger.debug(f"'{call_line}' does not look like an algorithm call.")
		return False  # Сигнализируем, что это не обработанный вызов

	algo_name = call_match.group(1).strip()
	args_str = call_match.group(2)  # Может быть None, если скобок нет
	args_str = args_str.strip() if args_str is not None else ""  # Строка аргументов "арг1, 'строка', 5" или ""

	logger.debug(f"Call parsed: name='{algo_name}', args_str='{args_str}'")

	# 2. Поиск алгоритма по имени
	if algo_name not in interpreter.algorithms:
		# Если имя совпадает с командой робота или другой командой, это не вызов алг.
		# (Проверку на команду робота/ключевое слово лучше делать до вызова этой функции)
		# Если это точно не команда, но алгоритма нет - ошибка.
		# TODO: Улучшить проверку, чтобы не путать вызов с переменной/командой.
		# Пока считаем, что если дошли сюда, то это должен быть вызов.
		raise KumirExecutionError(f"Алгоритм с именем '{algo_name}' не найден.")

	called_algo = interpreter.algorithms[algo_name]
	header_info = called_algo.get("header_info")
	if not header_info:
		# Это не должно происходить, если парсинг прошел успешно
		raise KumirExecutionError(f"Внутренняя ошибка: отсутствует информация о заголовке для алгоритма '{algo_name}'.")

	formal_params = header_info.get("params", [])  # Ожидаемые параметры [{'mode':.., 'type':.., 'name':..}, ...]
	logger.info(f"Found algorithm '{algo_name}'. Expected params: {formal_params}")

	# 3. Парсинг и вычисление фактических аргументов
	actual_args = []
	if args_str:
		# TODO: Улучшить парсинг аргументов, чтобы обрабатывать запятые внутри строк/выражений
		arg_tokens = [arg.strip() for arg in args_str.split(',') if arg.strip()]
		logger.debug(f"Argument tokens: {arg_tokens}")
		# Вычисляем каждый аргумент в КОНТЕКСТЕ ВЫЗЫВАЮЩЕЙ СТОРОНЫ
		caller_env = interpreter.get_current_environment()
		try:
			for token in arg_tokens:
				arg_value = safe_eval(token, caller_env, interpreter.robot)
				actual_args.append(arg_value)
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления аргумента '{token}' при вызове '{algo_name}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating argument '{token}' for '{algo_name}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка вычисления аргумента '{token}': {e}")
	logger.debug(f"Evaluated actual arguments: {actual_args}")

	# 4. Проверка соответствия количества аргументов
	if len(actual_args) != len(formal_params):
		raise KumirExecutionError(
			f"Неверное количество аргументов при вызове '{algo_name}'. Ожидалось {len(formal_params)}, передано {len(actual_args)}.")

	# 5. Создание нового локального окружения для вызываемого алгоритма
	local_env = {}

	# 6. Сопоставление и передача параметров
	vars_to_copy_back = {}  # Словари для переменных, которые нужно вернуть (по имени параметра и имени в caller_env)
	caller_env = interpreter.get_current_environment()  # Среда вызывающей стороны

	for i, formal_param in enumerate(formal_params):
		param_name = formal_param["name"]
		param_mode = formal_param["mode"]
		param_type = formal_param["type"]
		param_is_table = formal_param.get("is_table", False)  # Обработка таблиц
		actual_value = actual_args[i]

		logger.debug(
			f"Processing param '{param_name}': mode={param_mode}, type={param_type}, table={param_is_table}, actual_value={actual_value}")

		# Проверка типа фактического аргумента (базовая)
		# TODO: Реализовать более строгую проверку и конвертацию типов Кумира
		# try:
		#      validated_value = _validate_and_convert_value(actual_value, param_type, param_name)
		# except AssignmentError as type_err:
		#      raise KumirExecutionError(f"Ошибка типа для аргумента '{param_name}' при вызове '{algo_name}': {type_err}")

		validated_value = actual_value  # Пока без строгой валидации при передаче

		if param_mode == "знач" or param_mode == "арг":
			# Передача по значению (копируем)
			local_env[param_name] = {
				"type": param_type,
				"value": deepcopy(validated_value),  # Используем deepcopy для изоляции
				"kind": f"param_{param_mode}",
				"is_table": param_is_table
			}
			logger.debug(
				f"Passed '{param_name}' by value (mode {param_mode}). Copied value: {local_env[param_name]['value']}")
		elif param_mode == "рез":
			# Результат - создаем переменную в локальном окружении, инициализируем None
			local_env[param_name] = {
				"type": param_type,
				"value": None,  # Или {} для таблиц?
				"kind": "param_res",
				"is_table": param_is_table
			}
			# Запоминаем, что нужно будет вернуть значение этой переменной
			# Имя переменной в вызывающем окружении, куда вернуть результат,
			# должно совпадать с именем фактического аргумента (если это была переменная).
			# Ищем имя фактического аргумента (если это была переменная)
			actual_arg_token = arg_tokens[i]  # Выражение, переданное как аргумент
			# Простая проверка, является ли токен именем переменной в caller_env
			if actual_arg_token in caller_env:
				vars_to_copy_back[param_name] = actual_arg_token
				logger.debug(f"Param '{param_name}' (mode res) will be copied back to caller var '{actual_arg_token}'.")
			else:
				# Если передан литерал или выражение, результат вернуть некуда
				logger.warning(
					f"Param '{param_name}' (mode res) corresponds to non-variable argument '{actual_arg_token}'. Result will be lost.")
				vars_to_copy_back[param_name] = None  # Помечаем, что возвращать некуда

		elif param_mode == "аргрез":
			# Передача по ссылке (копируем значение, но будем копировать обратно)
			local_env[param_name] = {
				"type": param_type,
				"value": deepcopy(validated_value),
				"kind": "param_argres",
				"is_table": param_is_table
			}
			# Ищем имя фактического аргумента (должна быть переменная)
			actual_arg_token = arg_tokens[i]
			if actual_arg_token in caller_env and not caller_env[actual_arg_token].get("is_table",
																					   False) == param_is_table:
				# Тип таблицы должен совпадать
				raise KumirExecutionError(
					f"Тип таблицы/переменной не совпадает для аргрез параметра '{param_name}' и аргумента '{actual_arg_token}'.")
			if actual_arg_token in caller_env:
				vars_to_copy_back[param_name] = actual_arg_token
				logger.debug(
					f"Param '{param_name}' (mode argres) passed. Will copy back to caller var '{actual_arg_token}'. Value: {local_env[param_name]['value']}")
			else:
				# Попытка передать не-переменную как аргрез - ошибка
				raise KumirExecutionError(
					f"Аргумент для аргрез параметра '{param_name}' ('{actual_arg_token}') должен быть переменной.")

		else:
			raise KumirExecutionError(f"Неизвестный режим параметра '{param_mode}' для '{param_name}'.")

	# 7. Помещаем новый фрейм на стек
	interpreter.push_call_frame(algo_name, local_env)

	# 8. Выполняем тело алгоритма
	try:
		execute_lines(called_algo["body"], interpreter)  # Передаем интерпретатор для доступа к стеку
		logger.info(f"Algorithm '{algo_name}' body executed.")
	except Exception as body_exec_err:
		# Если ошибка внутри вызванного алгоритма, нужно снять фрейм и пробросить ошибку
		logger.error(f"Error occurred inside algorithm '{algo_name}': {body_exec_err}")
		interpreter.pop_call_frame()  # Снимаем фрейм с ошибкой
		raise  # Пробрасываем ошибку дальше

	# 9. Снимаем фрейм со стека после успешного выполнения
	finished_frame = interpreter.pop_call_frame()
	finished_env = finished_frame.local_env

	# 10. Обработка возвращаемых значений (копирование 'рез' и 'аргрез' обратно)
	caller_env = interpreter.get_current_environment()  # Снова получаем окружение вызывающей стороны
	logger.debug(
		f"Copying back results from '{algo_name}' to caller '{interpreter.call_stack[-1].algo_name if interpreter.call_stack else '(error?)'}'")
	for param_name, caller_var_name in vars_to_copy_back.items():
		if caller_var_name is None:  # Некуда было возвращать 'рез'
			continue

		if param_name not in finished_env:
			# Этого не должно быть
			logger.error(
				f"Internal error: Result parameter '{param_name}' not found in finished environment of '{algo_name}'.")
			continue
		if caller_var_name not in caller_env:
			# Переменная вызывающей стороны могла быть удалена? Маловероятно.
			logger.error(
				f"Internal error: Caller variable '{caller_var_name}' not found in caller environment for result copy back.")
			continue

		# Получаем значение из локального окружения вызванного алг.
		value_to_return = finished_env[param_name]["value"]
		target_type = caller_env[caller_var_name]["type"]
		target_is_table = caller_env[caller_var_name].get("is_table", False)
		finished_is_table = finished_env[param_name].get("is_table", False)

		# Проверяем совместимость типов (особенно для таблиц)
		if target_is_table != finished_is_table:
			logger.error(
				f"Cannot copy back result for '{param_name}': table/scalar mismatch between caller and callee.")
			# Можно бросить ошибку или проигнорировать
			continue

		try:
			# Валидируем и конвертируем возвращаемое значение к типу переменной в вызывающем окружении
			validated_return_value = _validate_and_convert_value(value_to_return, target_type, caller_var_name)
			# Копируем значение (используем deepcopy для сложных типов)
			caller_env[caller_var_name]["value"] = deepcopy(validated_return_value)
			logger.debug(f"Copied back '{param_name}' ({value_to_return}) to '{caller_var_name}'.")
		except AssignmentError as copy_back_err:
			logger.error(
				f"Error copying back result for param '{param_name}' to var '{caller_var_name}': {copy_back_err}")
		# Можно бросить ошибку или проигнорировать

	# 11. Возвращаем True, сигнализируя, что вызов был успешно обработан
	return True


# --- Модифицированные execute_lines и execute_line ---

def execute_lines(lines, interpreter):  # Убираем env, robot - берем из interpreter
	""" Выполняет список строк кода Кумира, используя стек вызовов интерпретатора. """
	i = 0
	n = len(lines)
	# Получаем текущее окружение из интерпретатора
	current_env = interpreter.get_current_environment()
	robot = interpreter.robot  # Получаем робота

	while i < n:
		line_raw = lines[i]
		line_strip = line_raw.strip()

		if not line_strip:
			i += 1
			continue

		# Логируем с указанием текущего алгоритма (фрейма)
		current_frame_name = interpreter.call_stack[-1].algo_name if interpreter.call_stack else "(unknown)"
		logger.debug(f"[{current_frame_name}] Exec line {i + 1}/{n}: '{line_strip}'")

		lower_line = line_strip.lower()
		processed_by_block_or_call = False

		try:
			# Обновляем текущее окружение перед каждой строкой (на случай, если стек изменился)
			current_env = interpreter.get_current_environment()

			# --- Обработка блочных структур ---
			# Передаем interpreter вместо env, robot
			if lower_line.startswith("если"):
				# process_if_block и другие обработчики блоков тоже нужно обновить,
				# чтобы они принимали interpreter
				# Пока оставим старую сигнатуру, передавая нужные части из interpreter
				i = process_if_block(lines, i, current_env, robot, interpreter)
				processed_by_block_or_call = True
			elif lower_line == "выбор":
				i = process_select_block(lines, i, current_env, robot, interpreter)
				processed_by_block_or_call = True
			elif lower_line.startswith("нц"):
				if re.match(r"нц\s+для", lower_line):
					i = process_loop_for(lines, i, current_env, robot, interpreter)
				elif re.match(r"нц\s+пока", lower_line):
					i = process_loop_while(lines, i, current_env, robot, interpreter)
				elif re.match(r"нц\s+.+?\s+раз", lower_line):
					i = process_loop_n_times(lines, i, current_env, robot, interpreter)
				elif lower_line == "нц":
					i = process_loop_infinite(lines, i, current_env, robot, interpreter)
				else:
					raise KumirExecutionError(f"Неизвестный синтаксис цикла 'нц': '{line_strip}'")
				processed_by_block_or_call = True

			# --- Попытка обработки как вызова алгоритма ---
			if not processed_by_block_or_call:
				# Передаем interpreter для доступа к стеку и списку алгоритмов
				if handle_algorithm_call(line_strip, interpreter):
					processed_by_block_or_call = True
					i += 1  # Переходим к следующей строке после успешного вызова

			# --- Обработка однострочных команд ---
			if not processed_by_block_or_call:
				# Передаем текущее окружение и робота
				execute_line(line_strip, current_env, robot, interpreter)
				i += 1

		# --- Обработка исключений ---
		# Блок except остается как в предыдущей версии, но ошибки теперь могут приходить
		# из handle_algorithm_call или измененных process_* функций
		except KumirExecutionError as e:
			if str(e) == "Выход":
				logger.error(f"[{current_frame_name}] Команда 'выход' использована вне цикла.")
				raise KumirExecutionError("Команда 'выход' может использоваться только внутри циклов ('нц'... 'кц').")
			else:
				logger.error(f"[{current_frame_name}] Execution error on line {i + 1} ('{line_strip}'): {e}")
				raise e
		except KumirEvalError as e:
			logger.error(f"[{current_frame_name}] Evaluation error on line {i + 1} ('{line_strip}'): {e}")
			raise KumirExecutionError(f"Ошибка вычисления на строке {i + 1}: {e}")
		except RobotError as e:
			logger.error(f"[{current_frame_name}] Robot error on line {i + 1} ('{line_strip}'): {e}")
			raise KumirExecutionError(f"Ошибка робота на строке {i + 1}: {e}")
		except (DeclarationError, AssignmentError, InputOutputError) as e:
			logger.error(f"[{current_frame_name}] Error on line {i + 1} ('{line_strip}'): {e}")
			raise KumirExecutionError(f"Ошибка на строке {i + 1}: {e}")
		except Exception as e:
			logger.exception(f"[{current_frame_name}] Unexpected error on line {i + 1} ('{line_strip}'): {e}")
			raise KumirExecutionError(f"Неожиданная ошибка на строке {i + 1}: {e}")


# execute_line теперь принимает env, robot явно (полученные из interpreter в execute_lines)
def execute_line(line, env, robot, interpreter=None):
	"""
	Выполняет одну строку кода Кумира. Не обрабатывает вызовы и блочные структуры.
	"""
	# Логирование теперь происходит в execute_lines
	# logger.debug(f"Executing single line: '{line}'")
	lower_line = line.lower()

	# 1. Объявление переменных
	for type_kw in ALLOWED_TYPES:
		if re.match(rf"^{type_kw}(?:\s+.*|$)", lower_line):
			# process_declaration ожидает только env
			process_declaration(line, env)
			return

	# 2. Присваивание
	if ":=" in line:
		# process_assignment ожидает env, robot
		process_assignment(line, env, robot)
		return

	# 3. Вывод
	if lower_line.startswith("вывод"):
		# process_output ожидает env, robot, interpreter
		process_output(line, env, robot, interpreter)
		return

	# 4. Ввод (Игнорируется)
	if lower_line.startswith("ввод"):
		logger.warning("Команда 'ввод' обнаружена, но игнорируется в серверном режиме.")
		return

	# 5. Команды управления (утв, дано, надо)
	if lower_line.startswith(("утв", "дано", "надо")):
		# process_control_command ожидает env, robot
		if process_control_command(line, env, robot):
			return

	# 6. Команды потока управления (стоп, выход, пауза)
	if lower_line == "стоп":
		logger.info("Execution stopped by 'стоп' command.")
		raise KumirExecutionError("Выполнение прервано командой 'стоп'.")

	if lower_line == "выход":
		logger.error("'выход' command used outside of a loop context.")
		raise KumirExecutionError("Выход")  # Должно быть поймано внутри цикла

	if lower_line == "пауза":
		logger.info("Command 'пауза' ignored in server execution mode.")
		return

	# 7. Команды робота
	# process_robot_command ожидает только robot
	if process_robot_command(line, robot):
		return

	# 8. Вызов другого алгоритма - обрабатывается в execute_lines через handle_algorithm_call

	# 9. Неизвестная команда
	logger.error(f"Unknown command or syntax error: '{line}'")
	raise KumirExecutionError(f"Неизвестная команда или синтаксическая ошибка: '{line}'")


# --- Функции обработки блоков (если, выбор, нц) ---
# Их сигнатуры нужно обновить, чтобы они принимали interpreter вместо env, robot
# Но пока для простоты оставим старые сигнатуры и будем передавать нужные части
# из interpreter внутрь execute_lines.

# process_if_block(lines, start_index, env, robot, interpreter): # Уже принимает interpreter
# process_select_block(lines, start_index, env, robot, interpreter): # Уже принимает interpreter
# process_loop_for(lines, start_index, env, robot, interpreter): # Уже принимает interpreter
# process_loop_while(lines, start_index, env, robot, interpreter): # Уже принимает interpreter
# process_loop_n_times(lines, start_index, env, robot, interpreter): # Уже принимает interpreter
# process_loop_infinite(lines, start_index, env, robot, interpreter): # Уже принимает interpreter

# Код этих функций (process_if_block и т.д.) остается без изменений,
# так как они уже вызывают safe_eval и execute_lines с нужными параметрами.
# --- Начало неизмененного кода ---
def process_control_command(line, env, robot=None):
	""" Обрабатывает команды управления: утв, дано, надо. """
	# ... (код без изменений) ...
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
			result = safe_eval(expr, env, robot)  # Передаем env и robot
			logger.debug(f"Control '{keyword}' evaluated '{expr}' -> {result} (type: {type(result)})")
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления выражения '{expr}' в команде '{keyword}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating control expr '{expr}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка вычисления '{expr}' в '{keyword}': {e}")
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
			raise KumirExecutionError(
				f"Отказ: условие '{expr}' в команде '{keyword}' ложно (результат: {failure_reason}).")
		else:
			logger.info(f"Control command success: '{keyword} {expr}' is True.")
			return True
	return False


def process_if_block(lines, start_index, env, robot, interpreter):
	""" Обрабатывает блок "если-то-[иначе]-все". """
	# ... (код без изменений) ...
	n = len(lines)
	header_line = lines[start_index].strip()
	if not header_line.lower().startswith("если"):
		raise KumirExecutionError("Внутренняя ошибка: process_if_block вызван не для строки 'если'.")
	condition_expr = header_line[len("если"):].strip()
	i = start_index + 1
	series1_lines = []
	series2_lines = []
	current_series = None
	found_then = False
	found_else = False
	end_if_index = -1
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower()
		if lower_line == "все":
			end_if_index = i;
			logger.debug(f"Found 'все' for 'если' at index {i}");
			break
		elif lower_line.startswith("то") and not found_then:
			found_then = True;
			current_series = series1_lines
			content_after_then = line[len("то"):].strip()
			if content_after_then: current_series.append(content_after_then)
			logger.debug(f"Found 'то' at index {i}. Content after: '{content_after_then}'")
		elif lower_line.startswith("иначе") and found_then and not found_else:
			found_else = True;
			current_series = series2_lines
			content_after_else = line[len("иначе"):].strip()
			if content_after_else: current_series.append(content_after_else)
			logger.debug(f"Found 'иначе' at index {i}. Content after: '{content_after_else}'")
		else:
			if current_series is not None:
				current_series.append(line)
			elif not found_then:
				logger.warning(f"Unexpected line '{line}' inside 'если' before 'то'. Assuming part of condition.")
				condition_expr += " " + line
			else:
				logger.error(f"Internal logic error: Line '{line}' encountered unexpectedly in 'если' parsing.")
				raise KumirExecutionError(f"Неожиданная строка '{line}' при разборе блока 'если'.")
		i += 1
	if end_if_index == -1: raise KumirExecutionError(
		f"Не найден 'все' для блока 'если', начавшегося на строке {start_index + 1}.")
	if not found_then: raise KumirExecutionError(
		f"Не найдено 'то' в блоке 'если', начавшемся на строке {start_index + 1}.")
	if not condition_expr: raise KumirExecutionError(f"Отсутствует условие после 'если' на строке {start_index + 1}.")
	logger.debug(f"Evaluating 'если' condition: '{condition_expr}'")
	try:
		cond_value = safe_eval(condition_expr, env, robot)  # Передаем env, robot
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
	if cond_bool:
		logger.debug(f"Executing 'то' block (lines {len(series1_lines)}).")
		execute_lines(series1_lines, interpreter)  # Передаем interpreter
	elif found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(series2_lines)}).")
		execute_lines(series2_lines, interpreter)  # Передаем interpreter
	else:
		logger.debug("Condition is false, no 'иначе' block to execute.")
	return end_if_index + 1


def process_select_block(lines, start_index, env, robot, interpreter):
	""" Обрабатывает блок "выбор-при-[иначе]-все". """
	# ... (код без изменений) ...
	n = len(lines)
	if not lines[start_index].strip().lower() == "выбор":
		raise KumirExecutionError("Внутренняя ошибка: process_select_block вызван не для строки 'выбор'.")
	i = start_index + 1
	branches = [];
	else_series = []
	found_else = False;
	end_select_index = -1
	current_branch_lines = None
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower()
		if lower_line == "все":
			end_select_index = i;
			logger.debug(f"Found 'все' for 'выбор' at index {i}");
			break
		elif lower_line.startswith("при"):
			if found_else: raise KumirExecutionError("Обнаружена ветка 'при' после 'иначе' в блоке 'выбор'.")
			parts = line.split(":", 1)
			if len(parts) != 2: raise KumirExecutionError(f"Отсутствует ':' после условия в ветке 'при': '{line}'")
			cond_part = parts[0].strip();
			condition_expr = cond_part[len("при"):].strip()
			if not condition_expr: raise KumirExecutionError(f"Отсутствует условие после 'при' в строке: '{line}'")
			first_command = parts[1].strip()
			current_branch_lines = [first_command] if first_command else []
			branches.append({"condition": condition_expr, "body": current_branch_lines})
			logger.debug(f"Found 'при' branch with condition '{condition_expr}'. First command: '{first_command}'")
		elif lower_line.startswith("иначе"):
			if found_else: raise KumirExecutionError("Обнаружено повторное 'иначе' в блоке 'выбор'.")
			if not branches: logger.warning("Блок 'иначе' найден до каких-либо веток 'при' в 'выбор'.")
			found_else = True;
			current_branch_lines = else_series
			content_after_else = line[len("иначе"):].strip()
			if content_after_else: current_branch_lines.append(content_after_else)
			logger.debug(f"Found 'иначе' block. Content after: '{content_after_else}'")
		else:
			if current_branch_lines is not None:
				current_branch_lines.append(line)
			else:
				raise KumirExecutionError(f"Неожиданная строка '{line}' внутри 'выбор' до начала веток 'при'/'иначе'.")
		i += 1
	if end_select_index == -1: raise KumirExecutionError(
		f"Не найден 'все' для блока 'выбор', начавшегося на строке {start_index + 1}.")
	if not branches and not found_else: logger.warning(
		"Конструкция 'выбор-все' не содержит веток 'при' или блока 'иначе'. Блок пуст.")
	executed = False
	for idx, branch in enumerate(branches):
		condition_expr = branch["condition"];
		series = branch["body"]
		logger.debug(f"Evaluating 'при' condition #{idx + 1}: {condition_expr}")
		try:
			cond_value = safe_eval(condition_expr, env, robot)  # Передаем env, robot
		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в ветке 'при' блока 'выбор': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating 'при' condition '{condition_expr}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка в условии 'при': {e}")
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
			execute_lines(series, interpreter)  # Передаем interpreter
			executed = True;
			break
	if not executed and found_else:
		logger.debug(f"Executing 'иначе' block (lines {len(else_series)}).")
		execute_lines(else_series, interpreter)  # Передаем interpreter
	elif not executed:
		logger.debug("No 'при' branch matched and no 'иначе' block found.")
	return end_select_index + 1


def process_loop_for(lines, start_index, env, robot, interpreter):
	""" Обрабатывает цикл 'нц для ... кц'. """
	# ... (код без изменений, вызывает execute_lines(loop_body, interpreter)) ...
	n = len(lines);
	header_line = lines[start_index].strip()
	match = re.match(
		r"нц\s+для\s+([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)\s+от\s+(.+?)\s+до\s+(.+?)(?:\s+шаг\s+(.+))?$",
		header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц для': {header_line}")
	var_name, start_expr, end_expr, step_expr = match.groups();
	step_expr = step_expr.strip() if step_expr else "1"
	logger.debug(f"Parsing 'нц для': var='{var_name}', from='{start_expr}', to='{end_expr}', step='{step_expr}'")
	i = start_index + 1;
	loop_body = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower()
		if lower_line.startswith("нц"):
			nesting_level += 1; logger.debug(f"Nested 'нц' found at index {i}, nesting level: {nesting_level}")
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; logger.debug(f"Found matching 'кц' for 'нц для' at index {i}"); break
			else:
				nesting_level -= 1; logger.debug(f"Nested 'кц' found at index {i}, nesting level: {nesting_level}")
		loop_body.append(line);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц для', начавшегося на строке {start_index + 1}.")
	try:
		start_val_raw = safe_eval(start_expr, env, robot);
		end_val_raw = safe_eval(end_expr, env, robot);
		step_val_raw = safe_eval(step_expr, env, robot)  # Передаем env, robot
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
	if step_val == 0: raise KumirExecutionError("Шаг в цикле 'нц для' не может быть равен нулю.")
	original_value = None;
	was_declared = var_name in env
	if was_declared:
		if env[var_name].get("is_table"): raise KumirExecutionError(
			f"Переменная цикла '{var_name}' не может быть таблицей.")
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
			env[var_name]["value"] = current
			logger.debug(f"'для {var_name}' iteration {iteration_count}, value = {current}")
			try:
				execute_lines(loop_body, interpreter)  # Передаем interpreter
			except KumirExecutionError as exit_e:
				if str(exit_e) == "Выход":
					logger.info(
						f"Команда 'выход' прервала цикл 'нц для {var_name}' на итерации {iteration_count}."); break
				else:
					raise exit_e
			except Exception as body_e:
				logger.error(f"Error inside 'нц для {var_name}' body (iteration {iteration_count}): {body_e}",
							 exc_info=True); raise KumirExecutionError(
					f"Ошибка в теле цикла 'для {var_name}': {body_e}")
			current += step_val
	finally:
		if was_declared:
			env[var_name]['value'] = original_value; logger.debug(f"Restored original value for '{var_name}'.")
		elif var_name in env and env[var_name].get("kind") == "local_loop":
			del env[var_name]; logger.debug(f"Removed temporary loop variable '{var_name}'.")
	logger.info(f"Finished 'нц для {var_name}' after {iteration_count} iterations.")
	return end_loop_index + 1


def process_loop_while(lines, start_index, env, robot, interpreter):
	""" Обрабатывает цикл 'нц пока ... кц'. """
	# ... (код без изменений, вызывает execute_lines(loop_body, interpreter)) ...
	n = len(lines);
	header_line = lines[start_index].strip();
	match = re.match(r"нц\s+пока\s+(.+)", header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц пока': {header_line}")
	condition_expr = match.group(1).strip();
	if not condition_expr: raise KumirExecutionError("Отсутствует условие после 'нц пока'.")
	logger.debug(f"Parsing 'нц пока': condition='{condition_expr}'")
	i = start_index + 1;
	loop_body = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower()
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; break
			else:
				nesting_level -= 1
		loop_body.append(line);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц пока', начавшегося на строке {start_index + 1}.")
	logger.info(f"Starting 'нц пока {condition_expr}'.");
	iteration_count = 0
	while True:
		iteration_count += 1
		try:
			cond_value = safe_eval(condition_expr, env, robot)  # Передаем env, robot
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
			execute_lines(loop_body, interpreter)  # Передаем interpreter
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала цикл 'нц пока' на итерации {iteration_count}."); break
			else:
				raise exit_e
		except Exception as body_e:
			logger.error(f"Error inside 'нц пока' body (iteration {iteration_count}): {body_e}",
						 exc_info=True); raise KumirExecutionError(f"Ошибка в теле цикла 'пока': {body_e}")
	logger.info(f"Finished 'нц пока {condition_expr}' after {iteration_count - 1} successful iterations.")
	return end_loop_index + 1


def process_loop_n_times(lines, start_index, env, robot, interpreter):
	""" Обрабатывает цикл 'нц <N> раз ... кц'. """
	# ... (код без изменений, вызывает execute_lines(loop_body, interpreter)) ...
	n = len(lines);
	header_line = lines[start_index].strip();
	match = re.match(r"нц\s+(.+?)\s+раз", header_line, re.IGNORECASE)
	if not match: raise KumirExecutionError(f"Неверный синтаксис заголовка цикла 'нц N раз': {header_line}")
	count_expr = match.group(1).strip();
	logger.debug(f"Parsing 'нц N раз': count_expr='{count_expr}'")
	try:
		count_raw = safe_eval(count_expr, env, robot)  # Передаем env, robot
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
	loop_body = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower()
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; break
			else:
				nesting_level -= 1
		loop_body.append(line);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц N раз', начавшегося на строке {start_index + 1}.")
	logger.info(f"Starting 'нц {count} раз'.")
	for iteration in range(count):
		current_iteration = iteration + 1
		logger.debug(f"'нц N раз' iteration {current_iteration}/{count}")
		try:
			execute_lines(loop_body, interpreter)  # Передаем interpreter
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала цикл 'нц N раз' на итерации {current_iteration}."); break
			else:
				raise exit_e
		except Exception as body_e:
			logger.error(f"Error inside 'нц N раз' body (iteration {current_iteration}): {body_e}",
						 exc_info=True); raise KumirExecutionError(f"Ошибка в теле цикла 'N раз': {body_e}")
	logger.info(f"Finished 'нц {count} раз'.")
	return end_loop_index + 1


def process_loop_infinite(lines, start_index, env, robot, interpreter):
	""" Обрабатывает 'бесконечный' цикл 'нц ... кц'. """
	# ... (код без изменений, вызывает execute_lines(loop_body, interpreter)) ...
	n = len(lines);
	header_line = lines[start_index].strip()
	if not header_line.lower() == "нц": raise KumirExecutionError(
		"Внутренняя ошибка: process_loop_infinite вызван не для 'нц'.")
	logger.debug("Parsing infinite 'нц' loop.")
	i = start_index + 1;
	loop_body = [];
	end_loop_index = -1;
	nesting_level = 0
	while i < n:
		line = lines[i].strip();
		lower_line = line.lower()
		if lower_line.startswith("нц"):
			nesting_level += 1
		elif lower_line == "кц":
			if nesting_level == 0:
				end_loop_index = i; break
			else:
				nesting_level -= 1
		loop_body.append(line);
		i += 1
	if end_loop_index == -1: raise KumirExecutionError(
		f"Не найден 'кц' для цикла 'нц', начавшегося на строке {start_index + 1}.")
	logger.info("Starting infinite 'нц' loop.");
	iteration_count = 0
	MAX_DURATION_S = 10;
	start_time = time.time()
	while True:
		iteration_count += 1;
		logger.debug(f"Infinite 'нц' loop iteration {iteration_count}")
		current_time_exec = time.time()
		if current_time_exec - start_time > MAX_DURATION_S: logger.error(
			f"Infinite loop 'нц' exceeded max duration ({MAX_DURATION_S}s) after {iteration_count} iterations."); raise KumirExecutionError(
			f"Превышено максимальное время выполнения ({MAX_DURATION_S}с) для цикла 'нц'.")
		try:
			execute_lines(loop_body, interpreter)  # Передаем interpreter
		except KumirExecutionError as exit_e:
			if str(exit_e) == "Выход":
				logger.info(f"Команда 'выход' прервала бесконечный цикл 'нц' на итерации {iteration_count}."); break
			else:
				raise exit_e
		except Exception as body_e:
			logger.error(f"Error inside infinite 'нц' body (iteration {iteration_count}): {body_e}",
						 exc_info=True); raise KumirExecutionError(f"Ошибка в теле цикла 'нц': {body_e}")
	logger.info(f"Finished infinite 'нц' loop after {iteration_count} iterations.")
	return end_loop_index + 1
# --- Конец неизмененного кода ---


# FILE END: execution.py
