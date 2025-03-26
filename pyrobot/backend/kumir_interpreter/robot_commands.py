"""
robot_commands.py
Описание: Обрабатывает и делегирует команды управления роботом.
"""
import logging

# Import RobotError if used
from .robot_state import RobotError, SimulatedRobot

logger = logging.getLogger('RobotCommands')

# Словарь для маппинга команд Кумира на методы объекта робота
ROBOT_ACTIONS = {
	"влево": "go_left",
	"вправо": "go_right",
	"вверх": "go_up",
	"вниз": "go_down",
	"закрасить": "do_paint"
	# Добавить другие команды по мере необходимости (н-р, маркеры)
	# "положить маркер": "put_marker",
	# "поднять маркер": "pick_marker",
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
			# Получаем метод робота по имени
			method_to_call = getattr(robot, method_name)
		except AttributeError:
			logger.error(f"Internal Error: Robot object lacks method '{method_name}' for command '{cmd}'")
			# This indicates a mismatch between ROBOT_ACTIONS and SimulatedRobot class
			raise AttributeError(f"У объекта робота нет метода '{method_name}'")

		logger.info(f"Executing robot command: {cmd} (calling method {method_name})")
		try:
			# Вызываем метод робота
			method_to_call()
			# Если метод не вызвал исключение, команда считается выполненной
			logger.debug(f"Robot command '{cmd}' executed successfully by robot object.")
			return True  # Команда распознана и выполнена (или попытка выполнения произведена)
		except RobotError as e:
			# Перехватываем специфические ошибки робота (стена, уже закрашено и т.д.)
			logger.warning(f"Robot command '{cmd}' failed: {e}")
			# Пробрасываем ошибку дальше, чтобы интерпретатор мог ее обработать
			raise e
		except Exception as e:
			# Перехватываем другие неожиданные ошибки из методов робота
			logger.error(f"Unexpected error during robot command '{cmd}': {e}", exc_info=True)
			raise  # Пробрасываем неожиданные ошибки
	else:
		# Строка не является известной командой робота
		logger.debug(f"'{cmd}' is not a known robot command.")
		return False
