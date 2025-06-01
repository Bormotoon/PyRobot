import sys
from typing import TYPE_CHECKING, cast
from pyrobot.backend.kumir_interpreter.kumir_exceptions import (
    KumirRuntimeError, KumirSyntaxError, DeclarationError, KumirNameError,
    KumirTypeError, KumirArgumentError, BreakSignal, ContinueSignal, StopExecutionSignal, ReturnSignal,
    KumirNotImplementedError
)
from ..generated.KumirParser import KumirParser
from ..generated.KumirParserVisitor import KumirParserVisitor
from ..kumir_datatypes import KumirType, KumirValue
from ..utils import KumirTypeConverter

if TYPE_CHECKING:
    from .scope_manager import ScopeManager
    from .expression_evaluator import ExpressionEvaluator
    from .procedure_manager import ProcedureManager
    from .main_visitor import KumirInterpreterVisitor

class StatementHandlerMixin(KumirParserVisitor):
    # This mixin expects the following attributes to be available on the class that uses it:
    # self.scope_manager: ScopeManager
    # self.expression_evaluator: ExpressionEvaluator
    # self.procedure_manager: ProcedureManager

    def _evaluate_condition(self, condition_val: KumirValue, context_name: str, expr_ctx) -> bool:
        """
        Evaluates a KumirValue as a boolean condition following Kumir semantics.
        For integers: 0 = False, non-zero = True
        For booleans: direct evaluation
        For other types: raises KumirTypeError
        """
        if condition_val is None:
            raise KumirTypeError(
                f"Условие в {context_name} не может быть неопределенным значением",
                line_index=expr_ctx.start.line -1,
                column_index=expr_ctx.start.column
            )
        
        try:
            converter = KumirTypeConverter()
            return converter.to_python_bool(condition_val)
        except KumirTypeError as e:
            # Re-raise with more specific context
            raise KumirTypeError(
                f"Условие в {context_name} должно быть логического или целого типа, получено: {condition_val.kumir_type}",
                line_index=expr_ctx.start.line -1,
                column_index=expr_ctx.start.column
            )

    def _determine_kumir_type_and_array_status(self, type_spec_ctx: KumirParser.TypeSpecifierContext) -> tuple[KumirType, bool]:
        """
        Определяет KumirType и является ли тип массивом на основе узла typeSpecifier.
        Возвращает кортеж (KumirType, is_array: bool).
        Выбрасывает KumirTypeError или KumirNotImplementedError в случае ошибки.
        """
        if type_spec_ctx.basicType():
            bt_ctx = type_spec_ctx.basicType()
            is_array_suffix = (type_spec_ctx.TABLE_SUFFIX() is not None)
            if bt_ctx.INTEGER_TYPE(): return KumirType.INT, is_array_suffix
            if bt_ctx.REAL_TYPE(): return KumirType.REAL, is_array_suffix
            if bt_ctx.BOOLEAN_TYPE(): return KumirType.BOOL, is_array_suffix
            if bt_ctx.CHAR_TYPE(): return KumirType.CHAR, is_array_suffix
            if bt_ctx.STRING_TYPE(): return KumirType.STR, is_array_suffix
        elif type_spec_ctx.arrayType(): # Явные типы массивов типа целтаб, вещтаб
            at_ctx = type_spec_ctx.arrayType()
            if at_ctx.INTEGER_ARRAY_TYPE(): return KumirType.INT, True
            if at_ctx.REAL_ARRAY_TYPE(): return KumirType.REAL, True
            if at_ctx.BOOLEAN_ARRAY_TYPE(): return KumirType.BOOL, True
            if at_ctx.CHAR_ARRAY_TYPE(): return KumirType.CHAR, True
            if at_ctx.STRING_ARRAY_TYPE(): return KumirType.STR, True
        elif type_spec_ctx.actorType():
            act_ctx = type_spec_ctx.actorType()
            is_array_suffix = (type_spec_ctx.TABLE_SUFFIX() is not None)
            if act_ctx.COLOR_TYPE(): return KumirType.COLOR, is_array_suffix
            # ... другие акторы ...
            raise KumirNotImplementedError(f"Тип актора {act_ctx.getText()} пока не поддерживается.",
                                        line_index=type_spec_ctx.start.line -1,
                                        column_index=type_spec_ctx.start.column)

        raise KumirTypeError(f"Неизвестный или неподдерживаемый тип: {type_spec_ctx.getText()}",
                               line_index=type_spec_ctx.start.line -1,
                               column_index=type_spec_ctx.start.column)

    def _is_explicit_array_type(self, type_spec_ctx: KumirParser.TypeSpecifierContext) -> bool:
        """Проверяет, является ли тип явно заданным как массив (например, 'целтаб')."""
        return type_spec_ctx.arrayType() is not None

    def visitVariableDeclarationStatement(self, ctx: KumirParser.VariableDeclarationContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)
        var_type_node = ctx.typeSpecifier()
        kumir_type, is_type_inherently_array = self._determine_kumir_type_and_array_status(var_type_node)

        for var_decl_item_ctx in ctx.variableList().variableDeclarationItem():
            var_name = var_decl_item_ctx.ID().getText()
            initial_value: KumirValue | None = None
            
            # Проверяем, есть ли инициализатор (= выражение)
            if var_decl_item_ctx.expression():
                initial_value_expr_ctx = var_decl_item_ctx.expression()
                initial_value = kiv_self.expression_evaluator.visit(initial_value_expr_ctx)
                if initial_value is None:
                    raise KumirRuntimeError(
                        f"Не удалось вычислить начальное значение для переменной '{var_name}'. Выражение вернуло None.",
                        line_index=initial_value_expr_ctx.start.line - 1,
                        column_index=initial_value_expr_ctx.start.column
                    )

            # Определяем, является ли переменная массивом по текущему объявлению
            # (т.е. есть границы [...] или тип сам по себе массив типа целтаб)
            array_bounds_nodes = var_decl_item_ctx.arrayBounds() # Это список узлов ArrayBoundsContext
            is_declared_as_array = bool(array_bounds_nodes) or is_type_inherently_array

            if is_declared_as_array:
                dimensions = []
                if array_bounds_nodes: # Явно заданы границы [N:M, K:L]
                    for bound_ctx in array_bounds_nodes:
                        lower_bound_expr = bound_ctx.expression(0)
                        upper_bound_expr = bound_ctx.expression(1)

                        lower_val_kv = kiv_self.expression_evaluator.visit(lower_bound_expr)
                        upper_val_kv = kiv_self.expression_evaluator.visit(upper_bound_expr)

                        if not (lower_val_kv and lower_val_kv.kumir_type == KumirType.INT.value and
                                upper_val_kv and upper_val_kv.kumir_type == KumirType.INT.value):
                            raise KumirTypeError(
                                f"Границы массива для '{var_name}' должны быть целыми числами.",
                                line_index=bound_ctx.start.line - 1,
                                column_index=bound_ctx.start.column
                            )
                        dimensions.append((lower_val_kv.value, upper_val_kv.value))
                
                kiv_self.scope_manager.declare_array(
                    var_name,
                    kumir_type,
                    dimensions,
                    line_index=var_decl_item_ctx.start.line - 1,
                    column_index=var_decl_item_ctx.start.column
                )

                if initial_value:
                    if initial_value.kumir_type == KumirType.TABLE.value:
                        kiv_self.scope_manager.update_variable(var_name, initial_value,
                                                          line_index=var_decl_item_ctx.expression().start.line - 1,
                                                          column_index=var_decl_item_ctx.expression().start.column)
                    else:
                        raise KumirTypeError(
                            f"Для массива '{var_name}' ожидался табличный литерал в качестве инициализатора, но получен {initial_value.kumir_type}.",
                            line_index=var_decl_item_ctx.expression().start.line - 1,
                            column_index=var_decl_item_ctx.expression().start.column
                        )
            else: # Обычная переменная (не массив)
                kiv_self.scope_manager.declare_variable(
                    var_name,
                    kumir_type,
                    initial_value,
                    line_index=var_decl_item_ctx.start.line - 1,
                    column_index=var_decl_item_ctx.start.column
                )
        return None

    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)
        
        # Если это просто expression (например, вызов процедуры без присваивания результата)
        if ctx.expression() and not ctx.ASSIGN():
            kiv_self.expression_evaluator.visit(ctx.expression())
            return

        # Если это lvalue ASSIGN expression
        if ctx.lvalue() and ctx.ASSIGN() and ctx.expression():
            lvalue_ctx = ctx.lvalue()
            var_name_node = lvalue_ctx.qualifiedIdentifier()
            
            # Вычисляем правую часть
            value_to_assign = kiv_self.expression_evaluator.visit(ctx.expression())
            if value_to_assign is None:
                 raise KumirRuntimeError(
                    f"Правая часть присваивания для '{lvalue_ctx.getText()}' не может быть вычислена (None).",
                    line_index=ctx.expression().start.line -1,
                    column_index=ctx.expression().start.column
                )

            if lvalue_ctx.RETURN_VALUE(): # Присваивание в 'знач' (возврат из функции)
                from ..definitions import FunctionReturnException
                kiv_self.procedure_manager.set_return_value(value_to_assign)
                # Генерируем исключение для немедленного возврата из функции
                raise FunctionReturnException(value_to_assign)

            elif var_name_node:
                var_name = var_name_node.getText()
                index_list_ctx = lvalue_ctx.indexList()

                if index_list_ctx: # Присваивание элементу массива/таблицы
                    # Собираем индексы
                    indices = []
                    if index_list_ctx.expression():
                        for i in range(len(index_list_ctx.expression())):
                            idx_expr_ctx = index_list_ctx.expression(i)
                            idx_kv = kiv_self.expression_evaluator.visit(idx_expr_ctx)
                            if idx_kv is None or idx_kv.kumir_type != KumirType.INT.value:
                                raise KumirTypeError(
                                    f"Индекс для '{var_name}' должен быть целым числом, получен {idx_kv}.",
                                    line_index=idx_expr_ctx.start.line -1,
                                    column_index=idx_expr_ctx.start.column
                                )
                            indices.append(idx_kv.value)
                    
                    # Проверяем, есть ли ':' для среза (пока не поддерживаем присваивание срезам)
                    if index_list_ctx.COLON():
                        raise KumirNotImplementedError(
                            f"Присваивание срезам таблиц ('{var_name}[{index_list_ctx.getText()}]') пока не поддерживается.",
                            line_index=index_list_ctx.start.line-1,
                            column_index=index_list_ctx.start.column
                        )

                    kiv_self.scope_manager.update_table_element(
                        var_name,
                        indices,
                        value_to_assign,
                        line_index=lvalue_ctx.start.line -1,
                        column_index=lvalue_ctx.start.column
                    )
                else: # Присваивание обычной переменной
                    kiv_self.scope_manager.update_variable(
                        var_name,
                        value_to_assign,
                        line_index=lvalue_ctx.start.line -1,
                        column_index=lvalue_ctx.start.column
                    )
            else:
                raise KumirSyntaxError(
                    f"Некорректная левая часть присваивания: {lvalue_ctx.getText()}",
                    line_index=lvalue_ctx.start.line-1,
                    column_index=lvalue_ctx.start.column
                )
        else:
            raise KumirSyntaxError(
                f"Некорректная инструкция присваивания: {ctx.getText()}",
                line_index=ctx.start.line-1,
                column_index=ctx.start.column
            )
        return None

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)
        
        if ctx.OUTPUT(): # Проверяем, что это команда ВЫВОД
            current_output = ""

            for i, arg_ctx in enumerate(ctx.ioArgumentList().ioArgument()):
                if arg_ctx.expression():
                    # arg_ctx.expression() возвращает список выражений
                    expressions = arg_ctx.expression()
                    if expressions:
                        # Берём первое выражение (основное значение для вывода)
                        main_expr = expressions[0]
                        value_to_print = kiv_self.expression_evaluator.visit(main_expr)
                        
                        if value_to_print is None:
                            raise KumirRuntimeError(
                                f"Не удалось вычислить значение для вывода аргумента {i+1} процедуры ВЫВОД.",
                                line_index=main_expr.start.line -1,
                                column_index=main_expr.start.column
                            )

                        # Обработка форматных спецификаторов
                        field_width = None
                        precision = None
                        
                        # Проверяем наличие форматных спецификаторов
                        if len(expressions) > 1:
                            # Второе выражение - ширина поля
                            width_expr = expressions[1]
                            width_value = kiv_self.expression_evaluator.visit(width_expr)
                            if width_value and width_value.kumir_type == KumirType.INT.value:
                                field_width = width_value.value
                                
                        if len(expressions) > 2:
                            # Третье выражение - точность (для вещественных чисел)
                            precision_expr = expressions[2]
                            precision_value = kiv_self.expression_evaluator.visit(precision_expr)
                            if precision_value and precision_value.kumir_type == KumirType.INT.value:
                                precision = precision_value.value

                    # Преобразование значения к строке с учетом типа и форматирования
                    formatted_str = ""
                    if value_to_print.kumir_type == KumirType.INT.value:
                        formatted_str = str(value_to_print.value)
                    elif value_to_print.kumir_type == KumirType.REAL.value:
                        if precision is not None:
                            # Форматируем с заданной точностью
                            formatted_str = f"{value_to_print.value:.{precision}f}"
                        else:
                            # Используем правильное форматирование для вещественных чисел КуМира
                            # Если это целое число (7.0), выводим как целое (7)
                            from ..utils import to_output_string
                            formatted_str = to_output_string(value_to_print)
                    elif value_to_print.kumir_type == KumirType.BOOL.value:
                        formatted_str = "истина" if value_to_print.value else "ложь"
                    elif value_to_print.kumir_type == KumirType.CHAR.value:
                        formatted_str = value_to_print.value
                    elif value_to_print.kumir_type == KumirType.STR.value:
                        formatted_str = value_to_print.value
                    else:
                        raise KumirTypeError(
                            f"Неизвестный или неподдерживаемый тип значения для вывода: {value_to_print.kumir_type}",
                            line_index=arg_ctx.start.line -1,
                            column_index=arg_ctx.start.column
                        )
                    
                    # Применяем форматирование ширины поля
                    if field_width is not None:
                        formatted_str = formatted_str.rjust(field_width)
                    
                    current_output += formatted_str

            if hasattr(kiv_self, 'io_handler') and kiv_self.io_handler is not None:
                kiv_self.io_handler.write_output(current_output)
            else:
                print(f"WARNING: io_handler is not available in StatementHandler. Output: {current_output}", file=sys.stderr)

        elif ctx.INPUT(): # Проверяем, что это команда ВВОД
            if not hasattr(kiv_self, 'io_handler') or kiv_self.io_handler is None:
                raise KumirRuntimeError("Обработчик ввода-вывода (io_handler) не инициализирован.",
                                        line_index=ctx.start.line -1,
                                        column_index=ctx.start.column)

            echo_values = []  # Собираем эхо всех введенных значений

            for i, arg_ctx in enumerate(ctx.ioArgumentList().ioArgument()):
                if arg_ctx.expression():
                    # For INPUT, we need to get the lvalue to assign to
                    # This is a bit tricky since we're expecting the expression to be an lvalue
                    expressions = arg_ctx.expression()
                    if expressions:
                        # Берём первое выражение (основное значение для ввода)
                        expr_ctx = expressions[0]
                        
                        # Try to extract variable info from the expression
                        target_var_name = ""
                        is_array_element = False
                        
                        # For now, handle simple cases - ID and postfix with array access
                        if hasattr(expr_ctx, 'getText'):
                            target_var_name = expr_ctx.getText()
                            # Extract just the variable name if it has array notation
                            if '[' in target_var_name and ']' in target_var_name:
                                target_var_name = target_var_name.split('[')[0]
                                is_array_element = True
                            # Otherwise it's a simple variable, keep is_array_element = False

                    try:
                        var_info = kiv_self.scope_manager.get_variable_info(target_var_name)
                        target_type = var_info['kumir_type']
                        is_array = var_info['is_table']

                    except KumirNameError:
                        raise KumirNameError(f"Переменная '{target_var_name}' не объявлена.",
                                             line_index=arg_ctx.start.line -1,
                                             column_index=arg_ctx.start.column)

                    input_str = kiv_self.io_handler.get_input_line("")

                    try:
                        if is_array_element:
                            # For array elements, we'll use the expression evaluator to handle the assignment
                            # This is a simplified approach for now
                            raise KumirNotImplementedError(
                                "Ввод в элементы массива пока не поддерживается полностью.",
                                line_index=arg_ctx.start.line -1,
                                column_index=arg_ctx.start.column
                            )
                        else: # Ввод в простую переменную
                            if target_type == KumirType.INT:
                                converted_value = KumirValue(int(input_str), KumirType.INT.value)
                            elif target_type == KumirType.REAL:
                                converted_value = KumirValue(float(input_str.replace(',', '.')), KumirType.REAL.value)
                            elif target_type == KumirType.BOOL:
                                if input_str.lower() in ["истина", "true", "1"]:
                                    converted_value = KumirValue(True, KumirType.BOOL.value)
                                elif input_str.lower() in ["ложь", "false", "0"]:
                                    converted_value = KumirValue(False, KumirType.BOOL.value)
                                else:
                                    raise ValueError("Для лог типа ожидалось 'истина' или 'ложь'.")
                            elif target_type == KumirType.CHAR:
                                if len(input_str) == 1:
                                    converted_value = KumirValue(input_str, KumirType.CHAR.value)
                                else:
                                    raise ValueError("Для лит типа ожидался один символ.")
                            elif target_type == KumirType.STR:
                                converted_value = KumirValue(input_str, KumirType.STR.value)
                            else:
                                raise KumirTypeError(f"Ввод для переменной типа {target_type} не поддерживается.")
                            
                            kiv_self.scope_manager.update_variable(target_var_name, converted_value,
                                                               line_index=arg_ctx.start.line -1,
                                                               column_index=arg_ctx.start.column)
                            
                            # Формируем эхо для этого значения
                            if converted_value.kumir_type == KumirType.INT.value:
                                echo_text = str(converted_value.value)
                            elif converted_value.kumir_type == KumirType.REAL.value:
                                # Используем правильное форматирование для вещественных чисел КуМира
                                from ..utils import to_output_string
                                echo_text = to_output_string(converted_value)
                            elif converted_value.kumir_type == KumirType.BOOL.value:
                                echo_text = "истина" if converted_value.value else "ложь"
                            elif converted_value.kumir_type == KumirType.CHAR.value:
                                echo_text = converted_value.value
                            elif converted_value.kumir_type == KumirType.STR.value:
                                echo_text = converted_value.value
                            else:
                                echo_text = str(converted_value.value)
                            
                            echo_values.append(echo_text)

                    except ValueError as e:
                        raise KumirTypeError(f"Ошибка преобразования ввода для '{target_var_name}': {input_str}. {e}",
                                             line_index=arg_ctx.start.line -1,
                                             column_index=arg_ctx.start.column)
                else:
                    raise KumirSyntaxError("Аргумент для ВВОД должен быть переменной или элементом массива.",
                                           line_index=arg_ctx.start.line -1,
                                           column_index=arg_ctx.start.column)
            
            # Выводим эхо всех введенных значений одной строкой через пробел
            if echo_values:
                echo_line = ' '.join(echo_values) + '\n'
                kiv_self.io_handler.write_output(echo_line)
        
        return None

    def visitIfStatement(self, ctx: KumirParser.IfStatementContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)
        condition_val = kiv_self.expression_evaluator.visit(ctx.expression())
        
        # Use the helper method for proper boolean evaluation
        condition_result = self._evaluate_condition(condition_val, "операторе ЕСЛИ", ctx.expression())

        if condition_result: # значение True
            self.visit(ctx.statementSequence(0)) # Блок ТО
        elif ctx.ELSE(): # Есть блок ИНАЧЕ
            self.visit(ctx.statementSequence(1)) # Блок ИНАЧЕ
        return None    # visitSwitchStatement реализован в ControlFlowVisitorMixin    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)

        if ctx.loopSpecifier():
            specifier = ctx.loopSpecifier()
            if specifier.WHILE(): # НЦ ПОКА условие ... КЦ
                while True:
                    condition_expr = specifier.expression(0)  # Получаем первое выражение
                    condition_val = kiv_self.expression_evaluator.visit(condition_expr)
                    
                    # Use the helper method for proper boolean evaluation
                    condition_result = self._evaluate_condition(condition_val, "цикле ПОКА", condition_expr)
                    if not condition_result:
                        break                    
                    try:
                        self.visit(ctx.statementSequence())
                    except ContinueSignal:
                        continue
                    except BreakSignal:
                        break
                
            elif specifier.FOR(): # НЦ ДЛЯ к от нач до кон шаг ш ... КЦ
                var_name = specifier.ID().getText()
                start_expr = specifier.expression(0)
                end_expr = specifier.expression(1)
                step_expr = specifier.expression(2) if len(specifier.expression()) > 2 else None

                start_val_kv = kiv_self.expression_evaluator.visit(start_expr)
                end_val_kv = kiv_self.expression_evaluator.visit(end_expr)
                
                step_val = 1
                if step_expr:
                    step_val_kv = kiv_self.expression_evaluator.visit(step_expr)
                    if step_val_kv is None or step_val_kv.kumir_type != KumirType.INT.value:
                         raise KumirTypeError(
                            f"Шаг в цикле ДЛЯ для переменной '{var_name}' должен быть целым числом.",
                            line_index=step_expr.start.line -1,
                            column_index=step_expr.start.column
                        )
                    step_val = step_val_kv.value
                    if step_val == 0:
                        raise KumirRuntimeError(
                            f"Шаг в цикле ДЛЯ для переменной '{var_name}' не может быть равен нулю.",
                             line_index=step_expr.start.line -1,
                             column_index=step_expr.start.column
                        )
                
                if not (start_val_kv and start_val_kv.kumir_type == KumirType.INT.value and \
                        end_val_kv and end_val_kv.kumir_type == KumirType.INT.value):
                    raise KumirTypeError(
                        f"Начальное и конечное значения для счетчика цикла '{var_name}' должны быть целыми числами.",
                        line_index=start_expr.start.line -1,
                        column_index=start_expr.start.column
                    )

                current_val = start_val_kv.value
                
                try:
                    var_info = kiv_self.scope_manager.get_variable_info(var_name)
                    if var_info['kumir_type'] != KumirType.INT and var_info['kumir_type'] != KumirType.REAL:
                         raise KumirTypeError(
                            f"Переменная цикла '{var_name}' должна быть числового типа (цел или вещ).",
                            line_index=specifier.ID().getSymbol().line -1,
                            column_index=specifier.ID().getSymbol().column
                        )
                except KumirNameError:
                    raise KumirNameError(
                        f"Переменная цикла '{var_name}' не объявлена.",
                        line_index=specifier.ID().getSymbol().line -1,
                        column_index=specifier.ID().getSymbol().column
                    )

                loop_condition = (lambda cv, ev, sv: cv <= ev) if step_val > 0 else (lambda cv, ev, sv: cv >= ev)

                while loop_condition(current_val, end_val_kv.value, step_val):
                    kiv_self.scope_manager.update_variable(var_name, KumirValue(current_val, KumirType.INT.value),
                                                       line_index=specifier.ID().getSymbol().line -1,
                                                       column_index=specifier.ID().getSymbol().column)
                    try:
                        self.visit(ctx.statementSequence())
                    except ContinueSignal:
                        current_val += step_val
                        continue
                    except BreakSignal:
                        break
                    current_val += step_val
            
            elif specifier.TIMES(): # НЦ N РАЗ ... КЦ
                count_expr = specifier.expression(0)
                count_val_kv = kiv_self.expression_evaluator.visit(count_expr)
                if count_val_kv is None or count_val_kv.kumir_type != KumirType.INT.value:
                    raise KumirTypeError(
                        f"Количество повторений в цикле 'N РАЗ' должно быть целым числом, получено: {count_val_kv}",
                        line_index=count_expr.start.line -1,
                        column_index=count_expr.start.column
                    )
                
                for _ in range(count_val_kv.value):
                    try:
                        self.visit(ctx.statementSequence())
                    except ContinueSignal:
                        continue
                    except BreakSignal:
                        break
            else:
                raise KumirSyntaxError(f"Неизвестный спецификатор цикла: {specifier.getText()}",
                                       line_index=specifier.start.line-1, column_index=specifier.start.column)

        else: # Простой цикл НЦ ... КЦ
            while True:
                try:
                    self.visit(ctx.statementSequence())
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break 
                
                if ctx.endLoopCondition():
                    cond_expr = ctx.endLoopCondition().expression()
                    cond_val = kiv_self.expression_evaluator.visit(cond_expr)
                    if cond_val is None or cond_val.kumir_type != KumirType.BOOL.value:
                         raise KumirTypeError(
                            f"Условие в 'КЦ ПРИ' должно быть логического типа, получено: {cond_val}",
                            line_index=cond_expr.start.line -1,
                            column_index=cond_expr.start.column
                        )
                    if cond_val.value:
                        break
        return None

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext) -> None:
        # Improved exit statement handling
        # Check the context to determine the appropriate exit type
        exit_text = ctx.getText().lower()
        
        # Check if we're in a loop context by examining parent nodes
        current = ctx.parentCtx
        is_in_loop = False
        
        # Walk up the parse tree to find loop context
        while current is not None:
            # Check if we're inside a loop statement (НЦ...КЦ)
            if isinstance(current, KumirParser.LoopStatementContext):
                is_in_loop = True
                break
            current = current.parentCtx if hasattr(current, 'parentCtx') else None
        
        # Determine the type of exit based on context and text
        if ("цикла" in exit_text or "loop" in exit_text or is_in_loop):
            # Exit from loop
            raise BreakSignal()
        elif ("процедуры" in exit_text or "procedure" in exit_text):
            # Exit from procedure
            raise ReturnSignal()
        else:
            # Default behavior - if ambiguous, prefer loop exit if we're in a loop
            if is_in_loop:
                raise BreakSignal()
            else:
                # Otherwise, stop execution entirely
                raise StopExecutionSignal()
        
        return None

    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)
        proc_name = ctx.qualifiedIdentifier().getText()
        args_ctx = ctx.argumentList()
        actual_args = []
        if args_ctx and args_ctx.expressionList():
            for expr_ctx in args_ctx.expressionList().expression():
                arg_val = kiv_self.expression_evaluator.visit(expr_ctx)
                if arg_val is None:
                    raise KumirRuntimeError(
                        f"Не удалось вычислить аргумент для вызова процедуры '{proc_name}'.",
                        line_index=expr_ctx.start.line -1,
                        column_index=expr_ctx.start.column
                    )
                actual_args.append(arg_val)
        
        kiv_self.procedure_manager.call_procedure(
            proc_name, 
            actual_args,
            line_index=ctx.start.line -1,
            column_index=ctx.start.column
        )
        return None

    def visitStopStatement(self, ctx: KumirParser.StopStatementContext) -> None:
        raise StopExecutionSignal()

    def visitPauseStatement(self, ctx: KumirParser.PauseStatementContext) -> None:
        pass

    def visitAssertionStatement(self, ctx: KumirParser.AssertionStatementContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)
        condition_val = kiv_self.expression_evaluator.visit(ctx.expression())
        
        # Use the helper method for proper boolean evaluation
        condition_result = self._evaluate_condition(condition_val, "УТВЕРЖДЕНИИ", ctx.expression())

        if not condition_result:
            error_message = "Утверждение не выполнено"
            
            raise KumirRuntimeError(
                error_message,
                line_index=ctx.start.line -1,
                column_index=ctx.start.column
            )
        return None

class StatementHandler(StatementHandlerMixin):
    def __init__(self, scope_manager, expression_evaluator, procedure_manager):
        self.scope_manager = scope_manager
        self.expression_evaluator = expression_evaluator
        self.procedure_manager = procedure_manager
