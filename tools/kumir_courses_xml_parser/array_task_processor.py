#!/usr/bin/env python3
"""
Специализированный процессор для задач на массивы.

Обрабатывает задачи, связанные с массивами:
- Заполнение массивов
- Поиск в массивах
- Сортировка массивов
- Операции над массивами
- Процедуры с массивами
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class ArrayTaskProcessor:
    """Процессор для задач на массивы."""
    
    def __init__(self):
        """Инициализация процессора массивов."""
        self.array_operations = {
            'fill_zeros': self._generate_fill_zeros,
            'fill_ones': self._generate_fill_ones,
            'fill_natural': self._generate_fill_natural,
            'fill_reverse': self._generate_fill_reverse,
            'reverse': self._generate_reverse,
            'shift_left': self._generate_shift_left,
            'shift_right': self._generate_shift_right,
            'sort_asc': self._generate_sort_ascending,
            'sort_desc': self._generate_sort_descending,
            'search_element': self._generate_search_element,
            'count_elements': self._generate_count_elements,
            'sum_elements': self._generate_sum_elements,
            'find_max': self._generate_find_max,
            'find_min': self._generate_find_min,
            'multiply_by_x': self._generate_multiply_by_x,
            'increment_by_x': self._generate_increment_by_x,
            'square_elements': self._generate_square_elements,
        }
    
    def process_tasks(self, tasks: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает список задач на массивы.
        
        Args:
            tasks: Список задач на массивы
            output_dir: Выходная директория
              Returns:
            Результаты обработки
        """
        results = {
            'processor_type': 'array',
            'total_tasks': len(tasks),
            'processed_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'files_created': {
                'py_files': 0,
                'kum_files': 0
            },
            'generated_files': {
                'python': [],
                'kumir': []
            },
            'task_details': [],
            'errors': []
        }
          # Создаем поддиректории
        py_dir = output_dir / "py" / "arrays"
        kum_dir = output_dir / "kum" / "arrays"
        py_dir.mkdir(parents=True, exist_ok=True)
        kum_dir.mkdir(parents=True, exist_ok=True)
        
        for i, task in enumerate(tasks, 1):
            try:
                task_result = self.process_single_task(task, i, py_dir, kum_dir)
                results['task_details'].append(task_result)
                results['processed_tasks'] += 1
                results['successful_tasks'] += 1
                
                if task_result['python_file']:
                    results['generated_files']['python'].append(task_result['python_file'])
                    results['files_created']['py_files'] += 1
                if task_result['kumir_file']:
                    results['generated_files']['kumir'].append(task_result['kumir_file'])
                    results['files_created']['kum_files'] += 1
                    
            except Exception as e:
                results['failed_tasks'] += 1
                error_msg = f"Ошибка при обработке задачи {i}: {str(e)}"
                results['errors'].append(error_msg)
                error_details = {
                    'task_id': f"array_{i}",
                    'error': str(e),
                    'title': task.get('title', 'Без названия')
                }
                results['task_details'].append(error_details)
        
        return results
    
    def process_single_task(self, task: Dict[str, Any], task_num: int, py_dir: Path, kum_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает одну задачу на массивы.
        
        Args:
            task: Данные задачи
            task_num: Номер задачи
            py_dir: Директория для Python файлов
            kum_dir: Директория для KUM файлов
            
        Returns:
            Результат обработки задачи
        """
        # Анализируем тип операции с массивом
        operation_type = self._detect_array_operation(task)
        
        # Генерируем базовое имя файла
        base_name = f"arr_{task_num:02d}_{operation_type}"
        
        # Генерируем Python код
        python_code = self._generate_python_solution(task, operation_type)
        python_file = py_dir / f"{base_name}.py"
        
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        # Сохраняем KUM код
        kumir_code = task.get('student_code', '')
        kumir_file = kum_dir / f"{base_name}.kum"
        
        with open(kumir_file, 'w', encoding='utf-8') as f:
            f.write(kumir_code)
        
        return {
            'task_id': base_name,
            'title': task.get('title', 'Массив'),
            'operation_type': operation_type,
            'python_file': str(python_file.relative_to(py_dir.parent.parent)),
            'kumir_file': str(kumir_file.relative_to(kum_dir.parent.parent)),
            'status': 'success'
        }
    
    def _detect_array_operation(self, task: Dict[str, Any]) -> str:
        """Определяет тип операции с массивом."""
        
        title = task.get('title', '').lower()
        code = task.get('student_code', '').lower()
        combined_text = f"{title} {code}"
        
        # Паттерны для определения операций
        if any(pattern in combined_text for pattern in ['заполни нулями', 'заполнить нулями', 'нули']):
            return 'fill_zeros'
        elif any(pattern in combined_text for pattern in ['заполни единицами', 'заполнить единицами', 'единицы']):
            return 'fill_ones'
        elif any(pattern in combined_text for pattern in ['натуральными числами', 'последовательно', '1,2,3']):
            return 'fill_natural'
        elif any(pattern in combined_text for pattern in ['обратный порядок', 'переверни', 'реверс']):
            return 'reverse'
        elif any(pattern in combined_text for pattern in ['сдвиг влево', 'сдвинь влево']):
            return 'shift_left'
        elif any(pattern in combined_text for pattern in ['сдвиг вправо', 'сдвинь вправо']):
            return 'shift_right'
        elif any(pattern in combined_text for pattern in ['сортировка', 'отсортируй', 'упорядочи']):
            if 'убыван' in combined_text:
                return 'sort_desc'
            else:
                return 'sort_asc'
        elif any(pattern in combined_text for pattern in ['найди', 'поиск', 'ищи']):
            return 'search_element'
        elif any(pattern in combined_text for pattern in ['посчитай', 'количество', 'сколько']):
            return 'count_elements'
        elif any(pattern in combined_text for pattern in ['сумма', 'суммируй']):
            return 'sum_elements'
        elif any(pattern in combined_text for pattern in ['максимум', 'наибольший', 'max']):
            return 'find_max'
        elif any(pattern in combined_text for pattern in ['минимум', 'наименьший', 'min']):
            return 'find_min'
        elif any(pattern in combined_text for pattern in ['умножь', 'произведение']):
            return 'multiply_by_x'
        elif any(pattern in combined_text for pattern in ['увеличь', 'прибавь', 'добавь']):
            return 'increment_by_x'
        elif any(pattern in combined_text for pattern in ['квадрат', 'возведи в степень']):
            return 'square_elements'
        else:
            return 'generic_array'
    
    def _generate_python_solution(self, task: Dict[str, Any], operation_type: str) -> str:
        """Генерирует Python решение для задачи на массивы."""
        
        if operation_type in self.array_operations:
            return self.array_operations[operation_type](task)
        else:
            return self._generate_generic_array_solution(task)
    
    def _generate_fill_zeros(self, task: Dict[str, Any]) -> str:
        """Генерирует код заполнения массива нулями."""
        return '''#!/usr/bin/env python3
"""
Заполнение массива нулями.
"""

def fill_array_with_zeros(size):
    """Заполняет массив нулями."""
    return [0] * size

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Создаем и заполняем массив
    arr = fill_array_with_zeros(n)
    
    # Выводим результат
    print("Массив заполнен нулями:")
    print(" ".join(map(str, arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_fill_ones(self, task: Dict[str, Any]) -> str:
        """Генерирует код заполнения массива единицами."""
        return '''#!/usr/bin/env python3
"""
Заполнение массива единицами.
"""

def fill_array_with_ones(size):
    """Заполняет массив единицами."""
    return [1] * size

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Создаем и заполняем массив
    arr = fill_array_with_ones(n)
    
    # Выводим результат
    print("Массив заполнен единицами:")
    print(" ".join(map(str, arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_fill_natural(self, task: Dict[str, Any]) -> str:
        """Генерирует код заполнения массива натуральными числами."""
        return '''#!/usr/bin/env python3
"""
Заполнение массива натуральными числами (1, 2, 3, ...).
"""

def fill_array_with_natural(size):
    """Заполняет массив натуральными числами."""
    return list(range(1, size + 1))

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Создаем и заполняем массив
    arr = fill_array_with_natural(n)
    
    # Выводим результат
    print("Массив заполнен натуральными числами:")
    print(" ".join(map(str, arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_fill_reverse(self, task: Dict[str, Any]) -> str:
        """Генерирует код заполнения массива в обратном порядке."""
        return '''#!/usr/bin/env python3
"""
Заполнение массива в обратном порядке.
"""

def fill_array_reverse(size):
    """Заполняет массив числами в обратном порядке."""
    return list(range(size, 0, -1))

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Создаем и заполняем массив
    arr = fill_array_reverse(n)
    
    # Выводим результат
    print("Массив заполнен в обратном порядке:")
    print(" ".join(map(str, arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_reverse(self, task: Dict[str, Any]) -> str:
        """Генерирует код для обращения массива."""
        return '''#!/usr/bin/env python3
"""
Обращение массива (переворот в обратном порядке).
"""

def reverse_array(arr):
    """Переворачивает массив."""
    return arr[::-1]

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Переворачиваем массив
    reversed_arr = reverse_array(arr)
    
    # Выводим результат
    print("Обращенный массив:")
    print(" ".join(map(str, reversed_arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_shift_left(self, task: Dict[str, Any]) -> str:
        """Генерирует код сдвига массива влево."""
        return '''#!/usr/bin/env python3
"""
Сдвиг массива влево на одну позицию.
"""

def shift_array_left(arr):
    """Сдвигает массив влево на одну позицию."""
    if len(arr) <= 1:
        return arr
    return arr[1:] + [arr[0]]

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Сдвигаем массив влево
    shifted_arr = shift_array_left(arr)
    
    # Выводим результат
    print("Массив после сдвига влево:")
    print(" ".join(map(str, shifted_arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_shift_right(self, task: Dict[str, Any]) -> str:
        """Генерирует код сдвига массива вправо."""
        return '''#!/usr/bin/env python3
"""
Сдвиг массива вправо на одну позицию.
"""

def shift_array_right(arr):
    """Сдвигает массив вправо на одну позицию."""
    if len(arr) <= 1:
        return arr
    return [arr[-1]] + arr[:-1]

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Сдвигаем массив вправо
    shifted_arr = shift_array_right(arr)
    
    # Выводим результат
    print("Массив после сдвига вправо:")
    print(" ".join(map(str, shifted_arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_sort_ascending(self, task: Dict[str, Any]) -> str:
        """Генерирует код сортировки по возрастанию."""
        return '''#!/usr/bin/env python3
"""
Сортировка массива по возрастанию.
"""

def sort_array_ascending(arr):
    """Сортирует массив по возрастанию."""
    return sorted(arr)

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Сортируем массив
    sorted_arr = sort_array_ascending(arr)
    
    # Выводим результат
    print("Отсортированный массив:")
    print(" ".join(map(str, sorted_arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_sort_descending(self, task: Dict[str, Any]) -> str:
        """Генерирует код сортировки по убыванию."""
        return '''#!/usr/bin/env python3
"""
Сортировка массива по убыванию.
"""

def sort_array_descending(arr):
    """Сортирует массив по убыванию."""
    return sorted(arr, reverse=True)

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Сортируем массив
    sorted_arr = sort_array_descending(arr)
    
    # Выводим результат
    print("Отсортированный массив по убыванию:")
    print(" ".join(map(str, sorted_arr)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_search_element(self, task: Dict[str, Any]) -> str:
        """Генерирует код поиска элемента."""
        return '''#!/usr/bin/env python3
"""
Поиск элемента в массиве.
"""

def search_element(arr, target):
    """Ищет элемент в массиве и возвращает его индекс."""
    try:
        return arr.index(target)
    except ValueError:
        return -1  # Элемент не найден

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Читаем искомый элемент
    target = int(input("Введите искомый элемент: "))
    
    # Ищем элемент
    index = search_element(arr, target)
    
    # Выводим результат
    if index != -1:
        print(f"Элемент {target} найден на позиции {index + 1}")
    else:
        print(f"Элемент {target} не найден")

if __name__ == "__main__":
    main()
'''
    
    def _generate_sum_elements(self, task: Dict[str, Any]) -> str:
        """Генерирует код суммирования элементов."""
        return '''#!/usr/bin/env python3
"""
Суммирование элементов массива.
"""

def sum_array_elements(arr):
    """Вычисляет сумму элементов массива."""
    return sum(arr)

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Вычисляем сумму
    total = sum_array_elements(arr)
    
    # Выводим результат
    print(f"Сумма элементов массива: {total}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_find_max(self, task: Dict[str, Any]) -> str:
        """Генерирует код поиска максимума."""
        return '''#!/usr/bin/env python3
"""
Поиск максимального элемента в массиве.
"""

def find_max_element(arr):
    """Находит максимальный элемент в массиве."""
    return max(arr) if arr else None

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Находим максимум
    max_element = find_max_element(arr)
    
    # Выводим результат
    print(f"Максимальный элемент: {max_element}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_find_min(self, task: Dict[str, Any]) -> str:
        """Генерирует код поиска минимума."""
        return '''#!/usr/bin/env python3
"""
Поиск минимального элемента в массиве.
"""

def find_min_element(arr):
    """Находит минимальный элемент в массиве."""
    return min(arr) if arr else None

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Находим минимум
    min_element = find_min_element(arr)
    
    # Выводим результат
    print(f"Минимальный элемент: {min_element}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_multiply_by_x(self, task: Dict[str, Any]) -> str:
        """Генерирует код умножения на число."""
        return '''#!/usr/bin/env python3
"""
Умножение всех элементов массива на число.
"""

def multiply_array_by_x(arr, x):
    """Умножает все элементы массива на число x."""
    return [element * x for element in arr]

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Читаем множитель
    x = int(input("Введите число для умножения: "))
    
    # Умножаем элементы
    result = multiply_array_by_x(arr, x)
    
    # Выводим результат
    print(f"Массив после умножения на {x}:")
    print(" ".join(map(str, result)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_increment_by_x(self, task: Dict[str, Any]) -> str:
        """Генерирует код увеличения на число."""
        return '''#!/usr/bin/env python3
"""
Увеличение всех элементов массива на число.
"""

def increment_array_by_x(arr, x):
    """Увеличивает все элементы массива на число x."""
    return [element + x for element in arr]

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Читаем добавку
    x = int(input("Введите число для увеличения: "))
    
    # Увеличиваем элементы
    result = increment_array_by_x(arr, x)
    
    # Выводим результат
    print(f"Массив после увеличения на {x}:")
    print(" ".join(map(str, result)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_square_elements(self, task: Dict[str, Any]) -> str:
        """Генерирует код возведения в квадрат."""
        return '''#!/usr/bin/env python3
"""
Возведение всех элементов массива в квадрат.
"""

def square_array_elements(arr):
    """Возводит все элементы массива в квадрат."""
    return [element ** 2 for element in arr]

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Возводим в квадрат
    result = square_array_elements(arr)
    
    # Выводим результат
    print("Массив после возведения в квадрат:")
    print(" ".join(map(str, result)))

if __name__ == "__main__":
    main()
'''
    
    def _generate_count_elements(self, task: Dict[str, Any]) -> str:
        """Генерирует код подсчета элементов."""
        return '''#!/usr/bin/env python3
"""
Подсчет элементов массива по условию.
"""

def count_elements_by_condition(arr, condition_func):
    """Подсчитывает элементы массива, удовлетворяющие условию."""
    return sum(1 for element in arr if condition_func(element))

def count_positive(arr):
    """Подсчитывает положительные элементы."""
    return count_elements_by_condition(arr, lambda x: x > 0)

def count_even(arr):
    """Подсчитывает четные элементы."""
    return count_elements_by_condition(arr, lambda x: x % 2 == 0)

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Подсчитываем элементы по разным условиям
    positive_count = count_positive(arr)
    even_count = count_even(arr)
    
    # Выводим результат
    print(f"Положительных элементов: {positive_count}")
    print(f"Четных элементов: {even_count}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_generic_array_solution(self, task: Dict[str, Any]) -> str:
        """Генерирует общее решение для массива."""
        return '''#!/usr/bin/env python3
"""
Общая задача с массивом.
"""

def process_array(arr):
    """Обрабатывает массив согласно условию задачи."""
    # Здесь должна быть логика согласно условию
    return arr

def main():
    # Читаем размер массива
    n = int(input("Введите размер массива: "))
    
    # Читаем элементы массива
    print("Введите элементы массива:")
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    # Обрабатываем массив
    result = process_array(arr)
    
    # Выводим результат
    print("Результат обработки массива:")
    print(" ".join(map(str, result)))

if __name__ == "__main__":
    main()
'''
