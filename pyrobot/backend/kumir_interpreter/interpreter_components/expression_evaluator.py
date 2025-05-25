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
    def __init__(self, scope_manager: ScopeManager, procedure_manager: ProcedureManager):
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
        # if ctx.expression():
        #     return self.visit(ctx.expression())
        pass # Обычно не используется в ExpressionEvaluator

    def visitLiteral(self, ctx: KumirParser.LiteralContext) -> KumirValue:
        text = ctx.getText()
        if ctx.INTEGER(): # Исправлено
            return KumirValue(value=int(text), kumir_type=KumirType.INT.value)
        elif ctx.REAL(): # Исправлено
            # Кумир использует запятую как десятичный разделитель
            return KumirValue(value=float(text.replace(',', '.')), kumir_type=KumirType.REAL.value) # Убедимся, что экранирование корректно
        elif ctx.STRING(): # Исправлено
            # Удаляем кавычки в начале и в конце
            return KumirValue(value=text[1:-1], kumir_type=KumirType.STR.value)
        elif ctx.TRUE(): # Исправлено
            return KumirValue(value=True, kumir_type=KumirType.BOOL.value)
        elif ctx.FALSE(): # Исправлено
            return KumirValue(value=False, kumir_type=KumirType.BOOL.value)
        # TODO: Добавить обработку CHAR_LITERAL, colorLiteral, NEWLINE_CONST из грамматики
        # elif ctx.CHAR_LITERAL():
        #     # ... логика для символьных литералов ...
        #     pass
        # elif ctx.colorLiteral():
        #     # ... логика для цветовых литералов ...
        #     pass
        # elif ctx.NEWLINE_CONST():
        #     # ... логика для нс ...
        #     pass
        else:
            pos = self._position_from_token(self._get_token_for_position(ctx))
            # Уточняем сообщение, так как некоторые литералы из грамматики еще не поддерживаются
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
    # ... existing code ...
    def visitSimpleAssignmentExpression(self, ctx: KumirParser.SimpleAssignmentExpressionContext) -> KumirValue:
        lvalue_node = ctx.lvalue() 
        var_name_node: Optional[Token] = None # Указываем, что это может быть токен или None
        is_table_access = False
        # indices_kumir_values: Optional[List[KumirValue]] = None # Не используется напрямую для присваивания
        evaluated_indices_python: Optional[List[Any]] = None 

        if not lvalue_node:
            # Это не должно произойти согласно грамматике, но для защиты:
            pos_token = self._get_token_for_position(ctx)
            pos = self._position_from_token(pos_token)
            raise KumirEvalError(
                "Отсутствует lvalue в выражении присваивания.",
                line_index=pos[0]-1,
                column_index=pos[1]
            )

        if lvalue_node.RETURN_VALUE():
            value_to_assign = self._visit_operand(ctx.expression())
            # Обработка 'знач :=' (возврат значения из процедуры)
            # Это значение должно быть установлено в ProcedureManager или аналогичном.
            # ExpressionEvaluator просто возвращает вычисленное значение.
            # Вызывающий код (например, StatementExecutor) должен обработать этот случай.
            # print(f"[DEBUG ExpressionEvaluator] 'знач' присвоено: {value_to_assign}", file=sys.stderr)
            return value_to_assign 

        q_id_node = lvalue_node.qualifiedIdentifier()
        if not q_id_node:
            pos_token = self._get_token_for_position(lvalue_node)
            pos = self._position_from_token(pos_token)
            raise KumirEvalError(
                "Некорректное lvalue: отсутствует идентификатор.",
                line_index=pos[0]-1,
                column_index=pos[1]
            )
        
        # qualifiedIdentifier : ID (AT ID)* ;
        # Пока что мы поддерживаем только простые ID в качестве lvalue для переменных.
        # TODO: Поддержать actor@field если это будет необходимо.
        if q_id_node.AT():
            pos_token = self._get_token_for_position(q_id_node.AT())
            pos = self._position_from_token(pos_token)
            raise KumirNotImplementedError(
                "Присваивание полям объектов (например, 'Робот@поле') пока не поддерживается.",
                line_index=pos[0]-1,
                column_index=pos[1]
            )
        
        ids = q_id_node.ID() # Это список токенов ID
        if not ids:
            pos_token = self._get_token_for_position(q_id_node)
            pos = self._position_from_token(pos_token)
            raise KumirEvalError(
                "Не удалось извлечь имя переменной из lvalue (qualifiedIdentifier не содержит ID).",
                line_index=pos[0]-1,
                column_index=pos[1]
            )
        var_name_node = ids[0] # Берем первый (и пока единственный поддерживаемый) ID
        
        if var_name_node is None: # Добавлена проверка на None
            # Эта ситуация не должна возникнуть, если ids не пустой, но для безопасности
            pos_token = self._get_token_for_position(q_id_node) 
            pos = self._position_from_token(pos_token)
            raise KumirEvalError(
                "Внутренняя ошибка: узел имени переменной отсутствует после извлечения из ID списка.",
                line_index=pos[0]-1,
                column_index=pos[1]
            )
        var_name = var_name_node.text # Используем .text вместо .getText()
        
        if lvalue_node.LBRACK(): # Доступ к таблице
            is_table_access = True
            index_list_node = lvalue_node.indexList()
            if index_list_node and index_list_node.expression():
                evaluated_indices_python = []
                for expr_idx_ctx in index_list_node.expression():
                    idx_val_kumir = self._visit_operand(expr_idx_ctx)
                    self._check_operand_type(idx_val_kumir, [KumirType.INT], "индекс таблицы", self._get_token_for_position(expr_idx_ctx))
                    evaluated_indices_python.append(idx_val_kumir.value) 
            else:
                # Ошибка: есть скобки, но нет списка индексов или он пуст
                # Токен '[' можно получить через lvalue_node.LBRACK().getSymbol()
                err_token = lvalue_node.LBRACK().getSymbol() if lvalue_node.LBRACK() else self._get_token_for_position(lvalue_node)
                pos = self._position_from_token(err_token)
                raise KumirEvalError(
                    "Ожидался непустой список индексов для доступа к таблице.",
                    line_index=pos[0]-1,
                    column_index=pos[1]
                )

        # Вычисляем правую часть ПОСЛЕ определения lvalue, на случай если lvalue некорректно
        value_to_assign = self._visit_operand(ctx.expression())

        if not isinstance(value_to_assign, KumirValue):
             # Эта проверка дублируется с _visit_operand, но для безопасности оставим
             pos_token = self._get_token_for_position(ctx.expression())
             pos = self._position_from_token(pos_token)
             raise KumirRuntimeError(
                f"Внутренняя ошибка: правая часть присваивания не вернула KumirValue (тип: {type(value_to_assign).__name__}).",
                line_index=pos[0]-1,
                column_index=pos[1]
            )

        if is_table_access:
            if evaluated_indices_python is None:
                # Эта ситуация не должна возникнуть из-за проверок выше, но для полноты
                pos_token = self._get_token_for_position(lvalue_node)
                pos = self._position_from_token(pos_token)
                raise KumirRuntimeError("Внутренняя ошибка: индексы таблицы не были вычислены.", line_index=pos[0]-1, column_index=pos[1])
            
            # TODO: Когда ScopeManager будет иметь метод update_table_element, использовать его.
            # self.scope_manager.update_table_element(
            #     var_name, 
            #     tuple(evaluated_indices_python),
            #     value_to_assign, 
            #     ctx_for_error=ctx 
            # )
            # Пока что имитируем ошибку, что это не реализовано, или если бы ScopeManager не имел метода:
            pos_err_token = self._get_token_for_position(ctx) # Общая позиция присваивания
            pos_err = self._position_from_token(pos_err_token)
            raise KumirNotImplementedError(
                f"Присваивание элементу таблицы '{var_name}' пока не поддерживается (требуется реализация в ScopeManager).",
                line_index=pos_err[0]-1,
                column_index=pos_err[1]
            )
        else:
            # Присваивание простой переменной
            # Передаем KumirValue в ScopeManager, он должен уметь с этим работать
            self.scope_manager.update_variable(var_name, value_to_assign, ctx_for_error=ctx)
        
        # Выражение присваивания в КуМир (если оно разрешено как выражение) должно возвращать присвоенное значение.
        return value_to_assign
