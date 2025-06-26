# pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py
# Этот файл будет содержать логику вычисения выражений для интерпретатора КуМира.

from __future__ import annotations
from antlr4 import ParserRuleContext, Token
from typing import Any, List, Tuple, Callable
from ..generated.KumirParser import KumirParser # Оставляем только этот импорт для KumirParser
from .scope_manager import ScopeManager
from .procedure_manager import ProcedureManager
from ..generated.KumirParserVisitor import KumirParserVisitor
from ..generated.KumirParser import KumirParser
from .scope_manager import ScopeManager # Исправленный импорт ScopeManager
from ..kumir_datatypes import KumirValue, KumirType, KumirTableVar # Добавлено
from ..kumir_exceptions import KumirEvalError, KumirTypeError, KumirNameError, KumirRuntimeError, KumirNotImplementedError, KumirArgumentError, KumirSyntaxError, KumirIndexError # Добавлены KumirRuntimeError, KumirNotImplementedError, KumirArgumentError, KumirSyntaxError, КумирIndexError
import operator # Добавлено для реляционных операций
from ..generated.KumirLexer import KumirLexer # Добавлено для констант токенов

# Словарь операций сравнения для реляционных выражений
COMPARISON_OPS = {
    KumirLexer.EQ: operator.eq,
    KumirLexer.NE: operator.ne,
    KumirLexer.LT: operator.lt,
    KumirLexer.GT: operator.gt,
    KumirLexer.LE: operator.le,
    KumirLexer.GE: operator.ge,
}

# Словарь логических операций
LOGICAL_OPS: dict[int, Callable[[bool, bool], bool]] = {
    KumirLexer.AND: lambda a, b: a and b,
    KumirLexer.OR: lambda a, b: a or b,
}


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main_visitor import KumirInterpreterVisitor

class ExpressionEvaluator(KumirParserVisitor):
    def __init__(self, main_visitor: 'KumirInterpreterVisitor', scope_manager: ScopeManager, procedure_manager: ProcedureManager): # Добавлен main_visitor
        self.main_visitor = main_visitor # Сохраняем main_visitor
        self.scope_manager = scope_manager
        self.procedure_manager = procedure_manager

    @staticmethod
    def _position_from_token(token: Token) -> Tuple[int, int]:
        """Извлекает номер строки и столбца из токена ANTLR."""
        return token.line, token.column

    @staticmethod
    def _get_token_from_node(node) -> Token:
        """
        Получает токен из узла AST (обрабатывает как TerminalNodeImpl, так и обычные токены).
        """
        if hasattr(node, 'symbol'):
            return node.symbol  # TerminalNodeImpl
        elif hasattr(node, 'start'):
            return node.start   # ParserRuleContext
        else:
            return node         # Предполагаем что это уже токен

    def _get_token_for_position(self, ctx: ParserRuleContext) -> Token:
        """Возвращает первый токен из контекста для определения позиции ошибки."""
        return ctx.start # start это токен

    def _check_operand_type(self, operand: KumirValue, expected_kumir_types: List[KumirType], operation_name: str, token_for_pos: Token):
        """
        Проверяет, что тип операнда KumirValue соответствует одному из ожидаемых KumirType.
        Выбрасывает KumirTypeError, если тип не соответствует.
        """
        # operand.kumir_type это строка, например "ЦЕЛ"
        # expected_kumir_types это список KumirType enum, например [KumirType.INT, KumirType.REAL]
        # Нам нужно сравнить строку с .value каждого элемента enum
        if operand.kumir_type not in [kt.value for kt in expected_kumir_types]:
            pos = self._position_from_token(token_for_pos)
            expected_types_str = ", ".join([kt.value for kt in expected_kumir_types])
            raise KumirTypeError(
                f"Тип операнда для операции \'{operation_name}\' должен быть одним из [{expected_types_str}], а получен \'{operand.kumir_type}\'.",
                line_index=pos[0], 
                column_index=pos[1]
            )

    def _visit_operand(self, expr_ctx: ParserRuleContext) -> KumirValue:
        """
        Обрабатывает контекст выражения, который должен дать KumirValue.
        Если результат visit не KumirValue, выбрасывает KumirRuntimeError.
        """
        value = self.visit(expr_ctx)
        if not isinstance(value, KumirValue):  # type: ignore[redundant-expr]
            pos_token = self._get_token_for_position(expr_ctx)
            pos = self._position_from_token(pos_token)
            # Эта ситуация не должна возникать, если все visit методы возвращают KumirValue
            raise KumirRuntimeError(
                f"Внутренняя ошибка: операнд не является KumirValue (получен тип {type(value).__name__}).",
                line_index=pos[0],
                column_index=pos[1]
            )
        return value

    # Visit methods for different expression types
    # ==========================================

    # def visitCompilationUnit(self, ctx: KumirParser.CompilationUnitContext):
    #     # Логика обхода корневого узла дерева разбора (если необходимо)
    #     # Обычно начинается с конкретного правила, например, program
    #     # return self.visit(ctx.program()) # Пример
    #     pass # TODO: Implement if needed, or remove

    def visitProgram(self, ctx: KumirParser.ProgramContext):
        # Предполагается, что основная логика программы (последовательность утверждений)
        # обрабатывается в StatementExecutor или аналогичном компоненте.
        # ExpressionEvaluator используется для вычисления значений выражений.
        # Если program содержит выражения верхнего уровня для вычисления (редко),
        # то здесь может быть логика. Чаще всего этот метод не нужен в ExpressionEvaluator.
        # Для примера, если бы программа была просто одним выражением:
        # if ctx.expression():
        #     return self.visit(ctx.expression())
        pass # Обычно не используется в ExpressionEvaluator
    
    def visitLiteral(self, ctx: KumirParser.LiteralContext) -> KumirValue:
        text = ctx.getText()
        # Получаем текст из литерала
        
        if ctx.INTEGER():
            return KumirValue(value=int(text), kumir_type=KumirType.INT.value)
        elif ctx.REAL():
            # Кумир использует запятую как десятичный разделитель
            return KumirValue(value=float(text.replace(',', '.')), kumir_type=KumirType.REAL.value)
        elif ctx.STRING():
            # Удаляем кавычки в начале и в конце
            return KumirValue(value=text[1:-1], kumir_type=KumirType.STR.value)
        elif ctx.CHAR_LITERAL():
            # Удаляем апострофы в начале и в конце для символьного литерала
            return KumirValue(value=text[1:-1], kumir_type=KumirType.CHAR.value)
        elif ctx.TRUE():
            return KumirValue(value=True, kumir_type=KumirType.BOOL.value)
        elif ctx.FALSE():
            return KumirValue(value=False, kumir_type=KumirType.BOOL.value)
        elif ctx.NEWLINE_CONST(): # константа нс
            # self.main_visitor.error_stream_out(f"DEBUG: ExpressionEvaluator.visitLiteral NEWLINE_CONST detected. Type: {type(ctx.NEWLINE_CONST())}, Text: {ctx.NEWLINE_CONST().getText()}\\n")
            return KumirValue("\n", KumirType.STR.value) # Настоящий символ перевода строки как строка
        else:
            pos = self._position_from_token(self._get_token_for_position(ctx))
            raise KumirNotImplementedError(f"Тип литерала '{text}' (контекст: {type(ctx).__name__}) пока не поддерживается или является неизвестным.", line_index=pos[0], column_index=pos[1])

    # ParenthesizedExpression - метка ParenthesizedExpr в primaryExpression
    # def visitParenthesizedExpression(self, ctx: KumirParser.ParenthesizedExpressionContext) -> KumirValue:
    #     return self.visit(ctx.expression())
    # Будет обработано в visitPrimaryExpression или visitParenthesizedExpr

    # IdentifierExpression - метка IdentifierAccessExpression в primaryExpression
    # def visitIdentifierExpression(self, ctx: KumirParser.IdentifierExpressionContext) -> KumirValue:
    #     name = ctx.IDENTIFIER().getText() # Или ctx.qualifiedIdentifier().getText()
    #     # Заменяем get_variable на lookup_variable
    #     # lookup_variable возвращает словарь var_info или вызывает KumirNameError
    #     var_info = self.scope_manager.lookup_variable(var_name, ctx_for_error=ctx)
        
    #     if var_info['is_table']:
    #         pos = self._position_from_token(self._get_token_for_position(ctx))
    #         raise KumirTypeError(f"Переменная '{var_name}' является таблицей и не может быть использована как простое значение в данном контексте.", line_index=pos[0], column_index=pos[1])

    #     # var_info['value'] - это Python-значение. var_info['type'] - строка типа Кумира.
    #     # Нам нужно создать KumirValue.
    #     # KumirType.from_string() может помочь преобразовать строку типа в KumirType enum,
    #     # а затем мы можем использовать .value для конструктора KumirValue.
    #     # Однако, KumirValue ожидает строку типа, так что var_info['type'] подходит напрямую.
        
    #     # Проверяем, инициализирована ли переменная (кроме таблиц, которые всегда "инициализированы" структурой)
    #     if not var_info.get('initialized', False) and not var_info['is_table']:
    #         pos = self._position_from_token(self._get_token_for_position(ctx))
    #         raise KumirValueError(f"Переменная '{var_name}' используется до присвоения значения.", line_index=pos[0], column_index=pos[1])

    #     python_value = var_info['value']
    #     kumir_type_str = var_info['type']
        
    #     return KumirValue(value=python_value, kumir_type=kumir_type_str)

    # TableElementExpression - метка TableAccessExpression в postfixExpression
    # def visitTableElementExpression(self, ctx: KumirParser.TableElementExpressionContext) -> KumirValue:
    #     table_name = ctx.IDENTIFIER().getText() # Или ctx.qualifiedIdentifier().getText()
    #     # Заменяем get_variable на lookup_variable
    #     table_info = self.scope_manager.lookup_variable(table_name, ctx_for_error=ctx.IDENTIFIER().getSymbol())

    #     if not table_info['is_table']:
    #         pos = self._position_from_token(ctx.IDENTIFIER().getSymbol())
    #         raise KumirTypeError(f"Переменная '{table_name}' не является таблицей.", line_index=pos[0], column_index=pos[1])

    #     # table_info['value'] должен быть экземпляром KumirTableVar
    #     kumir_table_var_instance = table_info['value']
    #     if not isinstance(kumir_table_var_instance, KumirTableVar):
    #         pos = self._position_from_token(ctx.IDENTIFIER().getSymbol())
    #         # Эта ошибка будет означать проблему в ScopeManager или логике объявления таблиц
    #         raise KumirRuntimeError(f"Внутренняя ошибка: переменная таблицы '{table_name}' не содержит ожидаемый объект KumirTableVar.", line_index=pos[0], column_index=pos[1])

    #     indices_ctx = ctx.expressionList().expression()
    #     evaluated_indices = []
    #     for expr_idx_ctx in indices_ctx:
    #         idx_val_kumir = self._visit_operand(expr_idx_ctx)
    #         self._check_operand_type(idx_val_kumir, [KumirType.INT], "индекс таблицы", self._get_token_for_position(expr_idx_ctx))
    #         evaluated_indices.append(idx_val_kumir.value)
        
    #     indices_tuple = tuple(evaluated_indices)
        
    #     try:
    #         # KumirTableVar.get_value должен возвращать KumirValue
    #         value_from_table = kumir_table_var_instance.get_value(indices_tuple, access_ctx=ctx) 
            
    #         if not isinstance(value_from_table, KumirValue):
    #             # Если KumirTableVar.get_value не возвращает KumirValue, это нужно исправить там.
    #             # Это критическая ошибка, указывающая на несоответствие контрактов.
    #             pos_token = self._get_token_for_position(ctx)
    #             pos = self._position_from_token(pos_token)
    #             raise KumirRuntimeError(
    #                 f"Внутренняя ошибка: KumirTableVar.get_value для таблицы '{table_name}' не вернул KumirValue (тип: {type(value_from_table).__name__}).",
    #                 line_index=pos[0], column_index=pos[1]
    #             )
    #         return value_from_table
    #     except KumirIndexError as e: 
    #         raise e 
    #     except KumirRuntimeError as e: # Другие ошибки времени выполнения из get_value
    #         raise e


    # UnaryMinusExpression -> UnaryExpression с правильной логикой
    def visitUnaryExpression(self, ctx: KumirParser.UnaryExpressionContext) -> KumirValue:
        """Обрабатывает унарные выражения: +expr, -expr, !expr или просто postfixExpression"""
        
        # Проверяем, есть ли унарный оператор
        if ctx.MINUS():
            op_token = ctx.MINUS().getSymbol()
            operand_val = self.visit(ctx.unaryExpression())
            self._check_operand_type(operand_val, [KumirType.INT, KumirType.REAL], "унарный минус", op_token)
            if operand_val.kumir_type == KumirType.INT.value:
                return KumirValue(value=-operand_val.value, kumir_type=KumirType.INT.value)
            elif operand_val.kumir_type == KumirType.REAL.value:
                return KumirValue(value=-operand_val.value, kumir_type=KumirType.REAL.value)
        elif ctx.PLUS():
            op_token = ctx.PLUS().getSymbol()
            operand_val = self.visit(ctx.unaryExpression())
            self._check_operand_type(operand_val, [KumirType.INT, KumirType.REAL], "унарный плюс", op_token)
            return operand_val
        elif ctx.NOT():
            op_token = ctx.NOT().getSymbol()
            operand_val = self.visit(ctx.unaryExpression())
            self._check_operand_type(operand_val, [KumirType.BOOL], "логическое НЕ", op_token)
            return KumirValue(value=not operand_val.value, kumir_type=KumirType.BOOL.value)
        elif ctx.postfixExpression():
            # Простое postfixExpression без унарного оператора
            return self.visit(ctx.postfixExpression())
        else:
            # Не должно происходить, если грамматика корректна
            pos = self._position_from_token(self._get_token_for_position(ctx))
            raise KumirRuntimeError("Неизвестный тип унарного выражения", line_index=pos[0], column_index=pos[1])
            
        # На всякий случай возвращаем что-то, хотя до сюда не должны дойти
        return KumirValue(value=0, kumir_type=KumirType.INT.value)




    def visitLogicalOrExpression(self, ctx: KumirParser.LogicalOrExpressionContext) -> KumirValue:
        """Обрабатывает логическое ИЛИ выражение"""
        # Проверяем, есть ли логическая операция ИЛИ
        logical_and_expressions = ctx.logicalAndExpression()
        
        if len(logical_and_expressions) == 1:
            # Простой случай: нет операции, просто делегируем дальше
            return self.visit(logical_and_expressions[0])
        
        # Есть операции ИЛИ: вычисляем слева направо
        result = self.visit(logical_and_expressions[0])
        
        for i in range(1, len(logical_and_expressions)):
            op_token = ctx.getChild(2*i - 1)  # Операторы находятся между выражениями
            right = self.visit(logical_and_expressions[i])
            
            # Получаем тип токена для логической операции
            if hasattr(op_token, 'symbol'):
                op_token_type = op_token.symbol.type
            else:
                op_token_type = op_token.type
            
            # Приводим операнды к boolean
            left_val = bool(result.value)
            right_val = bool(right.value)
            
            # Используем LOGICAL_OPS
            op_func = LOGICAL_OPS.get(op_token_type)
            if op_func:
                bool_result = op_func(left_val, right_val)
                result = KumirValue(value=bool_result, kumir_type=KumirType.BOOL.value)
            else:
                # Этого не должно произойти, если грамматика верна
                op_text = op_token.getText()
                pos = self._position_from_token(op_token.symbol if hasattr(op_token, 'symbol') else ctx.start)
                raise KumirRuntimeError(f"Неизвестный логический оператор: {op_text}", 
                                      line_index=pos[0], column_index=pos[1])
        
        return result

    def visitLogicalAndExpression(self, ctx: KumirParser.LogicalAndExpressionContext) -> KumirValue:
        """Обрабатывает логическое И выражение"""
        # Проверяем, есть ли логическая операция И
        equality_expressions = ctx.equalityExpression()
        
        if len(equality_expressions) == 1:
            # Простой случай: нет операции, просто делегируем дальше
            return self.visit(equality_expressions[0])
        
        # Есть операции И: вычисляем слева направо
        result = self.visit(equality_expressions[0])
        
        for i in range(1, len(equality_expressions)):
            op_token = ctx.getChild(2*i - 1)  # Операторы находятся между выражениями
            right = self.visit(equality_expressions[i])
            
            # Получаем тип токена для логической операции
            if hasattr(op_token, 'symbol'):
                op_token_type = op_token.symbol.type
            else:
                op_token_type = op_token.type
            
            # Приводим операнды к boolean
            left_val = bool(result.value)
            right_val = bool(right.value)
            
            # Используем LOGICAL_OPS
            op_func = LOGICAL_OPS.get(op_token_type)
            if op_func:
                bool_result = op_func(left_val, right_val)
                result = KumirValue(value=bool_result, kumir_type=KumirType.BOOL.value)
            else:
                # Этого не должно произойти, если грамматика верна
                op_text = op_token.getText()
                pos = self._position_from_token(op_token.symbol if hasattr(op_token, 'symbol') else ctx.start)
                raise KumirRuntimeError(f"Неизвестный логический оператор: {op_text}", 
                                      line_index=pos[0], column_index=pos[1])
        
        return result

    def visitEqualityExpression(self, ctx: KumirParser.EqualityExpressionContext) -> KumirValue:
        """Обрабатывает выражения равенства"""
        
        # Проверяем, есть ли бинарная операция равенства
        relational_expressions = ctx.relationalExpression()
        
        if len(relational_expressions) == 1:
            # Простой случай: нет операции, просто делегируем дальше
            return self.visit(relational_expressions[0])
          # Есть операции равенства: вычисляем слева направо
        result = self.visit(relational_expressions[0])
        
        for i in range(1, len(relational_expressions)):
            op_token = ctx.getChild(2*i - 1)  # Операторы находятся между выражениями
            right = self.visit(relational_expressions[i])
            
            op_text = op_token.getText()
            
            # Получаем тип токена для операции равенства
            if hasattr(op_token, 'symbol'):
                op_token_type = op_token.symbol.type
            else:
                op_token_type = op_token.type
            
            # Приводим типы для сравнения (берем значения из KumirValue)
            left_val = result.value
            right_val = right.value
              # Простое приведение типов для сравнения
            if isinstance(left_val, int) and isinstance(right_val, float):
                left_val = float(left_val)
            elif isinstance(left_val, float) and isinstance(right_val, int):
                right_val = float(right_val)
            
            # Используем COMPARISON_OPS (который содержит и операции равенства)
            op_func = COMPARISON_OPS.get(op_token_type)
            if op_func:
                bool_result = op_func(left_val, right_val)
                result = KumirValue(value=bool_result, kumir_type=KumirType.BOOL.value)
            else:
                # Этого не должно произойти, если грамматика верна
                # Для TerminalNodeImpl используем .symbol для получения токена
                pos = self._position_from_token(op_token.symbol if hasattr(op_token, 'symbol') else ctx.start)
                raise KumirRuntimeError(f"Неизвестный оператор равенства: {op_text}", 
                                      line_index=pos[0], column_index=pos[1])
        
        return result

    def visitRelationalExpression(self, ctx: KumirParser.RelationalExpressionContext) -> KumirValue:
        """Обрабатывает реляционные выражения"""
        
        # Проверяем, есть ли бинарная операция сравнения
        additive_expressions = ctx.additiveExpression()
        
        if len(additive_expressions) == 1:
            # Простой случай: нет операции, просто делегируем дальше
            return self.visit(additive_expressions[0])
          # Есть операции сравнения: вычисляем слева направо
        result = self.visit(additive_expressions[0])
        
        for i in range(1, len(additive_expressions)):
            op_token = ctx.getChild(2*i - 1)  # Операторы находятся между выражениями
            right = self.visit(additive_expressions[i])
            
            # result и right гарантированно KumirValue согласно типизации
            # Проверка не нужна - если типы неправильные, будет ошибка времени выполнения

            op_text = op_token.getText()
            
            # Получаем тип токена для операции сравнения
            if hasattr(op_token, 'symbol'):
                op_token_type = op_token.symbol.type
            else:
                op_token_type = op_token.type
            
            # Приводим типы для сравнения (берем значения из KumirValue)
            left_val = result.value
            right_val = right.value
            
            # Простое приведение типов для сравнения
            if isinstance(left_val, int) and isinstance(right_val, float):
                left_val = float(left_val)
            elif isinstance(left_val, float) and isinstance(right_val, int):
                right_val = float(right_val)
            
            # Используем COMPARISON_OPS
            op_func = COMPARISON_OPS.get(op_token_type)
            if op_func:
                bool_result = op_func(left_val, right_val)
                result = KumirValue(value=bool_result, kumir_type=KumirType.BOOL.value)
            else:
                # Этого не должно произойти, если грамматика верна
                # Для TerminalNodeImpl используем .symbol для получения токена
                pos = self._position_from_token(op_token.symbol if hasattr(op_token, 'symbol') else ctx.start)
                raise KumirRuntimeError(f"Неизвестный оператор отношения: {op_text}", 
                                      line_index=pos[0], column_index=pos[1])
        
        return result
    def visitAdditiveExpression(self, ctx: KumirParser.AdditiveExpressionContext) -> KumirValue:
        """Обрабатывает аддитивные выражения (например, expr + expr или expr - expr)"""

        # Проверяем, есть ли бинарная операция (число элементов в контексте)
        multiplicative_expressions = ctx.multiplicativeExpression()
        
        if len(multiplicative_expressions) == 1:
            # Простой случай: нет операции, просто делегируем дальше
            return self.visit(multiplicative_expressions[0])
          # Есть операции: вычисляем слева направо
        result = self.visit(multiplicative_expressions[0])
        
        for i in range(1, len(multiplicative_expressions)):
            op_token = ctx.getChild(2*i - 1)  # Операторы находятся между выражениями
            right = self.visit(multiplicative_expressions[i])
            
            # result и right гарантированно KumirValue согласно типизации
            op_text = op_token.getText()
            actual_token = self._get_token_from_node(op_token)
            
            if op_text == '+':
                # Сложение: числа или строки (ЛИТ и СИМ)
                if ((result.kumir_type == KumirType.STR.value or result.kumir_type == KumirType.CHAR.value) and 
                    (right.kumir_type == KumirType.STR.value or right.kumir_type == KumirType.CHAR.value)):
                    result = KumirValue(value=str(result.value) + str(right.value), kumir_type=KumirType.STR.value)
                elif ((result.kumir_type == KumirType.INT.value or result.kumir_type == KumirType.REAL.value) and 
                      (right.kumir_type == KumirType.INT.value or right.kumir_type == KumirType.REAL.value)):
                    if result.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value:
                        result = KumirValue(value=result.value + right.value, kumir_type=KumirType.INT.value)
                    else:
                        result = KumirValue(value=float(result.value) + float(right.value), kumir_type=KumirType.REAL.value)
                else:
                    raise KumirTypeError(
                        f"Операция сложения не применима к типам '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=actual_token.line, column_index=actual_token.column
                    )
            elif op_text == '-':
                # Вычитание: только числа
                if ((result.kumir_type == KumirType.INT.value or result.kumir_type == KumirType.REAL.value) and 
                    (right.kumir_type == KumirType.INT.value or right.kumir_type == KumirType.REAL.value)):
                    if result.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value:
                        result = KumirValue(value=result.value - right.value, kumir_type=KumirType.INT.value)
                    else:
                        result = KumirValue(value=float(result.value) - float(right.value), kumir_type=KumirType.REAL.value)
                else:
                    raise KumirTypeError(
                        f"Операция вычитания не применима к типам '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=actual_token.line, column_index=actual_token.column
                    )
            else:
                raise KumirEvalError(f"Неизвестный аддитивный оператор: {op_text}", 
                                   line_index=actual_token.line, column_index=actual_token.column)
        
        return result

    def visitMultiplicativeExpression(self, ctx: KumirParser.MultiplicativeExpressionContext) -> KumirValue:
        """Обрабатывает мультипликативные выражения"""
        
        # Проверяем, есть ли бинарная операция
        power_expressions = ctx.powerExpression()
        
        if len(power_expressions) == 1:
            # Простой случай: нет операции, просто делегируем дальше
            return self.visit(power_expressions[0])
        
        # Есть операции: вычисляем слева направо
        result = self.visit(power_expressions[0])
        
        for i in range(1, len(power_expressions)):
            op_token = ctx.getChild(2*i - 1)  # Операторы находятся между выражениями
            right = self.visit(power_expressions[i])
            
            op_text = op_token.getText()
            actual_token = self._get_token_from_node(op_token)
            
            if op_text == '*':
                # Умножение: только числа
                # Нормализуем типы для сравнения
                result_type_normalized = result.kumir_type
                right_type_normalized = right.kumir_type
                
                # Извлекаем базовые Python-значения из KumirValue объектов
                result_value = result.value
                if isinstance(result_value, KumirValue):
                    result_value = result_value.value
                
                right_value = right.value
                if isinstance(right_value, KumirValue):
                    right_value = right_value.value
                
                if ((result_type_normalized == KumirType.INT.value or result_type_normalized == KumirType.REAL.value) and
                    (right_type_normalized == KumirType.INT.value or right_type_normalized == KumirType.REAL.value)):
                    if result_type_normalized == KumirType.INT.value and right_type_normalized == KumirType.INT.value:
                        result = KumirValue(value=result_value * right_value, kumir_type=KumirType.INT.value)
                    else:
                        result = KumirValue(value=float(result_value) * float(right_value), kumir_type=KumirType.REAL.value)
                else:
                    raise KumirTypeError(
                        f"Операция умножения не применима к типам '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=actual_token.line, column_index=actual_token.column
                    )
            elif op_text == '/':
                # Обычное деление
                if ((result.kumir_type == KumirType.INT.value or result.kumir_type == KumirType.REAL.value) and
                    (right.kumir_type == KumirType.INT.value or right.kumir_type == KumirType.REAL.value)):
                    if float(right.value) == 0:
                        raise KumirEvalError("Деление на ноль.", line_index=actual_token.line, column_index=actual_token.column)
                    result = KumirValue(value=float(result.value) / float(right.value), kumir_type=KumirType.REAL.value)
                else:
                    raise KumirTypeError(
                        f"Операция деления не применима к типам '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=actual_token.line, column_index=actual_token.column
                    )
            elif op_text == 'div':
                # Целочисленное деление
                if (result.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value):
                    if right.value == 0:
                        raise KumirEvalError("Деление на ноль (div).", line_index=actual_token.line, column_index=actual_token.column)
                    result = KumirValue(value=result.value // right.value, kumir_type=KumirType.INT.value)
                else:
                    raise KumirTypeError(
                        f"Операция div применима только к целым числам, получены типы '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=actual_token.line, column_index=actual_token.column
                    )
            elif op_text == 'mod':
                # Остаток от деления
                if (result.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value):
                    if right.value == 0:
                        raise KumirEvalError("Деление на ноль (mod).", line_index=actual_token.line, column_index=actual_token.column)
                    result = KumirValue(value=result.value % right.value, kumir_type=KumirType.INT.value)
                else:
                    raise KumirTypeError(
                        f"Операция mod применима только к целым числам, получены типы '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=actual_token.line, column_index=actual_token.column
                    )
            else:
                raise KumirEvalError(f"Неизвестный мультипликативный оператор: {op_text}", 
                                   line_index=actual_token.line, column_index=actual_token.column)
        
        return result

    # Метод для обработки степенных выражений
    def visitPowerExpression(self, ctx: KumirParser.PowerExpressionContext) -> KumirValue:
        # PowerExpression: unaryExpression (POWER powerExpression)?
        unary_expr = self.visit(ctx.unaryExpression())
        if ctx.POWER():
            power_expr = self.visit(ctx.powerExpression())
            # Реализуем возведение в степень (правоассоциативно)
            base = unary_expr.value
            exponent = power_expr.value
            # Если оба int — результат int, иначе float
            if unary_expr.kumir_type == KumirType.INT.value and power_expr.kumir_type == KumirType.INT.value:
                result_value = int(base ** exponent)
                result_type = KumirType.INT.value
            else:
                result_value = float(base) ** float(exponent)
                result_type = KumirType.REAL.value
            return KumirValue(result_value, result_type)
        else:
            return unary_expr
    
    # Метод для обработки постфиксных выражений
    def visitPostfixExpression(self, ctx: KumirParser.PostfixExpressionContext) -> KumirValue:
        # PostfixExpression: primaryExpression (postfixOperator)*
        
        # Сначала получаем primary expression
        primary_expr = self.visit(ctx.primaryExpression())
        
        # Проверяем, есть ли дочерние элементы (постфиксные операторы)
        if ctx.getChildCount() == 1:
            # Только primaryExpression, без постфиксов
            return primary_expr
        
        # Обрабатываем постфиксные операторы
        for i in range(1, ctx.getChildCount()):
            child = ctx.getChild(i)
            
            # Если это LPAREN - значит вызов функции
            if hasattr(child, 'symbol') and child.symbol.type == KumirParser.LPAREN:
                # Это вызов функции - обрабатываем аргументы
                # Следующий элемент должен быть argumentList или RPAREN
                args = []
                arg_expressions = []
                arg_list_idx = i + 1
                if arg_list_idx < ctx.getChildCount():
                    next_child = ctx.getChild(arg_list_idx)
                    # Если есть argumentList, обрабатываем аргументы
                    if hasattr(next_child, 'expression') and callable(getattr(next_child, 'expression')):
                        # Это argumentList - сохраняем исходные выражения и вычисляем значения
                        arg_expressions = self._get_argument_expressions(next_child)
                        args = self._evaluate_argument_list(next_child)
                
                # primary_expr должно содержать имя функции
                if hasattr(primary_expr, 'value') and isinstance(primary_expr.value, str):
                    func_name = primary_expr.value
                    return self._call_function(func_name, args, arg_expressions, ctx)
                else:
                    pos = self._position_from_token(self._get_token_for_position(ctx))
                    raise KumirEvalError(f"Невозможно вызвать функцию: {primary_expr}", line_index=pos[0], column_index=pos[1])
            
            # Обработка массивов (LBRACK ... RBRACK)
            if hasattr(child, 'symbol') and child.symbol.type == KumirParser.LBRACK:
                # Это доступ к массиву - ищем indexList и RBRACK
                if i + 2 >= ctx.getChildCount():
                    pos = self._position_from_token(child.symbol)
                    raise KumirSyntaxError("Некорректная структура доступа к элементу таблицы после '['.", line_index=pos[0], column_index=pos[1])
                
                index_list_ctx = ctx.getChild(i + 1)
                rbrack_child = ctx.getChild(i + 2)
                
                if not (hasattr(index_list_ctx, 'getRuleIndex') and 
                        index_list_ctx.getRuleIndex() == KumirParser.RULE_indexList):
                    pos = self._position_from_token(child.symbol)
                    raise KumirSyntaxError("Ожидается список индексов после '['.", line_index=pos[0], column_index=pos[1])
                
                if not (hasattr(rbrack_child, 'symbol') and 
                        rbrack_child.symbol.type == KumirParser.RBRACK):
                    pos = self._position_from_token(child.symbol)
                    raise KumirSyntaxError("Ожидается ']' после списка индексов.", line_index=pos[0], column_index=pos[1])
                
                # Вычисляем индексы
                indices = []
                for expr_ctx in index_list_ctx.expression():
                    idx_val = self.visit(expr_ctx)
                    if idx_val.kumir_type != KumirType.INT.value:
                        pos = self._position_from_token(self._get_token_for_position(expr_ctx))
                        var_name = primary_expr.value if hasattr(primary_expr, 'value') and isinstance(primary_expr.value, str) else "переменная"
                        raise KumirEvalError(
                            f"Индекс для '{var_name}' должен быть целым числом, получено: {idx_val.value}",
                            line_index=pos[0], column_index=pos[1]
                        )
                    indices.append(idx_val.value)
                
                # Обрабатываем доступ к элементам массива или строки
                if (primary_expr.kumir_type == KumirType.STR.value and 
                    isinstance(primary_expr.value, KumirTableVar)):
                    # Это строковый массив - обрабатываем как массив
                    table_var = primary_expr.value
                    try:
                        element_value = table_var.get_value(tuple(indices), index_list_ctx)
                        return element_value
                    except Exception as e:
                        pos = self._position_from_token(self._get_token_for_position(index_list_ctx))
                        raise KumirEvalError(
                            f"Ошибка при доступе к элементу строкового массива: {e}",
                            line_index=pos[0], column_index=pos[1]
                        )
                        
                elif primary_expr.kumir_type == KumirType.STR.value:
                    # Доступ к символам обычной строки (не массива)
                    string_value = primary_expr.value
                    actual_string = string_value
                    
                    if len(indices) == 1:
                        # Доступ к одному символу
                        kumir_idx = indices[0]
                        if kumir_idx < 1 or kumir_idx > len(actual_string):
                            pos = self._position_from_token(self._get_token_for_position(index_list_ctx))
                            raise KumirIndexError(
                                f"Индекс символа {kumir_idx} вне допустимого диапазона [1..{len(actual_string)}]",
                                line_index=pos[0], column_index=pos[1]
                            )
                        py_idx = kumir_idx - 1  # КуМир 1-based -> Python 0-based
                        char_value = actual_string[py_idx]
                        return KumirValue(value=char_value, kumir_type=KumirType.CHAR.value)
                        
                    elif len(indices) == 2:
                        # Срез строки
                        k_idx1, k_idx2 = indices[0], indices[1]
                        if k_idx1 < 1 or k_idx2 < k_idx1:
                            pos = self._position_from_token(self._get_token_for_position(index_list_ctx))
                            raise KumirIndexError(
                                f"Неверные границы среза. Начальный индекс ({k_idx1}) должен быть >= 1, конечный ({k_idx2}) >= начального",
                                line_index=pos[0], column_index=pos[1]
                            )
                        
                        py_start = k_idx1 - 1
                        py_end = min(k_idx2, len(actual_string))
                        if py_start >= len(actual_string):
                            slice_value = ""
                        else:
                            slice_value = actual_string[py_start:py_end]
                        return KumirValue(value=slice_value, kumir_type=KumirType.STR.value)
                        
                    else:
                        pos = self._position_from_token(self._get_token_for_position(index_list_ctx))
                        raise KumirIndexError(
                            f"Для строки ожидается 1 индекс (символ) или 2 индекса (срез). Получено {len(indices)}",
                            line_index=pos[0], column_index=pos[1]
                        )
                        
                elif hasattr(primary_expr.value, 'get_value'):
                    # Это объект массива (KumirTableVar)
                    table_var = primary_expr.value
                    try:
                        element_value = table_var.get_value(tuple(indices), index_list_ctx)
                        return element_value
                    except Exception as e:
                        pos = self._position_from_token(self._get_token_for_position(index_list_ctx))
                        raise KumirEvalError(
                            f"Ошибка при доступе к элементу массива: {e}",
                            line_index=pos[0], column_index=pos[1]
                        )
                        
                else:
                    pos = self._position_from_token(self._get_token_for_position(ctx))
                    raise KumirEvalError(
                        f"Невозможно применить индексы к выражению типа {type(primary_expr)}",
                        line_index=pos[0], column_index=pos[1]
                    )
                
                # Пропускаем обработанные токены (LBRACK, indexList, RBRACK)
                i += 2
        
        return primary_expr
      # Метод для обработки первичных выражений
    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext) -> KumirValue:
        # PrimaryExpression может быть literal, identifier, parenthesizedExpr и т.д.
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.qualifiedIdentifier():
            # TODO: Обработка переменных и идентификаторов
            return self.visit(ctx.qualifiedIdentifier())
        elif ctx.RETURN_VALUE():
            # Обработка ключевого слова 'знач' - обращение к возвращаемому значению функции
            try:
                var_info, _ = self.main_visitor.scope_manager.find_variable('__знач__')
                if var_info is None:
                    pos = self._position_from_token(self._get_token_for_position(ctx))
                    raise KumirRuntimeError("Переменная '__знач__' не найдена.", line_index=pos[0], column_index=pos[1])
                return var_info['value']
            except Exception as e:
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirRuntimeError(f"Ошибка при обращении к 'знач': {e}", line_index=pos[0], column_index=pos[1])
        elif ctx.expression():
            # Выражение в скобках
            return self.visit(ctx.expression())
        elif ctx.arrayLiteral():
            # Обработка литералов массивов
            return self.visitArrayLiteral(ctx.arrayLiteral())
        else:
            pos = self._position_from_token(self._get_token_for_position(ctx))
            raise KumirNotImplementedError(f"Неизвестный тип первичного выражения: {ctx.getText()}", line_index=pos[0], column_index=pos[1])

    def visitQualifiedIdentifier(self, ctx: KumirParser.QualifiedIdentifierContext) -> KumirValue:
        """Обрабатывает идентификатор (имя переменной или функции) и возвращает её значение"""
        # qualifiedIdentifier: ID
        var_name = ctx.ID().getText()
        
        # Сначала проверяем, это встроенная функция
        if self._is_builtin_function(var_name):
            # Возвращаем имя функции как строковое значение для дальнейшей обработки в postfixExpression
            return KumirValue(var_name, KumirType.STR.value)
        
        # ДОБАВЛЕНО: Проверяем, это пользовательская функция в AlgorithmManager
        if hasattr(self.main_visitor, 'algorithm_manager') and self.main_visitor.algorithm_manager.has_algorithm(var_name):
            algorithm_def = self.main_visitor.algorithm_manager.get_algorithm(var_name)
            if algorithm_def and algorithm_def.is_function:
                # Это пользовательская функция - проверяем количество параметров
                if algorithm_def and len(algorithm_def.parameters) == 0:
                    # Функция без аргументов - вызываем её сразу
                    return self.main_visitor.call_user_function(var_name, [], ctx)
                else:
                    # Функция с аргументами - возвращаем имя для обработки в postfixExpression
                    return KumirValue(var_name, KumirType.STR.value)
            else:
                # Это процедура - возвращаем имя для обработки в postfixExpression
                return KumirValue(var_name, KumirType.STR.value)
          # Ищем переменную в scope_manager (возвращает кортеж (var_info, scope))
        var_info, _scope = self.scope_manager.find_variable(var_name)
        if var_info is None:
            pos = self._position_from_token(ctx.ID().symbol)
            raise KumirNameError(f"Переменная '{var_name}' не объявлена.", line_index=pos[0], column_index=pos[1])
          # var_info это словарь с ключами 'value', 'kumir_type', etc.
        value = var_info['value']
        kumir_type = var_info['kumir_type']
        
        # Для массивов (таблиц) возвращаем специальный KumirValue, содержащий KumirTableVar
        if hasattr(value, 'get_value') and hasattr(value, 'set_value'):  # Это KumirTableVar
            # Создаем KumirValue, который содержит ссылку на объект массива
            return KumirValue(value=value, kumir_type=kumir_type.value if hasattr(kumir_type, 'value') else str(kumir_type))
        
        # value уже должно быть KumirValue, просто возвращаем его
        if isinstance(value, KumirValue):
            return value
        else:
            # Если по какой-то причине value не KumirValue, создаем его
            # kumir_type это KumirType enum, нужно взять .value для строкового представления
            kumir_type_str = kumir_type.value if hasattr(kumir_type, 'value') else str(kumir_type)
            return KumirValue(value, kumir_type_str)

    def visitExpression(self, ctx: KumirParser.ExpressionContext) -> KumirValue:
        """Обрабатывает Expression узел, делегируя обработку дальше по дереву"""
        # Expression -> logicalOrExpression, делегируем обработку
        return self.visit(ctx.logicalOrExpression())    # ====== МЕТОДЫ ДЛЯ ОБРАБОТКИ ВСТРОЕННЫХ ФУНКЦИЙ ======
    
    def _is_builtin_function(self, name: str) -> bool:
        """Проверяет, является ли имя встроенной функцией"""
        # Проверяем в новом реестре встроенных функций
        if hasattr(self.main_visitor, 'builtin_function_handler'):
            return name in self.main_visitor.builtin_function_handler.functions
        
        # Fallback к старому списку для совместимости
        builtin_functions = {
            'div', 'mod', 'abs', 'sqrt', 'sin', 'cos', 'tan', 'arctan', 'sign',
            'irand', 'rand', 'цел', 'вещ', 'длина', 'позиция'
        }
        return name in builtin_functions
    
    def _evaluate_argument_list(self, arg_list_ctx) -> list[KumirValue]:
        """Вычисляет список аргументов функции"""
        args = []
        if hasattr(arg_list_ctx, 'expression') and callable(getattr(arg_list_ctx, 'expression')):
            # argumentList: expression (COMMA expression)*
            expressions = arg_list_ctx.expression()
            if isinstance(expressions, list):
                for expr in expressions:
                    result = self.visit(expr)
                    args.append(result)
            else:
                # Только один аргумент
                result = self.visit(expressions)
                args.append(result)
        return args
    
    def _get_argument_expressions(self, arg_list_ctx):
        """Извлекает исходные AST-узлы аргументов без их вычисления"""
        expressions = []
        if hasattr(arg_list_ctx, 'expression') and callable(getattr(arg_list_ctx, 'expression')):
            # argumentList: expression (COMMA expression)*
            expr_nodes = arg_list_ctx.expression()
            if isinstance(expr_nodes, list):
                expressions = expr_nodes
            else:
                # Только один аргумент
                expressions = [expr_nodes]
        return expressions

    def _call_function(self, func_name: str, args: list[KumirValue], arg_expressions: list[Any], ctx: Any) -> KumirValue:
        """Вызывает встроенную функцию с аргументами"""
        
        # Обрабатываем арифметические встроенные функции
        if func_name == 'div':
            if len(args) != 2:
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirArgumentError(f"Функция 'div' ожидает 2 аргумента, получено {len(args)}", line_index=pos[0], column_index=pos[1])
            
            a = args[0]
            b = args[1]
              # Проверяем типы
            if not isinstance(a.value, int) or not isinstance(b.value, int):
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirArgumentError(f"Функция 'div' применима только к целым числам", line_index=pos[0], column_index=pos[1])
            
            if b.value == 0:
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirEvalError("Деление на ноль (div)", line_index=pos[0], column_index=pos[1])
            
            result = a.value // b.value
            return KumirValue(result, KumirType.INT.value)
        
        elif func_name == 'mod':
            if len(args) != 2:
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirArgumentError(f"Функция 'mod' ожидает 2 аргумента, получено {len(args)}", line_index=pos[0], column_index=pos[1])
            
            a = args[0]
            b = args[1]
              # Проверяем типы
            if not isinstance(a.value, int) or not isinstance(b.value, int):
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirArgumentError(f"Функция 'mod' применима только к целым числам", line_index=pos[0], column_index=pos[1])
            
            if b.value == 0:
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirEvalError("Деление на ноль (mod)", line_index=pos[0], column_index=pos[1])
            
            result = a.value % b.value
            return KumirValue(result, KumirType.INT.value)
        
        elif func_name == 'abs':
            if len(args) != 1:
                pos = self._position_from_token(self._get_token_for_position(ctx))
                raise KumirArgumentError(f"Функция 'abs' ожидает 1 аргумент, получено {len(args)}", line_index=pos[0], column_index=pos[1])
            
            a = args[0]
            result = abs(a.value)
            return KumirValue(result, a.kumir_type)          # TODO: Добавить остальные встроенные функции при необходимости        # ДОБАВЛЕНО: Проверяем встроенные функции через builtin_function_handler
        
        # Сначала проверяем встроенные функции
        if hasattr(self.main_visitor, 'builtin_function_handler'):
            builtin_handler = self.main_visitor.builtin_function_handler
            if func_name.lower() in builtin_handler.functions:
                try:
                    # Получаем информацию о функции для определения типов параметров
                    func_info = builtin_handler.functions[func_name.lower()]
                    param_modes = func_info.get('param_modes', [])
                    
                    # Подготавливаем аргументы согласно param_modes
                    raw_args = []
                    for i, arg in enumerate(args):
                        # Определяем режим параметра
                        if i < len(param_modes) and len(param_modes) > 0:
                            # Есть информация о режимах для текущего количества аргументов
                            if len(args) <= len(param_modes):
                                mode_list = param_modes[len(args) - 1]  # Выбираем режимы для нужного количества аргументов
                                if i < len(mode_list):
                                    param_mode = mode_list[i]
                                else:
                                    param_mode = 'арг'  # по умолчанию
                            else:
                                param_mode = 'арг'  # по умолчанию
                        else:
                            param_mode = 'арг'  # по умолчанию
                        
                        if param_mode == 'рез':
                            # Для параметров "рез" нужно передать имя переменной
                            if i < len(arg_expressions):
                                var_name = self._extract_variable_name(arg_expressions[i])
                                raw_args.append(var_name)
                            else:
                                # Ошибка - не хватает выражений
                                pos = self._position_from_token(self._get_token_for_position(ctx))
                                raise KumirArgumentError(f"Недостаточно аргументов для функции '{func_name}'", line_index=pos[0], column_index=pos[1])
                        else:
                            # Для параметров "арг" передаем значение
                            raw_args.append(arg.value)
                    
                    # Вызываем встроенную функцию
                    result = builtin_handler.call_function(func_name, raw_args, ctx)
                    
                    # Оборачиваем результат в KumirValue, если нужно
                    if not isinstance(result, KumirValue):
                        if isinstance(result, int):
                            result = KumirValue(result, KumirType.INT.value)
                        elif isinstance(result, float):
                            result = KumirValue(result, KumirType.REAL.value)
                        elif isinstance(result, str):
                            result = KumirValue(result, KumirType.STR.value)
                        elif isinstance(result, bool):
                            result = KumirValue(result, KumirType.BOOL.value)
                        else:
                            result = KumirValue(result, "unknown")
                    
                    return result
                except Exception as e:
                    pos = self._position_from_token(self._get_token_for_position(ctx))
                    raise KumirEvalError(f"Ошибка при вызове функции '{func_name}': {str(e)}", line_index=pos[0], column_index=pos[1])
        
        # Потом проверяем пользовательские функции в AlgorithmManager
        
        if hasattr(self.main_visitor, 'algorithm_manager'):
            
            if self.main_visitor.algorithm_manager.has_algorithm(func_name):
                algorithm_def = self.main_visitor.algorithm_manager.get_algorithm(func_name)
                
                if algorithm_def and algorithm_def.is_function:
                    # Это пользовательская функция - вызываем её через main visitor
                    result = self.main_visitor.call_user_function(func_name, args, ctx)
                    return result
                else:
                    # Это процедура, а не функция - ошибка
                    pos = self._position_from_token(self._get_token_for_position(ctx))
                    raise KumirTypeError(f"'{func_name}' является процедурой, а не функцией, и не может использоваться в выражении", line_index=pos[0], column_index=pos[1])
        
        # Если дошли до сюда - неизвестная функция
        pos = self._position_from_token(self._get_token_for_position(ctx))
        raise KumirNotImplementedError(f"Встроенная функция '{func_name}' пока не реализована", line_index=pos[0], column_index=pos[1])

    def visit(self, tree) -> KumirValue:
        """Общий метод visit для обхода AST дерева"""
        result = super().visit(tree)
        return result

    def visitArrayLiteral(self, ctx: KumirParser.ArrayLiteralContext) -> KumirValue:
        """Обрабатывает литералы массивов (например, {1, 2, 3})"""
        expression_list = ctx.expressionList()
        
        if expression_list is None:
            # Пустой массив
            return KumirValue(value=[], kumir_type=KumirType.TABLE.value)
        
        # Вычисляем все выражения в массиве
        elements = []
        expressions = expression_list.expression()
        
        for expr in expressions:
            element_value = self.visit(expr)
            elements.append(element_value.value)
        
        return KumirValue(value=elements, kumir_type=KumirType.TABLE.value)
    
    def _extract_variable_name(self, expr_ctx):
        """Извлекает имя переменной из AST-узла выражения"""
        # Проверяем, является ли это простым идентификатором
        if hasattr(expr_ctx, 'getRuleIndex') and expr_ctx.getRuleIndex() == KumirParser.RULE_logicalOrExpression:
            # Идем по цепочке: logicalOrExpression -> logicalAndExpression -> ... -> qualifiedIdentifier
            return self._extract_variable_name_recursive(expr_ctx)
        else:
            # Попробуем извлечь текст напрямую
            text = expr_ctx.getText()
            return text
    
    def _extract_variable_name_recursive(self, ctx):
        """Рекурсивно извлекает имя переменной из сложных выражений"""
        # Если есть только один дочерний элемент, идем глубже
        if ctx.getChildCount() == 1:
            child = ctx.getChild(0)
            if hasattr(child, 'getRuleIndex'):
                return self._extract_variable_name_recursive(child)
            elif hasattr(child, 'getText'):
                return child.getText()
        
        # Если это qualifiedIdentifier
        if hasattr(ctx, 'getRuleIndex') and ctx.getRuleIndex() == KumirParser.RULE_qualifiedIdentifier:
            if hasattr(ctx, 'ID') and ctx.ID():
                return ctx.ID().getText()
        
        # Если это primaryExpression с qualifiedIdentifier
        if hasattr(ctx, 'qualifiedIdentifier') and ctx.qualifiedIdentifier():
            return self._extract_variable_name_recursive(ctx.qualifiedIdentifier())
        
        # Fallback - просто возвращаем текст
        return ctx.getText()
