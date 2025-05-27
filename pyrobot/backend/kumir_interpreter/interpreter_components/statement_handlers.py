from pyrobot.backend.kumir_interpreter.kumir_exceptions import (
    KumirRuntimeError, KumirSyntaxError, DeclarationError, KumirNameError,
    KumirTypeError, KumirArgumentError, BreakSignal, ContinueSignal, StopExecutionSignal, ReturnSignal, # Изменено StopSignal на StopExecutionSignal
    KumirNotImplementedError # Убедимся, что этот импорт корректен
)
from ..generated.KumirParser import KumirParser
from ..generated.KumirParserVisitor import KumirParserVisitor
from ..kumir_datatypes import KumirType, KumirValue # Удалены ArrayBounds, ArrayValue
from .scope_manager import ScopeManager
from .expression_evaluator import ExpressionEvaluator
from .procedure_manager import ProcedureManager

class StatementHandlerMixin(KumirParserVisitor):
    def __init__(self, scope_manager: ScopeManager, expression_evaluator: ExpressionEvaluator, procedure_manager: ProcedureManager):
        self.scope_manager = scope_manager
        self.expression_evaluator = expression_evaluator
        self.procedure_manager = procedure_manager

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
        var_type_node = ctx.typeSpecifier()
        kumir_type, is_type_inherently_array = self._determine_kumir_type_and_array_status(var_type_node)

        for var_decl_item_ctx in ctx.variableList().variableDeclarationItem():
            var_name = var_decl_item_ctx.ID().getText()
            initial_value: KumirValue | None = None
            
            # Проверяем, есть ли инициализатор (= выражение)
            if var_decl_item_ctx.expression():
                initial_value_expr_ctx = var_decl_item_ctx.expression()
                initial_value = self.expression_evaluator.visit(initial_value_expr_ctx)
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

                        lower_val_kv = self.expression_evaluator.visit(lower_bound_expr)
                        upper_val_kv = self.expression_evaluator.visit(upper_bound_expr)

                        if not (lower_val_kv and lower_val_kv.kumir_type == KumirType.INT.value and
                                upper_val_kv and upper_val_kv.kumir_type == KumirType.INT.value): # Сравнение с .value
                            raise KumirTypeError(
                                f"Границы массива для '{var_name}' должны быть целыми числами.",
                                line_index=bound_ctx.start.line - 1,
                                column_index=bound_ctx.start.column
                            )
                        dimensions.append((lower_val_kv.value, upper_val_kv.value))
                
                # Если тип сам по себе массив (целтаб), но границы не указаны,
                # то это динамический массив (размеры могут быть не заданы при объявлении).
                # В таком случае dimensions останется пустым, scope_manager должен это обработать.
                
                self.scope_manager.declare_array(
                    var_name,
                    kumir_type, # Базовый тип элементов массива
                    dimensions,
                    line_index=var_decl_item_ctx.start.line - 1,
                    column_index=var_decl_item_ctx.start.column
                )

                if initial_value:
                    if initial_value.kumir_type == KumirType.TABLE.value: # Сравнение с .value
                        # Присваиваем табличный литерал объявленному массиву
                        self.scope_manager.update_variable(var_name, initial_value,
                                                          line_index=var_decl_item_ctx.expression().start.line - 1,
                                                          column_index=var_decl_item_ctx.expression().start.column)
                    else:
                        raise KumirTypeError(
                            f"Для массива '{var_name}' ожидался табличный литерал в качестве инициализатора, но получен {initial_value.kumir_type}.",
                            line_index=var_decl_item_ctx.expression().start.line - 1,
                            column_index=var_decl_item_ctx.expression().start.column
                        )
            else: # Обычная переменная (не массив)
                self.scope_manager.declare_variable(
                    var_name,
                    kumir_type,
                    initial_value, # Может быть None
                    line_index=var_decl_item_ctx.start.line - 1,
                    column_index=var_decl_item_ctx.start.column
                )
        return None

    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext) -> None:
        # Логика присваивания: lvalue ASSIGN expression
        # или просто expression (например, вызов процедуры)
        
        # Если это просто expression (например, вызов процедуры без присваивания результата)
        if ctx.expression() and not ctx.ASSIGN():
            self.expression_evaluator.visit(ctx.expression())
            return

        # Если это lvalue ASSIGN expression
        if ctx.lvalue() and ctx.ASSIGN() and ctx.expression():
            lvalue_ctx = ctx.lvalue()
            var_name_node = lvalue_ctx.qualifiedIdentifier() # Может быть None, если lvalue это 'знач'
            
            # Вычисляем правую часть
            value_to_assign = self.expression_evaluator.visit(ctx.expression())
            if value_to_assign is None:
                 raise KumirRuntimeError(
                    f"Правая часть присваивания для '{lvalue_ctx.getText()}' не может быть вычислена (None).",
                    line_index=ctx.expression().start.line -1,
                    column_index=ctx.expression().start.column
                )

            if lvalue_ctx.RETURN_VALUE(): # Присваивание в 'знач' (возврат из функции)
                # print(f"Assigning to RETURN_VALUE: {value_to_assign}")
                # Это должно быть обработано в visitFunctionDefinition или ProcedureManager
                # Здесь мы можем, например, сохранить это значение в специальном месте ScopeManager
                # или ProcedureManager для текущей выполняемой функции.
                self.procedure_manager.set_return_value(value_to_assign)

            elif var_name_node:
                var_name = var_name_node.getText()
                index_list_ctx = lvalue_ctx.indexList()

                if index_list_ctx: # Присваивание элементу массива/таблицы
                    # print(f"Assigning to array element: {var_name}{index_list_ctx.getText()}")
                    # Логика вычисления индексов и обновления элемента таблицы
                    # Это должно быть в self.expression_evaluator или ScopeManager
                    # self.expression_evaluator.assign_table_element(var_name_node, index_list_ctx, value_to_assign)
                    # Пока что используем метод из scope_manager, если он есть, или expression_evaluator
                    
                    # Собираем индексы
                    indices = []
                    if index_list_ctx.expression(): # Может быть до двух выражений для 2D или одно для 1D/среза
                        for i in range(len(index_list_ctx.expression())):
                            idx_expr_ctx = index_list_ctx.expression(i)
                            idx_kv = self.expression_evaluator.visit(idx_expr_ctx)
                            if idx_kv is None or idx_kv.kumir_type != KumirType.INT.value: # Сравнение с .value
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

                    self.scope_manager.update_table_element(
                        var_name,
                        indices,
                        value_to_assign,
                        line_index=lvalue_ctx.start.line -1,
                        column_index=lvalue_ctx.start.column
                    )
                else: # Присваивание обычной переменной
                    # print(f"Assigning to variable: {var_name} = {value_to_assign}")
                    self.scope_manager.update_variable(
                        var_name,
                        value_to_assign,
                        line_index=lvalue_ctx.start.line -1,
                        column_index=lvalue_ctx.start.column
                    )
            else:
                # Не должно происходить, если грамматика верна (lvalue это ID или 'знач')
                raise KumirSyntaxError(
                    f"Некорректная левая часть присваивания: {lvalue_ctx.getText()}",
                    line_index=lvalue_ctx.start.line-1,
                    column_index=lvalue_ctx.start.column
                )
        else:
             # Не должно происходить, если грамматика верна
            raise KumirSyntaxError(
                f"Некорректная инструкция присваивания: {ctx.getText()}",
                line_index=ctx.start.line-1,
                column_index=ctx.start.column
            )
        return None

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext) -> None:
        # TODO: Реализовать логику для ВВОД и ВЫВОД
        # Нужно будет обращаться к self.expression_evaluator для вычисления выражений
        # и к какому-то механизму I/O (например, передаваемому в конструктор).
        # print(f"IO Statement: {ctx.getText()}")
        # if ctx.INPUT():
        #     # Логика для ВВОД
        #     for arg_ctx in ctx.ioArgumentList().ioArgument():
        #         if arg_ctx.expression(): # Ввод в переменную
        #             lvalue_expr = arg_ctx.expression() # Должно быть lvalue
        #             # ... получить имя переменной, возможно, индексы ...
        #             # ... прочитать значение от пользователя ...
        #             # ... обновить переменную через scope_manager ...
        #             pass
        # elif ctx.OUTPUT():
        #     # Логика для ВЫВОД
        #     for arg_ctx in ctx.ioArgumentList().ioArgument():
        #         if arg_ctx.NEWLINE_CONST():
        #             # print() # Вывод новой строки
        #             pass
        #         elif arg_ctx.expression():
        #             value_to_print = self.expression_evaluator.visit(arg_ctx.expression())
        #             # ... форматирование с учетом COLON ...
        #             # print(value_to_print.value, end='') # Печать значения
        #             pass
        #     # print() # Обычно вывод заканчивается переводом строки, если не было 'нс' в конце
        if ctx.OUTPUT():
            # Обработка аргументов вывода
            current_output = ""
            for i, arg_ctx in enumerate(ctx.ioArgument()):
                if arg_ctx.expression(): # Вывод выражения
                    value_to_print = self.expression_evaluator.visit(arg_ctx.expression())
                    if value_to_print is None:
                        raise KumirRuntimeError(
                            f"Не удалось вычислить значение для вывода аргумента {i+1} процедуры ВЫВОД.",
                            line_index=arg_ctx.start.line -1,
                            column_index=arg_ctx.start.column
                        )
                    
                    # Преобразование значения к строке с учетом типа
                    if value_to_print.kumir_type == KumirType.INT:
                        current_output += str(value_to_print.value)
                    elif value_to_print.kumir_type == KumirType.REAL:
                        current_output += str(value_to_print.value)
                    elif value_to_print.kumir_type == KumirType.BOOL:
                        current_output += "истина" if value_to_print.value else "ложь"
                    elif value_to_print.kumir_type == KumirType.CHAR:
                        current_output += value_to_print.value # Символы выводим как есть
                    elif value_to_print.kumir_type == KumirType.STR:
                        # Строки обрабатываем отдельно (возможно, с кавычками)
                        current_output += f'"{value_to_print.value}"'
                    else:
                        raise KumirTypeError(
                            f"Неизвестный тип значения для вывода: {value_to_print.kumir_type}",
                            line_index=arg_ctx.start.line -1,
                            column_index=arg_ctx.start.column
                        )
                else:
                    # Это литерал (например, строка) или управляющая команда (нс и др.)
                    io_val = arg_ctx.getText()
                    if io_val.startswith('"') and io_val.endswith('"'):
                        # Литерал строки, убираем кавычки
                        current_output += io_val[1:-1]
                    # Это команда 'нс' (новая строка) или другие управляющие символы
                    if io_val.lower() == "нс":
                        # Ничего не делаем, просто отменяем будущий перенос строки
                        # Фактически, это означает, что end для print будет '',
                        # но мы управляем этим через current_output
                        pass # Мы не добавляем \n в current_output
                    elif io_val.lower() == "переход": # Пример другой команды
                        current_output += "\\n" 
                    # Можно добавить другие команды
                else:
                    # Это значение для вывода
                    # ...existing code...

            # После обработки всех аргументов, если последний не был 'нс', добавляем перенос строки
            if not (ctx.ioArgument() and ctx.ioArgument()[-1].getText().lower() == 'нс'):
                current_output += '\\n'
            
            print(f"[DEBUG statement_handlers.visitIoStatement] About to call io_handler.write_output. current_output length: {len(current_output)}. current_output: >>>{current_output}<<<", file=sys.stderr)
            self.io_handler.write_output(current_output)

        elif ctx.INPUT_KW():
            # ...existing code...
    def visitIfStatement(self, ctx: KumirParser.IfStatementContext) -> None:
        # print(f"If Statement: {ctx.expression().getText()}")
        condition_val = self.expression_evaluator.visit(ctx.expression())
        if condition_val is None or condition_val.kumir_type != KumirType.BOOL:
            raise KumirTypeError(
                f"Условие в операторе ЕСЛИ должно быть логического типа, получено: {condition_val}",
                line_index=ctx.expression().start.line -1,
                column_index=ctx.expression().start.column
            )

        if condition_val.value: # значение True
            self.visit(ctx.statementSequence(0)) # Блок ТО
        elif ctx.ELSE(): # Есть блок ИНАЧЕ
            self.visit(ctx.statementSequence(1)) # Блок ИНАЧЕ
        return None

    def visitSwitchStatement(self, ctx: KumirParser.SwitchStatementContext) -> None:
        # TODO: Реализовать оператор ВЫБОР (switch)
        # print(f"Switch Statement encountered: {ctx.getText()}")
        # 1. Вычислить выражение после ВЫБОР (если оно есть по грамматике, сейчас нет)
        # 2. Пройти по всем caseBlock:
        #    - Вычислить выражение в caseBlock.expression()
        #    - Если совпало, выполнить caseBlock.statementSequence() и выйти (или нет, если fall-through)
        # 3. Если есть ELSE и ни один case не совпал, выполнить statementSequence в ELSE.
        pass

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext) -> None:
        # print(f"Loop Statement: {ctx.getText()}")
        # Общая структура для всех циклов: НЦ ... КЦ
        # Могут быть модификаторы: ПОКА, ДЛЯ, N РАЗ
        # Могут быть условия выхода: КЦ ПРИ

        if ctx.loopSpecifier():
            specifier = ctx.loopSpecifier()
            if specifier.WHILE(): # НЦ ПОКА условие ... КЦ
                # print("  Loop type: WHILE")
                while True:
                    condition_expr = specifier.expression()
                    condition_val = self.expression_evaluator.visit(condition_expr)
                    if condition_val is None or condition_val.kumir_type != KumirType.BOOL:
                        raise KumirTypeError(
                            f"Условие в цикле ПОКА должно быть логического типа, получено: {condition_val}",
                            line_index=condition_expr.start.line -1,
                            column_index=condition_expr.start.column
                        )
                    if not condition_val.value:
                        break # Выход из цикла while
                    
                    try:
                        self.visit(ctx.statementSequence())
                    except ContinueSignal:
                        continue # Переход к следующей итерации цикла while
                    except BreakSignal:
                        break # Выход из цикла while (из-за ВЫХОД)
                
            elif specifier.FOR(): # НЦ ДЛЯ к от нач до кон шаг ш ... КЦ
                # print("  Loop type: FOR")
                var_name = specifier.ID().getText()
                start_expr = specifier.expression(0)
                end_expr = specifier.expression(1)
                step_expr = specifier.expression(2) if len(specifier.expression()) > 2 else None

                start_val_kv = self.expression_evaluator.visit(start_expr)
                end_val_kv = self.expression_evaluator.visit(end_expr)
                
                step_val = 1 # Значение шага по умолчанию
                if step_expr:
                    step_val_kv = self.expression_evaluator.visit(step_expr)
                    if step_val_kv is None or step_val_kv.kumir_type != KumirType.INT: # Шаг должен быть целым
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
                
                if not (start_val_kv and start_val_kv.kumir_type == KumirType.INT and \
                        end_val_kv and end_val_kv.kumir_type == KumirType.INT):
                    raise KumirTypeError(
                        f"Начальное и конечное значения для счетчика цикла '{var_name}' должны быть целыми числами.",
                        line_index=start_expr.start.line -1, # Примерная линия
                        column_index=start_expr.start.column
                    )

                # Важно: переменная цикла создается/обновляется в текущей области видимости
                # Если ее нет, нужно объявить (но Кумир обычно требует ее объявления заранее)
                # Здесь мы будем обновлять существующую или создавать временную, если разрешено.
                # Для простоты, предположим, что переменная уже объявлена и имеет совместимый тип.
                # ScopeManager должен уметь обновлять переменную цикла.
                
                current_val = start_val_kv.value
                
                # Определяем, существует ли переменная цикла и ее тип
                try:
                    var_info = self.scope_manager.get_variable_info(var_name)
                    if var_info.kumir_type != KumirType.INT and var_info.kumir_type != KumirType.REAL: # Кумир позволяет REAL счетчики
                         raise KumirTypeError(
                            f"Переменная цикла '{var_name}' должна быть числового типа (цел или вещ).",
                            line_index=specifier.ID().getSymbol().line -1,
                            column_index=specifier.ID().getSymbol().column
                        )
                except KumirNameError: # Заменено KumirUndeclaredVariableError
                    # В стандартном Кумире переменная цикла должна быть объявлена.
                    # Если мы хотим разрешить неявное объявление, здесь нужно ее создать.
                    # Пока что будем следовать строгому правилу.
                    raise KumirNameError( # Заменено KumirUndeclaredVariableError
                        f"Переменная цикла '{var_name}' не объявлена.", # Сообщение изменено для ясности
                        line_index=specifier.ID().getSymbol().line -1,
                        column_index=specifier.ID().getSymbol().column
                    )

                loop_condition = (lambda cv, ev, sv: cv <= ev) if step_val > 0 else (lambda cv, ev, sv: cv >= ev)

                while loop_condition(current_val, end_val_kv.value, step_val):
                    self.scope_manager.update_variable(var_name, KumirValue(current_val, KumirType.INT.value), # Используем .value
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
                # print("  Loop type: N TIMES")
                count_expr = specifier.expression(0) # Первое (и единственное) выражение это N
                count_val_kv = self.expression_evaluator.visit(count_expr)
                if count_val_kv is None or count_val_kv.kumir_type != KumirType.INT:
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
            else: # Неизвестный спецификатор цикла (ошибка грамматики?)
                raise KumirSyntaxError(f"Неизвестный спецификатор цикла: {specifier.getText()}",
                                       line_index=specifier.start.line-1, column_index=specifier.start.column)

        else: # Простой цикл НЦ ... КЦ (бесконечный, если нет ВЫХОД или КЦ ПРИ)
            # print("  Loop type: Simple (infinite without break/endloop_cond)")
            while True:
                try:
                    self.visit(ctx.statementSequence())
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break 
                
                # Проверка условия КЦ ПРИ после выполнения тела цикла
                if ctx.endLoopCondition():
                    cond_expr = ctx.endLoopCondition().expression()
                    cond_val = self.expression_evaluator.visit(cond_expr)
                    if cond_val is None or cond_val.kumir_type != KumirType.BOOL:
                         raise KumirTypeError(
                            f"Условие в 'КЦ ПРИ' должно быть логического типа, получено: {cond_val}",
                            line_index=cond_expr.start.line -1,
                            column_index=cond_expr.start.column
                        )
                    if cond_val.value: # Если условие истинно, выходим
                        break
        return None

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext) -> None:
        # print("Exit Statement")
        if ctx.LOOP_EXIT(): # ВЫХОД ИЗ ЦИКЛА
            raise BreakSignal()
        elif ctx.PROCEDURE_EXIT(): # ВЫХОД (из процедуры/алгоритма)
            # В Кумире "ВЫХОД" без "ИЗ ЦИКЛА" означает выход из текущей подпрограммы (алг, под)
            # Если это главная программа (АЛГ), то это эквивалентно СТОП.
            # Если это подпрограмма, то это возврат из нее.
            # ProcedureManager должен будет это обработать.
            # Пока что будем использовать ReturnSignal без значения, если это не функция.
            # Если это функция, ReturnSignal должен нести значение.
            # Но здесь мы не знаем, функция это или процедура.
            # Пусть ProcedureManager решает, что делать с ReturnSignal()
            raise ReturnSignal() # Может быть уточнено в ProcedureManager
        return None

    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext) -> None:
        # print(f"Procedure Call Statement: {ctx.qualifiedIdentifier().getText()}")
        proc_name = ctx.qualifiedIdentifier().getText()
        # Аргументы могут отсутствовать
        args_ctx = ctx.argumentList()
        actual_args = []
        if args_ctx and args_ctx.expressionList():
            for expr_ctx in args_ctx.expressionList().expression():
                arg_val = self.expression_evaluator.visit(expr_ctx)
                if arg_val is None:
                    raise KumirRuntimeError(
                        f"Не удалось вычислить аргумент для вызова процедуры '{proc_name}'.",
                        line_index=expr_ctx.start.line -1,
                        column_index=expr_ctx.start.column
                    )
                actual_args.append(arg_val)
        
        # Вызов через ProcedureManager
        # ProcedureManager должен сам найти процедуру, проверить типы аргументов,
        # создать новый scope (если нужно), выполнить тело процедуры.
        # Если процедура - это функция, она вернет значение через ReturnSignal,
        # которое ProcedureManager должен будет передать обратно (или ExpressionEvaluator, если вызов в выражении).
        # Здесь это statement, так что возвращаемое значение функции игнорируется, если оно есть.
        self.procedure_manager.call_procedure(
            proc_name, 
            actual_args,
            line_index=ctx.start.line -1,
            column_index=ctx.start.column
        )
        return None

    def visitStopStatement(self, ctx: KumirParser.StopStatementContext) -> None:
        # print("Stop Statement")
        raise StopExecutionSignal() # Используем исправленное имя

    def visitPauseStatement(self, ctx: KumirParser.PauseStatementContext) -> None:
        # print("Pause Statement")
        # TODO: Реализовать логику ПАУЗА, если это интерактивный режим или отладка
        # В обычном пакетном выполнении может ничего не делать или выводить сообщение.
        # Для тестов пока просто pass.
        pass

    def visitAssertionStatement(self, ctx: KumirParser.AssertionStatementContext) -> None:
        # print(f"Assertion Statement: {ctx.expression().getText()}")
        condition_val = self.expression_evaluator.visit(ctx.expression())
        message_val = None
        if ctx.stringLiteral():
            # Стринг литерал в ANTLR уже содержит кавычки, их нужно убрать
            raw_text = ctx.stringLiteral().getText()
            if len(raw_text) >= 2 and raw_text.startswith('"') and raw_text.endswith('"'):
                message_text = raw_text[1:-1]
            else: # на случай если это одинарные кавычки или что-то еще
                message_text = raw_text 
            message_val = KumirValue(message_text, KumirType.STR.value)


        if condition_val is None or condition_val.kumir_type != KumirType.BOOL.value: # Сравнение с .value
            raise KumirTypeError(
                f"Условие в УТВЕРЖДЕНИЕ должно быть логического типа, получено: {condition_val}",
                line_index=ctx.expression().start.line -1,
                column_index=ctx.expression().start.column
            )

        if not condition_val.value: # Если условие ложно
            error_message = "Утверждение не выполнено"
            if message_val:
                error_message += f": {message_val.value}"
            
            raise KumirRuntimeError(
                error_message,
                line_index=ctx.start.line -1,
                column_index=ctx.start.column
            )
        return None

class StatementHandler(StatementHandlerMixin):
    def __init__(self, scope_manager: ScopeManager, expression_evaluator: ExpressionEvaluator, procedure_manager: ProcedureManager):
        super().__init__(scope_manager, expression_evaluator, procedure_manager)

    # Если потребуются какие-то специфичные для StatementHandler методы, не являющиеся visitXXX,
    # их можно добавить сюда. Пока что он просто наследует все от StatementHandlerMixin.

