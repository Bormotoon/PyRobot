from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

# Пробуем простую функцию double
with open('test_simple_func.kum', 'r', encoding='utf-8') as f:
    code = f.read()

print("Тестируем простую функцию double:")
print(code)
print("\nРезультат:")
try:
    result = interpret_kumir(code)
    print('УСПЕХ:', result)
except Exception as e:
    print('ОШИБКА:', str(e))
    import traceback
    traceback.print_exc()
