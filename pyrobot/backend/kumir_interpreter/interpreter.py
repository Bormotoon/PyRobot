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
        'printbin': { # Ключ теперь в нижнем регистре
            1: lambda n: print(format(n, '08b'), end='') # Аргумент n - это само значение
        }
    }

    def __init__(self):
        super().__init__()
        self.variables = {}  # Глобальные переменные
        self.scopes = [{}]  # Стек областей видимости, начинаем с глобальной
        self.debug = False  # Флаг для отладочного вывода (ОТКЛЮЧЕН)
        self.procedures = {}  # Словарь для хранения определений процедур/функций

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

    def _get_type_name_from_specifier(self, type_ctx: KumirParser.TypeSpecifierContext) -> str:
        """Извлекает строковое имя типа из узла typeSpecifier."""
        if type_ctx.basicType():
            type_token = type_ctx.basicType().start
            kumir_type = TYPE_MAP.get(type_token.type)
            if kumir_type:
                # Проверяем суффикс таблицы
                is_table = bool(type_ctx.TABLE_SUFFIX())
                # Пока возвращаем базовый тип, таблицы обрабатываются отдельно
                return kumir_type
            else:
                raise DeclarationError(f"Неизвестный базовый тип: {type_token.text}")
        elif type_ctx.arrayType():
            # TODO: Обработка имен типов массивов
            raise NotImplementedError("Типы массивов пока не поддерживаются в параметрах")
        elif type_ctx.actorType():
            # TODO: Обработка имен типов исполнителей
            raise NotImplementedError("Типы исполнителей пока не поддерживаются в параметрах")
        else:
            raise DeclarationError("Неизвестный typeSpecifier")

    def _get_param_mode(self, param_decl_ctx: KumirParser.ParameterDeclarationContext) -> str:
        """Определяет режим параметра (арг, рез, арг рез)."""
        if param_decl_ctx.IN_PARAM():
            return 'арг'
        elif param_decl_ctx.OUT_PARAM():
            return 'рез'
        elif param_decl_ctx.INOUT_PARAM():
            return 'арг рез'
        else:
            return 'арг' # По умолчанию 'арг'

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
        # print(f"[DEBUG][BinOp Eval] Op: {op_token.text}, Left: {repr(left_val)}, Right: {repr(right_val)}", file=sys.stderr) # DEBUG
        
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
            # Проверяем совместимость типов, кроме числовых
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
        # Сначала собираем все определения процедур/функций
        self.procedures = {} # Очищаем на всякий случай
        for item in ctx.children:
            if isinstance(item, (KumirParser.AlgorithmDefinitionContext, KumirParser.ModuleDefinitionContext)):
                 # Если это определение алгоритма или модуля (модули могут содержать алгоритмы)
                 self._collect_procedure_definitions(item)

        print(f"[DEBUG][VisitProgram] Собрано {len(self.procedures)} процедур/функций: {list(self.procedures.keys())}", file=sys.stderr)

        # Затем выполняем программу (посещаем всех детей)
        # Исполнение основного алгоритма произойдет при посещении его узла
        self.visitChildren(ctx)
        return None # Программа ничего не возвращает

    def _collect_procedure_definitions(self, ctx):
        """Рекурсивно собирает все определения алгоритмов (процедур/функций)."""
        if isinstance(ctx, KumirParser.AlgorithmDefinitionContext):
            header = ctx.algorithmHeader()
            if header:
                # Получаем имя процедуры/функции
                # Имя может состоять из нескольких токенов, используем getText()
                name_ctx = header.algorithmNameTokens()
                if name_ctx:
                    name = name_ctx.getText().strip() # Убираем лишние пробелы по краям
                    if not name:
                        line = header.start.line
                        raise DeclarationError(f"Строка {line}: Не удалось получить имя алгоритма.")

                    if name in self.procedures:
                        # TODO: Разрешить перегрузку или выдавать ошибку? Пока ошибка.
                        line = header.start.line
                        raise DeclarationError(f"Строка {line}: Алгоритм с именем '{name}' уже определен.")

                    print(f"[DEBUG][Collect] Найдено определение: '{name}'", file=sys.stderr)
                    # Сохраняем весь узел определения
                    self.procedures[name] = ctx
                else:
                    line = header.start.line
                    raise DeclarationError(f"Строка {line}: Отсутствует имя в заголовке алгоритма.")
        elif isinstance(ctx, KumirParser.ModuleDefinitionContext):
             # Рекурсивно обходим тело модуля
             body = ctx.moduleBody() if ctx.moduleBody() else ctx.implicitModuleBody()
             if body:
                 for item in body.children:
                      self._collect_procedure_definitions(item)
        # Добавим обработку programItem, если вдруг там могут быть определения
        elif hasattr(ctx, 'children') and ctx.children:
             for child in ctx.children:
                  if not isinstance(child, antlr4.tree.Tree.TerminalNode):
                      self._collect_procedure_definitions(child)

    def visitImplicitModuleBody(self, ctx: KumirParser.ImplicitModuleBodyContext):
        """Обработка неявного тела модуля (программы без явного объявления модуля)."""
        # Сбор процедур уже выполнен в visitProgram
        print("[DEBUG][Visit] Обработка implicitModuleBody", file=sys.stderr)
        # Просто выполняем содержимое
        for item in ctx.children:
             if isinstance(item, KumirParser.AlgorithmDefinitionContext):
                 # Выполняем только *основной* алгоритм
                 # Основным считаем тот, у которого нет параметров в заголовке
                 header = item.algorithmHeader()
                 if header and not header.parameterList():
                     print(f"[DEBUG][ImplicitBody] Запуск основного алгоритма: {header.algorithmNameTokens().getText().strip()}", file=sys.stderr)
                     self.visit(item) # Посещаем определение, что приведет к выполнению тела
                     break # Выполняем только первый найденный основной алгоритм
        return None

    def visitModuleDefinition(self, ctx: KumirParser.ModuleDefinitionContext):
        """Обработка определения модуля."""
        # Сбор процедур уже выполнен в visitProgram
        print("[DEBUG][Visit] Обработка moduleDefinition", file=sys.stderr)
        # Если это неявный модуль, делегируем visitImplicitModuleBody
        if ctx.implicitModuleBody():
            return self.visit(ctx.implicitModuleBody())
        else:
            # Для явных модулей пока ничего не делаем (только собираем процедуры)
            # В будущем здесь может быть выполнение инициализации модуля
            print("[DEBUG][ModuleDef] Явный модуль - выполнение пока не реализовано.", file=sys.stderr)
            return None

    def visitAlgorithmDefinition(self, ctx: KumirParser.AlgorithmDefinitionContext):
        """Обработка определения алгоритма (вызывается при обходе из visitImplicitModuleBody)."""
        # Этот метод теперь отвечает за *выполнение* алгоритма,
        # когда его вызывают для основного алгоритма.
        # Сбор определений уже произошел.
        name = ctx.algorithmHeader().algorithmNameTokens().getText().strip()
        print(f"[DEBUG][VisitAlgDef] Выполнение алгоритма '{name}'", file=sys.stderr)

        body = ctx.algorithmBody()
        if body:
             # Входим в область видимости для локальных переменных алгоритма
             # (хотя в КуМире нет явных локальных переменных на уровне АЛГ,
             # но это может понадобиться для функций и рекурсии)
             self.enter_scope()
             try:
                 # Обработка локальных объявлений (если они есть перед НАЧ)
                 # variableDeclaration уже обрабатывается в visitStatementSequence -> visitStatement
                 # pre/post conditions пока не обрабатываем

                 # Выполняем тело
                 self.visit(body)
             finally:
                 self.exit_scope()
        return None # Определение алгоритма само по себе ничего не возвращает

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

                # print(f"[DEBUG][MultOp Eval] Op: {op_token.text}, Left: {repr(result)}, Right: {repr(right_val)}", file=sys.stderr) # DEBUG
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
                # Обработка вызова процедуры/функции
                # 'value' здесь - это имя, полученное из primaryExpression
                if not isinstance(value, str):
                    # Если value не строка, значит primaryExpression вернуло не имя,
                    # а какое-то вычисленное значение (число, bool и т.д.), что некорректно для вызова.
                    line = ctx.primaryExpression().start.line
                    column = ctx.primaryExpression().start.column
                    raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вызова не процедуры/функции (получено значение типа {type(value).__name__})")
                
                proc_name = value
                args = self.visit(child) if child.getChildCount() > 0 else []
                print(f"[DEBUG][Postfix] Вызов процедуры/функции '{proc_name}' с аргументами: {args}", file=sys.stderr)
                
                # 1. Проверяем встроенные процедуры
                proc_name_lower = proc_name.lower() # Для встроенных используем нижний регистр
                if proc_name_lower in self.BUILTIN_FUNCTIONS:
                    arg_count = len(args)
                    builtin_variants = self.BUILTIN_FUNCTIONS[proc_name_lower]
                    
                    if arg_count not in builtin_variants:
                        raise KumirEvalError(f"Неверное количество аргументов для встроенной процедуры '{proc_name}': ожидалось одно из {list(builtin_variants.keys())}, получено {arg_count}")
                    
                    # Вызываем встроенную процедуру
                    try:
                        # Передаем аргументы как есть
                        result = builtin_variants[arg_count](*args)
                        print(f"[DEBUG][Postfix] Результат встроенной '{proc_name}': {result}", file=sys.stderr)
                        # Обновляем 'value' результатом вызова для цепочек вызовов
                        value = result 
                    except Exception as e:
                        line = child.start.line
                        column = child.start.column
                        raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка выполнения встроенной процедуры '{proc_name}': {e}")
                
                # 2. Если не встроенная, ищем пользовательскую процедуру
                elif proc_name in self.procedures:
                    proc_def_ctx = self.procedures[proc_name]
                    header = proc_def_ctx.algorithmHeader()
                    params_ctx = header.parameterList()
                    arg_list_ctx = child # Контекст списка аргументов вызова
                    
                    # --- Подготовка к обработке параметров рез/арг рез ---
                    output_params_mapping = [] # Список для {caller_var_name, proc_param_name}
                    # ----------------------------------------------------
                    
                    # Собираем информацию об ожидаемых параметрах (имя, тип, режим)
                    expected_params = []
                    if params_ctx:
                        param_index = 0 # Индекс для сопоставления с аргументами вызова
                        for param_decl_ctx in params_ctx.parameterDeclaration():
                            param_type_ctx = param_decl_ctx.typeSpecifier()
                            param_type_name = self._get_type_name_from_specifier(param_type_ctx)
                            mode = self._get_param_mode(param_decl_ctx)
                            
                            param_vars_list_ctx = param_decl_ctx.variableList()
                            if not param_vars_list_ctx:
                                raise KumirEvalError(f"Строка {param_decl_ctx.start.line}: Ошибка парсинга - отсутствует список переменных в объявлении параметра.")

                            for param_var_item_ctx in param_vars_list_ctx.variableDeclarationItem():
                                param_name = param_var_item_ctx.ID().getText()
                                expected_params.append({'name': param_name, 'type': param_type_name, 'mode': mode})
                                
                                # --- Сохраняем информацию для рез/арг рез ---
                                if mode in ['рез', 'арг рез']:
                                    if param_index < len(arg_list_ctx.expression()):
                                        arg_expr_ctx = arg_list_ctx.expression(param_index)
                                        try:
                                            primary_expr = arg_expr_ctx.logicalOrExpression() \
                                                           .logicalAndExpression(0).equalityExpression(0) \
                                                           .relationalExpression(0).additiveExpression(0) \
                                                           .multiplicativeExpression(0).powerExpression(0) \
                                                           .unaryExpression().postfixExpression() \
                                                           .primaryExpression()
                                            if primary_expr and primary_expr.qualifiedIdentifier():
                                                caller_var_name = primary_expr.qualifiedIdentifier().getText()
                                                caller_var_info, _ = self.find_variable(caller_var_name)
                                                if caller_var_info:
                                                    output_params_mapping.append({
                                                        'caller_var_name': caller_var_name,
                                                        'proc_param_name': param_name
                                                    })
                                                    print(f"[DEBUG][Param Map] Сопоставлен выходной параметр: '{caller_var_name}' -> '{param_name}'", file=sys.stderr)
                                                else:
                                                     raise KumirEvalError(f"Строка {arg_expr_ctx.start.line}: Переменная '{caller_var_name}', переданная как аргумент для параметра '{mode}', не найдена в вызывающей области.")
                                            else:
                                                raise KumirEvalError(f"Строка {arg_expr_ctx.start.line}: Аргумент для параметра '{mode}' ('{param_name}') должен быть переменной, а не выражением.")
                                        except AttributeError:
                                             raise KumirEvalError(f"Строка {arg_expr_ctx.start.line}: Не удалось распознать аргумент для параметра '{mode}' ('{param_name}') как переменную.")
                                    else:
                                        raise KumirEvalError("Несоответствие индекса параметра и аргумента.")
                                # -----------------------------------------
                                param_index += 1
                    
                    print(f"[DEBUG][ProcCall] Ожидаемые параметры для '{proc_name}': {expected_params}", file=sys.stderr)
                    print(f"[DEBUG][ProcCall] Сопоставление выходных параметров: {output_params_mapping}", file=sys.stderr)
                    
                    # Вычисляем аргументы вызова ОДИН РАЗ перед входом в процедуру
                    actual_args = self.visit(arg_list_ctx) if arg_list_ctx.getChildCount() > 0 else []
                    if len(actual_args) != len(expected_params):
                        raise KumirEvalError(f"Неверное количество аргументов для процедуры '{proc_name}': ожидалось {len(expected_params)}, получено {len(actual_args)}")
                    
                    # Создаем новую область видимости для процедуры
                    self.enter_scope()
                    return_value = None
                    try:
                        # Привязываем аргументы к параметрам в локальной области
                        for i, param_info in enumerate(expected_params):
                            arg_value = actual_args[i] 
                            param_name = param_info['name']
                            param_type = param_info['type']
                            param_mode = param_info['mode']

                            # Объявляем параметр в локальной области
                            self.declare_variable(param_name, param_type)
                            
                            # Инициализируем значение параметра в зависимости от режима
                            if param_mode in ['арг', 'арг рез']:
                                try:
                                    # Проверяем тип и присваиваем значение аргумента
                                    converted_arg_value = self._validate_and_convert_value_for_assignment(arg_value, param_type, param_name)
                                    self.update_variable(param_name, converted_arg_value) # Обновляем в локальной области
                                    print(f"[DEBUG][ProcCall Init] Инициализация параметра '{param_mode}' '{param_name}' значением {repr(converted_arg_value)}", file=sys.stderr)
                                except (AssignmentError, DeclarationError, KumirExecutionError) as e:
                                    line = arg_list_ctx.expression(i).start.line # Строка аргумента вызова
                                    raise KumirEvalError(f"Строка ~{line}: Ошибка типа при передаче аргумента №{i+1} в параметр '{param_name}': {e}")
                            elif param_mode == 'рез':
                                # Для 'рез' оставляем значение по умолчанию
                                print(f"[DEBUG][ProcCall Init] Параметр '{param_mode}' '{param_name}' инициализирован по умолчанию.", file=sys.stderr)

                        # Выполняем тело процедуры
                        print(f"[DEBUG][ProcCall] Выполнение тела процедуры '{proc_name}'", file=sys.stderr)
                        self.visit(proc_def_ctx.algorithmBody())

                        # --- Копируем результаты обратно в вызывающую область для рез/арг рез ---
                        print(f"[DEBUG][ProcCall Exit] Копирование результатов для '{proc_name}'", file=sys.stderr)
                        if len(self.scopes) < 2:
                             raise KumirExecutionError("Невозможно скопировать результаты: отсутствует вызывающая область видимости.")
                        caller_scope = self.scopes[-2] # Вызывающая область
                        local_scope = self.scopes[-1]  # Текущая (локальная) область
                        
                        for mapping in output_params_mapping:
                            caller_var_name = mapping['caller_var_name']
                            proc_param_name = mapping['proc_param_name']
                            
                            if proc_param_name not in local_scope:
                                raise KumirExecutionError(f"Внутренняя ошибка: параметр '{proc_param_name}' не найден в локальной области при выходе из '{proc_name}'.")
                            if caller_var_name not in caller_scope:
                                # Эта проверка уже была при создании mapping, но на всякий случай
                                raise KumirExecutionError(f"Внутренняя ошибка: переменная '{caller_var_name}' не найдена в вызывающей области при выходе из '{proc_name}'.")
                                
                            final_param_value = local_scope[proc_param_name]['value']
                            caller_var_info = caller_scope[caller_var_name]
                            target_type = caller_var_info['type']
                            
                            print(f"[DEBUG][ProcCall Exit] Копируем '{proc_param_name}' ({repr(final_param_value)}) -> '{caller_var_name}' ({target_type})", file=sys.stderr)
                            
                            # Обновляем переменную в вызывающей области
                            try:
                                # Используем _validate_and_convert для проверки типа перед записью в вызывающую область
                                converted_value = self._validate_and_convert_value_for_assignment(final_param_value, target_type, caller_var_name)
                                # Обновляем значение напрямую в словаре вызывающей области
                                caller_var_info['value'] = converted_value
                            except (AssignmentError, DeclarationError, KumirExecutionError) as e:
                                line = proc_def_ctx.algorithmHeader().start.line
                                raise KumirExecutionError(f"Строка ~{line}: Ошибка при возврате значения из параметра '{proc_param_name}' в переменную '{caller_var_name}': {e}")
                        # -----------------------------------------------------------------

                        # TODO: Обработка возвращаемых значений (`знач`) для функций
                        value = None # Для процедур возвращаем None

                    finally:
                        self.exit_scope() # Выходим из области видимости процедуры
                
                # 3. Если не найдена ни встроенная, ни пользовательская
                else:
                    line = ctx.primaryExpression().start.line
                    column = ctx.primaryExpression().start.column
                    raise KumirEvalError(f"Строка {line}, столбец {column}: Процедура или функция '{proc_name}' не определена")

            # Добавляем обработку других постфиксных операций, если они появятся
            # else:
            #    raise KumirEvalError("Неизвестная постфиксная операция")

        # Возвращаем последнее вычисленное значение (результат последнего вызова или primaryExpression)
        return value

    def visitExpressionList(self, ctx:KumirParser.ExpressionListContext):
        # expressionList: expression (COMMA expression)*
        if self.debug: print("[DEBUG][Visit] ExpressionList", file=sys.stderr)
        args = []
        if ctx:
            # Итерируем по дочерним узлам, чтобы выбрать только expression верхнего уровня
            for child in ctx.getChildren():
                # Проверяем, является ли дочерний узел expression
                # Использование getRuleIndex предпочтительнее isinstance для устойчивости к изменениям грамматики
                if hasattr(child, 'getRuleIndex') and child.getRuleIndex() == KumirParser.RULE_expression:
                    value = self.visit(child)
                    if self.debug: print(f"[DEBUG][ExprList] Аргумент: {value} (тип {type(value).__name__})", file=sys.stderr)
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
                # --- ИСПРАВЛЕНИЕ: Возвращаем значение, а не словарь ---
                if var_info['is_table']:
                    # Если это таблица, но обращаемся без индекса, возвращаем весь словарь значений
                    # (Для присваивания или передачи как аргумент)
                    # TODO: Уточнить поведение КуМир при передаче таблиц
                    print(f"[DEBUG][Primary] Возвращаем всю таблицу '{name}'", file=sys.stderr)
                    return var_info['value'] # Возвращаем словарь {индекс: значение}
                else:
                    # Для скалярной переменной возвращаем само значение
                    print(f"[DEBUG][Primary] Возвращаем значение переменной '{name}': {var_info['value']}", file=sys.stderr)
                    return var_info['value']
            # Если не переменная, возможно это имя процедуры/функции
            # В этом случае visitPostfixExpression должен обработать вызов
            # Возвращаем имя как строку, чтобы PostfixExpression знал, что вызывать
            print(f"[DEBUG][Primary] Возвращаем имя процедуры/функции '{name}'", file=sys.stderr)
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
        """Обработка цикла"""
        # Проверяем альтернативу REPEAT...UNTIL сначала
        if ctx.REPEAT(): # Цикл ДО
            while True:
                try:
                    self.visit(ctx.statementSequence())
                except LoopExitException:
                    break
                except Exception as e:
                    line = ctx.start.line
                    column = ctx.start.column
                    raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ДО: {str(e)}")
                
                # Проверяем условие выхода ПОСЛЕ выполнения тела
                condition = self.visit(ctx.expression())
                if isinstance(condition, dict):
                    condition = condition['value']
                if not isinstance(condition, bool):
                    raise KumirEvalError("Условие выхода из цикла ДО должно быть логическим")
                if condition:
                    break # Выходим, если условие истинно
            return None

        # Иначе, это цикл НЦ (loopSpec)
        loop_spec = ctx.loopSpec()
        if not loop_spec:
             # Это может быть устаревший LoopNaka или другая ошибка грамматики
             raise KumirExecutionError(f"Строка {ctx.start.line}: Неожиданная структура цикла. Ожидался loopSpec.")

        if loop_spec.TIMES():  # Цикл РАЗ
            count_expr = loop_spec.expression()
            if not count_expr:
                 raise KumirEvalError(f"Строка {loop_spec.start.line}: Отсутствует выражение для количества повторений цикла РАЗ")
            count = self.visit(count_expr)
            # if isinstance(count, dict):
            #     count = count['value'] # _get_value сделает это
            count_value = self._get_value(count)
            if not isinstance(count_value, int):
                raise KumirEvalError(f"Строка {loop_spec.start.line}: Количество повторений цикла РАЗ должно быть целым числом, получено {type(count_value).__name__}")
            if count_value < 0:
                # Поведение КуМир для отрицательного числа раз? Вероятно, 0 итераций.
                count_value = 0
                
            for i in range(count_value):
                try:
                    self.visit(ctx.statementSequence())
                except LoopExitException:
                    break
                except Exception as e:
                    line = ctx.start.line
                    column = ctx.start.column
                    raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла РАЗ (итерация {i+1}): {str(e)}")

        elif loop_spec.WHILE():  # Цикл ПОКА
            while True:
                condition_expr = loop_spec.expression()
                if not condition_expr:
                     raise KumirEvalError(f"Строка {loop_spec.start.line}: Отсутствует выражение условия для цикла ПОКА")
                condition = self.visit(condition_expr)
                condition_value = self._get_value(condition)
                if not isinstance(condition_value, bool):
                    raise KumirEvalError(f"Строка {loop_spec.start.line}: Условие цикла ПОКА должно быть логическим, получено {type(condition_value).__name__}")
                if not condition_value:
                    break
                try:
                    self.visit(ctx.statementSequence())
                except LoopExitException:
                    break
                except Exception as e:
                    line = ctx.start.line
                    column = ctx.start.column
                    raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ПОКА: {str(e)}")

        elif loop_spec.FOR():  # Цикл ДЛЯ
            var_name = loop_spec.ID().getText()
            if not var_name:
                 raise KumirEvalError(f"Строка {loop_spec.start.line}: Отсутствует имя переменной для цикла ДЛЯ")
            
            expr_list = loop_spec.expression()
            if len(expr_list) != 2:
                 raise KumirEvalError(f"Строка {loop_spec.start.line}: Ожидалось 2 выражения (начало, конец) для цикла ДЛЯ, получено {len(expr_list)}")
            start_expr = expr_list[0]
            end_expr = expr_list[1]

            start = self.visit(start_expr)
            end = self.visit(end_expr)
            start_value = self._get_value(start)
            end_value = self._get_value(end)
            
            if not isinstance(start_value, int):
                raise KumirEvalError(f"Строка {start_expr.start.line}: Начальное значение цикла ДЛЯ должно быть целым, получено {type(start_value).__name__}")
            if not isinstance(end_value, int):
                raise KumirEvalError(f"Строка {end_expr.start.line}: Конечное значение цикла ДЛЯ должно быть целым, получено {type(end_value).__name__}")
            
            # Создаем новую область видимости для переменной цикла
            self.enter_scope()
            try:
                # Объявляем переменную цикла в новой области
                self.declare_variable(var_name, 'цел') 
                step = 1
            finally:
                # Гарантируем выход из области видимости даже при ошибке
                self.exit_scope()
                direction_token = loop_spec.getChild(6) # TO или DOWNTO
                if direction_token.symbol.type == KumirLexer.DOWNTO:
                    step = -1
                    # Убрали проверку start < end, КуМир может выполнять 0 итераций
                    # if start_value < end_value:
                    #     print(f"[WARNING] Начальное значение ({start_value}) меньше конечного ({end_value}) для цикла ДЛЯ ... ДО. Цикл не будет выполнен.", file=sys.stderr)
                # else: # TO
                    # Убрали проверку start > end
                    # if start_value > end_value:
                    #     print(f"[WARNING] Начальное значение ({start_value}) больше конечного ({end_value}) для цикла ДЛЯ ... ДО. Цикл не будет выполнен.", file=sys.stderr)
                
                current = start_value
                while (step > 0 and current <= end_value) or (step < 0 and current >= end_value):
                    self.update_variable(var_name, current)
                    try:
                        self.visit(ctx.statementSequence())
                    except LoopExitException:
                        break
                    except Exception as e:
                        line = ctx.start.line # Ошибка в теле цикла
                        column = ctx.start.column
                        raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ДЛЯ (значение {var_name}={current}): {str(e)}")
                    current += step
        return value

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

    def visitStatement(self, ctx:KumirParser.StatementContext):
        if ctx.ioStatement():
            io_ctx = ctx.ioStatement()
            if io_ctx.INPUT():
                # --- Обработка ВВОДА здесь --- 
                # print("[DEBUG][Visit] Обработка ВВОДА в visitStatement", file=sys.stderr)
                args = io_ctx.ioArgumentList().ioArgument() if io_ctx.ioArgumentList() else []
                # --- ИЗМЕНЕНИЕ: Добавляем enumerate для получения индекса i ---
                for i, arg_ctx in enumerate(args):
                # ------------------------------------------------------------
                    try:
                        expressions = arg_ctx.expression()
                        if not expressions:
                            line = arg_ctx.start.line
                            column = arg_ctx.start.column
                            if arg_ctx.NEWLINE_CONST():
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Нельзя использовать 'нс' в операторе ввода")
                            else:
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Отсутствует переменная для ввода")

                        expr_ctx = expressions[0]
                        # Получаем имя переменной, но не вычисляем ее значение здесь
                        if not hasattr(expr_ctx, 'getText'): # Простая проверка, что это идентификатор
                             line = expr_ctx.start.line
                             column = expr_ctx.start.column
                             raise KumirEvalError(f"Строка {line}, столбец {column}: Ожидалось имя переменной для ввода, получено: {type(expr_ctx)}")
                        var_name = expr_ctx.getText()
                        if not var_name:
                            raise KumirEvalError(f"Строка {expr_ctx.start.line}: Не удалось получить имя переменной для ввода")

                        var_info, var_scope = self.find_variable(var_name)
                        if var_info is None:
                            raise KumirEvalError(f"Строка {expr_ctx.start.line}: Переменная '{var_name}' не найдена")

                        if var_info['is_table']:
                             # TODO: Обработка ввода в таблицу
                             raise NotImplementedError(f"Ввод в таблицу '{var_name}' пока не реализован.")

                        # Читаем ввод
                        try:
                            value_str = sys.stdin.readline().rstrip('\r\n')
                        except EOFError:
                             raise KumirInputRequiredError("Неожиданный конец ввода.")
                        # Отладка убрана

                        # --- Эхо ввода (пробел только МЕЖДУ значениями) --- 
                        sys.stdout.write(value_str)
                        if i < len(args) - 1: # Если это не последний аргумент
                            sys.stdout.write(' ')
                        # -------------------------------------------------

                        target_type = var_info['type']
                        try:
                            if target_type == INTEGER_TYPE:
                                value = int(value_str)
                            elif target_type == FLOAT_TYPE:
                                # Заменяем запятую на точку перед преобразованием
                                value = float(value_str.replace(',', '.'))
                            elif target_type == BOOLEAN_TYPE:
                                value_str_lower = value_str.lower()
                                if value_str_lower == 'да':
                                    value = True
                                elif value_str_lower == 'нет':
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
                            raise KumirEvalError(f"Строка {expr_ctx.start.line}: Ошибка преобразования типа для '{var_name}' при вводе значения '{value_str}': {e}")

                        # Обновляем значение переменной
                        self.update_variable(var_name, value)

                    except Exception as e:
                        if not isinstance(e, (KumirEvalError, KumirInputRequiredError)):
                            line = arg_ctx.start.line
                            column = arg_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Неожиданная ошибка при обработке ввода: {e}")
                        raise
                # Добавляем перенос строки после ввода
                sys.stdout.write('\n')
                return None # Завершили обработку ввода
            else: 
                # --- Обработка ВЫВОДА здесь --- 
                print("[DEBUG][Visit] Обработка ВЫВОДА в visitStatement", file=sys.stderr)
                args = io_ctx.ioArgumentList().ioArgument() if io_ctx.ioArgumentList() else []
                
                for i, arg_ctx in enumerate(args):
                    try:
                        if arg_ctx.NEWLINE_CONST():
                            sys.stdout.write('\n')
                            continue 

                        formatted_value = ""
                        expr_list = arg_ctx.expression() # Получаем узел(ы) expression из аргумента

                        if expr_list: # ЕСЛИ аргумент - это expression
                            # Получаем первый (и обычно единственный) узел expression
                            expr_ctx = expr_list[0] if isinstance(expr_list, list) else expr_list 
                            if expr_ctx is None:
                                line = arg_ctx.start.line
                                column = arg_ctx.start.column
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Получено некорректное выражение для вывода (None)")

                            # --- НОВАЯ ПРОВЕРКА: Является ли expression простым строковым литералом? ---
                            is_simple_string_literal = False
                            literal_value = None
                            try:
                                # Пробуем добраться до STRING через стандартную цепочку primaryExpression
                                primary = (expr_ctx.logicalOrExpression()
                                           .logicalAndExpression(0).equalityExpression(0)
                                           .relationalExpression(0).additiveExpression(0)
                                           .multiplicativeExpression(0).powerExpression(0)
                                           .unaryExpression().postfixExpression()
                                           .primaryExpression())
                                if primary and primary.literal() and primary.literal().STRING():
                                    is_simple_string_literal = True
                                    raw_text = primary.literal().STRING().getText()
                                    # Убираем кавычки и экранирование
                                    if len(raw_text) >= 2 and raw_text.startswith(('"', "'")) and raw_text.endswith(('"', "'")):
                                        # Сначала убираем кавычки, потом обрабатываем экранирование
                                        inner_text = raw_text[1:-1]
                                        # Простая замена для основных случаев, может потребовать доработки для сложных
                                        literal_value = inner_text.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                                    else:
                                        literal_value = raw_text # На всякий случай
                            except AttributeError:
                                # Цепочка нарушена, значит это не простой литерал
                                is_simple_string_literal = False

                            if is_simple_string_literal:
                                # Если это простой строковый литерал, используем его значение напрямую
                                print(f"[DEBUG][ВЫВОД] Expression распознан как строковый литерал: '{literal_value}'", file=sys.stderr)
                                formatted_value = literal_value
                            else:
                                # Иначе, вычисляем выражение как обычно
                                print(f"[DEBUG][ВЫВОД] Вычисление выражения: {expr_ctx.getText()}", file=sys.stderr)
                                # !!! ВЫЧИСЛЯЕМ ЗНАЧЕНИЕ ВЫРАЖЕНИЯ !!!
                                value = self.visit(expr_ctx)
                                # Извлекаем значение, если это переменная (т.е. visit вернул словарь)
                                value = self._get_value(value)

                                # !!! ПРОВЕРЯЕМ НА NONE ПОСЛЕ ВЫЧИСЛЕНИЯ !!!
                                if value is None:
                                    # Вот здесь возникает ошибка для неиниц. переменных
                                    expr_text = expr_ctx.getText() if hasattr(expr_ctx, 'getText') else '[Unknown Expression]'
                                    line = expr_ctx.start.line
                                    column = expr_ctx.start.column
                                    raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вывести неинициализированное значение (выражение: {expr_text})")

                                # Форматируем значение (кажется, _format_output_value не реализован?)
                                # TODO: Реализовать или проверить _format_output_value
                                formatted_value = self._format_output_value(value, arg_ctx)

                        elif arg_ctx.STRING(): # ИНАЧЕ ЕСЛИ аргумент - это строковый литерал НАПРЯМУЮ
                            print(f"[DEBUG][ВЫВОД] Аргумент распознан как прямой строковый литерал", file=sys.stderr)
                            text_node = arg_ctx.STRING()
                            if not text_node:
                                line = arg_ctx.start.line
                                column = arg_ctx.start.column
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Отсутствует строковый литерал для вывода")
                            text = text_node.getText()
                            # Извлекаем и очищаем строку
                            value = text[1:-1].replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                            # Строки не требуют форматирования :Ш:Т, используем как есть
                            formatted_value = value
                        else:
                            line = arg_ctx.start.line
                            column = arg_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Некорректный аргумент для вывода (ни выражение, ни строка)")
                        
                        # Печатаем отформатированный аргумент немедленно
                        sys.stdout.write(formatted_value)
                        
                    except Exception as e:
                        if not isinstance(e, KumirEvalError):
                            line = arg_ctx.start.line if arg_ctx else io_ctx.start.line
                            column = arg_ctx.start.column if arg_ctx else io_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка при обработке вывода: {e}")
                        raise
                
                # Добавляем перенос строки в конце вывода, 
                # ТОЛЬКО если это был не единственный строковый литерал-приглашение
                # ИЛИ если последний элемент вывода не был 'нс'.
                is_prompt_only = len(args) == 1 and is_simple_string_literal
                ends_with_newline_const = args and args[-1].NEWLINE_CONST()
                
                if not ends_with_newline_const and not is_prompt_only:
                    sys.stdout.write('\n')
                # -----------------------------------------------------
                
                return None # Завершаем обработку стейтмента
        elif ctx.exitStatement(): # Обработка команды ВЫХОД
            return self.visit(ctx.exitStatement())
        # ... (другие стейтменты) ...
        elif ctx.assignmentStatement():
            return self.visit(ctx.assignmentStatement())
        elif ctx.variableDeclaration():
            return self.visit(ctx.variableDeclaration())
        elif ctx.loopStatement():
            return self.visit(ctx.loopStatement())
        elif ctx.ifStatement():
            return self.visit(ctx.ifStatement())
        elif ctx.switchStatement():
            return self.visit(ctx.switchStatement())
        # Добавляем обработку вызова процедуры как statement
        elif ctx.expression(): # Если statement - это просто expression (например, вызов процедуры)
            self.visit(ctx.expression()) # Выполняем, игнорируем результат
            return None
        elif ctx.emptyStatement():
            return None # Ничего не делаем для пустого стейтмента
        elif ctx.compoundStatement(): # Обработка нач ... кц блоков
            return self.visit(ctx.compoundStatement().statementSequence())
        else:
             # Если это не известный нам тип statement, просто обходим детей
             # Это может быть точка с запятой или что-то еще
             print(f"[DEBUG][Visit Statement] Неизвестный тип statement: {ctx.toStringTree(recog=parser)}", file=sys.stderr)
             return self.visitChildren(ctx)

    # --- ИСПРАВЛЕНИЕ: Добавляем явный visitArgumentList ---
    def visitArgumentList(self, ctx: KumirParser.ArgumentListContext):
        # argumentList: expression (COMMA expression)*
        if self.debug: print("[DEBUG][Visit] ArgumentList", file=sys.stderr)
        args = []
        if ctx:
            # Итерируем по дочерним узлам, чтобы выбрать только expression верхнего уровня
            for child in ctx.getChildren():
                # Проверяем, является ли дочерний узел expression
                if hasattr(child, 'getRuleIndex') and child.getRuleIndex() == KumirParser.RULE_expression:
                    value = self.visit(child)
                    if self.debug: print(f"[DEBUG][ArgList] Аргумент: {value} (тип {type(value).__name__})")
                    args.append(value)

        if self.debug: print(f"[DEBUG][Visit] ArgumentList: результат = {args}", file=sys.stderr)
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
                # --- ИСПРАВЛЕНИЕ: Возвращаем значение, а не словарь ---
                if var_info['is_table']:
                    # Если это таблица, но обращаемся без индекса, возвращаем весь словарь значений
                    # (Для присваивания или передачи как аргумент)
                    # TODO: Уточнить поведение КуМир при передаче таблиц
                    print(f"[DEBUG][Primary] Возвращаем всю таблицу '{name}'", file=sys.stderr)
                    return var_info['value'] # Возвращаем словарь {индекс: значение}
                else:
                    # Для скалярной переменной возвращаем само значение
                    print(f"[DEBUG][Primary] Возвращаем значение переменной '{name}': {var_info['value']}", file=sys.stderr)
                    return var_info['value']
            # Если не переменная, возможно это имя процедуры/функции
            # В этом случае visitPostfixExpression должен обработать вызов
            # Возвращаем имя как строку, чтобы PostfixExpression знал, что вызывать
            print(f"[DEBUG][Primary] Возвращаем имя процедуры/функции '{name}'", file=sys.stderr)
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

    # --- НОВЫЙ МЕТОД: Форматирование вывода ---
    def _format_output_value(self, value, arg_ctx: KumirParser.IoArgumentContext) -> str:
        """Форматирует значение для вывода с учетом спецификаторов :Ш:Т."""
        width = None
        precision = None

        # Проверяем наличие спецификаторов формата
        if arg_ctx.COLON():
            format_specs = arg_ctx.INTEGER() # Может быть один или два
            if len(format_specs) == 1: # Только :Ш
                width = int(format_specs[0].getText())
                if self.debug: print(f"[DEBUG][Format] Ширина: {width}", file=sys.stderr)
            elif len(format_specs) >= 2: # :Ш:Т
                width = int(format_specs[0].getText())
                precision = int(format_specs[1].getText())
                if self.debug: print(f"[DEBUG][Format] Ширина: {width}, Точность: {precision}", file=sys.stderr)

        # Применяем форматирование
        if isinstance(value, (int, float)):
            if precision is not None: # Формат :Ш:Т (или только :Т, если Ш нет)
                if not isinstance(value, float): # Если целое, делаем вещ
                    value = float(value)
                format_string = f"{{:{width}.{precision}f}}" if width is not None else f"{{:.{precision}f}}"
                formatted = format_string.format(value)
                # Если ширина задана, Python уже добивает пробелами слева
                return formatted
            elif width is not None: # Только формат :Ш
                # Для целых и вещ добиваем пробелами слева до нужной ширины
                format_string = f"{{:{width}}}"
                # Конвертируем в строку перед форматированием ширины
                return format_string.format(str(value))
            else: # Без форматирования
                return str(value)
        elif isinstance(value, bool):
            # КуМир выводит 'да'/'нет'
            return 'да' if value else 'нет'
        else:
            # Строки и другие типы выводим как есть
            return str(value)

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