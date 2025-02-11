import math
import re

# Импорт класса интерпретатора робота из подмодуля kumir_interpreter.robot_interpreter
from .kumir_interpreter.robot_interpreter import KumirInterpreter

# ---------------------------------------------------------------------
# Константы и настройки
# ---------------------------------------------------------------------

# RESERVED_KEYWORDS – множество зарезервированных ключевых слов (неполный список основных ключевых слов из документации)
RESERVED_KEYWORDS = {"алг", "нач", "кон", "исп", "кон_исп", "дано", "надо", "арг", "рез", "аргрез", "знач", "цел",
    "вещ", "лог", "сим", "лит", "таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб", "и", "или", "не", "да", "нет",
    "утв", "выход", "ввод", "вывод", "нс", "если", "то", "иначе", "все", "выбор", "при", "нц", "кц", "кц_при", "раз",
    "пока", "для", "от", "до", "шаг"}

# ALLOWED_TYPES – множество разрешённых типов переменных в языке KUMIR
ALLOWED_TYPES = {"цел", "вещ", "лог", "сим", "лит"}

# MAX_INT – максимальное значение целого числа, как определено в документации
MAX_INT = 2147483647
# Для обратной совместимости оставляем псевдоним:
МАКСЦЕЛ = MAX_INT


# ---------------------------------------------------------------------
# Вспомогательные функции для работы с именами и константами
# ---------------------------------------------------------------------

def is_valid_identifier(identifier, var_type):
    """
    Проверяет, соответствует ли идентификатор требованиям:
      - Состоит из одного или нескольких слов, разделённых пробелами.
      - Первое слово не начинается с цифры.
      - Ни одно слово (за исключением допустимого случая для логических переменных)
        не является зарезервированным ключевым словом.
      - Допускаются только буквы (латинские и кириллические), цифры, символы "@" и "_".

    Параметры:
      identifier (str): Идентификатор для проверки.
      var_type (str): Тип переменной (например, "цел", "лог" и т.д.) для дополнительной проверки.

    Возвращаемое значение:
      bool: True, если идентификатор корректен, иначе False.
    """
    words = identifier.strip().split()
    if not words:
        return False
    if re.match(r'^\d', words[0]):  # Первое слово не должно начинаться с цифры
        return False
    for word in words:
        # Для логических переменных слово "не" допускается, если оно не первое
        if word.lower() in RESERVED_KEYWORDS:
            if var_type == "лог" and word.lower() == "не" and word != words[0]:
                continue
            return False
        # Проверяем, что слово соответствует шаблону: первая буква (латинская/кириллическая, @ или _)
        # и далее могут идти буквы, цифры, @ или _
        if not re.match(r'^[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*$', word):
            return False
    return True


def convert_hex_constants(expr):
    """
    Заменяет шестнадцатеричные константы, начинающиеся с символа '$',
    на формат, совместимый с Python (например, '$100' -> '0x100').

    Параметры:
      expr (str): Выражение, содержащее шестнадцатеричные константы.

    Возвращаемое значение:
      str: Измененное выражение с замененными шестнадцатеричными константами.
    """
    return re.sub(r'\$(?P<hex>[A-Fa-f0-9]+)', r'0x\g<hex>', expr)


def safe_eval(expr, eval_env):
    """
    Вычисляет выражение в безопасном окружении.

    Функция сначала заменяет шестнадцатеричные константы в выражении на формат Python,
    затем вызывает встроенную функцию eval() с ограниченным набором глобальных переменных (без доступа к __builtins__).

    Параметры:
      expr (str): Выражение для вычисления.
      eval_env (dict): Окружение, содержащее значения переменных, доступных для вычисления.

    Возвращаемое значение:
      Результат вычисления выражения.
    """
    expr = convert_hex_constants(expr)
    safe_globals = {"__builtins__": None, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt, "int": int,
        "float": float}
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    """
    Формирует словарь для вычисления выражений на основе текущего окружения переменных.

    Окружение хранится как: env[var_name] = {"type": ..., "value": ...}.

    Параметры:
      env (dict): Окружение переменных.

    Возвращаемое значение:
      dict: Словарь, где ключи – имена переменных, а значения – их текущие значения.
    """
    result = {}
    for var, info in env.items():
        result[var] = info.get("value")
    return result


# ---------------------------------------------------------------------
# Обработка объявлений переменных
# ---------------------------------------------------------------------

def process_declaration(line, env):
    """
    Обрабатывает строку объявления переменных.

    Формат объявления:
      <тип> [таб] <список идентификаторов, разделенных запятыми>
    Пример:
      цел длина, ширина, лог условие, лит мой текст
    Если переменная является таблицей, ее значение инициализируется как пустой словарь.

    Параметры:
      line (str): Строка объявления.
      env (dict): Окружение переменных, куда будут добавлены новые переменные.

    Возвращаемое значение:
      bool: True, если объявление успешно обработано, иначе False.

    Исключения:
      Генерирует Exception, если список переменных пуст, имя переменной некорректно,
      или переменная уже объявлена.
    """
    tokens = line.split()
    if not tokens:
        return False

    decl_type = tokens[0].lower()
    if decl_type not in ALLOWED_TYPES:
        return False

    idx = 1
    is_table = False
    # Если следующий токен начинается с "таб", объявляем таблицу
    if idx < len(tokens) and tokens[idx].lower().startswith("таб"):
        is_table = True
        idx += 1

    rest = " ".join(tokens[idx:])
    # Разделяем имена переменных по запятой
    identifiers = [ident.strip() for ident in rest.split(",") if ident.strip()]
    if not identifiers:
        raise Exception("Declaration without any variable names.")

    for ident in identifiers:
        if not is_valid_identifier(ident, decl_type):
            raise Exception(f"Invalid variable name: '{ident}'")
        if ident in env:
            raise Exception(f"Variable '{ident}' already declared.")
        # Добавляем переменную в окружение с заданным типом и начальным значением (пустой словарь для таблиц)
        env[ident] = {"type": decl_type, "value": {} if is_table else None, "kind": "global", "is_table": is_table}
    return True


# ---------------------------------------------------------------------
# Обработка присваиваний и команд вывода
# ---------------------------------------------------------------------

def process_assignment(line, env):
    """
    Обрабатывает присваивание вида: VARIABLE := EXPRESSION.

    Проверяет, что переменная объявлена, вычисляет выражение и преобразует результат к типу переменной.
    Обновляет значение переменной в окружении env.

    Параметры:
      line (str): Строка присваивания.
      env (dict): Окружение переменных.

    Исключения:
      Генерирует Exception при ошибках синтаксиса, вычисления выражения или преобразования типа.
    """
    parts = line.split(":=")
    if len(parts) != 2:
        raise Exception("Invalid assignment syntax.")
    left, right = parts[0].strip(), parts[1].strip()

    # Присваивание для элемента таблицы, например, a[i] или b[i,j]
    if "[" in left and left.endswith("]"):
        import re
        match = re.match(
            r"^([A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*(?:\s+[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*)*)\[(.+)\]$",
            left)
        if not match:
            raise Exception(f"Invalid syntax for array element assignment: {left}")
        var_name = match.group(1).strip()
        indices_expr = match.group(2).strip()
        index_tokens = [token.strip() for token in indices_expr.split(",")]
        eval_env = get_eval_env(env)
        try:
            indices = tuple(safe_eval(token, eval_env) for token in index_tokens)
        except Exception as e:
            raise Exception(f"Error evaluating indices in '{left}': {e}")
        if var_name not in env or not env[var_name].get("is_table"):
            raise Exception(f"Variable '{var_name}' is not declared as a table.")
        target_type = env[var_name]["type"]
        try:
            value = safe_eval(right, eval_env)
        except Exception as e:
            raise Exception(f"Error evaluating expression '{right}': {e}")
        try:
            if target_type == "цел":
                value = int(value)
                if not (-MAX_INT <= value <= MAX_INT):
                    raise Exception("Value out of range for integer type.")
            elif target_type == "вещ":
                value = float(value)
            elif target_type == "лог":
                if isinstance(value, bool):
                    pass
                elif isinstance(value, str):
                    low_val = value.lower()
                    if low_val == "да":
                        value = True
                    elif low_val == "нет":
                        value = False
                    else:
                        raise Exception("Invalid logical value.")
                else:
                    value = bool(value)
            elif target_type in {"сим", "лит"}:
                value = str(value)
                if target_type == "сим" and len(value) != 1:
                    raise Exception("Character variable must be exactly one symbol.")
            else:
                raise Exception(f"Unsupported variable type: {target_type}")
        except Exception as e:
            raise Exception(f"Error converting value for '{left}': {e}")
        if env[var_name]["value"] is None:
            env[var_name]["value"] = {}
        # Обновляем значение элемента таблицы
        env[var_name]["value"][indices] = value
        return

    # Присваивание для простой переменной
    if left not in env:
        raise Exception(f"Variable '{left}' is not declared.")
    eval_env = get_eval_env(env)
    try:
        value = safe_eval(right, eval_env)
    except Exception as e:
        raise Exception(f"Error evaluating expression '{right}': {e}")
    target_type = env[left]["type"]
    try:
        if target_type == "цел":
            value = int(value)
            if not (-MAX_INT <= value <= MAX_INT):
                raise Exception("Value out of range for integer type.")
        elif target_type == "вещ":
            value = float(value)
        elif target_type == "лог":
            if isinstance(value, bool):
                pass
            elif isinstance(value, str):
                low_val = value.lower()
                if low_val == "да":
                    value = True
                elif low_val == "нет":
                    value = False
                else:
                    raise Exception("Invalid logical value.")
            else:
                value = bool(value)
        elif target_type in {"сим", "лит"}:
            value = str(value)
            if target_type == "сим" and len(value) != 1:
                raise Exception("Character variable must be exactly one symbol.")
        else:
            raise Exception(f"Unsupported variable type: {target_type}")
    except Exception as e:
        raise Exception(f"Error converting value for variable '{left}': {e}")
    env[left]["value"] = value


def process_output(line, env):
    """
    Обрабатывает команду вывода.

    Формат: вывод expr1, ..., exprN
    Вычисляет выражение после слова "вывод" и выводит результат на экран.

    Параметры:
      line (str): Строка команды вывода.
      env (dict): Окружение переменных.
    """
    # Удаляем слово "вывод" и пробелы в начале
    content = line[5:].strip()
    eval_env = get_eval_env(env)
    try:
        # Пытаемся вычислить выражение
        value = safe_eval(content, eval_env)
    except Exception:
        # Если вычисление не удалось, выводим исходное содержимое
        value = content
    print(value)


# ---------------------------------------------------------------------
# Делегирование команд робота
# ---------------------------------------------------------------------

def process_robot_command(line, robot):
    """
    Если строка соответствует одной из команд управления роботом, вызывает соответствующую функцию.

    Поддерживаются команды:
      влево, вправо, вверх, вниз, закрасить.

    Параметры:
      line (str): Строка команды.
      robot (object): Объект робота, у которого должны быть методы: go_left, go_right, go_up, go_down, do_paint.

    Возвращаемое значение:
      bool: True, если строка распознана как команда робота и выполнена, иначе False.
    """
    cmd = line.lower().strip()
    robot_commands = {"влево": robot.go_left, "вправо": robot.go_right, "вверх": robot.go_up, "вниз": robot.go_down,
        "закрасить": robot.do_paint}
    if cmd in robot_commands:
        try:
            robot_commands[cmd]()
        except Exception as e:
            print(f"Error executing command '{line}': {e}")
        return True
    return False


# ---------------------------------------------------------------------
# Предварительная обработка кода и разделение на секции (вступление и алгоритмы)
# ---------------------------------------------------------------------

def preprocess_code(code):
    """
    Разбивает исходный код на строки, удаляет комментарии (начинающиеся с '|' или '#'),
    и объединяет несколько команд, разделённых точкой с запятой, в одну строку.

    Параметры:
      code (str): Исходный код программы.

    Возвращаемое значение:
      list of str: Список обработанных строк кода.
    """
    lines = []
    for line in code.splitlines():
        if '|' in line:
            # Удаляем комментарии, начинающиеся с '|'
            line = line.split('|')[0]
        if '#' in line:
            # Удаляем комментарии, начинающиеся с '#'
            line = line.split('#')[0]
        line = line.strip()
        if not line:
            continue
        # Разбиваем строку по символу ';' и удаляем лишние пробелы
        parts = [part.strip() for part in line.split(';') if part.strip()]
        lines.extend(parts)
    return lines


def separate_sections(lines):
    """
    Разделяет список строк кода на вступление (до первого алгоритма) и алгоритмы.

    Алгоритм определяется строкой, начинающейся со слова "алг".

    Параметры:
      lines (list of str): Список строк исходного кода.

    Возвращаемое значение:
      tuple:
        - introduction (list of str): Строки вступительной части.
        - algorithms (list of dict): Список алгоритмов, где каждый алгоритм представлен словарем с ключами:
             "header" – заголовок алгоритма,
             "body" – список строк тела алгоритма.

    Исключения:
      Генерируется Exception, если встречается "нач" без "алг" или "кон" без "нач".
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
            # Создаем новый алгоритм с заголовком и пустым телом
            current_algo = {"header": line, "body": []}
            in_algo = False
        elif lower_line == "нач":
            if current_algo is None:
                raise Exception("Error: 'нач' without 'алг'")
            in_algo = True
        elif lower_line == "кон":
            if current_algo is None or not in_algo:
                raise Exception("Error: 'кон' without 'нач'")
            in_algo = False  # После "кон" алгоритм считается завершённым
        else:
            if current_algo is None:
                # Если алгоритм ещё не начат, строка относится ко вступлению
                introduction.append(line)
            else:
                if in_algo:
                    # Если находимся внутри алгоритма, добавляем строку в тело алгоритма
                    current_algo["body"].append(line)
                else:
                    # Если строка находится до начала тела алгоритма, дополняем заголовок
                    current_algo["header"] += " " + line
    if current_algo is not None:
        algorithms.append(current_algo)
    return introduction, algorithms


def parse_algorithm_header(header_line):
    """
    Разбирает заголовок алгоритма, извлекая имя алгоритма (если указано) и описание параметров.

    Пример:
      алг тест (рез цел m, n, лит т, арг вещ y)
    Возвращает словарь с ключами:
      - "raw": исходный заголовок (без "алг")
      - "name": имя алгоритма (если указано)
      - "params": список параметров в виде кортежей (режим, тип, имя)

    Параметры:
      header_line (str): Строка заголовка алгоритма.

    Возвращаемое значение:
      dict: Словарь с разобранной информацией о заголовке алгоритма.
    """
    header_line = header_line.strip()
    if header_line.lower().startswith("алг"):
        header_line = header_line[3:].strip()  # Удаляем "алг"
    params = []
    name_part = header_line
    if "(" in header_line:
        parts = header_line.split("(", 1)
        name_part = parts[0].strip()
        params_part = parts[1].rsplit(")", 1)[0]
        tokens = params_part.split()
        mode = "арг"  # Режим по умолчанию
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
# Выполнение одной строки кода (из вступления или тела алгоритма)
# ---------------------------------------------------------------------

def execute_line(line, env, robot):
    """
    Выполняет одну строку кода.

    Поддерживаемые команды:
      - Объявления переменных (начинаются с: цел, вещ, лог, сим, лит)
      - Присваивания (оператор ":=")
      - Команда вывода (начинается со слова "вывод")
      - Команды управления роботом (влево, вправо, вверх, вниз, закрасить)

    Если команда не распознана, выводится сообщение об ошибке.

    Параметры:
      line (str): Строка кода для выполнения.
      env (dict): Окружение переменных.
      robot (object): Объект робота.
    """
    lower_line = line.lower()
    # Обработка объявления переменных
    for t in ALLOWED_TYPES:
        if lower_line.startswith(t):
            try:
                process_declaration(line, env)
            except Exception as e:
                print(f"Declaration error: {e}")
            return

    # Обработка присваивания
    if ":=" in line:
        try:
            process_assignment(line, env)
        except Exception as e:
            print(f"Assignment error: {e}")
        return

    # Обработка команды вывода
    if lower_line.startswith("вывод"):
        try:
            process_output(line, env)
        except Exception as e:
            print(f"Output command error: {e}")
        return

    # Обработка команд управления роботом
    if process_robot_command(line, robot):
        return

    # Если команда не распознана, выводим сообщение
    print(f"Unknown command: {line}")


# ---------------------------------------------------------------------
# Класс интерпретатора языка KUMIR
# ---------------------------------------------------------------------

class KumirLanguageInterpreter:
    """
    Интерпретатор языка KUMIR.

    Обеспечивает обработку исходного кода, его предварительную обработку, разделение на вступление и алгоритмы,
    парсинг заголовков алгоритмов, а затем выполнение вступительной части и основного алгоритма.

    Атрибуты:
      code (str): Исходный код программы.
      env (dict): Окружение переменных (например, {"имя": {"type": ..., "value": ..., ...}}).
      algorithms (dict): Словарь вспомогательных алгоритмов по именам.
      main_algorithm (dict): Основной алгоритм (первый найденный алгоритм).
      robot (KumirInterpreter): Экземпляр интерпретатора робота, управляющий перемещениями и действиями робота.
    """

    def __init__(self, code):
        """
        Инициализирует интерпретатор с заданным исходным кодом.

        Параметры:
          code (str): Исходный код программы на языке KUMIR.
        """
        self.code = code
        self.env = {}  # Окружение для переменных
        self.algorithms = {}  # Вспомогательные алгоритмы по имени
        self.main_algorithm = None  # Основной алгоритм
        # Создаем экземпляр интерпретатора робота
        self.robot = KumirInterpreter()

    def parse(self):
        """
        Обрабатывает исходный код: выполняет предварительную обработку, разделение на вступление и алгоритмы,
        а также парсинг заголовков алгоритмов.

        Процесс:
          1. Код обрабатывается функцией preprocess_code.
          2. Полученные строки разделяются на вступительную часть и секции алгоритмов с помощью separate_sections.
          3. Первый алгоритм считается основным, остальные сохраняются по именам.

        Исключения:
          Генерируется Exception, если в программе отсутствуют алгоритмы.
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
            # Остальные алгоритмы сохраняются в словаре по имени, если имя указано
            for alg in algo_sections[1:]:
                info = parse_algorithm_header(alg["header"])
                alg["header_info"] = info
                if info["name"]:
                    self.algorithms[info["name"]] = alg
        else:
            raise Exception("No algorithms found in the program.")

    def execute_introduction(self):
        """
        Выполняет вступительную часть программы (команды до первого алгоритма).
        Каждая строка вступления выполняется с помощью execute_line, что обновляет окружение и состояние робота.
        """
        for line in self.introduction:
            execute_line(line, self.env, self.robot)

    def execute_algorithm(self, algorithm):
        """
        Выполняет тело алгоритма (строки между командами 'нач' и 'кон').

        Параметры:
          algorithm (dict): Секция алгоритма с ключом "body", содержащим список строк кода.
        """
        for line in algorithm["body"]:
            execute_line(line, self.env, self.robot)

    def interpret(self):
        """
        Полное выполнение программы: парсинг, выполнение вступления и основного алгоритма.

        Возвращаемое значение:
          dict: Содержит обновленное окружение переменных и текущую позицию робота.
        """
        self.parse()
        self.execute_introduction()
        print("Executing main algorithm:")
        self.execute_algorithm(self.main_algorithm)
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
