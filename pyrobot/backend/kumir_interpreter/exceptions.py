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


# ============================================================================
# Исключения для работы с пользовательскими функциями и процедурами
# ============================================================================

class AlgorithmRedefinitionError(KumirExecutionError):
    """Ошибка повторного определения алгоритма с тем же именем."""
    def __init__(self, algorithm_name, line_number=None, column_number=None):
        message = f"Алгоритм '{algorithm_name}' уже определён"
        super().__init__(message, line_number, column_number)


class ArgumentMismatchError(KumirExecutionError):
    """Ошибка несоответствия аргументов при вызове алгоритма."""
    def __init__(self, algorithm_name, expected_count, actual_count, line_number=None, column_number=None):
        message = f"Алгоритм '{algorithm_name}' ожидает {expected_count} аргументов, передано {actual_count}"
        super().__init__(message, line_number, column_number)


class AlgorithmNotFoundError(KumirExecutionError):
    """Ошибка вызова неопределённого алгоритма."""
    def __init__(self, algorithm_name, line_number=None, column_number=None):
        message = f"Алгоритм '{algorithm_name}' не определён"
        super().__init__(message, line_number, column_number)


class ReturnValueError(KumirExecutionError):
    """Ошибки, связанные с возвратом значений из функций."""
    def __init__(self, message, line_number=None, column_number=None):
        super().__init__(message, line_number, column_number)


class MissingReturnValueError(ReturnValueError):
    """Ошибка отсутствия возвращаемого значения в функции."""
    def __init__(self, function_name, line_number=None, column_number=None):
        message = f"Функция '{function_name}' должна возвращать значение через 'знач'"
        super().__init__(message, line_number, column_number)


class InvalidReturnValueError(ReturnValueError):
    """Ошибка использования 'знач' в процедуре."""
    def __init__(self, procedure_name, line_number=None, column_number=None):
        message = f"Процедура '{procedure_name}' не может возвращать значение через 'знач'"
        super().__init__(message, line_number, column_number)


class ParameterModificationError(KumirExecutionError):
    """Ошибка попытки изменения параметра-аргумента."""
    def __init__(self, parameter_name, line_number=None, column_number=None):
        message = f"Нельзя изменять значение параметра-аргумента '{parameter_name}'"
        super().__init__(message, line_number, column_number)


class ParameterTypeError(KumirExecutionError):
    """Ошибка несоответствия типа аргумента типу параметра."""
    def __init__(self, parameter_name, expected_type, actual_type, line_number=None, column_number=None):
        message = f"Параметр '{parameter_name}' ожидает тип '{expected_type}', получен '{actual_type}'"
        super().__init__(message, line_number, column_number)


class FunctionReturnException(Exception):
    """
    Исключение для реализации немедленного возврата из функции при выполнении 'знач := выражение'.
    
    Это исключение используется для прерывания выполнения тела функции и передачи
    возвращаемого значения обратно в место вызова.
    """
    
    def __init__(self, return_value):
        self.return_value = return_value
        super().__init__(f"Function returned value: {return_value}")
