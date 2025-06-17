#!/usr/bin/env python3
"""
Прямая проверка генерации для array_fill задач
"""
import json
from kumir_pipeline import KumirToPythonPipeline

# Создаём экземпляр
pipeline = KumirToPythonPipeline('dummy.xml')

# Загружаем задачи из JSON
with open('kumir_python_solutions/tasks_data.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Проверяем первую задачу
task = tasks[0]  # "массив заполнить нулями"
print(f"🔍 Генерация для задачи: {task['task_name']}")
print(f"  task_id: {task['task_id']}")
print(f"  task_init: {task['task_init']}")
print(f"  task_todo: {task['task_todo']}")
print(f"  kumir_code: {task['kumir_code']}")

# Генерируем Python код
python_code = pipeline.generate_python_solution(task)
print(f"\n📝 Сгенерированный код:")
print("=" * 50)
print(python_code)
print("=" * 50)
