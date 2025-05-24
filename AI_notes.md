# Заметки AI по проекту PyRobot

---

## Общая информация по проекту

* **Запуск тестов:**
  * Все тесты: `python -m pytest -v tests/test_functional.py`
  * Конкретный тест: `python -m pytest -v tests/test_functional.py -k "имя_файла.kum"`
  * Все файлы kum: `tests/polyakov_kum`
* **Документация по языку Кумир:** `kumir2-master/userdocs/`
* **Исходный код оригинального Кумира (C++):** `kumir2-master/src`
* **Наиболее важные исходники:** `kumir2-master/src/kumir2-libs`, `kumir2-master/src/plugins`

---

# Выдержки из документации КуМир
алг тест_вывода
нач
  вывод "Привет, мир!", нс, "Как дела?"
  вывод "Это новая строка."
  вывод "Число:", 5, " Текст ", "еще текст"
  вывод вещественное число(2.5)
кц

Вывод нескольких значений через запятую:
* Если первое значение – строка, то все последующие значения выводятся подряд, без пробелов.
* Если первое значение – не строка, то перед каждым последующим значением выводится пробел.
* `нс` (нет символа) – специальное значение, которое отменяет автоматический перевод строки после вывода. Если `нс` не указан, то после вывода всех значений курсор переводится на новую строку.
* Неявные переносы строк в длинных строковых литералах не поддерживаются стандартным КуМиром так, как это может быть в некоторых других языках. Строка должна быть либо на одной строке в коде, либо конкатенироваться из нескольких частей.

---

## Заметки по доработке интерпретатора КуМира (до рефакторинга компонентов)

1.  **Обработка ошибок типов:**
    *   При присваивании значения неподходящего типа переменной (например, строки в целую).
    *   При передаче аргументов неверного типа в процедуры/функции.
    *   При использовании несовместимых типов в арифметических/логических операциях.
2.  **Области видимости:**
    *   Корректная работа с глобальными и локальными переменными.
    *   Обработка перекрытия имен.
    *   Видимость переменных внутри блоков (циклы, условия).
3.  **Массивы:**
    *   Объявление массивов с указанием границ.
    *   Доступ к элементам массива по индексу.
    *   Контроль выхода за границы массива.
    *   Многомерные массивы (если поддерживаются).
4.  **Процедуры и функции:**
    *   Объявление и вызов.
    *   Передача аргументов по значению и по ссылке (если есть `арг рез`).
    *   Возврат значений из функций.
    *   Рекурсивные вызовы.
5.  **Встроенные функции и процедуры:**
    *   Реализация основных встроенных функций (например, `цел`, `вещ`, `лог`, `текст`, `длина`, `копировать` и т.д.).
    *   Реализация встроенных процедур (например, `ввод`, `вывод`).
6.  **Управляющие конструкции:**
    *   Циклы (`нц для`, `нц пока`, `кц`).
    *   Условия (`если ... то ... иначе ... все`).
    *   Выход из циклов (`выход`).
7.  **Типы данных:**
    *   Корректная работа с основными типами: `цел`, `вещ`, `лог`, `сим`, `лит`.
    *   Преобразование типов (явное и неявное, если применимо).
8.  **Комментарии:**
    *   Игнорирование комментариев (обычно `|` до конца строки).
9.  **Обработка конца файла и ошибок парсинга:**
    *   Корректное завершение работы при достижении конца файла.
    *   Вывод информативных сообщений об ошибках синтаксического анализа.

---

## Заметки по разработке (до рефакторинга компонентов)

**2024-03-21:**
*   Начало работы над интерпретатором.
*   Создана базовая структура проекта.
*   Реализован парсер для основных конструкций языка.

**2024-04-10:**
*   Добавлена поддержка объявления переменных.
*   Реализована базовая логика присваивания.

**2024-05-15:**
*   Начата работа над арифметическими выражениями.
*   Добавлена поддержка операторов `+`, `-`, `*`, `/`.

**2024-06-01:**
*   Реализованы условные операторы (`если ... то ... иначе ... все`).
*   Добавлена поддержка логических выражений.

**2024-07-20:**
*   Начата работа над циклами (`нц для`, `нц пока`).
*   Реализована базовая логика итераций.

**2024-08-02:**
*   Обсуждение реализации `ExpressionEvaluator`.
*   План: выделить `ExpressionEvaluator` из основного класса интерпретатора.
*   Начать с `visitLiteral` и `visitQualifiedIdentifier`.

---
## 2025-05-23: Рефакторинг ExpressionEvaluator (Начало новой фазы)

**Контекст:** Продолжение рефакторинга `interpreter.py` с выделением `ExpressionEvaluator`. Пользователь выразил понимание сложности процесса и готов продолжать.
**План на тот момент:**
1.  Завершить реализацию методов в `pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py`.
    *   Реализовать `visitUnaryExpression`.
    *   Реализовать `visitPowerExpression`.
    *   Заполнить операционную логику в `visitMultiplicativeExpression`.
    *   Заполнить операционную логику в `visitAdditiveExpression`.
2.  Интегрировать и тщательно протестировать `ExpressionEvaluator`.

---
## 2025-05-24: Интеграция компонентов и отладка

**Контекст:** После завершения начального этапа рефакторинга `ExpressionEvaluator` и его интеграции с `KumirInterpreterVisitor` (а также других компонентов, таких как `ScopeManager`, `ProcedureManager`, `StatementHandler`, `DeclarationVisitorMixin`), начат запуск функциональных тестов (`tests/test_functional.py`) для выявления и устранения проблем.

**Обнаруженные и исправленные ошибки (хронология):**

1.  **`TabError: inconsistent use of tabs and spaces in indentation`**
    *   **Место:** `pyrobot/backend/kumir_interpreter/kumir_exceptions.py`.
    *   **Действие:** Исправлены отступы.
    *   **Статус:** Исправлено.

2.  **`ImportError: cannot import name 'KumirRuntimeError' from 'pyrobot.backend.kumir_interpreter.kumir_exceptions'`**
    *   **Место:** Импорт в `pyrobot/backend/kumir_interpreter/interpreter_components/main_visitor.py`.
    *   **Действие:** Добавлен класс `KumirRuntimeError(KumirExecutionError)` в `kumir_exceptions.py`.
    *   **Статус:** Исправлено.

3.  **`SyntaxError: unterminated f-string literal`**
    *   **Место:** `pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py`.
    *   **Действие:** Исправлена f-строка.
    *   **Статус:** Исправлено.

4.  **`ImportError: cannot import name 'StatementVisitorMixin'` (и аналогичные для других компонентов)**
    *   **Причина:** Отсутствие классов-заглушек или проблемы с их экспортом через `interpreter_components/__init__.py`.
    *   **Действия:** Созданы заглушки, скорректирован `__init__.py`, унифицированы импорты в `main_visitor.py`.
    *   **Статус:** Исправлено.

5.  **Ошибки компиляции в `main_visitor.py` после унификации импортов:**
    *   `Expected 0 positional arguments` для `IOHandler`.
        *   **Действие:** Добавлен конструктор в `IOHandler`.
    *   `Cannot access attribute "visitArrayLiteral"` для `ExpressionEvaluator`.
        *   **Действие:** Добавлены заглушки методов `visit*` в `ExpressionEvaluator`.
    *   **Статус:** Исправлено.

6.  **`SyntaxError: invalid syntax` (артефакт `</rewritten_file>`)**
    *   **Место:** `pyrobot/backend/kumir_interpreter/interpreter_components/builtin_functions.py`.
    *   **Действие:** Удалена ошибочная строка.
    *   **Статус:** Исправлено.

7.  **`ImportError: cannot import name 'ScopeManager' from partially initialized module 'pyrobot.backend.kumir_interpreter.interpreter_components'` (циклический импорт)**
    *   **Причина:** Цикл между `main_visitor.py` и `interpreter_components/__init__.py`.
    *   **Действия:** Убран импорт `KumirInterpreterVisitor` из `__init__.py`, импорты в `main_visitor.py` изменены на прямые.
    *   **Статус:** Исправлено.

8.  **`AttributeError: 'KumirInterpreterVisitor' object has no attribute '_validate_and_convert_value_for_assignment'`**
    *   **Действие:** Добавлена заглушка метода в `KumirInterpreterVisitor`.
    *   **Статус:** Исправлено (заглушкой).

9.  **`ImportError: cannot import name 'LoopBreakException' from 'pyrobot.backend.kumir_interpreter.kumir_exceptions'`**
    *   **Действие:** Добавлены `LoopBreakException` и `LoopContinueException` в `kumir_exceptions.py`.
    *   **Статус:** Исправлено.

10. **`AttributeError: 'KumirInterpreterVisitor' object has no attribute '_get_type_info_from_specifier'`**
    *   **Место:** `declaration_visitors.py`.
    *   **Действие:** Вызов заменен на `self._get_type_from_specifier_node(type_spec_ctx)`.
    *   **Статус:** Исправлено.

11. **`AttributeError: 'KumirInterpreterVisitor' object has no attribute '_create_variable_in_scope'`**
    *   **Место:** `declaration_visitors.py`.
    *   **Действие:** Вызовы заменены на `self.visitor.scope_manager.declare_variable(...)`.
    *   **Статус:** Исправлено.

12. **`ImportError: cannot import name 'StopExecutionException' from 'pyrobot.backend.kumir_interpreter.kumir_exceptions'` (повторяющаяся)**
    *   **Причина:** Изначально в `kumir_exceptions.py` был `StopExecutionSignal`. В `statement_handlers.py` ожидался `StopExecutionException`.
    *   **Действия:**
        *   `StopExecutionSignal` в `kumir_exceptions.py` переименован в `StopExecutionException` и сделан наследником `KumirExecutionError`.
        *   Проверены импорты в `statement_handlers.py`.
        *   Проведена очистка кэша `__pycache__`.
        *   Проведен изолированный тест импорта (показал, что абсолютный импорт работает).
        *   Изменен `statement_handlers.py` для импорта `kumir_exceptions as ke` и отладочной печати для проверки наличия `StopExecutionException`. **Ожидается запуск тестов пользователем для анализа вывода.**
    *   **Статус:** **В процессе отладки.**

**Уточнение по `ExpressionEvaluator` (добавлено 2025-05-24):**
*   В проекте существуют два файла:
    1.  `pyrobot/backend/kumir_interpreter/expression_evaluator.py` (старый, большой, более полный, но, вероятно, не используется активно).
    2.  `pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py` (новый, активный, над которым идет работа).
*   **Стратегия:** "Старый" файл служит источником логики. "Новый" файл является целевым компонентом в рефакторинге. Логика из старого файла переносится и адаптируется в новый, метод за методом.
*   **Задача:** Постепенно наполнить `interpreter_components/expression_evaluator.py` необходимой функциональностью, заимствуя и адаптируя код из `kumir_interpreter/expression_evaluator.py`.

**Текущая задача (основная):** Исправление ошибки `ImportError: cannot import name 'StopExecutionException'` в `statement_handlers.py`.
**Последние действия по ошибке:**
*   Изменен `statement_handlers.py` для импорта `kumir_exceptions as ke` и отладочной печати для проверки наличия `StopExecutionException`. **Ожидается запуск тестов пользователем для анализа вывода.**
**План по ошибке:**
1.  Получить от пользователя результат запуска тестов после изменения `statement_handlers.py`.
2.  Проанализировать вывод, особенно отладочную печать.
3.  Устранить `ImportError`.

**План по `ExpressionEvaluator` (после устранения `ImportError`):**
1.  Выбрать нереализованный метод в `interpreter_components/expression_evaluator.py` (например, `visitUnaryExpression`).
2.  Найти его реализацию в `kumir_interpreter/expression_evaluator.py`.
3.  Перенести и адаптировать реализацию в новый компонент.
4.  Повторять для других методов.

---

## План на 24.05.2025 (продолжение)

1.  **Исправить несоответствия имен контекстов ANTLR (Приоритет!):**
    *   Исправить тип `KumirParser.VariableDeclarationStatementContext` на `KumirParser.VariableDeclarationItemContext` в `pyrobot/backend/kumir_interpreter/statement_handlers.py`.
    *   Систематически проверить и исправить все остальные аннотации типов контекстов ANTLR (например, `WhileLoopContext`, `ForLoopContext`, `AssignmentStatementContext`, `IoStatementContext`, `IfStatementContext`, `ExpressionContext`, `ProcedureCallStatementContext`, `FunctionCallStatementContext`, `ReturnStatementContext`, `BlockContext`, `SubAlgorithmContext`) в `statement_handlers.py` и других затронутых файлах компонентов. Для этого потребуется сравнить имена из `kumir_lang/KumirParser.g4` и сгенерированного `pyrobot/backend/kumir_interpreter/generated/KumirParser.py` с используемыми аннотациями.
2.  **Решить `ImportError: cannot import name 'StopExecutionException'`:** Эта ошибка была отмечена ранее и может снова проявиться или быть замаскирована текущими ошибками контекста ANTLR.
3.  **Устранить `ModuleNotFoundError` в `statement_handlers.py` для относительного импорта:** (например, `.kumir_variable`, `.kumir_scope`, `.utils`). Это требует расследования, возможно, связано с `PYTHONPATH` или контекстом выполнения тестов.
4.  **Продолжить рефакторинг `ExpressionEvaluator`:** Систематически переносить и адаптировать логику из старого `expression_evaluator.py` в новый, расположенный в `interpreter_components`.
5.  **Систематическая отладка функциональных тестов:** После решения критических ошибок импорта и атрибутов, запустить функциональные тесты (`python -m pytest -v c:/Users/Bormotoon/VSCodeProjects/PyRobot/tests/test_functional.py > test_log.txt`) и методично исправлять сбои, указанные в `test_log.txt`.
6.  **Очистка кода:** Удалить все временные диагностические операторы `print` и неиспользуемые/временные импорты после того, как их цель будет достигнута.

**Выполненные шаги (24.05.2025):**
*   Записан текущий план в `AI_notes.md`.
*   Внесено исправление `VariableDeclarationStatementContext` -> `VariableDeclarationItemContext` в `statement_handlers.py`.

---

## План по VariableDeclaration:

1.  **`statement_handlers.py`**:
    *   Удалить метод `handle_variable_declaration`.
    *   Изменить `visitVariableDeclarationStatement` для вызова `self.interpreter.visitVariableDeclaration(ctx)` с типом `ctx: KumirParser.VariableDeclarationContext`.
    *   Проверить импорт `KumirParser`.
2.  **`interpreter_components/main_visitor.py` (и `declaration_visitors.py`)**:
    *   Проверить, что `visitVariableDeclaration` (из миксина) корректно вызывается при обходе дерева разбора для узла `variableDeclaration`.
    *   Убедиться, что `scope_manager.declare_variable` вызывается с корректными аргументами из `DeclarationVisitorMixin.visitVariableDeclaration`.
3.  **`interpreter_components/scope_manager.py`**:
    *   Метод `declare_variable` используется вместо `create_variable`. Проверить его использование.

## Текущие задачи (после VariableDeclaration):

1.  **Проверить `ScopeManager.declare_variable`**: Убедиться, что он корректно обрабатывает все случаи (скаляры, таблицы, инициализация).
2.  **Систематический обзор контекстов ANTLR**: Проверить все остальные обработчики операторов и выражений на корректное использование контекстов ANTLR.
3.  **Решить `ImportError: cannot import name 'StopExecutionException'`**: Если ошибка снова появится.
4.  **Решить `ModuleNotFoundError` для относительных импортов в `statement_handlers.py`**.
5.  **Продолжить рефакторинг `ExpressionEvaluator`**.
6.  **Систематическая отладка функциональных тестов**.
7.  **Очистка кода**: Удалить временные `print` и неиспользуемые импорты.