"""
robot_interpreter.py
Описание: Интерпретатор робота для языка KUMIR.
Обеспечивает хранение состояния робота, выполнение команд и логирование отладки.
"""

import logging
import re


class KumirInterpreterError(Exception):
	"""
	Пользовательское исключение для ошибок интерпретатора языка KUMIR.
	"""
	pass


class KumirInterpreter:
	"""
	Интерпретатор робота для языка KUMIR.

	Атрибуты:
	  robot_pos (dict): Текущая позиция робота в виде {'x': int, 'y': int}.
	  walls (set): Множество строк с описанием стен.
	  markers (dict): Объект с маркерами на поле.
	  colored_cells (set): Множество закрашенных клеток (формат "x,y").
	  logger (Logger): Логгер для отладки.
	"""

	def __init__(self):
		"""
		Инициализирует состояние робота и настраивает логирование.
		"""
		self.robot_pos = {"x": 0, "y": 0}
		self.walls = set()
		self.markers = {}
		self.colored_cells = set()

		# Настройка логгера
		self.logger = logging.getLogger('KumirInterpreter')
		handler = logging.StreamHandler()
		formatter = logging.Formatter('%(asctime)s - KumirInterpreter - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)
		self.logger.setLevel(logging.DEBUG)

	def reset(self):
		"""
		Сбрасывает состояние робота: позиция в (0, 0), очистка стен, маркеров и окрашенных клеток.
		"""
		self.logger.info("Interpreter state has been reset.")
		self.robot_pos = {"x": 0, "y": 0}
		self.walls.clear()
		self.markers.clear()
		self.colored_cells.clear()

	def interpret(self, code):
		"""
		Интерпретирует и выполняет заданный код на языке KUMIR.

		@param code: str - исходный код.
		@returns: dict - результат выполнения с данными робота и поля.
		"""
		self.logger.info("Starting code interpretation.")
		self.logger.debug(f"Input code:\n{code}")
		try:
			tokens = self.tokenize(code)
			self.logger.debug(f"Tokens: {tokens}")
			ast = self.parse(tokens)
			self.logger.debug(f"AST: {ast}")
			result = self.execute(ast)
			self.logger.info("Interpretation completed successfully.")
			self.logger.debug(f"Execution result: {result}")
			return {"success": True, "result": result}
		except KumirInterpreterError as e:
			self.logger.error(f"Interpreter error: {e}")
			return {"success": False, "message": str(e)}
		except Exception as e:
			self.logger.exception("Unknown error during code interpretation.")
			return {"success": False, "message": f"Unknown error: {str(e)}"}

	def tokenize(self, code):
		"""
		Разбивает код на строки (токены), удаляя пустые строки и комментарии.

		@param code: str - исходный код.
		@returns: list of str - список токенов.
		"""
		tokens = []
		lines = code.strip().split('\n')
		for line in lines:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			tokens.append(line)
		self.logger.debug(f"Tokenized code: {tokens}")
		return tokens

	def parse(self, tokens):
		"""
		Преобразует список токенов в абстрактное синтаксическое дерево (AST).

		@param tokens: list of str - список токенов.
		@returns: list of dict - AST.
		@raises KumirInterpreterError: если синтаксис некорректен.
		"""
		ast = []
		current_algorithm = None
		for token in tokens:
			token_lower = token.lower()
			self.logger.debug(f"Parsing token: {token_lower}")

			if token_lower == "использовать робот":
				# Команда для сброса состояния робота
				ast.append({"type": "use_robot"})
				self.logger.debug("Added 'use_robot' command to AST.")
			elif token_lower == "алг":
				# Начало алгоритма
				current_algorithm = {"type": "algorithm", "commands": []}
				ast.append(current_algorithm)
				self.logger.debug("Started algorithm block ('алг').")
			elif token_lower == "нач":
				if not current_algorithm:
					raise KumirInterpreterError("Syntax error: 'нач' without 'алг'")
				current_algorithm["in_block"] = True
				self.logger.debug("Beginning of algorithm body ('нач').")
			elif token_lower == "кон":
				if not current_algorithm or not current_algorithm.get("in_block"):
					raise KumirInterpreterError("Syntax error: 'кон' without 'нач'")
				current_algorithm["in_block"] = False
				self.logger.debug("End of algorithm body ('кон').")
			else:
				if not current_algorithm or not current_algorithm.get("in_block"):
					raise KumirInterpreterError(f"Syntax error: Command '{token}' outside of algorithm block")
				command = self.parse_command(token)
				current_algorithm["commands"].append(command)
				self.logger.debug(f"Added command to algorithm: {command}")

		self.logger.debug(f"Constructed AST: {ast}")
		return ast

	def parse_command(self, command_str):
		"""
		Преобразует строку команды в объект команды.

		@param command_str: str - строка команды.
		@returns: dict - объект команды.
		@raises KumirInterpreterError: если команда неизвестна.
		"""
		command_str_lower = command_str.lower().strip()
		self.logger.debug(f"Parsing command: {command_str_lower}")

		# Команды перемещения (action commands)
		if command_str_lower == "влево":
			return {"type": "action", "command": "left"}
		elif command_str_lower == "вправо":
			return {"type": "action", "command": "right"}
		elif command_str_lower == "вверх":
			return {"type": "action", "command": "up"}
		elif command_str_lower == "вниз":
			return {"type": "action", "command": "down"}
		elif command_str_lower == "закрасить":
			return {"type": "action", "command": "paint"}

		# Команды условий по направлению
		if re.match(r'^(слева|справа|сверху|снизу)\s+(стена|свободно)$', command_str_lower):
			direction, status = command_str_lower.split()
			direction_map = {"слева": "left", "справа": "right", "сверху": "up", "снизу": "down"}
			status_map = {"стена": "wall", "свободно": "free"}
			return {"type": "condition", "direction": direction_map.get(direction, direction),
					"status": status_map.get(status, status)}

		# Команды проверки состояния клетки
		if re.match(r'^клетка\s+(закрашена|чистая)$', command_str_lower):
			parts = command_str_lower.split()
			cell_status_map = {"закрашена": "painted", "чистая": "clear"}
			return {"type": "condition_cell", "status": cell_status_map.get(parts[1], parts[1])}

		# Команды измерения
		if command_str_lower in ["температура", "радиация"]:
			measurement_map = {"температура": "temperature", "радиация": "radiation"}
			return {"type": "measurement", "command": measurement_map.get(command_str_lower, command_str_lower)}

		raise KumirInterpreterError(f"Unknown command: {command_str}")

	def execute(self, ast):
		"""
		Выполняет AST и возвращает итоговое состояние.

		@param ast: list of dict - AST.
		@returns: dict - состояние робота, стен, маркеров и окрашенных клеток.
		"""
		self.logger.info("Starting AST execution.")
		for node in ast:
			self.logger.debug(f"Executing AST node: {node}")
			if node["type"] == "use_robot":
				self.reset()
			elif node["type"] == "algorithm":
				for command in node["commands"]:
					self.execute_command(command)
		self.logger.info("AST execution completed.")
		return {"robotPos": self.robot_pos, "walls": list(self.walls), "markers": self.markers,
				"coloredCells": list(self.colored_cells)}

	def execute_command(self, command):
		"""
		Выполняет одну команду, представленную в виде объекта.
		@param command: dict - объект команды.
		@raises KumirInterpreterError: если команда неизвестна.
		"""
		self.logger.debug(f"Executing command: {command}")
		cmd_type = command["type"]

		if cmd_type == "action":
			action = command["command"]
			if action == "left":
				self.go_left()
			elif action == "right":
				self.go_right()
			elif action == "up":
				self.go_up()
			elif action == "down":
				self.go_down()
			elif action == "paint":
				self.do_paint()
			else:
				raise KumirInterpreterError(f"Unknown action command: {action}")
		elif cmd_type == "condition":
			direction = command["direction"]
			status = command["status"]
			condition_result = self.check_direction(direction, status)
			self.logger.info(f"Condition [{direction} {status}]: {condition_result}")
		elif cmd_type == "condition_cell":
			status = command["status"]
			condition_result = self.check_cell(status)
			self.logger.info(f"Condition [cell {status}]: {condition_result}")
		elif cmd_type == "measurement":
			measure = command["command"]
			value = self.do_measurement(measure)
			self.logger.info(f"Measurement '{measure}': result = {value}")
		else:
			raise KumirInterpreterError(f"Unknown command type: {cmd_type}")

	def go_right(self):
		new_x = self.robot_pos["x"] + 1
		self.logger.debug(f"Attempting to move right to X={new_x}, Y={self.robot_pos['y']}")
		if self.is_move_allowed(new_x, self.robot_pos["y"]):
			self.robot_pos["x"] = new_x
			self.logger.info(f"Robot moved right. New position: {self.robot_pos}")
		else:
			raise KumirInterpreterError("Робот упёрся в стену справа.")

	def go_left(self):
		new_x = self.robot_pos["x"] - 1
		self.logger.debug(f"Attempting to move left to X={new_x}, Y={self.robot_pos['y']}")
		if self.is_move_allowed(new_x, self.robot_pos["y"]):
			self.robot_pos["x"] = new_x
			self.logger.info(f"Robot moved left. New position: {self.robot_pos}")
		else:
			raise KumirInterpreterError("Робот упёрся в стену слева.")

	def go_up(self):
		new_y = self.robot_pos["y"] - 1
		self.logger.debug(f"Attempting to move up to X={self.robot_pos['x']}, Y={new_y}")
		if self.is_move_allowed(self.robot_pos["x"], new_y):
			self.robot_pos["y"] = new_y
			self.logger.info(f"Robot moved up. New position: {self.robot_pos}")
		else:
			raise KumirInterpreterError("Робот упёрся в стену сверху.")

	def go_down(self):
		new_y = self.robot_pos["y"] + 1
		self.logger.debug(f"Attempting to move down to X={self.robot_pos['x']}, Y={new_y}")
		if self.is_move_allowed(self.robot_pos["x"], new_y):
			self.robot_pos["y"] = new_y
			self.logger.info(f"Robot moved down. New position: {self.robot_pos}")
		else:
			raise KumirInterpreterError("Робот упёрся в стену снизу.")

	def do_paint(self):
		"""Закрашивает текущую клетку, если она не закрашена."""
		pos_str = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		self.logger.debug(f"Attempting to paint cell: {pos_str}")
		if pos_str not in self.colored_cells:
			self.colored_cells.add(pos_str)
			self.logger.info(f"Cell {pos_str} painted.")
		else:
			raise KumirInterpreterError("Cell is already painted.")

	def check_direction(self, direction, status):
		"""
		Проверяет наличие стены или свободное пространство в указанном направлении.
		@param direction: str - направление ("left", "right", "up", "down").
		@param status: str - ожидаемый статус ("wall" или "free").
		@returns: bool - True, если условие выполнено, иначе False.
		"""
		self.logger.debug(f"Checking condition: {direction} {status}")
		dx, dy = 0, 0
		if direction == "left":
			dx = -1
		elif direction == "right":
			dx = 1
		elif direction == "up":
			dy = -1
		elif direction == "down":
			dy = 1
		else:
			raise KumirInterpreterError(f"Unknown direction: {direction}")

		target_x = self.robot_pos["x"] + dx
		target_y = self.robot_pos["y"] + dy

		# Формируем строку "x1,y1,x2,y2" для проверки наличия стены
		wall = f"{min(self.robot_pos['x'], target_x)},{min(self.robot_pos['y'], target_y)},{max(self.robot_pos['x'], target_x)},{max(self.robot_pos['y'], target_y)}"

		if status == "wall":
			result = (wall in self.walls)
			self.logger.debug(f"Wall {'exists' if result else 'does not exist'} along path {wall}.")
			return result
		elif status == "free":
			in_bounds = (0 <= target_x <= 10 and 0 <= target_y <= 10)
			no_wall = (wall not in self.walls)
			result = (in_bounds and no_wall)
			self.logger.debug(f"Free: {'yes' if result else 'no'}.")
			return result
		else:
			raise KumirInterpreterError(f"Unknown status: {status}")

	def check_cell(self, status):
		"""
		Проверяет, закрашена ли текущая клетка робота.
		@param status: str - ожидаемый статус ("painted" или "clear").
		@returns: bool - True, если условие выполнено, иначе False.
		"""
		pos_str = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		self.logger.debug(f"Checking cell state: {pos_str} - {status}")
		if status == "painted":
			result = (pos_str in self.colored_cells)
			self.logger.debug(f"Cell painted: {'yes' if result else 'no'}.")
			return result
		elif status == "clear":
			result = (pos_str not in self.colored_cells)
			self.logger.debug(f"Cell clear: {'yes' if result else 'no'}.")
			return result
		else:
			raise KumirInterpreterError(f"Unknown cell status: {status}")

	def do_measurement(self, measure):
		"""
		Выполняет измерение (например, температуры или радиации).
		@param measure: str - тип измерения.
		@returns: float - результат измерения.
		"""
		self.logger.debug(f"Performing measurement: {measure}")
		if measure == "temperature":
			return 25.0
		elif measure == "radiation":
			return 10.5
		else:
			raise KumirInterpreterError(f"Unknown measurement: {measure}")

	def is_move_allowed(self, x, y):
		self.logger.debug(f"Checking if move is allowed to X={x}, Y={y}")
		# Проверка границ поля (при необходимости замените 11 на актуальное значение ширины/высоты)
		if x < 0 or y < 0 or x >= 11 or y >= 11:
			self.logger.debug("Move disallowed: out of field bounds.")
			return False

		current_x = self.robot_pos["x"]
		current_y = self.robot_pos["y"]

		# Определяем направление движения и ожидаемую стену
		if x > current_x:  # движение вправо
			expected_wall = f"{current_x + 1},{current_y},{current_x + 1},{current_y + 1}"
		elif x < current_x:  # движение влево
			expected_wall = f"{current_x},{current_y},{current_x},{current_y + 1}"
		elif y > current_y:  # движение вниз
			expected_wall = f"{current_x},{current_y + 1},{current_x + 1},{current_y + 1}"
		elif y < current_y:  # движение вверх
			expected_wall = f"{current_x},{current_y},{current_x + 1},{current_y}"
		else:
			expected_wall = None

		if expected_wall and expected_wall in self.walls:
			self.logger.debug(f"Move disallowed: wall detected along path {expected_wall}.")
			return False

		self.logger.debug("Move allowed.")
		return True
