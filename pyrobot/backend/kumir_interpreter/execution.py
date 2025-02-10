# execution.py

from .declarations import (
    process_declaration,
    process_assignment,
    process_output,
    process_input
)
from .robot_commands import process_robot_command
from .safe_eval import safe_eval, get_eval_env
from .constants import ALLOWED_TYPES


def process_control_command(line, env):
    """
    Processes control commands: утв, дано, надо.
    Evaluates the logical expression (after the keyword) and, if the result is not true,
    raises an exception to terminate the current algorithm execution.
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
            condition = result if isinstance(result, bool) else (str(result).strip().lower() == "да")
            if not condition:
                raise Exception(f"Отказ: условие '{expr}' не выполнено (результат: {result}).")
            return True
    return False


def process_if_block(lines, start_index, env, robot, interpreter):
    """
    Processes the "если-то-[иначе]-все" block.
    Returns the index of the line after the block.
    Syntax:
        если условие
          то серия1
          [иначе серия2]
        все
    If the condition is true, series1 is executed; otherwise (if present) series2.
    """
    n = len(lines)
    cond_line = lines[start_index].strip()
    if not cond_line.lower().startswith("если"):
        raise Exception("Блок if должен начинаться со слова 'если'")
    condition_expr = cond_line[len("если"):].strip()
    i = start_index + 1
    series1 = []
    series2 = []
    found_then = False
    while i < n:
        line = lines[i].strip()
        lower_line = line.lower()
        if lower_line == "все":
            break
        elif lower_line.startswith("то") and not found_then:
            content = line[len("то"):].strip()
            if content:
                series1.append(content)
            found_then = True
            i += 1
            continue
        elif lower_line.startswith("иначе"):
            content = line[len("иначе"):].strip()
            if content:
                series2.append(content)
            i += 1
            while i < n and lines[i].strip().lower() != "все":
                series2.append(lines[i])
                i += 1
            break
        else:
            if not found_then:
                condition_expr += " " + line
            else:
                series1.append(line)
        i += 1

    if i >= n or lines[i].strip().lower() != "все":
        raise Exception("Отсутствует 'все' для завершения конструкции 'если'")
    eval_env = get_eval_env(env)
    try:
        cond_value = safe_eval(condition_expr, eval_env)
    except Exception as e:
        raise Exception(f"Ошибка вычисления условия in 'если': {e}")
    cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
    if cond_bool:
        execute_lines(series1, env, robot, interpreter)
    else:
        if series2:
            execute_lines(series2, env, robot, interpreter)
    return i + 1


def process_select_block(lines, start_index, env, robot, interpreter):
    """
    Processes the "выбор-при-[иначе]-все" block.
    Syntax:
        выбор
          при условие1 : серия1
          при условие2 : серия2
          ...
          [иначе серияN+1]
        все
    The first branch for which the condition is true is executed; if no condition is met and an "иначе" branch is present, it is executed.
    Returns the index of the line after the block.
    """
    n = len(lines)
    i = start_index + 1  # after "выбор"
    branches = []  # list of tuples (condition_expr, series_lines)
    else_series = []
    while i < n:
        line = lines[i].strip()
        lower_line = line.lower()
        if lower_line == "все":
            break
        if lower_line.startswith("при"):
            parts = line.split(":", 1)
            if len(parts) != 2:
                raise Exception("Неверный синтаксис ветки 'при': отсутствует двоеточие")
            cond_part = parts[0].strip()
            condition_expr = cond_part[len("при"):].strip()
            series_line = parts[1].strip()
            branches.append((condition_expr, [series_line]))
        elif lower_line.startswith("иначе"):
            content = line[len("иначе"):].strip()
            else_series.append(content)
            i += 1
            while i < n and lines[i].strip().lower() != "все":
                else_series.append(lines[i])
                i += 1
            break
        else:
            if branches:
                branches[-1][1].append(line)
            else:
                raise Exception("Неверный синтаксис конструкции 'выбор': ожидается 'при' или 'иначе'")
        i += 1

    if i >= n or lines[i].strip().lower() != "все":
        raise Exception("Отсутствует 'все' для завершения конструкции 'выбор'")
    eval_env = get_eval_env(env)
    executed = False
    for condition_expr, series in branches:
        try:
            cond_value = safe_eval(condition_expr, eval_env)
        except Exception as e:
            raise Exception(f"Ошибка вычисления условия в конструкции 'выбор': {e}")
        cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
        if cond_bool:
            execute_lines(series, env, robot, interpreter)
            executed = True
            break
    if not executed and else_series:
        execute_lines(else_series, env, robot, interpreter)
    return i + 1


def execute_lines(lines, env, robot, interpreter=None):
    """
    Executes a list of lines (for example, the body of an algorithm or a branch).
    Supports:
      - Loops:
          * "нц для" loop (for loop)
          * "нц пока" loop (while loop)
          * "нц <number> раз" loop (N times loop)
          * "нц-кц" loop (infinite loop if no special keyword is present)
      - Branching commands: "если" and "выбор"
      - Other commands (handled by execute_line)
    If the command "выход" is encountered within a loop, the loop is terminated.
    """
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        lower_line = line.lower()
        if lower_line.startswith("если"):
            i = process_if_block(lines, i, env, robot, interpreter)
            continue
        if lower_line.startswith("выбор"):
            i = process_select_block(lines, i, env, robot, interpreter)
            continue
        if lower_line.startswith("нц для"):
            tokens = lower_line.split()
            if len(tokens) < 6:
                raise Exception("Неверный синтаксис цикла 'для'")
            var = tokens[2]
            if tokens[3] != "от":
                raise Exception("Ожидается 'от' в цикле 'для'")
            start_expr = tokens[4]
            if tokens[5] != "до":
                raise Exception("Ожидается 'до' в цикле 'для'")
            end_expr = tokens[6]
            step_expr = "1"
            if len(tokens) > 7:
                if tokens[7] == "шаг" and len(tokens) > 8:
                    step_expr = tokens[8]
                else:
                    raise Exception("Неверный синтаксис шага в цикле 'для'")
            try:
                eval_env = get_eval_env(env)
                start_val = int(safe_eval(start_expr, eval_env))
                end_val = int(safe_eval(end_expr, eval_env))
                step_val = int(safe_eval(step_expr, eval_env))
            except Exception as e:
                raise Exception(f"Ошибка вычисления параметров цикла 'для': {e}")
            env[var] = {"type": "цел", "value": start_val, "kind": "local", "is_table": False}
            loop_body = []
            i += 1
            while i < n and lines[i].strip().lower() != "кц":
                loop_body.append(lines[i])
                i += 1
            if i == n:
                raise Exception("Отсутствует 'кц' для цикла 'для'")
            current = start_val

            def condition(val):
                return val <= end_val if step_val > 0 else val >= end_val

            while condition(current):
                env[var]["value"] = current
                try:
                    execute_lines(loop_body, env, robot, interpreter)
                except Exception as e:
                    if str(e).startswith("Выход"):
                        break
                    else:
                        raise e
                current += step_val
            i += 1  # skip "кц"
            continue
        if lower_line.startswith("нц пока"):
            condition_expr = line[len("нц пока"):].strip()
            loop_body = []
            i += 1
            while i < n and lines[i].strip().lower() != "кц":
                loop_body.append(lines[i])
                i += 1
            if i == n:
                raise Exception("Отсутствует 'кц' для цикла 'пока'")
            while True:
                eval_env = get_eval_env(env)
                try:
                    cond_val = safe_eval(condition_expr, eval_env)
                except Exception as e:
                    raise Exception(f"Ошибка вычисления условия цикла 'пока': {e}")
                cond_bool = cond_val if isinstance(cond_val, bool) else (str(cond_val).strip().lower() == "да")
                if not cond_bool:
                    break
                try:
                    execute_lines(loop_body, env, robot, interpreter)
                except Exception as e:
                    if str(e).startswith("Выход"):
                        break
                    else:
                        raise e
            i += 1  # skip "кц"
            continue
        if lower_line.startswith("нц"):
            tokens = lower_line.split()
            if len(tokens) >= 3 and tokens[2] == "раз":
                try:
                    count = int(tokens[1])
                except Exception as e:
                    raise Exception(f"Ошибка определения количества повторений в цикле 'N раз': {e}")
                loop_body = []
                i += 1
                while i < n and lines[i].strip().lower() != "кц":
                    loop_body.append(lines[i])
                    i += 1
                if i == n:
                    raise Exception("Отсутствует 'кц' для цикла 'N раз'")
                for _ in range(count):
                    try:
                        execute_lines(loop_body, env, robot, interpreter)
                    except Exception as e:
                        if str(e).startswith("Выход"):
                            break
                        else:
                            raise e
                i += 1  # skip "кц"
                continue
        if lower_line.startswith("нц") and lower_line == "нц":
            loop_body = []
            i += 1
            while i < n and lines[i].strip().lower() != "кц":
                loop_body.append(lines[i])
                i += 1
            if i == n:
                raise Exception("Отсутствует 'кц' для бесконечного цикла")
            while True:
                try:
                    execute_lines(loop_body, env, robot, interpreter)
                except Exception as e:
                    if str(e).startswith("Выход"):
                        break
                    else:
                        raise e
            i += 1  # skip "кц"
            continue
        if lower_line.startswith("выход"):
            raise Exception("Выход из цикла/алгоритма.")
        # Process remaining commands using execute_line
        execute_line(line, env, robot, interpreter)
        i += 1


def execute_line(line, env, robot, interpreter=None):
    """
    Executes a single line of code.
    Handles:
      - Declarations (starting with one of ALLOWED_TYPES)
      - Assignments (operator ":=")
      - Output command (starting with "вывод")
      - Input command (starting with "ввод")
      - Control commands (утв, дано, надо)
      - Robot control commands
      - Execution control commands: пауза, стоп
      - Invocation of procedure algorithms (if the line is not recognized)
    If the line is not recognized, prints a message.
    """
    lower_line = line.lower().strip()
    # Declarations
    for t in ALLOWED_TYPES:
        if lower_line.startswith(t):
            try:
                process_declaration(line, env)
            except Exception as e:
                print(f"Ошибка объявления: {e}")
            return

    # Assignments
    if ":=" in line:
        try:
            process_assignment(line, env)
        except Exception as e:
            print(f"Ошибка присваивания: {e}")
        return

    # Output (pass interpreter)
    if lower_line.startswith("вывод"):
        try:
            process_output(line, env, interpreter)
        except Exception as e:
            print(f"Ошибка команды 'вывод': {e}")
        return

    # Input
    if lower_line.startswith("ввод"):
        try:
            process_input(line, env)
        except Exception as e:
            print(f"Ошибка команды 'ввод': {e}")
        return

    # Control commands: утв, дано, надо
    if lower_line.startswith("утв") or lower_line.startswith("дано") or lower_line.startswith("надо"):
        try:
            process_control_command(line, env)
        except Exception as e:
            print(e)
            raise e
        return

    # Execution control commands: пауза, стоп
    if lower_line.startswith("пауза"):
        input("Пауза. Нажмите Enter для продолжения...")
        return
    if lower_line.startswith("стоп"):
        raise Exception("Выполнение программы прервано командой 'стоп'.")

    # Robot control commands
    if process_robot_command(line, robot):
        return

    # If interpreter is provided, check for procedure algorithm invocation
    if interpreter is not None:
        if process_algorithm_call(line, env, interpreter):
            return

    print(f"Неизвестная команда: {line}")


def process_algorithm_call(line, env, interpreter):
    """
    If the line is a procedure algorithm call,
    executes the corresponding algorithm body.
    Supports calls with parameters (parameterization is implemented in a simplified manner).
    Returns True if the call was handled.
    """
    line = line.strip()
    if "(" in line:
        name_part = line.split("(", 1)[0].strip()
    else:
        name_part = line
    if name_part in interpreter.algorithms:
        alg = interpreter.algorithms[name_part]
        execute_lines(alg["body"], env, interpreter.robot, interpreter)
        return True
    return False
