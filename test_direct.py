import sys
sys.path.append('.')

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

code = """алг цел Удвоить(арг цел x)
нач
    знач := x * 2
кон

алг ТестПараметры
нач
    цел результат
    результат := Удвоить(5)
    вывод результат, нс
кон"""

print("=== CODE ===")
print(code)
print("=== EXECUTING ===")

try:
    result = interpret_kumir(code, "")
    print("=== RESULT ===")
    print(result)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
