#!/usr/bin/env python3
"""
Debug script для проверки выполнения FOR цикла в task 18
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir
from io import StringIO

# Простой тест FOR цикла
code = """
алг test
нач
цел k, M, n
M := 5
n := 2**M
нц для k от M до 1 шаг -1
вывод n, " "
n := div(n,2)
кц
кон
"""

print("Debug test для FOR цикла")
print("Код:")
print(code)
print("\nРезультат:")

try:
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    old_stdin = sys.stdin
    sys.stdin = StringIO("")  # Пустой ввод
    
    result = interpret_kumir(code, "")  # Пустой input
    
    sys.stdout = old_stdout 
    sys.stdin = old_stdin
    
    print(f"'{result}'")
    
except Exception as e:
    sys.stdout = old_stdout
    sys.stdin = old_stdin
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
