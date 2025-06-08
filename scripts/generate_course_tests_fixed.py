#!/usr/bin/env python3
"""
Test generator for Polyakov courses.

Parses .kurs.xml and .work.xml files, extracts reference solutions from 'prg' attribute
of <USER_PRG>/<TESTED_PRG> elements, and creates pytest tests for testing the Kumir interpreter.

Based on analysis of XML structure from kurs_test_gen_info.md.
"""

import xml.etree.ElementTree as ET
import re
import html
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Константы
POLYAKOV_KURS_WORK_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/polyakov_kurs_work")
GENERATED_TESTS_DIR = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/generated_course_tests")
TEST_TEMPLATE_PATH = Path("c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/test_polyakov_kum.py")

# Убедимся, что директория для тестов существует
GENERATED_TESTS_DIR.mkdir(parents=True, exist_ok=True)


# ======================== СТРОКОВЫЕ ФУНКЦИИ ========================

def normalize_spaces(text: str) -> str:
    """Нормализует пробелы: убирает лишние, заменяет переносы строк на пробелы."""
    return re.sub(r'\s+', ' ', text.strip())


def extract_first_sentence(text: str) -> str:
    """Извлекает первое предложение из текста."""
    # Удаляем HTML теги
    clean_text = re.sub(r'<[^>]+>', '', text.strip())
    # Берем первое предложение (до точки, восклицательного или вопросительного знака)
    match = re.search(r'^[^.!?]*[.!?]?', clean_text)
    if match:
        return match.group(0).strip().rstrip('.!?')
    return clean_text[:100] + "..." if len(clean_text) > 100 else clean_text


def truncate_text(text: str, max_length: int = 50) -> str:
    """Обрезает текст до указанной длины, добавляя ... если нужно."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def clean_task_name_for_function(name: str) -> str:
    """Очищает название задачи для использования в имени функции."""
    # Убираем HTML теги
    cleaned = re.sub(r'<[^>]+>', '', name)
    
    # Транслитерация кириллицы в латиницу
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    # Применяем транслитерацию
    result = ''
    for char in cleaned:
        result += cyrillic_to_latin.get(char, char)
    cleaned = result
    
    # Убираем все символы кроме ASCII букв, цифр, подчеркиваний
    cleaned = re.sub(r'[^\w\s\-]', '', cleaned)
    # Заменяем пробелы и дефисы на подчеркивания
    cleaned = re.sub(r'[\s\-]+', '_', cleaned)
    # Убираем множественные подчеркивания
    cleaned = re.sub(r'_+', '_', cleaned)
    # Убираем подчеркивания в начале и конце
    cleaned = cleaned.strip('_')
    # Обрезаем до разумной длины (меньше, чтобы поместилось с префиксами)
    cleaned = truncate_text(cleaned, 60)
    return cleaned if cleaned else "unnamed_task"


def is_function_algorithm(algorithm_code: str) -> bool:
    """Проверяет, является ли алгоритм функцией (возвращает значение)."""
    lines = algorithm_code.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('алг '):
            # Проверяем, есть ли тип возвращаемого значения
            return bool(re.search(r'алг\s+(цел|вещ|лог|лит|сим)\s+', line))
    return False


def extract_algorithm_signature(algorithm_code: str) -> Optional[str]:
    """Извлекает сигнатуру алгоритма (первую строку с объявлением)."""
    lines = algorithm_code.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('алг '):
            return line_stripped
    return None


def generate_test_call_for_function(algorithm_code: str, task_name: str) -> str:
    """Генерирует код для тестирования функции с простыми входными данными."""
    signature = extract_algorithm_signature(algorithm_code)
    if not signature:
        return algorithm_code
    
    # Пытаемся понять, какие параметры принимает функция
    # Например: "алг цел квадрат(цел x)" -> нужно передать целое число
    
    # Простая эвристика: определяем тип и количество параметров
    param_match = re.search(r'\((.*?)\)', signature)
    if not param_match:
        # Функция без параметров
        func_name_match = re.search(r'алг\s+(?:цел|вещ|лог|лит|сим)\s+(\w+)', signature)
        if func_name_match:
            func_name = func_name_match.group(1)
            return f"""алг
нач
  результат := {func_name}()
  вывод результат, нс
кон

{algorithm_code}"""
    
    params_str = param_match.group(1).strip()
    if not params_str:
        # Функция без параметров
        func_name_match = re.search(r'алг\s+(?:цел|вещ|лог|лит|сим)\s+(\w+)', signature)
        if func_name_match:
            func_name = func_name_match.group(1)
            return f"""алг
нач
  результат := {func_name}()
  вывод результат, нс
кон

{algorithm_code}"""
    
    # Извлекаем имя функции
    func_name_match = re.search(r'алг\s+(?:цел|вещ|лог|лит|сим)\s+(\w+)', signature)
    if not func_name_match:
        return algorithm_code
    
    func_name = func_name_match.group(1)
    
    # Генерируем простые тестовые значения в зависимости от типов параметров
    # Парсим параметры: "цел x, вещ y" -> [("цел", "x"), ("вещ", "y")]
    params: List[Tuple[str, str]] = []
    for param in params_str.split(','):
        param = param.strip()
        if ' ' in param:
            parts = param.split()
            if len(parts) >= 2:
                param_type, param_name = parts[0], parts[1]
                params.append((param_type.strip(), param_name.strip()))
    
    # Генерируем тестовые значения
    test_values: List[str] = []
    for param_type, param_name in params:
        if param_type == 'цел':
            test_values.append('5')
        elif param_type == 'вещ':
            test_values.append('3.14')
        elif param_type == 'лог':
            test_values.append('да')
        elif param_type in ['лит', 'сим']:
            test_values.append('"тест"')
        else:
            test_values.append('0')  # Значение по умолчанию
    
    call_args = ', '.join(test_values)
    
    return f"""алг
нач
  результат := {func_name}({call_args})
  вывод результат, нс
кон

{algorithm_code}"""


# ======================== ОСНОВНЫЕ ФУНКЦИИ ========================

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
        
        # Ищем все элементы <T>
        for task_node in root.findall(".//T"):
            # Получаем task_id из xml:id
            task_id = task_node.get("{http://www.w3.org/XML/1998/namespace}id")
            if not task_id:
                continue
                
            # Проверяем, что это действительно задача (имеет <PROGRAM>)
            program_node = task_node.find("PROGRAM")
            if program_node is None or not program_node.text or not program_node.text.strip():
                continue
                
            # Получаем имя задачи
            task_name = task_node.get("{http://www.w3.org/XML/1998/namespace}name")
            
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
            
    except ET.ParseError as e:        print(f"❌ Error parsing XML file {kurs_file_path}: {e}")
    except Exception as e:
        print(f"❌ Unexpected error parsing {kurs_file_path}: {e}")
    
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
            match = re.match(r'алг\s+(?:цел|вещ|лог|лит|сим)?\s*([^(]+)', line)
            if match:
                name = match.group(1).strip()
                return clean_task_name_for_function(name)
        elif line.startswith('алг '):
            # Алгоритм без параметров
            match = re.match(r'алг\s+(?:цел|вещ|лог|лит|сим)?\s*(.+)', line)
            if match:
                name = match.group(1).strip()
                return clean_task_name_for_function(name)
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


def extract_solution_algorithm(kumir_code: str) -> Optional[str]:
    """
    Извлекает алгоритм __Решение__ из очищенного КуМир-кода.
    
    Алгоритм __Решение__ может находиться как в обычной части, так и в 
    скрытой части (маркированной |@hidden). Функция ищет его во всем коде.
    
    Returns:
        Код алгоритма __Решение__ или None если не найден
    """
    lines = kumir_code.split('\n')
    
    # Ищем начало алгоритма __Решение__ (учитываем разные форматы сигнатуры)
    solution_start = None
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        # Ищем по разным паттернам: "алг тип __Решение__" или "алг __Решение__"
        if (line_stripped.startswith('алг ') and '__Решение__' in line):
            solution_start = i
            break
    
    if solution_start is None:
        return None
    
    # Ищем соответствующий 'кон'
    algorithm_lines = []
    brace_count = 0
    found_begin = False
    
    for i in range(solution_start, len(lines)):
        line = lines[i].strip()
        algorithm_lines.append(lines[i])  # Сохраняем оригинальное форматирование
        
        if line == 'нач':
            found_begin = True
            brace_count += 1
        elif line == 'кон':
            if found_begin:
                brace_count -= 1
                if brace_count == 0:
                    break
        elif line.startswith('если ') and line.endswith(' то'):
            brace_count += 1
        elif line in ['все', 'иначе']:
            if found_begin:
                brace_count -= 1
        elif line.startswith('нц '):
            brace_count += 1
        elif line == 'кц':
            if found_begin:
                brace_count -= 1
    
    if algorithm_lines:
        return '\n'.join(algorithm_lines)
    
    return None


def generate_simple_test_kumir_program(solution_algorithm: str, task_name: str) -> str:
    """
    Генерирует простую КуМир-программу для тестирования алгоритма.
    
    Создаёт программу, которая:
    1. Если это функция - вызывает её с тестовыми данными и выводит результат
    2. Если это процедура - вызывает её с тестовыми данными
    3. Если это основной алгоритм - выполняет его как есть
    
    Новая логика: если найден __Решение__, используем его, иначе весь код.
    """
    
    # Проверяем, является ли алгоритм функцией
    if is_function_algorithm(solution_algorithm):
        # Извлекаем сигнатуру алгоритма для анализа
        signature = extract_algorithm_signature(solution_algorithm)
        if signature and '__Решение__' in signature:
            # Это функция __Решение__ - генерируем правильный тест
            return generate_test_call_for_function(solution_algorithm, task_name)
        else:
            # Другая функция - используем как есть с оберткой
            return generate_test_call_for_function(solution_algorithm, task_name)
    else:
        # Это процедура или алгоритм без возвращаемого значения
        signature = extract_algorithm_signature(solution_algorithm)
        if signature and '__Решение__' in signature:
            # Это процедура __Решение__ - создаем тест с вызовом
            return generate_test_call_for_procedure(solution_algorithm, task_name)
        else:
            # Основной алгоритм - возвращаем как есть
            return solution_algorithm


def generate_test_call_for_procedure(algorithm_code: str, task_name: str) -> str:
    """Генерирует код для тестирования процедуры."""
    signature = extract_algorithm_signature(algorithm_code)
    if not signature:
        return algorithm_code
    
    # Извлекаем имя процедуры
    proc_name_match = re.search(r'алг\s+(\w+)', signature)
    if not proc_name_match:
        return algorithm_code
    
    proc_name = proc_name_match.group(1)
    
    # Анализируем параметры процедуры
    param_match = re.search(r'\((.*?)\)', signature)
    if not param_match:
        # Процедура без параметров
        return f"""алг
нач
  {proc_name}()
  вывод "Процедура {proc_name} выполнена", нс
кон

{algorithm_code}"""
    
    params_str = param_match.group(1).strip()
    if not params_str:
        # Процедура без параметров
        return f"""алг
нач
  {proc_name}()
  вывод "Процедура {proc_name} выполнена", нс
кон

{algorithm_code}"""
    
    # Генерируем простые тестовые значения для процедуры
    # Парсим параметры и генерируем объявления и вызовы
    test_declarations = []
    test_values = []
    param_names = []
    
    for param in params_str.split(','):
        param = param.strip()
        
        # Process argres/arg parameters
        if param.startswith('аргрез ') or param.startswith('арг '):
            param = param.split(' ', 1)[1]  # Убираем аргрез/арг
        
        if ' ' in param:
            parts = param.split()
            if len(parts) >= 2:
                param_type, param_name = parts[0], parts[1]
                param_names.append(param_name)
                
                if param_type == 'цел':
                    test_declarations.append(f'цел {param_name}')
                    test_values.append(f'{param_name} := 5')
                elif param_type == 'вещ':
                    test_declarations.append(f'вещ {param_name}')
                    test_values.append(f'{param_name} := 3.14')
                elif param_type == 'лог':
                    test_declarations.append(f'лог {param_name}')
                    test_values.append(f'{param_name} := да')
                elif param_type in ['лит', 'сим']:
                    test_declarations.append(f'{param_type} {param_name}')
                    test_values.append(f'{param_name} := "тест"')
                else:
                    test_declarations.append(f'{param_type} {param_name}')
                    test_values.append(f'{param_name} := 0')
    
    if not param_names:
        # Если не удалось распарсить параметры
        return f"""алг
нач
  {proc_name}()
  вывод "Процедура {proc_name} выполнена", нс
кон

{algorithm_code}"""
    
    # Собираем код
    declarations = '\n  '.join(test_declarations)
    initializations = '\n  '.join(test_values)
    call_args = ', '.join(param_names)
    
    return f"""алг
нач
  {declarations}
  {initializations}
  {proc_name}({call_args})
  вывод "Процедура {proc_name} выполнена", нс
кон

{algorithm_code}"""


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
        return ""    # Генерируем тестовые функции
    test_functions: List[str] = []
    
    for task_id, data in tasks_with_solutions.items():
        task_name = data["name"]
        solution_code = data.get("solution", "")
        
        if not solution_code:
            print(f"⚠️  Пропускаем задачу '{task_name}' (ID: {task_id}) - нет решения")
            continue
        
        # Извлекаем эталонный алгоритм __Решение__
        solution_algorithm = extract_solution_algorithm(solution_code)
        if not solution_algorithm:
            print(f"⚠️  Не найден алгоритм __Решение__ для задачи '{task_name}' (ID: {task_id})")
            # Попробуем использовать весь код как есть
            solution_algorithm = solution_code
          # Генерируем простую тестовую программу
        test_kumir_program = generate_simple_test_kumir_program(solution_algorithm, task_name)
        
        # Создаем имя тестовой функции
        safe_course_name = sanitize_filename(course_name)
        safe_task_name = sanitize_filename(task_name)
        test_func_name = f"test_{safe_course_name}_{safe_task_name}_{task_id}"
        
        # Создаем pytest-тест
        test_function = f"""
def {test_func_name}(run_kumir_code_func, tmp_path):
    \"\"\"
    Тест для задачи: {task_name} (ID: {task_id})
    Курс: {course_name}
    \"\"\"
    kumir_code = '''{test_kumir_program}'''
    
    # Записываем во временный файл
    test_file = tmp_path / "test_{task_id}.kum"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(kumir_code)
    
    # Запускаем интерпретатор
    result = run_kumir_code_func(str(test_file))
    
    # Проверяем, что код выполнился без ошибок
    assert result.return_code == 0, f"Код завершился с ошибкой: {{result.stderr_output}}"
      # TODO: Добавить проверку конкретного вывода для каждой задачи
    print(f"Тест {test_func_name} выполнен. Вывод: {{result.stdout_output[:100]}}")
"""
        
        test_functions.append(test_function)
        print(f"✅ Сгенерирован тест для задачи '{task_name}' (ID: {task_id})")
    
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
    """Main function of the test generator."""
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting test generation...")
    print(f"Source directory: {POLYAKOV_KURS_WORK_DIR}")
    print(f"Target directory: {GENERATED_TESTS_DIR}")
    
    course_count = 0
    generated_files_count = 0
    total_tests_count = 0
    
    # Process each course
    for course_dir in POLYAKOV_KURS_WORK_DIR.iterdir():
        if not course_dir.is_dir():
            continue
            
        course_name = course_dir.name
        print(f"\n📚 Processing course: {course_name}")
        
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
