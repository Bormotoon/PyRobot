#!/usr/bin/env python3
"""
Генератор тестов для курсов Полякова.

Парсит .kurs.xml и .work.xml файлы, извлекает эталонные решения из атрибута 'prg'
элементов <USER_PRG>/<TESTED_PRG>, и создает pytest-тесты для проверки интерпретатора КуМир.

Основано на анализе структуры XML из kurs_test_gen_info.md.
"""

import xml.etree.ElementTree as ET
import re
import html
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Константы
POLYAKOV_KURS_WORK_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work")
GENERATED_TESTS_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/generated_course_tests")
TEST_TEMPLATE_PATH = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/test_polyakov_kum.py")

# Убедимся, что директория для тестов существует
GENERATED_TESTS_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    """Очищает имя файла от недопустимых символов для файловой системы."""
    # Удаляем недопустимые символы для имен файлов
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Заменяем пробелы на подчеркивания
    name = name.replace(" ", "_")
    # Удаляем множественные подчеркивания
    name = re.sub(r'_+', '_', name)
    # Убираем подчеркивания в начале и конце
    name = name.strip('_')
    return name if name else "unnamed"


def parse_kurs_xml(kurs_file_path: Path) -> Dict[str, Dict[str, str]]:
    """
    Парсит .kurs.xml файл и извлекает информацию о задачах.
    
    Returns:
        Dict[task_id, {name: str, id: str}]
    """
    tasks: Dict[str, Dict[str, str]] = {}
    
    try:
        tree = ET.parse(kurs_file_path)
        root = tree.getroot()
        
        # Ищем все элементы <T> с атрибутом id
        for task_node in root.findall(".//T[@id]"):
            task_id = task_node.get("id")
            if not task_id:
                continue
                
            # Проверяем, что это действительно задача (имеет <PROGRAM>)
            program_node = task_node.find("PROGRAM")
            if program_node is None or not program_node.text or not program_node.text.strip():
                continue
                
            # Получаем имя задачи
            task_name = None
            
            # Сначала пробуем из xml:name
            if task_name is None:
                task_name = task_node.get("{http://www.w3.org/XML/1998/namespace}name")
            
            # Потом из обычного name
            if task_name is None:
                task_name = task_node.get("name")
            
            # Если имя слишком техническое (типа "1-0"), ищем в описании
            if task_name is None or re.fullmatch(r"\d+-\d+", task_name):
                desc_node = task_node.find("DESC")
                if desc_node is not None and desc_node.text:
                    # Очищаем от HTML тегов и берем первое предложение
                    desc_text = re.sub(r'<[^>]+>', '', desc_node.text.strip())
                    first_sentence = desc_text.split('.')[0].strip()
                    if first_sentence:
                        task_name = first_sentence
            
            # Если все еще нет имени, генерируем стандартное
            if not task_name:
                task_name = f"Задача_{task_id}"
                
            tasks[task_id] = {
                "name": task_name,
                "id": task_id
            }
            
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга XML файла {kurs_file_path}: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка при парсинге {kurs_file_path}: {e}")
    
    return tasks


def clean_kumir_code_from_prg(raw_prg: str) -> str:
    """
    Очищает код КуМир из атрибута 'prg' согласно kurs_test_gen_info.md:
    1. Декодирует HTML-сущности
    2. Удаляет маркеры |@protected и |@hidden
    """
    # Декодируем HTML-сущности
    cleaned = html.unescape(raw_prg)
    
    # Удаляем маркеры защиты/скрытия
    cleaned = re.sub(r'\|@(protected|hidden)', '', cleaned)
    
    # Убираем лишние пустые строки
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    
    return cleaned.strip()


def extract_task_name_from_kumir_code(kumir_code: str) -> Optional[str]:
    """Извлекает название задачи из первой строки алгоритма."""
    lines = kumir_code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('алг ') and '(' in line:
            # Извлекаем название между "алг " и "("
            match = re.match(r'алг\s+([^(]+)', line)
            if match:
                return match.group(1).strip()
    return None


def parse_work_xml(work_file_path: Path, tasks_info: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """
    Парсит .work.xml файл и извлекает решения для задач.
    
    Ищет элементы <USER_PRG> и <TESTED_PRG> с атрибутом 'prg',
    согласно структуре, описанной в kurs_test_gen_info.md.
    
    Returns:
        Dict[task_id, cleaned_kumir_code]
    """
    solutions: Dict[str, str] = {}
    
    try:
        tree = ET.parse(work_file_path)
        root = tree.getroot()
        
        # Ищем элементы USER_PRG и TESTED_PRG
        for element_name in ["USER_PRG", "TESTED_PRG"]:
            for prg_element in root.findall(f".//{element_name}[@testId][@prg]"):
                test_id = prg_element.get("testId")
                raw_prg = prg_element.get("prg")
                
                if not test_id or not raw_prg:
                    continue
                    
                # Проверяем, что это задача из нашего курса
                if test_id not in tasks_info:
                    print(f"⚠️  Найдено решение для неизвестной задачи {test_id} в {work_file_path.name}")
                    continue
                
                # Очищаем код согласно info-файлу
                cleaned_code = clean_kumir_code_from_prg(raw_prg)
                
                if cleaned_code:
                    solutions[test_id] = cleaned_code
                    print(f"✅ Извлечено решение для задачи {test_id}: {tasks_info[test_id]['name']}")
                else:
                    print(f"⚠️  Пустое решение для задачи {test_id}")
        
        # Приоритет TESTED_PRG над USER_PRG если есть оба (обычно они идентичны)
                    
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга XML файла {work_file_path}: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка при парсинге {work_file_path}: {e}")
    
    return solutions


def generate_test_file_content(course_name: str, tasks_with_solutions: Dict[str, Dict[str, str]]) -> str:
    """
    Генерирует содержимое файла с pytest-тестами для курса.
    
    Args:
        course_name: Имя курса
        tasks_with_solutions: Dict[task_id, {name, id, solution?}]
    """
    
    # Читаем шаблон тестов
    try:
        with open(TEST_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"❌ Файл шаблона {TEST_TEMPLATE_PATH} не найден")
        return ""
    except Exception as e:
        print(f"❌ Ошибка чтения шаблона: {e}")
        return ""
    
    # Генерируем тестовые функции
    test_functions = []
    
    for task_id, data in tasks_with_solutions.items():
        task_name = data["name"]
        solution_code = data.get("solution", "")
        
        if not solution_code:
            print(f"⚠️  Пропускаем задачу '{task_name}' (ID: {task_id}) - нет решения")
            continue
        
        # Создаем безопасное имя для функции теста
        safe_course_name = sanitize_filename(course_name)
        safe_task_name = sanitize_filename(task_name)
        test_func_name = f"test_{safe_course_name}_{safe_task_name}_{task_id}"
        
        # Экранируем код для Python строки
        escaped_code = solution_code.replace('\\', '\\\\').replace("'''", "\\'\\'\\'")
        
        # Генерируем функцию теста
        test_function = f'''
def {test_func_name}(run_kumir_code_func, tmp_path):
    """
    Тест для задачи: {task_name} (ID: {task_id})
    Курс: {course_name}
    
    Ожидаемый результат: "Задание зачтено."
    """
    kumir_code = """{escaped_code}"""
    
    file_path = tmp_path / "{safe_course_name}_{safe_task_name}_{task_id}.kum"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    result = run_kumir_code_func(str(file_path))
    
    # Проверяем успешное выполнение
    assert result.return_code == 0, f"Код завершился с ошибкой: {{result.stderr_output}}"
    
    # Проверяем ожидаемый вывод
    expected_output = "Задание зачтено.\\n"
    assert result.stdout_output == expected_output, f"Неожиданный вывод.\\nОжидалось: {{expected_output!r}}\\nПолучено: {{result.stdout_output!r}}"
'''
        
        test_functions.append(test_function)
    
    if not test_functions:
        print(f"⚠️  Нет тестов для генерации в курсе {course_name}")
        return ""
    
    # Собираем итоговый файл
    # Берем шаблон и добавляем наши тесты в конец
    final_content = template_content.rstrip() + "\n\n"
    final_content += f"# Автогенерированные тесты для курса: {course_name}\n"
    final_content += f"# Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    final_content += "\n".join(test_functions)
    final_content += "\n"
    
    return final_content


def main():
    """Главная функция генератора тестов."""
    start_time = datetime.now()
    print(f"🚀 [{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Начинаем генерацию тестов...")
    print(f"📁 Исходная директория: {POLYAKOV_KURS_WORK_DIR}")
    print(f"📁 Целевая директория: {GENERATED_TESTS_DIR}")
    
    course_count = 0
    generated_files_count = 0
    total_tests_count = 0
    
    # Обрабатываем каждый курс
    for course_dir in POLYAKOV_KURS_WORK_DIR.iterdir():
        if not course_dir.is_dir():
            continue
            
        course_name = course_dir.name
        print(f"\n📚 Обрабатываем курс: {course_name}")
        
        # Ищем .kurs.xml файл
        kurs_file = None
        for pattern in [f"{course_name}.kurs.xml", "*.kurs.xml"]:
            matches = list(course_dir.glob(pattern))
            if matches:
                kurs_file = matches[0]
                break
        
        if not kurs_file:
            print(f"❌ Не найден .kurs.xml файл в {course_dir}")
            continue
        
        # Ищем .work.xml файл
        work_file = None
        for pattern in [f"Поляков_{course_name}.work.xml", "*.work.xml"]:
            matches = list(course_dir.glob(pattern))
            if matches:
                work_file = matches[0]
                break
        
        if not work_file:
            print(f"❌ Не найден .work.xml файл в {course_dir}")
            continue
        
        print(f"📄 Курс: {kurs_file.name}")
        print(f"📄 Решения: {work_file.name}")
        
        # Парсим файлы
        tasks_info = parse_kurs_xml(kurs_file)
        if not tasks_info:
            print(f"❌ Не найдено задач в {kurs_file.name}")
            continue
        
        print(f"📝 Найдено задач в курсе: {len(tasks_info)}")
        
        solutions = parse_work_xml(work_file, tasks_info)
        print(f"✅ Извлечено решений: {len(solutions)}")
        
        # Объединяем данные
        tasks_with_solutions = {}
        for task_id, task_data in tasks_info.items():
            combined_data = task_data.copy()
            if task_id in solutions:
                combined_data["solution"] = solutions[task_id]
            tasks_with_solutions[task_id] = combined_data
        
        # Генерируем тесты
        test_content = generate_test_file_content(course_name, tasks_with_solutions)
        if not test_content:
            print(f"❌ Не удалось сгенерировать тесты для {course_name}")
            continue
        
        # Сохраняем файл
        test_file_name = f"test_{sanitize_filename(course_name)}.py"
        test_file_path = GENERATED_TESTS_DIR / test_file_name
        
        try:
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(test_content)
            
            tests_in_file = len([task for task in tasks_with_solutions.values() if "solution" in task])
            print(f"✅ Сгенерирован файл: {test_file_path.name} ({tests_in_file} тестов)")
            
            generated_files_count += 1
            total_tests_count += tests_in_file
            
        except Exception as e:
            print(f"❌ Ошибка записи {test_file_path}: {e}")
        
        course_count += 1
    
    # Итоговая статистика
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n🎉 [{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Генерация завершена!")
    print(f"📊 Обработано курсов: {course_count}")
    print(f"📊 Сгенерировано файлов: {generated_files_count}")
    print(f"📊 Всего тестов: {total_tests_count}")
    print(f"⏱️  Время выполнения: {duration}")


if __name__ == "__main__":
    main()
