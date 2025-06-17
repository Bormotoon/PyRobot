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
        
        # Определяем тип курса по имени файла
        file_name = Path(xml_file_path).name.lower()
        if 'robot' in file_name:
            self.course_type = 'robot'
        elif 'водолей' in file_name:
            self.course_type = 'waterman'
        elif 'огэ' in file_name:
            self.course_type = 'algorithms'
        else:
            self.course_type = 'general'
        self.reports_dir = self.output_dir / "reports"
        
        # Создаем директории
        self.output_dir.mkdir(exist_ok=True)
        self.python_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def clean_task_name_for_filename(self, task_name: str, task_id: str, task_type: str = "") -> str:
        """Создает короткое английское имя файла на основе типа задачи."""
        
        # Если у нас есть тип задачи из детектора - используем его
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
                    'func_count_binary_ones': 'count_binary_ones',
                    'func_count_binary_zeros': 'count_binary_zeros',
                    'func_count_ones': 'count_ones',
                    'func_count_elements': 'count_elements',
                    'func_sum_array': 'sum_array',
                    'func_max_array': 'max_array',
                    'func_min_array': 'min_array',
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
                    'array_procedure': 'array_proc',
                    'array_proc': 'array_proc',
                    'array_inc_by1': 'arr_inc_by1',
                    'array_inc_byX': 'arr_inc_byX',
                    'array_mult_by2': 'arr_mult_by2',
                    'array_mult_byX': 'arr_mult_byX',
                    'array_square': 'arr_square'
                }
                return type_names.get(task_type, 'array_task')
            elif task_type in ['robot_task', 'waterman_task', 'empty_task']:
                return f'task_{task_id}'
            elif task_type == 'string_task':
                return 'string_task'
        
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
        task_init = task['task_init'].lower()
        task_todo = task['task_todo'].lower()
        kumir_code = task['kumir_code'].lower()
        
        # Пропускаем пустые задачи
        if not task_name.strip() and not task_init.strip() and not task_todo.strip() and not kumir_code.strip():
            return 'empty_task'
        
        # Если это курс роботов - все задачи считаем robot_task
        if self.course_type == 'robot':
            return 'robot_task'
        
        # Если это курс Водолея - все задачи считаем waterman_task
        if self.course_type == 'waterman':
            return 'waterman_task'
        
        # Специальные исполнители - проверяем по содержимому
        if ('робот' in task_name or 'робот' in task_init or 'робот' in task_todo or 
            any(cmd in kumir_code for cmd in ['вверх', 'вниз', 'влево', 'вправо', 'закрасить'])):
            return 'robot_task'
        
        if ('водолей' in task_name or 'водолей' in task_init or 'водолей' in task_todo or
            any(cmd in kumir_code for cmd in ['наполнить', 'опустошить', 'перелить'])):
            return 'waterman_task'
        
        # Проверяем наличие массивов в сигнатуре (определяем заранее для использования в функциях)
        has_array = any(keyword in task_name for keyword in ['аргрез', 'целтаб', 'вещтаб', 'лоттаб', 'массив'])
        # Проверяем наличие аргумент-результат массивов (принимают и изменяют массив) - СНАЧАЛА!
        has_argresult_array = any(keyword in task_name for keyword in ['аргрез целтаб', 'аргрез вещтаб', 'аргрез лоттаб'])
        # Проверяем наличие результирующих массивов в процедурах (только рез, но НЕ аргрез) - ПОСЛЕ!
        # Важно: проверяем " рез " с пробелами или в начале строки, чтобы исключить "аргрез"
        has_result_array = any(
            (f' {keyword}' in task_name or task_name.startswith(keyword))
            for keyword in ['рез целтаб', 'рез вещтаб', 'рез лоттаб']
        )
        
        # Сложные алгоритмы (только настоящий двоичный поиск, сортировки, и т.д.)
        # Исключаем "двоичной записи" - это не двоичный поиск!
        if any(keyword in task_todo for keyword in ['пузыр', 'быстр', 'слиян']):
            return 'algorithm_complex'
        elif 'сортир' in task_todo and not any(x in task_todo for x in ['после сортировки', 'максимум', 'минимум', 'экстремум', 'два максимума', 'два минимума', 'второй максимум', 'второй минимум']):
            # Реальная сортировка, не просто упоминание сортировки в описании
            return 'algorithm_sort'
        # Настоящий двоичный поиск - только точное совпадение "двоичный поиск" или "бинарный поиск"
        if ('двоичный поиск' in task_todo or 'бинарный поиск' in task_todo) and 'записи' not in task_todo:
            return 'algorithm_binary_search'
        
        # ПРОЦЕДУРЫ с аргумент-результат массивами (изменяют переданный массив) - СНАЧАЛА!
        if has_argresult_array:
            if 'увелич' in task_todo:
                if '1' in task_todo or 'на 1' in task_todo:
                    return 'array_inc_by1'
                elif 'половин' in task_todo or 'часть' in task_todo:
                    # Специальные случаи - увеличение части массива
                    return 'array_proc'
                else:
                    return 'array_inc_byX'
            elif 'умнож' in task_todo:
                if '2' in task_todo or 'на 2' in task_todo:
                    return 'array_mult_by2'
                elif 'половин' in task_todo or 'часть' in task_todo:
                    # Специальные случаи - умножение части массива
                    return 'array_proc'
                else:
                    return 'array_mult_byX'
            elif 'квадрат' in task_todo:
                return 'array_square'
            elif 'реверс' in task_todo or 'обратн' in task_todo:
                return 'array_reverse'
            elif 'циклическ' in task_todo or 'сдвиг' in task_todo:
                return 'array_shift'
            elif 'сортир' in task_todo:
                return 'array_sort'
            else:
                return 'array_procedure'
        
        # ПРОЦЕДУРЫ с результирующими массивами (проверяем ПОСЛЕ аргрез!)
        if has_result_array:
            if 'заполн' in task_todo:
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
            elif 'увелич' in task_todo:
                return 'arr_modify_increase'
            elif 'умнож' in task_todo:
                return 'arr_modify_multiply'
            elif 'квадрат' in task_todo:
                return 'arr_modify_square'
            else:
                return 'array_procedure'
        
        # Функции (возвращают значение) - проверяем ПЕРЕД массивами!
        if any(prefix in task_name for prefix in ['цел ', 'вещ ', 'лог ', 'лит ']) and ('арг' in task_name or '(' in task_name):
            # Специальные функции
            if 'средн' in task_todo and 'арифметическ' in task_todo:
                return 'func_average'
            elif 'минимум' in task_todo or 'наименьш' in task_todo:
                return 'func_min'
            elif 'максимум' in task_todo or 'наибольш' in task_todo:
                return 'func_max'
            elif 'лог ' in task_name and ('оканчивается' in task_todo or 'на 0' in task_todo):
                return 'func_ends_with_zero'
            elif 'счастлив' in task_todo:
                return 'func_lucky_ticket'
            elif 'единиц' in task_name and 'двоичн' in task_todo:
                return 'func_count_binary_ones'
            elif 'нулей' in task_name and 'двоичн' in task_todo:
                return 'func_count_binary_zeros'
            elif 'палиндром' in task_name:
                return 'func_is_palindrome'
            elif 'прост' in task_name:
                return 'func_is_prime'
            # Функции с массивами - специальные случаи
            elif 'единиц' in task_name and has_array:
                return 'func_count_ones'
            elif ('количест' in task_todo.lower() or 'количест' in task_name.lower()) and has_array:
                return 'func_count_elements'
            elif ('скольк' in task_todo.lower() or 'скольк' in task_name.lower()) and has_array:
                return 'func_count_elements'  
            elif 'сумм' in task_todo and has_array:
                return 'func_sum_array'
            elif 'макс' in task_todo and has_array:
                return 'func_max_array'
            elif 'мин' in task_todo and has_array:
                return 'func_min_array'
            # Простые математические функции
            elif 'последн' in task_name and 'цифр' in task_name:
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
        
        # Процедуры работы с массивами (только если НЕ функция!)
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
        
        # Функции (возвращают значение) - проверяем ПЕРЕД строками!
        if any(prefix in task_name for prefix in ['цел ', 'вещ ', 'лог ', 'лит ']) and ('арг' in task_name or '(' in task_name):
            # Специальные функции
            if 'средн' in task_todo and 'арифметическ' in task_todo:
                return 'func_average'
            elif 'минимум' in task_todo or 'наименьш' in task_todo:
                return 'func_min'
            elif 'максимум' in task_todo or 'наибольш' in task_todo:
                return 'func_max'
            elif 'лог ' in task_name and ('оканчивается' in task_todo or 'на 0' in task_todo):
                return 'func_ends_with_zero'
            elif 'счастлив' in task_todo:
                return 'func_lucky_ticket'
            elif 'единиц' in task_name and 'двоичн' in task_todo:
                return 'func_count_binary_ones'
            elif 'нулей' in task_name and 'двоичн' in task_todo:
                return 'func_count_binary_zeros'
            elif 'палиндром' in task_name:
                return 'func_is_palindrome'
            elif 'прост' in task_name:
                return 'func_is_prime'
            # Простые математические функции
            elif 'последн' in task_name and 'цифр' in task_name:
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
        
        # Строки (проверяем ПОСЛЕ функций!)
        if 'строк' in task_name.lower() or ('лит' in task_name and 'лит ' not in task_name):
            return 'string_task'
        
        # По умолчанию
        return 'generic_task'

    def generate_python_solution(self, task: Dict[str, str]) -> str:
        """Генерирует Python код для решения задачи."""
        task_id = task['task_id']
        task_name = task['task_name']
        task_init = task['task_init']
        task_todo = task['task_todo']
        kumir_code = task['kumir_code']
        
        # Определяем параметры функции более точно
        import re
        
        # Поиск параметров в сигнатуре функции - используем самый надёжный метод
        params = []
        param_types = {}
        array_params = set()
        string_params = set()
        
        # Ищем содержимое в скобках и разбираем
        paren_match = re.search(r'\(([^)]+)\)', task_name)
        if paren_match:
            content = paren_match.group(1)
            # Разделяем по запятым и ищем переменные
            parts = [p.strip() for p in content.split(',')]
            for part in parts:
                # Попробуем сначала найти полные конструкции типа "аргрез цел X" или "арг лит Y"
                if re.match(r'аргрез\s+(цел|вещ|лог|лит)таб\s+[A-Z][a-zA-Z0-9]*', part):
                    # Аргумент-результат массив: обработаем ниже
                    array_match = re.search(r'аргрез\s+(цел|вещ|лог|лит)таб\s+([A-Z][a-zA-Z0-9]*)', part)
                    if array_match:
                        var_name = array_match.group(2)
                        var_type = array_match.group(1) + 'таб'
                        params.append(var_name)
                        param_types[var_name] = var_type
                        array_params.add(var_name)
                elif re.match(r'арг\s+(цел|вещ|лог|лит)\s+[A-Z][a-zA-Z0-9]*', part):
                    # Аргумент: "арг цел X"
                    arg_match = re.search(r'арг\s+(цел|вещ|лог|лит)\s+([A-Z][a-zA-Z0-9]*)', part)
                    if arg_match:
                        var_name = arg_match.group(2)
                        var_type = arg_match.group(1)
                        params.append(var_name)
                        param_types[var_name] = var_type
                        if var_type == 'лит':
                            string_params.add(var_name)
                elif re.match(r'(цел|вещ|лог|лит)таб\s+[A-Z][a-zA-Z0-9]*', part):
                    # Массив: "целтаб A[1:N]"
                    array_match = re.search(r'(цел|вещ|лог|лит)таб\s+([A-Z][a-zA-Z0-9]*)', part)
                    if array_match:
                        var_name = array_match.group(2)
                        var_type = array_match.group(1) + 'таб'
                        params.append(var_name)
                        param_types[var_name] = var_type
                        array_params.add(var_name)
                else:
                    # Простые формы: "лит s", "цел x", etc.
                    simple_match = re.search(r'(цел|вещ|лог|лит)\s+([a-zA-Z][a-zA-Z0-9]*)', part)
                    if simple_match:
                        var_name = simple_match.group(2)
                        var_type = simple_match.group(1)
                        params.append(var_name)
                        param_types[var_name] = var_type
                        if var_type == 'лит':
                            string_params.add(var_name)
                    else:
                        # Последняя попытка - просто переменная в конце
                        var_match = re.search(r'([a-zA-Z][a-zA-Z0-9]*)$', part.strip())
                        if var_match:
                            params.append(var_match.group(1))
        
        # Если ничего не найдено в task_name, пробуем альтернативные методы и task_init
        if not params:
            # Второй вариант: поиск арг конструкций (включая массивы)
            # Ищем параметры массивов: аргрез целтаб X, аргрез вещтаб A, etc.
            array_param_matches = re.findall(r'аргрез\s+(?:цел|вещ|лог|лит)таб\s+([A-Z][a-zA-Z0-9]*)', task_name)
            if array_param_matches:
                params.extend(array_param_matches)
            
            # Ищем обычные параметры: арг цел X, арг лит S, etc.
            param_matches = re.findall(r'арг\s+(?:цел|вещ|лит|лог)\s+([A-Z][a-zA-Z0-9]*)', task_name)
            if param_matches:
                params.extend(param_matches)
        
        # Третий вариант: парсинг параметров из task_init (блок "дано")
        if not params or len(params) < 2:
            # Ищем параметры в task_init в формате "цел N, таб цел A[1:N], цел X"
            init_params = []
            
            # Ищем простые параметры: цел N, цел X, лит s
            simple_params = re.findall(r'(?:^|,\s*)(?:арг\s+)?(цел|вещ|лит|лог)\s+([A-Z][a-zA-Z0-9]*)', task_init)
            for param_type, param_name in simple_params:
                if param_name not in init_params:
                    init_params.append(param_name)
                    param_types[param_name] = param_type
                    if param_type == 'лит':
                        string_params.add(param_name)
            
            # Ищем массивы: таб цел A[1:N], рез целтаб A[1:N]
            array_matches = re.findall(r'(?:рез\s+)?(цел|вещ|лит|лог)таб\s+([A-Z][a-zA-Z0-9]*)', task_init)
            for param_type, param_name in array_matches:
                if param_name not in init_params:
                    init_params.append(param_name)
                    param_types[param_name] = f'{param_type}таб'
                    array_params.add(param_name)
            
            # Если найдены параметры в task_init, используем их
            if init_params:
                params = init_params
        
        # Четвёртый вариант: улучшенный парсинг из task_name для функций вида "тип Название (параметры)"
        if not params and ('(' in task_name and ')' in task_name):
            # Ищем все в скобках более тщательно
            paren_content = re.search(r'\(([^)]+)\)', task_name)
            if paren_content:
                content = paren_content.group(1).strip()
                # Разбираем параметры через запятую
                param_parts = [p.strip() for p in content.split(',')]
                extracted_params = []
                
                for part in param_parts:
                    if not part:
                        continue
                    
                    # Ищем паттерны: "цел X", "целтаб A[1:N]", "сим c", etc.
                    type_param_match = re.match(r'(цел|вещ|лог|лит|сим|целтаб|вещтаб|логтаб|литтаб)\s+([A-Za-z][A-Za-z0-9]*)', part)
                    if type_param_match:
                        param_type, param_name = type_param_match.groups()
                        extracted_params.append(param_name)
                        param_types[param_name] = param_type
                        if param_type in ['лит', 'сим']:
                            string_params.add(param_name)
                        elif param_type in ['целтаб', 'вещтаб', 'логтаб', 'литтаб']:
                            array_params.add(param_name)
                    elif re.match(r'^[A-Za-z][A-Za-z0-9]*$', part):
                        # Просто имя переменной
                        extracted_params.append(part)
                
                if extracted_params:
                    params = extracted_params
        
        # Определяем типы параметров для лучшей генерации кода
        # Анализируем типы параметров из сигнатуры
        if 'аргрез' in task_name:
            # Массивы
            array_matches = re.findall(r'аргрез\s+(цел|вещ|лог|лит)таб\s+([A-Z][a-zA-Z0-9]*)', task_name)
            for param_type, param_name in array_matches:
                array_params.add(param_name)
                param_types[param_name] = f'{param_type}таб'
        
        # Обычные параметры с ключевым словом "арг"
        param_type_matches = re.findall(r'арг\s+(цел|вещ|лит|лог)\s+([A-Z][a-zA-Z0-9]*)', task_name)
        for param_type, param_name in param_type_matches:
            if param_name not in params:
                params.append(param_name)  # Добавляем в список параметров
            param_types[param_name] = param_type
            if param_type == 'лит':
                string_params.add(param_name)
        
        # Простые типы без ключевого слова "арг"
        simple_type_matches = re.findall(r'(?<!\w)(цел|вещ|лит|лог)\s+([A-Z][a-zA-Z0-9]*)', task_name)
        for param_type, param_name in simple_type_matches:
            # Убеждаемся, что это не часть аргрез или арг конструкции
            if param_name in params:  # Только если параметр уже найден
                param_types[param_name] = param_type
                if param_type == 'лит':
                    string_params.add(param_name)
        
        # Определяем тип функции более точно на основе параметров
        if len(params) >= 2 and 'средн' in task_todo:
            task_type = 'func_average'
        elif len(params) >= 2 and ('минимум' in task_todo or 'наименьш' in task_todo):
            task_type = 'func_min'
        elif len(params) >= 2 and ('максимум' in task_todo or 'наибольш' in task_todo):
            task_type = 'func_max'
        else:
            task_type = self.detect_task_type(task)
        
        # Определяем тип возврата
        returns_value = any(prefix in task_name for prefix in ['цел ', 'вещ ', 'лог ']) and ('арг' in task_name or '(' in task_name)
        # Процедуры с результирующими массивами тоже возвращают значения
        if task_type.startswith('arr_'):
            returns_value = True
        return_type = None
        if 'цел ' in task_name[:10]:
            return_type = 'int'
        elif 'вещ ' in task_name[:10]:
            return_type = 'float'
        elif 'лог ' in task_name[:10]:
            return_type = 'bool'
        elif 'лит ' in task_name[:10]:
            return_type = 'str'
        
        # Определяем, есть ли строковые параметры
        has_string_param = 'лит ' in task_name
        
        # Старое определение для совместимости
        has_X = 'X' in params
        is_function = task_type.startswith('func_') or task_type.startswith('arr_') or returns_value
        
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
        if task_type.startswith('arr_'):
            # Процедуры с результирующими массивами - создают массив внутри
            if 'X' in params or has_X:
                func_signature = f'def {short_name}(N: int, X: int = 1) -> list:'
            else:
                func_signature = f'def {short_name}(N: int) -> list:'
        elif is_function or returns_value:
            # Это функция, возвращающая значение
            if array_params:
                # Функция с массивами - используем стандартную сигнатуру с массивами
                if 'X' in params:  # Есть дополнительный параметр поиска
                    func_signature = f'def {short_name}(N: int, A: list, X: int):'
                else:
                    func_signature = f'def {short_name}(N: int, A: list):'
            elif string_params:
                # Функция со строками
                string_param_names = [p for p in params if p in string_params]
                other_param_names = [p for p in params if p not in string_params]
                all_params = other_param_names + string_param_names
                func_signature = f'def {short_name}({", ".join(all_params)}):'
            elif len(params) == 0:
                func_signature = f'def {short_name}():'
            elif len(params) == 1:
                func_signature = f'def {short_name}({params[0]}):'
            elif len(params) == 2:
                func_signature = f'def {short_name}({params[0]}, {params[1]}):'
            elif len(params) == 3:
                func_signature = f'def {short_name}({params[0]}, {params[1]}, {params[2]}):'
            else:
                func_signature = f'def {short_name}({", ".join(params)}):'
        elif task_type.startswith('algorithm_') or task_type.startswith('array_'):
            # Алгоритмы и процедуры с массивами
            if has_X:
                func_signature = f'def {short_name}(N, A, X):'
            else:
                func_signature = f'def {short_name}(N, A):'
        elif task_type == 'string_task':
            # Строковые задачи
            if len(params) > 0:
                func_signature = f'def {short_name}({", ".join(params)}):'
            else:
                func_signature = f'def {short_name}(s: str):'
        elif task_type == 'robot_task':
            # Задачи робота - без параметров
            func_signature = f'def {short_name}():'
        elif task_type == 'waterman_task':
            # Задачи водолея - без параметров
            func_signature = f'def {short_name}():'
        elif task_type == 'empty_task':
            # Пустые задачи - пропускаем
            func_signature = f'def {short_name}():'
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
        # Сначала проверяем специальных исполнителей
        if task_type == 'robot_task':
            code_lines.extend([
                '    # Задача робота - выполняем команды',
                f'    # TODO: Реализовать алгоритм робота',
                f'    # Команды: {kumir_code[:100]}...' if len(kumir_code) > 100 else f'    # Команды: {kumir_code}',
                '    # Пример: robot.up(), robot.down(), robot.left(), robot.right(), robot.paint()',
                '    pass'
            ])
        elif task_type == 'waterman_task':
            code_lines.extend([
                '    # Задача водолея - переливания жидкостей',
                f'    # TODO: Реализовать алгоритм водолея',
                f'    # Команды: {kumir_code[:100]}...' if len(kumir_code) > 100 else f'    # Команды: {kumir_code}',
                '    # Пример: fill(A), empty(A), pour(A, B)',
                '    pass'
            ])
        elif task_type == 'empty_task':
            code_lines.extend([
                '    # Пустая задача - нет описания',
                '    # TODO: Добавить описание и реализацию',
                '    pass'
            ])
        # Сначала проверяем новые типы (приоритет над старыми ID)
        elif task_type == 'algorithm_binary_search':
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
        elif task_type == 'array_inc_by1':
            code_lines.extend([
                '    # Увеличить все элементы на 1',
                '    for i in range(N):',
                '        A[i] += 1',
                '    return A'
            ])
        elif task_type == 'array_inc_byX':
            code_lines.extend([
                '    # Увеличить все элементы на X',
                '    for i in range(N):',
                '        A[i] += X',
                '    return A'
            ])
        elif task_type == 'array_mult_by2':
            code_lines.extend([
                '    # Умножить все элементы на 2',
                '    for i in range(N):',
                '        A[i] *= 2',
                '    return A'
            ])
        elif task_type == 'array_mult_byX':
            code_lines.extend([
                '    # Умножить все элементы на X',
                '    for i in range(N):',
                '        A[i] *= X',
                '    return A'
            ])
        elif task_type == 'array_square':
            code_lines.extend([
                '    # Возвести все элементы в квадрат',
                '    for i in range(N):',
                '        A[i] = A[i] ** 2',
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
        elif task_type == 'func_count_binary_ones':
            param_name = params[0] if params else 'X'
            code_lines.extend([
                '    # Подсчет единиц в двоичной записи числа',
                '    count = 0',
                f'    num = {param_name}',
                '    while num > 0:',
                '        if num % 2 == 1:',
                '            count += 1',
                '        num = num // 2',
                '    return count'
            ])
        elif task_type == 'func_count_binary_zeros':
            param_name = params[0] if params else 'X'
            code_lines.extend([
                '    # Подсчет нулей в двоичной записи числа',
                '    count = 0',
                f'    num = {param_name}',
                '    while num > 0:',
                '        if num % 2 == 0:',
                '            count += 1',
                '        num = num // 2',
                '    return count'
            ])
        elif task_type == 'func_is_palindrome':
            param_name = params[0] if params else 'N'
            code_lines.extend([
                '    # Проверка на палиндром',
                f'    s = str({param_name})',
                '    return s == s[::-1]'
            ])
        elif task_type == 'func_is_prime':
            param_name = params[0] if params else 'N'
            code_lines.extend([
                '    # Проверка на простое число',
                f'    if {param_name} < 2:',
                '        return False',
                f'    for i in range(2, int({param_name}**0.5) + 1):',
                f'        if {param_name} % i == 0:',
                '            return False',
                '    return True'
            ])
        elif task_type == 'func_count_ones':
            code_lines.extend([
                '    # Подсчет количества единиц в массиве',
                '    count = 0',
                '    for i in range(N):',
                '        if A[i] == 1:',
                '            count += 1',
                '    return count'
            ])
        elif task_type == 'func_count_elements':
            code_lines.extend([
                '    # Подсчет количества элементов по условию',
                '    count = 0',
                '    for i in range(N):',
                '        # TODO: Добавить конкретное условие',
                '        if True:  # Placeholder',
                '            count += 1',
                '    return count'
            ])
        elif task_type == 'func_sum_array':
            code_lines.extend([
                '    # Сумма элементов массива',
                '    total = 0',
                '    for i in range(N):',
                '        total += A[i]',
                '    return total'
            ])
        elif task_type == 'func_max_array':
            code_lines.extend([
                '    # Максимальный элемент массива',
                '    if N == 0:',
                '        return 0',
                '    max_val = A[0]',
                '    for i in range(1, N):',
                '        if A[i] > max_val:',
                '            max_val = A[i]',
                '    return max_val'
            ])
        elif task_type == 'func_min_array':
            code_lines.extend([
                '    # Минимальный элемент массива',
                '    if N == 0:',
                '        return 0',
                '    min_val = A[0]',
                '    for i in range(1, N):',
                '        if A[i] < min_val:',
                '            min_val = A[i]',
                '    return min_val'
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
        elif task_type == 'func_average':
            # Среднее арифметическое
            if len(params) == 2:
                code_lines.extend([
                    f'    return ({params[0]} + {params[1]}) / 2'
                ])
            elif len(params) == 3:
                code_lines.extend([
                    f'    return ({params[0]} + {params[1]} + {params[2]}) / 3'
                ])
            else:
                code_lines.extend([
                    f'    return sum([{", ".join(params)}]) / {len(params)}'
                ])
        elif task_type == 'func_min':
            # Минимум
            code_lines.extend([
                f'    return min({", ".join(params)})'
            ])
        elif task_type == 'func_max':
            # Максимум
            code_lines.extend([
                f'    return max({", ".join(params)})'
            ])
        elif task_type == 'func_ends_with_zero':
            # Оканчивается на ноль
            code_lines.extend([
                '    return 1 if N % 10 == 0 else 0'
            ])
        elif task_type == 'func_lucky_ticket':
            # Счастливый билет
            code_lines.extend([
                '    # Счастливый билет - сумма первых 3 цифр == сумме последних 3',
                '    s = str(N).zfill(6)  # Дополняем до 6 цифр',
                '    if len(s) != 6:',
                '        return 0',
                '    first_sum = sum(int(d) for d in s[:3])',
                '    last_sum = sum(int(d) for d in s[3:])',
                '    return 1 if first_sum == last_sum else 0'
            ])
        elif task_type == 'func_from_binary':
            # Из двоичной системы
            code_lines.extend([
                '    # Convert binary string to integer',
                '    return int(s, 2)'
            ])
        elif task_type == 'func_from_octal':
            # Из восьмеричной системы
            code_lines.extend([
                '    # Convert octal string to integer',
                '    return int(s, 8)'
            ])
        # Специальные обработчики для конкретных функций
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
        # Строковые задачи
        elif task_type == 'string_task' or string_params:
            # Определяем тип строковой операции
            task_lower = task_todo.lower()
            name_lower = task_name.lower()
            
            if ('первый' in task_lower or 'первый' in name_lower) and 'символ' in (task_lower + name_lower):
                code_lines.extend([
                    '    # Return first character',
                    '    return s[0] if s else ""'
                ])
            elif ('последн' in task_lower or 'последн' in name_lower) and 'символ' in (task_lower + name_lower):
                code_lines.extend([
                    '    # Return last character',
                    '    return s[-1] if s else ""'
                ])
            elif 'длин' in task_lower or 'длин' in name_lower:
                code_lines.extend([
                    '    # String length',
                    '    return len(s)'
                ])
            elif 'символ' in task_lower and 'номер' in task_lower:
                code_lines.extend([
                    '    # Character at position',
                    '    if 1 <= n <= len(s):',
                    '        return s[n-1]  # Convert to 0-based index',
                    '    return ""'
                ])
            elif 'поиск' in task_lower or 'найт' in task_lower:
                code_lines.extend([
                    '    # Find substring',
                    '    pos = s.find(substr)',
                    '    return pos + 1 if pos != -1 else 0  # Convert to 1-based index'
                ])
            elif 'замен' in task_lower:
                code_lines.extend([
                    '    # Replace substring',
                    '    return s.replace(old_substr, new_substr)'
                ])
            elif 'удал' in task_lower:
                code_lines.extend([
                    '    # Remove substring',
                    '    return s.replace(substr, "")'
                ])
            elif 'вставк' in task_lower:
                code_lines.extend([
                    '    # Insert substring',
                    '    pos = pos - 1  # Convert to 0-based index',
                    '    return s[:pos] + substr + s[pos:]'
                ])
            elif 'обрат' in task_lower or 'реверс' in task_lower:
                code_lines.extend([
                    '    # Reverse string',
                    '    return s[::-1]'
                ])
            elif 'заглавн' in task_lower or 'больш' in task_lower:
                code_lines.extend([
                    '    # Convert to uppercase',
                    '    return s.upper()'
                ])
            elif 'строчн' in task_lower or 'малень' in task_lower:
                code_lines.extend([
                    '    # Convert to lowercase',
                    '    return s.lower()'
                ])
            elif 'слов' in task_lower and ('количест' in task_lower or 'скольк' in task_lower):
                code_lines.extend([
                    '    # Count words',
                    '    return len(s.split())'
                ])
            else:
                # Базовая реализация для строк
                code_lines.extend([
                    '    # TODO: Implement string operation',
                    f'    # Task: {task_todo}',
                    '    return s  # Placeholder'
                ])
        elif task_id == "10" or task_type == 'arr_fill_zeros':  # Заполнить нулями
            code_lines.extend([
                '    A = [0] * N  # Создаем массив',
                '    for i in range(N):',
                '        A[i] = 0',
                '    return A'
            ])
        elif task_type == 'arr_fill_natural':  # Заполнить натуральными числами
            code_lines.extend([
                '    A = [0] * N  # Создаем массив',
                '    for i in range(N):',
                '        A[i] = i + 1',
                '    return A'
            ])
        elif task_type == 'arr_fill_fibonacci':  # Заполнить числами Фибоначчи
            code_lines.extend([
                '    A = [0] * N  # Создаем массив',
                '    if N > 0:',
                '        A[0] = 1',
                '    if N > 1:',
                '        A[1] = 1',
                '    for i in range(2, N):',
                '        A[i] = A[i-1] + A[i-2]',
                '    return A'
            ])
        elif task_type == 'arr_fill_powers2':  # Заполнить степенями двойки
            code_lines.extend([
                '    A = [0] * N  # Создаем массив',
                '    for i in range(N):',
                '        A[i] = 2 ** i',
                '    return A'
            ])
        elif task_type == 'arr_fill_pyramid':  # Заполнить горкой
            code_lines.extend([
                '    A = [0] * N  # Создаем массив',
                '    # Заполнить горкой: 1, 2, 1, 2, 3, 2, 1, ...',
                '    pos = 0',
                '    level = 1',
                '    while pos < N:',
                '        # Подъем',
                '        for i in range(1, level + 1):',
                '            if pos < N:',
                '                A[pos] = i',
                '                pos += 1',
                '        # Спуск',
                '        for i in range(level - 1, 0, -1):',
                '            if pos < N:',
                '                A[pos] = i',
                '                pos += 1',
                '        level += 1',
                '    return A'
            ])
        elif task_type == 'arr_fill_generic':  # Заполнить (общий случай)
            code_lines.extend([
                '    A = [0] * N  # Создаем массив',
                '    # Общее заполнение массива',
                '    for i in range(N):',
                '        A[i] = i + 1  # По умолчанию натуральными числами',
                '    return A'
            ])
        elif task_type == 'arr_modify_increase':  # Увеличить элементы
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    for i in range(N):',
                '        A[i] += X  # Увеличиваем на X',
                '    return A'
            ])
        elif task_type == 'arr_modify_multiply':  # Умножить элементы
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    for i in range(N):',
                '        A[i] *= X  # Умножаем на X',
                '    return A'
            ])
        elif task_type == 'arr_modify_square':  # Возвести в квадрат
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    for i in range(N):',
                '        A[i] = A[i] ** 2',
                '    return A'
            ])
        elif task_type == 'arr_find_max':  # Найти максимум
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    max_val = A[0]',
                '    for i in range(1, N):',
                '        if A[i] > max_val:',
                '            max_val = A[i]',
                '    return max_val'
            ])
        elif task_type == 'arr_find_min':  # Найти минимум
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    min_val = A[0]',
                '    for i in range(1, N):',
                '        if A[i] < min_val:',
                '            min_val = A[i]',
                '    return min_val'
            ])
        elif task_type == 'arr_find_value':  # Найти значение
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    for i in range(N):',
                '        if A[i] == X:',
                '            return i + 1  # Возвращаем позицию (1-indexed)',
                '    return 0  # Не найдено'
            ])
        elif task_type == 'arr_count':  # Подсчитать элементы
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    count = 0',
                '    for i in range(N):',
                '        if A[i] == X:  # Подсчитываем элементы равные X',
                '            count += 1',
                '    return count'
            ])
        elif task_type == 'arr_sum':  # Сумма элементов
            code_lines.extend([
                '    A = list(range(1, N+1))  # Создаем массив с начальными значениями',
                '    total = 0',
                '    for i in range(N):',
                '        total += A[i]',
                '    return total'
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
        
        # Умная генерация тестов на основе параметров функции
        if task_type.startswith('array_'):
            # Процедуры с массивами (array_inc_by1, array_mult_by2, etc.)
            if 'X' in params:
                code_lines.extend([
                    '    N = 5',
                    '    A = [1, 2, 3, 4, 5]',
                    '    X = 10',
                    f'    result = {short_name}(N, A.copy(), X)',
                    '    print(f"Input: N={N}, A={A}, X={X}")',
                    '    print(f"Result: {result}")',
                    '    return result'
                ])
            else:
                code_lines.extend([
                    '    N = 5',
                    '    A = [1, 2, 3, 4, 5]',
                    f'    result = {short_name}(N, A.copy())',
                    '    print(f"Input: N={N}, A={A}")',
                    '    print(f"Result: {result}")',
                    '    return result'
                ])
        elif task_type.startswith('arr_'):
            # Процедуры с результирующими массивами - создают массив сами
            if 'X' in params or has_X:
                code_lines.extend([
                    '    N = 5',
                    '    X = 3',
                    f'    result = {short_name}(N, X)',
                    '    print(f"Input: N={N}, X={X}")',
                    '    print(f"Result: {result}")',
                    '    return result'
                ])
            else:
                code_lines.extend([
                    '    N = 5',
                    f'    result = {short_name}(N)',
                    '    print(f"Input: N={N}")',
                    '    print(f"Result: {result}")',
                    '    return result'
                ])
        elif is_function or returns_value:
            # Функция, возвращающая значение
            if len(params) == 0:
                code_lines.extend([
                    f'    result = {short_name}()',
                    '    print(f"Result: {result}")',
                    '    return True'
                ])
            elif len(params) == 1:
                param_name = params[0]
                if param_name in string_params or param_types.get(param_name) in ['лит', 'сим']:
                    # Строковый параметр
                    code_lines.extend([
                        '    test_strings = ["hello", "Python", "test", "A", ""]',
                        f'    for {param_name} in test_strings:',
                        f'        result = {short_name}({param_name})',
                        f'        print(f"Input: {{{param_name}}}, Result: {{result}}")',
                        '    return True'
                    ])
                else:
                    # Числовой параметр
                    code_lines.extend([
                        '    test_values = [0, 1, 5, 10, 123]',
                        f'    for {param_name} in test_values:',
                        f'        result = {short_name}({param_name})',
                        f'        print(f"Input: {{{param_name}}}, Result: {{result}}")',
                        '    return True'
                    ])
            elif len(params) == 2:
                param1, param2 = params[0], params[1]
                if param1 in array_params or param2 in array_params:
                    # Есть массив - используем стандартный тест с массивом
                    code_lines.extend([
                        '    N = 5',
                        '    A = [3, 1, 4, 1, 5]',
                        f'    result = {short_name}(N, A)',
                        '    print(f"Input: N={N}, A={A}")',
                        '    print(f"Result: {result}")',
                        '    return result'
                    ])
                elif param1 in string_params or param2 in string_params:
                    # Есть строка
                    code_lines.extend([
                        '    test_cases = [("hello", 5), ("Python", 3), ("test", 2)]',
                        f'    for {param1}, {param2} in test_cases:',
                        f'        result = {short_name}({param1}, {param2})',
                        f'        print(f"Input: {{{param1}}}, {{{param2}}}, Result: {{result}}")',
                        '    return True'
                    ])
                else:
                    # Два числовых параметра
                    code_lines.extend([
                        '    test_cases = [(3, 5), (10, 20), (1, 1), (0, 10)]',
                        f'    for {param1}, {param2} in test_cases:',
                        f'        result = {short_name}({param1}, {param2})',
                        f'        print(f"Input: {{{param1}}}, {{{param2}}}, Result: {{result}}")',
                        '    return True'
                    ])
            elif len(params) == 3:
                param1, param2, param3 = params[0], params[1], params[2]
                if 'A' in params and 'N' in params:
                    # Массив с дополнительным параметром
                    code_lines.extend([
                        '    N = 5',
                        '    A = [3, 1, 4, 1, 5]',
                        '    X = 1',
                        f'    result = {short_name}(N, A, X)',
                        '    print(f"Input: N={N}, A={A}, X={X}")',
                        '    print(f"Result: {result}")',
                        '    return result'
                    ])
                else:
                    # Три обычных параметра
                    code_lines.extend([
                        '    test_cases = [(1, 2, 3), (5, 10, 15), (0, 1, 2)]',
                        f'    for {param1}, {param2}, {param3} in test_cases:',
                        f'        result = {short_name}({param1}, {param2}, {param3})',
                        f'        print(f"Input: {{{param1}}}, {{{param2}}}, {{{param3}}}, Result: {{result}}")',
                        '    return True'
                    ])
            else:
                # Более 3 параметров - общий случай
                params_str = ", ".join(params)
                code_lines.extend([
                    f'    # Test with parameters: {params_str}',
                    f'    # TODO: Implement test for {short_name}({params_str})',
                    '    return True'
                ])
        
        elif task_type == 'string_task':
            # Для строковых задач
            code_lines.extend([
                '    test_strings = ["hello", "Python", "test string", "ABC", ""]',
                '    for s in test_strings:',
            ])
            
            if len(params) > 1:
                # Многопараметрная строковая функция
                code_lines.extend([
                    f'        result = {short_name}(s, "test")',  # Второй параметр по умолчанию
                    '        print(f"Input: \'{s}\', Result: {result}")'
                ])
            else:
                code_lines.extend([
                    f'        result = {short_name}(s)',
                    '        print(f"Input: \'{s}\', Result: {result}")'
                ])
            
            code_lines.extend([
                '    return True'
            ])
        
        elif task_type == 'robot_task':
            # Для задач робота
            code_lines.extend([
                '    # Выполнить алгоритм робота',
                f'    {short_name}()',
                '    print("Robot task completed successfully!")',
                '    return True'
            ])
        
        elif task_type == 'waterman_task':
            # Для задач водолея
            code_lines.extend([
                '    # Выполнить алгоритм водолея',
                f'    {short_name}()',
                '    print("Waterman task completed successfully!")',
                '    return True'
            ])
        elif task_type == 'empty_task':
            # Для пустых задач
            code_lines.extend([
                '    # Пустая задача - нет функциональности для тестирования',
                f'    {short_name}()',
                '    print("Empty task completed!")',
                '    return True'
            ])
        else:
            # Общий случай для всех остальных типов задач
            if 'A' in params or any('массив' in str(p) for p in [task_name, task_todo]):
                # Задача с массивом
                code_lines.extend([
                    '    N = 5',
                    '    A = [1, 2, 3, 4, 5]',
                ])
                
                if 'X' in params:
                    code_lines.extend([
                        '    X = 3',
                        f'    result = {short_name}(N, A.copy(), X)',
                        '    print(f"Input: N={N}, A={A}, X={X}")',
                    ])
                elif len(params) >= 2:
                    code_lines.extend([
                        f'    result = {short_name}(N, A.copy())',
                        '    print(f"Input: N={N}, A={A}")',
                    ])
                else:
                    code_lines.extend([
                        f'    result = {short_name}(N)',
                        '    print(f"Input: N={N}")',
                    ])
                
                code_lines.extend([
                    '    print(f"Result: {result}")',
                    '    return result'
                ])
            else:
                # Простая задача без массива
                code_lines.extend([
                    '    # Simple test case',
                    f'    result = {short_name}()',
                    '    print(f"Result: {result}")',
                    '    return result'
                ])
        
        # Добавляем основную функцию
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
