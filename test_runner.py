#!/usr/bin/env python3
"""
Простой скрипт для тестирования интерпретатора КуМир
"""
import sys
import os

# Добавляем корневую папку проекта в путь
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

if __name__ == "__main__":    if len(sys.argv) != 2:
        print("Использование: python test_runner.py <файл.kum>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        output = interpret_kumir(code)
        print(output)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
