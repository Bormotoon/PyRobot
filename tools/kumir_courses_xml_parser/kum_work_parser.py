import xml.etree.ElementTree as ET
import json
import re
import os
from typing import Optional, List, Dict, Any, Set

def parse_kumir_xml_to_json(xml_file_path: str, json_file_path: str) -> None:
    """
    Парсит XML-файл с задачами Кумира и сохраняет их в JSON.
    Исправленная версия с правильным извлечением блока "надо".
    """
    if not os.path.exists(xml_file_path):
        print(f"Ошибка: Файл не найден по пути: {xml_file_path}")
        return

    all_tasks_data: List[Dict[str, Any]] = []
    processed_ids: Set[str] = set()

    try:
        tree = ET.parse(xml_file_path)
        root: ET.Element = tree.getroot()
    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
        return

    elements_to_process = root.findall('.//USER_PRG') + root.findall('.//TESTED_PRG')

    for task_element in elements_to_process:
        test_id: Optional[str] = task_element.get('testId')
        prg_full_content: Optional[str] = task_element.get('prg')

        if not prg_full_content or not test_id or test_id in processed_ids:
            continue
        
        processed_ids.add(test_id)
        prg_full_content = prg_full_content.strip()

        # Отделяем тестовый блок
        testing_separator = "алг цел @тестирование|@hidden"
        student_program_part = prg_full_content.split(testing_separator, 1)[0].strip()

        # Извлекаем составные части с помощью регулярных выражений
        
        # 1. Извлекаем название алгоритма
        alg_match = re.search(r'алг\s+(.+?)\s*\|\@protected', student_program_part, re.DOTALL)
        alg_name = alg_match.group(1).strip() if alg_match else ""
        
        # 2. Извлекаем блок "дано" с улучшенной очисткой
        dano_match = re.search(r'дано\s*\|\s*(.+?)\s*\|\@protected', student_program_part, re.DOTALL)
        dano_content = dano_match.group(1).strip() if dano_match else ""
        # Улучшенная очистка от внутренних маркеров
        dano_clean = re.sub(r'\s*\|\s*', ' ', dano_content)
        dano_clean = re.sub(r'\s+', ' ', dano_clean).strip()
        
        # 3. Извлекаем блок "надо" - ИСПРАВЛЕННАЯ ЛОГИКА
        # Ищем начало блока "надо"
        nado_start_match = re.search(r'надо\s*\|', student_program_part)
        if nado_start_match:
            nado_start_pos = nado_start_match.start()
            # Ищем первый "нач|@protected" после "надо"
            nach_match = re.search(r'нач\s*\|\@protected', student_program_part[nado_start_pos:])
            if nach_match:
                # Блок "надо" заканчивается перед "нач|@protected"
                nado_end_pos = nado_start_pos + nach_match.start()
                nado_block = student_program_part[nado_start_pos:nado_end_pos].strip()
                
                # Извлекаем содержимое блока "надо", убирая служебные маркеры
                nado_content = re.sub(r'надо\s*\|\s*', '', nado_block)
                nado_content = re.sub(r'\|\@protected', '', nado_content)
                nado_content = re.sub(r'^\s*\|\s*', '', nado_content, flags=re.MULTILINE)
                nado_clean = re.sub(r'\s+', ' ', nado_content).strip()
            else:
                nado_clean = ""
        else:
            nado_clean = ""
          # 4. Извлекаем ученический код - ИСПРАВЛЕННАЯ ЛОГИКА
        student_code = ""
        # Ищем первый "нач|@protected" - это начало кода
        nach_match = re.search(r'нач\s*\|\@protected', student_program_part)
        if nach_match:
            code_start_pos = nach_match.start()  # Начинаем с "нач", а не после него
            
            # Ищем первый "кон|@protected" после начала кода
            kon_match = re.search(r'кон\s*\|\@protected', student_program_part[code_start_pos:])
            if kon_match:
                code_end_pos = code_start_pos + kon_match.end()  # Включаем "кон" в код
                student_code_raw = student_program_part[code_start_pos:code_end_pos].strip()
                
                # Очищаем код от маркеров, но оставляем "нач" и "кон"
                student_code = re.sub(r'\|\@protected', '', student_code_raw)
                student_code = re.sub(r'^\s*\|\s*', '', student_code, flags=re.MULTILINE)
                student_code = student_code.strip()

        task_data: Dict[str, str] = {
            "task_id": test_id,
            "task_name": alg_name,
            "task_init": dano_clean,
            "task_todo": nado_clean,
            "tast_kum_code": student_code
        }
        all_tasks_data.append(task_data)
          # Логирование для отладки
        if test_id in ["10", "13", "20", "22"]:  # Детальная отладка для некоторых задач
            print(f"task_id={test_id}: надо='{nado_clean[:50]}...', код='{student_code[:50]}...'")
        else:
            print(f"task_id={test_id}: код={'найден' if student_code else 'НЕ НАЙДЕН'} ({len(student_code)} символов)")
    
    all_tasks_data.sort(key=lambda x: int(x['task_id']) if x['task_id'].isdigit() else 0)
    
    print(f"Всего обработано и готово к записи: {len(all_tasks_data)} задач.")

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(all_tasks_data, f, ensure_ascii=False, indent=4)
        print(f"Данные успешно сохранены в файл: {json_file_path}")
    except IOError as e:
        print(f"Ошибка записи в файл: {e}")

if __name__ == '__main__':
    xml_filename = 'pol_kurs.xml'
    json_filename = 'tasks_output.json'
    
    if os.path.exists(xml_filename):
        parse_kumir_xml_to_json(xml_filename, json_filename)
    else:
        print(f"Ошибка: Не найден исходный файл '{xml_filename}'.")
        print("Пожалуйста, поместите его в одну папку со скриптом или укажите правильный путь.")
