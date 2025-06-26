# Visitor methods for declaration statements (variables, etc.)
import sys # Для print отладки
from typing import TYPE_CHECKING, cast

from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import (KumirEvalError, DeclarationError, AssignmentError)
from ..kumir_datatypes import KumirType, KumirValue, KumirTableVar
from ..definitions import Parameter, AlgorithmDefinition  # Импорт наших новых классов
from .type_utils import get_type_info_from_specifier

if TYPE_CHECKING:
    from .main_visitor import KumirInterpreterVisitor


def _create_table_from_array_literal(array_elements, element_type, dimension_bounds_list, ctx):
    """Создаёт KumirTableVar из литерала массива"""
    # Проверяем, что размеры совпадают
    if len(dimension_bounds_list) != 1:
        raise KumirEvalError(
            f"Инициализация многомерных массивов пока не поддерживается.",
            line_index=ctx.start.line - 1,
            column_index=ctx.start.column
        )
    
    min_idx, max_idx = dimension_bounds_list[0]
    expected_size = max_idx - min_idx + 1
    
    if len(array_elements) != expected_size:
        raise KumirEvalError(
            f"Количество элементов в литерале массива ({len(array_elements)}) не соответствует объявленному размеру [{min_idx}:{max_idx}] ({expected_size}).",
            line_index=ctx.start.line - 1,
            column_index=ctx.start.column
        )
    
    # Нормализуем тип элемента к верхнему регистру
    normalized_element_type = element_type.upper()
    
    # Создаём KumirTableVar
    table_var = KumirTableVar(normalized_element_type, dimension_bounds_list, ctx)
      # Заполняем данными через set_value для правильной обработки типов
    for i, element in enumerate(array_elements):
        index = min_idx + i
        table_var.set_value((index,), element, ctx)
    
    return table_var


class DeclarationVisitorMixin:
    # Этот метод будет полагаться на то, что KumirInterpreterVisitor (который будет использовать этот миксин)
    # имеет следующие атрибуты и методы:
    # self.scope_manager: ScopeManager
    # self.evaluator: ExpressionEvaluator
    # self._validate_and_convert_value_for_assignment(value, target_type, var_name)
    # self.TYPE_MAP (для старой логики, если останется)
    # self.INTEGER_TYPE, self.FLOAT_TYPE и т.д. (аналогично)
    # self.get_line_content_from_ctx (для KumirEvalError)

    def visitVariableDeclaration(self, ctx: KumirParser.VariableDeclarationContext):
        kiv_self = cast('KumirInterpreterVisitor', self)
        type_ctx = ctx.typeSpecifier()
        
        # Используем новую функцию для получения информации о типе
        try:
            base_kumir_type, is_table_type = get_type_info_from_specifier(kiv_self, type_ctx)
        except DeclarationError as e:
            # Если get_type_info_from_specifier уже установил line_index, column_index, line_content,
            # то просто перевыбрасываем. Если нет, добавляем их.
            if not (hasattr(e, 'line_index') and e.line_index is not None and \
                    hasattr(e, 'column_index') and e.column_index is not None and \
                    hasattr(e, 'line_content') and e.line_content is not None):
                line = type_ctx.start.line if hasattr(type_ctx, 'start') else -1
                col = type_ctx.start.column if hasattr(type_ctx, 'start') else -1
                lc = kiv_self.get_line_content_from_ctx(type_ctx)
                # Пересоздаем исключение, чтобы добавить информацию, если ее не было
                raise DeclarationError(str(e.args[0] if e.args else "Ошибка определения типа"), 
                                     line_index=line-1 if line != -1 else None, 
                                     column_index=col, 
                                     line_content=lc) from e
            else:
                raise # Перевыбрасываем оригинальное исключение, если оно уже полное


        if not base_kumir_type: # Эта проверка может быть избыточной, если get_type_info_from_specifier всегда возвращает тип или кидает исключение
            lc_fallback = kiv_self.get_line_content_from_ctx(type_ctx)
            raise DeclarationError(f"Строка {type_ctx.start.line}: Не удалось определить базовый тип для: {type_ctx.getText()}",
                                   line_index=type_ctx.start.line -1, 
                                   column_index=type_ctx.start.column,
                                   line_content=lc_fallback)

        for var_decl_item_ctx in ctx.variableList().variableDeclarationItem():
            var_name = var_decl_item_ctx.ID().getText()

            if is_table_type:
                if not var_decl_item_ctx.LBRACK():
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Для таблицы '{var_name}' ({base_kumir_type} таб) должны быть указаны границы в квадратных скобках.",
                        line_index=var_decl_item_ctx.ID().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.ID().getSymbol().column,
                        line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx))

                dimension_bounds_list = []
                array_bounds_nodes = var_decl_item_ctx.arrayBounds()
                if not array_bounds_nodes:
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Отсутствуют определения границ для таблицы '{var_name}'.",
                        line_index=var_decl_item_ctx.LBRACK().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.LBRACK().getSymbol().column,
                        line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx))

                for i, bounds_ctx in enumerate(array_bounds_nodes):
                    # Debug: обработка границ измерения
                    
                    if var_name == 'A': 
                        expr0_text = bounds_ctx.expression(0).getText()
                        expr1_text = bounds_ctx.expression(1).getText()
                        if expr1_text == 'N':
                            n_info_check, _ = kiv_self.scope_manager.find_variable('N')
                            if n_info_check:
                                # Переменная N найдена
                                pass
                            else:
                                # Переменная N не найдена
                                pass
                        if expr0_text == 'N':
                            n_info_check, _ = kiv_self.scope_manager.find_variable('N')
                            if n_info_check:
                                # Переменная N найдена
                                pass
                            else:
                                # Переменная N не найдена
                                pass

                    if not (bounds_ctx.expression(0) and bounds_ctx.expression(1) and bounds_ctx.COLON()):
                        raise DeclarationError(
                            f"Строка {bounds_ctx.start.line}: Некорректный формат границ для измерения {i + 1} таблицы '{var_name}'. Ожидается [нижняя:верхняя].",
                            line_index=bounds_ctx.start.line -1, 
                            column_index=bounds_ctx.start.column,
                            line_content=kiv_self.get_line_content_from_ctx(bounds_ctx))

                    min_idx_val = kiv_self.expression_evaluator.visitExpression(bounds_ctx.expression(0))
                    max_idx_val = kiv_self.expression_evaluator.visitExpression(bounds_ctx.expression(1))
                    
                    # Извлекаем значения из KumirValue
                    min_idx = min_idx_val.value if hasattr(min_idx_val, 'value') else min_idx_val
                    max_idx = max_idx_val.value if hasattr(max_idx_val, 'value') else max_idx_val

                    if not isinstance(min_idx, int):
                        raise KumirEvalError(
                            f"Строка {bounds_ctx.expression(0).start.line}: Нижняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {min_idx} (тип: {type(min_idx).__name__}).",
                            line_index=bounds_ctx.expression(0).start.line -1, 
                            column_index=bounds_ctx.expression(0).start.column,
                            line_content=kiv_self.get_line_content_from_ctx(bounds_ctx.expression(0)))
                    if not isinstance(max_idx, int):
                        raise KumirEvalError(
                            f"Строка {bounds_ctx.expression(1).start.line}: Верхняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {max_idx} (тип: {type(max_idx).__name__}).",
                            line_index=bounds_ctx.expression(1).start.line -1, 
                            column_index=bounds_ctx.expression(1).start.column,
                            line_content=kiv_self.get_line_content_from_ctx(bounds_ctx.expression(1)))

                    dimension_bounds_list.append((min_idx, max_idx))

                if not dimension_bounds_list:
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Не удалось определить границы для таблицы '{var_name}'.",
                        line_index=var_decl_item_ctx.ID().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.ID().getSymbol().column,
                        line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx))
                
                try:
                    kiv_self.scope_manager.declare_array(
                        var_name=var_name,
                        element_kumir_type=KumirType.from_string(base_kumir_type),
                        dimensions=dimension_bounds_list,
                        line_index=var_decl_item_ctx.ID().getSymbol().line - 1,
                        column_index=var_decl_item_ctx.ID().getSymbol().column
                    )
                    print(
                        f"[DEBUG][VisitVarDecl_Mixin] Объявлена таблица '{var_name}' тип {base_kumir_type}таб, границы: {dimension_bounds_list}",
                        file=sys.stderr)
                except (KumirEvalError, DeclarationError) as e:
                    if not hasattr(e, 'line_index') or e.line_index is None:
                         e.line_index = var_decl_item_ctx.start.line -1 if hasattr(var_decl_item_ctx, 'start') else None
                    if not hasattr(e, 'column_index') or e.column_index is None:
                         e.column_index = var_decl_item_ctx.start.column if hasattr(var_decl_item_ctx, 'start') else None
                    if not hasattr(e, 'line_content') or e.line_content is None:
                        e.line_content = kiv_self.get_line_content_from_ctx(var_decl_item_ctx)
                    raise
                
                if var_decl_item_ctx.expression():
                    # Инициализация таблицы литералом массива
                    try:
                        value_to_assign = kiv_self.expression_evaluator.visitExpression(var_decl_item_ctx.expression())
                        
                        # Для таблиц нужно создать KumirTableVar из литерала массива
                        if value_to_assign.kumir_type == KumirType.TABLE.value and isinstance(value_to_assign.value, list):
                            # Создаём KumirTableVar из литерала массива
                            table_var = _create_table_from_array_literal(
                                value_to_assign.value, 
                                base_kumir_type, 
                                dimension_bounds_list,
                                var_decl_item_ctx.expression()
                            )
                            validated_value = KumirValue(table_var, KumirType.TABLE.value)
                        else:
                            # Используем метод для валидации таблиц
                            validated_value = kiv_self._validate_and_convert_value_for_assignment(
                                value_to_assign, base_kumir_type, var_name, is_target_table=True
                            )
                        
                        kiv_self.scope_manager.update_variable(
                            var_name, 
                            validated_value, 
                            line_index=var_decl_item_ctx.expression().start.line - 1, 
                            column_index=var_decl_item_ctx.expression().start.column
                        )
                        print(
                            f"[DEBUG][VisitVarDecl_Mixin] Таблице '{var_name}' присвоено значение при инициализации: {validated_value}",
                            file=sys.stderr
                        )
                    except (AssignmentError, DeclarationError, KumirEvalError) as e:
                        line = var_decl_item_ctx.expression().start.line
                        column = var_decl_item_ctx.expression().start.column
                        if type(e) is KumirEvalError:
                            raise KumirEvalError(
                                f"Строка {line}, столбец {column}: Ошибка при инициализации таблицы '{var_name}': {e.args[0]}",
                                line_index=line-1, 
                                column_index=column, 
                                line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx.expression())
                            ) from e
                        else:
                            # AssignmentError or DeclarationError
                            raise KumirEvalError(
                                f"Строка {line}, столбец {column}: Ошибка при инициализации таблицы '{var_name}': {e.args[0]}",
                                line_index=line-1, 
                                column_index=column, 
                                line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx.expression())
                            ) from e

            else:  # Обычная (скалярная) переменная
                if var_decl_item_ctx.LBRACK():
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Скалярная переменная '{var_name}' (тип {base_kumir_type}) не может иметь указания границ массива.",
                        line_index=var_decl_item_ctx.LBRACK().getSymbol().line -1, 
                        column_index=var_decl_item_ctx.LBRACK().getSymbol().column,                        line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx))
                
                kiv_self.scope_manager.declare_variable(
                    name=var_name, 
                    kumir_type=KumirType.from_string(base_kumir_type),
                    initial_value=None,
                    line_index=var_decl_item_ctx.ID().getSymbol().line - 1,
                    column_index=var_decl_item_ctx.ID().getSymbol().column
                )

                if var_decl_item_ctx.expression():
                    value_to_assign = kiv_self.expression_evaluator.visitExpression(var_decl_item_ctx.expression())
                    
                    try:
                        # Используем метод self._validate_and_convert_value_for_assignment из основного класса Visitor
                        validated_value = kiv_self._validate_and_convert_value_for_assignment(value_to_assign, base_kumir_type, var_name, is_target_table=False)
                        kiv_self.scope_manager.update_variable(var_name, validated_value, line_index=var_decl_item_ctx.expression().start.line - 1, column_index=var_decl_item_ctx.expression().start.column)
                        print(
                            f"[DEBUG][VisitVarDecl_Mixin] Переменной '{var_name}' присвоено значение при инициализации: {validated_value}",
                            file=sys.stderr)
                    except (AssignmentError, DeclarationError, KumirEvalError) as e:
                        line = var_decl_item_ctx.expression().start.line
                        column = var_decl_item_ctx.expression().start.column
                        # Мы не можем напрямую использовать type(e)(...) т.к. KumirEvalError требует line_index, column_index
                        # Пересоздадим исключение с правильными аргументами, если это одна из наших ошибок
                        if type(e) is KumirEvalError:
                             raise KumirEvalError(
                                f"Строка {line}, столбец {column}: Ошибка при инициализации переменной '{var_name}': {e.args[0]}",
                                line_index=line-1, column_index=column, line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx.expression())
                            ) from e
                        else:
                             # AssignmentError or DeclarationError - эти ошибки не имеют line/col в конструкторе
                             # Оборачиваем в KumirEvalError
                             raise KumirEvalError(
                                f"Строка {line}, столбец {column}: Ошибка при инициализации переменной '{var_name}': {e.args[0]}",
                                line_index=line-1, column_index=column, line_content=kiv_self.get_line_content_from_ctx(var_decl_item_ctx.expression())
                             ) from e
        return None # Explicitly return None as variable declarations are statements

    # The following visit methods are for specific statement types if defined in grammar
    # and if they are not already handled by a more general rule like 'statement'
    # that then calls visitVariableDeclaration. If these are direct children of 'statement',
    # they might not be needed if visitVariableDeclaration covers all var decls.
    # However, if grammar has distinct rules like 'var_declare_assign_statement',
    # then dedicated visitors are appropriate.    # Based on KumirParser.g4, 'variableDeclaration' seems to be the main rule for declarations
    # within a statement context. Other specific declaration-like rules might be for global scope
    # or specific algorithm parts. For now, focusing on visitVariableDeclaration.
    
    # Placeholder for procedure/function declaration (handled by visitAlgorithmDefinition)
    def visitAlgorithmDefinition(self, ctx: KumirParser.AlgorithmDefinitionContext):
        kiv_self = cast('KumirInterpreterVisitor', self)
        algo_header_ctx = ctx.algorithmHeader()
        algo_name_tokens = algo_header_ctx.algorithmNameTokens().getText().strip()
        is_func = algo_header_ctx.typeSpecifier() is not None
        

        # Определяем тип возвращаемого значения для функций
        result_type = "void"
        if is_func:
            try:
                result_type, _ = get_type_info_from_specifier(kiv_self, algo_header_ctx.typeSpecifier())
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to get return type for function {algo_name_tokens}: {e}")
                result_type = "вещ"  # Fallback to float type        # Извлекаем параметры из контекста
        parameters = []
        param_list_ctx = algo_header_ctx.parameterList()
        if param_list_ctx:
            for param_decl_ctx in param_list_ctx.parameterDeclaration():
                # Извлечение информации о параметре
                param_names = []
                var_list_ctx = param_decl_ctx.variableList()
                if var_list_ctx:
                    for var_decl_item_ctx in var_list_ctx.variableDeclarationItem():
                        param_names.append(var_decl_item_ctx.ID().getText().strip())
                
                # Определение типа параметра
                param_type = "цел"  # По умолчанию
                is_table = False
                if param_decl_ctx.typeSpecifier():
                    try:
                        param_type, is_table = get_type_info_from_specifier(kiv_self, param_decl_ctx.typeSpecifier())
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Failed to get parameter type: {e}")
                
                # Определение режима параметра (арг, рез, аргрез)
                param_mode = "арг"  # По умолчанию
                if param_decl_ctx.IN_PARAM():
                    param_mode = "арг"
                elif param_decl_ctx.OUT_PARAM():
                    param_mode = "рез"  
                elif param_decl_ctx.INOUT_PARAM():
                    param_mode = "аргрез"# Создаем объекты Parameter для каждого имени
                for param_name in param_names:
                    param = Parameter(
                        name=param_name,
                        param_type=param_type,
                        mode=param_mode,
                        is_table=is_table
                    )
                    parameters.append(param)        # Создаем объект AlgorithmDefinition  
        algorithm_def = AlgorithmDefinition(
            name=algo_name_tokens,
            parameters=parameters,
            return_type=result_type if is_func else None,
            body_context=ctx.algorithmBody() if ctx.algorithmBody() else None,
            local_declarations=[]  # Пока пустой список, заполним позже при необходимости
        )

        # Регистрируем в новом AlgorithmManager
        try:
            kiv_self.algorithm_manager.register_algorithm(algorithm_def)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to register algorithm in AlgorithmManager {algo_name_tokens}: {e}")        # Также регистрируем в старом ProcedureManager для обратной совместимости
        try:
            kiv_self.procedure_manager.register_procedure(
                name=algo_name_tokens,
                ctx=ctx,
                is_function=is_func,
                result_type=result_type
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to register {algo_name_tokens}: {e}")
            raise        # ВАЖНО: Не выполняем тела пользовательских функций и процедур при их определении, 
        # только при явных вызовах. Это исправляет проблему с выполнением тела функции во время парсинга.
        # Если это алгоритм (функция или процедура), всегда пропускаем выполнение тела,
        # так как оно должно выполняться только при явном вызове.
        
        # Главный алгоритм в КУМИРе - это алгоритм без имени (пустая строка)
        is_main = algo_name_tokens == ""
        
        if is_func or not is_main:  # Если это функция или не главный алгоритм программы
            return None
            
        # В обычном режиме для ГЛАВНОГО алгоритма позволяем ANTLR обойти дочерние узлы
        # Это поведение по умолчанию, так что возвращаем результат по умолчанию
        return None # Algorithm definition is a declaration, not an expression with a value

    # Removed duplicated/placeholder visit methods for specific var/arr/proc/func declare statements
    # as visitVariableDeclaration and visitAlgorithmDefinition should cover these based on the G4 structure.