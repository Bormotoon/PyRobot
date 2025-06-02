#!/usr/bin/env python3
"""
Тест для проверки исправления проблемы с 'знач' assignment.
Функция должна продолжить выполнение после установки 'знач'.
"""

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

def test_znach_assignment_continues_execution():
    """Тест, что функция продолжает выполнение после 'знач := значение'"""
    
    # Код функции, которая устанавливает знач и продолжает выполнение
    kumir_code = """
алг цел тест_функция
нач
    знач := 42
    вывод "После установки знач"
кон

алг главный
нач
    вывод тест_функция
кон
"""
    
    print("Тестируем, что функция продолжает выполнение после установки 'знач'...")
    print("Код:")
    print(kumir_code)
    print("\nВыполнение:")
    
    try:
        result = interpret_kumir(kumir_code)
        
        print(f"Результат выполнения: {result!r}")
        
        # Проверяем, что вывод содержит и сообщение, и результат функции
        if "После установки знач" in result and "42" in result:
            print("✅ Функция продолжила выполнение после установки 'знач'!")
            return True
        else:
            print("❌ Функция не продолжила выполнение или не вернула правильное значение")
            print(f"Ожидали найти: 'После установки знач' и '42' в результате")
            return False
    except Exception as e:
        print(f"❌ Тест ПРОВАЛЕН - исключение: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_znach_assignment_continues_execution()
    exit(0 if success else 1)
