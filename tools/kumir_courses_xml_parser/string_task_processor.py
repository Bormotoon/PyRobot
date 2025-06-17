#!/usr/bin/env python3
"""
Специализированный процессор для задач на строки.

Обрабатывает задачи, связанные со строками:
- Поиск в строках
- Замена в строках
- Работа с символами
- Анализ строк
"""

from pathlib import Path
from typing import List, Dict, Any


class StringTaskProcessor:
    """Процессор для задач на строки."""
    
    def __init__(self):
        """Инициализация процессора строк."""
        self.string_operations = {
            'length': self._generate_string_length,
            'search': self._generate_string_search,
            'replace': self._generate_string_replace,
            'substring': self._generate_substring,
            'insert': self._generate_string_insert,
            'delete': self._generate_string_delete,
            'char_code': self._generate_char_code,
            'char_from_code': self._generate_char_from_code,
            'count_chars': self._generate_count_chars,
            'reverse_string': self._generate_reverse_string,
            'uppercase': self._generate_uppercase,
            'lowercase': self._generate_lowercase,
        }
    
    def process_tasks(self, tasks: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает список задач на строки.
        
        Args:
            tasks: Список задач на строки
            output_dir: Выходная директория
            
        Returns:
            Результаты обработки
        """
        results = {
            'processor_type': 'string',
            'total_tasks': len(tasks),
            'processed_tasks': 0,
            'generated_files': {
                'python': [],
                'kumir': []
            },
            'task_details': []
        }
        
        # Создаем поддиректории
        py_dir = output_dir / "py" / "strings"
        kum_dir = output_dir / "kum" / "strings"
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
                    'task_id': f"str_{i}",
                    'error': str(e),
                    'title': task.get('title', 'Без названия')
                }
                results['task_details'].append(error_details)
        
        return results
    
    def process_single_task(self, task: Dict[str, Any], task_num: int, py_dir: Path, kum_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает одну задачу на строки.
        
        Args:
            task: Данные задачи
            task_num: Номер задачи
            py_dir: Директория для Python файлов
            kum_dir: Директория для KUM файлов
            
        Returns:
            Результат обработки задачи
        """
        # Анализируем тип операции со строкой
        operation_type = self._detect_string_operation(task)
        
        # Генерируем базовое имя файла
        base_name = f"str_{task_num:02d}_{operation_type}"
        
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
            'title': task.get('title', 'Строка'),
            'operation_type': operation_type,
            'python_file': str(python_file.relative_to(py_dir.parent.parent)),
            'kumir_file': str(kumir_file.relative_to(kum_dir.parent.parent)),
            'status': 'success'
        }
    
    def _detect_string_operation(self, task: Dict[str, Any]) -> str:
        """Определяет тип операции со строкой."""
        
        title = task.get('title', '').lower()
        code = task.get('student_code', '').lower()
        combined_text = f"{title} {code}"
        
        # Паттерны для определения операций
        if any(pattern in combined_text for pattern in ['длин', 'длина', 'size', 'length']):
            return 'length'
        elif any(pattern in combined_text for pattern in ['найти', 'найди', 'поиск', 'search']):
            return 'search'
        elif any(pattern in combined_text for pattern in ['заменить', 'замени', 'replace']):
            return 'replace'
        elif any(pattern in combined_text for pattern in ['подстрока', 'копировать', 'substring']):
            return 'substring'
        elif any(pattern in combined_text for pattern in ['вставить', 'вставь', 'insert']):
            return 'insert'
        elif any(pattern in combined_text for pattern in ['удалить', 'удали', 'delete']):
            return 'delete'
        elif any(pattern in combined_text for pattern in ['код символа', 'код', 'ascii']):
            return 'char_code'
        elif any(pattern in combined_text for pattern in ['символ по коду', 'символ']):
            return 'char_from_code'
        elif any(pattern in combined_text for pattern in ['посчитай', 'количество', 'count']):
            return 'count_chars'
        elif any(pattern in combined_text for pattern in ['переверни', 'обрати', 'reverse']):
            return 'reverse_string'
        elif any(pattern in combined_text for pattern in ['заглавные', 'большие', 'upper']):
            return 'uppercase'
        elif any(pattern in combined_text for pattern in ['строчные', 'маленькие', 'lower']):
            return 'lowercase'
        else:
            return 'generic_string'
    
    def _generate_python_solution(self, task: Dict[str, Any], operation_type: str) -> str:
        """Генерирует Python решение для задачи на строки."""
        
        if operation_type in self.string_operations:
            return self.string_operations[operation_type](task)
        else:
            return self._generate_generic_string_solution(task)
    
    def _generate_string_length(self, task: Dict[str, Any]) -> str:
        """Генерирует код для определения длины строки."""
        return '''#!/usr/bin/env python3
"""
Определение длины строки.
"""

def get_string_length(s):
    """Возвращает длину строки."""
    return len(s)

def main():
    # Читаем строку
    text = input("Введите строку: ")
    
    # Определяем длину
    length = get_string_length(text)
    
    # Выводим результат
    print(f"Длина строки: {length}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_string_search(self, task: Dict[str, Any]) -> str:
        """Генерирует код для поиска в строке."""
        return '''#!/usr/bin/env python3
"""
Поиск подстроки в строке.
"""

def find_substring(text, pattern):
    """Ищет подстроку в тексте и возвращает позицию."""
    index = text.find(pattern)
    return index if index != -1 else -1

def main():
    # Читаем строку и образец
    text = input("Введите строку: ")
    pattern = input("Введите образец для поиска: ")
    
    # Ищем подстроку
    position = find_substring(text, pattern)
    
    # Выводим результат
    if position != -1:
        print(f"Подстрока найдена на позиции: {position + 1}")
    else:
        print("Подстрока не найдена")

if __name__ == "__main__":
    main()
'''
    
    def _generate_string_replace(self, task: Dict[str, Any]) -> str:
        """Генерирует код для замены в строке."""
        return '''#!/usr/bin/env python3
"""
Замена подстроки в строке.
"""

def replace_substring(text, old_pattern, new_pattern):
    """Заменяет все вхождения подстроки."""
    return text.replace(old_pattern, new_pattern)

def main():
    # Читаем параметры
    text = input("Введите строку: ")
    old_pattern = input("Что заменить: ")
    new_pattern = input("На что заменить: ")
    
    # Выполняем замену
    result = replace_substring(text, old_pattern, new_pattern)
    
    # Выводим результат
    print(f"Результат замены: {result}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_substring(self, task: Dict[str, Any]) -> str:
        """Генерирует код для извлечения подстроки."""
        return '''#!/usr/bin/env python3
"""
Извлечение подстроки.
"""

def get_substring(text, start, length):
    """Извлекает подстроку заданной длины начиная с позиции start."""
    return text[start:start + length]

def main():
    # Читаем параметры
    text = input("Введите строку: ")
    start = int(input("Начальная позиция (с 0): "))
    length = int(input("Длина подстроки: "))
    
    # Извлекаем подстроку
    result = get_substring(text, start, length)
    
    # Выводим результат
    print(f"Подстрока: {result}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_string_insert(self, task: Dict[str, Any]) -> str:
        """Генерирует код для вставки в строку."""
        return '''#!/usr/bin/env python3
"""
Вставка подстроки в строку.
"""

def insert_substring(text, position, substring):
    """Вставляет подстроку в заданную позицию."""
    return text[:position] + substring + text[position:]

def main():
    # Читаем параметры
    text = input("Введите строку: ")
    position = int(input("Позиция для вставки (с 0): "))
    substring = input("Что вставить: ")
    
    # Выполняем вставку
    result = insert_substring(text, position, substring)
    
    # Выводим результат
    print(f"Результат вставки: {result}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_string_delete(self, task: Dict[str, Any]) -> str:
        """Генерирует код для удаления из строки."""
        return '''#!/usr/bin/env python3
"""
Удаление части строки.
"""

def delete_substring(text, start, length):
    """Удаляет часть строки заданной длины начиная с позиции start."""
    return text[:start] + text[start + length:]

def main():
    # Читаем параметры
    text = input("Введите строку: ")
    start = int(input("Начальная позиция удаления (с 0): "))
    length = int(input("Длина удаляемой части: "))
    
    # Выполняем удаление
    result = delete_substring(text, start, length)
    
    # Выводим результат
    print(f"Результат удаления: {result}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_char_code(self, task: Dict[str, Any]) -> str:
        """Генерирует код для получения кода символа."""
        return '''#!/usr/bin/env python3
"""
Получение кода символа.
"""

def get_char_code(char):
    """Возвращает код символа."""
    return ord(char)

def main():
    # Читаем символ
    char = input("Введите символ: ")[0]
    
    # Получаем код
    code = get_char_code(char)
    
    # Выводим результат
    print(f"Код символа '{char}': {code}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_char_from_code(self, task: Dict[str, Any]) -> str:
        """Генерирует код для получения символа по коду."""
        return '''#!/usr/bin/env python3
"""
Получение символа по коду.
"""

def get_char_from_code(code):
    """Возвращает символ по его коду."""
    return chr(code)

def main():
    # Читаем код
    code = int(input("Введите код символа: "))
    
    # Получаем символ
    char = get_char_from_code(code)
    
    # Выводим результат
    print(f"Символ с кодом {code}: '{char}'")

if __name__ == "__main__":
    main()
'''
    
    def _generate_count_chars(self, task: Dict[str, Any]) -> str:
        """Генерирует код для подсчета символов."""
        return '''#!/usr/bin/env python3
"""
Подсчет символов в строке.
"""

def count_char(text, target_char):
    """Подсчитывает количество вхождений символа в строку."""
    return text.count(target_char)

def count_vowels(text):
    """Подсчитывает количество гласных."""
    vowels = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
    return sum(1 for char in text if char in vowels)

def main():
    # Читаем строку
    text = input("Введите строку: ")
    
    # Различные варианты подсчета
    target_char = input("Введите символ для подсчета: ")
    char_count = count_char(text, target_char)
    vowel_count = count_vowels(text)
    
    # Выводим результат
    print(f"Символ '{target_char}' встречается {char_count} раз")
    print(f"Гласных букв: {vowel_count}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_reverse_string(self, task: Dict[str, Any]) -> str:
        """Генерирует код для обращения строки."""
        return '''#!/usr/bin/env python3
"""
Обращение строки.
"""

def reverse_string(text):
    """Переворачивает строку."""
    return text[::-1]

def main():
    # Читаем строку
    text = input("Введите строку: ")
    
    # Переворачиваем
    reversed_text = reverse_string(text)
    
    # Выводим результат
    print(f"Обращенная строка: {reversed_text}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_uppercase(self, task: Dict[str, Any]) -> str:
        """Генерирует код для преобразования в верхний регистр."""
        return '''#!/usr/bin/env python3
"""
Преобразование в верхний регистр.
"""

def to_uppercase(text):
    """Преобразует строку в верхний регистр."""
    return text.upper()

def main():
    # Читаем строку
    text = input("Введите строку: ")
    
    # Преобразуем в верхний регистр
    upper_text = to_uppercase(text)
    
    # Выводим результат
    print(f"Верхний регистр: {upper_text}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_lowercase(self, task: Dict[str, Any]) -> str:
        """Генерирует код для преобразования в нижний регистр."""
        return '''#!/usr/bin/env python3
"""
Преобразование в нижний регистр.
"""

def to_lowercase(text):
    """Преобразует строку в нижний регистр."""
    return text.lower()

def main():
    # Читаем строку
    text = input("Введите строку: ")
    
    # Преобразуем в нижний регистр
    lower_text = to_lowercase(text)
    
    # Выводим результат
    print(f"Нижний регистр: {lower_text}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_generic_string_solution(self, task: Dict[str, Any]) -> str:
        """Генерирует общее решение для строки."""
        return '''#!/usr/bin/env python3
"""
Общая задача со строкой.
"""

def process_string(text):
    """Обрабатывает строку согласно условию задачи."""
    # Здесь должна быть логика согласно условию
    return text

def main():
    # Читаем строку
    text = input("Введите строку: ")
    
    # Обрабатываем строку
    result = process_string(text)
    
    # Выводим результат
    print(f"Результат обработки: {result}")

if __name__ == "__main__":
    main()
'''
