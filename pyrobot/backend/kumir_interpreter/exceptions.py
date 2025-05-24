# pyrobot/backend/kumir_interpreter/exceptions.py

class KumirExecutionError(RuntimeError):
    """Базовый класс для ошибок времени выполнения в интерпретаторе Кумира."""
    def __init__(self, message, line_number=None, column_number=None):
        super().__init__(message)
        self.line_number = line_number
        self.column_number = column_number
        self.message = message

    def __str__(self):
        if self.line_number is not None:
            return f"Ошибка выполнения (строка {self.line_number}): {self.message}"
        return f"Ошибка выполнения: {self.message}"

class BreakSignal(Exception):
    """Сигнал для выхода из цикла (оператор 'выход' внутри цикла)."""
    pass

class ContinueSignal(Exception): # Хотя пока не используется, но может пригодиться для 'продолжить'
    """Сигнал для перехода к следующей итерации цикла (если бы был оператор 'продолжить')."""
    pass

class ExitSignal(Exception):
    """Сигнал для завершения выполнения текущего алгоритма или всей программы ('выход' вне цикла)."""
    pass

class ReturnSignal(Exception):
    """Сигнал для возврата из процедуры или функции ('возврат')."""
    def __init__(self, value=None):
        self.value = value
        super().__init__("ReturnSignal") # Сообщение не так важно, главное - значение

class KumirNotImplementedError(KumirExecutionError):
    """Исключение для функциональности, которая еще не реализована."""
    def __init__(self, message="Функциональность еще не реализована", line_number=None, column_number=None):
        super().__init__(message, line_number, column_number)

# Можно добавить другие специфичные исключения по мере необходимости,
# например, для ошибок типизации, деления на ноль, выхода за границы массива и т.д.
# class DivisionByZeroError(KumirExecutionError):
#     def __init__(self, line_number=None, column_number=None):
#         super().__init__("Деление на ноль", line_number, column_number)

# class TypeMismatchError(KumirExecutionError):
#     def __init__(self, message, line_number=None, column_number=None):
#         super().__init__(message, line_number, column_number)

# classOutOfBoundsError(KumirExecutionError):
#     def __init__(self, message="Выход за границы массива", line_number=None, column_number=None):
#         super().__init__(message, line_number, column_number)
