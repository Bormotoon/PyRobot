"""
Тест простого выполнения функции КуМира.
Проверяет, можем ли мы сначала собрать определения, а затем выполнить вызов функции.
"""
import sys
import os

# Добавляем корень проекта в PYTHONPATH
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir
from pyrobot.backend.kumir_interpreter.interpreter_components.main_visitor import KumirInterpreterVisitor
from pyrobot.backend.kumir_interpreter.generated.KumirLexer import KumirLexer
from pyrobot.backend.kumir_interpreter.generated.KumirParser import KumirParser
from antlr4 import InputStream, CommonTokenStream

def test_simple_function_execution():
    """Тестирует выполнение простой функции КуМира."""
      # Простой код с функцией и её вызовом
    code = """алг цел сумма(арг цел x, арг цел y)
нач
  знач := x + y
кон

алг главный
нач
  вывод сумма(2, 3)
кон"""
    
    print("🧪 Тестирую выполнение простой функции...")
    print(f"📄 Код для выполнения:\n{code}")
    
    try:
        # Используем runtime_utils для полного выполнения
        print("🚀 Запускаю интерпретацию...")
        result = interpret_kumir(code)
        print(f"✅ Выполнение завершено! Результат: {result}")
        
        # Дополнительно проверим с прямым созданием visitor для отладки
        print("\n🔍 Дополнительная проверка с visitor...")
        
        # Создаем парсер
        input_stream = InputStream(code)
        lexer = KumirLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = KumirParser(token_stream)
        tree = parser.program()
        
        # Создаем visitor
        visitor = KumirInterpreterVisitor()
        
        # Первый проход - сбор определений
        print("� Собираю определения...")
        visitor.collect_definitions_only(tree)
        print("✅ Определения собраны!")
        
        # Проверим, что функция зарегистрирована
        print(f"📝 Функция 'сумма' найдена: {visitor.algorithm_manager.has_algorithm('сумма')}")
        if visitor.algorithm_manager.has_algorithm('сумма'):
            algo_def = visitor.algorithm_manager.get_algorithm('сумма')
            print(f"   Параметры: {len(algo_def.parameters)}")
            print(f"   Тип возврата: {algo_def.return_type}")
            for param in algo_def.parameters:
                print(f"   * {param.name}: {param.param_type} ({param.mode})")
                
    except Exception as e:
        print(f"❌ Ошибка при выполнении: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("🎉 Тест завершен!")
    return True

if __name__ == "__main__":
    test_simple_function_execution()
