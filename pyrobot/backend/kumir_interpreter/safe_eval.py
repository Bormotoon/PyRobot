# FILE START: safe_eval.py
import ast
import logging

# Импортируем исключения из нового файла
from .kumir_exceptions import KumirEvalError, KumirExecutionError, RobotError
from .ast_evaluator import SafeEvaluator, EvaluationError
from .kumir_expression_translator import kumir_expr_to_python_expr, TranslationError
from .robot_state import SimulatedRobot

# УДАЛЯЕМ импорт KumirExecutionError из execution
# from .execution import KumirExecutionError

logger = logging.getLogger('KumirSafeEval')


# Определение KumirEvalError УДАЛЕНО отсюда

def get_robot_sensors(robot):
    """Создает словарь функций-сенсоров робота для окружения."""
    if not robot or not isinstance(robot, SimulatedRobot):
        logger.warning("get_robot_sensors: Robot object is invalid or missing.")
        return {}
    sensors = {
        "слева_свободно": lambda: robot.check_direction("left", "free"),
        "справа_свободно": lambda: robot.check_direction("right", "free"),
        "сверху_свободно": lambda: robot.check_direction("up", "free"),
        "снизу_свободно": lambda: robot.check_direction("down", "free"),
        "слева_стена": lambda: robot.check_direction("left", "wall"),
        "справа_стена": lambda: robot.check_direction("right", "wall"),
        "сверху_стена": lambda: robot.check_direction("up", "wall"),
        "снизу_стена": lambda: robot.check_direction("down", "wall"),
        "клетка_закрашена": lambda: robot.check_cell("painted"),
        "клетка_чистая": lambda: robot.check_cell("clear"),
        "радиация": lambda: robot.do_measurement("radiation"),
        "температура": lambda: robot.do_measurement("temperature")
    }
    sensors["слевасвободно"] = sensors["слева_свободно"]
    sensors["справасвободно"] = sensors["справа_свободно"]
    sensors["сверхусвободно"] = sensors["сверху_свободно"]
    sensors["снизусвободно"] = sensors["снизу_свободно"]
    sensors["слевастена"] = sensors["слева_стена"]
    sensors["справастена"] = sensors["справа_стена"]
    sensors["сверхустена"] = sensors["сверху_стена"]
    sensors["снизустена"] = sensors["снизу_стена"]
    sensors["клетказакрашена"] = sensors["клетка_закрашена"]
    sensors["клеткачистая"] = sensors["клетка_чистая"]
    logger.debug(f"Generated robot sensors: {list(sensors.keys())}")
    return sensors


def safe_eval(kumir_expr, env, robot, interpreter):
    """
    Безопасно вычисляет выражение Кумира через AST.
    Использует interpreter для получения разрешенного окружения.
    """
    logger.info(f"Evaluating Kumir expression: '{kumir_expr}'")
    if interpreter is None:
        logger.error(f"safe_eval called without a valid interpreter instance for expression: '{kumir_expr}'")
        raise KumirEvalError("Внутренняя ошибка: отсутствует интерпретатор для вычисления выражения.")
    try:
        python_expr = kumir_expr_to_python_expr(kumir_expr)
        logger.debug(f"Translated to Python: '{python_expr}'")
        try:
            ast_node = ast.parse(python_expr, mode='eval')
        except SyntaxError as e:
            logger.error(
                f"Python Syntax Error after translation: {e}. "
                f"Original: '{kumir_expr}', Translated: '{python_expr}'"
            )
            raise KumirEvalError(
                f"Синтаксическая ошибка в выражении '{kumir_expr}' "
                f"(транслировано в '{python_expr}'): {e}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error parsing translated expression '{python_expr}'")
            raise KumirEvalError(f"Ошибка разбора выражения '{python_expr}': {e}")

        env_vars = interpreter._get_resolved_env_for_evaluator()
        logger.debug(f"Environment variables provided to evaluator: {env_vars}")
        robot_sensors = get_robot_sensors(robot)
        evaluator = SafeEvaluator(env_vars=env_vars, robot_sensors=robot_sensors)
        result = evaluator.visit(ast_node)
        logger.info(f"Evaluation result for '{kumir_expr}': {result}")
        return result    # Теперь KumirExecutionError импортируется из kumir_exceptions
    except (TranslationError, EvaluationError, RobotError, KumirExecutionError) as e:
        logger.error(f"Evaluation failed for '{kumir_expr}': {e}")
        raise KumirEvalError(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error evaluating '{kumir_expr}'")
        raise KumirEvalError(f"Неожиданная ошибка при вычислении выражения '{kumir_expr}': {e}")

# FILE END: safe_eval.py
