# FILE START: preprocessing.py
"""
Модуль preprocessing.py
@description Выполняет предварительную обработку исходного кода программы на языке KUMIR.
Удаляет комментарии, пустые строки, обрабатывает точки с запятой как разделители команд
(с учетом строковых литералов) и разделяет код на секции.
"""
import logging
import re
from .constants import RESERVED_KEYWORDS, ALLOWED_TYPES  # Импортируем типы для заголовков
from .identifiers import is_valid_identifier  # Для проверки имен параметров

logger = logging.getLogger('KumirPreprocessing')


def split_respecting_quotes(text, delimiter=';', quote_char='"'):
    """
    Разделяет строку по разделителю, игнорируя разделители внутри кавычек.
    """
    parts = []
    current_part = ""
    in_quotes = False
    escape = False  # Для возможных экранированных кавычек (простая реализация)

    for char in text:
        if char == quote_char and not escape:
            in_quotes = not in_quotes
            current_part += char  # Кавычка остается частью строки
        elif char == delimiter and not in_quotes:
            stripped_part = current_part.strip()
            if stripped_part:  # Добавляем непустые части
                parts.append(stripped_part)
            current_part = ""  # Начинаем новую часть
        else:
            current_part += char

        # Простейшее экранирование: '\' перед кавычкой (в Кумире обычно нет)
        if char == '\\' and not escape:
            escape = True
        else:
            escape = False

    # Добавляем последнюю часть
    stripped_part = current_part.strip()
    if stripped_part:
        parts.append(stripped_part)

    return parts


def preprocess_code(code):
    """
    Выполняет предварительную обработку кода KUMIR:
    - Удаляет комментарии (| или # до конца строки).
    - Удаляет пустые строки и лишние пробелы.
    - Обрабатывает точки с запятой (;) как разделители команд, уважая строки.

    Args:
        code (str): Исходный код программы.

    Returns:
        list: Список строк кода (команд), готовых к дальнейшему разбору.
    """
    processed_lines = []
    logger.debug("Starting code preprocessing...")
    line_number = 0
    for original_line in code.splitlines():
        line_number += 1
        # Удаляем комментарии (все после | или #)
        # Используем re.sub для удаления, т.к. split может быть сложнее с разными комментаторами
        line_no_comments = re.sub(r"[|#].*", "", original_line).strip()

        # Пропускаем полностью пустые строки (после удаления комментариев и пробелов)
        if not line_no_comments:
            continue

        # Используем новую функцию для разделения по ';' с учетом кавычек
        commands = split_respecting_quotes(line_no_comments, delimiter=';', quote_char='"')

        # Логируем, если строка разделилась на несколько команд
        if len(commands) > 1:
            logger.debug(f"Line {line_number} ('{line_no_comments}') split by ';' into: {commands}")
        elif commands:  # Если команда одна, но не пустая
            logger.debug(f"Line {line_number} processed into: ['{commands[0]}']")

        # Добавляем все полученные команды (не пустые) в общий список
        processed_lines.extend(commands)

    logger.info(f"Preprocessing finished. Total commands/lines for parsing: {len(processed_lines)}")
    return processed_lines


# Функция separate_sections остается без изменений
def separate_sections(lines):
    """
    Разделяет предварительно обработанные строки кода на:
    - Вступительную часть (до первого 'алг').
    - Список секций алгоритмов (каждая с заголовком и телом).

    Args:
        lines (list): Список строк кода после preprocess_code.

    Returns:
        tuple: (introduction: list, algorithms: list)
               algorithms - список словарей {'header': str, 'body': list}

    Raises:
        SyntaxError: При структурных ошибках ('нач' без 'алг', 'кон' без 'нач').
    """
    introduction = []
    algorithms = []
    current_algo_dict = None
    in_algo_body = False
    current_line_index = 0

    logger.debug("Separating code into introduction and algorithms...")

    for line in lines:
        current_line_index += 1
        lower_line = line.lower()

        if lower_line.startswith("алг"):
            if current_algo_dict is not None:
                if in_algo_body:
                    raise SyntaxError(
                        f"Структурная ошибка: отсутствует 'кон' для алгоритма, начинающегося с '{current_algo_dict['header']}' перед строкой {current_line_index}.")
                logger.debug(
                    f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
                algorithms.append(current_algo_dict)
            current_algo_dict = {"header": line, "body": []}
            in_algo_body = False
            logger.debug(f"Detected algorithm start at line {current_line_index}: '{line}'")
        elif lower_line == "нач":
            if current_algo_dict is None:
                raise SyntaxError(f"Структурная ошибка: 'нач' найден вне блока 'алг' (строка {current_line_index}).")
            if in_algo_body:
                raise SyntaxError(
                    f"Структурная ошибка: повторный 'нач' внутри блока алгоритма (строка {current_line_index}).")
            in_algo_body = True
            logger.debug(
                f"Entering algorithm body ('нач') for '{current_algo_dict['header']}' at line {current_line_index}.")
        elif lower_line == "кон":
            if current_algo_dict is None or not in_algo_body:
                raise SyntaxError(
                    f"Структурная ошибка: 'кон' найден без соответствующего 'нач' или вне блока 'алг' (строка {current_line_index}).")
            in_algo_body = False
            logger.debug(
                f"Exiting algorithm body ('кон') for '{current_algo_dict['header']}' at line {current_line_index}.")
            logger.debug(
                f"Completed algorithm '{current_algo_dict.get('header', '')}', body lines: {len(current_algo_dict.get('body', []))}")
            algorithms.append(current_algo_dict)
            current_algo_dict = None
        else:
            if current_algo_dict is None:
                introduction.append(line)
            else:
                if in_algo_body:
                    current_algo_dict["body"].append(line)
                else:  # Строка между 'алг' и 'нач' - часть заголовка
                    # НЕ объединяем через пробел, т.к. preprocess_code уже разделил команды
                    # Если строка не пустая, это ошибка синтаксиса заголовка или непредвиденная команда
                    if line.strip():  # Проверяем, что строка не просто пробелы
                        logger.warning(
                            f"Unexpected non-empty line '{line}' between 'алг' and 'нач' at index {current_line_index}. Treating as part of header (may cause parsing issues).")
                        # Пока добавим к заголовку, но это может быть неверно
                        current_algo_dict["header"] += " " + line
                    # Правильнее было бы вызвать ошибку, если заголовок не может быть многострочным
                    # raise SyntaxError(f"Неожиданная строка '{line}' между 'алг' и 'нач' (строка {current_line_index}).")

    if current_algo_dict is not None:
        if in_algo_body:
            raise SyntaxError(
                f"Структурная ошибка: отсутствует 'кон' для последнего алгоритма, начинающегося с '{current_algo_dict['header']}'.")
        logger.warning(
            f"Last 'алг' block ('{current_algo_dict['header']}') might be incomplete (missing 'нач'/'кон' or empty body).")
        algorithms.append(current_algo_dict)

    logger.info(
        f"Section separation complete. Introduction lines: {len(introduction)}, Algorithms found: {len(algorithms)}")
    return introduction, algorithms


def parse_algorithm_header(header_line):
    """
    Разбирает строку заголовка алгоритма ('алг имя [(параметры)]')
    на имя и список параметров с режимами и типами.

    Args:
        header_line (str): Полная строка заголовка (включая 'алг').

    Returns:
        dict: Словарь с ключами:
              'raw' (str): Исходная строка заголовка (без 'алг').
              'name' (str | None): Имя алгоритма или None.
              'params' (list): Список кортежей параметров (mode, type, name).
                                mode: 'арг', 'рез', 'аргрез', 'знач'
                                type: 'цел', 'вещ', 'лог', 'сим', 'лит', 'целтаб', ...
                                name: имя параметра

    Raises:
        ValueError: при синтаксических ошибках в заголовке или параметрах.
    """
    logger.debug(f"Parsing algorithm header: '{header_line}'")
    header_strip = header_line.strip()
    if not header_strip.lower().startswith("алг"):
        raise ValueError(f"Заголовок '{header_line}' не начинается с 'алг'.")

    content = header_strip[len("алг"):].strip()
    raw_header_content = content

    params = []
    name_part = content
    params_part_str = None

    # Ищем скобки для параметров
    param_match = re.match(r"^(.*?)\s*\((.*)\)\s*$", content)
    if param_match:
        name_part = param_match.group(1).strip()
        params_part_str = param_match.group(2).strip()
        logger.debug(f"Header has name='{name_part}', params='{params_part_str}'")
    elif "(" in content or ")" in content:
        # Непарные или некорректно расположенные скобки
        raise ValueError(f"Некорректный формат скобок в заголовке: '{content}'")
    else:  # Скобок нет
        name_part = content.strip()
        logger.debug(f"Header has name='{name_part}', no parameters.")

    # Проверяем имя алгоритма (если оно есть)
    algo_name = name_part if name_part else None
    if algo_name and not is_valid_identifier(algo_name, ""):
        # Имя может быть составным, is_valid_identifier это проверяет
        raise ValueError(f"Недопустимое имя алгоритма: '{algo_name}'")
    elif not algo_name:
        logger.debug("Algorithm is unnamed (likely the main algorithm).")

    # Парсим параметры, если они есть
    if params_part_str:
        # Используем регулярное выражение для разбора сегментов параметров
        # Сегмент: [режим] тип имя1 [, имя2] ...
        # Режимы: арг, рез, аргрез, знач
        # Типы: цел, вещ, лог, сим, лит, целтаб, вещтаб, ...
        # Имена: валидные идентификаторы
        # Разделитель сегментов - точка с запятой ';'
        segments = [seg.strip() for seg in params_part_str.split(';') if seg.strip()]
        if not segments:
            # Скобки есть, но внутри пусто или только ';'
            logger.warning(f"Parameter brackets exist but contain no valid parameter segments: '({params_part_str})'")

        for segment in segments:
            logger.debug(f"Parsing parameter segment: '{segment}'")
            segment_parts = segment.split()  # Разделяем по пробелам

            if not segment_parts: continue  # Пропускаем пустые сегменты

            current_mode = "арг"  # Режим по умолчанию
            part_index = 0

            # Проверяем наличие режима в начале сегмента
            first_word_lower = segment_parts[0].lower()
            if first_word_lower in ["арг", "рез", "аргрез", "знач"]:
                current_mode = first_word_lower
                part_index += 1
                logger.debug(f"Mode detected: '{current_mode}'")
            elif first_word_lower in ALLOWED_TYPES or first_word_lower.endswith("таб"):
                # Если первое слово похоже на тип, значит режим по умолчанию 'арг'
                logger.debug(f"Mode not specified, defaulting to 'арг'.")
            else:
                # Первое слово не режим и не тип - ошибка
                raise ValueError(
                    f"Неожиданное начало сегмента параметра: '{segment_parts[0]}' в '{segment}'. Ожидался режим или тип.")

            # Проверяем наличие типа
            if part_index >= len(segment_parts):
                raise ValueError(f"Отсутствует тип параметра в сегменте: '{segment}'")

            current_type = segment_parts[part_index].lower()
            # TODO: Более строгая валидация типов (например, что 'таб' идет после базового типа)
            is_table_type = current_type.endswith("таб")
            base_type = current_type[:-3] if is_table_type else current_type

            if base_type not in ALLOWED_TYPES:
                raise ValueError(f"Неизвестный тип параметра: '{current_type}' в сегменте '{segment}'")
            logger.debug(f"Type detected: '{current_type}' (table={is_table_type})")
            part_index += 1

            # Имена переменных (разделены запятыми)
            if part_index >= len(segment_parts):
                raise ValueError(f"Отсутствуют имена параметров после типа '{current_type}' в сегменте: '{segment}'")

            # Собираем остаток строки и разделяем по запятым
            names_str = " ".join(segment_parts[part_index:])
            param_names = [name.strip() for name in names_str.split(',') if name.strip()]

            if not param_names:
                raise ValueError(f"Не найдены имена параметров в сегменте: '{segment}'")

            for p_name in param_names:
                # Используем is_valid_identifier для проверки имени
                # Передаем current_type, чтобы разрешить 'не' для лог, если это релевантно для имен
                if not is_valid_identifier(p_name, current_type):
                    raise ValueError(f"Недопустимое имя параметра: '{p_name}' в сегменте '{segment}'")
                # Добавляем параметр в список
                params.append((current_mode, current_type, p_name))
                logger.debug(f"Parsed param: mode={current_mode}, type={current_type}, name={p_name}")

    # Собираем результат
    header_info = {
        "raw": raw_header_content,
        "name": algo_name,
        "params": params
    }
    logger.debug(f"Header parsed successfully: Name='{algo_name}', Params Count={len(params)}")
    return header_info

# FILE END: preprocessing.py