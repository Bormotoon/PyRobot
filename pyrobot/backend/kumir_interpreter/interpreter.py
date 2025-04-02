# FILE START: interpreter.py
import logging

# --->>> ДОБАВЛЯЕМ ИМПОРТ НЕДОСТАЮЩИХ ИСКЛЮЧЕНИЙ <<<---
from .declarations import DeclarationError, AssignmentError, InputOutputError
from .execution import execute_lines, KumirExecutionError  # Import execution logic
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header  # Import preprocessing
from .robot_state import RobotError, SimulatedRobot  # Ensure Robot imports are here
# Убираем импорт get_eval_env из .safe_eval - УЖЕ СДЕЛАНО
from .safe_eval import KumirEvalError  # Import safe evaluation

# Constants - можно вынести в constants.py, если не используется больше нигде
MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT

logger = logging.getLogger('KumirInterpreter')


class KumirLanguageInterpreter:
	"""
	Интерпретатор языка КУМИР с поддержкой пошагового исполнения.
	"""

	# Метод __init__ остается без изменений
	def __init__(self, code, initial_field_state=None):
		""" Инициализирует интерпретатор. """
		self.code = code
		self.env = {}
		self.algorithms = {}
		self.main_algorithm = None
		self.introduction = []
		self.output = ""
		self.logger = logger
		# --- Инициализация состояния поля ---
		default_state = {
			'width': 7, 'height': 7, 'robotPos': {'x': 0, 'y': 0},
			'walls': set(), 'markers': {}, 'coloredCells': set(),
			'symbols': {}, 'radiation': {}, 'temperature': {}  # Добавлены умолчания
		}
		current_state = initial_field_state if initial_field_state else default_state

		# Валидация размеров
		self.width = current_state.get('width', default_state['width'])
		self.height = current_state.get('height', default_state['height'])
		if not isinstance(self.width, int) or self.width < 1:
			self.logger.warning(f"Invalid width received: {self.width}. Using default: {default_state['width']}")
			self.width = default_state['width']
		if not isinstance(self.height, int) or self.height < 1:
			self.logger.warning(f"Invalid height received: {self.height}. Using default: {default_state['height']}")
			self.height = default_state['height']

		# Инициализация робота с начальным состоянием
		self.robot = SimulatedRobot(
			width=self.width, height=self.height,
			initial_pos=current_state.get('robotPos', default_state['robotPos']),
			initial_walls=set(current_state.get('walls', default_state['walls'])),
			initial_markers=current_state.get('markers', default_state['markers']),
			initial_colored_cells=set(current_state.get('coloredCells', default_state['coloredCells'])),
			initial_symbols=current_state.get('symbols', default_state['symbols']),
			initial_radiation=current_state.get('radiation', default_state['radiation']),
			initial_temperature=current_state.get('temperature', default_state['temperature'])
		)
		self.logger.info(
			f"Interpreter initialized. Field: {self.width}x{self.height}. Robot at: {self.robot.robot_pos}")
		if self.robot.symbols: logger.debug(f"Initial symbols: {self.robot.symbols}")
		if self.robot.radiation: logger.debug(f"Initial radiation: {self.robot.radiation}")
		if self.robot.temperature: logger.debug(f"Initial temperature: {self.robot.temperature}")

	# Метод get_state остается без изменений
	def get_state(self):
		""" Возвращает текущее состояние интерпретатора (копия). """
		state = {
			"env": self.env.copy(),
			"width": self.width,
			"height": self.height,
			"robot": self.robot.robot_pos.copy(),
			"walls": list(self.robot.walls),
			"permanentWalls": list(self.robot.permanent_walls),
			"markers": self.robot.markers.copy(),
			"coloredCells": list(self.robot.colored_cells),
			"symbols": self.robot.symbols.copy(),
			"radiation": self.robot.radiation.copy(),
			"temperature": self.robot.temperature.copy(),
			"output": self.output
		}
		return state

	# Метод parse остается без изменений
	def parse(self):
		""" Парсит исходный код на вступление и алгоритмы. """
		self.logger.info("Starting code parsing...")
		try:
			lines = preprocess_code(self.code)
			if not lines:
				logger.warning("Code is empty after preprocessing.")
				self.introduction = []
				self.main_algorithm = None
				self.algorithms = {}
				return

			self.introduction, algo_sections = separate_sections(lines)
			logger.info(
				f"Separated into {len(self.introduction)} introduction lines and {len(algo_sections)} algorithm sections.")

			if not algo_sections:
				logger.warning("No 'алг' sections found. Treating entire code as the main algorithm body.")
				self.main_algorithm = {
					"header": "алг (без имени)",
					"body": self.introduction,
					"header_info": {"raw": "(без имени)", "name": None, "params": []}
				}
				self.introduction = []
				self.algorithms = {}
			else:
				self.main_algorithm = algo_sections[0]
				self.main_algorithm["header_info"] = parse_algorithm_header(self.main_algorithm["header"])
				logger.debug(f"Parsed main algorithm header: {self.main_algorithm['header_info']}")

				self.algorithms = {}
				for alg in algo_sections[1:]:
					try:
						info = parse_algorithm_header(alg["header"])
						alg["header_info"] = info
						if info["name"]:
							if info["name"] in self.algorithms:
								logger.warning(f"Algorithm '{info['name']}' redefined.")
							self.algorithms[info["name"]] = alg
							logger.debug(f"Parsed auxiliary algorithm '{info['name']}'. Header: {info}")
						else:
							logger.warning(
								f"Auxiliary algorithm without a name found (header: '{info['raw']}'). It cannot be called.")
					except ValueError as header_err:
						logger.error(
							f"Error parsing auxiliary algorithm header '{alg.get('header', '')}': {header_err}")
						logger.warning(f"Skipping auxiliary algorithm due to header parsing error.")

			self.logger.info("Code parsing completed successfully.")

		except SyntaxError as se:
			self.logger.error(f"Syntax error during section separation: {se}", exc_info=True)
			raise KumirExecutionError(f"Ошибка структуры программы: {se}")
		except ValueError as ve:
			self.logger.error(f"Error parsing main algorithm header: {ve}", exc_info=True)
			raise KumirExecutionError(f"Ошибка в заголовке основного алгоритма: {ve}")
		except Exception as e:
			self.logger.error(f"Unexpected parsing failed: {e}", exc_info=True)
			raise KumirExecutionError(f"Ошибка разбора программы: {e}")

	# Метод _execute_block остается без изменений (или с предыдущими правками)
	def _execute_block(self, lines, phase_name, trace, progress_callback=None):
		# ... (код без изменений) ...
		self.logger.debug(f"Executing block: {phase_name}, Lines: {len(lines)}")
		current_line_index_in_block = 0
		executed_something = False

		try:
			# Передаем управление execute_lines
			execute_lines(lines, self.env, self.robot, self)
			executed_something = True

		# --->>> ЭТОТ БЛОК EXCEPT ТЕПЕРЬ ДОЛЖЕН РАБОТАТЬ КОРРЕКТНО <<<---
		except (
				KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
				InputOutputError) as e:
			error_msg = f"Ошибка: {str(e)}"
			self.logger.error(f"Error during execution of '{phase_name}': {error_msg}", exc_info=False)
			self.output += f"{error_msg}\n"
			state_after_error = self.get_state()
			trace.append({
				"phase": phase_name, "commandIndex": -1,
				"command": "Ошибка выполнения блока", "error": str(e),
				"stateAfter": state_after_error, "outputAfter": self.output
			})
			if progress_callback:
				progress_callback({
					"phase": phase_name, "commandIndex": -1,
					"output": self.output, "robotPos": state_after_error.get("robot"),
					"error": str(e)
				})
			return {"success": False, "error": str(e), "errorIndex": -1}
		except Exception as e:
			error_msg = f"Неожиданная ошибка: {str(e)}"
			self.logger.exception(f"Unexpected error during execution of '{phase_name}': {e}")
			self.output += f"{error_msg}\n"
			state_after_error = self.get_state()
			trace.append({
				"phase": phase_name, "commandIndex": -1,
				"command": "Неожиданная ошибка блока", "error": str(e),
				"stateAfter": state_after_error, "outputAfter": self.output
			})
			if progress_callback:
				progress_callback({
					"phase": phase_name, "commandIndex": -1,
					"output": self.output, "robotPos": state_after_error.get("robot"),
					"error": str(e)
				})
			return {"success": False, "error": error_msg, "errorIndex": -1}

		self.logger.debug(f"Block '{phase_name}' executed successfully.")
		return {"success": True}

	# Метод interpret остается без изменений (или с предыдущими правками)
	def interpret(self, progress_callback=None):
		# ... (код без изменений) ...
		trace = []
		self.output = ""
		self.env = {}

		try:
			self.parse()

			if self.introduction:
				self.logger.info("Executing introduction...")
				for idx, line in enumerate(self.introduction):
					line = line.strip();
					if not line: continue
					state_before = self.get_state();
					output_before = self.output
					try:
						execute_line(line, self.env, self.robot, self)
					except (KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
							InputOutputError) as e:  # Теперь этот except корректен
						error_msg = f"Ошибка во вступлении: {str(e)}"
						self.logger.error(f"{error_msg} на строке {idx + 1}: '{line}'", exc_info=False)
						self.output += f"{error_msg} (вступление, строка {idx + 1})\n"
						state_after_error = self.get_state();
						output_after_error = self.output
						trace.append({"phase": "introduction", "commandIndex": idx, "command": line, "error": str(e),
									  "stateAfter": state_after_error, "outputAfter": output_after_error})
						if progress_callback: progress_callback(
							{"phase": "introduction", "commandIndex": idx, "output": self.output,
							 "robotPos": state_after_error.get("robot"), "error": str(e)})
						final_state = self.get_state();
						final_state["output"] = self.output
						return {"trace": trace, "finalState": final_state, "success": False, "message": error_msg,
								"errorIndex": idx}

					state_after = self.get_state();
					output_after = self.output
					trace.append(
						{"phase": "introduction", "commandIndex": idx, "command": line, "stateAfter": state_after,
						 "outputAfter": output_after})
					if progress_callback: progress_callback(
						{"phase": "introduction", "commandIndex": idx, "output": self.output,
						 "robotPos": state_after.get("robot")})
				self.logger.info("Introduction executed successfully.")
			else:
				self.logger.info("No introduction part to execute.")

			if self.main_algorithm and self.main_algorithm.get("body"):
				self.logger.info("Executing main algorithm...")
				try:
					execute_lines(self.main_algorithm["body"], self.env, self.robot, self)
					self.logger.info("Main algorithm executed successfully.")
				except (KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
						InputOutputError) as e:  # Теперь этот except корректен
					error_msg = f"Ошибка в основном алгоритме: {str(e)}"
					self.logger.error(error_msg, exc_info=False)
					self.output += f"{error_msg} (основной алгоритм)\n"
					state_after_error = self.get_state();
					output_after_error = self.output
					trace.append(
						{"phase": "main", "commandIndex": -1, "command": "Ошибка выполнения алгоритма", "error": str(e),
						 "stateAfter": state_after_error, "outputAfter": output_after_error})
					if progress_callback: progress_callback({"phase": "main", "commandIndex": -1, "output": self.output,
															 "robotPos": state_after_error.get("robot"),
															 "error": str(e)})
					final_state = self.get_state();
					final_state["output"] = self.output
					return {"trace": trace, "finalState": final_state, "success": False, "message": error_msg,
							"errorIndex": -1}
			elif not self.main_algorithm:
				logger.warning("No main algorithm found or generated after parsing.")
				if not self.introduction:
					raise KumirExecutionError("Программа не содержит исполняемого кода.")
			else:
				logger.info("Main algorithm body is empty.")

			self.logger.info("Interpretation completed successfully.")
			final_state = self.get_state()
			final_state["output"] = self.output
			return {"trace": trace, "finalState": final_state, "success": True}

		# --->>> ЭТОТ БЛОК EXCEPT ТЕПЕРЬ ДОЛЖЕН РАБОТАТЬ КОРРЕКТНО <<<---
		except (
				KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
				InputOutputError) as e:
			error_msg = f"Ошибка выполнения: {str(e)}"
			self.logger.error(error_msg, exc_info=True)  # Логируем с traceback для диагностики
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after error: {state_err}")
				state_on_error = {"env": self.env, "robot": None, "coloredCells": [], "symbols": {},
								  "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": trace, "finalState": state_on_error, "success": False, "message": error_msg}
		except Exception as e:
			error_msg = f"Критическая внутренняя ошибка: {str(e)}"
			self.logger.exception(error_msg)
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after critical error: {state_err}")
				state_on_error = {"env": self.env, "robot": None, "coloredCells": [], "symbols": {},
								  "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": trace, "finalState": state_on_error, "success": False, "message": error_msg}

# FILE END: interpreter.py
