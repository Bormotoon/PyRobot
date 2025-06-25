# FILE START: kumir_exceptions.py
"""
Модуль для определения кастомных исключений интерпретатора Кумир.
Вынесен в отдельный файл для предотвращения циклических импортов.
"""


# Базовый класс для ошибок во время выполнения кода Кумира
class KumirExecutionError(Exception):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message)
        self.line_index = line_index
        self.column_index = column_index
        self.line_content = line_content

    def __str__(self):
        base_message = super().__str__()
        context = ""
        if self.line_index is not None:
            context += f"строка {self.line_index + 1}"
            if self.column_index is not None:
                context += f", столбец {self.column_index + 1}"

        if self.line_content is not None:
            if self.line_index is not None or self.column_index is not None:
                context += ":"
            context += f" \'{self.line_content}\'"
        return f"{base_message} ({context.strip()})" if context else base_message


# Ошибка робота (например, столкновение со стеной)
class RobotError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с объявлениями
class DeclarationError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с присваиванием
class AssignmentError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с вводом/выводом
class InputOutputError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Специальное исключение для запроса ввода
class KumirInputRequiredError(Exception):  # Не наследуем от KumirExecutionError, т.к. это не ошибка, а запрос
    def __init__(self, var_name, prompt, target_type):
        super().__init__(f"Требуется ввод для переменной {var_name} (тип {target_type}) с подсказкой: {prompt}")
        self.var_name = var_name
        self.prompt = prompt
        self.target_type = target_type


# Общая ошибка времени выполнения Кумир-программы
class KumirRuntimeError(KumirExecutionError): # Оставляем CapWords
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка типизации
class KumirTypeError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка значения (например, при преобразовании типов, выход за диапазон)
class KumirValueError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка вычисления выражения
class KumirEvalError(KumirRuntimeError):
    """Ошибка времени вычисления выражения."""
    pass

class KumirArgumentError(KumirValueError):
    """Ошибка в аргументах функции или процедуры."""
    pass

# Ошибка имени (например, использование необъявленной переменной)
class KumirNameError(KumirExecutionError): # ДОБАВЛЕНО
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Ошибка индексации (например, выход за границы массива)
class KumirIndexError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с файловыми операциями
class KumirFileError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с оператором ВОЗВРАТ
class KumirReturnError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Семантическая ошибка (например, несоответствие типов при вызове функции, неправильное использование конструкций)
class KumirSemanticError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Синтаксическая ошибка (добавлено)
class KumirSyntaxError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Ошибка: не реализовано
class KumirNotImplementedError(KumirExecutionError): # Добавлено, если еще не было
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Сигналы для управления потоком выполнения
class BreakSignal(Exception):
    """Сигнал для оператора ВЫХОД ИЗ ЦИКЛА."""
    pass

class ContinueSignal(Exception):
    """Сигнал для оператора ПРОДОЛЖИТЬ ЦИКЛ."""
    pass

class ReturnSignal(Exception):
    """Сигнал для оператора ВОЗВРАТ."""
    def __init__(self, value=None): # Может возвращать значение
        self.value = value
        super().__init__("Return signal with value: {}".format(value))

class ExitSignal(Exception):
    """Сигнал для оператора ВЫХОД (из процедуры/алгоритма)."""
    pass

class StopExecutionSignal(Exception): # Переименовано из StopExecutionException
    """Сигнал для полной остановки выполнения программы."""
    pass

# Убедимся, что LoopBreakException и LoopContinueException, если они использовались ранее,
# заменены на BreakSignal и ContinueSignal, или определены, если это отдельные концепции.
# Судя по предыдущим ошибкам, они были в from .exceptions import ...
# Если они были синонимами, то их можно удалить. Если нет - нужно их определить.
# Для простоты пока будем считать, что BreakSignal и ContinueSignal их заменяют.

# FILE END: kumir_exceptions.py