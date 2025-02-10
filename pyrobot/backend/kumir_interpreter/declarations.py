# declarations.py

from .constants import ALLOWED_TYPES, MAX_INT  # заменено МАКСЦЕЛ → MAX_INT (алиас уже установлен)
from .identifiers import is_valid_identifier
from .safe_eval import safe_eval, get_eval_env
from .file_functions import get_default_output, get_default_input


def process_declaration(line, env):
    """
    Processes a declaration statement.
    Format: <type> [tab] <comma-separated list of identifiers>
    Example: цел длина, ширина, лог условие, лит мой текст
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
        raise Exception("Объявление типа без указания имен величин.")

    for ident in identifiers:
        if not is_valid_identifier(ident, decl_type):
            raise Exception(f"Некорректное имя величины: '{ident}'")
        if ident in env:
            raise Exception(f"Величина '{ident}' уже объявлена.")
        env[ident] = {
            "type": decl_type,
            "value": {} if is_table else None,
            "kind": "global",
            "is_table": is_table
        }
    return True


def process_assignment(line, env):
    """
    Processes an assignment statement: VARIABLE := EXPRESSION.
    Supports assignment to simple variables and table elements.
    """
    parts = line.split(":=")
    if len(parts) != 2:
        raise Exception("Неверный синтаксис присваивания.")
    left, right = parts[0].strip(), parts[1].strip()

    # Assignment to a table element (e.g. a[i] or b[i,j])
    if "[" in left and left.endswith("]"):
        import re
        match = re.match(
            r"^([A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*(?:\s+[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*)*)\[(.+)\]$",
            left)
        if not match:
            raise Exception(f"Неверный синтаксис для присваивания элемента таблицы: {left}")
        var_name = match.group(1).strip()
        indices_expr = match.group(2).strip()
        index_tokens = [token.strip() for token in indices_expr.split(",")]
        eval_env = get_eval_env(env)
        try:
            indices = tuple(safe_eval(token, eval_env) for token in index_tokens)
        except Exception as e:
            raise Exception(f"Ошибка вычисления индексов в '{left}': {e}")
        if var_name not in env or not env[var_name].get("is_table"):
            raise Exception(f"Переменная '{var_name}' не объявлена как таблица.")
        target_type = env[var_name]["type"]
        try:
            value = safe_eval(right, eval_env)
        except Exception as e:
            raise Exception(f"Ошибка вычисления выражения '{right}': {e}")
        try:
            if target_type == "цел":
                value = int(value)
                if not (-MAX_INT <= value <= MAX_INT):
                    raise Exception("Значение вне допустимого диапазона для целого типа.")
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
                        raise Exception("Неверное логическое значение.")
                else:
                    value = bool(value)
            elif target_type in {"сим", "лит"}:
                value = str(value)
                if target_type == "сим" and len(value) != 1:
                    raise Exception("Символьная величина должна быть ровно один символ.")
            else:
                raise Exception(f"Неподдерживаемый тип величины: {target_type}")
        except Exception as e:
            raise Exception(f"Ошибка приведения значения для '{left}': {e}")
        if env[var_name]["value"] is None:
            env[var_name]["value"] = {}
        env[var_name]["value"][indices] = value
        return

    # Assignment for a simple variable
    if left not in env:
        raise Exception(f"Переменная '{left}' не объявлена.")
    eval_env = get_eval_env(env)
    try:
        value = safe_eval(right, eval_env)
    except Exception as e:
        raise Exception(f"Ошибка вычисления выражения '{right}': {e}")
    target_type = env[left]["type"]
    try:
        if target_type == "цел":
            value = int(value)
            if not (-MAX_INT <= value <= MAX_INT):
                raise Exception("Значение вне допустимого диапазона для целого типа.")
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
                    raise Exception("Неверное логическое значение.")
            else:
                value = bool(value)
        elif target_type in {"сим", "лит"}:
            value = str(value)
            if target_type == "сим" and len(value) != 1:
                raise Exception("Символьная величина должна быть ровно один символ.")
        else:
            raise Exception(f"Неподдерживаемый тип величины: {target_type}")
    except Exception as e:
        raise Exception(f"Ошибка приведения значения для переменной '{left}': {e}")
    env[left]["value"] = value


def process_output(line, env, interpreter=None):
    """
    Processes an output command.
    Format: вывод expression1, ..., expressionN
    If the first expression is a file-type variable, output is directed to that file;
    otherwise, if standard output is set (via НАЗНАЧИТЬ ВЫВОД), output is written there.
    The keyword нс is interpreted as a newline.
    If the parameter interpreter is provided, the output is appended to its buffer (interpreter.output).
    """
    content = line[5:].strip()
    expressions = [expr.strip() for expr in content.split(",") if expr.strip()]
    eval_env = get_eval_env(env)
    output_str = ""
    for expr in expressions:
        if expr.lower() == "нс":
            output_str += "\n"
        else:
            try:
                value = safe_eval(expr, eval_env)
            except Exception:
                value = expr
            output_str += str(value)
    default_out = get_default_output()
    if default_out is not None:
        try:
            default_out.write(output_str)
            default_out.flush()
        except Exception as e:
            print(f"Ошибка записи в файл вывода: {e}")
    elif interpreter is not None:
        interpreter.output += output_str + "\n"
    else:
        print(output_str)


def process_input(line, env):
    """
    Processes an input command.
    Format: ввод expression1, ..., expressionN
    If standard input is set (via НАЗНАЧИТЬ ВВОД), it is used; otherwise, input is requested from the keyboard.
    The entered values are assigned to the corresponding variables.
    """
    content = line[4:].strip()
    targets = [t.strip() for t in content.split(",") if t.strip()]
    default_in = get_default_input()
    if default_in is not None:
        input_str = default_in.read()
    else:
        input_str = input("Введите значения для команды 'ввод' (разделенные пробелом): ")
    values = input_str.split()
    if len(values) < len(targets):
        print("Предупреждение: введено меньше значений, чем требуется.")
    for i, target in enumerate(targets):
        if target.lower() == "нс":
            continue
        if target in env:
            var_type = env[target]["type"]
            try:
                if var_type == "цел":
                    val = int(values[i])
                elif var_type == "вещ":
                    val = float(values[i])
                elif var_type == "лог":
                    s = values[i].lower()
                    if s == "да":
                        val = True
                    elif s == "нет":
                        val = False
                    else:
                        val = bool(values[i])
                elif var_type in {"сим", "лит"}:
                    val = str(values[i])
                    if var_type == "сим" and len(val) != 1:
                        raise Exception("Символьная величина должна быть ровно один символ.")
                else:
                    raise Exception(f"Неподдерживаемый тип: {var_type}")
            except Exception as e:
                print(f"Ошибка преобразования значения для '{target}': {e}")
                continue
            env[target]["value"] = val
        else:
            print(f"Переменная '{target}' не объявлена.")
