# FILE START: interpreter.py
import logging

from .declarations import DeclarationError, AssignmentError, InputOutputError
from .execution import execute_lines, KumirExecutionError  # execute_lines теперь будет использовать стек
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_state import RobotError, SimulatedRobot
from .safe_eval import KumirEvalError

# Импорты для работы со стеком и окружениями

MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT

logger = logging.getLogger('KumirInterpreter')

# Максимальная глубина рекурсии/стека вызовов для предотвращения переполнения
MAX_CALL_STACK_DEPTH = 100


class CallStackFrame:
	"""Представляет один фрейм в стеке вызовов."""

	def __init__(self, algo_name, local_env, return_address=None):
		self.algo_name = algo_name  # Имя вызванного алгоритма (для отладки)
		self.local_env = local_env  # Локальное окружение (переменные и параметры)

	# self.return_address = return_address # Можно добавить указатель на место возврата

	def __repr__(self):
		return f"<Frame: {self.algo_name}, Env: {list(self.local_env.keys())}>"


class KumirLanguageInterpreter:
	"""
	Интерпретатор языка КУМИР с поддержкой стека вызовов и пошагового исполнения.
	"""

	def __init__(self, code, initial_field_state=None):
		self.code = code
		# self.env больше не используется напрямую, используем стек
		# self.env = {}
		self.algorithms = {}
		self.main_algorithm = None
		self.introduction = []
		self.output = ""
		self.logger = logger
		self.robot = None  # Инициализируем робота позже

		# --->>> ИНИЦИАЛИЗАЦИЯ СТЕКА ВЫЗОВОВ <<<---
		self.call_stack = []
		# Глобальное окружение будет в самом нижнем фрейме стека
		self.global_env = {}

		# Инициализация робота и поля (как раньше)
		self._initialize_robot_and_field(initial_field_state)
		self.logger.info(
			f"Interpreter initialized. Field: {self.width}x{self.height}. Robot at: {self.robot.robot_pos}")

	def _initialize_robot_and_field(self, initial_field_state):
		"""Инициализирует робота и размеры поля."""
		default_state = {
			'width': 7, 'height': 7, 'robotPos': {'x': 0, 'y': 0},
			'walls': set(), 'markers': {}, 'coloredCells': set(),
			'symbols': {}, 'radiation': {}, 'temperature': {}
		}
		current_state = initial_field_state if initial_field_state else default_state
		self.width = current_state.get('width', default_state['width'])
		self.height = current_state.get('height', default_state['height'])
		# Валидация размеров...
		if not isinstance(self.width, int) or self.width < 1: self.width = default_state['width']
		if not isinstance(self.height, int) or self.height < 1: self.height = default_state['height']

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

	def get_current_environment(self):
		"""Возвращает окружение текущего фрейма стека."""
		if not self.call_stack:
			# Это может произойти до начала выполнения или после ошибки
			# Вернем глобальное окружение как запасной вариант
			logger.warning("Call stack is empty, returning global environment.")
			return self.global_env
		# Возвращаем локальное окружение из верхнего фрейма
		return self.call_stack[-1].local_env

	def push_call_frame(self, algo_name, local_env):
		"""Помещает новый фрейм на стек вызовов."""
		if len(self.call_stack) >= MAX_CALL_STACK_DEPTH:
			logger.error(f"Maximum call stack depth ({MAX_CALL_STACK_DEPTH}) exceeded during call to '{algo_name}'.")
			raise KumirExecutionError("Превышена максимальная глубина рекурсии.")
		frame = CallStackFrame(algo_name, local_env)
		self.call_stack.append(frame)
		logger.debug(f"Pushed frame for '{algo_name}'. Stack depth: {len(self.call_stack)}")

	def pop_call_frame(self):
		"""Снимает верхний фрейм со стека вызовов."""
		if not self.call_stack:
			logger.error("Attempted to pop from an empty call stack.")
			raise KumirExecutionError("Внутренняя ошибка: Попытка возврата из пустого стека вызовов.")
		frame = self.call_stack.pop()
		logger.debug(f"Popped frame for '{frame.algo_name}'. Stack depth: {len(self.call_stack)}")
		return frame  # Возвращаем снятый фрейм (может быть полезно для возврата значений)

	def get_state(self):
		"""Возвращает текущее состояние интерпретатора (копия)."""
		# Используем текущее окружение для env
		current_env = self.get_current_environment()
		state = {
			# Используем текущее окружение из стека
			"env": current_env.copy() if current_env else {},  # Копия окружения переменных
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
			"output": self.output,
			# Добавим информацию о стеке для отладки (опционально)
			# "callStackDepth": len(self.call_stack),
			# "currentAlgorithm": self.call_stack[-1].algo_name if self.call_stack else "(global)"
		}
		return state

	# Метод parse остается без изменений (использует новую parse_algorithm_header)
	def parse(self):
		""" Парсит исходный код на вступление и алгоритмы. """
		# ... (код без изменений, использует новую parse_algorithm_header) ...
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
					# Используем результат нового парсера
					"header_info": parse_algorithm_header("алг (без имени)")
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

	# _execute_block больше не нужен в таком виде, т.к. execute_lines будет основной точкой входа
	# def _execute_block(...)

	def interpret(self, progress_callback=None):
		""" Полный цикл: парсинг и выполнение кода Кумира с использованием стека вызовов. """
		trace = []
		self.output = ""
		self.global_env = {}  # Сбрасываем глобальное окружение
		self.call_stack = []  # Очищаем стек вызовов
		# TODO: Сбросить состояние робота? Или использовать initial_state?
		# Пока сбрасываем робота при инициализации интерпретатора.

		try:
			# 1. Парсинг кода
			self.parse()

			# 2. Помещаем глобальное окружение в стек как базовый фрейм
			self.push_call_frame("(global)", self.global_env)

			# 3. Выполнение вступительной части (в глобальном окружении)
			if self.introduction:
				self.logger.info("Executing introduction in global scope...")
				# Передаем self (интерпретатор) в execute_lines, чтобы он мог работать со стеком
				execute_lines(self.introduction, self)  # Убрали env и robot
				self.logger.info("Introduction executed successfully.")
			else:
				self.logger.info("No introduction part to execute.")

			# 4. Выполнение основного алгоритма (если есть)
			if self.main_algorithm and self.main_algorithm.get("body"):
				self.logger.info("Executing main algorithm...")
				main_algo_name = self.main_algorithm["header_info"].get("name", "(main)")
				# Создаем окружение для основного алгоритма (может быть таким же, как глобальное,
				# или отдельным в зависимости от правил Кумира - пока делаем отдельным, но пустым)
				main_env = {}  # Или self.global_env.copy()? Пока пустое.
				# TODO: Если у основного алгоритма есть параметры, их нужно обработать (откуда брать значения?)
				# Обычно у главного `алг` нет параметров.
				self.push_call_frame(main_algo_name, main_env)  # Помещаем фрейм основного алг на стек

				try:
					# Выполняем тело основного алгоритма
					execute_lines(self.main_algorithm["body"], self)
					self.logger.info("Main algorithm executed successfully.")
				finally:
					# Снимаем фрейм основного алгоритма со стека по завершении (или ошибке)
					self.pop_call_frame()

			elif not self.main_algorithm:
				logger.warning("No main algorithm found or generated after parsing.")
				if not self.introduction:
					raise KumirExecutionError("Программа не содержит исполняемого кода.")
			else:
				logger.info("Main algorithm body is empty.")

			# 5. Проверка стека после выполнения
			if len(self.call_stack) != 1:  # Должен остаться только глобальный фрейм
				logger.warning(
					f"Call stack has unexpected depth ({len(self.call_stack)}) after execution. Should be 1.")
			# Возможно, где-то не сработал pop_call_frame при ошибке?

			# 6. Успешное завершение
			self.logger.info("Interpretation completed successfully.")
			final_state = self.get_state()  # Получаем финальное состояние (с глобальным env)
			final_state["output"] = self.output
			# Добавляем результат трассировки (если она собиралась)
			# TODO: Реализовать сбор трассировки внутри execute_lines/handle_algorithm_call
			return {"trace": trace, "finalState": final_state, "success": True}

		# Блок except остается как в предыдущей версии, он ловит ошибки из execute_lines
		except (
				KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
				InputOutputError) as e:
			error_msg = f"Ошибка выполнения: {str(e)}"
			# Логируем ошибку и стек вызовов на момент ошибки
			self.logger.error(error_msg, exc_info=True)
			self.logger.error(f"Call stack at error: {self.call_stack}")
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after error: {state_err}")
				state_on_error = {"env": self.global_env, "robot": None, "coloredCells": [], "symbols": {},
								  "output": self.output}  # Fallback
			state_on_error["output"] = self.output
			return {"trace": trace, "finalState": state_on_error, "success": False, "message": error_msg}
		except Exception as e:
			error_msg = f"Критическая внутренняя ошибка: {str(e)}"
			self.logger.exception(error_msg)
			self.logger.error(f"Call stack at critical error: {self.call_stack}")
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after critical error: {state_err}")
				state_on_error = {"env": self.global_env, "robot": None, "coloredCells": [], "symbols": {},
								  "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": trace, "finalState": state_on_error, "success": False, "message": error_msg}

# FILE END: interpreter.py
