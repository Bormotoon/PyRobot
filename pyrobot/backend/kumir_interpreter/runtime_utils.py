# runtime_utils.py
# Этот файл будет содержать вспомогательные утилиты, используемые интерпретатором.

from io import StringIO
import sys
from .generated.KumirLexer import KumirLexer
from .generated.KumirParser import KumirParser
from antlr4 import InputStream, CommonTokenStream
from .interpreter_components.constants import *
from .interpreter_components.declaration_visitors import DeclarationVisitorMixin
from .interpreter_components.procedure_manager import ProcedureManager
from .interpreter_components.statement_handlers import StatementHandler
from .expression_evaluator import ExpressionEvaluator
from .kumir_exceptions import KumirSyntaxError, KumirInputRequiredError
from .generated.KumirParserVisitor import KumirParserVisitor

# DiagnosticErrorListener и KumirInterpreterVisitor импортируем из interpreter_components или определяем здесь, если нужно
from .interpreter_components.main_visitor import DiagnosticErrorListener, KumirInterpreterVisitor

def interpret_kumir(code: str):
    """
    Интерпретирует код на языке КуМир.
    Args:
        code (str): Исходный код программы
    Returns:
        str: Захваченный вывод программы
    """
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
    stdout_capture = StringIO()
    sys.stdout = stdout_capture
    try:
        visitor.visit(tree)
    except KumirInputRequiredError:
        raise
    except Exception as e:
        raise
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    captured_content = stdout_capture.getvalue()
    if captured_content and not captured_content.endswith('\n'):
        captured_content += '\n'
    return captured_content