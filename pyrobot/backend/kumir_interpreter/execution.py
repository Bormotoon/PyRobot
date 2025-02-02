# execution.py

from declarations import process_declaration, process_assignment, process_output
from robot_commands import process_robot_command
from constants import ALLOWED_TYPES


def execute_line(line, env, robot):
    """
    Исполняет одну строку кода.
    Поддерживает:
      - Объявления величин (начинаются с одного из типов: цел, вещ, лог, сим, лит)
      - Присваивания (оператор ":=")
      - Команду вывода (начинается со слова "вывод")
      - Команды управления роботом (влево, вправо, вверх, вниз, закрасить)
    Если строка не распознана – выводит сообщение.
    """
    lower_line = line.lower()
    for t in ALLOWED_TYPES:
        if lower_line.startswith(t):
            try:
                process_declaration(line, env)
            except Exception as e:
                print(f"Ошибка объявления: {e}")
            return

    if ":=" in line:
        try:
            process_assignment(line, env)
        except Exception as e:
            print(f"Ошибка присваивания: {e}")
        return

    if lower_line.startswith("вывод"):
        try:
            process_output(line, env)
        except Exception as e:
            print(f"Ошибка команды 'вывод': {e}")
        return

    if process_robot_command(line, robot):
        return

    print(f"Неизвестная команда: {line}")
