from .kumir_exceptions import KumirEvalError

class KumirTableVar:
    def __init__(self, base_kumir_type_name, dimension_bounds_list, ctx):
        # base_kumir_type_name: 'ЦЕЛ', 'ВЕЩ', 'ЛИТ', 'ЛОГ', 'СИМ' (нормализованный)
        # dimension_bounds_list: список кортежей, например, [(-5, 5), (1, 10)] для 2D
        # ctx: контекст объявления для информации об ошибках (строка, столбец)
        self.base_kumir_type_name = base_kumir_type_name
        self.dimension_bounds_list = dimension_bounds_list
        self.dimensions = len(dimension_bounds_list)
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
        
        # TODO: Здесь должна быть проверка типа 'value' на совместимость с self.base_kumir_type_name
        # KumirValueType.get_kumir_type(value) поможет определить тип Python-значения.
        # Затем сравнить с self.base_kumir_type_name.

        self.data[indices_tuple] = value 