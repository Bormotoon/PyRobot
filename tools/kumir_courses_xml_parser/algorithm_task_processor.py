#!/usr/bin/env python3
"""
Специализированный процессор для алгоритмических задач.

Обрабатывает задачи общего характера:
- Циклы и условия
- Ввод-вывод
- Базовые алгоритмы
- Математические вычисления
"""

from pathlib import Path
from typing import List, Dict, Any


class AlgorithmTaskProcessor:
    """Процессор для алгоритмических задач."""
    
    def __init__(self):
        """Инициализация процессора алгоритмов."""
        self.algorithm_types = {
            'input_output': self._generate_input_output,
            'loops': self._generate_loops,
            'conditions': self._generate_conditions,
            'calculations': self._generate_calculations,
            'sorting': self._generate_sorting,
            'searching': self._generate_searching,
            'number_theory': self._generate_number_theory,
        }
    
    def process_tasks(self, tasks: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает список алгоритмических задач.
        
        Args:
            tasks: Список алгоритмических задач
            output_dir: Выходная директория
            
        Returns:
            Результаты обработки
        """
        results = {
            'processor_type': 'algorithm',
            'total_tasks': len(tasks),
            'processed_tasks': 0,
            'generated_files': {
                'python': [],
                'kumir': []
            },
            'task_details': []
        }
        
        # Создаем поддиректории
        py_dir = output_dir / "py" / "algorithms"
        kum_dir = output_dir / "kum" / "algorithms"
        py_dir.mkdir(parents=True, exist_ok=True)
        kum_dir.mkdir(parents=True, exist_ok=True)
        
        for i, task in enumerate(tasks, 1):
            try:
                task_result = self.process_single_task(task, i, py_dir, kum_dir)
                results['task_details'].append(task_result)
                results['processed_tasks'] += 1
                
                if task_result['python_file']:
                    results['generated_files']['python'].append(task_result['python_file'])
                if task_result['kumir_file']:
                    results['generated_files']['kumir'].append(task_result['kumir_file'])
                    
            except Exception as e:
                error_details = {
                    'task_id': f"alg_{i}",
                    'error': str(e),
                    'title': task.get('title', 'Без названия')
                }
                results['task_details'].append(error_details)
        
        return results
    
    def process_single_task(self, task: Dict[str, Any], task_num: int, py_dir: Path, kum_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает одну алгоритмическую задачу.
        
        Args:
            task: Данные задачи
            task_num: Номер задачи
            py_dir: Директория для Python файлов
            kum_dir: Директория для KUM файлов
            
        Returns:
            Результат обработки задачи
        """
        # Анализируем тип алгоритма
        algorithm_type = self._detect_algorithm_type(task)
        
        # Генерируем базовое имя файла
        base_name = f"alg_{task_num:02d}_{algorithm_type}"
        
        # Генерируем Python код
        python_code = self._generate_python_solution(task, algorithm_type)
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
            'title': task.get('title', 'Алгоритм'),
            'algorithm_type': algorithm_type,
            'python_file': str(python_file.relative_to(py_dir.parent.parent)),
            'kumir_file': str(kumir_file.relative_to(kum_dir.parent.parent)),
            'status': 'success'
        }
    
    def _detect_algorithm_type(self, task: Dict[str, Any]) -> str:
        """Определяет тип алгоритма."""
        
        title = task.get('title', '').lower()
        code = task.get('student_code', '').lower()
        combined_text = f"{title} {code}"
        
        # Паттерны для определения типов алгоритмов
        if any(pattern in combined_text for pattern in ['ввод', 'вывод', 'input', 'output', 'print']):
            return 'input_output'
        elif any(pattern in combined_text for pattern in ['цикл', 'нц', 'кц', 'loop', 'for', 'while']):
            return 'loops'
        elif any(pattern in combined_text for pattern in ['если', 'то', 'иначе', 'if', 'else', 'условие']):
            return 'conditions'
        elif any(pattern in combined_text for pattern in ['сортировка', 'sort', 'упорядочить']):
            return 'sorting'
        elif any(pattern in combined_text for pattern in ['поиск', 'найти', 'search', 'find']):
            return 'searching'
        elif any(pattern in combined_text for pattern in ['простое число', 'факториал', 'НОД', 'НОК']):
            return 'number_theory'
        elif any(pattern in combined_text for pattern in ['вычислить', 'формула', 'calculate']):
            return 'calculations'
        else:
            return 'generic_algorithm'
    
    def _generate_python_solution(self, task: Dict[str, Any], algorithm_type: str) -> str:
        """Генерирует Python решение для алгоритмической задачи."""
        
        if algorithm_type in self.algorithm_types:
            return self.algorithm_types[algorithm_type](task)
        else:
            return self._generate_generic_algorithm_solution(task)
    
    def _generate_input_output(self, task: Dict[str, Any]) -> str:
        """Генерирует код ввода-вывода."""
        return '''#!/usr/bin/env python3
"""
Задача на ввод-вывод данных.
"""

def process_input_output():
    """Обрабатывает ввод и вывод данных."""
    # Ввод одного числа
    n = int(input("Введите число: "))
    print(f"Вы ввели число: {n}")
    
    # Ввод нескольких чисел
    print("Введите два числа через пробел:")
    a, b = map(int, input().split())
    print(f"Первое число: {a}, второе число: {b}")
    
    # Ввод строки
    text = input("Введите текст: ")
    print(f"Вы ввели: {text}")
    
    # Ввод последовательности чисел
    count = int(input("Сколько чисел введете: "))
    numbers = []
    for i in range(count):
        num = int(input(f"Число {i+1}: "))
        numbers.append(num)
    
    print("Введенные числа:", numbers)
    
    # Вывод в разных форматах
    print(f"Сумма: {sum(numbers)}")
    print(f"Среднее: {sum(numbers) / len(numbers) if numbers else 0:.2f}")
    print("Числа в обратном порядке:", numbers[::-1])

def main():
    print("Демонстрация ввода-вывода")
    process_input_output()

if __name__ == "__main__":
    main()
'''
    
    def _generate_loops(self, task: Dict[str, Any]) -> str:
        """Генерирует код с циклами."""
        return '''#!/usr/bin/env python3
"""
Задача с использованием циклов.
"""

def demonstrate_for_loop():
    """Демонстрация цикла for."""
    print("Цикл for от 1 до 10:")
    for i in range(1, 11):
        print(f"i = {i}")
    
    print("\\nЦикл for с шагом 2:")
    for i in range(0, 21, 2):
        print(f"Четное число: {i}")

def demonstrate_while_loop():
    """Демонстрация цикла while."""
    print("\\nЦикл while для подсчета суммы:")
    n = int(input("Введите число для суммы от 1 до n: "))
    
    i = 1
    total = 0
    while i <= n:
        total += i
        i += 1
    
    print(f"Сумма от 1 до {n} = {total}")

def nested_loops_example():
    """Пример вложенных циклов."""
    print("\\nТаблица умножения (фрагмент):")
    for i in range(1, 6):
        for j in range(1, 6):
            print(f"{i * j:3d}", end=" ")
        print()  # Новая строка

def loop_with_conditions():
    """Цикл с условиями."""
    print("\\nПоиск простых чисел до 20:")
    for num in range(2, 21):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        
        if is_prime:
            print(f"{num} - простое число")

def sum_sequence():
    """Сумма последовательности с условием."""
    print("\\nВвод чисел до ввода 0:")
    total = 0
    count = 0
    
    while True:
        num = int(input("Введите число (0 для завершения): "))
        if num == 0:
            break
        total += num
        count += 1
    
    if count > 0:
        print(f"Сумма: {total}")
        print(f"Среднее: {total / count:.2f}")
        print(f"Количество чисел: {count}")
    else:
        print("Числа не были введены")

def main():
    print("Демонстрация различных типов циклов")
    
    demonstrate_for_loop()
    demonstrate_while_loop()
    nested_loops_example()
    loop_with_conditions()
    sum_sequence()

if __name__ == "__main__":
    main()
'''
    
    def _generate_conditions(self, task: Dict[str, Any]) -> str:
        """Генерирует код с условиями."""
        return '''#!/usr/bin/env python3
"""
Задача с использованием условных операторов.
"""

def simple_conditions():
    """Простые условия."""
    num = int(input("Введите число: "))
    
    if num > 0:
        print("Число положительное")
    elif num < 0:
        print("Число отрицательное")
    else:
        print("Число равно нулю")
    
    # Проверка четности
    if num % 2 == 0:
        print("Число четное")
    else:
        print("Число нечетное")

def complex_conditions():
    """Сложные условия."""
    age = int(input("Введите возраст: "))
    has_license = input("Есть ли водительские права? (да/нет): ").lower() == "да"
    
    if age >= 18 and has_license:
        print("Можно водить автомобиль")
    elif age >= 18 and not has_license:
        print("Нужно получить водительские права")
    else:
        print("Слишком молод для вождения")

def grade_evaluation():
    """Оценка по баллам."""
    score = int(input("Введите количество баллов (0-100): "))
    
    if score >= 90:
        grade = "Отлично"
    elif score >= 80:
        grade = "Хорошо"
    elif score >= 70:
        grade = "Удовлетворительно"
    elif score >= 60:
        grade = "Зачет"
    else:
        grade = "Незачет"
    
    print(f"Оценка: {grade}")

def triangle_type():
    """Определение типа треугольника."""
    print("Введите длины сторон треугольника:")
    a = float(input("Сторона a: "))
    b = float(input("Сторона b: "))
    c = float(input("Сторона c: "))
    
    # Проверка существования треугольника
    if a + b > c and a + c > b and b + c > a:
        print("Треугольник существует")
        
        # Определение типа
        if a == b == c:
            print("Равносторонний треугольник")
        elif a == b or b == c or a == c:
            print("Равнобедренный треугольник")
        else:
            print("Разносторонний треугольник")
        
        # Проверка на прямоугольность
        sides = sorted([a, b, c])
        if abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 0.001:
            print("Прямоугольный треугольник")
    else:
        print("Треугольник не существует")

def leap_year_check():
    """Проверка високосного года."""
    year = int(input("Введите год: "))
    
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                print(f"{year} - високосный год")
            else:
                print(f"{year} - не високосный год")
        else:
            print(f"{year} - високосный год")
    else:
        print(f"{year} - не високосный год")

def number_classification():
    """Классификация числа."""
    num = int(input("Введите целое число: "))
    
    print(f"Анализ числа {num}:")
    
    # Знак
    if num > 0:
        print("- положительное")
    elif num < 0:
        print("- отрицательное")
    else:
        print("- ноль")
    
    # Четность
    if num % 2 == 0:
        print("- четное")
    else:
        print("- нечетное")
    
    # Кратность 3
    if num % 3 == 0 and num != 0:
        print("- кратно 3")
    
    # Кратность 5
    if num % 5 == 0 and num != 0:
        print("- кратно 5")
    
    # Простое число
    if num > 1:
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        
        if is_prime:
            print("- простое число")
        else:
            print("- составное число")

def main():
    print("Демонстрация условных операторов")
    
    print("\\n1. Простые условия:")
    simple_conditions()
    
    print("\\n2. Сложные условия:")
    complex_conditions()
    
    print("\\n3. Оценка по баллам:")
    grade_evaluation()
    
    print("\\n4. Тип треугольника:")
    triangle_type()
    
    print("\\n5. Високосный год:")
    leap_year_check()
    
    print("\\n6. Классификация числа:")
    number_classification()

if __name__ == "__main__":
    main()
'''
    
    def _generate_calculations(self, task: Dict[str, Any]) -> str:
        """Генерирует код вычислений."""
        return '''#!/usr/bin/env python3
"""
Задача на математические вычисления.
"""

import math

def basic_calculations():
    """Базовые математические операции."""
    a = float(input("Введите первое число: "))
    b = float(input("Введите второе число: "))
    
    print(f"Сложение: {a} + {b} = {a + b}")
    print(f"Вычитание: {a} - {b} = {a - b}")
    print(f"Умножение: {a} * {b} = {a * b}")
    
    if b != 0:
        print(f"Деление: {a} / {b} = {a / b}")
        print(f"Целочисленное деление: {a} // {b} = {a // b}")
        print(f"Остаток от деления: {a} % {b} = {a % b}")
    else:
        print("Деление на ноль невозможно")
    
    print(f"Возведение в степень: {a} ^ {b} = {a ** b}")

def geometric_calculations():
    """Геометрические вычисления."""
    print("\\nВыберите фигуру:")
    print("1. Круг")
    print("2. Прямоугольник")
    print("3. Треугольник")
    
    choice = int(input("Ваш выбор: "))
    
    if choice == 1:
        radius = float(input("Введите радиус круга: "))
        area = math.pi * radius ** 2
        circumference = 2 * math.pi * radius
        print(f"Площадь круга: {area:.2f}")
        print(f"Длина окружности: {circumference:.2f}")
    
    elif choice == 2:
        length = float(input("Введите длину: "))
        width = float(input("Введите ширину: "))
        area = length * width
        perimeter = 2 * (length + width)
        print(f"Площадь прямоугольника: {area:.2f}")
        print(f"Периметр прямоугольника: {perimeter:.2f}")
    
    elif choice == 3:
        a = float(input("Введите первую сторону: "))
        b = float(input("Введите вторую сторону: "))
        c = float(input("Введите третью сторону: "))
        
        # Проверка существования треугольника
        if a + b > c and a + c > b and b + c > a:
            # Формула Герона
            s = (a + b + c) / 2
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
            perimeter = a + b + c
            print(f"Площадь треугольника: {area:.2f}")
            print(f"Периметр треугольника: {perimeter:.2f}")
        else:
            print("Треугольник с такими сторонами не существует")

def quadratic_equation():
    """Решение квадратного уравнения."""
    print("\\nРешение квадратного уравнения ax² + bx + c = 0")
    
    a = float(input("Введите коэффициент a: "))
    b = float(input("Введите коэффициент b: "))
    c = float(input("Введите коэффициент c: "))
    
    if a == 0:
        if b == 0:
            if c == 0:
                print("Любое число является решением")
            else:
                print("Уравнение не имеет решений")
        else:
            x = -c / b
            print(f"Линейное уравнение. Решение: x = {x}")
    else:
        discriminant = b**2 - 4*a*c
        print(f"Дискриминант: {discriminant}")
        
        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            print(f"Два различных корня: x1 = {x1:.2f}, x2 = {x2:.2f}")
        elif discriminant == 0:
            x = -b / (2*a)
            print(f"Один корень: x = {x:.2f}")
        else:
            real_part = -b / (2*a)
            imaginary_part = math.sqrt(-discriminant) / (2*a)
            print(f"Комплексные корни:")
            print(f"x1 = {real_part:.2f} + {imaginary_part:.2f}i")
            print(f"x2 = {real_part:.2f} - {imaginary_part:.2f}i")

def statistical_calculations():
    """Статистические вычисления."""
    print("\\nСтатистические вычисления")
    
    n = int(input("Введите количество чисел: "))
    numbers = []
    
    for i in range(n):
        num = float(input(f"Число {i+1}: "))
        numbers.append(num)
    
    if numbers:
        # Основные статистики
        total = sum(numbers)
        mean = total / len(numbers)
        maximum = max(numbers)
        minimum = min(numbers)
        
        # Медиана
        sorted_numbers = sorted(numbers)
        n = len(sorted_numbers)
        if n % 2 == 0:
            median = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
        else:
            median = sorted_numbers[n//2]
        
        # Дисперсия и стандартное отклонение
        variance = sum((x - mean)**2 for x in numbers) / len(numbers)
        std_dev = math.sqrt(variance)
        
        print(f"\\nРезультаты:")
        print(f"Сумма: {total:.2f}")
        print(f"Среднее арифметическое: {mean:.2f}")
        print(f"Медиана: {median:.2f}")
        print(f"Максимум: {maximum:.2f}")
        print(f"Минимум: {minimum:.2f}")
        print(f"Размах: {maximum - minimum:.2f}")
        print(f"Дисперсия: {variance:.2f}")
        print(f"Стандартное отклонение: {std_dev:.2f}")

def main():
    print("Математические вычисления")
    
    print("\\n1. Базовые операции:")
    basic_calculations()
    
    geometric_calculations()
    quadratic_equation()
    statistical_calculations()

if __name__ == "__main__":
    main()
'''
    
    def _generate_sorting(self, task: Dict[str, Any]) -> str:
        """Генерирует код сортировки."""
        return '''#!/usr/bin/env python3
"""
Алгоритмы сортировки.
"""

def bubble_sort(arr):
    """Сортировка пузырьком."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def selection_sort(arr):
    """Сортировка выбором."""
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def insertion_sort(arr):
    """Сортировка вставками."""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def quick_sort(arr):
    """Быстрая сортировка."""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

def merge_sort(arr):
    """Сортировка слиянием."""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """Слияние двух отсортированных массивов."""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def counting_sort(arr):
    """Сортировка подсчетом (для неотрицательных целых чисел)."""
    if not arr:
        return arr
    
    max_val = max(arr)
    count = [0] * (max_val + 1)
    
    # Подсчет вхождений
    for num in arr:
        count[num] += 1
    
    # Восстановление массива
    result = []
    for i in range(len(count)):
        result.extend([i] * count[i])
    
    return result

def demonstrate_sorting():
    """Демонстрация различных алгоритмов сортировки."""
    import random
    import time
    
    # Генерируем тестовые данные
    size = 20
    test_data = [random.randint(1, 100) for _ in range(size)]
    
    print(f"Исходный массив: {test_data}")
    print("\\nРезультаты сортировки различными алгоритмами:")
    
    algorithms = [
        ("Пузырьком", bubble_sort),
        ("Выбором", selection_sort),
        ("Вставками", insertion_sort),
        ("Быстрая", quick_sort),
        ("Слиянием", merge_sort),
        ("Подсчетом", counting_sort)
    ]
    
    for name, algorithm in algorithms:
        test_copy = test_data[:]
        start_time = time.time()
        sorted_array = algorithm(test_copy)
        end_time = time.time()
        
        print(f"{name:12}: {sorted_array[:10]}{'...' if len(sorted_array) > 10 else ''}")
        print(f"             Время: {(end_time - start_time)*1000:.2f} мс")

def custom_sort_demo():
    """Демонстрация пользовательской сортировки."""
    print("\\nПользовательский ввод для сортировки:")
    
    n = int(input("Введите количество элементов: "))
    arr = []
    
    for i in range(n):
        num = int(input(f"Элемент {i+1}: "))
        arr.append(num)
    
    print(f"\\nИсходный массив: {arr}")
    
    print("\\nВыберите алгоритм сортировки:")
    print("1. Пузырьком")
    print("2. Выбором") 
    print("3. Вставками")
    print("4. Быстрая сортировка")
    print("5. Встроенная сортировка Python")
    
    choice = int(input("Ваш выбор: "))
    
    if choice == 1:
        result = bubble_sort(arr[:])
    elif choice == 2:
        result = selection_sort(arr[:])
    elif choice == 3:
        result = insertion_sort(arr[:])
    elif choice == 4:
        result = quick_sort(arr[:])
    elif choice == 5:
        result = sorted(arr)
    else:
        print("Неверный выбор")
        return
    
    print(f"Отсортированный массив: {result}")
    
    # Сортировка по убыванию
    reverse_result = sorted(arr, reverse=True)
    print(f"По убыванию: {reverse_result}")

def main():
    print("Демонстрация алгоритмов сортировки")
    
    demonstrate_sorting()
    custom_sort_demo()

if __name__ == "__main__":
    main()
'''
    
    def _generate_searching(self, task: Dict[str, Any]) -> str:
        """Генерирует код поиска."""
        return '''#!/usr/bin/env python3
"""
Алгоритмы поиска.
"""

def linear_search(arr, target):
    """Линейный поиск."""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def binary_search(arr, target):
    """Бинарный поиск (массив должен быть отсортирован)."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def binary_search_recursive(arr, target, left=0, right=None):
    """Рекурсивный бинарный поиск."""
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)

def find_all_occurrences(arr, target):
    """Находит все вхождения элемента."""
    occurrences = []
    for i in range(len(arr)):
        if arr[i] == target:
            occurrences.append(i)
    return occurrences

def find_min_max(arr):
    """Находит минимальный и максимальный элементы."""
    if not arr:
        return None, None
    
    min_val = max_val = arr[0]
    min_idx = max_idx = 0
    
    for i in range(1, len(arr)):
        if arr[i] < min_val:
            min_val = arr[i]
            min_idx = i
        if arr[i] > max_val:
            max_val = arr[i]
            max_idx = i
    
    return (min_val, min_idx), (max_val, max_idx)

def find_second_largest(arr):
    """Находит второй по величине элемент."""
    if len(arr) < 2:
        return None
    
    unique_elements = list(set(arr))
    if len(unique_elements) < 2:
        return None
    
    unique_elements.sort(reverse=True)
    return unique_elements[1]

def search_in_range(arr, target, start, end):
    """Поиск в диапазоне индексов."""
    for i in range(start, min(end + 1, len(arr))):
        if arr[i] == target:
            return i
    return -1

def interpolation_search(arr, target):
    """Интерполяционный поиск (для равномерно распределенных данных)."""
    left, right = 0, len(arr) - 1
    
    while left <= right and target >= arr[left] and target <= arr[right]:
        if left == right:
            if arr[left] == target:
                return left
            return -1
        
        # Интерполяционная формула
        pos = left + ((target - arr[left]) * (right - left)) // (arr[right] - arr[left])
        
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            left = pos + 1
        else:
            right = pos - 1
    
    return -1

def demonstrate_search():
    """Демонстрация различных алгоритмов поиска."""
    import random
    
    # Создаем тестовый массив
    size = 20
    arr = sorted([random.randint(1, 100) for _ in range(size)])
    target = arr[random.randint(0, size-1)]  # Гарантированно есть в массиве
    
    print(f"Массив: {arr}")
    print(f"Ищем элемент: {target}")
    print()
    
    # Линейный поиск
    linear_result = linear_search(arr, target)
    print(f"Линейный поиск: {'найден на позиции ' + str(linear_result) if linear_result != -1 else 'не найден'}")
    
    # Бинарный поиск
    binary_result = binary_search(arr, target)
    print(f"Бинарный поиск: {'найден на позиции ' + str(binary_result) if binary_result != -1 else 'не найден'}")
    
    # Рекурсивный бинарный поиск
    recursive_result = binary_search_recursive(arr, target)
    print(f"Рекурсивный бинарный: {'найден на позиции ' + str(recursive_result) if recursive_result != -1 else 'не найден'}")
    
    # Все вхождения
    all_occurrences = find_all_occurrences(arr, target)
    print(f"Все вхождения: {all_occurrences}")
    
    # Минимум и максимум
    (min_val, min_idx), (max_val, max_idx) = find_min_max(arr)
    print(f"Минимум: {min_val} на позиции {min_idx}")
    print(f"Максимум: {max_val} на позиции {max_idx}")
    
    # Второй по величине
    second = find_second_largest(arr)
    print(f"Второй по величине: {second}")

def interactive_search():
    """Интерактивный поиск."""
    print("\\nИнтерактивный поиск")
    
    # Ввод массива
    n = int(input("Введите размер массива: "))
    arr = []
    
    print("Введите элементы массива:")
    for i in range(n):
        num = int(input(f"Элемент {i+1}: "))
        arr.append(num)
    
    # Сортируем для бинарного поиска
    sorted_arr = sorted(arr)
    
    while True:
        print(f"\\nМассив: {arr}")
        print(f"Отсортированный: {sorted_arr}")
        
        target = input("Введите элемент для поиска (или 'exit' для выхода): ")
        if target.lower() == 'exit':
            break
        
        try:
            target = int(target)
        except ValueError:
            print("Введите корректное число")
            continue
        
        print("\\nВыберите алгоритм поиска:")
        print("1. Линейный поиск")
        print("2. Бинарный поиск")
        print("3. Найти все вхождения")
        
        choice = input("Ваш выбор: ")
        
        if choice == '1':
            result = linear_search(arr, target)
            print(f"Результат: {'найден на позиции ' + str(result) if result != -1 else 'не найден'}")
        elif choice == '2':
            result = binary_search(sorted_arr, target)
            print(f"Результат в отсортированном массиве: {'найден на позиции ' + str(result) if result != -1 else 'не найден'}")
        elif choice == '3':
            occurrences = find_all_occurrences(arr, target)
            if occurrences:
                print(f"Найден на позициях: {occurrences}")
            else:
                print("Не найден")
        else:
            print("Неверный выбор")

def main():
    print("Демонстрация алгоритмов поиска")
    
    demonstrate_search()
    interactive_search()

if __name__ == "__main__":
    main()
'''
    
    def _generate_number_theory(self, task: Dict[str, Any]) -> str:
        """Генерирует код теории чисел."""
        return '''#!/usr/bin/env python3
"""
Задачи теории чисел.
"""

def is_prime(n):
    """Проверка на простое число."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def sieve_of_eratosthenes(limit):
    """Решето Эратосфена для нахождения всех простых чисел до limit."""
    if limit < 2:
        return []
    
    is_prime_arr = [True] * (limit + 1)
    is_prime_arr[0] = is_prime_arr[1] = False
    
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime_arr[i]:
            for j in range(i * i, limit + 1, i):
                is_prime_arr[j] = False
    
    return [i for i in range(2, limit + 1) if is_prime_arr[i]]

def factorial(n):
    """Вычисление факториала."""
    if n < 0:
        return None
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def factorial_iterative(n):
    """Итеративное вычисление факториала."""
    if n < 0:
        return None
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def gcd(a, b):
    """Наибольший общий делитель (алгоритм Евклида)."""
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    """Наименьшее общее кратное."""
    return abs(a * b) // gcd(a, b)

def fibonacci(n):
    """n-е число Фибоначчи."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def fibonacci_iterative(n):
    """Итеративное вычисление числа Фибоначчи."""
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def count_digits(n):
    """Подсчет количества цифр в числе."""
    return len(str(abs(n)))

def sum_of_digits(n):
    """Сумма цифр числа."""
    return sum(int(digit) for digit in str(abs(n)))

def reverse_number(n):
    """Обращение числа."""
    sign = -1 if n < 0 else 1
    return sign * int(str(abs(n))[::-1])

def is_palindrome_number(n):
    """Проверка, является ли число палиндромом."""
    return str(n) == str(n)[::-1]

def perfect_numbers(limit):
    """Находит все совершенные числа до limit."""
    perfect = []
    for n in range(2, limit + 1):
        divisors_sum = sum(i for i in range(1, n) if n % i == 0)
        if divisors_sum == n:
            perfect.append(n)
    return perfect

def prime_factorization(n):
    """Разложение числа на простые множители."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def demonstrate_number_theory():
    """Демонстрация функций теории чисел."""
    print("Демонстрация теории чисел")
    
    n = int(input("Введите число для анализа: "))
    
    print(f"\\nАнализ числа {n}:")
    print(f"Простое число: {is_prime(n)}")
    print(f"Количество цифр: {count_digits(n)}")
    print(f"Сумма цифр: {sum_of_digits(n)}")
    print(f"Обращенное число: {reverse_number(n)}")
    print(f"Палиндром: {is_palindrome_number(n)}")
    
    if n >= 0 and n <= 20:
        print(f"Факториал: {factorial(n)}")
        print(f"Число Фибоначчи: {fibonacci_iterative(n)}")
    
    if n > 1:
        factors = prime_factorization(n)
        print(f"Простые множители: {factors}")
    
    # Простые числа до n
    if n > 1 and n <= 100:
        primes = sieve_of_eratosthenes(n)
        print(f"Простые числа до {n}: {primes}")
    
    # НОД и НОК с другим числом
    m = int(input(f"\\nВведите второе число для НОД и НОК с {n}: "))
    print(f"НОД({n}, {m}) = {gcd(n, m)}")
    print(f"НОК({n}, {m}) = {lcm(n, m)}")

def number_sequences():
    """Различные числовые последовательности."""
    print("\\nЧисловые последовательности:")
    
    limit = int(input("Введите предел для последовательностей: "))
    
    # Простые числа
    primes = sieve_of_eratosthenes(limit)
    print(f"Простые числа до {limit}: {primes[:10]}{'...' if len(primes) > 10 else ''}")
    
    # Числа Фибоначчи
    fibs = []
    a, b = 0, 1
    while a <= limit:
        fibs.append(a)
        a, b = b, a + b
    print(f"Числа Фибоначчи до {limit}: {fibs}")
    
    # Совершенные числа
    if limit <= 10000:  # Ограничиваем для производительности
        perfect = perfect_numbers(limit)
        print(f"Совершенные числа до {limit}: {perfect}")
    
    # Палиндромы
    palindromes = [i for i in range(1, limit + 1) if is_palindrome_number(i)]
    print(f"Числа-палиндромы до {limit}: {palindromes[:20]}{'...' if len(palindromes) > 20 else ''}")

def main():
    demonstrate_number_theory()
    number_sequences()

if __name__ == "__main__":
    main()
'''
    
    def _generate_generic_algorithm_solution(self, task: Dict[str, Any]) -> str:
        """Генерирует общее алгоритмическое решение."""
        return '''#!/usr/bin/env python3
"""
Общая алгоритмическая задача.
"""

def generic_algorithm(data):
    """Универсальный алгоритм для обработки данных."""
    # Здесь должна быть логика согласно условию задачи
    return data

def process_input():
    """Обработка входных данных."""
    print("Ввод данных для обработки:")
    
    # Пример различных типов ввода
    choice = input("Тип данных (число/строка/список): ").lower()
    
    if choice == "число":
        data = float(input("Введите число: "))
    elif choice == "строка":
        data = input("Введите строку: ")
    elif choice == "список":
        n = int(input("Количество элементов: "))
        data = []
        for i in range(n):
            element = input(f"Элемент {i+1}: ")
            try:
                data.append(float(element))
            except ValueError:
                data.append(element)
    else:
        data = input("Введите данные: ")
    
    return data

def algorithm_template(steps):
    """Шаблон для выполнения алгоритма по шагам."""
    print("\\nВыполнение алгоритма:")
    
    for i, step in enumerate(steps, 1):
        print(f"Шаг {i}: {step}")
        input("Нажмите Enter для продолжения...")
    
    print("Алгоритм завершен!")

def main():
    print("Универсальная алгоритмическая задача")
    
    # Получаем входные данные
    input_data = process_input()
    print(f"Входные данные: {input_data}")
    
    # Обрабатываем данные
    result = generic_algorithm(input_data)
    print(f"Результат обработки: {result}")
    
    # Демонстрация пошагового выполнения
    steps = [
        "Анализ входных данных",
        "Применение основного алгоритма", 
        "Проверка результата",
        "Вывод результата"
    ]
    
    algorithm_template(steps)

if __name__ == "__main__":
    main()
'''
