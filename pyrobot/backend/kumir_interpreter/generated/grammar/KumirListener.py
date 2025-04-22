# Generated from grammar/Kumir.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .KumirParser import KumirParser
else:
    from KumirParser import KumirParser

# This class defines a complete listener for a parse tree produced by KumirParser.
class KumirListener(ParseTreeListener):

    # Enter a parse tree produced by KumirParser#start.
    def enterStart(self, ctx:KumirParser.StartContext):
        pass

    # Exit a parse tree produced by KumirParser#start.
    def exitStart(self, ctx:KumirParser.StartContext):
        pass


    # Enter a parse tree produced by KumirParser#program.
    def enterProgram(self, ctx:KumirParser.ProgramContext):
        pass

    # Exit a parse tree produced by KumirParser#program.
    def exitProgram(self, ctx:KumirParser.ProgramContext):
        pass


    # Enter a parse tree produced by KumirParser#declarations.
    def enterDeclarations(self, ctx:KumirParser.DeclarationsContext):
        pass

    # Exit a parse tree produced by KumirParser#declarations.
    def exitDeclarations(self, ctx:KumirParser.DeclarationsContext):
        pass



del KumirParser