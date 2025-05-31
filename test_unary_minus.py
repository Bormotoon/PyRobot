#!/usr/bin/env python3
# Простой тест для унарного минуса
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

def test_unary_minus():
    print("Test унарного минуса")
    
    code = """
алг test
нач
цел x
x := -5
вывод x
кон
"""
    
    print(f"Код:\n{code}")
    
    result = interpret_kumir(code)
    print(f"Результат: '{result}'")

if __name__ == "__main__":
    test_unary_minus()
