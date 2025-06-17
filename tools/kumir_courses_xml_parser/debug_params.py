#!/usr/bin/env python3
"""
Отладка парсинга параметров
"""

import re

def parse_params_debug(task_name):
    """Отладка парсинга параметров."""
    print(f"Парсим: {task_name}")
    
    params = []
    param_types = {}
    array_params = set()
    string_params = set()
    
    # Ищем содержимое в скобках и разбираем
    paren_match = re.search(r'\(([^)]+)\)', task_name)
    print(f"Скобки найдены: {paren_match.group(1) if paren_match else 'НЕТ'}")
    
    if paren_match:
        content = paren_match.group(1)
        # Разделяем по запятым и ищем переменные
        parts = [p.strip() for p in content.split(',')]
        print(f"Части: {parts}")
        
        for part in parts:
            print(f"  Обрабатываем часть: '{part}'")
            
            # Попробуем сначала найти полные конструкции типа "аргрез цел X" или "арг лит Y"
            if re.match(r'аргрез\s+(цел|вещ|лог|лит)таб\s+[A-Z][a-zA-Z0-9]*', part):
                print(f"    Массив: {part}")
                continue  # Будет обработано ниже
            elif re.match(r'арг\s+(цел|вещ|лог|лит)\s+[A-Z][a-zA-Z0-9]*', part):
                print(f"    Арг: {part}")
                continue  # Будет обработано ниже
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
                    print(f"    Простой тип: {var_type} {var_name}")
                else:
                    # Последняя попытка - просто переменная в конце
                    var_match = re.search(r'([a-zA-Z][a-zA-Z0-9]*)$', part.strip())
                    if var_match:
                        params.append(var_match.group(1))
                        print(f"    Просто переменная: {var_match.group(1)}")
    
    # Если ничего не найдено, пробуем альтернативные методы
    if not params:
        print("Пробуем альтернативные методы...")
        
        # Второй вариант: поиск арг конструкций (включая массивы)
        array_param_matches = re.findall(r'аргрез\s+(?:цел|вещ|лог|лит)таб\s+([A-Z][a-zA-Z0-9]*)', task_name)
        if array_param_matches:
            params.extend(array_param_matches)
            print(f"  Найдены параметры массивов: {array_param_matches}")
        
        # Ищем обычные параметры: арг цел X, арг лит S, etc.
        param_matches = re.findall(r'арг\s+(?:цел|вещ|лит|лог)\s+([A-Z][a-zA-Z0-9]*)', task_name)
        if param_matches:
            params.extend(param_matches)
            print(f"  Найдены арг параметры: {param_matches}")
    
    print(f"Итого параметров: {params}")
    print(f"Строковые параметры: {string_params}")
    print(f"Типы параметров: {param_types}")
    print("-" * 50)
    
    return params, string_params, param_types

# Тестируем
test_cases = [
    "сим Первый символ (лит s)",
    "Первый 0(аргрез лит s)",
    "цел Функция (арг цел X, арг лит Y)",
    "лог Проверка (арг цел A, арг вещ B)",
    "Обработка (аргрез целтаб A, арг цел N)"
]

for test_case in test_cases:
    parse_params_debug(test_case)
