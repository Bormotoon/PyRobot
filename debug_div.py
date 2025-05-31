#!/usr/bin/env python3
import sys
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.abspath('.'))

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

def main():
    print("Тестируем функцию div в файле 15-while.kum")
    
    try:
        # Читаем файл и запускаем интерпретатор
        file_path = 'tests/polyakov_kum/15-while.kum'
        test_input = '12345\n'
        
        print(f"Читаем файл: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"Код программы:\n{code}")
        print(f"Входные данные: {repr(test_input)}")
        
        result = interpret_kumir(code, test_input)
        print(f"Результат: {repr(result)}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
