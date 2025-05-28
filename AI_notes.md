## Хронологически Упорядоченные Заметки AI по Проекту PyRobot

---

### УСПЕШНОЕ ИСПРАВЛЕНИЕ АРИФМЕТИЧЕСКИХ ВЫРАЖЕНИЙ (2025-01-02)

**✅ КРИТИЧЕСКИЙ БАГ ИСПРАВЛЕН:** Арифметические выражения теперь работают корректно!

**Проблема:** Тест `2-2+2.kum` выводил "Ответ: 2" вместо "Ответ: 4" - арифметика не вычислялась.

**Исправления в `expression_evaluator.py`:**
1. **visitRelationalExpression:** Заменён неправильный доступ `ctx.expression()` на корректный `ctx.additiveExpression()`
2. **visitAdditiveExpression:** Реализована настоящая арифметика вместо простого pass-through
3. **visitMultiplicativeExpression:** Добавлена поддержка *, /, div, mod операций
4. **Исправлены синтаксические ошибки** с многострочным кодом в Python

**Результат тестирования:**
- ✅ `python test_current.py` → "Ответ: 4" (было "Ответ: 2")
- ✅ Арифметическое выражение `2+2` правильно вычисляется как `4`
- ✅ Корректная обработка типов ЦЕЛ/ВЕЩ

**Следующие шаги:**
1. Запустить основной функциональный тест для `2-2+2.kum`
2. Убрать отладочные print после подтверждения работы
3. Продолжить реализацию других уровней операций (реляционные, логические)

---

### Новое Уточнение по `вывод` и `нс` (2025-05-28)
**Источник:** `kum_reference.md` (предоставлен пользователем 2025-05-28).

- **Команда `вывод`**: Печатает аргументы подряд. **Не добавляет** новую строку (`\\n`) автоматически в конце.
- **Аргумент `нс`**: При использовании в `вывод` означает "напечатать символ новой строки (`\\n`)".
- **Итог**: Новая строка появляется только там, где в `вывод` указан `нс`.

**Пример из `kum_reference.md`:**
`вывод а, " ", б, "Привет!", нс` -> каждая такая команда выведет значения и затем переведет строку из-за `нс`.

**Это отменяет предыдущие неверные интерпретации `нс` как "отмены автоматического переноса".**

---

### 1. Общая Информация и Начальные Заметки (До Активного Рефакторинга Компонентов)

*   **Общая информация по проекту:**
    *   **Запуск тестов:**
        *   Все тесты: `python -m pytest -v tests/test_functional.py > test_Log.txt`
        *   Конкретный тест: `python -m pytest -v tests/test_functional.py -k "имя_файла.kum"  > test_Log.txt`
        *   Все файлы kum: `tests/polyakov_kum`
    *   **Документация по языку Кумир:** `kumir2-master/userdocs/`
    *   **Исходный код оригинального Кумира (C++):** `kumir2-master/src`
    *   **Наиболее важные исходники:** `kumir2-master/src/kumir2-libs`, `kumir2-master/src/plugins`

*   **Заметки по доработке интерпретатора КуМира (первоначальный список задач):**
    1.  **Обработка ошибок типов:** При присваивании, передаче аргументов, в операциях.
    2.  **Области видимости:** Глобальные, локальные, перекрытие имен, видимость в блоках.
    3.  **Массивы:** Объявление, доступ по индексу, контроль границ, многомерные массивы.
    4.  **Процедуры и функции:** Объявление, вызов, передача аргументов (значение/ссылка `арг рез`), возврат значений, рекурсия.
    5.  **Встроенные функции и процедуры:** Реализация (`цел`, `вещ`, `лог`, `текст`, `длина`, `копировать`, `ввод`, `вывод` и т.д.).
    6.  **Управляющие конструкции:** Циклы (`нц для`, `нц пока`, `кц`), условия (`если ... то ... иначе ... все`), выход из циклов (`выход`).
    7.  **Типы данных:** `цел`, `вещ`, `лог`, `сим`, `лит`. Преобразование типов.
    8.  **Комментарии:** Игнорирование (`|` до конца строки).
    9.  **Обработка конца файла и ошибок парсинга:** Корректное завершение, информативные сообщения.

*   **Заметки по разработке (исторический лог до начала рефакторинга компонентов):**
    *   Начало работы, базовая структура, парсер для основных конструкций.
    *   Поддержка объявления переменных, базовая логика присваивания.
    *   Арифметические выражения (`+`, `-`, `*`, `/`).
    *   Условные операторы, логические выражения.
    *   Циклы (`нц для`, `нц пока`), базовая логика итераций.
    *   Обсуждение реализации `ExpressionEvaluator`. План: выделить из основного интерпретатора. Начать с `visitLiteral` и `visitQualifiedIdentifier`.

---

### 2. Начало Рефакторинга Компонентов и Первичная Отладка

*   **Начало новой фазы: Рефакторинг `ExpressionEvaluator`:**
    *   **Контекст:** Продолжение рефакторинга `interpreter.py` с выделением `ExpressionEvaluator`.
    *   **План на тот момент:**
        1.  Завершить реализацию методов в `pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py`:
            *   `visitUnaryExpression`
            *   `visitPowerExpression`
            *   Операционная логика в `visitMultiplicativeExpression`
            *   Операционная логика в `visitAdditiveExpression`
        2.  Интегрировать и тщательно протестировать `ExpressionEvaluator`.

*   **Интеграция компонентов и отладка:**
    *   **Контекст:** Начальный этап рефакторинга `ExpressionEvaluator` и его интеграция с `KumirInterpreterVisitor` и другими компонентами (`ScopeManager`, `ProcedureManager`, `StatementHandler`, `DeclarationVisitorMixin`). Запуск функциональных тестов.
    *   **Обнаруженные и исправленные ошибки (хронология):**
        1.  `TabError: inconsistent use of tabs and spaces in indentation` в `pyrobot/backend/kumir_interpreter/kumir_exceptions.py`. (Исправлено)
        2.  `ImportError: cannot import name 'KumirRuntimeError'` из `kumir_exceptions` в `main_visitor.py`. (Добавлен класс `KumirRuntimeError(KumirExecutionError)` в `kumir_exceptions.py`, исправлено)
        3.  `SyntaxError: unterminated f-string literal` в `pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py`. (Исправлено)
        4.  `ImportError: cannot import name 'StatementVisitorMixin'` (и аналогичные). (Созданы заглушки, скорректирован `interpreter_components/__init__.py`, унифицированы импорты в `main_visitor.py`, исправлено)
        5.  Ошибки компиляции в `main_visitor.py` после унификации импортов:
            *   `Expected 0 positional arguments` для `IOHandler`. (Добавлен конструктор в `IOHandler`, исправлено)
            *   `Cannot access attribute "visitArrayLiteral"` для `ExpressionEvaluator`. (Добавлены заглушки `visit*` в `ExpressionEvaluator`, исправлено)
        6.  `SyntaxError: invalid syntax` (артефакт `</rewritten_file>`) в `pyrobot/backend/kumir_interpreter/interpreter_components/builtin_functions.py`. (Удалена ошибочная строка, исправлено)
        7.  `ImportError: cannot import name 'ScopeManager'` (циклический импорт между `main_visitor.py` и `interpreter_components/__init__.py`). (Убран импорт `KumirInterpreterVisitor` из `__init__.py`, импорты в `main_visitor.py` изменены на прямые, исправлено)
        8.  `AttributeError: 'KumirInterpreterVisitor' object has no attribute '_validate_and_convert_value_for_assignment'`. (Добавлена заглушка в `KumirInterpreterVisitor`, исправлено заглушкой)
        9.  `ImportError: cannot import name 'LoopBreakException'` из `kumir_exceptions`. (Добавлены `LoopBreakException` и `LoopContinueException` в `kumir_exceptions.py`, исправлено)
        10. `AttributeError: 'KumirInterpreterVisitor' object has no attribute '_get_type_info_from_specifier'` в `declaration_visitors.py`. (Заменен на `self._get_type_from_specifier_node(type_spec_ctx)`, исправлено)
        11. `AttributeError: 'KumirInterpreterVisitor' object has no attribute '_create_variable_in_scope'` в `declaration_visitors.py`. (Заменен на `self.visitor.scope_manager.declare_variable(...)`, исправлено)
        12. `ImportError: cannot import name 'StopExecutionException'` из `kumir_exceptions` (в `statement_handlers.py`).
            *   **Причина:** В `kumir_exceptions.py` был `StopExecutionSignal`, ожидался `StopExecutionException`.
            *   **Действия:** `StopExecutionSignal` переименован в `StopExecutionException` (наследник `KumirExecutionError`). Проверены импорты. Очищен кэш. Изменен `statement_handlers.py` для импорта `kumir_exceptions as ke` и отладочной печати.
            *   **Статус на тот момент:** В процессе отладки, ожидался запуск тестов пользователем.

    *   **Уточнение по `ExpressionEvaluator`:**
        *   Два файла:
            1.  `pyrobot/backend/kumir_interpreter/expression_evaluator.py` (старый, более полный, вероятно, не используется активно).
            2.  `pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py` (новый, активный, целевой).
        *   **Стратегия:** Перенос и адаптация логики из старого файла в новый.
        *   **Задача:** Постепенно наполнить `interpreter_components/expression_evaluator.py`.

    *   **Текущая задача на тот момент (основная):** Исправление `ImportError: cannot import name 'StopExecutionException'`.

---

### 3. Глубокая Отладка `statement_handlers.py` и `utils.py`

*   **Контекст:** Фокус на ошибки времени выполнения в `statement_handlers.py` и `utils.py`.
*   **Обнаруженные и исправленные ошибки:**
    1.  **`AttributeError: 'KumirTypeConverter' object has no attribute 'to_kumir_type'` и `AttributeError: 'KumirValue' object has no attribute 'name'` в `utils.py` (`to_python_number`)**:
        *   **Причина:** `KumirType` заменен на строковые представления (`type_str`), не все обращения обновлены.
        *   **Действия (в `utils.py`, `kumir_datatypes.py`):**
            *   В `KumirValue` поле `type` заменено на `type_str`.
            *   В `KumirTypeConverter.to_python_number` убрано обращение к `.name` у `kumir_value.type`.
            *   В `KumirValue.convert_string_to_type` параметр `kumir_type` заменен на `kumir_type_str`.
            *   В `KumirValue.are_types_compatible` параметры `type1`, `type2` заменены на `type1_str`, `type2_str`.
            *   В `KumirTypeConverter.to_python_bool` `kumir_value.type.name` заменено на `kumir_value.type_str` (предположительно, или `kumir_value.type` если `type` стало строкой).
            *   В `KumirTypeConverter.to_kumir_value` параметр `kumir_type` заменен на `kumir_type_str`.
            *   В `TypeDeterminer.determine_type` возвращаемые значения `KumirType.*` заменены на строки ("ЛОГ", "ЦЕЛ", "ВЕЩ", "ЛИТ").
        *   **Статус:** Исправлено в `utils.py`.

    2.  **`AttributeError: 'StatementHandler' object has no attribute 'visitExpression'` и другие отсутствующие методы `visit<RuleName>` в `StatementHandler`**:
        *   **Причина:** `StatementHandler` должен наследовать от `KumirParserVisitor` (ANTLR-сгенерированный), а не от `KumirVisitor`.
        *   **Действия:** Базовый класс `StatementHandler` изменен на `KumirParserVisitor`. Импорт изменен на `from .generated.KumirParserVisitor import KumirParserVisitor`.
        *   **Статус:** Исправлено в `statement_handlers.py`.

    3.  **Ошибки доступа к атрибутам контекста ANTLR в `statement_handlers.py` (например, `ctx.ID()`, `ctx.block()`, `ctx.KW_WHILE`, `ctx.KW_ELSE`)**:
        *   **Причина:** Изменение методов доступа к токенам/под-правилам после смены базового класса (например, `KW_WHILE()` стало `WHILE()`).
        *   **Действия (в `statement_handlers.py`):**
            *   `visitIfStatement`: `ctx.block(0)` -> `ctx.statementSequence(0)`, `ctx.KW_ELSE()` -> `ctx.ELSE()`.
            *   `visitLoopStatement`: Переписан для `ctx.loopSpecifier()` (`WHILE()`, `FOR()`, `TIMES()`) и `ctx.endLoopCondition()`. Добавлено управление областью видимости для переменной цикла `FOR`.
            *   `visitSwitchStatement`: Переписан для итерации по `ctx.caseBlock()`, получение выражения из `case_ctx.expression()`.
            *   `visitIoStatement`: `ctx.KW_INPUT()` -> `ctx.INPUT()`, `ctx.KW_OUTPUT()` -> `ctx.OUTPUT()`. `arg.expr()` -> `arg.expression(0)`. (Позже этот метод будет дорабатываться).
            *   `visitAssignmentStatement`: `ctx.IDENTIFIER()` (в `lvalue`) -> `ctx.qualifiedIdentifier().ID()`.
            *   `visitProcedureCallStatement`: `ctx.procedureIdentifier()` -> `ctx.qualifiedIdentifier()`.
            *   `visitExitStatement`: `ctx.KW_EXIT()` -> `ctx.EXIT()`.
            *   `visitPauseStatement`: `ctx.KW_PAUSE()` -> `ctx.PAUSE()`.
            *   Добавлены `visitStopStatement`, `visitAssertionStatement` на основе правил из `KumirParser.py`.
            *   Вызовы `self.visit(child_ctx)` заменены на `self.interpreter.visit(child_ctx)` для диспетчеризации через главный визитор.
        *   **Статус:** В основном исправлено, но требовалась проверка.

    4.  **Проблемы с сигналами `BreakSignal`, `ContinueSignal`, `ReturnSignal`, `ExitSignal`**:
        *   **Причина:** Не были определены.
        *   **Действия:** Добавлены классы `BreakSignal`, `ContinueSignal`, `ReturnSignal`, `ExitSignal` в `kumir_exceptions.py`.
        *   **Статус:** Исправлено.

    5.  **Ошибки в `statement_handlers.py`:**
        *   `AttributeError: Cannot access attribute "to_boolean" for class "KumirTypeConverter"`.
            *   **Причина:** В `utils.py` метод называется `to_python_bool`.
            *   **Действие:** Вызовы `type_converter.to_boolean(...)` заменены на `type_converter.to_python_bool(...)`. (Исправлено)
        *   `CompileError: No parameter named "is_fatal"` в `self.error_handler.runtime_error`.
            *   **Причина:** Метод `runtime_error` в `ErrorHandler` (`utils.py`) не принимает `is_fatal`.
            *   **Действие:** Параметр `is_fatal` удален из вызова в `visitStopStatement`. (Исправлено)

*   **План на тот момент:**
    1.  Продолжить реализацию и верификацию `statement_handlers.py` (циклы, `ВЫХОД`, `ВОЗВРАТ`, `СТОП`, `УТВ`, `ПАУЗА`). Разобраться с `visitBreakStatement`, `visitContinueStatement`. Убедиться в корректности `visitExitStatement`.
    2.  Решить проблемы в `expression_evaluator.py` (`visitQualifiedIdentifier`, `visitLiteral`).

---

### 4. Рефакторинг и Реализация `ExpressionEvaluator`

*   **План (ориентировочно до рефакторинга `kumir_datatypes.py`):**
    *   Рефакторинг `kumir_datatypes.py` и `utils.py`:
        *   Удалить дублирующее определение `KumirValue` из `utils.py`.
        *   Определить `KumirFunction` и `KumirTable` в `kumir_datatypes.py`.
        *   Обновить импорты в `expression_evaluator.py`.
    *   Исправление ошибок в `expression_evaluator.py`:
        *   Относительные импорты, доступ к токенам `KumirParser` (например, `KumirParser.MUL`), использование исключений вместо `is_error`, доступ к атрибутам контекста, проверки типов, удаление дублирующихся методов, реализация/импорт `get_kumir_type_name_from_py_value`.
    *   Проверка и тестирование `ExpressionEvaluator`.

*   **Рефакторинг `pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py` (основная работа):**
    *   **Цель:** Исправить доступ к атрибутам ANTLR, реализовать методы посещения, корректно обрабатывать таблицы и вызовы функций, интегрироваться с новыми компонентами.
    *   **Основные изменения:**
        *   Обновлены импорты.
        *   Скорректирован `_get_error_info` для извлечения информации об ошибках из узлов ANTLR.
        *   Методы `_perform_binary_operation` и `_perform_unary_operation` делегируют выполнение `self.visitor.operations_handler` (требует создания/интеграции). Улучшена обработка ошибок.
        *   Реализован `visitLiteral` (целые, вещественные, строковые, символьные, логические).
        *   Начата реализация `visitPrimaryExpression` (идентификаторы, `результат`, выражения в скобках). Доступ к переменным через `self.visitor.scope_manager.find_variable()`.
        *   Начата реализация `visitPostfixExpression` (доступ к элементам таблиц, вызовы функций/процедур).
            *   **Доступ к таблицам:** Проверка типа (`KumirTableVar`), вычисление индексов, проверка типов индексов и границ.
            *   **Вызовы функций/процедур:** Извлечение имени, вычисление аргументов. Маршрутизация через `self.visitor.procedure_manager.call_procedure` или `self.visitor.builtin_function_handler.call_builtin_function`.
        *   Скорректирован `visitUnaryExpression` (рекурсивная обработка, вызов `_perform_unary_operation`).
        *   Скорректированы `visitPowerExpression`, `visitMultiplicativeExpression`, `visitAdditiveExpression`, `visitRelationalExpression`, `visitEqualityExpression` (рекурсивный спуск, вызов `_perform_binary_operation`).
        *   Реализованы `visitLogicalAndExpression`, `visitLogicalOrExpression` (с сокращённым вычислением).
        *   Добавлен `visitExpression` (общая точка входа).
        *   Общий `visit(tree)` вызывает `tree.accept(self)`.
        *   Старые методы для lvalue (`_get_lvalue_structure_for_arg`, `_get_lvalue_for_assignment`, `_get_lvalue_for_read`) закомментированы.
    *   **Следующие шаги на тот момент:**
        1.  Создать/доработать `OperationsHandler`.
        2.  Завершить и протестировать `visitPostfixExpression`.
        3.  Проверить операторы и приоритеты.
        4.  Убедиться, что все пути возвращают `KumirValue` или исключение.
        5.  Разобраться с обработкой lvalue.

*   **Реализация вызова функций в `ExpressionEvaluator`:**
    *   **План для `_evaluate_postfix_expression` в `interpreter_components/expression_evaluator.py`:**
        1.  Извлечь имя функции из `primary_expr_ctx.qualifiedIdentifier().getText()`.
        2.  Получить список аргументов из `part_ctx.argumentList()`, вычислить их с помощью `self.evaluate()`.
        3.  Выполнить вызов через `self.visitor` (например, `self.visitor.call_user_function(...)`).
        4.  Обработать случай, когда `current_value` не является вызываемым.

*   **План исправлений `expression_evaluator.py` (возможно, обобщающий или следующий этап):**
    1.  Систематическое исправление ошибок: синтаксис Python, доступ к ANTLR, обработка `KumirValue`, возвращаемые типы, атрибуты `KumirValue`, дубликаты методов, `get_kumir_type_name_from_py_value`.
    2.  Запустить тест `2+2.kum` и итеративно исправлять.
    3.  Тщательно протестировать вызовы функций.
    4.  Усовершенствовать `visitPostfixExpression`.

---

### 5. Отладка `ProcedureManager` и `KumirDatatypes`

*   **Контекст:** Корректная обработка вызовов функций и возвращаемых значений.
*   **Выполненные действия:**
    1.  Исправлена ошибка синтаксиса f-строки в `procedure_manager.py` (блок `except Exception as e:` в `call_function`).
    2.  Повторно применены изменения в `call_function` в `procedure_manager.py`:
        *   Использование `KumirType.from_string(return_type_str)`.
        *   Проверка на `KumirType.UNKNOWN`.
        *   Использование `kumir_func_obj.type_converter.is_python_type_compatible_with_kumir_type()`.
        *   Улучшены сообщения об ошибках `KumirTypeError`.
    3.  Проверены и исправлены f-строки в `procedure_manager.py` (`get_function_definition`, `call_function`, `_collect_procedure_definitions`).
*   **Состояние файлов на тот момент:**
    *   `pyrobot/backend/kumir_interpreter/interpreter_components/procedure_manager.py` (Прочитан, Изменен)
    *   `pyrobot/backend/kumir_interpreter/kumir_datatypes.py` (Прочитан, Изменен ранее)
*   **Следующие шаги на тот момент:**
    1.  Тщательное тестирование вызовов функций с различными типами возвращаемых значений и сценариями ошибок.
    2.  Продолжить работу над `ExpressionEvaluator`, особенно над `visitPostfixExpression`.

---

### 6. Цикл Исправлений Статических Ошибок и Заглушек

*   **Проблема:** Статические ошибки анализатора кода в `statement_handlers.py` после исправлений импортов.
*   **Ошибки (перечень):**
    *   `ScopeManager`: Отсутствуют `declare_array`, `update_table_element`, `get_variable_info`. Методы `update_variable`, `declare_variable` не принимают `line_index`, `column_index`.
    *   `ProcedureManager`: Отсутствуют `set_return_value`, `call_procedure`.
    *   ANTLR контекст: `ExitStatementContext` не имеет `LOOP_EXIT`, `PROCEDURE_EXIT`. `AssertionStatementContext` не имеет `stringLiteral`.
*   **План:**
    1.  Проверить грамматику `KumirParser.g4` для `exitStatement`, `assertionStatement`.
    2.  Исправить доступ к атрибутам ANTLR в `statement_handlers.py`.
    3.  Реализовать заглушки для недостающих методов в `scope_manager.py`, `procedure_manager.py`.
    4.  Добавить `line_index`, `column_index` в `scope_manager.py`.
    5.  Запустить тест `1-empty.kum`.

*   **Реализация заглушек и подготовка к тесту:**
    *   **Контекст:** Доступ к `ctx.LOOP_EXIT()`, `ctx.PROCEDURE_EXIT()`, `ctx.stringLiteral()` должен работать.
    *   **План действий:**
        1.  **`ScopeManager` (`scope_manager.py`):** Добавить `declare_array(...)`, `update_table_element(...)`, `get_variable_info(...)`. Добавить `line_index`, `column_index` в `update_variable`, `declare_variable`.
        2.  **`ProcedureManager` (`procedure_manager.py`):** Добавить `set_return_value(...)`, `call_procedure(...)`.
        3.  Запустить тест `1-empty.kum > test_log.txt`.
        4.  Проанализировать `test_log.txt`.

*   **Этап 3 (исправление `scope_manager.py`, заглушки в `procedure_manager.py`):**
    *   **`scope_manager.py`:** Исправлена синтаксическая ошибка в `if` в `update_variable` (проверка размерностей таблиц).
    *   **`procedure_manager.py`:**
        *   Добавлена заглушка `set_return_value(self, value_to_assign: KumirValue)` (инициализирует `self._current_procedure_return_value`).
        *   Добавлена заглушка `call_procedure(self, proc_name: str, actual_args: List[Dict[str, Any]], line_index: int, column_index: int)` (вызывает `NotImplementedError`).
    *   **Следующий шаг:** Запустить тест `1-empty.kum`.

---

### 7. Итеративные Исправления `expression_evaluator.py` и `constants.py` (Пользователем Вручную)

*   **Этап 4:** Исправление `SyntaxError: expected 'except' or 'finally' block` в `expression_evaluator.py` (некорректные отступы строк ~369-370).
    *   **Следующий шаг:** Запустить тест `1-empty.kum`.
*   **Этап 5:** Исправление `SyntaxError: invalid syntax` в `expression_evaluator.py` на строке 423 (некорректный комментарий `# ═х 1 ш эх 2 шэфхъёр` после `else:`).
    *   **Следующий шаг:** Запустить тест `1-empty.kum`.
*   **Этап 6:** Исправление отступа у блока `else` (или связанного `if/elif`) в `expression_evaluator.py` (обработка строковых операций, строка ~423).
    *   **Следующий шаг:** Запустить тест `1-empty.kum`.
*   **Этап 7:** Исправление `ImportError` (DEFAULT_PRECISION).
    *   **`pyrobot/backend/kumir_interpreter/interpreter_components/constants.py`:** Добавлена `DEFAULT_PRECISION = 10`.
    *   **Следующий шаг:** Запустить тест `1-empty.kum`.

---

### 8. Доработка `statement_handlers.py` и `utils.py`

*   **План изменений:**
    1.  Исправить обработку ВВОД/ВЫВОД в `statement_handlers.py` (`visitIoStatement`) для корректного использования `ioArgumentList()`, `outputItem()`, `variableReference()`.
    2.  Проверить/исправить использование контекстных методов во всех `visit` методах в `statement_handlers.py`.
    3.  Добавить реализацию `to_python_bool`, `to_python_number` в `KumirTypeConverter` (`utils.py`).
    4.  Добавить импорт `Union` из `typing` в `utils.py`.
*   **Изменения выполнены:**
    *   **`utils.py`:**
        *   Добавлен `Union` в импорты `typing`.
        *   Реализованы `to_python_bool` и `to_python_number` в `KumirTypeConverter`.

---

### 9. Тестирование и Анализ Падений Тестов (Фокус на `interpret_kumir`)

*   **Тестирование `1-primes.kum` (после успеха `1-empty.kum`):**
    *   **План:** Запустить тест `1-primes.kum` с входными данными `'100\n'` и сравнить вывод.
    *   Проанализировать `test_log.txt`.

*   **Проблема: Тесты падают, `actual_output` из `run_kumir_program` – пустая строка.**
    *   **План исследования:**
        1.  Получить и проанализировать полный код `interpret_kumir` из `pyrobot/backend/kumir_interpreter/runtime_utils.py`.
        2.  Сравнить с версией из `old-interpreter.py` для выявления различий в захвате вывода (`try...finally`, `StringIO`).
        3.  Исследовать, как `IOHandler` и `KumirInterpreterVisitor` в новой архитектуре обрабатывают вывод.
        4.  Определить причину сбоев.
    *   **Состояние файлов для анализа:** `test_log.txt`, `tests/test_functional.py`, `tests/polyakov_kum/`, `runtime_utils.py`, `old-interpreter.py`.

*   **Анализ тестов PyRobot (детальный):**
    *   **Задача:** Понять, почему тесты не проходят, выявить основную причину.
    *   **Выполнено:**
        *   Запуск тестов `pytest -v tests/test_functional.py` -> `test_log.txt` (попытка 1).
        *   Анализ `test_log.txt` (попытка 1): 64 теста FAILED. `AssertionError`, `actual_output` пуст. Отладочные логи `stderr` подтверждают пустой вывод от `interpret_kumir`.
        *   Анализ старой `interpret_kumir` из `old-interpreter.py`.
        *   Восстановлена недостающая часть `interpret_kumir` и класс `DiagnosticErrorListener` в `runtime_utils.py` на основе старой версии.
        *   Исправлено дублирование `DiagnosticErrorListener` в `runtime_utils.py`.
        *   Запуск тестов -> `test_log.txt` (попытка 2, после исправления `runtime_utils.py`).
        *   Анализ `test_log.txt` (попытка 2): Все 64 теста по-прежнему FAILED. Проблема с пустым выводом осталась.
    *   **Вывод:** Проблема не в базовой структуре `interpret_kumir` в `runtime_utils.py` (которая была приведена в соответствие со старой), а глубже – в том, как новый интерпретатор (`KumirInterpreterVisitor` и его компоненты, особенно `IOHandler`) взаимодействует с системой вывода, или же он не выполняет команды вывода вообще.

---

## Сводный План Работ по Проекту PyRobot

1.  **Решение проблемы с пустым выводом в тестах:**
    *   Исследовать, как `IOHandler` и `KumirInterpreterVisitor` (и его компоненты) в новой архитектуре обрабатывают вывод команд типа `вывод`.
    *   Убедиться, что команды вывода корректно достигают `IOHandler` и что `IOHandler` правильно направляет вывод в `StringIO`, используемый в `interpret_kumir`.
    *   Проверить, выполняется ли вообще код, ответственный за вывод, в новом интерпретаторе.

2.  **Завершение и отладка `ExpressionEvaluator` (`pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py`):**
    *   **Перенос логики:** Продолжить перенос и адаптацию логики из старого `expression_evaluator.py` в новый компонент.
    *   **Реализация методов посещения:**
        *   Завершить `visitUnaryExpression`.
        *   Завершить `visitPowerExpression`.
        *   Заполнить операционную логику в `visitMultiplicativeExpression`.
        *   Заполнить операционную логику в `visitAdditiveExpression`.
        *   Завершить и тщательно протестировать `visitPostfixExpression`, особенно для сложных случаев (вызов функции, возвращающей таблицу, с последующим доступом по индексу; корректное извлечение имени функции и аргументов).
        *   Проверить и при необходимости исправить `visitQualifiedIdentifier` и `visitLiteral`.
    *   **Интеграция с `OperationsHandler`:** Создать или доработать `OperationsHandler` для выполнения бинарных и унарных операций с учётом типов Кумира. Делегировать ему выполнение операций из `_perform_binary_operation` и `_perform_unary_operation`.
    *   **Обработка lvalue:** Решить, где и как будет происходить определение и обновление значений переменных и элементов таблиц (например, в `StatementHandler` при обработке присваивания или ввода). Раскомментировать и адаптировать/заменить старые методы для работы с lvalue.
    *   **Корректность:**
        *   Проверить правильность обработки всех операторов и их приоритетов.
        *   Убедиться, что все пути кода возвращают `KumirValue` или вызывают исключение, обрабатываемое `ErrorHandler`.
        *   Исправить синтаксические ошибки Python, доступ к атрибутам контекста ANTLR, обработку `KumirValue`, возвращаемые типы, атрибуты `KumirValue`, дубликаты методов.
        *   Реализовать или правильно импортировать `get_kumir_type_name_from_py_value`.
    *   **Тестирование:**
        *   Интегрировать и тщательно протестировать `ExpressionEvaluator`.
        *   Запустить тест `2+2.kum` и итеративно вносить исправления.

3.  **Завершение и отладка `StatementHandler` (`pyrobot/backend/kumir_interpreter/statement_handlers.py`):**
    *   **Реализация и верификация методов `visit*`:**
        *   Тщательно протестировать все типы циклов (`ПОКА`, `ДЛЯ`, `N РАЗ`, `НЦ...КЦ ПОКА`, простой `НЦ...КЦ`).
        *   Тщательно протестировать `ВЫХОД`, `ВОЗВРАТ`, `СТОП`, `УТВ` (утверждение), `ПАУЗА`.
        *   Разобраться с закомментированными `visitBreakStatement` и `visitContinueStatement`. Определить, нужны ли отдельные правила или достаточно сигналов.
        *   Убедиться, что `visitExitStatement` корректно различает выход из программы, возврат из функции/процедуры и прерывание цикла (проверить использование `ctx.LOOP_EXIT()`, `ctx.PROCEDURE_EXIT()`).
        *   Проверить `visitAssertionStatement` и доступ к `ctx.stringLiteral()`.
    *   **Корректность ANTLR:**
        *   Проверить грамматику `KumirParser.g4` для всех используемых правил в `statement_handlers.py`.
        *   Исправить доступ к атрибутам контекста ANTLR на основе грамматики.
        *   Проверить и исправить использование контекстных методов во всех остальных `visit` методах.
    *   **Обработка ВВОД/ВЫВОД:** Исправить `visitIoStatement` для корректного использования контекстных методов ANTLR (например, `ioArgumentList()`, `outputItem()`, `variableReference()`).

4.  **Доработка и отладка `ProcedureManager` (`pyrobot/backend/kumir_interpreter/interpreter_components/procedure_manager.py`):**
    *   **Реализация заглушек:** Заполнить логикой заглушки методов `set_return_value` и `call_procedure`.
    *   **Тестирование:** Провести тщательное тестирование вызовов функций с различными типами возвращаемых значений и сценариями ошибок (неправильный тип возврата, возврат значения из процедуры, невозврат значения из функции и т.д.).

5.  **Доработка и отладка `ScopeManager` (`pyrobot/backend/kumir_interpreter/interpreter_components/scope_manager.py`):**
    *   **Реализация заглушек:** Заполнить логикой заглушки методов `declare_array`, `update_table_element`, `get_variable_info`.
    *   **Параметры методов:** Убедиться, что методы `update_variable`, `declare_variable` (и другие, где необходимо) принимают и используют `line_index`, `column_index` для более точной диагностики ошибок.

6.  **Рефакторинг и Утилиты:**
    *   **`kumir_datatypes.py` и `utils.py`:**
        *   Удалить дублирующее определение `KumirValue` из `utils.py` (если еще не сделано).
        *   Определить классы `KumirFunction` и `KumirTable` в `kumir_datatypes.py` (если еще не сделано).
        *   Обновить импорты в `expression_evaluator.py` и других компонентах для использования этих классов из `kumir_datatypes.py`.
    *   **`KumirTypeConverter` (в `utils.py`):** Убедиться, что методы `to_python_bool` и `to_python_number` полностью реализованы и корректно работают.

7.  **Общее тестирование и отладка:**
    *   После каждого значительного изменения запускать релевантные функциональные тесты (например, `1-empty.kum`, `1-primes.kum`, `2+2.kum`).
    *   Анализировать `test_log.txt` для выявления и устранения проблем.
    *   Проводить итеративную отладку, фокусируясь на одном компоненте или ошибке за раз.
    *   После устранения основных проблем с выводом и выполнением базовых операций, провести полный прогон всех тестов: `python -m pytest -v tests/test_functional.py`.

8.  **Документация:**
    *   Обновлять `AI_notes.md` с прогрессом, обнаруженными проблемами и их решениями.

---

### 23. ТЕКУЩАЯ ПРОБЛЕМА: visitLiteral не вызывается (28.05.2025)

**ОБНАРУЖЕННАЯ ПРОБЛЕМА:** Visitor pattern не маршрутизирует вызовы к `visitLiteral`, хотя контекст имеет правильный тип `LiteralContext`.

**ДЕТАЛЬНАЯ ДИАГНОСТИКА:**
- ✓ Цепочка visitor методов работает: `visitExpression` → `visitLogicalOrExpression` → ... → `visitPrimaryExpression` 
- ✓ `visitPrimaryExpression` правильно определяет, что это литерал: `ctx.literal()` возвращает объект типа `LiteralContext`
- ✓ Вызывается `self.visit(ctx.literal())` с правильным контекстом
- ✗ **ПРОБЛЕМА:** Метод `visitLiteral` не вызывается, хотя контекст типа `LiteralContext` передается в `visit()`

**ЛОГИ ОТЛАДКИ:**
```
!!! [DEBUG ExpressionEvaluator.visitPrimaryExpression] ctx.literal() type: <class 'pyrobot.backend.kumir_interpreter.generated.KumirParser.KumirParser.LiteralContext'> !!!
!!! [DEBUG ExpressionEvaluator.visit] CALLED! Tree: '2+' !!!
!!! [DEBUG ExpressionEvaluator.visit] Tree type: LiteralContext !!!
!!! [DEBUG ExpressionEvaluator.visit] RESULT: None !!!
```

**ГИПОТЕЗЫ:**
1. **Имя метода:** Возможно, правило в грамматике называется не `literal`, а по-другому
2. **Базовый класс:** Возможно, проблема с наследованием или переопределением метода
3. **Сгенерированный visitor:** Возможно, ANTLR сгенерировал visitor с другими именами методов

**СЛЕДУЮЩИЕ ШАГИ:** 
- Проверить сгенерированный KumirParserVisitor на предмет правильных имен методов
- Возможно, попробовать переименовать `visitLiteral` в другое имя
- Или добавить метод с правильным именем из сгенерированной грамматики

**КОД В РАБОТЕ:** ExpressionEvaluator.visitLiteral(), visitPrimaryExpression() с подробной отладкой

---

### Уточнение по Команде `вывод` и `нс` из `kum_reference.md` (2025-05-28)

**Источник:** Документ `kum_reference.md`, предоставленный пользователем 2025-05-28.

**Ключевые моменты по команде `вывод` и аргументу `нс`:**

1.  **Поведение команды `вывод`:**
    *   Команда `вывод` последовательно печатает значения всех переданных ей аргументов.
    *   Важно: По умолчанию команда `вывод` **НЕ добавляет** автоматически символ новой строки в конце своего выполнения.

2.  **Значение аргумента `нс`:**
    *   Когда `нс` используется в качестве одного из аргументов команды `вывод` (или `ввод`), оно интерпретируется как "переход на новую строку". Фактически, `нс` само по себе является инструкцией для вывода символа новой строки в текущую позицию.
    *   Следовательно, перевод строки в результатах работы команды `вывод` происходит **только в тех местах, где в списке аргументов указано `нс`**.

**Пример из `kum_reference.md` для `вывод`:**
```kumir
алг
нач
  цел а; а := 3
  вещ б; б := 1.3
  нц 5 раз
    вывод а, " ", б, "Привет!", нс
  кц
кон
```
**Результат:**
```
3 1.3Привет!
3 1.3Привет!
3 1.3Привет!
3 1.3Привет!
3 1.3Привет!
```
Каждая строка вывода завершается переводом строки именно благодаря `нс` в конце списка аргументов `вывод`.

**Пример `2-2+2.kum` с новым пониманием:**
Файл `tests/polyakov_kum/2-2+2.kum`:
```kumir
алг Оператор вывода
нач
  вывод '2+'        | Выведет "2+" без перевода строки
  вывод '2=?`, нс   | Выведет "2=?", затем выполнит перевод строки (из-за нс)
  вывод 'Ответ: 4'  | Выведет "Ответ: 4" без перевода строки (если это конец программы или дальше нет вывода с нс)
кон
```
Ожидаемый вывод `tests/polyakov_kum/2-2+2-out.txt`:
```
2+2=?
Ответ: 4
```
Это соответствует трассировке:
1. `вывод '2+'` -> печатает "2+". Буфер: `"2+"`
2. `вывод '2=?`, нс` -> печатает "2=?". Затем `нс` печатает `\\n`. Буфер: `"2+2=?\\n"`
3. `вывод 'Ответ: 4'` -> печатает "Ответ: 4". Буфер: `"2+2=?\\nОтвет: 4"`
Если после этого нет других выводов, то так и останется. Если это конец программы, то такой вывод и будет финальным.

**Вывод:** Это понимание отменяет предыдущие заметки, где предполагалось, что `нс` модифицирует поведение команды `вывод` по автоматическому добавлению новой строки. Теперь ясно: `вывод` не добавляет новую строку автоматически, а `нс` является явным указанием на ее добавление.

---

*   **Выдержки из документации КуМир (Команда `вывод`):**
    ```kumir
    алг тест_вывода
    нач
      вывод "Привет, мир!", нс, "Как дела?"
      вывод "Это новая строка."
      вывод "Число:", 5, " Текст ", "еще текст"
      вывод вещественное число(2.5)
    кц
    ```
    *   Вывод нескольких значений через запятую:
        *   Если первое значение – строка, то все последующие значения выводятся подряд, без пробелов.
        *   Если первое значение – не строка, то перед каждым последующим значением выводится пробел.
        *   ~~`нс` (нет символа) – специальное значение, которое отменяет автоматический перевод строки после вывода. Если `нс` не указан, то после вывода всех значений курсор переводится на новую строку.~~
            *   **[ЗАМЕНЕНО ИНФОРМАЦИЕЙ ОТ 2025-05-28]** Это описание `нс` было неверным. Согласно `kum_reference.md` (см. заметку "Новое Уточнение по `вывод` и `нс` (2025-05-28)"), `нс` само по себе является инструкцией "вывести символ новой строки". Команда `вывод` по умолчанию *не* добавляет автоматический перевод строки.
        *   Неявные переносы строк в длинных строковых литералах не поддерживаются стандартным КуМиром.
