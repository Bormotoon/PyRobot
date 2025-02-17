"""
robot_commands.py
Описание: Обрабатывает команды управления роботом.
"""


def process_robot_command(line, robot):
    """
    Обрабатывает строку команды управления роботом.

    Если строка соответствует одной из поддерживаемых команд (влево, вправо, вверх, вниз, закрасить),
    вызывается соответствующая функция объекта робота.

    Параметры:
      line (str): Строка команды, введенная пользователем.
      robot (object): Объект робота, который должен иметь методы:
                      go_left, go_right, go_up, go_down, do_paint.

    Возвращаемое значение:
      bool: True, если команда распознана и выполнена, иначе False.
    """
    # Приведение строки команды к нижнему регистру и удаление лишних пробелов
    cmd = line.lower().strip()

    # Словарь команд и соответствующих методов объекта робота
    robot_commands = {"влево": robot.go_left, "вправо": robot.go_right, "вверх": robot.go_up, "вниз": robot.go_down,
        "закрасить": robot.do_paint}

    if cmd in robot_commands:
        try:
            robot_commands[cmd]()  # Выполнение команды
        except Exception as e:
            print(f"Ошибка при выполнении команды '{line}': {e}")
        return True
    return False
