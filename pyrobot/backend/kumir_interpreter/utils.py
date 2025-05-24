from typing import Any
from .kumir_exceptions import KumirRuntimeError, KumirTypeError as KumirInvalidTypeException # Используем KumirTypeError как KumirInvalidTypeException

class KumirValue:
    def __init__(self, value: Any, type_str: str): # type_str вместо KumirType
        self.value = value
        self.type = type_str # "ЦЕЛ", "ВЕЩ", "ЛОГ", "ЛИТ", "ТАБ ЛИТ ИЗ [1:10]", etc.

    def __str__(self) -> str:
        if self.type == "ЛОГ": # Сравнение со строкой
            return "ДА" if self.value else "НЕТ"
        elif isinstance(self.value, list): # Для массивов
            return f"[{', '.join(map(str, self.value))}]" # Упрощенный вывод
        return str(self.value)

    @staticmethod
    def to_output_string(value: Any) -> str:
        if isinstance(value, bool):
            return "ДА" if value else "НЕТ"
        if isinstance(value, KumirValue):
            if value.type == "ЛОГ": # Сравнение со строкой
                return "ДА" if value.value else "НЕТ"
            return str(value.value) 
        return str(value)

    @staticmethod
    def get_element_type_from_array_type(array_type_str: str) -> str:
        if array_type_str.startswith("ТАБ"):
            parts = array_type_str.split(" ")
            if len(parts) > 1:
                return parts[1] 
        return array_type_str 

    @staticmethod
    def convert_string_to_type(s_value: str, kumir_type_str: str) -> Any: # kumir_type_str вместо kumir_type
        target_type = KumirValue.get_element_type_from_array_type(kumir_type_str)
        
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

    @staticmethod
    def are_types_compatible(type1_str: str, type2_str: str, for_assignment: bool = False) -> bool: # строки вместо KumirType
        # Простое сравнение строк для начала
        if type1_str == type2_str:
            return True
        # Можно добавить правила совместимости (например, ЦЕЛ и ВЕЩ)
        if for_assignment:
            if type1_str == "ВЕЩ" and type2_str == "ЦЕЛ": # Присваивание ЦЕЛ в ВЕЩ
                return True
        return False

class KumirTypeConverter:
    def to_python_bool(self, kumir_value: KumirValue) -> bool:
        if kumir_value is None or kumir_value.value is None:
            return False
        if kumir_value.type != "ЛОГ": # Сравнение со строкой
            raise KumirInvalidTypeException(f"Cannot convert {kumir_value.type} to a boolean.")
        return bool(kumir_value.value)

    def to_kumir_value(self, py_value, kumir_type_str: str) -> KumirValue: # kumir_type_str вместо KumirType
        return KumirValue(py_value, kumir_type_str)

    def to_python_number(self, kumir_value: KumirValue) -> (int | float):
        if kumir_value is None or kumir_value.value is None:
            raise ValueError("KumirValue is None or its internal value is None, cannot convert to number.")

        if kumir_value.type == "ЦЕЛ": # Сравнение со строкой
            return int(kumir_value.value)
        elif kumir_value.type == "ВЕЩ": # Сравнение со строкой
            return float(kumir_value.value)
        else:
            # kumir_value.type уже строка, так что .name не нужен
            raise KumirInvalidTypeException(
                f"Значение типа '{kumir_value.type}' не может быть преобразовано в число."
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
