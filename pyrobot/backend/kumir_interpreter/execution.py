"""
Модуль execution.py
@description Реализует функции для выполнения программ на языке KUMIR.
Модуль обрабатывает команды управления, условные блоки, циклы, присваивания, ввод/вывод,
а также вызовы алгоритмов робота. Функции интерпретируют строки кода и выполняют соответствующие действия
с использованием окружения переменных, робота и интерпретатора.
"""

from .constants import ALLOWED_TYPES
from .declarations import (process_declaration, process_assignment, process_output, process_input)
from .robot_commands import process_robot_command
from .safe_eval import safe_eval, get_eval_env


def process_control_command(line, env):
    """
    Обрабатывает команды управления: утв, дано, надо.
    Вычисляет логическое выражение (после ключевого слова) и, если результат не равен True,
    генерирует исключение для прекращения выполнения текущего алгоритма.

    Параметры:
      line (str): Строка команды управления.
      env (dict): Окружение переменных.

    Возвращаемое значение:
      bool: True, если команда успешно обработана, иначе False.

    Исключения:
      Генерирует Exception, если логическое выражение не может быть вычислено или его значение ложно.
    """
    lower_line = line.lower().strip()
    # Перебираем ключевые слова управления
    for keyword in ["утв", "дано", "надо"]:
        if lower_line.startswith(keyword):
            # Извлекаем выражение после ключевого слова
            expr = line[len(keyword):].strip()
            eval_env = get_eval_env(env)
            try:
                result = safe_eval(expr, eval_env)
            except Exception as e:
                raise Exception(f"Ошибка вычисления логического выражения '{expr}': {e}")
            # Если результат не является булевым, сравниваем строковое представление с "да"
            condition = result if isinstance(result, bool) else (str(result).strip().lower() == "да")
            if not condition:
                raise Exception(f"Отказ: условие '{expr}' не выполнено (результат: {result}).")
            return True
    return False


def process_if_block(lines, start_index, env, robot, interpreter):
    """
    Обрабатывает блок условного оператора "если-то-[иначе]-все".
    Если условие истинно, выполняется первая серия команд; в противном случае, если присутствует ветка "иначе",
    выполняется вторая серия команд.

    Синтаксис:
        если условие
          то серия1
          [иначе серия2]
        все

    Параметры:
      lines (list of str): Список строк программы.
      start_index (int): Индекс строки, с которой начинается блок if.
      env (dict): Окружение переменных.
      robot (object): Объект робота.
      interpreter (object): Объект интерпретатора (опционально), используемый для буферизации вывода.

    Возвращаемое значение:
      int: Индекс строки после завершения блока if.

    Исключения:
      Генерируется Exception, если блок if имеет неверный синтаксис или отсутствует слово "все".
    """
    n = len(lines)
    cond_line = lines[start_index].strip()
    if not cond_line.lower().startswith("если"):
        raise Exception("Блок if должен начинаться со слова 'если'")
    # Извлекаем условное выражение из строки, начиная сразу после "если"
    condition_expr = cond_line[len("если"):].strip()
    i = start_index + 1
    series1 = []  # Команды для выполнения, если условие истинно
    series2 = []  # Команды для выполнения в ветке "иначе" (если есть)
    found_then = False  # Флаг, указывающий, что обнаружена ветка "то"
    # Читаем строки блока до ключевого слова "все"
    while i < n:
        line = lines[i].strip()
        lower_line = line.lower()
        if lower_line == "все":
            break
        elif lower_line.startswith("то") and not found_then:
            # Обработка ветки "то"
            content = line[len("то"):].strip()
            if content:
                series1.append(content)
            found_then = True
            i += 1
            continue
        elif lower_line.startswith("иначе"):
            # Обработка ветки "иначе"
            content = line[len("иначе"):].strip()
            if content:
                series2.append(content)
            i += 1
            # Добавляем последующие строки до "все" в ветку "иначе"
            while i < n and lines[i].strip().lower() != "все":
                series2.append(lines[i])
                i += 1
            break
        else:
            if not found_then:
                # Если ветка "то" ещё не обнаружена, часть условия продолжается в следующих строках
                condition_expr += " " + line
            else:
                # После ветки "то" все строки относятся к серии команд для true-ветки
                series1.append(line)
        i += 1

    if i >= n or lines[i].strip().lower() != "все":
        raise Exception("Отсутствует 'все' для завершения конструкции 'если'")
    eval_env = get_eval_env(env)
    try:
        cond_value = safe_eval(condition_expr, eval_env)
    except Exception as e:
        raise Exception(f"Ошибка вычисления условия in 'если': {e}")
    # Приводим условное значение к булевому типу
    cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
    if cond_bool:
        execute_lines(series1, env, robot, interpreter)
    else:
        if series2:
            execute_lines(series2, env, robot, interpreter)
    return i + 1


def process_select_block(lines, start_index, env, robot, interpreter):
    """
    Обрабатывает блок оператора выбора "выбор-при-[иначе]-все".
    В блоке перечисляются ветки с условиями, и выполняется первая ветка, условие которой истинно.
    Если ни одно условие не истинно, а присутствует ветка "иначе", выполняется она.

    Синтаксис:
        выбор
          при условие1 : серия1
          при условие2 : серия2
          ...
          [иначе серияN+1]
        все

    Параметры:
      lines (list of str): Список строк программы.
      start_index (int): Индекс строки, с которой начинается блок выбора.
      env (dict): Окружение переменных.
      robot (object): Объект робота.
      interpreter (object): Объект интерпретатора для буферизации вывода (опционально).

    Возвращаемое значение:
      int: Индекс строки после завершения блока выбора.

    Исключения:
      Генерируется Exception, если синтаксис ветки 'при' неверен или отсутствует завершающее слово "все".
    """
    n = len(lines)
    i = start_index + 1  # Пропускаем строку "выбор"
    branches = []  # Список кортежей (условие, список команд)
    else_series = []  # Команды ветки "иначе", если присутствует
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
                # Добавляем дополнительные команды к последней ветке
                branches[-1][1].append(line)
            else:
                raise Exception("Неверный синтаксис конструкции 'выбор': ожидается 'при' или 'иначе'")
        i += 1

    if i >= n or lines[i].strip().lower() != "все":
        raise Exception("Отсутствует 'все' для завершения конструкции 'выбор'")
    eval_env = get_eval_env(env)
    executed = False
    # Проверяем каждую ветку и выполняем первую, условие которой истинно
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
    Выполняет список строк кода (например, тело алгоритма или ветку условного оператора).
    Поддерживаются:
      - Циклы:
          * "нц для" – цикл с переменной и диапазоном.
          * "нц пока" – цикл с условием.
          * "нц <число> раз" – цикл, выполняющийся заданное число раз.
          * "нц" – бесконечный цикл (если не указана команда выхода).
      - Условные операторы: "если" и "выбор".
      - Прочие команды, обрабатываемые функцией execute_line.
    Если встречается команда "выход", генерируется исключение для завершения цикла или алгоритма.

    Параметры:
      lines (list of str): Список строк кода для выполнения.
      env (dict): Окружение переменных.
      robot (object): Объект робота.
      interpreter (object, опционально): Объект интерпретатора для буферизации вывода.

    Исключения:
      Генерируются исключения для прерывания выполнения в случае ошибки или команды "выход".
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
            # Инициализируем переменную цикла как локальную
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

            # Выполняем тело цикла до тех пор, пока условие истинно
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
            i += 1  # Пропускаем "кц"
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
            # Бесконечное выполнение цикла до изменения условия
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
            i += 1  # Пропускаем "кц"
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
                i += 1  # Пропускаем "кц"
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
            i += 1  # Пропускаем "кц"
            continue
        if lower_line.startswith("выход"):
            raise Exception("Выход из цикла/алгоритма.")
        # Обработка остальных команд с помощью execute_line
        execute_line(line, env, robot, interpreter)
        i += 1


def execute_line(line, env, robot, interpreter=None):
    """
    Выполняет одну строку кода.
    Обрабатывает:
      - Объявления переменных (начинающиеся с одного из ALLOWED_TYPES).
      - Присваивания (оператор ":=").
      - Команду вывода (начинается со слова "вывод").
      - Команду ввода (начинается со слова "ввод").
      - Команды управления (утв, дано, надо).
      - Команды управления роботом.
      - Команды управления выполнением: пауза, стоп.
      - Вызовы процедурных алгоритмов (если строка не распознана как другая команда).
    Если команда не распознана, выводится сообщение об ошибке.

    Параметры:
      line (str): Строка кода для выполнения.
      env (dict): Окружение переменных.
      robot (object): Объект робота.
      interpreter (object, опционально): Объект интерпретатора для буферизации вывода и вызова алгоритмов.
    """
    lower_line = line.lower().strip()
    # Обработка объявления переменных
    for t in ALLOWED_TYPES:
        if lower_line.startswith(t):
            try:
                process_declaration(line, env)
            except Exception as e:
                print(f"Ошибка объявления: {e}")
            return

    # Обработка присваивания
    if ":=" in line:
        try:
            process_assignment(line, env)
        except Exception as e:
            print(f"Ошибка присваивания: {e}")
        return

    # Обработка команды вывода (передаем interpreter, если он есть)
    if lower_line.startswith("вывод"):
        try:
            process_output(line, env, interpreter)
        except Exception as e:
            print(f"Ошибка команды 'вывод': {e}")
        return

    # Обработка команды ввода
    if lower_line.startswith("ввод"):
        try:
            process_input(line, env)
        except Exception as e:
            print(f"Ошибка команды 'ввод': {e}")
        return

    # Обработка команд управления (утв, дано, надо)
    if lower_line.startswith("утв") or lower_line.startswith("дано") or lower_line.startswith("надо"):
        try:
            process_control_command(line, env)
        except Exception as e:
            print(e)
            raise e
        return

    # Команда паузы: ожидает нажатия Enter для продолжения
    if lower_line.startswith("пауза"):
        input("Пауза. Нажмите Enter для продолжения...")
        return
    # Команда стоп: прерывает выполнение программы
    if lower_line.startswith("стоп"):
        raise Exception("Выполнение программы прервано командой 'стоп'.")

    # Обработка команд управления роботом
    if process_robot_command(line, robot):
        return

    # Если передан интерпретатор, проверяем вызов процедуры (алгоритма)
    if interpreter is not None:
        if process_algorithm_call(line, env, interpreter):
            return

    # Если команда не распознана, выводим сообщение
    print(f"Неизвестная команда: {line}")


def process_algorithm_call(line, env, interpreter):
    """
    Обрабатывает вызов процедурного алгоритма.
    Если строка соответствует имени объявленного алгоритма,
    выполняет тело алгоритма.
    Поддерживается вызов с параметрами (параметризация реализована упрощенно).

    Параметры:
      line (str): Строка, содержащая вызов алгоритма.
      env (dict): Окружение переменных.
      interpreter (object): Объект интерпретатора, содержащий словарь алгоритмов.

    Возвращаемое значение:
      bool: True, если вызов алгоритма обработан, иначе False.
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
