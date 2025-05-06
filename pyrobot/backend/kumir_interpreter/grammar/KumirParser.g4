// KumirParser.g4
// Грамматика парсера ANTLR v4 для языка КуМир.
// Финальная версия, реализующая захват "всего" имени алгоритма
// после 'алг [тип]?' до '(' или начала следующего блока.
parser grammar KumirParser;

options { tokenVocab=KumirLexer; }

/*
 * =============================================================================
 * Вспомогательные правила: Литералы, Идентификаторы, Выражения
 * =============================================================================
 */
qualifiedIdentifier
    : ID
    ;
literal
    : INTEGER | REAL | STRING | CHAR_LITERAL | TRUE | FALSE | colorLiteral | NEWLINE_CONST
    ;
colorLiteral
    : PROZRACHNIY | BELIY | CHERNIY | SERIY | FIOLETOVIY | SINIY | GOLUBOY | ZELENIY | ZHELTIY | ORANZHEVIY | KRASNIY
    ;
expressionList
    : expression (COMMA expression)*
    ;
arrayLiteral
    : LBRACE expressionList? RBRACE
    ;
primaryExpression
    : literal | qualifiedIdentifier | RETURN_VALUE | LPAREN expression RPAREN | arrayLiteral
    ;
argumentList
    : expression (COMMA expression)*
    ;
indexList
    : expression (COLON expression)? | expression COMMA expression
    ;
postfixExpression
    : primaryExpression ( LBRACK indexList RBRACK | LPAREN argumentList? RPAREN )*
    ;
unaryExpression
    : (PLUS | MINUS | NOT) unaryExpression | postfixExpression
    ;
powerExpression
    : unaryExpression (POWER powerExpression)?
    ;
multiplicativeExpression
    : powerExpression ((MUL | DIV | DIV_OP | MOD_OP) powerExpression)*
    ;
additiveExpression
    : multiplicativeExpression ((PLUS | MINUS) multiplicativeExpression)*
    ;
relationalExpression
    : additiveExpression ((LT | GT | LE | GE) additiveExpression)*
    ;
equalityExpression
    : relationalExpression ((EQ | NE) relationalExpression)*
    ;
logicalAndExpression
    : equalityExpression (AND equalityExpression)*
    ;
logicalOrExpression
    : logicalAndExpression (OR logicalAndExpression)*
    ;
expression
    : logicalOrExpression
    ;

/*
 * =============================================================================
 * Типы данных и Описание Переменных
 * =============================================================================
 */
typeSpecifier
    : arrayType
    | basicType TABLE_SUFFIX?
    | actorType
    ;
basicType
    : INTEGER_TYPE | REAL_TYPE | BOOLEAN_TYPE | CHAR_TYPE | STRING_TYPE
    ;
actorType
    : KOMPL_TYPE | COLOR_TYPE | SCANCODE_TYPE | FILE_TYPE
    ;
arrayType
    : INTEGER_ARRAY_TYPE | REAL_ARRAY_TYPE | BOOLEAN_ARRAY_TYPE | CHAR_ARRAY_TYPE | STRING_ARRAY_TYPE
    ;
arrayBounds
    : expression COLON expression
    ;
variableDeclarationItem
    : ID (LBRACK arrayBounds (COMMA arrayBounds)* RBRACK)? ( EQ expression )?
    ;
variableList
    : variableDeclarationItem (COMMA variableDeclarationItem)*
    ;
variableDeclaration
    : typeSpecifier variableList
    ;
globalDeclaration
    : typeSpecifier variableList SEMICOLON?
    ;
globalAssignment
    : qualifiedIdentifier ASSIGN (literal | unaryExpression | arrayLiteral) SEMICOLON?
    ;

/*
 * =============================================================================
 * Параметры Алгоритма
 * =============================================================================
 */
parameterDeclaration
    : (IN_PARAM | OUT_PARAM | INOUT_PARAM)? typeSpecifier variableList
    ;
parameterList
    : parameterDeclaration (COMMA parameterDeclaration)*
    ;

/*
 * =============================================================================
 * Имена Алгоритмов (Исправленный предикат)
 * =============================================================================
 */
/**
 * algorithmNameTokens: Захватывает все токены, которые могут быть частью имени,
 * до тех пор, пока не встретится один из "стоп-токенов".
 * ИСПОЛЬЗУЕТ КОРРЕКТНЫЙ СИНТАКСИС ПРЕДИКАТА ДЛЯ PYTHON ('self._input', 'self.TOKEN_NAME').
 */
algorithmNameTokens
    : ( {self._input.LA(1) != self.LPAREN and \
         self._input.LA(1) != self.ALG_BEGIN and \
         self._input.LA(1) != self.PRE_CONDITION and \
         self._input.LA(1) != self.POST_CONDITION and \
         self._input.LA(1) != self.SEMICOLON and \
         self._input.LA(1) != self.EOF}? . // Захватываем ЛЮБОЙ токен, если он не стоп-токен
      )+ // Требуем хотя бы один токен для имени
    ;

/**
 * algorithmName: Используется только для проверки имени в конце блока 'кон'.
 */
algorithmName: ID+ ;


/*
 * =============================================================================
 * Структура Алгоритма (ЕДИНОЕ ПРАВИЛО algorithmHeader)
 * =============================================================================
 */
/**
 * algorithmHeader: Заголовок алгоритма.
 * Единое правило: алг [тип]? ИМЯ [(параметры)]? [;]?
 * Использует algorithmNameTokens для захвата имени.
 */
algorithmHeader
    : ALG_HEADER (typeSpecifier)? algorithmNameTokens (LPAREN parameterList? RPAREN)? SEMICOLON?
    ;

preCondition // дано
    : PRE_CONDITION expression SEMICOLON?
    ;
postCondition // надо
    : POST_CONDITION expression SEMICOLON?
    ;
algorithmBody
    : statementSequence
    ;
statementSequence
    : statement*
    ;

/**
 * lvalue: Левая часть присваивания (то, чему присваивают).
 */
lvalue
    : qualifiedIdentifier (LBRACK indexList RBRACK)? // Обычная переменная или элемент массива A[i]
    | RETURN_VALUE                                   // Специальная переменная 'знач'
    ;

assignmentStatement
    : lvalue ASSIGN expression // Присваивание через :=
    | expression               // Вызов процедуры или другое выражение как оператор
    ;
ioArgument
    : expression (COLON expression (COLON expression)?)?
    | NEWLINE_CONST
    ;
ioArgumentList
    : ioArgument (COMMA ioArgument)*
    ;
ioStatement
    : INPUT ioArgumentList
    | OUTPUT ioArgumentList
    ;
ifStatement
    : IF expression THEN statementSequence (ELSE statementSequence)? FI
    ;
caseBlock
    : CASE expression COLON statementSequence
    ;
switchStatement
    : SWITCH caseBlock+ (ELSE statementSequence)? FI
    ;
endLoopCondition
    : ENDLOOP_COND expression
    ;
loopSpecifier
    : FOR ID FROM expression TO expression (STEP expression)?
    | WHILE expression
    | expression TIMES
    ;
loopStatement
    : LOOP loopSpecifier? statementSequence (ENDLOOP | endLoopCondition)
    ;
exitStatement
    : EXIT
    ;
pauseStatement
    : PAUSE
    ;
stopStatement
    : STOP
    ;
assertionStatement
    : ASSERTION expression
    ;
procedureCallStatement
    : qualifiedIdentifier (LPAREN argumentList? RPAREN)?
    ;
statement
    : variableDeclaration SEMICOLON?
    | assignmentStatement SEMICOLON?
    | ioStatement SEMICOLON?
    | ifStatement SEMICOLON?
    | switchStatement SEMICOLON?
    | loopStatement SEMICOLON?
    | exitStatement SEMICOLON?
    | pauseStatement SEMICOLON?
    | stopStatement SEMICOLON?
    | assertionStatement SEMICOLON?
    | procedureCallStatement SEMICOLON?
    | SEMICOLON
    ;

/**
 * algorithmDefinition: Определение алгоритма целиком.
 */
algorithmDefinition
    : algorithmHeader (preCondition | postCondition | variableDeclaration)*
      ALG_BEGIN
      algorithmBody
      ALG_END (algorithmName)? SEMICOLON? // Используем algorithmName (ID+) для проверки
    ;

/*
 * =============================================================================
 * Структура Модуля
 * =============================================================================
 */
moduleName
    : qualifiedIdentifier
    | STRING
    ;
importStatement
    : IMPORT moduleName SEMICOLON?
    ;
programItem
    : importStatement
    | globalDeclaration
    | globalAssignment
    ;
moduleHeader
    : MODULE qualifiedIdentifier SEMICOLON?
    ;
moduleBody
    : (programItem | algorithmDefinition)*
    ;
implicitModuleBody
    : (programItem | algorithmDefinition)+
    ;
moduleDefinition
    : moduleHeader moduleBody ENDMODULE (qualifiedIdentifier)? SEMICOLON?
    | implicitModuleBody
    ;

/*
 * =============================================================================
 * Структура Программы (Стартовое правило)
 * =============================================================================
 */
/**
 * program: Основное правило, точка входа в грамматику.
 */
program
    : programItem* (moduleDefinition | algorithmDefinition)* EOF // Меняем + на *
    ;

// Конец файла KumirParser.g4