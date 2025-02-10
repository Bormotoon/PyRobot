# robot_commands.py

def process_robot_command(line, robot):
    """
    Если строка соответствует одной из команд управления роботом, вызывает соответствующую функцию.
    Поддерживаются команды: влево, вправо, вверх, вниз, закрасить.
    """
    cmd = line.lower().strip()
    robot_commands = {
        "влево": robot.left,
        "вправо": robot.right,
        "вверх": robot.up,
        "вниз": robot.down,
        "закрасить": robot.paint
    }
    if cmd in robot_commands:
        try:
            robot_commands[cmd]()
        except Exception as e:
            print(f"Ошибка при выполнении команды '{line}': {e}")
        return True
    return False
