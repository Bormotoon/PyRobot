# FILE START: interpreter.py
import logging
import copy
import math # Добавлено для pow
import operator # Добавлено для операций
# Добавляем импорт TerminalNode
from antlr4.tree.Tree import TerminalNode 

# Импортируем все исключения из одного места
from .kumir_exceptions import (KumirExecutionError, DeclarationError, AssignmentError,
                               InputOutputError, KumirInputRequiredError, KumirEvalError,
                               RobotError)
# Импортируем остальные зависимости
from .declarations import (get_default_value, _validate_and_convert_value,
                           process_declaration, process_assignment, process_output,
                           process_input)  # Больше не импортируем исключения отсюда
from .execution import execute_lines  # Больше не импортируем KumirExecutionError отсюда
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_state import SimulatedRobot  # Больше не импортируем RobotError отсюда
from .generated.KumirParserVisitor import KumirParserVisitor
from .generated.KumirParser import KumirParser
from .generated.KumirLexer import KumirLexer # Импортируем лексер для имен токенов
# Добавляем ErrorListener
from antlr4.error.ErrorListener import ErrorListener
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import sys
from typing import Any, Tuple, Optional, Dict

# Убрали импорт KumirEvalError из safe_eval

MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT
logger = logging.getLogger('KumirInterpreter')

# Словарь для маппинга токенов типа на строки
TYPE_MAP = {
    KumirLexer.INTEGER_TYPE: 'цел',
    KumirLexer.REAL_TYPE: 'вещ',
    KumirLexer.BOOLEAN_TYPE: 'лог',
    KumirLexer.CHAR_TYPE: 'сим',
    KumirLexer.STRING_TYPE: 'лит',
}

# Словари для операций
ARITHMETIC_OPS = {
    KumirLexer.PLUS: operator.add,
    KumirLexer.MINUS: operator.sub,
    KumirLexer.MUL: operator.mul,
    KumirLexer.DIV: operator.truediv, # Обычное деление -> вещ
    KumirLexer.DIV_OP: operator.floordiv, # Целочисленное деление -> цел
    KumirLexer.MOD_OP: operator.mod, # Остаток -> цел
    KumirLexer.POWER: operator.pow,
}

COMPARISON_OPS = {
    KumirLexer.EQ: operator.eq,
    KumirLexer.NE: operator.ne,
    KumirLexer.LT: operator.lt,
    KumirLexer.GT: operator.gt,
    KumirLexer.LE: operator.le,
    KumirLexer.GE: operator.ge,
}

# Добавляем логические операции
LOGICAL_OPS = {
    KumirLexer.AND: operator.and_,
    KumirLexer.OR: operator.or_,
    # NOT handled in unaryExpr
}

# Типы данных
INTEGER_TYPE = 'цел'
FLOAT_TYPE = 'вещ'
BOOLEAN_TYPE = 'лог'
CHAR_TYPE = 'сим'
STRING_TYPE = 'лит'

# Класс для вывода подробных ошибок парсинга
class DiagnosticErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"[DEBUG][Parser Error] Строка {line}:{column} около '{offendingSymbol.text if offendingSymbol else 'EOF'}' - {msg}", file=sys.stderr)

def get_default_value(kumir_type):
    """Возвращает значение по умолчанию для данного типа Кумира."""
    if kumir_type == 'цел': return 0
    if kumir_type == 'вещ': return 0.0
    if kumir_type == 'лог': return False # В Кумире логические по умолчанию могут быть не инициализированы, но False безопаснее
    if kumir_type == 'сим': return ''    # Или может быть ошибка?
    if kumir_type == 'лит': return ""
    return None # Для таблиц или неизвестных типов


class KumirInterpreterVisitor(KumirParserVisitor):
    """Обходит дерево разбора Кумира и выполняет семантические действия."""

    def __init__(self):
        super().__init__()
        self.variables = {}  # Глобальные переменные
        self.scopes = [{}]  # Стек областей видимости, начинаем с глобальной
        self.current_scope = self.scopes[0]  # Текущая область видимости
        self.debug = True  # Флаг для отладочного вывода
        self.had_output = False
        self.last_output = ""  # Буфер для накопления вывода
        self.suppress_newline = False  # Флаг для подавления переноса строки

    # --- Управление областями видимости и символами ---

    def enter_scope(self):
        """Входит в новую локальную область видимости."""
        self.scopes.append({}) # Добавляем новый пустой словарь для локальной области
        print(f"[DEBUG][Scope] Вошли в область уровня {len(self.scopes)}", file=sys.stderr)

    def exit_scope(self):
        """Выходит из текущей локальной области видимости."""
        if len(self.scopes) > 1:
            print(f"[DEBUG][Scope] Вышли из области уровня {len(self.scopes) - 1}", file=sys.stderr)
            self.scopes.pop()
        else:
            print("[ERROR][Scope] Попытка выйти из глобальной области!", file=sys.stderr)

    def declare_variable(self, name, kumir_type, is_table=False, dimensions=None):
        """Объявляет переменную в текущей области видимости."""
        current_scope = self.scopes[-1]
        if name in current_scope:
            # TODO: Использовать KumirExecutionError или DeclarationError
            raise Exception(f"Переменная '{name}' уже объявлена в этой области видимости.") 
        
        default_value = {} if is_table else get_default_value(kumir_type)
        current_scope[name] = {
            'type': kumir_type,
            'value': default_value,
            'is_table': is_table,
            'dimensions': dimensions if is_table else None
        }
        print(f"[DEBUG][Declare] Объявлена {'таблица' if is_table else 'переменная'} '{name}' тип {kumir_type} в области {len(self.scopes) - 1}", file=sys.stderr)

    def find_variable(self, var_name: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Ищет переменную во всех областях видимости и возвращает её информацию и область видимости."""
        for scope in reversed(self.scopes):
            if var_name in scope:
                return scope[var_name], scope
        return None, None

    def update_variable(self, var_name: str, value: Any) -> None:
        """Обновляет значение переменной в текущей области видимости."""
        var_info, scope = self.find_variable(var_name)
        if var_info is None or scope is None:
            raise KumirEvalError(f"Переменная '{var_name}' не найдена")
        
        # Проверяем тип значения
        if value is None:
            raise KumirEvalError(f"Попытка присвоить значение None переменной '{var_name}'")
            
        var_type = var_info.get('type')
        if var_type == INTEGER_TYPE:
            if not isinstance(value, int):
                raise KumirEvalError(f"Ожидалось целое число для '{var_name}', получено {type(value)}")
        elif var_type == FLOAT_TYPE:
            if not isinstance(value, (int, float)):
                raise KumirEvalError(f"Ожидалось вещественное число для '{var_name}', получено {type(value)}")
            value = float(value)
        elif var_type == BOOLEAN_TYPE:
            if not isinstance(value, bool):
                raise KumirEvalError(f"Ожидалось логическое значение для '{var_name}', получено {type(value)}")
        elif var_type == CHAR_TYPE:
            if not isinstance(value, str) or len(value) != 1:
                raise KumirEvalError(f"Ожидался символ для '{var_name}', получено {type(value)}")
        elif var_type == STRING_TYPE:
            if not isinstance(value, str):
                raise KumirEvalError(f"Ожидалась строка для '{var_name}', получено {type(value)}")
                
        var_info['value'] = value
        print(f"[DEBUG][Update] Обновлено значение переменной '{var_name}' = {value}", file=sys.stderr)

    # --- Вспомогательные методы для проверки и конвертации типов при присваивании ---

    def _validate_and_convert_value_for_assignment(self, value, target_type, var_name="переменной"):
        """Проверяет тип значения и выполняет неявные преобразования для присваивания."""
        value_type = type(value)

        if target_type == 'цел':
            if value_type is int:
                # Проверка на МАКСЦЕЛ, если нужно
                # if not (-МАКСЦЕЛ - 1 <= value <= МАКСЦЕЛ):
                #    raise AssignmentError(f"Значение {value} выходит за допустимый диапазон для типа ЦЕЛ.", var_name=var_name)
                return value
            elif value_type is float:
                # Нельзя присвоить вещ переменной цел
                raise AssignmentError(f"Нельзя присвоить вещественное значение ({value}) переменной типа ЦЕЛ.")
            else:
                # Другие типы тоже нельзя
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ЦЕЛ.")

        elif target_type == 'вещ':
            if value_type is int:
                # Неявное преобразование цел -> вещ
                return float(value)
            elif value_type is float:
                # Тип совпадает
                return value
            else:
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ВЕЩ.")

        elif target_type == 'лог':
            if value_type is bool:
                return value
            else:
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ЛОГ.")

        elif target_type == 'сим':
            if value_type is str and len(value) == 1:
                return value
            elif value_type is str and len(value) != 1:
                raise AssignmentError(f"Нельзя присвоить строку \"{value}\" (длина {len(value)}) переменной типа СИМ (требуется длина 1).")
            else:
                 raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа СИМ.")

        elif target_type == 'лит':
            if value_type is str:
                 # Неявное преобразование сим -> лит допускается (строка длины 1 - это тоже строка)
                return value
            else:
                raise AssignmentError(f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ЛИТ.")

        else:
            # Неизвестный целевой тип (может быть таблица или ошибка)
            raise DeclarationError(f"Неизвестный или неподдерживаемый целевой тип '{target_type}' для переменной '{var_name}'.")

    # --- Вспомогательные методы для вычислений ---

    def get_full_identifier(self, ctx: KumirParser.QualifiedIdentifierContext) -> str:
        """Возвращает полный текст идентификатора."""
        if ctx:
            return ctx.getText()
        return ""

    # --- Вспомогательные методы для вычислений и проверки типов в выражениях ---

    def _check_numeric(self, value, operation_name):
        """Проверяет, является ли значение числом (цел или вещ)."""
        if value is None:
            raise KumirEvalError(f"Попытка использовать неинициализированное значение в операции '{operation_name}'")
        if not isinstance(value, (int, float)):
            raise KumirEvalError(f"Операция '{operation_name}' не применима к нечисловому типу {type(value).__name__}.")
        return value

    def _check_logical(self, value, operation_name):
        """Проверяет, является ли значение логическим."""
        if value is None:
            raise KumirEvalError(f"Попытка использовать неинициализированное значение в операции '{operation_name}'")
        if not isinstance(value, bool):
            raise KumirEvalError(f"Операция '{operation_name}' не применима к нелогическому типу {type(value).__name__}.")
        return value

    def _check_comparable(self, value, operation_name):
        """Проверяет, что значение можно использовать в операциях сравнения."""
        if value is None:
            raise KumirEvalError(f"Попытка использовать неинициализированное значение в операции '{operation_name}'")
        if not isinstance(value, (int, float, str, bool)):
            raise KumirEvalError(f"Операция '{operation_name}' не применима к типу {type(value).__name__}.")
        return value

    def _perform_binary_operation(self, ctx, ops_map, type_check_func=None):
        """Общая логика для выполнения бинарных операций."""
        left_ctx = ctx.getChild(0)  # Левый операнд
        right_ctx = ctx.getChild(2)  # Правый операнд
        op_token = ctx.getChild(1).symbol  # Токен оператора
        
        left_val = self.visit(left_ctx)
        right_val = self.visit(right_ctx)
        
        # Получаем функцию операции из словаря
        operation = ops_map.get(op_token.type)
        if not operation:
            raise KumirEvalError(f"Неизвестная или неподдерживаемая бинарная операция: {op_token.text}")

        # Особая обработка для разных типов операций
        if op_token.type in [KumirLexer.AND, KumirLexer.OR]:
            # Логические операции
            left_val = self._check_logical(left_val, op_token.text)
            right_val = self._check_logical(right_val, op_token.text)
        elif op_token.type in [KumirLexer.EQ, KumirLexer.NE]:
            # Операции равенства/неравенства - работают с любыми типами
            left_val = self._check_comparable(left_val, op_token.text)
            right_val = self._check_comparable(right_val, op_token.text)
            # Проверяем совместимость типов
            if type(left_val) != type(right_val):
                raise KumirEvalError(f"Несовместимые типы в операции '{op_token.text}': {type(left_val).__name__} и {type(right_val).__name__}")
        elif op_token.type in [KumirLexer.LT, KumirLexer.GT, KumirLexer.LE, KumirLexer.GE]:
            # Операции сравнения - только для чисел и строк одного типа
            left_val = self._check_comparable(left_val, op_token.text)
            right_val = self._check_comparable(right_val, op_token.text)
            if type(left_val) != type(right_val):
                raise KumirEvalError(f"Несовместимые типы в операции '{op_token.text}': {type(left_val).__name__} и {type(right_val).__name__}")
            if not isinstance(left_val, (int, float, str)):
                raise KumirEvalError(f"Операция '{op_token.text}' не применима к типу {type(left_val).__name__}")
        else:
            # Арифметические операции
            left_val = self._check_numeric(left_val, op_token.text)
            right_val = self._check_numeric(right_val, op_token.text)

        # Особая обработка для деления
        if op_token.type == KumirLexer.DIV:  # Обычное деление
            if right_val == 0:
                raise KumirEvalError("Деление на ноль")
            return float(left_val) / float(right_val)
        elif op_token.type in [KumirLexer.DIV_OP, KumirLexer.MOD_OP]:  # div, mod
            if not isinstance(left_val, int) or not isinstance(right_val, int):
                raise KumirEvalError(f"Операция '{op_token.text}' применима только к целым числам")
            if right_val == 0:
                raise KumirEvalError(f"Целочисленное деление или остаток от деления на ноль ('{op_token.text}')")
            return operation(left_val, right_val)
            
        # Выполняем операцию
        try:
            result = operation(left_val, right_val)
            return result
        except TypeError as e:
            raise KumirEvalError(f"Ошибка типа при выполнении операции '{op_token.text}': {e}")
        except Exception as e:
            raise KumirEvalError(f"Ошибка при вычислении '{op_token.text}': {e}")

    # --- Переопределение методов visit --- 

    def visitProgram(self, ctx: KumirParser.ProgramContext):
        print("[DEBUG][Visit] Начало программы (program)", file=sys.stderr)
        # Глобальная область уже создана в __init__
        # Сбрасываем состояние вывода
        self.had_output = False
        self.last_output = ""
        self.suppress_newline = False
        
        # Обходим все алгоритмы в файле
        result = self.visitChildren(ctx)
        
        # Если были операторы вывода, добавляем финальный перевод строки
        if self.had_output:
            print("", end='\n')
            
        print("[DEBUG][Visit] Конец программы (program)", file=sys.stderr)
        return result

    def visitImplicitModuleBody(self, ctx: KumirParser.ImplicitModuleBodyContext):
        """Обработка неявного тела модуля (программы без явного объявления модуля)."""
        print("[DEBUG][Visit] Обработка implicitModuleBody", file=sys.stderr)
        return self.visitChildren(ctx)

    def visitModuleDefinition(self, ctx: KumirParser.ModuleDefinitionContext):
        """Обработка определения модуля."""
        print("[DEBUG][Visit] Обработка moduleDefinition", file=sys.stderr)
        return self.visitChildren(ctx)

    def visitAlgorithmDefinition(self, ctx: KumirParser.AlgorithmDefinitionContext):
        """
        Обработка определения алгоритма
        """
        print("Entering algorithm definition", file=sys.stderr)
        # Обработка заголовка алгоритма
        header = ctx.algorithmHeader()
        if header:
            print(f"Processing algorithm header: {header.getText()}", file=sys.stderr)

        # Обработка тела алгоритма
        body = ctx.algorithmBody()
        if body:
            print(f"Processing algorithm body", file=sys.stderr)
            self.visit(body)

        print("Exiting algorithm definition", file=sys.stderr)
        return None

    # Обработка объявлений скалярных переменных
    def visitVariableDeclaration(self, ctx: KumirParser.VariableDeclarationContext):
        print(f"[DEBUG][Visit] Обработка variableDeclaration", file=sys.stderr)
        type_ctx = ctx.typeSpecifier()
        
        # Определяем тип переменной
        if type_ctx.basicType():
            type_token = type_ctx.basicType().start
            kumir_type = TYPE_MAP.get(type_token.type)
            is_table = bool(type_ctx.TABLE_SUFFIX())
        elif type_ctx.arrayType():
            array_type = type_ctx.arrayType()
            # TODO: Обработка массивов
            raise NotImplementedError("Массивы пока не поддерживаются")
        elif type_ctx.actorType():
            actor_type = type_ctx.actorType()
            # TODO: Обработка специальных типов
            raise NotImplementedError("Специальные типы пока не поддерживаются")
        else:
            raise Exception("Неизвестный тип переменной")

        if not kumir_type:
            raise Exception(f"Неизвестный тип переменной: {type_token.text}")
            
        # Обходим список переменных
        for var_decl in ctx.variableList().variableDeclarationItem():
            var_name = var_decl.ID().getText()
            dimensions = None
            
            if var_decl.arrayBounds():
                # TODO: Обработка размерностей таблицы
                print(f"  -> Диапазоны для таблицы '{var_name}' пока не вычисляются.", file=sys.stderr)
                
            # Объявляем переменную с значением по умолчанию
            self.declare_variable(var_name, kumir_type, is_table=is_table, dimensions=dimensions)
            
            # Если есть инициализация, присваиваем значение
            if var_decl.expression():
                value = self.visit(var_decl.expression())
                if value is None:
                    value = get_default_value(kumir_type)
                self.update_variable(var_name, value)
            else:
                # Если нет инициализации, используем значение по умолчанию
                value = get_default_value(kumir_type)
                self.update_variable(var_name, value)
                
        return None

    # Обработка узла многословного идентификатора (переименован)
    def visitQualifiedIdentifier(self, ctx: KumirParser.QualifiedIdentifierContext):
        # Возвращаем идентификатор
        return self.get_full_identifier(ctx)

    # Обработка узла переменной
    def visitLvalue(self, ctx: KumirParser.LvalueContext):
        if ctx.RETURN_VALUE():
            print(f"[DEBUG][Visit] Обращение к специальной переменной 'знач'", file=sys.stderr)
            raise NotImplementedError("Обращение к 'знач' пока не реализовано.")
            
        var_name = self.get_full_identifier(ctx.qualifiedIdentifier())
        print(f"[DEBUG][Visit] Обращение к переменной/таблице: '{var_name}'", file=sys.stderr)
        
        var_info, _ = self.find_variable(var_name)
        if var_info is None:
            # Добавляем информацию о строке и столбце
            line = ctx.start.line
            column = ctx.start.column
            raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная '{var_name}' не найдена.")

        if ctx.indexList():
            print(f"  -> Это обращение к таблице '{var_name}'", file=sys.stderr)
            if not var_info['is_table']:
                line = ctx.start.line
                column = ctx.start.column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Попытка доступа по индексу к не табличной переменной '{var_name}'.")
            # TODO: Обработка индексов таблиц
            raise NotImplementedError(f"Обращение к элементу таблицы '{var_name}' пока не реализовано.")
        else:
            if var_info['is_table']:
                 print(f"  -> Это обращение ко всей таблице '{var_name}' (возвращаем словарь)", file=sys.stderr)
                 return var_info['value']
            else:
                print(f"  -> Возвращаем значение переменной '{var_name}': {var_info['value']}", file=sys.stderr)
                return var_info['value']

    # Обработка присваивания
    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        if ctx.lvalue():
            lvalue_ctx = ctx.lvalue()
            value = self.visit(ctx.expression()) 
            
            if lvalue_ctx.RETURN_VALUE():
                print("  -> Присваивание результату функции (знач)", file=sys.stderr)
                raise NotImplementedError("Присваивание результату функции (знач) пока не реализовано.")
            else:
                target_name = self.get_full_identifier(lvalue_ctx.qualifiedIdentifier())
                
                if lvalue_ctx.indexList():
                    print(f"  -> Присваивание элементу таблицы: '{target_name}[...]'", file=sys.stderr)
                    raise NotImplementedError(f"Присваивание элементу таблицы '{target_name}' пока не реализовано.")
                else:
                    try:
                        self.update_variable(target_name, value) 
                    except (AssignmentError, DeclarationError, KumirExecutionError) as e:
                        line = ctx.start.line
                        column = ctx.start.column
                        raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка присваивания '{target_name}': {e}")
                    except Exception as e: 
                        line = ctx.start.line
                        column = ctx.start.column
                        raise KumirExecutionError(f"Строка {line}, столбец {column}: Неожиданная ошибка при присваивании '{target_name}': {e}")
        else:
            # Это выражение-оператор (например, вызов процедуры)
            value = self.visit(ctx.expression())
            # Игнорируем возвращаемое значение, если оно есть
            
        return None

    # --- Обработка выражений --- 

    def visitExpression(self, ctx:KumirParser.ExpressionContext):
        # Стартовое правило для выражения - просто передаем дальше
        return self.visitChildren(ctx)

    def visitLogicalOrExpression(self, ctx:KumirParser.LogicalOrExpressionContext):
        if len(ctx.children) > 1:  # Есть операция ИЛИ
            return self._perform_binary_operation(ctx, LOGICAL_OPS)
        return self.visit(ctx.logicalAndExpression(0))

    def visitLogicalAndExpression(self, ctx:KumirParser.LogicalAndExpressionContext):
        if len(ctx.children) > 1:  # Есть операция И
            return self._perform_binary_operation(ctx, LOGICAL_OPS)
        return self.visit(ctx.equalityExpression(0))

    def visitEqualityExpression(self, ctx:KumirParser.EqualityExpressionContext):
        if len(ctx.children) > 1:  # Есть операция = или <>
            return self._perform_binary_operation(ctx, COMPARISON_OPS)
        return self.visit(ctx.relationalExpression(0))

    def visitRelationalExpression(self, ctx:KumirParser.RelationalExpressionContext):
        if len(ctx.children) > 1:  # Есть операция <, >, <=, >=
            return self._perform_binary_operation(ctx, COMPARISON_OPS)
        return self.visit(ctx.additiveExpression(0))

    def visitAdditiveExpression(self, ctx:KumirParser.AdditiveExpressionContext):
        if len(ctx.children) > 1: 
            result = self.visit(ctx.getChild(0))
            i = 1
            while i < len(ctx.children):
                op_token = ctx.getChild(i).symbol
                right_val = self.visit(ctx.getChild(i+1))
                
                result = self._check_numeric(result, op_token.text)
                right_val = self._check_numeric(right_val, op_token.text)
                
                operation = ARITHMETIC_OPS.get(op_token.type)
                if not operation:
                    raise KumirEvalError(f"Неизвестная операция сложения/вычитания: {op_token.text}")
                try:
                    result = operation(result, right_val)
                except Exception as e:
                    raise KumirEvalError(f"Ошибка при вычислении '{op_token.text}': {e}")
                i += 2
            return result
        else:
            return self.visit(ctx.multiplicativeExpression(0))

    def visitMultiplicativeExpression(self, ctx:KumirParser.MultiplicativeExpressionContext):
        if len(ctx.children) > 1: 
            result = self.visit(ctx.getChild(0))
            i = 1
            while i < len(ctx.children):
                op_token = ctx.getChild(i).symbol
                right_val = self.visit(ctx.getChild(i+1))
                
                result = self._check_numeric(result, op_token.text)
                right_val = self._check_numeric(right_val, op_token.text)
                
                operation = ARITHMETIC_OPS.get(op_token.type)
                if not operation:
                     raise KumirEvalError(f"Неизвестная операция умножения/деления: {op_token.text}")
                
                # Особая обработка для деления, div, mod
                if op_token.type == KumirLexer.DIV:
                    if right_val == 0: raise KumirEvalError("Деление на ноль.")
                    result = float(result) / float(right_val)
                elif op_token.type in [KumirLexer.DIV_OP, KumirLexer.MOD_OP]:
                    if not isinstance(result, int) or not isinstance(right_val, int):
                        raise KumirEvalError(f"Операция '{op_token.text}' применима только к целым числам.")
                    if right_val == 0:
                        raise KumirEvalError(f"Целочисленное деление или остаток от деления на ноль ('{op_token.text}').")
                    result = operation(result, right_val)
                else: # Умножение
                    try:
                        result = operation(result, right_val)
                    except Exception as e:
                         raise KumirEvalError(f"Ошибка при вычислении '{op_token.text}': {e}")
                i += 2
            return result
        else:
            return self.visit(ctx.powerExpression(0))
        
    def visitPowerExpression(self, ctx:KumirParser.PowerExpressionContext):
        if ctx.POWER():
            return self._perform_binary_operation(ctx, ARITHMETIC_OPS)
        else:
            return self.visit(ctx.unaryExpression())

    def visitUnaryExpression(self, ctx:KumirParser.UnaryExpressionContext):
        if ctx.PLUS() or ctx.MINUS() or ctx.NOT():
            op = None
            if ctx.PLUS(): op = '+'
            if ctx.MINUS(): op = '-'
            if ctx.NOT(): op = 'не'
            
            operand_value = self.visit(ctx.unaryExpression())
            
            if op == '+':
                return self._check_numeric(operand_value, "унарный плюс")
            elif op == '-':
                return -self._check_numeric(operand_value, "унарный минус")
            elif op == 'не':
                operand_value = self._check_logical(operand_value, "операция НЕ")
                return not operand_value
        else:
            return self.visit(ctx.postfixExpression())

    def visitPostfixExpression(self, ctx:KumirParser.PostfixExpressionContext):
        result = self.visit(ctx.primaryExpression())
        
        # Обработка индексов и вызовов функций
        for i in range(1, len(ctx.children), 2):
            if ctx.getChild(i).getText() == '[':
                # Обработка индексов
                if not isinstance(result, dict) or 'is_table' not in result:
                    raise KumirEvalError(f"Попытка доступа по индексу к не табличной переменной")
                # TODO: Обработка индексов таблиц
                raise NotImplementedError("Доступ к элементам таблиц пока не реализован")
            elif ctx.getChild(i).getText() == '(':
                # Обработка вызова функции
                # TODO: Реализовать вызов функций
                raise NotImplementedError("Вызов функций пока не реализован")
                
        return result

    def visitPrimaryExpression(self, ctx:KumirParser.PrimaryExpressionContext):
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.qualifiedIdentifier():
            var_name = self.get_full_identifier(ctx.qualifiedIdentifier())
            var_info, _ = self.find_variable(var_name)
            if var_info is None:
                line = ctx.start.line
                column = ctx.start.column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная '{var_name}' не найдена.")
            return var_info['value']
        elif ctx.RETURN_VALUE():
            raise NotImplementedError("Доступ к 'знач' пока не реализован")
        elif ctx.expression():
            return self.visit(ctx.expression())
        elif ctx.arrayLiteral():
            return self.visit(ctx.arrayLiteral())
        return None
        
    # --- Метод visitLoopStatement --- 
    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        # Получаем спецификатор цикла
        loop_spec = ctx.loopSpecifier()
        if not loop_spec:
            # TODO: Цикл без условия (до)
            raise NotImplementedError("Цикл без условия (до) пока не реализован")
            
        if loop_spec.FOR():  # Цикл ДЛЯ
            loop_var_name = loop_spec.ID().getText()
            start_val_ctx = loop_spec.expression(0)
            end_val_ctx = loop_spec.expression(1)
            step_ctx = loop_spec.expression(2) if len(loop_spec.expression()) > 2 else None

            # Вычисляем границы и шаг
            try:
                start_val = self.visit(start_val_ctx)
                end_val = self.visit(end_val_ctx)
                step_val = 1
                if step_ctx:
                    step_val = self.visit(step_ctx)
            except Exception as e:
                 line = start_val_ctx.start.line
                 column = start_val_ctx.start.column
                 raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка вычисления границ или шага цикла ДЛЯ: {e}")

            # Проверяем типы границ и шага
            if not isinstance(start_val, int):
                line = start_val_ctx.start.line
                column = start_val_ctx.start.column
                raise KumirEvalError(f"Строка {line}, столбец {column}: Начальное значение цикла ДЛЯ ('{start_val}') должно быть целым.")
            if not isinstance(end_val, int):
                line = end_val_ctx.start.line
                column = end_val_ctx.start.column
                raise KumirEvalError(f"Строка {line}, столбец {column}: Конечное значение цикла ДЛЯ ('{end_val}') должно быть целым.")
            if not isinstance(step_val, int):
                 line = step_ctx.start.line if step_ctx else start_val_ctx.start.line # Приблизительно
                 column = step_ctx.start.column if step_ctx else start_val_ctx.start.column
                 raise KumirEvalError(f"Строка {line}, столбец {column}: Шаг цикла ДЛЯ ('{step_val}') должен быть целым.")
            if step_val == 0:
                 line = step_ctx.start.line if step_ctx else start_val_ctx.start.line
                 column = step_ctx.start.column if step_ctx else start_val_ctx.start.column
                 raise KumirEvalError(f"Строка {line}, столбец {column}: Шаг цикла ДЛЯ не может быть равен нулю.")

            print(f"[DEBUG][Visit] Начало цикла ДЛЯ '{loop_var_name}' от {start_val} до {end_val} шаг {step_val}", file=sys.stderr)

            # Находим информацию о переменной цикла в текущей или внешней области
            var_info, var_scope = self.find_variable(loop_var_name)
            if var_info is None:
                line = loop_spec.ID().getSymbol().line
                column = loop_spec.ID().getSymbol().column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная цикла ДЛЯ '{loop_var_name}' не найдена.")
            if var_info.get('is_table'):
                line = loop_spec.ID().getSymbol().line
                column = loop_spec.ID().getSymbol().column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная цикла ДЛЯ '{loop_var_name}' не может быть таблицей.")
            if var_info.get('type') != 'цел':
                line = loop_spec.ID().getSymbol().line
                column = loop_spec.ID().getSymbol().column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная цикла ДЛЯ '{loop_var_name}' должна быть целого типа, а не '{var_info.get('type')}'.")

            # Определяем диапазон итераций
            current_val = start_val
            iteration_count = 0

            try:
                # Итерация цикла
                if step_val > 0:
                    while current_val <= end_val:
                        iteration_count += 1
                        if iteration_count > 100000: # Защита от бесконечных циклов
                             raise KumirExecutionError(f"Превышено максимальное число итераций цикла ДЛЯ ({iteration_count})")
                        # Обновляем значение переменной в ее области видимости
                        var_info['value'] = current_val 
                        print(f"  -> Итерация {iteration_count}: {loop_var_name} = {current_val}", file=sys.stderr)
                        # Выполняем тело цикла
                        self.visit(ctx.statementSequence())
                        current_val += step_val
                elif step_val < 0:
                     while current_val >= end_val:
                        iteration_count += 1
                        if iteration_count > 100000:
                             raise KumirExecutionError(f"Превышено максимальное число итераций цикла ДЛЯ ({iteration_count})")
                        var_info['value'] = current_val
                        print(f"  -> Итерация {iteration_count}: {loop_var_name} = {current_val}", file=sys.stderr)
                        self.visit(ctx.statementSequence())
                        current_val += step_val
                # Если start_val > end_val при step > 0 или start_val < end_val при step < 0, цикл не выполнится
                
            except Exception as loop_body_error:
                 # Перехватываем ошибки из тела цикла и добавляем информацию
                 line = ctx.statementSequence().start.line
                 column = ctx.statementSequence().start.column
                 raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ДЛЯ: {loop_body_error}")

            print(f"[DEBUG][Visit] Конец цикла ДЛЯ '{loop_var_name}'. Итераций: {iteration_count}", file=sys.stderr)
            
        elif loop_spec.WHILE():  # Цикл ПОКА
            condition_ctx = loop_spec.expression(0)
            print(f"[DEBUG][Visit] Начало цикла ПОКА", file=sys.stderr)
            
            iteration_count = 0
            max_iterations = 100000 # Защита

            while True:
                iteration_count += 1
                if iteration_count > max_iterations:
                    raise KumirExecutionError(f"Превышено максимальное число итераций цикла ПОКА ({iteration_count})")

                # Вычисляем условие
                try:
                    condition_value = self.visit(condition_ctx)
                except Exception as e:
                    line = condition_ctx.start.line
                    column = condition_ctx.start.column
                    raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка вычисления условия цикла ПОКА: {e}")
                
                # Проверяем тип условия
                if not isinstance(condition_value, bool):
                     line = condition_ctx.start.line
                     column = condition_ctx.start.column
                     raise KumirEvalError(f"Строка {line}, столбец {column}: Условие цикла ПОКА ('{condition_value}') должно быть логического типа, а не {type(condition_value).__name__}.")

                print(f"  -> Итерация {iteration_count}: Условие = {condition_value}", file=sys.stderr)
                if not condition_value: # Если условие == нет (False)
                    break # Выход из цикла

                # Выполняем тело цикла
                try:
                    self.visit(ctx.statementSequence())
                except Exception as loop_body_error:
                     line = ctx.statementSequence().start.line
                     column = ctx.statementSequence().start.column
                     raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ПОКА: {loop_body_error}")

            print(f"[DEBUG][Visit] Конец цикла ПОКА. Итераций: {iteration_count - 1}", file=sys.stderr) # -1 т.к. последняя проверка условия была лишней
            
        elif loop_spec.expression():  # Цикл РАЗ
            # TODO: Реализовать цикл РАЗ
            raise NotImplementedError("Цикл РАЗ пока не реализован")
            
        return None

    def visitIfStatement(self, ctx:KumirParser.IfStatementContext):
        """Обработка условного оператора."""
        print("[DEBUG][Visit] Обработка ifStatement", file=sys.stderr)
        
        # Вычисляем условие
        condition_ctx = ctx.expression()
        try:
            condition_value = self.visit(condition_ctx)
        except Exception as e:
            line = condition_ctx.start.line
            column = condition_ctx.start.column
            raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка вычисления условия: {e}")
        
        # Проверяем тип условия
        if not isinstance(condition_value, bool):
            line = condition_ctx.start.line
            column = condition_ctx.start.column
            raise KumirEvalError(f"Строка {line}, столбец {column}: Условие должно быть логического типа, а не {type(condition_value).__name__}.")
        
        print(f"  -> Условие = {condition_value}", file=sys.stderr)
        
        # Выполняем соответствующую ветвь
        if condition_value:
            # Ветвь "то"
            if ctx.statementSequence():
                return self.visit(ctx.statementSequence(0))
        else:
            # Ветвь "иначе", если есть
            if len(ctx.statementSequence()) > 1:
                return self.visit(ctx.statementSequence(1))
                
        return None

    def _handle_input(self, arg_ctx):
        """Вспомогательный метод для обработки ввода значения."""
        # Получаем контекст expression
        expressions = arg_ctx.expression()
        if not expressions or not expressions[0]:
            raise KumirEvalError(
                f"Некорректный аргумент ввода в строке {arg_ctx.start.line}, столбец {arg_ctx.start.column}"
            )
            
        # Первое выражение должно быть идентификатором
        expr_ctx = expressions[0]
        # Получаем имя переменной через visit
        try:
            var_name = expr_ctx.getText()
        except Exception:
            raise KumirEvalError(
                f"Ожидается имя переменной для ввода в строке {expr_ctx.start.line}"
            )
            
        if not isinstance(var_name, str):
            raise KumirEvalError(
                f"Некорректное имя переменной: {var_name} в строке {expr_ctx.start.line}"
            )
            
        # Находим информацию о переменной
        var_info, _ = self.find_variable(var_name)
        if var_info is None:
            raise KumirEvalError(
                f"Переменная '{var_name}' не найдена в строке {expr_ctx.start.line}"
            )
            
        # Запрашиваем ввод с учетом типа
        type_name = var_info['type']
        try:
            value = input()
            if type_name == 'цел':
                value = int(value)
            elif type_name == 'вещ':
                value = float(value)
            elif type_name == 'лог':
                value_str = value.lower()
                if value_str == 'да':
                    value = True
                elif value_str == 'нет':
                    value = False
                else:
                    raise ValueError("Ожидается 'да' или 'нет'")
            elif type_name == 'сим':
                if len(value) != 1:
                    raise ValueError("Ожидается один символ")
            elif type_name == 'лит':
                pass  # Строка уже в правильном формате
            else:
                raise KumirEvalError(f"Неподдерживаемый тип для ввода: {type_name}")
                
            # Обновляем значение переменной
            self.update_variable(var_name, value)
            
        except ValueError as e:
            raise KumirEvalError(
                f"Ошибка при вводе значения для '{var_name}' в строке {expr_ctx.start.line}: {str(e)}"
            )
        except Exception as e:
            raise KumirEvalError(
                f"Неожиданная ошибка при вводе для '{var_name}' в строке {expr_ctx.start.line}: {str(e)}"
            )

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext):
        """Обработка оператора ввода-вывода."""
        print("[DEBUG][Visit] Обработка ioStatement", file=sys.stderr)
        
        # Определяем тип операции (ввод/вывод)
        is_input = ctx.INPUT() is not None
        
        # Получаем список аргументов
        args = ctx.ioArgumentList().ioArgument() if ctx.ioArgumentList() else []
        
        if is_input:
            # Обработка оператора ввода
            for arg_ctx in args:
                try:
                    # Получаем контекст выражения для переменной
                    lvalue_ctx = arg_ctx.expression()
                    if not lvalue_ctx:
                        line = arg_ctx.start.line
                        column = arg_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Отсутствует выражение для ввода")
                    
                    # Получаем имя переменной
                    var_name = self.get_variable_name(lvalue_ctx)
                    if not var_name:
                        line = lvalue_ctx.start.line
                        column = lvalue_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Не удалось получить имя переменной для ввода")
                    
                    # Находим информацию о переменной
                    var_info, var_scope = self.find_variable(var_name)
                    if var_info is None:
                        line = lvalue_ctx.start.line
                        column = lvalue_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Переменная '{var_name}' не найдена")
                    
                    # Запрашиваем ввод у пользователя
                    prompt = f"Введите значение для переменной '{var_name}' ({var_info['type']}): "
                    value = input(prompt)
                    
                    # Преобразуем введенное значение в нужный тип
                    try:
                        if var_info['type'] == INTEGER_TYPE:
                            value = int(value)
                        elif var_info['type'] == FLOAT_TYPE:
                            value = float(value)
                        elif var_info['type'] == BOOLEAN_TYPE:
                            value = value.lower() == 'да'
                        elif var_info['type'] == CHAR_TYPE:
                            if len(value) != 1:
                                raise ValueError("Для символьного типа требуется ровно один символ")
                            value = value[0]
                        # Для строкового типа преобразование не требуется
                    except ValueError as e:
                        line = lvalue_ctx.start.line
                        column = lvalue_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка преобразования типа для '{var_name}': {e}")
                    
                    # Обновляем значение переменной
                    var_scope[var_name]['value'] = value
                    
                except Exception as e:
                    if not isinstance(e, KumirEvalError):
                        line = arg_ctx.start.line if arg_ctx else ctx.start.line
                        column = arg_ctx.start.column if arg_ctx else ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка при обработке ввода: {e}")
                    raise
        else:
            # Обработка оператора вывода
            output = []
            has_newline = True  # По умолчанию добавляем перевод строки
            
            for arg_ctx in args:
                try:
                    # Проверяем наличие спецификатора "нс"
                    if arg_ctx.NEWLINE_CONST():
                        has_newline = False
                        continue
                    
                    # Получаем значение выражения
                    expr_ctx = arg_ctx.expression()
                    if expr_ctx:
                        value = self.visit(expr_ctx)
                        if value is None:
                            line = expr_ctx.start.line
                            column = expr_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вывести неинициализированное значение")
                        
                        # Форматируем значение для вывода
                        if isinstance(value, bool):
                            value = "да" if value else "нет"
                        elif isinstance(value, (int, float)):
                            # Проверяем наличие спецификаторов ширины и точности
                            width = None
                            precision = None
                            if arg_ctx.INTEGER():
                                width = int(arg_ctx.INTEGER().getText())
                            if arg_ctx.FLOAT():
                                precision = int(arg_ctx.FLOAT().getText())
                            
                            # Применяем форматирование
                            if precision is not None:
                                value = f"{value:.{precision}f}"
                            else:
                                value = str(value)
                            
                            if width is not None:
                                value = value.rjust(width)
                        else:
                            value = str(value)
                        
                        output.append(value)
                    
                    # Проверяем наличие строкового литерала
                    elif arg_ctx.STRING():
                        text = arg_ctx.STRING().getText()
                        # Удаляем кавычки и экранирование
                        text = text[1:-1].replace('\\"', '"')
                        # Добавляем пробел после двоеточия
                        text = text.replace(":", ": ")
                        output.append(text)
                    
                except Exception as e:
                    if not isinstance(e, KumirEvalError):
                        line = arg_ctx.start.line if arg_ctx else ctx.start.line
                        column = arg_ctx.start.column if arg_ctx else ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка при обработке вывода: {e}")
                    raise
            
            # Выводим результат
            if output:
                print("".join(output), end='\n' if has_newline else '', file=sys.stdout)
        
        return None

    def visitSwitchStatement(self, ctx:KumirParser.SwitchStatementContext):
        """Обработка оператора выбора."""
        print("[DEBUG][Visit] Обработка switchStatement", file=sys.stderr)
        
        # Получаем значение для выбора
        switch_value = self.visit(ctx.expression())
        print(f"  -> Значение для выбора = {switch_value}", file=sys.stderr)
        
        # Проходим по всем вариантам
        for case_ctx in ctx.caseBlock():
            case_value = self.visit(case_ctx.expression())
            print(f"  -> Проверяем вариант: {case_value}", file=sys.stderr)
            
            if case_value == switch_value:
                print(f"  -> Выполняем вариант: {case_value}", file=sys.stderr)
                return self.visit(case_ctx.statementSequence())
        
        return None

    def visitLiteral(self, ctx:KumirParser.LiteralContext):
        """Обработка литералов."""
        if ctx.INTEGER():
            return int(ctx.INTEGER().getText())
        elif ctx.REAL():
            return float(ctx.REAL().getText())
        elif ctx.STRING():
            text = ctx.STRING().getText()
            # Убираем кавычки и обрабатываем escape-последовательности
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            return text.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace("\\'", "'")
        elif ctx.CHAR_LITERAL():
            text = ctx.CHAR_LITERAL().getText()
            # Убираем кавычки и обрабатываем escape-последовательности
            if text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            return text.replace('\\n', '\n').replace('\\t', '\t').replace("\\'", "'")
        elif ctx.TRUE():
            return True
        elif ctx.FALSE():
            return False
        elif ctx.NEWLINE_CONST():
            return '\n'
        elif ctx.colorLiteral():
            return self.visit(ctx.colorLiteral())
        return None

    def debug_print(self, message):
        """Выводит отладочное сообщение, если включен режим отладки."""
        if self.debug:
            print(f"[DEBUG] {message}", file=sys.stderr)

    def get_variable_type(self, var_name):
        """Возвращает тип переменной из текущей области видимости."""
        # Ищем переменную во всех областях видимости, начиная с текущей
        for scope in reversed(self.scopes):
            if var_name in scope:
                return scope[var_name]['type']
        raise KumirEvalError(f"Переменная '{var_name}' не найдена")

    def get_variable_name(self, expr_ctx):
        """Получает имя переменной из контекста выражения."""
        if isinstance(expr_ctx, KumirParser.QualifiedIdentifierContext):
            return expr_ctx.ID().getText()
        elif isinstance(expr_ctx, KumirParser.PrimaryExpressionContext):
            return self.get_variable_name(expr_ctx.qualifiedIdentifier())
        elif isinstance(expr_ctx, KumirParser.PostfixExpressionContext):
            return self.get_variable_name(expr_ctx.primaryExpression())
        elif isinstance(expr_ctx, KumirParser.UnaryExpressionContext):
            return self.get_variable_name(expr_ctx.postfixExpression())
        elif isinstance(expr_ctx, KumirParser.PowerExpressionContext):
            return self.get_variable_name(expr_ctx.unaryExpression())
        elif isinstance(expr_ctx, KumirParser.MultiplicativeExpressionContext):
            return self.get_variable_name(expr_ctx.powerExpression(0))
        elif isinstance(expr_ctx, KumirParser.AdditiveExpressionContext):
            return self.get_variable_name(expr_ctx.multiplicativeExpression(0))
        elif isinstance(expr_ctx, KumirParser.RelationalExpressionContext):
            return self.get_variable_name(expr_ctx.additiveExpression(0))
        elif isinstance(expr_ctx, KumirParser.EqualityExpressionContext):
            return self.get_variable_name(expr_ctx.relationalExpression(0))
        elif isinstance(expr_ctx, KumirParser.LogicalAndExpressionContext):
            return self.get_variable_name(expr_ctx.equalityExpression(0))
        elif isinstance(expr_ctx, KumirParser.LogicalOrExpressionContext):
            return self.get_variable_name(expr_ctx.logicalAndExpression(0))
        elif isinstance(expr_ctx, KumirParser.ExpressionContext):
            return self.get_variable_name(expr_ctx.logicalOrExpression())
        else:
            raise KumirEvalError(f"Не удалось получить имя переменной из выражения: {expr_ctx.getText()}")

def interpret_kumir(code: str):
    """
    Интерпретирует код на языке КуМир.
    
    Args:
        code (str): Исходный код программы
        
    Returns:
        str: Захваченный вывод программы
    """
    from antlr4 import InputStream, CommonTokenStream
    from .generated.KumirLexer import KumirLexer
    from .generated.KumirParser import KumirParser
    
    print("[DEBUG][Interpreter] Начало интерпретации", file=sys.stderr)
    print(f"[DEBUG][Interpreter] Код программы:\n{code}", file=sys.stderr)
    
    # Создаем поток символов из кода
    input_stream = InputStream(code)
    
    # Создаем лексер
    lexer = KumirLexer(input_stream)
    lexer.removeErrorListeners() # Убираем стандартный обработчик ошибок
    lexer.addErrorListener(DiagnosticErrorListener()) # Добавляем свой обработчик ошибок
    
    # Создаем поток токенов
    token_stream = CommonTokenStream(lexer)
    
    # Создаем парсер
    parser = KumirParser(token_stream)
    parser.removeErrorListeners() # Убираем стандартный обработчик ошибок
    parser.addErrorListener(DiagnosticErrorListener()) # Добавляем свой обработчик ошибок
    
    print("[DEBUG][Interpreter] Парсинг программы", file=sys.stderr)
    # Получаем дерево разбора
    tree = parser.program()
    
    print("[DEBUG][Interpreter] Создание интерпретатора", file=sys.stderr)
    # Создаем интерпретатор
    visitor = KumirInterpreterVisitor()
    
    print("[DEBUG][Interpreter] Начало выполнения", file=sys.stderr)
    # Выполняем программу
    visitor.visit(tree)
    
    print("[DEBUG][Interpreter] Конец выполнения", file=sys.stderr)
    return ""