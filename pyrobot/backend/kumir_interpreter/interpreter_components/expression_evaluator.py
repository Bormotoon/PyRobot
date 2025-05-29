# pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py
# Этот файл будет содержать логику вычисения выражений для интерпретатора КуМира.

from __future__ import annotations
from antlr4 import ParserRuleContext, Token
from typing import Any, List, Tuple, Optional, Union
from antlr4.tree.Tree import TerminalNode
from ..generated.KumirParser import KumirParser # Оставляем только этот импорт для KumirParser
from .scope_manager import ScopeManager
from .procedure_manager import ProcedureManager
from ..generated.KumirParserVisitor import KumirParserVisitor
from ..generated.KumirParser import KumirParser
from .scope_manager import ScopeManager # Исправленный импорт ScopeManager
from ..kumir_datatypes import KumirValue, KumirType # Добавлено
from ..kumir_exceptions import KumirEvalError, KumirTypeError, KumirNameError, KumirRuntimeError, KumirNotImplementedError # Добавлены KumirRuntimeError, KumirNotImplementedError
import sys # Добавлено


class ExpressionEvaluator(KumirParserVisitor):
    def __init__(self, main_visitor: 'KumirInterpreterVisitor', scope_manager: ScopeManager, procedure_manager: ProcedureManager): # Добавлен main_visitor
        self.main_visitor = main_visitor # Сохраняем main_visitor
        self.scope_manager = scope_manager
        self.procedure_manager = procedure_manager

    @staticmethod
    def _position_from_token(token: Token) -> Tuple[int, int]:
        """Извлекает номер строки и столбца из токена ANTLR."""
        return token.line, token.column

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
        if not isinstance(value, KumirValue):
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
        # if ctx.expression():        #     return self.visit(ctx.expression())
        pass # Обычно не используется в ExpressionEvaluator

    def visitLiteral(self, ctx: KumirParser.LiteralContext) -> KumirValue:
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        text = ctx.getText()
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] text = '{text}' !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] ctx.INTEGER() = {ctx.INTEGER()} !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] ctx.REAL() = {ctx.REAL()} !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] ctx.STRING() = {ctx.STRING()} !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] ctx.CHAR_LITERAL() = {ctx.CHAR_LITERAL()} !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] ctx.TRUE() = {ctx.TRUE()} !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] ctx.FALSE() = {ctx.FALSE()} !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visitLiteral] ctx.NEWLINE_CONST() = {ctx.NEWLINE_CONST()} !!!", file=sys.stderr)
        
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


    # UnaryMinusExpression -> UnaryPlusMinusExpr
    def visitUnaryPlusMinusExpr(self, ctx: KumirParser.UnaryPlusMinusExprContext) -> KumirValue:
        operand_val = self.visit(ctx.unaryExpression())
        op_token = None

        if ctx.MINUS():
            op_token = ctx.MINUS().getSymbol() # ANTLR TerminalNode.getSymbol() возвращает токен
            self._check_operand_type(operand_val, [KumirType.INT, KumirType.REAL], "унарный минус", op_token)
            if operand_val.kumir_type == KumirType.INT.value:
                return KumirValue(value=-operand_val.value, kumir_type=KumirType.INT.value)
            elif operand_val.kumir_type == KumirType.REAL.value:
                return KumirValue(value=-operand_val.value, kumir_type=KumirType.REAL.value)
        elif ctx.PLUS():
            op_token = ctx.PLUS().getSymbol()
            self._check_operand_type(operand_val, [KumirType.INT, KumirType.REAL], "унарный плюс", op_token)
            # Для унарного плюса значение не меняется, но тип проверяем
            return operand_val
        
        # Сюда не должны попасть, если грамматика корректна и ctx это UnaryPlusMinusExprContext
        # Но для безопасности, если вдруг op_token не был установлен (например, нет ни PLUS, ни MINUS)
        # Хотя грамматика unaryExpression: (PLUS | MINUS) unaryExpression # UnaryPlusMinusExpr
        # гарантирует наличие одного из них.
        # Если бы это было возможно, то:
        # raise KumirRuntimeError(ctx.start.line, ctx.start.column, "Неизвестный унарный оператор в UnaryPlusMinusExpr")
        return operand_val # Возвращаем operand_val, если это был унарный плюс

    def visitUnaryNotExpr(self, ctx: KumirParser.UnaryNotExprContext) -> KumirValue:
        op_token = ctx.NOT().getSymbol()
        operand_val = self.visit(ctx.unaryExpression())

        self._check_operand_type(operand_val, [KumirType.BOOL], "логическое НЕ", op_token)
        return KumirValue(value=not operand_val.value, kumir_type=KumirType.BOOL.value)

    # Посещение узла выражения с умножением/делением/остатком
    def visitMultiplicativeExpr(self, ctx: KumirParser.MultiplicativeExprContext) -> KumirValue:
        left = self._visit_operand(ctx.expression(0))
        right = self._visit_operand(ctx.expression(1))
        op_token = ctx.op # op это токен

        # Замечание: _visit_operand уже гарантирует, что left и right это KumirValue
        # поэтому явная проверка isinstance здесь не нужна, но оставлена для ясности
        if not (isinstance(left, KumirValue) and isinstance(right, KumirValue)):
            pos = self._position_from_token(op_token)
            raise KumirRuntimeError(
                f"Внутренняя ошибка: операнды не являются KumirValue (типы: {type(left).__name__}, {type(right).__name__}).",
                line_index=pos[0]-1, 
                column_index=pos[1]
            )

        if op_token.type == KumirParser.MUL:
            self._check_operand_type(left, [KumirType.INT, KumirType.REAL], "*", op_token)
            self._check_operand_type(right, [KumirType.INT, KumirType.REAL], "*", op_token)
            if left.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value:
                result = left.value * right.value
                return KumirValue(value=result, kumir_type=KumirType.INT.value)
            else:
                # Приведение к float для всех остальных случаев (INT*REAL, REAL*INT, REAL*REAL)
                result = float(left.value) * float(right.value)
                return KumirValue(value=result, kumir_type=KumirType.REAL.value)
        elif op_token.type == KumirParser.DIV:
            self._check_operand_type(left, [KumirType.INT, KumirType.REAL], "/", op_token)
            self._check_operand_type(right, [KumirType.INT, KumirType.REAL], "/", op_token)
            if float(right.value) == 0:
                raise KumirEvalError("Деление на ноль.", line_index=op_token.line -1, column_index=op_token.column)
            
            # Всегда вещественное деление, согласно документации Кумира
            result = float(left.value) / float(right.value)
            return KumirValue(value=result, kumir_type=KumirType.REAL.value)

        elif op_token.text == 'div': # Целочисленное деление
            self._check_operand_type(left, [KumirType.INT], "div", op_token)
            self._check_operand_type(right, [KumirType.INT], "div", op_token)
            if right.value == 0:
                raise KumirEvalError("Деление на ноль (div).", line_index=op_token.line - 1, column_index=op_token.column)
            result = left.value // right.value
            return KumirValue(value=result, kumir_type=KumirType.INT.value)
            
        elif op_token.text == 'mod': # Остаток от деления
            self._check_operand_type(left, [KumirType.INT], "mod", op_token)
            self._check_operand_type(right, [KumirType.INT], "mod", op_token)
            if right.value == 0:
                raise KumirEvalError("Деление на ноль (mod).", line_index=op_token.line - 1, column_index=op_token.column)
            result = left.value % right.value
            return KumirValue(value=result, kumir_type=KumirType.INT.value)
        else:
            # Эта ветка по идее не должна достигаться, если грамматика верна
            raise KumirEvalError(f"Неизвестный мультипликативный оператор: {op_token.text}", line_index=op_token.line - 1, column_index=op_token.column)

    # Посещение узла выражения со сложением/вычитанием
    def visitAdditiveExpr(self, ctx: KumirParser.AdditiveExprContext) -> KumirValue:
        left = self._visit_operand(ctx.expression(0))
        right = self._visit_operand(ctx.expression(1))
        op_token = ctx.op # op это токен

        # Замечание: _visit_operand уже гарантирует, что left и right это KumirValue
        if not (isinstance(left, KumirValue) and isinstance(right, KumirValue)):
            pos = self._position_from_token(op_token)
            raise KumirRuntimeError(
                f"Внутренняя ошибка: операнды не являются KumirValue (типы: {type(left).__name__}, {type(right).__name__}).",
                line_index=pos[0]-1,
                column_index=pos[1]
            )

        if op_token.type == KumirParser.PLUS:
            # Для сложения допустимы: ЦЕЛ+ЦЕЛ, ВЕЩ+ВЕЩ, ЦЕЛ+ВЕЩ, ВЕЩ+ЦЕЛ, ЛИТ+ЛИТ
            if left.kumir_type == KumirType.STR.value and right.kumir_type == KumirType.STR.value:
                result = str(left.value) + str(right.value)
                return KumirValue(value=result, kumir_type=KumirType.STR.value)
            elif (left.kumir_type == KumirType.INT.value or left.kumir_type == KumirType.REAL.value) and \
                 (right.kumir_type == KumirType.INT.value or right.kumir_type == KumirType.REAL.value):
                if left.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value:
                    result = left.value + right.value
                    return KumirValue(value=result, kumir_type=KumirType.INT.value)
                else:
                    # Приведение к float для всех остальных случаев (INT+REAL, REAL+INT, REAL+REAL)
                    result = float(left.value) + float(right.value)
                    return KumirValue(value=result, kumir_type=KumirType.REAL.value)
            else: # Несовместимые типы для сложения (например, число + строка)
                raise KumirTypeError(
                    f"Операция сложения '{op_token.text}' не применима к типам '{left.kumir_type}' и '{right.kumir_type}'.",
                    line_index=op_token.line - 1, column_index=op_token.column
                )
        elif op_token.type == KumirParser.MINUS:
            # Для вычитания: ЦЕЛ-ЦЕЛ, ВЕЩ-ВЕЩ, ЦЕЛ-ВЕЩ, ВЕЩ-ЦЕЛ. Строки не участвуют.
            if (left.kumir_type == KumirType.INT.value or left.kumir_type == KumirType.REAL.value) and \
               (right.kumir_type == KumirType.INT.value or right.kumir_type == KumirType.REAL.value):
                if left.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value:
                    result = left.value - right.value
                    return KumirValue(value=result, kumir_type=KumirType.INT.value)
                else:
                    # Приведение к float для всех остальных случаев (INT-REAL, REAL-INT, REAL-REAL)
                    result = float(left.value) - float(right.value)
                    return KumirValue(value=result, kumir_type=KumirType.REAL.value)
            else: # Несовместимые типы для вычитания (например, строка - число, или вычитание строк)
                raise KumirTypeError(
                    f"Операция вычитания '{op_token.text}' не применима к типам '{left.kumir_type}' и '{right.kumir_type}'.",
                    line_index=op_token.line - 1, column_index=op_token.column
                )
        else:
            # Эта ветка по идее не должна достигаться
            raise KumirEvalError(f"Неизвестный аддитивный оператор: {op_token.text}", line_index=op_token.line - 1, column_index=op_token.column)

    def visitLogicalOrExpression(self, ctx: KumirParser.LogicalOrExpressionContext) -> KumirValue:
        """Обрабатывает логическое ИЛИ выражение"""
        print(f"!!! [DEBUG ExpressionEvaluator.visitLogicalOrExpression] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        # Пока просто делегируем к следующему уровню
        return self.visit(ctx.logicalAndExpression(0))  # Берем первый элемент

    def visitLogicalAndExpression(self, ctx: KumirParser.LogicalAndExpressionContext) -> KumirValue:
        """Обрабатывает логическое И выражение"""
        print(f"!!! [DEBUG ExpressionEvaluator.visitLogicalAndExpression] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        # Пока просто делегируем к следующему уровню
        return self.visit(ctx.equalityExpression(0))  # Берем первый элемент

    def visitEqualityExpression(self, ctx: KumirParser.EqualityExpressionContext) -> KumirValue:
        """Обрабатывает выражения равенства"""
        print(f"!!! [DEBUG ExpressionEvaluator.visitEqualityExpression] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        # Пока просто делегируем к следующему уровню
        return self.visit(ctx.relationalExpression(0))  # Берем первый элемент    def visitRelationalExpression(self, ctx: KumirParser.RelationalExpressionContext) -> KumirValue:
        """Обрабатывает реляционные выражения"""
        print(f"!!! [DEBUG ExpressionEvaluator.visitRelationalExpression] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        
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
            
            if not (isinstance(result, KumirValue) and isinstance(right, KumirValue)):
                pos_err = self._position_from_token(op_token)
                raise KumirRuntimeError(
                    f"Внутренняя ошибка: операнды не являются KumirValue (типы: {type(result).__name__}, {type(right).__name__}).",
                    line_index=pos_err[0], 
                    column_index=pos_err[1]
                )

            op_text = op_token.getText()
            
            # TODO: Реализовать операции сравнения <, >, <=, >=
            # Пока просто делегируем дальше без операций
            pos = self._position_from_token(op_token)
            raise KumirNotImplementedError(f"Реляционная операция '{op_text}' пока не реализована.", 
                                         line_index=pos[0], column_index=pos[1])
        
        return result
    def visitAdditiveExpression(self, ctx: KumirParser.AdditiveExpressionContext) -> KumirValue:
        """Обрабатывает аддитивные выражения (например, expr + expr или expr - expr)"""
        print(f"!!! [DEBUG ExpressionEvaluator.visitAdditiveExpression] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)

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
            
            if not (isinstance(result, KumirValue) and isinstance(right, KumirValue)):
                # Для TerminalNodeImpl используем .symbol для получения токена
                pos_err = self._position_from_token(op_token.symbol if hasattr(op_token, 'symbol') else ctx.start)
                raise KumirRuntimeError(
                    f"Внутренняя ошибка: операнды не являются KumirValue (типы: {type(result).__name__}, {type(right).__name__}).",
                    line_index=pos_err[0], 
                    column_index=pos_err[1]
                )

            op_text = op_token.getText()
            
            if op_text == '+':
                # Сложение: числа или строки
                if result.kumir_type == KumirType.STR.value and right.kumir_type == KumirType.STR.value:
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
                        line_index=op_token.line, column_index=op_token.column
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
                        line_index=op_token.line, column_index=op_token.column
                    )
            else:
                raise KumirEvalError(f"Неизвестный аддитивный оператор: {op_text}", 
                                   line_index=op_token.line, column_index=op_token.column)
        
        return result

    def visitMultiplicativeExpression(self, ctx: KumirParser.MultiplicativeExpressionContext) -> KumirValue:
        """Обрабатывает мультипликативные выражения"""
        print(f"!!! [DEBUG ExpressionEvaluator.visitMultiplicativeExpression] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        
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
            
            if not (isinstance(result, KumirValue) and isinstance(right, KumirValue)):
                pos_err = self._position_from_token(op_token)
                raise KumirRuntimeError(
                    f"Внутренняя ошибка: операнды не являются KumirValue (типы: {type(result).__name__}, {type(right).__name__}).",
                    line_index=pos_err[0], 
                    column_index=pos_err[1]
                )

            op_text = op_token.getText()
            
            if op_text == '*':
                # Умножение: только числа
                if ((result.kumir_type == KumirType.INT.value or result.kumir_type == KumirType.REAL.value) and
                    (right.kumir_type == KumirType.INT.value or right.kumir_type == KumirType.REAL.value)):
                    if result.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value:
                        result = KumirValue(value=result.value * right.value, kumir_type=KumirType.INT.value)
                    else:
                        result = KumirValue(value=float(result.value) * float(right.value), kumir_type=KumirType.REAL.value)
                else:
                    raise KumirTypeError(
                        f"Операция умножения не применима к типам '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=op_token.line, column_index=op_token.column
                    )
            elif op_text == '/':
                # Обычное деление
                if ((result.kumir_type == KumirType.INT.value or result.kumir_type == KumirType.REAL.value) and
                    (right.kumir_type == KumirType.INT.value or right.kumir_type == KumirType.REAL.value)):
                    if float(right.value) == 0:
                        raise KumirEvalError("Деление на ноль.", line_index=op_token.line, column_index=op_token.column)
                    result = KumirValue(value=float(result.value) / float(right.value), kumir_type=KumirType.REAL.value)
                else:
                    raise KumirTypeError(
                        f"Операция деления не применима к типам '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=op_token.line, column_index=op_token.column
                    )
            elif op_text == 'div':
                # Целочисленное деление
                if (result.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value):
                    if right.value == 0:
                        raise KumirEvalError("Деление на ноль (div).", line_index=op_token.line, column_index=op_token.column)
                    result = KumirValue(value=result.value // right.value, kumir_type=KumirType.INT.value)
                else:
                    raise KumirTypeError(
                        f"Операция div применима только к целым числам, получены типы '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=op_token.line, column_index=op_token.column
                    )
            elif op_text == 'mod':
                # Остаток от деления
                if (result.kumir_type == KumirType.INT.value and right.kumir_type == KumirType.INT.value):
                    if right.value == 0:
                        raise KumirEvalError("Деление на ноль (mod).", line_index=op_token.line, column_index=op_token.column)
                    result = KumirValue(value=result.value % right.value, kumir_type=KumirType.INT.value)
                else:
                    raise KumirTypeError(
                        f"Операция mod применима только к целым числам, получены типы '{result.kumir_type}' и '{right.kumir_type}'.",
                        line_index=op_token.line, column_index=op_token.column
                    )
            else:
                raise KumirEvalError(f"Неизвестный мультипликативный оператор: {op_text}", 
                                   line_index=op_token.line, column_index=op_token.column)
        
        return result

    # Метод для обработки степенных выражений
    def visitPowerExpression(self, ctx: KumirParser.PowerExpressionContext) -> KumirValue:
        # PowerExpression: unaryExpression (POWER powerExpression)?
        unary_expr = self.visit(ctx.unaryExpression())
        
        # Если есть оператор степени
        if ctx.POWER():
            power_expr = self.visit(ctx.powerExpression())
            # TODO: Реализовать возведение в степень
            # Пока что возвращаем первый операнд
            return unary_expr
        else:
            return unary_expr

    # Метод для обработки унарных выражений  
    def visitUnaryExpression(self, ctx: KumirParser.UnaryExpressionContext) -> KumirValue:
        # UnaryExpression: postfixExpression | unaryPlusMinusExpr | unaryNotExpr
        # Базовый visitChildren должен вызвать правильный подметод
        return self.visitChildren(ctx)

    # Метод для обработки постфиксных выражений
    def visitPostfixExpression(self, ctx: KumirParser.PostfixExpressionContext) -> KumirValue:
        # PostfixExpression: primaryExpression (postfixOperator)*
        primary_expr = self.visit(ctx.primaryExpression())
        
        # TODO: Обработка постфиксных операторов (массивы, вызовы функций)
        # Пока что возвращаем только первичное выражение
        return primary_expr    # Метод для обработки первичных выражений
    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext) -> KumirValue:
        # PrimaryExpression может быть literal, identifier, parenthesizedExpr и т.д.
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.qualifiedIdentifier():
            # TODO: Обработка переменных и идентификаторов
            return self.visit(ctx.qualifiedIdentifier())
        elif ctx.RETURN_VALUE():
            # TODO: Обработка ключевого слова 'знач'
            pos = self._position_from_token(self._get_token_for_position(ctx))
            raise KumirNotImplementedError("Ключевое слово 'знач' пока не поддерживается.", line_index=pos[0], column_index=pos[1])
        elif ctx.expression():
            # Выражение в скобках
            return self.visit(ctx.expression())
        elif ctx.arrayLiteral():
            # TODO: Обработка литералов массивов
            pos = self._position_from_token(self._get_token_for_position(ctx))
            raise KumirNotImplementedError("Литералы массивов пока не поддерживаются.", line_index=pos[0], column_index=pos[1])
        else:
            pos = self._position_from_token(self._get_token_for_position(ctx))
            raise KumirNotImplementedError(f"Неизвестный тип первичного выражения: {ctx.getText()}", line_index=pos[0], column_index=pos[1])

    def visitQualifiedIdentifier(self, ctx: KumirParser.QualifiedIdentifierContext) -> KumirValue:
        """Обрабатывает идентификатор (имя переменной) и возвращает её значение"""
        # qualifiedIdentifier: ID
        var_name = ctx.ID().getText()
        print(f"!!! [DEBUG ExpressionEvaluator.visitQualifiedIdentifier] Поиск переменной: {var_name} !!!", file=sys.stderr)
        
        # Ищем переменную в scope_manager (возвращает кортеж (var_info, scope))
        var_info, scope = self.scope_manager.find_variable(var_name)
        if var_info is None:
            pos = self._position_from_token(ctx.ID().symbol)
            raise KumirNameError(f"Переменная '{var_name}' не объявлена.", line_index=pos[0], column_index=pos[1])
        
        # var_info это словарь с ключами 'value', 'kumir_type', etc.
        value = var_info['value']
        print(f"!!! [DEBUG ExpressionEvaluator.visitQualifiedIdentifier] Найдена переменная {var_name} = {value} !!!", file=sys.stderr)
        
        return value

    def visitExpression(self, ctx: KumirParser.ExpressionContext) -> KumirValue:
        """Обрабатывает Expression узел, делегируя обработку дальше по дереву"""
        print(f"!!! [DEBUG ExpressionEvaluator.visitExpression] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        # Expression -> logicalOrExpression, делегируем обработку
        return self.visit(ctx.logicalOrExpression())

    def visit(self, tree) -> KumirValue:
        """Общий метод visit для обхода AST дерева"""
        print(f"!!! [DEBUG ExpressionEvaluator.visit] CALLED! Tree: {tree.getText() if hasattr(tree, 'getText') else str(tree)} !!!", file=sys.stderr)
        print(f"!!! [DEBUG ExpressionEvaluator.visit] Tree type: {type(tree).__name__} !!!", file=sys.stderr)
        result = super().visit(tree)
        print(f"!!! [DEBUG ExpressionEvaluator.visit] RESULT: {result} !!!", file=sys.stderr)
        return result
