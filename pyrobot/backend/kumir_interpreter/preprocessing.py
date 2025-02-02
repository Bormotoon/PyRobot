# preprocessing.py

def preprocess_code(code):
    """
    Разбивает исходный код на строки, удаляет комментарии (начинающиеся с '|' или '#')
    и разбивает строки по точке с запятой.
    """
    lines = []
    for line in code.splitlines():
        if '|' in line:
            line = line.split('|')[0]
        if '#' in line:
            line = line.split('#')[0]
        line = line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(';') if part.strip()]
        lines.extend(parts)
    return lines


def separate_sections(lines):
    """
    Разделяет строки кода на вступление (до первого алгоритма) и алгоритмы.
    Алгоритм определяется строкой, начинающейся с "алг".
    """
    introduction = []
    algorithms = []
    current_algo = None
    in_algo = False

    for line in lines:
        lower_line = line.lower()
        if lower_line.startswith("алг"):
            if current_algo is not None:
                algorithms.append(current_algo)
            current_algo = {"header": line, "body": []}
            in_algo = False
        elif lower_line == "нач":
            if current_algo is None:
                raise Exception("Ошибка: 'нач' без 'алг'")
            in_algo = True
        elif lower_line == "кон":
            if current_algo is None or not in_algo:
                raise Exception("Ошибка: 'кон' без 'нач'")
            in_algo = False
        else:
            if current_algo is None:
                introduction.append(line)
            else:
                if in_algo:
                    current_algo["body"].append(line)
                else:
                    current_algo["header"] += " " + line
    if current_algo is not None:
        algorithms.append(current_algo)
    return introduction, algorithms


def parse_algorithm_header(header_line):
    """
    Разбирает заголовок алгоритма, выделяя имя алгоритма и описание параметров (если есть).
    Пример: алг тест (рез цел m, n, лит т, арг вещ y)
    Возвращает словарь с ключами:
      - "raw": исходный заголовок (без "алг")
      - "name": имя алгоритма (если задано)
      - "params": список параметров в виде кортежей (mode, type, name)
    """
    header_line = header_line.strip()
    if header_line.lower().startswith("алг"):
        header_line = header_line[3:].strip()
    params = []
    name_part = header_line
    if "(" in header_line:
        parts = header_line.split("(", 1)
        name_part = parts[0].strip()
        params_part = parts[1].rsplit(")", 1)[0]
        tokens = params_part.split()
        mode = "арг"  # режим по умолчанию
        current_type = None
        current_names = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in ["арг", "рез", "аргрез"]:
                if current_names and current_type is not None:
                    for n in current_names:
                        params.append((mode, current_type, n))
                    current_names = []
                mode = token
                i += 1
                if i < len(tokens):
                    current_type = tokens[i]
                    i += 1
                    while i < len(tokens) and tokens[i] not in ["арг", "рез", "аргрез"]:
                        name = tokens[i].strip(",")
                        current_names.append(name)
                        i += 1
                else:
                    break
            else:
                if current_type is None:
                    current_type = token
                else:
                    current_names.append(token.strip(","))
                i += 1
        if current_names and current_type is not None:
            for n in current_names:
                params.append((mode, current_type, n))
    header_info = {"raw": header_line, "name": name_part if name_part else None, "params": params}
    return header_info
