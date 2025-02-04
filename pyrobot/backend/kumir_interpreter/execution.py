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
    Обрабатывает команды контроля выполнения: утв, дано, надо.
    Вычисляет логическое выражение (после ключевого слова) и, если результат не является истинным,
    выбрасывает исключение, прекращающее выполнение текущего алгоритма.
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
    Обрабатывает блок конструкции "если-то-[иначе]-все".
    Возвращает индекс следующей строки после блока.
    Синтаксис:
        если условие
          то серия1
          [иначе серия2]
        все
    Если условие истинно – выполняется серия1, иначе (если есть) серия2.
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


def process_выбор_block(lines, start_index, env, robot, interpreter):
    """
    Обрабатывает блок конструкции "выбор-при-[иначе]-все".
    Синтаксис:
        выбор
          при условие1 : серия1
          при условие2 : серия2
          ...
          [иначе серияN+1]
        все
    Выполняется первая серия, для которой условие истинно; если ни одно условие не истинно, а блок "иначе" присутствует – выполняется она.
    Возвращает индекс следующей строки после блока.
    """
    n = len(lines)
    i = start_index + 1  # после "выбор"
    branches = []  # список кортежей (condition_expr, series_lines)
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
    Исполняет список строк (например, тело алгоритма или блока цикла, ветвления и т.д.).
    Поддерживает:
      - Циклы:
          * Цикл "для": начинается со строки, начинающейся с "нц для"
          * Цикл "пока": начинается с "нц пока"
          * Цикл "N раз": начинается с "нц" <число> "раз"
          * Цикл "нц-кц": если ни одно специальное слово не встречается, считается бесконечным (если не используется "выход")
      - Команды ветвления: "если" и "выбор"
      - Прочие команды (обрабатываются функцией execute_line)
    Если внутри цикла встречается команда "выход", цикл прерывается.
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
            i = process_выбор_block(lines, i, env, robot, interpreter)
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
            i += 1  # пропускаем "кц"
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
            i += 1  # пропускаем "кц"
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
                i += 1  # пропускаем "кц"
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
            i += 1  # пропускаем "кц"
            continue
        if lower_line.startswith("выход"):
            raise Exception("Выход из цикла/алгоритма.")
        # Остальные команды обрабатываем через execute_line
        execute_line(line, env, robot, interpreter)
        i += 1


def execute_line(line, env, robot, interpreter=None):
    """
    Исполняет одну строку кода.
    Обрабатывает:
      - Объявления (начинаются с одного из ALLOWED_TYPES)
      - Присваивания (оператор ":=")
      - Команду вывода (начинается со слова "вывод")
      - Команду ввода (начинается со слова "ввод")
      - Команды контроля (утв, дано, надо)
      - Команды управления роботом
      - Команды управления выполнением: пауза, стоп
      - Вызов алгоритмов-процедур (если строка не распознана)
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

    # Вывод (передаём interpreter)
    if lower_line.startswith("вывод"):
        try:
            process_output(line, env, interpreter)
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

    # Команды управления выполнением: пауза, стоп
    if lower_line.startswith("пауза"):
        input("Пауза. Нажмите Enter для продолжения...")
        return
    if lower_line.startswith("стоп"):
        raise Exception("Выполнение программы прервано командой 'стоп'.")

    # Команды управления Роботом
    if process_robot_command(line, robot):
        return

    # Если interpreter передан, проверяем вызов алгоритма-процедуры
    if interpreter is not None:
        if process_algorithm_call(line, env, interpreter):
            return

    print(f"Неизвестная команда: {line}")


def process_algorithm_call(line, env, interpreter):
    """
    Если строка является вызовом алгоритма-процедуры,
    выполняет тело соответствующего алгоритма.
    Поддерживаются вызовы с параметрами (параметризацию реализуем в упрощённом виде).
    Возвращает True, если вызов обработан.
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
