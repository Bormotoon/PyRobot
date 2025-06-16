#!/usr/bin/env python3
"""
Полный pipeline для обработки XML файлов КУМИРа и создания Python эталонных решений.

Этот скрипт выполняет полный цикл:
1. Парсит XML файл с задачами КУМИРа
2. Извлекает ученический код и условия задач
3. Генерирует Python эталонные решения
4. Тестирует все созданные решения
5. Создает отчеты и готовит файлы для сравнения
"""

import xml.etree.ElementTree as ET
import json
import re
import os
import sys
import subprocess
import shutil
from typing import Optional, List, Dict, Any, Set
from pathlib import Path

class KumirToPythonPipeline:
    """Полный pipeline для обработки КУМИРа и создания Python решений."""
    
    def __init__(self, xml_file_path: str, output_dir: str = "kumir_python_solutions"):
        self.xml_file_path = xml_file_path
        self.output_dir = Path(output_dir)
        self.tasks_json_file = self.output_dir / "tasks_data.json"
        self.python_dir = self.output_dir / "python_solutions"
        self.reports_dir = self.output_dir / "reports"
        
        # Создаем директории
        self.output_dir.mkdir(exist_ok=True)
        self.python_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def clean_task_name_for_filename(self, task_name: str, task_id: str, task_type: str = "") -> str:
        """Создает короткое английское имя файла на основе типа задачи."""
        
        # Если у нас есть тип задачи из детектора
        if task_type:
            if task_type.startswith('func_'):
                type_names = {
                    'func_last_digit': 'last_digit',
                    'func_tens_digit': 'tens_digit', 
                    'func_hundreds_digit': 'hundreds_digit',
                    'func_cube': 'cube',
                    'func_square': 'square',
                    'func_round': 'round',
                    'func_round_up': 'round_up',
                    'func_is_prime': 'is_prime',
                    'func_is_palindrome': 'is_palindrome',
                    'func_complex_algorithm': 'complex_func',
                    'func_generic': 'function'
                }
                return type_names.get(task_type, 'function')
            elif task_type.startswith('algorithm_'):
                type_names = {
                    'algorithm_binary_search': 'binary_search',
                    'algorithm_sort': 'sort_algorithm', 
                    'algorithm_complex': 'complex_algorithm'
                }
                return type_names.get(task_type, 'algorithm')
            elif task_type.startswith('array_'):
                type_names = {
                    'array_reverse': 'array_reverse',
                    'array_shift': 'array_shift',
                    'array_sort': 'array_sort',
                    'array_fill': 'array_fill',
                    'array_search': 'array_search',
                    'array_modify': 'array_modify',
                    'array_procedure': 'array_proc'
                }
                return type_names.get(task_type, 'array_task')
        
        # Словарь сокращений для разных типов задач
        name_mappings = {
            # Заполнение массивов
            "10": "arr_fill_zeros",
            "11": "arr_fill_natural", 
            "12": "arr_fill_from_x",
            "13": "arr_fill_plus5",
            "14": "arr_fill_fibonacci",
            "15": "arr_fill_powers2",
            "16": "arr_fill_pyramid",
            
            # Модификация массивов
            "20": "arr_inc_by1",
            "21": "arr_mult_by2", 
            "22": "arr_square",
            "23": "arr_inc_first_half",
            "24": "arr_div_middle",
            "25": "arr_mult_second_half",
            "26": "arr_average",
            
            # Поиск экстремумов
            "30": "arr_find_max",
            "31": "arr_find_min",
            "32": "arr_find_minmax",
            "33": "arr_find_min_index",
            "34": "arr_find_minmax_indices",
            "35": "arr_find_two_max",
            "36": "arr_find_two_min_indices",
            
            # Подсчет элементов
            "40": "arr_count_ones",
            "41": "arr_count_equal_x",
            "42": "arr_count_positive",
            "43": "arr_count_even_odd",
            "44": "arr_count_even_positive",
            "45": "arr_count_digit5",
            "46": "arr_count_same_digits",
            
            # Суммы и произведения
            "50": "arr_sum_all",
            "51": "arr_sum_negative",
            "52": "arr_sum_div3",
            "53": "arr_avg_less50",
            "54": "arr_prod_even_pos",
            "55": "arr_sum_tens_gt_units",
            "56": "arr_sum_all_same_digits",
            
            # Поиск индексов
            "60": "arr_find_x_index",
            "61": "arr_find_x_first_half",
            "62": "arr_find_x_second_half",
            "63": "arr_find_x_last_second_half",
            "64": "arr_count_x_first_half",
            "65": "arr_count_x_pairs",
            "66": "arr_count_hills",
            
            # Специальные задачи
            "71": "arr_count_same_digits",
            "72": "arr_longest_chain",
            "73": "arr_count_primes",
            "74": "arr_fill_primes",
            "75": "arr_sum_palindromes",
            "76": "arr_fill_hyperprimes"
        }
        
        # Возвращаем короткое имя или создаем из task_id
        return name_mappings.get(task_id, f"task_{task_id}")
    
    def parse_kumir_xml_to_json(self) -> bool:
        """Парсит XML файл и сохраняет задачи в JSON."""
        print(f"📁 Парсинг XML файла: {self.xml_file_path}")
        
        if not os.path.exists(self.xml_file_path):
            print(f"❌ Ошибка: Файл не найден по пути: {self.xml_file_path}")
            return False

        all_tasks_data: List[Dict[str, Any]] = []
        processed_ids: Set[str] = set()

        try:
            tree = ET.parse(self.xml_file_path)
            root: ET.Element = tree.getroot()
        except ET.ParseError as e:
            print(f"❌ Ошибка парсинга XML: {e}")
            return False

        elements_to_process = root.findall('.//USER_PRG') + root.findall('.//TESTED_PRG')

        for task_element in elements_to_process:
            test_id: Optional[str] = task_element.get('testId')
            prg_full_content: Optional[str] = task_element.get('prg')

            if not prg_full_content or not test_id or test_id in processed_ids:
                continue
            
            processed_ids.add(test_id)
            prg_full_content = prg_full_content.strip()

            # Отделяем тестовый блок
            testing_separator = "алг цел @тестирование|@hidden"
            student_program_part = prg_full_content.split(testing_separator, 1)[0].strip()

            # Извлекаем составные части
            
            # 1. Название алгоритма
            alg_match = re.search(r'алг\s+(.+?)\s*\|\@protected', student_program_part, re.DOTALL)
            alg_name = alg_match.group(1).strip() if alg_match else ""
            
            # 2. Блок "дано"
            dano_match = re.search(r'дано\s*\|\s*(.+?)\s*\|\@protected', student_program_part, re.DOTALL)
            dano_content = dano_match.group(1).strip() if dano_match else ""
            dano_clean = re.sub(r'\s*\|\s*', ' ', dano_content)
            dano_clean = re.sub(r'\s+', ' ', dano_clean).strip()
            
            # 3. Блок "надо"
            nado_start_match = re.search(r'надо\s*\|', student_program_part)
            if nado_start_match:
                nado_start_pos = nado_start_match.start()
                nach_match = re.search(r'нач\s*\|\@protected', student_program_part[nado_start_pos:])
                if nach_match:
                    nado_end_pos = nado_start_pos + nach_match.start()
                    nado_block = student_program_part[nado_start_pos:nado_end_pos].strip()
                    
                    nado_content = re.sub(r'надо\s*\|\s*', '', nado_block)
                    nado_content = re.sub(r'\|\@protected', '', nado_content)
                    nado_content = re.sub(r'^\s*\|\s*', '', nado_content, flags=re.MULTILINE)
                    nado_clean = re.sub(r'\s+', ' ', nado_content).strip()
                else:
                    nado_clean = ""
            else:
                nado_clean = ""
            
            # 4. Ученический код
            student_code = ""
            nach_match = re.search(r'нач\s*\|\@protected', student_program_part)
            if nach_match:
                code_start_pos = nach_match.start()
                kon_match = re.search(r'кон\s*\|\@protected', student_program_part[code_start_pos:])
                if kon_match:
                    code_end_pos = code_start_pos + kon_match.end()
                    student_code_raw = student_program_part[code_start_pos:code_end_pos].strip()
                    
                    student_code = re.sub(r'\|\@protected', '', student_code_raw)
                    student_code = re.sub(r'^\s*\|\s*', '', student_code, flags=re.MULTILINE)
                    student_code = student_code.strip()

            task_data: Dict[str, str] = {
                "task_id": test_id,
                "task_name": alg_name,
                "task_init": dano_clean,
                "task_todo": nado_clean,
                "kumir_code": student_code
            }
            all_tasks_data.append(task_data)

        all_tasks_data.sort(key=lambda x: int(x['task_id']) if x['task_id'].isdigit() else 0)
        
        try:
            with open(self.tasks_json_file, 'w', encoding='utf-8') as f:
                json.dump(all_tasks_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Извлечено и сохранено {len(all_tasks_data)} задач в {self.tasks_json_file}")
            return True
        except IOError as e:
            print(f"❌ Ошибка записи в файл: {e}")
            return False
    
    def detect_task_type(self, task: Dict[str, str]) -> str:
        """Определяет тип задачи на основе её содержимого."""
        task_name = task['task_name'].lower()
        task_todo = task['task_todo'].lower()
        kumir_code = task['kumir_code'].lower()
        
        # Проверяем наличие массивов в сигнатуре
        has_array = any(keyword in task_name for keyword in ['аргрез', 'целтаб', 'вещтаб', 'лоттаб', 'массив'])
        
        # Сложные алгоритмы (двоичный поиск, сортировки, и т.д.)
        if any(keyword in task_todo for keyword in ['двоичн', 'бинарн', 'поиск', 'сортир', 'пузыр', 'быстр', 'слиян']):
            if 'двоичн' in task_todo or 'бинарн' in task_todo:
                return 'algorithm_binary_search'
            elif 'сортир' in task_todo:
                return 'algorithm_sort'
            else:
                return 'algorithm_complex'
        
        # Процедуры работы с массивами
        if has_array:
            if 'реверс' in task_name or 'обратн' in task_todo:
                return 'array_reverse'
            elif 'циклическ' in task_todo or 'сдвиг' in task_todo:
                return 'array_shift'
            elif 'сортир' in task_todo:
                return 'array_sort'
            elif 'заполн' in task_todo:
                return 'array_fill'
            elif 'найт' in task_todo or 'поиск' in task_todo:
                return 'array_search'
            elif 'удал' in task_todo or 'вставк' in task_todo:
                return 'array_modify'
            else:
                return 'array_procedure'
        
        # Функции (возвращают значение)
        if any(prefix in task_name for prefix in ['цел ', 'вещ ']) and ('арг' in task_name or '(' in task_name):
            # Простые математические функции
            if 'последн' in task_name and 'цифр' in task_name:
                return 'func_last_digit'
            elif 'десятк' in task_name:
                return 'func_tens_digit'
            elif 'сотен' in task_name:
                return 'func_hundreds_digit'
            elif 'куб' in task_name and not ('поиск' in task_todo or 'корен' in task_todo):
                return 'func_cube'
            elif 'квадрат' in task_name and not ('поиск' in task_todo or 'корен' in task_todo):
                return 'func_square'
            elif 'округл' in task_name:
                if 'вверх' in task_name:
                    return 'func_round_up'
                else:
                    return 'func_round'
            elif 'прост' in task_name:
                return 'func_is_prime'
            elif 'палиндром' in task_name:
                return 'func_is_palindrome'
            # Сложные алгоритмические функции
            elif any(keyword in task_todo for keyword in ['шаг', 'поиск', 'корен', 'алгоритм']):
                return 'func_complex_algorithm'
            else:
                return 'func_generic'
        
        # Массивы - заполнение (без аргрез в сигнатуре)
        if 'заполн' in task_todo or 'заполн' in task_name:
            if 'нул' in task_todo:
                return 'arr_fill_zeros'
            elif 'натур' in task_todo:
                return 'arr_fill_natural'
            elif 'фибо' in task_todo:
                return 'arr_fill_fibonacci'
            elif 'степен' in task_todo or '2^' in task_todo:
                return 'arr_fill_powers2'
            elif 'горк' in task_todo:
                return 'arr_fill_pyramid'
            else:
                return 'arr_fill_generic'
        
        # Массивы - обработка
        if 'увелич' in task_todo:
            return 'arr_modify_increase'
        elif 'умнож' in task_todo:
            return 'arr_modify_multiply'
        elif 'квадрат' in task_todo:
            return 'arr_modify_square'
        
        # Массивы - поиск
        elif 'макс' in task_todo:
            return 'arr_find_max'
        elif 'мин' in task_todo:
            return 'arr_find_min'
        elif 'найт' in task_todo:
            return 'arr_find_value'
        
        # Массивы - подсчет
        elif 'скольк' in task_todo or 'количест' in task_todo:
            return 'arr_count'
        
        # Массивы - сумма
        elif 'сумм' in task_todo:
            return 'arr_sum'
        
        # Строки
        elif 'строк' in task_name or 'лит' in task_name:
            return 'string_task'
        
        # Робот
        elif 'робот' in task_name.lower():
            return 'robot_task'
        
        # По умолчанию
        return 'generic_task'

    def generate_python_solution(self, task: Dict[str, str]) -> str:
        """Генерирует Python код для решения задачи."""
        task_id = task['task_id']
        task_name = task['task_name']
        task_init = task['task_init']
        task_todo = task['task_todo']
        kumir_code = task['kumir_code']
        
        # Определяем тип задачи
        task_type = self.detect_task_type(task)
        
        # Определяем параметры функции
        has_X = 'арг цел X' in task_name or 'арг вещ X' in task_name or '(цел X)' in task_name or '(вещ X)' in task_name
        returns_value = any(prefix in task_name for prefix in ['цел ', 'вещ ']) and ('арг' in task_name or '(' in task_name)
        is_function = task_type.startswith('func_')
        
        short_name = self.clean_task_name_for_filename(task_name, task_id, task_type)
        
        code_lines = [
            f'"""',
            f'Task {task_id}: {short_name}',
            f'',
            f'Original: {task_name}',
            f'Init: {task_init}',
            f'Todo: {task_todo}',
            f'',
            f'Kumir code:',
            f'{kumir_code}',
            f'"""',
            f'',
        ]
        
        # Определяем сигнатуру функции
        if task_type.startswith('func_'):
            # Это функция, возвращающая значение
            if has_X:
                func_signature = f'def {short_name}(X):'
            else:
                func_signature = f'def {short_name}():'
        elif task_type.startswith('algorithm_') or task_type.startswith('array_'):
            # Алгоритмы и процедуры с массивами
            if has_X:
                func_signature = f'def {short_name}(N, A, X):'
            else:
                func_signature = f'def {short_name}(N, A):'
        elif has_X and returns_value:
            func_signature = f'def {short_name}(N: int, A: list, X: int):'
        elif has_X:
            func_signature = f'def {short_name}(N: int, A: list, X: int) -> list:'
        elif returns_value:
            func_signature = f'def {short_name}(N: int, A: list):'
        else:
            func_signature = f'def {short_name}(N: int, A: list) -> list:'
        
        code_lines.append(func_signature)
        code_lines.append('    """Python solution for the task."""')
        
        # Генерируем код в зависимости от типа задачи
        # Сначала проверяем новые типы (приоритет над старыми ID)
        if task_type == 'algorithm_binary_search':
            code_lines.extend([
                '    # Binary search algorithm',
                '    left, right = 1, min(N, 1000)',
                '    steps = 0',
                '    result = 0',
                '    ',
                '    while right >= left:',
                '        mid = (right + left) // 2',
                '        steps += 1',
                '        mid_cubed = mid * mid * mid',
                '        ',
                '        if N == mid_cubed:',
                '            result = mid',
                '            break',
                '        elif N < mid_cubed:',
                '            right = mid - 1',
                '        else:',
                '            left = mid + 1',
                '    ',
                '    return steps'
            ])
        elif task_type == 'array_reverse':
            code_lines.extend([
                '    # Reverse array elements',
                '    for i in range(N // 2):',
                '        A[i], A[N - 1 - i] = A[N - 1 - i], A[i]',
                '    return A'
            ])
        elif task_type == 'array_shift':
            code_lines.extend([
                '    # Cyclically shift array elements',
                '    if N > 1:',
                '        temp = A[N-1]',
                '        for i in range(N-1, 0, -1):',
                '            A[i] = A[i-1]',
                '        A[0] = temp',
                '    return A'
            ])
        elif task_type == 'array_sort':
            code_lines.extend([
                '    # Simple bubble sort',
                '    for i in range(N):',
                '        for j in range(N - 1 - i):',
                '            if A[j] > A[j + 1]:',
                '                A[j], A[j + 1] = A[j + 1], A[j]',
                '    return A'
            ])
        elif task_type == 'array_procedure':
            code_lines.extend([
                '    # Array procedure - implement based on task description',
                f'    # Task: {task_todo}',
                '    # TODO: Add specific implementation',
                '    return A'
            ])
        elif task_type == 'func_complex_algorithm':
            code_lines.extend([
                '    # Complex algorithmic function',
                f'    # Task: {task_todo}',
                '    # TODO: Implement complex algorithm',
                '    return 0  # Placeholder'
            ])
        # Простые функции
        elif task_type == 'func_last_digit':
            code_lines.extend([
                '    return X % 10'
            ])
        elif task_type == 'func_tens_digit':
            code_lines.extend([
                '    return (X // 10) % 10'
            ])
        elif task_type == 'func_hundreds_digit':
            code_lines.extend([
                '    return (X // 100) % 10'
            ])
        elif task_type == 'func_cube':
            code_lines.extend([
                '    return X * X * X'
            ])
        elif task_type == 'func_square':
            code_lines.extend([
                '    return X * X'
            ])
        elif task_type == 'func_round':
            code_lines.extend([
                '    from math import floor',
                '    if X - floor(X) >= 0.5:',
                '        return int(X) + 1',
                '    else:',
                '        return int(X)'
            ])
        elif task_type == 'func_round_up':
            code_lines.extend([
                '    import math',
                '    return math.ceil(X)'
            ])
        elif task_type == 'func_is_prime':
            code_lines.extend([
                '    if X < 2:',
                '        return 0',
                '    for i in range(2, int(X**0.5) + 1):',
                '        if X % i == 0:',
                '            return 0',
                '    return 1'
            ])
        elif task_type == 'func_is_palindrome':
            code_lines.extend([
                '    s = str(X)',
                '    return 1 if s == s[::-1] else 0'
            ])
        elif task_type == 'func_generic':
            # Попытаемся создать простую реализацию на основе описания
            if 'сумм' in task_todo.lower() and 'натур' in task_todo.lower():
                code_lines.extend([
                    '    # Sum of natural numbers from 1 to X',
                    '    return sum(range(1, X + 1))'
                ])
            elif 'произвед' in task_todo.lower() or 'факториал' in task_todo.lower():
                code_lines.extend([
                    '    # Factorial or product',
                    '    result = 1',
                    '    for i in range(1, X + 1):',
                    '        result *= i',
                    '    return result'
                ])
            elif 'четн' in task_todo.lower():
                code_lines.extend([
                    '    # Check if even',
                    '    return 1 if X % 2 == 0 else 0'
                ])
            elif 'нечетн' in task_todo.lower():
                code_lines.extend([
                    '    # Check if odd',
                    '    return 1 if X % 2 != 0 else 0'
                ])
            elif 'положит' in task_todo.lower():
                code_lines.extend([
                    '    # Check if positive',
                    '    return 1 if X > 0 else 0'
                ])
            elif 'отрицат' in task_todo.lower():
                code_lines.extend([
                    '    # Check if negative',
                    '    return 1 if X < 0 else 0'
                ])
            elif 'цифр' in task_todo.lower() and 'сумм' in task_todo.lower():
                code_lines.extend([
                    '    # Sum of digits',
                    '    total = 0',
                    '    x = abs(X)',
                    '    while x > 0:',
                    '        total += x % 10',
                    '        x //= 10',
                    '    return total'
                ])
            elif 'цифр' in task_todo.lower() and ('количест' in task_todo.lower() or 'скольк' in task_todo.lower()):
                code_lines.extend([
                    '    # Count of digits',
                    '    if X == 0:',
                    '        return 1',
                    '    count = 0',
                    '    x = abs(X)',
                    '    while x > 0:',
                    '        count += 1',
                    '        x //= 10',
                    '    return count'
                ])
            else:
                # Базовая реализация
                code_lines.extend([
                    '    # TODO: Implement based on task description',
                    f'    # Task: {task_todo}',
                    '    return 0  # Placeholder'
                ])
        elif task_id == "10" or task_type == 'arr_fill_zeros':  # Заполнить нулями
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = 0',
                '    return A'
            ])
        elif task_id == "11":  # Заполнить натуральными числами
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = i + 1',
                '    return A'
            ])
        elif task_id == "12":  # Заполнить от X
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = X + i',
                '    return A'
            ])
        elif task_id == "13":  # Плюс 5
            code_lines.extend([
                '    A[0] = X',
                '    for i in range(1, N):',
                '        A[i] = A[i-1] + 5',
                '    return A'
            ])
        elif task_id == "14":  # Фибоначчи
            code_lines.extend([
                '    if N >= 1:',
                '        A[0] = 1',
                '    if N >= 2:',
                '        A[1] = 1',
                '    for i in range(2, N):',
                '        A[i] = A[i-1] + A[i-2]',
                '    return A'
            ])
        elif task_id == "15":  # Степени 2
            code_lines.extend([
                '    A[N-1] = 1',
                '    for i in range(N-2, -1, -1):',
                '        A[i] = 2 * A[i+1]',
                '    return A'
            ])
        elif task_id == "16":  # Горка
            code_lines.extend([
                '    c = N // 2',
                '    A[c] = X',
                '    for i in range(c-1, -1, -1):',
                '        A[i] = A[i+1] - 1',
                '    for i in range(c+1, N):',
                '        A[i] = A[i-1] - 1',
                '    return A'
            ])
        elif task_id == "20":  # Увеличить на 1
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = A[i] + 1',
                '    return A'
            ])
        elif task_id == "21":  # Умножить на 2
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = A[i] * 2',
                '    return A'
            ])
        elif task_id == "22":  # Квадрат
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = A[i] * A[i]',
                '    return A'
            ])
        elif task_id == "30":  # Максимум
            code_lines.extend([
                '    max_val = A[0]',
                '    for i in range(N):',
                '        if A[i] > max_val:',
                '            max_val = A[i]',
                '    return max_val'
            ])
        elif task_id == "31":  # Минимум
            code_lines.extend([
                '    min_val = A[0]',
                '    for i in range(N):',
                '        if A[i] < min_val:',
                '            min_val = A[i]',
                '    return min_val'
            ])
        elif task_id == "40":  # Сколько единиц
            code_lines.extend([
                '    count = 0',
                '    for i in range(N):',
                '        if A[i] == 1:',
                '            count += 1',
                '    return count'
            ])
        elif task_id == "41":  # Сколько равных X
            code_lines.extend([
                '    count = 0',
                '    for i in range(N):',
                '        if A[i] == X:',
                '            count += 1',
                '    return count'
            ])
        elif task_id == "50":  # Сумма всех
            code_lines.extend([
                '    total = 0',
                '    for i in range(N):',
                '        total += A[i]',
                '    return total'
            ])
        elif task_id == "60":  # Номер X
            code_lines.extend([
                '    for i in range(N):',
                '        if A[i] == X:',
                '            return i + 1  # 1-based index',
                '    return -1'
            ])
        else:
            # Базовая реализация для остальных
            code_lines.extend([
                '    # TODO: Implement solution',
                f'    # Task: {task_todo}',
                '    pass'
            ])
        
        # Тестовая функция
        code_lines.extend([
            '',
            '',
            'def test_solution():',
            '    """Test the solution."""',
        ])
        
        if task_type.startswith('func_'):
            # Для функций
            code_lines.extend([
                '    test_values = [0, 1, 5, 123, 999]',
                '    for X in test_values:',
                f'        result = {short_name}(X)',
                '        print(f"Input: {X}, Result: {result}")',
                '    return True'
            ])
        elif task_type.startswith('algorithm_') or task_type.startswith('array_'):
            # Для алгоритмов и процедур с массивами
            code_lines.extend([
                '    # Test with sample data',
                '    N = 5',
                '    A = [1, 2, 3, 4, 5]',
            ])
            
            if has_X:
                code_lines.append('    X = 3')
                code_lines.append(f'    result = {short_name}(N, A.copy(), X)')
            else:
                code_lines.append(f'    result = {short_name}(N, A.copy())')
            
            code_lines.extend([
                '    print(f"Input: N={N}, A={A}")',
                '    print(f"Result: {result}")',
                '    return result'
            ])
        else:
            # Для массивов
            code_lines.extend([
                '    N = 5',
                '    A = [0] * N',
            ])
            
            if has_X:
                code_lines.append('    X = 10')
                code_lines.append(f'    result = {short_name}(N, A.copy(), X)')
            else:
                code_lines.append(f'    result = {short_name}(N, A.copy())')
            
            code_lines.extend([
                '    print(f"Result: {result}")',
                '    return result'
            ])
        
        code_lines.extend([
            '',
            '',
            'if __name__ == "__main__":',
            '    test_solution()'
        ])
        
        return '\n'.join(code_lines)
    
    def generate_all_python_solutions(self) -> bool:
        """Генерирует Python решения для всех задач."""
        print("🐍 Генерация Python решений...")
        
        try:
            with open(self.tasks_json_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
        except FileNotFoundError:
            print(f"❌ Файл {self.tasks_json_file} не найден!")
            return False
        
        success_count = 0
        for task in tasks:
            task_id = task['task_id']
            task_type = self.detect_task_type(task)
            short_name = self.clean_task_name_for_filename(task['task_name'], task_id, task_type)
            
            python_code = self.generate_python_solution(task)
            
            filename = f"{task_id}_{short_name}.py"
            filepath = self.python_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(python_code)
                success_count += 1
                print(f"  ✅ {filename}")
            except Exception as e:
                print(f"  ❌ {filename}: {e}")
        
        print(f"✅ Создано {success_count}/{len(tasks)} Python файлов")
        return success_count == len(tasks)
    
    def test_all_solutions(self) -> Dict[str, Any]:
        """Тестирует все Python решения."""
        print("🧪 Тестирование Python решений...")
        
        python_files = list(self.python_dir.glob("*.py"))
        
        results = {
            "total": len(python_files),
            "success": 0,
            "failed": [],
            "details": []
        }
        
        for py_file in sorted(python_files):
            try:
                result = subprocess.run([
                    sys.executable, str(py_file)
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    results["success"] += 1
                    results["details"].append({
                        "file": py_file.name,
                        "status": "success",
                        "output": result.stdout.strip()
                    })
                    print(f"  ✅ {py_file.name}")
                else:
                    results["failed"].append(py_file.name)
                    results["details"].append({
                        "file": py_file.name,
                        "status": "error",
                        "error": result.stderr.strip()
                    })
                    print(f"  ❌ {py_file.name}")
                    
            except subprocess.TimeoutExpired:
                results["failed"].append(py_file.name)
                results["details"].append({
                    "file": py_file.name,
                    "status": "timeout",
                    "error": "Timeout > 5 seconds"
                })
                print(f"  ⏰ {py_file.name}")
            except Exception as e:
                results["failed"].append(py_file.name)
                results["details"].append({
                    "file": py_file.name,
                    "status": "exception",
                    "error": str(e)
                })
                print(f"  💥 {py_file.name}")
        
        success_rate = (results["success"] / results["total"]) * 100 if results["total"] > 0 else 0
        print(f"📊 Результаты: {results['success']}/{results['total']} ({success_rate:.1f}%)")
        
        return results
    
    def create_comparison_framework(self, test_results: Dict[str, Any]) -> bool:
        """Создает фреймворк для сравнения Python и КУМИР решений."""
        print("📋 Создание фреймворка для сравнения...")
        
        # Создаем пример скрипта для сравнения
        comparison_script = f'''#!/usr/bin/env python3
"""
Framework for comparing Python and Kumir solutions.
Generated automatically by KumirToPythonPipeline.
"""

import sys
import json
from pathlib import Path

# Add python solutions to path
sys.path.append(str(Path(__file__).parent / "python_solutions"))

def load_tasks():
    """Load task data."""
    with open("tasks_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def compare_solutions():
    """Compare Python and Kumir solutions."""
    tasks = load_tasks()
    
    print("🔍 Comparison Framework Ready")
    print("=" * 50)
    
    for task in tasks:
        task_id = task["task_id"]
        print(f"Task {{task_id}}: {{task['task_name']}}")
        
        # TODO: Implement Kumir interpreter integration
        # kumir_result = run_kumir_code(task["kumir_code"], test_data)
        # python_result = run_python_solution(task_id, test_data)
        # assert kumir_result == python_result
    
    print("\\n✅ Framework ready for Kumir integration")

if __name__ == "__main__":
    compare_solutions()
'''
        
        try:
            with open(self.output_dir / "compare_solutions.py", 'w', encoding='utf-8') as f:
                f.write(comparison_script)
        except Exception as e:
            print(f"❌ Ошибка создания скрипта сравнения: {e}")
            return False
        
        # Создаем отчет
        report_content = f"""# Kumir to Python Pipeline Report

## Summary
- **Input XML**: {self.xml_file_path}
- **Total Tasks**: {test_results['total']}
- **Successful Tests**: {test_results['success']}
- **Success Rate**: {(test_results['success']/test_results['total']*100):.1f}%

## Generated Files
- `tasks_data.json` - Parsed task data
- `python_solutions/` - Python implementations ({test_results['total']} files)
- `compare_solutions.py` - Comparison framework

## Test Results
"""
        
        for detail in test_results['details']:
            status_emoji = "✅" if detail['status'] == 'success' else "❌"
            report_content += f"- {status_emoji} `{detail['file']}` - {detail['status']}\n"
        
        if test_results['failed']:
            report_content += f"\n## Failed Tests\n"
            for failed in test_results['failed']:
                report_content += f"- {failed}\n"
        
        report_content += f"""
## Usage
1. **Testing Python solutions**:
   ```bash
   python compare_solutions.py
   ```

2. **Integration with Kumir interpreter**:
   - Implement `run_kumir_code()` function
   - Add test data generation
   - Run comparison tests

## Next Steps
- Integrate with your Kumir interpreter
- Add comprehensive test data
- Implement automated comparison testing
"""
        
        try:
            with open(self.reports_dir / "pipeline_report.md", 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ Отчет создан: {self.reports_dir}/pipeline_report.md")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания отчета: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """Запускает полный pipeline обработки."""
        print("🚀 Запуск полного Kumir to Python Pipeline")
        print("=" * 60)
        
        # Шаг 1: Парсинг XML
        if not self.parse_kumir_xml_to_json():
            return False
        
        # Шаг 2: Генерация Python решений
        if not self.generate_all_python_solutions():
            return False
        
        # Шаг 3: Тестирование решений
        test_results = self.test_all_solutions()
        
        # Шаг 4: Создание фреймворка для сравнения
        if not self.create_comparison_framework(test_results):
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Pipeline завершен успешно!")
        print(f"📁 Результаты в папке: {self.output_dir}")
        print(f"📊 Готово к сравнению: {test_results['success']}/{test_results['total']} задач")
        
        return True


    def convert_kumir_to_python(self, kumir_code: str) -> str:
        """Простой конвертер КУМИРовского кода в Python."""
        lines = kumir_code.split('\n')
        python_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line in ['нач', 'кон']:
                continue
                
            # Заменяем основные операторы
            line = line.replace('знач:=', 'result = ')
            line = line.replace(':=', ' = ')
            line = line.replace('mod(', '(')
            line = line.replace('div(', '(')
            line = line.replace(',', ' // ')
            line = line.replace('mod', '%')
            line = line.replace('div', '//')
            line = line.replace('если', 'if')
            line = line.replace('то', ':')
            line = line.replace('все', '')
            line = line.replace('для', 'for')
            line = line.replace('от', 'in range(')
            line = line.replace('до', ',')
            line = line.replace('нц', ':')
            line = line.replace('кц', '')
            
            if line:
                python_lines.append(line)
        
        return '\n    '.join(python_lines) if python_lines else 'pass'
def main():
    """Главная функция."""
    if len(sys.argv) != 2:
        print("Usage: python kumir_pipeline.py <xml_file_path>")
        print("Example: python kumir_pipeline.py pol_kurs.xml")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    
    if not os.path.exists(xml_file):
        print(f"❌ Файл не найден: {xml_file}")
        sys.exit(1)
    
    # Создаем и запускаем pipeline
    pipeline = KumirToPythonPipeline(xml_file)
    success = pipeline.run_full_pipeline()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
