import re

def clean_debug_prints(file_path):
    """Аккуратно удаляет отладочные принты, сохраняя структуру файла"""
    print(f'Очищаю файл: {file_path}')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Проверяем, является ли строка отладочным принтом
        if ('print(f"!!! [DEBUG' in line or 
            'print(f"[DEBUG' in line):
            # Пропускаем эту строку
            i += 1
            continue
        
        # Проверяем закомментированные отладочные принты
        if ('# print(f"!!! [DEBUG' in line or 
            '# print(f"[DEBUG' in line):
            # Пропускаем эту строку
            i += 1
            continue
            
        cleaned_lines.append(line)
        i += 1
    
    # Записываем очищенный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f'Файл {file_path} очищен')

# Список файлов для очистки
files_to_clean = [
    'c:/Users/Bormotoon/VSCodeProjects/PyRobot/pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py',
    'c:/Users/Bormotoon/VSCodeProjects/PyRobot/pyrobot/backend/kumir_interpreter/interpreter_components/statement_visitors.py'
]

for file_path in files_to_clean:
    clean_debug_prints(file_path)

print('Все отладочные принты удалены!')
