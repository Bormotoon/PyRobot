# Functions for managing user-defined procedures and functions (algorithms) 
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from antlr4 import ParserRuleContext # Убрана TerminalNode, она импортируется ниже, если нужна
from antlr4.tree.Tree import TerminalNode # Импорт TerminalNode

# Локальные импорты КуМир (относительные)
from ..generated.KumirParser import KumirParser # Исправленный импорт KumirParser
from ..kumir_exceptions import DeclarationError, KumirArgumentError, KumirNameError, KumirTypeError, ProcedureExitCalled, AssignmentError, KumirEvalError, LoopExitException
from ..kumir_datatypes import KumirTableVar # Для TYPE_CHECKING, если понадобится для параметров
from .constants import VOID_TYPE # <--- Добавлен VOID_TYPE
from .scope_manager import get_default_value # <--- Import get_default_value
from .type_utils import get_type_info_from_specifier # <--- ДОБАВЛЕН ИМПОРТ

if TYPE_CHECKING:
    from ..interpreter import KumirInterpreterVisitor # Для тайп-хинтинга родительского визитора

class ProcedureManager:
    def __init__(self, visitor: 'KumirInterpreterVisitor'):
        self.visitor = visitor
        self.procedures: Dict[str, Dict[str, Any]] = {} # {name_lower: {name, ctx, params, is_func, result_type}}

    def clear_procedures(self):
        '''Очищает список известных процедур.'''
        self.procedures = {}

    # Сюда будут перенесены:
    # _collect_procedure_definitions
    # _execute_procedure_call
    # _extract_parameters
    # _get_param_mode
    # (возможно _get_result_type, _get_type_info_from_specifier, если решим их перенести) 

    def _get_param_mode(self, param_decl_ctx: KumirParser.ParameterDeclarationContext) -> str:
        """Определяет режим параметра ('арг', 'рез', 'арг рез')."""
        # В Kumir.g4 параметр режима описывается так:
        # parameterDeclaration: parameterModifier typeSpecifier variableList;
        # parameterModifier: ARG_RES_MODE | ARG_MODE | RES_MODE | EMPTY_MODE (?); // EMPTY_MODE - это отсутствие модификатора
        # ARG_MODE: 'арг'; RES_MODE: 'рез'; ARG_RES_MODE: 'арг' 'рез';

        # --- ИСПРАВЛЕНИЕ ДЛЯ ОШИБКИ ЛИНТЕРА 2332 ---
        # У ParameterDeclarationContext нет parameterModifier().
        # Режим определяется наличием токенов IN_PARAM, OUT_PARAM, INOUT_PARAM.
        
        has_in_param = hasattr(param_decl_ctx, 'IN_PARAM') and callable(param_decl_ctx.IN_PARAM) and param_decl_ctx.IN_PARAM()
        has_out_param = hasattr(param_decl_ctx, 'OUT_PARAM') and callable(param_decl_ctx.OUT_PARAM) and param_decl_ctx.OUT_PARAM()
        # INOUT_PARAM в грамматике не используется для прямого указания "арг рез", там просто "арг" и "рез" вместе
        # Но если бы был отдельный токен INOUT_PARAM, его бы проверяли так:
        # has_inout_param = hasattr(param_decl_ctx, 'INOUT_PARAM') and callable(param_decl_ctx.INOUT_PARAM) and param_decl_ctx.INOUT_PARAM()

        if has_in_param and has_out_param:
            return 'арг рез'
        elif has_in_param:
            return 'арг'
        elif has_out_param:
            return 'рез'
        else:
            # Если нет ни IN_PARAM, ни OUT_PARAM, по умолчанию это 'арг'
            return 'арг'
        # --- КОНЕЦ ИСПРАВЛЕНИЯ --- 

    def _extract_parameters(self, header_ctx: KumirParser.AlgorithmHeaderContext) -> Dict[str, Dict[str, Any]]:
        params = {}
        if header_ctx.parameterList():
            for param_decl_ctx in header_ctx.parameterList().parameterDeclaration():
                mode = self._get_param_mode(param_decl_ctx) # Вызов локального метода

                type_spec_ctx = param_decl_ctx.typeSpecifier()
                # Вызываем новую функцию get_type_info_from_specifier
                try:
                    base_kumir_type, is_table_type = get_type_info_from_specifier(self.visitor, type_spec_ctx)
                except DeclarationError as e:
                    # Аналогично DeclarationVisitorMixin, перевыбрасываем с доп. информацией, если нужно
                    if not (hasattr(e, 'line_index') and e.line_index is not None and \
                            hasattr(e, 'column_index') and e.column_index is not None and \
                            hasattr(e, 'line_content') and e.line_content is not None):
                        line = type_spec_ctx.start.line if hasattr(type_spec_ctx, 'start') else -1
                        col = type_spec_ctx.start.column if hasattr(type_spec_ctx, 'start') else -1
                        lc = self.visitor.get_line_content_from_ctx(type_spec_ctx)
                        raise DeclarationError(str(e.args[0] if e.args else "Ошибка определения типа параметра"),
                                             line_index=line-1 if line != -1 else None, 
                                             column_index=col, 
                                             line_content=lc) from e
                    else:
                        raise
                
                full_param_type = base_kumir_type
                if is_table_type:
                    full_param_type += 'таб'

                for var_item_ctx in param_decl_ctx.variableList().variableDeclarationItem():
                    param_name = var_item_ctx.ID().getText()
                    
                    dimensions = None 
                    if is_table_type:
                        pass

                    params[param_name.lower()] = {
                        'name': param_name,
                        'type': full_param_type, 
                        'base_type': base_kumir_type, 
                        'mode': mode,
                        'is_table': is_table_type,
                        'dimensions': dimensions, 
                        'decl_ctx': var_item_ctx 
                    }
        return params

    def _collect_procedure_definitions(self, ctx):
        """Собирает определения процедур/функций, вызывается рекурсивно."""
        if isinstance(ctx, KumirParser.AlgorithmDefinitionContext):
            header_ctx = ctx.algorithmHeader()
            if not header_ctx: # pragma: no cover
                line = ctx.start.line
                col = ctx.start.column
                lc = self.visitor.get_line_content_from_ctx(ctx)
                raise DeclarationError(f"Строка {line}: Отсутствует заголовок (header) для определения алгоритма.", line_index=line-1, column_index=col, line_content=lc)
            
            name_ctx = header_ctx.algorithmNameTokens() 
            if not name_ctx: # pragma: no cover
                line = header_ctx.start.line
                col = header_ctx.start.column
                lc = self.visitor.get_line_content_from_ctx(header_ctx)
                raise DeclarationError(f"Строка {line}: Отсутствует или не удалось получить имя в заголовке алгоритма (name_ctx is None).", line_index=line-1, column_index=col, line_content=lc)
            
            name = name_ctx.getText().strip()
            if not name: # pragma: no cover
                line = header_ctx.start.line
                raise DeclarationError(f"Строка {line}: Не удалось получить имя алгоритма.", line_index=line-1, column_index=header_ctx.start.column, line_content=self.visitor.get_line_content_from_ctx(header_ctx))

            name_lower = name.lower()
            if name_lower in self.procedures: # pragma: no cover
                original_decl_line = self.procedures[name_lower]['ctx'].start.line
                new_decl_line = header_ctx.start.line
                lc = self.visitor.get_line_content_from_ctx(header_ctx)
                raise DeclarationError(f"Строка {new_decl_line}: Алгоритм с именем '{name}' уже определен ранее на строке {original_decl_line}.", line_index=new_decl_line-1, column_index=header_ctx.start.column, line_content=lc)

            params_info = self._extract_parameters(header_ctx) 
            
            # Check if it's a function by presence of RETURN_TYPE token
            is_function = header_ctx.RETURN_TYPE() is not None
            
            result_type = None
            if is_function:
                result_type = self._get_result_type(header_ctx)
            
            self.procedures[name_lower] = {
                'name': name,
                'params': params_info,
                'is_function': is_function,
                'result_type': result_type,
                'body_ctx': ctx.algorithmBody(),
                'header_ctx': header_ctx 
            }

        # Рекурсивный обход дочерних узлов, если они есть
        # Обрабатываем Program, ModuleDefinition, ImplicitModuleBody
        elif isinstance(ctx, (KumirParser.ProgramContext, KumirParser.ImplicitModuleBodyContext)):
            if hasattr(ctx, 'children') and ctx.children:
                for child in ctx.children:
                    if not isinstance(child, TerminalNode):
                        self._collect_procedure_definitions(child)
        elif isinstance(ctx, KumirParser.ModuleDefinitionContext):
            # Рекурсивно обходим тело модуля
            body = ctx.moduleBody() if ctx.moduleBody() else ctx.implicitModuleBody()
            if body:
                for item in body.children:
                    if hasattr(item, 'children') or isinstance(item, (KumirParser.AlgorithmDefinitionContext, KumirParser.ModuleDefinitionContext)):
                        self._collect_procedure_definitions(item)
        # Добавим обработку programItem, если вдруг там могут быть определения
        elif hasattr(ctx, 'children') and ctx.children:
            for child in ctx.children:
                if not isinstance(child, TerminalNode):
                    if hasattr(child, 'children') or isinstance(child, (KumirParser.AlgorithmDefinitionContext, KumirParser.ModuleDefinitionContext)):
                        self._collect_procedure_definitions(child)

    def _execute_procedure_call(self, call_data: dict, args: List[Any], call_site_ctx: ParserRuleContext) -> Any:
        proc_name = call_data['name']
        proc_def = self.procedures.get(proc_name.lower())

        if not proc_def: # pragma: no cover
            lc_no_proc = self.visitor.get_line_content_from_ctx(call_site_ctx)
            raise KumirNameError(f"Процедура '{proc_name}' не найдена.", 
                                 line_index=(call_site_ctx.start.line -1) if call_site_ctx else None, 
                                 column_index=call_site_ctx.start.column if call_site_ctx else None, 
                                 line_content=lc_no_proc)

        body_ctx = proc_def['body_ctx']
        if not body_ctx: # pragma: no cover
            lc_no_body = self.visitor.get_line_content_from_ctx(call_site_ctx)
            raise KumirEvalError(f"Отсутствует тело для процедуры '{proc_name}'.",
                                 line_index=(call_site_ctx.start.line -1) if call_site_ctx else None, 
                                 column_index=call_site_ctx.start.column if call_site_ctx else None,
                                 line_content=lc_no_body)

        self.visitor.scope_manager.push_scope()
        # self.visitor.call_stack.append(proc_name) # Если будет использоваться стек вызовов

        # Объявление и инициализация параметров в новой области видимости
        for i, (formal_param_name_lower, formal_param_info) in enumerate(proc_def['params'].items()):
            param_name_original_case = formal_param_info['name']
            # param_base_type = formal_param_info['base_type'] # Не используется напрямую здесь после рефакторинга declare_variable
            param_is_table = formal_param_info['is_table']
            param_mode_for_evaluator = formal_param_info['mode_for_evaluator']
            
            declaration_dimensions = None
            actual_arg_value = None 
            
            if i < len(args):
                arg_data = args[i]
                
                if param_mode_for_evaluator == 'arg':
                    actual_arg_value = arg_data
                elif param_mode_for_evaluator == 'arg_res' or param_mode_for_evaluator == 'arg_res_table_special':
                    if isinstance(arg_data, dict) and 'value' in arg_data:
                        actual_arg_value = arg_data['value']
                        if param_is_table and isinstance(actual_arg_value, KumirTableVar):
                             declaration_dimensions = actual_arg_value.dimension_bounds_list 
                    else: 
                        lc_arg_res = self.visitor.get_line_content_from_ctx(call_site_ctx)
                        raise KumirArgumentError(f"Строка {call_site_ctx.start.line if call_site_ctx else '??'}: Некорректная структура аргумента для параметра '{param_name_original_case}' (режим 'арг рез').",
                                                 line_index=(call_site_ctx.start.line -1) if call_site_ctx else None, 
                                                 column_index=call_site_ctx.start.column if call_site_ctx else None,
                                                 line_content=lc_arg_res)
            else: # pragma: no cover
                lc_arg_count = self.visitor.get_line_content_from_ctx(call_site_ctx)
                raise KumirArgumentError(f"Строка {call_site_ctx.start.line if call_site_ctx else '??'}: Недостаточно аргументов для вызова процедуры '{proc_name}'.",
                                         line_index=(call_site_ctx.start.line-1) if call_site_ctx else None, 
                                         column_index=call_site_ctx.start.column if call_site_ctx else None,
                                         line_content=lc_arg_count)

            # 1. Объявляем переменную параметра
            self.visitor.scope_manager.declare_variable(
                name=param_name_original_case,
                kumir_type=formal_param_info['type'], 
                is_table=param_is_table,
                dimensions=declaration_dimensions, 
                ctx_declaration_item=call_site_ctx 
            )

            # 2. Присваиваем значение параметру (если нужно)
            if param_mode_for_evaluator == 'arg' or param_mode_for_evaluator == 'arg_res' or param_mode_for_evaluator == 'arg_res_table_special':
                if actual_arg_value is not None:
                    try:
                        validated_value = self.visitor._validate_and_convert_value_for_assignment(
                            actual_arg_value,
                            formal_param_info['type'], 
                            var_name=f"параметру '{param_name_original_case}'"
                        )
                        self.visitor.scope_manager.update_variable(param_name_original_case, validated_value, ctx_for_error=call_site_ctx)
                    except (KumirTypeError, KumirEvalError, AssignmentError) as e: 
                        lc_assign = self.visitor.get_line_content_from_ctx(call_site_ctx)
                        if not hasattr(e, 'line_index') or e.line_index is None:
                           e.line_index = call_site_ctx.start.line - 1 if call_site_ctx else None
                        if not hasattr(e, 'column_index') or e.column_index is None:
                           e.column_index = call_site_ctx.start.column if call_site_ctx else None
                        if not hasattr(e, 'line_content') or e.line_content is None:
                           e.line_content = lc_assign
                        raise 
            elif param_mode_for_evaluator == 'рез':
                # Для 'рез' параметров, они инициализируются значением по умолчанию их типа.
                # KumirTableVar сама себя инициализирует при создании через declare_variable.
                # Для простых типов, get_default_value было вызвано внутри declare_variable (в ScopeManager).
                pass


        # Если это функция, инициализируем '__знач__' значением по умолчанию для ее типа
        if proc_def['is_function']:
            expected_return_type = proc_def['result_type']
            if expected_return_type and expected_return_type != VOID_TYPE:
                self.visitor.scope_manager.declare_variable(
                    name="__знач__", 
                    kumir_type=expected_return_type, 
                    is_table=False, 
                    dimensions=None,
                    ctx_declaration_item=call_site_ctx
                )

        self.visitor.function_call_active = proc_def['is_function']
        execution_result = None

        try:
            self.visitor.visit(body_ctx)
        except ProcedureExitCalled: 
            pass 
        except LoopExitException as lee: 
            pass 

        if proc_def['is_function']:
            expected_return_type = proc_def['result_type']
            if expected_return_type and expected_return_type != VOID_TYPE:
                try:
                    return_var_info, _ = self.visitor.scope_manager.find_variable('__знач__') 
                    if return_var_info:
                        execution_result = return_var_info['value']
                    else: 
                        execution_result = get_default_value(expected_return_type) 
                except KumirNameError: 
                    execution_result = get_default_value(expected_return_type) 
            else: 
                execution_result = None
                

        # Для параметров 'рез' и 'арг рез' обновляем переменные в вызывающей области видимости
        current_proc_scope = self.visitor.scope_manager.scopes[-1]
        if len(self.visitor.scope_manager.scopes) > 1: # Убедимся, что есть вызывающая область
            caller_scope = self.visitor.scope_manager.scopes[-2]
            for i, (param_name_local_lower, formal_param_info) in enumerate(proc_def['params'].items()):
                param_name_local_original_case = formal_param_info['name']
                param_mode_for_evaluator = formal_param_info['mode_for_evaluator']

                if param_mode_for_evaluator in ['рез', 'arg_res', 'arg_res_table_special']:
                    local_var_info, _ = self.visitor.scope_manager.find_variable(param_name_local_original_case) 
                    if local_var_info is None: # pragma: no cover
                        lc_local_var = self.visitor.get_line_content_from_ctx(call_site_ctx)
                        raise KumirNameError(f"Внутренняя ошибка: локальная переменная параметра '{param_name_local_original_case}' не найдена.",
                                             line_index=(call_site_ctx.start.line-1) if call_site_ctx else None,
                                             column_index=call_site_ctx.start.column if call_site_ctx else None,
                                             line_content=lc_local_var)
                    
                    value_to_copy_back = local_var_info['value']
                    original_arg_spec = args[i] 

                    if isinstance(original_arg_spec, dict) and 'name_for_ref' in original_arg_spec:
                        original_var_name = original_arg_spec['name_for_ref']
                        original_var_scope_depth = original_arg_spec.get('scope_depth_for_ref') 
                        
                        try:
                            if original_var_scope_depth is not None and 0 <= original_var_scope_depth < len(self.visitor.scope_manager.scopes):
                                target_scope = self.visitor.scope_manager.scopes[original_var_scope_depth]
                                var_info_in_target_scope = target_scope.get(original_var_name.lower())

                                if not var_info_in_target_scope: # pragma: no cover
                                    lc_target_scope = self.visitor.get_line_content_from_ctx(call_site_ctx)
                                    raise KumirNameError(f"Переменная '{original_var_name}' для параметра '{param_name_local_original_case}' не найдена в целевой области видимости для обновления.",
                                                         line_index=(call_site_ctx.start.line -1) if call_site_ctx else None,
                                                         column_index=call_site_ctx.start.column if call_site_ctx else None,
                                                         line_content=lc_target_scope)

                                # For both table and scalar, we use _validate_and_convert_value_for_assignment from the visitor
                                validated_value_for_target = self.visitor._validate_and_convert_value_for_assignment(
                                    value_to_copy_back, # This is the value from the procedure's scope
                                    var_info_in_target_scope['type'],
                                    var_name=original_var_name
                                )
                                target_scope[original_var_name.lower()]['value'] = validated_value_for_target
                                target_scope[original_var_name.lower()]['initialized'] = True
                            else: # pragma: no cover
                                lc_scope_depth = self.visitor.get_line_content_from_ctx(call_site_ctx)
                                raise KumirEvalError(f"Ошибка обновления ссылочного параметра '{original_var_name}': некорректная глубина области видимости.",
                                                     line_index=(call_site_ctx.start.line -1) if call_site_ctx else None,
                                                     column_index=call_site_ctx.start.column if call_site_ctx else None,
                                                     line_content=lc_scope_depth)

                        except (KumirNameError, KumirTypeError, AssignmentError) as e: 
                            lc_copy_back = self.visitor.get_line_content_from_ctx(call_site_ctx)
                            self.visitor.error_stream.write(f"Внутренняя ошибка при копировании результата параметра '{param_name_local_original_case}' в '{original_var_name}' (строка {call_site_ctx.start.line if call_site_ctx else '??'}): {e}\\n")
                    elif isinstance(original_arg_spec, str): 
                        original_var_name = original_arg_spec
                        var_info_in_caller = caller_scope.get(original_var_name.lower())

                        if not var_info_in_caller: # pragma: no cover
                            lc_var_caller = self.visitor.get_line_content_from_ctx(call_site_ctx)
                            raise KumirNameError(f"Переменная '{original_var_name}' для 'рез' параметра не найдена в вызывающей области.",
                                                 line_index=(call_site_ctx.start.line -1) if call_site_ctx else None,
                                                 column_index=call_site_ctx.start.column if call_site_ctx else None,
                                                 line_content=lc_var_caller)
                        try:
                            validated_value_for_caller = self.visitor._validate_and_convert_value_for_assignment(
                                value_to_copy_back,
                                var_info_in_caller['type'],
                                original_var_name
                            )
                            caller_scope[original_var_name.lower()]['value'] = validated_value_for_caller
                            caller_scope[original_var_name.lower()]['initialized'] = True
                        except (KumirTypeError, KumirEvalError, AssignmentError) as e: 
                             lc_assign_res = self.visitor.get_line_content_from_ctx(call_site_ctx)
                             if not hasattr(e, 'line_index') or e.line_index is None: e.line_index = call_site_ctx.start.line -1 if call_site_ctx else None
                             if not hasattr(e, 'column_index') or e.column_index is None: e.column_index = call_site_ctx.start.column if call_site_ctx else None
                             if not hasattr(e, 'line_content') or e.line_content is None: e.line_content = lc_assign_res
                             raise
                    else: # pragma: no cover
                        arg_expr_ctx_for_error = call_site_ctx
                        # Safely try to get a more specific context for the argument
                        postfix_op = getattr(call_site_ctx, 'postfixOperator', lambda: None)()
                        if postfix_op:
                            arg_list_node = getattr(postfix_op, 'argumentList', lambda: None)()
                            if arg_list_node:
                                expressions = getattr(arg_list_node, 'expression', lambda: [])()
                                if i < len(expressions):
                                    arg_expr_ctx_for_error = expressions[i]
                        
                        lc_arg_mode = self.visitor.get_line_content_from_ctx(arg_expr_ctx_for_error)
                        err_line = arg_expr_ctx_for_error.start.line if arg_expr_ctx_for_error and hasattr(arg_expr_ctx_for_error, 'start') else None
                        err_col = arg_expr_ctx_for_error.start.column if arg_expr_ctx_for_error and hasattr(arg_expr_ctx_for_error, 'start') else None
                        raise KumirArgumentError(
                            f"Строка {err_line or '??'}: Для параметра '{param_name_local_original_case}' (режим '{param_mode_for_evaluator}') процедуры '{proc_name}' передан аргумент неподдерживаемого типа для обратного копирования ({type(original_arg_spec).__name__}).",
                            line_index=err_line -1 if err_line else None,
                            column_index=err_col,
                            line_content=lc_arg_mode
                        )
        
        self.visitor.scope_manager.pop_scope()
        self.visitor.function_call_active = False
        # print(f"[DEBUG][ProcManager] Exiting {proc_name}. Return value: {execution_result}", file=sys.stderr)
        return execution_result

    def _get_result_type(self, header_ctx: KumirParser.AlgorithmHeaderContext) -> Optional[str]:
        if header_ctx.RETURN_TYPE(): # Проверяем, что токен RETURN_TYPE существует
            all_type_specifiers = header_ctx.typeSpecifier() 
            actual_type_spec_ctx = None
            if isinstance(all_type_specifiers, list):
                if all_type_specifiers: 
                    actual_type_spec_ctx = all_type_specifiers[-1] 
            else: 
                actual_type_spec_ctx = all_type_specifiers
            
            if actual_type_spec_ctx:
                return_type_token_node = header_ctx.RETURN_TYPE() # Это TerminalNode
                error_line_for_return = return_type_token_node.getSymbol().line if return_type_token_node else header_ctx.start.line

                base_type, is_table = get_type_info_from_specifier(self.visitor, actual_type_spec_ctx)
                if is_table:
                    lc = self.visitor.get_line_content_from_ctx(actual_type_spec_ctx)
                    raise DeclarationError( 
                        f"Строка {error_line_for_return}: Функции не могут возвращать табличный тип '{base_type}таб'.",
                        line_index=error_line_for_return -1,
                        column_index=actual_type_spec_ctx.start.column,
                        line_content=lc
                    )
                return base_type
            else: 
                return_type_token_node_else = header_ctx.RETURN_TYPE() # Это TerminalNode
                error_line_for_return_else = return_type_token_node_else.getSymbol().line if return_type_token_node_else else header_ctx.start.line
                lc_else = self.visitor.get_line_content_from_ctx(header_ctx) 
                raise DeclarationError(
                    f"Строка {error_line_for_return_else}: Указан RETURN_TYPE, но не найден спецификатор типа возвращаемого значения.",
                    line_index=error_line_for_return_else -1,
                    column_index=header_ctx.start.column, 
                    line_content=lc_else
                )
        return None