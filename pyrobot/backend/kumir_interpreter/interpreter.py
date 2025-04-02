# FILE START: interpreter.py
import logging

from .declarations import DeclarationError, AssignmentError, InputOutputError, KumirInputRequiredError
# --->>> ИЗМЕНЯЕМ ИМПОРТ execute_lines, добавляем KumirExecutionError <<<---
from .execution import execute_lines, KumirExecutionError
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_state import RobotError, SimulatedRobot
from .safe_eval import KumirEvalError

MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT

logger = logging.getLogger('KumirInterpreter')


class KumirLanguageInterpreter:
	"""
	Интерпретатор языка КУМИР с поддержкой пошагового исполнения.
	"""

	def __init__(self, code, initial_field_state=None):
		""" Инициализирует интерпретатор. """
		self.code = code
		self.env = {}
		self.algorithms = {}
		self.main_algorithm = None
		self.introduction = []
		self.output = ""
		self.logger = logger
		self.trace = []  # Добавляем атрибут для трассировки
		self.progress_callback = None  # Для хранения колбэка

		default_state = {
			'width': 7, 'height': 7, 'robotPos': {'x': 0, 'y': 0},
			'walls': set(), 'markers': {}, 'coloredCells': set(),
			'symbols': {}, 'radiation': {}, 'temperature': {}
		}
		current_state = initial_field_state if initial_field_state else default_state

		self.width = current_state.get('width', default_state['width'])
		self.height = current_state.get('height', default_state['height'])
		if not isinstance(self.width, int) or self.width < 1:
			self.logger.warning(f"Invalid width received: {self.width}. Using default: {default_state['width']}")
			self.width = default_state['width']
		if not isinstance(self.height, int) or self.height < 1:
			self.logger.warning(f"Invalid height received: {self.height}. Using default: {default_state['height']}")
			self.height = default_state['height']

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
					"body": self.introduction,  # Весь код идет в тело
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

	# Метод _execute_block больше не нужен, т.к. логика перенесена в interpret
	# def _execute_block(...)

	def interpret(self, progress_callback=None):
		""" Полный цикл: парсинг и выполнение кода Кумира. """
		self.trace = []  # Сбрасываем трассировку
		self.output = ""  # Сбрасываем вывод
		self.env = {}  # Сбрасываем окружение
		self.progress_callback = progress_callback  # Сохраняем колбэк

		last_error_index = -1  # Для хранения индекса последней ошибки

		try:
			# 1. Парсинг кода
			self.parse()

			# 2. Выполнение вступления
			if self.introduction:
				self.logger.info("Executing introduction...")
				# execute_lines теперь сама обрабатывает ошибки и заполняет trace
				execute_lines(self.introduction, self.env, self.robot, self, self.trace, self.progress_callback,
							  "introduction")
				self.logger.info("Introduction executed successfully.")
			else:
				self.logger.info("No introduction part to execute.")

			# 3. Выполнение основного алгоритма
			if self.main_algorithm and self.main_algorithm.get("body"):
				self.logger.info("Executing main algorithm...")
				# Генерируем "оригинальные" индексы для основного алгоритма
				# В реальном парсере они бы брались из AST
				main_body_indices = list(range(len(self.main_algorithm["body"])))
				execute_lines(self.main_algorithm["body"], self.env, self.robot, self, self.trace,
							  self.progress_callback, "main", main_body_indices)
				self.logger.info("Main algorithm executed successfully.")
			elif not self.main_algorithm:
				logger.warning("No main algorithm found or generated after parsing.")
				if not self.introduction: raise KumirExecutionError("Программа не содержит исполняемого кода.")
			else:
				logger.info("Main algorithm body is empty.")

			# 4. Успешное завершение
			self.logger.info("Interpretation completed successfully.")
			final_state = self.get_state()
			# Убедимся, что вывод включен в финальное состояние
			final_state["output"] = self.output
			return {"trace": self.trace, "finalState": final_state, "success": True}

		except KumirInputRequiredError as e:
			logger.info(f"Execution paused, input required for '{e.var_name}'.")
			self.output += f"Ожидание ввода для '{e.var_name}'...\n"
			state_at_input = self.get_state()
			state_at_input["output"] = self.output
			# Находим индекс строки, где произошел запрос ввода
			error_line_index = e.line_index if hasattr(e, 'line_index') else -1
			last_error_index = error_line_index

			return {
				"trace": self.trace,
				"finalState": state_at_input,
				"success": False,
				"input_required": True,
				"var_name": e.var_name,
				"prompt": e.prompt,
				"target_type": e.target_type,
				"message": f"Требуется ввод для переменной '{e.var_name}'",
				"errorIndex": error_line_index  # Добавляем индекс строки
			}

		except (
				KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
				InputOutputError) as e:
			# Обработка всех остальных известных ошибок выполнения
			error_msg = f"Ошибка выполнения: {str(e)}"
			# Используем сохраненный индекс ошибки, если есть
			error_line_index = e.line_index if hasattr(e,
													   'line_index') and e.line_index is not None else last_error_index
			last_error_index = error_line_index  # Обновляем индекс последней ошибки

			self.logger.error(error_msg, exc_info=False)
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after error: {state_err}"); state_on_error = {"env": self.env,
																								 "robot": None,
																								 "output": self.output}  # Упрощенный fallback
			state_on_error["output"] = self.output
			return {
				"trace": self.trace,  # Включаем трассировку до ошибки
				"finalState": state_on_error,
				"success": False,
				"message": error_msg,
				"errorIndex": error_line_index  # Добавляем индекс строки
			}
		except Exception as e:
			# Обработка непредвиденных ошибок
			error_msg = f"Критическая внутренняя ошибка: {str(e)}"
			self.logger.exception(error_msg)  # Логируем с полным traceback
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after critical error: {state_err}"); state_on_error = {
					"env": self.env, "robot": None, "output": self.output}
			state_on_error["output"] = self.output
			return {
				"trace": self.trace,
				"finalState": state_on_error,
				"success": False,
				"message": error_msg,
				"errorIndex": last_error_index  # Индекс последней известной строки
			}

# FILE END: interpreter.py
