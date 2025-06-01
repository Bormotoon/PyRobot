# Детальный План Реализации Пользовательских Функций и Процедур в PyRobot

Этот документ описывает шаги по добавлению поддержки пользовательских функций и процедур в интерпретатор языка КуМир проекта PyRobot.

## Фаза 1: Расширение Грамматики и Парсинг Определений

1.  **Модификация `kumir_lang/KumirLexer.g4`:**
    *   **Действие:** Добавить новые токены, если необходимо.
    *   **Токены:**
        *   `ALG_KW: 'алг';` (если еще нет общего для начала программы)
        *   `PROC_KW: 'проц';` (если решим использовать отдельное слово для процедур, хотя КуМир обычно использует `алг` для всего)
        *   `FUNC_KW: 'функ';` (аналогично, если решим разделять)
        *   `ARG: 'арг';`
        *   `RES: 'рез';`
        *   `ARGRES: 'аргрез';`
        *   `VAL_KW: 'знач';`
        *   `TYPE_INT: 'цел';` (и другие типы, если они определяются как ключевые слова, а не идентификаторы)
        *   `TYPE_REAL: 'вещ';`
        *   `TYPE_BOOL: 'лог';`
        *   `TYPE_CHAR: 'сим';`
        *   `TYPE_STRING: 'лит';`
    *   **Примечание:** Убедиться, что `НАЧ` и `КОН` уже есть и корректно обрабатываются.

2.  **Модификация `kumir_lang/KumirParser.g4`:**
    *   **Действие:** Добавить и обновить правила для описания и вызова алгоритмов.
    *   **Новые/Обновленные Правила:**
        *   `program`: Должен позволять последовательность `algorithmDefinition` перед основным `mainAlgorithm` или как часть `preamble`.
            ```antlr
            program: preamble? (algorithmDefinition | useStatement)* mainAlgorithm EOF;
            preamble: (declaration | assignment | comment)*; // Пример
            mainAlgorithm: (ALG_KW ID?)? block; // Основной алгоритм может быть анонимным
            ```
        *   `algorithmDefinition`:
            ```antlr
            algorithmDefinition:
                ALG_KW (dataType)? ID LPAREN parameterList? RPAREN
                (localDeclarations)? // Описания локальных переменных
                block
                ;
            ```
        *   `parameterList`:
            ```antlr
            parameterList: parameterGroup (COMMA parameterGroup)*;
            parameterGroup:
                (ARG | RES | ARGRES) dataType ID (COMMA ID)*;
            ```
        *   `localDeclarations`: Похоже на `preamble` или часть `block`, где объявляются переменные, локальные для функции.
            ```antlr
            block: BEGIN statement* END; // BEGIN = нач, END = кон
            statement: ... | assignment | outputStatement | inputStatement | ifStatement | forLoop | whileLoop | procedureCallStatement | valueAssignment | ... ;
            ```
        *   `valueAssignment` (для `знач`):
            ```antlr
            valueAssignment: VAL_KW ASSIGNMENT expression SEMI?;
            ```
        *   `expression`: Должно включать `functionCall`.
            ```antlr
            expression:
                ...
                | ID LPAREN argumentList? RPAREN # functionCallExpression
                ...
                ;
            argumentList: expression (COMMA expression)*;
            ```
        *   `procedureCallStatement`: Для вызова процедур как отдельных команд.
            ```antlr
            procedureCallStatement: ID LPAREN argumentList? RPAREN SEMI?;
            ```
    *   **Примечание:** После изменения грамматики нужно будет перегенерировать парсер и лексер с помощью ANTLR.

3.  **Создание Структур для Хранения Алгоритмов (например, в `pyrobot/backend/kumir_interpreter/definitions.py` или внутри `ast_evaluator.py`):**
    *   **Действие:** Определить Python классы для представления функций/процедур.
    *   **Класс `AlgorithmDefinition`:**
        *   `name: str`
        *   `return_type: Optional[str]` (None для процедур)
        *   `parameters: List[Parameter]`
        *   `body_context: ParserRuleContext` (ссылка на `blockCtx` из ANTLR)
        *   `is_function: bool`
    *   **Класс `Parameter`:**
        *   `name: str`
        *   `param_type: str` (тип данных КуМира)
        *   `mode: str` (`'арг'`, `'рез'`, `'аргрез'`)
        *   `original_value_if_argres_or_res: Any` (для временного хранения)

4.  **Модификация `pyrobot/backend/kumir_interpreter/preprocessing.py` (или основного визитора):**
    *   **Действие:** Реализовать первый проход по дереву для сбора всех определений алгоритмов.
    *   **Логика:**
        *   Создать в классе интерпретатора/визитора словарь: `self.user_functions: Dict[str, AlgorithmDefinition] = {}`.
        *   Реализовать метод `visitAlgorithmDefinition(ctx: KumirParser.AlgorithmDefinitionContext)`:
            *   Извлечь имя, тип возврата (если есть), параметры (с их типами и режимами `арг`/`рез`/`аргрез`).
            *   Создать экземпляр `AlgorithmDefinition`.
            *   Сохранить в `self.user_functions`.
            *   Проверить на дублирование имен.
            *   Убедиться, что `знач` используется только в функциях (это можно сделать и позже, при анализе тела).

## Фаза 2: Реализация Вызова Алгоритмов и Управление Контекстом

1.  **Модификация `pyrobot/backend/kumir_interpreter/ast_evaluator.py` (или основного визитора):**
    *   **Действие:** Реализовать логику вызова функций и процедур.
    *   **Метод `visitFunctionCallExpression(ctx: KumirParser.FunctionCallExpressionContext)`:**
        *   Получить имя функции `func_name = ctx.ID().getText()`.
        *   Найти `AlgorithmDefinition` в `self.user_functions`. Если не найдено, проверить `self.builtins`. Если нет нигде – `KumirNameError`.
        *   Если это пользовательская функция:
            *   Проверить, что это действительно функция (`alg_def.is_function`).
            *   Подготовить аргументы: вычислить каждое выражение из `ctx.argumentList()`.
            *   Проверить соответствие количества и типов аргументов с `alg_def.parameters`.
            *   Создать новый фрейм стека вызовов или новую область видимости (см. ниже).
            *   Передать параметры (см. ниже).
            *   Выполнить тело функции `self.visit(alg_def.body_context)`.
            *   Получить возвращенное значение (через исключение или специальное поле).
            *   Уничтожить фрейм/область видимости.
            *   Вернуть результат.
    *   **Метод `visitProcedureCallStatement(ctx: KumirParser.ProcedureCallStatementContext)`:**
        *   Аналогично `visitFunctionCallExpression`, но для процедур.
        *   Проверить, что `alg_def.is_function` равно `False`.
        *   Не ожидает возвращаемого значения.

2.  **Модификация `pyrobot/backend/kumir_interpreter/declarations.py` и `ast_evaluator.py` для Областей Видимости:**
    *   **Действие:** Реализовать стековую модель областей видимости.
    *   **Предложение:**
        *   `self.variables` в `ast_evaluator.py` может стать списком словарей `List[Dict[str, Any]]`, где каждый словарь – это один уровень области видимости.
        *   При входе в функцию/процедуру: `self.variables.append({})`.
        *   При выходе: `self.variables.pop()`.
        *   Поиск переменной: итерировать по `self.variables` от конца к началу.
        *   Объявление локальной переменной: добавлять в `self.variables[-1]`.
    *   **Передача Параметров:**
        *   При вызове, перед `self.variables.append({})`:
            *   Для каждого параметра из `alg_def.parameters` и соответствующего аргумента:
                *   **`арг`**: Вычислить значение аргумента. Добавить в *новую* (еще не добавленную в стек) область видимости: `new_scope[param.name] = вычисленное_значение`.
                *   **`рез`**: Аргумент должен быть именем переменной. Запомнить это имя. В `new_scope[param.name]` присвоить значение по умолчанию для типа `param.param_type`.
                *   **`аргрез`**: Аргумент должен быть именем переменной. Найти значение этой переменной в текущей (вызывающей) области видимости. Добавить в `new_scope[param.name] = найденное_значение`. Запомнить имя исходной переменной.
        *   После этого `self.variables.append(new_scope)`.

3.  **Модификация `pyrobot/backend/kumir_interpreter/ast_evaluator.py` для `знач`:**
    *   **Действие:** Обработать команду `знач`.
    *   **Метод `visitValueAssignment(ctx: KumirParser.ValueAssignmentContext)`:**
        *   Убедиться, что мы находимся внутри выполнения функции (проверить текущий `AlgorithmDefinition`).
        *   Вычислить `ctx.expression()`.
        *   Проверить соответствие типа результата типу возврата функции.
        *   **Способ 1 (Исключение):**
            *   Сохранить результат в специальном поле текущего фрейма вызова или в самом интерпретаторе.
            *   Сгенерировать специальное исключение (например, `FunctionReturnValue(value)`), которое будет поймано в `visitFunctionCallExpression` для прекращения выполнения тела функции и возврата значения.
        *   **Способ 2 (Флаг):**
            *   Установить флаг `self.return_value_pending = True` и `self.current_return_value = ...`.
            *   В цикле выполнения команд (`execution.py`) проверять этот флаг и прерывать выполнение, если он установлен.

## Фаза 3: Завершение Выполнения Алгоритма и Обработка Параметров

1.  **Модификация `pyrobot/backend/kumir_interpreter/ast_evaluator.py` (в конце `visitFunctionCallExpression` / `visitProcedureCallStatement` или при обработке `кон`):**
    *   **Действие:** Обработать параметры `рез` и `аргрез` после выполнения тела алгоритма.
    *   **Логика:**
        *   Перед `self.variables.pop()`:
            *   Для каждого параметра `param` в `alg_def.parameters`:
                *   Если `param.mode == 'рез'` или `param.mode == 'аргрез'`:
                    *   Получить конечное значение `param.name` из текущей (локальной) области видимости (`self.variables[-1][param.name]`).
                    *   Присвоить это значение исходной переменной (имя которой мы запомнили при вызове) в *предыдущей* области видимости (`self.variables[-2]`).
    *   Если функция завершилась (дошла до `кон`) без `знач`, сгенерировать ошибку `KumirRuntimeError("Функция ... должна возвращать значение через знач")`.

## Фаза 4: Обработка Ошибок и Исключения

1.  **Модификация `pyrobot/backend/kumir_interpreter/exceptions.py`:**
    *   **Действие:** Добавить новые классы исключений.
    *   **Новые Исключения:**
        *   `AlgorithmRedefinitionError(KumirSyntaxError)`
        *   `ArgumentMismatchError(KumirTypeError)`
        *   `ReturnValueError(KumirTypeError)` (например, `знач` в процедуре, или не тот тип)
        *   `MissingReturnValueError(KumirRuntimeError)`
        *   `ParameterModificationError(KumirRuntimeError)` (попытка изменить `арг` параметр)

## Фаза 5: Тестирование

1.  **Создание Тестовых Файлов (`tests/polyakov_kum/` или новая директория):**
    *   Тесты на простое определение и вызов функций/процедур.
    *   Тесты на все типы параметров (`арг`, `рез`, `аргрез`) для разных типов данных.
    *   Тесты на рекурсию (факториал, числа Фибоначчи).
    *   Тесты на области видимости (локальные переменные, перекрытие глобальных).
    *   Тесты на корректную обработку ошибок (неверное число/тип аргументов, вызов неопределенной функции, `знач` в процедуре, отсутствие `знач` в функции).
    *   Использовать существующие примеры: `23-func-sumdig.kum`, `24-func-prime.kum`, `25-func-prime.kum`.
    *   Тесты на программы с несколькими алгоритмами.

## Дополнительные Замечания:

*   **Вступление (`preamble`):** Переменные, объявленные во вступлении, должны быть глобальными и доступными из всех алгоритмов.
*   **Основной алгоритм:** Может быть анонимным. Выполнение программы начинается с него после обработки всех определений алгоритмов.
*   **Порядок Определения:** В КуМире обычно не требуется предварительное объявление функции перед её использованием, если все определения разобраны до начала выполнения. Наш подход с первым проходом для сбора определений это обеспечит.
*   **Команда `ВЫХОД`:** Если `ВЫХОД` используется для выхода из функции/процедуры, это нужно будет учесть. Обычно `ВЫХОД` прерывает текущий цикл или тело алгоритма (если он не в цикле). Если он прерывает тело функции, то для функций это равносильно завершению без `знач` (ошибка), если только `знач` не было присвоено ранее.

Этот план должен дать нам хорошую основу. Я готова приступать к реализации, как только ты дашь отмашку!
