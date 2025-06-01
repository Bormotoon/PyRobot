# Functions for managing user-defined procedures and functions (algorithms) 
import sys
from typing import Dict, Any, List, Optional, TYPE_CHECKING, Union, Tuple # <--- ДОБАВЛЕН Tuple, List, Optional (List, Optional уже были, Tuple добавлен)
from antlr4 import ParserRuleContext # Убрана TerminalNode, она импортируется ниже, если нужна
from antlr4.tree.Tree import TerminalNode # Импорт TerminalNode

# Локальные импорты КуМир (относительные)
from ..generated.KumirParser import KumirParser # Исправленный импорт KumirParser
from ..kumir_exceptions import DeclarationError, KumirArgumentError, KumirNameError, KumirTypeError, ExitSignal, AssignmentError, KumirEvalError, BreakSignal # Заменены ProcedureExitCalled на ExitSignal и LoopExitException на BreakSignal
from ..kumir_datatypes import KumirTableVar, KumirFunction, KumirValue, KumirType # <--- ДОБАВЛЕН KumirType
from .constants import VOID_TYPE, INTEGER_TYPE, FLOAT_TYPE, STRING_TYPE, BOOLEAN_TYPE 
from .scope_manager import get_default_value # <--- Import get_default_value
from .type_utils import get_type_info_from_specifier # <--- ДОБАВЛЕН ИМПОРТ

if TYPE_CHECKING:
    from ..interpreter import KumirInterpreterVisitor # Для тайп-хинтинга родительского визитора

class ProcedureManager:
    def __init__(self, visitor: 'KumirInterpreterVisitor'): # ИСПРАВЛЕНО: Убраны лишние \\'        self.visitor = visitor
        self.procedures: Dict[str, Dict[str, Any]] = {} # {name_lower: {name, ctx, params, is_func, result_type}}
        self._current_procedure_return_value: Optional[KumirValue] = None # Для хранения значения из "знач"
        
    def set_return_value(self, value_to_assign: Optional[KumirValue]) -> None:
        """
        Устанавливает возвращаемое значение для текущей выполняемой функции.
        Используется оператором 'знач'.
        """
        # TODO: Проверить, что мы находимся внутри вызова функции, а не процедуры.
        # TODO: Проверить тип value_to_assign с ожидаемым типом возврата функции.
        self._current_procedure_return_value = value_to_assign

    def register_procedure(self, name: str, ctx: KumirParser.AlgorithmDefinitionContext, 
                          is_function: bool = False, result_type: str = VOID_TYPE) -> None:
        """
        Регистрирует процедуру или функцию в менеджере процедур.
        """
        name_lower = name.lower()
        
        if name_lower in self.procedures:
            raise DeclarationError(f"Алгоритм с именем '{name}' уже определен.")
        
        self.procedures[name_lower] = {
            'name': name,
            'ctx': ctx,
            'params': {},  # TODO: извлечь параметры
            'is_func': is_function,
            'result_type': result_type
        }
        
        print(f"[DEBUG][ProcedureManager] Зарегистрирован алгоритм '{name}' (функция: {is_function})", file=sys.stderr)

    def call_procedure(self, proc_name: str, actual_args: List[Dict[str, Any]], 
                       line_index: int, column_index: int) -> None:
        """
        Вызывает процедуру (не функцию) по имени.
        actual_args - список словарей {'name': Optional[str], 'value': KumirValue, 'is_expression': bool, 'var_name_for_update': Optional[str]}
        """
        # TODO: Реализовать логику вызова процедуры, включая:
        # 1. Поиск определения процедуры.
        # 2. Проверку количества и типов аргументов.
        # 3. Обработку параметров 'арг', 'рез', 'арг рез'.
        # 4. Создание новой области видимости.
        # 5. Объявление параметров в новой области.
        # 6. Выполнение тела процедуры.
        # 7. Обработку 'арг рез' и 'рез' параметров после выполнения.
        # 8. Выход из области видимости.
        # 9. Обработку ошибок (KumirNameError, KumirArgumentError, KumirTypeError).
        
        # Заглушка
        print(f"[INFO][ProcedureManager] Заглушка: вызов процедуры {proc_name} с аргументами: {actual_args} на строке {line_index+1}, колонке {column_index+1}")
        # pass
        raise NotImplementedError(f"Вызов процедуры '{proc_name}' еще не реализован.")

    def is_function_defined(self, name: str) -> bool:
        """Проверяет, определена ли функция с таким именем."""
        name_lower = name.lower()
        # Проверяем, что запись существует, что это функция, и что у нее есть тип результата (не VOID_TYPE)
        proc_data = self.procedures.get(name_lower)
        if not proc_data:
            return False
        return proc_data.get('is_function', False) and proc_data.get('result_type') != VOID_TYPE

    def get_function_definition(self, name: str, error_ctx: Optional[ParserRuleContext] = None) -> KumirFunction:
        """
        Извлекает определение функции и возвращает объект KumirFunction.
        Выбрасывает KumirNameError, если функция не найдена или это не функция.
        """
        name_lower = name.lower()
        if not self.is_function_defined(name): # Используем обновленный is_function_defined
            lc = self.visitor.get_line_content_from_ctx(error_ctx) if error_ctx else "Неизвестная строка"
            line = error_ctx.start.line if error_ctx and hasattr(error_ctx, 'start') else -1
            col = error_ctx.start.column if error_ctx and hasattr(error_ctx, 'start') else -1
            
            # Проверим, существует ли вообще процедура/алгоритм с таким именем
            if name_lower in self.procedures:
                # Если существует, но это не функция (т.е. процедура)
                raise KumirTypeError(f"'{name}' является процедурой, а не функцией, и не может быть использована в выражении.",
                                     line_index=line -1 if line != -1 else None,
                                     column_index=col if col != -1 else None,
                                     line_content=lc)
            else:
                # Если вообще не определена
                raise KumirNameError(f"Функция '{name}' не определена.",
                                     line_index=line -1 if line != -1 else None,
                                     column_index=col if col != -1 else None,
                                     line_content=lc)

        proc_data = self.procedures[name_lower]
        # Дополнительная проверка, хотя is_function_defined уже должна была это покрыть
        if not proc_data.get('is_function', False) or proc_data.get('result_type') == VOID_TYPE: # pragma: no cover
            lc = self.visitor.get_line_content_from_ctx(error_ctx) if error_ctx else "Неизвестная строка"
            line = error_ctx.start.line if error_ctx and hasattr(error_ctx, 'start') else -1
            col = error_ctx.start.column if error_ctx and hasattr(error_ctx, 'start') else -1
            raise KumirTypeError(f"'{name}' не является функцией или не возвращает значение, и не может быть использована в выражении.",
                                 line_index=line -1 if line != -1 else None,
                                 column_index=col if col != -1 else None,
                                 line_content=lc)
        
        extracted_params = []
        for param_info_dict in proc_data['params'].values():
            extracted_params.append({
                "name": param_info_dict["name"],
                "type": param_info_dict["type"], 
                "mode": param_info_dict["mode"], 
                "is_table": param_info_dict["is_table"],
                "base_type": param_info_dict["base_type"],
            })

        return KumirFunction(
            name=proc_data['name'],
            parameters=extracted_params, 
            body_ctx=proc_data['body_ctx'],
            return_type=proc_data['result_type'], # Должен быть корректным после _collect_procedure_definitions
            scope_manager=self.visitor.scope_manager,
            # Инициализируем type_converter и error_handler из visitor'а
            type_converter=self.visitor.type_converter,
            error_handler=self.visitor.error_handler
        )

    def call_function(self, func_or_name: Union[str, KumirFunction], 
                      args: List[KumirValue], 
                      call_site_ctx: ParserRuleContext) -> KumirValue:
        """
        Вызывает функцию (по имени или объекту KumirFunction) с заданными аргументами.
        Возвращает KumirValue.
        """
        kumir_func_obj: KumirFunction
        original_func_name_for_error = "" # Для более точных сообщений об ошибках

        if isinstance(func_or_name, str):
            original_func_name_for_error = func_or_name
            kumir_func_obj = self.get_function_definition(func_or_name, call_site_ctx)
        elif isinstance(func_or_name, KumirFunction):
            kumir_func_obj = func_or_name
            original_func_name_for_error = kumir_func_obj.name
        else: # pragma: no cover
            lc_type_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
            line_type_err = call_site_ctx.start.line if call_site_ctx and hasattr(call_site_ctx, 'start') else -1
            col_type_err = call_site_ctx.start.column if call_site_ctx and hasattr(call_site_ctx, 'start') else -1
            raise KumirTypeError("Некорректный тип для func_or_name в call_function.",
                                 line_index=line_type_err -1 if line_type_err != -1 else None,
                                 column_index=col_type_err if col_type_err != -1 else None,
                                 line_content=lc_type_err)

        proc_data_from_dict = self.procedures.get(kumir_func_obj.name.lower())
        if not proc_data_from_dict: # pragma: no cover
            lc_name_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
            line_name_err = call_site_ctx.start.line if call_site_ctx and hasattr(call_site_ctx, 'start') else -1
            col_name_err = call_site_ctx.start.column if call_site_ctx and hasattr(call_site_ctx, 'start') else -1
            raise KumirNameError(f"Внутренняя ошибка: определение для функции '{kumir_func_obj.name}' не найдено в self.procedures.",
                                 line_index=line_name_err -1 if line_name_err != -1 else None,
                                 column_index=col_name_err if col_name_err != -1 else None,
                                 line_content=lc_name_err)

        formal_params_list = list(proc_data_from_dict['params'].values())

        if len(args) != len(formal_params_list):
            lc_arg_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
            line_arg_err = call_site_ctx.start.line
            col_arg_err = call_site_ctx.start.column
            raise KumirArgumentError(
                f"Неверное количество аргументов для функции '{original_func_name_for_error}'. Ожидается {len(formal_params_list)}, получено {len(args)}.",
                line_index=line_arg_err -1, column_index=col_arg_err, line_content=lc_arg_err
            )

        # Подготовка аргументов для _execute_procedure_call
        # Важно: _execute_procedure_call ожидает Python значения, а не KumirValue
        # Также он сам обрабатывает 'арг рез' и 'рез' параметры, модифицируя переданные значения (если они mutable)
        # или возвращая их в словаре (для immutable).
        # Для вызова функции из выражения, все параметры должны быть 'арг' по своей сути,
        # т.к. выражение не может изменять переменные во внешней области видимости.
        # KumirFunction.call уже должен был это проверить и подготовить.
        
        python_args_for_execute = []
        for i, arg_kv in enumerate(args):
            formal_param_info = formal_params_list[i]
            
            # Проверка типа аргумента относительно формального параметра
            # Используем type_converter из KumirFunction, который был инициализирован из visitor
            if not kumir_func_obj.type_converter.are_types_compatible_for_assignment(
                target_type_str=formal_param_info['type'], # тип формального параметра
                value_kumir_type=arg_kv.kumir_type,        # тип фактического аргумента
                value_py_type=type(arg_kv.value),
                is_table_target=formal_param_info['is_table']
            ):
                lc_type_mismatch = self.visitor.get_line_content_from_ctx(call_site_ctx)
                line_type_mismatch = call_site_ctx.start.line
                col_type_mismatch = call_site_ctx.start.column
                
                # Получаем имя параметра для сообщения об ошибке
                param_name_for_error = formal_param_info.get('name', f'параметр {{i+1}}') # Исправлено: {{i+1}} для f-строки внутри f-строки

                raise KumirTypeError(
                    f"Тип аргумента для параметра '{param_name_for_error}' функции '{original_func_name_for_error}' несовместим. "
                    f"Ожидался тип '{formal_param_info['type']}', получен '{arg_kv.kumir_type}'.",
                    line_index=line_type_mismatch -1, column_index=col_type_mismatch, line_content=lc_type_mismatch
                )

            # Если параметр 'арг рез' или 'рез', а мы вызываем функцию из выражения, это ошибка.
            # KumirFunction.call должен был бы это отловить раньше, но дублирующая проверка не помешает.
            if formal_param_info['mode'] in ['рез', 'арг рез']: # pragma: no cover
                # Это не должно происходить, если KumirFunction.call работает правильно
                lc_mode_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
                raise KumirEvalError(f"Внутренняя ошибка: функция '{original_func_name_for_error}' с параметром '{formal_param_info['name']}' режима '{formal_param_info['mode']}' не может быть вызвана из выражения.",
                                     line_index=call_site_ctx.start.line -1, column_index=call_site_ctx.start.column, line_content=lc_mode_err)

            python_args_for_execute.append(arg_kv.value)


        # Вызов _execute_procedure_call, который выполняет тело процедуры/функции
        # и возвращает Python значение (или None для процедур)
        raw_return_value = self._execute_procedure_call(proc_data_from_dict, python_args_for_execute, call_site_ctx)

        return_type_str = kumir_func_obj.return_type # Это тип, который функция ОБЪЯВИЛА, что вернет
        
        if return_type_str is None or return_type_str == VOID_TYPE: # pragma: no cover
             # Это не должно произойти, т.к. get_function_definition отфильтровывает такие случаи
             lc_void_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
             raise KumirTypeError(f"Процедура '{original_func_name_for_error}' не может быть использована в выражении, так как не возвращает значение.",
                                  line_index=call_site_ctx.start.line -1, column_index=call_site_ctx.start.column, line_content=lc_void_err)

        # Преобразование и проверка возвращаемого значения
        try:
            expected_kumir_type_enum = KumirType.from_string(return_type_str)
            if expected_kumir_type_enum == KumirType.UNKNOWN: # pragma: no cover
                lc_ret_type_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
                raise KumirTypeError(
                    f"Функция '{original_func_name_for_error}' объявлена с неизвестным или неподдерживаемым типом возврата: '{return_type_str}'.",
                    line_index=call_site_ctx.start.line -1, column_index=call_site_ctx.start.column, line_content=lc_ret_type_err
                )

            # Проверяем, соответствует ли Python-тип возвращенного значения ожидаемому Kumir-типу
            if not kumir_func_obj.type_converter.is_python_type_compatible_with_kumir_type(
                raw_return_value, expected_kumir_type_enum.value # Используем .value для получения строки типа "ЦЕЛ", "ВЕЩ" и т.д.
            ):
                lc_ret_type_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
                actual_value_str_for_error = raw_return_value
                if hasattr(kumir_func_obj, 'error_handler') and kumir_func_obj.error_handler and hasattr(kumir_func_obj.error_handler, 'format_value_for_error'):
                    actual_value_str_for_error = kumir_func_obj.error_handler.format_value_for_error(raw_return_value)
                elif hasattr(kumir_func_obj, 'type_converter') and kumir_func_obj.type_converter and hasattr(kumir_func_obj.type_converter, 'to_string_for_error'):
                    actual_value_str_for_error = kumir_func_obj.type_converter.to_string_for_error(raw_return_value)

                raise KumirTypeError(
                    f"Функция '{original_func_name_for_error}' вернула значение типа, несовместимого с объявленным типом '{return_type_str}'. "
                    f"Получено значение: {actual_value_str_for_error} (Python тип: {type(raw_return_value).__name__}).",
                    line_index=call_site_ctx.start.line -1, column_index=call_site_ctx.start.column, line_content=lc_ret_type_err
                )

            # Если все хорошо, создаем KumirValue
            return KumirValue(raw_return_value, return_type_str)

        except KumirTypeError as e: # Перехватываем ошибки совместимости типов
            # Дополняем ошибку информацией о контексте вызова, если ее еще нет
            if not (hasattr(e, 'line_index') and e.line_index is not None): # pragma: no cover
                e.line_index = call_site_ctx.start.line -1
                e.column_index = call_site_ctx.start.column
                e.line_content = self.visitor.get_line_content_from_ctx(call_site_ctx)
            raise
        except Exception as e: # pragma: no cover
            # Обработка другихunexpected ошибок при создании KumirValue
            lc_internal_err = self.visitor.get_line_content_from_ctx(call_site_ctx)
            raise KumirEvalError(f"Внутренняя ошибка при обработке результата функции '{original_func_name_for_error}': {e}",
                                 line_index=call_site_ctx.start.line -1, column_index=call_site_ctx.start.column, line_content=lc_internal_err)


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

    def _get_result_type(self, header_ctx: KumirParser.AlgorithmHeaderContext) -> Optional[str]:
        """
        Определяет тип результата функции на основе typeSpecifier в заголовке.
        Возвращает строку типа КуМир (например, INTEGER_TYPE) или VOID_TYPE, если это процедура.
        """
        type_spec_ctx = header_ctx.typeSpecifier()
        if type_spec_ctx:
            try:
                # get_type_info_from_specifier возвращает (base_kumir_type, is_table_type)
                # Функции в КуМире не могут возвращать таблицы целиком, только значения базовых типов.
                # Поэтому нас интересует только base_kumir_type.
                base_kumir_type, _ = get_type_info_from_specifier(self.visitor, type_spec_ctx)
                return base_kumir_type
            except DeclarationError as e:
                # Перевыбрасываем ошибку, добавляя контекст из header_ctx, если его нет
                if not (hasattr(e, 'line_index') and e.line_index is not None): # pragma: no cover
                    line = header_ctx.start.line
                    col = header_ctx.start.column
                    lc = self.visitor.get_line_content_from_ctx(header_ctx)
                    raise DeclarationError(str(e.args[0] if e.args else "Ошибка определения типа результата функции"),
                                         line_index=line-1, 
                                         column_index=col, 
                                         line_content=lc) from e
                else: # pragma: no cover
                    raise
        return VOID_TYPE # Если typeSpecifier отсутствует, это процедура

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
                original_decl_line = self.procedures[name_lower]['header_ctx'].start.line # Используем header_ctx для более точной строки
                new_decl_line = header_ctx.start.line
                lc = self.visitor.get_line_content_from_ctx(header_ctx)
                raise DeclarationError(f"Строка {new_decl_line}: Алгоритм с именем '{name}' уже определен ранее на строке {original_decl_line}.", line_index=new_decl_line-1, column_index=header_ctx.start.column, line_content=lc)

            params_info = self._extract_parameters(header_ctx)
            
            # Определяем тип результата и является ли это функцией
            result_type = self._get_result_type(header_ctx) # Теперь _get_result_type возвращает VOID_TYPE для процедур
            is_function = result_type != VOID_TYPE
            
            self.procedures[name_lower] = {
                'name': name,
                'params': params_info,
                'is_function': is_function,
                'result_type': result_type if is_function else VOID_TYPE, # Сохраняем VOID_TYPE для процедур
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
        except ExitSignal: 
            pass 
        except BreakSignal as lee: 
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

    def _get_type_info_from_specifier(self, type_spec_ctx: KumirParser.TypeSpecifierContext) -> Tuple[str, Optional[List[Tuple[Optional[int], Optional[int]]]]]:
        if not self.visitor:
            # Это критическая ошибка конфигурации, если visitor не установлен к моменту вызова
            raise Exception("ProcedureManager.visitor не инициализирован, но требуется для _get_type_info_from_specifier")
        
        # Делегируем вызов методу из TypeUtilsMixin (или где он там будет) через visitor
        return self.visitor.get_type_info_from_specifier(type_spec_ctx)


# ... остальной код класса ...
# Например, visitProcedureCallStatement и другие методы, если они здесь остаются.
# Если _execute_procedure_call используется только для функций через call_function,
# то его логика для процедур (обработка modified_params) может быть не нужна в этом контексте.
# Однако, если он также будет вызываться для обычных процедурных вызовов (не из выражений),
# то эта логика важна.

# В контексте текущей задачи (вызов функций из выражений), _execute_procedure_call
# должен корректно обрабатывать возврат значения из функции и проверять типы.
# Логика обработки 'арг рез' и 'рез' для функций, вызываемых из выражений,
# должна быть такой, чтобы предотвращать их использование или вызывать ошибку,
# так как функции в выражениях не должны иметь побочных эффектов на внешние переменные.