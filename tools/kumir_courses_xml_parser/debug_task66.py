#!/usr/bin/env python3

import json
import re

# Загружаем данные для задачи 66
data = json.load(open('kumir_python_solutions/tasks_data.json'))
task66 = next((t for t in data if str(t.get('task_id', '')) == '66'), None)

if not task66:
    print("Задача 66 не найдена")
    exit()

task_name = task66['task_name']
task_init = task66['task_init']
task_todo = task66['task_todo']
kumir_code = task66['kumir_code']

print(f"Task name: {task_name}")
print(f"Task init: {task_init}")
print(f"Task todo: {task_todo}")
print()

# Проверяем детекцию типа
has_array = any(keyword in task_name for keyword in ['аргрез', 'целтаб', 'вещтаб', 'лоттаб', 'массив'])
has_argresult_array = any(keyword in task_name for keyword in ['аргрез целтаб', 'аргрез вещтаб', 'аргрез лоттаб'])

print(f"has_array: {has_array}")
print(f"has_argresult_array: {has_argresult_array}")

# Проверяем условие для функций
is_function = any(prefix in task_name for prefix in ['цел ', 'вещ ', 'лог ', 'лит ']) and ('арг' in task_name or '(' in task_name)
print(f"is_function: {is_function}")

# Проверяем условие для func_count_elements
has_skolko = 'скольк' in task_todo.lower() or 'скольк' in task_name.lower()
print(f"'скольк' in task_todo.lower() or task_name.lower(): {has_skolko}")
print(f"Should be func_count_elements: {has_skolko and has_array}")

print()
print("Эмуляция detect_task_type:")

if has_argresult_array:
    print("-> has_argresult_array: array_procedure")
elif is_function:
    if has_skolko and has_array:
        print("-> func_count_elements")
    else:
        print("-> general function")
else:
    print("-> other")
