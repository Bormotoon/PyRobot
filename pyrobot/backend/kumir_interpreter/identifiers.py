import re

from .constants import RESERVED_KEYWORDS


def is_valid_identifier(identifier, var_type):
    """
    Проверяет корректность идентификатора с учетом типа переменной.

    Требования к идентификатору:
      - Состоит из одного или нескольких слов, разделённых пробелами.
      - Первое слово не должно начинаться с цифры.
      - Каждое слово не должно совпадать с зарезервированным ключевым словом (за исключением допустимого случая для логических величин,
        где слово "не" может встречаться, если не является первым словом).
      - Слова могут содержать только буквы (кириллические и латинские), цифры, символы "@" и "_".

    Параметры:
      identifier (str): Идентификатор, который необходимо проверить.
      var_type (str): Тип переменной ("цел", "вещ", "лог", "сим", "лит" и т.д.), используется для исключения специфичных проверок.

    Возвращаемое значение:
      bool: True, если идентификатор корректен, иначе False.
    """
    # Разбиваем идентификатор на слова по пробелам после удаления лишних пробелов
    words = identifier.strip().split()
    if not words:
        return False
    # Проверяем, что первое слово не начинается с цифры
    if re.match(r'^\d', words[0]):
        return False
    for word in words:
        # Если слово является зарезервированным, то для логических величин допускается "не", если оно не первое слово
        if word.lower() in RESERVED_KEYWORDS:
            if var_type == "лог" and word.lower() == "не" and word != words[0]:
                continue
            return False
        # Проверяем, что слово соответствует допустимому шаблону: начинается с буквы, символа "@" или "_" и далее может содержать буквы, цифры, "@" или "_"
        if not re.match(r'^[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*$', word):
            return False
    return True


def convert_hex_constants(expr):
    """
    Заменяет шестнадцатеричные константы, начинающиеся с символа '$',
    на формат, понятный Python (например, '$100' преобразуется в '0x100').

    Параметры:
      expr (str): Строка, содержащая шестнадцатеричные константы.

    Возвращаемое значение:
      str: Строка с замененными шестнадцатеричными константами.
    """
    # Используем регулярное выражение для поиска последовательностей вида $[A-Fa-f0-9]+ и заменяем их на 0x[hex]
    return re.sub(r'\$(?P<hex>[A-Fa-f0-9]+)', r'0x\g<hex>', expr)
