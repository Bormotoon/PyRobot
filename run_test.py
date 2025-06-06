#!/usr/bin/env python3
"""
Простой скрипт для запуска теста без pytest для проверки
"""

import sys
import os

# Добавляем корень проекта в sys.path
project_root = os.path.abspath('.')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pyrobot.backend.kumir_interpreter.runtime_utils import interpret_kumir

# Читаем файл 1-0.kum
with open('1-0.kum', 'r', encoding='utf-8') as f:
    code = f.read()

print("=== ЗАПУСК ТЕСТИРОВАНИЯ ===")
print(f"Код первые 100 символов: {code[:100]!r}")

# Вызываем интерпретатор
result = interpret_kumir(code, None)

print("=== РЕЗУЛЬТАТ ===")
print(f"Результат: {result!r}")

# Проверяем ожидаемые условия
checks = [
    ("Результат начинается с SYNTAX_ERROR:", result.startswith("SYNTAX_ERROR:")),
    ("Содержит 'mismatched input 'надо'':", "mismatched input 'надо'" in result),
    ("Содержит 'строка 3':", "строка 3" in result),
]

print("=== ПРОВЕРКИ ===")
all_passed = True
for check_name, check_result in checks:
    status = "✓ ПРОШЛА" if check_result else "✗ НЕ ПРОШЛА"
    print(f"{check_name} {status}")
    if not check_result:
        all_passed = False

print("=== ИТОГ ===")
if all_passed:
    print("✓ ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
else:
    print("✗ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОШЛИ")

sys.exit(0 if all_passed else 1)
