# FILE START: interpreter.py
import logging

from .declarations import DeclarationError, AssignmentError, InputOutputError, KumirInputRequiredError
from .execution import execute_lines, KumirExecutionError
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_state import RobotError, SimulatedRobot
from .safe_eval import KumirEvalError

# Импортируем для создания scope при вызове

MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT
logger = logging.getLogger('KumirInterpreter')


class KumirLanguageInterpreter:
	"""Интерпретатор языка КУМИР с поддержкой вызова алгоритмов."""

	def __init__(self, code, initial_field_state=None):
		"""Инициализирует интерпретатор."""
		self.code = code
		self.global_env = {}  # Глобальное окружение
		self.algorithms = {}  # Словарь для хранения тел алгоритмов
		self.main_algorithm = None
		self.introduction = []
		self.output = ""
		self.logger = logger
		self.trace = []
		self.progress_callback = None

		# --->>> СТЕК ВЫЗОВОВ <<<---
		# Каждый элемент стека будет словарем:
		# {'name': имя_алгоритма, 'env': локальное_окружение, 'caller_env': окружение_вызывающего, 'return_target': имя_переменной_для_рез}
		self.call_stack = []
		# --- <<< КОНЕЦ ИЗМЕНЕНИЯ >>> ---

		default_state = {'width': 7, 'height': 7, 'robotPos': {'x': 0, 'y': 0}, 'walls': set(), 'markers': {},
						 'coloredCells': set(), 'symbols': {}, 'radiation': {}, 'temperature': {}}
		current_state = initial_field_state if initial_field_state else default_state
		self.width = current_state.get('width', default_state['width']);
		self.height = current_state.get('height', default_state['height'])
		if not isinstance(self.width, int) or self.width < 1: self.logger.warning(
			f"Invalid width: {self.width}. Using default."); self.width = default_state['width']
		if not isinstance(self.height, int) or self.height < 1: self.logger.warning(
			f"Invalid height: {self.height}. Using default."); self.height = default_state['height']
		self.robot = SimulatedRobot(width=self.width, height=self.height,
			initial_pos=current_state.get('robotPos', default_state['robotPos']),
			initial_walls=set(current_state.get('walls', [])),  # Убедимся, что создаем set
			initial_markers=current_state.get('markers', {}),
			initial_colored_cells=set(current_state.get('coloredCells', [])),  # Убедимся, что создаем set
			initial_symbols=current_state.get('symbols', {}), initial_radiation=current_state.get('radiation', {}),
			initial_temperature=current_state.get('temperature', {}))
		self.logger.info(
			f"Interpreter initialized. Field: {self.width}x{self.height}. Robot at: {self.robot.robot_pos}")

	# --->>> МЕТОДЫ ДЛЯ РАБОТЫ СО СТЕКОМ И ОКРУЖЕНИЕМ <<<---
	def get_current_env(self):
		"""Возвращает текущее активное окружение (локальное или глобальное)."""
		if self.call_stack:
			return self.call_stack[-1]['env']
		return self.global_env

	def push_call_stack(self, algo_name, local_env, caller_env, return_target=None):
		"""Добавляет запись о вызове в стек."""
		self.call_stack.append({'name': algo_name, 'env': local_env, 'caller_env': caller_env,
			# Ссылка на окружение, куда возвращать рез/аргрез
			'return_target': return_target  # Для функций (алг имя (арг...) тип рез)
		})
		self.logger.debug(
			f"Pushed '{algo_name}' onto call stack. Depth: {len(self.call_stack)}. Return target: {return_target}")

	def pop_call_stack(self):
		"""Удаляет запись о вызове из стека и возвращает ее."""
		if not self.call_stack:
			self.logger.error("Attempted to pop from an empty call stack.")
			return None
		popped = self.call_stack.pop()
		self.logger.debug(f"Popped '{popped.get('name')}' from call stack. Depth: {len(self.call_stack)}")
		return popped

	def resolve_variable(self, var_name):
		"""Ищет переменную сначала в локальном, затем в глобальном окружении."""
		current_env = self.get_current_env()
		if var_name in current_env:
			return current_env[var_name]
		if var_name in self.global_env:
			# Если переменная не найдена локально, но есть глобально, возвращаем ее
			# (Кумир поддерживает доступ к глобальным переменным из процедур)
			return self.global_env[var_name]
		# Переменная не найдена нигде
		return None  # Или бросать DeclarationError? Зависит от контекста вызова

	def update_variable(self, var_name, value):
		"""Обновляет значение переменной в текущем или глобальном окружении."""
		current_env = self.get_current_env()
		if var_name in current_env:
			if isinstance(current_env[var_name], dict):
				current_env[var_name]['value'] = value
				logger.debug(f"Updated local var '{var_name}' to {value}")
			else:
				logger.warning(f"Cannot update local var '{var_name}': invalid structure {current_env[var_name]}")
		elif var_name in self.global_env:
			if isinstance(self.global_env[var_name], dict):
				self.global_env[var_name]['value'] = value
				logger.debug(f"Updated global var '{var_name}' to {value}")
			else:
				logger.warning(f"Cannot update global var '{var_name}': invalid structure {self.global_env[var_name]}")
		else:
			# Попытка обновить несуществующую переменную - ошибка присваивания
			raise AssignmentError(f"Попытка присвоить значение необъявленной переменной '{var_name}'.")

	# --- <<< КОНЕЦ НОВЫХ МЕТОДОВ >>> ---

	def get_state(self):
		"""Возвращает текущее состояние интерпретатора (копия)."""
		# Используем get_current_env для получения переменных текущего scope
		current_env = self.get_current_env()
		state = {# Используем копию текущего окружения
			"env": current_env.copy() if current_env else {}, "global_env": self.global_env.copy(),
			# Можно добавить для отладки
			"call_stack_depth": len(self.call_stack),  # Глубина стека
			# Остальное состояние поля и робота
			"width": self.width, "height": self.height, "robot": self.robot.robot_pos.copy(),
			"walls": list(self.robot.walls), "permanentWalls": list(self.robot.permanent_walls),
			"markers": self.robot.markers.copy(), "coloredCells": list(self.robot.colored_cells),
			"symbols": self.robot.symbols.copy(), "radiation": self.robot.radiation.copy(),
			"temperature": self.robot.temperature.copy(), "output": self.output}
		return state

	def parse(self):
		"""Парсит исходный код на вступление и алгоритмы."""
		self.logger.info("Starting code parsing...")
		try:
			lines = preprocess_code(self.code)
			if not lines: logger.warning(
				"Code is empty after preprocessing."); self.introduction = []; self.main_algorithm = None; self.algorithms = {}; return

			self.introduction, algo_sections = separate_sections(lines)
			logger.info(
				f"Separated into {len(self.introduction)} intro lines and {len(algo_sections)} algorithm sections.")

			if not algo_sections:
				logger.warning("No 'алг' sections found. Treating entire code as main algorithm body.")
				self.main_algorithm = {"header": "алг (без имени)", "body": self.introduction,
									   "header_info": {"raw": "(без имени)", "name": None, "params": []}}
				self.introduction = [];
				self.algorithms = {}
			else:
				self.main_algorithm = algo_sections[0]
				try:
					self.main_algorithm["header_info"] = parse_algorithm_header(self.main_algorithm["header"])
				except ValueError as header_err:
					raise KumirExecutionError(f"Ошибка в заголовке основного алгоритма: {header_err}")
				logger.debug(f"Parsed main algorithm header: {self.main_algorithm['header_info']}")
				self.algorithms = {}
				for alg in algo_sections[1:]:
					try:
						info = parse_algorithm_header(alg["header"]);
						alg["header_info"] = info
						if info["name"]:
							if info["name"] in self.algorithms: logger.warning(f"Algorithm '{info['name']}' redefined.")
							self.algorithms[info["name"]] = alg;
							logger.debug(f"Parsed auxiliary algorithm '{info['name']}'.")
						else:
							logger.warning(
								f"Auxiliary algorithm without name found (header: '{info['raw']}'). Cannot be called.")
					except ValueError as header_err:
						logger.error(
							f"Error parsing aux algorithm header '{alg.get('header', '')}': {header_err}"); logger.warning(
							f"Skipping aux algorithm due to header error.")

			self.logger.info("Code parsing completed successfully.")
		except (SyntaxError, KumirExecutionError) as e:
			self.logger.error(f"Parsing failed: {e}", exc_info=True); raise e
		except Exception as e:
			self.logger.error(f"Unexpected parsing error: {e}", exc_info=True); raise KumirExecutionError(
				f"Ошибка разбора программы: {e}")

	def interpret(self, progress_callback=None):
		"""Полный цикл: парсинг и выполнение кода Кумира."""
		self.trace = [];
		self.output = "";
		self.global_env = {};
		self.call_stack = []  # Сбрасываем все перед запуском
		self.progress_callback = progress_callback
		last_error_index = -1

		try:
			self.parse()  # Парсим код

			# Выполнение вступления (в глобальном окружении)
			if self.introduction:
				self.logger.info("Executing introduction (global scope)...")
				# Индексы для вступления (0-based)
				intro_indices = list(range(len(self.introduction)))
				execute_lines(self.introduction, self.global_env, self.robot, self, self.trace, self.progress_callback,
							  "introduction", intro_indices)
				self.logger.info("Introduction executed successfully.")
			else:
				self.logger.info("No introduction part to execute.")

			# Выполнение основного алгоритма (начинается в глобальном окружении)
			if self.main_algorithm and self.main_algorithm.get("body"):
				self.logger.info("Executing main algorithm (starting in global scope)...")
				main_body_indices = list(range(len(self.main_algorithm["body"])))
				# Передаем global_env как текущее окружение для старта
				execute_lines(self.main_algorithm["body"], self.global_env, self.robot, self, self.trace,
							  self.progress_callback, "main", main_body_indices)
				self.logger.info("Main algorithm executed successfully.")
			elif not self.main_algorithm:
				logger.warning("No main algorithm found after parsing.")
				if not self.introduction: raise KumirExecutionError("Программа не содержит исполняемого кода.")
			else:
				logger.info("Main algorithm body is empty.")

			# Проверяем, что стек вызовов пуст в конце (не должно быть незавершенных вызовов)
			if self.call_stack:
				logger.error(
					f"Execution finished but call stack is not empty: {self.call_stack}")  # Это может указывать на ошибку в логике возврата из процедур

			# Успешное завершение
			self.logger.info("Interpretation completed successfully.")
			final_state = self.get_state();
			final_state["output"] = self.output
			return {"trace": self.trace, "finalState": final_state, "success": True}

		except KumirInputRequiredError as e:
			logger.info(f"Execution paused, input required for '{e.var_name}'.")
			self.output += f"Ожидание ввода для '{e.var_name}'...\n"
			state_at_input = self.get_state();
			state_at_input["output"] = self.output
			error_line_index = e.line_index if hasattr(e, 'line_index') else -1
			last_error_index = error_line_index
			return {"trace": self.trace, "finalState": state_at_input, "success": False, "input_required": True,
					"var_name": e.var_name, "prompt": e.prompt, "target_type": e.target_type,
					"message": f"Требуется ввод для переменной '{e.var_name}'", "errorIndex": error_line_index}

		except (KumirExecutionError, KumirEvalError, RobotError, DeclarationError, AssignmentError,
				InputOutputError) as e:
			error_msg = f"Ошибка выполнения: {str(e)}"
			error_line_index = getattr(e, 'line_index', -1);
			last_error_index = error_line_index
			self.logger.error(error_msg, exc_info=False)
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after error: {state_err}"); state_on_error = {
					"env": self.get_current_env(), "robot": None, "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": self.trace, "finalState": state_on_error, "success": False, "message": error_msg,
					"errorIndex": error_line_index}
		except Exception as e:
			error_msg = f"Критическая внутренняя ошибка: {type(e).__name__} - {e}"
			self.logger.exception(error_msg)
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after critical error: {state_err}"); state_on_error = {
					"env": self.get_current_env(), "robot": None, "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": self.trace, "finalState": state_on_error, "success": False, "message": error_msg,
					"errorIndex": last_error_index}

# FILE END: interpreter.py
