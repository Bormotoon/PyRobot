# FILE START: safe_eval.py
import ast
import logging

from .ast_evaluator import SafeEvaluator, EvaluationError
from .kumir_expression_translator import kumir_expr_to_python_expr, TranslationError
from .robot_state import SimulatedRobot, RobotError

logger = logging.getLogger('KumirSafeEval')


class KumirEvalError(Exception): pass


def get_robot_sensors(robot):
	"""Создает словарь функций-сенсоров робота для окружения."""
	if not robot or not isinstance(robot, SimulatedRobot): logger.warning(
		"get_robot_sensors: Robot object is invalid or missing."); return {}
	sensors = {}
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


def get_env_vars(env):
	"""Извлекает только значения переменных из полного окружения Кумира."""
	vars_only = {}
	if env:
		for var, info in env.items():
			if isinstance(info, dict) and 'value' in info:
				vars_only[var] = info.get("value")
			else:
				logger.warning(f"Unexpected structure in env for var '{var}'. Setting value to None."); vars_only[
					var] = None
	# logger.debug(f"Extracted env vars: {list(vars_only.keys())}") # Слишком многословно
	return vars_only


def safe_eval(kumir_expr, env, robot=None):
	"""Безопасно вычисляет выражение Кумира через AST."""
	logger.info(f"Evaluating Kumir expression: '{kumir_expr}'")
	try:
		python_expr = kumir_expr_to_python_expr(kumir_expr);
		logger.debug(f"Translated to Python: '{python_expr}'")
		try:
			ast_node = ast.parse(python_expr, mode='eval')
		except SyntaxError as e:
			logger.error(
				f"Python Syntax Error: {e}. Original: '{kumir_expr}', Translated: '{python_expr}'"); raise KumirEvalError(
				f"Синтаксическая ошибка: {e}")
		env_vars = get_env_vars(env);
		robot_sensors = get_robot_sensors(robot)
		evaluator = SafeEvaluator(env_vars=env_vars, robot_sensors=robot_sensors)
		result = evaluator.visit(ast_node)
		logger.info(f"Evaluation result for '{kumir_expr}': {result}")
		return result
	except (TranslationError, EvaluationError, RobotError) as e:
		logger.error(f"Evaluation failed for '{kumir_expr}': {e}"); raise KumirEvalError(str(e))
	except Exception as e:
		logger.exception(f"Unexpected error evaluating '{kumir_expr}': {e}"); raise KumirEvalError(
			f"Неожиданная ошибка вычисления: {e}")

# FILE END: safe_eval.py
