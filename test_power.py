"""
Тест операции возведения в степень
"""
from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

# Тест операции 2**5
test_code = '''
алг тест_степень
нач
цел M, n
M := 5
n := 2**M
вывод n
кон
'''

print("Тестирую операцию 2**5...")
try:
    result = interpret_kumir(test_code, '')
    print(f"Результат: '{result}'")
    print(f"Ожидаем: 32")
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
