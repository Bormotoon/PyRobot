# execution.py

from declarations import process_declaration, process_assignment, process_output
from robot_commands import process_robot_command
from safe_eval import safe_eval, get_eval_env
from constants import ALLOWED_TYPES


def process_control_command(line, env):
    """
    Обрабатывает команды контроля выполнения: утв, дано, надо.
    Вычисляет логическое выражение, и если оно ложно, прерывает выполнение алгоритма.
    """
    lower_line = line.lower().strip()
    for keyword in ["утв", "дано", "надо"]:
        if lower_line.startswith(keyword):
            expr = line[len(keyword):].strip()
            eval_env = get_eval_env(env)
            try:
                result = safe_eval(expr, eval_env)
            except Exception as e:
                raise Exception(f"Ошибка вычисления логического выражения '{expr}': {e}")
            if isinstance(result, bool):
                condition = result
            elif isinstance(result, str):
                condition = (result.lower() == "да")
            else:
                condition = bool(result)
            if not condition:
                raise Exception(f"Отказ: условие '{expr}' не выполнено (результат: {result}).")
            return True
    return False


def process_input(line, env):
    """
    Обрабатывает команду ввода.
    Формат: ввод выражение1, выражение2, ... , выражениеN
    Для простоты реализовано интерактивное чтение.
    """
    content = line[4:].strip()
    targets = [t.strip() for t in content.split(",") if t.strip()]
    input_str = input("Введите значения для команды 'ввод' (разделенные пробелом): ")
    values = input_str.split()
    if len(values) < len(targets):
        print("Предупреждение: введено меньше значений, чем требуется.")
    for i, target in enumerate(targets):
        if target.lower() == "нс":
            continue
        # Если target — простая переменная
        if target in env:
            var_type = env[target]["type"]
            try:
                if var_type == "цел":
                    val = int(values[i])
                elif var_type == "вещ":
                    val = float(values[i])
                elif var_type == "лог":
                    s = values[i].lower()
                    if s == "да":
                        val = True
                    elif s == "нет":
                        val = False
                    else:
                        val = bool(values[i])
                elif var_type in {"сим", "лит"}:
                    val = str(values[i])
                    if var_type == "сим" and len(val) != 1:
                        raise Exception("Символьная величина должна быть ровно один символ.")
                else:
                    raise Exception(f"Неподдерживаемый тип: {var_type}")
            except Exception as e:
                print(f"Ошибка преобразования значения для '{target}': {e}")
                continue
            env[target]["value"] = val
        else:
            # Поддержка ввода для элемента таблицы: a[i] или b[i,j]
            if "[" in target and target.endswith("]"):
                import re
                match = re.match(
                    r"^([A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*(?:\s+[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*)*)\[(.+)\]$",
                    target)
                if not match:
                    print(f"Неверный синтаксис для ввода: {target}")
                    continue
                var_name = match.group(1).strip()
                indices_expr = match.group(2).strip()
                index_tokens = [token.strip() for token in indices_expr.split(",")]
                try:
                    indices = tuple(safe_eval(token, get_eval_env(env)) for token in index_tokens)
                except Exception as e:
                    print(f"Ошибка вычисления индексов для '{target}': {e}")
                    continue
                if var_name not in env or not env[var_name].get("is_table"):
                    print(f"Переменная '{var_name}' не объявлена как таблица.")
                    continue
                var_type = env[var_name]["type"]
                try:
                    if var_type == "цел":
                        val = int(values[i])
                    elif var_type == "вещ":
                        val = float(values[i])
                    elif var_type == "лог":
                        s = values[i].lower()
                        if s == "да":
                            val = True
                        elif s == "нет":
                            val = False
                        else:
                            val = bool(values[i])
                    elif var_type in {"сим", "лит"}:
                        val = str(values[i])
                        if var_type == "сим" and len(val) != 1:
                            raise Exception("Символьная величина должна быть ровно один символ.")
                    else:
                        raise Exception(f"Неподдерживаемый тип: {var_type}")
                except Exception as e:
                    print(f"Ошибка преобразования значения для '{target}': {e}")
                    continue
                if env[var_name]["value"] is None:
                    env[var_name]["value"] = {}
                env[var_name]["value"][indices] = val
            else:
                print(f"Переменная '{target}' не объявлена.")


def process_algorithm_call(line, env, interpreter):
    """
    Проверяет, является ли строка вызовом алгоритма-процедуры.
    Поддерживаются формы:
       имя алгоритма-процедуры
       имя алгоритма-процедуры(список параметров)
    Для упрощения параметры не обрабатываются.
    """
    line = line.strip()
    if "(" in line:
        name_part = line.split("(", 1)[0].strip()
    else:
        name_part = line
    if name_part in interpreter.algorithms:
        alg = interpreter.algorithms[name_part]
        execute_lines(alg["body"], env, interpreter.robot)
        return True
    return False


def execute_line(line, env, robot, interpreter=None):
    """
    Исполняет одну строку кода.
    Обрабатываются:
      - Объявления (если строка начинается с одного из ALLOWED_TYPES)
      - Присваивания (оператор ":=")
      - Команда вывода (начинается со слова "вывод")
      - Команда ввода (начинается со слова "ввод")
      - Команды контроля (утв, дано, надо)
      - Команды управления роботом
      - Команды управления выполнением: пауза, стоп
      - Вызовы алгоритмов-процедур
      - Команда "выход" (для выхода из цикла или алгоритма)
    Если строка не распознана, выводится сообщение.
    """
    lower_line = line.lower().strip()

    # Объявления
    for t in ALLOWED_TYPES:
        if lower_line.startswith(t):
            try:
                process_declaration(line, env)
            except Exception as e:
                print(f"Ошибка объявления: {e}")
            return

    # Присваивания
    if ":=" in line:
        try:
            process_assignment(line, env)
        except Exception as e:
            print(f"Ошибка присваивания: {e}")
        return

    # Вывод
    if lower_line.startswith("вывод"):
        try:
            process_output(line, env)
        except Exception as e:
            print(f"Ошибка команды 'вывод': {e}")
        return

    # Ввод
    if lower_line.startswith("ввод"):
        try:
            process_input(line, env)
        except Exception as e:
            print(f"Ошибка команды 'ввод': {e}")
        return

    # Команды контроля: утв, дано, надо
    if lower_line.startswith("утв") or lower_line.startswith("дано") or lower_line.startswith("надо"):
        try:
            process_control_command(line, env)
        except Exception as e:
            print(e)
            raise e
        return

    # Команды управления выполнением: пауза и стоп
    if lower_line.startswith("пауза"):
        input("Пауза. Нажмите Enter для продолжения...")
        return
    if lower_line.startswith("стоп"):
        raise Exception("Выполнение программы прервано командой 'стоп'.")

    # Команды управления Роботом
    if process_robot_command(line, robot):
        return

    # Вызов алгоритма-процедуры (если интерпретатор передан)
    if interpreter is not None and process_algorithm_call(line, env, interpreter):
        return

    # Команда "выход" – используется для прерывания цикла или алгоритма
    if lower_line.startswith("выход"):
        raise Exception("Выход из цикла/алгоритма.")

    print(f"Неизвестная команда: {line}")


def execute_lines(lines, env, robot, interpreter=None):
    """
    Исполняет список строк (например, тело алгоритма или тело цикла).
    Поддерживается конструкция цикла:
      нц <число> раз
         ... (тело цикла)
      кц
    Если внутри цикла встречается команда "выход", то цикл прерывается.
    """
    i = 0
    while i < len(lines):
        line = lines[i]
        lower_line = line.lower().strip()
        # Обработка цикла: нц ... кц
        if lower_line.startswith("нц"):
            tokens = lower_line.split()
            if len(tokens) < 3 or tokens[2] != "раз":
                raise Exception("Неверный синтаксис цикла. Ожидается: нц <число> раз")
            try:
                count = int(tokens[1])
            except:
                raise Exception("Неверное число повторений в цикле.")
            loop_body = []
            i += 1
            while i < len(lines) and lines[i].lower().strip() != "кц":
                loop_body.append(lines[i])
                i += 1
            if i == len(lines):
                raise Exception("Отсутствует команда 'кц' для завершения цикла.")
            i += 1  # пропускаем "кц"
            for j in range(count):
                try:
                    execute_lines(loop_body, env, robot, interpreter)
                except Exception as e:
                    # Если команда "выход" вызвала исключение, прекращаем выполнение цикла
                    if str(e).startswith("Выход"):
                        break
                    else:
                        raise e
            continue
        # Если команда "выход" вне цикла
        if lower_line.startswith("выход"):
            raise Exception("Выход из алгоритма.")
        # Обработка прочих строк
        execute_line(line, env, robot, interpreter)
        i += 1
