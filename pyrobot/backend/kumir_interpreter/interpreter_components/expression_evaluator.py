\
# filepath: c:\\Users\\Bormotoon\\VSCodeProjects\\PyRobot\\pyrobot\\backend\\kumir_interpreter\\interpreter_components\\expression_evaluator.py
"""
Placeholder for ExpressionEvaluator.
This class is responsible for evaluating expressions in Kumir code.
It needs to be fully implemented based on the original interpreter.py logic.
"""
from typing import Any, List
from antlr4.tree.Tree import TerminalNode

from ..generated.KumirParser import KumirParser
from ..generated.KumirLexer import KumirLexer
from ..kumir_exceptions import KumirEvalError, KumirNotImplementedError, KumirTypeError

class ExpressionEvaluator:
    def __init__(self, visitor): # visitor is an instance of KumirInterpreterVisitor
        self.visitor = visitor

    def visitLiteral(self, ctx: KumirParser.LiteralContext) -> Any:
        if ctx.INTEGER():
            return int(ctx.INTEGER().getText())
        elif ctx.REAL():
            # Кумир использует запятую как десятичный разделитель
            return float(ctx.REAL().getText().replace(',', '.'))
        elif ctx.STRING():
            text = ctx.STRING().getText()
            # Удаляем кавычки по краям и заменяем двойные кавычки на одинарные внутри строки
            return text[1:-1].replace('""', '"') 
        elif ctx.CHAR():
            text = ctx.CHAR().getText()
            # Удаляем одинарные кавычки по краям
            return text[1:-1].replace("''", "'")
        elif ctx.LOGICAL():
            text = ctx.LOGICAL().getText().lower()
            if text == "да": return True
            if text == "нет": return False
        
        self.visitor.logger.error(f"Unsupported literal type: {ctx.getText()}") # pragma: no cover
        raise KumirEvalError(f"Неподдерживаемый тип литерала: {ctx.getText()}", getattr(ctx, 'start', None)) # pragma: no cover

    def visitQualifiedIdentifier(self, ctx: KumirParser.QualifiedIdentifierContext) -> Any:
        # Grammar: qualifiedIdentifier: ID (DOT ID)*;
        ids = ctx.ID()
        var_name_parts = [id_node.getText() for id_node in ids]

        if len(var_name_parts) == 1:
            var_name = var_name_parts[0]
            return self.visitor.scope_manager.lookup_variable(var_name, getattr(ids[0].symbol, 'line', None))
        else:
            full_name = ".".join(var_name_parts)
            self.visitor.logger.warning(f"Attempt to access qualified identifier '{full_name}', not fully implemented.")
            raise KumirNotImplementedError(
                f"Доступ к составным именам (типа '{full_name}') через точку пока не реализован.",
                getattr(ids[0].symbol, 'line', None)
            )

    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext) -> Any:
        # Grammar: primaryExpression: literal | qualifiedIdentifier | LPAREN expression RPAREN ;
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.qualifiedIdentifier():
            return self.visit(ctx.qualifiedIdentifier())
        elif ctx.LPAREN(): 
            return self.visit(ctx.expression())
        
        self.visitor.logger.error(f"Unknown primary expression type: {ctx.getText()}") # pragma: no cover
        raise KumirEvalError(f"Неизвестный тип первичного выражения: {ctx.getText()}", getattr(ctx, 'start', None)) # pragma: no cover

    def visitExpressionList(self, ctx: KumirParser.ExpressionListContext) -> List[Any]:
        # Grammar: expressionList : expression (COMMA expression)* ;
        if ctx is None: # Can be absent in some rules if optional
            return []
        return [self.visit(expr) for expr in ctx.expression()]

    def visitArgumentList(self, ctx: KumirParser.ArgumentListContext) -> List[Any]:
        # Grammar: argumentList : expression (COMMA expression)* ; (or similar)
        if ctx is None: # argumentList? means it can be absent
            return []
        return [self.visit(expr) for expr in ctx.expression()]

    def visitPostfixExpression(self, ctx: KumirParser.PostfixExpressionContext) -> Any:
        # Grammar: postfixExpression: primaryExpression ( LBRACK expressionList RBRACK | LPAREN argumentList? RPAREN | DOT ID )* ;
        
        current_value_or_name = self.visit(ctx.primaryExpression())
        
        child_idx = 1 
        while child_idx < len(ctx.children):
            operator_terminal_node = ctx.children[child_idx]

            if not isinstance(operator_terminal_node, TerminalNode): # pragma: no cover
                self.visitor.logger.error(f"Expected operator token in PostfixExpression, got {type(operator_terminal_node)}")
                raise KumirEvalError("Internal error: Expected operator in postfix expression.", getattr(ctx, 'start', None))

            op_token = operator_terminal_node.symbol # Use .symbol
            op_type = op_token.type

            if op_type == KumirLexer.LBRACK: 
                if not (child_idx + 2 < len(ctx.children) and \
                        isinstance(ctx.children[child_idx + 1], KumirParser.ExpressionListContext) and \
                        isinstance(ctx.children[child_idx + 2], TerminalNode) and \
                        ctx.children[child_idx + 2].symbol.type == KumirLexer.RBRACK): # Use .symbol
                    raise KumirEvalError("Некорректный синтаксис доступа к элементу массива.", getattr(op_token, 'line', None))

                expression_list_ctx = ctx.children[child_idx + 1]
                indices = self.visit(expression_list_ctx)
                
                table_obj = current_value_or_name
                try:
                    # Предполагается, что runtime_helpers.get_table_element обрабатывает 1-based индексацию Кумира
                    current_value_or_name = self.visitor.runtime_helpers.get_table_element(table_obj, indices, getattr(op_token, 'line', None))
                except KumirNotImplementedError: # Pass through if helper not ready
                    raise
                except Exception as e: # Catch specific errors from helper if possible
                     raise KumirEvalError(f"Ошибка доступа к элементу таблицы: {e}", getattr(op_token, 'line', None))

                child_idx += 3
            elif op_type == KumirLexer.LPAREN: 
                func_name_str = None
                primary_expr_node = ctx.primaryExpression()
                # Попытка получить имя функции, если primaryExpression - это простой идентификатор
                if primary_expr_node.qualifiedIdentifier() and \
                   len(primary_expr_node.qualifiedIdentifier().ID()) == 1 and \
                   not primary_expr_node.qualifiedIdentifier().DOT(): # Check for DOT list being empty or all None
                    func_name_str = primary_expr_node.qualifiedIdentifier().ID(0).getText()
                elif isinstance(current_value_or_name, str): # Если primaryExpression уже вернуло имя функции
                    func_name_str = current_value_or_name
                
                if func_name_str is None:
                     raise KumirTypeError(f"Вызываемый объект не является функцией (тип: {type(current_value_or_name).__name__}).", getattr(op_token, 'line', None))

                args = []
                if child_idx + 1 < len(ctx.children) and isinstance(ctx.children[child_idx + 1], KumirParser.ArgumentListContext):
                    if not (child_idx + 2 < len(ctx.children) and \
                            isinstance(ctx.children[child_idx + 2], TerminalNode) and \
                            ctx.children[child_idx + 2].symbol.type == KumirLexer.RPAREN): # Use .symbol
                        raise KumirEvalError("Некорректный вызов функции: отсутствует ')' после аргументов.", getattr(op_token, 'line', None))
                    
                    arg_list_ctx = ctx.children[child_idx + 1]
                    args = self.visit(arg_list_ctx)
                    child_idx += 3 
                elif child_idx + 1 < len(ctx.children) and \
                     isinstance(ctx.children[child_idx + 1], TerminalNode) and \
                     ctx.children[child_idx + 1].symbol.type == KumirLexer.RPAREN: # Use .symbol
                    child_idx += 2 
                else:
                    raise KumirEvalError("Некорректный вызов функции: отсутствует ')' или неверные аргументы.", getattr(op_token, 'line', None))

                current_value_or_name = self.visitor.procedure_manager.call_function(
                    func_name_str, 
                    args, 
                    getattr(op_token, 'line', None)
                )
            elif op_type == KumirLexer.DOT: 
                if not (child_idx + 1 < len(ctx.children) and \
                        isinstance(ctx.children[child_idx + 1], TerminalNode) and \
                        ctx.children[child_idx + 1].symbol.type == KumirLexer.ID): # Use .symbol
                    raise KumirEvalError("Некорректный доступ к члену: отсутствует ID после точки.", getattr(op_token, 'line', None))

                member_id_node = ctx.children[child_idx + 1]
                member_name = member_id_node.getText()
                
                # record_obj = current_value_or_name
                # current_value_or_name = self.visitor.runtime_helpers.get_record_field(record_obj, member_name, getattr(op_token, 'line', None))
                raise KumirNotImplementedError(f"Доступ к полям записей (типа '{member_name}') через точку пока не реализован.", getattr(op_token, 'line', None))
                # child_idx += 2 # Если будет реализовано
            else: # pragma: no cover
                self.visitor.logger.error(f"Unexpected operator in PostfixExpression loop: {operator_terminal_node.getText()}")
                raise KumirEvalError("Internal error: Unexpected operator in postfix processing.", getattr(op_token, 'line', None))
        
        return current_value_or_name

    def visitUnaryExpression(self, ctx: KumirParser.UnaryExpressionContext) -> Any:
        op_terminal_node = None 
        op_type = None

        if ctx.PLUS():
            op_terminal_node = ctx.PLUS()
            op_type = KumirLexer.PLUS
        elif ctx.MINUS():
            op_terminal_node = ctx.MINUS()
            op_type = KumirLexer.MINUS
        elif ctx.NOT(): 
            op_terminal_node = ctx.NOT()
            op_type = KumirLexer.NOT

        if op_terminal_node:
            # unaryExpression : (PLUS | MINUS | NOT) unaryExpression
            # Access unaryExpression as a method call, assuming it returns a single context
            operand_ctx = ctx.unaryExpression() # Corrected access
            operand_value = self.visit(operand_ctx)
            op_token = op_terminal_node.symbol # Use .symbol

            if op_type == KumirLexer.PLUS:
                if not isinstance(operand_value, (int, float)):
                    raise KumirTypeError(f"Операция унарный плюс применима только к числам, получено {type(operand_value).__name__}.", getattr(op_token, 'line', None))
                return operand_value 
            elif op_type == KumirLexer.MINUS:
                if not isinstance(operand_value, (int, float)):
                    raise KumirTypeError(f"Операция унарный минус применима только к числам, получено {type(operand_value).__name__}.", getattr(op_token, 'line', None))
                return -operand_value
            elif op_type == KumirLexer.NOT: 
                operand_value = self.visitor._check_logical(operand_value, operand_ctx, "не")
                return not operand_value
        elif ctx.postfixExpression():
            return self.visit(ctx.postfixExpression())
        
        self.visitor.logger.error(f"Invalid unary expression structure: {ctx.getText()}") # pragma: no cover
        raise KumirEvalError("Некорректная структура унарного выражения", getattr(ctx, 'start', None)) # pragma: no cover

    def visitPowerExpression(self, ctx: KumirParser.PowerExpressionContext) -> Any:
        # powerExpression : unaryExpression (POWER powerExpression)? ; (right-associative)
        left_operand = self.visit(ctx.unaryExpression())

        if ctx.POWER(): 
            right_operand_ctx = ctx.powerExpression() 
            right_operand = self.visit(right_operand_ctx)
            
            op_terminal_node = ctx.getChild(1) # Get TerminalNode for POWER
            if not isinstance(op_terminal_node, TerminalNode):
                self.visitor.logger.error(f"Expected a TerminalNode for POWER operator, got {type(op_terminal_node)}")
                raise ValueError("Invalid POWER operator node")

            op_token = op_terminal_node.symbol # Access symbol attribute

            if not isinstance(left_operand, (int, float)) or not isinstance(right_operand, (int, float)):
                raise KumirTypeError(f"Операция возведения в степень ('^') применима только к числам. Получены типы {type(left_operand).__name__} и {type(right_operand).__name__}.", getattr(op_token, 'line', None))
            
            try:
                val = left_operand ** right_operand
                if isinstance(val, complex): # pragma: no cover
                    raise KumirEvalError("Результат возведения в степень является комплексным числом, что не поддерживается.", getattr(op_token, 'line', None))
                return val
            except ZeroDivisionError: 
                 raise KumirEvalError("Ошибка при возведении в степень (например, ноль в отрицательной степени).", getattr(op_token, 'line', None))
            except ValueError: # pragma: no cover (hard to trigger without complex numbers enabled)
                 raise KumirEvalError("Ошибка при возведении в степень (например, отрицательное число в дробную степень, ведущую к комплексному числу).", getattr(op_token, 'line', None))
        return left_operand

    def visitMultiplicativeExpression(self, ctx: KumirParser.MultiplicativeExpressionContext) -> Any:
        # multiplicativeExpression : powerExpression ( (MUL | DIV | MOD | DIV_INT) powerExpression )* ;
        result = self.visit(ctx.powerExpression(0))

        num_ops = len(ctx.powerExpression()) - 1
        for i in range(num_ops):
            op_terminal_node = ctx.getChild(i * 2 + 1) # This is a TerminalNode
            op_token = op_terminal_node.symbol # Use .symbol
            op_type = op_token.type
            
            right_operand_ctx = ctx.powerExpression(i + 1)
            right_operand = self.visit(right_operand_ctx)

            if not (isinstance(result, (int, float)) and isinstance(right_operand, (int, float))):
                raise KumirTypeError(f"Операции умножения/деления/mod/div применимы только к числам. Получены типы {type(result).__name__} и {type(right_operand).__name__} для оператора '{op_terminal_node.getText()}'.", getattr(op_token, 'line', None))

            if op_type == KumirLexer.MUL:
                result *= right_operand
            elif op_type == KumirLexer.DIV: 
                if right_operand == 0:
                    raise KumirEvalError("Деление на ноль.", getattr(op_token, 'line', None))
                result /= right_operand # Actual division
            # Removed MOD and DIV_INT cases
            else: # pragma: no cover
                self.visitor.logger.error(f"Unknown multiplicative operator: {op_terminal_node.getText()}")
                raise KumirNotImplementedError(f"Оператор '{op_terminal_node.getText()}' не реализован.", getattr(op_token, 'line', None))
        return result

    def visitAdditiveExpression(self, ctx: KumirParser.AdditiveExpressionContext) -> Any:
        # additiveExpression : multiplicativeExpression ( (PLUS | MINUS) multiplicativeExpression )* ;
        result = self.visit(ctx.multiplicativeExpression(0))

        num_ops = len(ctx.multiplicativeExpression()) - 1
        for i in range(num_ops):
            op_terminal_node = ctx.getChild(i * 2 + 1) # This is a TerminalNode
            op_token = op_terminal_node.symbol # Use .symbol
            op_type = op_token.type

            right_operand_ctx = ctx.multiplicativeExpression(i + 1)
            right_operand = self.visit(right_operand_ctx)
            
            if op_type == KumirLexer.PLUS:
                if isinstance(result, (int, float)) and isinstance(right_operand, (int, float)):
                    result += right_operand
                elif isinstance(result, str) and isinstance(right_operand, str):
                    result += right_operand
                # TODO: Consider char + string, char + char based on Kumir spec
                else:
                    raise KumirTypeError(f"Операция сложения '+' неприменима к типам {type(result).__name__} и {type(right_operand).__name__}.", getattr(op_token, 'line', None))
            elif op_type == KumirLexer.MINUS:
                if isinstance(result, (int, float)) and isinstance(right_operand, (int, float)):
                    result -= right_operand
                else:
                    raise KumirTypeError(f"Операция вычитания '-' применима только к числам. Получены типы {type(result).__name__} и {type(right_operand).__name__}.", getattr(op_token, 'line', None))
            else: # pragma: no cover
                self.visitor.logger.error(f"Unknown additive operator: {op_terminal_node.getText()}")
                raise KumirNotImplementedError(f"Оператор '{op_terminal_node.getText()}' не реализован.", getattr(op_token, 'line', None))
        return result

    def visitRelationalExpression(self, ctx: KumirParser.RelationalExpressionContext) -> Any:
        # relationalExpression : additiveExpression ( (LT | GT | LE | GE) additiveExpression )? ;
        left_operand = self.visit(ctx.additiveExpression(0))

        if len(ctx.additiveExpression()) > 1:
            op_terminal_node = ctx.getChild(1) # This is a TerminalNode
            op_token = op_terminal_node.symbol
            op_type = op_token.type
            
            right_operand_ctx = ctx.additiveExpression(1)
            right_operand = self.visit(right_operand_ctx)

            # Type checking and potential conversion for relational operands
            left_operand, right_operand = self.visitor._check_relational_operands(left_operand, right_operand, op_token)

            if op_type == KumirLexer.LT:
                return left_operand < right_operand
            elif op_type == KumirLexer.GT:
                return left_operand > right_operand
            elif op_type == KumirLexer.LE:
                return left_operand <= right_operand
            elif op_type == KumirLexer.GE:
                return left_operand >= right_operand
            else: # pragma: no cover
                self.visitor.logger.error(f"Unknown relational operator: {op_terminal_node.getText()}")
                raise KumirNotImplementedError(f"Оператор сравнения '{op_terminal_node.getText()}' не реализован.", getattr(op_token, 'line', None))
        return left_operand

    def visitEqualityExpression(self, ctx: KumirParser.EqualityExpressionContext) -> Any:
        # equalityExpression : relationalExpression ( (EQ | NE) relationalExpression )* ;
        result = self.visit(ctx.relationalExpression(0))

        num_ops = len(ctx.relationalExpression()) - 1
        for i in range(num_ops):
            op_terminal_node = ctx.getChild(i * 2 + 1) # This is a TerminalNode
            op_token = op_terminal_node.symbol # Use .symbol
            op_type = op_token.type

            right_operand_ctx = ctx.relationalExpression(i + 1)
            right_operand = self.visit(right_operand_ctx)
            
            # Kumir type rules for equality can be strict.
            # Python's ==, != are quite flexible.
            # For now, allow comparison if types are "compatible" (e.g. numeric, or same type)
            # A strict Kumir might error on int == real unless explicitly casted, or on 1 == "1".
            # This behavior might need refinement.
            
            # Example of a stricter check (optional, depends on Kumir spec):
            # if not (type(result) == type(right_operand) or \
            #        (isinstance(result, (int, float)) and isinstance(right_operand, (int, float)))):
            #    raise KumirTypeError(f"Нельзя сравнивать на равенство/неравенство {type(result).__name__} и {type(right_operand).__name__} оператором {op_terminal_node.getText()}.", getattr(op_token, 'line', None))

            if op_type == KumirLexer.EQ:
                result = (result == right_operand)
            elif op_type == KumirLexer.NE:
                result = (result != right_operand)
            else: # pragma: no cover
                self.visitor.logger.error(f"Unknown equality operator: {op_terminal_node.getText()}")
                raise KumirNotImplementedError(f"Оператор равенства '{op_terminal_node.getText()}' не реализован.", getattr(op_token, 'line', None))
        return result

    def visitLogicalAndExpression(self, ctx: KumirParser.LogicalAndExpressionContext) -> Any:
        # logicalAndExpression : relationalExpression ( AND relationalExpression )* ;
        result = self.visit(ctx.relationalExpression(0))

        for i in range(len(ctx.AND())):
            op_terminal_node = ctx.AND(i) # This is a TerminalNode
            op_token = op_terminal_node.symbol # Access symbol attribute

            if op_token.type != KumirLexer.AND:
                self.visitor.logger.error(f"Expected 'и' (AND) operator token, got {op_token.text}")
                raise ValueError(f"Type error: Expected AND operator, got {op_token.text}")

            right_operand_ctx = ctx.relationalExpression(i + 1)
            right_operand = self.visit(right_operand_ctx)
            
            # Ensure operands are boolean or can be converted
            left_bool = self.visitor._to_kumir_bool(result)
            right_bool = self.visitor._to_kumir_bool(right_operand)
            
            result = left_bool and right_bool
        return result

    def visitLogicalOrExpression(self, ctx: KumirParser.LogicalOrExpressionContext) -> Any:
        # logicalOrExpression : logicalAndExpression ( OR logicalAndExpression )* ;
        result = self.visit(ctx.logicalAndExpression(0))

        for i in range(len(ctx.OR())):
            op_terminal_node = ctx.OR(i) # This is a TerminalNode
            op_token = op_terminal_node.symbol # Access symbol attribute

            if op_token.type != KumirLexer.OR:
                self.visitor.logger.error(f"Expected 'или' (OR) operator token, got {op_token.text}")
                raise ValueError(f"Type error: Expected OR operator, got {op_token.text}")

            right_operand_ctx = ctx.logicalAndExpression(i + 1)
            right_operand = self.visit(right_operand_ctx)

            # Ensure operands are boolean or can be converted
            left_bool = self.visitor._to_kumir_bool(result)
            right_bool = self.visitor._to_kumir_bool(right_operand)

            result = left_bool or right_bool
        return result
        
    def visitExpression(self, ctx: KumirParser.ExpressionContext) -> Any:
        # Grammar: expression : logicalOrExpression ; (typically)
        if ctx.logicalOrExpression():
            return self.visit(ctx.logicalOrExpression())
        
        self.visitor.logger.error(f"Unknown expression structure: {ctx.getText()}") # pragma: no cover
        raise KumirEvalError(f"Cannot evaluate expression: {ctx.getText()}", getattr(ctx, 'start', None)) # pragma: no cover

    def visit(self, tree: Any) -> Any:
        method_name = 'visit' + tree.__class__.__name__.replace('Context', '')
        if hasattr(self, method_name):
            visitor_method = getattr(self, method_name)
            return visitor_method(tree)
        
        # Fallback for specific contexts if not covered by naming convention
        if isinstance(tree, KumirParser.ExpressionListContext):
             return self.visitExpressionList(tree)
        if isinstance(tree, KumirParser.ArgumentListContext):
             return self.visitArgumentList(tree)

        self.visitor.logger.error(f"Unsupported expression tree type for visit: {type(tree).__name__} ({tree.getText()[:80]}...)")
        raise KumirNotImplementedError(f"Evaluation for expression element type {type(tree).__name__} is not implemented.", getattr(tree, 'start', None))
