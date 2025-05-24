from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import Token
from antlr4.tree.Tree import TerminalNodeImpl
from antlr4 import ParserRuleContext # <--- ДОБАВЛЕН ИМПОРТ

# Исправляем путь к generated
from pyrobot.backend.kumir_interpreter.generated.KumirParser import KumirParser
# Исправлен путь к исключениям, теперь они в отдельном файле
from .exceptions import BreakSignal, ExitSignal, ReturnSignal # Используем относительный импорт
from antlr4 import ParserRuleContext # Добавлено для _is_inside_loop

# Исправляем импорт KumirVisitor на KumirParserVisitor
from .generated.KumirParserVisitor import KumirParserVisitor 

from .kumir_exceptions import (
    BreakSignal, 
    ContinueSignal, 
    ReturnSignal, 
    ExitSignal, 
    KumirRuntimeError, 
    KumirTypeError
)
from .utils import KumirValue, KumirTypeConverter, ErrorHandler

import time

# Меняем базовый класс на KumirParserVisitor
class StatementHandler(KumirParserVisitor):
    def __init__(self, variable_manager, expression_evaluator, type_converter: KumirTypeConverter, error_handler: ErrorHandler, output_handler, interpreter_visitor):
        self.variable_manager = variable_manager
        self.expression_evaluator = expression_evaluator
        self.type_converter = type_converter
        self.error_handler = error_handler
        self.output_handler = output_handler
        self.interpreter = interpreter_visitor # Это KumirInterpreterVisitor

    def _get_simple_variable_name_from_expression(self, expr_ctx: KumirParser.ExpressionContext) -> str | None:
        if not expr_ctx: return None

        # Path: Expression -> LogicalOr -> LogicalAnd -> Equality -> Relational -> Additive -> Multiplicative -> Power -> Unary -> Postfix -> Primary -> QualifiedIdentifier
        
        node = expr_ctx.logicalOrExpression()
        if not node or node.OR(0) or node.logicalAndExpression(1): return None
        node = node.logicalAndExpression(0)
        if not node: return None # Should be caught by previous logicalAndExpression(1) check if structure is sound

        if node.AND(0) or node.equalityExpression(1): return None
        node = node.equalityExpression(0)
        if not node: return None

        if node.EQ(0) or node.NE(0) or node.relationalExpression(1): return None
        node = node.relationalExpression(0)
        if not node: return None

        if node.LT(0) or node.GT(0) or node.LE(0) or node.GE(0) or node.additiveExpression(1): return None
        node = node.additiveExpression(0)
        if not node: return None

        if node.PLUS(0) or node.MINUS(0) or node.multiplicativeExpression(1): return None
        node = node.multiplicativeExpression(0)
        if not node: return None

        if node.MUL(0) or node.DIV(0) or node.powerExpression(1): return None
        node = node.powerExpression(0)
        if not node: return None

        if node.POWER(): return None 
        unary_node = node.unaryExpression() # unaryExpression is a single node, not a list from powerExpression
        if not unary_node: return None

        if unary_node.NOT() or unary_node.PLUS() or unary_node.MINUS(): return None
        postfix_node = unary_node.postfixExpression()
        if not postfix_node: return None
        
        if postfix_node.LBRACK(0) or postfix_node.LPAREN(0): return None # Array access or function call
        primary_node = postfix_node.primaryExpression()
        if not primary_node: return None
        
        q_ident_node = primary_node.qualifiedIdentifier()
        if not q_ident_node or not q_ident_node.ID(): return None
        
        # Ensure primary_node is *only* qualifiedIdentifier
        if primary_node.literal() or primary_node.RETURN_VALUE() or primary_node.LPAREN() or primary_node.arrayLiteral():
            return None
            
        return q_ident_node.ID().getText()

    def visitStatement(self, ctx: KumirParser.StatementContext):
        # print(f"[DEBUG][SH] Visiting statement: {ctx.getText()}")
        # StatementContext сам по себе не выполняется, он содержит конкретный оператор.
        # KumirParserVisitor.visit будет вызван для конкретного типа оператора внутри StatementContext.
        # Например, если StatementContext содержит IfStatementContext, то будет вызван visitIfStatement.
        # Поэтому visitChildren(ctx) здесь корректен для диспетчеризации.
        return self.interpreter.visitChildren(ctx) # Используем visitChildren интерпретатора

    # Контексты, которые были проверены и исправлены или требуют внимания:
    # VariableDeclarationStatementContext -> visitVariableDeclaration (OK, существует в KumirParser.py)
    # AssignmentStatementContext -> visitAssignmentStatement (OK, скорректирован доступ к lvalue)
    # IoStatementContext -> visitIoStatement (OK, скорректирован доступ и имена токенов)
    # IfStatementContext -> visitIfStatement (OK, block заменен на statementSequence, KW_ELSE на ELSE)
    # LoopStatementContext -> visitLoopStatement (Переписан для корректной работы с loopSpecifier и endLoopCondition)
    # ProcedureCallStatementContext -> visitProcedureCallStatement (OK, скорректирован доступ)
    # ExitStatementContext -> visitExitStatement (Скорректирован)
    # StatementSequenceContext -> visitStatementSequence (Заменяет visitBlock)
    # SwitchStatementContext -> visitSwitchStatement (Переписан)
    # PauseStatementContext -> visitPauseStatement (Скорректирован, ПАУЗА без параметров)

    def visitVariableDeclaration(self, ctx: KumirParser.VariableDeclarationContext):
        # print(f"[DEBUG][SH] visitVariableDeclaration: {ctx.getText()}")
        self.interpreter.visitVariableDeclaration(ctx) 
        return None

    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        # print(f"[DEBUG][SH] visitAssignmentStatement: {ctx.getText()}")
        lval_ctx = ctx.lvalue()
        if lval_ctx and lval_ctx.qualifiedIdentifier():
            var_name = lval_ctx.qualifiedIdentifier().ID().getText()
            expression_ctx = ctx.expression()
            value = self.expression_evaluator.visit(expression_ctx) # Используем общий visit для expression_evaluator
            # print(f"[DEBUG][SH] Assigning {value} to {var_name}")
            self.interpreter.scope_manager.assign_variable(var_name, value)
        elif lval_ctx and lval_ctx.RETURN_VALUE():
            # Присваивание знач_возвр
            expression_ctx = ctx.expression()
            value = self.expression_evaluator.visit(expression_ctx)
            self.interpreter.scope_manager.set_return_value(value)
        else:
            # print(f"[ERROR][SH] Unsupported lvalue in assignment: {ctx.getText()}")
            self.error_handler.runtime_error(f"Неподдерживаемый тип левой части присваивания: {ctx.lvalue().getText()}", ctx)
        return None

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext):
        # print(f"[DEBUG][SH] visitIoStatement: {ctx.getText()}")
        if ctx.INPUT():
            # print(f"[DEBUG][SH] Input statement")
            if ctx.ioArgumentList():
                for arg_ctx in ctx.ioArgumentList().ioArgument(): 
                    expr_ctx = arg_ctx.expression(0) 
                    if expr_ctx:
                        var_name = self._get_simple_variable_name_from_expression(expr_ctx)
                        if var_name:
                            # print(f"[DEBUG][SH] Input for {var_name}")
                            self.interpreter.io_handler.handle_input(var_name)
                        else:
                            # print(f"[ERROR][SH] Input argument must be a simple variable, got: {expr_ctx.getText()}")
                            self.error_handler.runtime_error(f"Для ввода ожидалась простая переменная, а не выражение \'{expr_ctx.getText()}\'", expr_ctx)
                    elif arg_ctx.NEWLINE_CONST():
                        # print("[WARN][SH] NEWLINE_CONST used with INPUT, not meaningful.")
                        self.error_handler.runtime_error("Оператор ВВОД не может принять НС (новая строка) в качестве аргумента.", arg_ctx)
                    else: 
                        # print(f"[ERROR][SH] Invalid argument for INPUT: {arg_ctx.getText()}")
                        self.error_handler.runtime_error(f"Неверный аргумент для оператора ввода: {arg_ctx.getText()}", arg_ctx)
            else: 
                self.error_handler.runtime_error("Оператор ВВОД требует указания переменной.", ctx)

        elif ctx.OUTPUT():
            # print(f"[DEBUG][SH] Output statement")
            output_items = []
            if ctx.ioArgumentList():
                for arg_ctx in ctx.ioArgumentList().ioArgument():
                    if arg_ctx.expression(0): 
                        # TODO: Handle formatting expressions if arg_ctx.expression(1) etc. exist
                        value = self.expression_evaluator.visit(arg_ctx.expression(0))
                        output_items.append(value) # Передаем KumirValue
                    elif arg_ctx.NEWLINE_CONST():
                        output_items.append(KumirValue("\\n", "ЛИТ")) # Специальное значение для НС
            # print(f"[DEBUG][SH] Outputting: {output_items}")
            self.interpreter.io_handler.handle_output(output_items)
        return None

    def visitIfStatement(self, ctx: KumirParser.IfStatementContext):
        # print(f"[DEBUG][SH] visitIfStatement: {ctx.getText()}")
        condition_ctx = ctx.expression()
        condition_val = self.expression_evaluator.visit(condition_ctx)

        if self.type_converter.to_python_bool(condition_val): # Исправлено to_boolean на to_python_bool
            # print(f"[DEBUG][SH] If condition is True")
            self.interpreter.visit(ctx.statementSequence(0)) 
        elif ctx.ELSE() and ctx.statementSequence(1): 
            # print(f"[DEBUG][SH] If condition is False, executing Else block")
            self.interpreter.visit(ctx.statementSequence(1))
        return None

    def visitSwitchStatement(self, ctx: KumirParser.SwitchStatementContext):
        # print(f"[DEBUG][SH] visitSwitchStatement: {ctx.getText()}")
        # KumirParser.py: switchStatement : SWITCH caseBlock+ (ELSE statementSequence)? FI ;
        # caseBlock : CASE expression COLON statementSequence ;
        # Выражение для switch отсутствует в SwitchStatementContext, оно есть в каждом caseBlock.
        
        matched_case = False
        if ctx.caseBlock(): # caseBlock() возвращает список
            for case_ctx in ctx.caseBlock(): # case_ctx это CaseBlockContext
                condition_expr_ctx = case_ctx.expression()
                condition_value = self.expression_evaluator.visit(condition_expr_ctx)
                
                if self.type_converter.to_python_bool(condition_value): # Исправлено to_boolean на to_python_bool
                    matched_case = True
                    self.interpreter.visit(case_ctx.statementSequence())
                    break # Выходим из switch после первого совпадения

        if not matched_case and ctx.ELSE():
            # statementSequence() у SwitchStatementContext относится к блоку ELSE
            else_stmt_sequence = ctx.statementSequence() 
            if else_stmt_sequence:
                 self.interpreter.visit(else_stmt_sequence)
        return None

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        # print(f"[DEBUG][SH] visitLoopStatement: {ctx.getText()}")
        loop_body_stmts_ctx = ctx.statementSequence()
        loop_specifier_ctx = ctx.loopSpecifier()
        end_condition_ctx = ctx.endLoopCondition()

        if loop_specifier_ctx:
            # Цикл с явным спецификатором (ПОКА, ДЛЯ, N РАЗ)
            if loop_specifier_ctx.WHILE(): # ПОКА <усл> НЦ ... КЦ
                condition_expr = loop_specifier_ctx.expression(0)
                while True:
                    condition_value = self.expression_evaluator.visit(condition_expr)
                    if not self.type_converter.to_python_bool(condition_value): # Исправлено to_boolean на to_python_bool
                        break
                    try:
                        if loop_body_stmts_ctx: self.interpreter.visit(loop_body_stmts_ctx)
                    except BreakSignal:
                        return None # Выход из visitLoopStatement
                    except ContinueSignal:
                        continue
                return None

            elif loop_specifier_ctx.FOR(): # ДЛЯ <id> ОТ <выр1> ДО <выр2> (ШАГ <выр3>)? НЦ ... КЦ
                var_name_token = loop_specifier_ctx.ID()
                var_name = var_name_token.getText()

                from_expr_ctx = loop_specifier_ctx.expression(0)
                from_value = self.expression_evaluator.visit(from_expr_ctx)
                
                to_expr_ctx = loop_specifier_ctx.expression(1)
                to_value = self.expression_evaluator.visit(to_expr_ctx)

                step_kumir_value = KumirValue(1, "ЦЕЛ") # Значение по умолчанию для шага
                if loop_specifier_ctx.STEP(): 
                    if len(loop_specifier_ctx.expression()) > 2:
                        step_expr_ctx = loop_specifier_ctx.expression(2)
                        step_kumir_value = self.expression_evaluator.visit(step_expr_ctx)
                    else:
                        self.error_handler.runtime_error("Отсутствует выражение для шага после ШАГ", loop_specifier_ctx.STEP().symbol)
                        return None
                
                current_py_val = self.type_converter.to_python_number(from_value) 
                target_py_val = self.type_converter.to_python_number(to_value)
                step_py_val = self.type_converter.to_python_number(step_kumir_value)

                if step_py_val == 0:
                    self.error_handler.runtime_error("Шаг цикла ДЛЯ не может быть равен нулю", loop_specifier_ctx.STEP().symbol if loop_specifier_ctx.STEP() else var_name_token)
                    return None

                # Вход в область видимости цикла ДЛЯ
                self.interpreter.scope_manager.enter_scope(f"for_loop_{var_name}")
                # Объявляем переменную цикла. Тип берем из начального значения.
                self.interpreter.scope_manager.declare_variable(var_name, from_value.type_str, from_value, is_param=False, ctx=var_name_token)

                loop_condition = (lambda curr, target, step: curr <= target if step > 0 else curr >= target)

                while loop_condition(current_py_val, target_py_val, step_py_val):
                    current_kumir_val_for_scope = KumirValue(current_py_val, from_value.type_str) 
                    self.interpreter.scope_manager.assign_variable(var_name, current_kumir_val_for_scope, var_name_token)
                    try:
                        if loop_body_stmts_ctx: self.interpreter.visit(loop_body_stmts_ctx)
                    except BreakSignal:
                        break 
                    except ContinueSignal:
                        current_py_val += step_py_val
                        continue 
                    current_py_val += step_py_val
                
                self.interpreter.scope_manager.exit_scope() # Выход из области видимости цикла ДЛЯ
                return None

            elif loop_specifier_ctx.TIMES(): # <выражение> РАЗ НЦ ... КЦ
                count_expr_ctx = loop_specifier_ctx.expression(0)
                count_value = self.expression_evaluator.visit(count_expr_ctx)
                
                try:
                    num_times = int(self.type_converter.to_python_number(count_value))
                except (ValueError, TypeError) as e:
                    self.error_handler.runtime_error(f"Количество повторений цикла РАЗ должно быть целым числом, получено: {count_value.value}", count_expr_ctx)
                    return None
                
                if num_times < 0:
                    self.error_handler.runtime_error(f"Количество повторений цикла РАЗ не может быть отрицательным: {num_times}", count_expr_ctx)
                    return None

                for _ in range(num_times):
                    try:
                        if loop_body_stmts_ctx: self.interpreter.visit(loop_body_stmts_ctx)
                    except BreakSignal:
                        return None 
                    except ContinueSignal:
                        continue
                return None
            else:
                # Неизвестный тип loopSpecifier, ошибка грамматики?
                self.error_handler.runtime_error("Неизвестный тип спецификатора цикла.", loop_specifier_ctx)
                return None
        
        elif end_condition_ctx: # НЦ ... КЦ ПОКА <усл> (do-while)
            condition_expr = end_condition_ctx.expression()
            while True:
                try:
                    if loop_body_stmts_ctx: self.interpreter.visit(loop_body_stmts_ctx)
                except BreakSignal:
                    return None 
                except ContinueSignal:
                    # В цикле КЦ ПОКА, continue пропустит проверку условия и начнет следующую итерацию тела
                    # Это стандартное поведение do-while, если continue внутри.
                    # Если нужно сначала проверить условие, то continue должен быть обработан иначе,
                    # но обычно continue в do-while переходит к следующей итерации тела.
                    pass # Просто продолжаем, условие проверится после тела

                condition_value = self.expression_evaluator.visit(condition_expr)
                if not self.type_converter.to_python_bool(condition_value): # Исправлено to_boolean на to_python_bool
                    break
            return None
            
        else: # Простой НЦ ... КЦ (бесконечный цикл)
            while True:
                try:
                    if loop_body_stmts_ctx: self.interpreter.visit(loop_body_stmts_ctx)
                except BreakSignal:
                    return None
                except ContinueSignal:
                    continue
            return None # Технически недостижимо для бесконечного цикла без BreakSignal

    def _is_inside_loop(self, antlr_ctx: ParserRuleContext) -> bool:
        current_ctx = antlr_ctx.parentCtx
        while current_ctx is not None:
            if isinstance(current_ctx, KumirParser.LoopStatementContext):
                return True
            # Предотвращаем выход за пределы текущего алгоритма/функции
            if isinstance(current_ctx, KumirParser.AlgorithmDefinitionContext):
                return False
            current_ctx = current_ctx.parentCtx
        return False

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext):
        """
        Обрабатывает операторы ВЫХОД и ВОЗВРАТ.
        ВЫХОД:
            - Если внутри цикла: вызывает BreakSignal для выхода из цикла.
            - Если вне цикла: вызывает ExitSignal для завершения программы/алгоритма.
        ВОЗВРАТ:
            - Вызывает ReturnSignal(None), т.к. по грамматике KumirParser.g4
              ExitStatement не содержит выражения. Возврат значения из функции
              осуществляется через 'знач := выражение'.
        """
        exit_token_text = ctx.EXIT().symbol.text.lower()

        if exit_token_text == "выход":
            if self._is_inside_loop(ctx):
                # print("DEBUG: Raising BreakSignal (выход from loop)")
                raise BreakSignal()
            else:
                # print("DEBUG: Raising ExitSignal (выход from algorithm)")
                raise ExitSignal()
        elif exit_token_text == "возврат":
            # print("DEBUG: Raising ReturnSignal(None) (возврат from procedure/function)")
            raise ReturnSignal(None)
        else:
            # Эта ветка не должна достигаться, если лексер правильно относит
            # 'выход' и 'возврат' к токену EXIT.
            # Но на всякий случай оставим обработку непредвиденного токена.
            # В реальной ситуации здесь лучше выбросить более специфическую ошибку парсинга/интерпретации.
            raise RuntimeError(f"Неизвестный токен для ExitStatement: {exit_token_text}")

    def visitPauseStatement(self, ctx: KumirParser.PauseStatementContext):
        # print(f"[DEBUG][SH] visitPauseStatement: {ctx.getText()}")
        # KumirParser.py: pauseStatement : PAUSE ; (без выражения)
        # Если ПАУЗА должна принимать аргумент, грамматика должна быть другой.
        # Пока что реализуем как паузу на фиксированное небольшое время или ожидание действия.
        # print("[DEBUG][SH] Executing PAUSE (fixed small delay or interactive wait).")
        # self.interpreter.io_handler.handle_pause() # Предположим, io_handler может это обработать
        time.sleep(0.1) # Простая реализация небольшой задержки
        return None

    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext):
        # print(f"[DEBUG][SH] visitProcedureCallStatement: {ctx.getText()}")
        # Это вызов процедуры/алгоритма как оператора
        # Результат вызова (если это функция, вызванная как процедура) игнорируется.
        self.interpreter.visitProcedureCallStatement(ctx) # Передаем управление KumirInterpreterVisitor
        return None

    def visitStatementSequence(self, ctx: KumirParser.StatementSequenceContext):
        # print(f"[DEBUG][SH] visitStatementSequence: {ctx.getText()}")
        # Этот метод обрабатывает последовательность операторов.
        # KumirInterpreterVisitor.visitChildren обеспечит обход каждого statement внутри.
        return self.interpreter.visitChildren(ctx) # Используем visitChildren интерпретатора

    # TODO: Добавить visitStopStatement, visitAssertionStatement, если они нужны и определены в грамматике.
    # KumirParser.py содержит:
    # RULE_stopStatement = 50 -> class StopStatementContext(ParserRuleContext) -> def STOP(self)
    # RULE_assertionStatement = 51 -> class AssertionStatementContext(ParserRuleContext) -> def ASSERTION(self), def expression(self)

    def visitStopStatement(self, ctx: KumirParser.StopStatementContext):
        # print(f"[DEBUG][SH] visitStopStatement: {ctx.getText()}")
        # Команда СТОП обычно завершает всю программу немедленно.
        self.error_handler.runtime_error("Команда СТОП инициировала завершение программы.", ctx) # Удален is_fatal
        raise ExitSignal(is_program_exit=True) # Специальный ExitSignal для полной остановки
        # return None # Недостижимо

    def visitAssertionStatement(self, ctx: KumirParser.AssertionStatementContext):
        # print(f"[DEBUG][SH] visitAssertionStatement: {ctx.getText()}")
        condition_ctx = ctx.expression()
        condition_val = self.expression_evaluator.visit(condition_ctx)

        if not self.type_converter.to_python_bool(condition_val): # Исправлено to_boolean на to_python_bool
            assertion_text = condition_ctx.getText()
            self.error_handler.runtime_error(f"Утверждение не выполнено: {assertion_text}", ctx)
            # В Кумире утверждение обычно останавливает программу, если оно ложно.
            raise KumirRuntimeError(f"Утверждение не выполнено: {assertion_text}", ctx.start.line, ctx.start.column)
        return None