#!/usr/bin/env python3
"""
Мегатест парсера на всех курсах Полякова
Тестирует все XML файлы в папке polyakov_kurs_work и записывает подробный лог
"""

import os
import subprocess
import time
from pathlib import Path
import json

def run_parser_on_file(xml_file_path):
    """Запускает парсер на одном XML файле и возвращает результаты."""
    print(f"\n🚀 Тестирование: {xml_file_path.name}")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        # Запускаем парсер
        result = subprocess.run([
            'python3', 'kumir_pipeline.py', str(xml_file_path)
        ], capture_output=True, text=True, timeout=300)  # 5 минут таймаут
        
        end_time = time.time()
        duration = end_time - start_time
        
        success = result.returncode == 0
        output = result.stdout
        errors = result.stderr
        
        # Извлекаем статистику из вывода
        tasks_created = 0
        tasks_tested = 0
        success_rate = 0
        
        if "Создано" in output:
            try:
                line = [l for l in output.split('\n') if 'Создано' in l][0]
                parts = line.split('/')
                if len(parts) >= 2:
                    tasks_created = int(parts[0].split()[-1])
            except:
                pass
        
        if "Результаты:" in output:
            try:
                lines = output.split('\n')
                result_line = None
                for line in lines:
                    if 'Результаты:' in line and '/' in line:
                        result_line = line
                        break
                
                if result_line:
                    # Формат: "📊 Результаты: 139/209 (66.5%)"
                    import re
                    match = re.search(r'(\d+)/(\d+)\s*\(([0-9.]+)%\)', result_line)
                    if match:
                        success_count = int(match.group(1))
                        total_count = int(match.group(2))
                        success_rate = float(match.group(3))
                        tasks_tested = total_count
            except Exception as e:
                print(f"Ошибка парсинга результатов для {xml_file_path.name}: {e}")
                pass
        
        return {
            'file': xml_file_path.name,
            'success': success,
            'duration': duration,
            'tasks_created': tasks_created,
            'tasks_tested': tasks_tested,
            'success_rate': success_rate,
            'output': output,
            'errors': errors
        }
        
    except subprocess.TimeoutExpired:
        return {
            'file': xml_file_path.name,
            'success': False,
            'duration': 300,
            'tasks_created': 0,
            'tasks_tested': 0,
            'success_rate': 0,
            'output': '',
            'errors': 'TIMEOUT: Превышен лимит времени (5 минут)'
        }
    except Exception as e:
        return {
            'file': xml_file_path.name,
            'success': False,
            'duration': 0,
            'tasks_created': 0,
            'tasks_tested': 0,
            'success_rate': 0,
            'output': '',
            'errors': f'EXCEPTION: {str(e)}'
        }

def main():
    """Главная функция для тестирования всех курсов."""
    polyakov_dir = Path('/Users/bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work')
    
    if not polyakov_dir.exists():
        print(f"❌ Папка {polyakov_dir} не найдена!")
        return
    
    # Найти все XML файлы
    xml_files = list(polyakov_dir.glob('*.xml'))
    if not xml_files:
        print(f"❌ XML файлы в папке {polyakov_dir} не найдены!")
        return
    
    print(f"🔍 Найдено {len(xml_files)} XML файлов для тестирования")
    print(f"📁 Папка: {polyakov_dir}")
    
    results = []
    total_start_time = time.time()
    
    # Тестируем каждый файл
    for xml_file in sorted(xml_files):
        # Очищаем результаты предыдущего запуска
        subprocess.run(['rm', '-rf', 'kumir_python_solutions'], capture_output=True)
        
        result = run_parser_on_file(xml_file)
        results.append(result)
        
        # Показываем краткие результаты
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['file']}: {result['tasks_created']} задач, {result['success_rate']:.1f}% успех, {result['duration']:.1f}с")
        
        if not result['success'] and result['errors']:
            print(f"   Ошибка: {result['errors'][:200]}...")
    
    total_duration = time.time() - total_start_time
    
    # Создаём подробный отчёт
    create_detailed_report(results, total_duration)
    
    # Показываем общую статистику
    print_summary(results, total_duration)

def create_detailed_report(results, total_duration):
    """Создаёт подробный отчёт в файле."""
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    report_file = f'polyakov_test_report_{timestamp}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Отчёт тестирования парсера Kumir на курсах Полякова\n\n")
        f.write(f"**Дата:** {time.strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"**Общее время:** {total_duration:.1f} секунд\n")
        f.write(f"**Протестировано файлов:** {len(results)}\n\n")
        
        # Общая статистика
        successful = sum(1 for r in results if r['success'])
        total_tasks_created = sum(r['tasks_created'] for r in results)
        total_tasks_tested = sum(r['tasks_tested'] for r in results)
        avg_success_rate = sum(r['success_rate'] for r in results if r['success']) / max(successful, 1)
        
        f.write(f"## 📊 Общая статистика\n\n")
        f.write(f"- **Успешно обработано:** {successful}/{len(results)} файлов ({successful/len(results)*100:.1f}%)\n")
        f.write(f"- **Всего задач создано:** {total_tasks_created}\n")
        f.write(f"- **Всего задач протестировано:** {total_tasks_tested}\n")
        f.write(f"- **Средний процент успеха:** {avg_success_rate:.1f}%\n\n")
        
        # Детальные результаты по файлам
        f.write(f"## 📋 Детальные результаты\n\n")
        
        for result in results:
            status = "✅ УСПЕХ" if result['success'] else "❌ НЕУДАЧА"
            f.write(f"### {status}: {result['file']}\n\n")
            f.write(f"- **Время выполнения:** {result['duration']:.1f}с\n")
            f.write(f"- **Задач создано:** {result['tasks_created']}\n")
            f.write(f"- **Задач протестировано:** {result['tasks_tested']}\n")
            f.write(f"- **Процент успеха:** {result['success_rate']:.1f}%\n")
            
            if result['errors']:
                f.write(f"- **Ошибки:**\n```\n{result['errors']}\n```\n")
            
            # Показываем последние строки вывода для понимания результата
            if result['output']:
                lines = result['output'].split('\n')
                last_lines = [l for l in lines[-10:] if l.strip()]
                if last_lines:
                    f.write(f"- **Последние строки вывода:**\n```\n")
                    f.write('\n'.join(last_lines))
                    f.write(f"\n```\n")
            
            f.write(f"\n---\n\n")
        
        # Топ и проблемные файлы
        successful_results = [r for r in results if r['success']]
        if successful_results:
            best = max(successful_results, key=lambda x: x['success_rate'])
            f.write(f"## 🏆 Лучший результат\n\n")
            f.write(f"**{best['file']}**: {best['success_rate']:.1f}% ({best['tasks_tested']} задач)\n\n")
        
        failed_results = [r for r in results if not r['success']]
        if failed_results:
            f.write(f"## ⚠️ Проблемные файлы\n\n")
            for fail in failed_results:
                f.write(f"- **{fail['file']}**: {fail['errors'][:100]}...\n")
            f.write(f"\n")
    
    print(f"\n📄 Подробный отчёт сохранён: {report_file}")

def print_summary(results, total_duration):
    """Выводит краткую сводку результатов."""
    print(f"\n" + "=" * 80)
    print(f"🎯 ИТОГОВАЯ СВОДКА ТЕСТИРОВАНИЯ ПАРСЕРА")
    print(f"=" * 80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"📁 Протестировано файлов: {len(results)}")
    print(f"✅ Успешно: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"❌ Неудачно: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print(f"⏱️  Общее время: {total_duration:.1f} секунд")
    
    if successful:
        total_tasks_created = sum(r['tasks_created'] for r in successful)
        total_tasks_tested = sum(r['tasks_tested'] for r in successful)
        avg_success_rate = sum(r['success_rate'] for r in successful) / len(successful)
        
        print(f"\n📊 Статистика по задачам:")
        print(f"   Всего задач создано: {total_tasks_created}")
        print(f"   Всего задач протестировано: {total_tasks_tested}")
        print(f"   Средний процент успеха: {avg_success_rate:.1f}%")
        
        # Лучшие результаты
        best = max(successful, key=lambda x: x['success_rate'])
        print(f"\n🏆 Лучший результат: {best['file']} ({best['success_rate']:.1f}%)")
        
        # Худшие из успешных
        if len(successful) > 1:
            worst_successful = min(successful, key=lambda x: x['success_rate'])
            print(f"⚠️  Худший успешный: {worst_successful['file']} ({worst_successful['success_rate']:.1f}%)")
    
    if failed:
        print(f"\n❌ Неудачные файлы:")
        for fail in failed:
            error_short = fail['errors'].split('\n')[0][:60] if fail['errors'] else 'Неизвестная ошибка'
            print(f"   {fail['file']}: {error_short}...")
    
    print(f"\n🎉 Тестирование завершено!")

if __name__ == '__main__':
    main()
