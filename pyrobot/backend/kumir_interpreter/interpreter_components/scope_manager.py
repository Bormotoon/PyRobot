# Scope and variable management functions 
from typing import Any, Tuple, Optional, Dict, List
from antlr4 import ParserRuleContext
import sys # Добавлено для print в error_stream

from ..kumir_exceptions import DeclarationError, KumirEvalError, KumirIndexError, KumirTypeError, KumirNameError # Предполагаем, что kumir_exceptions на уровень выше
from ..kumir_datatypes import KumirTableVar # Предполагаем, что kumir_datatypes на уровень выше



def get_default_value(kumir_type):
    """Возвращает значение по умолчанию для данного типа Кумира."""
    if kumir_type == 'цел': return 0
    if kumir_type == 'вещ': return 0.0
    if kumir_type == 'лог': return False  # В Кумире логические по умолчанию могут быть не инициализированы, но False безопаснее
    if kumir_type == 'сим': return ''  # Или может быть ошибка?
    if kumir_type == 'лит': return ""
    return None  # Для таблиц или неизвестных типов



class ScopeManager:
    def __init__(self, visitor_ref):
        self.visitor = visitor_ref  # Ссылка на основной KumirInterpreterVisitor
        self.scopes: List[Dict[str, Any]] = [{}]  # Глобальная область видимости

    def get_program_lines_for_error(self):
        # Helper to safely access program_lines from the visitor
        if hasattr(self.visitor, 'program_lines') and self.visitor.program_lines:
            return self.visitor.program_lines
        return []

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
            # Здесь можно возбудить исключение, если такая ситуация недопустима
            print("Warning: Attempted to pop global scope", file=self.visitor.error_stream or sys.stderr)


    def pop_scope(self) -> None:
        """Синоним для exit_scope."""
        self.exit_scope()

    def declare_variable(self, name: str, kumir_type: str, 
                         is_table: bool = False, 
                         dimensions: Optional[List[Tuple[int, int]]] = None, 
                         ctx_declaration_item: Optional[ParserRuleContext] = None) -> None:
        """Объявляет переменную в текущей области видимости."""
        current_scope = self.scopes[-1]
        name_lower = name.lower()

        if name_lower in current_scope:
            line_idx = ctx_declaration_item.start.line - 1 if ctx_declaration_item and hasattr(ctx_declaration_item, 'start') else None
            col_idx = ctx_declaration_item.start.column if ctx_declaration_item and hasattr(ctx_declaration_item, 'start') else None
            l_content = self.get_line_content_from_ctx(ctx_declaration_item)
            raise DeclarationError(
                f"Переменная '{name}' уже объявлена в текущей области видимости.",
                line_index=line_idx,
                column_index=col_idx,
                line_content=l_content
            )

        default_value = None
        if is_table:
            if dimensions is None: # pragma: no cover
                # Этого не должно происходить, если парсер корректно обрабатывает объявления таблиц
                line_idx = ctx_declaration_item.start.line - 1 if ctx_declaration_item and hasattr(ctx_declaration_item, 'start') else None
                col_idx = ctx_declaration_item.start.column if ctx_declaration_item and hasattr(ctx_declaration_item, 'start') else None
                l_content = self.get_line_content_from_ctx(ctx_declaration_item)
                raise DeclarationError(
                    f"Размеры для таблицы '{name}' не определены.",
                    line_index=line_idx, column_index=col_idx, line_content=l_content
                )
            
            # Определяем базовый тип элемента таблицы (например, 'цел' из 'целтаб')
            base_element_type = kumir_type.replace('таб', '')
            # element_default_value = get_default_value(base_element_type) # Больше не нужен здесь

            default_value = KumirTableVar(
                base_kumir_type_name=base_element_type,
                dimension_bounds_list=dimensions,
                ctx=ctx_declaration_item 
            )
        else:
            default_value = get_default_value(kumir_type)

        current_scope[name_lower] = {
            'type': kumir_type,
            'value': default_value,
            'is_table': is_table,
            'initialized': is_table # Таблицы считаются инициализированными своей структурой
        }
        # print(f"[DEBUG][ScopeManager] Объявлена {'таблица' if is_table else 'переменная'} '{name}' типа '{kumir_type}' со значением по умолчанию: {current_scope[name_lower]['value']}", file=sys.stderr)


    def find_variable(self, var_name: str, ctx: Optional[ParserRuleContext] = None) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]: # Добавлен ctx
        """Ищет переменную во всех областях видимости, начиная с текущей."""
        var_name_lower = var_name.lower()
        for scope in reversed(self.scopes):
            if var_name_lower in scope:
                return scope[var_name_lower], scope  # Возвращаем информацию о переменной и саму область видимости
        # Если переменная не найдена, ctx здесь не используется для генерации ошибки,
        # это делается в вызывающем коде (например, в lookup_variable или update_variable)
        return None, None

    def update_variable(self, var_name: str, value: Any, ctx_for_error: Optional[ParserRuleContext] = None) -> None:
        """Обновляет значение существующей переменной."""
        var_info, scope = self.find_variable(var_name, ctx=ctx_for_error) # Передаем ctx_for_error дальше
        var_name_lower = var_name.lower()

        if not var_info or scope is None: # pragma: no cover
            line_idx = ctx_for_error.start.line - 1 if ctx_for_error else None
            col_idx = ctx_for_error.start.column if ctx_for_error else None
            l_content = self.get_line_content_from_ctx(ctx_for_error)
            raise KumirNameError(
                f"Переменная '{var_name}' не найдена.",
                line_index=line_idx, column_index=col_idx, line_content=l_content
            )

        target_type = var_info['type']
        
        # Проверка и преобразование значения перед присваиванием
        # Для таблиц, 'value' должно быть KumirTableVar, и проверка типов происходит внутри KumirTableVar.set_value
        # Для простых переменных, 'value' должно соответствовать target_type
        if var_info['is_table']:
            if not isinstance(value, KumirTableVar) and value is not None: # None допустим для сброса
                line_idx = ctx_for_error.start.line - 1 if ctx_for_error else None
                col_idx = ctx_for_error.start.column if ctx_for_error else None
                l_content = self.get_line_content_from_ctx(ctx_for_error)
                raise KumirTypeError(
                    f"Попытка присвоить не-табличное значение таблице '{var_name}'.",
                    line_index=line_idx, column_index=col_idx, line_content=l_content
                )
            # Здесь мы не вызываем _validate_and_convert_value_for_assignment, 
            # так как KumirTableVar сам управляет своими элементами.
            # Присваивание целой таблицы (TableA := TableB) должно копировать содержимое.
            # Если value это KumirTableVar, то оно просто присваивается.
            # Если value это None (например, при выходе из области видимости), это тоже ок.
            scope[var_name_lower]['value'] = value
            scope[var_name_lower]['initialized'] = True # Таблица всегда "инициализирована" своей структурой
        else:
            # Используем _validate_and_convert_value_for_assignment из visitor
            # Это потребует, чтобы visitor передал ссылку на себя в ScopeManager,
            # или ScopeManager должен иметь доступ к этим утилитам.
            # Пока предполагаем, что _validate_and_convert_value_for_assignment доступен через self.visitor
            if hasattr(self.visitor, '_validate_and_convert_value_for_assignment'):
                try:
                    validated_value = self.visitor._validate_and_convert_value_for_assignment(value, target_type, var_name)
                    scope[var_name_lower]['value'] = validated_value
                    scope[var_name_lower]['initialized'] = True
                except (KumirTypeError, KumirEvalError) as e:
                    # Перевыбрасываем исключение, добавляя контекст, если его нет
                    # TODO: Улучшить передачу контекста в исключения
                    e.line_index = e.line_index if e.line_index is not None else (ctx_for_error.start.line - 1 if ctx_for_error else None)
                    e.column_index = e.column_index if e.column_index is not None else (ctx_for_error.start.column if ctx_for_error else None)
                    e.line_content = e.line_content if e.line_content is not None else self.get_line_content_from_ctx(ctx_for_error)
                    raise e
            else: # pragma: no cover
                # Запасной вариант, если _validate_and_convert_value_for_assignment недоступен
                scope[var_name_lower]['value'] = value
                scope[var_name_lower]['initialized'] = True
        
        # print(f\"[DEBUG][ScopeManager] Обновлена переменная '{var_name}'. Новое значение: {scope[var_name_lower]['value']}\", file=sys.stderr)

    def lookup_variable(self, var_name: str, ctx_for_error: Optional[ParserRuleContext] = None) -> Optional[Dict[str, Any]]:
        """Ищет переменную и возвращает её информацию или возбуждает KumirNameError."""
        var_info, _ = self.find_variable(var_name)
        if var_info is None:
            line_idx = ctx_for_error.start.line - 1 if ctx_for_error and hasattr(ctx_for_error, 'start') else None
            col_idx = ctx_for_error.start.column if ctx_for_error and hasattr(ctx_for_error, 'start') else None
            l_content = self.get_line_content_from_ctx(ctx_for_error)
            raise KumirNameError(
                f"Переменная '{var_name}' не найдена.",
                line_index=line_idx, column_index=col_idx, line_content=l_content
            )
        return var_info