# Заметки по доработке интерпретатора КуМира

Задачи, которые нужно реализовать для прохождения тестов:

1.  **Встроенные функции `irand` и `rand`:**
    *   Проблема: Интерпретатор не распознает `irand` и `rand` как встроенные функции, считает их необъявленными переменными.
    *   Файл теста: `tests/polyakov_kum/7-rand.kum`
    *   Место в коде: Вероятно, `visitPostfixExpression` или `visitPrimaryExpression` в `pyrobot/backend/kumir_interpreter/interpreter.py`.

2.  **Цикл `нц N раз`:**
    *   Проблема: Интерпретатор вызывает `NotImplementedError`, так как этот тип цикла еще не реализован.
    *   Файл теста: `tests/polyakov_kum/8-if.kum`
    *   Место в коде: Ветка `elif loop_spec.expression():` в методе `visitLoopStatement` в `pyrobot/backend/kumir_interpreter/interpreter.py`. 

3.  **Оператор `выбор` (switch):**
    *   Проблема: `KumirEvalError: ... Ошибка вычисления условия: 'NoneType' object has no attribute 'start'`. Интерпретатор не может получить значение для сравнения.
    *   Файлы тестов: `11-switch.kum`, `12-switch.kum`.
    *   Место в коде: `visitSwitchStatement` в `interpreter.py` (требует также исправления грамматики `KumirParser.g4`).

4.  **Обработка переменных цикла:**
    *   Проблема: `KumirEvalError: ... name 'X' is not defined` или похожие ошибки в циклах `нц N раз`, `пока`, `для`.
    *   Файлы тестов: `13-loopN.kum`, `14-while.kum`, `17-for.kum`.
    *   Место в коде: `visitLoopStatement` в `interpreter.py`.

5.  **Цикл `до` (repeat...until):**
    *   Проблема: `NotImplementedError: Цикл без условия (до) пока не реализован`.
    *   Файл теста: `16-repeat.kum`.
    *   Место в коде: `visitLoopStatement` в `interpreter.py`.

6.  **Проблема с чтением ввода (`\n`):**
    *   Проблема: `KumirEvalError: ... Ошибка преобразования типа ... invalid literal for int() with base 10: 'X\n'`. `input()` считывает символ переноса строки вместе со значением.
    *   Файл теста: `20-proc-err.kum` (и, возможно, другие).
    *   Место в коде: Строка `value_str = input()` и последующая конвертация в `visitIoStatement` в `interpreter.py`. Нужно убирать `\n` перед `int()`. 

7.  **Несоответствие вывода (AssertionError):**
    *   Проблема: Фактический вывод не совпадает с ожидаемым (часто из-за промптов или логики вывода).
    *   Файлы тестов: `10-and.kum`, `15-while.kum`, `18-downto.kum`, `19-prime.kum`.
    *   Решение: Нужно сравнить вывод с оригинальным КуМиром и скорректировать либо ожидаемый вывод в `TEST_CASES` (добавив промпты, если они есть в программе), либо логику вывода в интерпретаторе. 