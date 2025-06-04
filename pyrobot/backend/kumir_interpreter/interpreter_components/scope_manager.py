# Scope and variable management functions 
from typing import Any, Tuple, Optional, Dict, List
from antlr4 import ParserRuleContext
import sys # Добавлено для print в error_stream

from ..kumir_exceptions import DeclarationError, KumirEvalError, KumirIndexError, KumirTypeError, KumirNameError
from ..kumir_datatypes import KumirType, KumirValue, KumirTableVar


# Вспомогательный класс для передачи информации о позиции в KumirTableVar
class DummyCtx:
    def __init__(self, line: int, column: int):
        class Start:
            def __init__(self, line: int, column: int):
                self.line = line
                self.column = column
        # KumirTableVar ожидает line 1-based, column 0-based (как ctx.start)
        self.start = Start(line, column)


def get_default_value(kumir_type: KumirType) -> KumirValue:
    """Возвращает KumirValue по умолчанию для данного KumirType."""
    if kumir_type == KumirType.INT:
        return KumirValue(0, KumirType.INT.value)
    if kumir_type == KumirType.REAL:
        return KumirValue(0.0, KumirType.REAL.value)
    if kumir_type == KumirType.BOOL:
        return KumirValue(False, KumirType.BOOL.value)
    if kumir_type == KumirType.CHAR:
        return KumirValue(None, KumirType.CHAR.value) 
    if kumir_type == KumirType.STR:
        return KumirValue("", KumirType.STR.value)
    if kumir_type == KumirType.COLOR: 
        return KumirValue("БЕЛЫЙ", KumirType.COLOR.value) 
    return KumirValue(None, kumir_type.value) 


class ScopeManager:
    def __init__(self, visitor_ref):
        self.visitor = visitor_ref  # Ссылка на основной KumirInterpreterVisitor
        self.scopes: List[Dict[str, Any]] = [{}]  # Глобальная область видимости
        # Структура для хранения информации о переменной:
        # {
        #   'name_original': str, 
        #   'kumir_type': KumirType, # KumirType enum для простых типов ИЛИ ТИП ЭЛЕМЕНТОВ для таблиц
        #   'value': KumirValue | KumirTableVar, 
        #   'is_table': bool,
        #   'initialized': bool,
        #   'line_declared': int, 
        #   'col_declared': int   
        # }

    def get_program_lines_for_error(self):
        # Helper to safely access program_lines from the visitor
        if hasattr(self.visitor, 'program_lines') and self.visitor.program_lines:
            return self.visitor.program_lines
        return []

    # Вспомогательный метод для получения строки кода по индексам (0-based)
    def get_line_content_from_coords(self, line_index_0_based: Optional[int]) -> Optional[str]:
        program_lines = self.get_program_lines_for_error()
        if line_index_0_based is not None and program_lines:
            if 0 <= line_index_0_based < len(program_lines):
                return program_lines[line_index_0_based]
        return None

    def get_line_content_from_ctx(self, ctx: Optional[ParserRuleContext]) -> Optional[str]:
        program_lines = self.get_program_lines_for_error()
        if ctx and ctx.start and program_lines:
            line_num_0_indexed = ctx.start.line - 1
            if 0 <= line_num_0_indexed < len(program_lines):
                return program_lines[line_num_0_indexed]
        return None

    def enter_scope(self) -> None:
        """Входит в новую локальную область видимости."""
        self.scopes.append({})
        # print(f"[DEBUG][ScopeManager] Вошли в область уровня {len(self.scopes)}", file=sys.stderr)

    def push_scope(self) -> None:
        """Синоним для enter_scope."""
        self.enter_scope()

    def exit_scope(self) -> None:
        """Выходит из текущей локальной области видимости."""
        if len(self.scopes) > 1:
            # print(f"[DEBUG][ScopeManager] Вышли из области уровня {len(self.scopes) -1}", file=sys.stderr)
            self.scopes.pop()
        else:
            # print("[ERROR][ScopeManager] Попытка выйти из глобальной области!", file=sys.stderr)
            # В KumirInterpreterVisitor.py есть обработка ошибок через self.error_handler
            if hasattr(self.visitor, 'error_handler') and hasattr(self.visitor.error_handler, 'internal_error'):
                 self.visitor.error_handler.internal_error("Попытка выйти из глобальной области видимости.", -1, -1)
            else:
                print("Warning: Attempted to pop global scope", file=sys.stderr)


    def pop_scope(self) -> None:
        """Синоним для exit_scope."""
        self.exit_scope()

    def declare_variable(self, name: str, kumir_type: KumirType,
                         initial_value: Optional[KumirValue],
                         line_index: int, column_index: int) -> None:
        """Объявляет простую (не массив) переменную в текущей области видимости."""
        current_scope = self.scopes[-1]
        name_lower = name.lower()

        if name_lower in current_scope:
            l_content = self.get_line_content_from_coords(line_index)
            raise DeclarationError(
                f"Переменная '{name}' уже объявлена в текущей области видимости.",
                line_index=line_index,
                column_index=column_index,
                line_content=l_content
            )

        final_value_obj = initial_value
        initialized = initial_value is not None

        if final_value_obj is None:
            final_value_obj = get_default_value(kumir_type)
            if kumir_type == KumirType.CHAR and final_value_obj.value is None:
                initialized = False 
            elif final_value_obj.value is not None : 
                initialized = True


        if initial_value is not None and initial_value.kumir_type != kumir_type.value:
            if not (kumir_type == KumirType.REAL and initial_value.kumir_type == KumirType.INT.value):
                l_content = self.get_line_content_from_coords(line_index)
                raise KumirTypeError(
                    f"Попытка инициализировать переменную '{name}' типа {kumir_type.name} значением типа {initial_value.kumir_type}.",
                    line_index=line_index, column_index=column_index, line_content=l_content
                )
            if kumir_type == KumirType.REAL and initial_value.kumir_type == KumirType.INT.value:
                final_value_obj = KumirValue(float(initial_value.value), KumirType.REAL.value)


        current_scope[name_lower] = {
            'name_original': name,
            'kumir_type': kumir_type, # Храним KumirType enum
            'value': final_value_obj, # Храним KumirValue
            'is_table': False,
            'initialized': initialized,
            'line_declared': line_index,
            'col_declared': column_index
        }

    def declare_array(self, var_name: str, element_kumir_type: KumirType,
                      dimensions: List[Tuple[int, int]],
                      line_index: int, column_index: int) -> None:
        """Объявляет массив (таблицу) в текущей области видимости."""
        current_scope = self.scopes[-1]
        name_lower = var_name.lower()

        if name_lower in current_scope:
            l_content = self.get_line_content_from_coords(line_index)
            raise DeclarationError(
                f"Переменная (массив) '{var_name}' уже объявлена в текущей области видимости.",
                line_index=line_index, column_index=column_index, line_content=l_content
            )
        
        # line_index 0-based, ctx.start.line 1-based
        # column_index 0-based, ctx.start.column 0-based
        dummy_ctx = DummyCtx(line_index + 1, column_index)
        
        table_value = KumirTableVar(
            element_kumir_type=element_kumir_type.value, # Передаем строку типа элемента
            dimension_bounds_list=dimensions,
            ctx=dummy_ctx
        )

        current_scope[name_lower] = {
            'name_original': var_name,
            'kumir_type': element_kumir_type, # Храним KumirType enum базового типа элементов
            'value': table_value,             # Храним экземпляр KumirTableVar
            'is_table': True,
            'initialized': True, 
            'line_declared': line_index,
            'col_declared': column_index
        }

    def find_variable(self, var_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Ищет переменную во всех областях видимости, начиная с текущей. Возвращает (var_info, scope) или (None, None)."""
        var_name_lower = var_name.lower()
        for scope in reversed(self.scopes):
            if var_name_lower in scope:
                return scope[var_name_lower], scope
        return None, None

    def find_variable_with_scope_depth(self, var_name: str) -> Optional[Tuple[Dict[str, Any], int]]:
        """
        Ищет переменную во всех областях видимости, возвращает информацию о переменной и глубину области видимости.
        Возвращает (var_info, scope_depth) или None если переменная не найдена.
        scope_depth = 0 для текущей области, 1 для родительской и т.д.
        """
        var_name_lower = var_name.lower()
        for depth, scope in enumerate(reversed(self.scopes)):
            if var_name_lower in scope:
                return scope[var_name_lower], depth
        return None

    def update_variable(self, var_name: str, value_to_assign: KumirValue,
                        line_index: int, column_index: int) -> None:
        """Обновляет значение существующей переменной (простой или целой таблицы)."""
        var_info, scope = self.find_variable(var_name)
        
        if not var_info or scope is None:
            l_content = self.get_line_content_from_coords(line_index)
            raise KumirNameError(
                f"Переменная '{var_name}' не найдена для обновления.",
                line_index=line_index, column_index=column_index, line_content=l_content
            )

        var_name_lower = var_info['name_original'].lower() 

        if var_info['is_table']:
            if not (value_to_assign.kumir_type == KumirType.TABLE.value and isinstance(value_to_assign.value, KumirTableVar)):
                l_content = self.get_line_content_from_coords(line_index)
                raise KumirTypeError(
                    f"Попытка присвоить не-табличное значение таблице '{var_info['name_original']}'. "
                    f"Получен тип {value_to_assign.kumir_type}.",
                    line_index=line_index, column_index=column_index, line_content=l_content
                )
            
            table_to_assign: KumirTableVar = value_to_assign.value
            current_table: KumirTableVar = var_info['value']

            if current_table.element_kumir_type != table_to_assign.element_kumir_type:
                l_content = self.get_line_content_from_coords(line_index)
                raise KumirTypeError(
                    f"Несовместимые типы элементов таблиц при присваивании \'{var_info['name_original']}\'. "
                    f"Ожидался {current_table.element_kumir_type}, получен {table_to_assign.element_kumir_type}.",
                    line_index=line_index, column_index=column_index, line_content=l_content
                )
            
            if (current_table.dimensions != table_to_assign.dimensions or
                current_table.dimension_bounds_list != table_to_assign.dimension_bounds_list):
                l_content = self.get_line_content_from_coords(line_index)
                raise KumirIndexError( 
                    f"Несовместимые размерности таблиц при присваивании \'{var_info['name_original']}\'.",
                    line_index=line_index, column_index=column_index, line_content=l_content
                )
              # Проводим присваивание таблицы
            # Заменяем содержимое текущей таблицы содержимым новой таблицы
            current_table.data.clear()  # Очищаем старые данные
            current_table.data.update(table_to_assign.data)  # Копируем новые данные
            scope[var_name_lower]['initialized'] = True
        else:
            # Простая переменная
            target_kumir_type: KumirType = var_info['kumir_type'] # Это KumirType enum
            
            if value_to_assign.kumir_type == target_kumir_type.value:
                scope[var_name_lower]['value'] = value_to_assign
            elif target_kumir_type == KumirType.REAL and value_to_assign.kumir_type == KumirType.INT.value:
                converted_value = KumirValue(float(value_to_assign.value), KumirType.REAL.value)
                scope[var_name_lower]['value'] = converted_value
            else:
                l_content = self.get_line_content_from_coords(line_index)
                raise KumirTypeError(
                    f"Несовместимость типов при присваивании переменной '{var_info['name_original']}'. "
                    f"Ожидался тип {target_kumir_type.name}, получен {value_to_assign.kumir_type}.",
                    line_index=line_index, column_index=column_index, line_content=l_content
                )
            scope[var_name_lower]['initialized'] = True
        
    def update_table_element(self, var_name: str, indices: List[int], value_to_assign: KumirValue,
                               line_index: int, column_index: int) -> None:
        """Обновляет значение элемента таблицы."""
        var_info, _ = self.find_variable(var_name) 

        if not var_info:
            l_content = self.get_line_content_from_coords(line_index)
            raise KumirNameError(
                f"Таблица '{var_name}' не найдена для обновления элемента.",
                line_index=line_index, column_index=column_index, line_content=l_content
            )

        if not var_info['is_table'] or not isinstance(var_info['value'], KumirTableVar):
            l_content = self.get_line_content_from_coords(line_index)
            raise KumirTypeError(
                f"Переменная '{var_info['name_original']}' не является таблицей.",
                line_index=line_index, column_index=column_index, line_content=l_content
            )

        table_var: KumirTableVar = var_info['value']
        # line_index 0-based, ctx.start.line 1-based
        # column_index 0-based, ctx.start.column 0-based
        dummy_access_ctx = DummyCtx(line_index + 1, column_index)
        try:
            table_var.set_value(tuple(indices), value_to_assign, dummy_access_ctx)
            var_info['initialized'] = True 
        except (KumirTypeError, KumirIndexError, KumirEvalError) as e:
            # Перезаписываем информацию о позиции, если она не была установлена в KumirTableVar
            # или если мы хотим использовать позицию операции присваивания элемента.
            # KumirTableVar уже должен использовать dummy_access_ctx.
            if e.line_index is None: e.line_index = line_index +1 # Ошибки из KumirTableVar могут быть 1-based
            if e.column_index is None: e.column_index = column_index
            if e.line_content is None: e.line_content = self.get_line_content_from_coords(line_index)
            raise e

    def get_variable_info(self, var_name: str,
                          line_index: Optional[int] = None,
                          column_index: Optional[int] = None,
                          is_read_operation: bool = False) -> Dict[str, Any]:
        """Ищет переменную и возвращает её информацию. 
        Возбуждает KumirNameError если не найдена, или KumirEvalError если не инициализирована (при is_read_operation=True)."""
        var_info, _ = self.find_variable(var_name)
        if var_info is None:
            l_content = self.get_line_content_from_coords(line_index) if line_index is not None else None
            raise KumirNameError(
                f"Переменная '{var_name}' не найдена.", 
                line_index=line_index, column_index=column_index, line_content=l_content
            )
        
        if is_read_operation and not var_info['is_table'] and not var_info['initialized']:
            l_content = self.get_line_content_from_coords(line_index) if line_index is not None else None
            raise KumirEvalError(
                f"Переменная '{var_info['name_original']}' используется до инициализации.",
                line_index=line_index, column_index=column_index, line_content=l_content
            )
        return var_info

    def lookup_variable(self, var_name: str, ctx_for_error: Optional[ParserRuleContext] = None, is_read_operation: bool = False) -> Dict[str, Any]:
        """Ищет переменную и возвращает её информацию. (Рекомендуется использовать get_variable_info)."""
        line_idx = ctx_for_error.start.line - 1 if ctx_for_error and hasattr(ctx_for_error, 'start') else None
        col_idx = ctx_for_error.start.column if ctx_for_error and hasattr(ctx_for_error, 'start') else None
        # Передаем is_read_operation в get_variable_info
        return self.get_variable_info(var_name, line_idx, col_idx, is_read_operation=is_read_operation)