from typing import Any
from .kumir_exceptions import KumirRuntimeError, KumirTypeError as KumirInvalidTypeException # Используем KumirTypeError как KumirInvalidTypeException

# KumirValue is now defined in kumir_datatypes.py

# Helper function (can be moved or expanded)
def get_kumir_type_name_from_py_value(py_value: Any) -> str:
    if isinstance(py_value, bool):
        return "ЛОГ"
    elif isinstance(py_value, int):
        return "ЦЕЛ"
    elif isinstance(py_value, float):
        return "ВЕЩ"
    elif isinstance(py_value, str):
        return "ЛИТ" # или СИМ, в зависимости от контекста, но ЛИТ чаще
    # Добавить другие типы по мере необходимости
    return "НЕИЗВЕСТНЫЙ_ТИП_PYTHON"

# Static methods from the old KumirValue can be standalone functions or part of other classes if more appropriate
def to_output_string(value: Any) -> str:
    from .kumir_datatypes import KumirValue # Local import to avoid circular dependency at module level
    if isinstance(value, bool):
        return "ДА" if value else "НЕТ"
    if isinstance(value, KumirValue):
        if value.kumir_type == "ЛОГ": # Сравнение со строкой
            return "ДА" if value.value else "НЕТ"
        return str(value.value) 
    return str(value)

def get_element_type_from_array_type(array_type_str: str) -> str:
    if array_type_str.startswith("ТАБ"):
        parts = array_type_str.split(" ")
        if len(parts) > 1:
            return parts[1] 
    return array_type_str 

def convert_string_to_type(s_value: str, kumir_type_str: str) -> Any:
    target_type = get_element_type_from_array_type(kumir_type_str)
    
    if target_type == "ЦЕЛ":
        try:
            return int(s_value)
        except ValueError:
            raise KumirInvalidTypeException(f"Невозможно преобразовать '{s_value}' в ЦЕЛ.")
    elif target_type == "ВЕЩ":
        try:
            return float(s_value.replace(',', '.'))
        except ValueError:
            raise KumirInvalidTypeException(f"Невозможно преобразовать '{s_value}' в ВЕЩ.")
    elif target_type == "ЛОГ":
        s_lower = s_value.strip().lower()
        if s_lower in ["да", "true", "истина"]:
            return True
        elif s_lower in ["нет", "false", "ложь"]:
            return False
        raise KumirInvalidTypeException(f"Невозможно преобразовать '{s_value}' в ЛОГ. Ожидается ДА или НЕТ.")
    elif target_type == "ЛИТ":
        return s_value
    else:
        raise KumirInvalidTypeException(f"Неизвестный или неподдерживаемый тип для ввода: {kumir_type_str}")

def are_types_compatible(type1_str: str, type2_str: str, for_assignment: bool = False) -> bool:
    if type1_str == type2_str:
        return True
    if for_assignment:
        if type1_str == "ВЕЩ" and type2_str == "ЦЕЛ":
            return True
    return False

class KumirTypeConverter:
    def to_python_bool(self, kumir_value_obj) -> bool: # kumir_value_obj is KumirValue from datatypes
        from .kumir_datatypes import KumirValue # Local import
        if not isinstance(kumir_value_obj, KumirValue):
            # Handle cases where it might not be a KumirValue object as expected
            # This might indicate an issue elsewhere or a need for broader type handling
            raise KumirInvalidTypeException(f"Expected KumirValue, got {type(kumir_value_obj)}")

        if kumir_value_obj.value is None:
            return False # Or raise error, depending on desired strictness
        if kumir_value_obj.kumir_type != "ЛОГ":
            raise KumirInvalidTypeException(f"Cannot convert {kumir_value_obj.kumir_type} to a boolean.")
        return bool(kumir_value_obj.value)

    def to_kumir_value(self, py_value, kumir_type_str: str):
        from .kumir_datatypes import KumirValue # Local import
        return KumirValue(py_value, kumir_type_str)

    def to_python_number(self, kumir_value_obj) -> (int | float): # kumir_value_obj is KumirValue from datatypes
        from .kumir_datatypes import KumirValue # Local import
        if not isinstance(kumir_value_obj, KumirValue):
            raise KumirInvalidTypeException(f"Expected KumirValue, got {type(kumir_value_obj)}")

        if kumir_value_obj.value is None:
            raise ValueError("KumirValue's internal value is None, cannot convert to number.")

        if kumir_value_obj.kumir_type == "ЦЕЛ":
            return int(kumir_value_obj.value)
        elif kumir_value_obj.kumir_type == "ВЕЩ":
            return float(kumir_value_obj.value)
        else:
            raise KumirInvalidTypeException(
                f"Значение типа '{kumir_value_obj.kumir_type}' не может быть преобразовано в число."
            )

class ErrorHandler:
    def __init__(self, interpreter):
        self.interpreter = interpreter
    def runtime_error(self, message, ctx):
        print(f"Runtime Error: {message} at line {ctx.start.line if ctx else 'N/A'}")
        raise KumirRuntimeError(message) # Используем KumirRuntimeError
    def type_error(self, message, ctx):
        print(f"Type Error: {message} at line {ctx.start.line if ctx else 'N/A'}")
        raise KumirInvalidTypeException(message)

class TypeDeterminer:
    def determine_type(self, py_value) -> str: # Возвращает строку вместо KumirType
        if isinstance(py_value, bool):
            return "ЛОГ"
        elif isinstance(py_value, int):
            return "ЦЕЛ"
        elif isinstance(py_value, float):
            return "ВЕЩ"
        elif isinstance(py_value, str):
            return "ЛИТ" 
        return "НЕИЗВЕСТНЫЙ" # Строковое значение по умолчанию
