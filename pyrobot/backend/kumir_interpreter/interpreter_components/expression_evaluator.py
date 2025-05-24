# pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py
# expression_evaluator.py
# Этот файл будет содержать логику вычисления выражений для интерпретатора КуМира.

from __future__ import annotations
import operator # Keep for existing _perform_binary_operation
import sys # Keep for existing debug prints
from typing import TYPE_CHECKING, Any, Callable, Optional, Tuple, Union, cast

from antlr4 import ParserRuleContext, TerminalNode
from antlr4.Token import CommonToken, Token # Added Token
# from antlr4.tree.Tree import ParseTree # Removed, not directly used by new code

from ..generated.KumirLexer import KumirLexer
from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import ( # Updated exception imports
    KumirRuntimeError, KumirTypeError, KumirArgumentError,
    KumirIndexError, KumirNotImplementedError, KumirSyntaxError, KumirEvalError # Added KumirSyntaxError, KumirEvalError
)
from ..kumir_datatypes import KumirValue, KumirTableVar # KumirValue is now imported from kumir_datatypes

if TYPE_CHECKING:
    from .main_visitor import KumirInterpreterVisitor # Для type hinting
    # from .operations_handler import OperationsHandler # For later

ARITHMETIC_OPS = {
    KumirLexer.PLUS: operator.add,
    KumirLexer.MINUS: operator.sub,
    KumirLexer.MUL: operator.mul,
    KumirLexer.DIV: operator.truediv,
    KumirLexer.POWER: operator.pow,
}

COMPARISON_OPS = {
    KumirLexer.EQ: operator.eq,
    KumirLexer.NE: operator.ne,
    KumirLexer.LT: operator.lt,
    KumirLexer.GT: operator.gt,
    KumirLexer.LE: operator.le,
    KumirLexer.GE: operator.ge,
}

LOGICAL_OPS = {
    KumirLexer.AND: lambda a, b: a and b,
    KumirLexer.OR: lambda a, b: a or b,
}

class ExpressionEvaluator:
    def __init__(self, visitor: KumirInterpreterVisitor): # Type hint updated
        self.visitor = visitor
        # self.operations_handler: OperationsHandler = visitor.operations_handler # For later

    def _get_error_info(self, node_or_token: Optional[Union[ParserRuleContext, TerminalNode, Token]]) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        if node_or_token is None:
            return None, None, None

        line, column = None, None
        text_line: Optional[str] = None

        if isinstance(node_or_token, Token): 
            token = node_or_token
            line = token.line
            column = token.column
        elif isinstance(node_or_token, TerminalNode):
            symbol = node_or_token.getSymbol() 
            line = symbol.line
            column = symbol.column
        elif isinstance(node_or_token, ParserRuleContext):
            start_token = node_or_token.start
            if start_token:
                line = start_token.line
                column = start_token.column
        
        if line is not None and self.visitor.error_handler:
            if hasattr(self.visitor.error_handler, 'get_error_line_content'):
                 text_line = self.visitor.error_handler.get_error_line_content(node_or_token)
            elif hasattr(self.visitor, 'get_line_content_from_ctx'): 
                 if isinstance(node_or_token, ParserRuleContext):
                     text_line = self.visitor.get_line_content_from_ctx(node_or_token)
            elif hasattr(self.visitor.error_handler, '_get_line_col_content'): 
                try:
                    _, _, extracted_content, _ = self.visitor.error_handler._get_line_col_content(node_or_token=node_or_token)
                    text_line = extracted_content
                except Exception: 
                    pass 

        return line, column, text_line

    def _get_value(self, value_obj: Any) -> Any: # Renamed 'value' to 'value_obj' to avoid conflict
        if isinstance(value_obj, dict) and 'value' in value_obj and 'type' in value_obj: # For old-style dict values
            return value_obj['value']
        if isinstance(value_obj, KumirValue): 
            return value_obj.value
        return value_obj

    def _handle_type_promotion_for_comparison(self, left_kumir_val: KumirValue, right_kumir_val: KumirValue, ctx: ParserRuleContext) -> Tuple[Any, Any]:
        left = self._get_value(left_kumir_val)
        right = self._get_value(right_kumir_val)

        if left is None or right is None:
            self.visitor.error_handler.runtime_error( 
                "Нельзя сравнивать с неинициализированным значением.",
                node_or_token=ctx 
            )
            return None, None 

        is_left_int = isinstance(left, int)
        is_left_float = isinstance(left, float)
        is_right_int = isinstance(right, int)
        is_right_float = isinstance(right, float)

        if is_left_int and is_right_float:
            # print(f"[DEBUG][TypePromoEE] Promoting left operand {left} (int) to float for comparison with {right} (float)", file=sys.stderr)
            return float(left), right
        if is_left_float and is_right_int:
            # print(f"[DEBUG][TypePromoEE] Promoting right operand {right} (int) to float for comparison with {left} (float)", file=sys.stderr)
            return left, float(right)
        return left, right

    def _check_numeric(self, kumir_val: KumirValue, operation_name: str, ctx: Optional[Union[ParserRuleContext, TerminalNode, Token]]) -> Any:
        # print(f"[DEBUG][_check_numericEE] ENTERED. Op: {operation_name}. Value initial: {repr(kumir_val)}.", file=sys.stderr)
        
        if not isinstance(kumir_val, KumirValue):
             self.visitor.error_handler.runtime_error(
                f"Ожидалось значение KumirValue для операции '{operation_name}', получено {type(kumir_val).__name__}",
                node_or_token=ctx
            )
             return None 

        processed_value = kumir_val.value
        # print(f"[DEBUG][_check_numericEE] Value for op '{operation_name}': {repr(processed_value)} (type: {type(processed_value).__name__})", file=sys.stderr)
        
        if processed_value is None: 
            # print(f"[DEBUG][_check_numericEE] Raising KumirEvalError: processed_value is None for op '{operation_name}'", file=sys.stderr)
            self.visitor.error_handler.runtime_error( 
                f"Попытка использовать неинициализированное значение в операции '{operation_name}'",
                node_or_token=ctx
            )
            return None 
        
        if not isinstance(processed_value, (int, float)):
            self.visitor.error_handler.type_error( 
                f"Операция '{operation_name}' ожидает числовое значение, получено {kumir_val.kumir_type} ('{processed_value}')",
                node_or_token=ctx
            )
            return None 
        return processed_value

    def _check_logical(self, kumir_val: KumirValue, operation_name: str, ctx: Optional[Union[ParserRuleContext, TerminalNode, Token]]) -> Any:
        if not isinstance(kumir_val, KumirValue):
             self.visitor.error_handler.runtime_error(
                f"Ожидалось значение KumirValue для логической операции '{operation_name}', получено {type(kumir_val).__name__}",
                node_or_token=ctx
            )
             return None

        processed_value = kumir_val.value
        if processed_value is None:
            self.visitor.error_handler.runtime_error( 
                f"Попытка использовать неинициализированное значение в логической операции '{operation_name}'",
                node_or_token=ctx
            )
            return None
        if not isinstance(processed_value, bool):
            self.visitor.error_handler.type_error( 
                f"Операция '{operation_name}' ожидает логическое значение (да/нет), получено {kumir_val.kumir_type} ('{processed_value}')",
                node_or_token=ctx
            )
            return None
        return processed_value

    def _check_comparable(self, kumir_val: KumirValue, operation_name: str, ctx: Optional[Union[ParserRuleContext, TerminalNode, Token]]) -> Any:
        if not isinstance(kumir_val, KumirValue):
            self.visitor.error_handler.runtime_error(
                f"Ожидалось значение KumirValue для операции сравнения '{operation_name}', получено {type(kumir_val).__name__}",
                node_or_token=ctx
            )
            return None
            
        processed_value = kumir_val.value
        if processed_value is None:
            self.visitor.error_handler.runtime_error( 
                f"Попытка использовать неинициализированное значение в операции сравнения '{operation_name}'",
                node_or_token=ctx
            )
            return None
        if not isinstance(processed_value, (int, float, str, bool)):
            self.visitor.error_handler.type_error( 
                f"Значение типа {kumir_val.kumir_type} ('{processed_value}') не может быть использовано в операции сравнения '{operation_name}'",
                node_or_token=ctx
            )
            return None
        return processed_value
        
    def _perform_binary_operation(self, left_kumir_val: KumirValue, right_kumir_val: KumirValue, op_token_node: TerminalNode, expression_node_ctx: ParserRuleContext) -> KumirValue:
        op_symbol = op_token_node.getSymbol() 
        op_text = op_symbol.text
        op_type = op_symbol.type

        # print(f"[DEBUG][PBO_OP_DETAILSEE] op_text='{op_text}', op_type_val={op_type}, KumirLexer.DIV={KumirLexer.DIV}", file=sys.stderr)
        
        checked_left_val = self._check_numeric(left_kumir_val, op_text, expression_node_ctx) 
        checked_right_val = self._check_numeric(right_kumir_val, op_text, expression_node_ctx)
        
        if checked_left_val is None or checked_right_val is None: # Error already handled by _check_numeric
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", expression_node_ctx)

        operation_func = ARITHMETIC_OPS.get(op_type)
        # print(f"[DEBUG][PBO_OP_DETAILSEE] op_text='{op_text}', op_type_val={op_type}, operation_func_found={bool(operation_func)}", file=sys.stderr)
        
        if not operation_func:
            self.visitor.error_handler.syntax_error(f"Неизвестный или нечисловой бинарный оператор: {op_text}", node_or_token=op_symbol)
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", expression_node_ctx)

        if op_type == KumirLexer.DIV:
            if checked_right_val == 0:
                self.visitor.error_handler.runtime_error("Деление на ноль.", node_or_token=expression_node_ctx)
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", expression_node_ctx)
        try:
            py_result = operation_func(checked_left_val, checked_right_val)
            
            result_kumir_type = "ВЕЩ" 
            if left_kumir_val.kumir_type == "ЦЕЛ" and right_kumir_val.kumir_type == "ЦЕЛ" and op_type != KumirLexer.DIV:
                if isinstance(py_result, int):
                    result_kumir_type = "ЦЕЛ"
                elif isinstance(py_result, float) and py_result.is_integer():
                    if op_type == KumirLexer.POWER:
                        if left_kumir_val.kumir_type == "ЦЕЛ" and right_kumir_val.kumir_type == "ЦЕЛ":
                             py_result = int(py_result) 
                             result_kumir_type = "ЦЕЛ"
                        else: 
                             result_kumir_type = "ВЕЩ"
            elif op_type == KumirLexer.DIV: 
                result_kumir_type = "ВЕЩ"
                if not isinstance(py_result, float): 
                    py_result = float(py_result)

            if result_kumir_type == "ВЕЩ" and isinstance(py_result, int):
                py_result = float(py_result)
            
            return self.visitor.type_converter.create_kumir_value(py_result, result_kumir_type, expression_node_ctx)

        except TypeError as e:
            self.visitor.error_handler.type_error(f"Несовместимые типы для операции '{op_text}': {left_kumir_val.kumir_type} и {right_kumir_val.kumir_type}. {e}", node_or_token=expression_node_ctx)
        except ZeroDivisionError: 
            self.visitor.error_handler.runtime_error("Деление на ноль.", node_or_token=expression_node_ctx)
        except OverflowError:
            self.visitor.error_handler.runtime_error(f"Переполнение при выполнении операции '{op_text}'.", node_or_token=expression_node_ctx)
        except Exception as e: 
            self.visitor.error_handler.runtime_error(f"Ошибка при вычислении бинарной операции '{op_text}': {e}", node_or_token=expression_node_ctx)
        
        return self.visitor.type_converter.create_kumir_value(None, "Ошибка", expression_node_ctx) 

    def visitLiteral(self, ctx: KumirParser.LiteralContext) -> KumirValue: 
        if ctx.INTEGER():
            val = int(ctx.INTEGER().getText())
            return self.visitor.type_converter.create_kumir_value(val, "ЦЕЛ", ctx)
        elif ctx.REAL():
            val_str = ctx.REAL().getText().replace(',', '.')
            val = float(val_str)
            return self.visitor.type_converter.create_kumir_value(val, "ВЕЩ", ctx)
        elif ctx.STRING():
            text = ctx.STRING().getText()
            val = text[1:-1].replace('\'\'\'', '\'') # Исправлено для одинарных кавычек, если КуМир их так удваивает. Если двойные, то "" -> "
            # В КуМире строки заключаются в двойные кавычки, а две двойные кавычки подряд внутри строки означают одну двойную кавычку.
            val = text[1:-1].replace('""', '"')
            return self.visitor.type_converter.create_kumir_value(val, "ЛИТ", ctx)
        elif ctx.CHAR_LITERAL():
            text = ctx.CHAR_LITERAL().getText()
            # Символьные литералы в КуМире: 'а', '#'
            # getText() вернет "'а'". Нам нужен 'а'.
            val = text[1:-1] 
            return self.visitor.type_converter.create_kumir_value(val, "СИМ", ctx)
        elif ctx.TRUE():
            return self.visitor.type_converter.create_kumir_value(True, "ЛОГ", ctx)
        elif ctx.FALSE():
            return self.visitor.type_converter.create_kumir_value(False, "ЛОГ", ctx)
        elif ctx.NEWLINE_CONST(): 
            self.visitor.error_handler.type_error(
                "Константа 'нс' не может быть использована как значение в выражении.",
                ctx.NEWLINE_CONST() 
            )
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx) 
        elif ctx.colorLiteral():
            return self.visitColorLiteral(ctx.colorLiteral())
        else:
            # Эта ветка не должна достигаться, если грамматика покрывает все литералы
            self.visitor.error_handler.syntax_error( 
                f"Неизвестный или нераспознанный тип литерала: {ctx.getText()}",
                ctx
            )
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

    def visitColorLiteral(self, ctx: KumirParser.ColorLiteralContext) -> KumirValue: 
        self.visitor.error_handler.not_implemented_error(
            f"Цветовые литералы пока не поддерживаются: {ctx.getText()}",
            ctx
        )
        return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx) 


    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitPrimaryExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        if ctx.literal():
            return self.visitLiteral(ctx.literal())
        elif ctx.qualifiedIdentifier():
            var_name = ctx.qualifiedIdentifier().getText()
            return self.visitor.get_variable_value(var_name, ctx) 
        elif ctx.RETURN_VALUE():
            return self.visitor.get_current_return_value(ctx)
        elif ctx.LPAREN() and ctx.RPAREN() and ctx.expression():
             return self.visitExpression(ctx.expression()) 
        else:
            self.visitor.error_handler.syntax_error(f"Неизвестная или невалидная структура primaryExpression: {ctx.getText()}", node_or_token=ctx)
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
        
    def visitPostfixExpression(self, ctx: KumirParser.PostfixExpressionContext) -> KumirValue:
        # print(f"[Enter] visitPostfixExpressionEE for {ctx.getText()}", file=sys.stderr)
        primary_expr_ctx = ctx.primaryExpression()
        if not primary_expr_ctx:
            self.visitor.error_handler.syntax_error("Отсутствует primaryExpression в postfixExpression.", node_or_token=ctx)
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

        current_eval_kumir_value = self.visitPrimaryExpression(primary_expr_ctx)
        # print(f"[DEBUG][PostfixEE] Primary eval: '{primary_expr_ctx.getText()}' -> {repr(current_eval_kumir_value)}", file=sys.stderr)

        num_children = len(ctx.children)
        child_idx = 1 # Начинаем после primaryExpression (индекс 0)

        while child_idx < num_children:
            op_node = ctx.getChild(child_idx) # Это может быть LBRACK или LPAREN (TerminalNode)

            if not isinstance(op_node, TerminalNode):
                err_node_info = op_node if isinstance(op_node, (ParserRuleContext, Token)) else ctx
                self.visitor.error_handler.syntax_error(f"Ожидался оператор ( [ или ( ) в постфиксном выражении, получен узел типа {type(op_node).__name__}.", node_or_token=err_node_info)
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

            op_symbol = op_node.getSymbol()
            op_type = op_symbol.type

            if op_type == KumirLexer.LBRACK: 
                if child_idx + 2 >= num_children: # LBRACK, indexList, RBRACK
                    self.visitor.error_handler.syntax_error("Неожиданный конец выражения после '[' при доступе к таблице.", node_or_token=op_symbol)
                    return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
                
                index_list_ctx = ctx.getChild(child_idx + 1)
                rbrack_node = ctx.getChild(child_idx + 2)

                if not isinstance(index_list_ctx, KumirParser.IndexListContext) or \
                   not (isinstance(rbrack_node, TerminalNode) and rbrack_node.getSymbol().type == KumirLexer.RBRACK):
                    err_node_info = index_list_ctx if isinstance(index_list_ctx, ParserRuleContext) else op_symbol
                    self.visitor.error_handler.syntax_error("Некорректный формат доступа к таблице, ожидался список индексов и ']'.", node_or_token=err_node_info)
                    return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
                
                current_eval_kumir_value = self.visitor.evaluate_table_access(current_eval_kumir_value, index_list_ctx, op_symbol)
                child_idx += 3 
            
            elif op_type == KumirLexer.LPAREN: 
                arg_list_ctx: Optional[KumirParser.ArgumentListContext] = None
                next_node_idx = child_idx + 1 
                
                # Проверяем, есть ли argumentList
                if next_node_idx < num_children and isinstance(ctx.getChild(next_node_idx), KumirParser.ArgumentListContext):
                    arg_list_ctx = cast(KumirParser.ArgumentListContext, ctx.getChild(next_node_idx))
                    next_node_idx += 1 
                
                # Проверяем наличие RPAREN
                if next_node_idx >= num_children or \
                   not (isinstance(ctx.getChild(next_node_idx), TerminalNode) and ctx.getChild(next_node_idx).getSymbol().type == KumirLexer.RPAREN):
                    self.visitor.error_handler.syntax_error("Неожиданный конец или неверный формат вызова функции, ожидалась ')' после списка аргументов.", node_or_token=op_symbol)
                    return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

                current_eval_kumir_value = self.visitor.evaluate_function_call(primary_expr_ctx, current_eval_kumir_value, arg_list_ctx, op_symbol)
                child_idx = next_node_idx + 1 
            else:
                self.visitor.error_handler.syntax_error(f"Неожиданный токен '{op_symbol.text}' в постфиксном выражении.", node_or_token=op_symbol)
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
            
            if current_eval_kumir_value.kumir_type == "Ошибка": # Если evaluate_table_access или evaluate_function_call вернули ошибку
                return current_eval_kumir_value
        
        # print(f"[Exit] visitPostfixExpressionEE for {ctx.getText()} -> returns {repr(current_eval_kumir_value)}", file=sys.stderr)
        return current_eval_kumir_value

    def visitUnaryExpression(self, ctx: KumirParser.UnaryExpressionContext) -> KumirValue:
        op_type_token: Optional[Token] = None
        op_str: Optional[str] = None # Для сообщений об ошибках

        if ctx.PLUS(): 
            op_type_token = ctx.PLUS().getSymbol()
            op_str = "унарный +"
        elif ctx.MINUS(): 
            op_type_token = ctx.MINUS().getSymbol()
            op_str = "унарный -"
        elif ctx.NOT(): 
            op_type_token = ctx.NOT().getSymbol()
            op_str = "не"
        
        # print(f"[DEBUG][visitUnaryExpressionEE] Called for ctx: {ctx.getText()}, op: {op_str}", file=sys.stderr)
        
        target_node_for_visit: Optional[ParserRuleContext] = None
        
        if op_type_token is not None: 
            # Грамматика: (PLUS | MINUS | NOT) unaryExpression
            unary_child_node = ctx.unaryExpression() 
            if unary_child_node:
                 target_node_for_visit = unary_child_node
            else: 
                 # Это синтаксическая ошибка, которую должен поймать парсер, но на всякий случай
                 self.visitor.error_handler.syntax_error(f"Оператор '{op_str}' без операнда в унарном выражении: {ctx.getText()}", node_or_token=op_type_token)
                 return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
        elif ctx.postfixExpression(): 
            # Грамматика: postfixExpression
            postfix_child_node = ctx.postfixExpression()
            if postfix_child_node: # Должен быть всегда, если эта ветка активна
                target_node_for_visit = postfix_child_node
            # else: # Не должно произойти по грамматике
        else: 
            # Не должно быть других альтернатив по грамматике
            self.visitor.error_handler.syntax_error(f"Некорректная структура унарного выражения: {ctx.getText()}", node_or_token=ctx)
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

        if not target_node_for_visit: # Дополнительная проверка
             self.visitor.error_handler.internal_error(f"Не удалось определить узел для вычисления в унарном выражении {ctx.getText()}", node_or_token=ctx)
             return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
        
        kumir_value: KumirValue
        if isinstance(target_node_for_visit, KumirParser.UnaryExpressionContext):
            kumir_value = self.visitUnaryExpression(target_node_for_visit) # Рекурсивный вызов
        elif isinstance(target_node_for_visit, KumirParser.PostfixExpressionContext):
            kumir_value = self.visitPostfixExpression(target_node_for_visit)
        else:
            self.visitor.error_handler.internal_error(f"Неожиданный тип узла ({type(target_node_for_visit).__name__}) для вычисления в унарном выражении.", node_or_token=target_node_for_visit)
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

        # print(f"[DEBUG][visitUnaryExpressionEE] Value from sub-expression '{target_node_for_visit.getText()}': {repr(kumir_value)}", file=sys.stderr)
        if kumir_value.kumir_type == "Ошибка": return kumir_value


        if op_type_token: # Если был унарный оператор
            py_value = None
            if op_type_token.type == KumirLexer.PLUS: 
                py_value = self._check_numeric(kumir_value, op_str, op_type_token)
                if py_value is not None: 
                     return kumir_value 
            elif op_type_token.type == KumirLexer.MINUS: 
                py_value = self._check_numeric(kumir_value, op_str, op_type_token)
                if py_value is not None:
                    # Тип результата такой же, как у операнда (ЦЕЛ -> ЦЕЛ, ВЕЩ -> ВЕЩ)
                    return self.visitor.type_converter.create_kumir_value(-py_value, kumir_value.kumir_type, op_type_token)
            elif op_type_token.type == KumirLexer.NOT: 
                py_value = self._check_logical(kumir_value, op_str, op_type_token)
                if py_value is not None:
                    return self.visitor.type_converter.create_kumir_value(not py_value, "ЛОГ", op_type_token)
            
            # Если py_value is None, значит была ошибка типа/значения, error_handler уже ее обработал
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", op_type_token or ctx)
        else: # Нет унарного оператора, просто возвращаем значение postfixExpression
            return kumir_value 

    def visitPowerExpression(self, ctx: KumirParser.PowerExpressionContext) -> KumirValue:
        # Грамматика: powerExpression : unaryExpression (POWER powerExpression)?
        base_unary_expr_ctx = ctx.unaryExpression() 
        if not base_unary_expr_ctx: # Не должно произойти по грамматике
            self.visitor.error_handler.syntax_error(f"Отсутствует базовое выражение в powerExpression. Текст: {ctx.getText()}", node_or_token=ctx)
            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
        
        base_kumir_value = self.visitUnaryExpression(base_unary_expr_ctx)
        if base_kumir_value.kumir_type == "Ошибка": return base_kumir_value

        power_op_terminal_node = ctx.POWER() # Это TerminalNodeImpl (если есть POWER) или None

        if power_op_terminal_node:
            # Есть операция '**', значит должна быть и правая часть (рекурсивный powerExpression)
            exponent_power_expr_ctx = ctx.powerExpression() 
            if not exponent_power_expr_ctx: # Не должно произойти по грамматике
                self.visitor.error_handler.syntax_error(
                    f"Отсутствует показатель степени после операции '**'.",
                    node_or_token=power_op_terminal_node 
                )
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
            
            exponent_kumir_value = self.visitPowerExpression(exponent_power_expr_ctx) # Рекурсивный вызов
            if exponent_kumir_value.kumir_type == "Ошибка": return exponent_kumir_value
            
            return self._perform_binary_operation(base_kumir_value, exponent_kumir_value, power_op_terminal_node, ctx)
        else:
            # Оператора POWER нет, значит это просто unaryExpression
            return base_kumir_value

    def visitMultiplicativeExpression(self, ctx: KumirParser.MultiplicativeExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitMultiplicativeExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        
        current_kumir_result = self.visitPowerExpression(ctx.powerExpression(0))
        # print(f"[DEBUG][visitMultiplicativeExpressionEE] Initial result from left powerExpression: {repr(current_kumir_result)}", file=sys.stderr)
        if current_kumir_result.kumir_type == "Ошибка": return current_kumir_result

        num_power_expressions = len(ctx.powerExpression())
        for i in range(num_power_expressions - 1):
            op_terminal_node = cast(TerminalNode, ctx.getChild(2 * i + 1)) 
            op_symbol = op_terminal_node.getSymbol()
            op_text = op_symbol.text
            
            right_operand_ctx = ctx.powerExpression(i + 1)
            right_kumir_operand = self.visitPowerExpression(right_operand_ctx)
            # print(f"[DEBUG][visitMultiplicativeExpressionEE] Right operand for '{op_text}': {repr(right_kumir_operand)}", file=sys.stderr)
            if right_kumir_operand.kumir_type == "Ошибка": return right_kumir_operand
            
            if op_symbol.type in ARITHMETIC_OPS: # MUL, DIV
                current_kumir_result = self._perform_binary_operation(current_kumir_result, right_kumir_operand, op_terminal_node, ctx)
            else: # Не должно произойти, если грамматика верна
                self.visitor.error_handler.syntax_error(f"Неизвестный или невалидный мультипликативный оператор: {op_text}", node_or_token=op_terminal_node)
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

            # print(f"[DEBUG][visitMultiplicativeExpressionEE] Result after '{op_text}': {repr(current_kumir_result)}", file=sys.stderr)
            if current_kumir_result.kumir_type == "Ошибка": 
                return current_kumir_result

        # print(f"[Exit] visitMultiplicativeExpressionEE for '{ctx.getText()}' -> returns {repr(current_kumir_result)}", file=sys.stderr)
        return current_kumir_result

    def visitAdditiveExpression(self, ctx: KumirParser.AdditiveExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitAdditiveExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        current_kumir_result = self.visitMultiplicativeExpression(ctx.multiplicativeExpression(0))
        # print(f"[DEBUG][visitAdditiveExpressionEE] Initial result from left multExpression: {repr(current_kumir_result)}", file=sys.stderr)
        if current_kumir_result.kumir_type == "Ошибка": return current_kumir_result

        num_mult_expressions = len(ctx.multiplicativeExpression())
        for i in range(num_mult_expressions - 1):
            op_terminal_node = cast(TerminalNode, ctx.getChild(2 * i + 1)) 
            op_symbol = op_terminal_node.getSymbol()
            op_text = op_symbol.text
            
            right_operand_ctx = ctx.multiplicativeExpression(i + 1)
            right_kumir_operand = self.visitMultiplicativeExpression(right_operand_ctx)
            if right_kumir_operand.kumir_type == "Ошибка": return right_kumir_operand

            val_left_py = self._get_value(current_kumir_result) 
            val_right_py = self._get_value(right_kumir_operand)

            # print(f"[DEBUG][visitAdditiveExpressionEE] Op: {op_text}, Left: {val_left_py} (type {type(val_left_py)}), Right: {val_right_py} (type {type(val_right_py)})", file=sys.stderr)

            if op_symbol.type == KumirLexer.PLUS or op_symbol.type == KumirLexer.MINUS:
                # Специальная обработка для сложения строк
                if current_kumir_result.kumir_type == "ЛИТ" or right_kumir_operand.kumir_type == "ЛИТ":
                    if current_kumir_result.kumir_type == "ЛИТ" and right_kumir_operand.kumir_type == "ЛИТ":
                        if op_symbol.type == KumirLexer.PLUS:
                            current_kumir_result = self.visitor.type_converter.create_kumir_value(str(val_left_py) + str(val_right_py), "ЛИТ", ctx)
                        else: # MINUS для строк не определен
                            self.visitor.error_handler.type_error(f"Операция '-' не применима к строкам.", node_or_token=op_symbol)
                            return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
                    else: # Попытка сложить/вычесть строку с нестрокой
                        self.visitor.error_handler.type_error(f"Нельзя складывать/вычитать строку с нестрокой без явного преобразования: '{val_left_py}' ({current_kumir_result.kumir_type}) и '{val_right_py}' ({right_kumir_operand.kumir_type})", node_or_token=op_symbol)
                        return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
                else: # Оба не строки, значит числовая операция
                    current_kumir_result = self._perform_binary_operation(current_kumir_result, right_kumir_operand, op_terminal_node, ctx)
            else: # Не должно произойти
                self.visitor.error_handler.syntax_error(f"Неизвестный или невалидный аддитивный оператор: {op_text}", node_or_token=op_symbol)
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
            
            # print(f"[DEBUG][visitAdditiveExpressionEE] Intermediate result: {repr(current_kumir_result)}", file=sys.stderr)
            if current_kumir_result.kumir_type == "Ошибка":
                return current_kumir_result
        
        # print(f"[Exit] visitAdditiveExpressionEE for '{ctx.getText()}' -> returns {repr(current_kumir_result)}", file=sys.stderr)
        return current_kumir_result

    def visitRelationalExpression(self, ctx: KumirParser.RelationalExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitRelationalExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        left_kumir_operand = self.visitAdditiveExpression(ctx.additiveExpression(0))
        # print(f"[DEBUG][visitRelationalExpressionEE] Received from first additiveExpression: {repr(left_kumir_operand)}", file=sys.stderr)
        if left_kumir_operand.kumir_type == "Ошибка": return left_kumir_operand

        if len(ctx.additiveExpression()) > 1: # Есть операция сравнения
            op_terminal_node = cast(TerminalNode, ctx.getChild(1)) 
            op_symbol = op_terminal_node.getSymbol()
            op_text = op_symbol.text
            
            right_kumir_operand = self.visitAdditiveExpression(ctx.additiveExpression(1))
            # print(f"[DEBUG][visitRelationalExpressionEE] Received for relational's right operand: {repr(right_kumir_operand)}", file=sys.stderr)
            if right_kumir_operand.kumir_type == "Ошибка": return right_kumir_operand
            
            # Проверка на возможность сравнения перед промоушеном
            # self._check_comparable(left_kumir_operand, op_text, op_symbol) # Должно быть вызвано, если необходимо
            # self._check_comparable(right_kumir_operand, op_text, op_symbol)

            promoted_left_py, promoted_right_py = self._handle_type_promotion_for_comparison(left_kumir_operand, right_kumir_operand, ctx)

            if promoted_left_py is None or promoted_right_py is None: 
                 return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

            op_func = COMPARISON_OPS.get(op_symbol.type)
            if op_func:
                # В КуМире нельзя сравнивать строки с числами и т.д. напрямую.
                # _handle_type_promotion_for_comparison приводит числа к одному типу.
                # Если после этого типы разные, и это не пара (число, число), то это ошибка.
                if type(promoted_left_py) != type(promoted_right_py) and \
                   not (isinstance(promoted_left_py, (int, float)) and isinstance(promoted_right_py, (int, float))):
                    self.visitor.error_handler.type_error(f"Нельзя сравнивать значения разных типов: {left_kumir_operand.kumir_type} ('{promoted_left_py}') и {right_kumir_operand.kumir_type} ('{promoted_right_py}') оператором '{op_text}'.", node_or_token=op_symbol)
                    return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

                py_result = op_func(promoted_left_py, promoted_right_py)
                current_kumir_result = self.visitor.type_converter.create_kumir_value(py_result, "ЛОГ", ctx)
            else: # Не должно произойти
                self.visitor.error_handler.syntax_error(f"Неизвестный или невалидный оператор сравнения: {op_text}", node_or_token=op_symbol)
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
            
            # print(f"[DEBUG][visitRelationalExpressionEE] Result after '{op_text}': {repr(current_kumir_result)}", file=sys.stderr)
            return current_kumir_result
        else: 
            return left_kumir_operand # Это не операция сравнения, а просто additiveExpression

    def visitEqualityExpression(self, ctx: KumirParser.EqualityExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitEqualityExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        left_kumir_operand = self.visitRelationalExpression(ctx.relationalExpression(0))
        # print(f"[DEBUG][visitEqualityExpressionEE] Received from first relationalExpression: {repr(left_kumir_operand)}", file=sys.stderr)
        if left_kumir_operand.kumir_type == "Ошибка": return left_kumir_operand

        if len(ctx.relationalExpression()) > 1: # Есть операция равенства/неравенства
            op_terminal_node = cast(TerminalNode, ctx.getChild(1))
            op_symbol = op_terminal_node.getSymbol()
            op_text = op_symbol.text

            right_kumir_operand = self.visitRelationalExpression(ctx.relationalExpression(1))
            # print(f"[DEBUG][visitEqualityExpressionEE] Received for equality's right operand: {repr(right_kumir_operand)}", file=sys.stderr)
            if right_kumir_operand.kumir_type == "Ошибка": return right_kumir_operand
            
            promoted_left_py, promoted_right_py = self._handle_type_promotion_for_comparison(left_kumir_operand, right_kumir_operand, ctx)

            if promoted_left_py is None or promoted_right_py is None:
                 return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
            
            op_func = COMPARISON_OPS.get(op_symbol.type) # EQ, NE
            if op_func:
                # Сравнение на равенство/неравенства в КуМире:
                # Числа сравниваются по значению (1 = 1.0).
                # Строки сравниваются лексикографически.
                # Логические значения сравниваются.
                # Сравнение разных типов (кроме числовых друг с другом) обычно дает ложь для EQ и истину для NE,
                # либо ошибку в строгих реализациях. Python `1 == "1"` -> False.
                # Будем следовать поведению Python, если типы разные и не числовые.
                py_result: bool
                if type(promoted_left_py) != type(promoted_right_py) and \
                   not (isinstance(promoted_left_py, (int, float)) and isinstance(promoted_right_py, (int, float))):
                    # Разные типы (не числа)
                    if op_symbol.type == KumirLexer.EQ:
                        py_result = False
                    elif op_symbol.type == KumirLexer.NE:
                        py_result = True
                    else: # Не должно быть других операторов здесь
                        py_result = op_func(promoted_left_py, promoted_right_py) 
                else: # Одинаковые типы или оба числовые
                    py_result = op_func(promoted_left_py, promoted_right_py)
                
                current_kumir_result = self.visitor.type_converter.create_kumir_value(py_result, "ЛОГ", ctx)
            else: # Не должно произойти
                self.visitor.error_handler.syntax_error(f"Неизвестный или невалидный оператор равенства/неравенства: {op_text}", node_or_token=op_symbol)
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
            
            # print(f"[DEBUG][visitEqualityExpressionEE] Result after comparison '{op_text}': {repr(current_kumir_result)}", file=sys.stderr)
            return current_kumir_result
        else:
            return left_kumir_operand # Это не операция равенства, а просто relationalExpression

    def visitLogicalAndExpression(self, ctx: KumirParser.LogicalAndExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitLogicalAndExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        current_kumir_result = self.visitEqualityExpression(ctx.equalityExpression(0))
        # print(f"[DEBUG][visitLogicalAndExpressionEE] Received from first equalityExpression: {repr(current_kumir_result)}", file=sys.stderr)
        if current_kumir_result.kumir_type == "Ошибка": return current_kumir_result
        
        num_equality_expressions = len(ctx.equalityExpression())
        if num_equality_expressions > 1: # Есть операция "И"
            # Проверяем левый операнд (current_kumir_result)
            # Оператор "И" - это ctx.getChild(1), ctx.getChild(3) и т.д.
            op_and_node_for_check = cast(TerminalNode, ctx.getChild(1))
            checked_left_py = self._check_logical(current_kumir_result, "И", op_and_node_for_check) 
            if checked_left_py is None: # Ошибка в _check_logical
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

            if not checked_left_py: # Short-circuit для 'И'
                return self.visitor.type_converter.create_kumir_value(False, "ЛОГ", ctx)

            # Если checked_left_py is True, продолжаем вычислять остальные
            # current_py_result хранит текущий результат логической операции (начинается с True)
            current_py_result = checked_left_py 

            for i in range(1, num_equality_expressions):
                op_and_node = cast(TerminalNode, ctx.getChild(2 * i - 1)) # Токен 'И'

                right_operand_ctx = ctx.equalityExpression(i)
                right_kumir_operand = self.visitEqualityExpression(right_operand_ctx)
                if right_kumir_operand.kumir_type == "Ошибка": return right_kumir_operand

                checked_right_py = self._check_logical(right_kumir_operand, "И", op_and_node)
                if checked_right_py is None: 
                     return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

                current_py_result = current_py_result and checked_right_py 
                if not current_py_result: # Short-circuit
                    return self.visitor.type_converter.create_kumir_value(False, "ЛОГ", ctx)
            
            # Если дошли сюда, все операнды были True
            return self.visitor.type_converter.create_kumir_value(True, "ЛОГ", ctx)
        
        else: # Только один equalityExpression
             # Если это выражение используется там, где ожидается ЛОГ, то проверка типа нужна.
             checked_val_py = self._check_logical(current_kumir_result, "логическое выражение", ctx)
             if checked_val_py is None: 
                 return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
             # current_kumir_result уже правильного типа (ЛОГ) или была ошибка
             return current_kumir_result


    def visitLogicalOrExpression(self, ctx: KumirParser.LogicalOrExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitLogicalOrExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        current_kumir_result = self.visitLogicalAndExpression(ctx.logicalAndExpression(0))
        # print(f"[DEBUG][visitLogicalOrExpressionEE] Received from first logicalAndExpression: {repr(current_kumir_result)}", file=sys.stderr)
        if current_kumir_result.kumir_type == "Ошибка": return current_kumir_result

        num_log_and_expressions = len(ctx.logicalAndExpression())
        if num_log_and_expressions > 1: # Есть операция "ИЛИ"
            op_or_node_for_check = cast(TerminalNode, ctx.getChild(1))
            checked_left_py = self._check_logical(current_kumir_result, "ИЛИ", op_or_node_for_check)
            if checked_left_py is None:
                return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)

            if checked_left_py: # Short-circuit для 'ИЛИ'
                return self.visitor.type_converter.create_kumir_value(True, "ЛОГ", ctx)

            current_py_result = checked_left_py # Начинается с False

            for i in range(1, num_log_and_expressions):
                op_or_node = cast(TerminalNode, ctx.getChild(2 * i - 1)) 

                right_operand_ctx = ctx.logicalAndExpression(i)
                right_kumir_operand = self.visitLogicalAndExpression(right_operand_ctx)
                if right_kumir_operand.kumir_type == "Ошибка": return right_kumir_operand
                
                checked_right_py = self._check_logical(right_kumir_operand, "ИЛИ", op_or_node)
                if checked_right_py is None:
                    return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
                
                current_py_result = current_py_result or checked_right_py
                if current_py_result: # Short-circuit
                    return self.visitor.type_converter.create_kumir_value(True, "ЛОГ", ctx)
            
            # Если дошли сюда, все операнды были False
            return self.visitor.type_converter.create_kumir_value(False, "ЛОГ", ctx)

        else: # Только один logicalAndExpression
            checked_val_py = self._check_logical(current_kumir_result, "логическое выражение", ctx)
            if checked_val_py is None:
                 return self.visitor.type_converter.create_kumir_value(None, "Ошибка", ctx)
            return current_kumir_result

    def visitExpression(self, ctx: KumirParser.ExpressionContext) -> KumirValue:
        # print(f"[DEBUG][visitExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        kumir_result = self.visitLogicalOrExpression(ctx.logicalOrExpression())
        # print(f"[DEBUG][visitExpressionEE] Received from visitLogicalOrExpression: {repr(kumir_result)}", file=sys.stderr)
        return kumir_result
    
    # Вспомогательные методы для lvalue - пока не используются и вызывают NotImplementedError
    def _get_lvalue_structure_for_arg(self, postfix_expr_ctx: KumirParser.PostfixExpressionContext) -> Tuple[Optional[Any], Optional[Any]]:
        self.visitor.error_handler.not_implemented_error("Метод _get_lvalue_structure_for_arg не реализован.", postfix_expr_ctx)
        return None, None

    def _get_lvalue_for_assignment(self, ctx: KumirParser.LvalueContext) -> Tuple[Optional[Any], Optional[Any]]:
        self.visitor.error_handler.not_implemented_error("Метод _get_lvalue_for_assignment не реализован.", ctx)
        return None, None

    def _get_lvalue_for_read(self, ctx: KumirParser.LvalueContext) -> Tuple[Optional[Any], Optional[Any]]:
        self.visitor.error_handler.not_implemented_error("Метод _get_lvalue_for_read не реализован.", ctx)
        return None, None