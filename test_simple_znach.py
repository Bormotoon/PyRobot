#!/usr/bin/env python3
"""
Простой тест для отладки проблемы с 'знач'.
"""

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

def test_simple_znach():
    """Простейший тест функции со 'знач'"""
    
    # Сначала тест без 'знач' - для проверки, что функция работает
    kumir_code1 = """
алг цел простая_функция
нач
    вывод "В функции"
    знач := 99
кон

алг главный
нач
    цел результат
    результат := простая_функция
    вывод "Результат:"
    вывод результат
кон
"""
    
    print("=== Тест 1: Функция с 'знач := 99' ===")
    print("Код:")
    print(kumir_code1)
    print("\nВыполнение:")
    
    try:
        result = interpret_kumir(kumir_code1)
        print(f"Результат: {result!r}")
    except Exception as e:
        print(f"Исключение: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_znach()
