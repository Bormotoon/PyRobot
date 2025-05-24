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

---
## 2025-05-24 (Продолжение): Отладка `statement_handlers.py` и `utils.py`

**Контекст:** После серии исправлений, связанных с импортами и структурой компонентов, фокус сместился на ошибки времени выполнения, возникающие в `statement_handlers.py` и связанные с ним утилиты в `utils.py`.

**Обнаруженные и исправленные ошибки:**

1.  **`AttributeError: 'KumirTypeConverter' object has no attribute 'to_kumir_type'` и `AttributeError: 'KumirValue' object has no attribute 'name'` в `utils.py` (`to_python_number`)**
    *   **Причина:** `KumirType` был заменен на строковые представления (`type_str`), но не все обращения были обновлены.
    *   **Действия:**
        *   В `KumirValue` поле `type` заменено на `type_str`.
        *   В `KumirTypeConverter.to_python_number` убрано обращение к `.name` у `kumir_value.type`.
        *   В `KumirValue.convert_string_to_type` параметр `kumir_type` заменен на `kumir_type_str`.
        *   В `KumirValue.are_types_compatible` параметры `type1` и `type2` заменены на `type1_str` и `type2_str`.
        *   В `KumirTypeConverter.to_python_bool` `kumir_value.type.name` заменено на `kumir_value.type`.
        *   В `KumirTypeConverter.to_kumir_value` параметр `kumir_type` заменен на `kumir_type_str`.
        *   В `TypeDeterminer.determine_type` возвращаемые значения `KumirType.*` заменены на строки ("ЛОГ", "ЦЕЛ", "ВЕЩ", "ЛИТ").
    *   **Статус:** Исправлено в `utils.py`.

2.  **`AttributeError: 'StatementHandler' object has no attribute 'visitExpression'` и другие ошибки, связанные с отсутствием методов `visit<RuleName>` в `StatementHandler`**
    *   **Причина:** `StatementHandler` должен наследовать от `KumirParserVisitor` (сгенерированного ANTLR), а не от `KumirVisitor` (который, возможно, был старым или кастомным классом). `KumirParserVisitor` содержит необходимые методы `visit*`.
    *   **Действия:**
        *   Базовый класс `StatementHandler` изменен на `KumirParserVisitor`.
        *   Импорт изменен с `.generated.KumirVisitor` на `from .generated.KumirParserVisitor import KumirParserVisitor`.
    *   **Статус:** Исправлено в `statement_handlers.py`.

3.  **Ошибки доступа к атрибутам контекста ANTLR в `statement_handlers.py` (например, `ctx.ID()`, `ctx.block()`, `ctx.KW_WHILE`, `ctx.KW_ELSE`)**
    *   **Причина:** После смены базового класса на `KumirParserVisitor` и анализа `KumirParser.py`, стало ясно, что методы доступа к токенам и под-правилам изменились (например, `KW_WHILE()` стало `WHILE()`, `block()` стало `statementSequence()`).
    *   **Действия:**
        *   `visitIfStatement`: `ctx.block(0)` заменено на `ctx.statementSequence(0)`, `ctx.KW_ELSE()` на `ctx.ELSE()`.
        *   `visitLoopStatement`: Переписан для использования `ctx.loopSpecifier()` (с проверками `WHILE()`, `FOR()`, `TIMES()`) и `ctx.endLoopCondition()`. Добавлено управление областью видимости для переменной цикла `FOR`.
        *   `visitSwitchStatement`: Переписан для итерации по `ctx.caseBlock()` и получения выражения из `case_ctx.expression()`.
        *   `visitIoStatement`: `ctx.KW_INPUT()` на `ctx.INPUT()`, `ctx.KW_OUTPUT()` на `ctx.OUTPUT()`. `arg.expr()` на `arg.expression(0)`.
        *   `visitAssignmentStatement`: `ctx.IDENTIFIER()` (в `lvalue`) на `ctx.qualifiedIdentifier().ID()`.
        *   `visitProcedureCallStatement`: `ctx.procedureIdentifier()` на `ctx.qualifiedIdentifier()`.
        *   `visitExitStatement`: `ctx.KW_EXIT()` на `ctx.EXIT()`.
        *   `visitPauseStatement`: `ctx.KW_PAUSE()` на `ctx.PAUSE()`.
        *   Добавлены `visitStopStatement` и `visitAssertionStatement` на основе правил из `KumirParser.py`.
        *   Вызовы `self.visit(child_ctx)` заменены на `self.interpreter.visit(child_ctx)` для корректной диспетчеризации через главный визитор.
    *   **Статус:** В основном исправлено, но требует тщательной проверки всех методов.

4.  **Проблемы с сигналами `BreakSignal`, `ContinueSignal`, `ReturnSignal`, `ExitSignal`**
    *   **Причина:** Эти сигналы не были определены.
    *   **Действия:** Добавлены классы `BreakSignal`, `ContinueSignal`, `ReturnSignal`, `ExitSignal` в `kumir_exceptions.py`.
    *   **Статус:** Исправлено.

5.  **Ошибки в `statement_handlers.py` при последней попытке редактирования (24 мая 2025):**
    *   `AttributeError: Cannot access attribute "to_boolean" for class "KumirTypeConverter"`.
        *   **Причина:** В `utils.py` метод называется `to_python_bool`.
        *   **Действие:** В `statement_handlers.py` вызовы `type_converter.to_boolean(...)` заменены на `type_converter.to_python_bool(...)`.
        *   **Статус:** Исправлено.
    *   `CompileError: No parameter named "is_fatal"` в `self.error_handler.runtime_error`.
        *   **Причина:** Метод `runtime_error` в `ErrorHandler` (в `utils.py`) не принимает параметр `is_fatal`.
        *   **Действие:** Параметр `is_fatal` удален из вызова `self.error_handler.runtime_error(...)` в `visitStopStatement` в `statement_handlers.py`.
        *   **Статус:** Исправлено.

**Текущие задачи и план:**

1.  **Продолжить реализацию и верификацию `statement_handlers.py`**:
    *   Тщательно протестировать все типы циклов (`ПОКА`, `ДЛЯ`, `N РАЗ`, `НЦ...КЦ ПОКА`, простой `НЦ...КЦ`).
    *   Тщательно протестировать `ВЫХОД`, `ВОЗВРАТ`, `СТОП`, `УТВ` (утверждение), `ПАУЗА`.
    *   Разобраться с закомментированными `visitBreakStatement` и `visitContinueStatement`. Определить, есть ли в Кумире отдельные ключевые слова/правила парсера для них, или достаточно `BreakSignal` / `ContinueSignal`, возбуждаемых из логики циклов.
    *   Убедиться, что `visitExitStatement` корректно различает выход из программы, возврат из функции/процедуры и прерывание цикла.

2.  **Решить проблемы в `expression_evaluator.py`**:
    *   Проверить и исправить `visitQualifiedIdentifier` и `visitLiteral`.

3.  Обновить `AI_notes.md` с прогрессом.

**Состояние кода (ключевые файлы):**
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\pyrobot\backend\kumir_interpreter\utils.py` (Прочитан, Изменен)
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\pyrobot\backend\kumir_interpreter\statement_handlers.py` (Множественные попытки изменения, последняя успешна после исправлений `to_boolean` и `is_fatal`)
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\pyrobot\backend\kumir_interpreter\expression_evaluator.py` (Просмотрен, ожидаются изменения)
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\pyrobot\backend\kumir_interpreter\kumir_exceptions.py` (Прочитан, Изменен)
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\pyrobot\backend\kumir_interpreter\generated\KumirParser.py` (Прочитан для справки)
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\pyrobot\backend\kumir_interpreter\generated\KumirParserVisitor.py` (Существование подтверждено)
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\pyrobot\backend\kumir_interpreter\kumir_datatypes.py` (Прочитан)
*   `c:\Users\Bormotoon\VSCodeProjects\PyRobot\AI_notes.md` (Обновляется)

**Последние изменения (24 мая 2025, вечер):**
*   **В `statement_handlers.py`**:
    *   Исправлены вызовы `type_converter.to_boolean` на `type_converter.to_python_bool`.
    *   Удален параметр `is_fatal` из вызова `error_handler.runtime_error` в `visitStopStatement`.
*   **В `AI_notes.md`**:
    *   Обновление от 2025-05-24: Файл AI_notes.md успешно создан/обновлен в корне проекта.

---

## Рефакторинг ExpressionEvaluator (ExpressionEvaluator.py)

**Начало рефакторинга `expression_evaluator.py`:**

*   **Цель:** Исправить доступ к атрибутам ANTLR, реализовать методы посещения для всех типов выражений, корректно обрабатывать доступ к таблицам и вызовы функций, интегрироваться с новыми компонентами интерпретатора (`ScopeManager`, `ProcedureManager`, `ErrorHandler`, `TypeConverter`, `OperationsHandler`).
*   **Основные изменения (первая часть):**
    *   Обновлены импорты.
    *   Скорректирован метод `_get_error_info` для правильного извлечения информации об ошибках из различных типов узлов ANTLR (контексты, терминальные узлы, токены).
    *   Методы `_perform_binary_operation` и `_perform_unary_operation` теперь делегируют выполнение операций гипотетическому `self.visitor.operations_handler` (его нужно будет создать или интегрировать существующую логику). Они также улучшают обработку ошибок, используя `_get_error_info` и `ErrorHandler`.
    *   Реализован `visitLiteral` для обработки всех типов литералов Кумира (целые, вещественные, строковые, символьные, логические).
    *   Начата реализация `visitPrimaryExpression` для обработки идентификаторов (переменных), ключевого слова `результат` и выражений в скобках. Доступ к переменным теперь осуществляется через `self.visitor.scope_manager.find_variable()`.
    *   Начата реализация `visitPostfixExpression` для обработки доступа к элементам таблиц и вызовов функций/процедур.
        *   **Доступ к таблицам:** Проверяется тип базового значения (должен быть `KumirTableVar`), вычисляются индексы, выполняется проверка типов индексов и границ.
        *   **Вызовы функций/процедур:** Извлекается имя функции, вычисляются аргументы. Вызовы маршрутизируются через `self.visitor.procedure_manager.call_procedure` или `self.visitor.builtin_function_handler.call_builtin_function`.
    *   Скорректирован `visitUnaryExpression` для правильной рекурсивной обработки цепочек унарных операций и вызова `_perform_unary_operation`.
    *   Скорректированы `visitPowerExpression`, `visitMultiplicativeExpression`, `visitAdditiveExpression`, `visitRelationalExpression`, `visitEqualityExpression` для рекурсивного спуска по дереву выражения и вызова `_perform_binary_operation` с правильными операндами и оператором.
    *   Реализованы `visitLogicalAndExpression` и `visitLogicalOrExpression` с поддержкой сокращённого вычисления (short-circuiting).
    *   Добавлен `visitExpression` как общая точка входа для вычисления выражений.
    *   Общий метод `visit(tree)` теперь вызывает `tree.accept(self)`.
    *   Старые методы для работы с lvalue (`_get_lvalue_structure_for_arg`, `_get_lvalue_for_assignment`, `_get_lvalue_for_read`) пока закомментированы, так как их логика, вероятно, будет перенесена или упрощена.

**Следующие шаги для `ExpressionEvaluator`:**
1.  Разбить код на части и отправить для применения в файл.
2.  Создать или доработать `OperationsHandler` для выполнения бинарных и унарных операций с учётом типов Кумира.
3.  Завершить и тщательно протестировать `visitPostfixExpression`, особенно для сложных случаев (например, вызов функции, возвращающей таблицу, с последующим доступом по индексу).
4.  Проверить корректность обработки всех операторов и их приоритетов.
5.  Убедиться, что все пути кода возвращают `KumirValue` или вызывают исключение, обрабатываемое `ErrorHandler`.
6.  Разобраться с обработкой lvalue: решить, где и как будет происходить определение и обновление значений переменных и элементов таблиц (например, в `StatementHandler` при обработке присваивания или ввода).