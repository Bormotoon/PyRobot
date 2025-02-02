# kumir_interpreter.py

import math
import re

from kumir_interpreter.robot_interpreter import KumirInterpreter

# ---------------------------------------------------------------------
# Константы и настройки
# ---------------------------------------------------------------------

# Зарезервированные ключевые слова (неполный, но включающий основные из документации)
RESERVED_KEYWORDS = {"алг", "нач", "кон", "исп", "кон_исп", "дано", "надо", "арг", "рез", "аргрез", "знач", "цел",
    "вещ", "лог", "сим", "лит", "таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб", "и", "или", "не", "да", "нет",
    "утв", "выход", "ввод", "вывод", "нс", "если", "то", "иначе", "все", "выбор", "при", "нц", "кц", "кц_при", "раз",
    "пока", "для", "от", "до", "шаг"}

# Допустимые типы величин
ALLOWED_TYPES = {"цел", "вещ", "лог", "сим", "лит"}

# Максимальные значения для целых
МАКСЦЕЛ = 2147483647


# ---------------------------------------------------------------------
# Вспомогательные функции для работы с именами и константами
# ---------------------------------------------------------------------

def is_valid_identifier(identifier, var_type):
    """
    Проверяет, что identifier соответствует требованиям:
    - Identifier состоит из одного или нескольких слов, разделённых пробелами.
    - Первое слово не начинается с цифры.
    - Ни одно из слов (за исключением допустимого встраивания "не" в логических величинах)
      не является зарезервированным ключевым словом.
    """
    words = identifier.strip().split()
    if not words:
        return False
    # Проверяем первое слово: не должно начинаться с цифры
    if re.match(r'^\d', words[0]):
        return False
    for word in words:
        # Для логических величин допускается, что слово "не" встречается, если не первое
        if word.lower() in RESERVED_KEYWORDS:
            if var_type == "лог" and word.lower() == "не" and word != words[0]:
                continue
            return False
        # Каждое слово должно состоять только из букв (латинских или кириллических), цифр, @ и _
        if not re.match(r'^[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*$', word):
            return False
    return True


def convert_hex_constants(expr):
    """
    Заменяет все вхождения шестнадцатеричных констант, начинающихся с '$',
    на строку, понятную Python (например, '$100' -> '0x100').
    """
    return re.sub(r'\$(?P<hex>[A-Fa-f0-9]+)', r'0x\g<hex>', expr)


def safe_eval(expr, eval_env):
    """
    Вычисляет выражение с использованием безопасного окружения.
    Подставляет шестнадцатеричные константы.
    """
    expr = convert_hex_constants(expr)
    safe_globals = {"__builtins__": None, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt, "int": int,
        "float": float, }
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    """
    Строит словарь для вычисления выражений, извлекая значения из нашего окружения.
    Наше окружение хранится в виде: env[var_name] = {"type": ..., "value": ...}
    """
    result = {}
    for var, info in env.items():
        result[var] = info.get("value")
    return result


# ---------------------------------------------------------------------
# Обработка объявлений величин
# ---------------------------------------------------------------------

def process_declaration(line, env):
    """
    Обрабатывает строку объявления величин.
    Формат: <тип> [таб] <список идентификаторов, разделённых запятыми>
    Например:
      цел длина, ширина
      вещ таб матрица[1:3, 1:4]   (табличные величины пока не поддерживаем полностью)
      лит мой текст
    После разбора для каждого идентификатора добавляем в env запись:
      env[имя] = {"type": тип, "value": None, "kind": "global"}
    Если имя не соответствует требованиям, генерируется исключение.
    """
    tokens = line.split()
    if not tokens:
        return

    decl_type = tokens[0].lower()
    if decl_type not in ALLOWED_TYPES:
        # Если объявление начинается не с одного из допустимых типов, не обрабатываем его здесь.
        return False

    # Если следующий токен равен "таб", то это табличная величина (пока не реализуем)
    idx = 1
    is_table = False
    if idx < len(tokens) and tokens[idx].lower().startswith("таб"):
        is_table = True
        idx += 1

    # Остальная часть строки считается списком идентификаторов, разделённых запятыми
    rest = " ".join(tokens[idx:])
    identifiers = [ident.strip() for ident in rest.split(",") if ident.strip()]
    if not identifiers:
        raise Exception("Объявление типа без указания имен величин.")

    for ident in identifiers:
        if not is_valid_identifier(ident, decl_type):
            raise Exception(f"Некорректное имя величины: '{ident}'")
        if ident in env:
            raise Exception(f"Величина '{ident}' уже объявлена.")
        env[ident] = {"type": decl_type, "value": None, "kind": "global", "is_table": is_table}
    return True


# ---------------------------------------------------------------------
# Обработка присваиваний и команд вывода
# ---------------------------------------------------------------------

def process_assignment(line, env):
    """
    Обрабатывает присваивание вида: <идентификатор> := <выражение>
    Проверяет, что идентификатор объявлен, вычисляет правую часть и приводит результат к типу величины.
    Обновляет значение переменной в env.
    """
    parts = line.split(":=")
    if len(parts) != 2:
        raise Exception("Неверный синтаксис присваивания.")
    left, right = parts[0].strip(), parts[1].strip()
    if left not in env:
        raise Exception(f"Переменная '{left}' не объявлена.")
    # Вычисляем выражение в безопасном окружении
    eval_env = get_eval_env(env)
    try:
        value = safe_eval(right, eval_env)
    except Exception as e:
        raise Exception(f"Ошибка вычисления выражения '{right}': {e}")
    # Приводим значение к объявленному типу
    target_type = env[left]["type"]
    try:
        if target_type == "цел":
            value = int(value)
            if not (-МАКСЦЕЛ <= value <= МАКСЦЕЛ):
                raise Exception("Значение вне допустимого диапазона для целого типа.")
        elif target_type == "вещ":
            value = float(value)
        elif target_type == "лог":
            # Допускаем bool или строковое представление "да"/"нет"
            if isinstance(value, bool):
                pass
            elif isinstance(value, str):
                low_val = value.lower()
                if low_val == "да":
                    value = True
                elif low_val == "нет":
                    value = False
                else:
                    raise Exception("Неверное логическое значение.")
            else:
                value = bool(value)
        elif target_type in {"сим", "лит"}:
            # Для символьной величины проверяем, что строка длиной 1 (сим) или любую (лит)
            value = str(value)
            if target_type == "сим" and len(value) != 1:
                raise Exception("Символьная величина должна быть ровно один символ.")
        else:
            # Неизвестный тип
            raise Exception(f"Неподдерживаемый тип величины: {target_type}")
    except Exception as e:
        raise Exception(f"Ошибка приведения значения для переменной '{left}': {e}")
    env[left]["value"] = value


def process_output(line, env):
    """
    Обрабатывает команду вывода. Ожидается, что строка начинается с 'вывод'.
    Вычисляет выражение после слова 'вывод' и выводит результат.
    """
    # Удаляем ключевое слово "вывод"
    content = line[5:].strip()
    eval_env = get_eval_env(env)
    try:
        value = safe_eval(content, eval_env)
    except Exception:
        value = content
    print(value)


# ---------------------------------------------------------------------
# Функция для делегирования команд исполнителю "Робот"
# ---------------------------------------------------------------------

def process_robot_command(line, robot):
    """
    Если строка соответствует одной из команд управления роботом, вызывает соответствующую функцию.
    Поддерживаются команды: влево, вправо, вверх, вниз, закрасить.
    """
    cmd = line.lower().strip()
    robot_commands = {"влево": robot.go_left, "вправо": robot.go_right, "вверх": robot.go_up, "вниз": robot.go_down,
        "закрасить": robot.do_paint}
    if cmd in robot_commands:
        try:
            robot_commands[cmd]()
        except Exception as e:
            print(f"Ошибка при выполнении команды '{line}': {e}")
        return True
    return False


# ---------------------------------------------------------------------
# Предварительная обработка и разбиение на строки/алгоритмы
# ---------------------------------------------------------------------

def preprocess_code(code):
    """
    Разбивает исходный код на строки, удаляет комментарии (строки, начинающиеся с '|' или '#')
    и объединяет несколько команд в одну с помощью точки с запятой.
    """
    lines = []
    for line in code.splitlines():
        # Удаляем комментарии: если встречается символ '|' или '#' – отбрасываем всё после него.
        if '|' in line:
            line = line.split('|')[0]
        if '#' in line:
            line = line.split('#')[0]
        line = line.strip()
        if not line:
            continue
        # Разбиваем по точке с запятой
        parts = [part.strip() for part in line.split(';') if part.strip()]
        lines.extend(parts)
    return lines


def separate_sections(lines):
    """
    Разделяет входные строки на вступление (до первого алгоритма) и алгоритмы.
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
            in_algo = False  # После "кон" алгоритм считается завершённым
        else:
            if current_algo is None:
                # До первого алгоритма – вступление
                introduction.append(line)
            else:
                if in_algo:
                    current_algo["body"].append(line)
                else:
                    # Строки между "алг" и "нач" считаем частью заголовка
                    current_algo["header"] += " " + line
    if current_algo is not None:
        algorithms.append(current_algo)
    return introduction, algorithms


def parse_algorithm_header(header_line):
    """
    Разбирает заголовок алгоритма.
    Из строки, начинающейся с "алг", извлекается имя алгоритма (если задано) и описание параметров.
    Пример:
      алг тест (рез цел m, n, лит т, арг вещ y)
    Возвращает словарь с ключами:
      - "raw": исходное содержимое заголовка (без "алг")
      - "name": имя алгоритма (если есть)
      - "params": список параметров в виде кортежей (mode, type, name)
    """
    header_line = header_line.strip()
    if header_line.lower().startswith("алг"):
        header_line = header_line[3:].strip()  # удаляем "алг"
    params = []
    name_part = header_line
    if "(" in header_line:
        parts = header_line.split("(", 1)
        name_part = parts[0].strip()
        params_part = parts[1].rsplit(")", 1)[0]
        # Простой разбор параметров (разделён пробелами)
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


# ---------------------------------------------------------------------
# Функция исполнения одной строки кода (вступление или тело алгоритма)
# ---------------------------------------------------------------------

def execute_line(line, env, robot):
    """
    Исполняет одну строку кода.
    Поддерживаются:
      - Объявления величин (начинаются с цел, вещ, лог, сим, лит)
      - Присваивания (оператор ":=")
      - Команда вывода (начинается со слова "вывод")
      - Команды управления роботом (влево, вправо, вверх, вниз, закрасить)
    Для неизвестных строк выводится сообщение.
    """
    lower_line = line.lower()
    # Объявление величин
    for t in ALLOWED_TYPES:
        if lower_line.startswith(t):
            # Попытка обработки объявления
            try:
                process_declaration(line, env)
            except Exception as e:
                print(f"Ошибка объявления: {e}")
            return

    # Присваивание
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

    # Команды управления Роботом
    if process_robot_command(line, robot):
        return

    # Если строка не распознана, сообщаем об этом.
    print(f"Неизвестная команда: {line}")


# ---------------------------------------------------------------------
# Класс интерпретатора языка Кумир
# ---------------------------------------------------------------------

class KumirLanguageInterpreter:
    def __init__(self, code):
        self.code = code
        # Окружение для переменных: словарь вида { var_name: {"type": ..., "value": ..., "kind": ..., "is_table": ...} }
        self.env = {}
        self.algorithms = {}  # Словарь для вспомогательных алгоритмов по имени
        self.main_algorithm = None
        # Создаем экземпляр исполнителя "Робот"
        self.robot = KumirInterpreter()

    def parse(self):
        """
        Обрабатывает исходный код: предварительная обработка, разделение на вступление и алгоритмы,
        разбор заголовков алгоритмов.
        """
        lines = preprocess_code(self.code)
        introduction, algo_sections = separate_sections(lines)
        self.introduction = introduction
        self.algo_sections = algo_sections

        if algo_sections:
            # Первый алгоритм считается основным
            self.main_algorithm = algo_sections[0]
            header_info = parse_algorithm_header(self.main_algorithm["header"])
            self.main_algorithm["header_info"] = header_info
            # Остальные алгоритмы сохраняем в таблице, если они имеют имя
            for alg in algo_sections[1:]:
                info = parse_algorithm_header(alg["header"])
                alg["header_info"] = info
                if info["name"]:
                    self.algorithms[info["name"]] = alg
        else:
            raise Exception("Нет алгоритмов в программе.")

    def execute_introduction(self):
        """Исполняет вступление (команды до первого алгоритма)."""
        for line in self.introduction:
            execute_line(line, self.env, self.robot)

    def execute_algorithm(self, algorithm):
        """Исполняет тело алгоритма (строки между 'нач' и 'кон')."""
        for line in algorithm["body"]:
            execute_line(line, self.env, self.robot)

    def interpret(self):
        """Полная интерпретация программы: парсинг, исполнение вступления и основного алгоритма."""
        self.parse()
        self.execute_introduction()
        print("Выполнение основного алгоритма:")
        self.execute_algorithm(self.main_algorithm)
        # Результат – обновленное окружение и текущая позиция робота.
        return {"env": self.env, "robot": self.robot.robot_pos}


# ---------------------------------------------------------------------
# Пример использования
# ---------------------------------------------------------------------

if __name__ == "__main__":
    sample_code = r'''
    | Это вступление
    цел длина, ширина, лог условие, лит мой текст
    длина := 10
    ширина := 15
    условие := да
    мой текст := "Пример текста"
    вывод "Вступление выполнено. Текст: " + мой текст

    | Это основной алгоритм (без имени)
    алг
    нач
      вывод "Площадь равна: " + (длина * ширина)
      влево
      вправо
      вверх
      вниз
      закрасить
    кон

    | Это вспомогательный алгоритм (пока не вызывается)
    алг цел площадь
    нач
      знач := длина * ширина
      вывод "Вспомогательный алгоритм: Площадь = " + знач
    кон
    '''
    interpreter = KumirLanguageInterpreter(sample_code)
    result = interpreter.interpret()
    print("Результат:", result)
