"""
Модуль declarations.py
@description Реализует функции для обработки объявлений, присваиваний, вывода и ввода в интерпретаторе языка KUMIR.
Функции обеспечивают парсинг строк с декларациями и присваиваниями, а также обработку команд вывода и ввода.
"""

from .constants import ALLOWED_TYPES, MAX_INT  # Импорт допустимых типов и максимального значения для целых чисел
from .file_functions import get_default_output, get_default_input  # Функции для получения стандартного вывода и ввода
from .identifiers import is_valid_identifier  # Функция для проверки корректности идентификатора
from .safe_eval import safe_eval, get_eval_env  # Функции для безопасного вычисления выражений и получения окружения


def process_declaration(line, env):
    """
    Обрабатывает оператор объявления переменных.
    Формат: <тип> [таб] <список идентификаторов, разделенных запятыми>
    Пример: цел длина, ширина, лог условие, лит мой текст
    Для таблиц значение инициализируется как пустой словарь.

    Параметры:
      line (str): Строка с оператором объявления.
      env (dict): Окружение, в котором регистрируются переменные.

    Возвращаемое значение:
      bool: True, если объявление успешно обработано, иначе False.

    Исключения:
      Генерируется Exception, если:
        - Объявление не содержит имен величин.
        - Имя величины некорректно.
        - Величина с таким именем уже объявлена.
    """
    tokens = line.split()
    if not tokens:
        return False

    # Первый токен - тип величины, приводим к нижнему регистру
    decl_type = tokens[0].lower()
    if decl_type not in ALLOWED_TYPES:
        return False

    idx = 1
    is_table = False
    # Если следующий токен начинается с "таб", то это объявление таблицы
    if idx < len(tokens) and tokens[idx].lower().startswith("таб"):
        is_table = True
        idx += 1

    # Остальные токены объединяются в одну строку и разделяются запятыми для получения списка идентификаторов
    rest = " ".join(tokens[idx:])
    identifiers = [ident.strip() for ident in rest.split(",") if ident.strip()]
    if not identifiers:
        raise Exception("Объявление типа без указания имен величин.")

    for ident in identifiers:
        # Проверяем корректность имени величины с учетом ее типа
        if not is_valid_identifier(ident, decl_type):
            raise Exception(f"Некорректное имя величины: '{ident}'")
        # Если величина уже объявлена в окружении, выдаем ошибку
        if ident in env:
            raise Exception(f"Величина '{ident}' уже объявлена.")
        # Инициализируем переменную с заданным типом и пустым значением (или пустым словарем для таблицы)
        env[ident] = {"type": decl_type, "value": {} if is_table else None, "kind": "global", "is_table": is_table}
    return True


def process_assignment(line, env):
    """
    Обрабатывает оператор присваивания переменной.
    Поддерживается присваивание для простых переменных и элементов таблицы.
    Формат: VARIABLE := EXPRESSION

    Параметры:
      line (str): Строка с оператором присваивания.
      env (dict): Окружение, содержащее объявленные переменные.

    Исключения:
      Генерируется Exception при ошибках синтаксиса, отсутствии переменной,
      ошибках вычисления выражения или приведении типа.
    """
    parts = line.split(":=")
    if len(parts) != 2:
        raise Exception("Неверный синтаксис присваивания.")
    left, right = parts[0].strip(), parts[1].strip()

    # Присваивание для элемента таблицы (например, a[i] или b[i,j])
    if "[" in left and left.endswith("]"):
        import re
        match = re.match(
            r"^([A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*(?:\s+[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*)*)\[(.+)\]$",
            left)
        if not match:
            raise Exception(f"Неверный синтаксис для присваивания элемента таблицы: {left}")
        var_name = match.group(1).strip()
        indices_expr = match.group(2).strip()
        # Разбиваем выражение индексов по запятым
        index_tokens = [token.strip() for token in indices_expr.split(",")]
        eval_env = get_eval_env(env)
        try:
            # Вычисляем индексы с помощью безопасного вычисления
            indices = tuple(safe_eval(token, eval_env) for token in index_tokens)
        except Exception as e:
            raise Exception(f"Ошибка вычисления индексов в '{left}': {e}")
        # Проверяем, что переменная объявлена как таблица
        if var_name not in env or not env[var_name].get("is_table"):
            raise Exception(f"Переменная '{var_name}' не объявлена как таблица.")
        target_type = env[var_name]["type"]
        try:
            value = safe_eval(right, eval_env)
        except Exception as e:
            raise Exception(f"Ошибка вычисления выражения '{right}': {e}")
        try:
            # Приведение значения к требуемому типу в зависимости от типа величины
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
        # Если значение таблицы еще не инициализировано, создаем пустой словарь
        if env[var_name]["value"] is None:
            env[var_name]["value"] = {}
        # Присваиваем вычисленное значение элементу таблицы с указанными индексами
        env[var_name]["value"][indices] = value
        return

    # Присваивание для простой переменной
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
    # Присваиваем вычисленное значение переменной
    env[left]["value"] = value


def process_output(line, env, interpreter=None):
    """
    Обрабатывает команду вывода.
    Формат: вывод expression1, ..., expressionN
    Если первое выражение является переменной файлового типа, вывод направляется в этот файл;
    иначе, если стандартный вывод установлен (через НАЗНАЧИТЬ ВЫВОД), вывод записывается туда.
    Ключевое слово "нс" интерпретируется как перевод строки.
    Если передан параметр interpreter, вывод добавляется в его буфер (interpreter.output).

    Параметры:
      line (str): Строка с командой вывода.
      env (dict): Окружение, содержащее переменные.
      interpreter (object, опционально): Объект интерпретатора для буферизации вывода.
    """
    # Извлекаем содержимое команды вывода, отбрасывая ключевое слово "вывод"
    content = line[5:].strip()
    expressions = [expr.strip() for expr in content.split(",") if expr.strip()]
    eval_env = get_eval_env(env)
    output_str = ""
    # Обрабатываем каждое выражение
    for expr in expressions:
        if expr.lower() == "нс":
            output_str += "\n"
        else:
            try:
                value = safe_eval(expr, eval_env)
            except Exception:
                # Если вычисление не удалось, используем исходное выражение
                value = expr
            output_str += str(value)
    # Пытаемся получить стандартный выходной поток
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
    Обрабатывает команду ввода.
    Формат: ввод expression1, ..., expressionN
    Если стандартный вход установлен (через НАЗНАЧИТЬ ВВОД), он используется;
    иначе запрашивается ввод с клавиатуры.
    Введенные значения присваиваются соответствующим переменным.

    Параметры:
      line (str): Строка с командой ввода.
      env (dict): Окружение, содержащее переменные.

    Выводит предупреждение, если введено меньше значений, чем требуется.
    """
    # Извлекаем имена переменных для присваивания, отбрасывая ключевое слово "ввод"
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
            # Присваиваем полученное значение переменной
            env[target]["value"] = val
        else:
            print(f"Переменная '{target}' не объявлена.")
