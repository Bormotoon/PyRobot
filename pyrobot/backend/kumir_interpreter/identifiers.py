# FILE START: identifiers.py
import re

# --->>> ДОБАВЛЯЕМ ИМПОРТЫ ИЗ constants <<<---
from .constants import RESERVED_KEYWORDS


def is_valid_identifier(identifier, var_type):
    """
    Проверяет корректность идентификатора с учетом типа переменной.
    """
    words = identifier.strip().split()
    if not words:
        return False
    # Проверяем, что первое слово не начинается с цифры
    first_word_match = re.match(r'^\d', words[0])
    if first_word_match:
        logger.debug(f"Identifier '{identifier}' rejected: first word '{words[0]}' starts with a digit.")
        return False

    for i, word in enumerate(words):
        word_lower = word.lower()
        # Проверка на зарезервированное слово
        if word_lower in RESERVED_KEYWORDS:
            # Исключение: 'не' допустимо для типа 'лог', если это не первое слово
            if var_type == "лог" and word_lower == "не" and i > 0:
                continue  # Допустимо 'лог переменная не простая'
            logger.debug(f"Identifier '{identifier}' rejected: word '{word}' is a reserved keyword.")
            return False
        # Проверка на допустимые символы (буквы, цифры, @, _) и начало слова
        if not re.match(r'^[A-Za-zА-Яа-яЁё@_][A-Za-zА-Яа-яЁё0-9@_]*$', word):
            logger.debug(
                f"Identifier '{identifier}' rejected: word '{word}' contains invalid characters or starts incorrectly.")
            return False
    # Если все проверки пройдены
    logger.debug(f"Identifier '{identifier}' is valid.")
    return True


# Функция convert_hex_constants остается без изменений
def convert_hex_constants(expr):
    """
    Заменяет шестнадцатеричные константы '$...' на формат Python '0x...'.
    """
    return re.sub(r'\$(?P<hex>[A-Fa-f0-9]+)', r'0x\g<hex>', expr)


# Добавим логгер, если его нет
import logging

logger = logging.getLogger('KumirIdentifiers')

# FILE END: identifiers.py