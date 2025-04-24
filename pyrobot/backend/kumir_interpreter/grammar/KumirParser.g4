// KumirParser.g4
// Грамматика парсера ANTLR v4 для языка КуМир.
// Определяет синтаксическую структуру программы на основе токенов от лексера.
// Эта версия включает исправления для многословных имен и инициализации переменных,
// а также измененную структуру стартового правила.
parser grammar KumirParser;

// Указываем, что нужно использовать токены, определённые в KumirLexer.g4
options { tokenVocab=KumirLexer; }

/*
 * =============================================================================
 * Стартовое правило и структура программы
 * =============================================================================
 */

/**
 * program: Основное правило, точка входа в грамматику.
 * Описывает общую структуру КуМир-программы.
 * Программа может начинаться с необязательной 'преамбулы' (элементы programItem),
 * за которой следует одно или более 'модулей' или 'алгоритмов'.
 * Заканчивается маркером конца файла (EOF).
 * ИЗМЕНЕНО: Используется programItem* вместо preamble? для потенциального
 * улучшения обработки начала файла.
 */
program
    : programItem* (moduleDefinition | algorithmDefinition)+ EOF
    ;

/**
 * programItem: Элемент, который может встречаться перед основными определениями модулей/алгоритмов.
 * Заменяет старый `preamble`. Может быть импортом, глобальным объявлением или присваиванием.
 */
programItem
    : importStatement
    | globalDeclaration
    | globalAssignment
    ;


/**
 * globalDeclaration: Описание глобальной переменной (или нескольких).
 * Начинается с указания типа, затем список переменных (возможно с размерами для таблиц
 * и начальными значениями через '='), может заканчиваться точкой с запятой.
 */
globalDeclaration
    : typeSpecifier variableList SEMICOLON?
    ;

/**
 * globalAssignment: Присваивание значения уже объявленной глобальной переменной.
 * Используется оператор ASSIGN (:=).
 * Позволяет присваивать литералы, результаты выражений или массивные литералы.
 * Может заканчиваться точкой с запятой.
 */
globalAssignment
    : qualifiedIdentifier ASSIGN (literal | unaryExpression | arrayLiteral) SEMICOLON?
    ;

/*
 * =============================================================================
 * Определение Модуля
 * =============================================================================
 */

/**
 * moduleDefinition: Определение модуля.
 * Может быть явным (с ключевыми словами MODULE/ENDMODULE)
 * или неявным (просто последовательность импортов, глобальных объявлений, алгоритмов).
 */
moduleDefinition
    : moduleHeader moduleBody ENDMODULE (qualifiedIdentifier)? SEMICOLON? // Явный модуль
    | implicitModuleBody                                                  // Неявный модуль (файл без `модуль`)
    ;

/**
 * moduleHeader: Заголовок явного модуля.
 * Ключевое слово MODULE, затем имя модуля (qualifiedIdentifier),
 * может заканчиваться точкой с запятой.
 */
moduleHeader
    : MODULE qualifiedIdentifier SEMICOLON?
    ;

/**
 * moduleBody: Тело модуля.
 * Содержит импорты, глобальные объявления или определения алгоритмов.
 */
moduleBody
    : (importStatement | globalDeclaration | algorithmDefinition)*
    ;

/**
 * implicitModuleBody: Тело неявного модуля.
 * То же, что и `moduleBody`, но без явного заголовка и конца модуля.
 * Используется, когда файл не начинается с `модуль`.
 */
implicitModuleBody
    : (programItem | algorithmDefinition)+ // Используем programItem для включения глобальных деклараций/импортов
    ;

/**
 * importStatement: Команда импорта модуля.
 * Ключевое слово IMPORT, затем имя модуля, может заканчиваться точкой с запятой.
 */
importStatement
    : IMPORT moduleName SEMICOLON?
    ;

/**
 * moduleName: Имя импортируемого модуля.
 * Может быть идентификатором или строковым литералом (для имен файлов).
 */
moduleName
    : qualifiedIdentifier
    | STRING
    ;

/*
 * =============================================================================
 * Определение Алгоритма
 * =============================================================================
 */

/**
 * algorithmDefinition: Определение алгоритма.
 * Начинается с заголовка (`algorithmHeader`),
 * затем могут идти необязательные секции `дано` (`preCondition`), `надо` (`postCondition`)
 * и описания локальных переменных (`variableDeclaration`).
 * Далее следует тело алгоритма между `нач` (ALG_BEGIN) и `кон` (ALG_END).
 * После `кон` может опционально проверяться имя алгоритма.
 * Может заканчиваться точкой с запятой.
 */
algorithmDefinition
    : algorithmHeader (preCondition | postCondition | variableDeclaration)*
      ALG_BEGIN
      algorithmBody
      ALG_END (algorithmName)? SEMICOLON?
    ;

/**
 * algorithmHeader: Заголовок алгоритма.
 * Начинается с `алг` (ALG_HEADER),
 * затем опционально тип возвращаемого значения (для функций),
 * затем имя алгоритма (`algorithmName`),
 * затем опционально список параметров в скобках (`parameterList`),
 * может заканчиваться точкой с запятой.
 */
algorithmHeader
    : ALG_HEADER (typeSpecifier)? algorithmName (LPAREN parameterList? RPAREN)? SEMICOLON?
    ;

/**
 * algorithmName: Имя алгоритма.
 * Может состоять из одного или нескольких ID, ключевого слова AND ('и') или INTEGER,
 * разделенных пробелами (которые обрабатываются лексером).
 * Исправлено для поддержки многословных имен и имен с числами/словом 'и' из тестов.
 */
algorithmName: (ID | AND | INTEGER)+ ;

/**
 * parameterList: Список параметров алгоритма в скобках.
 * Состоит из одного или нескольких описаний параметров, разделённых запятыми.
 */
parameterList
    : parameterDeclaration (COMMA parameterDeclaration)*
    ;

/**
 * parameterDeclaration: Описание одного или группы параметров одного типа.
 * Может начинаться с указания вида параметра (`арг`, `рез`, `аргрез`),
 * затем тип (`typeSpecifier`), затем список переменных (`variableList`).
 */
parameterDeclaration
    : (IN_PARAM | OUT_PARAM | INOUT_PARAM)? typeSpecifier variableList
    ;

/*
 * =============================================================================
 * Типы данных
 * =============================================================================
 */

/**
 * typeSpecifier: Определяет тип данных переменной или параметра.
 * Сначала проверяются составные типы массивов (например, `целтаб`),
 * затем базовые типы (возможно с суффиксом `таб`, если лексер не распознал составной тип),
 * затем типы исполнителей.
 */
typeSpecifier
    : arrayType                // Сначала проверяем явные типы массивов (целтаб, вещтаб и т.д.)
    | basicType TABLE_SUFFIX?  // Затем базовые типы (цел, вещ...), возможно с 'таб'
    | actorType                // Затем типы исполнителей (файл, цвет...)
    ;

/**
 * basicType: Основные встроенные типы данных.
 */
basicType
    : INTEGER_TYPE | REAL_TYPE | BOOLEAN_TYPE | CHAR_TYPE | STRING_TYPE
    ;

/**
 * actorType: Типы данных, связанные с исполнителями.
 */
actorType
    : KOMPL_TYPE | COLOR_TYPE | SCANCODE_TYPE | FILE_TYPE
    ;

/**
 * arrayType: Правило для явных токенов типов массивов, созданных лексером.
 * Например, `цел таб` распознаётся лексером как INTEGER_ARRAY_TYPE.
 */
arrayType
    : INTEGER_ARRAY_TYPE | REAL_ARRAY_TYPE | BOOLEAN_ARRAY_TYPE | CHAR_ARRAY_TYPE | STRING_ARRAY_TYPE
    ;

/*
 * =============================================================================
 * Описание Переменных
 * =============================================================================
 */

/**
 * variableList: Список переменных в объявлении.
 * Состоит из одного или нескольких элементов `variableDeclarationItem`, разделённых запятыми.
 */
variableList
    : variableDeclarationItem (COMMA variableDeclarationItem)*
    ;

/**
 * variableDeclarationItem: Описание одной переменной в списке.
 * Содержит имя (ID), опционально границы массива в квадратных скобках,
 * и опционально начальное значение, присваиваемое через '=' (EQ).
 * Инициализация при объявлении использует '=', а не ':='.
 */
variableDeclarationItem
    : ID (LBRACK arrayBounds (COMMA arrayBounds)* RBRACK)? // Опциональные границы массива
      ( EQ expression )? // Опциональная инициализация через '='
    ;

/**
 * arrayBounds: Границы одного измерения массива.
 * Два выражения (начальный и конечный индекс), разделённые двоеточием.
 */
arrayBounds
    : expression COLON expression
    ;

/*
 * =============================================================================
 * Секции 'дано' и 'надо'
 * =============================================================================
 */

/**
 * preCondition: Секция 'дано'.
 * Задает предусловие для выполнения алгоритма.
 * Состоит из ключевого слова PRE_CONDITION и логического выражения.
 */
preCondition // дано
    : PRE_CONDITION expression SEMICOLON?
    ;

/**
 * postCondition: Секция 'надо'.
 * Задает постусловие (цель) выполнения алгоритма.
 * Состоит из ключевого слова POST_CONDITION и логического выражения.
 */
postCondition // надо
    : POST_CONDITION expression SEMICOLON?
    ;

/*
 * =============================================================================
 * Тело Алгоритма и Операторы
 * =============================================================================
 */

/**
 * algorithmBody: Тело алгоритма.
 * Состоит из последовательности операторов.
 */
algorithmBody
    : statementSequence
    ;

/**
 * statementSequence: Последовательность операторов.
 * Ноль или более операторов.
 */
statementSequence
    : statement*
    ;

/**
 * statement: Один оператор языка КуМир.
 * Может быть объявлением переменной, присваиванием, вводом/выводом,
 * условным оператором, циклом и т.д.
 * Пустой оператор (точка с запятой) также допустим.
 */
statement
    : variableDeclaration SEMICOLON?      // Описание локальной переменной
    | assignmentStatement SEMICOLON?      // Присваивание или вызов процедуры/функции
    | ioStatement SEMICOLON?              // Ввод или вывод
    | ifStatement SEMICOLON?              // Условный оператор 'если'
    | switchStatement SEMICOLON?          // Оператор выбора 'выбор'
    | loopStatement SEMICOLON?            // Цикл 'нц'
    | exitStatement SEMICOLON?            // Выход из цикла/алгоритма
    | pauseStatement SEMICOLON?           // Приостановка выполнения
    | stopStatement SEMICOLON?            // Остановка выполнения
    | assertionStatement SEMICOLON?       // Утверждение 'утв'
    | procedureCallStatement SEMICOLON?   // Явный вызов процедуры (альтернатива через assignmentStatement)
    | SEMICOLON                           // Пустой оператор
    ;

/**
 * variableDeclaration: Описание локальной переменной внутри `нач...кон`.
 * Использует те же правила, что и `globalDeclaration`.
 */
variableDeclaration
    : typeSpecifier variableList
    ;

/**
 * assignmentStatement: Оператор присваивания или выражение-оператор.
 * Либо присваивание `lvalue := expression`.
 * Либо просто `expression`, что позволяет использовать вызовы процедур
 * (которые парсятся как `postfixExpression` -> `primaryExpression` -> `qualifiedIdentifier()`)
 * в качестве самостоятельных операторов.
 */
assignmentStatement
    : lvalue ASSIGN expression // Присваивание через :=
    | expression               // Вызов процедуры или другое выражение как оператор
    ;

/**
 * lvalue: Левая часть присваивания (то, чему присваивают).
 * Идентификатор переменной, возможно с индексами массива.
 */
lvalue
    : qualifiedIdentifier (LBRACK indexList RBRACK)?
    ;

/**
 * ioStatement: Оператор ввода или вывода.
 */
ioStatement
    : INPUT ioArgumentList  // ввод ...
    | OUTPUT ioArgumentList // вывод ...
    ;

/**
 * ioArgumentList: Список аргументов для ввода/вывода.
 * Один или несколько `ioArgument`, разделённых запятыми.
 */
ioArgumentList
    : ioArgument (COMMA ioArgument)*
    ;

/**
 * ioArgument: Один аргумент ввода/вывода.
 * Может быть выражением (возможно с форматом вывода через ':')
 * или константой новой строки 'нс'.
 */
ioArgument
    : expression (COLON expression (COLON expression)?)? // Выражение [ : ширина [ : точность ] ]
    | NEWLINE_CONST // нс
    ;

/**
 * ifStatement: Условный оператор 'если'.
 * `если условие то серия1 [иначе серия2] все`
 */
ifStatement
    : IF expression THEN statementSequence (ELSE statementSequence)? FI
    ;

/**
 * switchStatement: Оператор выбора 'выбор'.
 * `выбор [при условие1: серия1]... [иначе серияN] все`
 * Выражение после `выбор` не требуется (как в C/Java), проверяются условия в `при`.
 */
switchStatement
    : SWITCH caseBlock+ (ELSE statementSequence)? FI
    ;

/**
 * caseBlock: Один блок 'при' в операторе 'выбор'.
 * `при условие : серия_команд`
 */
caseBlock
    : CASE expression COLON statementSequence
    ;

/**
 * loopStatement: Оператор цикла 'нц'.
 * Может иметь спецификатор (`для`, `пока`, `N раз`) или быть без него (нц...кц).
 * Заканчивается либо `кц`, либо `кц при условие`.
 */
loopStatement
    : LOOP loopSpecifier? statementSequence (ENDLOOP | endLoopCondition)
    ;

/**
 * endLoopCondition: Условие завершения цикла `кц при`.
 * Использует специальный токен ENDLOOP_COND для `кц при` или `кц_при`.
 */
endLoopCondition
    : ENDLOOP_COND expression
    ;

/**
 * loopSpecifier: Уточнение типа цикла 'нц'.
 * Либо `для` с параметром, границами и шагом.
 * Либо `пока` с условием.
 * Либо `N раз` с количеством повторений.
 */
loopSpecifier
    : FOR ID FROM expression TO expression (STEP expression)? // для i от ... до ... шаг ...
    | WHILE expression                                      // пока ...
    | expression TIMES                                      // N раз
    ;

/**
 * exitStatement: Команда 'выход'.
 */
exitStatement
    : EXIT
    ;

/**
 * pauseStatement: Команда 'пауза'.
 */
pauseStatement
    : PAUSE
    ;

/**
 * stopStatement: Команда 'стоп'.
 */
stopStatement
    : STOP
    ;

/**
 * assertionStatement: Команда 'утв'.
 */
assertionStatement
    : ASSERTION expression
    ;

/**
 * procedureCallStatement: Явное правило для вызова процедуры.
 * Хотя вызов процедуры может быть обработан через `assignmentStatement` -> `expression`,
 * это правило может быть полезно для ясности или специфической обработки.
 * `имя_процедуры (аргументы?)`
 */
procedureCallStatement // Может быть избыточным, если `expression` покрывает вызовы
    : qualifiedIdentifier (LPAREN argumentList? RPAREN)?
    ;


/*
 * =============================================================================
 * Выражения (Expressions)
 * =============================================================================
 * Правила ниже определяют структуру выражений и порядок операторов (приоритет).
 * Правила организованы от низшего приоритета (логическое ИЛИ)
 * к высшему (первичные выражения).
 */

/**
 * expression: Самый общий вид выражения, начинается с логического ИЛИ.
 */
expression
    : logicalOrExpression
    ;

/**
 * logicalOrExpression: Логическое ИЛИ ('или'). Низший приоритет.
 * `a или b или c`
 */
logicalOrExpression
    : logicalAndExpression (OR logicalAndExpression)*
    ;

/**
 * logicalAndExpression: Логическое И ('и'). Приоритет выше 'или'.
 * `a и b и c`
 */
logicalAndExpression
    : equalityExpression (AND equalityExpression)*
    ;

/**
 * equalityExpression: Операторы равенства ('=', '<>'). Приоритет выше 'и'.
 * `a = b`, `a <> b`
 */
equalityExpression
    : relationalExpression ((EQ | NE) relationalExpression)*
    ;

/**
 * relationalExpression: Операторы сравнения ('<', '>', '<=', '>='). Приоритет выше равенства.
 * `a < b`, `a >= c`
 */
relationalExpression
    : additiveExpression ((LT | GT | LE | GE) additiveExpression)*
    ;

/**
 * additiveExpression: Сложение и вычитание ('+', '-'). Приоритет выше сравнения.
 * `a + b - c`
 */
additiveExpression
    : multiplicativeExpression ((PLUS | MINUS) multiplicativeExpression)*
    ;

/**
 * multiplicativeExpression: Умножение и деление ('*', '/'). Приоритет выше сложения/вычитания.
 * `a * b / c`
 */
multiplicativeExpression
    : powerExpression ((MUL | DIV) powerExpression)*
    ;

/**
 * powerExpression: Возведение в степень ('**'). Приоритет выше умножения/деления.
 * Правая ассоциативность: `a ** b ** c` парсится как `a ** (b ** c)`.
 * `a ** b`
 */
powerExpression
    : unaryExpression (POWER powerExpression)?
    ;

/**
 * unaryExpression: Унарные операторы (минус, плюс, НЕ). Высокий приоритет.
 * `-a`, `+b`, `не c`
 */
unaryExpression
    : (PLUS | MINUS | NOT) unaryExpression // Унарный плюс/минус или НЕ
    | postfixExpression                    // Или постфиксное выражение
    ;

/**
 * postfixExpression: Постфиксные операции (доступ к элементу массива/строки, вызов функции).
 * Применяются к первичному выражению (`primaryExpression`).
 * `a[i]`, `s[k:m]`, `f(x)`, `arr[i, j]()`
 */
postfixExpression
    : primaryExpression ( LBRACK indexList RBRACK   // Доступ к массиву/строке: A[i], A[i,j], s[k:m]
                        | LPAREN argumentList? RPAREN // Вызов функции: f(x, y)
                        )*                          // Может быть несколько подряд: matrix[i][j], func(x)(y)
    ;

/**
 * indexList: Список индексов для доступа к массиву/строке.
 * Поддерживает:
 *  - Один индекс: `A[i]`
 *  - Срез строки/массива: `s[k:m]`
 *  - Два индекса (для 2D массива): `matrix[i, j]`
 *  - Можно добавить 3 индекса для 3D массивов при необходимости.
 */
indexList
    : expression (COLON expression)? // Один индекс A[i] или срез s[k:m]
    | expression COMMA expression    // Два индекса A[i, j]
    // | expression COMMA expression COMMA expression // Для 3D
    ;

/**
 * argumentList: Список аргументов при вызове функции/процедуры.
 * Ноль или более выражений, разделённых запятыми.
 */
argumentList
    : expression (COMMA expression)*
    ;

/**
 * primaryExpression: Первичное, самое базовое выражение.
 * Это может быть литерал, идентификатор, переменная `знач`,
 * выражение в скобках или массивный литерал.
 */
primaryExpression
    : literal             // Число, строка, символ, да/нет, цвет, нс
    | qualifiedIdentifier // Имя переменной, константы, функции без аргументов
    | RETURN_VALUE        // Ключевое слово 'знач' внутри функции
    | LPAREN expression RPAREN // Выражение в скобках для изменения приоритета
    | arrayLiteral        // Массивный литерал {элемент1, элемент2, ...}
    ;

/**
 * arrayLiteral: Массивный литерал.
 * Фигурные скобки, внутри опционально список выражений.
 * `{1, 2, 3}`, `{"a", "b"}`
 */
arrayLiteral
    : LBRACE expressionList? RBRACE
    ;

/**
 * expressionList: Список выражений внутри массивного литерала.
 * Одно или более выражений, разделённых запятыми.
 */
expressionList
    : expression (COMMA expression)*
    ;

/**
 * qualifiedIdentifier: Квалифицированный идентификатор.
 * В данной версии упрощено до одного ID. В будущем может поддерживать
 * доступ к членам модуля/объекта, например `Модуль.Переменная`.
 */
qualifiedIdentifier
    : ID // Пока просто ID
    ;

/*
 * =============================================================================
 * Литералы
 * =============================================================================
 */

/**
 * literal: Конкретное значение (константа).
 */
literal
    : INTEGER         // 123, $FF
    | REAL            // 1.5, -0.5, 1e-3
    | STRING          // "привет", 'мир'
    | CHAR_LITERAL    // 'a', '%'
    | TRUE            // да
    | FALSE           // нет
    | colorLiteral    // красный, синий и т.д.
    | NEWLINE_CONST   // нс
    ;

/**
 * colorLiteral: Литералы для обозначения цветов.
 */
colorLiteral
    : PROZRACHNIY | BELIY | CHERNIY | SERIY | FIOLETOVIY | SINIY | GOLUBOY | ZELENIY | ZHELTIY | ORANZHEVIY | KRASNIY
    ;

// Конец файла KumirParser.g4