#!/usr/bin/env python3

"""
Отладочный скрипт для проверки операции возведения в степень ** в КуМире
"""

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

code = """
алг Тест степени
нач
цел n
n := 2**3
вывод n
кон
"""

print("=== Тест операции возведения в степень 2**3 ===")
result = interpret_kumir(code)
print(f"Результат: '{result}'")
print(f"Ожидается: '8'")
