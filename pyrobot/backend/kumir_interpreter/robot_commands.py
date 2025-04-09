# FILE START: robot_commands.py
"""
robot_commands.py
Описание: Обрабатывает и делегирует команды управления роботом.
"""
import logging

# Import RobotError from the new exceptions file
from .kumir_exceptions import RobotError
# SimulatedRobot нужен для проверки типа и вызова методов
from .robot_state import SimulatedRobot

logger = logging.getLogger('RobotCommands')

# Словарь для маппинга команд Кумира на методы объекта робота
ROBOT_ACTIONS = {
	"влево": "go_left",
	"вправо": "go_right",
	"вверх": "go_up",
	"вниз": "go_down",
	"закрасить": "do_paint"
	# "положить маркер": "put_marker", # Пример, если будет добавлено
	# "поднять маркер": "pick_marker", # Пример, если будет добавлено
}


def process_robot_command(line, robot):
	"""
	Пытается распознать и выполнить команду робота.

	Args:
		line (str): Строка кода, потенциально содержащая команду робота.
		robot (SimulatedRobot): Экземпляр симулированного робота.

	Returns:
		bool: True, если строка была распознана и (попытка) выполнения команды робота произведена, иначе False.

	Raises:
		RobotError: Если робот сообщает об ошибке (например, уперся в стену).
		AttributeError: Если команда найдена в словаре, но у робота нет такого метода.
	"""
	cmd = line.strip().lower()
	logger.debug(f"Attempting to process as robot command: '{cmd}'")

	if cmd in ROBOT_ACTIONS:
		method_name = ROBOT_ACTIONS[cmd]
		try:
			method_to_call = getattr(robot, method_name)
		except AttributeError:
			logger.error(f"Internal Error: Robot object lacks method '{method_name}' for command '{cmd}'")
			raise AttributeError(f"У объекта робота нет метода '{method_name}'")

		logger.info(f"Executing robot command: {cmd} (calling method {method_name})")
		try:
			method_to_call()  # Вызываем метод робота
			logger.debug(f"Robot command '{cmd}' executed successfully by robot object.")
			return True
		except RobotError as e:
			# Перехватываем и пробрасываем ошибки робота
			logger.warning(f"Robot command '{cmd}' failed: {e}")
			raise e  # Пробрасываем выше для обработки интерпретатором
		except Exception as e:
			# Перехватываем другие неожиданные ошибки
			logger.error(f"Unexpected error during robot command '{cmd}': {e}", exc_info=True)
			raise  # Пробрасываем выше

	else:
		logger.debug(f"'{cmd}' is not a known robot command.")
		return False

# FILE END: robot_commands.py