#!/usr/bin/env python3
"""
Тест для проверки правильной маршрутизации вызовов процедур.
Этот тест демонстрирует проблему и её исправление.
"""

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

def test_procedure_routing_problem():
    """Демонстрирует проблему с маршрутизацией процедур"""
    print("🔍 Тестируем проблему с маршрутизацией процедур...")
    
    code = """
алг удвоить(аргрез цел число)
нач
  число := число * 2
кон

алг главный
нач
  цел x
  x := 10
  удвоить(x)
  вывод x
кон
"""
    
    print("📄 Код для выполнения:")
    print(code)
    print("\n🚀 Запускаю интерпретацию...")
    
    try:
        result = interpret_kumir(code)
        print(f"✅ Выполнение завершено! Результат: {result.strip()}")
        if "20" in result:
            print("🎉 Процедура сработала правильно!")
        else:
            print("❌ Процедура не изменила значение переменной")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("📝 Это демонстрирует проблему с маршрутизацией:")
        print("   - Вызов процедуры 'удвоить(x)' обрабатывается как выражение")
        print("   - Expression evaluator правильно определяет, что это процедура") 
        print("   - Но отклоняет её с ошибкой 'procedures cannot be used in expressions'")
        print("   - Нужно исправить visitAssignmentStatement для правильной маршрутизации")

def test_function_vs_procedure():
    """Тестирует различие между функциями и процедурами"""
    print("\n🔍 Тестируем различие между функциями и процедурами...")
    
    code = """
алг цел удвоить_функция(арг цел число)
нач
  знач := число * 2
кон

алг удвоить_процедура(аргрез цел число)
нач
  число := число * 2
кон

алг главный
нач
  цел x, y
  x := 10
  y := 10
  
  // Функция должна работать в выражениях
  y := удвоить_функция(x)
  вывод y
  
  // Процедура должна работать как команда
  удвоить_процедура(x)
  вывод x
кон
"""
    
    print("📄 Код для выполнения:")
    print(code)
    print("\n🚀 Запускаю интерпретацию...")
    
    try:
        result = interpret_kumir(code)
        print(f"✅ Выполнение завершено! Результат: {result.strip()}")
        lines = result.strip().split('\n')
        if len(lines) >= 2 and lines[0] == "20" and lines[1] == "20":
            print("🎉 И функция, и процедура работают правильно!")
        else:
            print("❌ Что-то работает неправильно")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_procedure_routing_problem()
    test_function_vs_procedure()
