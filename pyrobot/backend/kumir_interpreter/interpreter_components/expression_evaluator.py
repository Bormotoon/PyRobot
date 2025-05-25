# pyrobot/backend/kumir_interpreter/interpreter_components/expression_evaluator.py
# expression_evaluator.py
# Этот файл будет содержать логику вычисения выражений для интерпретатора КуМира.

from __future__ import annotations
# import operator # Не используется напрямую, Python операторы используются
# import sys # Не используется для debug prints, используется logging
from typing import Any, TYPE_CHECKING, Optional

from antlr4 import ParserRuleContext # TerminalNode не используется напрямую
# from antlr4.tree.Tree import ParseTree # Не используется напрямую

import logging
from typing import Any, TYPE_CHECKING, Optional

# Локальные импорты КуМир (относительные)
from ..generated.KumirParser import KumirParser as AntlrGeneratedParser
from ..generated.KumirLexer import KumirLexer # Для токенов
from .main_visitor import KumirInterpreterVisitor # ИСПРАВЛЕННЫЙ ИМПОРТ
from ..kumir_exceptions import KumirEvalError, KumirTypeError, KumirArgumentError, KumirNameError, KumirIndexError # Добавлены KumirNameError, KumirIndexError
from ..kumir_datatypes import KumirValue, KumirVariable, KumirTableVar # KumirFunction, KumirProcedure - пока не используются напрямую здесь
from ..interpreter_components.constants import (
    INTEGER_TYPE, FLOAT_TYPE, STRING_TYPE, BOOLEAN_TYPE,
    ALLOWED_OPERATIONS
)
from ..utils import get_kumir_type_name_from_py_value, are_types_compatible
# Исправленный импорт для ANTLR сгенерированного парсера
from ..generated.KumirParser import KumirParser as AntlrGeneratedParser

if TYPE_CHECKING:
    # Предполагаем, что kumir_interpreter_visitor.py находится в .. 
    # (т.е. pyrobot/backend/kumir_interpreter/kumir_interpreter_visitor.py)
    from ..kumir_interpreter_visitor import KumirInterpreterVisitor

logger = logging.getLogger(__name__)

class ExpressionEvaluator:
    def __init__(self, visitor: 'KumirInterpreterVisitor'):
        self.visitor = visitor

    def _evaluate_literal(self, ctx: AntlrGeneratedParser.LiteralContext) -> KumirValue:
        if ctx.INTEGER(): # Используем INTEGER() вместо INTEGER_LITERAL()
            # Исправлен порядок аргументов KumirValue: (value, type_str)
            return KumirValue(int(ctx.INTEGER().getText()), INTEGER_TYPE)
        elif ctx.REAL(): # Используем REAL()
            val_str = ctx.REAL().getText().replace(',', '.')
            return KumirValue(float(val_str), FLOAT_TYPE)
        elif ctx.STRING(): # Используем STRING()
            text = ctx.STRING().getText()
            return KumirValue(text[1:-1], STRING_TYPE) # Удаляем кавычки
        elif ctx.TRUE(): # Используем TRUE()
            return KumirValue(True, BOOLEAN_TYPE)
        elif ctx.FALSE(): # Используем FALSE()
            return KumirValue(False, BOOLEAN_TYPE)
        # TODO: Обработать CHAR_LITERAL, если он используется в грамматике для выражений
        # elif ctx.CHAR_LITERAL():
        #     text = ctx.CHAR_LITERAL().getText()
        #     return KumirValue(text[1:-1], CHAR_TYPE) # CHAR_TYPE нужно импортировать
        else:
            logger.error(f"Неизвестный тип литерала: {ctx.getText()}")
            raise KumirEvalError(f"Неизвестный тип литерала: {ctx.getText()}", ctx)

    def _evaluate_primary_expression(self, ctx: AntlrGeneratedParser.PrimaryExpressionContext) -> KumirValue:
        """
        Обрабатывает первичные выражения: идентификаторы, литералы в скобках, 'результат'.
        """
        if ctx.qualifiedIdentifier():
            var_name = ctx.qualifiedIdentifier().getText()
            # Ищем переменную или функцию через scope_manager/procedure_manager
            # На этом этапе мы не знаем, будет ли это переменная или функция,
            # поэтому просто получаем информацию. Если это имя функции,
            # то current_value в _evaluate_postfix_expression будет KumirValue,
            # содержащее информацию о функции (или саму функцию), которую можно вызвать.
            # Если это переменная, то это ее значение.
            
            # Попытка найти как переменную
            variable_info, _ = self.visitor.scope_manager.find_variable(var_name, ctx.qualifiedIdentifier(), suppress_error=True) # ИЗМЕНЕНО
            if variable_info:
                return KumirValue(variable_info['value'], variable_info['type'])

            # Если не найдена как переменная, пытаемся найти как процедуру/функцию
            # ProcedureManager должен уметь возвращать дескриптор функции или специальный объект KumirFunction
            # который _evaluate_postfix_expression сможет обработать.
            # Пока предполагаем, что если это имя функции, то оно будет обработано в _evaluate_postfix_expression
            # на основе var_name. Здесь мы просто возвращаем "указатель" на имя.
            # Это потребует доработки в _evaluate_postfix_expression для обработки такого случая.
            # Либо ProcedureManager должен быть способен вернуть объект KumirFunction.
            
            # Временное решение: если это имя функции, оно будет передано как "имя"
            # и _evaluate_postfix_expression должен будет это распознать.
            # Более правильно было бы, чтобы scope_manager или procedure_manager вернул объект KumirFunction.
            
            # Проверяем, есть ли такая функция (без вызова ошибки, если нет)
            if self.visitor.procedure_manager.is_function_defined(var_name):
                 # Возвращаем специальный объект или KumirValue, который _evaluate_postfix_expression
                 # сможет интерпретировать как функцию для вызова.
                 # Пока просто вернем имя, а _evaluate_postfix_expression будет искать ее.
                 # Это не очень хорошо, т.к. KumirValue(var_name, "ИМЯ_ФУНКЦИИ_ТИП") - выдумка.
                 # Лучше, если procedure_manager вернет объект KumirFunction.
                 # Допустим, procedure_manager.get_function_definition(var_name) возвращает такой объект.
                 
                 # Пока что, если это идентификатор, который не является переменной,
                 # он будет обработан в _evaluate_postfix_expression как имя функции.
                 # Это значит, что current_value в _evaluate_postfix_expression будет KumirValue(имя_переменной, тип)
                 # или, если переменная не найдена, то _evaluate_postfix_expression должен будет использовать
                 # текст из primary_expr_ctx.qualifiedIdentifier().getText() как имя функции.
                 # Это не очень чисто.
                 pass # Даем коду ниже выбросить ошибку, если переменная не найдена и это не вызов функции.

            # Если переменная не найдена и это не имя известной функции (проверка выше закомментирована),
            # то scope_manager.find_variable выбросит KumirNameError.
            # Повторный вызов для генерации ошибки, если suppress_error был true и ничего не найдено.
            variable_info, _ = self.visitor.scope_manager.find_variable(var_name, ctx.qualifiedIdentifier())
            return KumirValue(variable_info['value'], variable_info['type'])


        elif ctx.LPAREN() and ctx.expression() and ctx.RPAREN():
            # Выражение в скобках, обрабатываем как обычное выражение
            return self.evaluate(ctx.expression())
        else:
            logger.error(f"Нераспознанное первичное выражение: {ctx.getText()}")
            raise KumirEvalError(f"Нераспознанное первичное выражение: {ctx.getText()}", ctx)

    def _evaluate_postfix_expression(self, ctx: AntlrGeneratedParser.PostfixExpressionContext) -> KumirValue:
        """
        Обрабатывает постфиксные выражения: доступ к элементам таблицы, вызовы функций.
        ctx здесь это AntlrGeneratedParser.PostfixExpressionContext (из правила postfixExpression)
        """
        primary_expr_ctx = ctx.primaryExpression()
        if not primary_expr_ctx: # pragma: no cover
            # Это не должно происходить согласно грамматике postfixExpression: primaryExpression (postfixPart)*
            raise KumirEvalError(f"Внутренняя ошибка: отсутствует primaryExpression в PostfixExpressionContext: {ctx.getText()}", ctx)
        
        # Сначала вычисляем базовое выражение (это может быть переменная, литерал, выражение в скобках)
        current_value = self._evaluate_primary_expression(primary_expr_ctx)
        
        # Имя функции, если primary_expr_ctx - это идентификатор.
        # Это основной способ вызова функции в КуМире.
        base_identifier_name: Optional[str] = None
        if primary_expr_ctx.qualifiedIdentifier():
            base_identifier_name = primary_expr_ctx.qualifiedIdentifier().getText()

        postfix_parts = ctx.postfixPart() 

        if postfix_parts: 
            for part_ctx in postfix_parts: 
                if part_ctx.indexList(): # Доступ к элементу таблицы ( LBRACK indexList RBRACK )
                    if not isinstance(current_value.value, KumirTableVar):
                        primary_expr_text = primary_expr_ctx.getText() 
                        raise KumirTypeError(
                            f"Попытка доступа по индексу к '{primary_expr_text}', который не является таблицей (тип: {current_value.kumir_type}).",
                            line_index=part_ctx.start.line -1, 
                            column_index=part_ctx.start.column,
                            line_content=self.visitor.get_line_content_from_ctx(part_ctx)
                        )
                    
                    table_var: KumirTableVar = current_value.value
                    indices = []
                    
                    idx_list_ctx = part_ctx.indexList() 
                    for expr_ctx in idx_list_ctx.expression(): 
                        index_val = self.evaluate(expr_ctx)
                        if index_val.kumir_type != INTEGER_TYPE:
                            raise KumirTypeError(
                                f"Индекс таблицы должен быть целым числом, получен {index_val.kumir_type} ({index_val.value}).",
                                line_index=expr_ctx.start.line -1,
                                column_index=expr_ctx.start.column,
                                line_content=self.visitor.get_line_content_from_ctx(expr_ctx)
                            )
                        indices.append(index_val.value)
                    
                    try:
                        # В KumirTableVar get_value должен возвращать Python значение.
                        # KumirValue создается здесь.
                        element_py_value = table_var.get_value(tuple(indices), part_ctx)
                        # Тип элемента таблицы берется из KumirTableVar
                        current_value = KumirValue(element_py_value, table_var.element_kumir_type) # ИЗМЕНЕНО: table_var.element_kumir_type
                    except IndexError as e: 
                        raise KumirIndexError(
                            f"Ошибка индекса таблицы: {e}",
                            line_index=part_ctx.start.line -1,
                            column_index=part_ctx.start.column,
                            line_content=self.visitor.get_line_content_from_ctx(part_ctx)
                        )
                    except KumirIndexError as e: # pragma: no cover
                        # Это исключение уже содержит всю необходимую информацию
                        raise e
                    except KumirEvalError as e: # Могут быть другие ошибки из _validate_indices
                        raise e


                elif part_ctx.LPAREN(): # Вызов функции ( LPAREN argumentList? RPAREN )
                    function_to_call_name: Optional[str] = None

                    if base_identifier_name:
                        # Это стандартный случай: f(x) или table_var.func(x) (если бы были методы)
                        # В КуМире это просто имя функции.
                        function_to_call_name = base_identifier_name
                    else:
                        # Случай типа (выражение_возвращающее_имя_функции_или_объект_функции)(аргументы)
                        # Например, (get_func_name())(args) или (my_array[1])(args) если элемент массива - функция
                        # Для КуМира это очень экзотично.
                        # Если current_value.value это объект KumirFunction, можно было бы извлечь имя.
                        # if isinstance(current_value.value, KumirFunction): # KumirFunction нужно импортировать
                        #    function_to_call_name = current_value.value.name
                        # elif isinstance(current_value.value, str) and self.visitor.procedure_manager.is_function_defined(current_value.value):
                        #    function_to_call_name = current_value.value # Если выражение вернуло имя функции как строку
                        
                        # Пока что, если база не была идентификатором, считаем это ошибкой для КуМира.
                        primary_text = primary_expr_ctx.getText()
                        raise KumirTypeError(
                            f"Выражение '{primary_text}' перед скобками вызова () не является именем функции.",
                            line_index=primary_expr_ctx.start.line -1,
                            column_index=primary_expr_ctx.start.column,
                            line_content=self.visitor.get_line_content_from_ctx(primary_expr_ctx)
                        )
                        
                    if not function_to_call_name: # pragma: no cover # Должно быть отловлено выше
                        primary_text = primary_expr_ctx.getText()
                        raise KumirTypeError(
                            f"Не удалось определить имя функции для вызова из '{primary_text}'.",
                            line_index=primary_expr_ctx.start.line -1,
                            column_index=primary_expr_ctx.start.column,
                            line_content=self.visitor.get_line_content_from_ctx(primary_expr_ctx)
                        )

                    # Сбор аргументов
                    args_ctx = part_ctx.argumentList()
                    evaluated_args: List[KumirValue] = [] # Явно типизируем
                    if args_ctx and args_ctx.expressionList():
                        for arg_expr_ctx in args_ctx.expressionList().expression():
                            evaluated_args.append(self.evaluate(arg_expr_ctx))
                    
                    try:
                        current_value = self.visitor.procedure_manager.call_function(
                            function_to_call_name, 
                            evaluated_args, 
                            part_ctx # Контекст для информации об ошибке (место вызова)
                        )
                    except (KumirNameError, KumirArgumentError, KumirTypeError, KumirEvalError) as e:
                        # Эти исключения уже должны быть правильно сформированы в ProcedureManager
                        raise e
                    # except Exception as e: # Ловим другие непредвиденные ошибки и оборачиваем
                    #     logger.exception(f"Непредвиденная ошибка при вызове функции '{function_to_call_name}': {e}") # Используем logger.exception для stack trace
                    #     raise KumirEvalError(
                    #         f"Ошибка при выполнении функции '{function_to_call_name}': {type(e).__name__} - {e}",
                    #         part_ctx
                    #     )
                
                # После обработки одной части постфикса (индекс или вызов),
                # current_value обновлено. Если есть еще postfix_parts,
                # они будут применены к этому новому current_value.
                # Например, f(x)[1] или table[1](args) (если бы элементы таблицы могли быть функциями)
                # Для этого base_identifier_name должен сбрасываться или переопределяться, если current_value
                # больше не связано с исходным идентификатором.
                # В КуМире цепочки типа f(x)[1] (где f возвращает таблицу) или tab[i]() (где элемент таблицы - функция)
                # являются стандартными.
                # Если current_value стало результатом вызова функции, и это не идентификатор,
                # то base_identifier_name для следующей итерации должен быть None.
                if isinstance(current_value.value, (KumirTableVar)): # Если результат - таблица, то следующий part_ctx может быть индексом
                    base_identifier_name = None # Сбрасываем, так как current_value теперь таблица, а не имя
                elif hasattr(current_value.value, '__call__'): # Если результат - вызываемый объект (например, KumirFunction)
                     # Если бы KumirFunction был объектом, можно было бы сохранить его имя
                     # if isinstance(current_value.value, KumirFunction):
                     # base_identifier_name = current_value.value.name
                     # else:
                     base_identifier_name = None
                else: # Если результат - простое значение, дальнейший вызов функции по имени невозможен
                    base_identifier_name = None


        return current_value

    def _evaluate_unary_expression(self, operator_text: str, operand_val: KumirValue, ctx: AntlrGeneratedParser.ExpressionContext) -> KumirValue:
        op_text_lower = operator_text.lower()
        if op_text_lower == '-':
            if operand_val.kumir_type == INTEGER_TYPE:
                return KumirValue(-operand_val.value, INTEGER_TYPE)
            elif operand_val.kumir_type == FLOAT_TYPE:
                return KumirValue(-operand_val.value, FLOAT_TYPE)
            else:
                type_name = get_kumir_type_name_from_py_value(operand_val.value)
                raise KumirTypeError(f"Унарный минус не применим к типу '{type_name}'.", ctx)
        elif op_text_lower == 'не':
            if operand_val.kumir_type == BOOLEAN_TYPE:
                return KumirValue(not operand_val.value, BOOLEAN_TYPE)
            else:
                type_name = get_kumir_type_name_from_py_value(operand_val.value)
                raise KumirTypeError(f"Логическое отрицание 'не' не применимо к типу '{type_name}'.", ctx)
        else:
            logger.error(f"Неизвестный унарный оператор: {operator_text}")
            raise KumirEvalError(f"Неизвестный унарный оператор: {operator_text}", ctx)

    def _calculate_binary_result(self, left_val: KumirValue, right_val: KumirValue, op_text: str, ctx: AntlrGeneratedParser.ExpressionContext) -> KumirValue:
        # op_text уже должен быть каноническим из _get_operator_text_from_binary_context
        # (например, 'И' 'ИЛИ', 'DIV', 'MOD' в верхнем регистре, если так в constants.py)
        # В constants.py ALLOWED_OPERATIONS ключи для 'И', 'ИЛИ', 'DIV', 'MOD' в верхнем регистре.
        # Остальные (+, -, *, /, <, >, =, <>, <=, >=) как есть.

        effective_op_text = op_text 
        if op_text.lower() in ['div', 'mod', 'и', 'или']:
            effective_op_text = op_text.upper() # Приводим к верхнему регистру для ключей в ALLOWED_OPERATIONS

        op_key = (left_val.kumir_type, right_val.kumir_type, effective_op_text)

        if op_key not in ALLOWED_OPERATIONS:
            left_type_name = get_kumir_type_name_from_py_value(left_val.value)
            right_type_name = get_kumir_type_name_from_py_value(right_val.value)
            # Используем оригинальный op_text для сообщения об ошибке, он более читаем для пользователя
            raise KumirTypeError(
                f"Операция '{op_text}' не поддерживается для типов '{left_type_name}' и '{right_type_name}'.",
                ctx
            )

        target_type = ALLOWED_OPERATIONS[op_key]
        result_value: Any = None 

        # Используем effective_op_text для логики, так как он соответствует ключам в ALLOWED_OPERATIONS
        # или op_text.lower() для удобства сравнения в Python
        
        py_op_check = op_text.lower() # Для удобства сравнения в Python

        if py_op_check == '+':
            if target_type == STRING_TYPE: # Конкатенация строк или символов
                result_value = str(left_val.value) + str(right_val.value)
            else: # Числовое сложение
                result_value = left_val.value + right_val.value
        elif py_op_check == '-':
            result_value = left_val.value - right_val.value
        elif py_op_check == '*':
            result_value = left_val.value * right_val.value
        elif py_op_check == '/': # Вещественное деление
            if right_val.value == 0 or right_val.value == 0.0: # Проверка деления на ноль
                raise KumirEvalError("Деление на ноль.", ctx)
            result_value = float(left_val.value) / float(right_val.value)
        elif py_op_check == 'div':
            if not (left_val.kumir_type == INTEGER_TYPE and right_val.kumir_type == INTEGER_TYPE):
                 raise KumirTypeError("Операция 'div' применима только к целым числам.", ctx) # Доп. проверка
            if right_val.value == 0:
                raise KumirEvalError("Деление на ноль (div).", ctx)
            result_value = left_val.value // right_val.value
        elif py_op_check == 'mod':
            if not (left_val.kumir_type == INTEGER_TYPE and right_val.kumir_type == INTEGER_TYPE):
                raise KumirTypeError("Операция 'mod' применима только к целым числам.", ctx) # Доп. проверка
            if right_val.value == 0:
                raise KumirEvalError("Деление на ноль (mod).", ctx)
        # Операции сравнения
        elif py_op_check == '=': result_value = left_val.value == right_val.value
        elif py_op_check == '<>': result_value = left_val.value != right_val.value
        elif py_op_check == '<': result_value = left_val.value < right_val.value
        elif py_op_check == '<=': result_value = left_val.value <= right_val.value
        elif py_op_check == '>': result_value = left_val.value > right_val.value
        elif py_op_check == '>=': result_value = left_val.value >= right_val.value
        # Логические операции
        elif py_op_check == 'и':
            result_value = bool(left_val.value) and bool(right_val.value)
        elif py_op_check == 'или':
            result_value = bool(left_val.value) or bool(right_val.value)
        # TODO: Возведение в степень '^' (POWER)
        # elif py_op_check == '^':
        #    # Логика для степени, учитывая типы и результат (цел/вещ)
        #    pass
        else:
            logger.error(f"Неизвестная или неподдерживаемая бинарная операция: {op_text}")
            raise KumirEvalError(f"Неизвестная или неподдерживаемая бинарная операция: {op_text}", ctx)

        if result_value is None and not (target_type == BOOLEAN_TYPE and py_op_check in ['=','<>','<','<=','>','>=','и','или']):
            logger.error(f"Логика для операции '{op_text}' не полностью реализована, результат None.")
            raise KumirEvalError(f"Логика для операции '{op_text}' не полностью реализована.", ctx)
            
        return KumirValue(result_value, target_type)

    def _get_operator_text_from_binary_context(self, ctx: AntlrGeneratedParser.ExpressionContext) -> str:
        # Для правил с метками, ANTLR создает специфические классы контекста.
        # Например, LogicalAndExprContext, ComparisonExprContext и т.д.
        if isinstance(ctx, AntlrGeneratedParser.LogicalAndExprContext):
            return ctx.KW_AND().getText() # "и"
        elif isinstance(ctx, AntlrGeneratedParser.LogicalOrExprContext):
            return ctx.KW_OR().getText() # "или"
        
        # Для правил типа expr op expr, где op - один из нескольких токенов,
        # например, multiplicativeExpression, additiveExpression, relationalExpression.
        # Оператор обычно является вторым дочерним элементом.
        # ctx.getChild(1) вернет ParseTree (TerminalNodeImpl), у которого есть getText().
        # Проверяем, что есть хотя бы 2 дочерних элемента (операнд, оператор, операнд -> 3)
        # или (операнд, оператор -> 2, если унарный в бинарном правиле, что не должно быть здесь)
        if ctx.getChildCount() >= 2: # Обычно 3 для бинарных: expr OP expr
            op_node = ctx.getChild(1)
            if op_node: # op_node может быть None, если дерево построено некорректно
                return op_node.getText()
        
        # Если не удалось извлечь оператор специфичными методами или через getChild(1)
        logger.error(f"Не удалось извлечь оператор из бинарного контекста: {type(ctx).__name__}, текст: {ctx.getText()}")
        raise KumirEvalError(f"Не удалось определить оператор для бинарного выражения типа {type(ctx).__name__}", ctx)


    def _evaluate_binary_expression_from_context(self, ctx: AntlrGeneratedParser.ExpressionContext) -> KumirValue:
        # ctx.expression() возвращает список всех дочерних узлов типа ExpressionContext.
        # Для бинарных операций их должно быть два.
        left_expr_ctx = ctx.expression(0)
        right_expr_ctx = ctx.expression(1)
        
        if left_expr_ctx is None or right_expr_ctx is None:
            raise KumirEvalError(f"Ожидалось два операнда для бинарной операции, но один или оба отсутствуют. Контекст: {ctx.getText()}", ctx)

        left_val = self.evaluate(left_expr_ctx)
        right_val = self.evaluate(right_expr_ctx)
        
        op_text = self._get_operator_text_from_binary_context(ctx)
        return self._calculate_binary_result(left_val, right_val, op_text, ctx)

    def evaluate(self, ctx: Optional[AntlrGeneratedParser.ExpressionContext]) -> KumirValue:
        if ctx is None:
            logger.error("Попытка вычислить None выражение.")
            # ctx для KumirEvalError здесь None, что может вызвать проблемы при форматировании ошибки.
            # Передаем текущий известный контекст, если есть, или фиктивный.
            # Но если ctx is None, то у нас нет контекста.
            raise KumirEvalError("Получено пустое (None) выражение для вычисления.", None) # type: ignore

        # Используем isinstance для определения конкретного типа контекста выражения,
        # созданного ANTLR на основе меток в грамматике (например, #PrimaryExpr).
        
        # Порядок важен: от более специфичных правил (меток) к более общим.
        # Метки в грамматике вида: expression # RuleNameLabel
        # создают класс RuleNameLabelContext, который является подклассом ExpressionContext.

        if isinstance(ctx, AntlrGeneratedParser.ParenthesizedExprContext):
            # Грамматика: expression : LPAREN expression RPAREN # ParenthesizedExpr
            return self.evaluate(ctx.expression()) 
        elif isinstance(ctx, AntlrGeneratedParser.PrimaryExprContext):
            # Грамматика: expression : primaryExpression # PrimaryExpr
            # primaryExpression() возвращает PrimaryExpressionContext
            return self._evaluate_primary_expression(ctx.primaryExpression())
        elif isinstance(ctx, AntlrGeneratedParser.PostfixExprContext):
            # Грамматика: expression : postfixExpression # PostfixExpr
            # postfixExpression() возвращает PostfixExpressionContext
            return self._evaluate_postfix_expression(ctx.postfixExpression())
        elif isinstance(ctx, AntlrGeneratedParser.UnaryMinusExprContext):
            # Грамматика: expression : MINUS expression # UnaryMinusExpr
            operand_val = self.evaluate(ctx.expression())
            # Оператор '-' фиксирован, передаем его текст
            return self._evaluate_unary_expression('-', operand_val, ctx)
        elif isinstance(ctx, AntlrGeneratedParser.NotExprContext):
            # Грамматика: expression : KW_NOT expression # NotExpr
            operand_val = self.evaluate(ctx.expression())
            op_text = ctx.KW_NOT().getText() # "не"
            return self._evaluate_unary_expression(op_text, operand_val, ctx)
        
        # Бинарные операции по типам контекста (созданным метками в грамматике)
        elif isinstance(ctx, (AntlrGeneratedParser.MultDivModExprContext, 
                               AntlrGeneratedParser.AddSubExprContext,
                               AntlrGeneratedParser.ComparisonExprContext, # Общий для <, >, <=, >=, =, <>, <=, >=
                               AntlrGeneratedParser.EqualityExprContext, # Если = и <> выделены в отдельное правило с меткой
                               AntlrGeneratedParser.LogicalAndExprContext,
                               AntlrGeneratedParser.LogicalOrExprContext
                               # AntlrGeneratedParser.PowerExprContext, # Если есть такое правило с меткой
                               )):
            # Эти контексты должны иметь expression(0) и expression(1)
            # и способ получить оператор (через getChild(1) или спец. метод токена)
            return self._evaluate_binary_expression_from_context(ctx)
        
        # Если грамматика не использует метки для всех вариантов expression,
        # а определяет их через порядок правил (precedence climbing),
        # то ctx будет просто ExpressionContext, и нужно анализировать его дочерние элементы.
        # Но современный ANTLR с метками предпочтительнее.
        # Если мы дошли сюда, значит, тип контекста не был распознан выше.

        else:
            type_name = type(ctx).__name__
            # Это может быть базовый ExpressionContext, если метки не покрыли все случаи,
            # или неизвестный/неожиданный тип контекста.
            # Если это базовый ExpressionContext, нужно анализировать его структуру:
            # ctx.children, ctx.getChildCount(), и т.д.
            # Например, если это бинарная операция без метки:
            # if ctx.getChildCount() == 3 and isinstance(ctx.getChild(0), AntlrGeneratedParser.ExpressionContext) \
            #   and isinstance(ctx.getChild(2), AntlrGeneratedParser.ExpressionContext):
            #    left = self.evaluate(ctx.expression(0))
            #    op = ctx.getChild(1).getText()
            #    right = self.evaluate(ctx.expression(1))
            #    return self._calculate_binary_result(left, right, op, ctx)

            logger.error(f"Неподдерживаемый или неизвестный тип ExpressionContext: {type_name}, текст: {ctx.getText()}")
            raise KumirEvalError(f"Неподдерживаемый тип выражения: {type_name}. Обратитесь к грамматике: {ctx.getText()}", ctx)

# TODO: Рассмотреть возможность кеширования результатов вычисления выражений.
# TODO: Добавить обработку CHAR_TYPE в _evaluate_literal и ALLOWED_OPERATIONS.
# TODO: Добавить обработку '^' (возведение в степень) в _calculate_binary_result и ALLOWED_OPERATIONS.
# TODO: Тщательно протестировать _evaluate_postfix_expression, особенно с учетом того,
#       что primaryExpression() возвращает контекст, а не значение, и что PostfixExprContext
#       подразумевает наличие постфиксных операторов.
# TODO: Реализовать вызовы функций в _evaluate_postfix_expression.