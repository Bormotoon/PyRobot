from typing import TYPE_CHECKING, cast, Optional, Any

from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import BreakSignal, KumirTypeError, KumirRuntimeError, KumirNameError, KumirNotImplementedError, StopExecutionSignal
from ..kumir_datatypes import KumirValue, KumirType # Для проверки типов результатов выражений, KumirType для объявления переменной цикла

if TYPE_CHECKING:
    from .main_visitor import KumirInterpreterVisitor


class ControlFlowVisitorMixin:

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        kiv_self = cast(KumirInterpreterVisitor, self)

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
                        kiv_self.scope_manager.declare_variable(
                            loop_var_name, 
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
        condition_value = None
        
        if condition_expr_ctx:
            condition_value_node = kiv_self.visit(condition_expr_ctx)
            condition_value = condition_value_node.value if isinstance(condition_value_node, KumirValue) else condition_value_node
            if not isinstance(condition_value, bool):
                err_line = condition_expr_ctx.start.line
                err_col = condition_expr_ctx.start.column
                lc = kiv_self.get_line_content_from_ctx(condition_expr_ctx)
                raise KumirTypeError(f"Строка {err_line}, поз. {err_col}: условие в операторе ЕСЛИ должно быть логического типа, а не {type(condition_value).__name__}.",
                                     line_index=err_line-1, column_index=err_col, line_content=lc)
        else: # pragma: no cover
            err_line = ctx.start.line
            err_col = ctx.start.column
            lc = kiv_self.get_line_content_from_ctx(ctx)
            raise KumirRuntimeError(f"Строка {err_line}, поз. {err_col}: отсутствует условие в операторе ЕСЛИ.",
                                 line_index=err_line-1, column_index=err_col, line_content=lc)

        if condition_value:
            if ctx.statementSequence(0):
                kiv_self.visit(ctx.statementSequence(0))
        elif ctx.ELSE() and ctx.statementSequence(1):
             kiv_self.visit(ctx.statementSequence(1))
        return None

    def visitSwitchStatement(self, ctx: KumirParser.SwitchStatementContext):
        kiv_self = cast(KumirInterpreterVisitor, self)
        # switchStatement: SWITCH caseBlock+ (ELSE statementSequence)? FI
        # caseBlock: CASE expression COLON statementSequence
        
        executed_case = False
        for case_block_ctx in ctx.caseBlock():
            condition_expr_ctx = case_block_ctx.expression()
            condition_val_node = kiv_self.visit(condition_expr_ctx)
            condition_val = condition_val_node.value if isinstance(condition_val_node, KumirValue) else condition_val_node

            if not isinstance(condition_val, bool):
                err_line = condition_expr_ctx.start.line
                err_col = condition_expr_ctx.start.column
                lc = kiv_self.get_line_content_from_ctx(condition_expr_ctx)
                raise KumirTypeError(f"Строка {err_line}, поз. {err_col}: условие в ПРИ оператора ВЫБОР должно быть логического типа, а не {type(condition_val).__name__}.",
                                     line_index=err_line-1, column_index=err_col, line_content=lc)
            
            if condition_val:
                if case_block_ctx.statementSequence():
                    kiv_self.visit(case_block_ctx.statementSequence())
                executed_case = True
                break 
        
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

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext):
        # exitStatement: EXIT
        # В КуМире ВЫХОД используется для выхода из цикла или процедуры/функции.
        # Мы генерируем BreakSignal для циклов.
        # Для процедур/функций ExitSignal генерируется в visitReturnStatement или при завершении.
        # Здесь мы должны решить, это выход из цикла или из процедуры.
        # Пока что будем считать, что EXIT в общем потоке - это выход из текущего цикла.
        # Если мы не внутри цикла, это может быть ошибкой или выходом из процедуры.
        # Для простоты, пусть EXIT всегда генерирует BreakSignal.
        # Более сложная логика потребовала бы отслеживания, находимся ли мы в цикле.
        raise BreakSignal()

    def visitStopStatement(self, ctx: KumirParser.StopStatementContext):
        # stopStatement: STOP
        kiv_self = cast(KumirInterpreterVisitor, self)
        kiv_self.error_stream_out("Выполнение программы остановлено оператором СТОП.\\n") # Используем error_stream_out
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
            kiv_self.error_stream_out(f"Ошибка времени выполнения: Утверждение (утв) ложно в строке {err_line}, поз. {err_col}.\\n") # Используем error_stream_out
            # Стандартный КуМир обычно прерывает выполнение здесь.
            raise KumirRuntimeError(f"Утверждение (утв) ложно.", line_index=err_line-1, column_index=err_col, line_content=lc)
        return None

    def visitPauseStatement(self, ctx: KumirParser.PauseStatementContext):
        kiv_self = cast(KumirInterpreterVisitor, self)
        # pauseStatement: PAUSE
        # В интерактивной среде это была бы пауза. В пакетном режиме можно проигнорировать или вывести сообщение.
        # print("[INFO] Оператор ПАУЗА выполнен.") # Или использовать error_stream_out, если это считается "выводом"
        kiv_self.error_stream_out("Оператор ПАУЗА выполнен.\n") # Сообщение в поток ошибок/информации
        # Можно добавить реальную паузу, если нужно для тестов, но обычно это не требуется для функциональных тестов.
        # import time
        # time.sleep(1) # Пауза на 1 секунду
        return None