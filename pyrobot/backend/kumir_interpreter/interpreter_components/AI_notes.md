## Заметки AI

### Контекст Задачи
Основная задача - отладка и завершение реализации `pyrobot\backend\kumir_interpreter\interpreter_components\expression_evaluator.py`.

### План работы
1.  **Добавить импорты в `expression_evaluator.py`**:
    *   `from ..kumir_datatypes import KumirValue, KumirType`
    *   `import sys`
    *   `from ..kumir_exceptions import KumirEvalError, KumirTypeError, KumirNameError`
2.  **Интегрировать `KumirValue` и `KumirType`**: Заменить временные строковые типы (например, `"INTEGER"`) на `KumirType.INT.value`, `KumirType.REAL.value` и т.д. во всех `visit` методах, где создаются экземпляры `KumirValue`.
3.  **Проверить и доработать `visitSimpleAssignmentExpression`**: Убедиться, что он корректно работает с простыми переменными и возвращает `KumirValue`. Реализацию для таблиц и `знач` пока оставим на потом.
4.  **Начать реализацию `visitPrimaryExpression`**: Сфокусируемся на обработке идентификаторов (загрузка значения переменной из `scope_manager`) и литералов.

### Выполненные изменения
- Создан файл AI_notes.md
- Добавлены импорты `KumirValue`, `KumirType`, `KumirEvalError`, `KumirTypeError`, `KumirNameError`, `KumirRuntimeError`, `KumirNotImplementedError` и `sys` в `expression_evaluator.py`.
