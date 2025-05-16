# expression_evaluator.py
# Этот файл будет содержать логику вычисления выражений для интерпретатора КуМира. 

from __future__ import annotations
import sys
import operator
from .generated.KumirLexer import KumirLexer
from .generated.KumirParser import KumirParser
from .kumir_exceptions import KumirEvalError, KumirSyntaxError
from .kumir_datatypes import KumirTableVar
from antlr4 import InputStream, CommonTokenStream # type: ignore
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from antlr4.tree.Tree import TerminalNode

if TYPE_CHECKING:
    from pyrobot.backend.kumir_interpreter.interpreter import KumirInterpreterVisitor # Для type hinting

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
    def __init__(self, visitor):
        self.visitor = visitor

    def _get_value(self, value):
        if isinstance(value, dict) and 'value' in value and 'type' in value:
            return value['value']
        return value

    def _handle_type_promotion_for_comparison(self, left, right, ctx):
        if left is None or right is None:
            raise KumirEvalError(
                f"Строка ~{ctx.start.line}: Нельзя сравнивать с неинициализированным значением.",
                ctx.start.line,
                ctx.start.column
            )
        is_left_int = isinstance(left, int)
        is_left_float = isinstance(left, float)
        is_right_int = isinstance(right, int)
        is_right_float = isinstance(right, float)
        if is_left_int and is_right_float:
            print(f"[DEBUG][TypePromoEE] Promoting left operand {left} (int) to float for comparison with {right} (float)", file=sys.stderr)
            return float(left), right
        if is_left_float and is_right_int:
            print(f"[DEBUG][TypePromoEE] Promoting right operand {right} (int) to float for comparison with {left} (float)", file=sys.stderr)
            return left, float(right)
        return left, right

    def _check_numeric(self, value, operation_name):
        print(f"[DEBUG][_check_numericEE] ENTERED. Op: {operation_name}. Value initial type: {type(value).__name__}.", file=sys.stderr)
        processed_value = self._get_value(value)
        print(f"[DEBUG][_check_numericEE] Value after _get_value for op '{operation_name}': {repr(processed_value)} (type: {type(processed_value).__name__})", file=sys.stderr)
        if processed_value is None:
            print(f"[DEBUG][_check_numericEE] Raising KumirEvalError: processed_value is None for op '{operation_name}'", file=sys.stderr)
            raise KumirEvalError(f"Попытка использовать неинициализированное значение в операции '{operation_name}'")
        if not isinstance(processed_value, (int, float)):
            print(f"[DEBUG][_check_numericEE] Raising KumirEvalError: not int/float for op '{operation_name}'. Value: {repr(processed_value)}, Type: {type(processed_value).__name__}", file=sys.stderr)
            raise KumirEvalError(f"Операция '{operation_name}' не применима к нечисловому типу {type(processed_value).__name__}.")
        return processed_value

    def _check_logical(self, value, operation_name):
        processed_value = self._get_value(value)
        if processed_value is None:
            raise KumirEvalError(f"Попытка использовать неинициализированное значение в операции '{operation_name}'")
        if not isinstance(processed_value, bool):
            if not isinstance(processed_value, int):
                 raise KumirEvalError(f"Операция '{operation_name}' не применима к нелогическому типу {type(processed_value).__name__}.")
        return processed_value

    def _check_comparable(self, value, operation_name):
        processed_value = self._get_value(value)
        if processed_value is None:
            raise KumirEvalError(f"Попытка использовать неинициализированное значение в операции '{operation_name}'")
        if not isinstance(processed_value, (int, float, str, bool)):
            raise KumirEvalError(f"Операция '{operation_name}' не применима к типу {type(processed_value).__name__}.")
        return processed_value
        
    def _perform_binary_operation(self, left_val, right_val, op_token, expression_node_ctx):
        op_text = op_token.text
        op_type = op_token.type
        print(f"[DEBUG][PBO_OP_DETAILSEE] op_text='{op_text}', op_type_val={op_type}, KumirLexer.DIV={KumirLexer.DIV}", file=sys.stderr)
        checked_left_val = self._check_numeric(left_val, op_text)
        checked_right_val = self._check_numeric(right_val, op_text)
        operation_func = ARITHMETIC_OPS.get(op_type)
        print(f"[DEBUG][PBO_OP_DETAILSEE] op_text='{op_text}', op_type_val={op_type}, operation_func_found={bool(operation_func)}", file=sys.stderr)
        if not operation_func:
            if op_type == KumirLexer.MOD or op_type == KumirLexer.DIV:
                 print(f"[DEBUG][PBO_OP_DETAILSEE] Keyword '{op_text}' was not found in ARITHMETIC_OPS. Raising error as expected.", file=sys.stderr)
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Неизвестный или неподдерживаемый арифметический оператор: {op_text} в выражении '{expression_node_ctx.getText()}'")
        if op_type == KumirLexer.DIV:
            if checked_right_val == 0:
                raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Деление на ноль в выражении '{expression_node_ctx.getText()}'")
            return float(checked_left_val) / float(checked_right_val)
        try:
            result = operation_func(checked_left_val, checked_right_val)
            return result
        except TypeError as e:
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Ошибка типа при выполнении операции '{op_text}' ({type(checked_left_val).__name__} {op_text} {type(checked_right_val).__name__}) в выражении '{expression_node_ctx.getText()}': {e}")
        except ZeroDivisionError:
             raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Ошибка деления на ноль или некорректная операция со степенью при вычислении '{op_text}' в выражении '{expression_node_ctx.getText()}'")
        except OverflowError:
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Переполнение при вычислении '{op_text}' в выражении '{expression_node_ctx.getText()}'")
        except Exception as e: 
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Ошибка при вычислении '{op_text}' в выражении '{expression_node_ctx.getText()}': {e}")

    def visitLiteral(self, ctx: KumirParser.LiteralContext):
        print(f"[DEBUG][visitLiteralEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        if ctx.INTEGER(): # Token INTEGER
            print(f"[DEBUG][visitLiteralEE] INTEGER: {ctx.INTEGER().getText()}", file=sys.stderr)
            return int(ctx.INTEGER().getText())
        elif ctx.REAL():    # Token REAL
            print(f"[DEBUG][visitLiteralEE] REAL: {ctx.REAL().getText()}", file=sys.stderr)
            return float(ctx.REAL().getText().replace(',', '.'))
        elif ctx.STRING():  # Token STRING
            print(f"[DEBUG][visitLiteralEE] STRING: {ctx.STRING().getText()}", file=sys.stderr)
            text = ctx.STRING().getText()
            if len(text) >= 2: # Строка должна иметь хотя бы кавычки
                quote_char = text[0]
                if text.endswith(quote_char) and (quote_char == '"' or quote_char == "'"):
                    core_text = text[1:-1]
                    if quote_char == '"':
                        return core_text.replace('""', '"') # Заменяем "" на "
                    elif quote_char == "'":
                        return core_text.replace("''", "'") # Заменяем '' на '
            # Если структура некорректна (например, непарные кавычки)
            # или это не стандартная строка в кавычках, это ошибка.
            # Однако, ANTLR должен был бы поймать синтаксически неверные строки раньше.
            # Если мы сюда попали с чем-то странным, безопаснее вызвать ошибку.
            print(f"[WARNING][visitLiteralEE] Potentially malformed STRING literal: {text}", file=sys.stderr)
            # Возвращаем текст без крайних символов, если они одинаковые кавычки, иначе целиком
            # Это запасной вариант, если предыдущие проверки не сработали, но он не очень надежен.
            if len(text) >= 2 and text[0] == text[-1] and (text[0] == '"' or text[0] == "'"):
                 return text[1:-1] # Очень упрощенное запасное поведение, может быть неверным для сложных случаев
            return text # Худший случай - вернуть как есть, или лучше ошибка

        elif ctx.CHAR_LITERAL(): # Token CHAR_LITERAL
            print(f"[DEBUG][visitLiteralEE] CHAR_LITERAL: {ctx.CHAR_LITERAL().getText()}", file=sys.stderr)
            text = ctx.CHAR_LITERAL().getText()
            if len(text) == 3 and text[0] == "'" and text[-1] == "'": # e.g. 'A'
                return text[1]
            elif text == "''''": # e.g. '''' for single quote char
                return "'"
            # По грамматике КуМира, символьный литерал - это один символ в одинарных кавычках.
            # Либо две одинарные кавычки для представления символа одинарной кавычки.
            # Все остальное должно быть синтаксической ошибкой, пойманной парсером.
            # Если мы здесь с чем-то другим, это неожиданно.
            raise KumirEvalError(f"Некорректный или неподдерживаемый символьный литерал: {text}", ctx.start.line, ctx.start.column if ctx.start else -1)
        elif ctx.TRUE():    # Token TRUE
            print(f"[DEBUG][visitLiteralEE] TRUE", file=sys.stderr)
            return True
        elif ctx.FALSE():   # Token FALSE
            print(f"[DEBUG][visitLiteralEE] FALSE", file=sys.stderr)
            return False
        elif ctx.NEWLINE_CONST(): # Token NEWLINE_CONST ('нс')
            print(f"[DEBUG][visitLiteralEE] NEWLINE_CONST (нс)", file=sys.stderr)
            return '\n'
        elif ctx.colorLiteral():
            color_node = ctx.colorLiteral()
            print(f"[DEBUG][visitLiteralEE] Delegating to colorLiteral: {color_node.getText()}", file=sys.stderr)
            if hasattr(self, 'visitColorLiteral'):
                 return self.visitColorLiteral(color_node)
            else:
                color_text = color_node.getText()
                print(f"[WARNING][visitLiteralEE] visitColorLiteral not implemented in EE, returning text: {color_text}", file=sys.stderr)
                return color_text
        else:
            print(f"[ERROR][visitLiteralEE] Unknown literal type: {ctx.getText()}", file=sys.stderr)
            raise KumirEvalError(f"Неизвестный тип литерала: {ctx.getText()}", ctx.start.line, ctx.start.column if ctx.start else -1)

    def visitColorLiteral(self, ctx: KumirParser.ColorLiteralContext):
        pass # Заглушка

    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext): # KumirParser.PrimaryExpressionContext
        visitor = self.visitor
        print(f"[DEBUG][visitPrimaryExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = None
        if ctx.literal():
            result = self.visitLiteral(ctx.literal())
        elif ctx.qualifiedIdentifier():
            name = ctx.qualifiedIdentifier().getText()
            # --- НАЧАЛО ОТЛАДКИ N В EVALUATOR ---
            if name == 'N':
                print(f"[DEBUG][EE_N_Check_Access] Пытаемся получить значение для 'N' в ExpressionEvaluator.", file=sys.stderr)
            # --- КОНЕЦ ОТЛАДКИ N В EVALUATOR ---
            var_info, _ = visitor.find_variable(name)
            if var_info:
                # --- НАЧАЛО ОТЛАДКИ N В EVALUATOR (ПОСЛЕ ПОИСКА) ---
                if name == 'N':
                    print(f"[DEBUG][EE_N_Check_Value] 'N' найдена в ExpressionEvaluator, var_info['value'] = {var_info['value']}", file=sys.stderr)
                # --- КОНЕЦ ОТЛАДКИ N В EVALUATOR ---
                is_table_access = var_info.get('is_table') and not ctx.parentCtx.LPAREN()
                # Check if it's a direct table access (no indices/args yet, handled by Postfix)
                is_direct_table_ref = (
                    not (hasattr(ctx.parentCtx, 'indexList') and ctx.parentCtx.indexList()) and
                    not (hasattr(ctx.parentCtx, 'argumentList') and ctx.parentCtx.argumentList())
                )

                if is_table_access and is_direct_table_ref:
                    print(f"[DEBUG][visitPrimaryExpressionEE] Returning KumirTableVar object for table: {name}", file=sys.stderr)
                    result = var_info['value'] 
                elif var_info.get('is_table'): # Table name for postfix processing
                    print(f"[DEBUG][visitPrimaryExpressionEE] Returning name for table (to be handled by Postfix): {name}", file=sys.stderr)
                    result = name
                else: # Scalar variable or function/procedure name
                    if callable(var_info.get('value')):
                        result = name
                    else:
                        result = var_info['value']
            else:
                print(f"[DEBUG][visitPrimaryExpressionEE] '{name}' not found as variable, assuming proc/func name.", file=sys.stderr)
                result = name 
        elif ctx.LPAREN():
            # When all expressions are moved, this will be self.visitExpression(ctx.expression())
            result = self.visitExpression(ctx.expression()) 
            print(f"[DEBUG][visitPrimaryExpressionEE] LPAREN expression result: {result}", file=sys.stderr)
        elif ctx.RETURN_VALUE():
            current_scope_dict = visitor.scopes[-1]
            if '__знач__' not in current_scope_dict:
                if len(visitor.scopes) > 1 and '__знач__' in visitor.scopes[-2]:
                    current_scope_dict = visitor.scopes[-2]
            if '__знач__' not in current_scope_dict:
                print(f"[DEBUG][visitPrimaryExpressionEE] '__знач__' not in current scope or caller scope. Current scopes: {visitor.scopes}", file=sys.stderr)
                raise KumirEvalError("Попытка использования неинициализированного возвращаемого значения 'знач'.", ctx.start.line, ctx.start.column)
            result = current_scope_dict['__знач__']
            print(f"[DEBUG][visitPrimaryExpressionEE] RETURN_VALUE (__знач__) result: {repr(result)} from scope: {current_scope_dict is visitor.scopes[-1]}", file=sys.stderr)
        else:
            print(f"[DEBUG][visitPrimaryExpressionEE] Unknown primary expression type: {ctx.getText()}", file=sys.stderr)
            raise KumirEvalError(f"Неизвестный тип первичного выражения: {ctx.getText()}", ctx.start.line, ctx.start.column)
        print(f"[DEBUG][visitPrimaryExpressionEE] Returning: {repr(result)} (type: {type(result)}) for ctx: {ctx.getText()}", file=sys.stderr)
        return result 

    def visitPostfixExpression(self, ctx): # KumirParser.PostfixExpressionContext
        visitor = self.visitor # Ссылка на основной интерпретатор
        print(f"[Enter] visitPostfixExpressionEE for {ctx.getText()}", file=sys.stderr)
        primary_expr_ctx = ctx.primaryExpression()
        if not primary_expr_ctx:
            raise KumirEvalError("Отсутствует primaryExpression в postfixExpression", ctx.start.line, ctx.start.column)

        current_eval_value = self.visitPrimaryExpression(primary_expr_ctx) # self.visitPrimaryExpression (этого класса)
        print(f"[DEBUG][PostfixEE] Primary eval: '{primary_expr_ctx.getText()}' -> {repr(current_eval_value)} (type: {type(current_eval_value).__name__})", file=sys.stderr)

        if len(ctx.children) > 1:
            first_op_token_node = ctx.getChild(1)

            if isinstance(first_op_token_node, TerminalNode) and first_op_token_node.getSymbol().type == KumirLexer.LBRACK:
                if len(ctx.children) < 4 or not (ctx.getChild(2).getRuleIndex() == KumirParser.RULE_indexList and \
                                                 isinstance(ctx.getChild(3), TerminalNode) and \
                                                 ctx.getChild(3).getSymbol().type == KumirLexer.RBRACK):
                    raise KumirSyntaxError(f"Строка {first_op_token_node.getSymbol().line}: Некорректная структура доступа к элементу таблицы после '['.", first_op_token_node.getSymbol().line, first_op_token_node.getSymbol().column)
                
                index_list_ctx = ctx.getChild(2)
                print(f"[DEBUG][PostfixEE] Обработка indexList: {index_list_ctx.getText()}", file=sys.stderr)
                
                table_name_or_value = current_eval_value
                kumir_table_var_obj = None

                if isinstance(table_name_or_value, str):
                    var_info, _ = visitor.find_variable(table_name_or_value)
                    if var_info is None:
                        raise KumirEvalError(f"Строка {primary_expr_ctx.start.line}: Таблица '{table_name_or_value}' не найдена.", primary_expr_ctx.start.line, primary_expr_ctx.start.column)
                    if not var_info['is_table']:
                        raise KumirEvalError(f"Строка {primary_expr_ctx.start.line}: Переменная '{table_name_or_value}' не является таблицей, доступ по индексу невозможен.", primary_expr_ctx.start.line, primary_expr_ctx.start.column)
                    kumir_table_var_obj = var_info['value']
                elif isinstance(table_name_or_value, KumirTableVar):
                    kumir_table_var_obj = table_name_or_value
                else: 
                    raise KumirEvalError(f"Строка {primary_expr_ctx.start.line}: Попытка доступа по индексу к выражению ('{primary_expr_ctx.getText()}'), которое не является таблицей.", primary_expr_ctx.start.line, primary_expr_ctx.start.column)

                if not isinstance(kumir_table_var_obj, KumirTableVar):
                     raise KumirEvalError(f"Строка {primary_expr_ctx.start.line}: Внутренняя ошибка: основа для индексации ('{primary_expr_ctx.getText()}') не является объектом KumirTableVar.", primary_expr_ctx.start.line, primary_expr_ctx.start.column)

                indices = []
                for expr_ctx_idx in index_list_ctx.expression():
                    # Здесь вызов visitor.visit, т.к. visitExpression еще не в этом классе
                    index_val = self.visitExpression(expr_ctx_idx) 
                    index_val_clean = self._get_value(index_val)
                    if not isinstance(index_val_clean, int):
                        raise KumirEvalError(f"Строка {expr_ctx_idx.start.line}: Индекс таблицы должен быть целым числом, получено: {index_val_clean} (тип: {type(index_val_clean).__name__}).", expr_ctx_idx.start.line, expr_ctx_idx.start.column)
                    indices.append(index_val_clean)
                
                indices_tuple = tuple(indices)
                table_display_name = primary_expr_ctx.getText()
                print(f"[DEBUG][PostfixEE] Попытка чтения из таблицы '{table_display_name}' по индексам {indices_tuple}", file=sys.stderr)
                try:
                    current_eval_value = kumir_table_var_obj.get_value(indices_tuple, index_list_ctx)
                    print(f"[DEBUG][PostfixEE] Значение из таблицы '{table_display_name}{indices_tuple}': {repr(current_eval_value)}", file=sys.stderr)
                except KumirEvalError as e:
                     err_line = e.line if hasattr(e, 'line') and e.line is not None else index_list_ctx.start.line
                     err_col = e.column if hasattr(e, 'column') and e.column is not None else index_list_ctx.start.column
                     raise KumirEvalError(f"Ошибка при доступе к элементу таблицы '{table_display_name}': {e.args[0]}", err_line, err_col)
            
            elif isinstance(first_op_token_node, TerminalNode) and first_op_token_node.getSymbol().type == KumirLexer.LPAREN:
                if not isinstance(current_eval_value, str):
                    line = primary_expr_ctx.start.line
                    column = primary_expr_ctx.start.column
                    raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вызова не процедуры/функции (основа вызова: '{primary_expr_ctx.getText()}', тип значения: {type(current_eval_value).__name__})", line, column)
                
                proc_name = current_eval_value
                args = []
                argument_list_ctx = None
                if len(ctx.children) > 2 and ctx.getChild(2).getRuleIndex() == KumirParser.RULE_argumentList:
                    argument_list_ctx = ctx.getChild(2)
                    if argument_list_ctx and argument_list_ctx.expression():
                        # visitArgumentList должен быть методом visitor или ExpressionEvaluator
                        # Если он в visitor, то visitor.visitArgumentList, если в EE, то self.visitArgumentList
                        args = visitor.visit(argument_list_ctx) 
                elif len(ctx.children) == 3 and isinstance(ctx.getChild(2), TerminalNode) and ctx.getChild(2).getSymbol().type == KumirLexer.RPAREN:
                    pass
                else:
                    err_line = first_op_token_node.getSymbol().line
                    raise KumirSyntaxError(f"Строка {err_line}: Некорректная структура вызова процедуры/функции '{proc_name}' после '('.", err_line, first_op_token_node.getSymbol().column)
                
                print(f"[DEBUG][PostfixEE] Вызов процедуры/функции '{proc_name}' с аргументами: {args}", file=sys.stderr)
                
                proc_name_lower = proc_name.lower()
                # Используем visitor.BUILTIN_FUNCTIONS и visitor.procedures
                if proc_name_lower in visitor.BUILTIN_FUNCTIONS:
                    arg_count = len(args)
                    builtin_variants = visitor.BUILTIN_FUNCTIONS[proc_name_lower]
                    if arg_count not in builtin_variants:
                        err_ctx_line = argument_list_ctx.start.line if argument_list_ctx else first_op_token_node.getSymbol().line
                        err_ctx_col = argument_list_ctx.start.column if argument_list_ctx else first_op_token_node.getSymbol().column
                        raise KumirEvalError(f"Строка ~{err_ctx_line}: Неверное количество аргументов для встроенной процедуры '{proc_name}': ожидалось одно из {list(builtin_variants.keys())}, получено {arg_count}", err_ctx_line, err_ctx_col)
                    try:
                        print(f"!!! [Builtin Call PRE EE] Calling '{proc_name_lower}' with args: {repr(args)} (types: {[type(arg) for arg in args]})", flush=True, file=sys.stderr)
                        result_of_call = builtin_variants[arg_count](*args)
                        print(f"!!! [Builtin Call POST EE] '{proc_name_lower}' returned: {repr(result_of_call)} (type: {type(result_of_call)})", flush=True, file=sys.stderr)
                        current_eval_value = result_of_call
                    except Exception as e:
                        err_ctx_line = argument_list_ctx.start.line if argument_list_ctx else first_op_token_node.getSymbol().line
                        err_ctx_col = argument_list_ctx.start.column if argument_list_ctx else first_op_token_node.getSymbol().column
                        if isinstance(e, KumirEvalError):
                             e.line = e.line if hasattr(e, 'line') and e.line is not None else err_ctx_line
                             e.column = e.column if hasattr(e, 'column') and e.column is not None else err_ctx_col
                             raise e
                        raise KumirEvalError(f"Строка ~{err_ctx_line}: Ошибка выполнения встроенной процедуры '{proc_name}': {e}", err_ctx_line, err_ctx_col) # KumirExecutionError -> KumirEvalError
                
                elif proc_name in visitor.procedures:
                    proc_def_ctx = visitor.procedures[proc_name]
                    header = proc_def_ctx.algorithmHeader()
                    params_decl_ctx_list = header.parameterList().parameterDeclaration() if header.parameterList() else []
                    actual_arg_expr_nodes = argument_list_ctx.expression() if argument_list_ctx else []
                    
                    output_params_mapping = []
                    expected_params_info = [] 

                    current_actual_arg_idx = 0
                    for param_decl_node in params_decl_ctx_list:
                        param_type_spec_ctx = param_decl_node.typeSpecifier()
                        # Используем visitor._get_type_info_from_specifier
                        param_base_type_str, param_is_table_decl = visitor._get_type_info_from_specifier(param_type_spec_ctx, param_decl_node.start.line)
                        mode = visitor._get_param_mode(param_decl_node) # Используем visitor._get_param_mode
                        
                        for param_var_item_ctx in param_decl_node.variableList().variableDeclarationItem():
                            param_name_in_proc = param_var_item_ctx.ID().getText()
                            # print(f"[DEBUG_PARAM_MODE_EE] Param: {param_name_in_proc}, Mode: {mode}", file=sys.stderr)
                            expected_params_info.append({
                                'name': param_name_in_proc, 
                                'type': param_base_type_str, 
                                'mode': mode, 
                                'is_table': param_is_table_decl,
                                'decl_ctx': param_var_item_ctx
                            })

                            if mode in ['рез', 'арг рез']:
                                if current_actual_arg_idx < len(actual_arg_expr_nodes):
                                    arg_expr_node_for_output: KumirParser.ExpressionContext = actual_arg_expr_nodes[current_actual_arg_idx]
                                    
                                    # Используем новый метод _get_lvalue_structure_for_arg
                                    lvalue_primary_expr_ctx, lvalue_indices_ctx = self._get_lvalue_structure_for_arg(arg_expr_node_for_output)
                                    # print(f"[DEBUG_LVALUE_STRUCT_EE] For arg '{arg_expr_node_for_output.getText()}': lvalue_primary_expr_ctx is SET, lvalue_indices_ctx is {'SET' if lvalue_indices_ctx else 'None'}", file=sys.stderr)
                                    
                                    if not lvalue_primary_expr_ctx or not lvalue_primary_expr_ctx.qualifiedIdentifier():
                                        err_line = arg_expr_node_for_output.start.line
                                        err_col = arg_expr_node_for_output.start.column
                                        param_display_name = param_var_item_ctx.ID().getText() # Имя параметра из объявления процедуры
                                        raise KumirEvalError(f"Строка {err_line}: Аргумент '{arg_expr_node_for_output.getText()}' для параметра '{param_display_name}' с режимом '{mode}' должен быть переменной или элементом таблицы.", err_line, err_col)

                                    caller_var_name_for_output = lvalue_primary_expr_ctx.getText() # Имя переменной в вызывающем коде
                                    
                                    # print(f"[DEBUG_PRE_APPEND_OPM_EE] Appending to OPM: param_name='{param_name_in_proc}', caller_var='{caller_var_name_for_output}', mode='{mode}'", file=sys.stderr)
                                    output_params_mapping.append({
                                        'param_name_in_proc': param_name_in_proc,
                                        'caller_var_name': caller_var_name_for_output,
                                        'caller_var_primary_ctx': lvalue_primary_expr_ctx,
                                        'caller_var_indices_ctx': lvalue_indices_ctx, # Может быть None
                                        'param_mode': mode
                                    })
                                else: # Недостаточно фактических аргументов
                                    err_line = proc_def_ctx.algorithmHeader().start.line
                                    err_col = proc_def_ctx.algorithmHeader().start.column
                                    param_display_name = param_var_item_ctx.ID().getText()
                                    raise KumirArgumentError(f"Строка {err_line}: Недостаточно аргументов для процедуры '{proc_name}'. Отсутствует аргумент для параметра '{param_display_name}' с режимом '{mode}'.", err_line, err_col)
                            
                            current_actual_arg_idx += 1
                        # print(f"[DEBUG_POST_PARAM_LOOP_EE] OPM after processing all items in param_decl_node '{param_decl_node.getText().replace("\n", " ")}': {output_params_mapping}", file=sys.stderr)
                    
                    num_expected_input_params = len([p for p in expected_params_info if p['mode'] in ['арг', 'арг рез']])
                    if len(args) != num_expected_input_params:
                        raise KumirEvalError(f"Неверное количество аргументов для '{proc_name}': ожидалось {num_expected_input_params} входных, передано {len(args)}.", first_op_token_node.getSymbol().line, first_op_token_node.getSymbol().column)
                    
                    actual_arg_values = args[:num_expected_input_params]
                    actual_arg_values_for_input_params = actual_arg_values[:num_expected_input_params]

                    # Сохраняем данные для _execute_procedure_call
                    visitor.prepare_procedure_call_data = {
                        'args_values_for_input_params': actual_arg_values_for_input_params,
                        'output_params_mapping': output_params_mapping, # Это список словарей
                        'expected_params_info': expected_params_info,
                        'actual_arg_expr_nodes': actual_arg_expr_nodes # Для сообщений об ошибках
                    }
                    # print(f"[DEBUG_FINAL_OPM_EE] Final OPM before setting prepare_procedure_call_data: {output_params_mapping}", file=sys.stderr)

                    # Это место, где мы должны вызвать self.visitor.visit(proc_def_ctx), а не evaluator
                    current_eval_value = visitor.visit(proc_def_ctx) 
                    
                    # Старый блок try...finally, который обрабатывал параметры и возвращал значения локально, УДАЛЕН.
                    # Эта логика теперь полностью перенесена в KumirInterpreterVisitor.visitAlgorithmDefinition (или аналогичный).
                                
                else:
                    raise KumirEvalError(f"Процедура или функция '{proc_name}' не найдена.", primary_expr_ctx.start.line, primary_expr_ctx.start.column)

        print(f"[Exit] visitPostfixExpressionEE for {ctx.getText()} -> returns {repr(current_eval_value)}", file=sys.stderr)
        return current_eval_value

    def visitUnaryExpression(self, ctx): # KumirParser.UnaryExpressionContext
        # --- ПЕРЕМЕЩЕННЫЙ БЛОК ИНИЦИАЛИЗАЦИИ op_type ---
        op_type = None
        if ctx.PLUS(): op_type = KumirLexer.PLUS
        elif ctx.MINUS(): op_type = KumirLexer.MINUS
        elif ctx.NOT(): op_type = KumirLexer.NOT
        # --- КОНЕЦ ПЕРЕМЕЩЕННОГО БЛОКА ---
        
        # visitor = self.visitor # Можно удалить или оставить, если используется где-то еще
        print(f"[DEBUG][visitUnaryExpressionEE] Called for ctx: {ctx.getText()}, op_type determined: {op_type}", file=sys.stderr)
        
        target_node_for_visit = None
        
        if op_type is not None: # Альтернатива: (PLUS | MINUS | NOT) unaryExpression
            # ctx.unaryExpression() возвращает ОДИН дочерний UnaryExpressionContext или None
            unary_child_node = ctx.unaryExpression() 
            if unary_child_node:
                 target_node_for_visit = unary_child_node
            else: # Этого не должно произойти, если есть оператор
                 raise KumirSyntaxError(f"Отсутствует операнд для унарного оператора", ctx.start.line, ctx.start.column)
        
        elif ctx.postfixExpression(): # Альтернатива: postfixExpression
            # ctx.postfixExpression() возвращает ОДИН PostfixExpressionContext или None
            postfix_child_node = ctx.postfixExpression()
            if postfix_child_node:
                target_node_for_visit = postfix_child_node
            else: # Этого не должно произойти
                 raise KumirSyntaxError(f"Отсутствует постфиксное выражение в унарном выражении", ctx.start.line, ctx.start.column)
        else: # Не должно быть других альтернатив по грамматике
            raise KumirSyntaxError(f"Некорректная структура унарного выражения: {ctx.getText()}", ctx.start.line, ctx.start.column)

        if not target_node_for_visit: # Дополнительная проверка на всякий случай
             raise KumirSyntaxError(f"Не удалось определить узел для вычисления в унарном выражении {ctx.getText()}", ctx.start.line, ctx.start.column)

        value = target_node_for_visit.accept(self) # <-- ИСПРАВЛЕНИЕ: Используем accept для dispatch
        print(f"[DEBUG][visitUnaryExpressionEE] Value from sub-expression '{target_node_for_visit.getText()}': {value} (type: {type(value)})", file=sys.stderr)

        # --- ВОССТАНОВЛЕННЫЙ БЛОК ПРИМЕНЕНИЯ ОПЕРАТОРА ---
        if op_type == KumirLexer.PLUS: # Унарный плюс
            result = self._check_numeric(value, "унарный +")
            # Унарный плюс не меняет значение числового типа
        elif op_type == KumirLexer.MINUS: # Унарный минус
            result = self._check_numeric(value, "унарный -")
            result = -result
        elif op_type == KumirLexer.NOT: # Логическое НЕ
            result = self._check_logical(value, "не")
            result = not result
        else: # Нет унарного оператора, op_type is None
            result = value # Просто возвращаем значение дочернего узла (postfixExpression)
        # --- КОНЕЦ ВОССТАНОВЛЕННОГО БЛОКА ---

        print(f"[DEBUG][visitUnaryExpressionEE] Returning: {result} (type: {type(result)}) for ctx: {ctx.getText()}", file=sys.stderr)
        return result

    def visitPowerExpression(self, ctx): # KumirParser.PowerExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitPowerExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        
        unary_expressions_or_obj = ctx.unaryExpression()
        first_unary_expr_ctx = None
        exponent_ctx = None

        if isinstance(unary_expressions_or_obj, list):
            if not unary_expressions_or_obj:
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Отсутствует базовое выражение в выражении степени.")
            first_unary_expr_ctx = unary_expressions_or_obj[0]
            if len(unary_expressions_or_obj) > 1:
                exponent_ctx = unary_expressions_or_obj[1]
        elif unary_expressions_or_obj:
            first_unary_expr_ctx = unary_expressions_or_obj
        else:
            raise KumirEvalError(f"Строка ~{ctx.start.line}: Неожиданная структура для unaryExpression в powerExpression.")

        result = self.visitUnaryExpression(first_unary_expr_ctx) # self.visitUnaryExpression
        print(f"[DEBUG][visitPowerExpressionEE] Received from first unaryExpression: {result} (type: {type(result)})", file=sys.stderr)

        if exponent_ctx:
            exponent = self.visitUnaryExpression(exponent_ctx) # self.visitUnaryExpression
            print(f"[DEBUG][visitPowerExpressionEE] Received for exponent: {exponent} (type: {type(exponent)})", file=sys.stderr)
            
            if not isinstance(result, (int, float)) or not isinstance(exponent, (int, float)):
                raise KumirEvalError(
                    f"Строка ~{ctx.start.line}: Операция возведения в степень применима только к числовым типам (получены {type(result).__name__} и {type(exponent).__name__})",
                    ctx.start.line,
                    ctx.start.column
                )
            try:
                result = result ** exponent
            except TypeError:
                 raise KumirEvalError(
                    f"Строка ~{ctx.start.line}: Ошибка типа при возведении в степень: {type(result).__name__} ** {type(exponent).__name__}",
                    ctx.start.line,
                    ctx.start.column
                )
        print(f"[DEBUG][visitPowerExpressionEE] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result
        
    def visitMultiplicativeExpression(self, ctx): # KumirParser.MultiplicativeExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitMultiplicativeExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visitPowerExpression(ctx.powerExpression(0)) # self.visitPowerExpression
        print(f"[DEBUG][visitMultiplicativeExpressionEE] Initial result from left powerExpression: {result} (type: {type(result)})", file=sys.stderr)

        for i in range(len(ctx.powerExpression()) - 1):
            op_node = ctx.getChild(2 * i + 1)
            op_token = op_node.getSymbol()
            op_text = op_token.text
            
            right_operand_ctx = ctx.powerExpression(i + 1)
            right_operand = self.visitPowerExpression(right_operand_ctx) # self.visitPowerExpression
            print(f"[DEBUG][visitMultiplicativeExpressionEE] Right operand for '{op_text}': {right_operand} (type: {type(right_operand)})", file=sys.stderr)
            
            if op_token.type in ARITHMETIC_OPS: # Только для +, -, *, /, ^. div/mod как функции тут не будут.
                result = self._perform_binary_operation(result, right_operand, op_token, ctx)
            else:
                # Этот блок не должен достигаться для Ключевых слов DIV/MOD, так как они обрабатываются как функции через Postfix.
                # Если грамматика допускает другие операторы здесь, их нужно обработать или выдать ошибку.
                print(f"[WARN][visitMultiplicativeExpressionEE] Operator '{op_text}' (type {op_token.type}) not in ARITHMETIC_OPS and not handled as function. Behavior undefined.", file=sys.stderr)
                # Пока что будем считать это ошибкой, если это не стандартный арифметический оператор
                raise KumirEvalError(f"Неподдерживаемый оператор '{op_text}' в multiplicativeExpression")

            print(f"[DEBUG][visitMultiplicativeExpressionEE] Result after '{op_text}': {result} (type: {type(result)})", file=sys.stderr)

        print(f"[Exit] visitMultiplicativeExpressionEE for '{ctx.getText()}' -> returns {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitAdditiveExpression(self, ctx): # KumirParser.AdditiveExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitAdditiveExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visitMultiplicativeExpression(ctx.multiplicativeExpression(0)) # self.visitMultiplicativeExpression
        print(f"[DEBUG][visitAdditiveExpressionEE] Initial result from left multExpression: {result} (type: {type(result)})", file=sys.stderr)

        for i in range(len(ctx.multiplicativeExpression()) - 1):
            op_node = ctx.getChild(2 * i + 1)
            op_token = op_node.getSymbol()
            op_text = op_token.text
            
            right_operand_ctx = ctx.multiplicativeExpression(i + 1)
            right_operand = self.visitMultiplicativeExpression(right_operand_ctx) # self.visitMultiplicativeExpression
            print(f"[DEBUG][visitAdditiveExpressionEE] Right operand for '{op_text}': {right_operand} (type: {type(right_operand)})", file=sys.stderr)

            result = self._perform_binary_operation(result, right_operand, op_token, ctx)
            print(f"[DEBUG][visitAdditiveExpressionEE] Result after '{op_text}': {result} (type: {type(result)})", file=sys.stderr)
            
        print(f"[Exit] visitAdditiveExpressionEE for '{ctx.getText()}' -> returns {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitRelationalExpression(self, ctx): # KumirParser.RelationalExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitRelationalExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visitAdditiveExpression(ctx.additiveExpression(0)) # self.visitAdditiveExpression
        print(f"[DEBUG][visitRelationalExpressionEE] Received from first additiveExpression: {result} (type: {type(result)})", file=sys.stderr)

        if len(ctx.additiveExpression()) > 1:
            op_text = ctx.getChild(1).getText() # op_text это <, >, <=, >=
            op_token = ctx.getChild(1).getSymbol() # Это TerminalNodeImpl, получаем токен
            
            right_operand_ctx = ctx.additiveExpression(1)
            right_operand = self.visitAdditiveExpression(right_operand_ctx) # self.visitAdditiveExpression
            print(f"[DEBUG][visitRelationalExpressionEE] Received for relational's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
            
            promoted_left, promoted_right = self._handle_type_promotion_for_comparison(result, right_operand, ctx)

            # Используем COMPARISON_OPS
            op_func = COMPARISON_OPS.get(op_token.type)
            if op_func:
                result = op_func(promoted_left, promoted_right)
            else:
                # Этого не должно произойти, если грамматика верна
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Неизвестный оператор отношения: {op_text}", ctx.start.line, ctx.start.column)
            print(f"[DEBUG][visitRelationalExpressionEE] Result after '{op_text}': {result}", file=sys.stderr)

        print(f"[DEBUG][visitRelationalExpressionEE] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitEqualityExpression(self, ctx): # KumirParser.EqualityExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitEqualityExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visitRelationalExpression(ctx.relationalExpression(0)) # self.visitRelationalExpression
        print(f"[DEBUG][visitEqualityExpressionEE] Received from first relationalExpression: {result} (type: {type(result)})", file=sys.stderr)

        if len(ctx.relationalExpression()) > 1:
            op_text = ctx.getChild(1).getText() # = или <>
            op_token = ctx.getChild(1).getSymbol()

            right_operand_ctx = ctx.relationalExpression(1)
            right_operand = self.visitRelationalExpression(right_operand_ctx) # self.visitRelationalExpression
            print(f"[DEBUG][visitEqualityExpressionEE] Received for equality's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
            
            promoted_left, promoted_right = self._handle_type_promotion_for_comparison(result, right_operand, ctx)
            
            op_func = COMPARISON_OPS.get(op_token.type)
            if op_func:
                result = op_func(promoted_left, promoted_right)
            else:
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Неизвестный оператор сравнения: {op_text}", ctx.start.line, ctx.start.column)
            print(f"[DEBUG][visitEqualityExpressionEE] Result after comparison '{op_text}': {result}", file=sys.stderr)
            
        print(f"[DEBUG][visitEqualityExpressionEE] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitLogicalAndExpression(self, ctx): # KumirParser.LogicalAndExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitLogicalAndExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visitEqualityExpression(ctx.equalityExpression(0)) # self.visitEqualityExpression
        print(f"[DEBUG][visitLogicalAndExpressionEE] Received from first equalityExpression: {result} (type: {type(result)})", file=sys.stderr)
        
        # Проверяем, нужно ли вычислять дальше (short-circuit evaluation for AND)
        # Если result уже False (или 0), то дальше можно не идти.
        # Но для полноты и логгирования пройдемся, если есть операторы.
        # КуМир, вероятно, делает полное вычисление.

        if len(ctx.equalityExpression()) > 1:
            op_token_type = KumirLexer.AND # Должен быть 'И'
            op_func = LOGICAL_OPS.get(op_token_type)
            if not op_func:
                raise KumirEvalError("Внутренняя ошибка: операция AND не найдена в LOGICAL_OPS")

            for i in range(1, len(ctx.equalityExpression())):
                # Перед вычислением правого операнда для 'И', проверим левый.
                # Если result (левый операнд) уже False, то результат всего выражения 'И' будет False.
                # В КуМире обычно полное вычисление, поэтому будем вычислять правый операнд всегда.
                # checked_left = self._check_logical(result, "И") # Проверим тип левого операнда
                # if not bool(checked_left): # Short-circuit
                #     result = False
                #     break

                right_operand_ctx = ctx.equalityExpression(i)
                right_operand = self.visitEqualityExpression(right_operand_ctx) # self.visitEqualityExpression
                print(f"[DEBUG][visitLogicalAndExpressionEE] Received for AND's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
                
                # Проверка типов перед операцией
                # _check_logical теперь возвращает обработанное значение (например, int в bool если нужно было бы)
                # Но Python `and` сам справится с bool/int.
                # Просто убедимся, что это не строки или что-то неожиданное.
                if not (isinstance(result, (bool, int)) and isinstance(right_operand, (bool, int))):
                    raise KumirEvalError(
                        f"Строка ~{ctx.start.line}: Ошибка типа: операция 'И' не применима к типам {type(result).__name__} и {type(right_operand).__name__}",
                        ctx.start.line,
                        ctx.start.column
                    )
                result = op_func(bool(result), bool(right_operand)) # Приводим к bool для консистентности
                print(f"[DEBUG][visitLogicalAndExpressionEE] Result after AND: {result}", file=sys.stderr)

        print(f"[DEBUG][visitLogicalAndExpressionEE] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitLogicalOrExpression(self, ctx): # KumirParser.LogicalOrExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitLogicalOrExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visitLogicalAndExpression(ctx.logicalAndExpression(0)) # self.visitLogicalAndExpression
        print(f"[DEBUG][visitLogicalOrExpressionEE] Received from first logicalAndExpression: {result} (type: {type(result)})", file=sys.stderr)

        if len(ctx.logicalAndExpression()) > 1:
            op_token_type = KumirLexer.OR # Должен быть 'ИЛИ'
            op_func = LOGICAL_OPS.get(op_token_type)
            if not op_func:
                raise KumirEvalError("Внутренняя ошибка: операция OR не найдена в LOGICAL_OPS")

            for i in range(1, len(ctx.logicalAndExpression())):
                # checked_left = self._check_logical(result, "ИЛИ")
                # if bool(checked_left): # Short-circuit for OR
                #     result = True
                #     break
                    
                right_operand_ctx = ctx.logicalAndExpression(i)
                right_operand = self.visitLogicalAndExpression(right_operand_ctx) # self.visitLogicalAndExpression
                print(f"[DEBUG][visitLogicalOrExpressionEE] Received for OR's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
                
                if not (isinstance(result, (bool, int)) and isinstance(right_operand, (bool, int))):
                    raise KumirEvalError(
                        f"Строка ~{ctx.start.line}: Ошибка типа: операция 'ИЛИ' не применима к типам {type(result).__name__} и {type(right_operand).__name__}",
                        ctx.start.line,
                        ctx.start.column
                    )
                result = op_func(bool(result), bool(right_operand))
                print(f"[DEBUG][visitLogicalOrExpressionEE] Result after OR: {result}", file=sys.stderr)
        
        print(f"[DEBUG][visitLogicalOrExpressionEE] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitExpression(self, ctx): # KumirParser.ExpressionContext
        # visitor = self.visitor
        print(f"[DEBUG][visitExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visitLogicalOrExpression(ctx.logicalOrExpression()) # self.visitLogicalOrExpression
        print(f"[DEBUG][visitExpressionEE] Received from visitLogicalOrExpression: {result} (type: {type(result)})", file=sys.stderr)
        print(f"[DEBUG][visitExpressionEE] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result 

    def _get_lvalue_structure_for_arg(self, expr_ctx: KumirParser.ExpressionContext) -> \
            tuple[KumirParser.PrimaryExpressionContext | None, KumirParser.IndexListContext | None]:
        """
        Разбирает ExpressionContext, чтобы найти нижележащие PrimaryExpressionContext (для имени переменной/таблицы)
        и IndexListContext (для индексов таблицы). Не производит полного вычисления.
        Возвращает (PrimaryExpressionContext | None, IndexListContext | None).
        """
        # print(f"[DEBUG][GetLValueStruct] ENTER for expr: {expr_ctx.getText()}", file=sys.stderr)

        current_ctx = expr_ctx
        # Спуск по дереву выражения до UnaryExpressionContext
        # Этот путь должен соответствовать грамматике и порядку разбора в visitXExpression методах
        if hasattr(current_ctx, 'logicalOrExpression') and current_ctx.logicalOrExpression():
            current_ctx = current_ctx.logicalOrExpression()
            if hasattr(current_ctx, 'logicalAndExpression') and current_ctx.logicalAndExpression() and len(current_ctx.logicalAndExpression()) > 0:
                current_ctx = current_ctx.logicalAndExpression(0)
                if hasattr(current_ctx, 'equalityExpression') and current_ctx.equalityExpression() and len(current_ctx.equalityExpression()) > 0:
                    current_ctx = current_ctx.equalityExpression(0)
                    if hasattr(current_ctx, 'relationalExpression') and current_ctx.relationalExpression() and len(current_ctx.relationalExpression()) > 0:
                        current_ctx = current_ctx.relationalExpression(0)
                        if hasattr(current_ctx, 'additiveExpression') and current_ctx.additiveExpression() and len(current_ctx.additiveExpression()) > 0:
                            current_ctx = current_ctx.additiveExpression(0)
                            print(f"[DEBUG_LVALUE_TYPES] Path: after add(0): current_ctx type = {type(current_ctx).__name__}", file=sys.stderr)
                            if hasattr(current_ctx, 'multiplicativeExpression') and current_ctx.multiplicativeExpression() and len(current_ctx.multiplicativeExpression()) > 0:
                                current_ctx = current_ctx.multiplicativeExpression(0) 
                                print(f"[DEBUG_LVALUE_TYPES] Path: after mult(0): current_ctx type = {type(current_ctx).__name__}", file=sys.stderr)
                                if hasattr(current_ctx, 'powerExpression') and current_ctx.powerExpression() and len(current_ctx.powerExpression()) > 0:
                                    # current_ctx здесь MultiplicativeExpressionContext, его powerExpression() -> list[PowerExpressionContext]
                                    power_expr_as_list_from_mult = current_ctx.powerExpression()
                                    print(f"[DEBUG_LVALUE_TYPES] Path: power_expr_as_list_from_mult ({type(power_expr_as_list_from_mult).__name__}), len={len(power_expr_as_list_from_mult)}", file=sys.stderr)
                                    current_ctx = power_expr_as_list_from_mult[0] # current_ctx теперь PowerExpressionContext
                                    print(f"[DEBUG_LVALUE_TYPES] Path: current_ctx after power_expr_as_list_from_mult[0] is {type(current_ctx).__name__}", file=sys.stderr)
                                    
                                    # unaryExpression() у PowerExpressionContext возвращает список UnaryExpressionContext
                                    unary_expressions_list = current_ctx.unaryExpression() 
                                    print(f"[DEBUG_LVALUE_TYPES] Path: unary_expressions_list from PowerExprCtx is {type(unary_expressions_list).__name__}", file=sys.stderr)
                                    if isinstance(unary_expressions_list, list): # Явная проверка, что это список
                                        print(f"[DEBUG_LVALUE_TYPES] Path: unary_expressions_list IS a list, len={len(unary_expressions_list)}", file=sys.stderr)
                                        if unary_expressions_list: # Проверка, что список не пуст
                                            current_ctx = unary_expressions_list[0] # current_ctx теперь UnaryExpressionContext
                                            print(f"[DEBUG_LVALUE_TYPES] Path: current_ctx after unary_expressions_list[0] is {type(current_ctx).__name__}", file=sys.stderr)
                                        else:
                                            # Список унарных выражений пуст
                                            print(f"[DEBUG_LVALUE_TYPES] Path: unary_expressions_list is empty for: {expr_ctx.getText()}", file=sys.stderr)
                                            return None, None
                                    elif isinstance(unary_expressions_list, KumirParser.UnaryExpressionContext): # Если вдруг вернулся один объект
                                        print(f"[DEBUG_LVALUE_TYPES] Path: unary_expressions_list IS a single UnaryExpressionContext", file=sys.stderr)
                                        current_ctx = unary_expressions_list # current_ctx теперь UnaryExpressionContext
                                    else:
                                        # Неожиданный тип для unary_expressions_list
                                        print(f"[DEBUG_LVALUE_TYPES] Path: unary_expressions_list is UNEXPECTED TYPE {type(unary_expressions_list).__name__} for: {expr_ctx.getText()}", file=sys.stderr)
                                        return None, None                                           
                                else:
                                    # print(f"[DEBUG][GetLValueStruct] No powerExpression in multExpression for: {expr_ctx.getText()}", file=sys.stderr)
                                    return None, None
                            else:
                                # print(f"[DEBUG][GetLValueStruct] No multExpression in addExpression for: {expr_ctx.getText()}", file=sys.stderr)
                                return None, None
                        else:
                            # print(f"[DEBUG][GetLValueStruct] No addExpression in relExpression for: {expr_ctx.getText()}", file=sys.stderr)
                            return None, None
                    else:
                        # print(f"[DEBUG][GetLValueStruct] No relExpression in eqExpression for: {expr_ctx.getText()}", file=sys.stderr)
                        return None, None
                else:
                    # print(f"[DEBUG][GetLValueStruct] No eqExpression in logAndExpression for: {expr_ctx.getText()}", file=sys.stderr)
                    return None, None
            else:
                # print(f"[DEBUG][GetLValueStruct] No logAndExpression in logOrExpression for: {expr_ctx.getText()}", file=sys.stderr)
                return None, None
        else:
            # print(f"[DEBUG][GetLValueStruct] Not a standard expression structure starting with logicalOr: {expr_ctx.getText()}", file=sys.stderr)
            return None, None

        if not isinstance(current_ctx, KumirParser.UnaryExpressionContext):
            # print(f"[DEBUG][GetLValueStruct] Expected UnaryExpressionContext, got {type(current_ctx).__name__} for: {expr_ctx.getText()}", file=sys.stderr)
            return None, None

        unary_expr_ctx = current_ctx
        primary_expr_ctx_candidate = None
        index_list_ctx_candidate = None

        if unary_expr_ctx.postfixExpression():
            postfix_expr_ctx = unary_expr_ctx.postfixExpression()
            primary_expr_ctx_candidate = postfix_expr_ctx.primaryExpression()
            if len(postfix_expr_ctx.children) > 1 and hasattr(postfix_expr_ctx, 'indexList') and postfix_expr_ctx.indexList():
                 op_token_node = postfix_expr_ctx.getChild(1)
                 if isinstance(op_token_node, TerminalNode) and op_token_node.getSymbol().type == KumirLexer.LBRACK:
                    index_list_ctx_candidate = postfix_expr_ctx.indexList()
        elif unary_expr_ctx.primaryExpression():
            primary_expr_ctx_candidate = unary_expr_ctx.primaryExpression()
            index_list_ctx_candidate = None
        else:
            # print(f"[DEBUG][GetLValueStruct] UnaryExpression has neither Postfix nor Primary for: {expr_ctx.getText()}", file=sys.stderr)
            return None, None

        if primary_expr_ctx_candidate and \
           primary_expr_ctx_candidate.LPAREN() and \
           primary_expr_ctx_candidate.expression() and \
           primary_expr_ctx_candidate.RPAREN():
            # print(f"[DEBUG][GetLValueStruct] Recursing for parenthesized primary: {primary_expr_ctx_candidate.expression().getText()}", file=sys.stderr)
            inner_primary, inner_indices = self._get_lvalue_structure_for_arg(primary_expr_ctx_candidate.expression())
            if inner_indices is not None and index_list_ctx_candidate is None:
                # print(f"[DEBUG][GetLValueStruct] Parenthesized expression was already indexed: {primary_expr_ctx_candidate.expression().getText()}", file=sys.stderr)
                return inner_primary, inner_indices
            # print(f"[DEBUG][GetLValueStruct] Using inner_primary '{inner_primary.getText() if inner_primary else 'None'}' and outer_indices '{index_list_ctx_candidate.getText() if index_list_ctx_candidate else 'None'}'", file=sys.stderr)
            return inner_primary, index_list_ctx_candidate
        
        # print(f"[DEBUG][GetLValueStruct] EXIT for {expr_ctx.getText()}. Primary: {primary_expr_ctx_candidate.getText() if primary_expr_ctx_candidate else 'None'}, Indices: {index_list_ctx_candidate.getText() if index_list_ctx_candidate else 'None'}", file=sys.stderr)
        return primary_expr_ctx_candidate, index_list_ctx_candidate

    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext): # KumirParser.PrimaryExpressionContext
        visitor = self.visitor
        print(f"[DEBUG][visitPrimaryExpressionEE] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = None
        if ctx.literal():
            result = self.visitLiteral(ctx.literal())
        elif ctx.qualifiedIdentifier():
            name = ctx.qualifiedIdentifier().getText()
            # --- НАЧАЛО ОТЛАДКИ N В EVALUATOR ---
            if name == 'N':
                print(f"[DEBUG][EE_N_Check_Access] Пытаемся получить значение для 'N' в ExpressionEvaluator.", file=sys.stderr)
            # --- КОНЕЦ ОТЛАДКИ N В EVALUATOR ---
            var_info, _ = visitor.find_variable(name)
            if var_info:
                # --- НАЧАЛО ОТЛАДКИ N В EVALUATOR (ПОСЛЕ ПОИСКА) ---
                if name == 'N':
                    print(f"[DEBUG][EE_N_Check_Value] 'N' найдена в ExpressionEvaluator, var_info['value'] = {var_info['value']}", file=sys.stderr)
                # --- КОНЕЦ ОТЛАДКИ N В EVALUATOR ---
                is_table_access = var_info.get('is_table') and not ctx.parentCtx.LPAREN()
                # Check if it's a direct table access (no indices/args yet, handled by Postfix)
                is_direct_table_ref = (
                    not (hasattr(ctx.parentCtx, 'indexList') and ctx.parentCtx.indexList()) and
                    not (hasattr(ctx.parentCtx, 'argumentList') and ctx.parentCtx.argumentList())
                )

                if is_table_access and is_direct_table_ref:
                    print(f"[DEBUG][visitPrimaryExpressionEE] Returning KumirTableVar object for table: {name}", file=sys.stderr)
                    result = var_info['value'] 
                elif var_info.get('is_table'): # Table name for postfix processing
                    print(f"[DEBUG][visitPrimaryExpressionEE] Returning name for table (to be handled by Postfix): {name}", file=sys.stderr)
                    result = name
                else: # Scalar variable or function/procedure name
                    if callable(var_info.get('value')):
                        result = name
                    else:
                        result = var_info['value']
            else:
                print(f"[DEBUG][visitPrimaryExpressionEE] '{name}' not found as variable, assuming proc/func name.", file=sys.stderr)
                result = name 
        elif ctx.LPAREN():
            # When all expressions are moved, this will be self.visitExpression(ctx.expression())
            result = self.visitExpression(ctx.expression()) 
            print(f"[DEBUG][visitPrimaryExpressionEE] LPAREN expression result: {result}", file=sys.stderr)
        elif ctx.RETURN_VALUE():
            current_scope_dict = visitor.scopes[-1]
            if '__знач__' not in current_scope_dict:
                if len(visitor.scopes) > 1 and '__знач__' in visitor.scopes[-2]:
                    current_scope_dict = visitor.scopes[-2]
            if '__знач__' not in current_scope_dict:
                print(f"[DEBUG][visitPrimaryExpressionEE] '__знач__' not in current scope or caller scope. Current scopes: {visitor.scopes}", file=sys.stderr)
                raise KumirEvalError("Попытка использования неинициализированного возвращаемого значения 'знач'.", ctx.start.line, ctx.start.column)
            result = current_scope_dict['__знач__']
            print(f"[DEBUG][visitPrimaryExpressionEE] RETURN_VALUE (__знач__) result: {repr(result)} from scope: {current_scope_dict is visitor.scopes[-1]}", file=sys.stderr)
        else:
            print(f"[DEBUG][visitPrimaryExpressionEE] Unknown primary expression type: {ctx.getText()}", file=sys.stderr)
            raise KumirEvalError(f"Неизвестный тип первичного выражения: {ctx.getText()}", ctx.start.line, ctx.start.column)
        print(f"[DEBUG][visitPrimaryExpressionEE] Returning: {repr(result)} (type: {type(result)}) for ctx: {ctx.getText()}", file=sys.stderr)
        return result 