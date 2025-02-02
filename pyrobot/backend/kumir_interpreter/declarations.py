# declarations.py

from constants import ALLOWED_TYPES, МАКСЦЕЛ
from identifiers import is_valid_identifier
from safe_eval import safe_eval, get_eval_env


def process_declaration(line, env):
    """
    Обрабатывает строку объявления величин.
    Формат: <тип> [таб] <список идентификаторов через запятую>
    Например: цел длина, ширина, лог условие, лит мой текст
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
        env[ident] = {"type": decl_type, "value": None, "kind": "global", "is_table": is_table}
    return True


def process_assignment(line, env):
    """
    Обрабатывает присваивание вида: <идентификатор> := <выражение>
    Вычисляет выражение в безопасном окружении и приводит значение к объявленному типу.
    """
    parts = line.split(":=")
    if len(parts) != 2:
        raise Exception("Неверный синтаксис присваивания.")
    left, right = parts[0].strip(), parts[1].strip()
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
            if not (-МАКСЦЕЛ <= value <= МАКСЦЕЛ):
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


def process_output(line, env):
    """
    Обрабатывает команду вывода. Вычисляет выражение после ключевого слова "вывод" и выводит результат.
    """
    content = line[5:].strip()  # всё после "вывод"
    eval_env = get_eval_env(env)
    try:
        value = safe_eval(content, eval_env)
    except Exception:
        value = content
    print(value)
