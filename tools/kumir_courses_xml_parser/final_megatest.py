#!/usr/bin/env python3
"""
Финальный мегатест всех курсов Полякова для получения итогового отчета
"""
import os
import subprocess
from datetime import datetime

def run_clean_megatest():
    """Запускает чистый мегатест на всех курсах"""
    
    print("🧹 ФИНАЛЬНЫЙ МЕГАТЕСТ ВСЕХ КУРСОВ")
    print("=" * 60)
    print(f"🕒 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Очищаем результаты
    print("1. Очистка старых результатов...")
    result = subprocess.run([
        'rm', '-rf', 
        'kumir_python_solutions/python_solutions/*',
        'kumir_python_solutions/reports/*',
        'kumir_python_solutions/tasks_data.json'
    ], shell=True, capture_output=True, text=True)
    print("   ✅ Очищено")
    
    # Список курсов
    courses = [
        ('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_Функции.work.xml', 'Функции'),
        ('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_Массивы.work.xml', 'Массивы'),
        ('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_Водолей.work.xml', 'Водолей'),
        ('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_Строки.work.xml', 'Строки'),
        ('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_C2.work.xml', 'C2'),
        ('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_ОГЭ.work.xml', 'ОГЭ'),
        ('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_Robot.work.xml', 'Robot'),
    ]
    
    results = {}
    
    # Тестируем каждый курс
    for course_path, course_name in courses:
        print(f"2. Тестирование курса '{course_name}'...")
        
        if not os.path.exists(course_path):
            print(f"   ⚠️  Файл не найден: {course_path}")
            continue
            
        # Запускаем pipeline
        result = subprocess.run([
            'python', 'kumir_pipeline.py', course_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Извлекаем результат из вывода
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if '📊 Результаты:' in line:
                    # Формат: "📊 Результаты: 87/87 (100.0%)"
                    parts = line.split('📊 Результаты:')[1].strip()
                    success_part = parts.split('(')[0].strip()  # "87/87"
                    percent_part = parts.split('(')[1].split(')')[0]  # "100.0%"
                    
                    success, total = success_part.split('/')
                    results[course_name] = {
                        'success': int(success),
                        'total': int(total),
                        'percent': percent_part
                    }
                    break
            
            status = "✅" if course_name in results else "❌"
            print(f"   {status} {course_name}: {results.get(course_name, {}).get('percent', 'FAILED')}")
        else:
            print(f"   ❌ {course_name}: ERROR")
            print(f"      Ошибка: {result.stderr[:200]}...")
    
    print()
    print("🏆 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    
    total_success = 0
    total_tasks = 0
    
    for course_name, stats in results.items():
        success_rate = float(stats['percent'].replace('%', ''))
        status = "🟢" if success_rate >= 95 else "🟡" if success_rate >= 85 else "🔴"
        
        print(f"{status} {course_name:12} | {stats['success']:3}/{stats['total']:3} ({stats['percent']:6})")
        total_success += stats['success']
        total_tasks += stats['total']
    
    if total_tasks > 0:
        overall_percent = total_success / total_tasks * 100
        print(f"")
        print(f"🎯 ОБЩИЙ ИТОГ:   | {total_success:3}/{total_tasks:3} ({overall_percent:5.1f}%)")
    
    print()
    print("📝 Финальный отчет сохранен в kumir_python_solutions/reports/")
    print("🎉 Мегатест завершен!")

if __name__ == "__main__":
    run_clean_megatest()
