# Generated from grammar/Kumir.g4 by ANTLR 4.13.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,7,54,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,3,1,3,1,
        3,1,3,1,4,1,4,5,4,34,8,4,10,4,12,4,37,9,4,1,5,4,5,40,8,5,11,5,12,
        5,41,1,5,1,5,1,6,1,6,5,6,48,8,6,10,6,12,6,51,9,6,1,6,1,6,0,0,7,1,
        1,3,2,5,3,7,4,9,5,11,6,13,7,1,0,4,6,0,65,90,95,95,97,122,1025,1025,
        1040,1103,1105,1105,7,0,48,57,65,90,95,95,97,122,1025,1025,1040,
        1103,1105,1105,3,0,9,10,13,13,32,32,2,0,10,10,13,13,56,0,1,1,0,0,
        0,0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,0,
        13,1,0,0,0,1,15,1,0,0,0,3,19,1,0,0,0,5,23,1,0,0,0,7,27,1,0,0,0,9,
        31,1,0,0,0,11,39,1,0,0,0,13,45,1,0,0,0,15,16,5,1072,0,0,16,17,5,
        1083,0,0,17,18,5,1075,0,0,18,2,1,0,0,0,19,20,5,1085,0,0,20,21,5,
        1072,0,0,21,22,5,1095,0,0,22,4,1,0,0,0,23,24,5,1082,0,0,24,25,5,
        1086,0,0,25,26,5,1085,0,0,26,6,1,0,0,0,27,28,5,1083,0,0,28,29,5,
        1080,0,0,29,30,5,1090,0,0,30,8,1,0,0,0,31,35,7,0,0,0,32,34,7,1,0,
        0,33,32,1,0,0,0,34,37,1,0,0,0,35,33,1,0,0,0,35,36,1,0,0,0,36,10,
        1,0,0,0,37,35,1,0,0,0,38,40,7,2,0,0,39,38,1,0,0,0,40,41,1,0,0,0,
        41,39,1,0,0,0,41,42,1,0,0,0,42,43,1,0,0,0,43,44,6,5,0,0,44,12,1,
        0,0,0,45,49,5,124,0,0,46,48,8,3,0,0,47,46,1,0,0,0,48,51,1,0,0,0,
        49,47,1,0,0,0,49,50,1,0,0,0,50,52,1,0,0,0,51,49,1,0,0,0,52,53,6,
        6,0,0,53,14,1,0,0,0,4,0,35,41,49,1,6,0,0
    ]

class KumirLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    K_ALG = 1
    K_NACH = 2
    K_KON = 3
    K_STR = 4
    IDENTIFIER = 5
    WS = 6
    COMMENT = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'\\u0430\\u043B\\u0433'", "'\\u043D\\u0430\\u0447'", "'\\u043A\\u043E\\u043D'", 
            "'\\u043B\\u0438\\u0442'" ]

    symbolicNames = [ "<INVALID>",
            "K_ALG", "K_NACH", "K_KON", "K_STR", "IDENTIFIER", "WS", "COMMENT" ]

    ruleNames = [ "K_ALG", "K_NACH", "K_KON", "K_STR", "IDENTIFIER", "WS", 
                  "COMMENT" ]

    grammarFileName = "Kumir.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


