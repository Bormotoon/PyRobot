# FILE START: interpreter.py
import logging
import copy

# Импортируем все исключения из одного места
from .kumir_exceptions import (KumirExecutionError, DeclarationError, AssignmentError,
                               InputOutputError, KumirInputRequiredError, KumirEvalError,
                               RobotError)
# Импортируем остальные зависимости
from .declarations import (get_default_value, _validate_and_convert_value,
                           process_declaration, process_assignment, process_output,
                           process_input)  # Больше не импортируем исключения отсюда
from .execution import execute_lines  # Больше не импортируем KumirExecutionError отсюда
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_state import SimulatedRobot  # Больше не импортируем RobotError отсюда

# Убрали импорт KumirEvalError из safe_eval

MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT
logger = logging.getLogger('KumirInterpreter')


class KumirLanguageInterpreter:
	"""Интерпретатор языка КУМИР с поддержкой вызова алгоритмов и ссылок."""

	# ... (Код __init__ и методов работы со стеком/ссылками остается тем же, что и в предыдущем ответе) ...
	def __init__(self, code, initial_field_state=None):
		"""Инициализирует интерпретатор."""
		self.code = code;
		self.global_env = {};
		self.algorithms = {};
		self.main_algorithm = None
		self.introduction = [];
		self.output = "";
		self.logger = logger;
		self.trace = []
		self.progress_callback = None;
		self.call_stack = []
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
		                            initial_walls=set(current_state.get('walls', [])),
		                            initial_markers=dict(current_state.get('markers', {})),
		                            initial_colored_cells=set(current_state.get('coloredCells', [])),
		                            initial_symbols=dict(current_state.get('symbols', {})),
		                            initial_radiation=dict(current_state.get('radiation', {})),
		                            initial_temperature=dict(current_state.get('temperature', {})))
		self.logger.info(
			f"Interpreter initialized. Field: {self.width}x{self.height}. Robot at: {self.robot.robot_pos}")

	def get_current_env_index(self):
		return len(self.call_stack) - 1

	def get_env_by_index(self, index):
		if index == -1:
			return self.global_env
		elif 0 <= index < len(self.call_stack):
			frame = self.call_stack[index];
			if 'env' in frame:
				return frame['env']
			else:
				self.logger.error(
					f"Internal error: 'env' key missing in call stack frame at index {index}"); raise KumirExecutionError(
					f"Внутренняя ошибка: отсутствует окружение в стеке вызовов ({index})")
		else:
			self.logger.error(f"Attempt to access invalid env index: {index}"); raise KumirExecutionError(
				f"Внутренняя ошибка: неверный индекс окружения {index}")

	def _resolve_reference(self, ref_info):
		if not isinstance(ref_info, dict) or ref_info.get('kind') != 'ref': self.logger.error(
			f"Invalid input to _resolve_reference: {ref_info}"); raise KumirExecutionError(
			"Внутренняя ошибка: неверные данные для разрешения ссылки.")
		visited_refs = set();
		current_info = ref_info;
		current_indices = ref_info.get('ref_indices')
		target_var_name = None  # Инициализируем
		target_env_index = None  # Инициализируем
		target_env = None  # Инициализируем
		while isinstance(current_info, dict) and current_info.get('kind') == 'ref':
			target_var_name = current_info.get('target_var_name');
			target_env_index = current_info.get('target_env_index')
			if target_var_name is None or target_env_index is None: raise KumirExecutionError(
				f"Внутренняя ошибка: некорректная структура ссылки для '{ref_info.get('target_var_name', '?')}'")
			ref_id = (target_env_index, target_var_name, current_indices)
			if ref_id in visited_refs: raise KumirExecutionError(
				f"Обнаружена циклическая ссылка на переменную '{target_var_name}'"); visited_refs.add(ref_id)
			try:
				target_env = self.get_env_by_index(target_env_index)
			except KumirExecutionError:
				raise KumirExecutionError(f"Ошибка разрешения ссылки: не найден контекст для '{target_var_name}'")
			if target_var_name not in target_env: raise KumirExecutionError(
				f"Ошибка разрешения ссылки: переменная '{target_var_name}' не найдена")
			next_info = target_env[target_var_name];
			next_ref_indices = next_info.get('ref_indices') if isinstance(next_info, dict) else None
			if next_info.get('kind') == 'ref' and next_ref_indices is not None: raise KumirExecutionError(
				f"Внутренняя ошибка: некорректная цепочка ссылок с индексами."); current_info = next_info
		if not isinstance(current_info, dict) or current_info.get('kind') != 'value': raise KumirExecutionError(
			f"Внутренняя ошибка: ссылка указывает на некорректный объект.")
		# target_env и target_var_name остались от последней итерации
		return target_env, target_var_name, current_indices

	def get_variable_info(self, var_name, env_index=None):
		if env_index is None: env_index = self.get_current_env_index()
		if env_index != -1:
			try:
				current_env = self.get_env_by_index(env_index);
				if var_name in current_env: return current_env[var_name]
			except KumirExecutionError:
				pass
		if var_name in self.global_env: return self.global_env[var_name]
		return None

	def resolve_variable_value(self, var_name, indices=None, env_index=None):
		if env_index is None: env_index = self.get_current_env_index()
		var_info = self.get_variable_info(var_name, env_index)
		if var_info is None: raise KumirExecutionError(f"Переменная '{var_name}' не найдена.")
		if not isinstance(var_info, dict): raise KumirExecutionError(
			f"Внутренняя ошибка: некорректная структура для переменной '{var_name}'.")
		if var_info.get('kind') == 'ref':
			try:
				target_env, target_var_name, ref_indices = self._resolve_reference(var_info)
				var_info_to_use = target_env.get(target_var_name)
				if var_info_to_use is None or var_info_to_use.get('kind') != 'value': raise KumirExecutionError(
					f"Внутренняя ошибка: целевая переменная '{target_var_name}' не найдена или некорректна после разрешения ссылки.")
				final_indices = indices if indices is not None else ref_indices
			except KumirExecutionError as e:
				raise e
		else:
			if indices is not None and var_info.get('kind') == 'ref': raise KumirExecutionError(
				"Внутренняя ошибка: некорректный доступ к элементу ссылки.")
			final_indices = indices;
			var_info_to_use = var_info
		final_var_info = var_info_to_use
		if final_indices is not None:
			if not final_var_info.get('is_table'): raise AssignmentError(
				f"Попытка доступа по индексу к не табличной переменной '{var_name}'.")
			dims = final_var_info.get('dimensions')
			if not dims or len(dims) != len(final_indices): raise AssignmentError(
				f"Неверное количество индексов ({len(final_indices)}) для таблицы '{var_name}', ожидалось {len(dims) if dims else '?'}.")
			for d_idx, idx_val in enumerate(final_indices):
				start, end = dims[d_idx];
				if not (start <= idx_val <= end): raise AssignmentError(
					f"Индекс #{d_idx + 1} ({idx_val}) вне диапазона [{start}:{end}] для '{var_name}'.")
			table_value_dict = final_var_info.get('value')
			if not isinstance(table_value_dict, dict): raise KumirExecutionError(
				f"Таблица '{var_name}' не инициализирована или повреждена.")
			element_value = table_value_dict.get(final_indices)
			if element_value is None: return get_default_value(final_var_info['type'])
			return element_value
		else:
			if final_var_info.get('is_table'):
				table_val = final_var_info.get('value'); return table_val if isinstance(table_val, dict) else {}
			else:
				scalar_val = final_var_info.get('value'); return get_default_value(
					final_var_info['type']) if scalar_val is None and final_var_info.get('type') else scalar_val

	def update_variable_value(self, var_name, value, indices=None, env_index=None):
		if env_index is None: env_index = self.get_current_env_index()
		var_info = self.get_variable_info(var_name, env_index)
		if var_info is None: raise KumirExecutionError(f"Переменная '{var_name}' не найдена для присваивания.")
		if not isinstance(var_info, dict): raise KumirExecutionError(
			f"Внутренняя ошибка: некорректная структура для переменной '{var_name}'.")
		if var_info.get('kind') == 'ref':
			try:
				target_env, target_var_name, ref_indices = self._resolve_reference(var_info)
				var_info_to_update = target_env.get(target_var_name)
				if var_info_to_update is None or var_info_to_update.get('kind') != 'value': raise KumirExecutionError(
					f"Внутренняя ошибка: целевая переменная '{target_var_name}' не найдена или некорректна после разрешения ссылки.")
				final_indices = indices if indices is not None else ref_indices;
				effective_var_name_for_error = target_var_name
			except KumirExecutionError as e:
				raise e
		else:
			if indices is not None and var_info.get('kind') == 'ref': raise KumirExecutionError(
				"Внутренняя ошибка: некорректное обновление элемента ссылки.")
			final_indices = indices;
			var_info_to_update = var_info;
			effective_var_name_for_error = var_name
		target_type = var_info_to_update['type'];
		is_table = var_info_to_update.get('is_table', False)
		try:
			if final_indices is None and is_table:
				if not isinstance(value, dict): raise AssignmentError(
					f"Попытка присвоить не таблицу (не словарь) табличной переменной '{effective_var_name_for_error}'")
				converted_value = value
			elif final_indices is not None and is_table:
				converted_value = _validate_and_convert_value(value, target_type,
				                                              f"{effective_var_name_for_error}[...]")
			elif not is_table:
				converted_value = _validate_and_convert_value(value, target_type, effective_var_name_for_error)
			else:
				raise KumirExecutionError(
					f"Неожиданное состояние при обновлении переменной '{effective_var_name_for_error}'")
		except (AssignmentError, TypeError) as e:
			raise AssignmentError(f"Ошибка типа при присваивании переменной '{effective_var_name_for_error}': {e}")
		if final_indices is not None:
			if not is_table: raise AssignmentError(
				f"Попытка присваивания по индексу не табличной переменной '{effective_var_name_for_error}'.")
			dims = var_info_to_update.get('dimensions')
			if not dims or len(dims) != len(final_indices): raise AssignmentError(
				f"Неверное количество индексов ({len(final_indices)}) для таблицы '{effective_var_name_for_error}', ожидалось {len(dims) if dims else '?'}.")
			for d_idx, idx_val in enumerate(final_indices):
				start, end = dims[d_idx];
				if not (start <= idx_val <= end): raise AssignmentError(
					f"Индекс #{d_idx + 1} ({idx_val}) вне диапазона [{start}:{end}] для '{effective_var_name_for_error}'.")
			if not isinstance(var_info_to_update.get('value'), dict): var_info_to_update['value'] = {}; logger.debug(
				f"Initialized table '{effective_var_name_for_error}' before setting element.")
			var_info_to_update['value'][final_indices] = converted_value;
			logger.debug(
				f"Updated table element {effective_var_name_for_error}{list(final_indices)} = {converted_value}")
		else:
			if is_table:
				var_info_to_update['value'] = converted_value; logger.debug(
					f"Updated entire table '{effective_var_name_for_error}'")
			else:
				var_info_to_update['value'] = converted_value; logger.debug(
					f"Updated scalar variable '{effective_var_name_for_error}' = {converted_value}")

	def push_call_stack(self, algo_name, local_env):
		caller_env_index = self.get_current_env_index()
		self.call_stack.append({'name': algo_name, 'env': local_env, 'caller_env_index': caller_env_index})
		self.logger.debug(
			f"Pushed '{algo_name}' onto call stack. Depth: {len(self.call_stack)}. Caller index: {caller_env_index}")

	def pop_call_stack(self):
		if not self.call_stack: self.logger.error("Attempted to pop from an empty call stack."); return None
		popped = self.call_stack.pop();
		self.logger.debug(f"Popped '{popped.get('name')}' from call stack. Depth: {len(self.call_stack)}");
		return popped

	def _get_env_for_frontend(self, env):
		resolved_env = {}
		if env:
			env_index = -1;
			if env is not self.global_env:
				for idx, frame in enumerate(self.call_stack):
					if frame.get('env') is env: env_index = idx; break
				if env_index == -1 and env: logger.warning(
					"_get_env_for_frontend received an unknown env object. Resolving from current scope."); env_index = self.get_current_env_index()
			for name in env.keys():
				try:
					value = self.resolve_variable_value(name, env_index=env_index); resolved_env[name] = value
				except KumirExecutionError as e:
					logger.warning(f"Skipping variable '{name}' for frontend state due to resolution error: {e}");
					resolved_env[name] = f"<ошибка: {e}>"
				except Exception as e:
					logger.error(f"Unexpected error resolving var '{name}' for frontend state: {e}"); resolved_env[
						name] = "<внутренняя ошибка>"
		return resolved_env

	def get_state(self):
		current_local_env_struct = self.call_stack[-1]['env'].copy() if self.call_stack else {};
		global_env_struct = self.global_env.copy()
		frontend_local_env = self._get_env_for_frontend(current_local_env_struct);
		frontend_global_env = self._get_env_for_frontend(global_env_struct)
		state = {"env": frontend_local_env, "global_env": frontend_global_env, "call_stack_depth": len(self.call_stack),
		         "width": self.width, "height": self.height, "robot": self.robot.robot_pos.copy(),
		         "walls": list(self.robot.walls),
		         "permanentWalls": list(self.robot.permanent_walls), "markers": self.robot.markers.copy(),
		         "coloredCells": list(self.robot.colored_cells),
		         "symbols": self.robot.symbols.copy(), "radiation": self.robot.radiation.copy(),
		         "temperature": self.robot.temperature.copy(), "output": self.output}
		return state

	def _get_resolved_env_for_evaluator(self):
		vars_only = {};
		current_env_index = self.get_current_env_index();
		current_env = self.get_env_by_index(current_env_index)
		env_keys_to_resolve = set(current_env.keys());
		if current_env_index != -1: env_keys_to_resolve.update(self.global_env.keys())
		for var_name in env_keys_to_resolve:
			try:
				value = self.resolve_variable_value(var_name); vars_only[var_name] = value
			except KumirExecutionError as e:
				logger.warning(f"Could not resolve value for variable '{var_name}' for evaluator: {e}. Skipping.")
			except Exception as e:
				logger.error(f"Unexpected error resolving variable '{var_name}' for evaluator: {e}. Skipping.",
				             exc_info=True)
		logger.debug(f"Resolved env vars for evaluator: {vars_only.keys()}")
		return vars_only

	def parse(self):
		# ... (код parse без изменений) ...
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
				main_header = "алг main";
				self.main_algorithm = {"header": main_header, "body": self.introduction,
				                       "header_info": parse_algorithm_header(main_header)}
				self.introduction = [];
				self.algorithms = {}
			else:
				self.main_algorithm = algo_sections[0]
				try:
					self.main_algorithm["header_info"] = parse_algorithm_header(self.main_algorithm["header"])
					if not self.main_algorithm["header_info"].get("name"): self.main_algorithm["header_info"][
						"name"] = "__main__"; logger.debug("Assigning default name '__main__' to main algorithm.")
				except ValueError as header_err:
					raise KumirExecutionError(f"Ошибка в заголовке основного алгоритма: {header_err}")
				logger.debug(f"Parsed main algorithm header: {self.main_algorithm['header_info']}")
				self.algorithms = {}
				for alg_dict in algo_sections[1:]:
					try:
						header_info = parse_algorithm_header(alg_dict["header"]);
						alg_name = header_info.get("name")
						if alg_name:
							if alg_name in self.algorithms: logger.warning(f"Algorithm '{alg_name}' redefined.")
							self.algorithms[alg_name] = {"header_info": header_info, "body": alg_dict.get("body", [])}
							logger.debug(f"Parsed auxiliary algorithm '{alg_name}'.")
						else:
							logger.warning(
								f"Auxiliary algorithm without name found (header: '{header_info.get('raw', '')}'). Cannot be called.")
					except ValueError as header_err:
						logger.error(
							f"Error parsing aux algorithm header '{alg_dict.get('header', '')}': {header_err}"); logger.warning(
							f"Skipping aux algorithm due to header error.")
			self.logger.info("Code parsing completed successfully.")
		except (SyntaxError, KumirExecutionError) as e:
			self.logger.error(f"Parsing failed: {e}", exc_info=True); raise e
		except Exception as e:
			self.logger.error(f"Unexpected parsing error: {e}", exc_info=True); raise KumirExecutionError(
				f"Ошибка разбора программы: {e}")

	def interpret(self, progress_callback=None):
		"""Полный цикл: парсинг и выполнение кода Кумира."""
		# ... (код interpret без изменений, использует обновленные методы) ...
		self.trace = [];
		self.output = "";
		self.global_env = {};
		self.call_stack = []
		self.progress_callback = progress_callback;
		last_error_index = -1
		try:
			self.parse()
			if self.introduction:
				self.logger.info("Executing introduction (global scope)...")
				intro_indices = list(range(len(self.introduction)))
				execute_lines(self.introduction, self.global_env, self.robot, self, self.trace, self.progress_callback,
				              "introduction", intro_indices)
				self.logger.info("Introduction executed successfully.")
			else:
				self.logger.info("No introduction part to execute.")
			if self.main_algorithm and self.main_algorithm.get("body"):
				main_algo_name = self.main_algorithm.get("header_info", {}).get("name", "__main__")
				self.logger.info(f"Executing main algorithm '{main_algo_name}' (starting in global scope)...")
				main_body_indices = list(range(len(self.main_algorithm["body"])))
				execute_lines(self.main_algorithm["body"], self.global_env, self.robot, self, self.trace,
				              self.progress_callback, main_algo_name, main_body_indices)
				self.logger.info("Main algorithm executed successfully.")
			elif not self.main_algorithm:
				logger.warning("No main algorithm found after parsing.")
				if not self.introduction: raise KumirExecutionError("Программа не содержит исполняемого кода.")
			else:
				logger.info("Main algorithm body is empty.")
			if self.call_stack: logger.error(f"Execution finished but call stack is not empty: {self.call_stack}")
			self.logger.info("Interpretation completed successfully.")
			final_state = self.get_state();
			final_state["output"] = self.output
			return {"trace": self.trace, "finalState": final_state, "success": True}
		except KumirInputRequiredError as e:
			logger.info(f"Execution paused, input required for '{e.var_name}'.");
			self.output += f"Ожидание ввода для '{e.var_name}'...\n"
			state_at_input = self.get_state();
			state_at_input["output"] = self.output
			error_line_index = e.line_index if hasattr(e, 'line_index') else -1;
			last_error_index = error_line_index
			return {"trace": self.trace, "finalState": state_at_input, "success": False, "input_required": True,
			        "var_name": e.var_name, "prompt": e.prompt, "target_type": e.target_type,
			        "message": f"Требуется ввод для переменной '{e.var_name}'", "errorIndex": error_line_index}
		# Теперь обрабатываем все ожидаемые ошибки Кумира здесь
		except (
		KumirExecutionError, DeclarationError, AssignmentError, InputOutputError, KumirEvalError, RobotError) as e:
			error_msg = f"Ошибка выполнения: {str(e)}";
			error_line_index = getattr(e, 'line_index', -1);
			last_error_index = error_line_index
			self.logger.error(error_msg, exc_info=False);
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after error: {state_err}");
				current_env_struct = self.call_stack[-1]['env'] if self.call_stack else self.global_env
				state_on_error = {"env": self._get_env_for_frontend(current_env_struct.copy()),
				                  "global_env": self._get_env_for_frontend(self.global_env.copy()), "robot": None,
				                  "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": self.trace, "finalState": state_on_error, "success": False, "message": error_msg,
			        "errorIndex": error_line_index}
		except Exception as e:
			error_msg = f"Критическая внутренняя ошибка: {type(e).__name__} - {e}";
			self.logger.exception(error_msg);
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
				logger.error(f"Failed to get state after critical error: {state_err}");
				current_env_struct = self.call_stack[-1]['env'] if self.call_stack else self.global_env
				state_on_error = {"env": self._get_env_for_frontend(current_env_struct.copy()),
				                  "global_env": self._get_env_for_frontend(self.global_env.copy()), "robot": None,
				                  "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": self.trace, "finalState": state_on_error, "success": False, "message": error_msg,
			        "errorIndex": last_error_index}

# FILE END: interpreter.py