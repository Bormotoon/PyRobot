# Visitor methods for declaration statements (variables, etc.) 
import sys # Для print отладки
from typing import TYPE_CHECKING, Any, Optional

from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import DeclarationError, KumirEvalError, AssignmentError, KumirNotImplementedError
from ..kumir_datatypes import KumirTableVar
from .type_utils import get_type_info_from_specifier
# Импортируем константы типов из constants.py, если они нужны напрямую,
# но TYPE_MAP и конкретные типы (INTEGER_TYPE и т.д.) лучше брать из visitor (self)
# или передавать как аргументы, если это возможно, чтобы избежать циклов.
# Пока что для простоты предположим, что они будут доступны через self (visitor).
# from .constants import TYPE_MAP, INTEGER_TYPE, FLOAT_TYPE, BOOLEAN_TYPE, CHAR_TYPE, STRING_TYPE

if TYPE_CHECKING:
    from ..interpreter import KumirInterpreterVisitor # Для аннотации типов


class DeclarationVisitorMixin:
    # Этот метод будет полагаться на то, что KumirInterpreterVisitor (который будет использовать этот миксин)
    # имеет следующие атрибуты и методы:
    # self.scope_manager: ScopeManager
    # self.evaluator: ExpressionEvaluator
    # self._validate_and_convert_value_for_assignment(value, target_type, var_name)
    # self.TYPE_MAP (для старой логики, если останется)
    # self.INTEGER_TYPE, self.FLOAT_TYPE и т.д. (аналогично)
    # self.get_line_content_from_ctx (для KumirEvalError)

    def visitVariableDeclaration(self: 'KumirInterpreterVisitor', ctx: KumirParser.VariableDeclarationContext):
        print(f"[DEBUG][VisitVarDecl_Mixin] Обработка variableDeclaration: {ctx.getText()}", file=sys.stderr)
        type_ctx = ctx.typeSpecifier()
        
        # Используем новую функцию для получения информации о типе
        try:
            base_kumir_type, is_table_type = get_type_info_from_specifier(self, type_ctx)
        except DeclarationError as e:
            # Если get_type_info_from_specifier уже установил line_index, column_index, line_content,
            # то просто перевыбрасываем. Если нет, добавляем их.
            if not (hasattr(e, 'line_index') and e.line_index is not None and \
                    hasattr(e, 'column_index') and e.column_index is not None and \
                    hasattr(e, 'line_content') and e.line_content is not None):
                line = type_ctx.start.line if hasattr(type_ctx, 'start') else -1
                col = type_ctx.start.column if hasattr(type_ctx, 'start') else -1
                lc = self.get_line_content_from_ctx(type_ctx)
                # Пересоздаем исключение, чтобы добавить информацию, если ее не было
                raise DeclarationError(str(e.args[0] if e.args else "Ошибка определения типа"), 
                                     line_index=line-1 if line != -1 else None, 
                                     column_index=col, 
                                     line_content=lc) from e
            else:
                raise # Перевыбрасываем оригинальное исключение, если оно уже полное

        print(f"[DEBUG][VisitVarDecl_Mixin] Тип определен через get_type_info_from_specifier: {base_kumir_type}, таблица: {is_table_type}", file=sys.stderr)

        # Удаляем старую логику определения типа, так как она теперь в get_type_info_from_specifier
        # base_kumir_type = None # <-- УДАЛИТЬ
        # is_table_type = False # <-- УДАЛИТЬ
        # TYPE_MAP = self.TYPE_MAP # <-- УДАЛИТЬ
        # INTEGER_TYPE = self.INTEGER_TYPE # <-- УДАЛИТЬ
        # ... и так далее для всех старых проверок type_ctx.basicType(), type_ctx.arrayType() ...
        # Этот блок кода (строки ~20-68 в оригинальном файле) должен быть полностью заменен вызовом выше.

        if not base_kumir_type: # Эта проверка может быть избыточной, если get_type_info_from_specifier всегда возвращает тип или кидает исключение
            lc_fallback = self.get_line_content_from_ctx(type_ctx)
            raise DeclarationError(f"Строка {type_ctx.start.line}: Не удалось определить базовый тип для: {type_ctx.getText()}",
                                   line_index=type_ctx.start.line -1, 
                                   column_index=type_ctx.start.column,
                                   line_content=lc_fallback)

        for var_decl_item_ctx in ctx.variableList().variableDeclarationItem():
            var_name = var_decl_item_ctx.ID().getText()
            print(f"[DEBUG][VisitVarDecl_Mixin] Обработка переменной/таблицы: {var_name}", file=sys.stderr)

            if is_table_type:
                if not var_decl_item_ctx.LBRACK():
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Для таблицы '{var_name}' ({base_kumir_type} таб) должны быть указаны границы в квадратных скобках.",
                        line_index=var_decl_item_ctx.ID().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.ID().getSymbol().column,
                        line_content=self.get_line_content_from_ctx(var_decl_item_ctx))

                dimension_bounds_list = []
                array_bounds_nodes = var_decl_item_ctx.arrayBounds()
                if not array_bounds_nodes:
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Отсутствуют определения границ для таблицы '{var_name}'.",
                        line_index=var_decl_item_ctx.LBRACK().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.LBRACK().getSymbol().column,
                        line_content=self.get_line_content_from_ctx(var_decl_item_ctx))

                for i, bounds_ctx in enumerate(array_bounds_nodes):
                    print(f"[DEBUG][VisitVarDecl_Mixin] Обработка границ измерения {i + 1} для '{var_name}': {bounds_ctx.getText()}",
                          file=sys.stderr)
                    
                    if var_name == 'A': 
                        expr0_text = bounds_ctx.expression(0).getText()
                        expr1_text = bounds_ctx.expression(1).getText()
                        print(f"[DEBUG][VarDecl_N_Check_Bounds_Mixin] Table '{var_name}', Dim {i+1}, MinExpr: '{expr0_text}', MaxExpr: '{expr1_text}'", file=sys.stderr)
                        if expr1_text == 'N':
                            n_info_check, _ = self.scope_manager.find_variable('N')
                            if n_info_check:
                                print(f"[DEBUG][VarDecl_N_Check_Value_Mixin] ПЕРЕД вычислением MaxExpr ('N'), N = {n_info_check['value']}", file=sys.stderr)
                            else:
                                print(f"[DEBUG][VarDecl_N_Check_Value_Mixin] ПЕРЕД вычислением MaxExpr ('N'), N не найдена!", file=sys.stderr)
                        if expr0_text == 'N':
                            n_info_check, _ = self.scope_manager.find_variable('N')
                            if n_info_check:
                                print(f"[DEBUG][VarDecl_N_Check_Value_Mixin] ПЕРЕД вычислением MinExpr ('N'), N = {n_info_check['value']}", file=sys.stderr)
                            else:
                                print(f"[DEBUG][VarDecl_N_Check_Value_Mixin] ПЕРЕД вычислением MinExpr ('N'), N не найдена!", file=sys.stderr)

                    if not (bounds_ctx.expression(0) and bounds_ctx.expression(1) and bounds_ctx.COLON()):
                        raise DeclarationError(
                            f"Строка {bounds_ctx.start.line}: Некорректный формат границ для измерения {i + 1} таблицы '{var_name}'. Ожидается [нижняя:верхняя].",
                            line_index=bounds_ctx.start.line -1, 
                            column_index=bounds_ctx.start.column,
                            line_content=self.get_line_content_from_ctx(bounds_ctx))

                    min_idx_val = self.evaluator.visitExpression(bounds_ctx.expression(0))
                    max_idx_val = self.evaluator.visitExpression(bounds_ctx.expression(1))
                    min_idx = min_idx_val
                    max_idx = max_idx_val

                    if not isinstance(min_idx, int):
                        raise KumirEvalError(
                            f"Строка {bounds_ctx.expression(0).start.line}: Нижняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {min_idx} (тип: {type(min_idx).__name__}).",
                            line_index=bounds_ctx.expression(0).start.line -1, 
                            column_index=bounds_ctx.expression(0).start.column,
                            line_content=self.get_line_content_from_ctx(bounds_ctx.expression(0)))
                    if not isinstance(max_idx, int):
                        raise KumirEvalError(
                            f"Строка {bounds_ctx.expression(1).start.line}: Верхняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {max_idx} (тип: {type(max_idx).__name__}).",
                            line_index=bounds_ctx.expression(1).start.line -1, 
                            column_index=bounds_ctx.expression(1).start.column,
                            line_content=self.get_line_content_from_ctx(bounds_ctx.expression(1)))

                    dimension_bounds_list.append((min_idx, max_idx))

                if not dimension_bounds_list:
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Не удалось определить границы для таблицы '{var_name}'.",
                        line_index=var_decl_item_ctx.ID().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.ID().getSymbol().column,
                        line_content=self.get_line_content_from_ctx(var_decl_item_ctx))

                try:
                    self.scope_manager.declare_variable(var_name, base_kumir_type + 'таб', 
                                          is_table=True, dimensions=dimension_bounds_list, 
                                          ctx_declaration_item=var_decl_item_ctx)
                    print(
                        f"[DEBUG][VisitVarDecl_Mixin] Объявлена таблица '{var_name}' тип {base_kumir_type}таб, границы: {dimension_bounds_list}",
                        file=sys.stderr)
                except (KumirEvalError, DeclarationError) as e:
                    if not hasattr(e, 'line_index') or e.line_index is None:
                         e.line_index = var_decl_item_ctx.start.line -1 if hasattr(var_decl_item_ctx, 'start') else None
                    if not hasattr(e, 'column_index') or e.column_index is None:
                         e.column_index = var_decl_item_ctx.start.column if hasattr(var_decl_item_ctx, 'start') else None
                    # Добавляем line_content если его нет
                    if not hasattr(e, 'line_content') or e.line_content is None:
                        e.line_content = self.get_line_content_from_ctx(var_decl_item_ctx)
                    raise

                if var_decl_item_ctx.expression():
                    raise KumirNotImplementedError(
                        f"Строка {var_decl_item_ctx.expression().start.line}: Инициализация таблиц при объявлении ('{var_name} = ...') пока не поддерживается.",
                        line_index=var_decl_item_ctx.expression().start.line -1, 
                        column_index=var_decl_item_ctx.expression().start.column,
                        line_content=self.get_line_content_from_ctx(var_decl_item_ctx.expression()))

            else:  # Обычная (скалярная) переменная
                if var_decl_item_ctx.LBRACK():
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Скалярная переменная '{var_name}' (тип {base_kumir_type}) не может иметь указания границ массива.",
                        line_index=var_decl_item_ctx.LBRACK().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.LBRACK().getSymbol().column,
                        line_content=self.get_line_content_from_ctx(var_decl_item_ctx))
                
                self.scope_manager.declare_variable(var_name, base_kumir_type, False, None, ctx_declaration_item=var_decl_item_ctx)

                if var_decl_item_ctx.expression():
                    value_to_assign = self.evaluator.visitExpression(var_decl_item_ctx.expression())

                    try:
                        # Используем метод self._validate_and_convert_value_for_assignment из основного класса Visitor
                        validated_value = self._validate_and_convert_value_for_assignment(value_to_assign, base_kumir_type, var_name)
                        self.scope_manager.update_variable(var_name, validated_value, ctx_for_error=var_decl_item_ctx.expression())
                        print(
                            f"[DEBUG][VisitVarDecl_Mixin] Переменной '{var_name}' присвоено значение при инициализации: {validated_value}",
                            file=sys.stderr)
                    except (AssignmentError, DeclarationError, KumirEvalError) as e:
                        line = var_decl_item_ctx.expression().start.line
                        column = var_decl_item_ctx.expression().start.column
                        # Мы не можем напрямую использовать type(e)(...) т.к. KumirEvalError требует line_index, column_index
                        # Пересоздадим исключение с правильными аргументами, если это одна из наших ошибок
                        if isinstance(e, KumirEvalError):
                             raise KumirEvalError(
                                f"Строка {line}, столбец {column}: Ошибка при инициализации переменной '{var_name}': {e.args[0]}",
                                line_index=line-1, column_index=column, line_content=self.get_line_content_from_ctx(var_decl_item_ctx.expression())
                            ) from e
                        elif isinstance(e, (AssignmentError, DeclarationError)): # Эти ошибки не имеют line/col в конструкторе
                             # Оборачиваем в KumirEvalError
                             raise KumirEvalError(
                                f"Строка {line}, столбец {column}: Ошибка при инициализации переменной '{var_name}': {e.args[0]}",
                                line_index=line-1, column_index=column, line_content=self.get_line_content_from_ctx(var_decl_item_ctx.expression())
                             ) from e
                        else: # pragma: no cover
                             raise # Другие типы ошибок
        return None 