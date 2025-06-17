#!/usr/bin/env python3
"""
Быстрый дебаг script для проверки detect_task_type
"""
import json
from kumir_pipeline import KumirToPythonPipeline

# Создаём экземпляр
pipeline = KumirToPythonPipeline('dummy.xml')

# Загружаем задачи из JSON
with open('kumir_python_solutions/tasks_data.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Проверяем первые несколько array_fill задач
print("🔍 Проверка типов задач:")
for task in tasks[:10]:
    task_type = pipeline.detect_task_type(task)
    print(f"  {task['task_name']}: {task_type}")
    if 'array_fill' in task['task_name'].lower():
        print(f"    Original: {task.get('original', 'N/A')}")
        print(f"    Params: {pipeline.extract_parameters(task.get('original', ''))}")
        print()
