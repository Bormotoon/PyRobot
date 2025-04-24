// KumirParser.g4
// ANTLR v4 Parser Grammar for the Kumir language.
// Final version after testing against provided examples.
parser grammar KumirParser;

options { tokenVocab=KumirLexer; } // Используем токены из KumirLexer.g4

// --- Entry Point ---
program
    : preamble? (moduleDefinition | algorithmDefinition)+ EOF
    ;

preamble
    : (importStatement | globalDeclaration | globalAssignment)*
    ;

globalDeclaration
    : typeSpecifier variableList SEMICOLON?
    ;

globalAssignment
    : qualifiedIdentifier ASSIGN (literal | unaryExpression) SEMICOLON?
    ;

// --- Module Definition ---
moduleDefinition
    : moduleHeader moduleBody ENDMODULE (qualifiedIdentifier)? SEMICOLON?
    | implicitModuleBody
    ;

moduleHeader
    : MODULE qualifiedIdentifier SEMICOLON?
    ;

moduleBody
    : (importStatement | globalDeclaration | algorithmDefinition)*
    ;

implicitModuleBody
    : (importStatement | globalDeclaration | algorithmDefinition)+
    ;

importStatement
    : IMPORT moduleName SEMICOLON?
    ;

moduleName
    : qualifiedIdentifier
    | STRING
    ;

// --- Algorithm Definition ---
algorithmDefinition
    : algorithmHeader (preCondition | postCondition | variableDeclaration)*
      ALG_BEGIN
      algorithmBody
      ALG_END (algorithmName)? SEMICOLON? // Allow optional name check at end
    ;

algorithmHeader
    : ALG_HEADER (typeSpecifier)? algorithmName (LPAREN parameterList? RPAREN)? SEMICOLON?
    ;

// *** CORRECTION 1 Applied ***
algorithmName: ID+ ; // Allows one or more IDs for the name

parameterList
    : parameterDeclaration (COMMA parameterDeclaration)*
    ;

parameterDeclaration
    : (IN_PARAM | OUT_PARAM | INOUT_PARAM)? typeSpecifier variableList
    ;

typeSpecifier
    // *** CORRECTION 2 Applied ***
    : basicType TABLE_SUFFIX?  // Covers 'цел', 'вещ', 'цел таб' etc. if TABLE_SUFFIX is separate token
    | actorType
    | arrayType                // Explicitly handle combined array type tokens
    ;

basicType
    : INTEGER_TYPE | REAL_TYPE | BOOLEAN_TYPE | CHAR_TYPE | STRING_TYPE
    ;

actorType
    : KOMPL_TYPE | COLOR_TYPE | SCANCODE_TYPE | FILE_TYPE
    ;

// *** CORRECTION 2 Applied ***
arrayType // Rule to handle combined array type tokens from lexer
    : INTEGER_ARRAY_TYPE | REAL_ARRAY_TYPE | BOOLEAN_ARRAY_TYPE | CHAR_ARRAY_TYPE | STRING_ARRAY_TYPE
    ;

variableList
    : variableDeclarationItem (COMMA variableDeclarationItem)*
    ;

variableDeclarationItem
    : ID (LBRACK arrayBounds (COMMA arrayBounds)* RBRACK)? (ASSIGN expression)? // Allow optional initialization
    ;

arrayBounds
    : expression COLON expression
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

// --- Statements ---
statement
    : variableDeclaration SEMICOLON?
    | assignmentStatement SEMICOLON?
    | ioStatement SEMICOLON?
    | ifStatement SEMICOLON?
    | switchStatement SEMICOLON?
    | loopStatement SEMICOLON?
    | exitStatement SEMICOLON?
    | pauseStatement SEMICOLON?
    | stopStatement SEMICOLON?  // Corrected from HALT based on docs
    | assertionStatement SEMICOLON?
    | procedureCallStatement SEMICOLON?
    | SEMICOLON
    ;

variableDeclaration
    : typeSpecifier variableList
    ;

assignmentStatement
    : (lvalue ASSIGN)? expression
    ;

lvalue
    : qualifiedIdentifier (LBRACK indexList RBRACK)? // Corrected: indexList instead of multiple expressions
    ;

ioStatement
    : INPUT ioArgumentList
    | OUTPUT ioArgumentList
    ;

ioArgumentList
    : ioArgument (COMMA ioArgument)*
    ;

ioArgument
    : expression (COLON expression (COLON expression)?)?
    | NEWLINE_CONST
    ;

ifStatement
    : IF expression THEN statementSequence (ELSE statementSequence)? FI
    ;

switchStatement
    // *** CORRECTION 3 Applied ***
    : SWITCH caseBlock+ (ELSE statementSequence)? FI // Removed mandatory expression after SWITCH
    ;

caseBlock
    : CASE expression COLON statementSequence
    ;

loopStatement
    : LOOP loopSpecifier? statementSequence (ENDLOOP | endLoopCondition)
    ;

endLoopCondition
    : ENDLOOP_COND expression // Handle кц_при / кц при
    ;

loopSpecifier
    : FOR ID FROM expression TO expression (STEP expression)?
    | WHILE expression
    | expression TIMES
    ;

exitStatement
    : EXIT
    ;

pauseStatement
    : PAUSE
    ;

stopStatement // Corrected from HALT
    : STOP
    ;

assertionStatement
    : ASSERTION expression // Assuming 'утв' maps to ASSERTION based on C++ code structure
    ;

procedureCallStatement
    : qualifiedIdentifier (LPAREN argumentList? RPAREN)?
    ;

// --- Expressions ---
expression
    : logicalOrExpression
    ;

logicalOrExpression
    : logicalAndExpression (OR logicalAndExpression)*
    ;

logicalAndExpression
    : equalityExpression (AND equalityExpression)*
    ;

equalityExpression
    : relationalExpression ((EQ | NE) relationalExpression)*
    ;

relationalExpression
    : additiveExpression ((LT | GT | LE | GE) additiveExpression)*
    ;

additiveExpression
    : multiplicativeExpression ((PLUS | MINUS) multiplicativeExpression)*
    ;

multiplicativeExpression
    : powerExpression ((MUL | DIV) powerExpression)*
    ;

powerExpression
    : unaryExpression (POWER powerExpression)?
    ;

unaryExpression
    : (PLUS | MINUS | NOT) unaryExpression
    | postfixExpression
    ;

postfixExpression
    : primaryExpression ( LBRACK indexList RBRACK // Array/string access
                        | LPAREN argumentList? RPAREN // Function call
                        )*
    ;

// Corrected indexList based on A[i], A[i,j], s[k], s[k:m] syntax
indexList
    : expression (COLON expression)? // Single index or slice for 1D/string
    | expression COMMA expression // 2D index
    | expression COMMA expression COMMA expression // 3D index (if needed)
    ;

argumentList
    : expression (COMMA expression)*
    ;

primaryExpression
    : literal
    | qualifiedIdentifier
    | RETURN_VALUE
    | LPAREN expression RPAREN
    ;

qualifiedIdentifier
    : ID
    ;

literal
    : INTEGER
    | REAL
    | STRING
    | CHAR_LITERAL
    | TRUE
    | FALSE
    | colorLiteral
    | NEWLINE_CONST
    ;

colorLiteral
    : PROZRACHNIY | BELIY | CHERNIY | SERIY | FIOLETOVIY | SINIY | GOLUBOY | ZELENIY | ZHELTIY | ORANZHEVIY | KRASNIY
    ;