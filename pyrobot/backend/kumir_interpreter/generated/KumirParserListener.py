# Generated from c:/Users/Bormotoon/VSCodeProjects/PyRobot/kumir_lang/KumirParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .KumirParser import KumirParser
else:
    from KumirParser import KumirParser

# This class defines a complete listener for a parse tree produced by KumirParser.
class KumirParserListener(ParseTreeListener):

    # Enter a parse tree produced by KumirParser#qualifiedIdentifier.
    def enterQualifiedIdentifier(self, ctx:KumirParser.QualifiedIdentifierContext):
        pass

    # Exit a parse tree produced by KumirParser#qualifiedIdentifier.
    def exitQualifiedIdentifier(self, ctx:KumirParser.QualifiedIdentifierContext):
        pass


    # Enter a parse tree produced by KumirParser#literal.
    def enterLiteral(self, ctx:KumirParser.LiteralContext):
        pass

    # Exit a parse tree produced by KumirParser#literal.
    def exitLiteral(self, ctx:KumirParser.LiteralContext):
        pass


    # Enter a parse tree produced by KumirParser#colorLiteral.
    def enterColorLiteral(self, ctx:KumirParser.ColorLiteralContext):
        pass

    # Exit a parse tree produced by KumirParser#colorLiteral.
    def exitColorLiteral(self, ctx:KumirParser.ColorLiteralContext):
        pass


    # Enter a parse tree produced by KumirParser#expressionList.
    def enterExpressionList(self, ctx:KumirParser.ExpressionListContext):
        pass

    # Exit a parse tree produced by KumirParser#expressionList.
    def exitExpressionList(self, ctx:KumirParser.ExpressionListContext):
        pass


    # Enter a parse tree produced by KumirParser#arrayLiteral.
    def enterArrayLiteral(self, ctx:KumirParser.ArrayLiteralContext):
        pass

    # Exit a parse tree produced by KumirParser#arrayLiteral.
    def exitArrayLiteral(self, ctx:KumirParser.ArrayLiteralContext):
        pass


    # Enter a parse tree produced by KumirParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:KumirParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:KumirParser.PrimaryExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#argumentList.
    def enterArgumentList(self, ctx:KumirParser.ArgumentListContext):
        pass

    # Exit a parse tree produced by KumirParser#argumentList.
    def exitArgumentList(self, ctx:KumirParser.ArgumentListContext):
        pass


    # Enter a parse tree produced by KumirParser#indexList.
    def enterIndexList(self, ctx:KumirParser.IndexListContext):
        pass

    # Exit a parse tree produced by KumirParser#indexList.
    def exitIndexList(self, ctx:KumirParser.IndexListContext):
        pass


    # Enter a parse tree produced by KumirParser#postfixExpression.
    def enterPostfixExpression(self, ctx:KumirParser.PostfixExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#postfixExpression.
    def exitPostfixExpression(self, ctx:KumirParser.PostfixExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#unaryExpression.
    def enterUnaryExpression(self, ctx:KumirParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#unaryExpression.
    def exitUnaryExpression(self, ctx:KumirParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#powerExpression.
    def enterPowerExpression(self, ctx:KumirParser.PowerExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#powerExpression.
    def exitPowerExpression(self, ctx:KumirParser.PowerExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:KumirParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:KumirParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:KumirParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:KumirParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#relationalExpression.
    def enterRelationalExpression(self, ctx:KumirParser.RelationalExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#relationalExpression.
    def exitRelationalExpression(self, ctx:KumirParser.RelationalExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#equalityExpression.
    def enterEqualityExpression(self, ctx:KumirParser.EqualityExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#equalityExpression.
    def exitEqualityExpression(self, ctx:KumirParser.EqualityExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#logicalAndExpression.
    def enterLogicalAndExpression(self, ctx:KumirParser.LogicalAndExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#logicalAndExpression.
    def exitLogicalAndExpression(self, ctx:KumirParser.LogicalAndExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#logicalOrExpression.
    def enterLogicalOrExpression(self, ctx:KumirParser.LogicalOrExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#logicalOrExpression.
    def exitLogicalOrExpression(self, ctx:KumirParser.LogicalOrExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#expression.
    def enterExpression(self, ctx:KumirParser.ExpressionContext):
        pass

    # Exit a parse tree produced by KumirParser#expression.
    def exitExpression(self, ctx:KumirParser.ExpressionContext):
        pass


    # Enter a parse tree produced by KumirParser#typeSpecifier.
    def enterTypeSpecifier(self, ctx:KumirParser.TypeSpecifierContext):
        pass

    # Exit a parse tree produced by KumirParser#typeSpecifier.
    def exitTypeSpecifier(self, ctx:KumirParser.TypeSpecifierContext):
        pass


    # Enter a parse tree produced by KumirParser#basicType.
    def enterBasicType(self, ctx:KumirParser.BasicTypeContext):
        pass

    # Exit a parse tree produced by KumirParser#basicType.
    def exitBasicType(self, ctx:KumirParser.BasicTypeContext):
        pass


    # Enter a parse tree produced by KumirParser#actorType.
    def enterActorType(self, ctx:KumirParser.ActorTypeContext):
        pass

    # Exit a parse tree produced by KumirParser#actorType.
    def exitActorType(self, ctx:KumirParser.ActorTypeContext):
        pass


    # Enter a parse tree produced by KumirParser#arrayType.
    def enterArrayType(self, ctx:KumirParser.ArrayTypeContext):
        pass

    # Exit a parse tree produced by KumirParser#arrayType.
    def exitArrayType(self, ctx:KumirParser.ArrayTypeContext):
        pass


    # Enter a parse tree produced by KumirParser#arrayBounds.
    def enterArrayBounds(self, ctx:KumirParser.ArrayBoundsContext):
        pass

    # Exit a parse tree produced by KumirParser#arrayBounds.
    def exitArrayBounds(self, ctx:KumirParser.ArrayBoundsContext):
        pass


    # Enter a parse tree produced by KumirParser#variableDeclarationItem.
    def enterVariableDeclarationItem(self, ctx:KumirParser.VariableDeclarationItemContext):
        pass

    # Exit a parse tree produced by KumirParser#variableDeclarationItem.
    def exitVariableDeclarationItem(self, ctx:KumirParser.VariableDeclarationItemContext):
        pass


    # Enter a parse tree produced by KumirParser#variableList.
    def enterVariableList(self, ctx:KumirParser.VariableListContext):
        pass

    # Exit a parse tree produced by KumirParser#variableList.
    def exitVariableList(self, ctx:KumirParser.VariableListContext):
        pass


    # Enter a parse tree produced by KumirParser#variableDeclaration.
    def enterVariableDeclaration(self, ctx:KumirParser.VariableDeclarationContext):
        pass

    # Exit a parse tree produced by KumirParser#variableDeclaration.
    def exitVariableDeclaration(self, ctx:KumirParser.VariableDeclarationContext):
        pass


    # Enter a parse tree produced by KumirParser#globalDeclaration.
    def enterGlobalDeclaration(self, ctx:KumirParser.GlobalDeclarationContext):
        pass

    # Exit a parse tree produced by KumirParser#globalDeclaration.
    def exitGlobalDeclaration(self, ctx:KumirParser.GlobalDeclarationContext):
        pass


    # Enter a parse tree produced by KumirParser#globalAssignment.
    def enterGlobalAssignment(self, ctx:KumirParser.GlobalAssignmentContext):
        pass

    # Exit a parse tree produced by KumirParser#globalAssignment.
    def exitGlobalAssignment(self, ctx:KumirParser.GlobalAssignmentContext):
        pass


    # Enter a parse tree produced by KumirParser#parameterDeclaration.
    def enterParameterDeclaration(self, ctx:KumirParser.ParameterDeclarationContext):
        pass

    # Exit a parse tree produced by KumirParser#parameterDeclaration.
    def exitParameterDeclaration(self, ctx:KumirParser.ParameterDeclarationContext):
        pass


    # Enter a parse tree produced by KumirParser#parameterList.
    def enterParameterList(self, ctx:KumirParser.ParameterListContext):
        pass

    # Exit a parse tree produced by KumirParser#parameterList.
    def exitParameterList(self, ctx:KumirParser.ParameterListContext):
        pass


    # Enter a parse tree produced by KumirParser#algorithmNameTokens.
    def enterAlgorithmNameTokens(self, ctx:KumirParser.AlgorithmNameTokensContext):
        pass

    # Exit a parse tree produced by KumirParser#algorithmNameTokens.
    def exitAlgorithmNameTokens(self, ctx:KumirParser.AlgorithmNameTokensContext):
        pass


    # Enter a parse tree produced by KumirParser#algorithmName.
    def enterAlgorithmName(self, ctx:KumirParser.AlgorithmNameContext):
        pass

    # Exit a parse tree produced by KumirParser#algorithmName.
    def exitAlgorithmName(self, ctx:KumirParser.AlgorithmNameContext):
        pass


    # Enter a parse tree produced by KumirParser#algorithmHeader.
    def enterAlgorithmHeader(self, ctx:KumirParser.AlgorithmHeaderContext):
        pass

    # Exit a parse tree produced by KumirParser#algorithmHeader.
    def exitAlgorithmHeader(self, ctx:KumirParser.AlgorithmHeaderContext):
        pass


    # Enter a parse tree produced by KumirParser#preCondition.
    def enterPreCondition(self, ctx:KumirParser.PreConditionContext):
        pass

    # Exit a parse tree produced by KumirParser#preCondition.
    def exitPreCondition(self, ctx:KumirParser.PreConditionContext):
        pass


    # Enter a parse tree produced by KumirParser#postCondition.
    def enterPostCondition(self, ctx:KumirParser.PostConditionContext):
        pass

    # Exit a parse tree produced by KumirParser#postCondition.
    def exitPostCondition(self, ctx:KumirParser.PostConditionContext):
        pass


    # Enter a parse tree produced by KumirParser#algorithmBody.
    def enterAlgorithmBody(self, ctx:KumirParser.AlgorithmBodyContext):
        pass

    # Exit a parse tree produced by KumirParser#algorithmBody.
    def exitAlgorithmBody(self, ctx:KumirParser.AlgorithmBodyContext):
        pass


    # Enter a parse tree produced by KumirParser#statementSequence.
    def enterStatementSequence(self, ctx:KumirParser.StatementSequenceContext):
        pass

    # Exit a parse tree produced by KumirParser#statementSequence.
    def exitStatementSequence(self, ctx:KumirParser.StatementSequenceContext):
        pass


    # Enter a parse tree produced by KumirParser#lvalue.
    def enterLvalue(self, ctx:KumirParser.LvalueContext):
        pass

    # Exit a parse tree produced by KumirParser#lvalue.
    def exitLvalue(self, ctx:KumirParser.LvalueContext):
        pass


    # Enter a parse tree produced by KumirParser#assignmentStatement.
    def enterAssignmentStatement(self, ctx:KumirParser.AssignmentStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#assignmentStatement.
    def exitAssignmentStatement(self, ctx:KumirParser.AssignmentStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#ioArgument.
    def enterIoArgument(self, ctx:KumirParser.IoArgumentContext):
        pass

    # Exit a parse tree produced by KumirParser#ioArgument.
    def exitIoArgument(self, ctx:KumirParser.IoArgumentContext):
        pass


    # Enter a parse tree produced by KumirParser#ioArgumentList.
    def enterIoArgumentList(self, ctx:KumirParser.IoArgumentListContext):
        pass

    # Exit a parse tree produced by KumirParser#ioArgumentList.
    def exitIoArgumentList(self, ctx:KumirParser.IoArgumentListContext):
        pass


    # Enter a parse tree produced by KumirParser#ioStatement.
    def enterIoStatement(self, ctx:KumirParser.IoStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#ioStatement.
    def exitIoStatement(self, ctx:KumirParser.IoStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#ifStatement.
    def enterIfStatement(self, ctx:KumirParser.IfStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#ifStatement.
    def exitIfStatement(self, ctx:KumirParser.IfStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#caseBlock.
    def enterCaseBlock(self, ctx:KumirParser.CaseBlockContext):
        pass

    # Exit a parse tree produced by KumirParser#caseBlock.
    def exitCaseBlock(self, ctx:KumirParser.CaseBlockContext):
        pass


    # Enter a parse tree produced by KumirParser#switchStatement.
    def enterSwitchStatement(self, ctx:KumirParser.SwitchStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#switchStatement.
    def exitSwitchStatement(self, ctx:KumirParser.SwitchStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#endLoopCondition.
    def enterEndLoopCondition(self, ctx:KumirParser.EndLoopConditionContext):
        pass

    # Exit a parse tree produced by KumirParser#endLoopCondition.
    def exitEndLoopCondition(self, ctx:KumirParser.EndLoopConditionContext):
        pass


    # Enter a parse tree produced by KumirParser#loopSpecifier.
    def enterLoopSpecifier(self, ctx:KumirParser.LoopSpecifierContext):
        pass

    # Exit a parse tree produced by KumirParser#loopSpecifier.
    def exitLoopSpecifier(self, ctx:KumirParser.LoopSpecifierContext):
        pass


    # Enter a parse tree produced by KumirParser#loopStatement.
    def enterLoopStatement(self, ctx:KumirParser.LoopStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#loopStatement.
    def exitLoopStatement(self, ctx:KumirParser.LoopStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#exitStatement.
    def enterExitStatement(self, ctx:KumirParser.ExitStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#exitStatement.
    def exitExitStatement(self, ctx:KumirParser.ExitStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#pauseStatement.
    def enterPauseStatement(self, ctx:KumirParser.PauseStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#pauseStatement.
    def exitPauseStatement(self, ctx:KumirParser.PauseStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#stopStatement.
    def enterStopStatement(self, ctx:KumirParser.StopStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#stopStatement.
    def exitStopStatement(self, ctx:KumirParser.StopStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#assertionStatement.
    def enterAssertionStatement(self, ctx:KumirParser.AssertionStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#assertionStatement.
    def exitAssertionStatement(self, ctx:KumirParser.AssertionStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#procedureCallStatement.
    def enterProcedureCallStatement(self, ctx:KumirParser.ProcedureCallStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#procedureCallStatement.
    def exitProcedureCallStatement(self, ctx:KumirParser.ProcedureCallStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#statement.
    def enterStatement(self, ctx:KumirParser.StatementContext):
        pass

    # Exit a parse tree produced by KumirParser#statement.
    def exitStatement(self, ctx:KumirParser.StatementContext):
        pass


    # Enter a parse tree produced by KumirParser#algorithmDefinition.
    def enterAlgorithmDefinition(self, ctx:KumirParser.AlgorithmDefinitionContext):
        pass

    # Exit a parse tree produced by KumirParser#algorithmDefinition.
    def exitAlgorithmDefinition(self, ctx:KumirParser.AlgorithmDefinitionContext):
        pass


    # Enter a parse tree produced by KumirParser#moduleName.
    def enterModuleName(self, ctx:KumirParser.ModuleNameContext):
        pass

    # Exit a parse tree produced by KumirParser#moduleName.
    def exitModuleName(self, ctx:KumirParser.ModuleNameContext):
        pass


    # Enter a parse tree produced by KumirParser#importStatement.
    def enterImportStatement(self, ctx:KumirParser.ImportStatementContext):
        pass

    # Exit a parse tree produced by KumirParser#importStatement.
    def exitImportStatement(self, ctx:KumirParser.ImportStatementContext):
        pass


    # Enter a parse tree produced by KumirParser#programItem.
    def enterProgramItem(self, ctx:KumirParser.ProgramItemContext):
        pass

    # Exit a parse tree produced by KumirParser#programItem.
    def exitProgramItem(self, ctx:KumirParser.ProgramItemContext):
        pass


    # Enter a parse tree produced by KumirParser#moduleHeader.
    def enterModuleHeader(self, ctx:KumirParser.ModuleHeaderContext):
        pass

    # Exit a parse tree produced by KumirParser#moduleHeader.
    def exitModuleHeader(self, ctx:KumirParser.ModuleHeaderContext):
        pass


    # Enter a parse tree produced by KumirParser#moduleBody.
    def enterModuleBody(self, ctx:KumirParser.ModuleBodyContext):
        pass

    # Exit a parse tree produced by KumirParser#moduleBody.
    def exitModuleBody(self, ctx:KumirParser.ModuleBodyContext):
        pass


    # Enter a parse tree produced by KumirParser#implicitModuleBody.
    def enterImplicitModuleBody(self, ctx:KumirParser.ImplicitModuleBodyContext):
        pass

    # Exit a parse tree produced by KumirParser#implicitModuleBody.
    def exitImplicitModuleBody(self, ctx:KumirParser.ImplicitModuleBodyContext):
        pass


    # Enter a parse tree produced by KumirParser#moduleDefinition.
    def enterModuleDefinition(self, ctx:KumirParser.ModuleDefinitionContext):
        pass

    # Exit a parse tree produced by KumirParser#moduleDefinition.
    def exitModuleDefinition(self, ctx:KumirParser.ModuleDefinitionContext):
        pass


    # Enter a parse tree produced by KumirParser#program.
    def enterProgram(self, ctx:KumirParser.ProgramContext):
        pass

    # Exit a parse tree produced by KumirParser#program.
    def exitProgram(self, ctx:KumirParser.ProgramContext):
        pass



del KumirParser