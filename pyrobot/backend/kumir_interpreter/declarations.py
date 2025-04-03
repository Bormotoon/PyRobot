# FILE START: declarations.py
"""
Модуль declarations.py
@description Обработка объявлений переменных, присваиваний, ввода/вывода.
"""
import logging
import math
import re
import sys

# --->>> ИМПОРТ is_valid_identifier ИЗ НУЖНОГО МЕСТА <<<---
from .identifiers import is_valid_identifier
from .safe_eval import safe_eval, KumirEvalError
from .robot_state import SimulatedRobot, RobotError
from .file_functions import get_default_input, get_default_output
# --->>> ИМПОРТ ALLOWED_TYPES из constants <<<---
from .constants import ALLOWED_TYPES, MAX_INT

logger = logging.getLogger('KumirDeclarations')


# ALLOWED_TYPES и MAX_INT теперь импортируются из constants
# ALLOWED_TYPES = {"цел", "вещ", "лог", "сим", "лит"}
# MAX_INT = 2147483647


class DeclarationError(Exception):
    pass


class AssignmentError(Exception):
    pass


class InputOutputError(Exception):
    pass


class KumirInputRequiredError(Exception):
    def __init__(self, var_name, prompt, target_type):
        self.var_name = var_name;
        self.prompt = prompt;
        self.target_type = target_type
        message = f"Требуется ввод для переменной '{var_name}' (тип: {target_type}). Подсказка: {prompt}"
        super().__init__(message)


# Функция _validate_and_convert_value остается без изменений
def _validate_and_convert_value(value, target_type, var_name_for_error):
    # ... (код без изменений) ...
    try:
        if target_type == "цел":
            converted_value = int(value);
            if not (-MAX_INT - 1 <= converted_value <= MAX_INT): raise ValueError(
                f"Значение {converted_value} выходит за допустимый диапазон для типа 'цел'.")
        elif target_type == "вещ":
            converted_value = float(value);
            if not math.isfinite(converted_value): raise ValueError(
                f"Значение {converted_value} не является конечным числом для типа 'вещ'.")
        elif target_type == "лог":
            if isinstance(value, bool):
                converted_value = value
            elif isinstance(value, str):
                low_val = value.lower().strip()
                if low_val == "да":
                    converted_value = True
                elif low_val == "нет":
                    converted_value = False
                else:
                    try:
                        num_val = float(value); converted_value = (num_val != 0)
                    except ValueError:
                        raise ValueError(
                            f"Недопустимое логическое значение: '{value}'. Ожидалось 'да', 'нет' или число.")
            elif isinstance(value, (int, float)):
                converted_value = (value != 0)
            else:
                converted_value = bool(value)
        elif target_type == "сим":
            converted_value = str(value);
            if len(converted_value) != 1: raise ValueError("Значение для типа 'сим' должно быть ровно одним символом.")
        elif target_type == "лит":
            converted_value = str(value)
        else:
            raise TypeError(f"Неподдерживаемый целевой тип: {target_type}")
        return converted_value
    except (ValueError, TypeError) as e:
        raise AssignmentError(
            f"Ошибка преобразования значения '{value}' к типу '{target_type}' для переменной '{var_name_for_error}': {e}")
    except Exception as e:
        raise AssignmentError(f"Неожиданная ошибка при преобразовании значения для '{var_name_for_error}': {e}")


def parse_dimensions(dim_spec_str):
    """
    Парсит строку размерностей таблицы вида "нач1:кон1, нач2:кон2, ...".
    Возвращает список кортежей [(нач1, кон1), (нач2, кон2), ...].
    """
    dimensions = []
    if not dim_spec_str:
        return dimensions  # Пустая спецификация

    dim_parts = [part.strip() for part in dim_spec_str.split(',') if part.strip()]
    for i, part in enumerate(dim_parts):
        match = re.match(r"^(-?\d+):(-?\d+)$", part)
        if not match:
            raise DeclarationError(
                f"Некорректный формат размерности #{i + 1}: '{part}'. Ожидался формат 'начало:конец'.")
        try:
            start_bound = int(match.group(1))
            end_bound = int(match.group(2))
            # В Кумире конец диапазона включается. Проверка start <= end не обязательна,
            # но может быть полезна для отлова ошибок.
            # if start_bound > end_bound:
            #     logger.warning(f"Dimension #{i+1} ('{part}') has start > end.")
            dimensions.append((start_bound, end_bound))
        except ValueError:
            # Это не должно произойти из-за regex, но на всякий случай
            raise DeclarationError(f"Границы размерности #{i + 1} ('{part}') не являются целыми числами.")
    return dimensions


def process_declaration(line, env):
    """
    Обрабатывает строку объявления переменной или таблицы, включая парсинг размерностей.
    """
    logger.debug(f"Processing declaration: '{line}'")
    tokens = line.split()
    if not tokens: raise DeclarationError("Пустая строка объявления.")

    decl_type_raw = tokens[0].lower()
    if decl_type_raw not in ALLOWED_TYPES: raise DeclarationError(f"Неизвестный тип переменной: '{tokens[0]}'")

    idx = 1
    is_table = False
    table_type_suffix = ""
    if idx < len(tokens) and tokens[idx].lower() == "таб":  # Ожидаем "таб" как отдельное слово
        is_table = True
        table_type_suffix = "таб"  # Например, целтаб
        idx += 1
        logger.debug(f"Declaration is for a table (Type: {decl_type_raw}).")

    full_type = decl_type_raw + table_type_suffix  # Собираем полный тип (цел, целтаб, ...)

    rest_of_line = " ".join(tokens[idx:])
    if not rest_of_line: raise DeclarationError(f"Отсутствуют имена переменных после типа '{tokens[0]}'.")

    # Разделяем по запятой, т.к. размерности теперь внутри скобок имени
    identifiers_raw = [ident.strip() for ident in rest_of_line.split(",") if ident.strip()]
    if not identifiers_raw: raise DeclarationError(f"Не найдены имена переменных в строке объявления: '{line}'")

    for ident_raw in identifiers_raw:
        var_name = ident_raw
        dimension_bounds = None  # Будет список кортежей [(start, end), ...]

        if is_table:
            # Ищем квадратные скобки для размерностей
            dim_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", ident_raw)
            if dim_match:
                var_name = dim_match.group(1).strip()
                dim_spec_str = dim_match.group(2).strip()
                try:
                    dimension_bounds = parse_dimensions(dim_spec_str)
                    logger.debug(f"Parsed dimensions for table '{var_name}': {dimension_bounds}")
                except DeclarationError as dim_err:
                    # Добавляем контекст к ошибке парсинга размерностей
                    raise DeclarationError(f"Ошибка в размерностях таблицы '{var_name}': {dim_err}")
            else:
                # Таблица объявлена без скобок - динамическая или ошибка?
                # В стандартном Кумире размерности обязательны при объявлении.
                # Считаем это ошибкой.
                raise DeclarationError(f"Для таблицы '{ident_raw}' не указаны размерности в квадратных скобках.")
        elif "[" in ident_raw or "]" in ident_raw:  # Скобки у не-таблицы
            raise DeclarationError(f"Неожиданные скобки '[]' в объявлении переменной (не таблицы): '{ident_raw}'")

        # Валидация имени
        if not is_valid_identifier(var_name, decl_type_raw):  # Передаем базовый тип
            raise DeclarationError(f"Недопустимое имя переменной/таблицы: '{var_name}'")
        if var_name in env:
            raise DeclarationError(f"Переменная или таблица '{var_name}' уже объявлена.")

        # Добавление в окружение
        env[var_name] = {
            "type": decl_type_raw,  # Базовый тип элемента
            "value": {} if is_table else None,  # Таблицы - словари
            "kind": "global",
            "is_table": is_table,
            "dimensions": dimension_bounds  # Сохраняем распарсенные границы
        }
        kind_str = "таблица" if is_table else "переменная"
        logger.info(
            f"Declared {kind_str} '{var_name}' base type '{decl_type_raw}'{f' with dimensions {dimension_bounds}' if dimension_bounds else ''}.")

    return True


# Функция process_assignment остается без изменений (она уже использует _validate_and_convert_value)
def process_assignment(line, env, robot=None):
    # ... (код без изменений) ...
    logger.debug(f"Processing assignment: '{line}'")
    parts = line.split(":=", 1)
    if len(parts) != 2: raise AssignmentError(
        f"Неверный синтаксис присваивания (отсутствует или несколько ':='): {line}")
    left_raw, right_expr = parts[0].strip(), parts[1].strip()
    if not left_raw: raise AssignmentError("Отсутствует переменная слева от ':='.")
    if not right_expr: raise AssignmentError("Отсутствует выражение справа от ':='.")
    try:
        rhs_value = safe_eval(right_expr, env, robot); logger.debug(
            f"Evaluated RHS '{right_expr}' -> {rhs_value} (type: {type(rhs_value)})")
    except KumirEvalError as e:
        raise KumirEvalError(f"Ошибка вычисления выражения '{right_expr}' в правой части присваивания: {e}")
    except Exception as e:
        logger.error(f"Unexpected error evaluating RHS '{right_expr}': {e}", exc_info=True); raise KumirEvalError(
            f"Неожиданная ошибка вычисления '{right_expr}': {e}")
    table_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", left_raw)
    if table_match:
        var_name = table_match.group(1).strip();
        indices_expr_str = table_match.group(2).strip()
        logger.debug(f"Assignment target is table '{var_name}' with indices expr '{indices_expr_str}'")
        if var_name not in env: raise DeclarationError(f"Таблица '{var_name}' не объявлена.")
        var_info = env[var_name]
        if not var_info.get("is_table"): raise AssignmentError(
            f"Переменная '{var_name}' не является таблицей, но используется с индексами.")
        index_tokens = [token.strip() for token in indices_expr_str.split(",") if token.strip()]
        if not index_tokens: raise AssignmentError(f"Отсутствуют индексы для таблицы '{var_name}'.")
        try:
            indices = []
            for token in index_tokens:
                index_val = safe_eval(token, env, robot)
                try:
                    indices.append(int(index_val))
                except (ValueError, TypeError):
                    raise KumirEvalError(
                        f"Индекс таблицы '{token}' (вычислен как '{index_val}') не является целым числом.")
            indices = tuple(indices);
            logger.debug(f"Evaluated table indices -> {indices}")
            # --->>> ДОБАВИТЬ ПРОВЕРКУ ГРАНИЦ ИНДЕКСОВ <<<---
            if var_info.get("dimensions"):
                if len(indices) != len(var_info["dimensions"]):
                    raise AssignmentError(
                        f"Неверное число индексов ({len(indices)}) для таблицы '{var_name}'. Ожидалось {len(var_info['dimensions'])}.")
                for dim_idx, index_val in enumerate(indices):
                    start_bound, end_bound = var_info["dimensions"][dim_idx]
                    if not (start_bound <= index_val <= end_bound):
                        raise AssignmentError(
                            f"Индекс #{dim_idx + 1} ({index_val}) выходит за границы диапазона [{start_bound}:{end_bound}] для таблицы '{var_name}'.")
        # --- <<< КОНЕЦ ПРОВЕРКИ ГРАНИЦ >>> ---
        except KumirEvalError as e:
            raise KumirEvalError(f"Ошибка вычисления индексов '{indices_expr_str}' для таблицы '{var_name}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error evaluating table indices '{indices_expr_str}': {e}",
                         exc_info=True); raise KumirEvalError(
                f"Неожиданная ошибка вычисления индексов '{indices_expr_str}': {e}")
        target_type = var_info["type"]
        try:
            converted_value = _validate_and_convert_value(rhs_value, target_type, f"{var_name}[{indices_expr_str}]")
        except AssignmentError as e:
            raise AssignmentError(f"Ошибка присваивания элементу {var_name}{list(indices)}: {e}")
        if var_info["value"] is None or not isinstance(var_info["value"], dict): var_info["value"] = {}
        var_info["value"][indices] = converted_value
        logger.info(f"Assigned value {converted_value} to table element {var_name}{list(indices)}.")
    else:
        var_name = left_raw;
        logger.debug(f"Assignment target is simple variable '{var_name}'")
        if var_name not in env: raise DeclarationError(f"Переменная '{var_name}' не объявлена.")
        var_info = env[var_name]
        if var_info.get("is_table"): raise AssignmentError(
            f"Попытка присвоить значение всей таблице '{var_name}' без указания индексов.")
        target_type = var_info["type"];
        converted_value = _validate_and_convert_value(rhs_value, target_type, var_name)
        var_info["value"] = converted_value;
        logger.info(f"Assigned value {converted_value} to variable '{var_name}'.")


# --->>> ИЗМЕНЯЕМ process_output <<<---
def process_output(line, env, robot=None, interpreter=None):
    """
    Обрабатывает команду 'вывод', корректно разделяя аргументы
    с учетом строковых литералов.
    """
    logger.debug(f"Processing output: '{line}'")
    content_part = line[len("вывод"):].strip()
    append_newline = True
    if content_part.lower().endswith(" нс"):
        content_part = content_part[:-len(" нс")].strip()
        append_newline = False
    elif content_part.lower() == "нс":
        content_part = ""
        append_newline = False

    output_str_parts = []
    if content_part:
        # Используем split_respecting_quotes для разделения по запятой
        parts_to_eval = split_respecting_quotes(content_part, delimiter=',', quote_char='"')

        if not parts_to_eval and content_part:  # Если не разделилось, но строка была, возможно, ошибка?
            logger.warning(
                f"Output arguments could not be split by comma (check quotes?): '{content_part}'. Treating as single argument.")
            # Попробуем обработать как один аргумент
            parts_to_eval = [content_part]

        for part_expr in parts_to_eval:
            part_expr_strip = part_expr.strip()  # Убираем пробелы вокруг каждого аргумента
            if not part_expr_strip: continue

            try:
                value = safe_eval(part_expr_strip, env, robot)
                if isinstance(value, bool):
                    output_str_parts.append("да" if value else "нет")
                else:
                    output_str_parts.append(str(value))
                logger.debug(f"Evaluated output part '{part_expr_strip}' -> '{output_str_parts[-1]}'")
            except KumirEvalError as e:
                logger.error(f"Error evaluating output part '{part_expr_strip}': {e}")
                raise InputOutputError(f"Ошибка вычисления выражения '{part_expr_strip}' в команде 'вывод': {e}")
            except Exception as e:
                logger.error(f"Unexpected error evaluating output part '{part_expr_strip}': {e}", exc_info=True)
                raise InputOutputError(f"Неожиданная ошибка в 'вывод' для '{part_expr_strip}': {e}")

    output_str = "".join(output_str_parts)
    if append_newline:
        output_str += "\n"

    if interpreter:
        if not hasattr(interpreter, 'output') or interpreter.output is None: interpreter.output = ""
        interpreter.output += output_str
        output_str_escaped = output_str.replace('\n', '\\n').replace('\r', '\\r')
        logger.info(f"Appended to output buffer: '{output_str_escaped}'")
    else:
        output_stream = get_default_output() or sys.stdout
        try:
            print(output_str, end="", file=output_stream, flush=True); logger.warning(
                "Interpreter context not provided for 'вывод', printed to default output.")
        except Exception as e:
            logger.error(f"Error writing to default output stream: {e}")


# --- <<< КОНЕЦ ИЗМЕНЕНИЙ process_output >>> ---

# Функция process_input остается без изменений (она уже генерирует исключение)
def process_input(line, env):
    # ... (код без изменений) ...
    logger.debug(f"Processing 'ввод': '{line}'. Raising InputRequiredError.")
    var_name = line[len("ввод"):].strip()
    if not var_name: raise InputOutputError("Отсутствует имя переменной после 'ввод'.")
    if not is_valid_identifier(var_name, ""): raise InputOutputError(
        f"Недопустимое имя переменной для ввода: '{var_name}'")
    if var_name not in env: raise DeclarationError(
        f"Переменная '{var_name}' не объявлена перед использованием в 'ввод'.")
    var_info = env[var_name]
    if var_info.get("is_table"): raise InputOutputError(f"Команда 'ввод' не поддерживается для таблиц ('{var_name}').")
    target_type = var_info["type"];
    prompt = f"Введите значение для '{var_name}' (тип: {target_type}): "
    logger.info(f"Input required for variable '{var_name}' (type: {target_type}). Raising exception.")
    raise KumirInputRequiredError(var_name=var_name, prompt=prompt, target_type=target_type)

# FILE END: declarations.py