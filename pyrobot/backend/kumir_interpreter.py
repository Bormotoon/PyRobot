# kumir_interpreter.py

import math
import re

from .kumir_interpreter.robot_interpreter import KumirInterpreter

# ---------------------------------------------------------------------
# Constants and settings
# ---------------------------------------------------------------------

# Reserved keywords (incomplete list including the main ones from the documentation)
RESERVED_KEYWORDS = {
    "алг", "нач", "кон", "исп", "кон_исп", "дано", "надо", "арг", "рез", "аргрез", "знач", "цел",
    "вещ", "лог", "сим", "лит", "таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб", "и", "или", "не",
    "да", "нет", "утв", "выход", "ввод", "вывод", "нс", "если", "то", "иначе", "все", "выбор", "при", "нц",
    "кц", "кц_при", "раз", "пока", "для", "от", "до", "шаг"
}

# Allowed variable types
ALLOWED_TYPES = {"цел", "вещ", "лог", "сим", "лит"}

# Maximum integer value (as defined in the documentation)
MAX_INT = 2147483647
# Для обратной совместимости оставляем псевдоним:
МАКСЦЕЛ = MAX_INT


# ---------------------------------------------------------------------
# Helper functions for names and constants
# ---------------------------------------------------------------------

def is_valid_identifier(identifier, var_type):
    """
    Checks that the identifier meets the requirements:
      - Consists of one or more words separated by spaces.
      - The first word does not start with a digit.
      - None of the words (except the allowed insertion of "не" in logical variables)
        is a reserved keyword.
    """
    words = identifier.strip().split()
    if not words:
        return False
    if re.match(r'^\d', words[0]):
        return False
    for word in words:
        # For logical variables, the word "не" is allowed if it is not the first word
        if word.lower() in RESERVED_KEYWORDS:
            if var_type == "лог" and word.lower() == "не" and word != words[0]:
                continue
            return False
        if not re.match(r'^[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*$', word):
            return False
    return True


def convert_hex_constants(expr):
    """
    Replaces all hexadecimal constants starting with '$' with a Python-compatible format.
    For example: '$100' -> '0x100'
    """
    return re.sub(r'\$(?P<hex>[A-Fa-f0-9]+)', r'0x\g<hex>', expr)


def safe_eval(expr, eval_env):
    """
    Evaluates the expression using a safe environment.
    Also replaces hexadecimal constants.
    """
    expr = convert_hex_constants(expr)
    safe_globals = {"__builtins__": None, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt, "int": int,
                    "float": float}
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    """
    Builds a dictionary for evaluating expressions by extracting the values from our environment.
    Our environment is stored as: env[var_name] = {"type": ..., "value": ...}
    """
    result = {}
    for var, info in env.items():
        result[var] = info.get("value")
    return result


# ---------------------------------------------------------------------
# Processing of variable declarations
# ---------------------------------------------------------------------

def process_declaration(line, env):
    """
    Processes a declaration line.
    Format: <type> [таб] <comma-separated list of identifiers>
    For example: цел длина, ширина, лог условие, лит мой текст
    For table variables, the value is initialized as an empty dictionary.
    """
    tokens = line.split()
    if not tokens:
        return False

    decl_type = tokens[0].lower()
    if decl_type not in ALLOWED_TYPES:
        return False

    idx = 1
    is_table = False
    if idx < len(tokens) and tokens[idx].lower().startswith("таб"):
        is_table = True
        idx += 1

    rest = " ".join(tokens[idx:])
    identifiers = [ident.strip() for ident in rest.split(",") if ident.strip()]
    if not identifiers:
        raise Exception("Declaration without any variable names.")

    for ident in identifiers:
        if not is_valid_identifier(ident, decl_type):
            raise Exception(f"Invalid variable name: '{ident}'")
        if ident in env:
            raise Exception(f"Variable '{ident}' already declared.")
        env[ident] = {"type": decl_type, "value": {} if is_table else None, "kind": "global", "is_table": is_table}
    return True


# ---------------------------------------------------------------------
# Processing of assignments and output commands
# ---------------------------------------------------------------------

def process_assignment(line, env):
    """
    Processes an assignment of the form: VARIABLE := EXPRESSION.
    Checks that the variable is declared, evaluates the expression and converts the result to the variable’s type.
    Updates the variable’s value in env.
    """
    parts = line.split(":=")
    if len(parts) != 2:
        raise Exception("Invalid assignment syntax.")
    left, right = parts[0].strip(), parts[1].strip()

    # If assignment for an array element (e.g. a[i] or b[i,j])
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
        env[var_name]["value"][indices] = value
        return

    # Assignment for a simple variable
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
    Processes an output command.
    Format: вывод expr1, ..., exprN
    Evaluates the expression after the word 'вывод' and prints the result.
    """
    content = line[5:].strip()
    eval_env = get_eval_env(env)
    try:
        value = safe_eval(content, eval_env)
    except Exception:
        value = content
    print(value)


# ---------------------------------------------------------------------
# Function to delegate robot commands
# ---------------------------------------------------------------------

def process_robot_command(line, robot):
    """
    If the line corresponds to one of the robot control commands, calls the corresponding function.
    Supported commands: влево, вправо, вверх, вниз, закрасить.
    """
    cmd = line.lower().strip()
    robot_commands = {
        "влево": robot.go_left,
        "вправо": robot.go_right,
        "вверх": robot.go_up,
        "вниз": robot.go_down,
        "закрасить": robot.do_paint
    }
    if cmd in robot_commands:
        try:
            robot_commands[cmd]()
        except Exception as e:
            print(f"Error executing command '{line}': {e}")
        return True
    return False


# ---------------------------------------------------------------------
# Preprocessing and splitting into lines/algorithms
# ---------------------------------------------------------------------

def preprocess_code(code):
    """
    Splits the source code into lines, removes comments (lines starting with '|' or '#'),
    and combines multiple commands into one using semicolons.
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
    Splits the input lines into an introduction (before the first algorithm) and algorithms.
    An algorithm is determined by a line starting with "алг".
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
                raise Exception("Error: 'нач' without 'алг'")
            in_algo = True
        elif lower_line == "кон":
            if current_algo is None or not in_algo:
                raise Exception("Error: 'кон' without 'нач'")
            in_algo = False  # After "кон", the algorithm is considered complete
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
    Parses the algorithm header, extracting the algorithm name (if provided) and the parameter description.
    Example:
      алг тест (рез цел m, n, лит т, арг вещ y)
    Returns a dictionary with keys:
      - "raw": the original header (without "алг")
      - "name": the algorithm name (if any)
      - "params": a list of parameters as tuples (mode, type, name)
    """
    header_line = header_line.strip()
    if header_line.lower().startswith("алг"):
        header_line = header_line[3:].strip()  # remove "алг"
    params = []
    name_part = header_line
    if "(" in header_line:
        parts = header_line.split("(", 1)
        name_part = parts[0].strip()
        params_part = parts[1].rsplit(")", 1)[0]
        tokens = params_part.split()
        mode = "арг"  # default mode
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
# Function to execute a single line of code (from the introduction or algorithm body)
# ---------------------------------------------------------------------

def execute_line(line, env, robot):
    """
    Executes a single line of code.
    Supports:
      - Variable declarations (starting with цел, вещ, лог, сим, лит)
      - Assignments (using ":=")
      - Output command (starting with "вывод")
      - Robot control commands (влево, вправо, вверх, вниз, закрасить)
    If the line is not recognized, prints a message.
    """
    lower_line = line.lower()
    # Variable declaration
    for t in ALLOWED_TYPES:
        if lower_line.startswith(t):
            try:
                process_declaration(line, env)
            except Exception as e:
                print(f"Declaration error: {e}")
            return

    # Assignment
    if ":=" in line:
        try:
            process_assignment(line, env)
        except Exception as e:
            print(f"Assignment error: {e}")
        return

    # Output
    if lower_line.startswith("вывод"):
        try:
            process_output(line, env)
        except Exception as e:
            print(f"Output command error: {e}")
        return

    # Robot control commands
    if process_robot_command(line, robot):
        return

    print(f"Unknown command: {line}")


# ---------------------------------------------------------------------
# Kumir Language Interpreter class
# ---------------------------------------------------------------------

class KumirLanguageInterpreter:
    def __init__(self, code):
        self.code = code
        # Environment for variables: a dictionary of the form { var_name: {"type": ..., "value": ..., "kind": ..., "is_table": ...} }
        self.env = {}
        self.algorithms = {}  # Dictionary for helper algorithms by name
        self.main_algorithm = None
        # Create an instance of the robot executor
        self.robot = KumirInterpreter()

    def parse(self):
        """
        Processes the source code: preprocessing, splitting into introduction and algorithms,
        and parsing algorithm headers.
        """
        lines = preprocess_code(self.code)
        introduction, algo_sections = separate_sections(lines)
        self.introduction = introduction
        self.algo_sections = algo_sections

        if algo_sections:
            # The first algorithm is considered the main one
            self.main_algorithm = algo_sections[0]
            header_info = parse_algorithm_header(self.main_algorithm["header"])
            self.main_algorithm["header_info"] = header_info
            # Save additional algorithms by name if provided
            for alg in algo_sections[1:]:
                info = parse_algorithm_header(alg["header"])
                alg["header_info"] = info
                if info["name"]:
                    self.algorithms[info["name"]] = alg
        else:
            raise Exception("No algorithms found in the program.")

    def execute_introduction(self):
        """Executes the introduction (commands before the first algorithm)."""
        for line in self.introduction:
            execute_line(line, self.env, self.robot)

    def execute_algorithm(self, algorithm):
        """Executes the body of an algorithm (lines between 'нач' and 'кон')."""
        for line in algorithm["body"]:
            execute_line(line, self.env, self.robot)

    def interpret(self):
        """Full interpretation of the program: parsing, executing the introduction and the main algorithm."""
        self.parse()
        self.execute_introduction()
        print("Executing main algorithm:")
        self.execute_algorithm(self.main_algorithm)
        # Return the updated environment and the current robot position.
        return {"env": self.env, "robot": self.robot.robot_pos}


# ---------------------------------------------------------------------
# Example usage
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
