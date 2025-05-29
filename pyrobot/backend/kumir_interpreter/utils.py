from typing import Any, Dict, Tuple, List, Optional, Union # <--- ДОБАВЛЕН Union

from .kumir_datatypes import KumirValue, KumirType
from .kumir_exceptions import KumirTypeError, KumirSemanticError, KumirRuntimeError # Добавила KumirRuntimeError

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
        elif value.kumir_type == "ВЕЩ" and isinstance(value.value, float):
            # Для вещественных чисел: если это целое число (7.0), выводим как целое (7)
            if value.value == float(int(value.value)):
                return str(int(value.value))
            else:
                return str(value.value)
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
            raise KumirTypeError(f"Невозможно преобразовать '{s_value}' в ЦЕЛ.")
    elif target_type == "ВЕЩ":
        try:
            return float(s_value.replace(',', '.'))
        except ValueError:
            raise KumirTypeError(f"Невозможно преобразовать '{s_value}' в ВЕЩ.")
    elif target_type == "ЛОГ":
        s_lower = s_value.strip().lower()
        if s_lower in ["да", "true", "истина"]:
            return True
        elif s_lower in ["нет", "false", "ложь"]:
            return False
        raise KumirTypeError(f"Невозможно преобразовать '{s_value}' в ЛОГ. Ожидается ДА или НЕТ.")
    elif target_type == "ЛИТ":
        return s_value
    else:
        raise KumirTypeError(f"Неизвестный или неподдерживаемый тип для ввода: {kumir_type_str}")

def are_types_compatible(type1_str: str, type2_str: str, for_assignment: bool = False) -> bool:
    if type1_str == type2_str:
        return True
    if for_assignment:
        if type1_str == "ВЕЩ" and type2_str == "ЦЕЛ":
            return True
    return False

class KumirTypeConverter:
    def __init__(self, scope_manager=None):
        self.scope_manager = scope_manager

    def to_python_bool(self, val: KumirValue) -> bool:
        if val.kumir_type == KumirType.BOOL.value:
            return bool(val.value)
        elif val.kumir_type == KumirType.INT.value:
            return val.value != 0
        elif val.kumir_type == KumirType.REAL.value:
            return val.value != 0.0
        # Для ЛИТ и других типов Кумира преобразование в ЛОГ не определено стандартно,
        # кроме как через сравнение с пустым значением или специфические функции,
        # которых в базовом Кумире нет для автоматического приведения.
        # Обычно Кумир требует явного сравнения для получения ЛОГ из ЛИТ.
        # Если нужно строгое поведение, здесь можно выбросить KumirTypeError.
        # Пока что, для совместимости с некоторыми языками, где непустая строка это true:
        elif val.kumir_type == KumirType.STR.value:
             # В Кумире строки не приводятся к ЛОГ напрямую.
             # Это поведение может быть нежелательным.
             # Для строгого соответствия Кумиру, здесь должна быть ошибка.
            raise KumirTypeError(f"Невозможно преобразовать ЛИТ '{val.value}' в ЛОГ напрямую.", None) # None - контекст ошибки, если есть
        else:
            raise KumirTypeError(f"Невозможно преобразовать тип {val.kumir_type} в ЛОГ.", None)

    def to_python_number(self, val: KumirValue) -> Union[int, float]:
        if val.kumir_type == KumirType.INT.value:
            return int(val.value)
        elif val.kumir_type == KumirType.REAL.value:
            return float(val.value)
        # В Кумире ЛОГ не преобразуется в число напрямую (ДА=1, НЕТ=0 не стандартно)
        # ЛИТ тоже не преобразуется в число напрямую без спец. функций.
        else:
            raise KumirTypeError(f"Невозможно преобразовать тип {val.kumir_type} в число (ЦЕЛ/ВЕЩ).", None)

    def to_string_for_display(self, val: KumirValue) -> str:
        if val is None or val.kumir_type == KumirType.UNKNOWN.value:
            return "НЕОПРЕД"

        # val.kumir_type это уже строка типа "ЦЕЛ", "ВЕЩ" и т.д.
        if val.kumir_type == KumirType.INT.value:
            return str(val.value)
        elif val.kumir_type == KumirType.REAL.value:
            return str(val.value)
        elif val.kumir_type == KumirType.BOOL.value:
            return "да" if val.value else "нет"
        elif val.kumir_type == KumirType.STR.value:
            return val.value # val.value уже строка
        elif val.kumir_type == KumirType.TABLE.value:
            # TODO: Реализовать корректный вывод массива в строку
            # Пока что так, чтобы не было ошибки. Позже нужно будет итерировать элементы.
            if isinstance(val.value, dict): # Предполагаем, что KumirTableVar.data это dict
                # Это очень упрощенный вывод, просто чтобы что-то было
                return "[" + ", ".join(map(str, val.value.values())) + "]" 
            return "<МАССИВ>"
        else:
            raise KumirTypeError(f"Неподдерживаемый тип для отображения: {val.kumir_type}", None)

    def convert_string_to_kumir_value(self, input_str: str, target_type_str: str, ctx_for_error: Any) -> KumirValue:
        # target_type_str это уже строка типа "ЦЕЛ", "ВЕЩ" и т.д.
        try:
            stripped_input = input_str.strip()
            if target_type_str == KumirType.INT.value:
                return KumirValue(int(stripped_input), KumirType.INT.value)
            elif target_type_str == KumirType.REAL.value:
                return KumirValue(float(stripped_input.replace(',', '.')), KumirType.REAL.value)
            elif target_type_str == KumirType.BOOL.value:
                val_lower = stripped_input.lower()
                if val_lower == "да":
                    return KumirValue(True, KumirType.BOOL.value)
                elif val_lower == "нет":
                    return KumirValue(False, KumirType.BOOL.value)
                else:
                    raise ValueError("Логическое значение должно быть 'да' или 'нет'")
            elif target_type_str == KumirType.STR.value:
                return KumirValue(input_str, KumirType.STR.value) # Для ЛИТ тип строка "как есть"
            else:
                raise KumirTypeError(f"Невозможно преобразовать строку в неизвестный тип: {target_type_str}", ctx_for_error)
        except ValueError as e:
            raise KumirTypeError(f'Ошибка преобразования строки "{input_str}" в тип {target_type_str}: {e}', ctx_for_error)

class ErrorHandler:
    def __init__(self, interpreter):
        self.interpreter = interpreter
    def runtime_error(self, message, ctx):
        print(f"Runtime Error: {message} at line {ctx.start.line if ctx else 'N/A'}")
        raise KumirRuntimeError(message) # Используем KumirRuntimeError
    def type_error(self, message, ctx):
        print(f"Type Error: {message} at line {ctx.start.line if ctx else 'N/A'}")
        raise KumirTypeError(message)

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
