import xml.etree.ElementTree as ET
import json
import re
import os
from typing import Optional, List, Dict, Any, Set

def parse_kumir_xml_to_json(xml_file_path: str, json_file_path: str) -> None:
    """
    Парсит XML-файл с задачами Кумира и сохраняет их в JSON.
    Эта версия не содержит проблемных конструкций и доверяет обработку
    XML-сущностей парсеру.
    """
    if not os.path.exists(xml_file_path):
        print(f"Ошибка: Файл не найден по пути: {xml_file_path}")
        return

    all_tasks_data: List[Dict[str, Any]] = []
    processed_ids: Set[str] = set()

    # Паттерн для разбора пользовательского блока
    pattern = re.compile(
        r"алг\s+(?P<name>.*?)\s*\|@protected\s*"
        r"дано\s*\|(?P<dano>.*?)\|@protected\s*"
        r"надо\s*\|(?P<nado>.*?)\|@protected\s*"
        r"(?P<code>.*)",
        re.DOTALL
    )

    try:
        tree = ET.parse(xml_file_path)
        root: ET.Element = tree.getroot()
    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
        return

    elements_to_process = root.findall('.//USER_PRG') + root.findall('.//TESTED_PRG')

    for task_element in elements_to_process:
        test_id: Optional[str] = task_element.get('testId')
        prg_full_code: Optional[str] = task_element.get('prg')

        if not prg_full_code or not test_id or test_id in processed_ids:
            continue
        
        processed_ids.add(test_id)
        
        # XML-парсер уже преобразовал в \n.
        # Никаких дополнительных замен не требуется.
        # Просто убираем лишние пробелы по краям всей строки.
        prg_full_code = prg_full_code.strip()

        # 1. Изолируем пользовательский блок по последнему маркеру конца
        end_marker = 'кон|@protected'
        end_marker_pos = prg_full_code.rfind(end_marker)
        
        if end_marker_pos == -1:
            continue

        user_block = prg_full_code[:end_marker_pos + len(end_marker)]

        # 2. Находим начало основного алгоритма (для задач с глобальными переменными)
        alg_marker_pos = user_block.find('алг ')
        if alg_marker_pos == -1:
            continue
            
        main_alg_block = user_block[alg_marker_pos:]
        
        # 3. Применяем regex к чистому блоку
        match = pattern.search(main_alg_block)
        
        if match:
            data = match.groupdict()
            
            # Очистка извлеченных секций
            dano_clean = data['dano'].strip().replace('\n       |', '\n').replace('|', '')
            nado_clean = data['nado'].strip().replace('\n       |', '\n').replace('|', '')
            full_code = data['code'].replace('|@protected', '').strip()
            
            task_data = {
                "testId": test_id,
                "название": data['name'].strip(),
                "дано": dano_clean,
                "надо": nado_clean,
                "ученический_код": full_code
            }
            all_tasks_data.append(task_data)
        else:
            print(f"Предупреждение: не удалось разобрать пользовательский блок для testId={test_id}")
    
    all_tasks_data.sort(key=lambda x: int(x['testId']) if x['testId'].isdigit() else 0)
    
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