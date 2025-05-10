// Generated from c:/Users/Bormotoon/CursorProjects/PyRobot/pyrobot/backend/kumir_interpreter/grammar/KumirParser.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast", "CheckReturnValue"})
public class KumirParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.13.1", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		MODULE=1, ENDMODULE=2, ALG_HEADER=3, ALG_BEGIN=4, ALG_END=5, PRE_CONDITION=6, 
		POST_CONDITION=7, ASSERTION=8, LOOP=9, ENDLOOP_COND=10, ENDLOOP=11, IF=12, 
		THEN=13, ELSE=14, FI=15, SWITCH=16, CASE=17, INPUT=18, OUTPUT=19, ASSIGN=20, 
		EXIT=21, PAUSE=22, STOP=23, IMPORT=24, FOR=25, WHILE=26, TIMES=27, FROM=28, 
		TO=29, STEP=30, NEWLINE_CONST=31, NOT=32, AND=33, OR=34, OUT_PARAM=35, 
		IN_PARAM=36, INOUT_PARAM=37, RETURN_VALUE=38, INTEGER_TYPE=39, REAL_TYPE=40, 
		BOOLEAN_TYPE=41, CHAR_TYPE=42, STRING_TYPE=43, TABLE_SUFFIX=44, KOMPL_TYPE=45, 
		COLOR_TYPE=46, SCANCODE_TYPE=47, FILE_TYPE=48, INTEGER_ARRAY_TYPE=49, 
		REAL_ARRAY_TYPE=50, CHAR_ARRAY_TYPE=51, STRING_ARRAY_TYPE=52, BOOLEAN_ARRAY_TYPE=53, 
		TRUE=54, FALSE=55, PROZRACHNIY=56, BELIY=57, CHERNIY=58, SERIY=59, FIOLETOVIY=60, 
		SINIY=61, GOLUBOY=62, ZELENIY=63, ZHELTIY=64, ORANZHEVIY=65, KRASNIY=66, 
		POWER=67, GE=68, LE=69, NE=70, PLUS=71, MINUS=72, MUL=73, DIV=74, EQ=75, 
		LT=76, GT=77, LPAREN=78, RPAREN=79, LBRACK=80, RBRACK=81, LBRACE=82, RBRACE=83, 
		COMMA=84, COLON=85, SEMICOLON=86, ATAT=87, AT=88, CHAR_LITERAL=89, STRING=90, 
		REAL=91, INTEGER=92, ID=93, LINE_COMMENT=94, DOC_COMMENT=95, WS=96;
	public static final int
		RULE_qualifiedIdentifier = 0, RULE_literal = 1, RULE_colorLiteral = 2, 
		RULE_expressionList = 3, RULE_arrayLiteral = 4, RULE_primaryExpression = 5, 
		RULE_argumentList = 6, RULE_indexList = 7, RULE_postfixExpression = 8, 
		RULE_unaryExpression = 9, RULE_powerExpression = 10, RULE_multiplicativeExpression = 11, 
		RULE_additiveExpression = 12, RULE_relationalExpression = 13, RULE_equalityExpression = 14, 
		RULE_logicalAndExpression = 15, RULE_logicalOrExpression = 16, RULE_expression = 17, 
		RULE_typeSpecifier = 18, RULE_basicType = 19, RULE_actorType = 20, RULE_arrayType = 21, 
		RULE_arrayBounds = 22, RULE_variableDeclarationItem = 23, RULE_variableList = 24, 
		RULE_variableDeclaration = 25, RULE_globalDeclaration = 26, RULE_globalAssignment = 27, 
		RULE_parameterDeclaration = 28, RULE_parameterList = 29, RULE_algorithmNameTokens = 30, 
		RULE_algorithmName = 31, RULE_algorithmHeader = 32, RULE_preCondition = 33, 
		RULE_postCondition = 34, RULE_algorithmBody = 35, RULE_statementSequence = 36, 
		RULE_lvalue = 37, RULE_assignmentStatement = 38, RULE_ioArgument = 39, 
		RULE_ioArgumentList = 40, RULE_ioStatement = 41, RULE_ifStatement = 42, 
		RULE_caseBlock = 43, RULE_switchStatement = 44, RULE_endLoopCondition = 45, 
		RULE_loopSpecifier = 46, RULE_loopStatement = 47, RULE_exitStatement = 48, 
		RULE_pauseStatement = 49, RULE_stopStatement = 50, RULE_assertionStatement = 51, 
		RULE_procedureCallStatement = 52, RULE_statement = 53, RULE_algorithmDefinition = 54, 
		RULE_moduleName = 55, RULE_importStatement = 56, RULE_programItem = 57, 
		RULE_moduleHeader = 58, RULE_moduleBody = 59, RULE_implicitModuleBody = 60, 
		RULE_moduleDefinition = 61, RULE_program = 62;
	private static String[] makeRuleNames() {
		return new String[] {
			"qualifiedIdentifier", "literal", "colorLiteral", "expressionList", "arrayLiteral", 
			"primaryExpression", "argumentList", "indexList", "postfixExpression", 
			"unaryExpression", "powerExpression", "multiplicativeExpression", "additiveExpression", 
			"relationalExpression", "equalityExpression", "logicalAndExpression", 
			"logicalOrExpression", "expression", "typeSpecifier", "basicType", "actorType", 
			"arrayType", "arrayBounds", "variableDeclarationItem", "variableList", 
			"variableDeclaration", "globalDeclaration", "globalAssignment", "parameterDeclaration", 
			"parameterList", "algorithmNameTokens", "algorithmName", "algorithmHeader", 
			"preCondition", "postCondition", "algorithmBody", "statementSequence", 
			"lvalue", "assignmentStatement", "ioArgument", "ioArgumentList", "ioStatement", 
			"ifStatement", "caseBlock", "switchStatement", "endLoopCondition", "loopSpecifier", 
			"loopStatement", "exitStatement", "pauseStatement", "stopStatement", 
			"assertionStatement", "procedureCallStatement", "statement", "algorithmDefinition", 
			"moduleName", "importStatement", "programItem", "moduleHeader", "moduleBody", 
			"implicitModuleBody", "moduleDefinition", "program"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'\\u043C\\u043E\\u0434\\u0443\\u043B\\u044C'", null, "'\\u0430\\u043B\\u0433'", 
			"'\\u043D\\u0430\\u0447'", "'\\u043A\\u043E\\u043D'", "'\\u0434\\u0430\\u043D\\u043E'", 
			"'\\u043D\\u0430\\u0434\\u043E'", "'\\u0443\\u0442\\u0432'", "'\\u043D\\u0446'", 
			null, "'\\u043A\\u0446'", "'\\u0435\\u0441\\u043B\\u0438'", "'\\u0442\\u043E'", 
			"'\\u0438\\u043D\\u0430\\u0447\\u0435'", "'\\u0432\\u0441\\u0435'", "'\\u0432\\u044B\\u0431\\u043E\\u0440'", 
			"'\\u043F\\u0440\\u0438'", "'\\u0432\\u0432\\u043E\\u0434'", "'\\u0432\\u044B\\u0432\\u043E\\u0434'", 
			"':='", "'\\u0432\\u044B\\u0445\\u043E\\u0434'", "'\\u043F\\u0430\\u0443\\u0437\\u0430'", 
			"'\\u0441\\u0442\\u043E\\u043F'", "'\\u0438\\u0441\\u043F\\u043E\\u043B\\u044C\\u0437\\u043E\\u0432\\u0430\\u0442\\u044C'", 
			"'\\u0434\\u043B\\u044F'", "'\\u043F\\u043E\\u043A\\u0430'", "'\\u0440\\u0430\\u0437'", 
			"'\\u043E\\u0442'", "'\\u0434\\u043E'", "'\\u0448\\u0430\\u0433'", "'\\u043D\\u0441'", 
			"'\\u043D\\u0435'", "'\\u0438'", "'\\u0438\\u043B\\u0438'", "'\\u0440\\u0435\\u0437'", 
			"'\\u0430\\u0440\\u0433'", null, "'\\u0437\\u043D\\u0430\\u0447'", "'\\u0446\\u0435\\u043B'", 
			"'\\u0432\\u0435\\u0449'", "'\\u043B\\u043E\\u0433'", "'\\u0441\\u0438\\u043C'", 
			"'\\u043B\\u0438\\u0442'", "'\\u0442\\u0430\\u0431'", "'\\u043A\\u043E\\u043C\\u043F\\u043B'", 
			"'\\u0446\\u0432\\u0435\\u0442'", "'\\u0441\\u043A\\u0430\\u043D\\u043A\\u043E\\u0434'", 
			"'\\u0444\\u0430\\u0439\\u043B'", null, null, null, null, null, "'\\u0434\\u0430'", 
			"'\\u043D\\u0435\\u0442'", "'\\u043F\\u0440\\u043E\\u0437\\u0440\\u0430\\u0447\\u043D\\u044B\\u0439'", 
			"'\\u0431\\u0435\\u043B\\u044B\\u0439'", null, "'\\u0441\\u0435\\u0440\\u044B\\u0439'", 
			"'\\u0444\\u0438\\u043E\\u043B\\u0435\\u0442\\u043E\\u0432\\u044B\\u0439'", 
			"'\\u0441\\u0438\\u043D\\u0438\\u0439'", "'\\u0433\\u043E\\u043B\\u0443\\u0431\\u043E\\u0439'", 
			null, null, "'\\u043E\\u0440\\u0430\\u043D\\u0436\\u0435\\u0432\\u044B\\u0439'", 
			"'\\u043A\\u0440\\u0430\\u0441\\u043D\\u044B\\u0439'", "'**'", null, 
			null, null, "'+'", "'-'", "'*'", "'/'", "'='", "'<'", "'>'", "'('", "')'", 
			"'['", "']'", "'{'", "'}'", "','", "':'", "';'", "'@@'", "'@'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, "MODULE", "ENDMODULE", "ALG_HEADER", "ALG_BEGIN", "ALG_END", "PRE_CONDITION", 
			"POST_CONDITION", "ASSERTION", "LOOP", "ENDLOOP_COND", "ENDLOOP", "IF", 
			"THEN", "ELSE", "FI", "SWITCH", "CASE", "INPUT", "OUTPUT", "ASSIGN", 
			"EXIT", "PAUSE", "STOP", "IMPORT", "FOR", "WHILE", "TIMES", "FROM", "TO", 
			"STEP", "NEWLINE_CONST", "NOT", "AND", "OR", "OUT_PARAM", "IN_PARAM", 
			"INOUT_PARAM", "RETURN_VALUE", "INTEGER_TYPE", "REAL_TYPE", "BOOLEAN_TYPE", 
			"CHAR_TYPE", "STRING_TYPE", "TABLE_SUFFIX", "KOMPL_TYPE", "COLOR_TYPE", 
			"SCANCODE_TYPE", "FILE_TYPE", "INTEGER_ARRAY_TYPE", "REAL_ARRAY_TYPE", 
			"CHAR_ARRAY_TYPE", "STRING_ARRAY_TYPE", "BOOLEAN_ARRAY_TYPE", "TRUE", 
			"FALSE", "PROZRACHNIY", "BELIY", "CHERNIY", "SERIY", "FIOLETOVIY", "SINIY", 
			"GOLUBOY", "ZELENIY", "ZHELTIY", "ORANZHEVIY", "KRASNIY", "POWER", "GE", 
			"LE", "NE", "PLUS", "MINUS", "MUL", "DIV", "EQ", "LT", "GT", "LPAREN", 
			"RPAREN", "LBRACK", "RBRACK", "LBRACE", "RBRACE", "COMMA", "COLON", "SEMICOLON", 
			"ATAT", "AT", "CHAR_LITERAL", "STRING", "REAL", "INTEGER", "ID", "LINE_COMMENT", 
			"DOC_COMMENT", "WS"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "KumirParser.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public KumirParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@SuppressWarnings("CheckReturnValue")
	public static class QualifiedIdentifierContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(KumirParser.ID, 0); }
		public QualifiedIdentifierContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_qualifiedIdentifier; }
	}

	public final QualifiedIdentifierContext qualifiedIdentifier() throws RecognitionException {
		QualifiedIdentifierContext _localctx = new QualifiedIdentifierContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_qualifiedIdentifier);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(126);
			match(ID);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LiteralContext extends ParserRuleContext {
		public TerminalNode INTEGER() { return getToken(KumirParser.INTEGER, 0); }
		public TerminalNode REAL() { return getToken(KumirParser.REAL, 0); }
		public TerminalNode STRING() { return getToken(KumirParser.STRING, 0); }
		public TerminalNode CHAR_LITERAL() { return getToken(KumirParser.CHAR_LITERAL, 0); }
		public TerminalNode TRUE() { return getToken(KumirParser.TRUE, 0); }
		public TerminalNode FALSE() { return getToken(KumirParser.FALSE, 0); }
		public ColorLiteralContext colorLiteral() {
			return getRuleContext(ColorLiteralContext.class,0);
		}
		public TerminalNode NEWLINE_CONST() { return getToken(KumirParser.NEWLINE_CONST, 0); }
		public LiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_literal; }
	}

	public final LiteralContext literal() throws RecognitionException {
		LiteralContext _localctx = new LiteralContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_literal);
		try {
			setState(136);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case INTEGER:
				enterOuterAlt(_localctx, 1);
				{
				setState(128);
				match(INTEGER);
				}
				break;
			case REAL:
				enterOuterAlt(_localctx, 2);
				{
				setState(129);
				match(REAL);
				}
				break;
			case STRING:
				enterOuterAlt(_localctx, 3);
				{
				setState(130);
				match(STRING);
				}
				break;
			case CHAR_LITERAL:
				enterOuterAlt(_localctx, 4);
				{
				setState(131);
				match(CHAR_LITERAL);
				}
				break;
			case TRUE:
				enterOuterAlt(_localctx, 5);
				{
				setState(132);
				match(TRUE);
				}
				break;
			case FALSE:
				enterOuterAlt(_localctx, 6);
				{
				setState(133);
				match(FALSE);
				}
				break;
			case PROZRACHNIY:
			case BELIY:
			case CHERNIY:
			case SERIY:
			case FIOLETOVIY:
			case SINIY:
			case GOLUBOY:
			case ZELENIY:
			case ZHELTIY:
			case ORANZHEVIY:
			case KRASNIY:
				enterOuterAlt(_localctx, 7);
				{
				setState(134);
				colorLiteral();
				}
				break;
			case NEWLINE_CONST:
				enterOuterAlt(_localctx, 8);
				{
				setState(135);
				match(NEWLINE_CONST);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ColorLiteralContext extends ParserRuleContext {
		public TerminalNode PROZRACHNIY() { return getToken(KumirParser.PROZRACHNIY, 0); }
		public TerminalNode BELIY() { return getToken(KumirParser.BELIY, 0); }
		public TerminalNode CHERNIY() { return getToken(KumirParser.CHERNIY, 0); }
		public TerminalNode SERIY() { return getToken(KumirParser.SERIY, 0); }
		public TerminalNode FIOLETOVIY() { return getToken(KumirParser.FIOLETOVIY, 0); }
		public TerminalNode SINIY() { return getToken(KumirParser.SINIY, 0); }
		public TerminalNode GOLUBOY() { return getToken(KumirParser.GOLUBOY, 0); }
		public TerminalNode ZELENIY() { return getToken(KumirParser.ZELENIY, 0); }
		public TerminalNode ZHELTIY() { return getToken(KumirParser.ZHELTIY, 0); }
		public TerminalNode ORANZHEVIY() { return getToken(KumirParser.ORANZHEVIY, 0); }
		public TerminalNode KRASNIY() { return getToken(KumirParser.KRASNIY, 0); }
		public ColorLiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_colorLiteral; }
	}

	public final ColorLiteralContext colorLiteral() throws RecognitionException {
		ColorLiteralContext _localctx = new ColorLiteralContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_colorLiteral);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(138);
			_la = _input.LA(1);
			if ( !(((((_la - 56)) & ~0x3f) == 0 && ((1L << (_la - 56)) & 2047L) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ExpressionListContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(KumirParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(KumirParser.COMMA, i);
		}
		public ExpressionListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expressionList; }
	}

	public final ExpressionListContext expressionList() throws RecognitionException {
		ExpressionListContext _localctx = new ExpressionListContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_expressionList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(140);
			expression();
			setState(145);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(141);
				match(COMMA);
				setState(142);
				expression();
				}
				}
				setState(147);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ArrayLiteralContext extends ParserRuleContext {
		public TerminalNode LBRACE() { return getToken(KumirParser.LBRACE, 0); }
		public TerminalNode RBRACE() { return getToken(KumirParser.RBRACE, 0); }
		public ExpressionListContext expressionList() {
			return getRuleContext(ExpressionListContext.class,0);
		}
		public ArrayLiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_arrayLiteral; }
	}

	public final ArrayLiteralContext arrayLiteral() throws RecognitionException {
		ArrayLiteralContext _localctx = new ArrayLiteralContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_arrayLiteral);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(148);
			match(LBRACE);
			setState(150);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (((((_la - 31)) & ~0x3f) == 0 && ((1L << (_la - 31)) & 8937537565251076227L) != 0)) {
				{
				setState(149);
				expressionList();
				}
			}

			setState(152);
			match(RBRACE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PrimaryExpressionContext extends ParserRuleContext {
		public LiteralContext literal() {
			return getRuleContext(LiteralContext.class,0);
		}
		public QualifiedIdentifierContext qualifiedIdentifier() {
			return getRuleContext(QualifiedIdentifierContext.class,0);
		}
		public TerminalNode RETURN_VALUE() { return getToken(KumirParser.RETURN_VALUE, 0); }
		public TerminalNode LPAREN() { return getToken(KumirParser.LPAREN, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode RPAREN() { return getToken(KumirParser.RPAREN, 0); }
		public ArrayLiteralContext arrayLiteral() {
			return getRuleContext(ArrayLiteralContext.class,0);
		}
		public PrimaryExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_primaryExpression; }
	}

	public final PrimaryExpressionContext primaryExpression() throws RecognitionException {
		PrimaryExpressionContext _localctx = new PrimaryExpressionContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_primaryExpression);
		try {
			setState(162);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case NEWLINE_CONST:
			case TRUE:
			case FALSE:
			case PROZRACHNIY:
			case BELIY:
			case CHERNIY:
			case SERIY:
			case FIOLETOVIY:
			case SINIY:
			case GOLUBOY:
			case ZELENIY:
			case ZHELTIY:
			case ORANZHEVIY:
			case KRASNIY:
			case CHAR_LITERAL:
			case STRING:
			case REAL:
			case INTEGER:
				enterOuterAlt(_localctx, 1);
				{
				setState(154);
				literal();
				}
				break;
			case ID:
				enterOuterAlt(_localctx, 2);
				{
				setState(155);
				qualifiedIdentifier();
				}
				break;
			case RETURN_VALUE:
				enterOuterAlt(_localctx, 3);
				{
				setState(156);
				match(RETURN_VALUE);
				}
				break;
			case LPAREN:
				enterOuterAlt(_localctx, 4);
				{
				setState(157);
				match(LPAREN);
				setState(158);
				expression();
				setState(159);
				match(RPAREN);
				}
				break;
			case LBRACE:
				enterOuterAlt(_localctx, 5);
				{
				setState(161);
				arrayLiteral();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ArgumentListContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(KumirParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(KumirParser.COMMA, i);
		}
		public ArgumentListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argumentList; }
	}

	public final ArgumentListContext argumentList() throws RecognitionException {
		ArgumentListContext _localctx = new ArgumentListContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_argumentList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(164);
			expression();
			setState(169);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(165);
				match(COMMA);
				setState(166);
				expression();
				}
				}
				setState(171);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IndexListContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(KumirParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(KumirParser.COMMA, i);
		}
		public IndexListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_indexList; }
	}

	public final IndexListContext indexList() throws RecognitionException {
		IndexListContext _localctx = new IndexListContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_indexList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(172);
			expression();
			setState(177);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(173);
				match(COMMA);
				setState(174);
				expression();
				}
				}
				setState(179);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PostfixExpressionContext extends ParserRuleContext {
		public PrimaryExpressionContext primaryExpression() {
			return getRuleContext(PrimaryExpressionContext.class,0);
		}
		public List<TerminalNode> LBRACK() { return getTokens(KumirParser.LBRACK); }
		public TerminalNode LBRACK(int i) {
			return getToken(KumirParser.LBRACK, i);
		}
		public List<IndexListContext> indexList() {
			return getRuleContexts(IndexListContext.class);
		}
		public IndexListContext indexList(int i) {
			return getRuleContext(IndexListContext.class,i);
		}
		public List<TerminalNode> RBRACK() { return getTokens(KumirParser.RBRACK); }
		public TerminalNode RBRACK(int i) {
			return getToken(KumirParser.RBRACK, i);
		}
		public List<TerminalNode> LPAREN() { return getTokens(KumirParser.LPAREN); }
		public TerminalNode LPAREN(int i) {
			return getToken(KumirParser.LPAREN, i);
		}
		public List<TerminalNode> RPAREN() { return getTokens(KumirParser.RPAREN); }
		public TerminalNode RPAREN(int i) {
			return getToken(KumirParser.RPAREN, i);
		}
		public List<ArgumentListContext> argumentList() {
			return getRuleContexts(ArgumentListContext.class);
		}
		public ArgumentListContext argumentList(int i) {
			return getRuleContext(ArgumentListContext.class,i);
		}
		public PostfixExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_postfixExpression; }
	}

	public final PostfixExpressionContext postfixExpression() throws RecognitionException {
		PostfixExpressionContext _localctx = new PostfixExpressionContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_postfixExpression);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(180);
			primaryExpression();
			setState(192);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,8,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					setState(190);
					_errHandler.sync(this);
					switch (_input.LA(1)) {
					case LBRACK:
						{
						setState(181);
						match(LBRACK);
						setState(182);
						indexList();
						setState(183);
						match(RBRACK);
						}
						break;
					case LPAREN:
						{
						setState(185);
						match(LPAREN);
						setState(187);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if (((((_la - 31)) & ~0x3f) == 0 && ((1L << (_la - 31)) & 8937537565251076227L) != 0)) {
							{
							setState(186);
							argumentList();
							}
						}

						setState(189);
						match(RPAREN);
						}
						break;
					default:
						throw new NoViableAltException(this);
					}
					} 
				}
				setState(194);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,8,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class UnaryExpressionContext extends ParserRuleContext {
		public UnaryExpressionContext unaryExpression() {
			return getRuleContext(UnaryExpressionContext.class,0);
		}
		public TerminalNode PLUS() { return getToken(KumirParser.PLUS, 0); }
		public TerminalNode MINUS() { return getToken(KumirParser.MINUS, 0); }
		public TerminalNode NOT() { return getToken(KumirParser.NOT, 0); }
		public PostfixExpressionContext postfixExpression() {
			return getRuleContext(PostfixExpressionContext.class,0);
		}
		public UnaryExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_unaryExpression; }
	}

	public final UnaryExpressionContext unaryExpression() throws RecognitionException {
		UnaryExpressionContext _localctx = new UnaryExpressionContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_unaryExpression);
		int _la;
		try {
			setState(198);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case NOT:
			case PLUS:
			case MINUS:
				enterOuterAlt(_localctx, 1);
				{
				setState(195);
				_la = _input.LA(1);
				if ( !(((((_la - 32)) & ~0x3f) == 0 && ((1L << (_la - 32)) & 1649267441665L) != 0)) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(196);
				unaryExpression();
				}
				break;
			case NEWLINE_CONST:
			case RETURN_VALUE:
			case TRUE:
			case FALSE:
			case PROZRACHNIY:
			case BELIY:
			case CHERNIY:
			case SERIY:
			case FIOLETOVIY:
			case SINIY:
			case GOLUBOY:
			case ZELENIY:
			case ZHELTIY:
			case ORANZHEVIY:
			case KRASNIY:
			case LPAREN:
			case LBRACE:
			case CHAR_LITERAL:
			case STRING:
			case REAL:
			case INTEGER:
			case ID:
				enterOuterAlt(_localctx, 2);
				{
				setState(197);
				postfixExpression();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PowerExpressionContext extends ParserRuleContext {
		public UnaryExpressionContext unaryExpression() {
			return getRuleContext(UnaryExpressionContext.class,0);
		}
		public TerminalNode POWER() { return getToken(KumirParser.POWER, 0); }
		public PowerExpressionContext powerExpression() {
			return getRuleContext(PowerExpressionContext.class,0);
		}
		public PowerExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_powerExpression; }
	}

	public final PowerExpressionContext powerExpression() throws RecognitionException {
		PowerExpressionContext _localctx = new PowerExpressionContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_powerExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(200);
			unaryExpression();
			setState(203);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==POWER) {
				{
				setState(201);
				match(POWER);
				setState(202);
				powerExpression();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class MultiplicativeExpressionContext extends ParserRuleContext {
		public List<PowerExpressionContext> powerExpression() {
			return getRuleContexts(PowerExpressionContext.class);
		}
		public PowerExpressionContext powerExpression(int i) {
			return getRuleContext(PowerExpressionContext.class,i);
		}
		public List<TerminalNode> MUL() { return getTokens(KumirParser.MUL); }
		public TerminalNode MUL(int i) {
			return getToken(KumirParser.MUL, i);
		}
		public List<TerminalNode> DIV() { return getTokens(KumirParser.DIV); }
		public TerminalNode DIV(int i) {
			return getToken(KumirParser.DIV, i);
		}
		public MultiplicativeExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_multiplicativeExpression; }
	}

	public final MultiplicativeExpressionContext multiplicativeExpression() throws RecognitionException {
		MultiplicativeExpressionContext _localctx = new MultiplicativeExpressionContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_multiplicativeExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(205);
			powerExpression();
			setState(210);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==MUL || _la==DIV) {
				{
				{
				setState(206);
				_la = _input.LA(1);
				if ( !(_la==MUL || _la==DIV) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(207);
				powerExpression();
				}
				}
				setState(212);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AdditiveExpressionContext extends ParserRuleContext {
		public List<MultiplicativeExpressionContext> multiplicativeExpression() {
			return getRuleContexts(MultiplicativeExpressionContext.class);
		}
		public MultiplicativeExpressionContext multiplicativeExpression(int i) {
			return getRuleContext(MultiplicativeExpressionContext.class,i);
		}
		public List<TerminalNode> PLUS() { return getTokens(KumirParser.PLUS); }
		public TerminalNode PLUS(int i) {
			return getToken(KumirParser.PLUS, i);
		}
		public List<TerminalNode> MINUS() { return getTokens(KumirParser.MINUS); }
		public TerminalNode MINUS(int i) {
			return getToken(KumirParser.MINUS, i);
		}
		public AdditiveExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_additiveExpression; }
	}

	public final AdditiveExpressionContext additiveExpression() throws RecognitionException {
		AdditiveExpressionContext _localctx = new AdditiveExpressionContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_additiveExpression);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(213);
			multiplicativeExpression();
			setState(218);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,12,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(214);
					_la = _input.LA(1);
					if ( !(_la==PLUS || _la==MINUS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(215);
					multiplicativeExpression();
					}
					} 
				}
				setState(220);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,12,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class RelationalExpressionContext extends ParserRuleContext {
		public List<AdditiveExpressionContext> additiveExpression() {
			return getRuleContexts(AdditiveExpressionContext.class);
		}
		public AdditiveExpressionContext additiveExpression(int i) {
			return getRuleContext(AdditiveExpressionContext.class,i);
		}
		public List<TerminalNode> LT() { return getTokens(KumirParser.LT); }
		public TerminalNode LT(int i) {
			return getToken(KumirParser.LT, i);
		}
		public List<TerminalNode> GT() { return getTokens(KumirParser.GT); }
		public TerminalNode GT(int i) {
			return getToken(KumirParser.GT, i);
		}
		public List<TerminalNode> LE() { return getTokens(KumirParser.LE); }
		public TerminalNode LE(int i) {
			return getToken(KumirParser.LE, i);
		}
		public List<TerminalNode> GE() { return getTokens(KumirParser.GE); }
		public TerminalNode GE(int i) {
			return getToken(KumirParser.GE, i);
		}
		public RelationalExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_relationalExpression; }
	}

	public final RelationalExpressionContext relationalExpression() throws RecognitionException {
		RelationalExpressionContext _localctx = new RelationalExpressionContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_relationalExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(221);
			additiveExpression();
			setState(226);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (((((_la - 68)) & ~0x3f) == 0 && ((1L << (_la - 68)) & 771L) != 0)) {
				{
				{
				setState(222);
				_la = _input.LA(1);
				if ( !(((((_la - 68)) & ~0x3f) == 0 && ((1L << (_la - 68)) & 771L) != 0)) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(223);
				additiveExpression();
				}
				}
				setState(228);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class EqualityExpressionContext extends ParserRuleContext {
		public List<RelationalExpressionContext> relationalExpression() {
			return getRuleContexts(RelationalExpressionContext.class);
		}
		public RelationalExpressionContext relationalExpression(int i) {
			return getRuleContext(RelationalExpressionContext.class,i);
		}
		public List<TerminalNode> EQ() { return getTokens(KumirParser.EQ); }
		public TerminalNode EQ(int i) {
			return getToken(KumirParser.EQ, i);
		}
		public List<TerminalNode> NE() { return getTokens(KumirParser.NE); }
		public TerminalNode NE(int i) {
			return getToken(KumirParser.NE, i);
		}
		public EqualityExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_equalityExpression; }
	}

	public final EqualityExpressionContext equalityExpression() throws RecognitionException {
		EqualityExpressionContext _localctx = new EqualityExpressionContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_equalityExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(229);
			relationalExpression();
			setState(234);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==NE || _la==EQ) {
				{
				{
				setState(230);
				_la = _input.LA(1);
				if ( !(_la==NE || _la==EQ) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(231);
				relationalExpression();
				}
				}
				setState(236);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LogicalAndExpressionContext extends ParserRuleContext {
		public List<EqualityExpressionContext> equalityExpression() {
			return getRuleContexts(EqualityExpressionContext.class);
		}
		public EqualityExpressionContext equalityExpression(int i) {
			return getRuleContext(EqualityExpressionContext.class,i);
		}
		public List<TerminalNode> AND() { return getTokens(KumirParser.AND); }
		public TerminalNode AND(int i) {
			return getToken(KumirParser.AND, i);
		}
		public LogicalAndExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicalAndExpression; }
	}

	public final LogicalAndExpressionContext logicalAndExpression() throws RecognitionException {
		LogicalAndExpressionContext _localctx = new LogicalAndExpressionContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_logicalAndExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(237);
			equalityExpression();
			setState(242);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==AND) {
				{
				{
				setState(238);
				match(AND);
				setState(239);
				equalityExpression();
				}
				}
				setState(244);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LogicalOrExpressionContext extends ParserRuleContext {
		public List<LogicalAndExpressionContext> logicalAndExpression() {
			return getRuleContexts(LogicalAndExpressionContext.class);
		}
		public LogicalAndExpressionContext logicalAndExpression(int i) {
			return getRuleContext(LogicalAndExpressionContext.class,i);
		}
		public List<TerminalNode> OR() { return getTokens(KumirParser.OR); }
		public TerminalNode OR(int i) {
			return getToken(KumirParser.OR, i);
		}
		public LogicalOrExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicalOrExpression; }
	}

	public final LogicalOrExpressionContext logicalOrExpression() throws RecognitionException {
		LogicalOrExpressionContext _localctx = new LogicalOrExpressionContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_logicalOrExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(245);
			logicalAndExpression();
			setState(250);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==OR) {
				{
				{
				setState(246);
				match(OR);
				setState(247);
				logicalAndExpression();
				}
				}
				setState(252);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ExpressionContext extends ParserRuleContext {
		public LogicalOrExpressionContext logicalOrExpression() {
			return getRuleContext(LogicalOrExpressionContext.class,0);
		}
		public ExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expression; }
	}

	public final ExpressionContext expression() throws RecognitionException {
		ExpressionContext _localctx = new ExpressionContext(_ctx, getState());
		enterRule(_localctx, 34, RULE_expression);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(253);
			logicalOrExpression();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TypeSpecifierContext extends ParserRuleContext {
		public ArrayTypeContext arrayType() {
			return getRuleContext(ArrayTypeContext.class,0);
		}
		public BasicTypeContext basicType() {
			return getRuleContext(BasicTypeContext.class,0);
		}
		public TerminalNode TABLE_SUFFIX() { return getToken(KumirParser.TABLE_SUFFIX, 0); }
		public ActorTypeContext actorType() {
			return getRuleContext(ActorTypeContext.class,0);
		}
		public TypeSpecifierContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_typeSpecifier; }
	}

	public final TypeSpecifierContext typeSpecifier() throws RecognitionException {
		TypeSpecifierContext _localctx = new TypeSpecifierContext(_ctx, getState());
		enterRule(_localctx, 36, RULE_typeSpecifier);
		try {
			setState(261);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case INTEGER_ARRAY_TYPE:
			case REAL_ARRAY_TYPE:
			case CHAR_ARRAY_TYPE:
			case STRING_ARRAY_TYPE:
			case BOOLEAN_ARRAY_TYPE:
				enterOuterAlt(_localctx, 1);
				{
				setState(255);
				arrayType();
				}
				break;
			case INTEGER_TYPE:
			case REAL_TYPE:
			case BOOLEAN_TYPE:
			case CHAR_TYPE:
			case STRING_TYPE:
				enterOuterAlt(_localctx, 2);
				{
				setState(256);
				basicType();
				setState(258);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,17,_ctx) ) {
				case 1:
					{
					setState(257);
					match(TABLE_SUFFIX);
					}
					break;
				}
				}
				break;
			case KOMPL_TYPE:
			case COLOR_TYPE:
			case SCANCODE_TYPE:
			case FILE_TYPE:
				enterOuterAlt(_localctx, 3);
				{
				setState(260);
				actorType();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class BasicTypeContext extends ParserRuleContext {
		public TerminalNode INTEGER_TYPE() { return getToken(KumirParser.INTEGER_TYPE, 0); }
		public TerminalNode REAL_TYPE() { return getToken(KumirParser.REAL_TYPE, 0); }
		public TerminalNode BOOLEAN_TYPE() { return getToken(KumirParser.BOOLEAN_TYPE, 0); }
		public TerminalNode CHAR_TYPE() { return getToken(KumirParser.CHAR_TYPE, 0); }
		public TerminalNode STRING_TYPE() { return getToken(KumirParser.STRING_TYPE, 0); }
		public BasicTypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_basicType; }
	}

	public final BasicTypeContext basicType() throws RecognitionException {
		BasicTypeContext _localctx = new BasicTypeContext(_ctx, getState());
		enterRule(_localctx, 38, RULE_basicType);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(263);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 17042430230528L) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ActorTypeContext extends ParserRuleContext {
		public TerminalNode KOMPL_TYPE() { return getToken(KumirParser.KOMPL_TYPE, 0); }
		public TerminalNode COLOR_TYPE() { return getToken(KumirParser.COLOR_TYPE, 0); }
		public TerminalNode SCANCODE_TYPE() { return getToken(KumirParser.SCANCODE_TYPE, 0); }
		public TerminalNode FILE_TYPE() { return getToken(KumirParser.FILE_TYPE, 0); }
		public ActorTypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_actorType; }
	}

	public final ActorTypeContext actorType() throws RecognitionException {
		ActorTypeContext _localctx = new ActorTypeContext(_ctx, getState());
		enterRule(_localctx, 40, RULE_actorType);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(265);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 527765581332480L) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ArrayTypeContext extends ParserRuleContext {
		public TerminalNode INTEGER_ARRAY_TYPE() { return getToken(KumirParser.INTEGER_ARRAY_TYPE, 0); }
		public TerminalNode REAL_ARRAY_TYPE() { return getToken(KumirParser.REAL_ARRAY_TYPE, 0); }
		public TerminalNode BOOLEAN_ARRAY_TYPE() { return getToken(KumirParser.BOOLEAN_ARRAY_TYPE, 0); }
		public TerminalNode CHAR_ARRAY_TYPE() { return getToken(KumirParser.CHAR_ARRAY_TYPE, 0); }
		public TerminalNode STRING_ARRAY_TYPE() { return getToken(KumirParser.STRING_ARRAY_TYPE, 0); }
		public ArrayTypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_arrayType; }
	}

	public final ArrayTypeContext arrayType() throws RecognitionException {
		ArrayTypeContext _localctx = new ArrayTypeContext(_ctx, getState());
		enterRule(_localctx, 42, RULE_arrayType);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(267);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 17451448556060672L) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ArrayBoundsContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode COLON() { return getToken(KumirParser.COLON, 0); }
		public ArrayBoundsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_arrayBounds; }
	}

	public final ArrayBoundsContext arrayBounds() throws RecognitionException {
		ArrayBoundsContext _localctx = new ArrayBoundsContext(_ctx, getState());
		enterRule(_localctx, 44, RULE_arrayBounds);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(269);
			expression();
			setState(270);
			match(COLON);
			setState(271);
			expression();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class VariableDeclarationItemContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(KumirParser.ID, 0); }
		public TerminalNode LBRACK() { return getToken(KumirParser.LBRACK, 0); }
		public List<ArrayBoundsContext> arrayBounds() {
			return getRuleContexts(ArrayBoundsContext.class);
		}
		public ArrayBoundsContext arrayBounds(int i) {
			return getRuleContext(ArrayBoundsContext.class,i);
		}
		public TerminalNode RBRACK() { return getToken(KumirParser.RBRACK, 0); }
		public TerminalNode EQ() { return getToken(KumirParser.EQ, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public List<TerminalNode> COMMA() { return getTokens(KumirParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(KumirParser.COMMA, i);
		}
		public VariableDeclarationItemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_variableDeclarationItem; }
	}

	public final VariableDeclarationItemContext variableDeclarationItem() throws RecognitionException {
		VariableDeclarationItemContext _localctx = new VariableDeclarationItemContext(_ctx, getState());
		enterRule(_localctx, 46, RULE_variableDeclarationItem);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(273);
			match(ID);
			setState(285);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==LBRACK) {
				{
				setState(274);
				match(LBRACK);
				setState(275);
				arrayBounds();
				setState(280);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==COMMA) {
					{
					{
					setState(276);
					match(COMMA);
					setState(277);
					arrayBounds();
					}
					}
					setState(282);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(283);
				match(RBRACK);
				}
			}

			setState(289);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==EQ) {
				{
				setState(287);
				match(EQ);
				setState(288);
				expression();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class VariableListContext extends ParserRuleContext {
		public List<VariableDeclarationItemContext> variableDeclarationItem() {
			return getRuleContexts(VariableDeclarationItemContext.class);
		}
		public VariableDeclarationItemContext variableDeclarationItem(int i) {
			return getRuleContext(VariableDeclarationItemContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(KumirParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(KumirParser.COMMA, i);
		}
		public VariableListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_variableList; }
	}

	public final VariableListContext variableList() throws RecognitionException {
		VariableListContext _localctx = new VariableListContext(_ctx, getState());
		enterRule(_localctx, 48, RULE_variableList);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(291);
			variableDeclarationItem();
			setState(296);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,22,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(292);
					match(COMMA);
					setState(293);
					variableDeclarationItem();
					}
					} 
				}
				setState(298);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,22,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class VariableDeclarationContext extends ParserRuleContext {
		public TypeSpecifierContext typeSpecifier() {
			return getRuleContext(TypeSpecifierContext.class,0);
		}
		public VariableListContext variableList() {
			return getRuleContext(VariableListContext.class,0);
		}
		public VariableDeclarationContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_variableDeclaration; }
	}

	public final VariableDeclarationContext variableDeclaration() throws RecognitionException {
		VariableDeclarationContext _localctx = new VariableDeclarationContext(_ctx, getState());
		enterRule(_localctx, 50, RULE_variableDeclaration);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(299);
			typeSpecifier();
			setState(300);
			variableList();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class GlobalDeclarationContext extends ParserRuleContext {
		public TypeSpecifierContext typeSpecifier() {
			return getRuleContext(TypeSpecifierContext.class,0);
		}
		public VariableListContext variableList() {
			return getRuleContext(VariableListContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public GlobalDeclarationContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_globalDeclaration; }
	}

	public final GlobalDeclarationContext globalDeclaration() throws RecognitionException {
		GlobalDeclarationContext _localctx = new GlobalDeclarationContext(_ctx, getState());
		enterRule(_localctx, 52, RULE_globalDeclaration);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(302);
			typeSpecifier();
			setState(303);
			variableList();
			setState(305);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(304);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class GlobalAssignmentContext extends ParserRuleContext {
		public QualifiedIdentifierContext qualifiedIdentifier() {
			return getRuleContext(QualifiedIdentifierContext.class,0);
		}
		public TerminalNode ASSIGN() { return getToken(KumirParser.ASSIGN, 0); }
		public LiteralContext literal() {
			return getRuleContext(LiteralContext.class,0);
		}
		public UnaryExpressionContext unaryExpression() {
			return getRuleContext(UnaryExpressionContext.class,0);
		}
		public ArrayLiteralContext arrayLiteral() {
			return getRuleContext(ArrayLiteralContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public GlobalAssignmentContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_globalAssignment; }
	}

	public final GlobalAssignmentContext globalAssignment() throws RecognitionException {
		GlobalAssignmentContext _localctx = new GlobalAssignmentContext(_ctx, getState());
		enterRule(_localctx, 54, RULE_globalAssignment);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(307);
			qualifiedIdentifier();
			setState(308);
			match(ASSIGN);
			setState(312);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,24,_ctx) ) {
			case 1:
				{
				setState(309);
				literal();
				}
				break;
			case 2:
				{
				setState(310);
				unaryExpression();
				}
				break;
			case 3:
				{
				setState(311);
				arrayLiteral();
				}
				break;
			}
			setState(315);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(314);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ParameterDeclarationContext extends ParserRuleContext {
		public TypeSpecifierContext typeSpecifier() {
			return getRuleContext(TypeSpecifierContext.class,0);
		}
		public VariableListContext variableList() {
			return getRuleContext(VariableListContext.class,0);
		}
		public TerminalNode IN_PARAM() { return getToken(KumirParser.IN_PARAM, 0); }
		public TerminalNode OUT_PARAM() { return getToken(KumirParser.OUT_PARAM, 0); }
		public TerminalNode INOUT_PARAM() { return getToken(KumirParser.INOUT_PARAM, 0); }
		public ParameterDeclarationContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_parameterDeclaration; }
	}

	public final ParameterDeclarationContext parameterDeclaration() throws RecognitionException {
		ParameterDeclarationContext _localctx = new ParameterDeclarationContext(_ctx, getState());
		enterRule(_localctx, 56, RULE_parameterDeclaration);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(318);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 240518168576L) != 0)) {
				{
				setState(317);
				_la = _input.LA(1);
				if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 240518168576L) != 0)) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			setState(320);
			typeSpecifier();
			setState(321);
			variableList();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ParameterListContext extends ParserRuleContext {
		public List<ParameterDeclarationContext> parameterDeclaration() {
			return getRuleContexts(ParameterDeclarationContext.class);
		}
		public ParameterDeclarationContext parameterDeclaration(int i) {
			return getRuleContext(ParameterDeclarationContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(KumirParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(KumirParser.COMMA, i);
		}
		public ParameterListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_parameterList; }
	}

	public final ParameterListContext parameterList() throws RecognitionException {
		ParameterListContext _localctx = new ParameterListContext(_ctx, getState());
		enterRule(_localctx, 58, RULE_parameterList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(323);
			parameterDeclaration();
			setState(328);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(324);
				match(COMMA);
				setState(325);
				parameterDeclaration();
				}
				}
				setState(330);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AlgorithmNameTokensContext extends ParserRuleContext {
		public List<TerminalNode> LPAREN() { return getTokens(KumirParser.LPAREN); }
		public TerminalNode LPAREN(int i) {
			return getToken(KumirParser.LPAREN, i);
		}
		public List<TerminalNode> ALG_BEGIN() { return getTokens(KumirParser.ALG_BEGIN); }
		public TerminalNode ALG_BEGIN(int i) {
			return getToken(KumirParser.ALG_BEGIN, i);
		}
		public List<TerminalNode> PRE_CONDITION() { return getTokens(KumirParser.PRE_CONDITION); }
		public TerminalNode PRE_CONDITION(int i) {
			return getToken(KumirParser.PRE_CONDITION, i);
		}
		public List<TerminalNode> POST_CONDITION() { return getTokens(KumirParser.POST_CONDITION); }
		public TerminalNode POST_CONDITION(int i) {
			return getToken(KumirParser.POST_CONDITION, i);
		}
		public List<TerminalNode> SEMICOLON() { return getTokens(KumirParser.SEMICOLON); }
		public TerminalNode SEMICOLON(int i) {
			return getToken(KumirParser.SEMICOLON, i);
		}
		public List<TerminalNode> EOF() { return getTokens(KumirParser.EOF); }
		public TerminalNode EOF(int i) {
			return getToken(KumirParser.EOF, i);
		}
		public AlgorithmNameTokensContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_algorithmNameTokens; }
	}

	public final AlgorithmNameTokensContext algorithmNameTokens() throws RecognitionException {
		AlgorithmNameTokensContext _localctx = new AlgorithmNameTokensContext(_ctx, getState());
		enterRule(_localctx, 60, RULE_algorithmNameTokens);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(332); 
			_errHandler.sync(this);
			_alt = 1;
			do {
				switch (_alt) {
				case 1:
					{
					{
					setState(331);
					_la = _input.LA(1);
					if ( _la <= 0 || (((((_la - -1)) & ~0x3f) == 0 && ((1L << (_la - -1)) & 417L) != 0) || _la==LPAREN || _la==SEMICOLON) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				setState(334); 
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,28,_ctx);
			} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AlgorithmNameContext extends ParserRuleContext {
		public List<TerminalNode> ID() { return getTokens(KumirParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(KumirParser.ID, i);
		}
		public AlgorithmNameContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_algorithmName; }
	}

	public final AlgorithmNameContext algorithmName() throws RecognitionException {
		AlgorithmNameContext _localctx = new AlgorithmNameContext(_ctx, getState());
		enterRule(_localctx, 62, RULE_algorithmName);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(337); 
			_errHandler.sync(this);
			_alt = 1;
			do {
				switch (_alt) {
				case 1:
					{
					{
					setState(336);
					match(ID);
					}
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				setState(339); 
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,29,_ctx);
			} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AlgorithmHeaderContext extends ParserRuleContext {
		public TerminalNode ALG_HEADER() { return getToken(KumirParser.ALG_HEADER, 0); }
		public AlgorithmNameTokensContext algorithmNameTokens() {
			return getRuleContext(AlgorithmNameTokensContext.class,0);
		}
		public TypeSpecifierContext typeSpecifier() {
			return getRuleContext(TypeSpecifierContext.class,0);
		}
		public TerminalNode LPAREN() { return getToken(KumirParser.LPAREN, 0); }
		public TerminalNode RPAREN() { return getToken(KumirParser.RPAREN, 0); }
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public ParameterListContext parameterList() {
			return getRuleContext(ParameterListContext.class,0);
		}
		public AlgorithmHeaderContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_algorithmHeader; }
	}

	public final AlgorithmHeaderContext algorithmHeader() throws RecognitionException {
		AlgorithmHeaderContext _localctx = new AlgorithmHeaderContext(_ctx, getState());
		enterRule(_localctx, 64, RULE_algorithmHeader);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(341);
			match(ALG_HEADER);
			setState(343);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,30,_ctx) ) {
			case 1:
				{
				setState(342);
				typeSpecifier();
				}
				break;
			}
			setState(345);
			algorithmNameTokens();
			setState(351);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==LPAREN) {
				{
				setState(346);
				match(LPAREN);
				setState(348);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 17996497085792256L) != 0)) {
					{
					setState(347);
					parameterList();
					}
				}

				setState(350);
				match(RPAREN);
				}
			}

			setState(354);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(353);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PreConditionContext extends ParserRuleContext {
		public TerminalNode PRE_CONDITION() { return getToken(KumirParser.PRE_CONDITION, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public PreConditionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_preCondition; }
	}

	public final PreConditionContext preCondition() throws RecognitionException {
		PreConditionContext _localctx = new PreConditionContext(_ctx, getState());
		enterRule(_localctx, 66, RULE_preCondition);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(356);
			match(PRE_CONDITION);
			setState(357);
			expression();
			setState(359);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(358);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PostConditionContext extends ParserRuleContext {
		public TerminalNode POST_CONDITION() { return getToken(KumirParser.POST_CONDITION, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public PostConditionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_postCondition; }
	}

	public final PostConditionContext postCondition() throws RecognitionException {
		PostConditionContext _localctx = new PostConditionContext(_ctx, getState());
		enterRule(_localctx, 68, RULE_postCondition);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(361);
			match(POST_CONDITION);
			setState(362);
			expression();
			setState(364);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(363);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AlgorithmBodyContext extends ParserRuleContext {
		public StatementSequenceContext statementSequence() {
			return getRuleContext(StatementSequenceContext.class,0);
		}
		public AlgorithmBodyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_algorithmBody; }
	}

	public final AlgorithmBodyContext algorithmBody() throws RecognitionException {
		AlgorithmBodyContext _localctx = new AlgorithmBodyContext(_ctx, getState());
		enterRule(_localctx, 70, RULE_algorithmBody);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(366);
			statementSequence();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class StatementSequenceContext extends ParserRuleContext {
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public StatementSequenceContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statementSequence; }
	}

	public final StatementSequenceContext statementSequence() throws RecognitionException {
		StatementSequenceContext _localctx = new StatementSequenceContext(_ctx, getState());
		enterRule(_localctx, 72, RULE_statementSequence);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(371);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & -17860605963520L) != 0) || ((((_la - 64)) & ~0x3f) == 0 && ((1L << (_la - 64)) & 1044660615L) != 0)) {
				{
				{
				setState(368);
				statement();
				}
				}
				setState(373);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LvalueContext extends ParserRuleContext {
		public QualifiedIdentifierContext qualifiedIdentifier() {
			return getRuleContext(QualifiedIdentifierContext.class,0);
		}
		public TerminalNode LBRACK() { return getToken(KumirParser.LBRACK, 0); }
		public IndexListContext indexList() {
			return getRuleContext(IndexListContext.class,0);
		}
		public TerminalNode RBRACK() { return getToken(KumirParser.RBRACK, 0); }
		public TerminalNode RETURN_VALUE() { return getToken(KumirParser.RETURN_VALUE, 0); }
		public LvalueContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lvalue; }
	}

	public final LvalueContext lvalue() throws RecognitionException {
		LvalueContext _localctx = new LvalueContext(_ctx, getState());
		enterRule(_localctx, 74, RULE_lvalue);
		int _la;
		try {
			setState(382);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case ID:
				enterOuterAlt(_localctx, 1);
				{
				setState(374);
				qualifiedIdentifier();
				setState(379);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==LBRACK) {
					{
					setState(375);
					match(LBRACK);
					setState(376);
					indexList();
					setState(377);
					match(RBRACK);
					}
				}

				}
				break;
			case RETURN_VALUE:
				enterOuterAlt(_localctx, 2);
				{
				setState(381);
				match(RETURN_VALUE);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AssignmentStatementContext extends ParserRuleContext {
		public LvalueContext lvalue() {
			return getRuleContext(LvalueContext.class,0);
		}
		public TerminalNode ASSIGN() { return getToken(KumirParser.ASSIGN, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public AssignmentStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_assignmentStatement; }
	}

	public final AssignmentStatementContext assignmentStatement() throws RecognitionException {
		AssignmentStatementContext _localctx = new AssignmentStatementContext(_ctx, getState());
		enterRule(_localctx, 76, RULE_assignmentStatement);
		try {
			setState(389);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,39,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(384);
				lvalue();
				setState(385);
				match(ASSIGN);
				setState(386);
				expression();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(388);
				expression();
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IoArgumentContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public List<TerminalNode> COLON() { return getTokens(KumirParser.COLON); }
		public TerminalNode COLON(int i) {
			return getToken(KumirParser.COLON, i);
		}
		public TerminalNode NEWLINE_CONST() { return getToken(KumirParser.NEWLINE_CONST, 0); }
		public IoArgumentContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ioArgument; }
	}

	public final IoArgumentContext ioArgument() throws RecognitionException {
		IoArgumentContext _localctx = new IoArgumentContext(_ctx, getState());
		enterRule(_localctx, 78, RULE_ioArgument);
		int _la;
		try {
			setState(401);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,42,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(391);
				expression();
				setState(398);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==COLON) {
					{
					setState(392);
					match(COLON);
					setState(393);
					expression();
					setState(396);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==COLON) {
						{
						setState(394);
						match(COLON);
						setState(395);
						expression();
						}
					}

					}
				}

				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(400);
				match(NEWLINE_CONST);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IoArgumentListContext extends ParserRuleContext {
		public List<IoArgumentContext> ioArgument() {
			return getRuleContexts(IoArgumentContext.class);
		}
		public IoArgumentContext ioArgument(int i) {
			return getRuleContext(IoArgumentContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(KumirParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(KumirParser.COMMA, i);
		}
		public IoArgumentListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ioArgumentList; }
	}

	public final IoArgumentListContext ioArgumentList() throws RecognitionException {
		IoArgumentListContext _localctx = new IoArgumentListContext(_ctx, getState());
		enterRule(_localctx, 80, RULE_ioArgumentList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(403);
			ioArgument();
			setState(408);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(404);
				match(COMMA);
				setState(405);
				ioArgument();
				}
				}
				setState(410);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IoStatementContext extends ParserRuleContext {
		public IoArgumentListContext ioArgumentList() {
			return getRuleContext(IoArgumentListContext.class,0);
		}
		public TerminalNode INPUT() { return getToken(KumirParser.INPUT, 0); }
		public TerminalNode OUTPUT() { return getToken(KumirParser.OUTPUT, 0); }
		public IoStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ioStatement; }
	}

	public final IoStatementContext ioStatement() throws RecognitionException {
		IoStatementContext _localctx = new IoStatementContext(_ctx, getState());
		enterRule(_localctx, 82, RULE_ioStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(411);
			_la = _input.LA(1);
			if ( !(_la==INPUT || _la==OUTPUT) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			setState(412);
			ioArgumentList();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IfStatementContext extends ParserRuleContext {
		public TerminalNode IF() { return getToken(KumirParser.IF, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode THEN() { return getToken(KumirParser.THEN, 0); }
		public List<StatementSequenceContext> statementSequence() {
			return getRuleContexts(StatementSequenceContext.class);
		}
		public StatementSequenceContext statementSequence(int i) {
			return getRuleContext(StatementSequenceContext.class,i);
		}
		public TerminalNode FI() { return getToken(KumirParser.FI, 0); }
		public TerminalNode ELSE() { return getToken(KumirParser.ELSE, 0); }
		public IfStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ifStatement; }
	}

	public final IfStatementContext ifStatement() throws RecognitionException {
		IfStatementContext _localctx = new IfStatementContext(_ctx, getState());
		enterRule(_localctx, 84, RULE_ifStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(414);
			match(IF);
			setState(415);
			expression();
			setState(416);
			match(THEN);
			setState(417);
			statementSequence();
			setState(420);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ELSE) {
				{
				setState(418);
				match(ELSE);
				setState(419);
				statementSequence();
				}
			}

			setState(422);
			match(FI);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class CaseBlockContext extends ParserRuleContext {
		public TerminalNode CASE() { return getToken(KumirParser.CASE, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode COLON() { return getToken(KumirParser.COLON, 0); }
		public StatementSequenceContext statementSequence() {
			return getRuleContext(StatementSequenceContext.class,0);
		}
		public CaseBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_caseBlock; }
	}

	public final CaseBlockContext caseBlock() throws RecognitionException {
		CaseBlockContext _localctx = new CaseBlockContext(_ctx, getState());
		enterRule(_localctx, 86, RULE_caseBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(424);
			match(CASE);
			setState(425);
			expression();
			setState(426);
			match(COLON);
			setState(427);
			statementSequence();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class SwitchStatementContext extends ParserRuleContext {
		public TerminalNode SWITCH() { return getToken(KumirParser.SWITCH, 0); }
		public TerminalNode FI() { return getToken(KumirParser.FI, 0); }
		public List<CaseBlockContext> caseBlock() {
			return getRuleContexts(CaseBlockContext.class);
		}
		public CaseBlockContext caseBlock(int i) {
			return getRuleContext(CaseBlockContext.class,i);
		}
		public TerminalNode ELSE() { return getToken(KumirParser.ELSE, 0); }
		public StatementSequenceContext statementSequence() {
			return getRuleContext(StatementSequenceContext.class,0);
		}
		public SwitchStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_switchStatement; }
	}

	public final SwitchStatementContext switchStatement() throws RecognitionException {
		SwitchStatementContext _localctx = new SwitchStatementContext(_ctx, getState());
		enterRule(_localctx, 88, RULE_switchStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(429);
			match(SWITCH);
			setState(431); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(430);
				caseBlock();
				}
				}
				setState(433); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==CASE );
			setState(437);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ELSE) {
				{
				setState(435);
				match(ELSE);
				setState(436);
				statementSequence();
				}
			}

			setState(439);
			match(FI);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class EndLoopConditionContext extends ParserRuleContext {
		public TerminalNode ENDLOOP_COND() { return getToken(KumirParser.ENDLOOP_COND, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public EndLoopConditionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_endLoopCondition; }
	}

	public final EndLoopConditionContext endLoopCondition() throws RecognitionException {
		EndLoopConditionContext _localctx = new EndLoopConditionContext(_ctx, getState());
		enterRule(_localctx, 90, RULE_endLoopCondition);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(441);
			match(ENDLOOP_COND);
			setState(442);
			expression();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LoopSpecifierContext extends ParserRuleContext {
		public TerminalNode FOR() { return getToken(KumirParser.FOR, 0); }
		public TerminalNode ID() { return getToken(KumirParser.ID, 0); }
		public TerminalNode FROM() { return getToken(KumirParser.FROM, 0); }
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode TO() { return getToken(KumirParser.TO, 0); }
		public TerminalNode STEP() { return getToken(KumirParser.STEP, 0); }
		public TerminalNode WHILE() { return getToken(KumirParser.WHILE, 0); }
		public TerminalNode TIMES() { return getToken(KumirParser.TIMES, 0); }
		public LoopSpecifierContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_loopSpecifier; }
	}

	public final LoopSpecifierContext loopSpecifier() throws RecognitionException {
		LoopSpecifierContext _localctx = new LoopSpecifierContext(_ctx, getState());
		enterRule(_localctx, 92, RULE_loopSpecifier);
		int _la;
		try {
			setState(459);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case FOR:
				enterOuterAlt(_localctx, 1);
				{
				setState(444);
				match(FOR);
				setState(445);
				match(ID);
				setState(446);
				match(FROM);
				setState(447);
				expression();
				setState(448);
				match(TO);
				setState(449);
				expression();
				setState(452);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==STEP) {
					{
					setState(450);
					match(STEP);
					setState(451);
					expression();
					}
				}

				}
				break;
			case WHILE:
				enterOuterAlt(_localctx, 2);
				{
				setState(454);
				match(WHILE);
				setState(455);
				expression();
				}
				break;
			case NEWLINE_CONST:
			case NOT:
			case RETURN_VALUE:
			case TRUE:
			case FALSE:
			case PROZRACHNIY:
			case BELIY:
			case CHERNIY:
			case SERIY:
			case FIOLETOVIY:
			case SINIY:
			case GOLUBOY:
			case ZELENIY:
			case ZHELTIY:
			case ORANZHEVIY:
			case KRASNIY:
			case PLUS:
			case MINUS:
			case LPAREN:
			case LBRACE:
			case CHAR_LITERAL:
			case STRING:
			case REAL:
			case INTEGER:
			case ID:
				enterOuterAlt(_localctx, 3);
				{
				setState(456);
				expression();
				setState(457);
				match(TIMES);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LoopStatementContext extends ParserRuleContext {
		public TerminalNode LOOP() { return getToken(KumirParser.LOOP, 0); }
		public StatementSequenceContext statementSequence() {
			return getRuleContext(StatementSequenceContext.class,0);
		}
		public TerminalNode ENDLOOP() { return getToken(KumirParser.ENDLOOP, 0); }
		public EndLoopConditionContext endLoopCondition() {
			return getRuleContext(EndLoopConditionContext.class,0);
		}
		public LoopSpecifierContext loopSpecifier() {
			return getRuleContext(LoopSpecifierContext.class,0);
		}
		public LoopStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_loopStatement; }
	}

	public final LoopStatementContext loopStatement() throws RecognitionException {
		LoopStatementContext _localctx = new LoopStatementContext(_ctx, getState());
		enterRule(_localctx, 94, RULE_loopStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(461);
			match(LOOP);
			setState(463);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,49,_ctx) ) {
			case 1:
				{
				setState(462);
				loopSpecifier();
				}
				break;
			}
			setState(465);
			statementSequence();
			setState(468);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case ENDLOOP:
				{
				setState(466);
				match(ENDLOOP);
				}
				break;
			case ENDLOOP_COND:
				{
				setState(467);
				endLoopCondition();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ExitStatementContext extends ParserRuleContext {
		public TerminalNode EXIT() { return getToken(KumirParser.EXIT, 0); }
		public ExitStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_exitStatement; }
	}

	public final ExitStatementContext exitStatement() throws RecognitionException {
		ExitStatementContext _localctx = new ExitStatementContext(_ctx, getState());
		enterRule(_localctx, 96, RULE_exitStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(470);
			match(EXIT);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PauseStatementContext extends ParserRuleContext {
		public TerminalNode PAUSE() { return getToken(KumirParser.PAUSE, 0); }
		public PauseStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_pauseStatement; }
	}

	public final PauseStatementContext pauseStatement() throws RecognitionException {
		PauseStatementContext _localctx = new PauseStatementContext(_ctx, getState());
		enterRule(_localctx, 98, RULE_pauseStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(472);
			match(PAUSE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class StopStatementContext extends ParserRuleContext {
		public TerminalNode STOP() { return getToken(KumirParser.STOP, 0); }
		public StopStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_stopStatement; }
	}

	public final StopStatementContext stopStatement() throws RecognitionException {
		StopStatementContext _localctx = new StopStatementContext(_ctx, getState());
		enterRule(_localctx, 100, RULE_stopStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(474);
			match(STOP);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AssertionStatementContext extends ParserRuleContext {
		public TerminalNode ASSERTION() { return getToken(KumirParser.ASSERTION, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public AssertionStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_assertionStatement; }
	}

	public final AssertionStatementContext assertionStatement() throws RecognitionException {
		AssertionStatementContext _localctx = new AssertionStatementContext(_ctx, getState());
		enterRule(_localctx, 102, RULE_assertionStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(476);
			match(ASSERTION);
			setState(477);
			expression();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ProcedureCallStatementContext extends ParserRuleContext {
		public QualifiedIdentifierContext qualifiedIdentifier() {
			return getRuleContext(QualifiedIdentifierContext.class,0);
		}
		public TerminalNode LPAREN() { return getToken(KumirParser.LPAREN, 0); }
		public TerminalNode RPAREN() { return getToken(KumirParser.RPAREN, 0); }
		public ArgumentListContext argumentList() {
			return getRuleContext(ArgumentListContext.class,0);
		}
		public ProcedureCallStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_procedureCallStatement; }
	}

	public final ProcedureCallStatementContext procedureCallStatement() throws RecognitionException {
		ProcedureCallStatementContext _localctx = new ProcedureCallStatementContext(_ctx, getState());
		enterRule(_localctx, 104, RULE_procedureCallStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(479);
			qualifiedIdentifier();
			setState(485);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==LPAREN) {
				{
				setState(480);
				match(LPAREN);
				setState(482);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (((((_la - 31)) & ~0x3f) == 0 && ((1L << (_la - 31)) & 8937537565251076227L) != 0)) {
					{
					setState(481);
					argumentList();
					}
				}

				setState(484);
				match(RPAREN);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class StatementContext extends ParserRuleContext {
		public VariableDeclarationContext variableDeclaration() {
			return getRuleContext(VariableDeclarationContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public AssignmentStatementContext assignmentStatement() {
			return getRuleContext(AssignmentStatementContext.class,0);
		}
		public IoStatementContext ioStatement() {
			return getRuleContext(IoStatementContext.class,0);
		}
		public IfStatementContext ifStatement() {
			return getRuleContext(IfStatementContext.class,0);
		}
		public SwitchStatementContext switchStatement() {
			return getRuleContext(SwitchStatementContext.class,0);
		}
		public LoopStatementContext loopStatement() {
			return getRuleContext(LoopStatementContext.class,0);
		}
		public ExitStatementContext exitStatement() {
			return getRuleContext(ExitStatementContext.class,0);
		}
		public PauseStatementContext pauseStatement() {
			return getRuleContext(PauseStatementContext.class,0);
		}
		public StopStatementContext stopStatement() {
			return getRuleContext(StopStatementContext.class,0);
		}
		public AssertionStatementContext assertionStatement() {
			return getRuleContext(AssertionStatementContext.class,0);
		}
		public StatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statement; }
	}

	public final StatementContext statement() throws RecognitionException {
		StatementContext _localctx = new StatementContext(_ctx, getState());
		enterRule(_localctx, 106, RULE_statement);
		try {
			setState(528);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case INTEGER_TYPE:
			case REAL_TYPE:
			case BOOLEAN_TYPE:
			case CHAR_TYPE:
			case STRING_TYPE:
			case KOMPL_TYPE:
			case COLOR_TYPE:
			case SCANCODE_TYPE:
			case FILE_TYPE:
			case INTEGER_ARRAY_TYPE:
			case REAL_ARRAY_TYPE:
			case CHAR_ARRAY_TYPE:
			case STRING_ARRAY_TYPE:
			case BOOLEAN_ARRAY_TYPE:
				enterOuterAlt(_localctx, 1);
				{
				setState(487);
				variableDeclaration();
				setState(489);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,53,_ctx) ) {
				case 1:
					{
					setState(488);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case NEWLINE_CONST:
			case NOT:
			case RETURN_VALUE:
			case TRUE:
			case FALSE:
			case PROZRACHNIY:
			case BELIY:
			case CHERNIY:
			case SERIY:
			case FIOLETOVIY:
			case SINIY:
			case GOLUBOY:
			case ZELENIY:
			case ZHELTIY:
			case ORANZHEVIY:
			case KRASNIY:
			case PLUS:
			case MINUS:
			case LPAREN:
			case LBRACE:
			case CHAR_LITERAL:
			case STRING:
			case REAL:
			case INTEGER:
			case ID:
				enterOuterAlt(_localctx, 2);
				{
				setState(491);
				assignmentStatement();
				setState(493);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,54,_ctx) ) {
				case 1:
					{
					setState(492);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case INPUT:
			case OUTPUT:
				enterOuterAlt(_localctx, 3);
				{
				setState(495);
				ioStatement();
				setState(497);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,55,_ctx) ) {
				case 1:
					{
					setState(496);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case IF:
				enterOuterAlt(_localctx, 4);
				{
				setState(499);
				ifStatement();
				setState(501);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,56,_ctx) ) {
				case 1:
					{
					setState(500);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case SWITCH:
				enterOuterAlt(_localctx, 5);
				{
				setState(503);
				switchStatement();
				setState(505);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,57,_ctx) ) {
				case 1:
					{
					setState(504);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case LOOP:
				enterOuterAlt(_localctx, 6);
				{
				setState(507);
				loopStatement();
				setState(509);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,58,_ctx) ) {
				case 1:
					{
					setState(508);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case EXIT:
				enterOuterAlt(_localctx, 7);
				{
				setState(511);
				exitStatement();
				setState(513);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,59,_ctx) ) {
				case 1:
					{
					setState(512);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case PAUSE:
				enterOuterAlt(_localctx, 8);
				{
				setState(515);
				pauseStatement();
				setState(517);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,60,_ctx) ) {
				case 1:
					{
					setState(516);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case STOP:
				enterOuterAlt(_localctx, 9);
				{
				setState(519);
				stopStatement();
				setState(521);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,61,_ctx) ) {
				case 1:
					{
					setState(520);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case ASSERTION:
				enterOuterAlt(_localctx, 10);
				{
				setState(523);
				assertionStatement();
				setState(525);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,62,_ctx) ) {
				case 1:
					{
					setState(524);
					match(SEMICOLON);
					}
					break;
				}
				}
				break;
			case SEMICOLON:
				enterOuterAlt(_localctx, 11);
				{
				setState(527);
				match(SEMICOLON);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AlgorithmDefinitionContext extends ParserRuleContext {
		public AlgorithmHeaderContext algorithmHeader() {
			return getRuleContext(AlgorithmHeaderContext.class,0);
		}
		public TerminalNode ALG_BEGIN() { return getToken(KumirParser.ALG_BEGIN, 0); }
		public AlgorithmBodyContext algorithmBody() {
			return getRuleContext(AlgorithmBodyContext.class,0);
		}
		public TerminalNode ALG_END() { return getToken(KumirParser.ALG_END, 0); }
		public List<PreConditionContext> preCondition() {
			return getRuleContexts(PreConditionContext.class);
		}
		public PreConditionContext preCondition(int i) {
			return getRuleContext(PreConditionContext.class,i);
		}
		public List<PostConditionContext> postCondition() {
			return getRuleContexts(PostConditionContext.class);
		}
		public PostConditionContext postCondition(int i) {
			return getRuleContext(PostConditionContext.class,i);
		}
		public List<VariableDeclarationContext> variableDeclaration() {
			return getRuleContexts(VariableDeclarationContext.class);
		}
		public VariableDeclarationContext variableDeclaration(int i) {
			return getRuleContext(VariableDeclarationContext.class,i);
		}
		public AlgorithmNameContext algorithmName() {
			return getRuleContext(AlgorithmNameContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public AlgorithmDefinitionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_algorithmDefinition; }
	}

	public final AlgorithmDefinitionContext algorithmDefinition() throws RecognitionException {
		AlgorithmDefinitionContext _localctx = new AlgorithmDefinitionContext(_ctx, getState());
		enterRule(_localctx, 108, RULE_algorithmDefinition);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(530);
			algorithmHeader();
			setState(536);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 17996256567623872L) != 0)) {
				{
				setState(534);
				_errHandler.sync(this);
				switch (_input.LA(1)) {
				case PRE_CONDITION:
					{
					setState(531);
					preCondition();
					}
					break;
				case POST_CONDITION:
					{
					setState(532);
					postCondition();
					}
					break;
				case INTEGER_TYPE:
				case REAL_TYPE:
				case BOOLEAN_TYPE:
				case CHAR_TYPE:
				case STRING_TYPE:
				case KOMPL_TYPE:
				case COLOR_TYPE:
				case SCANCODE_TYPE:
				case FILE_TYPE:
				case INTEGER_ARRAY_TYPE:
				case REAL_ARRAY_TYPE:
				case CHAR_ARRAY_TYPE:
				case STRING_ARRAY_TYPE:
				case BOOLEAN_ARRAY_TYPE:
					{
					setState(533);
					variableDeclaration();
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				}
				setState(538);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(539);
			match(ALG_BEGIN);
			setState(540);
			algorithmBody();
			setState(541);
			match(ALG_END);
			setState(543);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,66,_ctx) ) {
			case 1:
				{
				setState(542);
				algorithmName();
				}
				break;
			}
			setState(546);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(545);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ModuleNameContext extends ParserRuleContext {
		public QualifiedIdentifierContext qualifiedIdentifier() {
			return getRuleContext(QualifiedIdentifierContext.class,0);
		}
		public TerminalNode STRING() { return getToken(KumirParser.STRING, 0); }
		public ModuleNameContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_moduleName; }
	}

	public final ModuleNameContext moduleName() throws RecognitionException {
		ModuleNameContext _localctx = new ModuleNameContext(_ctx, getState());
		enterRule(_localctx, 110, RULE_moduleName);
		try {
			setState(550);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case ID:
				enterOuterAlt(_localctx, 1);
				{
				setState(548);
				qualifiedIdentifier();
				}
				break;
			case STRING:
				enterOuterAlt(_localctx, 2);
				{
				setState(549);
				match(STRING);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ImportStatementContext extends ParserRuleContext {
		public TerminalNode IMPORT() { return getToken(KumirParser.IMPORT, 0); }
		public ModuleNameContext moduleName() {
			return getRuleContext(ModuleNameContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public ImportStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_importStatement; }
	}

	public final ImportStatementContext importStatement() throws RecognitionException {
		ImportStatementContext _localctx = new ImportStatementContext(_ctx, getState());
		enterRule(_localctx, 112, RULE_importStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(552);
			match(IMPORT);
			setState(553);
			moduleName();
			setState(555);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(554);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ProgramItemContext extends ParserRuleContext {
		public ImportStatementContext importStatement() {
			return getRuleContext(ImportStatementContext.class,0);
		}
		public GlobalDeclarationContext globalDeclaration() {
			return getRuleContext(GlobalDeclarationContext.class,0);
		}
		public GlobalAssignmentContext globalAssignment() {
			return getRuleContext(GlobalAssignmentContext.class,0);
		}
		public ProgramItemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_programItem; }
	}

	public final ProgramItemContext programItem() throws RecognitionException {
		ProgramItemContext _localctx = new ProgramItemContext(_ctx, getState());
		enterRule(_localctx, 114, RULE_programItem);
		try {
			setState(560);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case IMPORT:
				enterOuterAlt(_localctx, 1);
				{
				setState(557);
				importStatement();
				}
				break;
			case INTEGER_TYPE:
			case REAL_TYPE:
			case BOOLEAN_TYPE:
			case CHAR_TYPE:
			case STRING_TYPE:
			case KOMPL_TYPE:
			case COLOR_TYPE:
			case SCANCODE_TYPE:
			case FILE_TYPE:
			case INTEGER_ARRAY_TYPE:
			case REAL_ARRAY_TYPE:
			case CHAR_ARRAY_TYPE:
			case STRING_ARRAY_TYPE:
			case BOOLEAN_ARRAY_TYPE:
				enterOuterAlt(_localctx, 2);
				{
				setState(558);
				globalDeclaration();
				}
				break;
			case ID:
				enterOuterAlt(_localctx, 3);
				{
				setState(559);
				globalAssignment();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ModuleHeaderContext extends ParserRuleContext {
		public TerminalNode MODULE() { return getToken(KumirParser.MODULE, 0); }
		public QualifiedIdentifierContext qualifiedIdentifier() {
			return getRuleContext(QualifiedIdentifierContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public ModuleHeaderContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_moduleHeader; }
	}

	public final ModuleHeaderContext moduleHeader() throws RecognitionException {
		ModuleHeaderContext _localctx = new ModuleHeaderContext(_ctx, getState());
		enterRule(_localctx, 116, RULE_moduleHeader);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(562);
			match(MODULE);
			setState(563);
			qualifiedIdentifier();
			setState(565);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==SEMICOLON) {
				{
				setState(564);
				match(SEMICOLON);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ModuleBodyContext extends ParserRuleContext {
		public List<ProgramItemContext> programItem() {
			return getRuleContexts(ProgramItemContext.class);
		}
		public ProgramItemContext programItem(int i) {
			return getRuleContext(ProgramItemContext.class,i);
		}
		public List<AlgorithmDefinitionContext> algorithmDefinition() {
			return getRuleContexts(AlgorithmDefinitionContext.class);
		}
		public AlgorithmDefinitionContext algorithmDefinition(int i) {
			return getRuleContext(AlgorithmDefinitionContext.class,i);
		}
		public ModuleBodyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_moduleBody; }
	}

	public final ModuleBodyContext moduleBody() throws RecognitionException {
		ModuleBodyContext _localctx = new ModuleBodyContext(_ctx, getState());
		enterRule(_localctx, 118, RULE_moduleBody);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(571);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 17996256584400904L) != 0) || _la==ID) {
				{
				setState(569);
				_errHandler.sync(this);
				switch (_input.LA(1)) {
				case IMPORT:
				case INTEGER_TYPE:
				case REAL_TYPE:
				case BOOLEAN_TYPE:
				case CHAR_TYPE:
				case STRING_TYPE:
				case KOMPL_TYPE:
				case COLOR_TYPE:
				case SCANCODE_TYPE:
				case FILE_TYPE:
				case INTEGER_ARRAY_TYPE:
				case REAL_ARRAY_TYPE:
				case CHAR_ARRAY_TYPE:
				case STRING_ARRAY_TYPE:
				case BOOLEAN_ARRAY_TYPE:
				case ID:
					{
					setState(567);
					programItem();
					}
					break;
				case ALG_HEADER:
					{
					setState(568);
					algorithmDefinition();
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				}
				setState(573);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ImplicitModuleBodyContext extends ParserRuleContext {
		public List<ProgramItemContext> programItem() {
			return getRuleContexts(ProgramItemContext.class);
		}
		public ProgramItemContext programItem(int i) {
			return getRuleContext(ProgramItemContext.class,i);
		}
		public List<AlgorithmDefinitionContext> algorithmDefinition() {
			return getRuleContexts(AlgorithmDefinitionContext.class);
		}
		public AlgorithmDefinitionContext algorithmDefinition(int i) {
			return getRuleContext(AlgorithmDefinitionContext.class,i);
		}
		public ImplicitModuleBodyContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_implicitModuleBody; }
	}

	public final ImplicitModuleBodyContext implicitModuleBody() throws RecognitionException {
		ImplicitModuleBodyContext _localctx = new ImplicitModuleBodyContext(_ctx, getState());
		enterRule(_localctx, 120, RULE_implicitModuleBody);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(576); 
			_errHandler.sync(this);
			_alt = 1;
			do {
				switch (_alt) {
				case 1:
					{
					setState(576);
					_errHandler.sync(this);
					switch (_input.LA(1)) {
					case IMPORT:
					case INTEGER_TYPE:
					case REAL_TYPE:
					case BOOLEAN_TYPE:
					case CHAR_TYPE:
					case STRING_TYPE:
					case KOMPL_TYPE:
					case COLOR_TYPE:
					case SCANCODE_TYPE:
					case FILE_TYPE:
					case INTEGER_ARRAY_TYPE:
					case REAL_ARRAY_TYPE:
					case CHAR_ARRAY_TYPE:
					case STRING_ARRAY_TYPE:
					case BOOLEAN_ARRAY_TYPE:
					case ID:
						{
						setState(574);
						programItem();
						}
						break;
					case ALG_HEADER:
						{
						setState(575);
						algorithmDefinition();
						}
						break;
					default:
						throw new NoViableAltException(this);
					}
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				setState(578); 
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,75,_ctx);
			} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ModuleDefinitionContext extends ParserRuleContext {
		public ModuleHeaderContext moduleHeader() {
			return getRuleContext(ModuleHeaderContext.class,0);
		}
		public ModuleBodyContext moduleBody() {
			return getRuleContext(ModuleBodyContext.class,0);
		}
		public TerminalNode ENDMODULE() { return getToken(KumirParser.ENDMODULE, 0); }
		public QualifiedIdentifierContext qualifiedIdentifier() {
			return getRuleContext(QualifiedIdentifierContext.class,0);
		}
		public TerminalNode SEMICOLON() { return getToken(KumirParser.SEMICOLON, 0); }
		public ImplicitModuleBodyContext implicitModuleBody() {
			return getRuleContext(ImplicitModuleBodyContext.class,0);
		}
		public ModuleDefinitionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_moduleDefinition; }
	}

	public final ModuleDefinitionContext moduleDefinition() throws RecognitionException {
		ModuleDefinitionContext _localctx = new ModuleDefinitionContext(_ctx, getState());
		enterRule(_localctx, 122, RULE_moduleDefinition);
		int _la;
		try {
			setState(590);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case MODULE:
				enterOuterAlt(_localctx, 1);
				{
				setState(580);
				moduleHeader();
				setState(581);
				moduleBody();
				setState(582);
				match(ENDMODULE);
				setState(584);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,76,_ctx) ) {
				case 1:
					{
					setState(583);
					qualifiedIdentifier();
					}
					break;
				}
				setState(587);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SEMICOLON) {
					{
					setState(586);
					match(SEMICOLON);
					}
				}

				}
				break;
			case ALG_HEADER:
			case IMPORT:
			case INTEGER_TYPE:
			case REAL_TYPE:
			case BOOLEAN_TYPE:
			case CHAR_TYPE:
			case STRING_TYPE:
			case KOMPL_TYPE:
			case COLOR_TYPE:
			case SCANCODE_TYPE:
			case FILE_TYPE:
			case INTEGER_ARRAY_TYPE:
			case REAL_ARRAY_TYPE:
			case CHAR_ARRAY_TYPE:
			case STRING_ARRAY_TYPE:
			case BOOLEAN_ARRAY_TYPE:
			case ID:
				enterOuterAlt(_localctx, 2);
				{
				setState(589);
				implicitModuleBody();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ProgramContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(KumirParser.EOF, 0); }
		public List<ProgramItemContext> programItem() {
			return getRuleContexts(ProgramItemContext.class);
		}
		public ProgramItemContext programItem(int i) {
			return getRuleContext(ProgramItemContext.class,i);
		}
		public List<ModuleDefinitionContext> moduleDefinition() {
			return getRuleContexts(ModuleDefinitionContext.class);
		}
		public ModuleDefinitionContext moduleDefinition(int i) {
			return getRuleContext(ModuleDefinitionContext.class,i);
		}
		public ProgramContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_program; }
	}

	public final ProgramContext program() throws RecognitionException {
		ProgramContext _localctx = new ProgramContext(_ctx, getState());
		enterRule(_localctx, 124, RULE_program);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(595);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,79,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(592);
					programItem();
					}
					} 
				}
				setState(597);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,79,_ctx);
			}
			setState(599); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(598);
				moduleDefinition();
				}
				}
				setState(601); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & 17996256584400906L) != 0) || _la==ID );
			setState(603);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static final String _serializedATN =
		"\u0004\u0001`\u025e\u0002\u0000\u0007\u0000\u0002\u0001\u0007\u0001\u0002"+
		"\u0002\u0007\u0002\u0002\u0003\u0007\u0003\u0002\u0004\u0007\u0004\u0002"+
		"\u0005\u0007\u0005\u0002\u0006\u0007\u0006\u0002\u0007\u0007\u0007\u0002"+
		"\b\u0007\b\u0002\t\u0007\t\u0002\n\u0007\n\u0002\u000b\u0007\u000b\u0002"+
		"\f\u0007\f\u0002\r\u0007\r\u0002\u000e\u0007\u000e\u0002\u000f\u0007\u000f"+
		"\u0002\u0010\u0007\u0010\u0002\u0011\u0007\u0011\u0002\u0012\u0007\u0012"+
		"\u0002\u0013\u0007\u0013\u0002\u0014\u0007\u0014\u0002\u0015\u0007\u0015"+
		"\u0002\u0016\u0007\u0016\u0002\u0017\u0007\u0017\u0002\u0018\u0007\u0018"+
		"\u0002\u0019\u0007\u0019\u0002\u001a\u0007\u001a\u0002\u001b\u0007\u001b"+
		"\u0002\u001c\u0007\u001c\u0002\u001d\u0007\u001d\u0002\u001e\u0007\u001e"+
		"\u0002\u001f\u0007\u001f\u0002 \u0007 \u0002!\u0007!\u0002\"\u0007\"\u0002"+
		"#\u0007#\u0002$\u0007$\u0002%\u0007%\u0002&\u0007&\u0002\'\u0007\'\u0002"+
		"(\u0007(\u0002)\u0007)\u0002*\u0007*\u0002+\u0007+\u0002,\u0007,\u0002"+
		"-\u0007-\u0002.\u0007.\u0002/\u0007/\u00020\u00070\u00021\u00071\u0002"+
		"2\u00072\u00023\u00073\u00024\u00074\u00025\u00075\u00026\u00076\u0002"+
		"7\u00077\u00028\u00078\u00029\u00079\u0002:\u0007:\u0002;\u0007;\u0002"+
		"<\u0007<\u0002=\u0007=\u0002>\u0007>\u0001\u0000\u0001\u0000\u0001\u0001"+
		"\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001"+
		"\u0001\u0001\u0003\u0001\u0089\b\u0001\u0001\u0002\u0001\u0002\u0001\u0003"+
		"\u0001\u0003\u0001\u0003\u0005\u0003\u0090\b\u0003\n\u0003\f\u0003\u0093"+
		"\t\u0003\u0001\u0004\u0001\u0004\u0003\u0004\u0097\b\u0004\u0001\u0004"+
		"\u0001\u0004\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005"+
		"\u0001\u0005\u0001\u0005\u0001\u0005\u0003\u0005\u00a3\b\u0005\u0001\u0006"+
		"\u0001\u0006\u0001\u0006\u0005\u0006\u00a8\b\u0006\n\u0006\f\u0006\u00ab"+
		"\t\u0006\u0001\u0007\u0001\u0007\u0001\u0007\u0005\u0007\u00b0\b\u0007"+
		"\n\u0007\f\u0007\u00b3\t\u0007\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b"+
		"\u0001\b\u0001\b\u0003\b\u00bc\b\b\u0001\b\u0005\b\u00bf\b\b\n\b\f\b\u00c2"+
		"\t\b\u0001\t\u0001\t\u0001\t\u0003\t\u00c7\b\t\u0001\n\u0001\n\u0001\n"+
		"\u0003\n\u00cc\b\n\u0001\u000b\u0001\u000b\u0001\u000b\u0005\u000b\u00d1"+
		"\b\u000b\n\u000b\f\u000b\u00d4\t\u000b\u0001\f\u0001\f\u0001\f\u0005\f"+
		"\u00d9\b\f\n\f\f\f\u00dc\t\f\u0001\r\u0001\r\u0001\r\u0005\r\u00e1\b\r"+
		"\n\r\f\r\u00e4\t\r\u0001\u000e\u0001\u000e\u0001\u000e\u0005\u000e\u00e9"+
		"\b\u000e\n\u000e\f\u000e\u00ec\t\u000e\u0001\u000f\u0001\u000f\u0001\u000f"+
		"\u0005\u000f\u00f1\b\u000f\n\u000f\f\u000f\u00f4\t\u000f\u0001\u0010\u0001"+
		"\u0010\u0001\u0010\u0005\u0010\u00f9\b\u0010\n\u0010\f\u0010\u00fc\t\u0010"+
		"\u0001\u0011\u0001\u0011\u0001\u0012\u0001\u0012\u0001\u0012\u0003\u0012"+
		"\u0103\b\u0012\u0001\u0012\u0003\u0012\u0106\b\u0012\u0001\u0013\u0001"+
		"\u0013\u0001\u0014\u0001\u0014\u0001\u0015\u0001\u0015\u0001\u0016\u0001"+
		"\u0016\u0001\u0016\u0001\u0016\u0001\u0017\u0001\u0017\u0001\u0017\u0001"+
		"\u0017\u0001\u0017\u0005\u0017\u0117\b\u0017\n\u0017\f\u0017\u011a\t\u0017"+
		"\u0001\u0017\u0001\u0017\u0003\u0017\u011e\b\u0017\u0001\u0017\u0001\u0017"+
		"\u0003\u0017\u0122\b\u0017\u0001\u0018\u0001\u0018\u0001\u0018\u0005\u0018"+
		"\u0127\b\u0018\n\u0018\f\u0018\u012a\t\u0018\u0001\u0019\u0001\u0019\u0001"+
		"\u0019\u0001\u001a\u0001\u001a\u0001\u001a\u0003\u001a\u0132\b\u001a\u0001"+
		"\u001b\u0001\u001b\u0001\u001b\u0001\u001b\u0001\u001b\u0003\u001b\u0139"+
		"\b\u001b\u0001\u001b\u0003\u001b\u013c\b\u001b\u0001\u001c\u0003\u001c"+
		"\u013f\b\u001c\u0001\u001c\u0001\u001c\u0001\u001c\u0001\u001d\u0001\u001d"+
		"\u0001\u001d\u0005\u001d\u0147\b\u001d\n\u001d\f\u001d\u014a\t\u001d\u0001"+
		"\u001e\u0004\u001e\u014d\b\u001e\u000b\u001e\f\u001e\u014e\u0001\u001f"+
		"\u0004\u001f\u0152\b\u001f\u000b\u001f\f\u001f\u0153\u0001 \u0001 \u0003"+
		" \u0158\b \u0001 \u0001 \u0001 \u0003 \u015d\b \u0001 \u0003 \u0160\b"+
		" \u0001 \u0003 \u0163\b \u0001!\u0001!\u0001!\u0003!\u0168\b!\u0001\""+
		"\u0001\"\u0001\"\u0003\"\u016d\b\"\u0001#\u0001#\u0001$\u0005$\u0172\b"+
		"$\n$\f$\u0175\t$\u0001%\u0001%\u0001%\u0001%\u0001%\u0003%\u017c\b%\u0001"+
		"%\u0003%\u017f\b%\u0001&\u0001&\u0001&\u0001&\u0001&\u0003&\u0186\b&\u0001"+
		"\'\u0001\'\u0001\'\u0001\'\u0001\'\u0003\'\u018d\b\'\u0003\'\u018f\b\'"+
		"\u0001\'\u0003\'\u0192\b\'\u0001(\u0001(\u0001(\u0005(\u0197\b(\n(\f("+
		"\u019a\t(\u0001)\u0001)\u0001)\u0001*\u0001*\u0001*\u0001*\u0001*\u0001"+
		"*\u0003*\u01a5\b*\u0001*\u0001*\u0001+\u0001+\u0001+\u0001+\u0001+\u0001"+
		",\u0001,\u0004,\u01b0\b,\u000b,\f,\u01b1\u0001,\u0001,\u0003,\u01b6\b"+
		",\u0001,\u0001,\u0001-\u0001-\u0001-\u0001.\u0001.\u0001.\u0001.\u0001"+
		".\u0001.\u0001.\u0001.\u0003.\u01c5\b.\u0001.\u0001.\u0001.\u0001.\u0001"+
		".\u0003.\u01cc\b.\u0001/\u0001/\u0003/\u01d0\b/\u0001/\u0001/\u0001/\u0003"+
		"/\u01d5\b/\u00010\u00010\u00011\u00011\u00012\u00012\u00013\u00013\u0001"+
		"3\u00014\u00014\u00014\u00034\u01e3\b4\u00014\u00034\u01e6\b4\u00015\u0001"+
		"5\u00035\u01ea\b5\u00015\u00015\u00035\u01ee\b5\u00015\u00015\u00035\u01f2"+
		"\b5\u00015\u00015\u00035\u01f6\b5\u00015\u00015\u00035\u01fa\b5\u0001"+
		"5\u00015\u00035\u01fe\b5\u00015\u00015\u00035\u0202\b5\u00015\u00015\u0003"+
		"5\u0206\b5\u00015\u00015\u00035\u020a\b5\u00015\u00015\u00035\u020e\b"+
		"5\u00015\u00035\u0211\b5\u00016\u00016\u00016\u00016\u00056\u0217\b6\n"+
		"6\f6\u021a\t6\u00016\u00016\u00016\u00016\u00036\u0220\b6\u00016\u0003"+
		"6\u0223\b6\u00017\u00017\u00037\u0227\b7\u00018\u00018\u00018\u00038\u022c"+
		"\b8\u00019\u00019\u00019\u00039\u0231\b9\u0001:\u0001:\u0001:\u0003:\u0236"+
		"\b:\u0001;\u0001;\u0005;\u023a\b;\n;\f;\u023d\t;\u0001<\u0001<\u0004<"+
		"\u0241\b<\u000b<\f<\u0242\u0001=\u0001=\u0001=\u0001=\u0003=\u0249\b="+
		"\u0001=\u0003=\u024c\b=\u0001=\u0003=\u024f\b=\u0001>\u0005>\u0252\b>"+
		"\n>\f>\u0255\t>\u0001>\u0004>\u0258\b>\u000b>\f>\u0259\u0001>\u0001>\u0001"+
		">\u0000\u0000?\u0000\u0002\u0004\u0006\b\n\f\u000e\u0010\u0012\u0014\u0016"+
		"\u0018\u001a\u001c\u001e \"$&(*,.02468:<>@BDFHJLNPRTVXZ\\^`bdfhjlnprt"+
		"vxz|\u0000\f\u0001\u00008B\u0002\u0000  GH\u0001\u0000IJ\u0001\u0000G"+
		"H\u0002\u0000DELM\u0002\u0000FFKK\u0001\u0000\'+\u0001\u0000-0\u0001\u0000"+
		"15\u0001\u0000#%\u0004\u0001\u0004\u0004\u0006\u0007NNVV\u0001\u0000\u0012"+
		"\u0013\u0286\u0000~\u0001\u0000\u0000\u0000\u0002\u0088\u0001\u0000\u0000"+
		"\u0000\u0004\u008a\u0001\u0000\u0000\u0000\u0006\u008c\u0001\u0000\u0000"+
		"\u0000\b\u0094\u0001\u0000\u0000\u0000\n\u00a2\u0001\u0000\u0000\u0000"+
		"\f\u00a4\u0001\u0000\u0000\u0000\u000e\u00ac\u0001\u0000\u0000\u0000\u0010"+
		"\u00b4\u0001\u0000\u0000\u0000\u0012\u00c6\u0001\u0000\u0000\u0000\u0014"+
		"\u00c8\u0001\u0000\u0000\u0000\u0016\u00cd\u0001\u0000\u0000\u0000\u0018"+
		"\u00d5\u0001\u0000\u0000\u0000\u001a\u00dd\u0001\u0000\u0000\u0000\u001c"+
		"\u00e5\u0001\u0000\u0000\u0000\u001e\u00ed\u0001\u0000\u0000\u0000 \u00f5"+
		"\u0001\u0000\u0000\u0000\"\u00fd\u0001\u0000\u0000\u0000$\u0105\u0001"+
		"\u0000\u0000\u0000&\u0107\u0001\u0000\u0000\u0000(\u0109\u0001\u0000\u0000"+
		"\u0000*\u010b\u0001\u0000\u0000\u0000,\u010d\u0001\u0000\u0000\u0000."+
		"\u0111\u0001\u0000\u0000\u00000\u0123\u0001\u0000\u0000\u00002\u012b\u0001"+
		"\u0000\u0000\u00004\u012e\u0001\u0000\u0000\u00006\u0133\u0001\u0000\u0000"+
		"\u00008\u013e\u0001\u0000\u0000\u0000:\u0143\u0001\u0000\u0000\u0000<"+
		"\u014c\u0001\u0000\u0000\u0000>\u0151\u0001\u0000\u0000\u0000@\u0155\u0001"+
		"\u0000\u0000\u0000B\u0164\u0001\u0000\u0000\u0000D\u0169\u0001\u0000\u0000"+
		"\u0000F\u016e\u0001\u0000\u0000\u0000H\u0173\u0001\u0000\u0000\u0000J"+
		"\u017e\u0001\u0000\u0000\u0000L\u0185\u0001\u0000\u0000\u0000N\u0191\u0001"+
		"\u0000\u0000\u0000P\u0193\u0001\u0000\u0000\u0000R\u019b\u0001\u0000\u0000"+
		"\u0000T\u019e\u0001\u0000\u0000\u0000V\u01a8\u0001\u0000\u0000\u0000X"+
		"\u01ad\u0001\u0000\u0000\u0000Z\u01b9\u0001\u0000\u0000\u0000\\\u01cb"+
		"\u0001\u0000\u0000\u0000^\u01cd\u0001\u0000\u0000\u0000`\u01d6\u0001\u0000"+
		"\u0000\u0000b\u01d8\u0001\u0000\u0000\u0000d\u01da\u0001\u0000\u0000\u0000"+
		"f\u01dc\u0001\u0000\u0000\u0000h\u01df\u0001\u0000\u0000\u0000j\u0210"+
		"\u0001\u0000\u0000\u0000l\u0212\u0001\u0000\u0000\u0000n\u0226\u0001\u0000"+
		"\u0000\u0000p\u0228\u0001\u0000\u0000\u0000r\u0230\u0001\u0000\u0000\u0000"+
		"t\u0232\u0001\u0000\u0000\u0000v\u023b\u0001\u0000\u0000\u0000x\u0240"+
		"\u0001\u0000\u0000\u0000z\u024e\u0001\u0000\u0000\u0000|\u0253\u0001\u0000"+
		"\u0000\u0000~\u007f\u0005]\u0000\u0000\u007f\u0001\u0001\u0000\u0000\u0000"+
		"\u0080\u0089\u0005\\\u0000\u0000\u0081\u0089\u0005[\u0000\u0000\u0082"+
		"\u0089\u0005Z\u0000\u0000\u0083\u0089\u0005Y\u0000\u0000\u0084\u0089\u0005"+
		"6\u0000\u0000\u0085\u0089\u00057\u0000\u0000\u0086\u0089\u0003\u0004\u0002"+
		"\u0000\u0087\u0089\u0005\u001f\u0000\u0000\u0088\u0080\u0001\u0000\u0000"+
		"\u0000\u0088\u0081\u0001\u0000\u0000\u0000\u0088\u0082\u0001\u0000\u0000"+
		"\u0000\u0088\u0083\u0001\u0000\u0000\u0000\u0088\u0084\u0001\u0000\u0000"+
		"\u0000\u0088\u0085\u0001\u0000\u0000\u0000\u0088\u0086\u0001\u0000\u0000"+
		"\u0000\u0088\u0087\u0001\u0000\u0000\u0000\u0089\u0003\u0001\u0000\u0000"+
		"\u0000\u008a\u008b\u0007\u0000\u0000\u0000\u008b\u0005\u0001\u0000\u0000"+
		"\u0000\u008c\u0091\u0003\"\u0011\u0000\u008d\u008e\u0005T\u0000\u0000"+
		"\u008e\u0090\u0003\"\u0011\u0000\u008f\u008d\u0001\u0000\u0000\u0000\u0090"+
		"\u0093\u0001\u0000\u0000\u0000\u0091\u008f\u0001\u0000\u0000\u0000\u0091"+
		"\u0092\u0001\u0000\u0000\u0000\u0092\u0007\u0001\u0000\u0000\u0000\u0093"+
		"\u0091\u0001\u0000\u0000\u0000\u0094\u0096\u0005R\u0000\u0000\u0095\u0097"+
		"\u0003\u0006\u0003\u0000\u0096\u0095\u0001\u0000\u0000\u0000\u0096\u0097"+
		"\u0001\u0000\u0000\u0000\u0097\u0098\u0001\u0000\u0000\u0000\u0098\u0099"+
		"\u0005S\u0000\u0000\u0099\t\u0001\u0000\u0000\u0000\u009a\u00a3\u0003"+
		"\u0002\u0001\u0000\u009b\u00a3\u0003\u0000\u0000\u0000\u009c\u00a3\u0005"+
		"&\u0000\u0000\u009d\u009e\u0005N\u0000\u0000\u009e\u009f\u0003\"\u0011"+
		"\u0000\u009f\u00a0\u0005O\u0000\u0000\u00a0\u00a3\u0001\u0000\u0000\u0000"+
		"\u00a1\u00a3\u0003\b\u0004\u0000\u00a2\u009a\u0001\u0000\u0000\u0000\u00a2"+
		"\u009b\u0001\u0000\u0000\u0000\u00a2\u009c\u0001\u0000\u0000\u0000\u00a2"+
		"\u009d\u0001\u0000\u0000\u0000\u00a2\u00a1\u0001\u0000\u0000\u0000\u00a3"+
		"\u000b\u0001\u0000\u0000\u0000\u00a4\u00a9\u0003\"\u0011\u0000\u00a5\u00a6"+
		"\u0005T\u0000\u0000\u00a6\u00a8\u0003\"\u0011\u0000\u00a7\u00a5\u0001"+
		"\u0000\u0000\u0000\u00a8\u00ab\u0001\u0000\u0000\u0000\u00a9\u00a7\u0001"+
		"\u0000\u0000\u0000\u00a9\u00aa\u0001\u0000\u0000\u0000\u00aa\r\u0001\u0000"+
		"\u0000\u0000\u00ab\u00a9\u0001\u0000\u0000\u0000\u00ac\u00b1\u0003\"\u0011"+
		"\u0000\u00ad\u00ae\u0005T\u0000\u0000\u00ae\u00b0\u0003\"\u0011\u0000"+
		"\u00af\u00ad\u0001\u0000\u0000\u0000\u00b0\u00b3\u0001\u0000\u0000\u0000"+
		"\u00b1\u00af\u0001\u0000\u0000\u0000\u00b1\u00b2\u0001\u0000\u0000\u0000"+
		"\u00b2\u000f\u0001\u0000\u0000\u0000\u00b3\u00b1\u0001\u0000\u0000\u0000"+
		"\u00b4\u00c0\u0003\n\u0005\u0000\u00b5\u00b6\u0005P\u0000\u0000\u00b6"+
		"\u00b7\u0003\u000e\u0007\u0000\u00b7\u00b8\u0005Q\u0000\u0000\u00b8\u00bf"+
		"\u0001\u0000\u0000\u0000\u00b9\u00bb\u0005N\u0000\u0000\u00ba\u00bc\u0003"+
		"\f\u0006\u0000\u00bb\u00ba\u0001\u0000\u0000\u0000\u00bb\u00bc\u0001\u0000"+
		"\u0000\u0000\u00bc\u00bd\u0001\u0000\u0000\u0000\u00bd\u00bf\u0005O\u0000"+
		"\u0000\u00be\u00b5\u0001\u0000\u0000\u0000\u00be\u00b9\u0001\u0000\u0000"+
		"\u0000\u00bf\u00c2\u0001\u0000\u0000\u0000\u00c0\u00be\u0001\u0000\u0000"+
		"\u0000\u00c0\u00c1\u0001\u0000\u0000\u0000\u00c1\u0011\u0001\u0000\u0000"+
		"\u0000\u00c2\u00c0\u0001\u0000\u0000\u0000\u00c3\u00c4\u0007\u0001\u0000"+
		"\u0000\u00c4\u00c7\u0003\u0012\t\u0000\u00c5\u00c7\u0003\u0010\b\u0000"+
		"\u00c6\u00c3\u0001\u0000\u0000\u0000\u00c6\u00c5\u0001\u0000\u0000\u0000"+
		"\u00c7\u0013\u0001\u0000\u0000\u0000\u00c8\u00cb\u0003\u0012\t\u0000\u00c9"+
		"\u00ca\u0005C\u0000\u0000\u00ca\u00cc\u0003\u0014\n\u0000\u00cb\u00c9"+
		"\u0001\u0000\u0000\u0000\u00cb\u00cc\u0001\u0000\u0000\u0000\u00cc\u0015"+
		"\u0001\u0000\u0000\u0000\u00cd\u00d2\u0003\u0014\n\u0000\u00ce\u00cf\u0007"+
		"\u0002\u0000\u0000\u00cf\u00d1\u0003\u0014\n\u0000\u00d0\u00ce\u0001\u0000"+
		"\u0000\u0000\u00d1\u00d4\u0001\u0000\u0000\u0000\u00d2\u00d0\u0001\u0000"+
		"\u0000\u0000\u00d2\u00d3\u0001\u0000\u0000\u0000\u00d3\u0017\u0001\u0000"+
		"\u0000\u0000\u00d4\u00d2\u0001\u0000\u0000\u0000\u00d5\u00da\u0003\u0016"+
		"\u000b\u0000\u00d6\u00d7\u0007\u0003\u0000\u0000\u00d7\u00d9\u0003\u0016"+
		"\u000b\u0000\u00d8\u00d6\u0001\u0000\u0000\u0000\u00d9\u00dc\u0001\u0000"+
		"\u0000\u0000\u00da\u00d8\u0001\u0000\u0000\u0000\u00da\u00db\u0001\u0000"+
		"\u0000\u0000\u00db\u0019\u0001\u0000\u0000\u0000\u00dc\u00da\u0001\u0000"+
		"\u0000\u0000\u00dd\u00e2\u0003\u0018\f\u0000\u00de\u00df\u0007\u0004\u0000"+
		"\u0000\u00df\u00e1\u0003\u0018\f\u0000\u00e0\u00de\u0001\u0000\u0000\u0000"+
		"\u00e1\u00e4\u0001\u0000\u0000\u0000\u00e2\u00e0\u0001\u0000\u0000\u0000"+
		"\u00e2\u00e3\u0001\u0000\u0000\u0000\u00e3\u001b\u0001\u0000\u0000\u0000"+
		"\u00e4\u00e2\u0001\u0000\u0000\u0000\u00e5\u00ea\u0003\u001a\r\u0000\u00e6"+
		"\u00e7\u0007\u0005\u0000\u0000\u00e7\u00e9\u0003\u001a\r\u0000\u00e8\u00e6"+
		"\u0001\u0000\u0000\u0000\u00e9\u00ec\u0001\u0000\u0000\u0000\u00ea\u00e8"+
		"\u0001\u0000\u0000\u0000\u00ea\u00eb\u0001\u0000\u0000\u0000\u00eb\u001d"+
		"\u0001\u0000\u0000\u0000\u00ec\u00ea\u0001\u0000\u0000\u0000\u00ed\u00f2"+
		"\u0003\u001c\u000e\u0000\u00ee\u00ef\u0005!\u0000\u0000\u00ef\u00f1\u0003"+
		"\u001c\u000e\u0000\u00f0\u00ee\u0001\u0000\u0000\u0000\u00f1\u00f4\u0001"+
		"\u0000\u0000\u0000\u00f2\u00f0\u0001\u0000\u0000\u0000\u00f2\u00f3\u0001"+
		"\u0000\u0000\u0000\u00f3\u001f\u0001\u0000\u0000\u0000\u00f4\u00f2\u0001"+
		"\u0000\u0000\u0000\u00f5\u00fa\u0003\u001e\u000f\u0000\u00f6\u00f7\u0005"+
		"\"\u0000\u0000\u00f7\u00f9\u0003\u001e\u000f\u0000\u00f8\u00f6\u0001\u0000"+
		"\u0000\u0000\u00f9\u00fc\u0001\u0000\u0000\u0000\u00fa\u00f8\u0001\u0000"+
		"\u0000\u0000\u00fa\u00fb\u0001\u0000\u0000\u0000\u00fb!\u0001\u0000\u0000"+
		"\u0000\u00fc\u00fa\u0001\u0000\u0000\u0000\u00fd\u00fe\u0003 \u0010\u0000"+
		"\u00fe#\u0001\u0000\u0000\u0000\u00ff\u0106\u0003*\u0015\u0000\u0100\u0102"+
		"\u0003&\u0013\u0000\u0101\u0103\u0005,\u0000\u0000\u0102\u0101\u0001\u0000"+
		"\u0000\u0000\u0102\u0103\u0001\u0000\u0000\u0000\u0103\u0106\u0001\u0000"+
		"\u0000\u0000\u0104\u0106\u0003(\u0014\u0000\u0105\u00ff\u0001\u0000\u0000"+
		"\u0000\u0105\u0100\u0001\u0000\u0000\u0000\u0105\u0104\u0001\u0000\u0000"+
		"\u0000\u0106%\u0001\u0000\u0000\u0000\u0107\u0108\u0007\u0006\u0000\u0000"+
		"\u0108\'\u0001\u0000\u0000\u0000\u0109\u010a\u0007\u0007\u0000\u0000\u010a"+
		")\u0001\u0000\u0000\u0000\u010b\u010c\u0007\b\u0000\u0000\u010c+\u0001"+
		"\u0000\u0000\u0000\u010d\u010e\u0003\"\u0011\u0000\u010e\u010f\u0005U"+
		"\u0000\u0000\u010f\u0110\u0003\"\u0011\u0000\u0110-\u0001\u0000\u0000"+
		"\u0000\u0111\u011d\u0005]\u0000\u0000\u0112\u0113\u0005P\u0000\u0000\u0113"+
		"\u0118\u0003,\u0016\u0000\u0114\u0115\u0005T\u0000\u0000\u0115\u0117\u0003"+
		",\u0016\u0000\u0116\u0114\u0001\u0000\u0000\u0000\u0117\u011a\u0001\u0000"+
		"\u0000\u0000\u0118\u0116\u0001\u0000\u0000\u0000\u0118\u0119\u0001\u0000"+
		"\u0000\u0000\u0119\u011b\u0001\u0000\u0000\u0000\u011a\u0118\u0001\u0000"+
		"\u0000\u0000\u011b\u011c\u0005Q\u0000\u0000\u011c\u011e\u0001\u0000\u0000"+
		"\u0000\u011d\u0112\u0001\u0000\u0000\u0000\u011d\u011e\u0001\u0000\u0000"+
		"\u0000\u011e\u0121\u0001\u0000\u0000\u0000\u011f\u0120\u0005K\u0000\u0000"+
		"\u0120\u0122\u0003\"\u0011\u0000\u0121\u011f\u0001\u0000\u0000\u0000\u0121"+
		"\u0122\u0001\u0000\u0000\u0000\u0122/\u0001\u0000\u0000\u0000\u0123\u0128"+
		"\u0003.\u0017\u0000\u0124\u0125\u0005T\u0000\u0000\u0125\u0127\u0003."+
		"\u0017\u0000\u0126\u0124\u0001\u0000\u0000\u0000\u0127\u012a\u0001\u0000"+
		"\u0000\u0000\u0128\u0126\u0001\u0000\u0000\u0000\u0128\u0129\u0001\u0000"+
		"\u0000\u0000\u01291\u0001\u0000\u0000\u0000\u012a\u0128\u0001\u0000\u0000"+
		"\u0000\u012b\u012c\u0003$\u0012\u0000\u012c\u012d\u00030\u0018\u0000\u012d"+
		"3\u0001\u0000\u0000\u0000\u012e\u012f\u0003$\u0012\u0000\u012f\u0131\u0003"+
		"0\u0018\u0000\u0130\u0132\u0005V\u0000\u0000\u0131\u0130\u0001\u0000\u0000"+
		"\u0000\u0131\u0132\u0001\u0000\u0000\u0000\u01325\u0001\u0000\u0000\u0000"+
		"\u0133\u0134\u0003\u0000\u0000\u0000\u0134\u0138\u0005\u0014\u0000\u0000"+
		"\u0135\u0139\u0003\u0002\u0001\u0000\u0136\u0139\u0003\u0012\t\u0000\u0137"+
		"\u0139\u0003\b\u0004\u0000\u0138\u0135\u0001\u0000\u0000\u0000\u0138\u0136"+
		"\u0001\u0000\u0000\u0000\u0138\u0137\u0001\u0000\u0000\u0000\u0139\u013b"+
		"\u0001\u0000\u0000\u0000\u013a\u013c\u0005V\u0000\u0000\u013b\u013a\u0001"+
		"\u0000\u0000\u0000\u013b\u013c\u0001\u0000\u0000\u0000\u013c7\u0001\u0000"+
		"\u0000\u0000\u013d\u013f\u0007\t\u0000\u0000\u013e\u013d\u0001\u0000\u0000"+
		"\u0000\u013e\u013f\u0001\u0000\u0000\u0000\u013f\u0140\u0001\u0000\u0000"+
		"\u0000\u0140\u0141\u0003$\u0012\u0000\u0141\u0142\u00030\u0018\u0000\u0142"+
		"9\u0001\u0000\u0000\u0000\u0143\u0148\u00038\u001c\u0000\u0144\u0145\u0005"+
		"T\u0000\u0000\u0145\u0147\u00038\u001c\u0000\u0146\u0144\u0001\u0000\u0000"+
		"\u0000\u0147\u014a\u0001\u0000\u0000\u0000\u0148\u0146\u0001\u0000\u0000"+
		"\u0000\u0148\u0149\u0001\u0000\u0000\u0000\u0149;\u0001\u0000\u0000\u0000"+
		"\u014a\u0148\u0001\u0000\u0000\u0000\u014b\u014d\b\n\u0000\u0000\u014c"+
		"\u014b\u0001\u0000\u0000\u0000\u014d\u014e\u0001\u0000\u0000\u0000\u014e"+
		"\u014c\u0001\u0000\u0000\u0000\u014e\u014f\u0001\u0000\u0000\u0000\u014f"+
		"=\u0001\u0000\u0000\u0000\u0150\u0152\u0005]\u0000\u0000\u0151\u0150\u0001"+
		"\u0000\u0000\u0000\u0152\u0153\u0001\u0000\u0000\u0000\u0153\u0151\u0001"+
		"\u0000\u0000\u0000\u0153\u0154\u0001\u0000\u0000\u0000\u0154?\u0001\u0000"+
		"\u0000\u0000\u0155\u0157\u0005\u0003\u0000\u0000\u0156\u0158\u0003$\u0012"+
		"\u0000\u0157\u0156\u0001\u0000\u0000\u0000\u0157\u0158\u0001\u0000\u0000"+
		"\u0000\u0158\u0159\u0001\u0000\u0000\u0000\u0159\u015f\u0003<\u001e\u0000"+
		"\u015a\u015c\u0005N\u0000\u0000\u015b\u015d\u0003:\u001d\u0000\u015c\u015b"+
		"\u0001\u0000\u0000\u0000\u015c\u015d\u0001\u0000\u0000\u0000\u015d\u015e"+
		"\u0001\u0000\u0000\u0000\u015e\u0160\u0005O\u0000\u0000\u015f\u015a\u0001"+
		"\u0000\u0000\u0000\u015f\u0160\u0001\u0000\u0000\u0000\u0160\u0162\u0001"+
		"\u0000\u0000\u0000\u0161\u0163\u0005V\u0000\u0000\u0162\u0161\u0001\u0000"+
		"\u0000\u0000\u0162\u0163\u0001\u0000\u0000\u0000\u0163A\u0001\u0000\u0000"+
		"\u0000\u0164\u0165\u0005\u0006\u0000\u0000\u0165\u0167\u0003\"\u0011\u0000"+
		"\u0166\u0168\u0005V\u0000\u0000\u0167\u0166\u0001\u0000\u0000\u0000\u0167"+
		"\u0168\u0001\u0000\u0000\u0000\u0168C\u0001\u0000\u0000\u0000\u0169\u016a"+
		"\u0005\u0007\u0000\u0000\u016a\u016c\u0003\"\u0011\u0000\u016b\u016d\u0005"+
		"V\u0000\u0000\u016c\u016b\u0001\u0000\u0000\u0000\u016c\u016d\u0001\u0000"+
		"\u0000\u0000\u016dE\u0001\u0000\u0000\u0000\u016e\u016f\u0003H$\u0000"+
		"\u016fG\u0001\u0000\u0000\u0000\u0170\u0172\u0003j5\u0000\u0171\u0170"+
		"\u0001\u0000\u0000\u0000\u0172\u0175\u0001\u0000\u0000\u0000\u0173\u0171"+
		"\u0001\u0000\u0000\u0000\u0173\u0174\u0001\u0000\u0000\u0000\u0174I\u0001"+
		"\u0000\u0000\u0000\u0175\u0173\u0001\u0000\u0000\u0000\u0176\u017b\u0003"+
		"\u0000\u0000\u0000\u0177\u0178\u0005P\u0000\u0000\u0178\u0179\u0003\u000e"+
		"\u0007\u0000\u0179\u017a\u0005Q\u0000\u0000\u017a\u017c\u0001\u0000\u0000"+
		"\u0000\u017b\u0177\u0001\u0000\u0000\u0000\u017b\u017c\u0001\u0000\u0000"+
		"\u0000\u017c\u017f\u0001\u0000\u0000\u0000\u017d\u017f\u0005&\u0000\u0000"+
		"\u017e\u0176\u0001\u0000\u0000\u0000\u017e\u017d\u0001\u0000\u0000\u0000"+
		"\u017fK\u0001\u0000\u0000\u0000\u0180\u0181\u0003J%\u0000\u0181\u0182"+
		"\u0005\u0014\u0000\u0000\u0182\u0183\u0003\"\u0011\u0000\u0183\u0186\u0001"+
		"\u0000\u0000\u0000\u0184\u0186\u0003\"\u0011\u0000\u0185\u0180\u0001\u0000"+
		"\u0000\u0000\u0185\u0184\u0001\u0000\u0000\u0000\u0186M\u0001\u0000\u0000"+
		"\u0000\u0187\u018e\u0003\"\u0011\u0000\u0188\u0189\u0005U\u0000\u0000"+
		"\u0189\u018c\u0003\"\u0011\u0000\u018a\u018b\u0005U\u0000\u0000\u018b"+
		"\u018d\u0003\"\u0011\u0000\u018c\u018a\u0001\u0000\u0000\u0000\u018c\u018d"+
		"\u0001\u0000\u0000\u0000\u018d\u018f\u0001\u0000\u0000\u0000\u018e\u0188"+
		"\u0001\u0000\u0000\u0000\u018e\u018f\u0001\u0000\u0000\u0000\u018f\u0192"+
		"\u0001\u0000\u0000\u0000\u0190\u0192\u0005\u001f\u0000\u0000\u0191\u0187"+
		"\u0001\u0000\u0000\u0000\u0191\u0190\u0001\u0000\u0000\u0000\u0192O\u0001"+
		"\u0000\u0000\u0000\u0193\u0198\u0003N\'\u0000\u0194\u0195\u0005T\u0000"+
		"\u0000\u0195\u0197\u0003N\'\u0000\u0196\u0194\u0001\u0000\u0000\u0000"+
		"\u0197\u019a\u0001\u0000\u0000\u0000\u0198\u0196\u0001\u0000\u0000\u0000"+
		"\u0198\u0199\u0001\u0000\u0000\u0000\u0199Q\u0001\u0000\u0000\u0000\u019a"+
		"\u0198\u0001\u0000\u0000\u0000\u019b\u019c\u0007\u000b\u0000\u0000\u019c"+
		"\u019d\u0003P(\u0000\u019dS\u0001\u0000\u0000\u0000\u019e\u019f\u0005"+
		"\f\u0000\u0000\u019f\u01a0\u0003\"\u0011\u0000\u01a0\u01a1\u0005\r\u0000"+
		"\u0000\u01a1\u01a4\u0003H$\u0000\u01a2\u01a3\u0005\u000e\u0000\u0000\u01a3"+
		"\u01a5\u0003H$\u0000\u01a4\u01a2\u0001\u0000\u0000\u0000\u01a4\u01a5\u0001"+
		"\u0000\u0000\u0000\u01a5\u01a6\u0001\u0000\u0000\u0000\u01a6\u01a7\u0005"+
		"\u000f\u0000\u0000\u01a7U\u0001\u0000\u0000\u0000\u01a8\u01a9\u0005\u0011"+
		"\u0000\u0000\u01a9\u01aa\u0003\"\u0011\u0000\u01aa\u01ab\u0005U\u0000"+
		"\u0000\u01ab\u01ac\u0003H$\u0000\u01acW\u0001\u0000\u0000\u0000\u01ad"+
		"\u01af\u0005\u0010\u0000\u0000\u01ae\u01b0\u0003V+\u0000\u01af\u01ae\u0001"+
		"\u0000\u0000\u0000\u01b0\u01b1\u0001\u0000\u0000\u0000\u01b1\u01af\u0001"+
		"\u0000\u0000\u0000\u01b1\u01b2\u0001\u0000\u0000\u0000\u01b2\u01b5\u0001"+
		"\u0000\u0000\u0000\u01b3\u01b4\u0005\u000e\u0000\u0000\u01b4\u01b6\u0003"+
		"H$\u0000\u01b5\u01b3\u0001\u0000\u0000\u0000\u01b5\u01b6\u0001\u0000\u0000"+
		"\u0000\u01b6\u01b7\u0001\u0000\u0000\u0000\u01b7\u01b8\u0005\u000f\u0000"+
		"\u0000\u01b8Y\u0001\u0000\u0000\u0000\u01b9\u01ba\u0005\n\u0000\u0000"+
		"\u01ba\u01bb\u0003\"\u0011\u0000\u01bb[\u0001\u0000\u0000\u0000\u01bc"+
		"\u01bd\u0005\u0019\u0000\u0000\u01bd\u01be\u0005]\u0000\u0000\u01be\u01bf"+
		"\u0005\u001c\u0000\u0000\u01bf\u01c0\u0003\"\u0011\u0000\u01c0\u01c1\u0005"+
		"\u001d\u0000\u0000\u01c1\u01c4\u0003\"\u0011\u0000\u01c2\u01c3\u0005\u001e"+
		"\u0000\u0000\u01c3\u01c5\u0003\"\u0011\u0000\u01c4\u01c2\u0001\u0000\u0000"+
		"\u0000\u01c4\u01c5\u0001\u0000\u0000\u0000\u01c5\u01cc\u0001\u0000\u0000"+
		"\u0000\u01c6\u01c7\u0005\u001a\u0000\u0000\u01c7\u01cc\u0003\"\u0011\u0000"+
		"\u01c8\u01c9\u0003\"\u0011\u0000\u01c9\u01ca\u0005\u001b\u0000\u0000\u01ca"+
		"\u01cc\u0001\u0000\u0000\u0000\u01cb\u01bc\u0001\u0000\u0000\u0000\u01cb"+
		"\u01c6\u0001\u0000\u0000\u0000\u01cb\u01c8\u0001\u0000\u0000\u0000\u01cc"+
		"]\u0001\u0000\u0000\u0000\u01cd\u01cf\u0005\t\u0000\u0000\u01ce\u01d0"+
		"\u0003\\.\u0000\u01cf\u01ce\u0001\u0000\u0000\u0000\u01cf\u01d0\u0001"+
		"\u0000\u0000\u0000\u01d0\u01d1\u0001\u0000\u0000\u0000\u01d1\u01d4\u0003"+
		"H$\u0000\u01d2\u01d5\u0005\u000b\u0000\u0000\u01d3\u01d5\u0003Z-\u0000"+
		"\u01d4\u01d2\u0001\u0000\u0000\u0000\u01d4\u01d3\u0001\u0000\u0000\u0000"+
		"\u01d5_\u0001\u0000\u0000\u0000\u01d6\u01d7\u0005\u0015\u0000\u0000\u01d7"+
		"a\u0001\u0000\u0000\u0000\u01d8\u01d9\u0005\u0016\u0000\u0000\u01d9c\u0001"+
		"\u0000\u0000\u0000\u01da\u01db\u0005\u0017\u0000\u0000\u01dbe\u0001\u0000"+
		"\u0000\u0000\u01dc\u01dd\u0005\b\u0000\u0000\u01dd\u01de\u0003\"\u0011"+
		"\u0000\u01deg\u0001\u0000\u0000\u0000\u01df\u01e5\u0003\u0000\u0000\u0000"+
		"\u01e0\u01e2\u0005N\u0000\u0000\u01e1\u01e3\u0003\f\u0006\u0000\u01e2"+
		"\u01e1\u0001\u0000\u0000\u0000\u01e2\u01e3\u0001\u0000\u0000\u0000\u01e3"+
		"\u01e4\u0001\u0000\u0000\u0000\u01e4\u01e6\u0005O\u0000\u0000\u01e5\u01e0"+
		"\u0001\u0000\u0000\u0000\u01e5\u01e6\u0001\u0000\u0000\u0000\u01e6i\u0001"+
		"\u0000\u0000\u0000\u01e7\u01e9\u00032\u0019\u0000\u01e8\u01ea\u0005V\u0000"+
		"\u0000\u01e9\u01e8\u0001\u0000\u0000\u0000\u01e9\u01ea\u0001\u0000\u0000"+
		"\u0000\u01ea\u0211\u0001\u0000\u0000\u0000\u01eb\u01ed\u0003L&\u0000\u01ec"+
		"\u01ee\u0005V\u0000\u0000\u01ed\u01ec\u0001\u0000\u0000\u0000\u01ed\u01ee"+
		"\u0001\u0000\u0000\u0000\u01ee\u0211\u0001\u0000\u0000\u0000\u01ef\u01f1"+
		"\u0003R)\u0000\u01f0\u01f2\u0005V\u0000\u0000\u01f1\u01f0\u0001\u0000"+
		"\u0000\u0000\u01f1\u01f2\u0001\u0000\u0000\u0000\u01f2\u0211\u0001\u0000"+
		"\u0000\u0000\u01f3\u01f5\u0003T*\u0000\u01f4\u01f6\u0005V\u0000\u0000"+
		"\u01f5\u01f4\u0001\u0000\u0000\u0000\u01f5\u01f6\u0001\u0000\u0000\u0000"+
		"\u01f6\u0211\u0001\u0000\u0000\u0000\u01f7\u01f9\u0003X,\u0000\u01f8\u01fa"+
		"\u0005V\u0000\u0000\u01f9\u01f8\u0001\u0000\u0000\u0000\u01f9\u01fa\u0001"+
		"\u0000\u0000\u0000\u01fa\u0211\u0001\u0000\u0000\u0000\u01fb\u01fd\u0003"+
		"^/\u0000\u01fc\u01fe\u0005V\u0000\u0000\u01fd\u01fc\u0001\u0000\u0000"+
		"\u0000\u01fd\u01fe\u0001\u0000\u0000\u0000\u01fe\u0211\u0001\u0000\u0000"+
		"\u0000\u01ff\u0201\u0003`0\u0000\u0200\u0202\u0005V\u0000\u0000\u0201"+
		"\u0200\u0001\u0000\u0000\u0000\u0201\u0202\u0001\u0000\u0000\u0000\u0202"+
		"\u0211\u0001\u0000\u0000\u0000\u0203\u0205\u0003b1\u0000\u0204\u0206\u0005"+
		"V\u0000\u0000\u0205\u0204\u0001\u0000\u0000\u0000\u0205\u0206\u0001\u0000"+
		"\u0000\u0000\u0206\u0211\u0001\u0000\u0000\u0000\u0207\u0209\u0003d2\u0000"+
		"\u0208\u020a\u0005V\u0000\u0000\u0209\u0208\u0001\u0000\u0000\u0000\u0209"+
		"\u020a\u0001\u0000\u0000\u0000\u020a\u0211\u0001\u0000\u0000\u0000\u020b"+
		"\u020d\u0003f3\u0000\u020c\u020e\u0005V\u0000\u0000\u020d\u020c\u0001"+
		"\u0000\u0000\u0000\u020d\u020e\u0001\u0000\u0000\u0000\u020e\u0211\u0001"+
		"\u0000\u0000\u0000\u020f\u0211\u0005V\u0000\u0000\u0210\u01e7\u0001\u0000"+
		"\u0000\u0000\u0210\u01eb\u0001\u0000\u0000\u0000\u0210\u01ef\u0001\u0000"+
		"\u0000\u0000\u0210\u01f3\u0001\u0000\u0000\u0000\u0210\u01f7\u0001\u0000"+
		"\u0000\u0000\u0210\u01fb\u0001\u0000\u0000\u0000\u0210\u01ff\u0001\u0000"+
		"\u0000\u0000\u0210\u0203\u0001\u0000\u0000\u0000\u0210\u0207\u0001\u0000"+
		"\u0000\u0000\u0210\u020b\u0001\u0000\u0000\u0000\u0210\u020f\u0001\u0000"+
		"\u0000\u0000\u0211k\u0001\u0000\u0000\u0000\u0212\u0218\u0003@ \u0000"+
		"\u0213\u0217\u0003B!\u0000\u0214\u0217\u0003D\"\u0000\u0215\u0217\u0003"+
		"2\u0019\u0000\u0216\u0213\u0001\u0000\u0000\u0000\u0216\u0214\u0001\u0000"+
		"\u0000\u0000\u0216\u0215\u0001\u0000\u0000\u0000\u0217\u021a\u0001\u0000"+
		"\u0000\u0000\u0218\u0216\u0001\u0000\u0000\u0000\u0218\u0219\u0001\u0000"+
		"\u0000\u0000\u0219\u021b\u0001\u0000\u0000\u0000\u021a\u0218\u0001\u0000"+
		"\u0000\u0000\u021b\u021c\u0005\u0004\u0000\u0000\u021c\u021d\u0003F#\u0000"+
		"\u021d\u021f\u0005\u0005\u0000\u0000\u021e\u0220\u0003>\u001f\u0000\u021f"+
		"\u021e\u0001\u0000\u0000\u0000\u021f\u0220\u0001\u0000\u0000\u0000\u0220"+
		"\u0222\u0001\u0000\u0000\u0000\u0221\u0223\u0005V\u0000\u0000\u0222\u0221"+
		"\u0001\u0000\u0000\u0000\u0222\u0223\u0001\u0000\u0000\u0000\u0223m\u0001"+
		"\u0000\u0000\u0000\u0224\u0227\u0003\u0000\u0000\u0000\u0225\u0227\u0005"+
		"Z\u0000\u0000\u0226\u0224\u0001\u0000\u0000\u0000\u0226\u0225\u0001\u0000"+
		"\u0000\u0000\u0227o\u0001\u0000\u0000\u0000\u0228\u0229\u0005\u0018\u0000"+
		"\u0000\u0229\u022b\u0003n7\u0000\u022a\u022c\u0005V\u0000\u0000\u022b"+
		"\u022a\u0001\u0000\u0000\u0000\u022b\u022c\u0001\u0000\u0000\u0000\u022c"+
		"q\u0001\u0000\u0000\u0000\u022d\u0231\u0003p8\u0000\u022e\u0231\u0003"+
		"4\u001a\u0000\u022f\u0231\u00036\u001b\u0000\u0230\u022d\u0001\u0000\u0000"+
		"\u0000\u0230\u022e\u0001\u0000\u0000\u0000\u0230\u022f\u0001\u0000\u0000"+
		"\u0000\u0231s\u0001\u0000\u0000\u0000\u0232\u0233\u0005\u0001\u0000\u0000"+
		"\u0233\u0235\u0003\u0000\u0000\u0000\u0234\u0236\u0005V\u0000\u0000\u0235"+
		"\u0234\u0001\u0000\u0000\u0000\u0235\u0236\u0001\u0000\u0000\u0000\u0236"+
		"u\u0001\u0000\u0000\u0000\u0237\u023a\u0003r9\u0000\u0238\u023a\u0003"+
		"l6\u0000\u0239\u0237\u0001\u0000\u0000\u0000\u0239\u0238\u0001\u0000\u0000"+
		"\u0000\u023a\u023d\u0001\u0000\u0000\u0000\u023b\u0239\u0001\u0000\u0000"+
		"\u0000\u023b\u023c\u0001\u0000\u0000\u0000\u023cw\u0001\u0000\u0000\u0000"+
		"\u023d\u023b\u0001\u0000\u0000\u0000\u023e\u0241\u0003r9\u0000\u023f\u0241"+
		"\u0003l6\u0000\u0240\u023e\u0001\u0000\u0000\u0000\u0240\u023f\u0001\u0000"+
		"\u0000\u0000\u0241\u0242\u0001\u0000\u0000\u0000\u0242\u0240\u0001\u0000"+
		"\u0000\u0000\u0242\u0243\u0001\u0000\u0000\u0000\u0243y\u0001\u0000\u0000"+
		"\u0000\u0244\u0245\u0003t:\u0000\u0245\u0246\u0003v;\u0000\u0246\u0248"+
		"\u0005\u0002\u0000\u0000\u0247\u0249\u0003\u0000\u0000\u0000\u0248\u0247"+
		"\u0001\u0000\u0000\u0000\u0248\u0249\u0001\u0000\u0000\u0000\u0249\u024b"+
		"\u0001\u0000\u0000\u0000\u024a\u024c\u0005V\u0000\u0000\u024b\u024a\u0001"+
		"\u0000\u0000\u0000\u024b\u024c\u0001\u0000\u0000\u0000\u024c\u024f\u0001"+
		"\u0000\u0000\u0000\u024d\u024f\u0003x<\u0000\u024e\u0244\u0001\u0000\u0000"+
		"\u0000\u024e\u024d\u0001\u0000\u0000\u0000\u024f{\u0001\u0000\u0000\u0000"+
		"\u0250\u0252\u0003r9\u0000\u0251\u0250\u0001\u0000\u0000\u0000\u0252\u0255"+
		"\u0001\u0000\u0000\u0000\u0253\u0251\u0001\u0000\u0000\u0000\u0253\u0254"+
		"\u0001\u0000\u0000\u0000\u0254\u0257\u0001\u0000\u0000\u0000\u0255\u0253"+
		"\u0001\u0000\u0000\u0000\u0256\u0258\u0003z=\u0000\u0257\u0256\u0001\u0000"+
		"\u0000\u0000\u0258\u0259\u0001\u0000\u0000\u0000\u0259\u0257\u0001\u0000"+
		"\u0000\u0000\u0259\u025a\u0001\u0000\u0000\u0000\u025a\u025b\u0001\u0000"+
		"\u0000\u0000\u025b\u025c\u0005\u0000\u0000\u0001\u025c}\u0001\u0000\u0000"+
		"\u0000Q\u0088\u0091\u0096\u00a2\u00a9\u00b1\u00bb\u00be\u00c0\u00c6\u00cb"+
		"\u00d2\u00da\u00e2\u00ea\u00f2\u00fa\u0102\u0105\u0118\u011d\u0121\u0128"+
		"\u0131\u0138\u013b\u013e\u0148\u014e\u0153\u0157\u015c\u015f\u0162\u0167"+
		"\u016c\u0173\u017b\u017e\u0185\u018c\u018e\u0191\u0198\u01a4\u01b1\u01b5"+
		"\u01c4\u01cb\u01cf\u01d4\u01e2\u01e5\u01e9\u01ed\u01f1\u01f5\u01f9\u01fd"+
		"\u0201\u0205\u0209\u020d\u0210\u0216\u0218\u021f\u0222\u0226\u022b\u0230"+
		"\u0235\u0239\u023b\u0240\u0242\u0248\u024b\u024e\u0253\u0259";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}