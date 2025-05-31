#!/usr/bin/env python3
"""
Отладочный скрипт для тестирования цикла downto в задаче 18
"""

import sys
import os

# Добавляем пути к модулям проекта
sys.path.insert(0, os.path.dirname(__file__))

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir
from io import StringIO

def test_downto_loop():
    """Тестируем цикл downto с детальной отладкой"""
    
    # Простая программа для теста
    program_text = """
алг Тест цикл downto
нач
цел n, k, M
M := 5
вывод "M = ", M
n := 2**M
вывод "n = ", n
вывод "Начинаем цикл от ", M, " до 1 шаг -1"
нц для k от M до 1 шаг -1
    вывод "k = ", k, ", n = ", n
    n := div(n,2)
кц
вывод "Цикл закончен"
кон
"""
    
    print("=== Тестируем цикл downto ===")
    print("Программа:")
    print(program_text)
    print("\n=== Выполнение ===")
    
    try:
        # Выполняем программу с помощью функции interpret_kumir
        output = interpret_kumir(program_text, "")
        
        print(f"Вывод программы:")
        print(output)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_downto_loop()
