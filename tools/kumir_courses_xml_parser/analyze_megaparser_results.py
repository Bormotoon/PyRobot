#!/usr/bin/env python3
import json
import os
from collections import defaultdict

def analyze_results():
    """Анализ результатов мегапарсера по типам задач"""
    
    # Загружаем данные
    with open('kumir_python_solutions/tasks_data.json', 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    
    # Читаем отчет для определения успешных тестов
    successful_files = set()
    failed_files = set()
    
    with open('kumir_python_solutions/reports/pipeline_report.md', 'r', encoding='utf-8') as f:
        content = f.read()
        for line in content.split('\n'):
            if '✅' in line and '.py' in line:
                # Извлекаем имя файла
                filename = line.split('`')[1] if '`' in line else ''
                if filename.endswith('.py'):
                    successful_files.add(filename)
            elif '❌' in line and '.py' in line:
                filename = line.split('`')[1] if '`' in line else ''
                if filename.endswith('.py'):
                    failed_files.add(filename)
    
    # Анализируем по типам
    stats_by_type = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
    
    for task in tasks:
        task_type = task.get('task_type', 'unknown')
        task_id = task['task_id']
        
        # Определяем имя файла (может быть несколько вариантов)
        clean_name = task.get('clean_name', f"task_{task_id}")
        possible_filenames = [
            f"{task_id}_{clean_name}.py",
            f"{clean_name}.py",
            f"{task_id}_task_{task_id}.py"
        ]
        
        stats_by_type[task_type]['total'] += 1
        
        # Проверяем какой файл существует и прошел ли он тест
        file_found = False
        for filename in possible_filenames:
            if filename in successful_files:
                stats_by_type[task_type]['success'] += 1
                file_found = True
                break
            elif filename in failed_files:
                stats_by_type[task_type]['failed'] += 1
                file_found = True
                break
        
        if not file_found:
            stats_by_type[task_type]['failed'] += 1
    
    # Выводим статистику
    print("🔍 АНАЛИЗ РЕЗУЛЬТАТОВ МЕГАПАРСЕРА")
    print("=" * 60)
    
    total_tasks = len(tasks)
    total_success = len(successful_files)
    total_failed = len(failed_files)
    
    print(f"📊 Общая статистика:")
    print(f"   Всего задач: {total_tasks}")
    print(f"   Успешных: {total_success} ({total_success/total_tasks*100:.1f}%)")
    print(f"   Неуспешных: {total_failed} ({total_failed/total_tasks*100:.1f}%)")
    print()
    
    print("📋 Статистика по типам задач:")
    for task_type, stats in sorted(stats_by_type.items()):
        total = stats['total']
        success = stats['success']
        success_rate = success / total * 100 if total > 0 else 0
        
        status = "🟢" if success_rate >= 90 else "🟡" if success_rate >= 70 else "🔴"
        print(f"   {status} {task_type:20} | {success:3}/{total:3} ({success_rate:5.1f}%)")
    
    print()
    
    # Находим проблемные задачи
    print("🚨 Проблемные задачи:")
    problem_tasks = []
    for task in tasks:
        task_type = task.get('task_type', 'unknown')
        task_id = task['task_id']
        clean_name = task.get('clean_name', f"task_{task_id}")
        
        possible_filenames = [
            f"{task_id}_{clean_name}.py",
            f"{clean_name}.py", 
            f"{task_id}_task_{task_id}.py"
        ]
        
        failed = False
        for filename in possible_filenames:
            if filename in failed_files:
                failed = True
                problem_tasks.append({
                    'task_id': task_id,
                    'task_type': task_type,
                    'filename': filename,
                    'task_name': task.get('task_name', ''),
                })
                break
    
    # Группируем проблемные задачи по типам
    problems_by_type = defaultdict(list)
    for problem in problem_tasks:
        problems_by_type[problem['task_type']].append(problem)
    
    for task_type, problems in sorted(problems_by_type.items()):
        if len(problems) > 0:
            print(f"\n   {task_type} ({len(problems)} проблем):")
            for p in problems[:5]:  # Показываем первые 5
                print(f"     • {p['task_id']} ({p['filename']}) - {p['task_name'][:50]}...")
            if len(problems) > 5:
                print(f"     ... и еще {len(problems) - 5} задач")

if __name__ == "__main__":
    analyze_results()
