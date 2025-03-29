"""
Модуль execution.py
@description Реализует функции для выполнения управляющих конструкций
языка KUMIR (циклы, условия) и диспетчеризацию отдельных команд.
"""
import logging
import re

from .declarations import process_declaration, process_assignment, process_output, process_input, ALLOWED_TYPES
from .robot_commands import process_robot_command  # Handles robot actions
from .safe_eval import safe_eval, get_eval_env, KumirEvalError  # For evaluating expressions
# Import RobotError to handle potential errors from robot commands/sensors
from .robot_state import RobotError  # Assuming refactored robot module

logger = logging.getLogger('KumirExecution')


class KumirExecutionError(Exception):
    pass


def process_control_command(line, env):
    """ Обрабатывает команды управления: утв, дано, надо. """
    lower_line = line.lower().strip()
    keyword = None
    for kw in ["утв", "дано", "надо"]:
        if lower_line.startswith(kw): keyword = kw; break
    if keyword:
        expr = line[len(keyword):].strip()
        if not expr: raise KumirExecutionError(f"'{keyword}' требует логическое выражение.")
        eval_env = get_eval_env(env)  # Робот здесь не нужен для обычных утв
        try:
            result = safe_eval(expr, eval_env)
            logger.debug(f"Control '{keyword}' evaluated '{expr}' -> {result}")
        except Exception as e:
            raise KumirEvalError(f"Ошибка вычисления '{expr}' в '{keyword}': {e}")
        condition = result if isinstance(result, bool) else (str(result).strip().lower() == "да")
        if not condition:
            logger.warning(f"Control fail: '{keyword} {expr}' -> False.")
            raise KumirExecutionError(f"Отказ: условие '{expr}' в '{keyword}' не выполнено ({result}).")
        logger.info(f"Control '{keyword} {expr}' OK.")
        return True
    return False


def process_if_block(lines, start_index, env, robot, interpreter):
    """ Обрабатывает блок "если-то-[иначе]-все". """
    n = len(lines);
    header_line = lines[start_index].strip()
    if not header_line.lower().startswith("если"): raise KumirExecutionError(
        "Internal Error: process_if_block без 'если'.")
    condition_expr = header_line[len("если"):].strip()
    i = start_index + 1;
    series1_lines = [];
    series2_lines = [];
    current_series = None
    found_then, found_else, end_if_index = False, False, -1
    while i < n:  # --- Parsing ---
        line = lines[i].strip();
        lower_line = line.lower()
        if lower_line == "все":
            end_if_index = i; break
        elif lower_line.startswith("то") and not found_then:
            found_then = True;
            current_series = series1_lines;
            content = line[len("то"):].strip()
            if content: current_series.append(content)
        elif lower_line.startswith("иначе") and found_then and not found_else:
            found_else = True;
            current_series = series2_lines;
            content = line[len("иначе"):].strip()
            if content: current_series.append(content)
        else:
            if current_series is not None:
                current_series.append(line)
            elif not found_then:
                condition_expr += " " + line  # Multi-line condition
            else:
                raise KumirExecutionError(f"Неожиданная строка в 'если': '{line}'.")
        i += 1
    # --- Validation ---
    if end_if_index == -1: raise KumirExecutionError("Отсутствует 'все' для 'если'.")
    if not found_then: raise KumirExecutionError("Отсутствует 'то' в 'если'.")
    if not condition_expr: raise KumirExecutionError("Отсутствует условие после 'если'.")
    # --- Evaluation ---
    logger.debug(f"Evaluating 'если': {condition_expr}")
    # === FIX: Pass robot to get_eval_env for sensor functions ===
    eval_env_with_robot = get_eval_env(env, robot)
    try:
        cond_value = safe_eval(condition_expr, eval_env_with_robot)  # Use env with robot sensors
    except Exception as e:
        raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'если': {e}")
    cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
    logger.info(f"'Если {condition_expr}' -> {cond_bool}.")
    # --- Execution ---
    if cond_bool:
        execute_lines(series1_lines, env, robot, interpreter)
    elif found_else:
        execute_lines(series2_lines, env, robot, interpreter)
    return end_if_index + 1


def process_select_block(lines, start_index, env, robot, interpreter):
    """ Обрабатывает блок "выбор-при-[иначе]-все". """
    n = len(lines);
    i = start_index + 1
    if not lines[start_index].strip().lower() == "выбор": raise KumirExecutionError(
        "Internal: process_select_block без 'выбор'.")
    branches = [];
    else_series = [];
    found_else, end_select_index = False, -1;
    current_branch_lines = None
    while i < n:  # --- Parsing ---
        line = lines[i].strip();
        lower_line = line.lower()
        if lower_line == "все":
            end_select_index = i; break
        elif lower_line.startswith("при"):
            if found_else: raise KumirExecutionError("'при' после 'иначе' в 'выбор'.")
            parts = line.split(":", 1)
            if len(parts) != 2: raise KumirExecutionError(f"Нет ':' в ветке 'при': '{line}'")
            cond_part = parts[0].strip();
            condition_expr = cond_part[len("при"):].strip()
            if not condition_expr: raise KumirExecutionError(f"Нет условия после 'при': '{line}'")
            series_line = parts[1].strip();
            current_branch_lines = [series_line] if series_line else []
            branches.append((condition_expr, current_branch_lines))
        elif lower_line.startswith("иначе"):
            if found_else: raise KumirExecutionError("Повторное 'иначе' в 'выбор'.")
            found_else = True;
            current_branch_lines = else_series;
            content = line[len("иначе"):].strip()
            if content: current_branch_lines.append(content)
        else:
            if current_branch_lines is not None:
                current_branch_lines.append(line)
            else:
                raise KumirExecutionError(f"Неожиданная строка в 'выбор': '{line}'.")
        i += 1
    # --- Validation ---
    if end_select_index == -1: raise KumirExecutionError("Отсутствует 'все' для 'выбор'.")
    if not branches and not found_else: logger.warning("Конструкция 'выбор' пуста.")
    # --- Evaluation ---
    # === FIX: Pass robot to get_eval_env ===
    eval_env_with_robot = get_eval_env(env, robot)
    executed = False
    for idx, (condition_expr, series) in enumerate(branches):
        logger.debug(f"Eval 'при' #{idx + 1}: {condition_expr}")
        try:
            cond_value = safe_eval(condition_expr, eval_env_with_robot)  # Use env with robot sensors
        except Exception as e:
            raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'выбор': {e}")
        cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
        logger.info(f"'При {condition_expr}' -> {cond_bool}.")
        if cond_bool:
            logger.debug(f"Exec 'при' branch #{idx + 1}...")
            execute_lines(series, env, robot, interpreter);
            executed = True;
            break
    if not executed and found_else: logger.debug("Exec 'иначе' branch..."); execute_lines(else_series, env, robot,
                                                                                          interpreter)
    return end_select_index + 1


def process_loop_for(lines, start_index, env, robot, interpreter):
    """ Обрабатывает цикл 'нц для ... кц'. """
    n = len(lines);
    header_line = lines[start_index].strip()
    match = re.match(r"нц\s+для\s+([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)\s+от\s+(.+)\s+до\s+(.+?)(?:\s+шаг\s+(.+))?$",
                     header_line.lower())
    if not match: raise KumirExecutionError(f"Неверный синтаксис 'нц для': {header_line}")
    var_name, start_expr, end_expr, step_expr = match.groups();
    step_expr = step_expr if step_expr else "1"
    # --- Find loop body ---
    i = start_index + 1;
    loop_body = [];
    end_loop_index = -1;
    nesting = 0
    while i < n:
        line = lines[i].strip();
        lower_line = line.lower()
        if lower_line.startswith("нц"):
            nesting += 1
        elif lower_line == "кц":
            if nesting == 0:
                end_loop_index = i; break
            else:
                nesting -= 1
        loop_body.append(line);
        i += 1
    if end_loop_index == -1: raise KumirExecutionError("Отсутствует 'кц' для 'нц для'.")
    # --- Evaluate params ---
    # === FIX: Pass robot - needed if range depends on sensors? Unlikely but possible ===
    eval_env_with_robot = get_eval_env(env, robot)  # Use robot env here too
    try:
        start_val = int(safe_eval(start_expr, eval_env_with_robot))
        end_val = int(safe_eval(end_expr, eval_env_with_robot))
        step_val = int(safe_eval(step_expr, eval_env_with_robot))
    except Exception as e:
        raise KumirEvalError(f"Ошибка вычисления параметров 'для': {e}")
    if step_val == 0: raise KumirExecutionError("Шаг в 'для' не может быть 0.")
    # --- Execute Loop ---
    original_value = None;
    was_declared = var_name in env
    if was_declared:
        original_value = env[var_name].get('value'); env[var_name]['value'] = None  # Temporarily clear
    else:
        env[var_name] = {"type": "цел", "value": None, "kind": "local", "is_table": False}
    current = start_val;
    logger.info(f"Start 'нц для {var_name}' {start_val}..{end_val} step {step_val}.")
    iter_count = 0
    try:
        condition = (step_val > 0 and current <= end_val) or (step_val < 0 and current >= end_val)
        while condition:
            iter_count += 1;
            env[var_name]["value"] = current
            logger.debug(f"'для {var_name}' iter {iter_count}, val={current}")
            try:
                execute_lines(loop_body, env, robot, interpreter)
            except KumirExecutionError as e:
                if str(e) == "Выход":
                    logger.info("'выход' прервал 'для'.")
                    break  # Move the break statement here
                else:
                    raise e
            current += step_val
            condition = (step_val > 0 and current <= end_val) or (step_val < 0 and current >= end_val)
    finally:  # --- Restore/Cleanup ---
        if was_declared:
            env[var_name]['value'] = original_value; logger.debug(f"Restored '{var_name}'.")
        elif var_name in env:
            del env[var_name]; logger.debug(f"Removed temp loop var '{var_name}'.")
    logger.info(f"End 'нц для {var_name}' after {iter_count} iters.")
    return end_loop_index + 1


def process_loop_while(lines, start_index, env, robot, interpreter):
    """ Обрабатывает цикл 'нц пока ... кц'. """
    n = len(lines);
    header_line = lines[start_index].strip();
    match = re.match(r"нц\s+пока\s+(.+)", header_line.lower())
    if not match: raise KumirExecutionError(f"Неверный синтаксис 'нц пока': {header_line}")
    condition_expr = match.group(1).strip();
    if not condition_expr: raise KumirExecutionError("Нет условия после 'нц пока'.")
    # --- Find body ---
    i = start_index + 1;
    loop_body = [];
    end_loop_index = -1;
    nesting = 0
    while i < n:
        line = lines[i].strip();
        lower_line = line.lower()
        if lower_line.startswith("нц"):
            nesting += 1
        elif lower_line == "кц":
            if nesting == 0:
                end_loop_index = i; break
            else:
                nesting -= 1
        loop_body.append(line);
        i += 1
    if end_loop_index == -1: raise KumirExecutionError("Отсутствует 'кц' для 'нц пока'.")
    # --- Execute ---
    logger.info(f"Start 'нц пока {condition_expr}'.")
    iter_count = 0
    while True:
        iter_count += 1
        # === FIX: Pass robot to get_eval_env ===
        eval_env_with_robot = get_eval_env(env, robot)
        try:
            cond_value = safe_eval(condition_expr, eval_env_with_robot)  # Use env with sensors
        except Exception as e:
            raise KumirEvalError(f"Ошибка вычисления условия '{condition_expr}' в 'пока': {e}")
        cond_bool = cond_value if isinstance(cond_value, bool) else (str(cond_value).strip().lower() == "да")
        logger.debug(f"'пока' condition '{condition_expr}' -> {cond_bool} (Iter {iter_count})")
        if not cond_bool: logger.debug("Выход из 'нц пока'."); break
        try:
            execute_lines(loop_body, env, robot, interpreter)
        except KumirExecutionError as e:
            if str(e) == "Выход": logger.info("'выход' прервал 'пока'.")
        else:
            raise e
    logger.info(f"End 'нц пока {condition_expr}' after {iter_count - 1} success iters.")
    return end_loop_index + 1


def process_loop_n_times(lines, start_index, env, robot, interpreter):
    """ Обрабатывает цикл 'нц <N> раз ... кц'. """
    n = len(lines);
    header_line = lines[start_index].strip();
    match = re.match(r"нц\s+(\d+)\s+раз", header_line.lower())
    if not match: raise KumirExecutionError(f"Неверный синтаксис 'N раз': {header_line}")
    try:
        count = int(match.group(1))
    except ValueError:
        raise KumirExecutionError(f"Неверное число повторений 'N раз': {match.group(1)}")
    if count < 0: raise KumirExecutionError(f"Число повторений 'N раз' < 0: {count}")
    # --- Find body ---
    i = start_index + 1;
    loop_body = [];
    end_loop_index = -1;
    nesting = 0
    while i < n:
        line = lines[i].strip();
        lower_line = line.lower()
        if lower_line.startswith("нц"):
            nesting += 1
        elif lower_line == "кц":
            if nesting == 0:
                end_loop_index = i; break
            else:
                nesting -= 1
        loop_body.append(line);
        i += 1
    if end_loop_index == -1: raise KumirExecutionError("Отсутствует 'кц' для 'N раз'.")
    # --- Execute ---
    logger.info(f"Start 'нц {count} раз'.")
    for iteration in range(count):
        logger.debug(f"'N раз' iter {iteration + 1}/{count}")
        try:
            execute_lines(loop_body, env, robot, interpreter)
        except KumirExecutionError as e:
            if str(e) == "Выход":
                logger.info(f"'выход' прервал 'N раз' на итерации {iteration + 1}.")
                break
            else:
                raise e
    logger.info(f"End 'нц {count} раз'.")
    return end_loop_index + 1


def process_loop_infinite(lines, start_index, env, robot, interpreter):
    """ Обрабатывает цикл 'нц ... кц'. """
    n = len(lines);
    i = start_index + 1
    if not lines[start_index].strip().lower() == "нц": raise KumirExecutionError(
        "Internal: process_loop_infinite без 'нц'.")
    # --- Find body ---
    loop_body = [];
    end_loop_index = -1;
    nesting = 0
    while i < n:
        line = lines[i].strip();
        lower_line = line.lower()
        if lower_line.startswith("нц"):
            nesting += 1
        elif lower_line == "кц":
            if nesting == 0:
                end_loop_index = i; break
            else:
                nesting -= 1
        loop_body.append(line);
        i += 1
    if end_loop_index == -1: raise KumirExecutionError("Отсутствует 'кц' для 'нц'.")
    # --- Execute ---
    logger.info("Start infinite 'нц' loop.");
    iter_count = 0
    while True:
        iter_count += 1;
        logger.debug(f"Infinite 'нц' iter {iter_count}")
        try:
            execute_lines(loop_body, env, robot, interpreter)
        except KumirExecutionError as e:
            if str(e) == "Выход":
                logger.info(f"'выход' прервал 'нц' на итерации {iter_count}.")
            else:
                raise e
    # Safeguard (optional, configure limit externally?)
    # if iter_count > 10000: raise KumirExecutionError("Превышен лимит итераций для 'нц'.")
    logger.info(f"End infinite 'нц'.")
    return end_loop_index + 1


def process_algorithm_call(line, env, robot, interpreter):
    """ Обрабатывает вызов другого алгоритма (простая реализация без параметров). """
    line_strip = line.strip()
    call_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_]*)(?:\(.*\))?$", line_strip)
    if call_match:
        algo_name = call_match.group(1)
        if algo_name in interpreter.algorithms:
            logger.info(f"Executing algorithm call: {algo_name}")
            alg_to_run = interpreter.algorithms[algo_name]
            execute_lines(alg_to_run["body"], env, robot, interpreter)  # Pass current context
            logger.info(f"Finished call: {algo_name}")
            return True
    return False


def execute_lines(lines, env, robot, interpreter=None):
    """ Выполняет список строк кода. """
    i = 0;
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if not line: i += 1; continue  # Skip empty
        lower_line = line.lower();
        processed = False
        # --- Block Structures ---
        if lower_line.startswith("если"):
            i = process_if_block(lines, i, env, robot, interpreter); processed = True
        elif lower_line == "выбор":
            i = process_select_block(lines, i, env, robot, interpreter); processed = True
        elif lower_line.startswith("нц"):
            if lower_line.startswith("нц для"):
                i = process_loop_for(lines, i, env, robot, interpreter)
            elif lower_line.startswith("нц пока"):
                i = process_loop_while(lines, i, env, robot, interpreter)
            elif re.match(r"нц\s+\d+\s+раз", lower_line):
                i = process_loop_n_times(lines, i, env, robot, interpreter)
            elif lower_line == "нц":
                i = process_loop_infinite(lines, i, env, robot, interpreter)
            else:
                raise KumirExecutionError(f"Неизвестный тип 'нц': {line}")
            processed = True
        # --- Single Line ---
        if not processed: execute_line(line, env, robot, interpreter); i += 1


def execute_line(line, env, robot, interpreter=None):
    """ Выполняет одну строку кода. """
    logger.debug(f"Exec line: '{line}'")
    line_strip = line.strip();
    lower_line = line_strip.lower()
    # 1. Declaration
    for kw in ALLOWED_TYPES:
        if re.match(rf"^{kw}(?:\s+.*|$)", lower_line): process_declaration(line_strip, env); return
    # 2. Assignment
    if ":=" in line_strip: process_assignment(line_strip, env); return
    # 3. Output
    if lower_line.startswith("вывод"): process_output(line_strip, env, interpreter); return
    # 4. Input (Warning only)
    if lower_line.startswith("ввод"): process_input(line_strip, env); logger.warning(
        "Команда 'ввод' не работает в веб-режиме."); return
    # 5. Control (утв, дано, надо)
    if lower_line.startswith(("утв", "дано", "надо")):
        if process_control_command(line_strip, env): return
    # 6. Flow (стоп, выход, пауза)
    if lower_line == "стоп": raise KumirExecutionError("Выполнение прервано командой 'стоп'.")
    if lower_line == "выход": raise KumirExecutionError("Выход")
    if lower_line == "пауза": logger.info("Команда 'пауза' проигнорирована."); return
    # 7. Robot Commands
    # === FIX: Need to catch RobotError here if raised by process_robot_command ===
    try:
        if process_robot_command(line_strip, robot): return
    except RobotError as e:  # Catch specific robot errors (e.g., wall collision)
        logger.error(f"Ошибка робота: {e} при выполнении '{line_strip}'")
        raise KumirExecutionError(f"Ошибка робота: {e}")  # Re-raise as execution error
    # =========================================================================
    # 8. Algorithm Call
    if interpreter and process_algorithm_call(line_strip, env, robot, interpreter): return
    # Unknown
    logger.error(f"Неизвестная команда: {line_strip}")
    raise KumirExecutionError(f"Неизвестная команда: {line_strip}")