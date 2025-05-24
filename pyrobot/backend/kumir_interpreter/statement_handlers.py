from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from pyrobot.backend.kumir_interpreter.generated.KumirLexer import KumirLexer
from pyrobot.backend.kumir_interpreter.generated.KumirParser import KumirParser
from pyrobot.backend.kumir_interpreter.generated.KumirParserVisitor import KumirParserVisitor

from pyrobot.backend.kumir_interpreter.kumir_exceptions import KumirLexerError, KumirParserError, KumirRuntimeError, KumirArgumentError #, KumirIndexError, KumirReturnError, KumirFileError
from pyrobot.backend.kumir_interpreter.kumir_variable import KumirVariable # Путь исправлен
# from pyrobot.backend.kumir_interpreter.expression_evaluator import ExpressionEvaluator # Будет получен из interpreter
from pyrobot.backend.kumir_interpreter.kumir_scope import KumirScope # Путь исправлен
from pyrobot.backend.kumir_interpreter.interpreter_components.io_handler import IOHandler
from pyrobot.backend.kumir_interpreter.interpreter_components.main_visitor import KumirInterpreterVisitor


class StatementHandler(KumirParserVisitor):
    def __init__(self, interpreter: KumirInterpreterVisitor, io_handler: IOHandler):
        self.interpreter = interpreter
        self.io_handler = io_handler
        self.expression_evaluator = self.interpreter.expression_evaluator

    def visitVariableDeclarationStatement(self, ctx: KumirParser.VariableDeclarationContext):
        return self.interpreter.visitVariableDeclaration(ctx)

    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        pass # Заглушка

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext):
        pass # Заглушка

    def visitIfStatement(self, ctx: KumirParser.IfStatementContext):
        pass # Заглушка

    def _evaluate_condition(self, condition_ctx: KumirParser.ExpressionContext) -> bool:
        value = self.expression_evaluator.visitExpression(condition_ctx)
        if not isinstance(value, bool):
            # TODO: Использовать KumirTypeError после его определения
            raise TypeError(f"Условие должно быть логического типа, получено {type(value)}")
        return value

    def visitWhileLoop(self, ctx: KumirParser.WhileLoopContext):
        pass # Заглушка

    def visitForLoop(self, ctx: KumirParser.ForLoopContext):
        pass # Заглушка

    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext):
        pass # Заглушка

    def visitFunctionCallStatement(self, ctx: KumirParser.FunctionCallStatementContext):
        pass # Заглушка

    def visitReturnStatement(self, ctx: KumirParser.ReturnStatementContext):
        pass # Заглушка

    def visitBlock(self, ctx: KumirParser.BlockContext):
        pass

    def visitSubAlgorithm(self, ctx: KumirParser.SubAlgorithmContext):
        pass # Заглушка