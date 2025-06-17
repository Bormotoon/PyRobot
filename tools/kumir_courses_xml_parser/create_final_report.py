#!/usr/bin/env python3
import json
import os
from collections import defaultdict

def create_final_report():
    """Создает финальный отчет по результатам мегапарсера"""
    
    # Загружаем данные
    with open('kumir_python_solutions/tasks_data.json', 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    
    # Определяем курс по последнему обработанному файлу
    course_name = "Функции"  # это последний обработанный курс
    
    # Читаем отчет для определения успешных тестов
    successful_files = set()
    failed_files = set()
    
    with open('kumir_python_solutions/reports/pipeline_report.md', 'r', encoding='utf-8') as f:
        content = f.read()
        for line in content.split('\n'):
            if '✅' in line and '.py' in line:
                filename = line.split('`')[1] if '`' in line else ''
                if filename.endswith('.py'):
                    successful_files.add(filename)
            elif '❌' in line and '.py' in line:
                filename = line.split('`')[1] if '`' in line else ''
                if filename.endswith('.py'):
                    failed_files.add(filename)
    
    print("🏆 ФИНАЛЬНЫЙ ОТЧЕТ ПО МЕГАПАРСЕРУ")
    print("=" * 60)
    print(f"📚 Курс: {course_name}")
    print(f"📊 Всего задач в последнем курсе: {len(tasks)}")
    print(f"✅ Успешных тестов: {len(successful_files)}")
    print(f"❌ Неуспешных тестов: {len(failed_files)}")
    print(f"📈 Общий процент успеха: {len(successful_files)/(len(successful_files)+len(failed_files))*100:.1f}%")
    print()
    
    # Анализируем по типам задач в рамках одного курса
    stats_by_type = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
    
    for task in tasks:
        task_type = task.get('task_type', 'unknown')
        task_id = task['task_id']
        
        # Находим соответствующий файл
        found_file = None
        found_status = None
        
        # Ищем среди всех файлов
        for filename in successful_files:
            if task_id in filename:
                found_file = filename
                found_status = 'success'
                break
        
        if not found_file:
            for filename in failed_files:
                if task_id in filename:
                    found_file = filename
                    found_status = 'failed'
                    break
        
        stats_by_type[task_type]['total'] += 1
        if found_status == 'success':
            stats_by_type[task_type]['success'] += 1
        else:
            stats_by_type[task_type]['failed'] += 1
    
    print("📋 Статистика по типам задач:")
    for task_type, stats in sorted(stats_by_type.items()):
        total = stats['total']
        success = stats['success']
        success_rate = success / total * 100 if total > 0 else 0
        
        status = "🟢" if success_rate >= 90 else "🟡" if success_rate >= 70 else "🔴"
        print(f"   {status} {task_type:20} | {success:3}/{total:3} ({success_rate:5.1f}%)")
    
    print()
    
    # Анализируем проблемные файлы
    print("🚨 Основные проблемы:")
    
    # Сгруппируем неуспешные файлы по паттернам
    problem_patterns = defaultdict(list)
    
    for filename in failed_files:
        if '_task_' in filename:
            problem_patterns['Базовые задачи (task)'].append(filename)
        elif 'sum_array' in filename:
            problem_patterns['Суммирование массивов'].append(filename)
        elif 'count_elements' in filename:
            problem_patterns['Подсчет элементов'].append(filename)
        elif 'average' in filename:
            problem_patterns['Среднее арифметическое'].append(filename)
        elif 'sort_algorithm' in filename:
            problem_patterns['Алгоритмы сортировки'].append(filename)
        else:
            problem_patterns['Прочие'].append(filename)
    
    for pattern, files in problem_patterns.items():
        if len(files) > 0:
            print(f"   • {pattern}: {len(files)} проблем")
            if len(files) <= 5:
                for f in files:
                    print(f"     - {f}")
            else:
                for f in files[:3]:
                    print(f"     - {f}")
                print(f"     ... и еще {len(files) - 3}")
    
    print()
    print("💡 Рекомендации:")
    print("   1. Проверить генерацию кода для базовых задач (task_XXX)")
    print("   2. Улучшить алгоритмы для работы с массивами")
    print("   3. Исправить определение типов задач в detect_task_type")
    print("   4. Протестировать каждый курс отдельно для точной диагностики")

if __name__ == "__main__":
    create_final_report()
