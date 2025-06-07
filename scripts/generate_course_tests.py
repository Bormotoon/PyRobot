import os
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Dict, List, Optional # Убрал Any

# Константы
POLYAKOV_KURS_WORK_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work")
GENERATED_TESTS_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/generated_course_tests")
TEST_TEMPLATE_PATH = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/test_polyakov_kum.py")

GENERATED_TESTS_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str) -> str:
    """Очищает имя файла от недопустимых символов."""
    name = re.sub(r'[\/*?:"<>|]',"", name)
    name = name.replace(" ", "_")
    return name

def parse_kurs_xml(kurs_file_path: Path) -> Dict[str, Dict[str, str]]:
    """Парсит .kurs.xml файл и извлекает информацию о задачах."""
    tasks: Dict[str, Dict[str, str]] = {}
    try:
        tree = ET.parse(kurs_file_path)
        root = tree.getroot()
        # Ищем задачи внутри разделов <T>
        # Пространство имен xml может присутствовать, поэтому используем его в поиске
        # namespaces = {'xml': 'http://www.w3.org/XML/1998/namespace'} # Не всегда нужно явно
        
        # Сначала найдем все элементы <T>, которые являются разделами или уроками
        # А потом уже внутри них будем искать <task>
        # Элементы <T> могут быть вложенными. Будем искать <task> на любом уровне вложенности внутри <KURS>
        for task_element in root.findall(".//T[@xml:id][@xml:name]/T[@xml:id][@xml:name]"): # Ищем подуроки с задачами
            task_id = task_element.get("{http://www.w3.org/XML/1998/namespace}id")
            task_name_from_attr = task_element.get("{http://www.w3.org/XML/1998/namespace}name")
            
            # Если не нашли с пространством имен, пробуем без него (на случай разного форматирования XML)
            if not task_id:
                task_id = task_element.get("id")
            if not task_name_from_attr:
                 task_name_from_attr = task_element.get("name")

            # Описание задачи может быть в <DESC>
            desc_element = task_element.find("DESC")
            task_description = desc_element.text.strip() if desc_element is not None and desc_element.text else ""

            # Имя задачи: используем xml:name если есть, иначе DESC, иначе генерируем
            task_name = task_name_from_attr if task_name_from_attr else task_description.split('.')[0] # Первое предложение из описания
            if not task_name: # Если и описания нет
                task_name = f"Задача_{task_id}"
            
            if task_id:
                # Убедимся, что это действительно задача, а не просто раздел
                # В структуре .kurs.xml задачи - это элементы <T>, у которых есть <PROGRAM> или <DESC> и нет дочерних <T>
                # Но для простоты пока будем считать все <T> с id и name задачами, если они не корневые
                # Более точный критерий - наличие <PROGRAM>prog/...</PROGRAM>
                program_element = task_element.find("PROGRAM")
                is_real_task = program_element is not None and program_element.text and "prog/" in program_element.text

                # Другой вариант - задачи это <T>, у которых нет дочерних <T> и есть id
                # Исключаем корневой элемент KURS и разделы верхнего уровня, если они не являются задачами
                # Задачи - это обычно самые глубоко вложенные элементы <T>
                
                # Новый подход: ищем элементы <T>, у которых есть атрибут xml:id и xml:name,
                # и которые НЕ являются корневым элементом <KURS> и не содержат других <T> (т.е. листовые узлы <T>)
                # Однако, структура сложнее: задачи это <T> внутри других <T>.
                # Будем искать все <T> у которых есть id и name, и которые содержат <DESC> и <PROGRAM>
                
                # Самый надежный способ - искать <T> элементы, которые имеют атрибут id и имя,
                # и находятся внутри другого <T> элемента (который является уроком/разделом)
                # или являются прямыми потомками <KURS>, если структура плоская.
                # В файле "Массивы.kurs.xml" задачи - это <T> внутри <T>.
                # <KURS> -> <T name="Урок..."> -> <T name="1-0" id="10"> (это задача)

                # Пересмотренная логика: ищем все <T> элементы с атрибутом 'id'.
                # Это наиболее общий признак задачи в этих файлах.
                # Имя задачи берем из 'xml:name' или 'name'.
                
                # Финальная логика для parse_kurs_xml:
                # Задачи - это элементы <T>, имеющие атрибут xml:id (или просто id)
                # и находящиеся внутри другого элемента <T> (раздела) или напрямую под <KURS> (если курс плоский).
                # Для файла "Массивы.kurs.xml" структура: <KURS> -> <T (урок)> -> <T (задача с id)>.
                # Поэтому ищем все <T> с id.
                
                # Пройдемся по всем <T> элементам в документе, имеющим атрибут 'id'
                for task_node in root.findall(".//T[@id]"): # Ищем по атрибуту 'id' без пространства имен
                    current_task_id = task_node.get("id")
                    current_task_name = task_node.get("{http://www.w3.org/XML/1998/namespace}name")
                    if not current_task_name: # Пробуем без namespace
                        current_task_name = task_node.get("name")
                    
                    # Используем описание, если имя не найдено или оно слишком общее (типа "1-0")
                    if not current_task_name or re.match(r"^\d+-\d+$", current_task_name):
                        desc_node = task_node.find("DESC")
                        if desc_node is not None and desc_node.text:
                            # Берем первую строку описания как имя
                            current_task_name = desc_node.text.strip().split('\\n')[0].split('.')[0]

                    if not current_task_name: # Если все еще нет имени
                        current_task_name = f"Задача_{current_task_id}"

                    if current_task_id:
                         # Проверяем, есть ли элемент <PROGRAM> и он не пустой - это хороший индикатор задачи
                        program_node = task_node.find("PROGRAM")
                        if program_node is not None and program_node.text and program_node.text.strip():
                             tasks[current_task_id] = {"name": current_task_name, "id": current_task_id}
                        elif program_node is not None : # Если есть тег PROGRAM, но он пуст - возможно, это раздел
                            # Если нет дочерних <T>, то это может быть задача без пути к файлу .kum
                            if not task_node.find("T"):
                                tasks[current_task_id] = {"name": current_task_name, "id": current_task_id}


    except ET.ParseError as e:
        print(f"Ошибка парсинга {kurs_file_path}: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при парсинге {kurs_file_path}: {e}")
    return tasks

def parse_work_xml(work_file_path: Path, tasks_info: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """Парсит .work.xml файл и извлекает решения для задач."""
    solutions: Dict[str, str] = {}
    try:
        tree = ET.parse(work_file_path)
        root = tree.getroot()
        for task_solution_element in root.findall(".//task_solution"):
            task_id = task_solution_element.get("id")
            if task_id and task_id in tasks_info:
                source_element = task_solution_element.find(".//source")
                if source_element is not None and source_element.text:
                    solution_code = source_element.text.strip()
                    
                    # Корректное удаление обертки КУМИРа
                    # Сначала проверяем более длинную конструкцию с \n, потом с \n
                    # Это на случай, если XML парсер по-разному обрабатывает переносы строк
                    patterns_to_remove_start = [
                        "алг программа\nнач\n", # С литеральным \n
                        "алг программа\nнач\n"   # С реальным \n
                    ]
                    patterns_to_remove_end = [
                        "\nкон", # С литеральным \n
                        "\nкон"   # С реальным \n
                    ]

                    for pattern in patterns_to_remove_start:
                        if solution_code.startswith(pattern):
                            solution_code = solution_code[len(pattern):]
                            break
                    
                    for pattern in patterns_to_remove_end:
                        if solution_code.endswith(pattern):
                            solution_code = solution_code[:-len(pattern)]
                            break
                            
                    solutions[task_id] = solution_code.strip()
                else:
                    print(f"Предупреждение: Не найден или пуст элемент <source> для задачи {task_id} в {work_file_path}")
            elif task_id:
                print(f"Предупреждение: Найдено решение для неизвестной задачи {task_id} в {work_file_path} (отсутствует в .kurs.xml)")

    except ET.ParseError as e:
        print(f"Ошибка парсинга {work_file_path}: {e}")
    return solutions

def generate_test_file_content(course_name: str, tasks_with_solutions: Dict[str, Dict[str, str]]) -> str:
    """Генерирует содержимое файла с pytest-тестами для одного курса."""
    
    try:
        with open(TEST_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл шаблона {TEST_TEMPLATE_PATH} не найден.")
        # Возвращаем пустую строку или возбуждаем исключение, чтобы остановить генерацию для этого курса
        return ""


    test_functions_code: List[str] = []
    for task_id, data in tasks_with_solutions.items():
        task_name = data["name"]
        solution_code = data.get("solution", "") # Получаем решение, если оно есть
        
        if not solution_code:
            print(f"Предупреждение: Отсутствует код решения для задачи '{task_name}' (ID: {task_id}) в курсе '{course_name}'. Тест будет пропущен.")
            continue

        escaped_solution_code = solution_code.replace("\\", "\\\\").replace("'", "\'").replace("\n", "\\n").replace('"', '''"''')
        
        test_func_name = f"test_{sanitize_filename(course_name)}_{sanitize_filename(task_name)}_{task_id}"
        temp_kum_file_name = sanitize_filename(f"{course_name}_{task_name}_{task_id}.kum")
        
        test_function = f"""
def {test_func_name}(run_kumir_code_func, tmp_path: Path):
    kumir_code = '''{escaped_solution_code}'''
    file_path = tmp_path / "{temp_kum_file_name}"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    result = run_kumir_code_func(str(file_path))
    assert result.return_code == 0, f"Код КуМира завершился с ошибкой: {{result.stderr_output}}\nКод:\n{{kumir_code}}"
"""
        test_functions_code.append(test_function)

    lines = template_content.split('\n')
    insert_after_line_index = -1 

    # Ищем место для вставки: после всех импортов и фикстур, но перед первым тестом
    # Или просто в конец файла, если шаблон пустой или не содержит тестов
    
    last_import_or_fixture_line = 0
    first_test_line = -1

    for i, line in enumerate(lines):
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            last_import_or_fixture_line = i
        if line.strip().startswith("@pytest.fixture"): # Учитываем фикстуры
             # Ищем конец фикстуры (следующая пустая строка или начало def)
            for j in range(i + 1, len(lines)):
                if not lines[j].strip() or lines[j].strip().startswith("def "):
                    last_import_or_fixture_line = j -1 # Конец фикстуры - предыдущая строка
                    break
            else: # Если фикстура идет до конца файла
                last_import_or_fixture_line = len(lines) -1


        if line.strip().startswith("def test_") and first_test_line == -1:
            first_test_line = i
            break # Нашли первый тест, дальше не ищем

    if first_test_line != -1:
        # Если есть тесты, вставляем перед первым из них, но после импортов/фикстур
        insert_after_line_index = max(last_import_or_fixture_line, 0) if first_test_line == 0 else first_test_line -1
        # Берем все до этой точки
        header_lines = lines[:insert_after_line_index + 1]
         # Если мы вставляем перед первым тестом, то старые тесты нам не нужны
        if insert_after_line_index + 1 < len(lines) and lines[insert_after_line_index+1].strip().startswith("def test_"):
             pass # Старые тесты будут заменены
        elif first_test_line > 0 : # Если первый тест не в начале, то сохраняем все до него
             header_lines = lines[:first_test_line]


    elif last_import_or_fixture_line > 0:
        # Если тестов нет, но есть импорты/фикстуры, вставляем после них
        insert_after_line_index = last_import_or_fixture_line
        header_lines = lines[:insert_after_line_index + 1]
    else:
        # Если шаблон почти пустой (нет ни тестов, ни значимых импортов)
        # Просто берем все, что есть (может быть копирайт или комментарии)
        header_lines = lines
        insert_after_line_index = len(lines) -1


    # Если в шаблоне вообще не было строк (маловероятно, но возможно)
    if not lines:
        header_lines = ["import pytest", "from pathlib import Path"] # Минимальные необходимые импорты
        insert_after_line_index = len(header_lines) -1


    header = "\n".join(header_lines)
    if not header.strip() and not test_functions_code: # Если и шапка пустая, и тестов нет
        return "" # Не генерировать пустой файл

    # Добавляем пустую строку после шапки, если она не пустая и есть тесты для вставки
    if header.strip() and test_functions_code:
        header += "\n"

    generated_notice = f"# Файл сгенерирован автоматически скриптом generate_course_tests.py\n"
    generated_notice += f"# Курс: {course_name}\n\n"
    
    final_code = generated_notice + header + "\n\n" + "\n\n".join(test_functions_code)
    
    return final_code.strip() + "\n" # Убедимся, что в конце есть одна новая строка

def main():
    """Главная функция для генерации тестов."""
    print(f"Сканирование директории с курсами: {POLYAKOV_KURS_WORK_DIR}")
    
    found_courses_count = 0
    generated_files_count = 0

    for course_dir_item in POLYAKOV_KURS_WORK_DIR.iterdir():
        if course_dir_item.is_dir():
            course_name = course_dir_item.name
            print(f"  Найден курс: {course_name}")
            found_courses_count += 1
            
            # Ищем .kurs.xml файл. Имя файла может быть не точно таким же, как имя папки.
            # Например, папка "arrkum", файл "Массивы.kurs.xml"
            kurs_file: Optional[Path] = None
            possible_kurs_files = list(course_dir_item.glob("*.kurs.xml"))
            if possible_kurs_files:
                kurs_file = possible_kurs_files[0] # Берем первый найденный
                if len(possible_kurs_files) > 1:
                    print(f"    Предупреждение: Найдено несколько .kurs.xml файлов в {course_dir_item}. Используется: {kurs_file.name}")
            
            work_file: Optional[Path] = None
            possible_work_files = list(course_dir_item.glob("*.work.xml"))
            if possible_work_files:
                work_file = possible_work_files[0] # Берем первый найденный
                if len(possible_work_files) > 1:
                    print(f"    Предупреждение: Найдено несколько .work.xml файлов в {course_dir_item}. Используется: {work_file.name}")

            if kurs_file and kurs_file.exists() and work_file and work_file.exists():
                print(f"    Файл описания курса: {kurs_file.name}")
                print(f"    Файл решений: {work_file.name}")
                
                tasks_info = parse_kurs_xml(kurs_file)
                if not tasks_info:
                    print(f"    Предупреждение: Не найдено задач в {kurs_file.name} для курса '{course_name}'. Пропуск.")
                    continue
                    
                solutions = parse_work_xml(work_file, tasks_info)
                # Не будем выводить предупреждение, если нет решений, т.к. parse_work_xml уже это делает
                                    
                tasks_with_solutions: Dict[str, Dict[str,str]] = {}
                for task_id, task_data in tasks_info.items():
                    if task_id in solutions and solutions[task_id]: # Убедимся, что решение не пустое
                        tasks_with_solutions[task_id] = {
                            "name": task_data["name"],
                            "solution": solutions[task_id]
                        }
                    else:
                        print(f"    Предупреждение: Нет решения или оно пустое для задачи '{task_data['name']}' (ID: {task_id}) в курсе '{course_name}'.")

                if not tasks_with_solutions:
                    print(f"    Предупреждение: Нет задач с корректными решениями для генерации тестов в курсе '{course_name}'. Пропуск.")
                    continue

                test_file_name = f"test_{sanitize_filename(course_name)}.py"
                test_file_path = GENERATED_TESTS_DIR / test_file_name
                
                print(f"    Генерация файла теста: {test_file_path}")
                
                test_content = generate_test_file_content(course_name, tasks_with_solutions)
                
                if test_content: # Генерируем файл, только если есть что генерировать
                    with open(test_file_path, "w", encoding="utf-8") as f:
                        f.write(test_content)
                    print(f"    Файл теста {test_file_path.name} успешно сгенерирован.")
                    generated_files_count +=1
                else:
                    print(f"    Предупреждение: Контент для файла теста {test_file_path.name} не был сгенерирован (возможно, из-за отсутствия шаблона или задач).")
                
            else:
                if not (kurs_file and kurs_file.exists()):
                    print(f"    Предупреждение: Файл .kurs.xml не найден в директории {course_dir_item}")
                if not (work_file and work_file.exists()):
                     print(f"    Предупреждение: Файл .work.xml не найден в директории {course_dir_item}")
    
    print(f"\nСканирование завершено. Найдено курсов: {found_courses_count}.")
    print(f"Сгенерировано файлов с тестами: {generated_files_count}.")

if __name__ == "__main__":
    main()

import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Dict, List # Убрал Any и Optional
from datetime import datetime

# Константы
POLYAKOV_KURS_WORK_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work")
GENERATED_TESTS_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/generated_course_tests")
TEST_TEMPLATE_PATH = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/test_polyakov_kum.py")

GENERATED_TESTS_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str) -> str:
    """Очищает имя файла от недопустимых символов."""
    name = re.sub(r'[\/*?:"<>|]',"", name)
    name = name.replace(" ", "_")
    return name

def parse_kurs_xml(kurs_file_path: Path) -> Dict[str, Dict[str, str]]:
    """Парсит .kurs.xml файл и извлекает информацию о задачах."""
    tasks: Dict[str, Dict[str, str]] = {}
    try:
        tree = ET.parse(kurs_file_path)
        root = tree.getroot()
        
        # Пространство имен для атрибутов вроде xml:id
        ns = {'xml': 'http://www.w3.org/XML/1998/namespace'}

        for task_node in root.findall(".//T"): # Ищем все элементы <T>
            task_id = task_node.get(f"{{{ns['xml']}}}id")
            if not task_id: # Пробуем без пространства имен
                task_id = task_node.get("id")

            if task_id:
                # Задачи должны иметь непустой элемент <PROGRAM>
                program_node = task_node.find("PROGRAM")
                if program_node is not None and program_node.text and program_node.text.strip():
                    # Получаем имя задачи
                    task_name_attr = task_node.get(f"{{{ns['xml']}}}name")
                    if not task_name_attr:
                        task_name_attr = task_node.get("name")

                    current_task_name = task_name_attr
                    
                    # Если имя из атрибута отсутствует, слишком общее, или похоже на автогенеренное,
                    # пытаемся извлечь его из <DESC>
                    if not current_task_name or \
                       re.fullmatch(r"\d+-\d+", current_task_name or "") or \
                       (current_task_name or "").startswith("Задача_"):
                        
                        desc_node = task_node.find("DESC")
                        if desc_node is not None and desc_node.text:
                            # Очищаем от HTML тегов (например, <BR>) и берем первую строку/предложение
                            desc_text_cleaned = re.sub('<[^<]+?>', '', desc_node.text.strip())
                            name_from_desc = desc_text_cleaned.split('\\n')[0].split('.')[0].strip()
                            if name_from_desc: # Если удалось что-то извлечь
                                current_task_name = name_from_desc
                    
                    # Если имя все еще не определено, генерируем стандартное
                    if not current_task_name:
                        current_task_name = f"Задача_{task_id}"
                    
                    tasks[task_id] = {"name": current_task_name, "id": task_id}
                # else:
                #     # Элемент <T> с ID, но без <PROGRAM> или с пустым <PROGRAM> - это, скорее всего, раздел, а не задача.
                #     # Либо задача, для которой не указан файл с кодом. Такие пропускаем.
                #     # print(f"DEBUG: Пропускаем узел T с ID {task_id} - нет PROGAM или он пуст.")
                #     pass
            # else:
            #     # Элемент <T> без ID - это точно не задача, которую мы ищем.
            #     # print(f"DEBUG: Пропускаем узел T без ID.")
            #     pass

    except ET.ParseError as e:
        print(f"Ошибка парсинга XML в файле {kurs_file_path}: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при парсинге {kurs_file_path}: {e}")
    return tasks

def parse_work_xml(work_file_path: Path, tasks_info: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """Парсит .work.xml файл и извлекает решения для задач."""
    solutions: Dict[str, str] = {}
    try:
        tree = ET.parse(work_file_path)
        root = tree.getroot()
        for task_solution_element in root.findall(".//task_solution"):
            task_id = task_solution_element.get("id")
            if task_id and task_id in tasks_info:
                source_element = task_solution_element.find(".//source")
                if source_element is not None and source_element.text:
                    solution_code = source_element.text.strip()
                    
                    # Корректное удаление обертки КУМИРа
                    # Сначала проверяем более длинную конструкцию с \n, потом с \n
                    # Это на случай, если XML парсер по-разному обрабатывает переносы строк
                    patterns_to_remove_start = [
                        "алг программа\nнач\n", # С литеральным \n
                        "алг программа\nнач\n"   # С реальным \n
                    ]
                    patterns_to_remove_end = [
                        "\nкон", # С литеральным \n
                        "\nкон"   # С реальным \n
                    ]

                    for pattern in patterns_to_remove_start:
                        if solution_code.startswith(pattern):
                            solution_code = solution_code[len(pattern):]
                            break
                    
                    for pattern in patterns_to_remove_end:
                        if solution_code.endswith(pattern):
                            solution_code = solution_code[:-len(pattern)]
                            break
                            
                    solutions[task_id] = solution_code.strip()
                else:
                    print(f"Предупреждение: Не найден или пуст элемент <source> для задачи {task_id} в {work_file_path}")
            elif task_id:
                print(f"Предупреждение: Найдено решение для неизвестной задачи {task_id} в {work_file_path} (отсутствует в .kurs.xml)")

    except ET.ParseError as e:
        print(f"Ошибка парсинга {work_file_path}: {e}")
    return solutions

def generate_test_file_content(course_name: str, tasks_with_solutions: Dict[str, Dict[str, str]]) -> str:
    """Генерирует содержимое файла с pytest-тестами для одного курса."""
    
    try:
        with open(TEST_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл шаблона {TEST_TEMPLATE_PATH} не найден.")
        # Возвращаем пустую строку или возбуждаем исключение, чтобы остановить генерацию для этого курса
        return ""


    test_functions_code: List[str] = []
    for task_id, data in tasks_with_solutions.items():
        task_name = data["name"]
        solution_code = data.get("solution", "") # Получаем решение, если оно есть
        
        if not solution_code:
            print(f"Предупреждение: Отсутствует код решения для задачи '{task_name}' (ID: {task_id}) в курсе '{course_name}'. Тест будет пропущен.")
            continue

        escaped_solution_code = solution_code.replace("\\", "\\\\").replace("'", "\'").replace("\n", "\\n").replace('"', '''"''')
        
        test_func_name = f"test_{sanitize_filename(course_name)}_{sanitize_filename(task_name)}_{task_id}"
        temp_kum_file_name = sanitize_filename(f"{course_name}_{task_name}_{task_id}.kum")
        
        test_function = f"""
def {test_func_name}(run_kumir_code_func, tmp_path: Path):
    kumir_code = '''{escaped_solution_code}'''
    file_path = tmp_path / "{temp_kum_file_name}"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    result = run_kumir_code_func(str(file_path))
    assert result.return_code == 0, f"Код КуМира завершился с ошибкой: {{result.stderr_output}}\nКод:\n{{kumir_code}}"
"""
        test_functions_code.append(test_function)

    lines = template_content.split('\n')
    insert_after_line_index = -1 

    # Ищем место для вставки: после всех импортов и фикстур, но перед первым тестом
    # Или просто в конец файла, если шаблон пустой или не содержит тестов
    
    last_import_or_fixture_line = 0
    first_test_line = -1

    for i, line in enumerate(lines):
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            last_import_or_fixture_line = i
        if line.strip().startswith("@pytest.fixture"): # Учитываем фикстуры
             # Ищем конец фикстуры (следующая пустая строка или начало def)
            for j in range(i + 1, len(lines)):
                if not lines[j].strip() or lines[j].strip().startswith("def "):
                    last_import_or_fixture_line = j -1 # Конец фикстуры - предыдущая строка
                    break
            else: # Если фикстура идет до конца файла
                last_import_or_fixture_line = len(lines) -1


        if line.strip().startswith("def test_") and first_test_line == -1:
            first_test_line = i
            break # Нашли первый тест, дальше не ищем

    if first_test_line != -1:
        # Если есть тесты, вставляем перед первым из них, но после импортов/фикстур
        insert_after_line_index = max(last_import_or_fixture_line, 0) if first_test_line == 0 else first_test_line -1
        # Берем все до этой точки
        header_lines = lines[:insert_after_line_index + 1]
         # Если мы вставляем перед первым тестом, то старые тесты нам не нужны
        if insert_after_line_index + 1 < len(lines) and lines[insert_after_line_index+1].strip().startswith("def test_"):
             pass # Старые тесты будут заменены
        elif first_test_line > 0 : # Если первый тест не в начале, то сохраняем все до него
             header_lines = lines[:first_test_line]
        else: # Если тестов нет или они в самом начале, берем все до конца импортов/фикстур
            header_lines = lines[:last_import_or_fixture_line + 1]
            
        # Собираем итоговый контент
        # Сначала заголовок (импорты, фикстуры из шаблона)
        # Затем новые сгенерированные тесты
        final_content = "\\n".join(header_lines) + "\\n\\n" + "\\n\\n".join(test_functions_code) + "\\n"
    
    else: # Если в шаблоне вообще нет тестов (def test_)
        # Просто добавляем новые тесты после всех импортов и фикстур
        final_content = "\\n".join(lines[:last_import_or_fixture_line + 1]) + "\\n\\n" + "\\n\\n".join(test_functions_code) + "\\n"

    return final_content

def main():
    """Главная функция для генерации тестов."""
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Начало генерации тестов...")

    GENERATED_TESTS_DIR.mkdir(parents=True, exist_ok=True) # Убедимся, что директория существует

    course_count = 0
    generated_test_files_count = 0

    for kurs_dir in POLYAKOV_KURS_WORK_DIR.iterdir():
        if kurs_dir.is_dir():
            course_name = kurs_dir.name
            print(f"  Обработка курса: {course_name}")

            kurs_file = kurs_dir / f"{course_name}.kurs.xml" # Ожидаемое имя файла курса
            # Иногда имя файла курса может отличаться от имени директории, например, "Массивы.kurs.xml"
            # Попробуем найти .kurs.xml файл в директории, если стандартное имя не подошло
            if not kurs_file.exists():
                found_kurs_files = list(kurs_dir.glob("*.kurs.xml"))
                if found_kurs_files:
                    kurs_file = found_kurs_files[0] # Берем первый найденный
                else:
                    print(f"    Предупреждение: Не найден .kurs.xml файл для курса {course_name}. Пропускаем.")
                    continue
            
            work_file = kurs_dir / f"Поляков_{course_name}.work.xml" # Ожидаемое имя файла с решениями
            # Аналогично для .work.xml
            if not work_file.exists():
                found_work_files = list(kurs_dir.glob("*.work.xml"))
                if found_work_files:
                    work_file = found_work_files[0]
                else:
                    print(f"    Предупреждение: Не найден .work.xml файл для курса {course_name}. Решения не будут извлечены.")
                    # Продолжаем, даже если нет файла решений, задачи из .kurs.xml все равно могут быть полезны
                    # Но тесты для них не будут содержать эталонного кода.
                    # В generate_test_file_content есть проверка на отсутствие решения.
                    pass # work_file останется None или неверным, parse_work_xml обработает это

            tasks_info = parse_kurs_xml(kurs_file)
            if not tasks_info:
                print(f"    Предупреждение: Не найдено задач в {kurs_file.name} для курса {course_name}. Пропускаем генерацию тестов для этого курса.")
                continue

            solutions: Dict[str, str] = {}
            if work_file and work_file.exists():
                 solutions = parse_work_xml(work_file, tasks_info)
            else:
                print(f"    Информация: Файл решений {work_file.name if work_file else 'не указан'} не найден или не существует. Тесты будут сгенерированы без эталонных решений.")


            tasks_with_solutions: Dict[str, Dict[str, str]] = {}
            for task_id, task_data in tasks_info.items():
                tasks_with_solutions[task_id] = task_data.copy() # Копируем, чтобы не изменять исходный tasks_info
                if task_id in solutions:
                    tasks_with_solutions[task_id]["solution"] = solutions[task_id] # FIX: Исправлено экранирование
                else:
                    # Если решения нет, оставляем поле "solution" отсутствующим или None
                    # Функция generate_test_file_content это обработает
                    print(f"      Информация: Для задачи '{task_data['name']}' (ID: {task_id}) не найдено решение в {work_file.name if work_file else 'файле решений'}.")


            if not any("\"solution\"" in data for data in tasks_with_solutions.values()):
                print(f"    Предупреждение: Для курса {course_name} не найдено ни одного решения для задач. Файл тестов не будет создан.")
                continue

            test_content = generate_test_file_content(course_name, tasks_with_solutions)

            if test_content: # Если контент успешно сгенерирован
                test_file_name = f"test_{sanitize_filename(course_name)}.py"
                test_file_path = GENERATED_TESTS_DIR / test_file_name
                try:
                    with open(test_file_path, "w", encoding="utf-8") as f:
                        f.write(test_content)
                    print(f"    Успешно сгенерирован файл тестов: {test_file_path}")
                    generated_test_files_count += 1
                except IOError as e:
                    print(f"    Ошибка записи файла тестов {test_file_path}: {e}")
            else:
                print(f"    Предупреждение: Контент для файла тестов курса {course_name} не был сгенерирован (возможно, из-за отсутствия шаблона или задач с решениями).")

            course_count += 1
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Генерация тестов завершена.")
    print(f"  Всего обработано курсов: {course_count}")
    print(f"  Сгенерировано файлов с тестами: {generated_test_files_count}")
    print(f"  Затрачено времени: {duration}")

if __name__ == "__main__":
    main()
