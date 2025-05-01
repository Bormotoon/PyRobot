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
# Исключение для команды ВЫХОД из цикла
class LoopExitException(Exception):
    pass

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
import random # <-- Добавляем импорт random
import antlr4

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

    # --- Словарь для встроенных функций/процедур ---
    # Используем строки для имен ключей, чтобы избежать путаницы с регистром
    BUILTIN_FUNCTIONS = {
        'rand': {
            0: lambda: random.random(), # rand()
            2: lambda a, b: random.uniform(a, b) # rand(A, B)
        },
        'irand': {
            0: lambda: random.randint(0, МАКСЦЕЛ), # irand()
            1: lambda n: random.randint(0, n - 1) if n > 0 else 0, # irand(N)
            2: lambda a, b: random.randint(min(a,b), max(a,b)) # irand(A, B) - Кумир требует min/max
        },
        'printBin': {
            1: lambda n: print(format(self._get_value(n), '08b'), end='') # printBin(N) - выводит число в двоичном виде
        }
    }

    def __init__(self):
        super().__init__()
        self.variables = {}  # Глобальные переменные
        self.scopes = [{}]  # Стек областей видимости, начинаем с глобальной
        self.current_scope = self.scopes[0]  # Текущая область видимости
        self.debug = True  # Флаг для отладочного вывода
        self.had_output = False
        self.last_output = ""  # Буфер для накопления вывода
        self.suppress_newline = False  # Флаг для подавления переноса строки
        self.procedures = {}  # Словарь для хранения определений процедур

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

    def _get_value(self, value):
        """Извлекает значение из переменной или возвращает само значение."""
        if isinstance(value, dict) and 'value' in value:
            return value['value']
        return value

    def _check_numeric(self, value, operation_name):
        """Проверяет, является ли значение числом (цел или вещ)."""
        value = self._get_value(value)
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
        value = self._get_value(value)
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
            if not (isinstance(left_val, (int, float)) and isinstance(right_val, (int, float))):
                if type(left_val) != type(right_val):
                    raise KumirEvalError(f"Несовместимые типы в операции '{op_token.text}': {type(left_val).__name__} и {type(right_val).__name__}")
        elif op_token.type in [KumirLexer.LT, KumirLexer.GT, KumirLexer.LE, KumirLexer.GE]:
            # Операции сравнения - только для чисел и строк одного типа
            left_val = self._check_comparable(left_val, op_token.text)
            right_val = self._check_comparable(right_val, op_token.text)
            # --- ИСПРАВЛЕНИЕ: Разрешаем сравнение int и float --- 
            is_left_num = isinstance(left_val, (int, float))
            is_right_num = isinstance(right_val, (int, float))
            if not ((is_left_num and is_right_num) or (type(left_val) == type(right_val))):
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
        """Обрабатывает всю программу."""
        # Сначала собираем все определения процедур
        self._collect_procedure_definitions(ctx)
        # Затем выполняем программу
        return self.visitChildren(ctx)

    def _collect_procedure_definitions(self, ctx: KumirParser.ProgramContext):
        """Собирает все определения процедур перед выполнением программы."""
        for child in ctx.children:
            if isinstance(child, KumirParser.AlgorithmDefinitionContext):
                # Получаем имя процедуры
                name = child.algorithmHeader().qualifiedIdentifier().getText()
                # Сохраняем определение процедуры
                self.procedures[name] = child

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
        print(f"[DEBUG][Visit Expression] Контекст: {ctx.getText()}", file=sys.stderr)
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
        if ctx.getChildCount() == 2: # Есть оператор
            op_symbol = ctx.getChild(0).symbol
            operand_value = self.visit(ctx.getChild(1)) # Посещаем операнд (который тоже unaryExpression)

            op_type = op_symbol.type
            op_text = op_symbol.text
            if self.debug: print(f"[DEBUG][Visit] UnaryExpression: {op_text} {operand_value}", file=sys.stderr)
            
            if op_type == KumirLexer.PLUS:
                result = self._check_numeric(operand_value, 'унарный +')
                if self.debug: print(f"[DEBUG][Unary] Результат +: {result}", file=sys.stderr)
                return result
            elif op_type == KumirLexer.MINUS:
                result = -self._check_numeric(operand_value, 'унарный -')
                if self.debug: print(f"[DEBUG][Unary] Результат -: {result}", file=sys.stderr)
                return result
            elif op_type == KumirLexer.NOT:
                result = not self._check_logical(operand_value, 'не')
                if self.debug: print(f"[DEBUG][Unary] Результат НЕ: {result}", file=sys.stderr)
                return result
        else:
            # Просто postfixExpression
            if self.debug: print(f"[DEBUG][Visit] UnaryExpression -> PostfixExpression", file=sys.stderr)
            return self.visit(ctx.postfixExpression())

    def visitPostfixExpression(self, ctx:KumirParser.PostfixExpressionContext):
        """Обрабатывает постфиксные выражения, включая вызовы процедур."""
        # Сначала обрабатываем primaryExpression
        primary = ctx.primaryExpression()
        if not primary:
            raise KumirEvalError("Отсутствует primaryExpression в postfixExpression")

        # Получаем значение primaryExpression
        value = self.visit(primary)

        # Обрабатываем постфиксные операции (индексы и вызовы)
        for i in range(1, ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, antlr4.tree.Tree.TerminalNode):
                continue  # Пропускаем терминальные узлы (скобки и т.д.)

            if child.getRuleIndex() == KumirParser.RULE_indexList:
                # Обработка индексации массива
                if not isinstance(value, list):
                    raise KumirEvalError("Попытка индексации не массива")
                index = self.visit(child)
                if not isinstance(index, int):
                    raise KumirEvalError("Индекс массива должен быть целым числом")
                if index < 0 or index >= len(value):
                    raise KumirEvalError(f"Индекс {index} вне границ массива [0..{len(value)-1}]")
                value = value[index]

            elif child.getRuleIndex() == KumirParser.RULE_argumentList:
                # Обработка вызова процедуры
                if not isinstance(value, str):
                    raise KumirEvalError("Попытка вызвать не процедуру")
                proc_name = value
                
                # Проверяем, является ли это встроенной процедурой
                if proc_name in self.BUILTIN_FUNCTIONS:
                    # Получаем аргументы
                    args = self.visit(child) if child.getChildCount() > 0 else []
                    arg_count = len(args)
                    
                    # Проверяем, есть ли версия процедуры с таким количеством аргументов
                    if arg_count not in self.BUILTIN_FUNCTIONS[proc_name]:
                        raise KumirEvalError(f"Неверное количество аргументов для встроенной процедуры '{proc_name}': ожидалось одно из {list(self.BUILTIN_FUNCTIONS[proc_name].keys())}, получено {arg_count}")
                    
                    # Вызываем встроенную процедуру
                    return self.BUILTIN_FUNCTIONS[proc_name][arg_count](*args)
                
                # Если это не встроенная процедура, проверяем пользовательские процедуры
                if proc_name not in self.procedures:
                    raise KumirEvalError(f"Процедура '{proc_name}' не определена")
                
                # Получаем аргументы
                args = self.visit(child) if child.getChildCount() > 0 else []
                
                # Создаем новую область видимости для процедуры
                self.enter_scope()
                try:
                    # Привязываем аргументы к параметрам
                    proc_def = self.procedures[proc_name]
                    if len(args) != len(proc_def['params']):
                        raise KumirEvalError(f"Неверное количество аргументов для процедуры '{proc_name}': ожидалось {len(proc_def['params'])}, получено {len(args)}")
                    
                    for param, arg in zip(proc_def['params'], args):
                        self.declare_variable(param['name'], param['type'])
                        self.update_variable(param['name'], arg)
                    
                    # Выполняем тело процедуры
                    self.visit(proc_def['body'])
                    
                    # Получаем возвращаемое значение, если есть
                    if 'return_value' in self.current_scope:
                        value = self.current_scope['return_value']
                    else:
                        value = None
                finally:
                    self.exit_scope()

        return value

    def visitExpressionList(self, ctx:KumirParser.ExpressionListContext):
        # expressionList: expression (COMMA expression)*
        if self.debug: print("[DEBUG][Visit] ExpressionList", file=sys.stderr)
        args = []
        if ctx: # Проверяем, что контекст не None
            for i, expr_ctx in enumerate(ctx.expression()):
                value = self.visit(expr_ctx)
                if self.debug: print(f"[DEBUG][ExprList] Аргумент #{i+1}: {value} (тип {type(value).__name__})", file=sys.stderr)
                args.append(value)
        if self.debug: print(f"[DEBUG][Visit] ExpressionList: результат = {args}", file=sys.stderr)
        return args # Возвращаем список вычисленных значений аргументов

    def visitPrimaryExpression(self, ctx:KumirParser.PrimaryExpressionContext):
        """Обрабатывает первичные выражения."""
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.qualifiedIdentifier():
            name = ctx.qualifiedIdentifier().getText()
            # Проверяем, является ли это переменной
            var_info, _ = self.find_variable(name)
            if var_info:
                return var_info
            # Если не переменная, возможно это имя процедуры
            return name
        elif ctx.RETURN_VALUE():
            if 'return_value' not in self.current_scope:
                raise KumirEvalError("Попытка использовать неинициализированное возвращаемое значение")
            return self.current_scope['return_value']
        elif ctx.LPAREN():
            return self.visit(ctx.expression())
        elif ctx.arrayLiteral():
            return self.visit(ctx.arrayLiteral())
        else:
            raise KumirEvalError("Некорректное первичное выражение")

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        # Получаем спецификатор цикла
        loop_spec = ctx.loopSpecifier()
        statement_sequence_ctx = ctx.statementSequence()
        max_iterations = 100000 # Защита от бесконечных циклов
        iteration_count = 0

        if not loop_spec:
            # Обработка циклов без явного спецификатора (нц...кц и нц...кц при)
            end_condition_ctx = ctx.endLoopCondition()

            if end_condition_ctx: # Цикл "до тех пор" (нц ... кц при условие)
                print(f"[DEBUG][Visit] Начало цикла ДО ТЕХ ПОР (КЦ ПРИ)", file=sys.stderr)
                condition_expr_ctx = end_condition_ctx.expression()
                while True:
                    iteration_count += 1
                    if iteration_count > max_iterations:
                         raise KumirExecutionError(f"Превышено максимальное число итераций цикла ДО ТЕХ ПОР ({iteration_count})")
                    
                    # Выполняем тело цикла
                    try:
                        self.visit(statement_sequence_ctx)
                    except LoopExitException:
                        print("[DEBUG][Visit] Выход из цикла ДО ТЕХ ПОР по команде ВЫХОД", file=sys.stderr)
                        break # Прерываем цикл по команде ВЫХОД
                    except Exception as loop_body_error:
                         line = statement_sequence_ctx.start.line
                         column = statement_sequence_ctx.start.column
                         raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ДО ТЕХ ПОР: {loop_body_error}")

                    # Вычисляем условие выхода
                    try:
                        condition_value = self.visit(condition_expr_ctx)
                    except Exception as e:
                        line = condition_expr_ctx.start.line
                        column = condition_expr_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка вычисления условия выхода цикла ДО ТЕХ ПОР: {e}")
                    
                    if not isinstance(condition_value, bool):
                        line = condition_expr_ctx.start.line
                        column = condition_expr_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Условие выхода цикла ДО ТЕХ ПОР ('{condition_value}') должно быть логического типа, а не {type(condition_value).__name__}.")

                    print(f"  -> Итерация {iteration_count}: Условие выхода = {condition_value}", file=sys.stderr)
                    if condition_value: # Если условие ВЫХОДА == да (True)
                        break # Выход из цикла

                print(f"[DEBUG][Visit] Конец цикла ДО ТЕХ ПОР. Итераций: {iteration_count}", file=sys.stderr)

            else: # Безусловный цикл (нц ... кц)
                print(f"[DEBUG][Visit] Начало безусловного цикла (НЦ-КЦ)", file=sys.stderr)
                while True:
                    iteration_count += 1
                    if iteration_count > max_iterations:
                         raise KumirExecutionError(f"Превышено максимальное число итераций безусловного цикла ({iteration_count})")
                    
                    print(f"  -> Итерация {iteration_count}", file=sys.stderr)
                    # Выполняем тело цикла
                    try:
                        self.visit(statement_sequence_ctx)
                    except LoopExitException:
                        print("[DEBUG][Visit] Выход из безусловного цикла по команде ВЫХОД", file=sys.stderr)
                        break # Прерываем цикл по команде ВЫХОД
                    except Exception as loop_body_error:
                         line = statement_sequence_ctx.start.line
                         column = statement_sequence_ctx.start.column
                         raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри безусловного цикла: {loop_body_error}")
                
                print(f"[DEBUG][Visit] Конец безусловного цикла. Итераций: {iteration_count}", file=sys.stderr)
            
        elif loop_spec.FOR():  # Цикл ДЛЯ
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

            # --- Начало изменений для области видимости ---
            self.enter_scope() # Входим в новую область видимости для цикла
            # Весь блок работы с циклом должен быть внутри одного try...finally
            # чтобы гарантировать выход из области видимости.
            iteration_count = 0 # Инициализируем счетчик здесь
            try:
                # Объявляем переменную цикла в локальной области видимости
                var_type = 'цел' 
                self.declare_variable(loop_var_name, var_type)
                self.update_variable(loop_var_name, start_val)
                var_info, _ = self.find_variable(loop_var_name)
                
                if var_info is None:
                    raise KumirExecutionError(f"Не удалось создать локальную переменную цикла '{loop_var_name}'")

                current_val = start_val
                max_iterations = 100000 # Защита от бесконечных циклов

                # Основной цикл
                if step_val > 0:
                    while current_val <= end_val:
                        iteration_count += 1
                        if iteration_count > max_iterations:
                            raise KumirExecutionError(f"Превышено максимальное число итераций цикла ДЛЯ ({iteration_count})")
                        
                        print(f"  -> Итерация {iteration_count}: {loop_var_name} = {current_val}", file=sys.stderr)
                        
                        # Выполняем тело цикла
                        try:
                            self.visit(statement_sequence_ctx)
                        except LoopExitException:
                            print("[DEBUG][Visit] Выход из цикла ДЛЯ по команде ВЫХОД", file=sys.stderr)
                            break # Прерываем цикл while
                        # Ошибки из тела цикла будут пойманы внешним try/except/finally
                        current_val += step_val
                elif step_val < 0:
                    while current_val >= end_val:
                        iteration_count += 1
                        if iteration_count > max_iterations:
                            raise KumirExecutionError(f"Превышено максимальное число итераций цикла ДЛЯ ({iteration_count})")
                        
                        print(f"  -> Итерация {iteration_count}: {loop_var_name} = {current_val}", file=sys.stderr)
                        
                        # Выполняем тело цикла
                        try:
                            self.visit(statement_sequence_ctx)
                        except LoopExitException:
                            print("[DEBUG][Visit] Выход из цикла ДЛЯ по команде ВЫХОД", file=sys.stderr)
                            break # Прерываем цикл while
                        # Ошибки из тела цикла будут пойманы внешним try/except/finally
                        current_val += step_val
            except Exception as e:
                raise e
            finally:
                self.exit_scope() # Гарантируем выход из области видимости
                print(f"[DEBUG][Visit] Конец цикла ДЛЯ. Итераций: {iteration_count}", file=sys.stderr)
            
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
                    self.visit(statement_sequence_ctx)
                except LoopExitException:
                    print("[DEBUG][Visit] Выход из цикла ПОКА по команде ВЫХОД", file=sys.stderr)
                    break # Прерываем цикл
                except Exception as loop_body_error:
                     line = statement_sequence_ctx.start.line
                     column = statement_sequence_ctx.start.column
                     raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ПОКА: {loop_body_error}")

            print(f"[DEBUG][Visit] Конец цикла ПОКА. Итераций: {iteration_count - 1}", file=sys.stderr) # -1 т.к. последняя проверка условия была лишней
            
        elif loop_spec.expression():  # Цикл РАЗ
            times_expr_ctx = loop_spec.expression(0) # Получаем контекст выражения N
            statement_sequence_ctx = ctx.statementSequence() # Получаем контекст тела цикла

            # Вычисляем количество повторений
            try:
                times_value = self.visit(times_expr_ctx)
            except Exception as e:
                line = times_expr_ctx.start.line
                column = times_expr_ctx.start.column
                raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка вычисления количества повторений цикла РАЗ: {e}")

            # Проверяем тип и значение
            if not isinstance(times_value, int):
                line = times_expr_ctx.start.line
                column = times_expr_ctx.start.column
                raise KumirEvalError(f"Строка {line}, столбец {column}: Количество повторений цикла РАЗ ('{times_value}') должно быть целым числом, а не {type(times_value).__name__}.")
            if times_value < 0:
                line = times_expr_ctx.start.line
                column = times_expr_ctx.start.column
                raise KumirEvalError(f"Строка {line}, столбец {column}: Количество повторений цикла РАЗ ('{times_value}') не может быть отрицательным.")

            max_iterations = 100000 # Защита от слишком больших чисел
            if times_value > max_iterations:
                 raise KumirExecutionError(f"Запрошено слишком большое число итераций цикла РАЗ ({times_value}), максимум {max_iterations}")

            print(f"[DEBUG][Visit] Начало цикла {times_value} РАЗ", file=sys.stderr)

            # Итерация цикла
            for i in range(times_value):
                iteration_num = i + 1
                print(f"  -> Итерация {iteration_num} из {times_value}", file=sys.stderr)
                # Выполняем тело цикла
                try:
                    self.visit(statement_sequence_ctx)
                except LoopExitException:
                    print("[DEBUG][Visit] Выход из цикла РАЗ по команде ВЫХОД", file=sys.stderr)
                    break # Прерываем цикл for
                except Exception as loop_body_error:
                     # TODO: По возможности, получить номер строки из loop_body_error
                     line = statement_sequence_ctx.start.line
                     column = statement_sequence_ctx.start.column
                     raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла РАЗ (итерация {iteration_num}): {loop_body_error}")

            print(f"[DEBUG][Visit] Конец цикла РАЗ. Итераций: {times_value}", file=sys.stderr)

        elif loop_spec.REPEAT(): # Цикл ДО (REPEAT ... UNTIL)
            condition_ctx = loop_spec.expression(0)
            print(f"[DEBUG][Visit] Начало цикла ДО", file=sys.stderr)
            
            iteration_count = 0
            max_iterations = 100000 # Защита

            while True:
                iteration_count += 1
                if iteration_count > max_iterations:
                    raise KumirExecutionError(f"Превышено максимальное число итераций цикла ДО ({iteration_count})")

                print(f"  -> Итерация {iteration_count}", file=sys.stderr)
                # Выполняем тело цикла ПЕРЕД проверкой условия
                try:
                    self.visit(statement_sequence_ctx)
                except LoopExitException:
                    print("[DEBUG][Visit] Выход из цикла ДО по команде ВЫХОД", file=sys.stderr)
                    break # Прерываем цикл
                except Exception as loop_body_error:
                     line = statement_sequence_ctx.start.line
                     column = statement_sequence_ctx.start.column
                     raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ДО: {loop_body_error}")

                # Вычисляем условие выхода
                try:
                    condition_value = self.visit(condition_ctx)
                except Exception as e:
                    line = condition_ctx.start.line
                    column = condition_ctx.start.column
                    raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка вычисления условия цикла ДО: {e}")
                
                # Проверяем тип условия
                if not isinstance(condition_value, bool):
                     line = condition_ctx.start.line
                     column = condition_ctx.start.column
                     raise KumirEvalError(f"Строка {line}, столбец {column}: Условие цикла ДО ('{condition_value}') должно быть логического типа, а не {type(condition_value).__name__}.")

                print(f"  -> Проверка условия выхода: {condition_value}", file=sys.stderr)
                if condition_value: # Если условие == да (True)
                    break # Выход из цикла

            print(f"[DEBUG][Visit] Конец цикла ДО. Итераций: {iteration_count}", file=sys.stderr)

        return None

    def visitIfStatement(self, ctx:KumirParser.IfStatementContext):
        """Обработка условного оператора."""
        print("[DEBUG][Visit] Обработка ifStatement", file=sys.stderr)
        
        # Вычисляем условие
        condition_ctx = ctx.expression()
        try:
            condition_value = self.visit(condition_ctx)
            condition_value = self._get_value(condition_value)
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
            value = input().rstrip()
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
        """Обработка операторов ввода/вывода."""
        print("[DEBUG][Visit] Обработка ioStatement", file=sys.stderr)
        
        # Определяем тип оператора
        is_input = ctx.INPUT() is not None
        
        # Получаем список аргументов
        args = ctx.ioArgumentList().ioArgument() if ctx.ioArgumentList() else []
        
        if is_input:
            # --- Обработка ВВОДА ---
            for arg_ctx in args:
                try:
                    # Получаем контекст выражения (переменной для ввода)
                    expressions = arg_ctx.expression()
                    if not expressions:
                        line = arg_ctx.start.line
                        column = arg_ctx.start.column
                        if arg_ctx.NEWLINE_CONST():
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Нельзя использовать 'нс' в операторе ввода")
                        else:
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Отсутствует переменная для ввода")
                    
                    # Берем первое выражение как переменную для ввода
                    expr_ctx = expressions[0]
                    var_name = self.get_variable_name(expr_ctx)
                    if not var_name:
                        raise KumirEvalError(f"Строка {expr_ctx.start.line}: Не удалось получить имя переменной для ввода")
                    
                    # Находим информацию о переменной
                    var_info, var_scope = self.find_variable(var_name)
                    if var_info is None:
                        raise KumirEvalError(f"Строка {expr_ctx.start.line}: Переменная '{var_name}' не найдена")
                    
                    # Читаем ввод и убираем пробельные символы справа
                    value_str = input().rstrip()
                    # Убираем возможный литерал \n в конце
                    if value_str.endswith('\\n'):
                        value_str = value_str[:-2]
                    
                    # Преобразуем значение в нужный тип
                    target_type = var_info['type']
                    try:
                        if target_type == INTEGER_TYPE:
                            value = int(value_str)
                        elif target_type == FLOAT_TYPE:
                            value = float(value_str)
                        elif target_type == BOOLEAN_TYPE:
                            value_str = value_str.lower()
                            if value_str == 'да':
                                value = True
                            elif value_str == 'нет':
                                value = False
                            else:
                                raise ValueError("Ожидается 'да' или 'нет'")
                        elif target_type == CHAR_TYPE:
                            if len(value_str) != 1:
                                raise ValueError("Ожидается один символ")
                            value = value_str
                        elif target_type == STRING_TYPE:
                            value = value_str
                        else:
                            raise KumirEvalError(f"Неподдерживаемый тип для ввода: {target_type}")
                    except ValueError as e:
                        raise KumirEvalError(f"Строка {expr_ctx.start.line}: Ошибка преобразования типа для '{var_name}': {e}")
                    
                    # Обновляем значение переменной
                    if var_scope is None:
                        raise KumirEvalError("Не найдена область видимости для переменной ввода")
                    var_scope[var_name]['value'] = value
                    
                except Exception as e:
                    if not isinstance(e, KumirEvalError):
                        line = arg_ctx.start.line
                        column = arg_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка при обработке ввода: {e}")
                    raise
        else:
            # --- Обработка ВЫВОДА ---
            for arg_ctx in args:
                try:
                    # Проверяем наличие форматирования
                    width = None
                    precision = None
                    if arg_ctx.INTEGER():
                        width = int(arg_ctx.INTEGER().getText())
                        if width <= 0:
                            raise KumirEvalError(f"Строка {arg_ctx.start.line}: Неверный формат ширины ({width}).")
                    if arg_ctx.REAL():
                        precision = float(arg_ctx.REAL().getText())
                        if precision <= 0:
                            raise KumirEvalError(f"Строка {arg_ctx.start.line}: Неверный формат точности ({precision}).")
                    
                    # Получаем значение для вывода
                    if arg_ctx.expression():
                        value = self.visit(arg_ctx.expression()[0])
                        # Форматируем значение
                        if isinstance(value, bool):
                            formatted_value = "да" if value else "нет"
                        elif isinstance(value, float) and precision is not None:
                            formatted_value = f"{value:.{int(precision)}f}"
                        else:
                            formatted_value = str(value)
                        
                        if width is not None:
                            formatted_value = formatted_value.rjust(width)
                    elif arg_ctx.STRING():
                        text_node = arg_ctx.STRING()
                        if not text_node:
                            line = arg_ctx.start.line
                            column = arg_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Отсутствует строковый литерал для вывода")
                        text = text_node.getText()
                        formatted_value = text[1:-1].replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                    elif arg_ctx.NEWLINE_CONST():
                        formatted_value = "\n"
                    else:
                        line = arg_ctx.start.line
                        column = arg_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Некорректный аргумент для вывода")
                    
                    # Выводим значение
                    print(formatted_value, end='')
                    self.had_output = True
                    
                except Exception as e:
                    if not isinstance(e, KumirEvalError):
                        line = arg_ctx.start.line
                        column = arg_ctx.start.column
                        raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка при обработке вывода: {e}")
                    raise
            
            # Добавляем перенос строки, если это не последний аргумент и не было явного нс
            if not any(arg_ctx.NEWLINE_CONST() for arg_ctx in args):
                print()
        
        return None

    def visitSwitchStatement(self, ctx:KumirParser.SwitchStatementContext):
        """Обработка оператора выбора."""
        print("[DEBUG][Visit] Обработка switchStatement", file=sys.stderr)
        
        # Получаем значение для выбора
        # !!! ГРАММАТИКА НЕ СОДЕРЖИТ expression В switchStatement!
        # !!! ЭТО НУЖНО ИСПРАВИТЬ В KumirParser.g4 И ПЕРЕГЕНЕРИРОВАТЬ ПАРСЕР.
        # switch_value = self.visit(ctx.expression()) # <-- ЭТА СТРОКА ВЫЗЫВАЕТ ОШИБКУ ЛИНТЕРА
        switch_value = None # Временное решение, чтобы не падало. Тесты на switch не пройдут.
        print(f"  -> Значение для выбора = {switch_value} (ВРЕМЕННОЕ ЗНАЧЕНИЕ!)", file=sys.stderr)
        
        # Проходим по всем вариантам
        for case_ctx in ctx.caseBlock():
            case_value = self.visit(case_ctx.expression())
            print(f"  -> Проверяем вариант: {case_value}", file=sys.stderr)
            
            if case_value == switch_value:
                print(f"  -> Выполняем вариант: {case_value}", file=sys.stderr)
                return self.visit(case_ctx.statementSequence())
        
        return None

    def visitLiteral(self, ctx:KumirParser.LiteralContext):
        """Обрабатывает литералы."""
        if ctx.INTEGER():
            return int(ctx.INTEGER().getText())
        elif ctx.REAL():
            return float(ctx.REAL().getText())
        elif ctx.STRING():
            text = ctx.STRING().getText()
            return text[1:-1].replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
        elif ctx.CHAR_LITERAL():
            text = ctx.CHAR_LITERAL().getText()
            return text[1:-1].replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
        elif ctx.TRUE():
            return True
        elif ctx.FALSE():
            return False
        elif ctx.colorLiteral():
            return self.visit(ctx.colorLiteral())
        elif ctx.NEWLINE_CONST():
            return '\n'
        else:
            raise KumirEvalError("Некорректный литерал")

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

    # Вспомогательная функция для форматирования
    def _format_output_value(self, value, ctx):
        """Форматирует значение для вывода."""
        value = self._get_value(value)
        if value is None:
            raise KumirEvalError("Попытка вывести неинициализированное значение")
            
        # Получаем параметры форматирования
        width = None
        precision = None
        
        # Проверяем наличие параметров форматирования в контексте
        if hasattr(ctx, 'ioArgument'):
            io_arg = ctx.ioArgument()
            if io_arg and hasattr(io_arg, 'INTEGER'):
                width = int(io_arg.INTEGER().getText())
            if io_arg and hasattr(io_arg, 'REAL'):
                precision = float(io_arg.REAL().getText())
            
        # Форматируем значение
        if isinstance(value, bool):
            formatted = "да" if value else "нет"
        elif isinstance(value, float) and precision is not None:
            formatted = f"{value:.{int(precision)}f}"
        else:
            formatted = str(value)
            
        # Применяем ширину
        if width is not None:
            formatted = formatted.rjust(width)
            
        return formatted

    # ... visitStatement теперь обрабатывает ВЫВОД ...
    def visitStatement(self, ctx:KumirParser.StatementContext):
        # ... (другие типы стейтментов) ... 
        if ctx.ioStatement():
            io_ctx = ctx.ioStatement()
            if io_ctx.INPUT():
                # Ввод обрабатывается в visitIoStatement
                return self.visit(io_ctx)
            else: 
                # --- Обработка ВЫВОДА здесь --- 
                print("[DEBUG][Visit] Обработка ВЫВОДА в visitStatement", file=sys.stderr)
                args = io_ctx.ioArgumentList().ioArgument() if io_ctx.ioArgumentList() else []
                
                for arg_ctx in args:
                    try:
                        # ВОЗВРАЩАЕМ обработку нс как добавление \n
                        if arg_ctx.NEWLINE_CONST():
                            sys.stdout.write('\n')
                            continue 

                        formatted_value = ""
                        expr_list = arg_ctx.expression()
                        if expr_list:
                            expr_ctx = expr_list[0] if isinstance(expr_list, list) else expr_list
                            if expr_ctx is None:
                                line = arg_ctx.start.line
                                column = arg_ctx.start.column
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Получено некорректное выражение для вывода (None)") # Исправлено
                            
                            value = self.visit(expr_ctx)
                            if value is None:
                                line = expr_ctx.start.line
                                column = expr_ctx.start.column
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вывести неинициализированное значение") # Исправлено
                            
                            formatted_value = self._format_output_value(value, arg_ctx)
                        
                        elif arg_ctx.STRING():
                            text_node = arg_ctx.STRING()
                            if not text_node:
                                line = arg_ctx.start.line
                                column = arg_ctx.start.column
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Отсутствует строковый литерал для вывода") # Исправлено
                            text = text_node.getText()
                            formatted_value = text[1:-1].replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                        else:
                            # Добавляем обработку случая, когда нет ни expression, ни STRING (хотя грамматика не должна этого допускать)
                            line = arg_ctx.start.line
                            column = arg_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Некорректный аргумент для вывода (ни выражение, ни строка)")
                        
                        sys.stdout.write(formatted_value)
                        
                    except Exception as e:
                        # ... (обработка ошибок) ...
                        if not isinstance(e, KumirEvalError):
                            line = arg_ctx.start.line if arg_ctx else io_ctx.start.line
                            column = arg_ctx.start.column if arg_ctx else io_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка при обработке вывода: {e}")
                        raise
                
                return None # Завершаем обработку стейтмента
        elif ctx.exitStatement(): # Обработка команды ВЫХОД
            return self.visit(ctx.exitStatement())
        
        # ... (обработка других стейтментов) ... 
        else:
             # Если это не известный нам тип statement, просто обходим детей
             # Это может быть точка с запятой или пустой стейтмент
             return self.visitChildren(ctx)

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext):
        """Обработка команды ВЫХОД."""
        print("[DEBUG][Visit] Команда ВЫХОД", file=sys.stderr)
        raise LoopExitException() # Бросаем исключение для прерывания цикла

    def visitColorLiteral(self, ctx:KumirParser.ColorLiteralContext):
        """Обрабатывает цветовые литералы."""
        if ctx.PROZRACHNIY():
            return "прозрачный"
        elif ctx.BELIY():
            return "белый"
        elif ctx.CHERNIY():
            return "черный"
        elif ctx.SERIY():
            return "серый"
        elif ctx.FIOLETOVIY():
            return "фиолетовый"
        elif ctx.SINIY():
            return "синий"
        elif ctx.GOLUBOY():
            return "голубой"
        elif ctx.ZELENIY():
            return "зеленый"
        elif ctx.ZHELTIY():
            return "желтый"
        elif ctx.ORANZHEVIY():
            return "оранжевый"
        elif ctx.KRASNIY():
            return "красный"
        else:
            raise KumirEvalError("Некорректный цветовой литерал")

    def visitArrayLiteral(self, ctx:KumirParser.ArrayLiteralContext):
        """Обрабатывает литералы массивов."""
        if not ctx.expressionList():
            return []
        return [self.visit(expr) for expr in ctx.expressionList().expression()]

    def visitIndexList(self, ctx:KumirParser.IndexListContext):
        """Обрабатывает индексы массивов."""
        if ctx.COLON():
            # Диапазон индексов
            start = self.visit(ctx.expression(0))
            end = self.visit(ctx.expression(1))
            if not isinstance(start, int) or not isinstance(end, int):
                raise KumirEvalError("Границы диапазона должны быть целыми числами")
            return slice(start, end)
        else:
            # Одиночный индекс
            return self.visit(ctx.expression(0))

    def visitArgumentList(self, ctx:KumirParser.ArgumentListContext):
        """Обрабатывает списки аргументов."""
        return [self.visit(expr) for expr in ctx.expression()]

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