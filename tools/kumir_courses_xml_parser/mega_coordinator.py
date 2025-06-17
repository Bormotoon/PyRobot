#!/usr/bin/env python3
"""
Координатор мегапарсера - главный компонент модульной архитектуры.

Этот модуль координирует работу всех специализированных парсеров задач:
- ArrayTaskProcessor - для задач на массивы
- StringTaskProcessor - для задач на строки  
- FunctionTaskProcessor - для задач на функции
- RobotTaskProcessor - для задач с роботом
- AlgorithmTaskProcessor - для алгоритмических задач
- TaskFinalizer - финальная обработка и генерация файлов
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import xml.etree.ElementTree as ET

# Импортируем специализированные процессоры
from array_task_processor import ArrayTaskProcessor
from string_task_processor import StringTaskProcessor
from function_task_processor import FunctionTaskProcessor
from robot_task_processor import RobotTaskProcessor
from algorithm_task_processor import AlgorithmTaskProcessor
from task_finalizer import TaskFinalizer
from task_detector import TaskTypeDetector


class MegaCoordinator:
    """
    Главный координатор мегапарсера.
    
    Распределяет задачи между специализированными процессорами
    и координирует их работу.
    """
    
    def __init__(self, input_folder: str, output_folder: str = "parsed_xml_results"):
        """
        Инициализация координатора.
        
        Args:
            input_folder: Папка с XML файлами
            output_folder: Папка для результатов
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        
        # Настройка логирования
        self.setup_logging()
        
        # Инициализация детектора типов задач
        self.detector = TaskTypeDetector()
        
        # Инициализация специализированных процессоров
        self.processors = {
            'array': ArrayTaskProcessor(),
            'string': StringTaskProcessor(),
            'function': FunctionTaskProcessor(),
            'robot': RobotTaskProcessor(),
            'algorithm': AlgorithmTaskProcessor()
        }
        
        # Инициализация финализатора
        self.finalizer = TaskFinalizer()
        
        # Статистика обработки
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_tasks': 0,
            'processed_tasks': 0,
            'task_types': {},
            'errors': []
        }
    
    def setup_logging(self):
        """Настройка системы логирования."""
        log_dir = self.output_folder / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "mega_coordinator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def process_all_files(self) -> Dict[str, Any]:
        """
        Обрабатывает все XML файлы в входной папке.
        
        Returns:
            Dict с результатами обработки
        """
        self.logger.info(f"Начинаем обработку файлов в папке: {self.input_folder}")
        
        # Находим все XML файлы
        xml_files = list(self.input_folder.glob("*.xml"))
        if not xml_files:
            self.logger.warning(f"XML файлы не найдены в папке: {self.input_folder}")
            return self.stats
        
        self.stats['total_files'] = len(xml_files)
        self.logger.info(f"Найдено {len(xml_files)} XML файлов")
          # Обрабатываем каждый файл
        all_processor_results = {}
        for xml_file in xml_files:
            try:
                file_results = self.process_single_file(xml_file)
                self.stats['processed_files'] += 1
                
                # Собираем результаты процессоров для общей финализации
                if 'processor_results' in file_results:
                    for processor_type, results in file_results['processor_results'].items():
                        if processor_type not in all_processor_results:
                            all_processor_results[processor_type] = {
                                'processed_tasks': 0,
                                'successful_tasks': 0, 
                                'failed_tasks': 0,
                                'files_created': {'py_files': 0, 'kum_files': 0},
                                'errors': []
                            }
                        
                        # Аккумулируем результаты
                        all_processor_results[processor_type]['processed_tasks'] += results.get('processed_tasks', 0)
                        all_processor_results[processor_type]['successful_tasks'] += results.get('successful_tasks', 0)
                        all_processor_results[processor_type]['failed_tasks'] += results.get('failed_tasks', 0)
                        
                        files_info = results.get('files_created', {})
                        all_processor_results[processor_type]['files_created']['py_files'] += files_info.get('py_files', 0)
                        all_processor_results[processor_type]['files_created']['kum_files'] += files_info.get('kum_files', 0)
                        
                        all_processor_results[processor_type]['errors'].extend(results.get('errors', []))
                        
            except Exception as e:
                error_msg = f"Ошибка при обработке файла {xml_file}: {str(e)}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        # Выполняем общую финализацию всех результатов
        if all_processor_results:
            try:
                self.logger.info("Выполняем финальную финализацию всех результатов")
                final_results = self.finalizer.finalize_results(self.output_folder, all_processor_results)
                self.stats['finalization_results'] = final_results
            except Exception as e:
                error_msg = f"Ошибка при финальной финализации: {str(e)}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        # Создаем итоговую статистику
        self.save_final_statistics()
        
        self.logger.info(f"Обработка завершена. Результаты в папке: {self.output_folder}")
        return self.stats
    
    def process_single_file(self, xml_file: Path) -> Dict[str, Any]:
        """
        Обрабатывает один XML файл.
        
        Args:
            xml_file: Путь к XML файлу
            
        Returns:
            Dict с результатами обработки файла
        """
        self.logger.info(f"Обрабатываем файл: {xml_file.name}")
        
        # Создаем выходную папку для этого файла
        file_output_dir = self.output_folder / xml_file.stem
        file_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Парсим XML
        tasks = self.parse_xml_file(xml_file)
        self.stats['total_tasks'] += len(tasks)
        
        # Группируем задачи по типам
        grouped_tasks = self.group_tasks_by_type(tasks)
        
        # Обрабатываем каждую группу задач специализированным процессором
        processed_results = {}
        for task_type, task_list in grouped_tasks.items():
            if task_type in self.processors:
                processor = self.processors[task_type]
                try:
                    results = processor.process_tasks(task_list, file_output_dir)
                    processed_results[task_type] = results
                    self.stats['processed_tasks'] += len(task_list)
                    
                    # Обновляем статистику по типам
                    if task_type not in self.stats['task_types']:
                        self.stats['task_types'][task_type] = 0
                    self.stats['task_types'][task_type] += len(task_list)
                    
                except Exception as e:
                    error_msg = f"Ошибка в процессоре {task_type}: {str(e)}"
                    self.logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
            else:
                self.logger.warning(f"Процессор для типа задач '{task_type}' не найден")        # Финализируем обработку файла
        file_results = self.finalizer.finalize_results(
            file_output_dir, processed_results
        )
        
        # Добавляем результаты процессоров для общей финализации
        file_results['processor_results'] = processed_results
        
        # Сохраняем результаты для этого файла
        self.save_file_results(file_output_dir, file_results)
        
        return file_results
    
    def parse_xml_file(self, xml_file: Path) -> List[Dict[str, Any]]:
        """
        Парсит XML файл и извлекает задачи.
        
        Args:
            xml_file: Путь к XML файлу
            
        Returns:
            Список задач
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            tasks = []
            
            # Ищем задачи в разных возможных структурах
            task_elements = []
            
            # Структура 1: прямые элементы TASK или TESTED_PRG
            task_elements.extend(root.findall(".//TASK"))
            task_elements.extend(root.findall(".//TESTED_PRG"))
            task_elements.extend(root.findall(".//USER_PRG"))
            
            for i, task_elem in enumerate(task_elements, 1):
                task_data = {
                    'id': str(i),
                    'xml_element': task_elem,
                    'title': self.extract_task_title(task_elem),
                    'student_code': self.extract_student_code(task_elem),
                    'test_data': self.extract_test_data(task_elem),
                    'source_file': xml_file.name
                }
                tasks.append(task_data)
            
            self.logger.info(f"Извлечено {len(tasks)} задач из файла {xml_file.name}")
            return tasks
            
        except ET.ParseError as e:
            self.logger.error(f"Ошибка парсинга XML файла {xml_file}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при парсинге {xml_file}: {str(e)}")
            return []
    
    def extract_task_title(self, task_elem) -> str:
        """Извлекает название задачи."""
        # Пробуем разные варианты
        title_elem = task_elem.find('title')
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        
        name_elem = task_elem.find('name')
        if name_elem is not None and name_elem.text:
            return name_elem.text.strip()
        
        # Извлекаем из атрибутов
        if 'title' in task_elem.attrib:
            return task_elem.attrib['title']
        if 'name' in task_elem.attrib:
            return task_elem.attrib['name']
        
        return f"Задача {task_elem.tag}"
    
    def extract_student_code(self, task_elem) -> str:
        """Извлекает ученический код из задачи."""
        # Ищем текст программы в разных местах
        code_elements = [
            task_elem.find('.//code'),
            task_elem.find('.//text'),
            task_elem.find('.//program'),
            task_elem.find('.//prg_text')
        ]
        
        for code_elem in code_elements:
            if code_elem is not None and code_elem.text:
                return code_elem.text.strip()
        
        # Если прямого текста нет, берем весь текст элемента
        if task_elem.text and task_elem.text.strip():
            return task_elem.text.strip()
        
        return ""
    
    def extract_test_data(self, task_elem) -> Dict[str, Any]:
        """Извлекает тестовые данные (дано/надо)."""
        test_data = {
            'input': [],
            'output': [],
            'examples': []
        }
        
        # Ищем блоки с тестовыми данными
        test_elements = task_elem.findall('.//test')
        for test_elem in test_elements:
            input_elem = test_elem.find('input')
            output_elem = test_elem.find('output')
            
            if input_elem is not None and output_elem is not None:
                test_data['examples'].append({
                    'input': input_elem.text.strip() if input_elem.text else '',
                    'output': output_elem.text.strip() if output_elem.text else ''
                })
        
        return test_data
    
    def group_tasks_by_type(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Группирует задачи по типам для обработки специализированными процессорами.
        
        Args:
            tasks: Список задач
            
        Returns:
            Dict с группировкой задач по типам
        """
        grouped = {
            'array': [],
            'string': [],
            'function': [],
            'robot': [],
            'algorithm': []
        }
        
        for task in tasks:
            task_type = self.detector.detect_task_type(task)
            if task_type in grouped:
                grouped[task_type].append(task)
            else:
                # По умолчанию относим к алгоритмическим задачам
                grouped['algorithm'].append(task)
        
        # Логируем статистику
        for task_type, task_list in grouped.items():
            if task_list:
                self.logger.info(f"Тип '{task_type}': {len(task_list)} задач")
        
        return grouped
    
    def save_file_results(self, output_dir: Path, results: Dict[str, Any]):
        """Сохраняет результаты обработки файла."""
        results_file = output_dir / "processing_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def save_final_statistics(self):
        """Сохраняет итоговую статистику обработки."""
        stats_file = self.output_folder / "mega_coordinator_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Итоговая статистика сохранена в {stats_file}")


def main():
    """Главная функция для запуска координатора."""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', '/?']:
        print("""
🚀 Мегапарсер КуМир - Модульная архитектура v2.0

ИСПОЛЬЗОВАНИЕ:
    python mega_coordinator.py <input_folder> [output_folder]

ПАРАМЕТРЫ:
    input_folder  - Папка с XML файлами курсов КуМир (обязательный)
    output_folder - Папка для результатов (опциональный, по умолчанию: 'parsed_xml_results')

ПРИМЕРЫ:
    python mega_coordinator.py ./courses
    python mega_coordinator.py ./courses ./results
    python mega_coordinator.py "C:\\Courses\\Polyakov" "C:\\Results"

ПОДРОБНЕЕ:
    Читайте README.md для полной документации
        """)
        sys.exit(0 if len(sys.argv) > 1 else 1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "parsed_xml_results"
    
    coordinator = MegaCoordinator(input_folder, output_folder)
    results = coordinator.process_all_files()
    
    print(f"\n=== ИТОГИ ОБРАБОТКИ ===")
    print(f"Обработано файлов: {results['processed_files']}/{results['total_files']}")
    print(f"Обработано задач: {results['processed_tasks']}/{results['total_tasks']}")
    print(f"Типы задач: {results['task_types']}")
    if results['errors']:
        print(f"Ошибки: {len(results['errors'])}")


if __name__ == "__main__":
    main()
