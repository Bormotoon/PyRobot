from typing import TYPE_CHECKING, Any, Optional, Tuple, List, Dict
from antlr4 import ParserRuleContext
import sys

from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import (KumirSyntaxError, KumirEvalError, KumirNotImplementedError, 
                                KumirNameError, KumirArgumentError, KumirTypeError, KumirIndexError,
                                KumirInputError, LoopBreakException, LoopContinueException, ProcedureExitCalled,
                                StopExecutionException, AssertionError_, KumirExecutionError)
from ..kumir_datatypes import KumirTableVar
from .constants import (STRING_TYPE, KUMIR_TRUE, KUMIR_FALSE,
                        INTEGER_TYPE, FLOAT_TYPE, CHAR_TYPE, BOOLEAN_TYPE)

if TYPE_CHECKING:
    from ..interpreter import KumirInterpreterVisitor


class StatementHandler:
    def __init__(self, visitor: 'KumirInterpreterVisitor'):
        self.visitor = visitor

    def _get_error_info(self, ctx: Optional[ParserRuleContext]) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        line_idx, col_idx, lc = None, None, None
        if ctx and hasattr(ctx, 'start') and ctx.start:
            line_idx = ctx.start.line - 1
            col_idx = ctx.start.column
            lc = self.visitor.get_line_content_from_ctx(ctx)
        return line_idx, col_idx, lc

    def visitLvalue(self, ctx: KumirParser.LvalueContext):
        """
        Обрабатывает узел lvalue, извлекая имя переменной, информацию о ней
        и вычисленные индексы (если есть).
        Этот метод теперь находится в StatementHandler.
        """
        # print(f"[DEBUG][StatementHandler.visitLvalue] Called for LValue: {ctx.getText()}", file=sys.stderr)

        if not hasattr(ctx, 'qualifiedIdentifier') or not callable(ctx.qualifiedIdentifier):
            line_idx_err, col_idx_err, lc_err = self._get_error_info(ctx)
            raise KumirSyntaxError("Некорректное lvalue: отсутствует метод qualifiedIdentifier.",
                                   line_index=line_idx_err,
                                   column_index=col_idx_err,
                                   line_content=lc_err)
        
        q_ident_node = ctx.qualifiedIdentifier()
        if not q_ident_node:
            line_idx_err, col_idx_err, lc_err = self._get_error_info(ctx)
            raise KumirSyntaxError("Некорректное lvalue: отсутствует идентификатор.",
                                   line_index=line_idx_err,
                                   column_index=col_idx_err,
                                   line_content=lc_err)

        var_name = q_ident_node.getText()
        # print(f"[DEBUG][StatementHandler.visitLvalue] LValue var_name: '{var_name}'", file=sys.stderr)
        
        # Получаем информацию о переменной из текущих scopes
        var_info, _ = self.visitor.scope_manager.find_variable(var_name, ctx=q_ident_node) # ИСПРАВЛЕНО: ctx_for_error=q_ident_node -> ctx=q_ident_node
        # print(f"[DEBUG][StatementHandler.visitLvalue] Found var_info for '{var_name}': {var_info}", file=sys.stderr)
        if var_info is None: # Дополнительная проверка, find_variable должен был бы вызвать ошибку, но для безопасности
            line_idx_err, col_idx_err, lc_err = self._get_error_info(q_ident_node)
            raise KumirNameError(f"Переменная '{var_name}' не найдена при обработке lvalue.",
                                 line_index=line_idx_err, column_index=col_idx_err, line_content=lc_err)

        indices = []
        index_list_node = ctx.indexList()
        if index_list_node:
            # print(f"[DEBUG][StatementHandler.visitLvalue] LValue has indices: {index_list_node.getText()}", file=sys.stderr)
            if hasattr(index_list_node, 'expression') and callable(index_list_node.expression):
                for index_expr_ctx in index_list_node.expression():
                    idx_val = self.visitor.evaluator.visitExpression(index_expr_ctx)
                    if not isinstance(idx_val, int):
                        line_idx_err, col_idx_err, lc_err = self._get_error_info(index_expr_ctx)
                        raise KumirEvalError(f"Индекс для '{var_name}' должен быть целым числом (в LValue).",
                                           line_index=line_idx_err,
                                           column_index=col_idx_err,
                                           line_content=lc_err)
                    indices.append(idx_val)
            # print(f"[DEBUG][StatementHandler.visitLvalue] Evaluated indices for '{var_name}': {indices}", file=sys.stderr)

        return {
            'type': 'variable', # Этот тип может быть избыточен, т.к. мы работаем с lvalue
            'name': var_name,
            'var_info': var_info, 
            'indices': indices if index_list_node else None
        }

    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        l_value_ctx = ctx.lvalue()
        expr_ctx = ctx.expression()

        if not l_value_ctx and not ctx.ASSIGN():
            if expr_ctx:
                is_simple_identifier_call = False
                proc_name_candidate = ""
                current_expr = expr_ctx
                try:
                    if hasattr(current_expr, 'logicalOrExpression') and current_expr.logicalOrExpression():
                        current_expr = current_expr.logicalOrExpression()
                        if hasattr(current_expr, 'logicalAndExpression') and len(current_expr.logicalAndExpression()) == 1:
                            current_expr = current_expr.logicalAndExpression(0)
                            if hasattr(current_expr, 'equalityExpression') and len(current_expr.equalityExpression()) == 1:
                                current_expr = current_expr.equalityExpression(0)
                                if hasattr(current_expr, 'relationalExpression') and len(current_expr.relationalExpression()) == 1:
                                    current_expr = current_expr.relationalExpression(0)
                                    if hasattr(current_expr, 'additiveExpression') and len(current_expr.additiveExpression()) == 1:
                                        current_expr = current_expr.additiveExpression(0)
                                        if hasattr(current_expr, 'multiplicativeExpression') and len(current_expr.multiplicativeExpression()) == 1:
                                            current_expr = current_expr.multiplicativeExpression(0)
                                            if hasattr(current_expr, 'powerExpression') and current_expr.powerExpression():
                                                current_expr = current_expr.powerExpression()
                                                if hasattr(current_expr, 'unaryExpression') and len(current_expr.unaryExpression()) == 1:
                                                    current_expr = current_expr.unaryExpression(0)
                                                    if hasattr(current_expr, 'postfixExpression') and current_expr.postfixExpression():
                                                        current_expr = current_expr.postfixExpression()
                                                        if hasattr(current_expr, 'primaryExpression') and current_expr.primaryExpression():
                                                            primary_expr = current_expr.primaryExpression()
                                                            if primary_expr.qualifiedIdentifier() and not current_expr.postfixOperator():
                                                                proc_name_candidate = primary_expr.qualifiedIdentifier().getText()
                                                                is_simple_identifier_call = True
                except Exception:
                    is_simple_identifier_call = False

                proc_name_lower = proc_name_candidate.lower()
                if is_simple_identifier_call and self.visitor.procedure_manager and proc_name_lower in self.visitor.procedure_manager.procedures:
                    proc_info = self.visitor.procedure_manager.procedures[proc_name_lower]
                    has_only_res_params = True
                    has_any_params = False
                    if proc_info.get('params'):
                        has_any_params = True
                        for p_info in proc_info['params'].values():
                            if p_info.get('mode_for_evaluator') != 'рез': 
                                has_only_res_params = False
                                break
                    
                    if not has_any_params or has_only_res_params:
                        call_data_for_statement = {'name': proc_name_candidate}
                        self.visitor.procedure_manager._execute_procedure_call(call_data_for_statement, [], expr_ctx)
                        return
                
                self.visitor.evaluator.visitExpression(expr_ctx) 
            return

        if not l_value_ctx or not expr_ctx or not ctx.ASSIGN():
            line_idx, col_idx, lc = self._get_error_info(ctx)
            raise KumirSyntaxError("Некорректный оператор присваивания.",
                                   line_index=line_idx, column_index=col_idx, line_content=lc)

        value_to_assign = self.visitor.evaluator.visitExpression(expr_ctx)

        if l_value_ctx.RETURN_VALUE():
            if not self.visitor.function_call_active:
                line_idx, col_idx, lc_ret = self._get_error_info(l_value_ctx)
                raise KumirEvalError("Присваивание 'знач' возможно только внутри функции.",
                                   line_index=line_idx, column_index=col_idx, line_content=lc_ret)
            
            znach_info, _ = self.visitor.scope_manager.find_variable("__знач__")
            if znach_info is None: 
                line_idx, col_idx, lc_znach = self._get_error_info(l_value_ctx)
                raise KumirEvalError("Внутренняя ошибка: переменная '__знач__' не найдена в области видимости функции.",
                                   line_index=line_idx, column_index=col_idx, line_content=lc_znach)

            expected_return_type = znach_info['type']
            
            validated_value = self.visitor._validate_and_convert_value_for_assignment(
                value_to_assign, 
                expected_return_type, 
                var_name="возвращаемому значению 'знач'"
            )
            self.visitor.scope_manager.update_variable("__знач__", validated_value, ctx_for_error=l_value_ctx)
            return

        q_ident_node = l_value_ctx.qualifiedIdentifier()
        if not q_ident_node:
            line_idx, col_idx, lc_q = self._get_error_info(l_value_ctx)
            raise KumirNotImplementedError(f"Присваивание в lvalue вида '{l_value_ctx.getText()}' не поддерживается.",
                                           line_index=line_idx, column_index=col_idx, line_content=lc_q)
        
        var_name = q_ident_node.getText()
        var_info, _ = self.visitor.scope_manager.find_variable(var_name)
        if var_info is None:
            line_idx, col_idx, lc_name = self._get_error_info(q_ident_node)
            raise KumirNameError(f"Переменная '{var_name}' не найдена.",
                                 line_index=line_idx, column_index=col_idx, line_content=lc_name)

        index_list_node = l_value_ctx.indexList()
        if index_list_node:
            indices = []
            for index_expr_ctx in index_list_node.expression():
                idx_val = self.visitor.evaluator.visitExpression(index_expr_ctx)
                if not isinstance(idx_val, int):
                    line_idx, col_idx, lc_idx = self._get_error_info(index_expr_ctx)
                    raise KumirEvalError(f"Индекс для '{var_name}' должен быть целым числом.",
                                       line_index=line_idx, column_index=col_idx, line_content=lc_idx)
                indices.append(idx_val)
            
            if var_info['is_table']:
                table_var: KumirTableVar = var_info['value']
                if not isinstance(table_var, KumirTableVar):
                    line_idx, col_idx, lc_tbl_var = self._get_error_info(q_ident_node)
                    raise KumirEvalError(f"Переменная '{var_name}' не является корректным объектом таблицы.",
                                       line_index=line_idx, column_index=col_idx, line_content=lc_tbl_var)
                
                validated_value_for_element = self.visitor._validate_and_convert_value_for_assignment(
                    value_to_assign, 
                    table_var.base_kumir_type_name,
                    var_name=f"элементу таблицы '{var_name}'"
                )
                try:
                    table_var.set_value(indices, validated_value_for_element, access_ctx=index_list_node)
                except KumirIndexError as e:
                    line_idx, col_idx, lc_idx_set = self._get_error_info(index_list_node)
                    raise KumirIndexError(str(e), 
                                        line_index=line_idx, column_index=col_idx, line_content=lc_idx_set) from e
                except KumirTypeError as e:
                    line_idx, col_idx, lc_type_set = self._get_error_info(expr_ctx)
                    raise KumirTypeError(str(e), 
                                        line_index=line_idx, column_index=col_idx, line_content=lc_type_set) from e
                var_info['initialized'] = True
            
            elif var_info['type'] == STRING_TYPE:
                if len(indices) != 1:
                    line_idx, col_idx, lc_str_idx = self._get_error_info(index_list_node)
                    raise KumirArgumentError(f"Для присваивания символу строки '{var_name}' требуется один индекс.",
                                           line_index=line_idx, column_index=col_idx, line_content=lc_str_idx)
                kumir_idx = indices[0]
                if not isinstance(value_to_assign, str) or len(value_to_assign) != 1:
                    line_idx, col_idx, lc_str_val = self._get_error_info(expr_ctx)
                    raise KumirTypeError(f"При присваивании символу строки '{var_name}[{kumir_idx}]' значение должно быть одиночным символом (тип СИМ).",
                                       line_index=line_idx, column_index=col_idx, line_content=lc_str_val)
                current_string_value = var_info['value']
                if not isinstance(current_string_value, str):
                    line_idx, col_idx, lc_str_var = self._get_error_info(q_ident_node)
                    raise KumirEvalError(f"Переменная '{var_name}' имеет некорректный тип для строковой операции.",
                                       line_index=line_idx, column_index=col_idx, line_content=lc_str_var)
                py_idx = kumir_idx - 1
                if not (0 <= py_idx < len(current_string_value)):
                    line_idx, col_idx, lc_str_bnd = self._get_error_info(index_list_node)
                    raise KumirIndexError(f"Индекс {kumir_idx} выходит за границы строки '{var_name}' (длина {len(current_string_value)}).",
                                        line_index=line_idx, column_index=col_idx, line_content=lc_str_bnd)
                string_list = list(current_string_value)
                string_list[py_idx] = value_to_assign
                new_string_value = "".join(string_list)
                self.visitor.scope_manager.update_variable(var_name, new_string_value, ctx_for_error=q_ident_node)
            else:
                line_idx, col_idx, lc_tbl_str = self._get_error_info(q_ident_node)
                raise KumirTypeError(f"Переменная '{var_name}' не является таблицей или строкой, индексация не применима.",
                                   line_index=line_idx, column_index=col_idx, line_content=lc_tbl_str)
        else: 
            validated_value = self.visitor._validate_and_convert_value_for_assignment(
                value_to_assign, 
                var_info['type'], 
                var_name=f"переменной '{var_name}'"
            )
            self.visitor.scope_manager.update_variable(var_name, validated_value, ctx_for_error=q_ident_node)
        return None

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext):
        if ctx.INPUT():
            var_name_nodes: List[Optional[KumirParser.QualifiedIdentifierContext]] = []
            qualified_identifiers = ctx.qualifiedIdentifier()
            if isinstance(qualified_identifiers, list):
                var_name_nodes = qualified_identifiers
            elif qualified_identifiers is not None:
                var_name_nodes = [qualified_identifiers]
            
            index_list_nodes: List[Optional[KumirParser.IndexListContext]] = []
            index_lists = ctx.indexList()
            if isinstance(index_lists, list):
                index_list_nodes = index_lists
            elif index_lists is not None:
                index_list_nodes = [index_lists]
            
            num_vars = len(var_name_nodes)
            num_indices_groups = len(index_list_nodes)

            if num_indices_groups != 0 and num_indices_groups != num_vars:
                line_idx, col_idx, lc = self._get_error_info(ctx)
                raise KumirSyntaxError(
                    f"Во вводе указано {num_vars} переменных и {num_indices_groups} групп индексов. "
                    f"Количество групп индексов должно быть 0 или равно количеству переменных.",
                    line_index=line_idx, column_index=col_idx, line_content=lc)

            for i, var_name_node in enumerate(var_name_nodes):
                if var_name_node is None: continue
                var_name = var_name_node.getText()
                var_info, _ = self.visitor.scope_manager.find_variable(var_name)
                
                if var_info is None:
                    line_idx, col_idx, lc_name_err = self._get_error_info(var_name_node)
                    raise KumirNameError(f"Переменная '{var_name}' не найдена.",
                                         line_index=line_idx, column_index=col_idx, line_content=lc_name_err)

                if var_info.get('is_const', False):
                    line_idx, col_idx, lc_const_err = self._get_error_info(var_name_node)
                    raise KumirEvalError(f"Нельзя вводить значение в константу '{var_name}'.",
                                         line_index=line_idx, column_index=col_idx, line_content=lc_const_err)

                user_input_value = None
                if hasattr(self.visitor, 'get_input_line'):
                    prompt = f"Введите значение для {var_name} (тип {var_info['type']}): "
                    try:
                        user_input_value = self.visitor.get_input_line(prompt=prompt)
                        if user_input_value is None:
                            line_idx, col_idx, lc_eof_err = self._get_error_info(ctx)
                            raise KumirInputError("Ввод был прерван или достигнут конец файла.", 
                                                line_index=line_idx, column_index=col_idx, line_content=lc_eof_err)
                    except Exception as e:
                        line_idx, col_idx, lc_cb_err = self._get_error_info(ctx)
                        raise KumirInputError(f"Ошибка при получении ввода: {str(e)}", 
                                            line_index=line_idx, column_index=col_idx, line_content=lc_cb_err) from e
                else:
                    line_idx, col_idx, lc_no_cb_err = self._get_error_info(ctx)
                    raise KumirNotImplementedError("Функция ввода не предоставлена интерпретатору.",
                                                 line_index=line_idx, column_index=col_idx, line_content=lc_no_cb_err)

                try:
                    target_type = var_info['type']
                    converted_value = None
                    if target_type == INTEGER_TYPE: converted_value = int(user_input_value)
                    elif target_type == FLOAT_TYPE: converted_value = float(user_input_value)
                    elif target_type == CHAR_TYPE:
                        if isinstance(user_input_value, str) and len(user_input_value) == 1:
                            converted_value = user_input_value
                        else: raise ValueError("для типа ЛИТ ожидался один символ")
                    elif target_type == STRING_TYPE: converted_value = str(user_input_value)
                    elif target_type == BOOLEAN_TYPE:
                        u_val_lower = str(user_input_value).lower()
                        if u_val_lower in ["да", "истина", "true", "1", "yes"]: converted_value = KUMIR_TRUE
                        elif u_val_lower in ["нет", "ложь", "false", "0", "no"]: converted_value = KUMIR_FALSE
                        else:
                            try:
                                num_val = float(user_input_value)
                                converted_value = KUMIR_TRUE if num_val != 0 else KUMIR_FALSE
                            except ValueError: raise ValueError("для типа ЛОГ ожидалось значение истина/ложь или число")
                    else:
                        line_idx, col_idx, lc_type_err = self._get_error_info(var_name_node)
                        raise KumirTypeError(f"Ввод значений типа '{target_type}' для переменной '{var_name}' не поддерживается.",
                                             line_index=line_idx, column_index=col_idx, line_content=lc_type_err)
                except ValueError as e:
                    line_idx, col_idx, lc_val_err = self._get_error_info(ctx)
                    raise KumirTypeError(f"Введенное значение '{user_input_value}' не соответствует типу '{var_info['type']}' переменной '{var_name}'. {e}",
                                         line_index=line_idx, column_index=col_idx, line_content=lc_val_err)

                current_index_list_node: Optional[KumirParser.IndexListContext] = None
                if num_indices_groups > 0 and i < num_indices_groups :
                    current_index_list_node = index_list_nodes[i]

                if current_index_list_node:
                    if current_index_list_node is None: continue

                    indices = []
                    for index_expr_ctx in current_index_list_node.expression():
                        idx_val = self.visitor.evaluator.visitExpression(index_expr_ctx)
                        if not isinstance(idx_val, int):
                            line_idx, col_idx, lc_idx_err = self._get_error_info(index_expr_ctx)
                            raise KumirEvalError(f"Индекс для '{var_name}' должен быть целым числом.",
                                               line_index=line_idx, column_index=col_idx, line_content=lc_idx_err)
                        indices.append(idx_val)

                    if var_info['is_table']:
                        table_var: KumirTableVar = var_info['value']
                        if not isinstance(table_var, KumirTableVar):
                             line_idx, col_idx, lc_tbl_err = self._get_error_info(var_name_node)
                             raise KumirEvalError(f"Переменная '{var_name}' не является корректным объектом таблицы.",
                                                line_index=line_idx, column_index=col_idx, line_content=lc_tbl_err)
                        
                        validated_value_for_element = self.visitor._validate_and_convert_value_for_assignment(
                            converted_value, table_var.base_kumir_type_name,
                            var_name=f"элементу таблицы '{var_name}'"
                        )
                        try:
                            table_var.set_value(indices, validated_value_for_element, access_ctx=current_index_list_node)
                        except KumirIndexError as e_idx:
                            line_idx, col_idx, lc_idx_set_err = self._get_error_info(current_index_list_node)
                            raise KumirIndexError(str(e_idx),
                                                line_index=line_idx, column_index=col_idx, line_content=lc_idx_set_err) from e_idx
                        var_info['initialized'] = True
                    elif var_info['type'] == STRING_TYPE:
                        if len(indices) != 1:
                            line_idx, col_idx, lc_str_idx_err = self._get_error_info(current_index_list_node)
                            raise KumirArgumentError(f"Для ввода в символ строки '{var_name}' требуется один индекс.",
                                                   line_index=line_idx, column_index=col_idx, line_content=lc_str_idx_err)
                        kumir_idx = indices[0]
                        if not (isinstance(converted_value, str) and len(converted_value) == 1):
                            line_idx, col_idx, lc_str_val_err = self._get_error_info(ctx)
                            raise KumirTypeError(f"При вводе в символ строки '{var_name}[{kumir_idx}]' значение должно быть одиночным символом (тип СИМ).",
                                               line_index=line_idx, column_index=col_idx, line_content=lc_str_val_err)
                        
                        current_string_value = var_info['value']
                        if not isinstance(current_string_value, str):
                            line_idx, col_idx, lc_str_var_err = self._get_error_info(var_name_node)
                            raise KumirEvalError(f"Переменная '{var_name}' имеет некорректный тип для строковой операции.",
                                               line_index=line_idx, column_index=col_idx, line_content=lc_str_var_err)
                        
                        py_idx = kumir_idx - 1
                        if not (0 <= py_idx < len(current_string_value)):
                            line_idx, col_idx, lc_str_bnd_err = self._get_error_info(current_index_list_node)
                            raise KumirIndexError(f"Индекс {kumir_idx} выходит за границы строки '{var_name}' (длина {len(current_string_value)}).",
                                                line_index=line_idx, column_index=col_idx, line_content=lc_str_bnd_err)
                        
                        string_list = list(current_string_value)
                        string_list[py_idx] = converted_value
                        new_string_value = "".join(string_list)
                        self.visitor.scope_manager.update_variable(var_name, new_string_value, ctx_for_error=var_name_node)
                    else:
                        line_idx, col_idx, lc_tbl_str_err = self._get_error_info(var_name_node)
                        raise KumirTypeError(f"Переменная '{var_name}' не является таблицей или строкой, индексация при вводе не применима.",
                                           line_index=line_idx, column_index=col_idx, line_content=lc_tbl_str_err)
                else: 
                    validated_value = self.visitor._validate_and_convert_value_for_assignment(
                        converted_value, var_info['type'],
                        var_name=f"переменной '{var_name}'"
                    )
                    self.visitor.scope_manager.update_variable(var_name, validated_value, ctx_for_error=var_name_node)

        elif ctx.OUTPUT():
            output_parts = []
            expression_nodes: List[Optional[KumirParser.ExpressionContext]] = []
            expressions = ctx.expression()
            if isinstance(expressions, list):
                expression_nodes = expressions
            elif expressions is not None:
                expression_nodes = [expressions]

            for expr_ctx in expression_nodes:
                if expr_ctx is None: continue
                value = self.visitor.evaluator.visitExpression(expr_ctx)
                if isinstance(value, bool):
                    output_parts.append(str(KUMIR_TRUE) if value else str(KUMIR_FALSE))
                elif isinstance(value, float):
                    output_parts.append(str(value))
                elif value is None: 
                    line_idx, col_idx, lc_none_err = self._get_error_info(expr_ctx)
                    raise KumirTypeError("Попытка вывода значения типа ПУСТО.",
                                         line_index=line_idx, column_index=col_idx, line_content=lc_none_err)
                else:
                    output_parts.append(str(value))
            
            self.visitor.write_output("".join(output_parts))
            
            newline_node = ctx.NEWLINE() 
            if newline_node: 
                self.visitor.write_output("\n")

        elif ctx.NEWLINE() and \
             not (ctx.INPUT()) and \
             not (ctx.OUTPUT()):
            self.visitor.write_output("\n")
        else:
            line_idx, col_idx, lc_unknown_err = self._get_error_info(ctx)
            raise KumirNotImplementedError(f"Неизвестный или некорректный IO оператор: {ctx.getText()}",
                                         line_index=line_idx, column_index=col_idx, line_content=lc_unknown_err)
        return None

    def visitIfStatement(self, ctx: KumirParser.IfStatementContext):
        """Обработка условного оператора."""
        # print(f"[DEBUG][visitIfStatement] Called for ctx: {ctx.getText()} with id: {id(ctx)}", file=self.visitor.error_stream)

        condition_expr_ctx = None
        statement_sequences_list = []
        has_else_kw = False

        try:
            condition_expr_ctx = ctx.expression()
            statement_sequences_list = ctx.statementSequence()
            has_else_kw = bool(ctx.ELSE()) 
            # print(f"[DEBUG][visitIfStatement] Successfully got expression and statementSequence. Condition type: {type(condition_expr_ctx).__name__}, Sequences count: {len(statement_sequences_list)}, Has ELSE: {has_else_kw}", file=self.visitor.error_stream)
        except AttributeError as e:
            # print(f"[DEBUG][visitIfStatement] AttributeError CAUGHT IMMEDIATELY: {e}", file=self.visitor.error_stream)
            # print(f"[DEBUG][visitIfStatement] Attributes of ctx ({type(ctx).__name__}) AT POINT OF ERROR:", file=self.visitor.error_stream)
            # for attr_name in dir(ctx):
            #     if not attr_name.startswith('__'):
            #         try: print(f"  {attr_name}: {getattr(ctx, attr_name)}", file=self.visitor.error_stream)
            #         except: print(f"  {attr_name}: <Error getting>", file=self.visitor.error_stream)
            raise 

        line_idx_cond, col_idx_cond, lc_cond = self._get_error_info(ctx) # For general syntax error

        if condition_expr_ctx is None:
            raise KumirSyntaxError("Отсутствует условное выражение в операторе ЕСЛИ", 
                                   line_index=line_idx_cond, column_index=col_idx_cond, line_content=lc_cond)
        
        condition_value = None 
        try:
            condition_value = self.visitor.evaluator.visitExpression(condition_expr_ctx) 
        except Exception as e:
            line_idx_eval, col_idx_eval, lc_eval = self._get_error_info(condition_expr_ctx)
            raise KumirEvalError(f"Ошибка вычисления условия: {e}", 
                                 line_index=line_idx_eval, column_index=col_idx_eval, line_content=lc_eval) from e

        if not isinstance(condition_value, bool):
            line_idx_type, col_idx_type, lc_type = self._get_error_info(condition_expr_ctx)
            raise KumirEvalError(
                f"Условие должно быть логического типа, а не {type(condition_value).__name__}.", 
                line_index=line_idx_type, column_index=col_idx_type, line_content=lc_type)

        # print(f"  -> Условие = {condition_value}", file=self.visitor.error_stream)

        if condition_value:
            if statement_sequences_list and len(statement_sequences_list) > 0: 
                then_branch_ctx = statement_sequences_list[0]
                if then_branch_ctx is not None: 
                    return self.visitor.visit(then_branch_ctx) 
        else:
            if has_else_kw and statement_sequences_list and len(statement_sequences_list) > 1: 
                else_branch_ctx = statement_sequences_list[1]
                if else_branch_ctx is not None: 
                    return self.visitor.visit(else_branch_ctx) 
        return None

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        loop_spec = ctx.loopSpecifier()
        body = ctx.statementSequence()
        condition_ctx = None
        loop_var_name = None
        start_expr_ctx, end_expr_ctx, step_expr_ctx = None, None, None
        
        # Используем атрибуты visitor для управления состоянием цикла
        self.visitor.loop_depth += 1
        self.visitor.exit_flags.append(False) # Флаг для текущего уровня цикла

        line_idx, col_idx, lc = self._get_error_info(loop_spec if loop_spec else ctx)

        # Определяем тип цикла и извлекаем его параметры
        if loop_spec.WHILE():
            condition_ctx = loop_spec.expression()
            if not condition_ctx: # Добавлена проверка
                raise KumirSyntaxError("Отсутствует условное выражение в цикле ПОКА",
                                       line_index=line_idx, column_index=col_idx, line_content=lc)
        elif loop_spec.REPEAT(): # нц ... раз
            count_expr_ctx = loop_spec.expression()
            if not count_expr_ctx:
                raise KumirSyntaxError("Отсутствует выражение для количества повторений в цикле 'нц...раз'", 
                                       line_index=line_idx, column_index=col_idx, line_content=lc)
            
            loop_count_val = self.visitor.evaluator.visitExpression(count_expr_ctx)
            if not isinstance(loop_count_val, int) or loop_count_val < 0:
                l_idx_cnt, c_idx_cnt, lc_cnt = self._get_error_info(count_expr_ctx)
                raise KumirEvalError("Количество повторений в цикле 'нц...раз' должно быть не отрицательным целым числом.",
                                   line_index=l_idx_cnt, column_index=c_idx_cnt, line_content=lc_cnt)
            
            for _ in range(loop_count_val):
                if self.visitor.exit_flags[-1]: break
                try:
                    self.visitor.visit(body) # Используем self.visitor.visit
                except LoopBreakException: 
                    break
                except LoopContinueException: 
                    continue 
            
            self.visitor.exit_flags.pop()
            self.visitor.loop_depth -= 1
            return None

        elif loop_spec.FOR():
            loop_var_ctx = loop_spec.qualifiedIdentifier()
            if not loop_var_ctx:
                raise KumirSyntaxError("Отсутствует переменная цикла в операторе ДЛЯ",
                                       line_index=line_idx, column_index=col_idx, line_content=lc)
            loop_var_name = loop_var_ctx.getText()
            
            expressions = loop_spec.expression() 
            if len(expressions) < 2:
                raise KumirSyntaxError("Недостаточно выражений для границ цикла ДЛЯ",
                                       line_index=line_idx, column_index=col_idx, line_content=lc)
            start_expr_ctx = expressions[0]
            end_expr_ctx = expressions[1]
            if len(expressions) > 2:
                step_expr_ctx = expressions[2]
        
        elif loop_spec.UNTIL(): 
            condition_ctx = loop_spec.expression()
            if not condition_ctx: # Добавлена проверка
                raise KumirSyntaxError("Отсутствует условное выражение в цикле ДО ПОКА НЕ",
                                       line_index=line_idx, column_index=col_idx, line_content=lc)
        else:
            raise KumirNotImplementedError(f"Тип цикла не поддерживается: {loop_spec.getText()}",
                                           line_index=line_idx, column_index=col_idx, line_content=lc)

        # Логика выполнения циклов
        if loop_spec.WHILE():
            while True:
                if self.visitor.exit_flags[-1]: break
                condition_value = self.visitor.evaluator.visitExpression(condition_ctx)
                if not isinstance(condition_value, bool):
                    l_idx_cond, c_idx_cond, lc_cond = self._get_error_info(condition_ctx)
                    raise KumirEvalError("Условие цикла ПОКА должно быть логического типа.",
                                       line_index=l_idx_cond, column_index=c_idx_cond, line_content=lc_cond)
                if not condition_value: break
                try:
                    self.visitor.visit(body)
                except LoopBreakException:
                    break
                except LoopContinueException:
                    continue
        
        elif loop_spec.UNTIL(): 
            while True:
                if self.visitor.exit_flags[-1]: break
                try:
                    self.visitor.visit(body)
                except LoopBreakException:
                    break
                except LoopContinueException:
                    continue
                
                condition_value = self.visitor.evaluator.visitExpression(condition_ctx)
                if not isinstance(condition_value, bool):
                    l_idx_cond_u, c_idx_cond_u, lc_cond_u = self._get_error_info(condition_ctx)
                    raise KumirEvalError("Условие цикла ДО ПОКА НЕ должно быть логического типа.",
                                       line_index=l_idx_cond_u, column_index=c_idx_cond_u, line_content=lc_cond_u)
                if condition_value: 
                    break

        elif loop_spec.FOR():
            # Используем scope_manager из visitor
            self.visitor.scope_manager.push_scope() 
            start_val = self.visitor.evaluator.visitExpression(start_expr_ctx)
            end_val = self.visitor.evaluator.visitExpression(end_expr_ctx)
            step_val = 1
            if step_expr_ctx:
                step_val = self.visitor.evaluator.visitExpression(step_expr_ctx)
                if not isinstance(step_val, int) or step_val == 0:
                    l_idx_step, c_idx_step, lc_step = self._get_error_info(step_expr_ctx)
                    raise KumirEvalError("Шаг в цикле ДЛЯ должен быть ненулевым целым числом.",
                                       line_index=l_idx_step, column_index=c_idx_step, line_content=lc_step)
            
            if not (isinstance(start_val, int) and isinstance(end_val, int)):
                err_ctx_for = start_expr_ctx if not isinstance(start_val, int) else end_expr_ctx
                l_idx_for_bound, c_idx_for_bound, lc_for_bound = self._get_error_info(err_ctx_for)
                raise KumirEvalError("Границы цикла ДЛЯ должны быть целыми числами.",
                                   line_index=l_idx_for_bound, column_index=c_idx_for_bound, line_content=lc_for_bound)

            # Используем scope_manager из visitor и константу INTEGER_TYPE
            self.visitor.scope_manager.declare_variable(loop_var_name, INTEGER_TYPE, is_table=False, dimensions_info=None, ctx_declaration_item=loop_var_ctx)
            current_val = start_val

            while True:
                if self.visitor.exit_flags[-1]: break
                if step_val > 0 and current_val > end_val: break
                if step_val < 0 and current_val < end_val: break
                
                self.visitor.scope_manager.update_variable(loop_var_name, current_val, ctx_for_error=loop_var_ctx)
                try:
                    self.visitor.visit(body)
                except LoopBreakException:
                    break
                except LoopContinueException:
                    current_val += step_val
                    continue
                current_val += step_val
            
            self.visitor.scope_manager.pop_scope()

        self.visitor.exit_flags.pop()
        self.visitor.loop_depth -= 1
        return None

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext):
        # print(f"[DEBUG][VisitExit] Entered. loop_depth={self.visitor.loop_depth}, call_stack exists: {hasattr(self.visitor, 'call_stack') and bool(self.visitor.call_stack)}, scopes depth: {len(self.visitor.scope_manager.scopes)}", file=self.visitor.error_stream)

        # 1. Проверяем, находимся ли мы внутри цикла
        if self.visitor.loop_depth > 0 and self.visitor.exit_flags:
            # print(f"[DEBUG][VisitExit] 'выход' из цикла. loop_depth={self.visitor.loop_depth}", file=self.visitor.error_stream)
            self.visitor.exit_flags[-1] = True
            # Вместо `return None` из оригинального интерпретатора, который просто завершал visit,
            # здесь мы должны бросить исключение, которое прервет выполнение текущей ветки `visit(body)` в цикле.
            # Это важно, так как StatementHandler не управляет напрямую потоком выполнения так, как это делал KumirInterpreterVisitor.
            # LoopBreakException будет пойман в visitLoopStatement.
            raise LoopBreakException() # ИЗМЕНЕНО: Бросаем LoopBreakException

        # 2. Проверяем, находимся ли мы внутри вызова процедуры/функции
        is_in_procedure_call = (len(self.visitor.scope_manager.scopes) > 1) 
        if hasattr(self.visitor, 'call_stack') and self.visitor.call_stack:
            is_in_procedure_call = True

        if is_in_procedure_call:
            # print(f"[DEBUG][VisitExit] 'выход' из процедуры/функции. Глубина scopes: {len(self.visitor.scope_manager.scopes)}. Call_stack active: {hasattr(self.visitor, 'call_stack') and bool(self.visitor.call_stack)}", file=self.visitor.error_stream)
            line_idx, col_idx, lc = self._get_error_info(ctx)
            raise ProcedureExitCalled(f"Выход из процедуры/функции на строке {ctx.start.line}", line_index=line_idx, column_index=col_idx, line_content=lc)

        # 3. 'выход' в основном теле программы
        # print(f"[DEBUG][VisitExit] 'выход' из основного блока программы.", file=self.visitor.error_stream)
        line_idx, col_idx, lc = self._get_error_info(ctx)
        raise KumirExecutionError("Команда 'выход' в главном блоке программы.", line_index=line_idx, column_index=col_idx, line_content=lc)

    def visitPauseStatement(self, ctx: KumirParser.PauseStatementContext):
        # В реальном окружении здесь могла бы быть задержка или ожидание ввода от пользователя.
        # В текущей симуляции просто выводим сообщение.
        message_node = ctx.STRING_LITERAL_WITH_NS() if hasattr(ctx, 'STRING_LITERAL_WITH_NS') and callable(ctx.STRING_LITERAL_WITH_NS) else None
        message = "" # По умолчанию пустое сообщение
        if message_node:
            # Удаляем кавычки и обрабатываем "нс"
            raw_text = message_node.getText()
            # Убираем внешние кавычки
            if raw_text.startswith('"') and raw_text.endswith('"'):
                message = raw_text[1:-1]
            else:
                message = raw_text # Если нет кавычек (маловероятно по грамматике)
            # Заменяем последовательности нс на реальные переводы строк
            message = message.replace("нс", "\n")
        
        # print(f"[ПАУЗА] {message if message else 'Нажмите Enter для продолжения...'}", file=self.visitor.error_stream)
        # Вместо print в error_stream, мы должны использовать output_stream, так как это взаимодействие с пользователем
        print(f"{message if message else 'Нажмите Enter для продолжения...'}", file=self.visitor.output_stream)
        
        # Ожидание действия от пользователя (например, нажатия Enter)
        # В данном контексте это может быть просто вызов input() без присваивания результата.
        # Однако, это заблокирует выполнение, если нет интерактивного ввода.
        # Для автоматических тестов лучше не блокировать.
        # Если self.visitor.input_stream это sys.stdin и он не был перенаправлен, то input() сработает.
        # Если это StringIO, то input() может вызвать ошибку или вернуть пустую строку.
        try:
            # Попытка прочитать строку, чтобы имитировать ожидание
            # Если input_stream не интерактивный, это может не сработать как ожидается.
            if hasattr(self.visitor.input_stream, 'isatty') and self.visitor.input_stream.isatty():
                input() # Ждем нажатия Enter только если ввод интерактивный
            elif self.visitor.input_stream != sys.stdin : # Если input_stream был переопределен (например, для тестов)
                 # Можно прочитать строку из буфера, если там что-то есть, или ничего не делать.
                 # self.visitor.get_input_line() # Это может потребовать ввод, что не всегда хорошо здесь
                 pass # В неинтерактивном режиме просто продолжаем
        except RuntimeError as e:
            # Например, "input(): lost sys.stdin" если stdin был переназначен и закрыт
            print(f"[WARNING][PAUSE] Не удалось ожидать ввод: {e}", file=self.visitor.error_stream)
        return None

    def visitStopStatement(self, ctx: KumirParser.StopStatementContext):
        line_idx, col_idx, lc = self._get_error_info(ctx)
        raise StopExecutionException("Выполнение программы остановлено оператором СТОП.", 
                                   line_index=line_idx, column_index=col_idx, line_content=lc)

    def visitAssertionStatement(self, ctx: KumirParser.AssertionStatementContext):
        condition_ctx = ctx.expression()
        message_node = ctx.STRING_LITERAL_WITH_NS() if hasattr(ctx, 'STRING_LITERAL_WITH_NS') and callable(ctx.STRING_LITERAL_WITH_NS) else None
        message = "Утверждение ложно"

        if message_node:
            raw_text = message_node.getText()
            if raw_text.startswith('"') and raw_text.endswith('"'):
                message = raw_text[1:-1]
            else:
                message = raw_text
            message = message.replace("нс", "\n")

        condition_value = self.visitor.evaluator.visitExpression(condition_ctx)

        if not isinstance(condition_value, bool):
            line_idx, col_idx, lc = self._get_error_info(condition_ctx)
            raise KumirEvalError("Условие в утверждении должно быть логического типа.",
                               line_index=line_idx, column_index=col_idx, line_content=lc)

        if not condition_value:
            line_idx, col_idx, lc = self._get_error_info(ctx)
            raise AssertionError_(
                f"Утверждение не выполнено: {message} (выражение: {condition_ctx.getText()})",
                line_index=line_idx, column_index=col_idx, line_content=lc
            )
        return None

    # ... (other statement handlers will be added here)

