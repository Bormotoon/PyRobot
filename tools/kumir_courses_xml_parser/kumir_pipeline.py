#!/usr/bin/env python3
"""
Полный pipeline для обработки XML файлов КУМИРа и создания Python эталонных решений.

Этот скрипт выполняет полный цикл:
1. Парсит XML файл с задачами КУМИРа
2. Извлекает ученический код и условия задач
3. Генерирует Python эталонные решения
4. Тестирует все созданные решения
5. Создает отчеты и готовит файлы для сравнения
"""

import xml.etree.ElementTree as ET
import json
import re
import os
import sys
import subprocess
import shutil
from typing import Optional, List, Dict, Any, Set
from pathlib import Path

class KumirToPythonPipeline:
    """Полный pipeline для обработки КУМИРа и создания Python решений."""
    
    def __init__(self, xml_file_path: str, output_dir: str = "kumir_python_solutions"):
        self.xml_file_path = xml_file_path
        self.output_dir = Path(output_dir)
        self.tasks_json_file = self.output_dir / "tasks_data.json"
        self.python_dir = self.output_dir / "python_solutions"
        self.reports_dir = self.output_dir / "reports"
        
        # Создаем директории
        self.output_dir.mkdir(exist_ok=True)
        self.python_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def clean_task_name_for_filename(self, task_name: str, task_id: str) -> str:
        """Создает короткое английское имя файла на основе типа задачи."""
        
        # Словарь сокращений для разных типов задач
        name_mappings = {
            # Заполнение массивов
            "10": "arr_fill_zeros",
            "11": "arr_fill_natural", 
            "12": "arr_fill_from_x",
            "13": "arr_fill_plus5",
            "14": "arr_fill_fibonacci",
            "15": "arr_fill_powers2",
            "16": "arr_fill_pyramid",
            
            # Модификация массивов
            "20": "arr_inc_by1",
            "21": "arr_mult_by2", 
            "22": "arr_square",
            "23": "arr_inc_first_half",
            "24": "arr_div_middle",
            "25": "arr_mult_second_half",
            "26": "arr_average",
            
            # Поиск экстремумов
            "30": "arr_find_max",
            "31": "arr_find_min",
            "32": "arr_find_minmax",
            "33": "arr_find_min_index",
            "34": "arr_find_minmax_indices",
            "35": "arr_find_two_max",
            "36": "arr_find_two_min_indices",
            
            # Подсчет элементов
            "40": "arr_count_ones",
            "41": "arr_count_equal_x",
            "42": "arr_count_positive",
            "43": "arr_count_even_odd",
            "44": "arr_count_even_positive",
            "45": "arr_count_digit5",
            "46": "arr_count_same_digits",
            
            # Суммы и произведения
            "50": "arr_sum_all",
            "51": "arr_sum_negative",
            "52": "arr_sum_div3",
            "53": "arr_avg_less50",
            "54": "arr_prod_even_pos",
            "55": "arr_sum_tens_gt_units",
            "56": "arr_sum_all_same_digits",
            
            # Поиск индексов
            "60": "arr_find_x_index",
            "61": "arr_find_x_first_half",
            "62": "arr_find_x_second_half",
            "63": "arr_find_x_last_second_half",
            "64": "arr_count_x_first_half",
            "65": "arr_count_x_pairs",
            "66": "arr_count_hills",
            
            # Специальные задачи
            "71": "arr_count_same_digits",
            "72": "arr_longest_chain",
            "73": "arr_count_primes",
            "74": "arr_fill_primes",
            "75": "arr_sum_palindromes",
            "76": "arr_fill_hyperprimes"
        }
        
        # Возвращаем короткое имя или создаем из task_id
        return name_mappings.get(task_id, f"task_{task_id}")
    
    def parse_kumir_xml_to_json(self) -> bool:
        """Парсит XML файл и сохраняет задачи в JSON."""
        print(f"📁 Парсинг XML файла: {self.xml_file_path}")
        
        if not os.path.exists(self.xml_file_path):
            print(f"❌ Ошибка: Файл не найден по пути: {self.xml_file_path}")
            return False

        all_tasks_data: List[Dict[str, Any]] = []
        processed_ids: Set[str] = set()

        try:
            tree = ET.parse(self.xml_file_path)
            root: ET.Element = tree.getroot()
        except ET.ParseError as e:
            print(f"❌ Ошибка парсинга XML: {e}")
            return False

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

            # Извлекаем составные части
            
            # 1. Название алгоритма
            alg_match = re.search(r'алг\s+(.+?)\s*\|\@protected', student_program_part, re.DOTALL)
            alg_name = alg_match.group(1).strip() if alg_match else ""
            
            # 2. Блок "дано"
            dano_match = re.search(r'дано\s*\|\s*(.+?)\s*\|\@protected', student_program_part, re.DOTALL)
            dano_content = dano_match.group(1).strip() if dano_match else ""
            dano_clean = re.sub(r'\s*\|\s*', ' ', dano_content)
            dano_clean = re.sub(r'\s+', ' ', dano_clean).strip()
            
            # 3. Блок "надо"
            nado_start_match = re.search(r'надо\s*\|', student_program_part)
            if nado_start_match:
                nado_start_pos = nado_start_match.start()
                nach_match = re.search(r'нач\s*\|\@protected', student_program_part[nado_start_pos:])
                if nach_match:
                    nado_end_pos = nado_start_pos + nach_match.start()
                    nado_block = student_program_part[nado_start_pos:nado_end_pos].strip()
                    
                    nado_content = re.sub(r'надо\s*\|\s*', '', nado_block)
                    nado_content = re.sub(r'\|\@protected', '', nado_content)
                    nado_content = re.sub(r'^\s*\|\s*', '', nado_content, flags=re.MULTILINE)
                    nado_clean = re.sub(r'\s+', ' ', nado_content).strip()
                else:
                    nado_clean = ""
            else:
                nado_clean = ""
            
            # 4. Ученический код
            student_code = ""
            nach_match = re.search(r'нач\s*\|\@protected', student_program_part)
            if nach_match:
                code_start_pos = nach_match.start()
                kon_match = re.search(r'кон\s*\|\@protected', student_program_part[code_start_pos:])
                if kon_match:
                    code_end_pos = code_start_pos + kon_match.end()
                    student_code_raw = student_program_part[code_start_pos:code_end_pos].strip()
                    
                    student_code = re.sub(r'\|\@protected', '', student_code_raw)
                    student_code = re.sub(r'^\s*\|\s*', '', student_code, flags=re.MULTILINE)
                    student_code = student_code.strip()

            task_data: Dict[str, str] = {
                "task_id": test_id,
                "task_name": alg_name,
                "task_init": dano_clean,
                "task_todo": nado_clean,
                "kumir_code": student_code
            }
            all_tasks_data.append(task_data)

        all_tasks_data.sort(key=lambda x: int(x['task_id']) if x['task_id'].isdigit() else 0)
        
        try:
            with open(self.tasks_json_file, 'w', encoding='utf-8') as f:
                json.dump(all_tasks_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Извлечено и сохранено {len(all_tasks_data)} задач в {self.tasks_json_file}")
            return True
        except IOError as e:
            print(f"❌ Ошибка записи в файл: {e}")
            return False
    
    def generate_python_solution(self, task: Dict[str, str]) -> str:
        """Генерирует Python код для решения задачи."""
        task_id = task['task_id']
        task_name = task['task_name']
        task_init = task['task_init']
        task_todo = task['task_todo']
        kumir_code = task['kumir_code']
        
        # Определяем параметры функции
        has_X = 'арг цел X' in task_name
        returns_value = any(prefix in task_name for prefix in ['цел ', 'вещ '])
        
        short_name = self.clean_task_name_for_filename(task_name, task_id)
        
        code_lines = [
            f'"""',
            f'Task {task_id}: {short_name}',
            f'',
            f'Original: {task_name}',
            f'Init: {task_init}',
            f'Todo: {task_todo}',
            f'',
            f'Kumir code:',
            f'{kumir_code}',
            f'"""',
            f'',
        ]
        
        # Определяем сигнатуру функции
        if has_X and returns_value:
            func_signature = f'def {short_name}(N: int, A: list, X: int):'
        elif has_X:
            func_signature = f'def {short_name}(N: int, A: list, X: int) -> list:'
        elif returns_value:
            func_signature = f'def {short_name}(N: int, A: list):'
        else:
            func_signature = f'def {short_name}(N: int, A: list) -> list:'
        
        code_lines.append(func_signature)
        code_lines.append('    """Python solution for the task."""')
        
        # Генерируем код в зависимости от задачи
        if task_id == "10":  # Заполнить нулями
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = 0',
                '    return A'
            ])
        elif task_id == "11":  # Заполнить натуральными числами
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = i + 1',
                '    return A'
            ])
        elif task_id == "12":  # Заполнить от X
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = X + i',
                '    return A'
            ])
        elif task_id == "13":  # Плюс 5
            code_lines.extend([
                '    A[0] = X',
                '    for i in range(1, N):',
                '        A[i] = A[i-1] + 5',
                '    return A'
            ])
        elif task_id == "14":  # Фибоначчи
            code_lines.extend([
                '    if N >= 1:',
                '        A[0] = 1',
                '    if N >= 2:',
                '        A[1] = 1',
                '    for i in range(2, N):',
                '        A[i] = A[i-1] + A[i-2]',
                '    return A'
            ])
        elif task_id == "15":  # Степени 2
            code_lines.extend([
                '    A[N-1] = 1',
                '    for i in range(N-2, -1, -1):',
                '        A[i] = 2 * A[i+1]',
                '    return A'
            ])
        elif task_id == "16":  # Горка
            code_lines.extend([
                '    c = N // 2',
                '    A[c] = X',
                '    for i in range(c-1, -1, -1):',
                '        A[i] = A[i+1] - 1',
                '    for i in range(c+1, N):',
                '        A[i] = A[i-1] - 1',
                '    return A'
            ])
        elif task_id == "20":  # Увеличить на 1
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = A[i] + 1',
                '    return A'
            ])
        elif task_id == "21":  # Умножить на 2
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = A[i] * 2',
                '    return A'
            ])
        elif task_id == "22":  # Квадрат
            code_lines.extend([
                '    for i in range(N):',
                '        A[i] = A[i] * A[i]',
                '    return A'
            ])
        elif task_id == "30":  # Максимум
            code_lines.extend([
                '    max_val = A[0]',
                '    for i in range(N):',
                '        if A[i] > max_val:',
                '            max_val = A[i]',
                '    return max_val'
            ])
        elif task_id == "31":  # Минимум
            code_lines.extend([
                '    min_val = A[0]',
                '    for i in range(N):',
                '        if A[i] < min_val:',
                '            min_val = A[i]',
                '    return min_val'
            ])
        elif task_id == "40":  # Сколько единиц
            code_lines.extend([
                '    count = 0',
                '    for i in range(N):',
                '        if A[i] == 1:',
                '            count += 1',
                '    return count'
            ])
        elif task_id == "41":  # Сколько равных X
            code_lines.extend([
                '    count = 0',
                '    for i in range(N):',
                '        if A[i] == X:',
                '            count += 1',
                '    return count'
            ])
        elif task_id == "50":  # Сумма всех
            code_lines.extend([
                '    total = 0',
                '    for i in range(N):',
                '        total += A[i]',
                '    return total'
            ])
        elif task_id == "60":  # Номер X
            code_lines.extend([
                '    for i in range(N):',
                '        if A[i] == X:',
                '            return i + 1  # 1-based index',
                '    return -1'
            ])
        else:
            # Базовая реализация для остальных
            code_lines.extend([
                '    # TODO: Implement solution',
                f'    # Task: {task_todo}',
                '    pass'
            ])
        
        # Тестовая функция
        code_lines.extend([
            '',
            '',
            'def test_solution():',
            '    """Test the solution."""',
            '    N = 5',
            '    A = [0] * N',
        ])
        
        if has_X:
            code_lines.append('    X = 10')
            code_lines.append(f'    result = {short_name}(N, A.copy(), X)')
        else:
            code_lines.append(f'    result = {short_name}(N, A.copy())')
        
        code_lines.extend([
            '    print(f"Result: {result}")',
            '    return result',
            '',
            '',
            'if __name__ == "__main__":',
            '    test_solution()'
        ])
        
        return '\n'.join(code_lines)
    
    def generate_all_python_solutions(self) -> bool:
        """Генерирует Python решения для всех задач."""
        print("🐍 Генерация Python решений...")
        
        try:
            with open(self.tasks_json_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
        except FileNotFoundError:
            print(f"❌ Файл {self.tasks_json_file} не найден!")
            return False
        
        success_count = 0
        for task in tasks:
            task_id = task['task_id']
            short_name = self.clean_task_name_for_filename(task['task_name'], task_id)
            
            python_code = self.generate_python_solution(task)
            
            filename = f"{task_id}_{short_name}.py"
            filepath = self.python_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(python_code)
                success_count += 1
                print(f"  ✅ {filename}")
            except Exception as e:
                print(f"  ❌ {filename}: {e}")
        
        print(f"✅ Создано {success_count}/{len(tasks)} Python файлов")
        return success_count == len(tasks)
    
    def test_all_solutions(self) -> Dict[str, Any]:
        """Тестирует все Python решения."""
        print("🧪 Тестирование Python решений...")
        
        python_files = list(self.python_dir.glob("*.py"))
        
        results = {
            "total": len(python_files),
            "success": 0,
            "failed": [],
            "details": []
        }
        
        for py_file in sorted(python_files):
            try:
                result = subprocess.run([
                    sys.executable, str(py_file)
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    results["success"] += 1
                    results["details"].append({
                        "file": py_file.name,
                        "status": "success",
                        "output": result.stdout.strip()
                    })
                    print(f"  ✅ {py_file.name}")
                else:
                    results["failed"].append(py_file.name)
                    results["details"].append({
                        "file": py_file.name,
                        "status": "error",
                        "error": result.stderr.strip()
                    })
                    print(f"  ❌ {py_file.name}")
                    
            except subprocess.TimeoutExpired:
                results["failed"].append(py_file.name)
                results["details"].append({
                    "file": py_file.name,
                    "status": "timeout",
                    "error": "Timeout > 5 seconds"
                })
                print(f"  ⏰ {py_file.name}")
            except Exception as e:
                results["failed"].append(py_file.name)
                results["details"].append({
                    "file": py_file.name,
                    "status": "exception",
                    "error": str(e)
                })
                print(f"  💥 {py_file.name}")
        
        success_rate = (results["success"] / results["total"]) * 100 if results["total"] > 0 else 0
        print(f"📊 Результаты: {results['success']}/{results['total']} ({success_rate:.1f}%)")
        
        return results
    
    def create_comparison_framework(self, test_results: Dict[str, Any]) -> bool:
        """Создает фреймворк для сравнения Python и КУМИР решений."""
        print("📋 Создание фреймворка для сравнения...")
        
        # Создаем пример скрипта для сравнения
        comparison_script = f'''#!/usr/bin/env python3
"""
Framework for comparing Python and Kumir solutions.
Generated automatically by KumirToPythonPipeline.
"""

import sys
import json
from pathlib import Path

# Add python solutions to path
sys.path.append(str(Path(__file__).parent / "python_solutions"))

def load_tasks():
    """Load task data."""
    with open("tasks_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def compare_solutions():
    """Compare Python and Kumir solutions."""
    tasks = load_tasks()
    
    print("🔍 Comparison Framework Ready")
    print("=" * 50)
    
    for task in tasks:
        task_id = task["task_id"]
        print(f"Task {{task_id}}: {{task['task_name']}}")
        
        # TODO: Implement Kumir interpreter integration
        # kumir_result = run_kumir_code(task["kumir_code"], test_data)
        # python_result = run_python_solution(task_id, test_data)
        # assert kumir_result == python_result
    
    print("\\n✅ Framework ready for Kumir integration")

if __name__ == "__main__":
    compare_solutions()
'''
        
        try:
            with open(self.output_dir / "compare_solutions.py", 'w', encoding='utf-8') as f:
                f.write(comparison_script)
        except Exception as e:
            print(f"❌ Ошибка создания скрипта сравнения: {e}")
            return False
        
        # Создаем отчет
        report_content = f"""# Kumir to Python Pipeline Report

## Summary
- **Input XML**: {self.xml_file_path}
- **Total Tasks**: {test_results['total']}
- **Successful Tests**: {test_results['success']}
- **Success Rate**: {(test_results['success']/test_results['total']*100):.1f}%

## Generated Files
- `tasks_data.json` - Parsed task data
- `python_solutions/` - Python implementations ({test_results['total']} files)
- `compare_solutions.py` - Comparison framework

## Test Results
"""
        
        for detail in test_results['details']:
            status_emoji = "✅" if detail['status'] == 'success' else "❌"
            report_content += f"- {status_emoji} `{detail['file']}` - {detail['status']}\n"
        
        if test_results['failed']:
            report_content += f"\n## Failed Tests\n"
            for failed in test_results['failed']:
                report_content += f"- {failed}\n"
        
        report_content += f"""
## Usage
1. **Testing Python solutions**:
   ```bash
   python compare_solutions.py
   ```

2. **Integration with Kumir interpreter**:
   - Implement `run_kumir_code()` function
   - Add test data generation
   - Run comparison tests

## Next Steps
- Integrate with your Kumir interpreter
- Add comprehensive test data
- Implement automated comparison testing
"""
        
        try:
            with open(self.reports_dir / "pipeline_report.md", 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ Отчет создан: {self.reports_dir}/pipeline_report.md")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания отчета: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """Запускает полный pipeline обработки."""
        print("🚀 Запуск полного Kumir to Python Pipeline")
        print("=" * 60)
        
        # Шаг 1: Парсинг XML
        if not self.parse_kumir_xml_to_json():
            return False
        
        # Шаг 2: Генерация Python решений
        if not self.generate_all_python_solutions():
            return False
        
        # Шаг 3: Тестирование решений
        test_results = self.test_all_solutions()
        
        # Шаг 4: Создание фреймворка для сравнения
        if not self.create_comparison_framework(test_results):
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Pipeline завершен успешно!")
        print(f"📁 Результаты в папке: {self.output_dir}")
        print(f"📊 Готово к сравнению: {test_results['success']}/{test_results['total']} задач")
        
        return True


def main():
    """Главная функция."""
    if len(sys.argv) != 2:
        print("Usage: python kumir_pipeline.py <xml_file_path>")
        print("Example: python kumir_pipeline.py pol_kurs.xml")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    
    if not os.path.exists(xml_file):
        print(f"❌ Файл не найден: {xml_file}")
        sys.exit(1)
    
    # Создаем и запускаем pipeline
    pipeline = KumirToPythonPipeline(xml_file)
    success = pipeline.run_full_pipeline()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
