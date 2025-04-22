# Generated from grammar/Kumir.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,7,21,2,0,7,0,2,1,7,1,2,2,7,2,1,0,1,0,1,0,1,1,1,1,1,1,3,1,13,
        8,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,0,0,3,0,2,4,0,0,18,0,6,1,0,0,0,2,
        9,1,0,0,0,4,17,1,0,0,0,6,7,3,2,1,0,7,8,5,0,0,1,8,1,1,0,0,0,9,10,
        5,1,0,0,10,12,5,5,0,0,11,13,3,4,2,0,12,11,1,0,0,0,12,13,1,0,0,0,
        13,14,1,0,0,0,14,15,5,2,0,0,15,16,5,3,0,0,16,3,1,0,0,0,17,18,5,4,
        0,0,18,19,5,5,0,0,19,5,1,0,0,0,1,12
    ]

class KumirParser ( Parser ):

    grammarFileName = "Kumir.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\\u0430\\u043B\\u0433'", "'\\u043D\\u0430\\u0447'", 
                     "'\\u043A\\u043E\\u043D'", "'\\u043B\\u0438\\u0442'" ]

    symbolicNames = [ "<INVALID>", "K_ALG", "K_NACH", "K_KON", "K_STR", 
                      "IDENTIFIER", "WS", "COMMENT" ]

    RULE_start = 0
    RULE_program = 1
    RULE_declarations = 2

    ruleNames =  [ "start", "program", "declarations" ]

    EOF = Token.EOF
    K_ALG=1
    K_NACH=2
    K_KON=3
    K_STR=4
    IDENTIFIER=5
    WS=6
    COMMENT=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class StartContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def program(self):
            return self.getTypedRuleContext(KumirParser.ProgramContext,0)


        def EOF(self):
            return self.getToken(KumirParser.EOF, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_start

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStart" ):
                listener.enterStart(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStart" ):
                listener.exitStart(self)




    def start(self):

        localctx = KumirParser.StartContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_start)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 6
            self.program()
            self.state = 7
            self.match(KumirParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def K_ALG(self):
            return self.getToken(KumirParser.K_ALG, 0)

        def IDENTIFIER(self):
            return self.getToken(KumirParser.IDENTIFIER, 0)

        def K_NACH(self):
            return self.getToken(KumirParser.K_NACH, 0)

        def K_KON(self):
            return self.getToken(KumirParser.K_KON, 0)

        def declarations(self):
            return self.getTypedRuleContext(KumirParser.DeclarationsContext,0)


        def getRuleIndex(self):
            return KumirParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = KumirParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9
            self.match(KumirParser.K_ALG)
            self.state = 10
            self.match(KumirParser.IDENTIFIER)
            self.state = 12
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 11
                self.declarations()


            self.state = 14
            self.match(KumirParser.K_NACH)
            self.state = 15
            self.match(KumirParser.K_KON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeclarationsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def K_STR(self):
            return self.getToken(KumirParser.K_STR, 0)

        def IDENTIFIER(self):
            return self.getToken(KumirParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return KumirParser.RULE_declarations

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeclarations" ):
                listener.enterDeclarations(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeclarations" ):
                listener.exitDeclarations(self)




    def declarations(self):

        localctx = KumirParser.DeclarationsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_declarations)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 17
            self.match(KumirParser.K_STR)
            self.state = 18
            self.match(KumirParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





