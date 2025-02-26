"""
kumir_interpreter.py
Описание: Интерпретатор языка KUMIR.
Обеспечивает парсинг, токенизацию, выполнение кода и логирование каждого шага выполнения.
"""

import math
import re
import time

# Импорт интерпретатора робота из вложенного модуля
from .kumir_interpreter.robot_interpreter import KumirInterpreter

# ---------------------------------------------------------------------
# Константы и настройки
# ---------------------------------------------------------------------

RESERVED_KEYWORDS = {"алг", "нач", "кон", "исп", "кон_исп", "дано", "надо", "арг", "рез", "аргрез", "знач", "цел",
					 "вещ", "лог", "сим", "лит", "таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб", "и", "или",
					 "не", "да", "нет", "утв", "выход", "ввод", "вывод", "нс", "если", "то", "иначе", "все", "выбор",
					 "при", "нц", "кц", "кц_при", "раз", "пока", "для", "от", "до", "шаг"}

ALLOWED_TYPES = {"цел", "вещ", "лог", "сим", "лит"}
MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT


# ---------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------

def is_valid_identifier(identifier, var_type):
	"""
	Проверяет корректность идентификатора для переменной.
	@param identifier: str - имя переменной.
	@param var_type: str - тип переменной.
	@returns: bool - True, если идентификатор корректен, иначе False.
	"""
	words = identifier.strip().split()
	if not words:
		return False
	if re.match(r'^\d', words[0]):
		return False
	for word in words:
		if word.lower() in RESERVED_KEYWORDS:
			if var_type == "лог" and word.lower() == "не" and word != words[0]:
				continue
			return False
		if not re.match(r'^[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*$', word):
			return False
	return True


def convert_hex_constants(expr):
	"""
	Заменяет шестнадцатеричные константы (начинающиеся с '$') на формат, понятный Python.
	@param expr: str - исходное выражение.
	@returns: str - преобразованное выражение.
	"""
	return re.sub(r'\$(?P<hex>[A-Fa-f0-9]+)', r'0x\g<hex>', expr)


def safe_eval(expr, eval_env):
	"""
	Безопасно вычисляет выражение с использованием ограниченного набора встроенных функций.
	@param expr: str - выражение для вычисления.
	@param eval_env: dict - окружение переменных.
	@returns: результат вычисления.
	"""
	expr = convert_hex_constants(expr)
	safe_globals = {"__builtins__": None, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt, "int": int,
					"float": float}
	return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
	"""
	Формирует окружение для вычисления выражений из переменных.
	@param env: dict - окружение переменных.
	@returns: dict - словарь переменных с их значениями.
	"""
	result = {}
	for var, info in env.items():
		result[var] = info.get("value")
	return result


# ---------------------------------------------------------------------
# Обработка объявлений, присваиваний и вывода
# ---------------------------------------------------------------------

def process_declaration(line, env):
	"""
	Обрабатывает оператор объявления переменной.
	@param line: str - строка объявления.
	@param env: dict - окружение переменных.
	@returns: bool - True, если объявление обработано.
	@raises Exception: если объявление некорректно.
	"""
	tokens = line.split()
	if not tokens:
		return False
	decl_type = tokens[0].lower()
	if decl_type not in ALLOWED_TYPES:
		return False
	idx = 1
	is_table = False
	if idx < len(tokens) and tokens[idx].lower().startswith("таб"):
		is_table = True
		idx += 1
	rest = " ".join(tokens[idx:])
	identifiers = [ident.strip() for ident in rest.split(",") if ident.strip()]
	if not identifiers:
		raise Exception("Declaration without any variable names.")
	for ident in identifiers:
		if not is_valid_identifier(ident, decl_type):
			raise Exception(f"Invalid variable name: '{ident}'")
		if ident in env:
			raise Exception(f"Variable '{ident}' already declared.")
		env[ident] = {"type": decl_type, "value": {} if is_table else None, "kind": "global", "is_table": is_table}
	return True


def process_assignment(line, env):
	"""
	Обрабатывает оператор присваивания.
	@param line: str - строка присваивания.
	@param env: dict - окружение переменных.
	@raises Exception: если синтаксис или преобразование некорректны.
	"""
	parts = line.split(":=")
	if len(parts) != 2:
		raise Exception("Invalid assignment syntax.")
	left, right = parts[0].strip(), parts[1].strip()
	if "[" in left and left.endswith("]"):
		import re
		match = re.match(
			r"^([A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*(?:\s+[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*)*)\[(.+)\]$",
			left)
		if not match:
			raise Exception(f"Invalid syntax for array element assignment: {left}")
		var_name = match.group(1).strip()
		indices_expr = match.group(2).strip()
		index_tokens = [token.strip() for token in indices_expr.split(",")]
		eval_env = get_eval_env(env)
		try:
			indices = tuple(safe_eval(token, eval_env) for token in index_tokens)
		except Exception as e:
			raise Exception(f"Error evaluating indices in '{left}': {e}")
		if var_name not in env or not env[var_name].get("is_table"):
			raise Exception(f"Variable '{var_name}' is not declared as a table.")
		target_type = env[var_name]["type"]
		try:
			value = safe_eval(right, eval_env)
		except Exception as e:
			raise Exception(f"Error evaluating expression '{right}': {e}")
		try:
			if target_type == "цел":
				value = int(value)
				if not (-MAX_INT <= value <= MAX_INT):
					raise Exception("Value out of range for integer type.")
			elif target_type == "вещ":
				value = float(value)
			elif target_type == "лог":
				if isinstance(value, bool):
					pass
				elif isinstance(value, str):
					low_val = value.lower()
					if low_val == "да":
						value = True
					elif low_val == "нет":
						value = False
					else:
						raise Exception("Invalid logical value.")
				else:
					value = bool(value)
			elif target_type in {"сим", "лит"}:
				value = str(value)
				if target_type == "сим" and len(value) != 1:
					raise Exception("Character variable must be exactly one symbol.")
			else:
				raise Exception(f"Unsupported variable type: {target_type}")
		except Exception as e:
			raise Exception(f"Error converting value for '{left}': {e}")
		if env[var_name]["value"] is None:
			env[var_name]["value"] = {}
		env[var_name]["value"][indices] = value
		return

	if left not in env:
		raise Exception(f"Variable '{left}' is not declared.")
	eval_env = get_eval_env(env)
	try:
		value = safe_eval(right, eval_env)
	except Exception as e:
		raise Exception(f"Error evaluating expression '{right}': {e}")
	target_type = env[left]["type"]
	try:
		if target_type == "цел":
			value = int(value)
			if not (-MAX_INT <= value <= MAX_INT):
				raise Exception("Value out of range for integer type.")
		elif target_type == "вещ":
			value = float(value)
		elif target_type == "лог":
			if isinstance(value, bool):
				pass
			elif isinstance(value, str):
				low_val = value.lower()
				if low_val == "да":
					value = True
				elif low_val == "нет":
					value = False
				else:
					raise Exception("Invalid logical value.")
			else:
				value = bool(value)
		elif target_type in {"сим", "лит"}:
			value = str(value)
			if target_type == "сим" and len(value) != 1:
				raise Exception("Character variable must be exactly one symbol.")
		else:
			raise Exception(f"Unsupported variable type: {target_type}")
	except Exception as e:
		raise Exception(f"Error converting value for variable '{left}': {e}")
	env[left]["value"] = value


def process_output(line, env):
	"""
	Обрабатывает команду вывода и печатает результат.
	@param line: str - строка команды вывода.
	@param env: dict - окружение переменных.
	"""
	content = line[5:].strip()
	eval_env = get_eval_env(env)
	try:
		value = safe_eval(content, eval_env)
	except Exception:
		value = content
	print(value)


def process_robot_command(line, robot):
	cmd = line.lower().strip()
	robot_commands = {"влево": robot.go_left, "вправо": robot.go_right, "вверх": robot.go_up, "вниз": robot.go_down,
					  "закрасить": robot.do_paint}
	if cmd in robot_commands:
		# Убираем try/except, чтобы исключение поднималось дальше
		robot_commands[cmd]()
		return True
	return False


def preprocess_code(code):
	lines = []
	for line in code.splitlines():
		# Удаляем всё, что идёт после символа '|' или '#'
		if '|' in line:
			line = line.split('|')[0]
		if '#' in line:
			line = line.split('#')[0]
		line = line.strip()
		if not line:
			continue
		# Если строка равна "использовать робот" (без учета регистра), пропускаем её
		if line.lower() == "использовать робот":
			continue
		# Разбиваем строку по символу ';' (если их несколько)
		parts = [part.strip() for part in line.split(';') if part.strip()]
		lines.extend(parts)
	return lines


def separate_sections(lines):
	"""
	Разделяет строки кода на вступление и секции алгоритмов.
	@param lines: list of str - строки кода.
	@returns: tuple (introduction, algorithms)
	"""
	introduction = []
	algorithms = []
	current_algo = None
	in_algo = False
	for line in lines:
		lower_line = line.lower()
		if lower_line.startswith("алг"):
			if current_algo is not None:
				algorithms.append(current_algo)
			current_algo = {"header": line, "body": []}
			in_algo = False
		elif lower_line == "нач":
			if current_algo is None:
				raise Exception("Error: 'нач' without 'алг'")
			in_algo = True
		elif lower_line == "кон":
			if current_algo is None or not in_algo:
				raise Exception("Error: 'кон' without 'нач'")
			in_algo = False
		else:
			if current_algo is None:
				introduction.append(line)
			else:
				if in_algo:
					current_algo["body"].append(line)
				else:
					current_algo["header"] += " " + line
	if current_algo is not None:
		algorithms.append(current_algo)
	return introduction, algorithms


def parse_algorithm_header(header_line):
	"""
	Разбирает заголовок алгоритма для извлечения имени и параметров.
	@param header_line: str - строка заголовка.
	@returns: dict - информация о заголовке (raw, name, params).
	"""
	header_line = header_line.strip()
	if header_line.lower().startswith("алг"):
		header_line = header_line[3:].strip()
	params = []
	name_part = header_line
	if "(" in header_line:
		parts = header_line.split("(", 1)
		name_part = parts[0].strip()
		params_part = parts[1].rsplit(")", 1)[0]
		tokens = params_part.split()
		mode = "арг"
		current_type = None
		current_names = []
		i = 0
		while i < len(tokens):
			token = tokens[i]
			if token in ["арг", "рез", "аргрез"]:
				if current_names and current_type is not None:
					for n in current_names:
						params.append((mode, current_type, n))
					current_names = []
				mode = token
				i += 1
				if i < len(tokens):
					current_type = tokens[i]
					i += 1
					while i < len(tokens) and tokens[i] not in ["арг", "рез", "аргрез"]:
						current_names.append(tokens[i].replace(",", ""))
						i += 1
				else:
					break
			else:
				if current_type is None:
					current_type = token
				else:
					current_names.append(tokens[i].replace(",", ""))
				i += 1
		if current_names and current_type is not None:
			for n in current_names:
				params.append((mode, current_type, n))
	return {"raw": header_line, "name": name_part if name_part else None, "params": params}


def execute_line(line, env, robot, interpreter=None):
	# Приводим строку к нижнему регистру и нормализуем пробелы
	normalized_line = ' '.join(line.strip().lower().split())
	# Если команда равна "использовать робот", считаем её успешно выполненной как заглушку
	if normalized_line == "использовать робот":
		if interpreter is not None:
			interpreter.output += "Команда 'использовать Робот' выполнена (заглушка).\n"
			interpreter.logger.info("Команда 'использовать Робот' выполнена (заглушка).")
		return

	try:
		if any(normalized_line.startswith(t) for t in ALLOWED_TYPES):
			process_declaration(line, env)
		elif ":=" in line:
			process_assignment(line, env)
		elif normalized_line.startswith("вывод"):
			process_output(line, env)
			if interpreter is not None:
				interpreter.output += f"Вывод: {line}\n"
		elif process_robot_command(line, robot):
			# Команда робота выполнена внутри process_robot_command
			pass
		else:
			unknown_msg = f"Unknown command: {line}"
			print(unknown_msg)
			if interpreter is not None:
				interpreter.output += unknown_msg + "\n"
	except Exception as e:
		error_message = f"Ошибка при выполнении команды: {line} - {e}"
		print(error_message)
		if interpreter is not None:
			interpreter.output += error_message + "\n"
			interpreter.logger.error(error_message)
		return

	if interpreter is not None:
		success_msg = f"Команда выполнена: {line}"
		interpreter.output += success_msg + "\n"
		interpreter.logger.info(success_msg)


class KumirLanguageInterpreter:
	"""
	Интерпретатор языка КУМИР с поддержкой пошагового исполнения.
	Записывает лог каждого шага в буфер self.output.
	"""

	def __init__(self, code):
		"""
		Инициализирует интерпретатор с исходным кодом.
		@param code: str - исходный код программы.
		"""
		self.code = code
		self.env = {}
		self.algorithms = {}
		self.main_algorithm = None
		self.robot = KumirInterpreter()
		self.output = ""  # Буфер для логирования каждого шага
		self.logger = self.robot.logger

	def get_state(self):
		"""
		Возвращает текущее состояние интерпретатора.
		@returns: dict - копия окружения, позиция робота и список окрашенных клеток.
		"""
		return {"env": self.env.copy(), "robot": self.robot.robot_pos.copy(),
				"coloredCells": list(self.robot.colored_cells)}

	def parse(self):
		"""
		Парсит исходный код, разделяя его на вступление и алгоритмы.
		@raises Exception: если алгоритмы не найдены.
		"""
		lines = preprocess_code(self.code)
		self.introduction, self.algo_sections = separate_sections(lines)
		if self.algo_sections:
			self.main_algorithm = self.algo_sections[0]
			header_info = parse_algorithm_header(self.main_algorithm["header"])
			self.main_algorithm["header_info"] = header_info
			for alg in self.algo_sections[1:]:
				info = parse_algorithm_header(alg["header"])
				alg["header_info"] = info
				if info["name"]:
					self.algorithms[info["name"]] = alg
		else:
			raise Exception("No algorithms in the program.")

	def execute_introduction(self, trace, step_delay=0, step_by_step=False):
		"""
		Выполняет вступительную часть программы, записывая лог каждого шага.
		@param trace: list - список событий.
		@param step_delay: int - задержка между шагами.
		@param step_by_step: bool - режим пошагового исполнения.
		"""
		for idx, line in enumerate(self.introduction):
			event_before = {"phase": "introduction", "commandIndex": idx, "command": line,
							"stateBefore": self.get_state(), "outputBefore": self.output}
			trace.append(event_before)
			execute_line(line, self.env, self.robot, self)
			event_after = {"phase": "introduction", "commandIndex": idx, "command": line,
						   "stateAfter": self.get_state(), "outputAfter": self.output}
			trace.append(event_after)
			if step_by_step:
				time.sleep(step_delay)

	def execute_algorithm(self, algorithm, trace, step_delay=0, step_by_step=False):
		"""
		Выполняет основной алгоритм, записывая лог каждого шага.
		@param algorithm: dict - объект алгоритма.
		@param trace: list - список событий.
		@param step_delay: int - задержка между шагами.
		@param step_by_step: bool - режим пошагового исполнения.
		"""
		for idx, line in enumerate(algorithm["body"]):
			event_before = {"phase": "main", "commandIndex": idx, "command": line, "stateBefore": self.get_state(),
							"outputBefore": self.output}
			trace.append(event_before)
			execute_line(line, self.env, self.robot, self)
			event_after = {"phase": "main", "commandIndex": idx, "command": line, "stateAfter": self.get_state(),
						   "outputAfter": self.output}
			trace.append(event_after)
			if step_by_step:
				time.sleep(step_delay)

	def interpret(self, step_by_step=True, step_delay=0):
		"""
		Интерпретирует и выполняет программу, записывая лог каждого шага.
		@param step_by_step: bool - режим пошагового исполнения.
		@param step_delay: int - задержка между шагами.
		@returns: dict - финальное состояние и трассировка выполнения.
		"""
		self.parse()
		trace = []
		self.execute_introduction(trace, step_delay, step_by_step)
		self.logger.info("Выполнение основного алгоритма:")
		self.execute_algorithm(self.main_algorithm, trace, step_delay, step_by_step)
		final_state = {"env": self.env, "robot": self.robot.robot_pos, "coloredCells": list(self.robot.colored_cells),
					   "output": self.output}
		return {"trace": trace, "finalState": final_state}


if __name__ == "__main__":
	sample_code = r'''
    | Это вступление
    цел длина, ширина, лог условие, лит мой текст
    длина := 10
    ширина := 15
    условие := да
    мой текст := "Пример текста"
    вывод "Вступление выполнено. Текст: " + мой текст

    | Это основной алгоритм (без имени)
    алг
    нач
      вывод "Площадь равна: " + (длина * ширина)
      влево
      вправо
      вверх
      вниз
      закрасить
    кон

    | Это вспомогательный алгоритм (пока не вызывается)
    алг цел площадь
    нач
      знач := длина * ширина
      вывод "Вспомогательный алгоритм: Площадь = " + знач
    кон
    '''
	interpreter = KumirLanguageInterpreter(sample_code)
	result = interpreter.interpret(step_by_step=False, step_delay=0)
	print("Результат:", result)
