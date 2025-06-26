from typing import TYPE_CHECKING, cast

from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import BreakSignal, KumirTypeError, KumirRuntimeError, KumirNotImplementedError, StopExecutionSignal
from ..kumir_datatypes import KumirValue, KumirType # Для проверки типов результатов выражений, KumirType для объявления переменной цикла
from ..utils import KumirTypeConverter

if TYPE_CHECKING:
    from .main_visitor import KumirInterpreterVisitor


class ControlFlowVisitorMixin:

    def _evaluate_condition(self, condition_val: KumirValue, context_name: str, expr_ctx) -> bool:
        """
        Evaluates a KumirValue as a boolean condition following Kumir semantics.
        For integers: 0 = False, non-zero = True
        For booleans: direct evaluation
        For other types: raises KumirTypeError
        """
        try:
            converter = KumirTypeConverter()
            return converter.to_python_bool(condition_val)
        except KumirTypeError:
            # Re-raise with more specific context
            raise KumirTypeError(
                f"Условие в {context_name} должно быть логического или целого типа, получено: {condition_val.kumir_type}",
                line_index=expr_ctx.start.line -1,
                column_index=expr_ctx.start.column
            )

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        # Избегаем циклического импорта - используем cast
        kiv_self = cast('KumirInterpreterVisitor', self)

        loop_specifier_ctx = ctx.loopSpecifier()
        statement_sequence_ctx = ctx.statementSequence()
        end_loop_condition_ctx = ctx.endLoopCondition() # Может быть None
        end_loop_simple_ctx = ctx.ENDLOOP() # Может быть None

        try:
            if loop_specifier_ctx:
                # Цикл с явным спецификатором (ДЛЯ, ПОКА, N РАЗ)
                if loop_specifier_ctx.FOR(): # нц для ...
                    # FOR ID FROM expression TO expression (STEP expression)?
                    loop_var_name = loop_specifier_ctx.ID().getText()
                    
                    start_expr_ctx = loop_specifier_ctx.expression(0)
                    end_expr_ctx = loop_specifier_ctx.expression(1)
                    step_expr_ctx = loop_specifier_ctx.expression(2) if len(loop_specifier_ctx.expression()) > 2 else None

                    start_val_node = kiv_self.visit(start_expr_ctx)
                    end_val_node = kiv_self.visit(end_expr_ctx)
                    
                    start_val = start_val_node.value if isinstance(start_val_node, KumirValue) else start_val_node
                    end_val = end_val_node.value if isinstance(end_val_node, KumirValue) else end_val_node

                    if not isinstance(start_val, int):
                        raise KumirTypeError(f"Начальное значение в цикле ДЛЯ для '{loop_var_name}' должно быть целым.", line_index=start_expr_ctx.start.line-1, column_index=start_expr_ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(start_expr_ctx))
                    if not isinstance(end_val, int):
                        raise KumirTypeError(f"Конечное значение в цикле ДЛЯ для '{loop_var_name}' должно быть целым.", line_index=end_expr_ctx.start.line-1, column_index=end_expr_ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(end_expr_ctx))

                    step_val = 1
                    if step_expr_ctx:
                        step_val_node = kiv_self.visit(step_expr_ctx)
                        step_val = step_val_node.value if isinstance(step_val_node, KumirValue) else step_val_node
                        if not isinstance(step_val, int):
                            raise KumirTypeError(f"Шаг в цикле ДЛЯ для '{loop_var_name}' должен быть целым.", line_index=step_expr_ctx.start.line-1, column_index=step_expr_ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(step_expr_ctx))
                        if step_val == 0:
                             raise KumirRuntimeError(f"Шаг в цикле ДЛЯ для '{loop_var_name}' не может быть равен нулю.", line_index=step_expr_ctx.start.line-1, column_index=step_expr_ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(step_expr_ctx))
                    
                    kiv_self.scope_manager.enter_scope() # Removed f-string scope name, not used by scope_manager
                    try:
                        # Объявляем переменную цикла как ЦЕЛ
                        loop_var_id_token = loop_specifier_ctx.ID().symbol
                        kiv_self.scope_manager.declare_variable(                            loop_var_name, 
                            KumirType.INT, # В КуМире переменная цикла ДЛЯ всегда целая
                            None, # Начальное значение присваивается ниже
                            line_index=loop_var_id_token.line - 1, 
                            column_index=loop_var_id_token.column
                        )
                        
                        current_val = start_val
                        # Первое присвоение значения переменной цикла
                        kiv_self.scope_manager.update_variable(
                            loop_var_name, 
                            KumirValue(current_val, KumirType.INT.value), 
                            line_index=loop_var_id_token.line - 1, 
                            column_index=loop_var_id_token.column
                        )

                        while (step_val > 0 and current_val <= end_val) or \
                              (step_val < 0 and current_val >= end_val):
                            # Обновление значения переменной цикла на каждой итерации
                            kiv_self.scope_manager.update_variable(
                                loop_var_name, 
                                KumirValue(current_val, KumirType.INT.value),
                                line_index=loop_var_id_token.line - 1, # Используем позицию ID переменной цикла
                                column_index=loop_var_id_token.column
                            )
                            try:
                                if statement_sequence_ctx:
                                    kiv_self.visit(statement_sequence_ctx)
                            except BreakSignal:
                                break # Выход из while по ВЫХОД
                            
                            if end_loop_condition_ctx:
                                condition_val_node = kiv_self.visit(end_loop_condition_ctx.expression())
                                condition_val = condition_val_node.value if isinstance(condition_val_node, KumirValue) else condition_val_node
                                if not isinstance(condition_val, bool):
                                    raise KumirTypeError("Условие в КЦ ПРИ должно быть логическим.", line_index=end_loop_condition_ctx.expression().start.line-1, column_index=end_loop_condition_ctx.expression().start.column, line_content=kiv_self.get_line_content_from_ctx(end_loop_condition_ctx.expression()))
                                if condition_val:
                                    break 
                            
                            current_val += step_val
                    finally:
                        kiv_self.scope_manager.exit_scope()

                elif loop_specifier_ctx.WHILE(): # нц пока ...
                    condition_expr_ctx = loop_specifier_ctx.expression(0)
                    while True:
                        condition_val_node = kiv_self.visit(condition_expr_ctx)
                        condition_val = condition_val_node.value if isinstance(condition_val_node, KumirValue) else condition_val_node
                        if not isinstance(condition_val, bool):
                           raise KumirTypeError("Условие в цикле ПОКА должно быть логическим.", line_index=condition_expr_ctx.start.line-1, column_index=condition_expr_ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(condition_expr_ctx))
                        if not condition_val:
                            break

                        try:
                            if statement_sequence_ctx:
                                kiv_self.visit(statement_sequence_ctx)
                        except BreakSignal:
                            break 
                        
                        if end_loop_condition_ctx:
                            cond_val_node_kc = kiv_self.visit(end_loop_condition_ctx.expression())
                            cond_val_kc = cond_val_node_kc.value if isinstance(cond_val_node_kc, KumirValue) else cond_val_node_kc
                            if not isinstance(cond_val_kc, bool):
                                raise KumirTypeError("Условие в КЦ ПРИ должно быть логическим.", line_index=end_loop_condition_ctx.expression().start.line-1, column_index=end_loop_condition_ctx.expression().start.column, line_content=kiv_self.get_line_content_from_ctx(end_loop_condition_ctx.expression()))
                            if cond_val_kc:
                                break 
                
                elif loop_specifier_ctx.TIMES(): # нц N раз
                    times_expr_ctx = loop_specifier_ctx.expression(0)
                    times_val_node = kiv_self.visit(times_expr_ctx)
                    times_val = times_val_node.value if isinstance(times_val_node, KumirValue) else times_val_node

                    if not isinstance(times_val, int):
                        raise KumirTypeError("Количество повторений в цикле N РАЗ должно быть целым.", line_index=times_expr_ctx.start.line-1, column_index=times_expr_ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(times_expr_ctx))
                    
                    if times_val < 0: 
                        times_val = 0

                    for _ in range(times_val):
                        try:
                            if statement_sequence_ctx:
                                kiv_self.visit(statement_sequence_ctx)
                        except BreakSignal:
                            break 
                        
                        if end_loop_condition_ctx:
                            condition_val_node = kiv_self.visit(end_loop_condition_ctx.expression())
                            condition_val = condition_val_node.value if isinstance(condition_val_node, KumirValue) else condition_val_node
                            if not isinstance(condition_val, bool):
                                raise KumirTypeError("Условие в КЦ ПРИ должно быть логическим.", line_index=end_loop_condition_ctx.expression().start.line-1, column_index=end_loop_condition_ctx.expression().start.column, line_content=kiv_self.get_line_content_from_ctx(end_loop_condition_ctx.expression()))
                            if condition_val:
                                break 
                else: # pragma: no cover
                    raise KumirNotImplementedError(f"Неизвестный спецификатор цикла: {loop_specifier_ctx.getText()}", line_index=loop_specifier_ctx.start.line-1, column_index=loop_specifier_ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(loop_specifier_ctx))

            else: # Бесконечный цикл (нц ... кц) или цикл с условием выхода (нц ... кц при)
                while True:
                    try:
                        if statement_sequence_ctx:
                            kiv_self.visit(statement_sequence_ctx)
                    except BreakSignal:
                        break 
                    
                    if end_loop_condition_ctx:
                        condition_val_node = kiv_self.visit(end_loop_condition_ctx.expression())
                        condition_val = condition_val_node.value if isinstance(condition_val_node, KumirValue) else condition_val_node
                        if not isinstance(condition_val, bool):
                            raise KumirTypeError("Условие в КЦ ПРИ должно быть логическим.", line_index=end_loop_condition_ctx.expression().start.line-1, column_index=end_loop_condition_ctx.expression().start.column, line_content=kiv_self.get_line_content_from_ctx(end_loop_condition_ctx.expression()))
                        if condition_val:
                            break 
                    elif end_loop_simple_ctx:
                        pass
                    else: # pragma: no cover
                        raise KumirRuntimeError("Цикл должен завершаться либо КЦ, либо КЦ ПРИ.", line_index=ctx.start.line-1, column_index=ctx.start.column, line_content=kiv_self.get_line_content_from_ctx(ctx))
        except StopExecutionSignal: # pragma: no cover
            raise 
        
        return None

    def visitIfStatement(self, ctx: KumirParser.IfStatementContext):
        kiv_self = cast(KumirInterpreterVisitor, self)
        condition_expr_ctx = ctx.expression()
        
        if condition_expr_ctx:
            condition_value_node = kiv_self.visit(condition_expr_ctx)
            
            # Convert to KumirValue if needed
            if isinstance(condition_value_node, KumirValue):
                condition_val = condition_value_node
            else:
                # Handle case where the expression evaluator returns raw Python values
                condition_val = KumirValue(condition_value_node, KumirType.BOOL.value)
            
            # Use the helper method for proper boolean evaluation
            condition_result = self._evaluate_condition(condition_val, "операторе ЕСЛИ", condition_expr_ctx)
        else: # pragma: no cover
            err_line = ctx.start.line
            err_col = ctx.start.column
            lc = kiv_self.get_line_content_from_ctx(ctx)
            raise KumirRuntimeError(f"Строка {err_line}, поз. {err_col}: отсутствует условие в операторе ЕСЛИ.",
                                 line_index=err_line-1, column_index=err_col, line_content=lc)

        if condition_result:
            if ctx.statementSequence(0):
                kiv_self.visit(ctx.statementSequence(0))
        elif ctx.ELSE() and ctx.statementSequence(1):
             kiv_self.visit(ctx.statementSequence(1))
        return None

    def visitSwitchStatement(self, ctx: KumirParser.SwitchStatementContext):
        kiv_self = cast('KumirInterpreterVisitor', self)
        # switchStatement: SWITCH caseBlock+ (ELSE statementSequence)? FI
        # caseBlock: CASE expression COLON statementSequence
        
        executed_case = False
        for case_block_ctx in ctx.caseBlock():
            condition_expr_ctx = case_block_ctx.expression()
            
            # Вычисляем выражение как логическое (например, m = 1, m = 2, etc.)
            condition_val_node = kiv_self.expression_evaluator.visit(condition_expr_ctx)
            
            # Преобразуем результат в boolean согласно семантике КУМИРа
            condition_bool = self._evaluate_condition(condition_val_node, "оператора ВЫБОР (ПРИ)", condition_expr_ctx)
            
            if condition_bool:
                if case_block_ctx.statementSequence():
                    kiv_self.visit(case_block_ctx.statementSequence())
                executed_case = True
                break  # Выходим после выполнения первого истинного условия
        
        # Если ни одно условие не выполнилось, выполняем блок ИНАЧЕ (если есть)
        if not executed_case and ctx.ELSE():
            # The statementSequence for ELSE will be at index len(ctx.caseBlock())
            # in the list of all statementSequences of the switchStatement.
            else_clause_stm_seq_index = len(ctx.caseBlock())
            all_stm_sequences = ctx.statementSequence() # Get the list of all statement sequences

            if len(all_stm_sequences) > else_clause_stm_seq_index:
                else_body_sequence = all_stm_sequences[else_clause_stm_seq_index]
                if else_body_sequence: 
                     kiv_self.visit(else_body_sequence)        
        return None
        
    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext) -> None:
        # Отключена эта реализация в пользу более детальной в statement_handlers.py
        # которая правильно определяет контекст (цикл vs процедура)
        pass

    def visitStopStatement(self, ctx: KumirParser.StopStatementContext) -> None:
        # stopStatement: STOP
        _kiv_self = cast('KumirInterpreterVisitor', self)  # Может понадобиться позже
        # Выполнение программы остановлено оператором СТОП
        raise StopExecutionSignal()

    def visitAssertionStatement(self, ctx: KumirParser.AssertionStatementContext):
        kiv_self = cast(KumirInterpreterVisitor, self)
        # assertionStatement: ASSERTION expression
        expr_ctx = ctx.expression()
        value_node = kiv_self.visit(expr_ctx)
        value = value_node.value if isinstance(value_node, KumirValue) else value_node

        if not isinstance(value, bool):
            err_line = expr_ctx.start.line
            err_col = expr_ctx.start.column
            lc = kiv_self.get_line_content_from_ctx(expr_ctx)
            raise KumirTypeError(f"Строка {err_line}, поз. {err_col}: выражение в УТВ должно быть логического типа, а не {type(value).__name__}.",
                                 line_index=err_line-1, column_index=err_col, line_content=lc)
        
        if not value:
            err_line = ctx.start.line
            err_col = ctx.start.column
            lc = kiv_self.get_line_content_from_ctx(ctx)
            # В КуМире сообщение об ошибке УТВ обычно стандартное
            # Стандартный КуМир обычно прерывает выполнение здесь.
            raise KumirRuntimeError(f"Утверждение (утв) ложно.", line_index=err_line-1, column_index=err_col, line_content=lc)
        return None

    def visitPauseStatement(self, ctx: KumirParser.PauseStatementContext):
        _kiv_self = cast(KumirInterpreterVisitor, self)  # Может понадобиться позже
        # pauseStatement: PAUSE
        # В интерактивной среде это была бы пауза. В пакетном режиме можно проигнорировать или вывести сообщение.
        # Оператор ПАУЗА выполнен - логируется через основную систему логирования
        # Можно добавить реальную паузу, если нужно для тестов, но обычно это не требуется для функциональных тестов.
        # import time
        # time.sleep(1) # Пауза на 1 секунду
        return None