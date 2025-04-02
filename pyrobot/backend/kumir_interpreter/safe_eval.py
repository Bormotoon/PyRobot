# FILE START: safe_eval.py
import ast
import logging

from .ast_evaluator import SafeEvaluator, EvaluationError
from .kumir_expression_translator import kumir_expr_to_python_expr, TranslationError
# math больше не нужен здесь, если не используется вне SAFE_GLOBALS
# Убираем импорты функций, которые были ТОЛЬКО для SAFE_GLOBALS
# Оставляем импорты, нужные для этого модуля:
from .robot_state import SimulatedRobot, RobotError

# Импортируем SAFE_GLOBALS из нового модуля

logger = logging.getLogger('KumirSafeEval')


class KumirEvalError(Exception): pass


# Функция get_robot_sensors остается без изменений
def get_robot_sensors(robot):
	"""Создает словарь функций-сенсоров робота для окружения."""
	if not robot or not isinstance(robot, SimulatedRobot):
		logger.warning("get_robot_sensors: Robot object is invalid or missing.")
		return {}

	sensors = {}
	# Используем лямбды для замыкания 'robot'
	sensors["слева_свободно"] = lambda: robot.check_direction("left", "free")
	sensors["справа_свободно"] = lambda: robot.check_direction("right", "free")
	sensors["сверху_свободно"] = lambda: robot.check_direction("up", "free")
	sensors["снизу_свободно"] = lambda: robot.check_direction("down", "free")
	sensors["слева_стена"] = lambda: robot.check_direction("left", "wall")
	sensors["справа_стена"] = lambda: robot.check_direction("right", "wall")
	sensors["сверху_стена"] = lambda: robot.check_direction("up", "wall")
	sensors["снизу_стена"] = lambda: robot.check_direction("down", "wall")
	sensors["клетка_закрашена"] = lambda: robot.check_cell("painted")
	sensors["клетка_чистая"] = lambda: robot.check_cell("clear")
	sensors["радиация"] = lambda: robot.do_measurement("radiation")
	sensors["температура"] = lambda: robot.do_measurement("temperature")

	logger.debug(f"Generated robot sensors: {list(sensors.keys())}")
	return sensors


# Функция get_env_vars остается без изменений
def get_env_vars(env):
	"""Извлекает только значения переменных из полного окружения Кумира."""
	vars_only = {}
	if env:
		for var, info in env.items():
			if isinstance(info, dict) and 'value' in info:
				vars_only[var] = info.get("value")
			else:
				# Логируем предупреждение, если структура env неожиданная
				logger.warning(f"Unexpected structure in env for var '{var}'. Setting value to None.")
				vars_only[var] = None
	logger.debug(f"Extracted env vars: {list(vars_only.keys())}")
	return vars_only


# Функция safe_eval остается почти без изменений,
# т.к. SafeEvaluator теперь сам получает SAFE_GLOBALS при инициализации.
def safe_eval(kumir_expr, env, robot=None):
	"""
	Безопасно вычисляет выражение Кумира, используя трансляцию в Python AST
	и его последующий обход в контролируемом окружении.
	"""
	logger.info(f"Evaluating Kumir expression: '{kumir_expr}'")

	try:
		# 1. Транслируем выражение Кумира в Python
		python_expr = kumir_expr_to_python_expr(kumir_expr)
		logger.debug(f"Translated to Python: '{python_expr}'")

		# 2. Парсим Python выражение в AST
		try:
			ast_node = ast.parse(python_expr, mode='eval')
		# Закомментируем дамп AST, может быть слишком многословно
		# logger.debug(f"Parsed AST: {ast.dump(ast_node)}")
		except SyntaxError as e:
			logger.error(
				f"Python Syntax Error after translation: {e}. Original: '{kumir_expr}', Translated: '{python_expr}'")
			raise KumirEvalError(f"Синтаксическая ошибка в выражении '{kumir_expr}': {e}")

		# 3. Подготавливаем окружение для вычислителя
		env_vars = get_env_vars(env)
		robot_sensors = get_robot_sensors(robot)

		# 4. Создаем и запускаем безопасный вычислитель AST
		# SafeEvaluator сам импортирует SAFE_GLOBALS из kumir_globals
		evaluator = SafeEvaluator(env_vars=env_vars, robot_sensors=robot_sensors)
		result = evaluator.visit(ast_node)
		logger.info(f"Evaluation result for '{kumir_expr}': {result}")
		return result

	except (TranslationError, EvaluationError, RobotError) as e:
		logger.error(f"Evaluation failed for '{kumir_expr}': {e}")
		raise KumirEvalError(str(e))
	except Exception as e:
		logger.exception(f"Unexpected error during evaluation of '{kumir_expr}': {e}")
		raise KumirEvalError(f"Неожиданная ошибка вычисления выражения '{kumir_expr}': {e}")

# FILE END: safe_eval.py
