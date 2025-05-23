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
CHAR_TYPE = 'сим'
STRING_TYPE = 'лит'

VOID_TYPE = 'пусто' # Тип для процедур, не возвращающих значение (не используется в явных объявлениях, но полезен внутренне)

# Логические константы Кумира
KUMIR_TRUE = "истина"
KUMIR_FALSE = "ложь"

# Дополнительные константы, если понадобятся
# ... 