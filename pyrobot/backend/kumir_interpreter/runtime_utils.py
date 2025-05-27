# runtime_utils.py
# Этот файл будет содержать вспомогательные утилиты, используемые интерпретатором.

from io import StringIO
import sys
import logging 
from typing import Optional

# ANTLR and generated code
from .generated.KumirLexer import KumirLexer
from .generated.KumirParser import KumirParser
from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

# Interpreter components
from .interpreter_components.main_visitor import KumirInterpreterVisitor
from .kumir_exceptions import KumirSyntaxError, KumirInputRequiredError, KumirRuntimeError 

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG) # Добавим базовую конфигурацию логирования

class DiagnosticErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_msg = f"Синтаксическая ошибка: {msg}"
        # KumirSyntaxError ожидает line_index (0-based).
        raise KumirSyntaxError(error_msg, line_index=line - 1, column_index=column)

def interpret_kumir(code: str, input_data: Optional[str] = None) -> str:
    """
    Интерпретирует код на языке КуМир.
    Args:
        code (str): Исходный код программы
        input_data (Optional[str]): Входные данные для программы.
    Returns:
        str: Захваченный вывод программы или сообщение об ошибке.
    """
    logger.debug(f"interpret_kumir called with code:\\n{code}") # Лог входного кода
    input_stream_antl = InputStream(code)
    lexer = KumirLexer(input_stream_antl)
    lexer.removeErrorListeners()
    error_listener = DiagnosticErrorListener()
    lexer.addErrorListener(error_listener)

    token_stream = CommonTokenStream(lexer)
    parser = KumirParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = None
    try:
        tree = parser.program()
    except KumirSyntaxError as e:
        line_info = f"строка {e.line_index + 1}" if e.line_index is not None else "N/A"
        col_info = f", столбец {e.column_index}" if e.column_index is not None else ""
        return f"SYNTAX_ERROR: {e.args[0]} ({line_info}{col_info})"
    except Exception as e:
        error_info = f"UNEXPECTED_PARSING_ERROR: {type(e).__name__}: {e}"
        return error_info

    original_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    input_buffer = StringIO(input_data if input_data else "")
    program_lines_list = code.splitlines()

    def input_fn():
        line = input_buffer.readline()
        return line.rstrip('\\r\\n')
    
    def output_fn(text: str):
        logger.debug(f"output_fn called with text: '{text}'") # Лог вызова output_fn
        captured_output.write(text)
        # captured_output.flush() # Для StringIO обычно не нужен, но можно добавить для консистентности

    def error_fn(text: str):
        sys.stderr.write(text)
        # sys.stderr.flush() # Для stderr может быть полезно

    visitor = KumirInterpreterVisitor(
        input_stream=input_fn,
        output_stream=output_fn, 
        error_stream=error_fn,
        program_lines=program_lines_list
    )

    try:
        visitor.visitProgram(tree)
    except KumirInputRequiredError:
        pass 
    except KumirSyntaxError as e: 
        line_info = f"строка {e.line_index + 1}" if e.line_index is not None else "N/A"
        col_info = f", столбец {e.column_index}" if e.column_index is not None else ""
        captured_output.write(f"\\nRUNTIME_SYNTAX_ERROR: {e.args[0]} ({line_info}{col_info})")
    except KumirRuntimeError as e:
        line_info = f"строка {e.line_index + 1}" if hasattr(e, 'line_index') and e.line_index is not None else "N/A"
        col_info = f", столбец {e.column_index}" if hasattr(e, 'column_index') and e.column_index is not None else ""
        captured_output.write(f"\\nRUNTIME_ERROR: {e.args[0]} ({line_info}{col_info})")
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        captured_output.write(f"\\nUNEXPECTED_EXECUTION_ERROR: {type(e).__name__}: {e}\\n{tb_str}")
    finally:
        sys.stdout = original_stdout

    final_output = captured_output.getvalue()
    logger.debug(f"interpret_kumir returning output:\\n{final_output}") # Лог возвращаемого значения
    return final_output

# Пример использования (можно раскомментировать для быстрой проверки)
# if __name__ == '__main__':
#     test_code_simple = """
#     алг начало
#       вывод "Привет, мир!"
#     кон
#     """
#     print(f"--- Test Simple ---\\nOutput:\\n{interpret_kumir(test_code_simple)}\\n--------------------")

#     test_code_input = """
#     алг начало
#       цел а
#       ввод а
#       вывод "Вы ввели: ", а * 2
#     кон
#     """
#     print(f"--- Test Input ---\\nOutput:\\n{interpret_kumir(test_code_input, input_data='123')}\\n--------------------")
    
#     test_code_error_syntax = """
#     алг начало
#       вывод "Привет, мир!
#     кон
#     """
#     print(f"--- Test Syntax Error ---\\nOutput:\\n{interpret_kumir(test_code_error_syntax)}\\n--------------------")

#     test_code_error_runtime = """
#     алг начало
#       цел а
#       а := 1 / 0
#       вывод а
#     кон
#     """
#     # Ожидаем, что KumirRuntimeError (или специфическая ошибка деления на ноль) будет поймана.
#     # В Kumir'е деление целого на ноль - это ошибка времени выполнения.
#     print(f"--- Test Runtime Error ---\\nOutput:\\n{interpret_kumir(test_code_error_runtime)}\\n--------------------")