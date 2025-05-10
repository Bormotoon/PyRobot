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
                               RobotError, KumirSyntaxError)
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
    KumirLexer.DIV: operator.truediv,    # Обычное деление -> вещ
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
    KumirLexer.AND: lambda a, b: a and b,
    KumirLexer.OR: lambda a, b: a or b,
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
        error_message = f"Строка {line}:{column} около '{offendingSymbol.text if offendingSymbol else 'EOF'}': {msg}"
        # --- ВЫБРАСЫВАЕМ ИСКЛЮЧЕНИЕ --- 
        print(f"[DEBUG][Parser Error] {error_message}", file=sys.stderr)
        raise KumirSyntaxError(error_message)

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
        },
        'div': {
            2: lambda a, b: int(a) // int(b) if b != 0 else (_ for _ in ()).throw(KumirEvalError("Целочисленное деление на ноль"))
        },
        'mod': {
            2: lambda a, b: int(a) % int(b) if b != 0 else (_ for _ in ()).throw(KumirEvalError("Остаток от деления на ноль"))
        }
    }

    def __init__(self):
        super().__init__()
        self.variables = {}  # Глобальные переменные
        self.scopes = [{}]  # Стек областей видимости, начинаем с глобальной
        self.debug = True  # Флаг для отладочного вывода (ВКЛЮЧЕН)
        self.procedures = {}  # Словарь для хранения определений процедур/функций
        self.logger = logging.getLogger(__name__) # <--- ДОБАВЛЕНО
        # --- DEBUG PRINT --- 
        print(f"[DEBUG][INIT] KumirInterpreterVisitor initialized. Available methods starting with '_handle': {[name for name in dir(self) if callable(getattr(self, name)) and name.startswith('_handle')]}", file=sys.stderr) #stdout -> stderr
        # --- END DEBUG PRINT ---

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
        print(f"[DEBUG][Declare] Объявлена {'таблица' if is_table else 'переменная'} '{name}' тип {kumir_type} в области {len(self.scopes) - 1}", file=sys.stderr) #stdout -> stderr

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
        if self.debug: print(f"[DEBUG][FindVar] Поиск переменной '{var_name}'", file=sys.stderr) #stdout -> stderr
        for i, scope in enumerate(reversed(self.scopes)):
            scope_level = len(self.scopes) - 1 - i
            if var_name in scope:
                if self.debug: print(f"[DEBUG][FindVar] Найдена '{var_name}' в области {scope_level}", file=sys.stderr) #stdout -> stderr
                return scope[var_name], scope
        if self.debug: print(f"[DEBUG][FindVar] Переменная '{var_name}' НЕ найдена", file=sys.stderr) #stdout -> stderr
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
        print(f"[DEBUG][Update] Обновлено значение переменной '{var_name}' = {value}", file=sys.stderr) #stdout -> stderr

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

    def _handle_type_promotion_for_comparison(self, left, right, ctx):
        # Если один из операндов None, это ошибка, которая должна была быть поймана раньше,
        # но на всякий случай проверим.
        if left is None or right is None:
            raise KumirEvalError(
                f"Строка ~{ctx.start.line}: Нельзя сравнивать с неинициализированным значением.",
                ctx.start.line,
                ctx.start.column
            )

        is_left_int = isinstance(left, int)
        is_left_float = isinstance(left, float)
        is_right_int = isinstance(right, int)
        is_right_float = isinstance(right, float)

        # Приведение int к float для сравнения
        if is_left_int and is_right_float:
            print(f"[DEBUG][TypePromo] Promoting left operand {left} (int) to float for comparison with {right} (float)", file=sys.stderr) #stdout -> stderr
            return float(left), right
        if is_left_float and is_right_int:
            print(f"[DEBUG][TypePromo] Promoting right operand {right} (int) to float for comparison with {left} (float)", file=sys.stderr) #stdout -> stderr
            return left, float(right)
        
        # Если типы уже совместимы (оба числа, или оба строки, или оба bool), или не числа, оставляем как есть.
        # Проверка на несоответствие типов, не являющихся числами, должна быть в вызывающем методе.
        return left, right

    def _check_numeric(self, value, operation_name):
        print(f"[DEBUG][_check_numeric] ENTERED. Op: {operation_name}. Value initial type: {type(value).__name__}.", file=sys.stderr)
        processed_value = self._get_value(value)
        print(f"[DEBUG][_check_numeric] Value after _get_value for op '{operation_name}': {repr(processed_value)} (type: {type(processed_value).__name__})", file=sys.stderr)
        if processed_value is None:
            print(f"[DEBUG][_check_numeric] Raising KumirEvalError: processed_value is None for op '{operation_name}'", file=sys.stderr)
            raise KumirEvalError(f"Попытка использовать неинициализированное значение в операции '{operation_name}'")
        if not isinstance(processed_value, (int, float)):
            print(f"[DEBUG][_check_numeric] Raising KumirEvalError: not int/float for op '{operation_name}'. Value: {repr(processed_value)}, Type: {type(processed_value).__name__}", file=sys.stderr)
            raise KumirEvalError(f"Операция '{operation_name}' не применима к нечисловому типу {type(processed_value).__name__}.")
        # print(f"[DEBUG][_check_numeric] Returning: {repr(processed_value)}", file=sys.stderr)
        return processed_value

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

    def _perform_binary_operation(self, left_val, right_val, op_token, expression_node_ctx):
        """Выполняет бинарную арифметическую операцию над уже вычисленными значениями."""
        op_text = op_token.text  # e.g. "+", "-"
        op_type = op_token.type  # e.g. KumirLexer.PLUS

        # <<< DETAILED DEBUG FOR OPERATOR >>>
        # Пока убрали KumirLexer.MOD, т.к. точное имя токена не подтверждено
        print(f"[DEBUG][PBO_OP_DETAILS] op_text='{op_text}', op_type_val={op_type}, KumirLexer.DIV={KumirLexer.DIV}", file=sys.stderr)

        # Для арифметических операций (сложение, вычитание, умножение, деление, степень)
        # ожидаем числовые операнды.
        # print(f"[DEBUG][_perform_binary_operation] Before _check_numeric for left: {repr(left_val)}, op: {op_text}", file=sys.stderr)
        checked_left_val = self._check_numeric(left_val, op_text)
        # print(f"[DEBUG][_perform_binary_operation] Before _check_numeric for right: {repr(right_val)}, op: {op_text}", file=sys.stderr)
        checked_right_val = self._check_numeric(right_val, op_text)
        # print(f"[DEBUG][_perform_binary_operation] After _check_numeric. Left: {repr(checked_left_val)}, Right: {repr(checked_right_val)}", file=sys.stderr)

        operation_func = ARITHMETIC_OPS.get(op_type)
        
        # <<< DETAILED DEBUG FOR OP_FUNC >>>
        print(f"[DEBUG][PBO_OP_DETAILS] op_text='{op_text}', op_type_val={op_type}, operation_func_found={bool(operation_func)}", file=sys.stderr)

        if not operation_func:
            # Эта ситуация не должна возникать, если op_token пришел из Additive/MultiplicativeExpression,
            # так как грамматика ограничивает операторы.
            # <<< DETAILED DEBUG FOR 'mod'/'div' NOT FOUND >>>
            if op_type == KumirLexer.MOD or op_type == KumirLexer.DIV:
                 print(f"[DEBUG][PBO_OP_DETAILS] Keyword '{op_text}' was not found in ARITHMETIC_OPS. Raising error as expected.", file=sys.stderr)
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Неизвестный или неподдерживаемый арифметический оператор: {op_text} в выражении '{expression_node_ctx.getText()}'")

        # Стандартное деление '/' в КуМире всегда дает ВЕЩ результат.
        if op_type == KumirLexer.DIV: # This is for '/' (DIV_OP), not the keyword 'div'
            if checked_right_val == 0:
                raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Деление на ноль в выражении '{expression_node_ctx.getText()}'")
            return float(checked_left_val) / float(checked_right_val)
        
        # Для остальных арифметических операций (+, -, *, ^)
        try:
            # print(f"[DEBUG][_perform_binary_operation] Executing: {checked_left_val} {op_text} {checked_right_val} using {operation_func}", file=sys.stderr)
            result = operation_func(checked_left_val, checked_right_val)
            # print(f"[DEBUG][_perform_binary_operation] Result: {repr(result)}", file=sys.stderr)
            return result
        except TypeError as e:
            # Эта ошибка может возникнуть, если _check_numeric пропустил несовместимый тип (маловероятно) 
            # или если сама операция Python не может быть выполнена (например, int ** large_float, что может быть не тем, что ожидает КуМир)
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Ошибка типа при выполнении операции '{op_text}' ({type(checked_left_val).__name__} {op_text} {type(checked_right_val).__name__}) в выражении '{expression_node_ctx.getText()}': {e}")
        except ZeroDivisionError: # Для оператора ** с отрицательным основанием и дробным показателем, или 0**отриц_число
             raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Ошибка деления на ноль или некорректная операция со степенью при вычислении '{op_text}' в выражении '{expression_node_ctx.getText()}'")
        except OverflowError:
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Переполнение при вычислении '{op_text}' в выражении '{expression_node_ctx.getText()}'")
        except Exception as e: # Другие возможные математические ошибки
            raise KumirEvalError(f"Строка ~{expression_node_ctx.start.line}: Ошибка при вычислении '{op_text}' в выражении '{expression_node_ctx.getText()}': {e}")

    # --- Переопределение методов visit ---

    def visitProgram(self, ctx: KumirParser.ProgramContext):
        """Обрабатывает всю программу."""
        # Сначала собираем все определения процедур/функций
        self.procedures = {} # Очищаем на всякий случай
        for item in ctx.children:
            if isinstance(item, (KumirParser.AlgorithmDefinitionContext, KumirParser.ModuleDefinitionContext)):
                 # Если это определение алгоритма или модуля (модули могут содержать алгоритмы)
                 self._collect_procedure_definitions(item)

        print(f"[DEBUG][VisitProgram] Собрано {len(self.procedures)} процедур/функций: {list(self.procedures.keys())}", file=sys.stderr) #stdout -> stderr

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

                    print(f"[DEBUG][Collect] Найдено определение: '{name}'", file=sys.stderr) #stdout -> stderr
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
        print("[DEBUG][Visit] Обработка implicitModuleBody", file=sys.stderr) #stdout -> stderr
        # Просто выполняем содержимое
        for item in ctx.children:
             if isinstance(item, KumirParser.AlgorithmDefinitionContext):
                 # Выполняем только *основной* алгоритм
                 # Основным считаем тот, у которого нет параметров в заголовке
                 header = item.algorithmHeader()
                 if header and not header.parameterList():
                     print(f"[DEBUG][ImplicitBody] Запуск основного алгоритма: {header.algorithmNameTokens().getText().strip()}", file=sys.stderr) #stdout -> stderr
                     self.visit(item) # Посещаем определение, что приведет к выполнению тела
                     break # Выполняем только первый найденный основной алгоритм
        return None

    def visitModuleDefinition(self, ctx: KumirParser.ModuleDefinitionContext):
        """Обработка определения модуля."""
        # Сбор процедур уже выполнен в visitProgram
        print("[DEBUG][Visit] Обработка moduleDefinition", file=sys.stderr) #stdout -> stderr
        # Если это неявный модуль, делегируем visitImplicitModuleBody
        if ctx.implicitModuleBody():
            return self.visit(ctx.implicitModuleBody())
        else:
            # Для явных модулей пока ничего не делаем (только собираем процедуры)
            # В будущем здесь может быть выполнение инициализации модуля
            print("[DEBUG][ModuleDef] Явный модуль - выполнение пока не реализовано.", file=sys.stderr) #stdout -> stderr
            return None

    def visitAlgorithmDefinition(self, ctx: KumirParser.AlgorithmDefinitionContext):
        """Обработка определения алгоритма (вызывается при обходе из visitImplicitModuleBody)."""
        # Этот метод теперь отвечает за *выполнение* алгоритма,
        # когда его вызывают для основного алгоритма.
        # Сбор определений уже произошел.
        name = ctx.algorithmHeader().algorithmNameTokens().getText().strip()
        print(f"[DEBUG][VisitAlgDef] Выполнение алгоритма '{name}'", file=sys.stderr) #stdout -> stderr

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
        print(f"[DEBUG][Visit] Обработка variableDeclaration", file=sys.stderr) #stdout -> stderr
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
                print(f"  -> Диапазоны для таблицы '{var_name}' пока не вычисляются.", file=sys.stderr) #stdout -> stderr
                
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
            print(f"[DEBUG][Visit] Обращение к специальной переменной 'знач'", file=sys.stderr) #stdout -> stderr
            raise NotImplementedError("Обращение к 'знач' пока не реализовано.")
            
        var_name = self.get_full_identifier(ctx.qualifiedIdentifier())
        print(f"[DEBUG][Visit] Обращение к переменной/таблице: '{var_name}'", file=sys.stderr) #stdout -> stderr
        
        var_info, _ = self.find_variable(var_name)
        if var_info is None:
            # Добавляем информацию о строке и столбце
            line = ctx.start.line
            column = ctx.start.column
            raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная '{var_name}' не найдена.")

        if ctx.indexList():
            # print(f"  -> Это обращение к таблице '{var_name}'", file=sys.stderr)
            if not var_info['is_table']:
                line = ctx.start.line
                column = ctx.start.column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Попытка доступа по индексу к не табличной переменной '{var_name}'.")
            # TODO: Обработка индексов таблиц
            raise NotImplementedError(f"Обращение к элементу таблицы '{var_name}' пока не реализовано.")
        else:
            if var_info['is_table']:
                #  print(f"  -> Это обращение ко всей таблице '{var_name}' (возвращаем словарь)", file=sys.stderr)
                 return var_info['value']
            else:
                # print(f"  -> Возвращаем значение переменной '{var_name}': {var_info['value']}", file=sys.stderr)
                return var_info['value']

    # Обработка присваивания
    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        if ctx.lvalue():
            lvalue_ctx = ctx.lvalue()
            value_to_assign = self.visit(ctx.expression())
            
            if lvalue_ctx.RETURN_VALUE():
                current_scope = self.scopes[-1]
                # Проверяем, находимся ли мы внутри вызова процедуры/функции
                # (т.е. есть ли более одной области видимости)
                if len(self.scopes) > 1: # Глобальная + локальная = минимум 2
                    current_scope['__знач__'] = value_to_assign
                    # print(f"[DEBUG][Return Value] Присвоено 'знач' = {repr(value_to_assign)} в области {len(self.scopes) -1}", file=sys.stdout)
                else:
                    raise KumirExecutionError("Нельзя использовать 'знач :=' вне тела алгоритма.")
            else:
                target_name = self.get_full_identifier(lvalue_ctx.qualifiedIdentifier())
                
                if lvalue_ctx.indexList():
                    # print(f"  -> Присваивание элементу таблицы: '{target_name}[...]'", file=sys.stderr)
                    raise NotImplementedError(f"Присваивание элементу таблицы '{target_name}' пока не реализовано.")
                else:
                    try:
                        self.update_variable(target_name, value_to_assign) 
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

    def visitExpression(self, ctx: KumirParser.ExpressionContext):
        print(f"[DEBUG][visitExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        # print(f"[DEBUG][visitExpression] Expecting to get a value from visitLogicalOrExpression")
        result = self.visit(ctx.logicalOrExpression())
        print(f"[DEBUG][visitExpression] Received from visitLogicalOrExpression: {result} (type: {type(result)})", file=sys.stderr)
        print(f"[DEBUG][visitExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitLogicalOrExpression(self, ctx: KumirParser.LogicalOrExpressionContext):
        print(f"[DEBUG][visitLogicalOrExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        if not ctx.logicalAndExpression():  # Should not happen based on grammar
            # print(f"[DEBUG][visitLogicalOrExpression] No logicalAndExpression, returning None early.")
            return None

        # print(f"[DEBUG][visitLogicalOrExpression] Expecting to get a value from the first logicalAndExpression")
        result = self.visit(ctx.logicalAndExpression(0))
        print(f"[DEBUG][visitLogicalOrExpression] Received from first logicalAndExpression: {result} (type: {type(result)})", file=sys.stderr)

        if len(ctx.logicalAndExpression()) > 1:
            for i in range(1, len(ctx.logicalAndExpression())):
                # print(f"[DEBUG][visitLogicalOrExpression] Processing OR operation. Current result: {result}")
                # print(f"[DEBUG][visitLogicalOrExpression] Expecting to get a value from next logicalAndExpression")
                right_operand_ctx = ctx.logicalAndExpression(i)
                right_operand = self.visit(right_operand_ctx)
                print(f"[DEBUG][visitLogicalOrExpression] Received for OR's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
                if not isinstance(result, (bool, int)) or not isinstance(right_operand, (bool, int)):
                    raise KumirEvalError(
                        f"Строка ~{ctx.start.line}: Ошибка типа: операция 'ИЛИ' не применима к типам {type(result).__name__} и {type(right_operand).__name__}",
                        ctx.start.line,
                        ctx.start.column
                    )
                result = bool(result) or bool(right_operand)
                # print(f"[DEBUG][visitLogicalOrExpression] Result after OR: {result}")
        
        print(f"[DEBUG][visitLogicalOrExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitLogicalAndExpression(self, ctx: KumirParser.LogicalAndExpressionContext):
        print(f"[DEBUG][visitLogicalAndExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        if not ctx.equalityExpression(): # Should not happen
            # print(f"[DEBUG][visitLogicalAndExpression] No equalityExpression, returning None early.")
            return None

        # print(f"[DEBUG][visitLogicalAndExpression] Expecting to get a value from the first equalityExpression")
        result = self.visit(ctx.equalityExpression(0))
        print(f"[DEBUG][visitLogicalAndExpression] Received from first equalityExpression: {result} (type: {type(result)})", file=sys.stderr)
        
        if len(ctx.equalityExpression()) > 1:
            for i in range(1, len(ctx.equalityExpression())):
                # print(f"[DEBUG][visitLogicalAndExpression] Processing AND operation. Current result: {result}")
                # print(f"[DEBUG][visitLogicalAndExpression] Expecting to get a value from next equalityExpression")
                right_operand_ctx = ctx.equalityExpression(i)
                right_operand = self.visit(right_operand_ctx)
                print(f"[DEBUG][visitLogicalAndExpression] Received for AND's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
                if not isinstance(result, (bool, int)) or not isinstance(right_operand, (bool, int)):
                    raise KumirEvalError(
                        f"Строка ~{ctx.start.line}: Ошибка типа: операция 'И' не применима к типам {type(result).__name__} и {type(right_operand).__name__}",
                        ctx.start.line,
                        ctx.start.column
                    )
                result = bool(result) and bool(right_operand)
                # print(f"[DEBUG][visitLogicalAndExpression] Result after AND: {result}")

        print(f"[DEBUG][visitLogicalAndExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitEqualityExpression(self, ctx: KumirParser.EqualityExpressionContext):
        print(f"[DEBUG][visitEqualityExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        # print(f"[DEBUG][visitEqualityExpression] Expecting to get a value from the first relationalExpression")
        result = self.visit(ctx.relationalExpression(0))
        print(f"[DEBUG][visitEqualityExpression] Received from first relationalExpression: {result} (type: {type(result)})", file=sys.stderr)

        if len(ctx.relationalExpression()) > 1:
            # print(f"[DEBUG][visitEqualityExpression] Processing equality/inequality. Current result: {result}")
            op = ctx.getChild(1).getText()
            # print(f"[DEBUG][visitEqualityExpression] Operator: {op}")
            # print(f"[DEBUG][visitEqualityExpression] Expecting to get a value from the second relationalExpression")
            right_operand_ctx = ctx.relationalExpression(1)
            right_operand = self.visit(right_operand_ctx)
            print(f"[DEBUG][visitEqualityExpression] Received for equality's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
            
            original_left = result
            original_right = right_operand

            # --- DEBUG CHECKS ---
            print(f"[DEBUG][PRE-COMPARE CHECK EQ] type(self): {type(self)}", file=sys.stderr)
            print(f"[DEBUG][PRE-COMPARE CHECK EQ] hasattr(self, '_handle_type_promotion_for_comparison'): {hasattr(self, '_handle_type_promotion_for_comparison')}", file=sys.stderr)
            # --- END DEBUG CHECKS ---
            result, right_operand = self._handle_type_promotion_for_comparison(result, right_operand, ctx)

            if op == '=':
                result = result == right_operand
            elif op == '<>':
                result = result != right_operand
            else:
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Неизвестный оператор сравнения: {op}", ctx.start.line, ctx.start.column)
            # print(f"[DEBUG][visitEqualityExpression] Result after comparison: {result}")
            
        print(f"[DEBUG][visitEqualityExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitRelationalExpression(self, ctx: KumirParser.RelationalExpressionContext):
        # print(f"[DEBUG][visitRelationalExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visit(ctx.additiveExpression(0))
        # print(f"[DEBUG][visitRelationalExpression] Received from first additiveExpression: {result} (type: {type(result)})", file=sys.stderr)

        if len(ctx.additiveExpression()) > 1:
            op = ctx.getChild(1).getText()
            right_operand_ctx = ctx.additiveExpression(1)
            right_operand = self.visit(right_operand_ctx)
            # print(f"[DEBUG][visitRelationalExpression] Received for relational's right operand: {right_operand} (type: {type(right_operand)})", file=sys.stderr)
            
            result, right_operand = self._handle_type_promotion_for_comparison(result, right_operand, ctx)

            if op == '<':
                result = result < right_operand
            elif op == '>':
                result = result > right_operand
            elif op == '<=':
                result = result <= right_operand
            elif op == '>=':
                result = result >= right_operand
            else:
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Неизвестный оператор отношения: {op}", ctx.start.line, ctx.start.column)

        # print(f"[DEBUG][visitRelationalExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitAdditiveExpression(self, ctx: KumirParser.AdditiveExpressionContext):
        # print(f"[DEBUG][visitAdditiveExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visit(ctx.multiplicativeExpression(0))
        # print(f"[DEBUG][visitAdditiveExpression] Initial result from left multiplicativeExpression: {result} (type: {type(result)})", file=sys.stderr)

        for i in range(len(ctx.multiplicativeExpression()) - 1):
            op_node = ctx.getChild(2 * i + 1) # op_node is TerminalNodeImpl
            op_token = op_node.getSymbol()    # op_token is Token
            op_text = op_token.text
            # print(f"[DEBUG][visitAdditiveExpression] Operator: {op_text}, Token type: {op_token.type}", file=sys.stderr)
            
            right_operand_ctx = ctx.multiplicativeExpression(i + 1)
            right_operand = self.visit(right_operand_ctx)
            # print(f"[DEBUG][visitAdditiveExpression] Right operand for '{op_text}': {right_operand} (type: {type(right_operand)})", file=sys.stderr)

            # print(f"[DEBUG][PRE_PERFORM_OP_ADD] op_text:'{op_text}', L_operand:'{result}'({type(result).__name__}), R_operand:'{right_operand}'({type(right_operand).__name__}), expr_ctx:'{ctx.getText()}'", file=sys.stderr)
            result = self._perform_binary_operation(result, right_operand, op_token, ctx)
            # print(f"[DEBUG][visitAdditiveExpression] Result after '{op_text}': {result} (type: {type(result)})", file=sys.stderr)
            
        # print(f"[Exit] visitAdditiveExpression for '{ctx.getText()}' -> returns {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitMultiplicativeExpression(self, ctx: KumirParser.MultiplicativeExpressionContext):
        # print(f"[DEBUG][visitMultiplicativeExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        result = self.visit(ctx.powerExpression(0))
        # print(f"[DEBUG][visitMultiplicativeExpression] Initial result from left powerExpression: {result} (type: {type(result)})", file=sys.stderr)

        for i in range(len(ctx.powerExpression()) - 1):
            op_node = ctx.getChild(2 * i + 1) # op_node is TerminalNodeImpl
            op_token = op_node.getSymbol()    # op_token is Token
            op_text = op_token.text
            # print(f"[DEBUG][visitMultiplicativeExpression] Operator: {op_text}, Token type: {op_token.type}", file=sys.stderr)

            right_operand_ctx = ctx.powerExpression(i + 1)
            right_operand = self.visit(right_operand_ctx)
            # print(f"[DEBUG][visitMultiplicativeExpression] Right operand for '{op_text}': {right_operand} (type: {type(right_operand)})", file=sys.stderr)
            
            # print(f"[DEBUG][PRE_PERFORM_OP_MULT] op_text:'{op_text}', L_operand:'{result}'({type(result).__name__}), R_operand:'{right_operand}'({type(right_operand).__name__}), expr_ctx:'{ctx.getText()}'", file=sys.stderr)
            # --- ВАЖНО: Проверяем, что op_token действительно от арифметической операции, а не от div/mod как ключевых слов ---
            # Для div/mod, которые обрабатываются как BUILTIN_FUNCTIONS, здесь не должно быть вызова _perform_binary_operation
            if op_token.type in ARITHMETIC_OPS: # Только для +, -, *, /, ^
            result = self._perform_binary_operation(result, right_operand, op_token, ctx)
            else:
                # Если это не стандартный арифметический оператор (например, это был 'div' или 'mod' как ключевое слово),
                # то левый операнд (result) уже должен был быть обработан visitPowerExpression,
                # а правый операнд (right_operand) должен быть результатом вызова функции div/mod.
                # Однако, эта логика сейчас неверна, так как div/mod обрабатываются в visitPostfixExpression.
                # Этот блок else, скорее всего, не должен достигаться, если PostfixExpression правильно обрабатывает div/mod.
                # Если мы сюда попали, значит что-то не так с порядком вызовов или грамматикой.
                # Пока просто переприсвоим result, если это был не арифметический оператор, хотя это и неправильно.
                # Это место требует пересмотра, если div/mod не работают.
                # print(f"[WARN][visitMultiplicativeExpression] Operator '{op_text}' (type {op_token.type}) not in ARITHMETIC_OPS. Current result: {result}, right_operand (potentially from func call): {right_operand}", file=sys.stderr)
                # Для div/mod, обработанных как функции, `right_operand` здесь будет результатом вызова этой функции,
                # а `result` будет предыдущим значением. Это неверно для последовательности типа "a div b * c".
                # Оставим пока так, чтобы не ломать то, что работало, но это слабое место.
                # Если `right_operand` пришел из `visit(ctx.powerExpression(i + 1))` и это был вызов функции,
                # то `result` должен быть обновлен.
                # НО! `_perform_binary_operation` уже вызывается для ARITHMETIC_OPS.
                # Если это div/mod, они должны были быть обработаны в visitPostfixExpression -> _call_builtin_function.
                # Значит, `visit(ctx.powerExpression(i + 1))` вернул бы число, а не имя функции.
                # Этот else, вероятно, не нужен, если грамматика и PostfixExpression работают правильно.
                # Я его пока закомментирую. Если что-то сломается с div/mod, будем смотреть сюда.
                # if op_text.lower() in ['div', 'mod'] and not (op_token.type in ARITHMETIC_OPS):
                #    print(f"[WARN][visitMultiplicativeExpression] Reassigning result for func-like '{op_text}'. Old: {result}, New: {right_operand}", file=sys.stderr)
                #    result = right_operand # Это все еще кажется неверным для цепочек
                pass


            # print(f"[DEBUG][visitMultiplicativeExpression] Result after '{op_text}': {result} (type: {type(result)})", file=sys.stderr)

        # print(f"[Exit] visitMultiplicativeExpression for '{ctx.getText()}' -> returns {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitPowerExpression(self, ctx: KumirParser.PowerExpressionContext):
        # print(f"[DEBUG][visitPowerExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        
        unary_expressions_or_obj = ctx.unaryExpression() # Get the list of unary expressions or a single object
        
        first_unary_expr_ctx = None
        exponent_ctx = None

        if isinstance(unary_expressions_or_obj, list):
            if not unary_expressions_or_obj: # Should not happen if grammar ensures at least one
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Отсутствует базовое выражение в выражении степени.")
            first_unary_expr_ctx = unary_expressions_or_obj[0]
            if len(unary_expressions_or_obj) > 1:
                exponent_ctx = unary_expressions_or_obj[1]
        elif unary_expressions_or_obj: # It's a single UnaryExpressionContext object
            first_unary_expr_ctx = unary_expressions_or_obj
        else: # Should not happen
            raise KumirEvalError(f"Строка ~{ctx.start.line}: Неожиданная структура для unaryExpression в powerExpression.")

        # print(f"[DEBUG][visitPowerExpression] Expecting to get a value from the first unaryExpression")
        result = self.visit(first_unary_expr_ctx)
        print(f"[DEBUG][visitPowerExpression] Received from first unaryExpression: {result} (type: {type(result)})", file=sys.stderr)

        if exponent_ctx: # If there is an exponent part
            # print(f"[DEBUG][visitPowerExpression] Processing power operation. Current result: {result}")
            # print(f"[DEBUG][visitPowerExpression] Expecting to get a value from the second unaryExpression (exponent)")
            exponent = self.visit(exponent_ctx)
            print(f"[DEBUG][visitPowerExpression] Received for exponent: {exponent} (type: {type(exponent)})", file=sys.stderr)
            
            if not isinstance(result, (int, float)) or not isinstance(exponent, (int, float)):
                raise KumirEvalError(
                    f"Строка ~{ctx.start.line}: Операция возведения в степень применима только к числовым типам (получены {type(result).__name__} и {type(exponent).__name__})",
                    ctx.start.line,
                    ctx.start.column
                )
            try:
                result = result ** exponent
            except TypeError:
                 raise KumirEvalError(
                    f"Строка ~{ctx.start.line}: Ошибка типа при возведении в степень: {type(result).__name__} ** {type(exponent).__name__}",
                    ctx.start.line,
                    ctx.start.column
                )
            # print(f"[DEBUG][visitPowerExpression] Result after power operation: {result}")

        print(f"[DEBUG][visitPowerExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result
        
    def visitUnaryExpression(self, ctx: KumirParser.UnaryExpressionContext):
        print(f"[DEBUG][visitUnaryExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        if ctx.postfixExpression():
            # print(f"[DEBUG][visitUnaryExpression] No unary operator, visiting postfixExpression")
            # print(f"[DEBUG][visitUnaryExpression] Expecting to get a value from postfixExpression")
            result = self.visit(ctx.postfixExpression())
            print(f"[DEBUG][visitUnaryExpression] Received from postfixExpression: {result} (type: {type(result)})", file=sys.stderr)
            print(f"[DEBUG][visitUnaryExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
            return result
        
        operator = ctx.getChild(0).getText()
        # print(f"[DEBUG][visitUnaryExpression] Unary operator: {operator}")
        # print(f"[DEBUG][visitUnaryExpression] Expecting to get a value from recursive call to visitUnaryExpression for operand")
        operand = self.visit(ctx.unaryExpression(0)) # unaryExpression is recursive for multiple operators
        print(f"[DEBUG][visitUnaryExpression] Received for operand: {operand} (type: {type(operand)})", file=sys.stderr)

        if operator == '-':
            if not isinstance(operand, (int, float)):
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Унарный минус применим только к числам (получен {type(operand).__name__})", ctx.start.line, ctx.start.column)
            result = -operand
        elif operator.lower() == 'не':
            if not isinstance(operand, (bool, int)): # int can be cast to bool
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Логическое отрицание 'не' применимо только к логическим или целым значениям (получен {type(operand).__name__})", ctx.start.line, ctx.start.column)
            result = not bool(operand)
        elif operator == '+': # Unary plus
            if not isinstance(operand, (int, float)):
                raise KumirEvalError(f"Строка ~{ctx.start.line}: Унарный плюс применим только к числам (получен {type(operand).__name__})", ctx.start.line, ctx.start.column)
            result = operand # Unary plus doesn't change the value
        else:
            raise KumirEvalError(f"Строка ~{ctx.start.line}: Неизвестный унарный оператор: {operator}", ctx.start.line, ctx.start.column)
        
        # print(f"[DEBUG][visitUnaryExpression] Result after unary operation: {result}")
        print(f"[DEBUG][visitUnaryExpression] Returning: {result} (type: {type(result)})", file=sys.stderr)
        return result

    def visitPostfixExpression(self, ctx: KumirParser.PostfixExpressionContext):
        # print(f"[Enter] visitPostfixExpression for {ctx.getText()}", file=sys.stderr)
        primary = ctx.primaryExpression()
        if not primary:
            raise KumirEvalError("Отсутствует primaryExpression в postfixExpression")

        current_eval_value = self.visit(primary)

        for i in range(1, ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, antlr4.tree.Tree.TerminalNode):
                continue

            if child.getRuleIndex() == KumirParser.RULE_indexList:
                # ... (обработка индексации, current_eval_value обновляется)
                if not isinstance(current_eval_value, list): # Проверка типа перед индексацией
                    raise KumirEvalError("Попытка индексации не массива")
                index_val = self.visit(child) # visitIndexList должен вернуть либо int, либо (int, int) для среза
                # TODO: Более сложная обработка срезов и многомерных массивов
                if isinstance(index_val, int):
                    if index_val < 0 or index_val >= len(current_eval_value):
                        raise KumirEvalError(f"Индекс {index_val} вне границ массива [0..{len(current_eval_value)-1}]")
                    current_eval_value = current_eval_value[index_val]
                else: 
                    raise KumirEvalError("Сложные индексы (срезы, многомерные) пока не полностью поддерживаются.")

            elif child.getRuleIndex() == KumirParser.RULE_argumentList:
                if not isinstance(current_eval_value, str):
                    line = ctx.primaryExpression().start.line
                    column = ctx.primaryExpression().start.column
                    raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вызова не процедуры/функции (получено значение типа {type(current_eval_value).__name__})")
                
                proc_name = current_eval_value
                args = self.visit(child) if child.getChildCount() > 0 else []
                # print(f"[DEBUG][Postfix] Вызов процедуры/функции '{proc_name}' с аргументами: {args}", file=sys.stderr)
                
                proc_name_lower = proc_name.lower()
                if proc_name_lower in self.BUILTIN_FUNCTIONS:
                    arg_count = len(args)
                    builtin_variants = self.BUILTIN_FUNCTIONS[proc_name_lower]
                    if arg_count not in builtin_variants:
                        raise KumirEvalError(f"Неверное количество аргументов для встроенной процедуры '{proc_name}': ожидалось одно из {list(builtin_variants.keys())}, получено {arg_count}")
                    try:
                        # Добавляем print перед вызовом
                        print(f"!!! [Builtin Call PRE] Calling '{proc_name_lower}' with args: {repr(args)} (types: {[type(arg) for arg in args]})", flush=True, file=sys.stderr)
                        result_of_call = builtin_variants[arg_count](*args)
                        # Добавляем print после вызова
                        print(f"!!! [Builtin Call POST] '{proc_name_lower}' returned: {repr(result_of_call)} (type: {type(result_of_call)})", flush=True, file=sys.stderr)
                        current_eval_value = result_of_call
                    except Exception as e:
                        line = child.start.line
                        column = child.start.column
                        raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка выполнения встроенной процедуры '{proc_name}': {e}")
                
                elif proc_name in self.procedures:
                    proc_def_ctx = self.procedures[proc_name]
                    header = proc_def_ctx.algorithmHeader()
                    params_ctx = header.parameterList()
                    arg_list_ctx = child
                    output_params_mapping = []
                    expected_params = []

                    if params_ctx:
                        param_index = 0
                        for param_decl_ctx in params_ctx.parameterDeclaration():
                            param_type_ctx = param_decl_ctx.typeSpecifier()
                            param_type_name = self._get_type_name_from_specifier(param_type_ctx)
                            mode = self._get_param_mode(param_decl_ctx)
                            param_vars_list_ctx = param_decl_ctx.variableList()
                            if not param_vars_list_ctx: raise KumirEvalError(f"Строка {param_decl_ctx.start.line}: Ошибка парсинга - отсутствует список переменных в объявлении параметра.")
                            for param_var_item_ctx in param_vars_list_ctx.variableDeclarationItem():
                                param_name_map = param_var_item_ctx.ID().getText()
                                expected_params.append({'name': param_name_map, 'type': param_type_name, 'mode': mode})
                                if mode in ['рез', 'арг рез']:
                                    # ... (логика output_params_mapping как была)
                                    if param_index < len(arg_list_ctx.expression()):
                                        arg_expr_ctx = arg_list_ctx.expression(param_index)
                                        try:
                                            current_expr_node = arg_expr_ctx
                                            path_to_id = ['logicalOrExpression', 'logicalAndExpression', 'equalityExpression', 
                                                          'relationalExpression', 'additiveExpression', 'multiplicativeExpression', 
                                                          'powerExpression', 'unaryExpression', 'postfixExpression', 
                                                          'primaryExpression']
                                            temp_node = current_expr_node
                                            valid_path = True
                                            for rule_name_part in path_to_id:
                                                if hasattr(temp_node, rule_name_part) and callable(getattr(temp_node, rule_name_part)):
                                                    node_or_list = getattr(temp_node, rule_name_part)()
                                                    if isinstance(node_or_list, list): temp_node = node_or_list[0] if node_or_list else None
                                                    else: temp_node = node_or_list
                                                    if temp_node is None: valid_path = False; break
                                                else: valid_path = False; break
                                            if valid_path and hasattr(temp_node, 'qualifiedIdentifier') and temp_node.qualifiedIdentifier():
                                                caller_var_name = temp_node.qualifiedIdentifier().getText()
                                                caller_var_info, _ = self.find_variable(caller_var_name)
                                                if caller_var_info:
                                                    output_params_mapping.append({'caller_var_name': caller_var_name, 'proc_param_name': param_name_map})
                                                    # print(f"[DEBUG][Param Map] Сопоставлен выходной параметр: '{caller_var_name}' -> '{param_name_map}'", file=sys.stderr)
                                                else: raise KumirEvalError(f"Строка {arg_expr_ctx.start.line}: Переменная '{caller_var_name}', переданная как аргумент для параметра '{mode}', не найдена в вызывающей области.")
                                            elif mode in ['рез', 'арг рез']: raise KumirEvalError(f"Строка {arg_expr_ctx.start.line}: Аргумент для параметра '{mode}' ('{param_name_map}') должен быть простой переменной.")
                                        except AttributeError as e_attr: 
                                            # print(f"[WARN][Param Map] Не удалось сопоставить '{param_name_map}': {e_attr}", file=sys.stderr)
                                            if mode == 'арг рез': raise KumirEvalError(f"Строка {arg_expr_ctx.start.line}: Не удалось распознать аргумент для 'арг рез' ('{param_name_map}') как переменную.")
                                    elif mode == 'арг рез': raise KumirEvalError(f"Отсутствует аргумент для 'арг рез' '{param_name_map}' в '{proc_name}'.")
                                param_index += 1
                    
                    # print(f"[DEBUG][ProcCall] Ожидаемые параметры для '{proc_name}': {expected_params}", file=sys.stderr)
                    # print(f"[DEBUG][ProcCall] Сопоставление выходных параметров: {output_params_mapping}", file=sys.stderr)
                    actual_args = self.visit(arg_list_ctx) if arg_list_ctx.getChildCount() > 0 else []
                    num_expected_input_args = len([p for p in expected_params if p['mode'] in ['арг', 'арг рез']])
                    if len(actual_args) != num_expected_input_args:
                        raise KumirEvalError(f"Неверное количество аргументов для '{proc_name}': ожидалось {num_expected_input_args} входных, получено {len(actual_args)}")
                    
                    self.enter_scope()
                    local_scope = self.scopes[-1]
                    local_scope['__знач__'] = None
                    
                    # Переменная для хранения результата вызова этой пользовательской функции/процедуры
                    # Она будет обновлена либо из __знач__, либо из последнего рез/аргрез параметра
                    procedure_call_result_value = None 

                    try:
                        arg_idx_counter = 0
                        for param_info_loop in expected_params: # Избегаем конфликта имен с i внешнего цикла
                            param_name_inner = param_info_loop['name']
                            param_type_inner = param_info_loop['type']
                            param_mode_inner = param_info_loop['mode']
                            self.declare_variable(param_name_inner, param_type_inner)
                            if param_mode_inner in ['арг', 'арг рез']:
                                if arg_idx_counter < len(actual_args):
                                    arg_value_inner = actual_args[arg_idx_counter]
                                    if self.debug: print(f"[DEBUG][ProcCall PRE_VALIDATE] Param '{param_name_inner}' ({param_type_inner}), got arg_value_inner: {repr(arg_value_inner)} from actual_args[{arg_idx_counter}]", file=sys.stderr)
                                    try:
                                        converted_arg_value = self._validate_and_convert_value_for_assignment(arg_value_inner, param_type_inner, param_name_inner)
                                        self.update_variable(param_name_inner, converted_arg_value)
                                        # print(f"[DEBUG][ProcCall Init] Инициализация параметра '{param_mode_inner}' '{param_name_inner}' значением {repr(converted_arg_value)}", file=sys.stderr)
                                    except (AssignmentError, DeclarationError, KumirExecutionError) as e:
                                        line = arg_list_ctx.expression(arg_idx_counter).start.line
                                        raise KumirEvalError(f"Строка ~{line}: Ошибка типа при передаче аргумента №{arg_idx_counter+1} в параметр '{param_name_inner}': {e}")
                                    arg_idx_counter += 1
                                else: 
                                    raise KumirEvalError(f"Недостаточно аргументов для '{param_mode_inner}' '{param_name_inner}'.")
                            elif param_mode_inner == 'рез':
                                # print(f"[DEBUG][ProcCall Init] Параметр '{param_mode_inner}' '{param_name_inner}' инициализирован по умолчанию.", file=sys.stderr)
                                pass # Просто регистрируем, значение будет установлено в теле процедуры
                        
                        # print(f"[DEBUG][ProcCall] Выполнение тела процедуры '{proc_name}'", file=sys.stderr)
                        self.visit(proc_def_ctx.algorithmBody())


                        caller_scope = self.scopes[-2]
                        
                        for mapping in output_params_mapping:
                            caller_var_name = mapping['caller_var_name']
                            proc_param_name = mapping['proc_param_name']
                            
                            if proc_param_name not in local_scope:
                                raise KumirExecutionError(f"Внутренняя ошибка: параметр '{proc_param_name}' не найден в локальной области при выходе из '{proc_name}'.")
                            if caller_var_name not in caller_scope:
                                raise KumirExecutionError(f"Внутренняя ошибка: переменная '{caller_var_name}' не найдена в вызывающей области при выходе из '{proc_name}'.")
                                
                            final_param_value = local_scope[proc_param_name]['value']
                            caller_var_info = caller_scope[caller_var_name]
                            target_type = caller_var_info['type']
                            
                            # print(f"[DEBUG][ProcCall Exit] Копируем '{proc_param_name}' ({repr(final_param_value)}) -> '{caller_var_name}' ({target_type})", file=sys.stderr)
                            
                            try:
                                converted_value = self._validate_and_convert_value_for_assignment(final_param_value, target_type, caller_var_name)
                                caller_var_info['value'] = converted_value
                            except (AssignmentError, DeclarationError, KumirExecutionError) as e:
                                line = proc_def_ctx.algorithmHeader().start.line
                                raise KumirExecutionError(f"Строка ~{line}: Ошибка при возврате значения из параметра '{proc_param_name}' в переменную '{caller_var_name}': {e}")
                        
                        # --- Определение возвращаемого значения ---
                        if header.typeSpecifier(): # Если это явно объявленная функция (алг ТИП ...)
                            value = local_scope.get('__знач__')
                            if value is None: # Если 'знач :=' не было выполнено
                                func_signature_for_error = f"{header.typeSpecifier().getText()} {proc_name}"
                                raise KumirEvalError(f"Функция '{func_signature_for_error}' не присвоила значение переменной 'знач'.")
                            # print(f"[DEBUG][ProcCall Return] Явный возврат 'знач' из функции '{proc_name}': {repr(value)}", file=sys.stderr)
                        else: # Если это процедура (алг ИМЯ ...)
                              # или используется как функция с неявным возвратом через последний 'рез'
                            result_params_in_order = [p['name'] for p in expected_params if p['mode'] == 'рез']
                            inout_result_params_in_order = [p['name'] for p in expected_params if p['mode'] == 'арг рез']
                            
                            potential_return_param_name = None
                            if result_params_in_order:
                                potential_return_param_name = result_params_in_order[-1]
                            elif inout_result_params_in_order:
                                potential_return_param_name = inout_result_params_in_order[-1]

                            if potential_return_param_name and potential_return_param_name in local_scope:
                                value = local_scope[potential_return_param_name]['value']
                                # print(f"[DEBUG][ProcCall Return] Неявный возврат из '{proc_name}' через параметр '{potential_return_param_name}': {repr(value)}", file=sys.stderr)
                            else: # Добавил else, чтобы value всегда было определено
                                value = None # Обычная процедура без возвращаемого значения или не удалось найти параметр
                                # print(f"[DEBUG][ProcCall Return] Процедура '{proc_name}' вернула None (нет явного/неявного возврата через рез/аргрез или 'знач')", file=sys.stderr)
                        current_eval_value = value # Обновляем current_eval_value результатом вызова
                    finally:
                        self.exit_scope()
                else:
                    # Это не процедура из self.procedures и не встроенная.
                    line = ctx.primaryExpression().start.line
                    column = ctx.primaryExpression().start.column
                    raise KumirExecutionError(f"Строка {line}, столбец {column}: Процедура или функция '{proc_name}' не найдена.")
        print(f"[Exit] visitPostfixExpression for {ctx.getText()} -> returns {repr(current_eval_value)}", file=sys.stderr)
        return current_eval_value

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
        print(f"[DEBUG][visitPrimaryExpression] Called for ctx: {ctx.getText()}", file=sys.stderr) # Добавляем file=sys.stderr
        if ctx.literal():
            result = self.visit(ctx.literal())
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
                    result = var_info['value'] # Возвращаем словарь {индекс: значение}
                else:
                    # Для скалярной переменной возвращаем само значение
                    print(f"[DEBUG][Primary] Возвращаем значение переменной '{name}': {var_info['value']}", file=sys.stderr)
                    result = var_info['value']
            # Если не переменная, возможно это имя процедуры/функции
            # В этом случае visitPostfixExpression должен обработать вызов
            # Возвращаем имя как строку, чтобы PostfixExpression знал, что вызывать
            else:
                print(f"[DEBUG][Primary] Возвращаем имя процедуры/функции '{name}'", file=sys.stderr)
                result = name
        elif ctx.RETURN_VALUE():
            # Используем последний элемент из стека self.scopes
            current_scope_dict = self.scopes[-1]
            if '__знач__' not in current_scope_dict: # Проверяем в словаре текущей области
                raise KumirEvalError("Попытка использования неинициализированного возвращаемого значения")
            result = current_scope_dict['__знач__'] # Читаем по ключу '__знач__'
        elif ctx.LPAREN():
            result = self.visit(ctx.expression())
        elif ctx.arrayLiteral():
            result = self.visit(ctx.arrayLiteral())
        else:
            raise KumirEvalError("Некорректное первичное выражение")

        print(f"[DEBUG][visitPrimaryExpression] Returning: {result} (type: {type(result)})", file=sys.stderr) # Добавляем file=sys.stderr
        return result

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
            loop_count = 0 # Счетчик итераций для отладки
            if self.debug: print(f"[DEBUG][While 15] Вход в цикл ПОКА", file=sys.stderr)
            while True:
                condition_expr = loop_spec.expression()
                if not condition_expr:
                     raise KumirEvalError(f"Строка {loop_spec.start.line}: Отсутствует выражение условия для цикла ПОКА")
                condition = self.visit(condition_expr)
                condition_value = self._get_value(condition)
                if self.debug: print(f"[DEBUG][While 15] Итерация {loop_count}, проверка условия ({condition_expr.getText()}): {condition_value}", file=sys.stderr)
                if not isinstance(condition_value, bool):
                    raise KumirEvalError(f"Строка {loop_spec.start.line}: Условие цикла ПОКА должно быть логическим, получено {type(condition_value).__name__}")
                if not condition_value:
                    if self.debug: print(f"[DEBUG][While 15] Условие ложно, выход из цикла.", file=sys.stderr)
                    break
                # --- DEBUG 15-while --- 
                n_val_before = self.find_variable('n')[0]['value'] if self.find_variable('n')[0] else 'N/A'
                count_val_before = self.find_variable('count')[0]['value'] if self.find_variable('count')[0] else 'N/A'
                if self.debug: print(f"[DEBUG][While 15] Перед телом итерации {loop_count}: n={n_val_before}, count={count_val_before}", file=sys.stderr)
                # ---------------------
                try:
                    self.visit(ctx.statementSequence())
                except LoopExitException:
                    break
                except Exception as e:
                    line = ctx.start.line
                    column = ctx.start.column
                    raise KumirExecutionError(f"Строка {line}, столбец {column}: Ошибка внутри цикла ПОКА: {str(e)}")
                # --- DEBUG 15-while --- 
                n_val_after = self.find_variable('n')[0]['value'] if self.find_variable('n')[0] else 'N/A'
                count_val_after = self.find_variable('count')[0]['value'] if self.find_variable('count')[0] else 'N/A'
                if self.debug: print(f"[DEBUG][While 15] После тела итерации {loop_count}: n={n_val_after}, count={count_val_after}", file=sys.stderr)
                # ---------------------
                loop_count += 1 # Увеличиваем счетчик итераций

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
                if self.debug: print("[DEBUG][OUTPUT] Начало обработки вывода", file=sys.stderr)
                args = io_ctx.ioArgumentList().ioArgument() if io_ctx.ioArgumentList() else []
                
                printed_non_literal = False 

                for i, arg_ctx in enumerate(args):
                    arg_text_debug = arg_ctx.getText()
                    if self.debug: print(f"[DEBUG][OUTPUT] Обработка аргумента {i}: {arg_text_debug}", file=sys.stderr)
                    try:
                        if arg_ctx.NEWLINE_CONST():
                            if self.debug: print(f"[DEBUG][OUTPUT] Печать НС", file=sys.stderr)
                            sys.stdout.write('\n')
                            printed_non_literal = True
                            continue 

                        formatted_value = ""
                        expr_list = arg_ctx.expression()
                        is_simple_string_literal = False
                        literal_value = None

                        if expr_list: 
                            expr_ctx = expr_list[0] if isinstance(expr_list, list) else expr_list 
                            if expr_ctx is None:
                                line = arg_ctx.start.line
                                column = arg_ctx.start.column
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Получено некорректное выражение для вывода (None)")
                            
                            # --- Определяем, простой ли это строковый литерал --- 
                            try:
                                primary = (expr_ctx.logicalOrExpression()
                                           .logicalAndExpression(0).equalityExpression(0)
                                           .relationalExpression(0).additiveExpression(0)
                                           .multiplicativeExpression(0).powerExpression(0)
                                           .unaryExpression().postfixExpression()
                                           .primaryExpression())
                                if primary and primary.literal() and primary.literal().STRING():
                                    is_simple_string_literal = True
                                    raw_text = primary.literal().STRING().getText()
                                    if len(raw_text) >= 2 and raw_text.startswith(('"', "'")) and raw_text.endswith(('"', "'")):
                                        inner_text = raw_text[1:-1]
                                        literal_value = inner_text.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                                    else:
                                        literal_value = raw_text
                            except AttributeError:
                                is_simple_string_literal = False
                            # ---------------------------------------------------------
                            
                            if self.debug: print(f"[DEBUG][OUTPUT] Аргумент {i}: is_simple_string_literal={is_simple_string_literal}, literal_value='{literal_value}'", file=sys.stderr)

                            if is_simple_string_literal:
                                formatted_value = literal_value
                                if self.debug: print(f"[DEBUG][OUTPUT] Аргумент {i}: Значение - строка '{formatted_value}'", file=sys.stderr)
                            else:
                                if self.debug: print(f"[DEBUG][OUTPUT] Аргумент {i}: Вычисление выражения {expr_ctx.getText()}", file=sys.stderr)
                                if self.debug: print(f"[DEBUG][OUTPUT][VISIT_STATEMENT] Перед вызовом self.visit для выражения: {expr_ctx.getText()}", file=sys.stderr)
                                value = self.visit(expr_ctx)
                                if self.debug: print(f"[DEBUG][OUTPUT][VISIT_STATEMENT] После вызова self.visit, value = {repr(value)} (type: {type(value).__name__}) для выражения: {expr_ctx.getText()}", file=sys.stderr)
                                value = self._get_value(value)
                                if self.debug: print(f"[DEBUG][OUTPUT] Аргумент {i}: Вычислено value={repr(value)} ({type(value).__name__})", file=sys.stderr)
                                
                                if value is None:
                                    expr_text = expr_ctx.getText() if hasattr(expr_ctx, 'getText') else '[Unknown Expression]'
                                    line = expr_ctx.start.line
                                    column = expr_ctx.start.column
                                    raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вывести неинициализированное значение (выражение: {expr_text})")

                                formatted_value = self._format_output_value(value, arg_ctx)
                                printed_non_literal = True 
                        elif arg_ctx.STRING(): 
                            text_node = arg_ctx.STRING()
                            if not text_node:
                                line = arg_ctx.start.line
                                column = arg_ctx.start.column
                                raise KumirEvalError(f"Строка {line}, столбец {column}: Отсутствует строковый литерал для вывода")
                            text = text_node.getText()
                            value = text[1:-1].replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                            formatted_value = value
                        else:
                            line = arg_ctx.start.line
                            column = arg_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Некорректный аргумент для вывода (ни выражение, ни строка)")
                        
                        if self.debug: print(f"[DEBUG][OUTPUT] Аргумент {i}: Печать formatted_value='{formatted_value}'", file=sys.stderr)
                        sys.stdout.write(formatted_value)
                        
                    # --- ИСПРАВЛЕНО: except блок с правильным отступом --- 
                    except Exception as e:
                        if not isinstance(e, KumirEvalError):
                            line = arg_ctx.start.line if arg_ctx else io_ctx.start.line
                            column = arg_ctx.start.column if arg_ctx else io_ctx.start.column
                            raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка при обработке вывода: {e}")
                        raise
                
                # --- Обработка финального переноса строки --- 
                ends_with_newline_const = args and args[-1].NEWLINE_CONST()
                if printed_non_literal and not ends_with_newline_const:
                     sys.stdout.write('\n')
                # -------------------------------------------
                if self.debug: print("[DEBUG][OUTPUT] Конец обработки вывода", file=sys.stderr)
                return None
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
        parent_ctx = ctx.parentCtx # Получаем родительский контекст (это должен быть PostfixExpression)
        func_name_debug = "UNKNOWN_FUNC"
        if isinstance(parent_ctx, KumirParser.PostfixExpressionContext) and parent_ctx.primaryExpression():
            func_name_debug = parent_ctx.primaryExpression().getText()
        
        if self.debug: print(f"[Enter] visitArgumentList for {func_name_debug}({ctx.getText()})", file=sys.stderr)
        args = []
        for i, expr_ctx in enumerate(ctx.expression()):
            raw_arg_value = self.visitExpression(expr_ctx) # <--- ЯВНЫЙ ВЫЗОВ
            if self.debug: print(f"[DEBUG][ArgList Proc] For {func_name_debug}, Arg {i} ({expr_ctx.getText()}): evaluated to {repr(raw_arg_value)} ({type(raw_arg_value).__name__})", file=sys.stderr)
            args.append(raw_arg_value)
        if self.debug: print(f"[Exit] visitArgumentList for {func_name_debug}({ctx.getText()}) -> returns {repr(args)}", file=sys.stderr)
        return args

    def visitPrimaryExpression(self, ctx:KumirParser.PrimaryExpressionContext):
        print(f"[DEBUG][visitPrimaryExpression] Called for ctx: {ctx.getText()}", file=sys.stderr) # Добавляем file=sys.stderr
        if ctx.literal():
            result = self.visit(ctx.literal())
        elif ctx.qualifiedIdentifier():
            name = ctx.qualifiedIdentifier().getText()
            var_info, _ = self.find_variable(name)
            if var_info:
                if var_info['is_table']:
                    # Если это таблица, но обращаемся без индекса, возвращаем весь словарь значений
                    # (Для присваивания или передачи как аргумент)
                    # TODO: Уточнить поведение КуМир при передаче таблиц
                    print(f"[DEBUG][Primary] Возвращаем всю таблицу '{name}'", file=sys.stderr)
                    result = var_info['value'] # Возвращаем словарь {индекс: значение}
                else:
                    # Для скалярной переменной возвращаем само значение
                    print(f"[DEBUG][Primary] Возвращаем значение переменной '{name}': {var_info['value']}", file=sys.stderr)
                    result = var_info['value']
            else:
                print(f"[DEBUG][Primary] Возвращаем имя процедуры/функции '{name}'", file=sys.stderr)
                result = name
        elif ctx.RETURN_VALUE():
            # Используем последний элемент из стека self.scopes
            current_scope_dict = self.scopes[-1]
            if '__знач__' not in current_scope_dict: # Проверяем в словаре текущей области
                raise KumirEvalError("Попытка использования неинициализированного возвращаемого значения")
            result = current_scope_dict['__знач__']
        elif ctx.LPAREN():
            result = self.visit(ctx.expression())
        elif ctx.arrayLiteral():
            result = self.visit(ctx.arrayLiteral())
        else:
            raise KumirEvalError("Некорректное первичное выражение")

        print(f"[DEBUG][visitPrimaryExpression] Returning: {result} (type: {type(result)})", file=sys.stderr) # Добавляем file=sys.stderr
        return result

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

    # --- Метод для visitLiteral ---
    def visitLiteral(self, ctx:KumirParser.LiteralContext):
        text_debug = ctx.getText()
        # print(f"[DEBUG][VisitLiteral] Processing literal: '{text_debug}'", file=sys.stderr)

        if ctx.INTEGER():
            text = ctx.INTEGER().getText()
            val = None
            if text.startswith('$'): # Hex
                val = int(text[1:], 16)
            else: # Decimal
                val = int(text)
            # print(f"[DEBUG][VisitLiteral] INTEGER '{text}' parsed as {repr(val)} (type {type(val).__name__})", file=sys.stderr)
            return val
        elif ctx.REAL():
            val = float(ctx.REAL().getText().replace(',', '.')) # Заменяем запятую на точку для совместимости
            # print(f"[DEBUG][VisitLiteral] REAL '{ctx.REAL().getText()}' parsed as {repr(val)} (type {type(val).__name__})", file=sys.stderr)
            return val
        elif ctx.STRING():
            text = ctx.STRING().getText()
            val = text[1:-1].replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
            # print(f"[DEBUG][VisitLiteral] STRING '{text}' parsed as {repr(val)} (type {type(val).__name__})", file=sys.stderr)
            return val
        elif ctx.CHAR_LITERAL():
            text = ctx.CHAR_LITERAL().getText()
            val = text[1:-1].replace('\\\\"', '"').replace("\\\\'", "'").replace('\\\\\\\\', '\\\\') # Аналогично STRING
            # print(f"[DEBUG][VisitLiteral] CHAR_LITERAL '{text}' parsed as {repr(val)} (type {type(val).__name__})", file=sys.stderr)
            return val
        elif ctx.TRUE():
            # print(f"[DEBUG][VisitLiteral] TRUE parsed as True", file=sys.stderr)
            return True
        elif ctx.FALSE():
            # print(f"[DEBUG][VisitLiteral] FALSE parsed as False", file=sys.stderr)
            return False
        elif ctx.colorLiteral():
            val = ctx.colorLiteral().getText()
            # print(f"[DEBUG][VisitLiteral] colorLiteral '{val}' parsed as string", file=sys.stderr)
            return val 
        elif ctx.NEWLINE_CONST():
            # print(f"[DEBUG][VisitLiteral] NEWLINE_CONST parsed as '\\n'", file=sys.stderr)
            return '\\n' 

        # print(f"[DEBUG][VisitLiteral] Literal '{text_debug}' did not match any known literal type, returning None (ERROR!)", file=sys.stderr)
        return None 
    # --- Конец visitLiteral ---

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
    # DiagnosticErrorListener is defined in this file, so no relative import needed.
    
    input_stream = InputStream(code)
    lexer = KumirLexer(input_stream)
    lexer.removeErrorListeners() 
    error_listener = DiagnosticErrorListener() # Instantiate local class
    lexer.addErrorListener(error_listener)
    
    token_stream = CommonTokenStream(lexer)
    parser = KumirParser(token_stream)
    parser.removeErrorListeners() 
    parser.addErrorListener(error_listener) # Используем тот же слушатель для парсера

    tree = None
    try:
        tree = parser.program() # Attempt to parse
        # After parsing, check if the listener collected any syntax errors
        # No need to check error_listener.errors if DiagnosticErrorListener raises immediately.
        # if error_listener.errors:
        #     first_error = error_listener.errors[0]
        #     # print(f"[DEBUG_INTERPRET_KUMIR] Syntax errors found by listener: {error_listener.errors}", file=sys.stderr)
        #     raise KumirSyntaxError(first_error['message'], first_error['line'], first_error['column'])
    except KumirSyntaxError: # Re-raise if DiagnosticErrorListener raised it
        raise
    except Exception as e: # Catch other ANTLR or parsing-related exceptions
        # print(f"[DEBUG_INTERPRET_KUMIR] ANTLR parsing failed: {e}", file=sys.stderr) # Используем sys.stderr для таких сообщений
        raise KumirSyntaxError(f"Ошибка синтаксического анализа: {e}", 0, 0) from e

    visitor = KumirInterpreterVisitor()
    
    original_stdout = sys.stdout
    original_stderr = sys.stderr 

    stdout_capture = StringIO()
    sys.stdout = stdout_capture 

    try:
        visitor.visit(tree)
    except KumirInputRequiredError:
        # print(f"[DEBUG][interpret_kumir] InputRequiredError caught. Output so far: {stdout_capture.getvalue()}", file=original_stderr) # original_stderr здесь будет правильным
        raise 
    except Exception as e:
        # print(f"[ERROR][interpret_kumir] Exception during KUMIR program execution: {type(e).__name__} - {e}", file=original_stderr)
        # import traceback
        # traceback.print_exc(file=original_stderr)
        raise 
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
            
    # DEBUG PRINT ПЕРЕД ВОЗВРАТОМ (используем sys.stderr, так как original_stderr восстановлен)
    print(f"[DEBUG_INTERPRET_KUMIR] About to return from interpret_kumir. stdout_capture type: {type(stdout_capture)}", file=sys.stderr)
    captured_content = stdout_capture.getvalue()
    print(f"[DEBUG_INTERPRET_KUMIR] Content of stdout_capture ({len(captured_content)} chars):\n>>>\\n{captured_content}\\n<<<", file=sys.stderr)
        
    return captured_content