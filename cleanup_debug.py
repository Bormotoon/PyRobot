import re

# Список файлов для очистки
files_to_clean = [
    'c:/Users/Bormotoon/VSCodeProjects/PyRobot/pyrobot/backend/kumir_interpreter/interpreter_components/statement_visitors.py',
    'c:/Users/Bormotoon/VSCodeProjects/PyRobot/pyrobot/backend/kumir_interpreter/interpreter_components/control_flow_visitors.py'
]

# Паттерны для поиска строк с DEBUG принтами
patterns = [
    r'            print\(f"!!! \[DEBUG.*?!!!", file=sys\.stderr\)\n',
    r'                    print\(f"!!! \[DEBUG.*?!!!", file=sys\.stderr\)\n',
    r'                print\(f"\[DEBUG.*?", file=sys\.stderr\)\n',
    r'            print\(f"\[DEBUG.*?", file=sys\.stderr\)\n',
    r'        print\(f"\[DEBUG.*?", file=sys\.stderr\)\n',
    r'                        print\(f"\[DEBUG.*?", file=sys\.stderr\)\n'
]

for file_path in files_to_clean:
    print(f'Очищаю файл: {file_path}')
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Удаляем все такие строки
    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Сохраняем файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Файл {file_path} очищен')

print('Все отладочные принты удалены!')
