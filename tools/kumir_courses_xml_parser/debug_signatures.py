#!/usr/bin/env python3
"""
Дебаг генерации сигнатур для array_fill задач
"""
import json
from kumir_pipeline import KumirToPythonPipeline

# Создаём экземпляр
pipeline = KumirToPythonPipeline('dummy.xml')

# Загружаем задачи из JSON
with open('kumir_python_solutions/tasks_data.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Проверяем первую array_fill задачу
for task in tasks:
    if 'array_fill' in task['task_name'].lower():
        print(f"🔍 Анализ задачи: {task['task_name']}")
        
        task_type = pipeline.detect_task_type(task)
        print(f"  task_type: {task_type}")
        
        # Эмулируем логику из generate_python_solution
        task_name = task.get('task_name', 'unknown_task')
        original = task.get('original', '')
        todo = task.get('todo', '')
        kumir_code = task.get('kumir_code', '')
        
        # Эмулируем detect_parameters
        params = []
        if 'цел N' in original or 'цел n' in original.lower():
            params.append('N')
        if 'рез целтаб A' in original or 'целтаб A' in original:
            params.append('A') 
        if 'арг цел X' in original or 'арг X' in original:
            params.append('X')
        
        print(f"  params: {params}")
        
        # Ключевые флаги
        is_function = 'функ ' in kumir_code or task_type in ['algorithm_binary_search', 'function']
        returns_value = ('нач' in kumir_code and 'знач:=' in kumir_code) or task_type in ['algorithm_binary_search', 'function']
        array_params = any('цел' in p or 'A' in p for p in [original])
        string_params = []
        has_X = 'X' in params
        
        print(f"  is_function: {is_function}")
        print(f"  returns_value: {returns_value}")
        print(f"  array_params: {array_params}")
        print(f"  has_X: {has_X}")
        
        # Симулируем логику выбора сигнатуры
        if is_function or returns_value:
            print("  -> Попадает в блок is_function or returns_value")
        elif task_type.startswith('algorithm_') or task_type.startswith('array_'):
            print("  -> Попадает в блок array_ алгоритмов")
        else:
            print("  -> Попадает в другой блок")
            
        print()
        break
