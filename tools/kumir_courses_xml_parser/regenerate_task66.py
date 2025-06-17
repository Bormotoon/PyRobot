#!/usr/bin/env python3
import json
from kumir_pipeline import KumirToPythonPipeline

# Загружаем данные
with open('kumir_python_solutions/tasks_data.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Создаем pipeline для курса массивов
pipeline = KumirToPythonPipeline('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_Массивы.work.xml')

# Найдем задачу 66
task66 = None
for task in tasks:
    if task['task_id'] == '66':
        task66 = task
        break

if task66:
    print('🔧 ПЕРЕСОЗДАНИЕ ЗАДАЧИ 66')
    print('=' * 50)
    
    # Отладим каждый шаг
    task_type = pipeline.detect_task_type(task66)
    print(f'1. Detected task_type: {task_type}')
    
    short_name = pipeline.clean_task_name_for_filename(task66['task_name'], task66['task_id'], task_type)
    print(f'2. Short name: {short_name}')
    
    # Генерируем код
    print('3. Генерируем Python код...')
    python_code = pipeline.generate_python_solution(task66)
    
    print('\n4. Первые строки кода:')
    for i, line in enumerate(python_code.split('\n')[:10]):
        print(f'   {i+1:2}: {line}')
    
    # Сохраняем файл
    filename = f"{task66['task_id']}_{short_name}.py"
    filepath = f"kumir_python_solutions/python_solutions/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    print(f'\n✅ Файл {filename} создан')
    
    # Тестируем
    print('5. Тестируем...')
    try:
        success, output = pipeline.test_python_file(filepath)
        print(f'   Результат: {"✅ SUCCESS" if success else "❌ FAILED"}')
        if output:
            print(f'   Вывод: {output[:200]}...' if len(output) > 200 else f'   Вывод: {output}')
    except Exception as e:
        print(f'   ❌ Ошибка тестирования: {e}')
        
else:
    print('❌ Task 66 not found!')
