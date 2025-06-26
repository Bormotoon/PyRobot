#!/usr/bin/env python3
"""
Скрипт для исправления типизации в автогенерированном файле KumirParser.py
для совместимости со strict mode Python.
"""

import re
import sys
from pathlib import Path

def fix_parser_types(file_path):
    """Исправляет типизацию в файле парсера ANTLR."""
    
    print(f"Исправляем типизацию в {file_path}")
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем типизацию ParserRuleContext параметров
    print("Исправляем parent:ParserRuleContext=None -> parent:Optional[ParserRuleContext]=None")
    content = re.sub(
        r'parent:ParserRuleContext=None',
        r'parent:Optional[ParserRuleContext]=None',
        content
    )
    
    # Исправляем типизацию int параметров с именем i
    print("Исправляем i:int=None -> i:Optional[int]=None")
    content = re.sub(
        r'\bi:int=None\b',
        r'i:Optional[int]=None',
        content
    )
    
    # Сохраняем файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Файл {file_path} успешно исправлен!")

def main():
    """Главная функция."""
    parser_file = Path("pyrobot/backend/kumir_interpreter/generated/KumirParser.py")
    
    if not parser_file.exists():
        print(f"Файл {parser_file} не найден!")
        sys.exit(1)
    
    fix_parser_types(parser_file)
    print("Исправление типизации завершено!")

if __name__ == "__main__":
    main()
