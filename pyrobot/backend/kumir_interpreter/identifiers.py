# identifiers.py

import re
from .constants import RESERVED_KEYWORDS


def is_valid_identifier(identifier, var_type):
    """
    Проверяет, что identifier соответствует требованиям:
      - Состоит из одного или нескольких слов, разделённых пробелами.
      - Первое слово не начинается с цифры.
      - Ни одно слово (за исключением допустимого случая для логических величин)
        не является зарезервированным ключевым словом.
      - Допустимы только буквы (кириллические и латинские), цифры, символы "@" и "_".
    """
    words = identifier.strip().split()
    if not words:
        return False
    if re.match(r'^\d', words[0]):
        return False
    for word in words:
        if word.lower() in RESERVED_KEYWORDS:
            # Для логических величин допустимо встраивание "не", если оно не первое
            if var_type == "лог" and word.lower() == "не" and word != words[0]:
                continue
            return False
        if not re.match(r'^[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*$', word):
            return False
    return True


def convert_hex_constants(expr):
    """
    Заменяет шестнадцатеричные константы, начинающиеся с '$', на формат, понятный Python.
    Например: '$100' -> '0x100'
    """
    return re.sub(r'\$(?P<hex>[A-Fa-f0-9]+)', r'0x\g<hex>', expr)
