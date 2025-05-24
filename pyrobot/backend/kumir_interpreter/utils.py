from typing import Any

class KumirValue:
    def __init__(self, value: Any, type_str: str):
        self.value = value
        self.type = type_str # "ЦЕЛ", "ВЕЩ", "ЛОГ", "ЛИТ", "ТАБ ЛИТ ИЗ [1:10]", etc.

    def __str__(self) -> str:
        if self.type == "ЛОГ":
            return "ДА" if self.value else "НЕТ"
        elif isinstance(self.value, list): # Для массивов
            return f"[{', '.join(map(str, self.value))}]" # Упрощенный вывод
        return str(self.value)

    @staticmethod
    def to_output_string(value: Any) -> str:
        if isinstance(value, bool):
            return "ДА" if value else "НЕТ"
        if isinstance(value, KumirValue):
            if value.type == "ЛОГ":
                return "ДА" if value.value else "НЕТ"
            return str(value.value) # Выводим внутреннее значение для KumirValue
        return str(value)

    @staticmethod
    def get_element_type_from_array_type(array_type_str: str) -> str:
        # Пример: "ТАБ ЛИТ ИЗ [1:10]" -> "ЛИТ"
        # "ТАБ ЦЕЛ ИЗ [1:5, 1:3]" -> "ЦЕЛ"
        if array_type_str.startswith("ТАБ"):
            parts = array_type_str.split(" ")
            if len(parts) > 1:
                return parts[1] # Тип элемента
        return array_type_str # Если не ТАБ, или формат не тот, возвращаем как есть (может быть простой тип)

    @staticmethod
    def convert_string_to_type(s_value: str, kumir_type: str) -> Any:
        target_type = KumirValue.get_element_type_from_array_type(kumir_type) # Для случаев типа "ТАБ ЛИТ ..."
        
        if target_type == "ЦЕЛ":
            try:
                return int(s_value)
            except ValueError:
                raise KumirTypeError(f"Невозможно преобразовать '{s_value}' в ЦЕЛ.")
        elif target_type == "ВЕЩ":
            try:
                # Кумир использует запятую как десятичный разделитель
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
            return s_value # Строки остаются строками
        else:
            # Для ТАБ и других сложных типов, сам ввод строки не создает их.
            # Этот метод для преобразования *одного* значения.
            raise KumirTypeError(f"Неизвестный или неподдерживаемый тип для ввода: {kumir_type}")

    @staticmethod
    def are_types_compatible(type1: str, type2: str, for_assignment: bool = False) -> bool:
        """
        Проверяет совместимость двух типов Кумира.
        type1 - тип значения, которое присваивается или передается.
        type2 - тип переменной или параметра, которому присваивается.
        for_assignment=True означает, что ЦЕЛ можно присвоить ВЕЩ.
        """
        # Простое сравнение строк для начала
        if type1 == type2:
            return True
        
        # Совместимость для присваивания: ЦЕЛ -> ВЕЩ
        if for_assignment and type1 == "ЦЕЛ" and type2 == "ВЕЩ":
            return True
        
        # TODO: Добавить более сложные правила совместимости, если они есть в Кумире
        # (например, для массивов одинакового типа, но разных размеров - обычно несовместимы)
        return False
