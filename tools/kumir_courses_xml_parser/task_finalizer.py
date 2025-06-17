#!/usr/bin/env python3
"""
Финализатор задач - компонент для итоговой обработки результатов.

Этот модуль собирает результаты всех специализированных процессоров
и формирует итоговые файлы для тестирования:
- Сводный pytest файл
- Сводный KuMir файл
- Документацию по задачам
- Конфигурационные файлы
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class TaskFinalizer:
    """
    Финализатор для обработки результатов всех процессоров задач.
    
    Собирает результаты, создает итоговые файлы для тестирования
    и документацию.
    """
    
    def __init__(self):
        """Инициализация финализатора."""
        self.logger = logging.getLogger(__name__)
        
    def finalize_results(self, output_dir: Path, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Финализирует результаты обработки всех процессоров.
        
        Args:
            output_dir: Директория для сохранения результатов
            all_results: Результаты всех процессоров
            
        Returns:
            Dict с информацией о созданных файлах
        """
        self.logger.info("Начинаем финализацию результатов")
        
        finalized = {
            'summary': self._create_summary(all_results),
            'files_created': [],
            'statistics': self._calculate_statistics(all_results),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Создаем сводный pytest файл
            pytest_file = self._create_consolidated_pytest(output_dir, all_results)
            if pytest_file:
                finalized['files_created'].append(str(pytest_file))
            
            # Создаем сводный KuMir файл  
            kumir_file = self._create_consolidated_kumir(output_dir, all_results)
            if kumir_file:
                finalized['files_created'].append(str(kumir_file))
            
            # Создаем документацию
            docs_file = self._create_documentation(output_dir, all_results)
            if docs_file:
                finalized['files_created'].append(str(docs_file))
            
            # Создаем конфигурационный файл
            config_file = self._create_test_config(output_dir, all_results)
            if config_file:
                finalized['files_created'].append(str(config_file))
            
            # Сохраняем сводку финализации
            summary_file = output_dir / "finalization_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(finalized, f, ensure_ascii=False, indent=2)
            finalized['files_created'].append(str(summary_file))
            
            self.logger.info(f"Финализация завершена. Создано {len(finalized['files_created'])} файлов")
            
        except Exception as e:
            self.logger.error(f"Ошибка при финализации: {str(e)}")
            finalized['error'] = str(e)
        
        return finalized
    
    def _create_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Создает сводку по всем результатам."""
        summary = {
            'total_processors': 0,
            'total_tasks': 0,
            'tasks_by_type': {},
            'files_by_type': {'py': 0, 'kum': 0},
            'successful_tasks': 0,
            'failed_tasks': 0
        }
        
        for processor_type, results in all_results.items():
            if isinstance(results, dict) and 'processed_tasks' in results:
                summary['total_processors'] += 1
                processed = results.get('processed_tasks', 0)
                summary['total_tasks'] += processed
                summary['tasks_by_type'][processor_type] = processed
                
                # Подсчитываем файлы
                files_info = results.get('files_created', {})
                summary['files_by_type']['py'] += files_info.get('py_files', 0)
                summary['files_by_type']['kum'] += files_info.get('kum_files', 0)
                
                # Подсчитываем успешные/неуспешные задачи
                summary['successful_tasks'] += results.get('successful_tasks', 0)
                summary['failed_tasks'] += results.get('failed_tasks', 0)
        
        return summary
    
    def _calculate_statistics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Вычисляет детальную статистику."""
        stats = {
            'processing_rate': 0.0,
            'success_rate': 0.0,
            'files_per_task': 0.0,
            'most_common_type': None,
            'least_common_type': None,
            'error_summary': []
        }
        
        summary = self._create_summary(all_results)
        total_tasks = summary['total_tasks']
        
        if total_tasks > 0:
            stats['processing_rate'] = (summary['successful_tasks'] / total_tasks) * 100
            stats['success_rate'] = (summary['successful_tasks'] / total_tasks) * 100
            
            total_files = summary['files_by_type']['py'] + summary['files_by_type']['kum']
            stats['files_per_task'] = total_files / total_tasks if total_tasks > 0 else 0
            
            # Находим самый и наименее популярный тип задач
            if summary['tasks_by_type']:
                sorted_types = sorted(summary['tasks_by_type'].items(), key=lambda x: x[1])
                stats['least_common_type'] = sorted_types[0][0] if sorted_types[0][1] > 0 else None
                stats['most_common_type'] = sorted_types[-1][0]
        
        # Собираем ошибки
        for processor_type, results in all_results.items():
            if isinstance(results, dict) and 'errors' in results:
                for error in results['errors']:
                    stats['error_summary'].append(f"{processor_type}: {error}")
        
        return stats
    
    def _create_consolidated_pytest(self, output_dir: Path, all_results: Dict[str, Any]) -> Optional[Path]:
        """Создает сводный pytest файл."""
        pytest_dir = output_dir / "consolidated_tests"
        pytest_dir.mkdir(parents=True, exist_ok=True)
        
        pytest_file = pytest_dir / "test_all_kumir_tasks.py"
        
        try:
            with open(pytest_file, 'w', encoding='utf-8') as f:
                f.write('#!/usr/bin/env python3\n')
                f.write('"""\n')
                f.write('Сводный тест для всех задач КуМир.\n')
                f.write(f'Сгенерирован автоматически: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write('"""\n\n')
                
                f.write('import pytest\n')
                f.write('import sys\n')
                f.write('import os\n')
                f.write('from pathlib import Path\n\n')
                
                f.write('# Добавляем пути к модулям задач\n')
                f.write('current_dir = Path(__file__).parent\n')
                f.write('sys.path.insert(0, str(current_dir.parent))\n\n')
                
                # Импортируем все тестовые модули
                f.write('# Импорты тестовых модулей\n')
                for processor_type, results in all_results.items():
                    if isinstance(results, dict) and results.get('processed_tasks', 0) > 0:
                        f.write(f'try:\n')
                        f.write(f'    from {processor_type}.py import test_{processor_type}_tasks\n')
                        f.write(f'except ImportError:\n')
                        f.write(f'    print(f"Не удалось импортировать тесты для {processor_type}")\n\n')
                
                # Создаем основной тестовый класс
                f.write('class TestAllKumirTasks:\n')
                f.write('    """Сводный класс для тестирования всех типов задач КуМир."""\n\n')
                
                # Добавляем методы для каждого типа задач
                for processor_type, results in all_results.items():
                    if isinstance(results, dict) and results.get('processed_tasks', 0) > 0:
                        processed_count = results.get('processed_tasks', 0)
                        f.write(f'    def test_{processor_type}_tasks(self):\n')
                        f.write(f'        """\n')
                        f.write(f'        Тестирует задачи типа {processor_type}.\n')
                        f.write(f'        Количество задач: {processed_count}\n')
                        f.write(f'        """\n')
                        f.write(f'        try:\n')
                        f.write(f'            test_{processor_type}_tasks()\n')
                        f.write(f'            print(f"✓ Тесты {processor_type} прошли успешно")\n')
                        f.write(f'        except Exception as e:\n')
                        f.write(f'            pytest.fail(f"Ошибка в тестах {processor_type}: {{e}}")\n\n')
                
                # Добавляем вспомогательные методы
                f.write('    @pytest.fixture(autouse=True)\n')
                f.write('    def setup_method(self):\n')
                f.write('        """Настройка перед каждым тестом."""\n')
                f.write('        print(f"\\n--- Запуск теста {self._testMethodName} ---")\n\n')
                
                f.write('if __name__ == "__main__":\n')
                f.write('    pytest.main([__file__, "-v"])\n')
            
            self.logger.info(f"Создан сводный pytest файл: {pytest_file}")
            return pytest_file
            
        except Exception as e:
            self.logger.error(f"Ошибка при создании pytest файла: {str(e)}")
            return None
    
    def _create_consolidated_kumir(self, output_dir: Path, all_results: Dict[str, Any]) -> Optional[Path]:
        """Создает сводный файл с примерами KuMir кода."""
        kumir_dir = output_dir / "consolidated_kumir"
        kumir_dir.mkdir(parents=True, exist_ok=True)
        
        kumir_file = kumir_dir / "all_tasks_examples.kum"
        
        try:
            with open(kumir_file, 'w', encoding='utf-8') as f:
                f.write('! Сводный файл с примерами решений задач КуМир\n')
                f.write(f'! Сгенерирован автоматически: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write('! ==========================================\n\n')
                
                for processor_type, results in all_results.items():
                    if isinstance(results, dict) and results.get('processed_tasks', 0) > 0:
                        processed_count = results.get('processed_tasks', 0)
                        
                        f.write(f'! ===== ЗАДАЧИ ТИПА: {processor_type.upper()} =====\n')
                        f.write(f'! Количество задач: {processed_count}\n')
                        f.write(f'! Описание: Задачи на {self._get_type_description(processor_type)}\n')
                        f.write('! ======================================\n\n')
                        
                        # Добавляем примеры кода для каждого типа
                        example_code = self._get_example_kumir_code(processor_type)
                        f.write(example_code)
                        f.write('\n! --------------------------------------\n\n')
                
                f.write('! Конец файла примеров\n')
            
            self.logger.info(f"Создан сводный KuMir файл: {kumir_file}")
            return kumir_file
            
        except Exception as e:
            self.logger.error(f"Ошибка при создании KuMir файла: {str(e)}")
            return None
    
    def _create_documentation(self, output_dir: Path, all_results: Dict[str, Any]) -> Optional[Path]:
        """Создает документацию по обработанным задачам."""
        docs_file = output_dir / "tasks_documentation.md"
        
        try:
            with open(docs_file, 'w', encoding='utf-8') as f:
                f.write('# Документация по обработанным задачам КуМир\n\n')
                f.write(f'**Дата генерации:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                
                # Общая статистика
                summary = self._create_summary(all_results)
                f.write('## Общая статистика\n\n')
                f.write(f'- **Всего процессоров:** {summary["total_processors"]}\n')
                f.write(f'- **Всего задач:** {summary["total_tasks"]}\n')
                f.write(f'- **Успешно обработано:** {summary["successful_tasks"]}\n')
                f.write(f'- **Не удалось обработать:** {summary["failed_tasks"]}\n')
                f.write(f'- **Создано Python файлов:** {summary["files_by_type"]["py"]}\n')
                f.write(f'- **Создано KuMir файлов:** {summary["files_by_type"]["kum"]}\n\n')
                
                # Детали по типам задач
                f.write('## Детали по типам задач\n\n')
                for processor_type, task_count in summary['tasks_by_type'].items():
                    if task_count > 0:
                        f.write(f'### {processor_type.title()} задачи\n\n')
                        f.write(f'**Количество:** {task_count}\n\n')
                        f.write(f'**Описание:** {self._get_type_description(processor_type)}\n\n')
                        
                        # Добавляем информацию о конкретных результатах
                        results = all_results.get(processor_type, {})
                        if isinstance(results, dict):
                            f.write('**Результаты обработки:**\n')
                            f.write(f'- Успешно: {results.get("successful_tasks", 0)}\n')
                            f.write(f'- Ошибки: {results.get("failed_tasks", 0)}\n')
                            
                            files_info = results.get('files_created', {})
                            f.write(f'- Python файлов: {files_info.get("py_files", 0)}\n')
                            f.write(f'- KuMir файлов: {files_info.get("kum_files", 0)}\n\n')
                            
                            # Показываем ошибки, если есть
                            errors = results.get('errors', [])
                            if errors:
                                f.write('**Ошибки:**\n')
                                for error in errors[:5]:  # Показываем только первые 5 ошибок
                                    f.write(f'- {error}\n')
                                if len(errors) > 5:
                                    f.write(f'- ... и еще {len(errors) - 5} ошибок\n')
                                f.write('\n')
                
                # Рекомендации
                f.write('## Рекомендации\n\n')
                stats = self._calculate_statistics(all_results)
                
                if stats['success_rate'] < 90:
                    f.write('⚠️ **Низкий процент успешной обработки задач.** ')
                    f.write('Рекомендуется проверить качество входных данных и логику парсеров.\n\n')
                
                if len(stats['error_summary']) > 0:
                    f.write('🔍 **Обнаружены ошибки обработки.** ')
                    f.write('Рекомендуется проанализировать логи и исправить выявленные проблемы.\n\n')
                
                f.write('## Использование результатов\n\n')
                f.write('1. **Для тестирования:** Используйте файлы в папке `consolidated_tests/`\n')
                f.write('2. **Для изучения:** Просмотрите примеры в папке `consolidated_kumir/`\n')
                f.write('3. **Для отладки:** Проверьте логи в соответствующих папках процессоров\n\n')
            
            self.logger.info(f"Создана документация: {docs_file}")
            return docs_file
            
        except Exception as e:
            self.logger.error(f"Ошибка при создании документации: {str(e)}")
            return None
    
    def _create_test_config(self, output_dir: Path, all_results: Dict[str, Any]) -> Optional[Path]:
        """Создает конфигурационный файл для тестирования."""
        config_file = output_dir / "test_config.json"
        
        try:
            config = {
                'test_configuration': {
                    'generated_at': datetime.now().isoformat(),
                    'total_tasks': self._create_summary(all_results)['total_tasks'],
                    'processors': []
                },
                'pytest_settings': {
                    'timeout': 30,
                    'verbose': True,
                    'capture': 'sys'
                },
                'kumir_settings': {
                    'encoding': 'utf-8',
                    'line_endings': 'unix'
                }
            }
            
            # Добавляем конфигурацию для каждого процессора
            for processor_type, results in all_results.items():
                if isinstance(results, dict) and results.get('processed_tasks', 0) > 0:
                    processor_config = {
                        'type': processor_type,
                        'task_count': results.get('processed_tasks', 0),
                        'success_rate': 0.0,
                        'test_files': [],
                        'kumir_files': []
                    }
                    
                    # Вычисляем процент успеха
                    successful = results.get('successful_tasks', 0)
                    total = results.get('processed_tasks', 0)
                    if total > 0:
                        processor_config['success_rate'] = (successful / total) * 100
                    
                    config['test_configuration']['processors'].append(processor_config)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Создан конфигурационный файл: {config_file}")
            return config_file
            
        except Exception as e:
            self.logger.error(f"Ошибка при создании конфигурации: {str(e)}")
            return None
    
    def _get_type_description(self, processor_type: str) -> str:
        """Возвращает описание типа задач."""
        descriptions = {
            'array': 'работу с массивами (заполнение, сортировка, поиск)',
            'string': 'работу со строками (поиск, замена, преобразования)',
            'function': 'функции и процедуры (вычисления, рекурсия)',
            'robot': 'исполнителя Робот (движение, закраска, лабиринты)',
            'algorithm': 'базовые алгоритмы (циклы, условия, вычисления)'
        }
        return descriptions.get(processor_type, 'различные алгоритмические задачи')
    
    def _get_example_kumir_code(self, processor_type: str) -> str:
        """Возвращает пример кода для типа задач."""
        examples = {
            'array': '''! Пример задачи на массивы
алг массив_пример
нач
  цел таб A[1:10]
  цел i
  нц для i от 1 до 10
    A[i] := случайное(1, 100)
  кц
  ! Вывод массива
  нц для i от 1 до 10
    вывод A[i], " "
  кц
кон''',
            
            'string': '''! Пример задачи на строки  
алг строка_пример
нач
  лит s := "Привет, мир!"
  цел длина := длин(s)
  вывод "Длина строки: ", длина, нс
  
  ! Поиск символа
  цел позиция := позиция_символа(s, "м")
  вывод "Позиция 'м': ", позиция, нс
кон''',
            
            'function': '''! Пример функции
алг цел факториал(цел n)
нач
  если n <= 1
    то знач := 1
    иначе знач := n * факториал(n-1)
  все
кон

алг функция_пример
нач
  цел результат := факториал(5)
  вывод "5! = ", результат, нс
кон''',
            
            'robot': '''! Пример задачи с Роботом
использовать Робот
алг робот_пример  
нач
  нц пока не стена_справа
    вправо
    нц пока не стена_снизу
      вниз
      закрасить
    кц
  кц
кон''',
            
            'algorithm': '''! Пример алгоритмической задачи
алг алгоритм_пример
нач
  цел n, сумма := 0, i
  вывод "Введите n: "
  ввод n
  
  нц для i от 1 до n
    сумма := сумма + i
  кц
  
  вывод "Сумма чисел от 1 до ", n, " = ", сумма, нс
кон'''
        }
        
        return examples.get(processor_type, '! Пример задачи\nалг пример\nнач\n  ! Код задачи\nкон')
