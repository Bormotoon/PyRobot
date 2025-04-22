// pyrobot/backend/kumir_interpreter/grammar/Kumir.g4
// Полная грамматика Кумир (Этап 3: Выражения)
// Исправлена поддержка многословных идентификаторов
// Добавлена поддержка 'использовать' и вступления (опциональный блок перед алгоритмами)
// Исправлена обработка 'не' (как оператора и как части имени)

grammar Kumir;

// --- Parser Rules ---

// Стартовое правило: опционально 'использовать', опциональный блок (вступление), 0 или больше алгоритмов
// Семантически, блок вступления должен содержать только неветвящиеся команды (описания, присваивания и т.п.)
start: NL* usesClause? block? (NL* algorithm)* NL* EOF;

// Директивы 'использовать'
usesClause: (useStatement NL+)+ ;
useStatement: K_USE compoundIdentifier ;

// Алгоритм
algorithm: algHeader NL+ declarations K_NACH NL* block K_KON NL* ;

// Заголовок алгоритма
// Используем compoundIdentifier для имени алгоритма
algHeader: K_ALG (algType? compoundIdentifier)? (parameters)? (danoClause)? (nadoClause)? ;
algType: typeKeyword ;
parameters: LPAREN paramDeclList? RPAREN ;
paramDeclList: paramDecl (COMMA paramDecl)* ;
// Используем variableNameList (с compoundIdentifier) внутри paramDecl
paramDecl: paramMode? typeKeyword variableNameList ;
paramMode: K_ARG | K_REZ | K_ARGREZ ;
danoClause: NL+ K_DANO expression ;
nadoClause: NL+ K_NADO expression ;

// Объявления
declarations: declaration* ;
declaration: typeDecl NL+ ;
typeDecl: scalarDecl | tableDecl ;
// Используем variableNameList (с compoundIdentifier) внутри scalarDecl
scalarDecl: typeKeyword variableNameList ;
// Список имен переменных/таблиц для объявления
variableNameList: compoundIdentifier (COMMA compoundIdentifier)* ;
// Используем compoundIdentifier для имени таблицы
tableDecl: K_TAB typeKeyword compoundIdentifier LBRACK indexRangeList RBRACK ;
indexRangeList: indexRange (COMMA indexRange)* ;
indexRange: expression COLON expression ;
typeKeyword: K_CEL | K_VESH | K_LOG | K_SIM | K_LIT ;

// Блок команд
block: statement* ;

// Команда (пока базовая + заглушки)
statement: ( assignment
           | ioStatement
           | ifStatement
           | selectStatement
           | forLoop
           | whileLoop
           | timesLoop
           | procedureCall // Использует compoundIdentifier внутри
           | assertStatement
           | exitStatement
           | stopStatement
           | pauseStatement
           ) NL+ ;

// Присваивание: либо переменной, либо возврат значения функции через знач
// Используем compoundIdentifier в variable
assignment: (variable | K_ZNACH) ASSIGN expression ;

// Используем variableNameList (с compoundIdentifier) внутри ioStatement
ioStatement: K_VVOD variableNameList | K_VYVOD outputItemList ;
outputItemList: outputItem (COMMA outputItem)* ;
outputItem: expression | K_NS ;
ifStatement: K_ESLI expression K_TO NL+ block (K_INACHE NL+ block)? K_VSE ;
selectStatement: K_VYBOR (NL+ K_PRI expression COLON NL+ block)+ (NL+ K_INACHE NL+ block)? NL+ K_VSE ;
// Используем compoundIdentifier для переменной цикла
forLoop: K_NC K_DLYA compoundIdentifier K_OT expression K_DO expression (K_SHAG expression)? NL+ block K_KC ;
whileLoop: K_NC K_POKA expression NL+ block K_KC ;
timesLoop: K_NC expression K_RAZ NL+ block K_KC ;
// Используем compoundIdentifier для имени процедуры
procedureCall: compoundIdentifier (LPAREN expressionList? RPAREN)? ;
assertStatement: K_UTV expression ;
exitStatement: K_VYHOD ;
stopStatement: K_STOP ;
pauseStatement: K_PAUZA ;

// Переменная (включая таблицы)
// Используем compoundIdentifier для имени переменной
variable: compoundIdentifier (LBRACK expressionList RBRACK)? ;
expressionList: expression (COMMA expression)* ;

// Выражение (пока очень простое)
expression: logicalOrExpr ;

// --- Выражения с приоритетами ---

logicalOrExpr: logicalAndExpr (K_ILI logicalAndExpr)* ;

logicalAndExpr: comparisonExpr (K_I comparisonExpr)* ;

// Унарный НЕ имеет более высокий приоритет, см. unaryExpr
comparisonExpr: addSubExpr ((EQ | NEQ | LT | GT | LE | GE) addSubExpr)? ;

addSubExpr: mulDivModExpr ((PLUS | MINUS) mulDivModExpr)* ;

mulDivModExpr: powerExpr ((MUL | DIV | K_DIV | K_MOD) powerExpr)* ;

powerExpr: unaryExpr (POW unaryExpr)* ; // POW право-ассоциативен

// Обработка 'не' как унарного оператора через литерал
unaryExpr: (PLUS | MINUS | 'не')? primaryExpr ;

primaryExpr
    : literal
    | variable       // Использует compoundIdentifier внутри
    | functionCall   // Использует compoundIdentifier внутри
    | LPAREN expression RPAREN
    ;

// Используем compoundIdentifier для имени функции
functionCall: compoundIdentifier LPAREN expressionList? RPAREN ;

literal: NUMBER | STRING | CHAR | K_DA | K_NET ;

// Новое правило для многословного идентификатора
// Это последовательность из одного или более IDENTIFIER подряд.
// Пробелы между ними пропускаются лексером (WS -> skip).
compoundIdentifier: IDENTIFIER+ ;


// --- Lexer Rules ---

// Keywords (Все ключевые слова из документации)
K_ALG: 'алг';
K_NACH: 'нач';
K_KON: 'кон';
K_ISP: 'исп'; // Для 'использовать' - см. K_USE
K_KON_ISP: 'кон_исп';
K_USE: 'использовать'; // Добавлено
K_DANO: 'дано';
K_NADO: 'надо';
K_ARG: 'арг';
K_REZ: 'рез';
K_ARGREZ: 'аргрез';
K_ZNACH: 'знач';
K_CEL: 'цел';
K_VESH: 'вещ';
K_LOG: 'лог';
K_SIM: 'сим';
K_LIT: 'лит';
K_TAB: 'таб';
K_I: 'и';
K_ILI: 'или';
K_DA: 'да';
K_NET: 'нет';
K_UTV: 'утв';
K_VYHOD: 'выход';
K_VVOD: 'ввод';
K_VYVOD: 'вывод';
K_NS: 'нс';
K_ESLI: 'если';
K_TO: 'то';
K_INACHE: 'иначе';
K_VSE: 'все';
K_VYBOR: 'выбор';
K_PRI: 'при';
K_NC: 'нц';
K_KC: 'кц';
K_KC_PRI: 'кц_при';
K_RAZ: 'раз';
K_POKA: 'пока';
K_DLYA: 'для';
K_OT: 'от';
K_DO: 'до';
K_SHAG: 'шаг';
K_STOP: 'стоп';
K_PAUZA: 'пауза';
K_DIV: 'div'; // Добавлено
K_MOD: 'mod'; // Добавлено

// Operators and Delimiters
ASSIGN: ':=' ;
COMMA: ',' ;
LPAREN: '(' ;
RPAREN: ')' ;
LBRACK: '[' ;
RBRACK: ']' ;
COLON: ':' ;
PLUS : '+' ;
MINUS : '-' ;
MUL : '*' ;
DIV : '/' ;
POW : '**' ;
EQ : '=' ;
NEQ : '<>' ;
LT : '<' ;
GT : '>' ;
LE : '<=' ;
GE : '>=' ;

// Identifier (одно слово) - НЕ включает пробелы
IDENTIFIER: [a-zA-Zа-яА-ЯёЁ_] [a-zA-Zа-яА-ЯёЁ0-9_@]*; // Добавил @

// Literals
NUMBER: '-'? DIGIT+ ('.' DIGIT+)? (([eE]) [+-]? DIGIT+)?
      | '$'[0-9a-fA-F]+ ;
CHAR: '\'' ( ESCAPE_SEQ | ~['\\] )* '\'' ;
STRING: '"' ( ESCAPE_SEQ | ~["\\] )*? '"' ;

// Whitespace and Newlines
WS: [ \t]+ -> skip; // Вернули пропуск пробелов и табов
NL: [\r\n]+ ;       // Переносы строк - отдельные токены

// Comment
COMMENT: '|' ~[\r\n]* -> skip; // Комментарий '|' до конца строки

// Fragments
fragment DIGIT: [0-9];
fragment ESCAPE_SEQ : '\\' . ; // Фрагмент для escape-последовательностей
 