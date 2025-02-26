"""
robot_commands.py
Описание: Обрабатывает команды управления роботом.
"""


def process_robot_command(line, robot):
	cmd = line.strip().lower()
	robot_commands = {
		"влево": robot.go_left,
		"вправо": robot.go_right,
		"вверх": robot.go_up,
		"вниз": robot.go_down,
		"закрасить": robot.do_paint
	}
	if cmd in robot_commands:
		# Просто вызываем команду – если она вызывает ошибку, она пробросится дальше
		robot_commands[cmd]()
		return True
	return False
