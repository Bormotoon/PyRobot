# Generated from pyrobot/backend/kumir_interpreter/grammar/KumirParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .KumirParser import KumirParser
else:
    from KumirParser import KumirParser

# This class defines a complete generic visitor for a parse tree produced by KumirParser.

class KumirParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by KumirParser#qualifiedIdentifier.
    def visitQualifiedIdentifier(self, ctx:KumirParser.QualifiedIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#literal.
    def visitLiteral(self, ctx:KumirParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#colorLiteral.
    def visitColorLiteral(self, ctx:KumirParser.ColorLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#expressionList.
    def visitExpressionList(self, ctx:KumirParser.ExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#arrayLiteral.
    def visitArrayLiteral(self, ctx:KumirParser.ArrayLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:KumirParser.PrimaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#argumentList.
    def visitArgumentList(self, ctx:KumirParser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#indexList.
    def visitIndexList(self, ctx:KumirParser.IndexListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#postfixExpression.
    def visitPostfixExpression(self, ctx:KumirParser.PostfixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#unaryExpression.
    def visitUnaryExpression(self, ctx:KumirParser.UnaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#powerExpression.
    def visitPowerExpression(self, ctx:KumirParser.PowerExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:KumirParser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#additiveExpression.
    def visitAdditiveExpression(self, ctx:KumirParser.AdditiveExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#relationalExpression.
    def visitRelationalExpression(self, ctx:KumirParser.RelationalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#equalityExpression.
    def visitEqualityExpression(self, ctx:KumirParser.EqualityExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx:KumirParser.LogicalAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#logicalOrExpression.
    def visitLogicalOrExpression(self, ctx:KumirParser.LogicalOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#expression.
    def visitExpression(self, ctx:KumirParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#typeSpecifier.
    def visitTypeSpecifier(self, ctx:KumirParser.TypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#basicType.
    def visitBasicType(self, ctx:KumirParser.BasicTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#actorType.
    def visitActorType(self, ctx:KumirParser.ActorTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#arrayType.
    def visitArrayType(self, ctx:KumirParser.ArrayTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#arrayBounds.
    def visitArrayBounds(self, ctx:KumirParser.ArrayBoundsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#variableDeclarationItem.
    def visitVariableDeclarationItem(self, ctx:KumirParser.VariableDeclarationItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#variableList.
    def visitVariableList(self, ctx:KumirParser.VariableListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx:KumirParser.VariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#globalDeclaration.
    def visitGlobalDeclaration(self, ctx:KumirParser.GlobalDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#globalAssignment.
    def visitGlobalAssignment(self, ctx:KumirParser.GlobalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#parameterDeclaration.
    def visitParameterDeclaration(self, ctx:KumirParser.ParameterDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#parameterList.
    def visitParameterList(self, ctx:KumirParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algorithmNameTokens.
    def visitAlgorithmNameTokens(self, ctx:KumirParser.AlgorithmNameTokensContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algorithmName.
    def visitAlgorithmName(self, ctx:KumirParser.AlgorithmNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algorithmHeader.
    def visitAlgorithmHeader(self, ctx:KumirParser.AlgorithmHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#preCondition.
    def visitPreCondition(self, ctx:KumirParser.PreConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#postCondition.
    def visitPostCondition(self, ctx:KumirParser.PostConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algorithmBody.
    def visitAlgorithmBody(self, ctx:KumirParser.AlgorithmBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#statementSequence.
    def visitStatementSequence(self, ctx:KumirParser.StatementSequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#lvalue.
    def visitLvalue(self, ctx:KumirParser.LvalueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#assignmentStatement.
    def visitAssignmentStatement(self, ctx:KumirParser.AssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#ioArgument.
    def visitIoArgument(self, ctx:KumirParser.IoArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#ioArgumentList.
    def visitIoArgumentList(self, ctx:KumirParser.IoArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#ioStatement.
    def visitIoStatement(self, ctx:KumirParser.IoStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#ifStatement.
    def visitIfStatement(self, ctx:KumirParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#caseBlock.
    def visitCaseBlock(self, ctx:KumirParser.CaseBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#switchStatement.
    def visitSwitchStatement(self, ctx:KumirParser.SwitchStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#endLoopCondition.
    def visitEndLoopCondition(self, ctx:KumirParser.EndLoopConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#loopSpecifier.
    def visitLoopSpecifier(self, ctx:KumirParser.LoopSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#loopStatement.
    def visitLoopStatement(self, ctx:KumirParser.LoopStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#exitStatement.
    def visitExitStatement(self, ctx:KumirParser.ExitStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#pauseStatement.
    def visitPauseStatement(self, ctx:KumirParser.PauseStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#stopStatement.
    def visitStopStatement(self, ctx:KumirParser.StopStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#assertionStatement.
    def visitAssertionStatement(self, ctx:KumirParser.AssertionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#procedureCallStatement.
    def visitProcedureCallStatement(self, ctx:KumirParser.ProcedureCallStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#statement.
    def visitStatement(self, ctx:KumirParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#algorithmDefinition.
    def visitAlgorithmDefinition(self, ctx:KumirParser.AlgorithmDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#moduleName.
    def visitModuleName(self, ctx:KumirParser.ModuleNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#importStatement.
    def visitImportStatement(self, ctx:KumirParser.ImportStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#programItem.
    def visitProgramItem(self, ctx:KumirParser.ProgramItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#moduleHeader.
    def visitModuleHeader(self, ctx:KumirParser.ModuleHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#moduleBody.
    def visitModuleBody(self, ctx:KumirParser.ModuleBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#implicitModuleBody.
    def visitImplicitModuleBody(self, ctx:KumirParser.ImplicitModuleBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#moduleDefinition.
    def visitModuleDefinition(self, ctx:KumirParser.ModuleDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by KumirParser#program.
    def visitProgram(self, ctx:KumirParser.ProgramContext):
        return self.visitChildren(ctx)



del KumirParser