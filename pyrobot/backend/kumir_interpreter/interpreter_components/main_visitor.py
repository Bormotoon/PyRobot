# filepath: c:\\Users\\Bormotoon\\VSCodeProjects\\PyRobot\\pyrobot\\backend\\kumir_interpreter\\interpreter_components\\main_visitor.py
import logging
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import ParserRuleContext, Token # Для ctx.toStringTree() и проверки типа узла
from typing import Any, List, Dict, Optional, Callable, cast

# Локальные импорты КуМир (относительные)
from ..generated.KumirLexer import KumirLexer
from ..generated.KumirParser import KumirParser
from ..generated.KumirParserVisitor import KumirParserVisitor # Базовый визитор ANTLR
from .. import kumir_exceptions # <--- Добавляем импорт модуля исключений
from ..kumir_exceptions import KumirRuntimeError, KumirSyntaxError, ExitSignal, StopExecutionSignal, KumirNameError, DeclarationError, KumirEvalError # Изменения: ProcedureExitCalled -> ExitSignal, LoopExitException -> BreakSignal
from ..kumir_datatypes import KumirReturnValue, KumirValue, KumirType 
from ..definitions import AlgorithmManager  # Импорт наших новых классов
from ..utils import KumirTypeConverter  # Импорт type converter

# Импорты компонентов интерпретатора из __init__.py текущего пакета
from .scope_manager import ScopeManager
from .procedure_manager import ProcedureManager
from .expression_evaluator import ExpressionEvaluator
from .declaration_visitors import DeclarationVisitorMixin
from .statement_handlers import StatementHandlerMixin
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
        self.logger = logging.getLogger(__name__)
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
                self.logger.error(f"Ошибка в строке {line}, позиция {column}: {msg}") 

    def get_errors(self) -> List[KumirSyntaxError]:
        return self.errors

class KumirInterpreterVisitor(DeclarationVisitorMixin, StatementHandlerMixin, StatementVisitorMixin, ControlFlowVisitorMixin, KumirParserVisitor): 
    def __init__(self, input_stream: Optional[Callable[[], str]] = None, 
                 output_stream: Optional[Callable[[str], None]] = None,
                 error_stream: Optional[Callable[[str], None]] = None, # Callable, а не SupportsWrite
                 program_lines: Optional[List[str]] = None,
                 global_vars: Optional[Dict[str, Any]] = None,
                 precision: int = DEFAULT_PRECISION,
                 echo_input: bool = True):
        super().__init__() 
        
        # Настраиваем logger
        self.logger = logging.getLogger(__name__)
        
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
        self.algorithm_manager = AlgorithmManager()  # Новый менеджер алгоритмов
        self.type_converter = KumirTypeConverter()  # Инициализируем type_converter
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
        self.builtin_procedure_handler = BuiltinProcedureHandler(self) # Предполагаем наличие
        
        # Настройка error stream через логирование вместо print
        if error_stream:
            self.error_stream_out = error_stream
        else:
            logger = logging.getLogger(__name__)
            def log_error(message: str) -> None:
                logger.error(message)
            self.error_stream_out = log_error        
        # Настройка эхо ввода (автоматический вывод введённых значений)
        self.echo_input = echo_input
        
        self.current_algorithm_name: Optional[str] = None
        self.current_algorithm_is_function: bool = False
        self.current_algorithm_result_type: Optional[str] = None
        self.return_value: Optional[KumirReturnValue] = None 
        self.stop_execution_flag = False
        self.function_call_active: bool = False # ДОБАВЛЕНО
        
        # Флаг для режима "только сбор определений" (не выполнять тела алгоритмов)
        self.definition_collection_mode: bool = False
        
        # Робот и его обработчик команд
        self.robot = None
        self.robot_command_handler = None
        self.progress_callback = None

        if global_vars:
            for name, value_info in global_vars.items():
                self.scope_manager.scopes[0][name.lower()] = {'value': value_info, 'type': 'глоб_неизв', 'is_table': False, 'dimensions': None, 'initialized': True}

    def validate_and_convert_value_for_assignment(self, value: Any, target_kumir_type: str, var_name: str, is_target_table: bool, element_type: Optional[str] = None) -> Any:
        # TODO: Implement actual validation and conversion logic based on the original interpreter.
        # This is a placeholder.
        # Basic type checking and conversion can be added here.
        # For now, just return the value as is.
        
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
        return None    # ДОБАВЛЕНО: Методы для связи с IOHandler
    def get_input_line(self, prompt: str) -> str:
        if not self.io_handler: # pragma: no cover
            raise KumirRuntimeError("IOHandler не инициализирован.")
        return self.io_handler.get_input_line(prompt)

    def write_output(self, text: str) -> None:
        if not self.io_handler: # pragma: no cover
            raise KumirRuntimeError("IOHandler не инициализирован.")
        self.io_handler.write_output(text)
    
    # Методы для робота и прогресс-коллбека
    def set_robot(self, robot):
        """Устанавливает робота для выполнения команд."""
        self.robot = robot
    
    def set_robot_command_handler(self, handler):
        """Устанавливает обработчик команд робота."""
        self.robot_command_handler = handler
    
    def set_progress_callback(self, callback):
        """Устанавливает коллбек для отправки прогресса выполнения."""
        self.progress_callback = callback
    
    # КОНЕЦ ДОБАВЛЕННЫХ МЕТОДОВ    # ДОБАВЛЕНО: Методы для управления режимом сбора определений
    def set_definition_collection_mode(self, mode: bool) -> None:
        """Устанавливает режим сбора определений (не выполнять тела алгоритмов)"""
        self.definition_collection_mode = mode
        
    def is_definition_collection_mode(self) -> bool:
        """Возвращает True, если включен режим сбора определений"""
        return self.definition_collection_mode
        
    def collect_definitions_only(self, tree: ParserRuleContext) -> None:
        """Первый проход: собирает только определения функций и процедур"""
        self.set_definition_collection_mode(True)
        try:
            self.visit(tree)
        finally:
            self.set_definition_collection_mode(False)
    # КОНЕЦ ДОБАВЛЕННЫХ МЕТОДОВ

    # Основной метод для запуска интерпретации с корневого узла (program)    
    def visitProgram(self, ctx: KumirParser.ProgramContext):
        
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
                
                if mod_def_ctx.implicitModuleBody():
                    
                    if mod_def_ctx.implicitModuleBody().algorithmDefinition():
                        for alg_def_ctx in mod_def_ctx.implicitModuleBody().algorithmDefinition():
                            self.visitAlgorithmDefinition(alg_def_ctx) # Собираем информацию
                elif mod_def_ctx.moduleBody(): # Явный модуль
                    if mod_def_ctx.moduleBody().algorithmDefinition():
                        for alg_def_ctx in mod_def_ctx.moduleBody().algorithmDefinition():
                            self.visitAlgorithmDefinition(alg_def_ctx) # Собираем информацию
        
        # Ищем "главный" алгоритм для выполнения или первый попавшийся, если "главного" нет
        # В простом случае без явного "главного" алгоритма, КуМир может ничего не выполнять,
        # если это просто набор процедур. Для тестов нам нужен какой-то вход.
        # Пока что не будем автоматически запускать алгоритмы здесь.
        # Запуск будет инициироваться извне через execute_algorithm_node или interpret_kumir.

        return None # visitProgram обычно ничего не возвращает

    def visitImplicitModuleBody(self, ctx: KumirParser.ImplicitModuleBodyContext):
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
            # actual_params = proc_info.get('params', {})  # Не используется
            if args:
                # TODO: Проверка количества и типов аргументов
                # ... (эта логика есть в _execute_procedure_call старого интерпретатора)
                pass
            
            # Инициализация 'знач' для функций
            if self.current_algorithm_is_function and self.current_algorithm_result_type and self.current_algorithm_result_type != VOID_TYPE:
                try:
                    # is_table_check = False  # Не используется
                    # current_algorithm_result_type здесь точно строка и не VOID_TYPE
                    # Поэтому дополнительная проверка на isinstance(self.current_algorithm_result_type, str) не нужна.
                    # is_table_check = 'таб' in self.current_algorithm_result_type  # Не используется
                    
                    self.scope_manager.declare_variable(
                        name='знач',
                        kumir_type=KumirType.from_string(self.current_algorithm_result_type), # Convert string to KumirType
                        initial_value=None,
                        line_index=alg_ctx.algorithmHeader().start.line - 1,
                        column_index=alg_ctx.algorithmHeader().start.column
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
                    
                    # Ищем 'знач' в текущей области видимости
                    znach_val_info = self.scope_manager.lookup_variable('знач', alg_ctx) # Используем alg_ctx для контекста ошибки
                    if znach_val_info:
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
                    return self.return_value # Уже KumirReturnValue
                else: # self.return_value is None and self.current_algorithm_result_type == VOID_TYPE
                    return KumirReturnValue(value=None, type=VOID_TYPE)
            else: # Процедура
                return None # Процедуры ничего не возвращают (кроме как через параметры 'рез')

        except ExitSignal: # Перехватываем ВЫХОД из процедуры/функции
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
            self.stop_execution_flag = True # Устанавливаем флаг
            raise # Передаем сигнал выше, чтобы остановить всю программу
        finally:
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
                # Парсим границы массива
                dimensions = []
                array_bounds_nodes = var_item_ctx.arrayBounds()
                if array_bounds_nodes:
                    for i, bounds_ctx in enumerate(array_bounds_nodes):
                        
                        if not (bounds_ctx.expression(0) and bounds_ctx.expression(1) and bounds_ctx.COLON()):
                            raise DeclarationError(
                                f"Строка {bounds_ctx.start.line}: Некорректный формат границ для измерения {i + 1} таблицы '{var_name}'. Ожидается [нижняя:верхняя].",
                                line_index=bounds_ctx.start.line -1, 
                                column_index=bounds_ctx.start.column,
                                line_content=self.get_line_content_from_ctx(bounds_ctx))

                        min_idx_val = self.expression_evaluator.visitExpression(bounds_ctx.expression(0))
                        max_idx_val = self.expression_evaluator.visitExpression(bounds_ctx.expression(1))
                        
                        # Извлекаем значения из KumirValue
                        min_idx = min_idx_val.value if hasattr(min_idx_val, 'value') else min_idx_val
                        max_idx = max_idx_val.value if hasattr(max_idx_val, 'value') else max_idx_val

                        if not isinstance(min_idx, int):
                            raise KumirEvalError(
                                f"Строка {bounds_ctx.expression(0).start.line}: Нижняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {min_idx} (тип: {type(min_idx).__name__}).",
                                line_index=bounds_ctx.expression(0).start.line -1, 
                                column_index=bounds_ctx.expression(0).start.column,
                                line_content=self.get_line_content_from_ctx(bounds_ctx.expression(0)))
                        if not isinstance(max_idx, int):
                            raise KumirEvalError(
                                f"Строка {bounds_ctx.expression(1).start.line}: Верхняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {max_idx} (тип: {type(max_idx).__name__}).",
                                line_index=bounds_ctx.expression(1).start.line -1, 
                                column_index=bounds_ctx.expression(1).start.column,
                                line_content=self.get_line_content_from_ctx(bounds_ctx.expression(1)))

                        dimensions.append((min_idx, max_idx))
                    # Границы для таблицы определены
                else:
                    raise DeclarationError(
                        f"Строка {var_item_ctx.LBRACK().getSymbol().line}: Отсутствуют определения границ для таблицы '{var_name}'.",
                        line_index=var_item_ctx.LBRACK().getSymbol().line -1, 
                        column_index=var_item_ctx.LBRACK().getSymbol().column,
                        line_content=self.get_line_content_from_ctx(var_item_ctx))

            if var_item_ctx.EQ(): 
                initial_value_ctx = var_item_ctx.expression()
            
            # Determine final type based on whether it's a table type
            if is_table_type:
                # For table types, declare as array
                if dimensions is None:
                    dimensions = []  # Empty dimensions for dynamic arrays
                self.scope_manager.declare_array(
                    var_name=var_name,
                    element_kumir_type=KumirType.from_string(base_kumir_type),
                    dimensions=dimensions,
                    line_index=var_item_ctx.ID().getSymbol().line - 1,
                    column_index=var_item_ctx.ID().getSymbol().column
                )
            else:
                # For simple types, declare as variable
                self.scope_manager.declare_variable(
                    name=var_name,
                    kumir_type=KumirType.from_string(base_kumir_type),
                    initial_value=None,
                    line_index=var_item_ctx.ID().getSymbol().line - 1,
                    column_index=var_item_ctx.ID().getSymbol().column
                )
            
            if initial_value_ctx:
                value_to_assign = self.visit(initial_value_ctx)
                if value_to_assign is None:
                    raise KumirEvalError(f"Не удалось вычислить начальное значение для переменной '{var_name}'", 
                                       line_index=initial_value_ctx.start.line - 1,
                                       column_index=initial_value_ctx.start.column)
                
                # После проверки на None, гарантируем что value_to_assign не None
                assert value_to_assign is not None  # type narrowing для Pylance
                
                # Получено значение для инициализации таблицы
                if is_table_type:
                    # Для таблиц нужно создать KumirTableVar из литерала массива
                    if value_to_assign.kumir_type == KumirType.TABLE.value and isinstance(value_to_assign.value, list):
                        # Создаем KumirTableVar из литерала массива
                        # Импортируем функцию создания таблицы из литерала
                        from .declaration_visitors import _create_table_from_array_literal  # type: ignore[attr-defined]
                        
                        # Создаём KumirTableVar из литерала массива
                        table_var = _create_table_from_array_literal(
                            value_to_assign.value, 
                            base_kumir_type, 
                            dimensions,
                            initial_value_ctx
                        )
                        validated_value = KumirValue(table_var, KumirType.TABLE.value)
                        # KumirTableVar создан успешно
                    else:
                        validated_value = cast(KumirInterpreterVisitor, self).validate_and_convert_value_for_assignment(
                            value_to_assign, 
                            base_kumir_type, 
                            var_name,
                            is_table_type
                        )
                else:
                    validated_value = cast(KumirInterpreterVisitor, self).validate_and_convert_value_for_assignment(
                        value_to_assign, 
                        base_kumir_type, 
                        var_name,
                        is_table_type
                    )
                
                self.scope_manager.update_variable(
                    var_name, 
                    validated_value, 
                    line_index=var_item_ctx.expression().start.line - 1,
                    column_index=var_item_ctx.expression().start.column
                )
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
        # find_variable принимает только var_name
        var_info, _ = self.scope_manager.find_variable(var_name)
        if not var_info: # pragma: no cover - find_variable должен кинуть исключение
            raise KumirNameError(f"Переменная '{var_name}' не объявлена.", 
                                 line_index=ctx.qualifiedIdentifier().start.line-1,
                                 column_index=ctx.qualifiedIdentifier().start.column,
                                 line_content=self.get_line_content_from_ctx(ctx.qualifiedIdentifier()))

        validated_value = cast(KumirInterpreterVisitor, self).validate_and_convert_value_for_assignment(
            value_to_assign, 
            var_info['kumir_type'], 
            var_name,
            var_info['is_table']
        )
        self.scope_manager.update_variable(
            var_name, 
            validated_value, 
            line_index=ctx.qualifiedIdentifier().start.line - 1,
            column_index=ctx.qualifiedIdentifier().start.column
        )
        return None

    def visitImportStatement(self, ctx: KumirParser.ImportStatementContext): 
        module_name_rule_node = ctx.moduleName() # Это ModuleNameContext

        # moduleName : qualifiedIdentifier | STRING ;
        # module_name_node будет либо QualifiedIdentifierContext, либо Token
        module_name_node = module_name_rule_node.qualifiedIdentifier() or module_name_rule_node.STRING()

        if module_name_node is None:
            # Эта ситуация не должна возникать при корректном дереве разбора для данного правила.
            self.logger.error("Ошибка: Не удалось извлечь узел имени модуля в import.")
            # TODO: Рассмотреть возможность выброса исключения или более строгой обработки ошибки
            return None

        module_name = module_name_node.getText() # Работает и для RuleContext, и для Token

        # Теперь проверяем, был ли это STRING токен, чтобы удалить кавычки
        if isinstance(module_name_node, Token): # Проверяем, является ли это токеном
            if module_name_node.type == KumirLexer.STRING:
                module_name = module_name[1:-1] # Удаляем кавычки
        # elif isinstance(module_name_node, KumirParser.QualifiedIdentifierContext):
            # Для QualifiedIdentifierContext .getText() уже дает правильное имя,            # и дополнительная обработка не требуется.
            self.logger.warning(f"Предупреждение: Импорт модуля '{module_name}' пока не поддерживается и будет проигнорирован.")
        return None

    def visit(self, tree):
        if self.stop_execution_flag:            return None 
        return super().visit(tree)
    
    def _call_user_function(self, func_name: str, args: List[Any], ctx: ParserRuleContext) -> 'KumirValue':
        """Вызывает пользовательскую функцию с заданными аргументами через procedure_manager"""
        from ..kumir_datatypes import KumirValue
        
        # Используем публичный метод execute_user_function для единообразной логики
        return_value = self.procedure_manager.execute_user_function(func_name, args, ctx)
        
        if not isinstance(return_value, KumirValue) and return_value is not None:
            # Попытка преобразовать в KumirValue, если нужно
            from ..kumir_datatypes import KumirType
            if isinstance(return_value, int):
                return_value = KumirValue(return_value, KumirType.INT.value)
            elif isinstance(return_value, float):
                return_value = KumirValue(return_value, KumirType.REAL.value)
            elif isinstance(return_value, bool):
                return_value = KumirValue(return_value, KumirType.BOOL.value)
            elif isinstance(return_value, str):
                return_value = KumirValue(return_value, KumirType.STR.value)
        
        return return_value

    def _call_user_procedure(self, proc_name: str, args: List[Any], ctx: ParserRuleContext) -> None:
        """Вызывает пользовательскую процедуру с заданными аргументами"""
        from ..kumir_datatypes import KumirValue, KumirType
        from ..kumir_exceptions import KumirRuntimeError, KumirArgumentError
        from ..definitions import FunctionReturnException
        
        # Получаем определение процедуры
        algorithm_def = self.algorithm_manager.get_algorithm(proc_name)
        
        if algorithm_def is None:
            raise KumirRuntimeError(f"Процедура '{proc_name}' не найдена")
        
        if algorithm_def.is_function:
            raise KumirRuntimeError(f"'{proc_name}' является функцией, а не процедурой")
        
        # Проверяем количество аргументов
        if len(args) != len(algorithm_def.parameters):
            raise KumirArgumentError(f"Процедура '{proc_name}' ожидает {len(algorithm_def.parameters)} аргументов, получено {len(args)}")
        
        # Создаем новую область видимости для процедуры
        self.scope_manager.push_scope()
        
        # Отслеживаем параметры рез/аргрез для копирования обратно
        output_parameters = []
        
        try:
            # Объявляем параметры в новой области видимости
            for i, param in enumerate(algorithm_def.parameters):
                param_value = args[i]
                
                # Обработка разных режимов параметров
                if param.mode == 'арг':
                    # Параметр по значению - простое копирование
                    # Преобразуем аргумент в KumirValue, если это еще не KumirValue
                    if not isinstance(param_value, KumirValue):
                        # Попытка автоматического преобразования типа
                        if isinstance(param_value, int):
                            param_value = KumirValue(param_value, KumirType.INT.value)
                        elif isinstance(param_value, float):
                            param_value = KumirValue(param_value, KumirType.REAL.value)
                        elif isinstance(param_value, bool):
                            param_value = KumirValue(param_value, KumirType.BOOL.value)
                        elif isinstance(param_value, str):
                            if len(param_value) == 1:
                                param_value = KumirValue(param_value, KumirType.CHAR.value)
                            else:
                                param_value = KumirValue(param_value, KumirType.STR.value)
                        else:
                            raise KumirRuntimeError(f"Неподдерживаемый тип аргумента: {type(param_value)}")
                    
                    # Получаем KumirType из строкового представления типа параметра
                    param_kumir_type = KumirType.from_string(param.param_type)
                    
                    # Объявляем параметр как переменную в области видимости процедуры
                    self.scope_manager.declare_variable(
                        param.name,
                        param_kumir_type,
                        param_value,
                        ctx.start.line,
                        ctx.start.column
                    )
                    
                elif param.mode == 'рез':
                    # Параметр только для вывода - инициализируем пустым значением
                    param_kumir_type = KumirType.from_string(param.param_type)
                    
                    # Создаем начальное значение по типу
                    if param_kumir_type == KumirType.INT:
                        initial_value = KumirValue(0, KumirType.INT.value)
                    elif param_kumir_type == KumirType.REAL:
                        initial_value = KumirValue(0.0, KumirType.REAL.value)
                    elif param_kumir_type == KumirType.BOOL:
                        initial_value = KumirValue(False, KumirType.BOOL.value)
                    elif param_kumir_type == KumirType.CHAR:
                        initial_value = KumirValue(' ', KumirType.CHAR.value)
                    elif param_kumir_type == KumirType.STR:
                        initial_value = KumirValue('', KumirType.STR.value)
                    else:
                        initial_value = KumirValue(None, param_kumir_type.value)
                    
                    # Объявляем параметр с начальным значением
                    self.scope_manager.declare_variable(
                        param.name,
                        param_kumir_type,
                        initial_value,
                        ctx.start.line,
                        ctx.start.column
                    )
                    
                    # Запоминаем для копирования обратно
                    # ВАЖНО: рез параметр требует имя переменной, а не значение
                    if isinstance(param_value, str):
                        # param_value должно быть именем переменной
                        output_parameters.append({
                            'param_name': param.name,
                            'target_var_name': param_value,
                            'mode': 'рез'
                        })
                    else:
                        raise KumirRuntimeError(f"Параметр 'рез' должен быть именем переменной, получено: {type(param_value)}")
                    
                elif param.mode == 'аргрез':
                    # Параметр для ввода-вывода - копируем значение и запоминаем для обратного копирования
                    if isinstance(param_value, str):
                        # param_value это имя переменной - получаем её значение
                        var_info, _ = self.scope_manager.find_variable(param_value)
                        if var_info is None:
                            raise KumirRuntimeError(f"Переменная '{param_value}' не найдена для параметра 'аргрез'")
                        
                        # Используем значение переменной
                        actual_value = var_info['value']
                        if not isinstance(actual_value, KumirValue):
                            # Преобразуем в KumirValue
                            if isinstance(actual_value, int):
                                actual_value = KumirValue(actual_value, KumirType.INT.value)
                            elif isinstance(actual_value, float):
                                actual_value = KumirValue(actual_value, KumirType.REAL.value)
                            elif isinstance(actual_value, bool):
                                actual_value = KumirValue(actual_value, KumirType.BOOL.value)
                            elif isinstance(actual_value, str):
                                if len(actual_value) == 1:
                                    actual_value = KumirValue(actual_value, KumirType.CHAR.value)
                                else:
                                    actual_value = KumirValue(actual_value, KumirType.STR.value)
                            else:
                                actual_value = KumirValue(actual_value, KumirType.UNKNOWN.value)
                        
                        param_kumir_type = KumirType.from_string(param.param_type)
                        
                        # Объявляем параметр с копией значения
                        self.scope_manager.declare_variable(
                            param.name,
                            param_kumir_type,
                            actual_value,
                            ctx.start.line,
                            ctx.start.column
                        )
                        
                        # Запоминаем для копирования обратно
                        output_parameters.append({
                            'param_name': param.name,
                            'target_var_name': param_value,
                            'mode': 'аргрез'
                        })
                    else:
                        raise KumirRuntimeError(f"Параметр 'аргрез' должен быть именем переменной, получено: {type(param_value)}")
                    
                else:
                    raise KumirRuntimeError(f"Неизвестный режим параметра: {param.mode}")
            
            # Сброс возвращаемого значения процедуры/функции
            self.procedure_manager.set_return_value(None)
            
            # Выполняем тело процедуры
            try:
                self.visit(algorithm_def.body_context)
                
            except FunctionReturnException:
                # Процедуры не должны возвращать значения через 'знач := выражение'
                raise KumirRuntimeError(f"Процедура '{proc_name}' не может возвращать значения через 'знач := выражение'")
            
            # Копируем значения выходных параметров обратно в вызывающую область
            for output_param in output_parameters:
                param_name = output_param['param_name']
                target_var_name = output_param['target_var_name']
                
                # Получаем текущее значение параметра в процедуре
                param_var_info, _ = self.scope_manager.find_variable(param_name)
                if param_var_info:
                    param_value = param_var_info['value']
                    
                    # Обновляем переменную в предыдущей области видимости
                    # Временно выходим из текущей области
                    self.scope_manager.pop_scope()
                    try:
                        self.scope_manager.update_variable(target_var_name, param_value, line_index=0, column_index=0)
                    finally:
                        # Возвращаемся в область процедуры для корректной очистки
                        self.scope_manager.push_scope()
                
        finally:
            # Всегда восстанавливаем предыдущую область видимости
            self.scope_manager.pop_scope()


