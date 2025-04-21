# Generated from Kumir.g4 by ANTLR 4.13.2
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


    # Enter a parse tree produced by KumirParser#algorithm.
    def enterAlgorithm(self, ctx:KumirParser.AlgorithmContext):
        pass

    # Exit a parse tree produced by KumirParser#algorithm.
    def exitAlgorithm(self, ctx:KumirParser.AlgorithmContext):
        pass


    # Enter a parse tree produced by KumirParser#algHeader.
    def enterAlgHeader(self, ctx:KumirParser.AlgHeaderContext):
        pass

    # Exit a parse tree produced by KumirParser#algHeader.
    def exitAlgHeader(self, ctx:KumirParser.AlgHeaderContext):
        pass


    # Enter a parse tree produced by KumirParser#algType.
    def enterAlgType(self, ctx:KumirParser.AlgTypeContext):
        pass

    # Exit a parse tree produced by KumirParser#algType.
    def exitAlgType(self, ctx:KumirParser.AlgTypeContext):
        pass


    # Enter a parse tree produced by KumirParser#parameters.
    def enterParameters(self, ctx:KumirParser.ParametersContext):
        pass

    # Exit a parse tree produced by KumirParser#parameters.
    def exitParameters(self, ctx:KumirParser.ParametersContext):
        pass


    # Enter a parse tree produced by KumirParser#paramDeclList.
    def enterParamDeclList(self, ctx:KumirParser.ParamDeclListContext):
        pass

    # Exit a parse tree produced by KumirParser#paramDeclList.
    def exitParamDeclList(self, ctx:KumirParser.ParamDeclListContext):
        pass


    # Enter a parse tree produced by KumirParser#paramDecl.
    def enterParamDecl(self, ctx:KumirParser.ParamDeclContext):
        pass

    # Exit a parse tree produced by KumirParser#paramDecl.
    def exitParamDecl(self, ctx:KumirParser.ParamDeclContext):
        pass


    # Enter a parse tree produced by KumirParser#paramMode.
    def enterParamMode(self, ctx:KumirParser.ParamModeContext):
        pass

    # Exit a parse tree produced by KumirParser#paramMode.
    def exitParamMode(self, ctx:KumirParser.ParamModeContext):
        pass


    # Enter a parse tree produced by KumirParser#danoClause.
    def enterDanoClause(self, ctx:KumirParser.DanoClauseContext):
        pass

    # Exit a parse tree produced by KumirParser#danoClause.
    def exitDanoClause(self, ctx:KumirParser.DanoClauseContext):
        pass


    # Enter a parse tree produced by KumirParser#nadoClause.
    def enterNadoClause(self, ctx:KumirParser.NadoClauseContext):
        pass

    # Exit a parse tree produced by KumirParser#nadoClause.
    def exitNadoClause(self, ctx:KumirParser.NadoClauseContext):
        pass


    # Enter a parse tree produced by KumirParser#declarations.
    def enterDeclarations(self, ctx:KumirParser.DeclarationsContext):
        pass

    # Exit a parse tree produced by KumirParser#declarations.
    def exitDeclarations(self, ctx:KumirParser.DeclarationsContext):
        pass


    # Enter a parse tree produced by KumirParser#declaration.
    def enterDeclaration(self, ctx:KumirParser.DeclarationContext):
        pass

    # Exit a parse tree produced by KumirParser#declaration.
    def exitDeclaration(self, ctx:KumirParser.DeclarationContext):
        pass


    # Enter a parse tree produced by KumirParser#typeDecl.
    def enterTypeDecl(self, ctx:KumirParser.TypeDeclContext):
        pass

    # Exit a parse tree produced by KumirParser#typeDecl.
    def exitTypeDecl(self, ctx:KumirParser.TypeDeclContext):
        pass


    # Enter a parse tree produced by KumirParser#scalarDecl.
    def enterScalarDecl(self, ctx:KumirParser.ScalarDeclContext):
        pass

    # Exit a parse tree produced by KumirParser#scalarDecl.
    def exitScalarDecl(self, ctx:KumirParser.ScalarDeclContext):
        pass


    # Enter a parse tree produced by KumirParser#variableNameList.
    def enterVariableNameList(self, ctx:KumirParser.VariableNameListContext):
        pass

    # Exit a parse tree produced by KumirParser#variableNameList.
    def exitVariableNameList(self, ctx:KumirParser.VariableNameListContext):
        pass


    # Enter a parse tree produced by KumirParser#tableDecl.
    def enterTableDecl(self, ctx:KumirParser.TableDeclContext):
        pass

    # Exit a parse tree produced by KumirParser#tableDecl.
    def exitTableDecl(self, ctx:KumirParser.TableDeclContext):
        pass


    # Enter a parse tree produced by KumirParser#indexRangeList.
    def enterIndexRangeList(self, ctx:KumirParser.IndexRangeListContext):
        pass

    # Exit a parse tree produced by KumirParser#indexRangeList.
    def exitIndexRangeList(self, ctx:KumirParser.IndexRangeListContext):
        pass


    # Enter a parse tree produced by KumirParser#indexRange.
    def enterIndexRange(self, ctx:KumirParser.IndexRangeContext):
        pass

    # Exit a parse tree produced by KumirParser#indexRange.
    def exitIndexRange(self, ctx:KumirParser.IndexRangeContext):
        pass


    # Enter a parse tree produced by KumirParser#typeKeyword.
    def enterTypeKeyword(self, ctx:KumirParser.TypeKeywordContext):
        pass

    # Exit a parse tree produced by KumirParser#typeKeyword.
    def exitTypeKeyword(self, ctx:KumirParser.TypeKeywordContext):
        pass


    # Enter a parse tree produced by KumirParser#block.
    def enterBlock(self, ctx:KumirParser.BlockContext):
        pass

    # Exit a parse tree produced by KumirParser#block.
    def exitBlock(self, ctx:KumirParser.BlockContext):
        pass


    # Enter a parse tree produced by KumirParser#statement.
    def enterStatement(self, ctx:KumirParser.StatementContext):
        pass

    # Exit a parse tree produced by KumirParser#statement.
    def exitStatement(self, ctx:KumirParser.StatementContext):
        pass


    # Enter a parse tree produced by KumirParser#assignment.
    def enterAssignment(self, ctx:KumirParser.AssignmentContext):
        pass

    # Exit a parse tree produced by KumirParser#assignment.
    def exitAssignment(self, ctx:KumirParser.AssignmentContext):
        pass


    # Enter a parse tree produced by KumirParser#ioStatement.
    def enterIoStatement(self, ctx:KumirParser.IoStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#ioStatement.
    def exitIoStatement(self, ctx:KumirParser.IoStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#outputItemList.
    def enterOutputItemList(self, ctx:KumirParser.OutputItemListContext):
        pass

    # Exit a parse tree produced by KumirParser#outputItemList.
    def exitOutputItemList(self, ctx:KumirParser.OutputItemListContext):
        pass


    # Enter a parse tree produced by KumirParser#outputItem.
    def enterOutputItem(self, ctx:KumirParser.OutputItemContext):
        pass

    # Exit a parse tree produced by KumirParser#outputItem.
    def exitOutputItem(self, ctx:KumirParser.OutputItemContext):
        pass


    # Enter a parse tree produced by KumirParser#ifStatement.
    def enterIfStatement(self, ctx:KumirParser.IfStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#ifStatement.
    def exitIfStatement(self, ctx:KumirParser.IfStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#selectStatement.
    def enterSelectStatement(self, ctx:KumirParser.SelectStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#selectStatement.
    def exitSelectStatement(self, ctx:KumirParser.SelectStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#forLoop.
    def enterForLoop(self, ctx:KumirParser.ForLoopContext):
        pass

    # Exit a parse tree produced by KumirParser#forLoop.
    def exitForLoop(self, ctx:KumirParser.ForLoopContext):
        pass


    # Enter a parse tree produced by KumirParser#whileLoop.
    def enterWhileLoop(self, ctx:KumirParser.WhileLoopContext):
        pass

    # Exit a parse tree produced by KumirParser#whileLoop.
    def exitWhileLoop(self, ctx:KumirParser.WhileLoopContext):
        pass


    # Enter a parse tree produced by KumirParser#timesLoop.
    def enterTimesLoop(self, ctx:KumirParser.TimesLoopContext):
        pass

    # Exit a parse tree produced by KumirParser#timesLoop.
    def exitTimesLoop(self, ctx:KumirParser.TimesLoopContext):
        pass


    # Enter a parse tree produced by KumirParser#procedureCall.
    def enterProcedureCall(self, ctx:KumirParser.ProcedureCallContext):
        pass

    # Exit a parse tree produced by KumirParser#procedureCall.
    def exitProcedureCall(self, ctx:KumirParser.ProcedureCallContext):
        pass


    # Enter a parse tree produced by KumirParser#assertStatement.
    def enterAssertStatement(self, ctx:KumirParser.AssertStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#assertStatement.
    def exitAssertStatement(self, ctx:KumirParser.AssertStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#exitStatement.
    def enterExitStatement(self, ctx:KumirParser.ExitStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#exitStatement.
    def exitExitStatement(self, ctx:KumirParser.ExitStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#stopStatement.
    def enterStopStatement(self, ctx:KumirParser.StopStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#stopStatement.
    def exitStopStatement(self, ctx:KumirParser.StopStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#pauseStatement.
    def enterPauseStatement(self, ctx:KumirParser.PauseStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#pauseStatement.
    def exitPauseStatement(self, ctx:KumirParser.PauseStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#variable.
    def enterVariable(self, ctx:KumirParser.VariableContext):
        pass

    # Exit a parse tree produced by KumirParser#variable.
    def exitVariable(self, ctx:KumirParser.VariableContext):
        pass


    # Enter a parse tree produced by KumirParser#expressionList.
    def enterExpressionList(self, ctx:KumirParser.ExpressionListContext):
        pass

    # Exit a parse tree produced by KumirParser#expressionList.
    def exitExpressionList(self, ctx:KumirParser.ExpressionListContext):
        pass


    # Enter a parse tree produced by KumirParser#expression.
    def enterExpression(self, ctx:KumirParser.ExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#expression.
    def exitExpression(self, ctx:KumirParser.ExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#logicalOrExpr.
    def enterLogicalOrExpr(self, ctx:KumirParser.LogicalOrExprContext):
        pass

    # Exit a parse tree produced by KumirParser#logicalOrExpr.
    def exitLogicalOrExpr(self, ctx:KumirParser.LogicalOrExprContext):
        pass


    # Enter a parse tree produced by KumirParser#logicalAndExpr.
    def enterLogicalAndExpr(self, ctx:KumirParser.LogicalAndExprContext):
        pass

    # Exit a parse tree produced by KumirParser#logicalAndExpr.
    def exitLogicalAndExpr(self, ctx:KumirParser.LogicalAndExprContext):
        pass


    # Enter a parse tree produced by KumirParser#comparisonExpr.
    def enterComparisonExpr(self, ctx:KumirParser.ComparisonExprContext):
        pass

    # Exit a parse tree produced by KumirParser#comparisonExpr.
    def exitComparisonExpr(self, ctx:KumirParser.ComparisonExprContext):
        pass


    # Enter a parse tree produced by KumirParser#addSubExpr.
    def enterAddSubExpr(self, ctx:KumirParser.AddSubExprContext):
        pass

    # Exit a parse tree produced by KumirParser#addSubExpr.
    def exitAddSubExpr(self, ctx:KumirParser.AddSubExprContext):
        pass


    # Enter a parse tree produced by KumirParser#mulDivModExpr.
    def enterMulDivModExpr(self, ctx:KumirParser.MulDivModExprContext):
        pass

    # Exit a parse tree produced by KumirParser#mulDivModExpr.
    def exitMulDivModExpr(self, ctx:KumirParser.MulDivModExprContext):
        pass


    # Enter a parse tree produced by KumirParser#powerExpr.
    def enterPowerExpr(self, ctx:KumirParser.PowerExprContext):
        pass

    # Exit a parse tree produced by KumirParser#powerExpr.
    def exitPowerExpr(self, ctx:KumirParser.PowerExprContext):
        pass


    # Enter a parse tree produced by KumirParser#unaryExpr.
    def enterUnaryExpr(self, ctx:KumirParser.UnaryExprContext):
        pass

    # Exit a parse tree produced by KumirParser#unaryExpr.
    def exitUnaryExpr(self, ctx:KumirParser.UnaryExprContext):
        pass


    # Enter a parse tree produced by KumirParser#primaryExpr.
    def enterPrimaryExpr(self, ctx:KumirParser.PrimaryExprContext):
        pass

    # Exit a parse tree produced by KumirParser#primaryExpr.
    def exitPrimaryExpr(self, ctx:KumirParser.PrimaryExprContext):
        pass


    # Enter a parse tree produced by KumirParser#functionCall.
    def enterFunctionCall(self, ctx:KumirParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by KumirParser#functionCall.
    def exitFunctionCall(self, ctx:KumirParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by KumirParser#literal.
    def enterLiteral(self, ctx:KumirParser.LiteralContext):
        pass

    # Exit a parse tree produced by KumirParser#literal.
    def exitLiteral(self, ctx:KumirParser.LiteralContext):
        pass


    # Enter a parse tree produced by KumirParser#compoundIdentifier.
    def enterCompoundIdentifier(self, ctx:KumirParser.CompoundIdentifierContext):
        pass

    # Exit a parse tree produced by KumirParser#compoundIdentifier.
    def exitCompoundIdentifier(self, ctx:KumirParser.CompoundIdentifierContext):
        pass



del KumirParser