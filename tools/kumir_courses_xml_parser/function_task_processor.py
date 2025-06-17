#!/usr/bin/env python3
"""
Специализированный процессор для задач на функции.

Обрабатывает задачи, связанные с функциями и процедурами:
- Математические функции
- Функции с параметрами
- Рекурсивные функции
- Процедуры
"""

from pathlib import Path
from typing import List, Dict, Any


class FunctionTaskProcessor:
    """Процессор для задач на функции."""
    
    def __init__(self):
        """Инициализация процессора функций."""
        self.function_types = {
            'math_function': self._generate_math_function,
            'recursive_function': self._generate_recursive_function,
            'procedure_with_params': self._generate_procedure_with_params,
            'boolean_function': self._generate_boolean_function,
            'conversion_function': self._generate_conversion_function,
            'validation_function': self._generate_validation_function,
        }
    
    def process_tasks(self, tasks: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает список задач на функции.
        
        Args:
            tasks: Список задач на функции
            output_dir: Выходная директория
            
        Returns:
            Результаты обработки
        """
        results = {
            'processor_type': 'function',
            'total_tasks': len(tasks),
            'processed_tasks': 0,
            'generated_files': {
                'python': [],
                'kumir': []
            },
            'task_details': []
        }
        
        # Создаем поддиректории
        py_dir = output_dir / "py" / "functions"
        kum_dir = output_dir / "kum" / "functions"
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
                    'task_id': f"func_{i}",
                    'error': str(e),
                    'title': task.get('title', 'Без названия')
                }
                results['task_details'].append(error_details)
        
        return results
    
    def process_single_task(self, task: Dict[str, Any], task_num: int, py_dir: Path, kum_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает одну задачу на функции.
        
        Args:
            task: Данные задачи
            task_num: Номер задачи
            py_dir: Директория для Python файлов
            kum_dir: Директория для KUM файлов
            
        Returns:
            Результат обработки задачи
        """
        # Анализируем тип функции
        function_type = self._detect_function_type(task)
        
        # Генерируем базовое имя файла
        base_name = f"func_{task_num:02d}_{function_type}"
        
        # Генерируем Python код
        python_code = self._generate_python_solution(task, function_type)
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
            'title': task.get('title', 'Функция'),
            'function_type': function_type,
            'python_file': str(python_file.relative_to(py_dir.parent.parent)),
            'kumir_file': str(kumir_file.relative_to(kum_dir.parent.parent)),
            'status': 'success'
        }
    
    def _detect_function_type(self, task: Dict[str, Any]) -> str:
        """Определяет тип функции."""
        
        title = task.get('title', '').lower()
        code = task.get('student_code', '').lower()
        combined_text = f"{title} {code}"
        
        # Паттерны для определения типов функций
        if any(pattern in combined_text for pattern in ['рекурсия', 'рекурсивная', 'factorial', 'fibonacci']):
            return 'recursive_function'
        elif any(pattern in combined_text for pattern in ['процедура', 'proc', 'арг', 'рез']):
            return 'procedure_with_params'
        elif any(pattern in combined_text for pattern in ['истина', 'ложь', 'логическая', 'boolean', 'проверка']):
            return 'boolean_function'
        elif any(pattern in combined_text for pattern in ['преобразовать', 'перевести', 'конвертировать']):
            return 'conversion_function'
        elif any(pattern in combined_text for pattern in ['проверить', 'правильность', 'валидация']):
            return 'validation_function'
        elif any(pattern in combined_text for pattern in ['математическая', 'вычислить', 'формула']):
            return 'math_function'
        else:
            return 'generic_function'
    
    def _generate_python_solution(self, task: Dict[str, Any], function_type: str) -> str:
        """Генерирует Python решение для задачи на функции."""
        
        if function_type in self.function_types:
            return self.function_types[function_type](task)
        else:
            return self._generate_generic_function_solution(task)
    
    def _generate_math_function(self, task: Dict[str, Any]) -> str:
        """Генерирует математическую функцию."""
        return '''#!/usr/bin/env python3
"""
Математическая функция.
"""

def math_function(x):
    """Математическая функция для вычислений."""
    # Пример: квадратичная функция
    return x * x + 2 * x + 1

def calculate_polynomial(a, b, c, x):
    """Вычисляет полином ax^2 + bx + c."""
    return a * x * x + b * x + c

def main():
    # Читаем входные данные
    x = float(input("Введите значение x: "))
    
    # Вычисляем функцию
    result1 = math_function(x)
    print(f"f(x) = x^2 + 2x + 1 = {result1}")
    
    # Пример с полиномом
    a = float(input("Введите коэффициент a: "))
    b = float(input("Введите коэффициент b: "))
    c = float(input("Введите коэффициент c: "))
    
    result2 = calculate_polynomial(a, b, c, x)
    print(f"P(x) = {a}x^2 + {b}x + {c} = {result2}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_recursive_function(self, task: Dict[str, Any]) -> str:
        """Генерирует рекурсивную функцию."""
        return '''#!/usr/bin/env python3
"""
Рекурсивная функция.
"""

def factorial(n):
    """Вычисляет факториал числа рекурсивно."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    """Вычисляет число Фибоначчи рекурсивно."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def power(base, exp):
    """Возводит число в степень рекурсивно."""
    if exp == 0:
        return 1
    if exp == 1:
        return base
    return base * power(base, exp - 1)

def gcd(a, b):
    """Находит НОД двух чисел (алгоритм Евклида)."""
    if b == 0:
        return a
    return gcd(b, a % b)

def main():
    # Демонстрация различных рекурсивных функций
    n = int(input("Введите число: "))
    
    print(f"Факториал {n}: {factorial(n)}")
    print(f"Фибоначчи {n}: {fibonacci(n)}")
    
    base = int(input("Введите основание степени: "))
    exp = int(input("Введите показатель степени: "))
    print(f"{base}^{exp} = {power(base, exp)}")
    
    a = int(input("Введите первое число для НОД: "))
    b = int(input("Введите второе число для НОД: "))
    print(f"НОД({a}, {b}) = {gcd(a, b)}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_procedure_with_params(self, task: Dict[str, Any]) -> str:
        """Генерирует процедуру с параметрами."""
        return '''#!/usr/bin/env python3
"""
Процедура с параметрами.
"""

def swap_values(a, b):
    """Обменивает значения двух переменных."""
    return b, a

def increment_by_value(x, increment):
    """Увеличивает значение на заданную величину."""
    return x + increment

def process_array_elements(arr, operation):
    """Обрабатывает элементы массива заданной операцией."""
    if operation == "double":
        return [x * 2 for x in arr]
    elif operation == "square":
        return [x * x for x in arr]
    elif operation == "increment":
        return [x + 1 for x in arr]
    else:
        return arr

def calculate_statistics(numbers):
    """Вычисляет статистики для списка чисел."""
    if not numbers:
        return 0, 0, 0, 0
    
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    maximum = max(numbers)
    minimum = min(numbers)
    
    return total, average, maximum, minimum

def main():
    # Демонстрация обмена значений
    a = int(input("Введите первое число: "))
    b = int(input("Введите второе число: "))
    print(f"До обмена: a = {a}, b = {b}")
    
    a, b = swap_values(a, b)
    print(f"После обмена: a = {a}, b = {b}")
    
    # Демонстрация увеличения значения
    x = int(input("Введите число для увеличения: "))
    inc = int(input("На сколько увеличить: "))
    result = increment_by_value(x, inc)
    print(f"Результат: {result}")
    
    # Обработка массива
    n = int(input("Введите размер массива: "))
    arr = []
    for i in range(n):
        arr.append(int(input(f"Элемент {i+1}: ")))
    
    doubled = process_array_elements(arr, "double")
    print(f"Удвоенные элементы: {doubled}")
    
    # Статистики
    total, avg, max_val, min_val = calculate_statistics(arr)
    print(f"Сумма: {total}, Среднее: {avg:.2f}")
    print(f"Максимум: {max_val}, Минимум: {min_val}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_boolean_function(self, task: Dict[str, Any]) -> str:
        """Генерирует логическую функцию."""
        return '''#!/usr/bin/env python3
"""
Логическая функция.
"""

def is_even(n):
    """Проверяет, является ли число четным."""
    return n % 2 == 0

def is_prime(n):
    """Проверяет, является ли число простым."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def is_palindrome(s):
    """Проверяет, является ли строка палиндромом."""
    s = s.lower().replace(" ", "")
    return s == s[::-1]

def is_in_range(value, min_val, max_val):
    """Проверяет, находится ли значение в диапазоне."""
    return min_val <= value <= max_val

def is_positive(n):
    """Проверяет, является ли число положительным."""
    return n > 0

def main():
    # Тестирование различных логических функций
    num = int(input("Введите число: "))
    
    print(f"Число {num} четное: {is_even(num)}")
    print(f"Число {num} простое: {is_prime(num)}")
    print(f"Число {num} положительное: {is_positive(num)}")
    
    # Проверка диапазона
    min_val = int(input("Введите минимум диапазона: "))
    max_val = int(input("Введите максимум диапазона: "))
    print(f"Число {num} в диапазоне [{min_val}, {max_val}]: {is_in_range(num, min_val, max_val)}")
    
    # Проверка палиндрома
    text = input("Введите строку для проверки на палиндром: ")
    print(f"Строка '{text}' является палиндромом: {is_palindrome(text)}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_conversion_function(self, task: Dict[str, Any]) -> str:
        """Генерирует функцию преобразования."""
        return '''#!/usr/bin/env python3
"""
Функция преобразования.
"""

def celsius_to_fahrenheit(celsius):
    """Преобразует температуру из Цельсия в Фаренгейт."""
    return celsius * 9/5 + 32

def fahrenheit_to_celsius(fahrenheit):
    """Преобразует температуру из Фаренгейта в Цельсий."""
    return (fahrenheit - 32) * 5/9

def meters_to_feet(meters):
    """Преобразует метры в футы."""
    return meters * 3.28084

def feet_to_meters(feet):
    """Преобразует футы в метры."""
    return feet / 3.28084

def decimal_to_binary(decimal):
    """Преобразует десятичное число в двоичное."""
    return bin(decimal)[2:]  # Убираем префикс '0b'

def binary_to_decimal(binary_str):
    """Преобразует двоичное число в десятичное."""
    return int(binary_str, 2)

def main():
    # Демонстрация различных преобразований
    
    # Температура
    temp_c = float(input("Введите температуру в Цельсиях: "))
    temp_f = celsius_to_fahrenheit(temp_c)
    print(f"{temp_c}°C = {temp_f:.2f}°F")
    
    # Длина
    length_m = float(input("Введите длину в метрах: "))
    length_ft = meters_to_feet(length_m)
    print(f"{length_m} м = {length_ft:.2f} футов")
    
    # Системы счисления
    decimal = int(input("Введите десятичное число: "))
    binary = decimal_to_binary(decimal)
    print(f"Десятичное {decimal} = двоичное {binary}")
    
    binary_input = input("Введите двоичное число: ")
    try:
        decimal_result = binary_to_decimal(binary_input)
        print(f"Двоичное {binary_input} = десятичное {decimal_result}")
    except ValueError:
        print("Некорректное двоичное число")

if __name__ == "__main__":
    main()
'''
    
    def _generate_validation_function(self, task: Dict[str, Any]) -> str:
        """Генерирует функцию валидации."""
        return '''#!/usr/bin/env python3
"""
Функция валидации.
"""

def is_valid_email(email):
    """Проверяет корректность email адреса (упрощенная версия)."""
    return '@' in email and '.' in email.split('@')[-1]

def is_valid_phone(phone):
    """Проверяет корректность номера телефона."""
    # Убираем все не-цифры
    digits = ''.join(filter(str.isdigit, phone))
    return len(digits) >= 10

def is_valid_password(password):
    """Проверяет сложность пароля."""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit

def is_valid_date(day, month, year):
    """Проверяет корректность даты."""
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    # Количество дней в месяце
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Проверка на високосный год
    if month == 2 and is_leap_year(year):
        max_days = 29
    else:
        max_days = days_in_month[month - 1]
    
    return day <= max_days

def is_leap_year(year):
    """Проверяет, является ли год високосным."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def main():
    # Тестирование различных валидаций
    
    email = input("Введите email: ")
    print(f"Email корректен: {is_valid_email(email)}")
    
    phone = input("Введите номер телефона: ")
    print(f"Телефон корректен: {is_valid_phone(phone)}")
    
    password = input("Введите пароль: ")
    print(f"Пароль достаточно сложный: {is_valid_password(password)}")
    
    # Проверка даты
    day = int(input("Введите день: "))
    month = int(input("Введите месяц: "))
    year = int(input("Введите год: "))
    
    print(f"Дата {day:02d}.{month:02d}.{year} корректна: {is_valid_date(day, month, year)}")
    print(f"Год {year} високосный: {is_leap_year(year)}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_generic_function_solution(self, task: Dict[str, Any]) -> str:
        """Генерирует общее решение для функции."""
        return '''#!/usr/bin/env python3
"""
Общая функция.
"""

def generic_function(param):
    """Универсальная функция для обработки параметра."""
    # Здесь должна быть логика согласно условию задачи
    return param

def process_data(data):
    """Обрабатывает входные данные."""
    result = generic_function(data)
    return result

def main():
    # Читаем входные данные
    data = input("Введите данные: ")
    
    # Пытаемся преобразовать в число, если возможно
    try:
        data = float(data)
    except ValueError:
        pass  # Оставляем как строку
    
    # Обрабатываем данные
    result = process_data(data)
    
    # Выводим результат
    print(f"Результат обработки: {result}")

if __name__ == "__main__":
    main()
'''
