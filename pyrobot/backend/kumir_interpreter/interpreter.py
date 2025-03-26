import logging

# from .robot_state import SimulatedRobot, RobotError # Already imported
from .execution import execute_lines, KumirExecutionError
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_state import RobotError, SimulatedRobot  # Ensure SimulatedRobot is imported here
from .safe_eval import KumirEvalError

# Constants
MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT

logger = logging.getLogger('KumirInterpreter')


class KumirLanguageInterpreter:
	"""
	Интерпретатор языка КУМИР с поддержкой пошагового исполнения.
	Выполняет код, управляет состоянием робота и генерирует трассировку.
	"""

	def __init__(self, code, initial_field_state=None):
		"""
		Инициализирует интерпретатор.
		Args:
			code (str): Исходный код программы.
			initial_field_state (dict, optional): Начальное состояние поля (width, height, robotPos, walls, markers, coloredCells).
		"""
		self.code = code
		self.env = {}
		self.algorithms = {}
		self.main_algorithm = None
		self.introduction = []
		self.output = ""
		self.logger = logger

		# Initialize Robot State
		default_state = {'width': 7, 'height': 7, 'robotPos': {'x': 0, 'y': 0},
						 'walls': set(), 'markers': {}, 'coloredCells': set()}
		current_state = initial_field_state if initial_field_state else default_state

		self.width = current_state.get('width', default_state['width'])
		self.height = current_state.get('height', default_state['height'])

		if not isinstance(self.width, int) or self.width < 1:
			self.logger.warning(f"Invalid initial width ({self.width}), defaulting to {default_state['width']}.")
			self.width = default_state['width']
		if not isinstance(self.height, int) or self.height < 1:
			self.logger.warning(f"Invalid initial height ({self.height}), defaulting to {default_state['height']}.")
			self.height = default_state['height']

		# Initialize the simulated robot
		self.robot = SimulatedRobot(
			width=self.width,
			height=self.height,
			initial_pos=current_state.get('robotPos', default_state['robotPos']),
			initial_walls=set(current_state.get('walls', default_state['walls'])),
			initial_markers=current_state.get('markers', default_state['markers']),
			initial_colored_cells=set(current_state.get('coloredCells', default_state['coloredCells']))
		)
		self.logger.info(
			f"Interpreter initialized with field {self.width}x{self.height}. Robot at {self.robot.robot_pos}")

	def get_state(self):
		"""
		Возвращает текущее состояние интерпретатора и робота.
		Returns:
			dict: Состояние окружения, позиция робота и окрашенные клетки.
		"""
		# === FIX HERE: Access attributes directly, return copies ===
		return {
			"env": self.env.copy(),
			"robot": self.robot.robot_pos.copy(),  # Use robot_pos attribute, return copy
			"coloredCells": list(self.robot.colored_cells)  # Use colored_cells attribute, convert set to list for JSON
		}

	# ==========================================================

	def parse(self):
		""" Parses the source code """
		self.logger.info("Parsing code...")
		try:
			lines = preprocess_code(self.code)
			self.introduction, algo_sections = separate_sections(lines)

			if not algo_sections:
				raise KumirExecutionError("В программе не найдены алгоритмы ('алг').")

			self.main_algorithm = algo_sections[0]
			header_info = parse_algorithm_header(self.main_algorithm["header"])
			self.main_algorithm["header_info"] = header_info
			self.logger.debug(f"Parsed main algorithm header: {header_info}")

			for alg in algo_sections[1:]:
				info = parse_algorithm_header(alg["header"])
				alg["header_info"] = info
				if info["name"]:
					if info["name"] in self.algorithms:
						self.logger.warning(f"Algorithm '{info['name']}' redefined.")
					self.algorithms[info["name"]] = alg
					self.logger.debug(f"Parsed auxiliary algorithm '{info['name']}'")
				else:
					self.logger.warning(f"Unnamed algorithm found after the first one: {info['raw']}")

			self.logger.info("Code parsing completed.")
		except Exception as e:
			self.logger.error(f"Parsing failed: {e}", exc_info=True)
			raise KumirExecutionError(f"Ошибка разбора кода: {e}")

	def _execute_block(self, lines, phase_name, trace, progress_callback=None):
		""" Executes a block of code (introduction or algorithm body). """
		for idx, line in enumerate(lines):
			# Ensure line is not empty before processing
			if not line.strip():
				continue

			state_before = self.get_state()
			output_before = self.output
			# Optimization: Only include stateBefore if needed for debugging or trace visualization
			# event_before = { ... stateBefore ... }
			# trace.append(event_before)

			try:
				# Pass self as interpreter context
				execute_lines([line], self.env, self.robot, self)

			except (RobotError, KumirEvalError, KumirExecutionError, Exception) as e:
				error_msg = f"Ошибка выполнения: {str(e)}"
				self.logger.error(f"{error_msg} в строке {idx + 1}: {line}", exc_info=False)
				self.output += error_msg + "\n"

				state_after_error = self.get_state()
				output_after_error = self.output

				error_event = {
					"phase": phase_name, "commandIndex": idx, "command": line,
					"error": str(e),
					"stateAfter": state_after_error,
					"outputAfter": output_after_error
				}
				trace.append(error_event)

				if progress_callback:
					progress_callback({
						"phase": phase_name, "commandIndex": idx, "output": self.output,
						"robotPos": state_after_error["robot"], "error": str(e)
					})
				return {"success": False, "error": str(e), "errorIndex": idx}

			# If execution succeeded
			state_after_success = self.get_state()
			output_after_success = self.output

			event_after = {
				"phase": phase_name, "commandIndex": idx, "command": line,
				"stateAfter": state_after_success,
				"outputAfter": output_after_success
			}
			trace.append(event_after)

			if progress_callback:
				progress_callback({
					"phase": phase_name, "commandIndex": idx, "output": self.output,
					"robotPos": state_after_success["robot"]
				})

		return {"success": True}

	def interpret(self, progress_callback=None):
		""" Interprets and executes the program. """
		trace = []
		try:
			self.parse()

			self.logger.info("Executing introduction...")
			intro_result = self._execute_block(self.introduction, "introduction", trace, progress_callback)
			if not intro_result["success"]:
				self.logger.error("Execution stopped due to error in introduction.")
				final_state = self.get_state()
				final_state["output"] = self.output
				return {
					"trace": trace, "finalState": final_state, "success": False,
					"message": intro_result.get("error", "Ошибка во вступлении."),
					"errorIndex": intro_result.get("errorIndex")
				}

			self.logger.info("Executing main algorithm...")
			if not self.main_algorithm:
				raise KumirExecutionError("Основной алгоритм не найден после парсинга.")

			algo_result = self._execute_block(self.main_algorithm["body"], "main", trace, progress_callback)

			final_state = self.get_state()
			final_state["output"] = self.output

			if not algo_result["success"]:
				self.logger.error("Execution stopped due to error in main algorithm.")
				return {
					"trace": trace, "finalState": final_state, "success": False,
					"message": algo_result.get("error", "Ошибка в основном алгоритме."),
					"errorIndex": algo_result.get("errorIndex")
				}

			self.logger.info("Interpretation completed successfully.")
			return {"trace": trace, "finalState": final_state, "success": True}

		except (RobotError, KumirEvalError, KumirExecutionError, Exception) as e:
			error_message = f"Критическая ошибка интерпретации: {str(e)}"
			self.logger.error(error_message, exc_info=True)
			self.output += error_message + "\n"
			try:
				final_state_on_error = self.get_state()
			except:
				final_state_on_error = {"env": self.env, "robot": None, "coloredCells": []}

			final_state_on_error["output"] = self.output
			return {
				"trace": trace, "finalState": final_state_on_error, "success": False,
				"message": error_message
			}


# Example Usage (for testing if run directly)
if __name__ == "__main__":
	sample_code = r'''
    использовать Робот
    | Это вступление
    цел длина
    длина := 5
    вывод "Длина: ", длина, нс

    алг
    нач
      вывод "Начало алгоритма", нс
      вправо
      вниз
      закрасить
      если справа стена то
          вывод "Справа стена!", нс
      иначе
          вправо
      все
      # пауза | Команда пауза теперь не блокирует сервер
      вывод "Конец алгоритма", нс
      # стоп | Команда стоп вызовет ошибку и остановит выполнение
    кон
    '''
	print("--- Running Interpreter Test ---")
	logging.basicConfig(level=logging.DEBUG)  # Setup logging for test
	test_interpreter = KumirLanguageInterpreter(sample_code)
	result = test_interpreter.interpret()
	print("\n--- Interpretation Result ---")
	# More readable output
	print(f"Success: {result['success']}")
	print(f"Message: {result.get('message', 'N/A')}")
	if not result['success']:
		print(f"Error Index: {result.get('errorIndex', 'N/A')}")
	print("\n--- Final State ---")
	print(f"  Robot Position: {result['finalState']['robot']}")
	print(f"  Colored Cells: {result['finalState']['coloredCells']}")
	print(f"  Environment: {result['finalState']['env']}")
	print("\n--- Final Output Buffer ---")
	print(result['finalState']['output'])
	# print("\n--- Trace ---")
	# import json
	# print(json.dumps(result['trace'], indent=2, ensure_ascii=False))
	print("--- Test End ---")
