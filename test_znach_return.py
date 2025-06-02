#!/usr/bin/env python3
"""
Тест для проверки, возвращает ли функция правильное значение после установки 'знач'.
"""

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

def test_znach_return_value():
    """Тест, что функция возвращает правильное значение после установки 'знач'"""
    
    kumir_code = """
алг цел тест_знач
нач
    вывод "До установки знач"
    знач := 42
    вывод "После установки знач"
кон

алг главный
нач
    вывод "Результат функции:"
    вывод тест_знач
кон
"""
    
    print("=== Тест возвращаемого значения функции со 'знач' ===")
    print("Код:")
    print(kumir_code)
    print("\nВыполнение:")
    
    try:
        result = interpret_kumir(kumir_code)
        print(f"Полный результат: {result!r}")
        
        lines = result.strip().split('\n')
        print(f"Строки вывода: {lines}")
        
        # Анализируем результат
        has_before = any("До установки знач" in line for line in lines)
        has_after = any("После установки знач" in line for line in lines)
        has_42 = any("42" in line for line in lines)
        
        print(f"Найдено 'До установки знач': {has_before}")
        print(f"Найдено 'После установки знач': {has_after}")
        print(f"Найдено '42': {has_42}")
        
        if has_before and has_after and has_42:
            print("✅ Функция продолжила выполнение после установки 'знач' и вернула правильное значение!")
        elif has_before and not has_after:
            print("❌ Функция прервалась после установки 'знач' (нет 'После установки знач')")
        elif not has_42:
            print("❌ Функция не вернула правильное значение (нет '42')")
        else:
            print("❌ Неожиданное поведение")
            
    except Exception as e:
        print(f"Исключение: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_znach_return_value()
