#!/usr/bin/env python3
import json
from kumir_pipeline import KumirToPythonPipeline

# Загружаем данные
with open('kumir_python_solutions/tasks_data.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Создаем pipeline
pipeline = KumirToPythonPipeline('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work/Поляков_Массивы.work.xml')

# Найдем задачу 20
task20 = None
for task in tasks:
    if task['task_id'] == '20':
        task20 = task
        break

if task20:
    print('Task 20:')
    print('task_name:', repr(task20['task_name']))
    print('task_todo:', repr(task20['task_todo']))
    
    # Отладим detect_task_type
    task_type = pipeline.detect_task_type(task20)
    print(f'Detected task_type: {task_type}')
    
    # Отладим clean_task_name_for_filename
    short_name = pipeline.clean_task_name_for_filename(task20['task_name'], task20['task_id'], task_type)
    print(f'Short name: {short_name}')
else:
    print('Task 20 not found!')
