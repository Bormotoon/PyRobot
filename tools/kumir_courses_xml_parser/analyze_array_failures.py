#!/usr/bin/env python3
"""
Скрипт для анализа неудачных тестов массивов.
Находит проблемы в сгенерированном коде и предлагает решения.
"""

import os
import re
import subprocess
import json
from pathlib import Path


def analyze_file(file_path):
    """Анализ конкретного файла Python на предмет ошибок."""
    print(f"\n🔍 Анализ файла: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Поиск определения функции
        func_match = re.search(r'def (\w+)\((.*?)\):', content)
        if func_match:
            func_name = func_match.group(1)
            func_params = func_match.group(2).strip()
            print(f"   Функция: {func_name}({func_params})")
        
        # Поиск вызовов в тестах
        test_calls = re.findall(r'assert.*?(\w+)\((.*?)\)', content)
        if test_calls:
            print(f"   Тесты:")
            for call_func, call_params in test_calls:
                print(f"     {call_func}({call_params})")
        
        # Проверка на несоответствие параметров
        if func_match and test_calls:
            func_params_count = len([p for p in func_params.split(',') if p.strip()]) if func_params else 0
            for call_func, call_params in test_calls:
                call_params_count = len([p for p in call_params.split(',') if p.strip()]) if call_params else 0
                if call_func == func_name and func_params_count != call_params_count:
                    print(f"   ❌ ПРОБЛЕМА: Несоответствие параметров функции ({func_params_count}) и вызова ({call_params_count})")
        
        # Поиск других проблем
        if 'N' in content and 'A' not in func_params:
            print(f"   ⚠️  ПРОБЛЕМА: Используется N, но A отсутствует в параметрах")
            
        if 'range(N)' in content and 'N' not in func_params:
            print(f"   ⚠️  ПРОБЛЕМА: Используется range(N), но N отсутствует в параметрах")
            
    except Exception as e:
        print(f"   ❌ Ошибка при анализе: {e}")


def find_failed_tests():
    """Находит все неудачные тесты массивов."""
    solutions_dir = Path("kumir_python_solutions/python_solutions")
    
    if not solutions_dir.exists():
        print("❌ Папка kumir_python_solutions/python_solutions не найдена")
        return []
    
    failed_files = []
    
    # Запускаем тесты и ловим неудачные
    for py_file in solutions_dir.glob("*.py"):
        try:
            result = subprocess.run(['python', str(py_file)], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                failed_files.append(py_file)
        except subprocess.TimeoutExpired:
            failed_files.append(py_file)
        except Exception:
            failed_files.append(py_file)
    
    return failed_files


def categorize_failures(failed_files):
    """Категоризация ошибок по типам."""
    categories = {
        'signature_mismatch': [],
        'missing_params': [],
        'array_problems': [],
        'other': []
    }
    
    for file_path in failed_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Анализ типа проблемы
            if 'array_fill' in file_path.name or 'array_proc' in file_path.name:
                func_match = re.search(r'def (\w+)\((.*?)\):', content)
                test_calls = re.findall(r'assert.*?(\w+)\((.*?)\)', content)
                
                if func_match and test_calls:
                    func_params = func_match.group(2).strip()
                    func_params_count = len([p for p in func_params.split(',') if p.strip()]) if func_params else 0
                    
                    for call_func, call_params in test_calls:
                        call_params_count = len([p for p in call_params.split(',') if p.strip()]) if call_params else 0
                        if func_params_count != call_params_count:
                            categories['signature_mismatch'].append(file_path)
                            break
                    else:
                        if 'N' in content and 'N' not in func_params:
                            categories['missing_params'].append(file_path)
                        else:
                            categories['array_problems'].append(file_path)
                else:
                    categories['array_problems'].append(file_path)
            else:
                categories['other'].append(file_path)
                
        except Exception:
            categories['other'].append(file_path)
    
    return categories


def main():
    print("🔍 Анализ неудачных тестов массивов")
    print("=" * 50)
    
    # Находим неудачные тесты
    print("🕵️ Поиск неудачных тестов...")
    failed_files = find_failed_tests()
    
    if not failed_files:
        print("🎉 Все тесты прошли успешно!")
        return
    
    print(f"❌ Найдено {len(failed_files)} неудачных тестов")
    
    # Категоризация
    categories = categorize_failures(failed_files)
    
    print(f"\n📊 Категоризация проблем:")
    print(f"   Несоответствие сигнатур: {len(categories['signature_mismatch'])}")
    print(f"   Отсутствие параметров: {len(categories['missing_params'])}")
    print(f"   Проблемы с массивами: {len(categories['array_problems'])}")
    print(f"   Другие проблемы: {len(categories['other'])}")
    
    # Детальный анализ наиболее проблемных файлов
    print(f"\n🔍 Детальный анализ наиболее проблемных файлов:")
    
    # Сначала анализируем несоответствия сигнатур
    if categories['signature_mismatch']:
        print(f"\n🚨 Несоответствие сигнатур ({len(categories['signature_mismatch'])} файлов):")
        for file_path in categories['signature_mismatch'][:10]:  # Первые 10
            analyze_file(file_path)
    
    # Потом отсутствие параметров
    if categories['missing_params']:
        print(f"\n⚠️ Отсутствие параметров ({len(categories['missing_params'])} файлов):")
        for file_path in categories['missing_params'][:5]:  # Первые 5
            analyze_file(file_path)


if __name__ == '__main__':
    main()
