"""
Тест простого выполнения функции КуМира.
Проверяет, можем ли мы сначала собрать определения, а затем выполнить вызов функции.
"""
import sys
import os

# Добавляем корень проекта в PYTHONPATH
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from pyrobot.backend.kumir_interpreter.interpreter import KumirInterpreter

def test_simple_function_execution():
    """Тестирует выполнение простой функции КуМира."""
    
    # Простой код с функцией и её вызовом
    code = """алг цел сумма(арг цел x, арг цел y)
нач
  знач := x + y
кон

алг
нач
  вывод сумма(2, 3)
кон"""
    
    print("🧪 Тестирую выполнение простой функции...")
    print(f"📄 Код для выполнения:\n{code}")
    
    try:
        # Создаем интерпретатор и парсим код
        interpreter = KumirInterpreter()
        tree = interpreter.parse(code)
        
        # Первый проход - сбор определений
        print("🔍 Запускаю первый проход (сбор определений)...")
        interpreter.collect_definitions_only(tree)
        print("✅ Первый проход завершен!")
        
        # Второй проход - выполнение основного алгоритма
        print("🚀 Запускаю второй проход (выполнение)...")
        result = interpreter.interpret(tree)
        print(f"✅ Выполнение завершено! Результат: {result}")
        
        # Проверим, что функция зарегистрирована
        print(f"📝 Функция 'сумма' найдена: {interpreter.algorithm_manager.has_algorithm('сумма')}")
        if interpreter.algorithm_manager.has_algorithm('сумма'):
            algo_def = interpreter.algorithm_manager.get_algorithm('сумма')
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
