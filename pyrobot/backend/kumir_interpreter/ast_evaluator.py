# FILE START: ast_evaluator.py
import ast
import logging
import operator

# Импортируем SAFE_GLOBALS из нового модуля
from .kumir_globals import SAFE_GLOBALS
from .robot_state import RobotError

logger = logging.getLogger('KumirAstEvaluator')


class EvaluationError(Exception):
	"""Ошибка во время вычисления AST."""
	pass


class SafeEvaluator(ast.NodeVisitor):
	"""
	Безопасный вычислитель AST для выражений Кумира.
	"""

	def __init__(self, env_vars, robot_sensors):
		"""
		Инициализация вычислителя.
		"""
		self.env = env_vars
		# Объединяем глобально разрешенные функции/константы с сенсорами робота
		self.allowed_callables = {**SAFE_GLOBALS, **robot_sensors}
		logger.debug(
			f"Evaluator initialized. Env keys: {list(env_vars.keys())}, Callables: {list(self.allowed_callables.keys())}")

	# Методы visit_... остаются без изменений, как в предыдущем ответе
	def visit(self, node):
		# ... (код без изменений) ...
		method_name = 'visit_' + node.__class__.__name__
		visitor = getattr(self, method_name, self.generic_visit)
		logger.debug(f"Visiting node: {node.__class__.__name__}, Method: {visitor.__name__}")
		try:
			return visitor(node)
		except EvaluationError:  # Пробрасываем ошибки EvaluationError
			raise
		except RobotError as e:  # Пробрасываем ошибки робота
			logger.warning(f"Robot error during evaluation: {e}")
			raise EvaluationError(f"Ошибка робота: {e}")  # Оборачиваем в EvaluationError
		except Exception as e:
			logger.error(f"Unexpected error visiting {node.__class__.__name__}: {e}", exc_info=True)
			raise EvaluationError(f"Неожиданная ошибка вычисления узла {node.__class__.__name__}: {e}")

	def generic_visit(self, node):
		# ... (код без изменений) ...
		logger.error(f"Unsupported AST node type encountered: {node.__class__.__name__}")
		raise EvaluationError(f"Неподдерживаемый тип узла AST: {node.__class__.__name__}")

	def visit_Expression(self, node):
		# ... (код без изменений) ...
		return self.visit(node.body)

	def visit_Constant(self, node):
		# ... (код без изменений) ...
		logger.debug(f"Visiting Constant: {node.value}")
		return node.value

	def visit_Name(self, node):
		# ... (код без изменений) ...
		name = node.id
		logger.debug(f"Visiting Name: {name}")
		# 1. Ищем в переменных окружения
		if name in self.env:
			logger.debug(f"Found '{name}' in env: {self.env[name]}")
			return self.env[name]
		# 2. Ищем в разрешенных глобальных функциях/константах/сенсорах
		if name in self.allowed_callables:
			logger.debug(f"Found '{name}' in allowed callables.")
			return self.allowed_callables[name]

		logger.error(f"Name '{name}' not found in env or allowed callables.")
		raise EvaluationError(f"Неизвестное имя: '{name}'")

	def visit_BinOp(self, node):
		# ... (код без изменений) ...
		logger.debug(f"Visiting BinOp: {type(node.op)}")
		left_val = self.visit(node.left)
		right_val = self.visit(node.right)
		logger.debug(f"BinOp operands: left={left_val} ({type(left_val)}), right={right_val} ({type(right_val)})")

		op_map = {
			ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
			ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
			ast.Pow: operator.pow,
		}
		op_func = op_map.get(type(node.op))

		if op_func:
			try:
				result = op_func(left_val, right_val)
				logger.debug(f"BinOp result: {result}")
				return result
			except ZeroDivisionError:
				logger.error("Division by zero detected.")
				raise EvaluationError("Деление на ноль")
			except TypeError as e:
				logger.error(f"TypeError in BinOp: {e}")
				raise EvaluationError(f"Ошибка типа в операции {type(node.op).__name__}: {e}")
			except Exception as e:
				logger.error(f"Error in BinOp {type(node.op).__name__}: {e}", exc_info=True)
				raise EvaluationError(f"Ошибка в бинарной операции {type(node.op).__name__}: {e}")
		else:
			logger.error(f"Unsupported binary operator: {type(node.op)}")
			raise EvaluationError(f"Неподдерживаемый бинарный оператор: {type(node.op).__name__}")

	def visit_BoolOp(self, node):
		# ... (код без изменений) ...
		logger.debug(f"Visiting BoolOp: {type(node.op)}")
		results = []
		op_is_and = isinstance(node.op, ast.And)

		for value_node in node.values:
			val = self.visit(value_node)
			if op_is_and and not val:
				logger.debug("BoolOp (and) short-circuited to False")
				return False
			if not op_is_and and val:
				logger.debug("BoolOp (or) short-circuited to True")
				return True
			results.append(val)

		final_result = results[-1]
		logger.debug(f"BoolOp final result: {final_result}")
		return final_result

	def visit_UnaryOp(self, node):
		# ... (код без изменений) ...
		logger.debug(f"Visiting UnaryOp: {type(node.op)}")
		operand_val = self.visit(node.operand)
		logger.debug(f"UnaryOp operand: {operand_val} ({type(operand_val)})")

		if isinstance(node.op, ast.Not):
			result = not operand_val
			logger.debug(f"UnaryOp (Not) result: {result}")
			return result
		elif isinstance(node.op, ast.USub):
			try:
				result = -operand_val
				logger.debug(f"UnaryOp (USub) result: {result}")
				return result
			except TypeError as e:
				logger.error(f"TypeError in UnaryOp (USub): {e}")
				raise EvaluationError(f"Ошибка типа в унарном минусе: {e}")
		else:
			logger.error(f"Unsupported unary operator: {type(node.op)}")
			raise EvaluationError(f"Неподдерживаемый унарный оператор: {type(node.op).__name__}")

	def visit_Compare(self, node):
		# ... (код без изменений) ...
		logger.debug(f"Visiting Compare: ops={node.ops}")
		left_val = self.visit(node.left)
		results = []

		current_left = left_val
		for i, op in enumerate(node.ops):
			comparator_node = node.comparators[i]
			current_right = self.visit(comparator_node)
			logger.debug(f"Compare step {i}: left={current_left}, op={type(op).__name__}, right={current_right}")

			op_map = {
				ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
				ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
			}
			op_func = op_map.get(type(op))

			if op_func:
				try:
					result = op_func(current_left, current_right)
					results.append(result)
					current_left = current_right
				except TypeError as e:
					logger.error(f"TypeError in Compare: {e}")
					raise EvaluationError(f"Ошибка типа в сравнении {type(op).__name__}: {e}")
				except Exception as e:
					logger.error(f"Error in Compare {type(op).__name__}: {e}", exc_info=True)
					raise EvaluationError(f"Ошибка в сравнении {type(op).__name__}: {e}")
			else:
				logger.error(f"Unsupported comparison operator: {type(op)}")
				raise EvaluationError(f"Неподдерживаемый оператор сравнения: {type(op).__name__}")

		final_result = all(results)
		logger.debug(f"Compare final result: {final_result}")
		return final_result

	def visit_Call(self, node):
		# ... (код без изменений) ...
		logger.debug(f"Visiting Call: func={getattr(node.func, 'id', node.func)}")
		func_obj = self.visit(node.func)

		if not callable(func_obj):
			logger.error(f"Attempted to call non-callable object: {func_obj}")
			raise EvaluationError(f"Попытка вызова не функции: {getattr(node.func, 'id', '<неизвестно>')}")

		func_name = getattr(node.func, 'id', None)
		is_allowed = False
		if func_name:
			is_allowed = func_name in self.allowed_callables
		else:
			# Проверяем сам объект
			for allowed_name, allowed_val in self.allowed_callables.items():
				if func_obj is allowed_val:
					is_allowed = True
					func_name = allowed_name  # Нашли имя для логгирования
					break

		if not is_allowed:
			logger.error(f"Attempted to call disallowed function/object: {func_name or func_obj}")
			raise EvaluationError(f"Вызов функции '{func_name or '<неизвестный объект>'}' не разрешен.")

		args = [self.visit(arg) for arg in node.args]
		kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords if kw.arg is not None}

		logger.debug(f"Calling function '{func_name or '<lambda/other>'}' with args: {args}, kwargs: {kwargs}")

		try:
			result = func_obj(*args, **kwargs)
			logger.debug(f"Call result: {result}")
			return result
		except RobotError as e:
			logger.warning(f"Robot error during function call '{func_name}': {e}")
			raise  # Пробрасываем ошибку робота
		except TypeError as e:
			logger.error(f"TypeError during function call '{func_name}': {e}")
			raise EvaluationError(f"Ошибка типа при вызове функции '{func_name}': {e}")
		except Exception as e:
			logger.error(f"Error during function call '{func_name}': {e}", exc_info=True)
			raise EvaluationError(f"Ошибка при вызове функции '{func_name}': {e}")

	# --- Запрещенные или опасные узлы ---
	def visit_Attribute(self, node):
		# ... (код без изменений) ...
		logger.error(f"Disallowed AST node: Attribute access (e.g., obj.attr)")
		raise EvaluationError("Доступ к атрибутам объектов запрещен.")

	def visit_Subscript(self, node):
		# ... (код без изменений) ...
		logger.debug(f"Visiting Subscript")
		value = self.visit(node.value)
		slice_val = self.visit(node.slice)
		index = slice_val

		logger.debug(f"Subscript: value={value}, index={index}")

		if isinstance(value, dict):
			try:
				result = value[index]
				logger.debug(f"Subscript result (dict access): {result}")
				return result
			except KeyError:
				logger.error(f"KeyError accessing dict with index {index}")
				raise EvaluationError(f"Ошибка доступа к таблице: элемент с индексом {index} не найден.")
			except TypeError as e:
				logger.error(f"TypeError during dict access with index {index}: {e}")
				raise EvaluationError(f"Ошибка типа при доступе к таблице: {e}")
		else:
			logger.error(f"Disallowed subscript access on type {type(value)}")
			raise EvaluationError(
				f"Доступ по индексу разрешен только для таблиц (словарей), не для {type(value).__name__}.")

	def visit_Lambda(self, node):  # ... и остальные запреты без изменений ...
		logger.error("Disallowed AST node: Lambda")
		raise EvaluationError("Создание lambda-функций запрещено.")

	def visit_ListComp(self, node):
		logger.error("Disallowed AST node: List Comprehension")
		raise EvaluationError("Генераторы списков запрещены.")

	def visit_DictComp(self, node):
		logger.error("Disallowed AST node: Dict Comprehension")
		raise EvaluationError("Генераторы словарей запрещены.")

	def visit_SetComp(self, node):
		logger.error("Disallowed AST node: Set Comprehension")
		raise EvaluationError("Генераторы множеств запрещены.")

	def visit_GeneratorExp(self, node):
		logger.error("Disallowed AST node: Generator Expression")
		raise EvaluationError("Выражения-генераторы запрещены.")

	def visit_Yield(self, node):
		logger.error("Disallowed AST node: Yield")
		raise EvaluationError("Использование yield запрещено.")

	def visit_YieldFrom(self, node):
		logger.error("Disallowed AST node: Yield From")
		raise EvaluationError("Использование yield from запрещено.")

	def visit_Await(self, node):
		logger.error("Disallowed AST node: Await")
		raise EvaluationError("Использование await запрещено.")

	def visit_AsyncFunctionDef(self, node):
		logger.error("Disallowed AST node: Async Function Definition")
		raise EvaluationError("Определение async-функций запрещено.")

	def visit_Import(self, node):
		logger.error("Disallowed AST node: Import")
		raise EvaluationError("Импорт модулей запрещен.")

	def visit_ImportFrom(self, node):
		logger.error("Disallowed AST node: Import From")
		raise EvaluationError("Импорт из модулей запрещен.")

# Можно добавить запрет на другие узлы по мере необходимости

# FILE END: ast_evaluator.py
