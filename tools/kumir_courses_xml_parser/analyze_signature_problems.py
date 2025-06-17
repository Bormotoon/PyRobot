#!/usr/bin/env python3
"""
Анализ проблем с сигнатурами функций
"""

import os
import re
from pathlib import Path

def analyze_signature_problems():
    """Анализирует проблемы с сигнатурами в сгенерированных файлах."""
    solutions_dir = Path("kumir_python_solutions/python_solutions")
    
    problems = []
    
    for py_file in solutions_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Найти определение функции
            func_match = re.search(r'def (\w+)\((.*?)\):', content)
            if not func_match:
                continue
                
            func_name = func_match.group(1)
            func_params = func_match.group(2).strip()
            func_params_list = [p.strip().split(':')[0].strip() for p in func_params.split(',') if p.strip()]
            
            # Найти все вызовы функции в тестах
            test_calls = re.findall(rf'{func_name}\((.*?)\)', content)
            
            # Найти оригинальную сигнатуру из комментария
            original_match = re.search(r'Original: (.+)', content)
            original = original_match.group(1) if original_match else ""
            
            # Найти вызовы в test_solution
            test_func_match = re.search(r'def test_solution.*?\n(.*?)(?=def|\Z)', content, re.DOTALL)
            if test_func_match:
                test_content = test_func_match.group(1)
                test_calls_in_test = re.findall(rf'{func_name}\((.*?)\)', test_content)
            else:
                test_calls_in_test = []
            
            # Анализируем проблемы
            problem_found = False
            problem_desc = []
            
            # Проверяем соответствие параметров и вызовов
            for call_params in test_calls_in_test:
                call_params_clean = call_params.strip()
                if call_params_clean:
                    call_params_list = [p.strip() for p in call_params_clean.split(',') if p.strip()]
                else:
                    call_params_list = []
                
                if len(func_params_list) != len(call_params_list):
                    problem_found = True
                    problem_desc.append(f"Сигнатура: {len(func_params_list)} параметров, вызов: {len(call_params_list)}")
            
            # Проверяем использование неопределённых переменных
            if 'A[' in content and 'A' not in func_params:
                problem_found = True
                problem_desc.append("Использует A[], но A нет в параметрах")
            
            if 'X' in content and 'X' not in func_params and 'x' not in func_params:
                problem_found = True
                problem_desc.append("Использует X, но X нет в параметрах")
            
            if 'N' in content and 'N' not in func_params and 'n' not in func_params:
                problem_found = True
                problem_desc.append("Использует N, но N нет в параметрах")
            
            if problem_found:
                problems.append({
                    'file': py_file.name,
                    'original': original,
                    'func_signature': f"{func_name}({func_params})",
                    'problems': problem_desc
                })
                
        except Exception as e:
            print(f"Ошибка анализа {py_file}: {e}")
    
    return problems

def main():
    print("🔍 Анализ проблем с сигнатурами функций")
    print("=" * 60)
    
    problems = analyze_signature_problems()
    
    if not problems:
        print("✅ Проблем с сигнатурами не найдено!")
        return
    
    print(f"❌ Найдено {len(problems)} файлов с проблемами:\n")
    
    # Группируем по типам проблем
    by_type = {}
    for problem in problems:
        for prob_desc in problem['problems']:
            if prob_desc not in by_type:
                by_type[prob_desc] = []
            by_type[prob_desc].append(problem)
    
    # Показываем статистику
    print("📊 Статистика проблем:")
    for prob_type, items in by_type.items():
        print(f"   {prob_type}: {len(items)} файлов")
    
    print(f"\n🔍 Детали проблем (первые 15):")
    for i, problem in enumerate(problems[:15]):
        print(f"\n{i+1}. {problem['file']}")
        print(f"   Оригинал: {problem['original']}")
        print(f"   Сигнатура: {problem['func_signature']}")
        for prob in problem['problems']:
            print(f"   ❌ {prob}")

if __name__ == '__main__':
    main()
