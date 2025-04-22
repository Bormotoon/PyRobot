# Generated from pyrobot/backend/kumir_interpreter/grammar/Kumir.g4 by ANTLR 4.6
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .KumirParser import KumirParser
else:
    from KumirParser import KumirParser

# This class defines a complete generic visitor for a parse tree produced by KumirParser.

class KumirVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by KumirParser#start.
    def visitStart(self, ctx:KumirParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#usesClause.
    def visitUsesClause(self, ctx:KumirParser.UsesClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#useStatement.
    def visitUseStatement(self, ctx:KumirParser.UseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algorithm.
    def visitAlgorithm(self, ctx:KumirParser.AlgorithmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algHeader.
    def visitAlgHeader(self, ctx:KumirParser.AlgHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algType.
    def visitAlgType(self, ctx:KumirParser.AlgTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#parameters.
    def visitParameters(self, ctx:KumirParser.ParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#paramDeclList.
    def visitParamDeclList(self, ctx:KumirParser.ParamDeclListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#paramDecl.
    def visitParamDecl(self, ctx:KumirParser.ParamDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#paramMode.
    def visitParamMode(self, ctx:KumirParser.ParamModeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#danoClause.
    def visitDanoClause(self, ctx:KumirParser.DanoClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#nadoClause.
    def visitNadoClause(self, ctx:KumirParser.NadoClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#declarations.
    def visitDeclarations(self, ctx:KumirParser.DeclarationsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#declaration.
    def visitDeclaration(self, ctx:KumirParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#typeDecl.
    def visitTypeDecl(self, ctx:KumirParser.TypeDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#scalarDecl.
    def visitScalarDecl(self, ctx:KumirParser.ScalarDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#variableNameList.
    def visitVariableNameList(self, ctx:KumirParser.VariableNameListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#tableDecl.
    def visitTableDecl(self, ctx:KumirParser.TableDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#indexRangeList.
    def visitIndexRangeList(self, ctx:KumirParser.IndexRangeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#indexRange.
    def visitIndexRange(self, ctx:KumirParser.IndexRangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#typeKeyword.
    def visitTypeKeyword(self, ctx:KumirParser.TypeKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#block.
    def visitBlock(self, ctx:KumirParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#introBlock.
    def visitIntroBlock(self, ctx:KumirParser.IntroBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#statement.
    def visitStatement(self, ctx:KumirParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#assignment.
    def visitAssignment(self, ctx:KumirParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#ioStatement.
    def visitIoStatement(self, ctx:KumirParser.IoStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#outputItemList.
    def visitOutputItemList(self, ctx:KumirParser.OutputItemListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#outputItem.
    def visitOutputItem(self, ctx:KumirParser.OutputItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#ifStatement.
    def visitIfStatement(self, ctx:KumirParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#selectStatement.
    def visitSelectStatement(self, ctx:KumirParser.SelectStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#forLoop.
    def visitForLoop(self, ctx:KumirParser.ForLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#whileLoop.
    def visitWhileLoop(self, ctx:KumirParser.WhileLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#timesLoop.
    def visitTimesLoop(self, ctx:KumirParser.TimesLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#procedureCall.
    def visitProcedureCall(self, ctx:KumirParser.ProcedureCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#assertStatement.
    def visitAssertStatement(self, ctx:KumirParser.AssertStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#exitStatement.
    def visitExitStatement(self, ctx:KumirParser.ExitStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#stopStatement.
    def visitStopStatement(self, ctx:KumirParser.StopStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#pauseStatement.
    def visitPauseStatement(self, ctx:KumirParser.PauseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#variable.
    def visitVariable(self, ctx:KumirParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#expressionList.
    def visitExpressionList(self, ctx:KumirParser.ExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#expression.
    def visitExpression(self, ctx:KumirParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#logicalOrExpr.
    def visitLogicalOrExpr(self, ctx:KumirParser.LogicalOrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#logicalAndExpr.
    def visitLogicalAndExpr(self, ctx:KumirParser.LogicalAndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#comparisonExpr.
    def visitComparisonExpr(self, ctx:KumirParser.ComparisonExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#addSubExpr.
    def visitAddSubExpr(self, ctx:KumirParser.AddSubExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#mulDivModExpr.
    def visitMulDivModExpr(self, ctx:KumirParser.MulDivModExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#powerExpr.
    def visitPowerExpr(self, ctx:KumirParser.PowerExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#unaryExpr.
    def visitUnaryExpr(self, ctx:KumirParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#primaryExpr.
    def visitPrimaryExpr(self, ctx:KumirParser.PrimaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#functionCall.
    def visitFunctionCall(self, ctx:KumirParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#literal.
    def visitLiteral(self, ctx:KumirParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#compoundIdentifier.
    def visitCompoundIdentifier(self, ctx:KumirParser.CompoundIdentifierContext):
        return self.visitChildren(ctx)



del KumirParser