# Глобальные константы и маппинги типов
from pyrobot.backend.kumir_interpreter.generated.KumirLexer import KumirLexer

MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT

# Словарь для маппинга токенов типа на строки
TYPE_MAP = {
    KumirLexer.INTEGER_TYPE: 'цел',
    KumirLexer.REAL_TYPE: 'вещ',
    KumirLexer.BOOLEAN_TYPE: 'лог',
    KumirLexer.CHAR_TYPE: 'сим',
    KumirLexer.STRING_TYPE: 'лит',
}

# Типы данных (строковые константы для удобства)
INTEGER_TYPE = 'цел'
FLOAT_TYPE = 'вещ'
BOOLEAN_TYPE = 'лог'
CHAR_TYPE = 'сим' # Corrected from "лит"
STRING_TYPE = 'лит' # Corrected from "текст"
VOID_TYPE = "пусто" # For procedures or functions that don't return a value explicitly

# Новые константы для операций и типов
ALLOWED_OPERATIONS = {
    # Арифметические операции
    '+': {
        (INTEGER_TYPE, INTEGER_TYPE): INTEGER_TYPE,
        (FLOAT_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (FLOAT_TYPE, INTEGER_TYPE): FLOAT_TYPE,
        (STRING_TYPE, STRING_TYPE): STRING_TYPE, # Конкатенация строк
        (CHAR_TYPE, CHAR_TYPE): STRING_TYPE, # Символ + Символ = Строка
        (STRING_TYPE, CHAR_TYPE): STRING_TYPE,
        (CHAR_TYPE, STRING_TYPE): STRING_TYPE,
    },
    '-': {
        (INTEGER_TYPE, INTEGER_TYPE): INTEGER_TYPE,
        (FLOAT_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (FLOAT_TYPE, INTEGER_TYPE): FLOAT_TYPE,
    },
    '*': {
        (INTEGER_TYPE, INTEGER_TYPE): INTEGER_TYPE,
        (FLOAT_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (FLOAT_TYPE, INTEGER_TYPE): FLOAT_TYPE,
    },
    '/': { # Деление всегда дает вещественный результат в Кумире
        (INTEGER_TYPE, INTEGER_TYPE): FLOAT_TYPE,
        (FLOAT_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (FLOAT_TYPE, INTEGER_TYPE): FLOAT_TYPE,
    },
    'DIV': { # Целочисленное деление
        (INTEGER_TYPE, INTEGER_TYPE): INTEGER_TYPE,
    },
    'MOD': { # Остаток от деления
        (INTEGER_TYPE, INTEGER_TYPE): INTEGER_TYPE,
    },
    '^': { # Возведение в степень
        # Правило: если основание ЦЕЛ, показатель ЦЕЛ >= 0, то результат ЦЕЛ.
        # Иначе результат ВЕЩ. Это будет обрабатываться в ExpressionEvaluator,
        # здесь указываем наиболее общий случай или базовые возможности.
        # Для статической проверки можно указать оба варианта или более общий (ВЕЩ).
        # Динамическое определение типа результата для ^ будет в ExpressionEvaluator.
        (INTEGER_TYPE, INTEGER_TYPE): INTEGER_TYPE, # Потенциально ЦЕЛ или ВЕЩ
        (FLOAT_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): FLOAT_TYPE,
        (FLOAT_TYPE, INTEGER_TYPE): FLOAT_TYPE,
    },
    # Логические операции
    'И': {(BOOLEAN_TYPE, BOOLEAN_TYPE): BOOLEAN_TYPE},
    'ИЛИ': {(BOOLEAN_TYPE, BOOLEAN_TYPE): BOOLEAN_TYPE},
    # Операции сравнения (все возвращают логический тип)
    '<': {
        (INTEGER_TYPE, INTEGER_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, FLOAT_TYPE): BOOLEAN_TYPE,
        (STRING_TYPE, STRING_TYPE): BOOLEAN_TYPE, (CHAR_TYPE, CHAR_TYPE): BOOLEAN_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, INTEGER_TYPE): BOOLEAN_TYPE,
    },
    '>': {
        (INTEGER_TYPE, INTEGER_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, FLOAT_TYPE): BOOLEAN_TYPE,
        (STRING_TYPE, STRING_TYPE): BOOLEAN_TYPE, (CHAR_TYPE, CHAR_TYPE): BOOLEAN_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, INTEGER_TYPE): BOOLEAN_TYPE,
    },
    '<=': {
        (INTEGER_TYPE, INTEGER_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, FLOAT_TYPE): BOOLEAN_TYPE,
        (STRING_TYPE, STRING_TYPE): BOOLEAN_TYPE, (CHAR_TYPE, CHAR_TYPE): BOOLEAN_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, INTEGER_TYPE): BOOLEAN_TYPE,
    },
    '>=': {
        (INTEGER_TYPE, INTEGER_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, FLOAT_TYPE): BOOLEAN_TYPE,
        (STRING_TYPE, STRING_TYPE): BOOLEAN_TYPE, (CHAR_TYPE, CHAR_TYPE): BOOLEAN_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, INTEGER_TYPE): BOOLEAN_TYPE,
    },
    '=': { # Равенство применимо ко всем базовым типам
        (INTEGER_TYPE, INTEGER_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, FLOAT_TYPE): BOOLEAN_TYPE,
        (STRING_TYPE, STRING_TYPE): BOOLEAN_TYPE, (CHAR_TYPE, CHAR_TYPE): BOOLEAN_TYPE,
        (BOOLEAN_TYPE, BOOLEAN_TYPE): BOOLEAN_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, INTEGER_TYPE): BOOLEAN_TYPE, # Сравнение целого и вещ
    },
    '<>': { # Неравенство
        (INTEGER_TYPE, INTEGER_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, FLOAT_TYPE): BOOLEAN_TYPE,
        (STRING_TYPE, STRING_TYPE): BOOLEAN_TYPE, (CHAR_TYPE, CHAR_TYPE): BOOLEAN_TYPE,
        (BOOLEAN_TYPE, BOOLEAN_TYPE): BOOLEAN_TYPE,
        (INTEGER_TYPE, FLOAT_TYPE): BOOLEAN_TYPE, (FLOAT_TYPE, INTEGER_TYPE): BOOLEAN_TYPE,
    },
}

# Иерархия типов для автоматического приведения (ключ - из какого типа, значение - множество типов, к которым можно привести)
TYPE_HIERARCHY = {
    INTEGER_TYPE: {FLOAT_TYPE},
    FLOAT_TYPE: set(),
    STRING_TYPE: set(),
    CHAR_TYPE: {STRING_TYPE}, # Символ можно использовать как строку из одного символа
    BOOLEAN_TYPE: set(),
}

# Унарные операции
UNARY_OPERATIONS = {
    '-': {INTEGER_TYPE: INTEGER_TYPE, FLOAT_TYPE: FLOAT_TYPE}, # Унарный минус
    'НЕ': {BOOLEAN_TYPE: BOOLEAN_TYPE}, # Логическое отрицание
}

# Дополнительные типы данных, если они будут использоваться в KumirValue.type_name
TABLE_TYPE = "таб"
ALGORITHM_TYPE = "алг" # Для ссылок на алгоритмы (если это будет объектом первого класса)
# ... можно добавить другие специфичные типы Кумира