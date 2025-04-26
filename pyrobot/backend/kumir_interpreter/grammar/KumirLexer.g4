// KumirLexer.g4
// Лексер ANTLR v4 для языка КуМир.
lexer grammar KumirLexer;

// --- Ключевые слова (основной язык) ---
MODULE              : ('модуль' | 'МОДУЛЬ');
ENDMODULE           : ('конец' WS 'модуля' | 'КОНЕЦ' WS 'МОДУЛЯ' | 'конецмодуля' | 'КОНЕЦМОДУЛЯ' | 'конец_модуля' | 'КОНЕЦ_МОДУЛЯ');
ALG_HEADER          : ('алг' | 'АЛГ');
ALG_BEGIN           : ('нач' | 'НАЧ');
ALG_END             : ('кон' | 'КОН');
PRE_CONDITION       : ('дано' | 'ДАНО');
POST_CONDITION      : ('надо' | 'НАДО');
ASSERTION           : ('утв' | 'УТВ');
LOOP                : ('нц' | 'НЦ');
ENDLOOP_COND        : ('кц' WS 'при') | 'кц_при' | ('КЦ' WS 'ПРИ') | 'КЦ_ПРИ';
ENDLOOP             : ('кц' | 'КЦ');
IF                  : ('если' | 'ЕСЛИ');
THEN                : ('то' | 'ТО');
ELSE                : ('иначе' | 'ИНАЧЕ');
FI                  : ('все' | 'ВСЕ');
SWITCH              : ('выбор' | 'ВЫБОР');
CASE                : ('при' | 'ПРИ');
INPUT               : ('ввод' | 'ВВОД');
OUTPUT              : ('вывод' | 'ВЫВОД');
ASSIGN              : ':=';
EXIT                : ('выход' | 'ВЫХОД');
PAUSE               : ('пауза' | 'ПАУЗА');
STOP                : ('стоп' | 'СТОП');
IMPORT              : ('использовать' | 'ИСПОЛЬЗОВАТЬ');
FOR                 : ('для' | 'ДЛЯ');
WHILE               : ('пока' | 'ПОКА');
TIMES               : ('раз' | 'РАЗ');
FROM                : ('от' | 'ОТ');
TO                  : ('до' | 'ДО');
STEP                : ('шаг' | 'ШАГ');
NEWLINE_CONST       : ('нс' | 'НС');
NOT                 : ('не' | 'НЕ');
AND                 : ('и' | 'И');
OR                  : ('или' | 'ИЛИ');
OUT_PARAM           : ('рез' | 'РЕЗ');
IN_PARAM            : ('арг' | 'АРГ');
INOUT_PARAM         : ('аргрез' | 'АРГРЕЗ' | 'арг' WS 'рез' | 'АРГ' WS 'РЕЗ' | 'арг_рез' | 'АРГ_РЕЗ');
RETURN_VALUE        : ('знач' | 'ЗНАЧ');

// --- Типы данных ---
INTEGER_TYPE        : ('цел' | 'ЦЕЛ');
REAL_TYPE           : ('вещ' | 'ВЕЩ');
BOOLEAN_TYPE        : ('лог' | 'ЛОГ');
CHAR_TYPE           : ('сим' | 'СИМ');
STRING_TYPE         : ('лит' | 'ЛИТ');
TABLE_SUFFIX        : 'таб' | 'ТАБ';
KOMPL_TYPE          : ('компл' | 'КОМПЛ');
COLOR_TYPE          : ('цвет' | 'ЦВЕТ');
SCANCODE_TYPE       : ('сканкод' | 'СКАНКОД');
FILE_TYPE           : ('файл' | 'ФАЙЛ');
INTEGER_ARRAY_TYPE  : ('цел' WS? 'таб' | 'ЦЕЛ' WS? 'ТАБ' | 'цел_таб' | 'ЦЕЛ_ТАБ');
REAL_ARRAY_TYPE     : ('вещ' WS? 'таб' | 'ВЕЩ' WS? 'ТАБ' | 'вещ_таб' | 'ВЕЩ_ТАБ');
CHAR_ARRAY_TYPE     : ('сим' WS? 'таб' | 'СИМ' WS? 'ТАБ' | 'сим_таб' | 'СИМ_ТАБ');
STRING_ARRAY_TYPE   : ('лит' WS? 'таб' | 'ЛИТ' WS? 'ТАБ' | 'лит_таб' | 'ЛИТ_ТАБ');
BOOLEAN_ARRAY_TYPE  : ('лог' WS? 'таб' | 'ЛОГ' WS? 'ТАБ' | 'лог_таб' | 'ЛОГ_ТАБ');

// --- Константы ---
TRUE                : ('да' | 'ДА');
FALSE               : ('нет' | 'НЕТ');
PROZRACHNIY         : ('прозрачный' | 'ПРОЗРАЧНЫЙ');
BELIY               : ('белый' | 'БЕЛЫЙ');
CHERNIY             : ('чёрный' | 'черный' | 'ЧЁРНЫЙ' | 'ЧЕРНЫЙ');
SERIY               : ('серый' | 'СЕРЫЙ');
FIOLETOVIY          : ('фиолетовый' | 'ФИОЛЕТОВЫЙ');
SINIY               : ('синий' | 'СИНИЙ');
GOLUBOY             : ('голубой' | 'ГОЛУБОЙ');
ZELENIY             : ('зелёный' | 'зеленый' | 'ЗЕЛЁНЫЙ' | 'ЗЕЛЕНЫЙ');
ZHELTIY             : ('жёлтый' | 'желтый' | 'ЖЁЛТЫЙ' | 'ЖЕЛТЫЙ');
ORANZHEVIY          : ('оранжевый' | 'ОРАНЖЕВЫЙ');
KRASNIY             : ('красный' | 'КРАСНЫЙ');

// --- Операторы ---
POWER               : '**';
GE                  : '>=' | '≥';
LE                  : '<=' | '≤';
NE                  : '<>' | '≠';
PLUS                : '+';
MINUS               : '-';
MUL                 : '*';
DIV                 : '/';
DIV_OP              : ('div' | 'DIV');
MOD_OP              : ('mod' | 'MOD');
EQ                  : '=';
LT                  : '<';
GT                  : '>';
LPAREN              : '(';
RPAREN              : ')';
LBRACK              : '[';
RBRACK              : ']';
LBRACE              : '{';
RBRACE              : '}';
COMMA               : ',';
COLON               : ':';
SEMICOLON           : ';';
ATAT                : '@@';
AT                  : '@';

// --- Литералы ---
CHAR_LITERAL        : '\'' ( EscapeSequence | ~['\\\r\n] ) '\'' ;
STRING              : '"' ( EscapeSequence | ~["\\\r\n] )*? '"'
                    | '\'' ( EscapeSequence | ~['\\\r\n] )*? '\''
                    ;
REAL                : (DIGIT+ '.' DIGIT* | '.' DIGIT+) ExpFragment?
                    | DIGIT+ ExpFragment
                    ;
INTEGER             : DecInteger | HexInteger ;

// --- Идентификатор ---
ID                  : LETTER (LETTER | DIGIT | '_' | '@')* ;

// --- Комментарии ---
LINE_COMMENT        : '|' ~[\r\n]* -> channel(HIDDEN);
DOC_COMMENT         : '#' ~[\r\n]* -> channel(HIDDEN);

// --- Пробельные символы ---
WS                  : [ \t\r\n]+ -> skip;

// --- Фрагменты ---
fragment DIGIT      : [0-9];
fragment HEX_DIGIT  : [0-9a-fA-F];
fragment LETTER     : [a-zA-Zа-яА-ЯёЁ];
fragment DecInteger : DIGIT+;
fragment HexInteger : '$' HEX_DIGIT+;
fragment ExpFragment: [eEеЕ] [+-]? DIGIT+;
fragment EscapeSequence
                    : '\\' [btnfr"'\\]
                    ;