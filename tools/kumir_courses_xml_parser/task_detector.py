#!/usr/bin/env python3
"""
Детектор типов задач для мегапарсера.

Анализирует задачи и определяет их тип для направления
к соответствующему специализированному процессору.
"""

import re
from typing import Dict, Any, List


class TaskTypeDetector:
    """Детектор типов задач на основе анализа кода и названий."""
    
    def __init__(self):
        """Инициализация детектора с паттернами для каждого типа задач."""
        
        # Паттерны для задач на массивы
        self.array_patterns = [
            r'таб\s+[а-яё]+\s*\[',  # объявление массива
            r'нц\s+для\s+[а-яё]+\s+от',  # циклы по массиву
            r'дай\s+размер',  # получение размера массива
            r'заполни\s+массив',
            r'отсортируй',
            r'найди\s+в\s+массиве',
            r'переверни\s+массив',
            r'сдвинь\s+массив',
            r'массив',
            r'элемент',
            r'\[.+\]',  # индексация массива
        ]
        
        # Паттерны для строковых задач
        self.string_patterns = [
            r'лит\s+[а-яё]+',  # объявление строки
            r'длин\s*\(',  # функция длины строки
            r'найти\s*\(',  # поиск в строке
            r'заменить\s*\(',  # замена в строке
            r'копировать\s*\(',  # копирование части строки
            r'вставить\s*\(',  # вставка в строку
            r'удалить\s*\(',  # удаление из строки
            r'символ\s*\(',  # работа с символами
            r'код\s*\(',  # получение кода символа
            r'строка',
            r'текст',
            r'символ',
        ]
        
        # Паттерны для функций
        self.function_patterns = [
            r'алг\s+[а-яё]+\s*\(',  # объявление функции
            r'функ\s+[а-яё]+\s*\(',  # объявление функции
            r'знач\s+[а-яё]+',  # параметры по значению
            r'арг\s+[а-яё]+',  # параметры-аргументы
            r'рез\s+[а-яё]+',  # параметры-результаты
            r'вернуть',  # возврат значения
            r'функция',
            r'процедура',
        ]
        
        # Паттерны для робота
        self.robot_patterns = [
            r'вверх',
            r'вниз', 
            r'влево',
            r'вправо',
            r'закрасить',
            r'свободно\s+(сверху|снизу|слева|справа)',
            r'стена\s+(сверху|снизу|слева|справа)',
            r'клетка\s+закрашена',
            r'робот',
            r'поле',
            r'клетка',
        ]
        
        # Паттерны для алгоритмических задач
        self.algorithm_patterns = [
            r'бинарный\s+поиск',
            r'сортировка',
            r'рекурсия',
            r'динамическое\s+программирование',
            r'жадный\s+алгоритм',
            r'граф',
            r'дерево',
            r'поиск\s+в\s+глубину',
            r'поиск\s+в\s+ширину',
            r'алгоритм',
        ]
        
        # Ключевые слова в названиях задач
        self.title_keywords = {
            'array': [
                'массив', 'элемент', 'таблица', 'список', 'сортировка',
                'поиск', 'заполнение', 'обращение', 'сдвиг'
            ],
            'string': [
                'строка', 'текст', 'символ', 'слово', 'предложение',
                'поиск', 'замена', 'длина', 'подстрока'
            ],
            'function': [
                'функция', 'процедура', 'алгоритм', 'подпрограмма',
                'параметр', 'аргумент', 'возврат'
            ],
            'robot': [
                'робот', 'поле', 'клетка', 'стена', 'лабиринт',
                'движение', 'закраска'
            ],
            'algorithm': [
                'алгоритм', 'рекурсия', 'итерация', 'цикл',
                'условие', 'ветвление', 'граф', 'дерево'
            ]
        }
    
    def detect_task_type(self, task: Dict[str, Any]) -> str:
        """
        Определяет тип задачи на основе анализа кода и названия.
        
        Args:
            task: Данные задачи
            
        Returns:
            Тип задачи: 'array', 'string', 'function', 'robot', 'algorithm'
        """
        # Извлекаем текст для анализа
        text_to_analyze = []
        
        if 'title' in task and task['title']:
            text_to_analyze.append(task['title'].lower())
        
        if 'student_code' in task and task['student_code']:
            text_to_analyze.append(task['student_code'].lower())
        
        combined_text = ' '.join(text_to_analyze)
        
        # Подсчитываем совпадения для каждого типа
        type_scores = {
            'array': 0,
            'string': 0, 
            'function': 0,
            'robot': 0,
            'algorithm': 0
        }
        
        # Анализируем по паттернам кода
        type_scores['array'] += self._count_pattern_matches(combined_text, self.array_patterns)
        type_scores['string'] += self._count_pattern_matches(combined_text, self.string_patterns)
        type_scores['function'] += self._count_pattern_matches(combined_text, self.function_patterns)
        type_scores['robot'] += self._count_pattern_matches(combined_text, self.robot_patterns)
        type_scores['algorithm'] += self._count_pattern_matches(combined_text, self.algorithm_patterns)
        
        # Анализируем по ключевым словам в названии
        title_text = task.get('title', '').lower()
        for task_type, keywords in self.title_keywords.items():
            for keyword in keywords:
                if keyword in title_text:
                    type_scores[task_type] += 2  # Название имеет больший вес
        
        # Дополнительные эвристики
        type_scores = self._apply_additional_heuristics(task, type_scores)
        
        # Находим тип с максимальным счетом
        max_score = max(type_scores.values())
        if max_score == 0:
            return 'algorithm'  # По умолчанию
        
        # Возвращаем тип с наибольшим счетом
        for task_type, score in type_scores.items():
            if score == max_score:
                return task_type
        
        return 'algorithm'
    
    def _count_pattern_matches(self, text: str, patterns: List[str]) -> int:
        """Подсчитывает количество совпадений паттернов в тексте."""
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count
    
    def _apply_additional_heuristics(self, task: Dict[str, Any], scores: Dict[str, int]) -> Dict[str, int]:
        """Применяет дополнительные эвристики для уточнения типа задачи."""
        
        student_code = task.get('student_code', '').lower()
        title = task.get('title', '').lower()
        
        # Эвристика 1: Если есть объявления массивов - точно массивы
        if re.search(r'таб\s+[а-яё]+\s*\[', student_code):
            scores['array'] += 5
        
        # Эвристика 2: Если есть объявления строк - точно строки
        if re.search(r'лит\s+[а-яё]+', student_code):
            scores['string'] += 5
        
        # Эвристика 3: Если есть объявления функций - точно функции
        if re.search(r'(алг|функ)\s+[а-яё]+\s*\(', student_code):
            scores['function'] += 5
        
        # Эвристика 4: Команды робота - точно робот
        robot_commands = ['вверх', 'вниз', 'влево', 'вправо', 'закрасить']
        for command in robot_commands:
            if command in student_code:
                scores['robot'] += 3
        
        # Эвристика 5: Анализ по источнику файла
        source_file = task.get('source_file', '').lower()
        if 'робот' in source_file or 'robot' in source_file:
            scores['robot'] += 3
        elif 'массив' in source_file or 'array' in source_file:
            scores['array'] += 3
        elif 'строк' in source_file or 'string' in source_file:
            scores['string'] += 3
        elif 'функ' in source_file or 'function' in source_file:
            scores['function'] += 3
        
        return scores
    
    def get_detailed_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Возвращает детальный анализ задачи для отладки.
        
        Args:
            task: Данные задачи
            
        Returns:
            Подробная информация об анализе
        """
        text_to_analyze = []
        
        if 'title' in task and task['title']:
            text_to_analyze.append(task['title'].lower())
        
        if 'student_code' in task and task['student_code']:
            text_to_analyze.append(task['student_code'].lower())
        
        combined_text = ' '.join(text_to_analyze)
        
        analysis = {
            'detected_type': self.detect_task_type(task),
            'text_analyzed': combined_text[:200] + '...' if len(combined_text) > 200 else combined_text,
            'pattern_matches': {
                'array': self._count_pattern_matches(combined_text, self.array_patterns),
                'string': self._count_pattern_matches(combined_text, self.string_patterns),
                'function': self._count_pattern_matches(combined_text, self.function_patterns),
                'robot': self._count_pattern_matches(combined_text, self.robot_patterns),
                'algorithm': self._count_pattern_matches(combined_text, self.algorithm_patterns)
            },
            'title_keywords_found': {},
            'source_file': task.get('source_file', '')
        }
        
        # Анализируем ключевые слова в названии
        title_text = task.get('title', '').lower()
        for task_type, keywords in self.title_keywords.items():
            found_keywords = [kw for kw in keywords if kw in title_text]
            if found_keywords:
                analysis['title_keywords_found'][task_type] = found_keywords
        
        return analysis
