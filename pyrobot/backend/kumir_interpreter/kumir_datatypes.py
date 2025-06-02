from typing import Any, Dict, List, Optional, Union
from .kumir_exceptions import KumirEvalError, KumirTypeError 
from enum import Enum

class KumirType(Enum):
    INT = "ЦЕЛ"
    REAL = "ВЕЩ"
    BOOL = "ЛОГ"
    STR = "ЛИТ"
    CHAR = "СИМ"  # Добавлен тип CHAR
    TABLE = "ТАБ"
    COLOR = "ЦВЕТ" # Добавлен тип COLOR
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
        if normalized_type_str == "СИМВОЛ": # Добавлена обработка для "СИМВОЛ"
            return KumirType.CHAR
        if normalized_type_str == "ЦВЕТ": # Добавлена обработка для "ЦВЕТ"
            return KumirType.COLOR
        
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
    def __init__(self, value: Any, kumir_type: str): # kumir_type должен быть строкой, например, KumirType.INT.value
        self.value: Any = value
        self.kumir_type: str = kumir_type 

    def __repr__(self) -> str:
        return f"KumirValue(value={self.value!r}, kumir_type='{self.kumir_type}')"

    def __str__(self) -> str:
        # For practical purposes, often we just need the string representation of the value
        if self.kumir_type == KumirType.BOOL.value: # Сравнение с .value для строки "ЛОГ"
            return "да" if self.value else "нет"
        return str(self.value)

    def to_kumir_string_representation(self) -> str:
        """
        Returns the string representation of the value as it would appear in Kumir.
        e.g., True -> "да", False -> "нет"
        """
        if self.kumir_type == KumirType.BOOL.value:
            return "да" if self.value else "нет"
        elif self.kumir_type == KumirType.STR.value:
            # В Кумире строки обычно выводятся без дополнительных кавычек, если это значение переменной.
            # Литералы строк в коде имеют кавычки. Для вывода значения - просто содержимое.
            return str(self.value)
        # Для INT и REAL, стандартное преобразование в строку подходит.
        # Кумир может иметь специфичное форматирование для ВЕЩ (например, запятая как разделитель),
        # но пока что просто str(). Это может потребовать доработки для точного соответствия.
        return str(self.value)

class KumirTableVar:
    def __init__(self, element_kumir_type: str, dimension_bounds_list: List[tuple[int, int]], ctx: Any):
        # element_kumir_type: 'ЦЕЛ', 'ВЕЩ', 'ЛИТ', 'ЛОГ' (нормализованный)
        # dimension_bounds_list: список кортежей, например, [(-5, 5), (1, 10)] для 2D
        # ctx: контекст объявления для информации об ошибках (строка, столбец)
        self.element_kumir_type: str = element_kumir_type # ИЗМЕНЕНО
        # Добавляем kumir_type как алиас для обратной совместимости
        self.kumir_type: str = element_kumir_type  # ИСПРАВЛЕНИЕ AttributeError
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

    def get_value(self, indices_tuple, access_ctx) -> KumirValue: # Добавляем type hint для возвращаемого значения
        self._validate_indices(indices_tuple, access_ctx)
        
        if indices_tuple not in self.data:
            # Элемент не инициализирован. В Кумире это ошибка при чтении.
            # В некоторых реализациях может быть значение по умолчанию, но стандарт требует инициализации.
            pos = (access_ctx.start.line, access_ctx.start.column) if access_ctx and hasattr(access_ctx, 'start') else (None, None)
            raise KumirEvalError(
                f"Попытка чтения неинициализированного элемента таблицы по индексам {indices_tuple}.",
                line_index=pos[0], column_index=pos[1]
            )
        # Ожидаем, что в self.data уже хранится KumirValue благодаря set_value
        return self.data[indices_tuple]

    def set_value(self, indices_tuple, value: Any, access_ctx: Any):
        self._validate_indices(indices_tuple, access_ctx)
        
        final_value_to_store: KumirValue
        pos_line = access_ctx.start.line if access_ctx and hasattr(access_ctx, 'start') else None
        pos_col = access_ctx.start.column if access_ctx and hasattr(access_ctx, 'start') else None

        if isinstance(value, KumirValue):
            # Значение уже KumirValue
            if value.kumir_type == self.element_kumir_type:
                final_value_to_store = value
            elif self.element_kumir_type == KumirType.REAL.value and value.kumir_type == KumirType.INT.value:
                # Неявное преобразование ЦЕЛ -> ВЕЩ при присваивании в ячейку ВЕЩ
                final_value_to_store = KumirValue(float(value.value), KumirType.REAL.value)
            else:
                raise KumirTypeError(
                    f"Несовместимый тип для элемента таблицы. Ожидается '{self.element_kumir_type}', получен '{value.kumir_type}'.",
                    line_index=pos_line, column_index=pos_col
                )
        else:
            # Значение - это Python-значение. Проверяем и оборачиваем.
            py_value = value
            target_kumir_type_str = self.element_kumir_type

            if target_kumir_type_str == KumirType.INT.value:
                if not isinstance(py_value, int):
                    raise KumirTypeError(f"Значение для ячейки таблицы типа '{target_kumir_type_str}' должно быть целым числом (int), получено {type(py_value).__name__}.", line_index=pos_line, column_index=pos_col)
                final_value_to_store = KumirValue(py_value, target_kumir_type_str)
            elif target_kumir_type_str == KumirType.REAL.value:
                if not isinstance(py_value, (int, float)):
                    raise KumirTypeError(f"Значение для ячейки таблицы типа '{target_kumir_type_str}' должно быть числом (int, float), получено {type(py_value).__name__}.", line_index=pos_line, column_index=pos_col)
                # Если Python int присваивается в ВЕЩ ячейку, преобразуем в float
                final_value_to_store = KumirValue(float(py_value), target_kumir_type_str)
            elif target_kumir_type_str == KumirType.BOOL.value:
                if not isinstance(py_value, bool):
                    raise KumirTypeError(f"Значение для ячейки таблицы типа '{target_kumir_type_str}' должно быть логическим (bool), получено {type(py_value).__name__}.", line_index=pos_line, column_index=pos_col)
                final_value_to_store = KumirValue(py_value, target_kumir_type_str)
            elif target_kumir_type_str == KumirType.STR.value:
                if not isinstance(py_value, str):
                    raise KumirTypeError(f"Значение для ячейки таблицы типа '{target_kumir_type_str}' должно быть строкой (str), получено {type(py_value).__name__}.", line_index=pos_line, column_index=pos_col)
                final_value_to_store = KumirValue(py_value, target_kumir_type_str)
            else:
                # Для неизвестных или не базовых типов element_kumir_type (маловероятно для типизированных таблиц)
                # TODO: Рассмотреть, как обрабатывать более сложные типы, если они появятся для элементов таблиц
                raise KumirTypeError(f"Неподдерживаемый тип элемента таблицы для присваивания Python-значения: '{target_kumir_type_str}'.", line_index=pos_line, column_index=pos_col)

        self.data[indices_tuple] = final_value_to_store

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