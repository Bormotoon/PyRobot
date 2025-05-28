\
# filepath: c:\\Users\\Bormotoon\\VSCodeProjects\\PyRobot\\pyrobot\\backend\\kumir_interpreter\\interpreter_components\\main_visitor.py
import sys
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import ParserRuleContext, TerminalNode, Token # Для ctx.toStringTree() и проверки типа узла
from typing import Any, List, Dict, Optional, Callable, Tuple, cast

# Локальные импорты КуМир (относительные)
from ..generated.KumirLexer import KumirLexer
from ..generated.KumirParser import KumirParser
from ..generated.KumirParserVisitor import KumirParserVisitor # Базовый визитор ANTLR
from .. import kumir_exceptions # <--- Добавляем импорт модуля исключений
from ..kumir_exceptions import KumirSemanticError, KumirRuntimeError, KumirSyntaxError, ExitSignal, BreakSignal, StopExecutionSignal, KumirNameError, KumirTypeError # Изменения: ProcedureExitCalled -> ExitSignal, LoopExitException -> BreakSignal
from ..kumir_datatypes import KumirTableVar, KumirReturnValue 

# Импорты компонентов интерпретатора из __init__.py текущего пакета
from .scope_manager import ScopeManager
from .procedure_manager import ProcedureManager
from .expression_evaluator import ExpressionEvaluator
from .declaration_visitors import DeclarationVisitorMixin
from .statement_visitors import StatementVisitorMixin
from .control_flow_visitors import ControlFlowVisitorMixin
from .io_handler import IOHandler
from .builtin_handlers import BuiltinFunctionHandler, BuiltinProcedureHandler
from .constants import (
    VOID_TYPE, DEFAULT_PRECISION, TYPE_MAP, 
    INTEGER_TYPE, FLOAT_TYPE, BOOLEAN_TYPE, CHAR_TYPE, STRING_TYPE
) 
from .type_utils import get_type_info_from_specifier # <--- ИМПОРТ УЖЕ БЫЛ, ПРОВЕРЯЕМ

class DiagnosticErrorListener(ErrorListener):
    def __init__(self, error_stream_writer=None):
        super().__init__()
        self.errors: List[KumirSyntaxError] = []
        self.error_stream_writer = error_stream_writer

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Сохраняем информацию о строке, где произошла ошибка
        # recognizer.getInputStream() дает поток токенов, нам нужен исходный текст, если доступен
        # Обычно recognizer - это парсер, у него есть _input - поток токенов,
        # а у потока токенов есть tokenSource, у которого есть inputStream - поток символов.
        # Но проще получить строки из KumirInterpreterVisitor, если он их хранит.
        # Пока оставим None, если не сможем получить.
        line_content = None 
        
        # Формируем сообщение об ошибке
        error_message = f"Синтаксическая ошибка: {msg}"
        ks_error = KumirSyntaxError(error_message, line_index=line - 1, column_index=column, line_content=line_content)
        self.errors.append(ks_error)
        if self.error_stream_writer:
            # Проверяем, есть ли у error_stream_writer метод write
            if hasattr(self.error_stream_writer, 'write') and callable(self.error_stream_writer.write):
                self.error_stream_writer.write(f"Ошибка в строке {line}, позиция {column}: {msg}\\\\n")
            else:
                # Если нет, используем print или другой механизм
                print(f"Ошибка в строке {line}, позиция {column}: {msg}", file=__import__('sys').stderr) 

    def get_errors(self) -> List[KumirSyntaxError]:
        return self.errors

class KumirInterpreterVisitor(DeclarationVisitorMixin, StatementVisitorMixin, ControlFlowVisitorMixin, KumirParserVisitor): 
    def __init__(self, input_stream: Optional[Callable[[], str]] = None, 
                 output_stream: Optional[Callable[[str], None]] = None,
                 error_stream: Optional[Callable[[str], None]] = None, # Callable, а не SupportsWrite
                 program_lines: Optional[List[str]] = None,
                 global_vars: Optional[Dict[str, Any]] = None,
                 precision: int = DEFAULT_PRECISION,
                 echo_input: bool = True):
        super().__init__() 
        
        # Добавляем константы типов как атрибуты для использования в type_utils
        self.TYPE_MAP = TYPE_MAP
        self.INTEGER_TYPE = INTEGER_TYPE
        self.FLOAT_TYPE = FLOAT_TYPE
        self.BOOLEAN_TYPE = BOOLEAN_TYPE
        self.CHAR_TYPE = CHAR_TYPE
        self.STRING_TYPE = STRING_TYPE
        
        self.program_lines = program_lines if program_lines is not None else []
        self.precision = precision
        self.kumir_exceptions = kumir_exceptions # Сохраняем модуль для передачи в IOHandler

        self.scope_manager = ScopeManager(self)
        self.procedure_manager = ProcedureManager(self)
        self.expression_evaluator = ExpressionEvaluator(self, self.scope_manager, self.procedure_manager) # Передаем self (main_visitor)
        
        # Создаем IOHandler, передавая модуль исключений и потоки. Visitor будет None сначала.
        self.io_handler = IOHandler(
            kumir_exceptions_module=self.kumir_exceptions, 
            visitor=None, # Visitor будет установлен позже
            input_stream=input_stream, 
            output_stream=output_stream,
            error_stream=error_stream # error_stream уже есть в конструкторе KumirInterpreterVisitor
        )
        self.io_handler.set_visitor(self) # Устанавливаем visitor в IOHandler

        self.builtin_function_handler = BuiltinFunctionHandler(self) # Предполагаем наличие
        self.builtin_procedure_handler = BuiltinProcedureHandler(self) # Предполагаем наличие        self.error_stream_out = error_stream if error_stream else lambda x: print(x, file=__import__('sys').stderr) # Используем правильные кавычки
        
        # Настройка эхо ввода (автоматический вывод введённых значений)
        self.echo_input = echo_input
        
        self.current_algorithm_name: Optional[str] = None
        self.current_algorithm_is_function: bool = False
        self.current_algorithm_result_type: Optional[str] = None
        self.return_value: Optional[KumirReturnValue] = None 
        self.stop_execution_flag = False
        self.function_call_active: bool = False # ДОБАВЛЕНО

        if global_vars:
            for name, value_info in global_vars.items():
                self.scope_manager.scopes[0][name.lower()] = {'value': value_info, 'type': 'глоб_неизв', 'is_table': False, 'dimensions': None, 'initialized': True}

    def _validate_and_convert_value_for_assignment(self, value: Any, target_kumir_type: str, var_name: str, is_target_table: bool, element_type: Optional[str] = None) -> Any:
        # TODO: Implement actual validation and conversion logic based on the original interpreter.
        # This is a placeholder.
        # Basic type checking and conversion can be added here.
        # For now, just return the value as is.
        # print(f"[DEBUG VALIDATE] var: {var_name}, value: {value} ({type(value)}), target_type: {target_kumir_type}, is_table: {is_target_table}, element_type: {element_type}")
        
        # Placeholder logic:
        # if target_kumir_type == "цел":
        #     if not isinstance(value, int):
        #         try:
        #             return int(value)
        #         except ValueError:
        #             raise KumirTypeError(f"Невозможно преобразовать значение '{value}' к типу ЦЕЛ для переменной '{var_name}'.")
        # elif target_kumir_type == "вещ":
        #     if not isinstance(value, (int, float)):
        #         try:
        #             return float(value)
        #         except ValueError:
        #             raise KumirTypeError(f"Невозможно преобразовать значение '{value}' к типу ВЕЩ для переменной '{var_name}'.")
        # elif target_kumir_type == "лог":
        #     if not isinstance(value, bool):
        #         raise KumirTypeError(f"Значение для переменной '{var_name}' (ЛОГ) должно быть логическим, получено: {value}.")
        # elif target_kumir_type == "сим":
        #     if not isinstance(value, str) or len(value) != 1:
        #         # Allow conversion from int 0-255 or other types if appropriate for Kumir
        #         pass # For now, no strict check
        # elif target_kumir_type == "лит":
        #     if not isinstance(value, str):
        #         try:
        #             return str(value)
        #         except:
        #             raise KumirTypeError(f"Невозможно преобразовать значение '{value}' к типу ЛИТ для переменной '{var_name}'.")
        
        # If it's a table, the 'value' might be a KumirTableVar or a list of values.
        # The 'element_type' would be relevant here if we were initializing/assigning individual elements.
        return value

    def get_line_content_from_ctx(self, ctx: Optional[ParserRuleContext]) -> Optional[str]:
        if ctx and hasattr(ctx, 'start') and self.program_lines:
            line_num_0_indexed = ctx.start.line - 1
            if 0 <= line_num_0_indexed < len(self.program_lines):
                return self.program_lines[line_num_0_indexed]
        return None

    # ДОБАВЛЕНО: Методы для связи с IOHandler
    def get_input_line(self, prompt: str) -> str:
        if not self.io_handler: # pragma: no cover
            raise KumirRuntimeError("IOHandler не инициализирован.")
        return self.io_handler.get_input_line(prompt)

    def write_output(self, text: str) -> None:
        if not self.io_handler: # pragma: no cover
            raise KumirRuntimeError("IOHandler не инициализирован.")
        self.io_handler.write_output(text)
    # КОНЕЦ ДОБАВЛЕННЫХ МЕТОДОВ

    # Основной метод для запуска интерпретации с корневого узла (program)    
    def visitProgram(self, ctx: KumirParser.ProgramContext):
        print(f"\n!!! [DEBUG main_visitor.visitProgram] CALLED! Context: {ctx.getText()[:100]}... !!!", file=sys.stderr)
        
        # DEBUG: расширенная отладка
        with open("debug_interpret.log", "a", encoding="utf-8") as f:
            f.write(f"visitProgram: ctx has {len(ctx.children) if ctx.children else 0} children\n")
            if ctx.children:
                for i, child in enumerate(ctx.children):
                    f.write(f"  Child {i}: {type(child).__name__} = {child.getText()[:50]}\n")
            
            f.write(f"ctx.programItem() count: {len(ctx.programItem()) if ctx.programItem() else 0}\n")
            f.write(f"ctx.moduleDefinition() count: {len(ctx.moduleDefinition()) if ctx.moduleDefinition() else 0}\n")
        
        # Обработка глобальных объявлений и присваиваний (programItem*)
        if ctx.programItem():
            for item_ctx in ctx.programItem():
                self.visit(item_ctx) # Это вызовет visitGlobalDeclaration, visitGlobalAssignment, visitImportStatement

        # Обработка определений модулей/алгоритмов (moduleDefinition+)
        # В КуМир обычно один "главный" алгоритм или модуль без явного вызова.
        # Если есть алгоритм "главный" или единственный, его можно было бы запустить.
        # Пока просто обходим все определения.
        
        # Сначала соберем все определения алгоритмов
        # Это важно, чтобы процедуры были известны до их вызова
        if ctx.moduleDefinition():
            for mod_def_ctx in ctx.moduleDefinition():
                # DEBUG: 
                with open("debug_interpret.log", "a", encoding="utf-8") as f:
                    f.write(f"Processing moduleDefinition: {mod_def_ctx.getText()[:100]}\n")
                    f.write(f"  has implicitModuleBody: {mod_def_ctx.implicitModuleBody() is not None}\n")
                    f.write(f"  has moduleBody: {mod_def_ctx.moduleBody() is not None}\n")
                
                if mod_def_ctx.implicitModuleBody():
                    with open("debug_interpret.log", "a", encoding="utf-8") as f:
                        f.write(f"  Processing implicitModuleBody\n")
                        f.write(f"    algorithmDefinition count: {len(mod_def_ctx.implicitModuleBody().algorithmDefinition()) if mod_def_ctx.implicitModuleBody().algorithmDefinition() else 0}\n")
                    
                    if mod_def_ctx.implicitModuleBody().algorithmDefinition():
                        for alg_def_ctx in mod_def_ctx.implicitModuleBody().algorithmDefinition():
                            with open("debug_interpret.log", "a", encoding="utf-8") as f:
                                f.write(f"      Calling visitAlgorithmDefinition for: {alg_def_ctx.getText()[:50]}\n")
                            self.visitAlgorithmDefinition(alg_def_ctx) # Собираем информацию
                elif mod_def_ctx.moduleBody(): # Явный модуль
                    with open("debug_interpret.log", "a", encoding="utf-8") as f:
                        f.write(f"  Processing explicit moduleBody\n")
                    if mod_def_ctx.moduleBody().algorithmDefinition():
                        for alg_def_ctx in mod_def_ctx.moduleBody().algorithmDefinition():
                            with open("debug_interpret.log", "a", encoding="utf-8") as f:
                                f.write(f"      Calling visitAlgorithmDefinition for: {alg_def_ctx.getText()[:50]}\n")
                            self.visitAlgorithmDefinition(alg_def_ctx) # Собираем информацию
        
        # Ищем "главный" алгоритм для выполнения или первый попавшийся, если "главного" нет
        # В простом случае без явного "главного" алгоритма, КуМир может ничего не выполнять,
        # если это просто набор процедур. Для тестов нам нужен какой-то вход.
        # Пока что не будем автоматически запускать алгоритмы здесь.
        # Запуск будет инициироваться извне через execute_algorithm_node или interpret_kumir.

        return None # visitProgram обычно ничего не возвращает

    def visitImplicitModuleBody(self, ctx: KumirParser.ImplicitModuleBodyContext):
        # print("[DEBUG] Visiting ImplicitModuleBody")
        # self.procedure_manager._collect_procedure_definitions(ctx) # TODO: Implement or move

        # Обработка programItem и algorithmDefinition внутри неявного модуля
        # Порядок важен: сначала объявления, потом определения алгоритмов, потом выполнение (если есть точка входа)
        
        # Сначала обрабатываем все programItem (глобальные переменные, импорты)
        if ctx.programItem():
            for item_ctx in ctx.programItem():
                self.visit(item_ctx)
        
        # Затем "регистрируем" все определения алгоритмов (но не выполняем их тела)
        # Это уже сделано на уровне visitProgram или будет сделано при прямом вызове visitAlgorithmDefinition
        # if ctx.algorithmDefinition():
        #     for alg_def_ctx in ctx.algorithmDefinition():
        #         self.visitAlgorithmDefinition(alg_def_ctx) # Только сбор информации

        # Выполнение кода внутри implicitModuleBody (если это не определения алгоритмов)
        # В КуМире код "вне" алгоритмов обычно не выполняется, кроме глобальных присваиваний.
        # Если бы здесь были "свободные" операторы, их нужно было бы посетить.
        # Но грамматика implicitModuleBody: (programItem | algorithmDefinition)+
        # не предполагает "свободных" операторов.
        return None

    # Метод для выполнения конкретного узла алгоритма (например, "главного")
    def execute_algorithm_node(self, alg_name: str, args: Optional[List[Any]] = None):
        # print(f"[DEBUG] Attempting to execute algorithm: {alg_name} with args: {args}")
        alg_name_lower = alg_name.lower()
        if alg_name_lower not in self.procedure_manager.procedures:
            # Попробуем найти его, если он еще не был "собран"
            # Это может произойти, если visitProgram/visitImplicitModuleBody не были вызваны или не нашли его
            # Для этого нам нужен контекст всего дерева. Предположим, он сохранен.
            # Это сложный сценарий, пока что будем считать, что процедура должна быть известна.
            raise KumirRuntimeError(f"Алгоритм '{alg_name}' не найден.")

        proc_info = self.procedure_manager.procedures[alg_name_lower]
        alg_ctx = proc_info['ctx'] # Это AlgorithmDefinitionContext

        if not isinstance(alg_ctx, KumirParser.AlgorithmDefinitionContext): # pragma: no cover
            raise KumirRuntimeError(f"Контекст для алгоритма '{alg_name}' не является AlgorithmDefinitionContext.")

        # Устанавливаем текущее имя алгоритма и флаг функции
        self.current_algorithm_name = proc_info['name']
        self.current_algorithm_is_function = proc_info['is_func']
        self.current_algorithm_result_type = proc_info.get('result_type')
        self.return_value = None # Сбрасываем предыдущее значение

        # Создаем новую область видимости для параметров и локальных переменных алгоритма
        self.scope_manager.enter_scope() 
        
        try:
            # Логика подготовки параметров и 'знач' (если функция) теперь в DeclarationVisitorMixin.visitAlgorithmDefinition
            # или должна быть вызвана здесь перед visit(alg_ctx.algorithmBody())
            # DeclarationVisitorMixin.visitAlgorithmDefinition должен был уже быть вызван (в visitProgram)
            # для сбора информации. Теперь нам нужно "активировать" область видимости и параметры.
            
            # Это часть логики из DeclarationVisitorMixin, адаптированная для вызова:
            # 1. Установить параметры в текущую область видимости
            # self.procedure_manager._setup_parameters_for_call(proc_info, args, alg_ctx.algorithmHeader())
            # 2. Инициализировать 'знач' для функций
            # if self.current_algorithm_is_function:
            #    self._setup_function_return_variable(alg_ctx.algorithmHeader())
            # Эти шаги должны быть частью visitAlgorithmDefinition при выполнении, а не только при сборе.
            # Пока что положимся на то, что DeclarationVisitorMixin правильно управляет этим при вызове.
            # Или, если DeclarationVisitorMixin.visitAlgorithmDefinition только собирает, то здесь нужна логика.
            
            # Пересмотренная логика: visitAlgorithmDefinition из миксина отвечает за создание области для параметров
            # и локальных переменных при первом проходе (сбор информации). 
            # При execute_algorithm_node мы повторно не вызываем visitAlgorithmDefinition целиком,
            # а только его часть, ответственную за выполнение тела.
            # Однако, параметры и '
            
            # --- Начало секции, которая может дублировать или должна быть в DeclarationVisitorMixin --- 
            # Установка параметров в текущую область
            actual_params = proc_info.get('params', {})
            if args:
                # TODO: Проверка количества и типов аргументов
                # ... (эта логика есть в _execute_procedure_call старого интерпретатора)
                pass
            
            # Инициализация 'знач' для функций
            if self.current_algorithm_is_function and self.current_algorithm_result_type and self.current_algorithm_result_type != VOID_TYPE:
                try:
                    is_table_check = False
                    # current_algorithm_result_type здесь точно строка и не VOID_TYPE
                    # Поэтому дополнительная проверка на isinstance(self.current_algorithm_result_type, str) не нужна.
                    is_table_check = 'таб' in self.current_algorithm_result_type
                    
                    self.scope_manager.declare_variable(
                        name='знач',
                        kumir_type=self.current_algorithm_result_type, # current_algorithm_result_type здесь гарантированно str
                        is_table= is_table_check, 
                        ctx_declaration_item=alg_ctx.algorithmHeader()
                    )
                except KumirNameError: 
                    pass 
            # --- Конец секции --- 

            # 2. Посещение тела алгоритма (нач ... кон)
            # visitAlgorithmDefinition отвечает за парсинг заголовка и параметров.
            # Нам нужно выполнить именно тело.
            if alg_ctx.algorithmBody(): # Проверяем, что тело существует
                 self.visit(alg_ctx.algorithmBody()) # Это вызовет visitAlgorithmBody
            else: # pragma: no cover
                # Алгоритм без тела (только заголовок) - это странно, но возможно по грамматике
                pass # Ничего не делаем

            # 3. Получение и возврат результата для функций
            if self.current_algorithm_is_function:
                if self.return_value is None and self.current_algorithm_result_type != VOID_TYPE:
                    # Если функция должна была вернуть значение, но не сделала этого через 'знач :='
                    # или если 'знач' не было присвоено.
                    # В КуМире это может быть ошибкой времени выполнения или поведением по умолчанию.
                    # Для некоторых типов может быть значение по умолчанию.
                    # Пока что будем считать, что если return_value is None, то функция вернула "пустоту"
                    # или неявно вернула значение по умолчанию для своего типа.
                    # Если тип VOID_TYPE, то все нормально.
                    # Если не VOID_TYPE, то это может быть ошибка, если 'знач' не было присвоено.
                    # Однако, 'знач' может быть инициализировано по умолчанию при входе в функцию.
                    # Это поведение обрабатывается в visitAlgorithmDefinition -> _setup_function_return_variable
                    
                    # Проверяем, было ли значение 'знач' установлено
                    # (оно хранится в текущей области видимости)
                    # print(f"[DEBUG] Function {self.current_algorithm_name} finishing. Return value obj: {self.return_value}")
                    
                    # Ищем 'знач' в текущей области видимости
                    znach_val_info = self.scope_manager.lookup_variable('знач', alg_ctx) # Используем alg_ctx для контекста ошибки
                    if znach_val_info:
                        # print(f"[DEBUG] 'знач' found in scope: {znach_val_info}")
                        # Убедимся, что тип соответствует
                        # expected_type = self.current_algorithm_result_type
                        # actual_type = znach_val_info['type'] # TODO: get actual type of value
                        # if not self.type_checker.check_type_compatibility(expected_type, actual_type, znach_val_info['value']):
                        #    raise KumirTypeError(...)
                        return KumirReturnValue(value=znach_val_info['value'], type=znach_val_info['type']) # Возвращаем KumirReturnValue
                    elif self.current_algorithm_result_type != VOID_TYPE:
                        # Если 'знач' не найдено и тип не VOID, это проблема
                        raise KumirRuntimeError(f"Функция '{self.current_algorithm_name}' должна вернуть значение, но 'знач' не было присвоено или найдено.",
                                                line_index=alg_ctx.ALG_END().symbol.line -1 if alg_ctx.ALG_END() else None,
                                                column_index=alg_ctx.ALG_END().symbol.column if alg_ctx.ALG_END() else None,
                                                line_content=self.get_line_content_from_ctx(alg_ctx)
                                                )
                    else: # VOID_TYPE
                        return KumirReturnValue(value=None, type=VOID_TYPE)

                elif self.return_value is not None:
                    # print(f"[DEBUG] Function {self.current_algorithm_name} returning explicit value: {self.return_value.value} of type {self.return_value.type}")
                    return self.return_value # Уже KumirReturnValue
                else: # self.return_value is None and self.current_algorithm_result_type == VOID_TYPE
                    return KumirReturnValue(value=None, type=VOID_TYPE)
            else: # Процедура
                return None # Процедуры ничего не возвращают (кроме как через параметры 'рез')

        except ExitSignal: # Перехватываем ВЫХОД из процедуры/функции
            # print(f"[DEBUG] ProcedureExitCalled caught in execute_algorithm_node for {self.current_algorithm_name}")
            if self.current_algorithm_is_function:
                # Если это функция, и она должна была вернуть значение, но был ВЫХОД
                # Нужно проверить, было ли присвоено 'знач'
                znach_val_info = self.scope_manager.lookup_variable('знач', alg_ctx)
                if znach_val_info:
                    return KumirReturnValue(value=znach_val_info['value'], type=znach_val_info['type'])
                elif self.current_algorithm_result_type != VOID_TYPE:
                     raise KumirRuntimeError(f"Функция '{self.current_algorithm_name}' завершилась оператором ВЫХОД до присваивания значения 'знач'.",
                                            line_index=alg_ctx.ALG_END().symbol.line -1 if alg_ctx.ALG_END() else None, 
                                            column_index=alg_ctx.ALG_END().symbol.column if alg_ctx.ALG_END() else None,
                                            line_content=self.get_line_content_from_ctx(alg_ctx)
                                            )
                else: # VOID_TYPE
                    return KumirReturnValue(value=None, type=VOID_TYPE)
            return None # Для процедур ВЫХОД просто завершает выполнение
        except StopExecutionSignal:
            # print("[DEBUG] StopExecutionSignal caught by execute_algorithm_node, re-raising.")
            self.stop_execution_flag = True # Устанавливаем флаг
            raise # Передаем сигнал выше, чтобы остановить всю программу
        finally:
            # print(f"[DEBUG] Exiting scope for algorithm: {self.current_algorithm_name}")
            self.scope_manager.exit_scope()
            self.current_algorithm_name = None # Сбрасываем состояние
            self.current_algorithm_is_function = False
            self.current_algorithm_result_type = None
            # self.return_value = None # Не сбрасываем здесь, т.к. он может быть результатом


    # visitAlgorithmDefinition - теперь в DeclarationVisitorMixin
    # def visitAlgorithmDefinition(self, ctx: KumirParser.AlgorithmDefinitionContext):
    #     # Логика перенесена в DeclarationVisitorMixin
    #     # Этот метод теперь вызывается из миксина через super() или напрямую
    #     return super().visitAlgorithmDefinition(ctx)


    def visitAlgorithmBody(self, ctx: KumirParser.AlgorithmBodyContext):
        # print(f"[DEBUG] Visiting AlgorithmBody for: {self.current_algorithm_name}")
        # Область видимости для параметров и 'знач' уже должна быть создана
        # в visitAlgorithmDefinition (через DeclarationVisitorMixin)
        # или в execute_algorithm_node (для "главного" алгоритма).

        # Локальные переменные алгоритма объявляются в его теле (после 'нач', перед операторами)
        # Эти объявления обрабатываются visitVariableDeclaration, который вызывается при обходе statementSequence.
        # Поэтому отдельный вход в область видимости здесь не нужен, если он уже был для параметров.
        # Однако, если это тело "главного" алгоритма, вызванного через execute_algorithm_node,
        # то execute_algorithm_node уже создал область.

        # Если DeclarationVisitorMixin.visitAlgorithmDefinition создала область для параметров,
        # то здесь мы находимся внутри этой области. Локальные переменные будут добавлены в нее же.
        
        # Если это тело алгоритма (нач ... кон), то оно выполняется в своей области видимости.
        # Эта область создается в DeclarationVisitorMixin.visitAlgorithmDefinition (для параметров и 'знач')
        # и затем используется для локальных переменных.
        # self.scope_manager.enter_scope() # <--- УБРАНО, т.к. область уже должна быть создана

        # Посещаем последовательность операторов
        if ctx.statementSequence(): # Убедимся, что есть что посещать
            self.visit(ctx.statementSequence())

        # self.scope_manager.exit_scope() # <--- УБРАНО, выход из области делается в конце visitAlgorithmDefinition или execute_algorithm_node
        return None # Тело алгоритма само по себе ничего не возвращает

    # visitVariableDeclaration - теперь в DeclarationVisitorMixin
    # def visitVariableDeclaration(self, ctx: KumirParser.VariableDeclarationContext):
    #     # Логика перенесена в DeclarationVisitorMixin
    #     return super().visitVariableDeclaration(ctx)

    # _get_type_info_from_specifier - теперь в type_utils.py и используется в DeclarationVisitorMixin
    # def _get_type_info_from_specifier(self, type_spec_ctx: KumirParser.TypeSpecifierContext) -> Tuple[str, bool]:
    #     # Логика перенесена
    #     pass

    # Методы для выражений (будут делегированы ExpressionEvaluator)
    def visitExpression(self, ctx: KumirParser.ExpressionContext):
        return self.expression_evaluator.visitExpression(ctx)

    def visitLiteral(self, ctx: KumirParser.LiteralContext):
        return self.expression_evaluator.visitLiteral(ctx)

    def visitQualifiedIdentifier(self, ctx: KumirParser.QualifiedIdentifierContext):
        # Это может быть переменная или вызов функции без аргументов
        # ExpressionEvaluator должен будет это разрешить
        return self.expression_evaluator.visitQualifiedIdentifier(ctx)

    def visitPostfixExpression(self, ctx: KumirParser.PostfixExpressionContext):
        return self.expression_evaluator.visitPostfixExpression(ctx)
    
    def visitUnaryExpression(self, ctx: KumirParser.UnaryExpressionContext):
        return self.expression_evaluator.visitUnaryExpression(ctx)

    def visitPowerExpression(self, ctx: KumirParser.PowerExpressionContext):
        return self.expression_evaluator.visitPowerExpression(ctx)

    def visitMultiplicativeExpression(self, ctx: KumirParser.MultiplicativeExpressionContext):
        return self.expression_evaluator.visitMultiplicativeExpression(ctx)

    def visitAdditiveExpression(self, ctx: KumirParser.AdditiveExpressionContext):
        return self.expression_evaluator.visitAdditiveExpression(ctx)

    def visitRelationalExpression(self, ctx: KumirParser.RelationalExpressionContext):
        return self.expression_evaluator.visitRelationalExpression(ctx)

    def visitEqualityExpression(self, ctx: KumirParser.EqualityExpressionContext):
        return self.expression_evaluator.visitEqualityExpression(ctx)

    def visitLogicalAndExpression(self, ctx: KumirParser.LogicalAndExpressionContext):
        return self.expression_evaluator.visitLogicalAndExpression(ctx)

    def visitLogicalOrExpression(self, ctx: KumirParser.LogicalOrExpressionContext):
        return self.expression_evaluator.visitLogicalOrExpression(ctx)
    
    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext):
        return self.expression_evaluator.visitPrimaryExpression(ctx)

    def visitArrayLiteral(self, ctx: KumirParser.ArrayLiteralContext):
        return self.expression_evaluator.visitArrayLiteral(ctx)

    # Обработка глобальных элементов (programItem)
    def visitGlobalDeclaration(self, ctx: KumirParser.GlobalDeclarationContext):
        type_spec_ctx = ctx.typeSpecifier()
        base_kumir_type, is_table_type = get_type_info_from_specifier(cast('KumirInterpreterVisitor', self), type_spec_ctx)

        for var_item_ctx in ctx.variableList().variableDeclarationItem():
            var_name = var_item_ctx.ID().getText()
            dimensions = None
            initial_value_ctx = None

            if var_item_ctx.LBRACK(): 
                self.error_stream(f"Предупреждение: Парсинг границ для глобальных таблиц ('{var_name}') пока не полностью реализован в visitGlobalDeclaration и будет пропущен.\n")
                pass 

            if var_item_ctx.EQ(): 
                initial_value_ctx = var_item_ctx.expression()
            
            final_kumir_type = base_kumir_type
            actual_is_table = is_table_type
            if dimensions: 
                final_kumir_type += 'таб' # Убедимся, что 'таб' есть, если is_table_type истинно и есть границы
                actual_is_table = True
            elif is_table_type and not dimensions: 
                final_kumir_type += 'таб'

            self.scope_manager.declare_variable(
                name=var_name,
                kumir_type=final_kumir_type, 
                is_table=actual_is_table,
                dimensions=dimensions,
                ctx_declaration_item=var_item_ctx
            )

            if initial_value_ctx:
                value_to_assign = self.visit(initial_value_ctx)
                validated_value = cast(KumirInterpreterVisitor, self)._validate_and_convert_value_for_assignment(
                    value_to_assign, 
                    final_kumir_type, 
                    var_name,
                    actual_is_table
                )
                self.scope_manager.update_variable(var_name, validated_value, var_item_ctx)
        return None

    def visitGlobalAssignment(self, ctx: KumirParser.GlobalAssignmentContext):
        # Это для присваиваний вне основного блока (например, инициализация глобальных переменных модуля)
        # Логика может быть похожа на visitAssignmentStatement, но с учетом глобальной области видимости
        var_name = ctx.qualifiedIdentifier().getText()
        value_expr_ctx = None
        if ctx.literal(): value_expr_ctx = ctx.literal()
        elif ctx.unaryExpression(): value_expr_ctx = ctx.unaryExpression()
        elif ctx.arrayLiteral(): value_expr_ctx = ctx.arrayLiteral()
        
        if not value_expr_ctx: 
            raise KumirSyntaxError("Отсутствует выражение для присваивания в глобальном присваивании.",
                                   line_index=ctx.start.line-1, column_index=ctx.start.column,
                                   line_content=self.get_line_content_from_ctx(ctx))

        value_to_assign = self.visit(value_expr_ctx)
        
        # Получаем информацию о переменной (тип, является ли таблицей)
        # Исправляем вызов find_variable - он принимает ctx как второй аргумент
        var_info, _ = self.scope_manager.find_variable(var_name, ctx=ctx.qualifiedIdentifier())
        if not var_info: # pragma: no cover - find_variable должен кинуть исключение
            raise KumirNameError(f"Переменная '{var_name}' не объявлена.", 
                                 line_index=ctx.qualifiedIdentifier().start.line-1,
                                 column_index=ctx.qualifiedIdentifier().start.column,
                                 line_content=self.get_line_content_from_ctx(ctx.qualifiedIdentifier()))

        validated_value = cast(KumirInterpreterVisitor, self)._validate_and_convert_value_for_assignment(
            value_to_assign, 
            var_info['type'], 
            var_name,
            var_info['is_table']
        )
        self.scope_manager.update_variable(var_name, validated_value, ctx.qualifiedIdentifier())
        return None

    def visitImportStatement(self, ctx: KumirParser.ImportStatementContext): 
        module_name_rule_node = ctx.moduleName() # Это ModuleNameContext

        # moduleName : qualifiedIdentifier | STRING ;
        # module_name_node будет либо QualifiedIdentifierContext, либо Token
        module_name_node = module_name_rule_node.qualifiedIdentifier() or module_name_rule_node.STRING()

        if module_name_node is None:
            # Эта ситуация не должна возникать при корректном дереве разбора для данного правила.
            if self.error_stream:
                self.error_stream("Ошибка: Не удалось извлечь узел имени модуля в import.\\n")
            # TODO: Рассмотреть возможность выброса исключения или более строгой обработки ошибки
            return None

        module_name = module_name_node.getText() # Работает и для RuleContext, и для Token

        # Теперь проверяем, был ли это STRING токен, чтобы удалить кавычки
        if isinstance(module_name_node, Token): # Проверяем, является ли это токеном
            if module_name_node.type == KumirLexer.STRING:
                module_name = module_name[1:-1] # Удаляем кавычки
        # elif isinstance(module_name_node, KumirParser.QualifiedIdentifierContext):
            # Для QualifiedIdentifierContext .getText() уже дает правильное имя,
            # и дополнительная обработка не требуется.
            # pass

        if self.error_stream:
            self.error_stream(f"Предупреждение: Импорт модуля '{module_name}' пока не поддерживается и будет проигнорирован.\\n")
        return None

    def visit(self, tree):
        if self.stop_execution_flag: 
            return None 
        return super().visit(tree)

    # KumirParser.GlobalDeclarationContext
    def visitGlobalDeclaration(self, ctx: KumirParser.GlobalDeclarationContext):
        # print(f"[DEBUG VISIT] GlobalDeclaration: {ctx.getText()}")
        # globalDeclaration: KW_АЛГ qualifiedIdentifier algorithmHeader SEMI algorithmBody KW_КОН SEMI
        #                 | KW_ИСПОЛЬЗОВАТЬ qualifiedIdentifier SEMI
        #                 | varDeclaration SEMI
        #                 ;
        if ctx.KW_АЛГ():
            # Это определение алгоритма (процедуры или функции)
            # Собираем информацию и регистрируем в ProcedureManager
            alg_name_ctx = ctx.qualifiedIdentifier()
            alg_name = alg_name_ctx.getText().lower()
            
            # Проверяем, не является ли имя зарезервированным (например, имя встроенной функции/процедуры)
            # TODO: Добавить проверку на конфликт с встроенными именами
            
            header_ctx = ctx.algorithmHeader()
            is_function = header_ctx.KW_ТИПА() is not None
            result_type_spec = header_ctx.typeSpecifier() if is_function else None
            result_kumir_type: Optional[str] = None
            result_element_type: Optional[str] = None # Для табличных функций

            if is_function and result_type_spec:
                type_info = get_type_info_from_specifier(result_type_spec)
                result_kumir_type = type_info['kumir_type']
                if type_info['is_table']:
                    result_element_type = type_info['element_type']
                    # Дополнительно можно сохранить информацию о размерностях, если это нужно ProcedureManager
            
            # Собираем параметры
            params_list = []
            if header_ctx.formalParameters():
                for formal_param_ctx in header_ctx.formalParameters().formalParameter():
                    param_info = self.procedure_manager.extract_parameter_info(formal_param_ctx)
                    params_list.append(param_info)

            self.procedure_manager.register_procedure(
                name=alg_name,
                ctx_node=ctx.algorithmBody(), # Тело алгоритма
                params_info=params_list,
                is_function=is_function,
                result_kumir_type=result_kumir_type,
                result_element_type=result_element_type, # Передаем тип элемента для табличных функций
                declaration_ctx=header_ctx # Для сообщений об ошибках
            )
            # print(f"[DEBUG PROC_REG] Зарегистрирован {'функция' if is_function else 'алгоритм'} {alg_name} с параметрами: {params_list}, тип результата: {result_kumir_type}")

        elif ctx.KW_ИСПОЛЬЗОВАТЬ():
            module_name_node = ctx.qualifiedIdentifier()
            if module_name_node:
                module_name = module_name_node.getText()
                # print(f"[DEBUG VISIT] Используется модуль: {module_name}")
                # TODO: Реализовать логику импорта модулей. 
                # Сейчас просто выводим предупреждение, если есть куда.
                if self.error_stream_out:
                    self.error_stream_out(f"Предупреждение: Импорт модуля '{module_name}' пока не поддерживается и будет проигнорирован.\n")
            else: # pragma: no cover
                if self.error_stream_out:
                    self.error_stream_out("Ошибка: Не удалось извлечь узел имени модуля в import.\n")

        elif ctx.varDeclaration():
            # Это глобальное объявление переменной
            # print(f"[DEBUG VISIT] Глобальное varDeclaration: {ctx.varDeclaration().getText()}")
            # varDeclaration : typeSpecifier varList
            type_spec_ctx = ctx.varDeclaration().typeSpecifier()
            var_list_ctx = ctx.varDeclaration().varList()
            
            type_info = get_type_info_from_specifier(type_spec_ctx)
            base_kumir_type = type_info['kumir_type']
            is_table = type_info['is_table']
            element_type = type_info['element_type'] # Будет None, если не таблица
            # print(f"[DEBUG GLOBAL VAR_DECL] Base type: {base_kumir_type}, is_table: {is_table}, element_type: {element_type}")

            for var_item_ctx in var_list_ctx.varItem():
                var_name_node = var_item_ctx.qualifiedIdentifier()
                var_name = var_name_node.getText().lower()
                
                # print(f"[DEBUG GLOBAL VAR_DECL] Processing var: {var_name}")

                dimensions: Optional[List[Tuple[KumirValue, KumirValue]]] = None
                actual_is_table = is_table # Используем тип из typeSpecifier как основной

                # Если в varItem есть свои tableBounds, они переопределяют табличность из typeSpecifier
                # (хотя по грамматике это не должно происходить для глобальных переменных,
                # tableBounds обычно внутри АЛГ/НАЧ)
                # Но если грамматика ANTLR это позволяет, обработаем.
                # В стандартном КуМире размеры таблиц для глобальных переменных не указываются при объявлении.
                # Они либо динамические, либо их размер определяется при первом присваивании/использовании.
                # Для статических глобальных массивов (если бы они были как в C), размеры были бы нужны.
                # Пока будем считать, что tableBounds здесь не должно быть для глобальных.
                if var_item_ctx.tableBounds(): # pragma: no cover
                    if self.error_stream_out:
                         self.error_stream_out(f"Предупреждение: Парсинг границ для глобальных таблиц ('{var_name}') пока не полностью реализован в visitGlobalDeclaration и будет пропущен.\n")
                    # Если бы мы их парсили:
                    # dimensions_info = self.expression_evaluator.visitTableBounds(var_item_ctx.tableBounds())
                    # dimensions = dimensions_info['dimensions_values']
                    # actual_is_table = True # Явно указаны границы, значит это таблица

                # print(f"[DEBUG GLOBAL VAR_DECL] Declaring global var: {var_name}, type: {base_kumir_type}, is_table: {actual_is_table}, element_type (if table): {element_type if actual_is_table else None}")
                self.scope_manager.declare_variable(
                    var_name=var_name,
                    kumir_type_str=base_kumir_type if not actual_is_table else element_type, # Для таблицы передаем тип элемента
                    is_table=actual_is_table,
                    dimensions_values=dimensions, # Будет None для глобальных, пока не реализуем парсинг границ. Имя параметра изменено на dimensions_values
                    line_index=var_name_node.start.line -1, # 0-based
                    column_index=var_name_node.start.column, # 0-based
                    ctx_node=var_item_ctx # Для более точных сообщений об ошибках. Имя параметра изменено на ctx_node
                )
        else: # pragma: no cover
            # Этого не должно случиться, если грамматика верна
            if self.error_stream_out:
                self.error_stream_out(f"Неизвестный тип globalDeclaration: {ctx.getText()}\n")
        
        return None # Глобальные объявления не возвращают значения для выражений

    # KumirParser.ProcedureCallStatementContext    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext):
        print(f"\n!!! [DEBUG main_visitor.visitProcedureCallStatement] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        # print(f"[DEBUG VISIT] ProcedureCallStatement: {ctx.getText()}")
        # procedureCallStatement : qualifiedIdentifier LPAREN (expression (COMMA expression)*)? RPAREN SEMI ;
        proc_name = ctx.qualifiedIdentifier().getText().lower()
        
        # Проверяем, не является ли имя зарезервированным (например, имя встроенной функции/процедуры)
        # TODO: Добавить проверку на конфликт с встроенными именами
        
        # Собираем фактические аргументы
        actual_args = []
        if ctx.expression():
            for expr_ctx in ctx.expression():
                arg_value = self.visit(expr_ctx)
                actual_args.append(arg_value)
        
        # Вызываем процедуру (или функцию)
        # Для этого используем общую логику вызова, которая была в старом интерпретаторе
        # Но без явного указания контекста, полагаемся на текущий
        # Если процедура не найдена, будет вызвано исключение KumirRuntimeError        return self.procedure_manager._execute_procedure_call(
            proc_name, 
            actual_args,
            ctx.qualifiedIdentifier() # Для контекста ошибок
        )

    # KumirParser.AssignmentStatementContext
    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        print(f"\n!!! [DEBUG main_visitor.visitAssignmentStatement] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        # print(f"[DEBUG VISIT] AssignmentStatement: {ctx.getText()}")
        # assignmentStatement : qualifiedIdentifier ASSIGN expression SEMI ;
        var_name = ctx.qualifiedIdentifier().getText()
        value_expr_ctx = ctx.expression()
        
        if not value_expr_ctx: 
            raise KumirSyntaxError("Отсутствует выражение для присваивания.",
                                   line_index=ctx.start.line-1, column_index=ctx.start.column,
                                   line_content=self.get_line_content_from_ctx(ctx))

        value_to_assign = self.visit(value_expr_ctx)
        
        # Получаем информацию о переменной (тип, является ли таблицей)
        # Исправляем вызов find_variable - он принимает ctx как второй аргумент
        var_info, var_ctx = self.scope_manager.find_variable(var_name, ctx=ctx.qualifiedIdentifier())
        if not var_info: # pragma: no cover - find_variable должен кинуть исключение
            raise KumirNameError(f"Переменная '{var_name}' не объявлена.", 
                                 line_index=ctx.qualifiedIdentifier().start.line-1,
                                 column_index=ctx.qualifiedIdentifier().start.column,
                                 line_content=self.get_line_content_from_ctx(ctx.qualifiedIdentifier()))

        # Специальная обработка для 'рез' - это выходной параметр процедуры
        if var_name == 'рез' and not var_info['is_table']:
            # 'рез' должен быть табличным, если это выходной параметр
            # Принудительно делаем его табличным, если это возможно по грамматике
            var_info['is_table'] = True
            var_info['type'] += 'таб' # Добавляем 'таб' к типу

        validated_value = cast(KumirInterpreterVisitor, self)._validate_and_convert_value_for_assignment(            value_to_assign, 
            var_info['type'], 
            var_name,
            var_info['is_table']
        )
        self.scope_manager.update_variable(var_name, validated_value, ctx.qualifiedIdentifier())
        return None
