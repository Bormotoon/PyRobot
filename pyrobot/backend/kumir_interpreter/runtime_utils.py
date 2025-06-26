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
from .kumir_exceptions import KumirSyntaxError, KumirInputRequiredError, KumirRuntimeError, ExitSignal

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
    # DEBUG: записываем в файл для отладки
    with open("debug_interpret.log", "w", encoding="utf-8") as f:
        f.write(f"interpret_kumir CALLED! Code first 200 chars:\n{code[:200]!r}\n")
    
    logger.debug(f"interpret_kumir called with code:\\n{code}") # Лог входного кода
    
    # Создаем лексер и парсер
    input_stream_antl = InputStream(code)
    lexer = KumirLexer(input_stream_antl)
    lexer.removeErrorListeners()
    error_listener = DiagnosticErrorListener()
    lexer.addErrorListener(error_listener)

    token_stream = CommonTokenStream(lexer)
    parser = KumirParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    # Парсим код
    tree = None
    try:
        with open("debug_interpret.log", "a", encoding="utf-8") as f:
            f.write("About to parse code with parser.program()\n")
        tree = parser.program()
        with open("debug_interpret.log", "a", encoding="utf-8") as f:
            f.write(f"Parsing successful! Tree type: {type(tree)}\n")
            f.write(f"Tree text first 100 chars: {tree.getText()[:100]}\n")
    except KumirSyntaxError as e:
        line_info = f"строка {e.line_index + 1}" if hasattr(e, 'line_index') and e.line_index is not None else "N/A"
        col_info = f", столбец {e.column_index}" if hasattr(e, 'column_index') and e.column_index is not None else ""
        return f"Ошибка в коде: {e.args[0]} ({line_info}{col_info})"
    except Exception as e:
        error_info = f"Внутренняя ошибка парсера: {type(e).__name__}: {e}"
        with open("debug_interpret.log", "a", encoding="utf-8") as f:
            f.write(f"PARSING ERROR: {error_info}\n")
        return error_info

    # Настраиваем захват вывода
    original_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output    # Настраиваем входные данные
    input_buffer = StringIO(input_data if input_data else "")
    program_lines_list = code.splitlines()

    def input_fn():
        line = input_buffer.readline()
        result = line.rstrip('\r\n')
        return result
    
    def output_fn(text: str):
        logger.debug(f"output_fn called with text: '{text}'") # Лог вызова output_fn
        captured_output.write(text)
        with open("debug_interpret.log", "a", encoding="utf-8") as f:
            f.write(f"output_fn called with: {text!r}\n")
        
    def error_fn(text: str):
        sys.stderr.write(text)

    # Создаем visitor
    visitor = KumirInterpreterVisitor(
        input_stream=input_fn,
        output_stream=output_fn, 
        error_stream=error_fn,
        program_lines=program_lines_list
    )
    
    # DEBUG: проверяем что visitor создался
    with open("debug_interpret.log", "a", encoding="utf-8") as f:
        f.write(f"Visitor created successfully. Type: {type(visitor)}\n")
        f.write(f"About to call visitor.visitProgram(tree)\n")
        
    # Выполняем программу
    try:
        visitor.visitProgram(tree)
        with open("debug_interpret.log", "a", encoding="utf-8") as debug_f:
            debug_f.write(f"visitor.visitProgram(tree) completed successfully\n")
            
        # После сбора определений алгоритмов, нужно найти и запустить главный алгоритм
        # В КуМире обычно есть один алгоритм без параметров, который запускается автоматически
        with open("debug_interpret.log", "a", encoding="utf-8") as debug_f:
            debug_f.write(f"Available procedures: {list(visitor.procedure_manager.procedures.keys())}\n")        
        # Ищем алгоритм для запуска
        # Может быть "главный" или единственный алгоритм
        algorithm_to_run = None
        
        if visitor.procedure_manager.procedures:
            # Сначала ищем алгоритм с именем "главный"
            if "главный" in visitor.procedure_manager.procedures:
                algorithm_to_run = "главный"
            else:
                # Если нет "главного", берем первую ПРОЦЕДУРУ (не функцию)
                for alg_name_lower, alg_data in visitor.procedure_manager.procedures.items():
                    # Процедура - это алгоритм без возвращаемого значения (is_function=False)
                    if not alg_data.get('is_function', False):
                        algorithm_to_run = alg_name_lower
                        break
        
        if algorithm_to_run:
            with open("debug_interpret.log", "a", encoding="utf-8") as debug_f:
                debug_f.write(f"Executing algorithm: {algorithm_to_run}\n")
            visitor.execute_algorithm_node(algorithm_to_run)
            with open("debug_interpret.log", "a", encoding="utf-8") as debug_f:
                debug_f.write(f"Algorithm {algorithm_to_run} executed successfully\n")
        else:
            with open("debug_interpret.log", "a", encoding="utf-8") as debug_f:
                debug_f.write(f"No algorithms found to execute\n")
    except KumirInputRequiredError:
        pass
    except ExitSignal:
        # ExitSignal - это нормальное завершение программы или процедуры с помощью "выход все"
        # Для главной программы просто завершаем без ошибки
        pass
    except KumirSyntaxError as e:
        line_info = f"строка {e.line_index + 1}" if hasattr(e, 'line_index') and e.line_index is not None else "N/A"
        col_info = f", столбец {e.column_index}" if hasattr(e, 'column_index') and e.column_index is not None else ""
        captured_output.write(f"\\nОшибка в коде: {e.args[0]} ({line_info}{col_info})")
    except KumirRuntimeError as e:
        line_info = f"строка {e.line_index + 1}" if hasattr(e, 'line_index') and e.line_index is not None else "N/A"
        col_info = f", столбец {e.column_index}" if hasattr(e, 'column_index') and e.column_index is not None else ""
        captured_output.write(f"\\nОшибка выполнения: {e.args[0]} ({line_info}{col_info})")
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        captured_output.write(f"\\nВнутренняя ошибка интерпретатора: {type(e).__name__}: {e}")
        with open("debug_interpret.log", "a", encoding="utf-8") as debug_f:
            debug_f.write(f"EXCEPTION in visitor.visitProgram: {type(e).__name__}: {e}\n{tb_str}\n")
    finally:
        sys.stdout = original_stdout    # Получаем результат
    final_output = captured_output.getvalue()
    
    # Добавляем перевод строки в конец, если его нет (как в старом интерпретаторе)
    if final_output and not final_output.endswith('\n'):
        final_output += '\n'
        logger.debug("Added final newline to output") # Лог добавления перевода строки
    
    logger.debug(f"interpret_kumir returning output:\\n{final_output}") # Лог возвращаемого значения
    
    # DEBUG: записываем в файл для отладки  
    with open("debug_interpret.log", "a", encoding="utf-8") as f:
        f.write(f"Final output: {final_output!r}\n")
        
    return final_output

def run_kumir_file(file_path: str, input_data: Optional[str] = None) -> str:
    """
    Загружает и выполняет файл КуМира.
    Args:
        file_path (str): Путь к файлу с кодом КуМира
        input_data (Optional[str]): Входные данные для программы
    Returns:
        str: Результат выполнения программы
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        return interpret_kumir(code, input_data)
    except FileNotFoundError:
        return f"ОШИБКА: Файл '{file_path}' не найден"
    except UnicodeDecodeError as e:
        return f"ОШИБКА: Не удалось прочитать файл '{file_path}': {e}"

# Пример использования (можно раскомментировать для быстрой проверки)
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Запуск файла из командной строки
        file_path = sys.argv[1]
        input_data = None
        if len(sys.argv) > 2:
            input_data = sys.argv[2]
        
        print(f"Запуск файла: {file_path}")
        result = run_kumir_file(file_path, input_data)
        print("=== РЕЗУЛЬТАТ ===")
        print(result)
        print("=== КОНЕЦ ===")
    else:
        # Тестовые примеры
        test_code_simple = """
        алг начало
          вывод "Привет, мир!"
        кон
        """
        print(f"--- Test Simple ---\\nOutput:\\n{interpret_kumir(test_code_simple)}\\n--------------------")

        test_code_input = """
        алг начало
          цел а
          ввод а
          вывод "Вы ввели: ", а * 2
        кон
        """
        print(f"--- Test Input ---\\nOutput:\\n{interpret_kumir(test_code_input, input_data='123')}\\n--------------------")
        
        test_code_error_syntax = """
        алг начало
          вывод "Привет, мир!
        кон
        """
        print(f"--- Test Syntax Error ---\\nOutput:\\n{interpret_kumir(test_code_error_syntax)}\\n--------------------")

        test_code_error_runtime = """
        алг начало
          цел а
          а := 1 / 0
          вывод а
        кон
        """
        # Ожидаем, что KumirRuntimeError (или специфическая ошибка деления на ноль) будет поймана.
        # В Kumir'е деление целого на ноль - это ошибка времени выполнения.
        print(f"--- Test Runtime Error ---\\nOutput:\\n{interpret_kumir(test_code_error_runtime)}\\n--------------------")
