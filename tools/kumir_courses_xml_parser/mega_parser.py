#!/usr/bin/env python3
"""
Универсальный мегапарсер для обработки множественных XML файлов КУМИРа.

Этот скрипт принимает на вход папку с любым количеством XML-файлов,
для каждого XML-файла создает отдельную директорию (по имени xml-файла),
внутри которой генерирует Python решения с правильными короткими именами.

Структура выходных данных:
input_folder/
├── file1.xml
├── file2.xml
└── file3.xml

output_folder/
├── file1/
│   ├── tasks_data.json
│   ├── python_solutions/
│   │   ├── task_10_arr_fill_zeros.py
│   │   ├── task_11_arr_fill_natural.py
│   │   └── ...
│   └── reports/
│       ├── test_results.json
│       └── comparison_framework.json
├── file2/
│   └── ... (аналогично)
└── file3/
    └── ... (аналогично)
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from kumir_pipeline import KumirToPythonPipeline


class MegaParser:
    """Универсальный мегапарсер для обработки множественных XML файлов КУМИРа."""
    
    def __init__(self, input_folder: str, output_folder: str = "parsed_xml_results"):
        """
        Инициализация мегапарсера.
        
        Args:
            input_folder: Папка с XML файлами
            output_folder: Папка для результатов (по умолчанию "parsed_xml_results")
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        
        # Создаем выходную папку
        self.output_folder.mkdir(exist_ok=True)
        
        # Настройка логирования
        self.setup_logging()
        
        # Статистика обработки
        self.stats = {
            'total_xml_files': 0,
            'processed_successfully': 0,
            'failed_processing': 0,
            'failed_files': []
        }
    
    def setup_logging(self):
        """Настройка системы логирования."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.output_folder / 'mega_parser.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_input_folder(self) -> bool:
        """
        Проверяет существование входной папки и наличие XML файлов.
        
        Returns:
            bool: True если папка существует и содержит XML файлы
        """
        if not self.input_folder.exists():
            self.logger.error(f"❌ Входная папка не найдена: {self.input_folder}")
            return False
        
        if not self.input_folder.is_dir():
            self.logger.error(f"❌ Путь не является папкой: {self.input_folder}")
            return False
        
        xml_files = self.find_xml_files()
        if not xml_files:
            self.logger.error(f"❌ В папке {self.input_folder} не найдено XML файлов")
            return False
        
        self.logger.info(f"✅ Найдено {len(xml_files)} XML файлов для обработки")
        return True
    
    def find_xml_files(self) -> List[Path]:
        """
        Находит все XML файлы во входной папке.
        
        Returns:
            List[Path]: Список путей к XML файлам
        """
        xml_files = []
        
        # Ищем XML файлы в корневой папке
        for file_path in self.input_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.xml':
                xml_files.append(file_path)
        
        # Ищем XML файлы в подпапках (один уровень вложенности)
        for subfolder in self.input_folder.iterdir():
            if subfolder.is_dir():
                for file_path in subfolder.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() == '.xml':
                        xml_files.append(file_path)
        
        # Сортируем по имени файла
        xml_files.sort(key=lambda x: x.name.lower())
        
        return xml_files
    
    def get_output_directory_name(self, xml_file_path: Path) -> str:
        """
        Создает имя выходной директории на основе имени XML файла.
        
        Args:
            xml_file_path: Путь к XML файлу
            
        Returns:
            str: Имя директории (без расширения .xml)
        """
        return xml_file_path.stem
    
    def create_output_structure(self):
        """Создает структуру выходных папок."""
        try:
            self.output_folder.mkdir(exist_ok=True)
            self.logger.info(f"📁 Создана выходная папка: {self.output_folder}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания выходной папки: {e}")
            raise
    
    def process_single_xml_file(self, xml_file_path: Path) -> bool:
        """
        Обрабатывает один XML файл.
        
        Args:
            xml_file_path: Путь к XML файлу
            
        Returns:
            bool: True если обработка прошла успешно
        """
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🔄 Обработка файла: {xml_file_path.name}")
        
        # Создаем имя выходной директории
        output_dir_name = self.get_output_directory_name(xml_file_path)
        output_dir_path = self.output_folder / output_dir_name
        
        try:
            # Создаем pipeline для обработки этого XML файла
            pipeline = KumirToPythonPipeline(
                xml_file_path=str(xml_file_path),
                output_dir=str(output_dir_path)
            )
            
            # Запускаем полную обработку
            success = pipeline.run_full_pipeline()
            
            if success:
                self.logger.info(f"✅ Файл {xml_file_path.name} обработан успешно")
                self.logger.info(f"📁 Результаты сохранены в: {output_dir_path}")
                return True
            else:
                self.logger.error(f"❌ Ошибка обработки файла {xml_file_path.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Исключение при обработке {xml_file_path.name}: {e}")
            return False
    
    def create_summary_report(self):
        """Создает сводный отчет по всем обработанным файлам."""
        summary_data = {
            'processing_summary': self.stats,
            'output_structure': self.get_output_structure_info(),
            'recommendations': self.get_recommendations()
        }
        
        summary_file = self.output_folder / 'mega_parser_summary.json'
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"📊 Сводный отчет сохранен: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания сводного отчета: {e}")
    
    def get_output_structure_info(self) -> Dict[str, Any]:
        """Получает информацию о структуре выходных папок."""
        structure_info = {
            'total_directories': 0,
            'directories': []
        }
        
        try:
            for item in self.output_folder.iterdir():
                if item.is_dir() and item.name != '__pycache__':
                    dir_info = {
                        'name': item.name,
                        'path': str(item),
                        'has_tasks_data': (item / 'tasks_data.json').exists(),
                        'has_python_solutions': (item / 'python_solutions').exists(),
                        'has_reports': (item / 'reports').exists(),
                        'python_files_count': self.count_python_files(item / 'python_solutions')
                    }
                    structure_info['directories'].append(dir_info)
                    structure_info['total_directories'] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа структуры выходных папок: {e}")
        
        return structure_info
    
    def count_python_files(self, python_dir: Path) -> int:
        """Подсчитывает количество Python файлов в папке."""
        if not python_dir.exists():
            return 0
        
        try:
            return len([f for f in python_dir.iterdir() 
                       if f.is_file() and f.suffix == '.py'])
        except:
            return 0
    
    def get_recommendations(self) -> List[str]:
        """Генерирует рекомендации на основе результатов обработки."""
        recommendations = []
        
        if self.stats['failed_processing'] > 0:
            recommendations.append(
                f"⚠️  {self.stats['failed_processing']} файлов не удалось обработать. "
                "Проверьте логи для получения подробной информации."
            )
        
        if self.stats['processed_successfully'] > 0:
            recommendations.append(
                f"✅ {self.stats['processed_successfully']} файлов обработано успешно. "
                "Проверьте созданные Python решения в соответствующих папках."
            )
        
        recommendations.append(
            "📝 Для каждой папки доступны: tasks_data.json (данные задач), "
            "python_solutions/ (Python решения), reports/ (отчеты и тесты)."
        )
        
        return recommendations
    
    def print_final_summary(self):
        """Выводит финальную сводку результатов."""
        print("\n" + "=" * 80)
        print("🎯 ИТОГОВЫЙ ОТЧЕТ МЕГАПАРСЕРА")
        print("=" * 80)
        print(f"📁 Входная папка: {self.input_folder}")
        print(f"📁 Выходная папка: {self.output_folder}")
        print(f"📊 Всего XML файлов: {self.stats['total_xml_files']}")
        print(f"✅ Обработано успешно: {self.stats['processed_successfully']}")
        print(f"❌ Ошибок обработки: {self.stats['failed_processing']}")
        
        if self.stats['failed_files']:
            print(f"\n❌ Файлы с ошибками:")
            for failed_file in self.stats['failed_files']:
                print(f"   - {failed_file}")
        
        if self.stats['processed_successfully'] > 0:
            print(f"\n📂 Структура результатов:")
            print(f"   {self.output_folder}/")
            try:
                for item in self.output_folder.iterdir():
                    if item.is_dir() and item.name not in ['__pycache__', '.git']:
                        print(f"   ├── {item.name}/")
                        if (item / 'python_solutions').exists():
                            py_count = self.count_python_files(item / 'python_solutions')
                            print(f"   │   ├── python_solutions/ ({py_count} файлов)")
                        if (item / 'tasks_data.json').exists():
                            print(f"   │   ├── tasks_data.json")
                        if (item / 'reports').exists():
                            print(f"   │   └── reports/")
            except:
                pass
        
        print("=" * 80)
    
    def run_mega_parser(self) -> bool:
        """
        Запускает полную обработку всех XML файлов.
        
        Returns:
            bool: True если обработка завершена успешно
        """
        print("🚀 ЗАПУСК УНИВЕРСАЛЬНОГО МЕГАПАРСЕРА")
        print("=" * 60)
        
        # Проверяем входную папку
        if not self.validate_input_folder():
            return False
        
        # Создаем структуру выходных папок
        try:
            self.create_output_structure()
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка создания структуры: {e}")
            return False
        
        # Находим все XML файлы
        xml_files = self.find_xml_files()
        self.stats['total_xml_files'] = len(xml_files)
        
        self.logger.info(f"🔍 Найдено XML файлов для обработки: {len(xml_files)}")
        
        # Обрабатываем каждый XML файл
        for xml_file in xml_files:
            try:
                success = self.process_single_xml_file(xml_file)
                
                if success:
                    self.stats['processed_successfully'] += 1
                else:
                    self.stats['failed_processing'] += 1
                    self.stats['failed_files'].append(xml_file.name)
                    
            except KeyboardInterrupt:
                self.logger.warning("⏹️  Обработка прервана пользователем")
                break
            except Exception as e:
                self.logger.error(f"❌ Неожиданная ошибка при обработке {xml_file.name}: {e}")
                self.stats['failed_processing'] += 1
                self.stats['failed_files'].append(xml_file.name)
        
        # Создаем сводный отчет
        self.create_summary_report()
        
        # Выводим финальную сводку
        self.print_final_summary()
        
        # Определяем успешность выполнения
        success = self.stats['processed_successfully'] > 0
        
        if success:
            self.logger.info("🎉 Мегапарсер завершил работу успешно!")
        else:
            self.logger.error("❌ Мегапарсер не смог обработать ни одного файла")
        
        return success


def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("❌ Использование: python mega_parser.py <input_folder> [output_folder]")
        print("\nПримеры:")
        print("  python mega_parser.py xml_files/")
        print("  python mega_parser.py xml_files/ results/")
        print("  python mega_parser.py C:/path/to/xml/files/ D:/output/")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "parsed_xml_results"
    
    if not os.path.exists(input_folder):
        print(f"❌ Входная папка не найдена: {input_folder}")
        sys.exit(1)
    
    # Создаем и запускаем мегапарсер
    mega_parser = MegaParser(input_folder, output_folder)
    success = mega_parser.run_mega_parser()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
