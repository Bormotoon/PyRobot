from typing import Any, Dict, List, Optional, Union
from .kumir_exceptions import KumirEvalError
from enum import Enum

class KumirType(Enum):
    INT = "ЦЕЛ"
    REAL = "ВЕЩ"
    BOOL = "ЛОГ"
    STR = "ЛИТ"
    TABLE = "ТАБ"
    VOID = "VOID" # For procedures that don't return a value
    FUNC_ID = "FUNC_ID" # For identifying a function name before call
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def from_string(type_str: str) -> 'KumirType':
        """
        Converts a string representation of a Kumir type to a KumirType enum member.
        Handles variations in case and common abbreviations.
        """
        normalized_type_str = type_str.strip().upper()
        # Handle common full names first
        if normalized_type_str == "ЦЕЛОЕ":
            return KumirType.INT
        if normalized_type_str == "ВЕЩЕСТВЕННОЕ":
            return KumirType.REAL
        if normalized_type_str == "ЛОГИЧЕСКОЕ":
            return KumirType.BOOL
        if normalized_type_str == "ЛИТЕРА": # Кумир использует "лит" для типа и "сим" для символа в строке
            return KumirType.STR
        
        # Handle enum values (ЦЕЛ, ВЕЩ, etc.)
        for kumir_type in KumirType:
            if kumir_type.value == normalized_type_str:
                return kumir_type
        
        # Handle potential table types like "ТАБ ЦЕЛ", "ТАБ ВЕЩ"
        if normalized_type_str.startswith("ТАБ "):
            return KumirType.TABLE # For now, just identify it as TABLE. Specific element type handling is elsewhere.

        # Fallback for unknown types
        # Consider raising an error or returning UNKNOWN based on strictness needs
        # For now, let's return UNKNOWN to avoid crashing if a new type appears
        # or if a more complex type string (like for specific table types) is passed.
        # This part might need adjustment based on how type strings are generated/used.
        # print(f"Warning: Unknown Kumir type string encountered: '{type_str}'") # Optional: for debugging
        return KumirType.UNKNOWN

class KumirValue:
    """
    Represents a value in the Kumir language, encapsulating both the
    Python-level value and its Kumir type.
    """
    def __init__(self, value: Any, kumir_type: str):
        self.value: Any = value
        self.kumir_type: str = kumir_type # "ЦЕЛ", "ВЕЩ", "ЛОГ", "СИМ", "ТАБ"

    def __repr__(self) -> str:
        return f"KumirValue(value={self.value!r}, kumir_type='{self.kumir_type}')"

    def __str__(self) -> str:
        # For practical purposes, often we just need the string representation of the value
        if self.kumir_type == "ЛОГ":
            return "да" if self.value else "нет"
        return str(self.value)

class KumirTableVar:
    def __init__(self, element_kumir_type: str, dimension_bounds_list: List[tuple[int, int]], ctx: Any): # ИЗМЕНЕНО: base_kumir_type_name -> element_kumir_type, добавлены type hints
        # element_kumir_type: 'ЦЕЛ', 'ВЕЩ', 'ЛИТ', 'ЛОГ' (нормализованный)
        # dimension_bounds_list: список кортежей, например, [(-5, 5), (1, 10)] для 2D
        # ctx: контекст объявления для информации об ошибках (строка, столбец)
        self.element_kumir_type: str = element_kumir_type # ИЗМЕНЕНО
        self.dimension_bounds_list: List[tuple[int, int]] = dimension_bounds_list # Добавлен type hint
        self.dimensions: int = len(dimension_bounds_list) # Добавлен type hint
        self.declaration_ctx = ctx # Сохраняем контекст для возможных ошибок
        self.data = {}  # Хранит актуальные данные, ключи - кортежи индексов

        for i, (min_idx, max_idx) in enumerate(self.dimension_bounds_list):
            if not (isinstance(min_idx, int) and isinstance(max_idx, int)):
                raise KumirEvalError(
                    f"Границы измерения {i+1} для таблицы должны быть целыми числами.",
                    self.declaration_ctx.start.line, self.declaration_ctx.start.column
                )
            if min_idx > max_idx:
                raise KumirEvalError(
                    f"Неверные границы для измерения {i+1} таблицы: минимальный индекс {min_idx} > максимального индекса {max_idx}.",
                    self.declaration_ctx.start.line, self.declaration_ctx.start.column
                )

    def _validate_indices(self, indices_tuple, access_ctx):
        # access_ctx: контекст доступа к элементу для информации об ошибках
        if not isinstance(indices_tuple, tuple):
            raise KumirEvalError(
                "Внутренняя ошибка: индексы таблицы должны быть кортежем.",
                access_ctx.start.line, access_ctx.start.column
            )

        if len(indices_tuple) != self.dimensions:
            raise KumirEvalError(
                f"Неверное количество индексов для таблицы. Ожидается {self.dimensions}, получено {len(indices_tuple)}.",
                access_ctx.start.line, access_ctx.start.column
            )

        for i, index_val in enumerate(indices_tuple):
            if not isinstance(index_val, int):
                raise KumirEvalError(
                    f"Индекс для измерения {i+1} должен быть целым числом. Получено: '{index_val}' (тип: {type(index_val).__name__}).",
                    access_ctx.start.line, access_ctx.start.column
                )
            
            min_bound, max_bound = self.dimension_bounds_list[i]
            if not (min_bound <= index_val <= max_bound):
                raise KumirEvalError(
                    f"Индекс [{index_val}] вне допустимых границ [{min_bound}:{max_bound}] для измерения {i+1}.",
                    access_ctx.start.line, access_ctx.start.column
                )
        return True

    def get_value(self, indices_tuple, access_ctx):
        self._validate_indices(indices_tuple, access_ctx)
        
        if indices_tuple not in self.data:
            raise KumirEvalError(
                f"Попытка чтения неинициализированного элемента таблицы по индексам {indices_tuple}.",
                access_ctx.start.line, access_ctx.start.column
            )
        return self.data[indices_tuple]

    def set_value(self, indices_tuple, value, access_ctx):
        self._validate_indices(indices_tuple, access_ctx)
        
        # TODO: Здесь должна быть проверка типа \\\'value\\\' на совместимость с self.element_kumir_type
        # KumirValueType.get_kumir_type(value) поможет определить тип Python-значения.
        # Затем сравнить с self.element_kumir_type.

        self.data[indices_tuple] = value

class KumirVariable:
    """
    Represents a variable in the Kumir language, which can be a simple value or a table.
    """
    def __init__(self, name: str, kumir_type: str, value: Any, is_table: bool = False, 
                 table_def: Optional['KumirTableVar'] = None, 
                 element_type_name: Optional[str] = None): # element_type_name теперь соответствует KumirTableVar.element_kumir_type
        self.name: str = name
        self.kumir_type: str = kumir_type 
        self.value: Any = value 
        self.is_table: bool = is_table
        self.table_def: Optional[KumirTableVar] = table_def 
        # Для таблиц element_type_name должен совпадать с table_def.element_kumir_type, если table_def задан
        self.element_type_name: Optional[str] = element_type_name if element_type_name else (table_def.element_kumir_type if table_def else None) # ИЗМЕНЕНО

    def __repr__(self) -> str:
        if self.is_table:
            return f"KumirVariable(name='{self.name}', kumir_type='{self.kumir_type}', is_table=True, element_type='{self.element_type_name}')"
        else:
            return f"KumirVariable(name='{self.name}', kumir_type='{self.kumir_type}', value={self.value!r})"

class KumirReturnValue:
    """Класс для инкапсуляции возвращаемого значения из функции Кумира."""
    def __init__(self, value: Any, type: str):
        self.value = value
        self.type = type # Строковое представление типа Кумира, например, \\\'цел\\\', \\\'вещ\\\'

    def __repr__(self):
        return f"KumirReturnValue(value={self.value!r}, type=\'{self.type}\')"

class KumirFunction:
    """Заглушка для представления функции Кумира."""
    def __init__(self, name: str, parameters: List[Any], body_ctx: Any, return_type: str, 
                 scope_manager: Any, type_converter: Any = None, error_handler: Any = None): # Упрощенные параметры
        self.name = name
        self.parameters = parameters # Список (имя_параметра, тип_параметра, режим_параметра)
        self.body_ctx = body_ctx # Контекст тела функции для выполнения
        self.return_type = return_type # Ожидаемый тип возвращаемого значения
        self.scope_manager = scope_manager # Для создания локальной области видимости при вызове
        self.type_converter = type_converter
        self.error_handler = error_handler

    def __repr__(self) -> str:
        return f"<KumirFunction name='{self.name}'>"

class KumirTable:
    """Заглушка для представления таблицы Кумира (как типа, а не переменной). 
       KumirTableVar используется для экземпляров таблиц."""
    def __init__(self, name: str, element_type: str, dimensions: int):
        self.name = name # Например, "таб цел"
        self.element_type = element_type # Например, "цел"
        self.dimensions = dimensions # Количество измерений

    def __repr__(self) -> str:
        return f"<KumirTable name='{self.name}' element_type='{self.element_type}' dimensions={self.dimensions}>"