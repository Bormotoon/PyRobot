#!/usr/bin/env python3
# Простой тест без pytest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, 'c:/Users/Bormotoon/VSCodeProjects/PyRobot')

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir
from pyrobot.backend.kumir_interpreter.kumir_exceptions import KumirSyntaxError, KumirEvalError

def test_simple_kumir():
    """Простой тест интерпретатора КуМир"""
    kumir_code = '''алг
нач
  результат := __Решение__("тест")
  вывод результат, нс
кон

алг сим __Решение__(лит s)
нач
знач:= s[1]
кон'''
    
    print(f"Testing Kumir code: {kumir_code[:50]}...")
    
    try:
        output = interpret_kumir(kumir_code, None)
        print(f"✅ Test passed! Output: {output}")
        return True
    except KumirSyntaxError as e:
        print(f"❌ KumirSyntaxError: {e}")
        return False
    except KumirEvalError as e:
        print(f"❌ KumirEvalError: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting simple test...")
    success = test_simple_kumir()
    print(f"Test result: {'SUCCESS' if success else 'FAILURE'}")
