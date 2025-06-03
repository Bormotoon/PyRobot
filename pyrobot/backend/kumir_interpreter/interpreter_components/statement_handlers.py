import sys
from typing import TYPE_CHECKING, cast, Optional, List, Dict
from pyrobot.backend.kumir_interpreter.kumir_exceptions import (
    KumirRuntimeError, KumirSyntaxError, DeclarationError, KumirNameError,
    KumirTypeError, KumirArgumentError, BreakSignal, ContinueSignal, StopExecutionSignal, ExitSignal,
    KumirNotImplementedError
)
from ..generated.KumirParser import KumirParser
from ..generated.KumirParserVisitor import KumirParserVisitor
from ..generated.KumirLexer import KumirLexer
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
            # Проверяем, является ли это вызовом процедуры
            procedure_name = self._extract_procedure_name_from_expression(ctx.expression())
            print(f"[DEBUG] AssignmentStatement: извлечено имя процедуры: {procedure_name} из выражения: {ctx.expression().getText()}", file=sys.stderr)
            
            if procedure_name and hasattr(kiv_self, 'procedure_manager'):
                is_proc_defined = kiv_self.procedure_manager.is_procedure_defined(procedure_name)
                print(f"[DEBUG] AssignmentStatement: процедура '{procedure_name}' определена: {is_proc_defined}", file=sys.stderr)
                
                if is_proc_defined:
                    print(f"[DEBUG] AssignmentStatement: обрабатываем как вызов процедуры '{procedure_name}'", file=sys.stderr)
                    # Это вызов процедуры - обрабатываем через procedure call handler
                    self._handle_procedure_call_from_expression(ctx.expression())
                    return
                else:
                    print(f"[DEBUG] AssignmentStatement: '{procedure_name}' не является процедурой, обрабатываем как выражение", file=sys.stderr)
            else:
                print(f"[DEBUG] AssignmentStatement: обрабатываем как обычное выражение", file=sys.stderr)
                # Обычное выражение - в expression evaluator
                kiv_self.expression_evaluator.visit(ctx.expression())
            return

        # Если это lvalue ASSIGN expression
        if ctx.lvalue() and ctx.ASSIGN() and ctx.expression():
            lvalue_ctx = ctx.lvalue()
            var_name_node = lvalue_ctx.qualifiedIdentifier()            # Вычисляем правую часть
            value_to_assign = kiv_self.expression_evaluator.visit(ctx.expression())
            if value_to_assign is None:
                raise KumirRuntimeError(
                    f"Правая часть присваивания для '{lvalue_ctx.getText()}' не может быть вычислена (None).",
                    line_index=ctx.expression().start.line -1,
                    column_index=ctx.expression().start.column
                )

            if lvalue_ctx.RETURN_VALUE(): # Присваивание в 'знач' (возврат из функции)
                # В КуМире знач := выражение НЕ прерывает выполнение функции,
                # а только устанавливает значение для возврата.
                # Функция продолжает выполняться до конца.
                print(f"[DEBUG] Устанавливаю возвращаемое значение: {value_to_assign}", file=sys.stderr)
                kiv_self.procedure_manager.set_return_value(value_to_assign)

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
                # Инициализируем переменные в начале цикла
                value_to_print = None
                field_width = None
                precision = None
                formatted_str = ""
                
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
                        # Проверяем наличие форматных спецификаторов
                        if len(expressions) > 1:
                            # Второе выражение - ширина поля
                            width_expr = expressions[1]
                            width_value = kiv_self.expression_evaluator.visit(width_expr)
                            if width_value and width_value.kumir_type == KumirType.INT.value:
                                field_width = width_value.value
                                
                        if len(expressions) > 2:                            # Третье выражение - точность (для вещественных чисел)
                            precision_expr = expressions[2]
                            precision_value = kiv_self.expression_evaluator.visit(precision_expr)
                            if precision_value and precision_value.kumir_type == KumirType.INT.value:
                                precision = precision_value.value                        # Преобразование значения к строке с учетом типа и форматирования
                        # Нормализуем тип - обрабатываем и строковый и enum варианты
                        type_value = value_to_print.kumir_type
                        if hasattr(type_value, 'value'):
                            # Это enum объект, берем его значение
                            type_value = type_value.value
                        
                        if type_value == KumirType.INT.value or type_value == 'ЦЕЛ':
                            formatted_str = str(value_to_print.value)
                        elif type_value == KumirType.REAL.value or type_value == 'ВЕЩ':
                            if precision is not None:
                                # Форматируем с заданной точностью
                                formatted_str = f"{value_to_print.value:.{precision}f}"
                            else:
                                # Используем правильное форматирование для вещественных чисел КуМира
                                # Если это целое число (7.0), выводим как целое (7)
                                from ..utils import to_output_string
                                formatted_str = to_output_string(value_to_print)
                        elif type_value == KumirType.BOOL.value or type_value == 'ЛОГ':
                            formatted_str = "истина" if value_to_print.value else "ложь"
                        elif type_value == KumirType.CHAR.value or type_value == 'СИМ':
                            formatted_str = value_to_print.value
                        elif type_value == KumirType.STR.value or type_value == 'ЛИТЕР':
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
                # Инициализируем переменные в начале цикла
                target_var_name = ""
                is_array_element = False
                
                if arg_ctx.expression():
                    # For INPUT, we need to get the lvalue to assign to
                    # This is a bit tricky since we're expecting the expression to be an lvalue
                    # Но пока просто поддержим ввод в простые переменные
                    expressions = arg_ctx.expression()
                    if expressions:
                        # Берём первое выражение (основное значение для ввода)
                        expr_ctx = expressions[0]
                        
                        # Try to extract variable info from the expression
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
        elif ("процедуры" in exit_text or "procedure" in exit_text) or "все" in exit_text or "all" in exit_text:
            # Exit from procedure (вызов все / all)
            raise ExitSignal()
        else:
            # Default behavior - если контекст неоднозначен, в цикле используем выход из цикла
            if is_in_loop:
                raise BreakSignal()
            else:
                # Иначе, выход из текущей процедуры/алгоритма
                raise ExitSignal()
        return None

    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext) -> None:
        kiv_self = cast('KumirInterpreterVisitor', self)
        proc_name = ctx.qualifiedIdentifier().getText()
        args_ctx = ctx.argumentList()
        actual_args = []
        if args_ctx:
            # argumentList содержит expression напрямую, а не через expressionList
            for expr_ctx in args_ctx.expression():
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

    def _extract_procedure_name_from_expression(self, expr_ctx: 'KumirParser.ExpressionContext') -> Optional[str]:
        """
        Извлекает имя алгоритма из expression context для проверки, является ли это вызовом процедуры.
        
        Анализирует структуру AST: expression → logicalOrExpression → ... → postfixExpression → primaryExpression → qualifiedIdentifier
        
        Returns:
            str: Имя алгоритма, если это вызов функции/процедуры
            None: Если это не вызов или не удалось извлечь имя
        """
        try:
            # expression → logicalOrExpression
            log_or_expr = expr_ctx.logicalOrExpression()
            if not log_or_expr:
                return None
            
            # logicalOrExpression → logicalAndExpression (берем первую)
            log_and_exprs = log_or_expr.logicalAndExpression()
            if not log_and_exprs or len(log_and_exprs) == 0:
                return None
            log_and_expr = log_and_exprs[0]
            
            # logicalAndExpression → equalityExpression (берем первую)
            eq_exprs = log_and_expr.equalityExpression()
            if not eq_exprs or len(eq_exprs) == 0:
                return None
            eq_expr = eq_exprs[0]
            
            # equalityExpression → relationalExpression (берем первую)
            rel_exprs = eq_expr.relationalExpression()
            if not rel_exprs or len(rel_exprs) == 0:
                return None
            rel_expr = rel_exprs[0]
            
            # relationalExpression → additiveExpression (берем первую)
            add_exprs = rel_expr.additiveExpression()
            if not add_exprs or len(add_exprs) == 0:
                return None
            add_expr = add_exprs[0]
            
            # additiveExpression → multiplicativeExpression (берем первую)
            mul_exprs = add_expr.multiplicativeExpression()
            if not mul_exprs or len(mul_exprs) == 0:
                return None
            mul_expr = mul_exprs[0]
            
            # multiplicativeExpression → powerExpression (берем первую)
            pow_exprs = mul_expr.powerExpression()
            if not pow_exprs or len(pow_exprs) == 0:
                return None
            pow_expr = pow_exprs[0]
            
            # powerExpression → unaryExpression
            unary_expr = pow_expr.unaryExpression()
            if not unary_expr:
                return None
            
            # unaryExpression → postfixExpression (если без унарных операторов)
            postfix_expr = unary_expr.postfixExpression()
            if not postfix_expr:
                return None
            
            # postfixExpression → primaryExpression
            primary_expr = postfix_expr.primaryExpression()
            if not primary_expr:
                return None
            
            # primaryExpression → qualifiedIdentifier
            qualified_id = primary_expr.qualifiedIdentifier()
            if not qualified_id:
                return None
              # Проверяем, что у postfixExpression есть аргументы (признак вызова с параметрами)
            # Структура: primaryExpression LPAREN argumentList? RPAREN
            has_arguments = False
            if len(postfix_expr.children) > 1:
                for i in range(1, len(postfix_expr.children)):
                    child = postfix_expr.children[i]
                    # Используем getattr для безопасной проверки типа токена
                    if hasattr(child, 'getSymbol') and getattr(child.getSymbol(), 'type', None) == getattr(KumirLexer, 'LPAREN', None):
                        # Это вызов функции/процедуры с аргументами
                        has_arguments = True
                        break
            
            # Возвращаем имя как потенциальный вызов процедуры 
            # (независимо от того, есть ли аргументы)
            # Вызывающий код должен проверить, является ли это действительно процедурой
            return qualified_id.getText()
            
        except Exception:
            # Если что-то пошло не так при анализе AST, возвращаем None
            return None
            
    def _handle_procedure_call_from_expression(self, expr_ctx: 'KumirParser.ExpressionContext') -> None:
        """
        Обрабатывает вызов процедуры из expression context.
        Извлекает имя процедуры и аргументы из AST и вызывает procedure_manager.
        """
        kiv_self = cast('KumirInterpreterVisitor', self)
        
        # Извлекаем имя процедуры (мы уже знаем, что это вызов процедуры)
        procedure_name = self._extract_procedure_name_from_expression(expr_ctx)
        if not procedure_name:
            raise KumirRuntimeError(
                f"Не удалось извлечь имя процедуры из выражения: {expr_ctx.getText()}",
                line_index=expr_ctx.start.line - 1,
                column_index=expr_ctx.start.column
            )
        print(f"[DEBUG] _handle_procedure_call_from_expression: procedure_name = {procedure_name}", file=sys.stderr)
          # Извлекаем выражения аргументов из postfix expression
        arg_expressions = []
        postfix_expr = self._extract_postfix_expression(expr_ctx)
        print(f"[DEBUG] _handle_procedure_call_from_expression: postfix_expr = {postfix_expr}", file=sys.stderr)
        
        if postfix_expr is None:
            print(f"[DEBUG] _handle_procedure_call_from_expression: postfix_expr is None!", file=sys.stderr)
        else:
            print(f"[DEBUG] _handle_procedure_call_from_expression: postfix_expr has {len(postfix_expr.children)} children", file=sys.stderr)
            
            # Проходим по детям postfixExpression: name LPAREN argumentList? RPAREN
            for i, child in enumerate(postfix_expr.children):
                child_type = type(child).__name__
                child_text = child.getText() if hasattr(child, 'getText') else str(child)
                print(f"[DEBUG] _handle_procedure_call_from_expression: child[{i}] type={child_type}, text='{child_text}'", file=sys.stderr)
                
                # Ищем ArgumentListContext (по названию класса)
                if 'ArgumentList' in child_type:
                    print(f"[DEBUG] _handle_procedure_call_from_expression: Найден ArgumentListContext!", file=sys.stderr)
                    if hasattr(child, 'expression'):
                        expressions = child.expression()
                        print(f"[DEBUG] _handle_procedure_call_from_expression: ArgumentList содержит {len(expressions) if expressions else 0} выражений", file=sys.stderr)
                        if expressions:
                            arg_expressions = expressions
                            break
                    break          # Анализируем аргументы с учетом режимов параметров
        try:
            analyzed_args = self._analyze_procedure_arguments(procedure_name, arg_expressions)
            
            # Вызываем процедуру через procedure_manager
            try:
                kiv_self.procedure_manager.call_procedure_with_analyzed_args(
                    procedure_name,
                    analyzed_args,
                    line_index=expr_ctx.start.line - 1,
                    column_index=expr_ctx.start.column
                )
            except ExitSignal:
                # ExitSignal от процедуры должен завершать ТОЛЬКО саму процедуру,
                # а НЕ пробрасываться дальше. Это стандартная семантика КуМира.
                print(f"[DEBUG] _handle_procedure_call_from_expression: перехватили ExitSignal, НЕ пробрасываем (процедура завершена корректно)", file=sys.stderr)
                # НЕ пробрасываем ExitSignal дальше - процедура корректно завершилась
                
        except Exception as e:
            print(f"[DEBUG] _handle_procedure_call_from_expression: перехватили исключение типа {type(e).__name__}: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            if isinstance(e, (KumirRuntimeError, KumirTypeError, KumirNameError)):
                raise
            else:
                raise KumirRuntimeError(
                    f"Ошибка при вызове процедуры из выражения: {str(e)}",
                    line_index=expr_ctx.start.line - 1,
                    column_index=expr_ctx.start.column
                )

    def _extract_postfix_expression(self, expr_ctx: 'KumirParser.ExpressionContext'):
        """Извлекает postfixExpression из expression context"""
        try:
            log_or_expr = expr_ctx.logicalOrExpression()
            if not log_or_expr:
                return None
            
            log_and_exprs = log_or_expr.logicalAndExpression()
            if not log_and_exprs:
                return None
            log_and_expr = log_and_exprs[0]
            
            eq_exprs = log_and_expr.equalityExpression()
            if not eq_exprs:
                return None
            eq_expr = eq_exprs[0]
            
            rel_exprs = eq_expr.relationalExpression()
            if not rel_exprs:
                return None
            rel_expr = rel_exprs[0]
            
            add_exprs = rel_expr.additiveExpression()
            if not add_exprs:
                return None
            add_expr = add_exprs[0]
            
            mul_exprs = add_expr.multiplicativeExpression()
            if not mul_exprs:
                return None
            mul_expr = mul_exprs[0]
            
            pow_exprs = mul_expr.powerExpression()
            if not pow_exprs:
                return None
            pow_expr = pow_exprs[0]
            
            unary_expr = pow_expr.unaryExpression()
            if not unary_expr:
                return None
            
            return unary_expr.postfixExpression()
        except:
            return None

    def _analyze_procedure_arguments(self, procedure_name: str, arg_expressions: List['KumirParser.ExpressionContext']) -> List[Dict]:
        """
        Анализирует аргументы процедуры с учетом режимов параметров ('арг', 'рез', 'аргрез').
        Возвращает список словарей с информацией о каждом аргументе.
        """
        kiv_self = cast('KumirInterpreterVisitor', self)
        
        # Получаем информацию о процедуре
        proc_name_lower = procedure_name.lower()
        if proc_name_lower not in kiv_self.procedure_manager.procedures:
            raise KumirNameError(f"Процедура '{procedure_name}' не определена.")
        
        proc_data = kiv_self.procedure_manager.procedures[proc_name_lower]
        formal_params_list = list(proc_data['params'].values())
        
        # Проверяем количество аргументов
        if len(arg_expressions) != len(formal_params_list):
            raise KumirArgumentError(
                f"Неверное количество аргументов для процедуры '{procedure_name}'. "
                f"Ожидается {len(formal_params_list)}, получено {len(arg_expressions)}."
            )
        
        analyzed_args = []
        
        for i, (expr_ctx, formal_param) in enumerate(zip(arg_expressions, formal_params_list)):
            param_mode = formal_param['mode']
            param_name = formal_param.get('name', f'параметр {i+1}')
            
            # DEBUG: анализ режима параметра убран для production
            pass
            
            if param_mode in ['арг', 'arg']:
                # Для 'арг' параметров вычисляем значение
                arg_value = kiv_self.expression_evaluator.visit(expr_ctx)
                if arg_value is None:
                    raise KumirRuntimeError(f"Не удалось вычислить значение аргумента для параметра '{param_name}'")
                
                analyzed_args.append({
                    'mode': param_mode,
                    'value': arg_value,
                    'variable_info': None  # Для 'арг' не нужно
                })
                
            elif param_mode in ['рез', 'res', 'аргрез', 'argres']:
                # Для 'рез'/'аргрез' нужно извлечь имя переменной для обратной записи
                var_name = self._extract_variable_name_from_expression(expr_ctx)
                if not var_name:
                    raise KumirRuntimeError(
                        f"Для параметра режима '{param_mode}' требуется переменная, "
                        f"а не выражение: {expr_ctx.getText()}"
                    )
                
                # Для 'аргрез' также вычисляем исходное значение
                arg_value = None
                if param_mode in ['аргрез', 'argres']:
                    arg_value = kiv_self.expression_evaluator.visit(expr_ctx)
                    if arg_value is None:
                        raise KumirRuntimeError(f"Не удалось вычислить значение аргумента для параметра '{param_name}'")
                
                # Получаем информацию о переменной для обратной записи
                var_info = kiv_self.scope_manager.find_variable_with_scope_depth(var_name)
                if not var_info:
                    raise KumirNameError(f"Переменная '{var_name}' не определена")
                
                analyzed_args.append({
                    'mode': param_mode,
                    'value': arg_value,  # None для 'рез', значение для 'аргрез'
                    'variable_info': {
                        'name': var_name,
                        'scope_depth': var_info[1],  # Глубина области видимости
                        'current_value': var_info[0]['value']  # Текущее значение
                    }
                })
                
            else:
                raise KumirRuntimeError(f"Неизвестный режим параметра: '{param_mode}'")
        
        return analyzed_args

    def _extract_variable_name_from_expression(self, expr_ctx: 'KumirParser.ExpressionContext') -> Optional[str]:
        """
        Извлекает имя переменной из простого выражения вида 'имя_переменной'.
        Возвращает None, если выражение не является простой переменной.
        """
        try:
            # Проходим по цепочке: expression -> logicalOrExpression -> ... -> postfixExpression
            postfix_expr = self._extract_postfix_expression(expr_ctx)
            if not postfix_expr or not postfix_expr.children:
                return None
            
            # Проверяем, что это простой identifier (один элемент)
            if len(postfix_expr.children) == 1:
                child = postfix_expr.children[0]
                if hasattr(child, 'getText'):
                    return child.getText()
            
            return None
        except:
            return None

class StatementHandler(StatementHandlerMixin):
    def __init__(self, scope_manager, expression_evaluator, procedure_manager):
        self.scope_manager = scope_manager
        self.expression_evaluator = expression_evaluator
        self.procedure_manager = procedure_manager
