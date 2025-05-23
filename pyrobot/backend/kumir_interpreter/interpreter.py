# FILE START: interpreter.py
# Test comment
import logging
import copy
import math  # Добавлено для pow
import operator  # Добавлено для операций
# Добавляем импорт TerminalNode
from antlr4.tree.Tree import TerminalNode
from antlr4.tree.Tree import TerminalNodeImpl # ДОБАВЛЯЮ ЭТОТ ИМПОРТ

# Импортируем все исключения из одного места
from .kumir_exceptions import (KumirExecutionError, DeclarationError, AssignmentError,
                               InputOutputError, KumirInputRequiredError, KumirEvalError,
                                RobotError, KumirSyntaxError, KumirNotImplementedError,
                                KumirNameError, KumirTypeError, KumirIndexError, KumirInputError,
                                KumirArgumentError, ProcedureExitCalled, StopExecutionException,
                                RobotMovementError, RobotActionError, RobotSensorError,
                                AssertionError_, KumirReturnError) # Восстановлены недостающие


# Исключение для команды ВЫХОД из цикла
class LoopExitException(Exception):
    pass

# Добавим определения для LoopBreakException и LoopContinueException, если они отсутствуют
class LoopBreakException(Exception):
    """Исключение для команды ВЫХОД из цикла (аналог LoopExitException, используется в try-except)."""
    pass

class LoopContinueException(Exception):
    """Исключение для команды ПРОДОЛЖИТЬ в цикле (если будет реализована)."""
    pass

# Импортируем остальные зависимости
from .declarations import (_validate_and_convert_value, # УДАЛЯЕМ get_default_value
                           process_declaration, process_assignment, process_output,
                           process_input)  # Больше не импортируем исключения отсюда
from .execution import execute_lines  # Больше не импортируем KumirExecutionError отсюда
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_state import SimulatedRobot  # Больше не импортируем RobotError отсюда
from .generated.KumirParserVisitor import KumirParserVisitor
from .generated.KumirParser import KumirParser
from .generated.KumirLexer import KumirLexer  # Импортируем лексер для имен токенов
# Добавляем ErrorListener
from antlr4.error.ErrorListener import ErrorListener
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import sys
from typing import Any, Tuple, Optional, Dict, List, Callable
import random  # <-- Добавляем импорт random
import antlr4
from .kumir_datatypes import KumirTableVar # Оставляем только KumirTableVar
# Добавляем ExpressionEvaluator
from .expression_evaluator import ExpressionEvaluator
from antlr4 import ParserRuleContext # <--- ДОБАВЛЮ СЮДА
# Импортируем математические функции Kumir
from .math_functions import div, mod, irand, rand # <--- ДОБАВЛЯЮ ЭТИ ИМПОРТЫ
# Импортируем константы
from .interpreter_components.constants import (MAX_INT, МАКСЦЕЛ, TYPE_MAP,
                                               INTEGER_TYPE, FLOAT_TYPE, BOOLEAN_TYPE,
                                               CHAR_TYPE, STRING_TYPE, VOID_TYPE, KUMIR_TRUE, KUMIR_FALSE)
# Импортируем ScopeManager и get_default_value
from .interpreter_components.scope_manager import ScopeManager, get_default_value
# from .interpreter_components import builtin_functions as bf # <--- bf больше не нужен здесь напрямую
# Импортируем новый словарь BUILTIN_FUNCTIONS
from .interpreter_components.builtin_handlers import BUILTIN_FUNCTIONS
from .interpreter_components.declaration_visitors import DeclarationVisitorMixin
from .interpreter_components.procedure_manager import ProcedureManager # <--- ADDED IMPORT
from .interpreter_components.statement_handlers import StatementHandler # Added import

logger = logging.getLogger('KumirInterpreter')

# Словарь для маппинга токенов типа на строки
TYPE_MAP = {
    KumirLexer.INTEGER_TYPE: 'цел',
    KumirLexer.REAL_TYPE: 'вещ',
    KumirLexer.BOOLEAN_TYPE: 'лог',
    KumirLexer.CHAR_TYPE: 'сим',
    KumirLexer.STRING_TYPE: 'лит',
}

# Типы данных
INTEGER_TYPE = 'цел'
FLOAT_TYPE = 'вещ'
BOOLEAN_TYPE = 'лог'
CHAR_TYPE = 'сим'
STRING_TYPE = 'лит'


# Класс для вывода подробных ошибок парсинга
class DiagnosticErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Вместо сбора ошибок, сразу возбуждаем исключение
        # Используем KumirSyntaxError для единообразия
        # line_content можно попытаться получить, если recognizer.inputStream доступен и содержит строки
        # program_text = recognizer.inputStream.getText(0, recognizer.inputStream.size)
        # program_lines = program_text.splitlines()
        # lc = program_lines[line - 1] if 0 < line <= len(program_lines) else None
        # print(f"Syntax Error: line {line}:{column} {msg}", file=sys.stderr) # stdout -> stderr
        raise KumirSyntaxError(
            message=f"Ошибка синтаксиса: {msg}",
            line_index=line -1, # ANTLR строки 1-индексированные
            column_index=column,
            # line_content=lc # Пока не получаем содержимое строки здесь
        )


class KumirInterpreterVisitor(KumirParserVisitor, DeclarationVisitorMixin):
    """Обходит дерево разбора Кумира и выполняет семантические действия."""

    # --- Словарь для встроенных функций/процедур УДАЛЕН ОТСЮДА ---
    # BUILTIN_FUNCTIONS = { ... } # <--- Весь этот блок удаляется

    def __init__(self, robot=None, input_stream=None, output_stream=None, error_stream=None, echo_input=True):
        super().__init__()
        self.robot = robot
        # self.scopes: List[Dict[str, Any]] = [{}]  # Global scope # <-- This seems to be managed by scope_manager now
        self.current_scope_level = 0
        # self.procedures: Dict[str, Dict[str, Any]] = {} # <-- УДАЛЕНО
        self.loop_depth = 0  # Глубина вложенности циклов
        self.exit_flags = [] # Флаги для команды ВЫХОД из цикла

        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self.error_stream = error_stream or sys.stderr
        self.echo_input = echo_input
        self.input_buffer: List[str] = []
        self.program_lines: List[str] = [] # Будет заполнено в interpret()
        
        self.return_value_from_function: Any = None # Для хранения значения из `знач`
        self.function_call_active = False # Флаг, что мы внутри вызова функции

        # Инициализация ExpressionEvaluator
        # Передаем self (KumirInterpreterVisitor) в ExpressionEvaluator
        self.evaluator = ExpressionEvaluator(self)
        self.BUILTIN_FUNCTIONS = BUILTIN_FUNCTIONS

        self.scope_manager = ScopeManager(self) # <--- ИНИЦИАЛИЗАЦИЯ SCOPEMANAGER
        self.procedure_manager = ProcedureManager(self) # <--- INITIALIZE ProcedureManager
        self.statement_handler = StatementHandler(self) # Added StatementHandler initialization

    # --- Вспомогательные методы для проверки и конвертации типов при присваивании ---

    def _convert_input_to_type(self, input_str: str, target_kumir_type: str, error_source_ctx: antlr4.ParserRuleContext) -> Any:
        """
        Преобразует строку ввода в целевой тип КуМира.
        Выбрасывает KumirEvalError при ошибке преобразования.
        error_source_ctx используется для получения номера строки/колонки для ошибки.
        Этот метод УСТАРЕЛ. Логика преобразования ввода находится в StatementHandler.visitIoStatement.
        """
        # Логика этого метода перенесена в StatementHandler.visitIoStatement.
        # Он не должен больше вызываться напрямую.
        line_idx, col_idx, lc = None, None, None
        if error_source_ctx and hasattr(error_source_ctx, 'start') and error_source_ctx.start:
            line_idx = error_source_ctx.start.line - 1
            col_idx = error_source_ctx.start.column
            lc = self.get_line_content_from_ctx(error_source_ctx)
        
        raise KumirNotImplementedError(
            f"Метод _convert_input_to_type устарел и не должен вызываться. "
            f"Логика преобразования ввода находится в StatementHandler.visitIoStatement.",
            line_index=line_idx, column_index=col_idx, line_content=lc
        )

    def _validate_and_convert_value_for_assignment(self, value, target_type, var_name="переменной"):
        """Проверяет тип значения и выполняет неявные преобразования для присваивания."""
        value_type = type(value)

        if target_type == 'цел':
            if value_type is int:
                # Проверка на МАКСЦЕЛ, если нужно
                # if not (-МАКСЦЕЛ - 1 <= value <= МАКСЦЕЛ):
                #    raise AssignmentError(f"Значение {value} выходит за допустимый диапазон для типа ЦЕЛ.", var_name=var_name)
                return value
            elif value_type is float:
                # Нельзя присвоить вещ переменной цел
                raise AssignmentError(f"Нельзя присвоить вещественное значение ({value}) переменной типа ЦЕЛ.")
            else:  # <--- Эта строка должна иметь 12 пробелов отступа (3 уровня)
                # Другие типы тоже нельзя
                raise AssignmentError(
                    f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ЦЕЛ.")  # <--- Эта 16 пробелов (4 уровня)
        # Строка 279, на которую ошибка ->
        elif target_type == 'вещ':
            if value_type is int:
                # Неявное преобразование цел -> вещ
                return float(value)
            elif value_type is float:
                # Тип совпадает
                return value
            else:
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ВЕЩ.")

        elif target_type == 'лог':
            if value_type is bool:
                return value
            else:
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ЛОГ.")

        elif target_type == 'сим':
            if value_type is str and len(value) == 1:
                return value
            elif value_type is str and len(value) != 1:
                raise AssignmentError(
                    f"Нельзя присвоить строку \"{value}\" (длина {len(value)}) переменной типа СИМ (требуется длина 1).")
            else:
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа СИМ.")

        elif target_type == 'лит':
            if value_type is str:
                # Неявное преобразование сим -> лит допускается (строка длины 1 - это тоже строка)
                return value
            else:
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ЛИТ.")
        else:
            # Неизвестный целевой тип (может быть таблица или ошибка)
            raise DeclarationError(
                f"Неизвестный или неподдерживаемый целевой тип '{target_type}' для переменной '{var_name}'.")

    # --- Вспомогательные методы для вычислений ---

    def get_full_identifier(self, ctx: KumirParser.QualifiedIdentifierContext) -> str:
        """Возвращает полный текст идентификатора."""
        if ctx:
            return ctx.getText()
        return ""

    # --- Переопределение методов visit ---

    def visitProgram(self, ctx: KumirParser.ProgramContext):
        """Обрабатывает всю программу."""
        # Сбор определений процедур делегирован self.procedure_manager._collect_procedure_definitions,
        # который вызывается в self.interpret() перед началом обхода дерева.
        self.visitChildren(ctx)
        return None

    def visitImplicitModuleBody(self, ctx: KumirParser.ImplicitModuleBodyContext):
        """Обработка неявного тела модуля (программы без явного объявления модуля)."""
        # Сбор процедур уже выполнен в visitProgram
        print("[DEBUG][Visit] Обработка implicitModuleBody", file=sys.stderr)  # stdout -> stderr
        # Просто выполняем содержимое
        for item in ctx.children:
            if isinstance(item, KumirParser.AlgorithmDefinitionContext):
                # Выполняем только *основной* алгоритм
                # Основным считаем тот, у которого нет параметров в заголовке
                header = item.algorithmHeader()
                if header and not header.parameterList():
                    print(
                        f"[DEBUG][ImplicitBody] Запуск основного алгоритма: {header.algorithmNameTokens().getText().strip()}",
                        file=sys.stderr)
                    self.scope_manager.enter_scope()
                    try:
                        self.visit(item)
                    finally:
                        self.scope_manager.exit_scope() # <--- ДОБАВЬ ЭТУ СТРОКУ
                    break
        return None

    def visitModuleDefinition(self, ctx: KumirParser.ModuleDefinitionContext):
        """Обработка определения модуля."""
        # Сбор процедур уже выполнен в visitProgram
        print("[DEBUG][Visit] Обработка moduleDefinition", file=sys.stderr)  # stdout -> stderr
        # Если это неявный модуль, делегируем visitImplicitModuleBody
        if ctx.implicitModuleBody():
            return self.visit(ctx.implicitModuleBody())
        else:
            # Для явных модулей пока ничего не делаем (только собираем процедуры)
            # В будущем здесь может быть выполнение инициализации модуля
            # print("[DEBUG][ModuleDef] Явный модуль - выполнение пока не реализовано.",
            #       file=sys.stderr)  # stdout -> stderr
            return None

    def visitAlgorithmBody(self, ctx: KumirParser.AlgorithmBodyContext):
        """Обработка тела алгоритма."""
        # print(f"[DEBUG][VisitAlgorithmBody] ENTERED. Body text: {ctx.getText()[:100]}...", file=sys.stderr)
        if ctx.statementSequence():
            # print(f"[DEBUG][VisitAlgorithmBody] Visiting statementSequence.", file=sys.stderr)
            self.visit(ctx.statementSequence())
        # print(f"[DEBUG][VisitAlgorithmBody] EXITED.", file=sys.stderr)
        return None

    def visitStatementSequence(self, ctx: KumirParser.StatementSequenceContext): # Убедимся, что ctx на месте
        """Обработка последовательности операторов."""
        # print(f"[DEBUG][VisitStatementSequence] ENTERED. Sequence text: {ctx.getText()[:100]}...", file=sys.stderr)
        statements = ctx.statement()
        if statements:
            # print(f"[DEBUG][VisitStatementSequence] Found {len(statements)} statements.", file=sys.stderr)
            for i, stmt_ctx in enumerate(statements):
                # print(f"[DEBUG][VisitStatementSequence] Visiting statement #{i}: {stmt_ctx.getText()[:100]}...", file=sys.stderr)
                try:
                    self.visit(stmt_ctx)
                except LoopBreakException:
                    # print(f"[DEBUG][StatementSequence] LoopBreakException caught. Propagating.", file=sys.stderr)
                    raise
                except LoopContinueException:
                    # print(f"[DEBUG][StatementSequence] LoopContinueException caught. Propagating.", file=sys.stderr)
                    raise
                except ProcedureExitCalled:
                    # print(f"[DEBUG][StatementSequence] ProcedureExitCalled caught. Propagating.", file=sys.stderr)
                    raise
        # print(f"[DEBUG][VisitStatementSequence] EXITED.", file=sys.stderr)
        return None

    # Обработка узла многословного идентификатора (переименован)
    def visitQualifiedIdentifier(self, ctx: KumirParser.QualifiedIdentifierContext):
        # Возвращаем идентификатор
        return self.get_full_identifier(ctx)

    # Обработка узла переменной
    def visitLvalue(self, ctx: KumirParser.LvalueContext):
        # Этот метод может быть нужен, если lvalue обрабатывается отдельно,
        # например, для получения информации о переменной перед присваиванием.
        # В текущей реализации visitAssignmentStatement напрямую работает с qualifiedIdentifier и indexList.
        # Если visitLvalue все же вызывается, он должен вернуть информацию, достаточную для присваивания.
        # Например, имя переменной, информацию об индексах (если есть), и, возможно, текущее значение (хотя это опасно).

        # print(f"[DEBUG][visitLvalue] Called for LValue: {ctx.getText()}", file=sys.stderr)

        if not hasattr(ctx, 'qualifiedIdentifier') or not callable(ctx.qualifiedIdentifier):
            raise KumirSyntaxError("Некорректное lvalue: отсутствует метод qualifiedIdentifier.",
                                   line_index=ctx.start.line-1,
                                   column_index=ctx.start.column,
                                   line_content=self.get_line_content_from_ctx(ctx))
        
        q_ident_node = ctx.qualifiedIdentifier()
        if not q_ident_node:
            raise KumirSyntaxError("Некорректное lvalue: отсутствует идентификатор.",
                                   line_index=ctx.start.line-1,
                                   column_index=ctx.start.column,
                                   line_content=self.get_line_content_from_ctx(ctx))

        var_name = q_ident_node.getText()
        # print(f"[DEBUG][visitLvalue] LValue var_name: '{var_name}'", file=sys.stderr)
        
        # Получаем информацию о переменной из текущих scopes
        # Используем self.scope_manager.find_variable
        var_info = self.scope_manager.find_variable(var_name, ctx=q_ident_node)
        # print(f"[DEBUG][visitLvalue] Found var_info for '{var_name}': {var_info}", file=sys.stderr)

                    indices = []
        index_list_node = ctx.indexList()
        if index_list_node:
            # print(f"[DEBUG][visitLvalue] LValue has indices: {index_list_node.getText()}", file=sys.stderr)
            if hasattr(index_list_node, 'expression') and callable(index_list_node.expression):
                for index_expr_ctx in index_list_node.expression():
                    idx_val = self.evaluator.visitExpression(index_expr_ctx)
                        if not isinstance(idx_val, int):
                        raise KumirEvalError(f"Индекс для '{var_name}' должен быть целым числом (в LValue).",
                                           line_index=index_expr_ctx.start.line-1,
                                           column_index=index_expr_ctx.start.column,
                                           line_content=self.get_line_content_from_ctx(index_expr_ctx))
                        indices.append(idx_val)
            # print(f"[DEBUG][visitLvalue] Evaluated indices for '{var_name}': {indices}", file=sys.stderr)

        # visitLvalue должен вернуть структуру, которую visitAssignmentStatement сможет использовать.
        # Например, словарь с именем, информацией о переменной и индексами.
        return {
            'type': 'variable',
            'name': var_name,
            'var_info': var_info, # Словарь с type, value, is_table, initialized
            'indices': indices if index_list_node else None
        }

    # Обработка присваивания
    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        # Метод перенесен в StatementHandler
        return self.statement_handler.visitAssignmentStatement(ctx)

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext):
        # Метод перенесен в StatementHandler
        return self.statement_handler.visitIoStatement(ctx)

    def visitStatement(self, ctx: KumirParser.StatementContext):
        # print(f"[DEBUG][VisitStatement] Visiting statement: {ctx.getText()} (type: {type(ctx).__name__})", file=self.error_stream)
        if ctx.assignmentStatement():
            return self.visitAssignmentStatement(ctx.assignmentStatement())
        elif ctx.ioStatement():
            return self.visitIoStatement(ctx.ioStatement())
        elif ctx.loopStatement():
            return self.visitLoopStatement(ctx.loopStatement())
        elif ctx.ifStatement():
            return self.visitIfStatement(ctx.ifStatement())
        elif ctx.procedureCallStatement():
            # print(f"[DEBUG][VisitStatement] procedureCallStatement: {ctx.procedureCallStatement().getText()}", file=sys.stderr)
            # Вызов процедуры как отдельного оператора.
            # ExpressionEvaluator должен уметь обрабатывать узел ProcedureCallStatementContext.
            # Обычно он это делает через visitPostfixExpression, но здесь сам узел statement.
            # Передаем его в ExpressionEvaluator.
            return self.evaluator.visitExpression(ctx.procedureCallStatement()) # ИСПРАВЛЕНО: visit -> visitExpression
        elif ctx.exitStatement():
            return self.visitExitStatement(ctx.exitStatement())
        elif ctx.pauseStatement():
            return self.visitPauseStatement(ctx.pauseStatement())
        elif ctx.stopStatement():
            return self.visitStopStatement(ctx.stopStatement())
        elif ctx.assertionStatement():
            return self.visitAssertionStatement(ctx.assertionStatement())
        elif ctx.emptyStatement(): # Ошибка линтера здесь может быть ложной
                return None
        elif ctx.robotCommand(): # Ошибка линтера здесь может быть ложной
            return self.visitRobotCommand(ctx.robotCommand())
        elif ctx.errorStatement():
            line_idx, col_idx, lc = None, None, None
            if hasattr(ctx.errorStatement(), 'exception') and ctx.errorStatement().exception:
                 token = ctx.errorStatement().exception
                 line_idx = token.line -1
                 col_idx = token.column
                 lc = self.get_line_content_from_ctx(ctx.errorStatement())
            else: # Общий случай, если нет specific exception token
                 if hasattr(ctx, 'start') and ctx.start:
                    line_idx = ctx.start.line -1
                    col_idx = ctx.start.column
                    lc = self.get_line_content_from_ctx(ctx)

            raise KumirSyntaxError(f"Обнаружена синтаксическая ошибка парсером: '{ctx.errorStatement().getText()}'",
                                   line_index=line_idx, column_index=col_idx, line_content=lc)
            else:
            line_idx, col_idx, lc = None, None, None
            if hasattr(ctx, 'start') and ctx.start:
                line_idx = ctx.start.line - 1
                col_idx = ctx.start.column
                lc = self.get_line_content_from_ctx(ctx)
            raise KumirNotImplementedError(f"Неизвестный тип оператора: {ctx.getText()}", line_index=line_idx, column_index=col_idx, line_content=lc)

    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext):
        # Для ProcedureCallStatementContext нужно будет реализовать visitProcedureCallStatement
        # или, если это выражение, его можно передать в expression_evaluator.
        # Пока что просто вызываем visitChildren, если visitProcedureCallStatement не реализован.
        if hasattr(self, 'visitProcedureCallStatement'):
            return self.visit(ctx)
        else:
            # Это старая заглушка, которая вызывала ошибку, т.к. ProcedureCallStatementContext не имеет expression()
            # self.evaluator.visit(child.expression()) 
            # Вместо этого, если нет спец. обработчика, можно просто обойти детей
            # или вызвать ошибку о нереализованной фиче.
            print(f"[WARNING][visitStatement] visitProcedureCallStatement not implemented for: {ctx.getText()}", file=sys.stderr)
            # return self.visitChildren(ctx) # Может быть небезопасно, если дети - не операторы
            raise KumirNotImplementedError(f"Вызов процедуры '{ctx.getText()}' пока не поддерживается.", ctx.start.line)

    # --- ИСПРАВЛЕНИЕ: Добавляем явный visitArgumentList как метод ---
    def visitArgumentList(self, ctx: KumirParser.ArgumentListContext):
        parent_ctx = ctx.parentCtx 
        func_name_debug = "UNKNOWN_FUNC"
        if isinstance(parent_ctx, KumirParser.PostfixExpressionContext) and parent_ctx.primaryExpression():
            func_name_debug = parent_ctx.primaryExpression().getText()

        if self.debug: print(f"[Enter] visitArgumentList for {func_name_debug}({ctx.getText()})", file=sys.stderr)
        args = []
        for i, expr_ctx in enumerate(ctx.expression()):
            raw_arg_value = self.evaluator.visitExpression(expr_ctx)
            if self.debug: print(
                f"[DEBUG][ArgList Proc] For {func_name_debug}, Arg {i} ({expr_ctx.getText()}): evaluated to {repr(raw_arg_value)} ({type(raw_arg_value).__name__})",
                file=sys.stderr)
            args.append(raw_arg_value)
        if self.debug: print(f"[Exit] visitArgumentList for {func_name_debug}({ctx.getText()}) -> returns {repr(args)}",
                             file=sys.stderr)
        return args

    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext):
        # Логика этого метода должна быть в ExpressionEvaluator.
        line_idx, col_idx, lc = None, None, None
        if hasattr(ctx, 'start') and ctx.start:
            line_idx = ctx.start.line - 1
            col_idx = ctx.start.column
            lc = self.get_line_content_from_ctx(ctx)
        raise KumirNotImplementedError(
            f"visitPrimaryExpression не должен вызываться напрямую в KumirInterpreterVisitor. Обработка выражений делегируется ExpressionEvaluator.",
            line_index=line_idx, column_index=col_idx, line_content=lc
        )

    # --- НОВЫЙ МЕТОД: Форматирование вывода (уже был, проверяем отступ)---
    def _format_output_value(self, value, arg_ctx: KumirParser.IoArgumentContext) -> str:
        # Этот метод теперь не используется, так как форматирование происходит в StatementHandler.visitIoStatement
        # или напрямую при выводе. Оставляем заглушку или удаляем.
        # Для безопасности пока оставим заглушку с NotImplementedError.
        # print(f"[DEBUG][DEPRECATED _format_output_value] Called with value: {value}", file=sys.stderr)
        # raise KumirNotImplementedError("_format_output_value is deprecated and should not be called.")
        # ПРОСТО УДАЛЯЕМ, т.к. StatementHandler этим занимается
        pass

    # --- Метод для visitLiteral (уже был, проверяем отступ, но он помечен как удаленный)---
    # Этот метод, скорее всего, не используется, так как visitLiteral есть в ExpressionEvaluator
    def visitLiteral(self, ctx: KumirParser.LiteralContext):
        # Этот метод также не должен вызываться напрямую в KumirInterpreterVisitor.
        # Обработка литералов - задача ExpressionEvaluator.
        # print(f"[DEBUG][visitLiteral] KIV.visitLiteral called for '{ctx.getText() if ctx else 'None'}' - DELEGATING TO EVALUATOR (ERROR IF CALLED)", file=self.error_stream)
        line_idx, col_idx, lc = self.get_line_content_from_ctx(ctx), self.get_line_content_from_ctx(ctx), self.get_line_content_from_ctx(ctx)
        if hasattr(ctx, 'start') and ctx.start:
            line_idx = ctx.start.line - 1
            col_idx = ctx.start.column
            lc = self.get_line_content_from_ctx(ctx)
        raise KumirNotImplementedError(
            f"visitLiteral не должен вызываться напрямую в KumirInterpreterVisitor. Обработка литералов делегируется ExpressionEvaluator.",
            line_index=line_idx, column_index=col_idx, line_content=lc
        )

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        # Метод перенесен в StatementHandler
        return self.statement_handler.visitLoopStatement(ctx)

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext):
        # Метод перенесен в StatementHandler
        return self.statement_handler.visitExitStatement(ctx)

    def visitIfStatement(self, ctx: KumirParser.IfStatementContext):
        # Метод перенесен в StatementHandler
        return self.statement_handler.visitIfStatement(ctx)

    # --- Функции ввода-вывода (старая реализация, теперь в StatementHandler и get_input_line/write_output) ---
    def _handle_input(self, arg_ctx):
        # Этот метод больше не должен использоваться напрямую.
        # Логика ввода была перенесена в StatementHandler.visitIoStatement
        # и использует self.get_input_line()
        pass # УДАЛЕНО - логика в StatementHandler

    # def _handle_output(self, args_ctx): ... # Оставляем закомментированным, т.к. был pass

    # Новые методы, делегирующие в StatementHandler
    def visitPauseStatement(self, ctx: KumirParser.PauseStatementContext):
        return self.statement_handler.visitPauseStatement(ctx)

    def visitStopStatement(self, ctx: KumirParser.StopStatementContext):
        return self.statement_handler.visitStopStatement(ctx)

    def visitAssertionStatement(self, ctx: KumirParser.AssertionStatementContext):
        return self.statement_handler.visitAssertionStatement(ctx)

    def visitRobotCommand(self, ctx: KumirParser.RobotCommandContext):
        """Обработка команд исполнителя Робот."""
        # print(f"[DEBUG][VisitRobotCommand] Executing robot command: {ctx.getText()}", file=sys.stderr)
        command_name_node = None
        if hasattr(ctx, 'UP') and ctx.UP(): command_name_node = ctx.UP()
        elif hasattr(ctx, 'DOWN') and ctx.DOWN(): command_name_node = ctx.DOWN()
        elif hasattr(ctx, 'LEFT') and ctx.LEFT(): command_name_node = ctx.LEFT()
        elif hasattr(ctx, 'RIGHT') and ctx.RIGHT(): command_name_node = ctx.RIGHT()
        elif hasattr(ctx, 'PAINT') and ctx.PAINT(): command_name_node = ctx.PAINT()

        if command_name_node:
            command_name = command_name_node.getText()
            lc = self.get_line_content_from_ctx(ctx)
            raise KumirNotImplementedError(
                f"Команда исполнителя Робот '{command_name}' пока не реализована.",
                line_index=ctx.start.line -1,
                column_index=ctx.start.column,
                line_content=lc
            )
        else:
            lc = self.get_line_content_from_ctx(ctx)
            raise KumirSyntaxError(
                "Неизвестная или некорректная команда Робота.",
                line_index=ctx.start.line -1,
                column_index=ctx.start.column,
                line_content=lc
            )
        return None

    # --- Глобальная область видимости и выполнение программы ---
    def push_scope(self):
        """Алиас для enter_scope (для совместимости)."""
        self.scope_manager.enter_scope()

    def pop_scope(self):
        """Алиас для exit_scope (для совместимости)."""
        self.scope_manager.exit_scope()

    def get_child_safely(self, parent_ctx: antlr4.ParserRuleContext, child_name: str) -> Optional[antlr4.ParserRuleContext]:
        """
        Безопасно получает дочерний узел по имени его метода-аксессора.
        Если метод возвращает список, берет первый элемент.
        Возвращает None, если атрибут/метод отсутствует или список пуст.
        """
        # Используем sys.stderr для отладочных сообщений, если они нужны
        # import sys # Убедимся, что sys импортирован, если будем раскомментировать принты

        if not parent_ctx or not hasattr(parent_ctx, child_name):
            # print(f"[DEBUG][get_child_safely] Parent context is None or attribute '{child_name}' not found on {type(parent_ctx).__name__}.", file=sys.stderr)
            return None
        
        try:
            child_attr = getattr(parent_ctx, child_name)
            
            child_node_or_list = None
            if callable(child_attr):
                # print(f"[DEBUG][get_child_safely] Calling method '{child_name}()' on {type(parent_ctx).__name__}", file=sys.stderr)
                child_node_or_list = child_attr()
            else:
                # print(f"[DEBUG][get_child_safely] Accessing attribute '{child_name}' on {type(parent_ctx).__name__}", file=sys.stderr)
                child_node_or_list = child_attr

            if isinstance(child_node_or_list, list):
                # print(f"[DEBUG][get_child_safely] Method '{child_name}()' returned a list of length {len(child_node_or_list)}", file=sys.stderr)
                return child_node_or_list[0] if child_node_or_list else None
            # Проверим, что это экземпляр ParserRuleContext или None, прежде чем вернуть
            elif isinstance(child_node_or_list, antlr4.ParserRuleContext) or child_node_or_list is None:
                # print(f"[DEBUG][get_child_safely] Method '{child_name}()' returned: {type(child_node_or_list).__name__}", file=sys.stderr)
                return child_node_or_list
            else:
                # print(f"[DEBUG][get_child_safely] Method '{child_name}()' returned unexpected type: {type(child_node_or_list).__name__}. Value: {str(child_node_or_list)[:100]}", file=sys.stderr)
                # Если это не список и не ParserRuleContext (и не None), это может быть TerminalNode или что-то еще.
                # Для LValue разбора мы обычно ожидаем ParserRuleContext.
                # Если возвращается TerminalNodeImpl, это может быть ID, но get_full_identifier работает с QualifiedIdentifierContext.
                # Пока что вернем его, если это ANTLR дерево, иначе None.
                if hasattr(child_node_or_list, 'symbol'): # Признак TerminalNodeImpl
                    return child_node_or_list 
                return None # Не то, что мы обычно ищем как "узел контекста" для дальнейшего разбора lvalue
                
        except Exception as e:
            # print(f"[ERROR][get_child_safely] Exception while getting child '{child_name}' from {type(parent_ctx).__name__}: {e}", file=sys.stderr)
            return None

    # Вспомогательные методы для evaluate_expression, если еще не там
    # (или они могут быть в ExpressionEvaluator)

    def _call_builtin_function(self, func_name: str, args: List[Any], ctx: ParserRuleContext):
        print(f"[DEBUG][_call_builtin_function] Calling '{func_name}' with args: {args}", file=sys.stderr)
        func_name_lower = func_name.lower()
        # Используем self.BUILTIN_FUNCTIONS, который теперь ссылается на импортированный словарь
        if func_name_lower not in self.BUILTIN_FUNCTIONS:
            # --- ИСПРАВЛЕНИЕ KumirEvalError ---
            l_content_bf_not_found = self.get_line_content_from_ctx(ctx)
            raise KumirEvalError(f"Строка {ctx.start.line}: Встроенная функция '{func_name}' не найдена.", line_index=ctx.start.line -1, column_index=ctx.start.column, line_content=l_content_bf_not_found) 
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

        func_info = self.BUILTIN_FUNCTIONS[func_name_lower]
        min_args = func_info.get('min_args', 0)
        max_args = func_info.get('max_args', float('inf'))
        arg_count = len(args)

        if not (min_args <= arg_count <= max_args):
            expected_args_str = str(min_args) if min_args == max_args else f"от {min_args} до {max_args}"
            raise KumirArgumentError(
                f"Неверное количество аргументов для функции '{func_name}'. Ожидалось {expected_args_str}, получено {arg_count}.",
                line_index=ctx.start.line - 1,
                column_index=ctx.start.column,
                line_content=self.get_line_content_from_ctx(ctx)
            )

        # Проверка типов аргументов, если определены arg_types
        expected_arg_types_options = func_info.get('arg_types')
        if expected_arg_types_options: # Это список списков возможных наборов типов
            actual_arg_types = [self._get_kumir_type_name(arg) for arg in args]
            match_found = False
            for expected_types_set in expected_arg_types_options:
                if len(expected_types_set) == arg_count:
                    current_set_match = True
                    for i, expected_type in enumerate(expected_types_set):
                        if expected_type == 'любой': continue # Тип 'любой' всегда подходит
                        if not self._check_type_compatibility(actual_arg_types[i], expected_type, args[i]):
                            current_set_match = False
                            break
                    if current_set_match:
                        match_found = True
                        break
            
            if not match_found:
                # Формируем сообщение об ошибке с более детальной информацией
                expected_types_str_list = []
                for opt_idx, opt_set in enumerate(expected_arg_types_options):
                    if len(opt_set) == arg_count: # Показываем только те варианты, которые совпадают по количеству аргументов
                        expected_types_str_list.append(f"вариант {opt_idx+1}: ({', '.join(opt_set)})")
                
                if not expected_types_str_list: # Если нет вариантов с таким кол-вом аргументов (хотя это должно было отсечься раньше)
                    expected_details = f"для количества аргументов {arg_count} не определены ожидаемые типы."
                else:
                    expected_details = "ожидались типы: " + " или ".join(expected_types_str_list)
                
                raise KumirArgumentError(
                    f"Несоответствие типов аргументов для функции '{func_name}'. Переданы типы: ({', '.join(actual_arg_types)}), а {expected_details}.",
                    line_index=ctx.start.line - 1,
                    column_index=ctx.start.column,
                    line_content=self.get_line_content_from_ctx(ctx)
                )

        handler = func_info['handler']
        try:
            # Передаем self (экземпляр KumirInterpreterVisitor) первым аргументом в handler
            return handler(self, args, ctx) 
        except KumirEvalError as e:
            # --- ИСПРАВЛЕНИЕ: Атрибуты line/column могут отсутствовать или быть None ---
            # Проверяем, есть ли у 'e' уже установленные line_index и column_index.
            # Если нет, или они None, устанавливаем их из ctx.
            # Это нужно делать аккуратно, чтобы не перезаписать более точную информацию из вложенного вызова.
            # Пока что, если line_index не установлен или None, используем ctx.
            if not hasattr(e, 'line') or e.line is None:
                 # Устанавливаем, только если еще не установлено
                 # Это может быть неидеально, если ошибка произошла глубже с другой строкой
                 # Но для ошибок из хендлеров без информации о строке, это лучше чем ничего.
                 # setattr(e, 'line_index', ctx.start.line - 1) # Закомментировано, т.к. KumirEvalError неизменяемый
                 pass 
            if not hasattr(e, 'column') or e.column is None:
                 # setattr(e, 'column_index', ctx.start.column) # Закомментировано
                 pass
            raise # Перевыбрасываем оригинальное исключение 'e'
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
        except Exception as e:
            # Перехватываем другие возможные исключения из хендлера
            # и оборачиваем их в KumirEvalError с указанием строки
            print(f"[ERROR][_call_builtin_function] Unexpected error in handler for '{func_name}': {type(e).__name__}: {e}", file=sys.stderr)
            # traceback.print_exc(file=sys.stderr)
            # --- ИСПРАВЛЕНИЕ KumirEvalError ---
            raise KumirEvalError(f"Строка {ctx.start.line}: Ошибка при выполнении встроенной функции '{func_name}': {e}", line_index=ctx.start.line -1, column_index=ctx.start.column -1 if hasattr(ctx.start, 'column') and ctx.start.column > 0 else 0)
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    def _get_kumir_type_name(self, value: Any) -> str:
        """Возвращает КуМир-совместимое имя типа для данного Python-значения."""
        py_type = type(value)
        if py_type is int:
            return 'цел'
        elif py_type is float:
            return 'вещ'
        elif py_type is bool:
            return 'лог'
        elif py_type is str:
            # В КуМире 'лит' для строк, 'сим' для одиночных символов.
            # Для общих целей (например, сообщения об ошибках) 'лит' подходит.
            # Если нужен 'сим', контекст вызова должен это учитывать.
            return 'лит'
        elif isinstance(value, KumirTableVar):
            # Для таблиц возвращаем их базовый тип
            return value.base_kumir_type_name
        else:
            # Для неизвестных Python-типов
            # print(f"[WARNING][_get_kumir_type_name] Неизвестный Python тип: {py_type.__name__} для значения {repr(value)}. Возвращено 'неизвестный тип'.", file=sys.stderr)
            return 'неизвестный тип'

    def _check_type_compatibility(self, actual_type_str: str, expected_type_str: str, actual_value: Any) -> bool:
        """
        Проверяет совместимость фактического типа значения КуМир с ожидаемым типом.
        Например, 'цел' совместим с 'вещ'.
        """
        if actual_type_str == expected_type_str:
            return True
        
        # Разрешаем целое число там, где ожидается вещественное
        if expected_type_str == 'вещ' and actual_type_str == 'цел':
            return True
        
        # Разрешаем символ там, где ожидается строка (лит)
        if expected_type_str == 'лит' and actual_type_str == 'сим':
            return True

        # Можно добавить другие правила совместимости, если потребуется.
        # Например, если бы у нас был общий тип "число", который включал бы и цел, и вещ.

        return False

    # --- ОБРАБОТЧИКИ ДЛЯ НОВЫХ ВСТРОЕННЫХ ФУНКЦИЙ УДАЛЕНЫ (irand, rand) ---
    # def _handle_irand(self, a: int, b: int, ctx: Optional[ParserRuleContext]):
    #     ...
    # def _handle_rand(self, a: Any, b: Any, ctx: Optional[ParserRuleContext]):
    #     ...
            

    # --- ДОБАВЛЯЕМ НОВЫЙ МЕТОД VISITSWITCHSTATEMENT ---
    def visitSwitchStatement(self, ctx: KumirParser.SwitchStatementContext):
        print(f"[DEBUG][visitSwitchStatement] ENTERED for ctx: {ctx.getText()}", file=sys.stderr)

        # Убедимся, что здесь нет старой логики поиска глобального switch_expr_ctx
        # и генерации KumirSyntaxError, если он не найден.
        # Пример удаляемых строк (если они есть):
        # switch_expr_ctx = None 
        # if hasattr(ctx, 'expression') ... :
        #    ...
        # if not switch_expr_ctx:
        #     raise KumirSyntaxError("Отсутствует выражение в операторе ВЫБОР", ctx.start.line, ctx.start.column)

        # Актуальная логика, основанная на том, что глобального выражения нет:
        # Выражение, по которому идет switch, видимо, отсутствует как отдельная сущность.
        # Вместо этого, каждая ветка "при" имеет свое условие.

        executed_branch = False
        
        case_block_nodes = [] 
        if hasattr(ctx, 'caseBlock') and callable(ctx.caseBlock): 
            potential_case_blocks = ctx.caseBlock() 
            if isinstance(potential_case_blocks, list):
                case_block_nodes = potential_case_blocks 
            elif potential_case_blocks is not None: 
                case_block_nodes = [potential_case_blocks] 
        
        if not case_block_nodes and hasattr(ctx, 'getTypedRuleContexts'): # Добавим проверку на getTypedRuleContexts
            typed_case_blocks = ctx.getTypedRuleContexts(KumirParser.CaseBlockContext) 
            if typed_case_blocks:
                case_block_nodes = typed_case_blocks

        print(f"[DEBUG][visitSwitchStatement] Found {len(case_block_nodes)} caseBlock node(s).", file=sys.stderr)

        for i_case, current_case_block_ctx in enumerate(case_block_nodes):
            if not current_case_block_ctx or not isinstance(current_case_block_ctx, KumirParser.CaseBlockContext):
                print(f"[DEBUG][visitSwitchStatement]   Node {i_case} is None or not a CaseBlockContext, skipping.", file=sys.stderr)
                continue

            print(f"[DEBUG][visitSwitchStatement] Processing caseBlock {i_case}: {current_case_block_ctx.getText()}", file=sys.stderr)
            
            # --- ОТЛАДКА: ЧТО ЕСТЬ ВНУТРИ CaseBlockContext? ---
            # print(f"[DEBUG][visitSwitchStatement]   Attributes of current_case_block_ctx ({type(current_case_block_ctx).__name__}):", file=sys.stderr)
            # for attr_name in dir(current_case_block_ctx):
            #     if not attr_name.startswith('__'):
            #         try:
            #             is_method_likely = callable(getattr(current_case_block_ctx, attr_name)) and \
            #                               hasattr(getattr(current_case_block_ctx, attr_name), '__code__') and \
            #                               getattr(current_case_block_ctx, attr_name).__code__.co_argcount == 1 # self
            #             if is_method_likely and attr_name not in ['getText', 'toString', 'parentCtx', 'getPayload', 'getSourceInterval', 'getRuleContext']:
            #                  print(f"    {attr_name}: <method>", file=sys.stderr)
            #             else:
            #                 attr_value = getattr(current_case_block_ctx, attr_name)
            #                 print(f"    {attr_name}: {attr_value}", file=sys.stderr)
            #         except Exception as e_attr:
            #             print(f"    {attr_name}: <Error getting attribute: {e_attr}>", file=sys.stderr)
            # --- КОНЕЦ ОТЛАДКИ ---

            # --- НАЧАЛО ИЗМЕНЕНИЙ ---
            condition_expr_ctx = None
            if hasattr(current_case_block_ctx, 'expression') and callable(current_case_block_ctx.expression):
                condition_expr_ctx = current_case_block_ctx.expression() # Используем .expression()
            
            if not condition_expr_ctx:
                print(f"[ERROR][visitSwitchStatement]   CaseBlock {i_case} does not have a callable .expression() method or it returned None. Skipping.", file=sys.stderr)
                continue
            
            # Дополнительная проверка типа, если нужно
            if not isinstance(condition_expr_ctx, KumirParser.ExpressionContext):
                print(f"[ERROR][visitSwitchStatement]   Call to .expression() on CaseBlock {i_case} did not return an ExpressionContext (got {type(condition_expr_ctx).__name__}). Skipping.", file=sys.stderr)
                continue
            # --- КОНЕЦ ИЗМЕНЕНИЙ ---

            # Эта проверка может стать избыточной, но оставим пока для безопасности
            if not condition_expr_ctx:
                 print(f"[ERROR][visitSwitchStatement]   CaseBlock {i_case} resolved to a None condition_expr_ctx (this should not happen after previous checks). Skipping.", file=sys.stderr)
                 continue

            print(f"[DEBUG][visitSwitchStatement]   Condition for case {i_case}: {condition_expr_ctx.getText()}", file=sys.stderr)
            
            # Вычисляем условие ветки "при"
            # Условие должно вычисляться в логическое значение или значение, которое можно сравнить
            # Например, "при m=1", "при x > 5", "при флаг"
            # Результат visitExpression должен быть bool или чем-то, что _perform_binary_operation (для =) может обработать
            
            # Здесь нам нужно не просто вычислить значение выражения (например, m=1),
            # а вычислить значение условия (т.е. результат сравнения m с 1).
            # ExpressionEvaluator.visitExpression должен сам обработать операторы сравнения типа '='
            condition_value = self.evaluator.visitExpression(condition_expr_ctx) # ИЗМЕНЕНО visit на visitExpression
            
            print(f"[DEBUG][visitSwitchStatement]   Condition value for case {i_case}: {condition_value} (type: {type(condition_value).__name__})", file=sys.stderr)

            # Проверяем, истинно ли условие
            # Для КуМира, если это не bool, то 0/0.0 это ложь, остальное - истина.
            # Но лучше, если visitExpression для сравнений (m=1) вернет bool.
            is_condition_true = False
            if isinstance(condition_value, bool):
                is_condition_true = condition_value
            elif isinstance(condition_value, (int, float)):
                is_condition_true = (condition_value != 0) # В КуМире 0 - ложь, не 0 - истина
            else:
                print(f"[WARNING][visitSwitchStatement] Condition for case {i_case} evaluated to non-boolean/non-numeric type: {type(condition_value)}. Treating as FALSE.", file=sys.stderr)
            
            if is_condition_true:
                print(f"[DEBUG][visitSwitchStatement]   Condition for case {i_case} is TRUE. Executing its statementSequence.", file=sys.stderr)
                
                statement_seq_ctx = current_case_block_ctx.statementSequence()
                if statement_seq_ctx:
                    self.visit(statement_seq_ctx)
                else:
                    print(f"[WARNING][visitSwitchStatement] Case {i_case} is TRUE but has no statementSequence.", file=sys.stderr)
                
                executed_branch = True
                break  # Выходим из цикла for по case_branch_nodes, так как нашли подходящую ветку

        # Если ни одна ветка "при" не выполнилась и есть "иначе"
        if not executed_branch:
            # Проверяем наличие ELSE на уровне SwitchStatementContext
            else_token = ctx.ELSE() if hasattr(ctx, 'ELSE') and callable(ctx.ELSE) else None
            if else_token:
                 # Ищем statementSequence, которая относится к ELSE.
                 # --- ИСПРАВЛЕНИЕ ДЛЯ ОШИБКИ ЛИНТЕРА 2133, 2139 ---
                 # В KumirParser.SwitchStatementContext нет метода otherwiseBranch().
                 # Вместо этого, если есть ELSE(), то соответствующий statementSequence
                 # можно найти, если он является одним из дочерних узлов statementSequence()
                 # и идет после caseBlock'ов.
                 # Если ctx.statementSequence() возвращает список, и у нас был хотя бы один caseBlock,
                 # то statementSequence для ELSE будет последним в этом списке, если он есть.
                 
                 else_statement_sequence_ctx = None
                 all_statement_sequences = ctx.statementSequence() # Это список
                 num_case_blocks = len(case_block_nodes) # case_block_nodes уже определены выше

                 if isinstance(all_statement_sequences, list) and len(all_statement_sequences) > num_case_blocks:
                     # Если есть больше statementSequences, чем caseBlocks,
                     # и есть токен ELSE, то последний statementSequence - это ветка "иначе"
                     else_statement_sequence_ctx = all_statement_sequences[-1]
                 elif isinstance(all_statement_sequences, KumirParser.StatementSequenceContext) and num_case_blocks == 0 and else_token :
                     # Если нет case-блоков, но есть ELSE и один statementSequence
                     else_statement_sequence_ctx = all_statement_sequences
                 # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
                 
                 if else_statement_sequence_ctx:
                    print(f"[DEBUG][visitSwitchStatement] Executing OTHERWISE branch: {else_statement_sequence_ctx.getText()}", file=sys.stderr)
                    self.visit(else_statement_sequence_ctx)
                 else:
                    print(f"[WARNING][visitSwitchStatement] ELSE branch exists, but its statementSequence was not found or is empty.", file=sys.stderr)
            else:
                print(f"[DEBUG][visitSwitchStatement] No matching CASE and no OTHERWISE branch.", file=sys.stderr)
        
        return None

    def get_line_content_from_ctx(self, ctx):
        if ctx and hasattr(ctx, 'start') and ctx.start and hasattr(self, 'program_lines') and self.program_lines:
            # ANTLR линии 1-индексированные, self.program_lines 0-индексированный
            line_num_0_indexed = ctx.start.line - 1
            if 0 <= line_num_0_indexed < len(self.program_lines):
                return self.program_lines[line_num_0_indexed]
        return None

    def interpret(self, tree, program_text):
        self.program_lines = program_text.splitlines()
        
        self.scope_manager.scopes = [{}] 
        self.procedure_manager.clear_procedures() # Clear any previous procedures
        self.loop_depth = 0
        self.exit_flags = []
        self.input_buffer = []
        self.return_value_from_function = None
        self.function_call_active = False

        self.procedure_manager._collect_procedure_definitions(tree) # <--- CALL DELEGATED

        main_alg_name = None
        main_alg_proc_info = None # Store the whole proc_info for main algorithm
        
        # Find main algorithm (no params, not a function)
        for name_lower, proc_info_candidate in self.procedure_manager.procedures.items():
            if not proc_info_candidate.get('params') and not proc_info_candidate.get('is_function'):
                if not main_alg_name: 
                    main_alg_name = proc_info_candidate['name'] 
                    main_alg_proc_info = proc_info_candidate
                    break 
        
        if not main_alg_name or not main_alg_proc_info:
            if len(self.procedure_manager.procedures) == 1:
                single_proc_name_lower = list(self.procedure_manager.procedures.keys())[0]
                main_alg_proc_info = self.procedure_manager.procedures[single_proc_name_lower]
                main_alg_name = main_alg_proc_info['name']
                if main_alg_proc_info.get('params') or main_alg_proc_info.get('is_function'):
                     lc = self.get_line_content_from_ctx(main_alg_proc_info.get('header_ctx'))
                     raise KumirEvalError("Не найден главный алгоритм для запуска (единственная процедура/функция требует аргументы или является функцией).",
                                          line_index=main_alg_proc_info.get('header_ctx').start.line -1 if main_alg_proc_info.get('header_ctx') else None,
                                          column_index=main_alg_proc_info.get('header_ctx').start.column if main_alg_proc_info.get('header_ctx') else None,
                                          line_content=lc)
            else:
                raise KumirEvalError("Не найден главный алгоритм для запуска (алгоритм без параметров и не функция).")

        try:
            main_call_data = {
                'name': main_alg_name,
            }
            main_call_site_ctx = main_alg_proc_info.get('header_ctx')
            self.procedure_manager._execute_procedure_call(main_call_data, [], main_call_site_ctx)

        except KumirSyntaxError as e: 
            self.error_stream.write(str(e) + '\n')
            return None
        except KumirNotImplementedError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except KumirEvalError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except KumirNameError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except KumirTypeError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except KumirIndexError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except KumirArgumentError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except DeclarationError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except AssignmentError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except InputOutputError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except RobotMovementError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except RobotSensorError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except RobotActionError as e:
            self.error_stream.write(str(e) + '\n')
            return None
        except StopExecutionException:
            pass 
        except Exception as e:
            self.error_stream.write(f"Неожиданная ошибка выполнения: {type(e).__name__}: {e}\n")
            return None
        finally:
            pass

        # Захват вывода, если KumirInterpreterVisitor сам пишет в self.output_stream
        # Если interpret_kumir использует redirect_stdout, то это не нужно здесь.
        # Однако, если output_stream это StringIO, то его значение и есть результат.
        if hasattr(self.output_stream, 'getvalue'):
            # print("[DEBUG][Interpret] Returning output_stream.getvalue()", file=sys.stderr)
            return self.output_stream.getvalue()
        else:
            # print("[DEBUG][Interpret] output_stream has no getvalue. Returning None as output.", file=sys.stderr)
            return None # или пустую строку, если ожидается строка

    def get_input_line(self, prompt: Optional[str] = None) -> str:
        """Читает строку из input_stream. Опционально выводит prompt."""
        if prompt and hasattr(self.output_stream, 'isatty') and self.output_stream.isatty():
            self.output_stream.write(prompt)
            self.output_stream.flush()
        if self.input_buffer:
            return self.input_buffer.pop(0)
        line = self.input_stream.readline()
        if not line:
            raise KumirInputError("Достигнут конец входного потока (EOF)")
        return line.rstrip('\r\n')

    def write_output(self, text: str):
        """Пишет текст в output_stream."""
        self.output_stream.write(text)

# Эта функция должна быть на верхнем уровне модуля, а не методом класса
def interpret_kumir(code: str):
    """
    Интерпретирует код на языке КуМир.

    Args:
        code (str): Исходный код программы

    Returns:
        str: Захваченный вывод программы
    """
    from antlr4 import InputStream, CommonTokenStream # УБРАН tree
    from .generated.KumirLexer import KumirLexer
    from .generated.KumirParser import KumirParser
    # DiagnosticErrorListener is defined in this file, so no relative import needed.

    input_stream = InputStream(code)
    lexer = KumirLexer(input_stream)
    lexer.removeErrorListeners()
    error_listener = DiagnosticErrorListener()  # Instantiate local class
    lexer.addErrorListener(error_listener)

    token_stream = CommonTokenStream(lexer)
    parser = KumirParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)  # Используем тот же слушатель для парсера

    tree = None
    try:
        tree = parser.program()  # Attempt to parse
    except KumirSyntaxError:  # Re-raise if DiagnosticErrorListener raised it
        raise
    except Exception as e:  # Catch other ANTLR or parsing-related exceptions
        raise KumirSyntaxError(f"Ошибка синтаксического анализа: {e}", 0, 0) from e

    visitor = KumirInterpreterVisitor() # Конструктор без аргументов

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    stdout_capture = StringIO()       # <--- Сначала объявляем
    sys.stdout = stdout_capture 
    
    # --- DEBUG ID ---    
    print(f"[DEBUG_INTERPRET_KUMIR_SETUP] id(sys.stdout) after assignment: {id(sys.stdout)}, id(stdout_capture): {id(stdout_capture)}", file=sys.stderr) # <--- Потом используем
    # --- END DEBUG ID ---

    try:
        visitor.visit(tree)
    except KumirInputRequiredError:
        raise
    except Exception as e:
        raise
    finally:
        # --- DEBUG ID ---    
        print(f"[DEBUG_INTERPRET_KUMIR_FINALLY] id(sys.stdout) before restore: {id(sys.stdout)}, id(stdout_capture): {id(stdout_capture)}", file=sys.stderr)
        # --- END DEBUG ID ---
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    print(
        f"[DEBUG_INTERPRET_KUMIR] About to return from interpret_kumir. stdout_capture type: {type(stdout_capture)}",
        file=sys.stderr)
    captured_content = stdout_capture.getvalue()

    # --- НОВОЕ: Добавляем \n в конец, если его нет --- 
    if captured_content and not captured_content.endswith('\n'):
        captured_content += '\n'
        print("[DEBUG_INTERPRET_KUMIR] Appended final newline to stdout_capture.", file=sys.stderr)
    # --- КОНЕЦ НОВОГО ---

    print(
        f"[DEBUG_INTERPRET_KUMIR] Content of stdout_capture ({len(captured_content)} chars):\n>>>\n{captured_content}\n<<<",
        file=sys.stderr)

    return captured_content