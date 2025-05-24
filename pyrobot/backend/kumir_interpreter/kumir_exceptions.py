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


# Ошибка ввода-вывода (можно использовать существующий InputOutputError или этот, если нужна специфичная логика)
class KumirIOError(InputOutputError): # Наследуем от InputOutputError для согласованности
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибки парсера и лексера (обычно возникают до этапа выполнения)
class KumirSyntaxError(Exception): # Базовый для лексера и парсера, не наследуется от KumirExecutionError
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

class KumirLexerError(KumirSyntaxError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

class KumirParserError(KumirSyntaxError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Ошибка обращения к неопределенному имени (переменной, процедуре)
class KumirNameError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Ошибка, указывающая на нереализованную функциональность
class KumirNotImplementedError(KumirExecutionError):
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)


# Исключения для управления потоком выполнения (не ошибки)
class ControlFlowException(Exception):
    """Базовый класс для исключений, управляющих потоком выполнения."""
    pass

class BreakException(ControlFlowException):
    """Исключение для оператора break (или его аналога в Кумире)."""
    pass

class ContinueException(ControlFlowException):
    """Исключение для оператора continue (или его аналога в Кумире)."""
    pass

class ReturnValueException(ControlFlowException):
    """Исключение для возврата значения из функции или выхода из процедуры."""
    def __init__(self, value=None):
        super().__init__()
        self.value = value

# StopExecutionException определен ниже и наследуется от KumirExecutionError
# class StopExecutionException(ControlFlowException): 
#     """Исключение для оператора СТОП или других условий прекращения выполнения алгоритма."""
#     def __init__(self, message="Выполнение алгоритма прервано."):
#         super().__init__(message)

# Можно добавить другие специфичные ошибки при необходимости

class ProcedureExitCalled(KumirExecutionError): # Уже существует, просто для контекста
    pass

# Исключения для управления потоком в циклах
class LoopExitException(KumirExecutionError): # Уже существует, просто для контекста
    def __init__(self, message="Выход из цикла (LoopExitException)", line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

class LoopBreakException(LoopExitException): # Используется для команды ВЫХОД ИЗ ЦИКЛА - это определение оставляем
    """Исключение для команды ВЫХОД ИЗ ЦИКЛА."""
    def __init__(self, message="Выход из цикла по команде ВЫХОД ИЗ ЦИКЛА", line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

class LoopContinueException(KumirExecutionError): # Используется для команды ПРОДОЛЖИТЬ ЦИКЛ - это определение оставляем
    """Исключение для команды ПРОДОЛЖИТЬ ЦИКЛ."""
    def __init__(self, message="Переход к следующей итерации цикла по команде ПРОДОЛЖИТЬ ЦИКЛ", line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Добавляем недостающие исключения
class KumirSemanticError(KumirExecutionError):
    """Общая семантическая ошибка, не подпадающая под другие категории."""
    def __init__(self, message, line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

class StopExecutionException(KumirExecutionError):  # Было StopExecutionSignal(Exception) - это определение оставляем
    """Исключение для полной остановки выполнения программы (команда СТОП)."""
    def __init__(self, message="Выполнение программы остановлено командой СТОП", line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

class AssertionError_(KumirExecutionError):
    """Исключение для команды УТВЕРЖДЕНИЕ."""
    def __init__(self, message="Утверждение ложно", line_index=None, column_index=None, line_content=None):
        super().__init__(message, line_index, column_index, line_content)

# Ошибка времени выполнения Кумир (общая)
# class KumirRuntimeError(KumirExecutionError): # Это определение уже есть выше, удаляем дубликат

# FILE END: kumir_exceptions.py