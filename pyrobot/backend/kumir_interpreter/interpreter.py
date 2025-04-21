# FILE START: interpreter.py
import logging
import copy
import math # Добавлено для pow
import operator # Добавлено для операций

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
from .generated.KumirVisitor import KumirVisitor
from .generated.KumirParser import KumirParser
from .generated.KumirLexer import KumirLexer # Импортируем лексер для имен токенов
# Добавляем ErrorListener
from antlr4.error.ErrorListener import ErrorListener

# Убрали импорт KumirEvalError из safe_eval

MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT
logger = logging.getLogger('KumirInterpreter')

# Словарь для маппинга токенов типа на строки
TYPE_MAP = {
    KumirLexer.K_CEL: 'цел',
    KumirLexer.K_VESH: 'вещ',
    KumirLexer.K_LOG: 'лог',
    KumirLexer.K_SIM: 'сим',
    KumirLexer.K_LIT: 'лит',
}

# Словари для операций
ARITHMETIC_OPS = {
    KumirLexer.PLUS: operator.add,
    KumirLexer.MINUS: operator.sub,
    KumirLexer.MUL: operator.mul,
    KumirLexer.DIV: operator.truediv, # Обычное деление -> вещ
    KumirLexer.K_DIV: operator.floordiv, # Целочисленное деление -> цел
    KumirLexer.K_MOD: operator.mod, # Остаток -> цел
    KumirLexer.POW: operator.pow,
}

COMPARISON_OPS = {
    KumirLexer.EQ: operator.eq,
    KumirLexer.NEQ: operator.ne,
    KumirLexer.LT: operator.lt,
    KumirLexer.GT: operator.gt,
    KumirLexer.LE: operator.le,
    KumirLexer.GE: operator.ge,
}

# Добавляем логические операции
LOGICAL_OPS = {
    KumirLexer.K_I: operator.and_,
    KumirLexer.K_ILI: operator.or_,
    # KumirLexer.K_NE handled in unaryExpr
}

# Класс для вывода подробных ошибок парсинга
class DiagnosticErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"[DEBUG][Parser Error] Строка {line}:{column} около '{offendingSymbol.text if offendingSymbol else 'EOF'}' - {msg}")

def get_default_value(kumir_type):
    """Возвращает значение по умолчанию для данного типа Кумира."""
    if kumir_type == 'цел': return 0
    if kumir_type == 'вещ': return 0.0
    if kumir_type == 'лог': return False # В Кумире логические по умолчанию могут быть не инициализированы, но False безопаснее
    if kumir_type == 'сим': return ''    # Или может быть ошибка?
    if kumir_type == 'лит': return ""
    return None # Для таблиц или неизвестных типов


class KumirInterpreterVisitor(KumirVisitor):
    """Обходит дерево разбора Кумира и выполняет семантические действия."""

    def __init__(self):
        self.scopes = [{'global': {}}] # Стек областей видимости, [0] - глобальная
        self.current_scope_level = 0 # Уровень текущей области (0 - глобальная)
        # TODO: Добавить обработку возвращаемых значений функций

    # --- Управление областями видимости и символами ---

    def enter_scope(self):
        """Входит в новую локальную область видимости."""
        self.scopes.append({}) # Добавляем новый пустой словарь для локальной области
        self.current_scope_level += 1
        print(f"[DEBUG][Scope] Вошли в область уровня {self.current_scope_level}")

    def exit_scope(self):
        """Выходит из текущей локальной области видимости."""
        if self.current_scope_level > 0:
            print(f"[DEBUG][Scope] Вышли из области уровня {self.current_scope_level}")
            self.scopes.pop()
            self.current_scope_level -= 1
        else:
            print("[ERROR][Scope] Попытка выйти из глобальной области!")

    def declare_variable(self, name, kumir_type, is_table=False, dimensions=None):
        """Объявляет переменную в текущей области видимости."""
        current_scope = self.scopes[self.current_scope_level]
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
        print(f"[DEBUG][Declare] Объявлена {'таблица' if is_table else 'переменная'} '{name}' тип {kumir_type} в области {self.current_scope_level}")

    def find_variable(self, name):
        """Ищет переменную, начиная с текущей области и поднимаясь к глобальной."""
        # Добавим проверку, что имя не пустое
        if not name or not isinstance(name, str):
             raise KumirEvalError(f"Некорректное имя переменной для поиска: {name}")

        for i in range(self.current_scope_level, -1, -1):
            scope = self.scopes[i]
            if name in scope:
                return scope[name], scope
        return None, None

    def update_variable(self, name, value):
        """Обновляет значение существующей переменной с проверкой типов."""
        var_info, scope = self.find_variable(name)
        if var_info is None:
            raise KumirExecutionError(f"Переменная '{name}' не найдена для присваивания.")
        
        if var_info['is_table']:
            # TODO: Обработка присваивания таблицам/элементам
            print(f"[WARN][Assign] Присваивание таблице '{name}' пока не реализовано.")
            pass # Пока ничего не делаем
        else:
            target_type = var_info['type']
            try:
                converted_value = self._validate_and_convert_value_for_assignment(value, target_type, name)
                var_info['value'] = converted_value
                print(f"[DEBUG][Assign] Переменной '{name}' присвоено значение: {converted_value} (тип: {type(converted_value).__name__})")
            except AssignmentError as e:
                # Перехватываем ошибку типа и добавляем контекст
                raise AssignmentError(f"Ошибка типа при присваивании переменной '{name}': {e}")
            except Exception as e:
                # Другие возможные ошибки
                raise KumirExecutionError(f"Ошибка при присваивании переменной '{name}': {e}")

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

    def get_full_identifier(self, ctx: KumirParser.CompoundIdentifierContext) -> str:
        """Возвращает полный текст многословного идентификатора."""
        # Собираем тексты всех дочерних токенов IDENTIFIER
        # Контекст compoundIdentifier теперь напрямую содержит список IDENTIFIER
        identifier_parts = [child.getText() for child in ctx.IDENTIFIER()]
        full_name = ' '.join(identifier_parts)
        # print(f"[DEBUG] Собрали идентификатор: '{full_name}' из {len(identifier_parts)} частей") # Убрал дублирующий print
        return full_name

    # --- Вспомогательные методы для вычислений и проверки типов в выражениях ---

    def _check_numeric(self, value, operation_name):
        """Проверяет, является ли значение числом (цел или вещ)."""
        if not isinstance(value, (int, float)):
            raise KumirEvalError(f"Операция '{operation_name}' не применима к нечисловому типу {type(value).__name__}.")
        return value

    def _check_logical(self, value, operation_name):
        """Проверяет, является ли значение логическим."""
        if not isinstance(value, bool):
            raise KumirEvalError(f"Операция '{operation_name}' не применима к нелогическому типу {type(value).__name__}.")
        return value

    def _perform_binary_operation(self, ctx, ops_map, type_check_func=None):
        """Общая логика для выполнения бинарных операций."""
        left_ctx = ctx.getChild(0) # Левый операнд
        right_ctx = ctx.getChild(2) # Правый операнд
        op_token = ctx.getChild(1).symbol # Токен оператора
        
        left_val = self.visit(left_ctx)
        right_val = self.visit(right_ctx)
        
        # Выполняем проверку типов, если функция передана
        if type_check_func:
            left_val = type_check_func(left_val, op_token.text)
            right_val = type_check_func(right_val, op_token.text)
        else: # По умолчанию проверяем на числовой тип (для арифметики и сравнений)
            left_val = self._check_numeric(left_val, op_token.text)
            right_val = self._check_numeric(right_val, op_token.text)
            
        # Получаем функцию операции из словаря
        operation = ops_map.get(op_token.type)
        if not operation:
            raise KumirEvalError(f"Неизвестная или неподдерживаемая бинарная операция: {op_token.text}")

        # Особая обработка для деления, div, mod
        if op_token.type == KumirLexer.DIV: # Обычное деление
            if right_val == 0:
                raise KumirEvalError("Деление на ноль.")
            # Результат всегда вещ
            return float(left_val) / float(right_val)
        elif op_token.type in [KumirLexer.K_DIV, KumirLexer.K_MOD]: # div, mod
            if not isinstance(left_val, int) or not isinstance(right_val, int):
                 raise KumirEvalError(f"Операция '{op_token.text}' применима только к целым числам.")
            if right_val == 0:
                raise KumirEvalError(f"Целочисленное деление или остаток от деления на ноль ('{op_token.text}').")
            # Выполняем операцию (результат цел)
            return operation(left_val, right_val)
            
        # Выполняем остальные операции
        try:
            result = operation(left_val, right_val)
            # Для сравнений результат всегда лог
            # Для арифметики тип результата зависит от операции и операндов
            # (уже обрабатывается стандартными операторами Python)
            return result
        except TypeError as e:
            raise KumirEvalError(f"Ошибка типа при выполнении операции '{op_token.text}': {e}")
        except Exception as e:
             raise KumirEvalError(f"Ошибка при вычислении '{op_token.text}': {e}")

    # --- Переопределение методов visit --- 

    def visitStart(self, ctx: KumirParser.StartContext):
        print("[DEBUG][Visit] Начало программы (start)")
        # Глобальная область уже создана в __init__
        # Обходим все алгоритмы в файле
        result = self.visitChildren(ctx)
        print("[DEBUG][Visit] Конец программы (start)")
        return result

    def visitAlgorithm(self, ctx: KumirParser.AlgorithmContext):
        # Получение имени алгоритма, если оно есть
        alg_name = "<анонимный>"
        if ctx.algHeader().compoundIdentifier(): # Изменено на compoundIdentifier
            alg_name = self.get_full_identifier(ctx.algHeader().compoundIdentifier()) 
        
        print(f"[DEBUG][Visit] Вход в алгоритм '{alg_name}'") # Добавил имя в лог
        self.enter_scope() # Создаем локальную область для алгоритма
        
        # Посещаем объявления и блок команд
        self.visitChildren(ctx) 

        self.exit_scope() # Выходим из локальной области
        print(f"[DEBUG][Visit] Выход из алгоритма '{alg_name}'") # Добавил имя в лог
        return None

    # Обработка объявлений скалярных переменных
    def visitScalarDecl(self, ctx: KumirParser.ScalarDeclContext):
        print(f"[DEBUG][Visit] Обработка scalarDecl")
        type_token = ctx.typeKeyword().start 
        kumir_type = TYPE_MAP.get(type_token.type)
        if not kumir_type:
            raise Exception(f"Неизвестный тип переменной: {type_token.text}")
            
        # Обходим список имен переменных (variableNameList содержит compoundIdentifier)
        for var_id_ctx in ctx.variableNameList().compoundIdentifier(): # Изменено на compoundIdentifier
            var_name = self.get_full_identifier(var_id_ctx)
            self.declare_variable(var_name, kumir_type, is_table=False)
        return None

    # Обработка объявлений таблиц (пока без обработки диапазонов)
    def visitTableDecl(self, ctx: KumirParser.TableDeclContext):
        print(f"[DEBUG][Visit] Обработка tableDecl")
        type_token = ctx.typeKeyword().start
        kumir_type = TYPE_MAP.get(type_token.type)
        if not kumir_type:
            raise Exception(f"Неизвестный тип таблицы: {type_token.text}")
            
        table_name = self.get_full_identifier(ctx.compoundIdentifier()) # Изменено на compoundIdentifier
        
        dimensions = None 
        print(f"  -> Диапазоны для таблицы '{table_name}' пока не вычисляются.")

        self.declare_variable(table_name, kumir_type, is_table=True, dimensions=dimensions)
        return None

    # Обработка узла многословного идентификатора (переименован)
    def visitCompoundIdentifier(self, ctx: KumirParser.CompoundIdentifierContext):
        # Этот метод теперь вызывается для compoundIdentifier.
        # Вернем полный идентификатор, собранный нашим методом.
        return self.get_full_identifier(ctx)

    # Обработка узла переменной
    def visitVariable(self, ctx: KumirParser.VariableContext):
        var_name = self.get_full_identifier(ctx.compoundIdentifier()) # Изменено на compoundIdentifier
        print(f"[DEBUG][Visit] Обращение к переменной/таблице: '{var_name}'")
        
        var_info, _ = self.find_variable(var_name)
        if var_info is None:
            # Добавляем информацию о строке и столбце
            line = ctx.start.line
            column = ctx.start.column
            raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная '{var_name}' не найдена.")

        if ctx.expressionList():
            print(f"  -> Это обращение к таблице '{var_name}'")
            if not var_info['is_table']:
                line = ctx.start.line
                column = ctx.start.column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Попытка доступа по индексу к не табличной переменной '{var_name}'.")
            # TODO: Обработка индексов таблиц
            raise NotImplementedError(f"Обращение к элементу таблицы '{var_name}' пока не реализовано.")
        else:
            if var_info['is_table']:
                 print(f"  -> Это обращение ко всей таблице '{var_name}' (возвращаем словарь)")
                 return var_info['value']
            else:
                print(f"  -> Возвращаем значение переменной '{var_name}': {var_info['value']}")
                return var_info['value']

    # Обработка присваивания
    def visitAssignment(self, ctx: KumirParser.AssignmentContext):
        print("[DEBUG][Visit] Обработка assignment")
        value = self.visit(ctx.expression()) 
        print(f"[DEBUG][Visit] Вычислено значение для присваивания: {value} (тип: {type(value).__name__})")

        if ctx.variable():
            var_ctx = ctx.variable()
            target_name = self.get_full_identifier(var_ctx.compoundIdentifier()) # Изменено на compoundIdentifier
            
            if var_ctx.expressionList():
                print(f"  -> Присваивание элементу таблицы: '{target_name}[...]'")
                raise NotImplementedError(f"Присваивание элементу таблицы '{target_name}' пока не реализовано.")
            else:
                print(f"  -> Присваивание переменной/таблице: '{target_name}'")
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

        elif ctx.K_ZNACH():
            print("  -> Присваивание результату функции (знач)")
            raise NotImplementedError("Присваивание результату функции (знач) пока не реализовано.")
        else:
            line = ctx.start.line
            column = ctx.start.column
            raise KumirExecutionError(f"Строка {line}, столбец {column}: Неизвестный тип цели присваивания.")

        return None 

    # --- Обработка выражений --- 

    def visitExpression(self, ctx:KumirParser.ExpressionContext):
        # Стартовое правило для выражения - просто передаем дальше
        return self.visitChildren(ctx)

    def visitLogicalOrExpr(self, ctx:KumirParser.LogicalOrExprContext):
        if ctx.K_ILI():
            # Теперь используем _perform_binary_operation
            return self._perform_binary_operation(ctx, LOGICAL_OPS, type_check_func=self._check_logical)
        else:
             return self.visit(ctx.logicalAndExpr(0))

    def visitLogicalAndExpr(self, ctx:KumirParser.LogicalAndExprContext):
        if ctx.K_I():
             # Теперь используем _perform_binary_operation
             return self._perform_binary_operation(ctx, LOGICAL_OPS, type_check_func=self._check_logical)
        else:
             return self.visit(ctx.comparisonExpr(0))
        
    def visitComparisonExpr(self, ctx:KumirParser.ComparisonExprContext):
        # В грамматике ComparisonExpr всегда содержит два AddSubExpr и оператор сравнения, если это бинарная операция
        if len(ctx.children) > 1: # Проверяем, есть ли оператор и второй операнд
            # Теперь используем _perform_binary_operation (проверка на числовой тип по умолчанию)
            return self._perform_binary_operation(ctx, COMPARISON_OPS)
        else:
            return self.visit(ctx.addSubExpr(0))
        
    def visitAddSubExpr(self, ctx:KumirParser.AddSubExprContext):
        # В грамматике AddSubExpr содержит нечетное число детей (>1), если есть операции
        if len(ctx.children) > 1: 
            # Теперь используем _perform_binary_operation (проверка на числовой тип по умолчанию)
            # Обрабатываем лево-ассоциативность: вычисляем слева направо
            result = self.visit(ctx.getChild(0)) # Вычисляем самый левый операнд
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
            return self.visit(ctx.mulDivModExpr(0))

    def visitMulDivModExpr(self, ctx:KumirParser.MulDivModExprContext):
        # Аналогично AddSubExpr, обрабатываем лево-ассоциативность
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
                elif op_token.type in [KumirLexer.K_DIV, KumirLexer.K_MOD]:
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
            return self.visit(ctx.powerExpr(0))
        
    def visitPowerExpr(self, ctx:KumirParser.PowerExprContext):
        # Возведение в степень право-ассоциативно, обрабатываем справа налево
        operands_ctx = ctx.unaryExpr()
        if len(operands_ctx) == 1:
            return self.visit(operands_ctx[0]) # Нет операции POW
        
        # Вычисляем самый правый операнд
        right_val = self.visit(operands_ctx[-1])
        
        # Идем справа налево по операциям
        for i in range(len(operands_ctx) - 2, -1, -1):
            left_val = self.visit(operands_ctx[i])
            op_name = '**'
            left_val = self._check_numeric(left_val, op_name)
            right_val = self._check_numeric(right_val, op_name)
            try:
                # print(f"[DEBUG][Eval] {left_val} {op_name} {right_val}")
                result = math.pow(left_val, right_val)
                # print(f"[DEBUG][Eval]  = {result}")
                # В Кумире результат pow может быть целым, если возможно
                if result == int(result):
                    right_val = int(result)
                else:
                    right_val = float(result)
            except ValueError as e: # Например, 0**(-1) 
                 raise KumirEvalError(f"Ошибка при возведении в степень: {e}")
            except OverflowError:
                 raise KumirEvalError(f"Переполнение при возведении в степень")
            except Exception as e:
                 raise KumirEvalError(f"Ошибка при возведении в степень: {e}")
                 
        return right_val # Конечный результат после всех возведений

    def visitUnaryExpr(self, ctx:KumirParser.UnaryExprContext):
       op = None
       if ctx.PLUS(): op = '+'
       if ctx.MINUS(): op = '-'
       if ctx.K_NE(): op = 'не'
       
       operand_value = self.visit(ctx.primaryExpr())
       
       if op == '+':
           return self._check_numeric(operand_value, "унарный плюс")
       elif op == '-':
           return -self._check_numeric(operand_value, "унарный минус")
       elif op == 'не':
           operand_value = self._check_logical(operand_value, "операция НЕ")
           return not operand_value # Выполняем логическое НЕ
       else:
           return operand_value

    def visitPrimaryExpr(self, ctx:KumirParser.PrimaryExprContext):
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.variable():
            return self.visit(ctx.variable())
        elif ctx.functionCall():
            # Получаем имя функции
            func_name = self.get_full_identifier(ctx.functionCall().compoundIdentifier()) # Изменено на compoundIdentifier
            print(f"[WARN][Expr] Вызов функции '{func_name}' пока не реализован")
            # TODO: Реализовать вызов функции (вычисление аргументов, поиск функции, выполнение)
            return None
        elif ctx.expression(): # Скобки
            return self.visit(ctx.expression())
        return None
        
    def visitLiteral(self, ctx:KumirParser.LiteralContext):
        if ctx.NUMBER():
            num_str = ctx.NUMBER().getText()
            if '.' in num_str or 'e' in num_str or 'E' in num_str:
                print(f"  -> Литерал ВЕЩ: {float(num_str)}")
                return float(num_str)
            elif num_str.startswith('$'):
                 print(f"  -> Литерал ЦЕЛ (hex): {int(num_str[1:], 16)}")
                 return int(num_str[1:], 16)
            else:
                print(f"  -> Литерал ЦЕЛ: {int(num_str)}")
                return int(num_str)
        elif ctx.STRING():
            # Убираем кавычки и обрабатываем escape-последовательности (пока просто убираем кавычки)
            str_val = ctx.STRING().getText()[1:-1] 
            # TODO: Правильная обработка escape sequences
            print(f"  -> Литерал ЛИТ: '{str_val}'")
            return str_val
        elif ctx.CHAR():
            # Убираем кавычки и обрабатываем escape-последовательности (пока просто убираем кавычки)
            char_val = ctx.CHAR().getText()[1:-1] 
             # TODO: Правильная обработка escape sequences
            print(f"  -> Литерал СИМ: '{char_val}'")
            return char_val
        elif ctx.K_DA(): 
            print(f"  -> Литерал ЛОГ: True")
            return True
        elif ctx.K_NET(): 
            print(f"  -> Литерал ЛОГ: False")
            return False
        return None
        
    # --- Метод visitForLoop (примерно) ---
    def visitForLoop(self, ctx: KumirParser.ForLoopContext):
        loop_var_name = self.get_full_identifier(ctx.compoundIdentifier()) # Изменено на compoundIdentifier
        start_val = self.visit(ctx.expression(0))
        end_val = self.visit(ctx.expression(1))
        step_val = 1
        if ctx.expression(2): # Если есть шаг
            step_val = self.visit(ctx.expression(2))
        
        print(f"[DEBUG][Visit] Начало цикла ДЛЯ '{loop_var_name}' от {start_val} до {end_val} шаг {step_val}")
        
        # TODO: Правильная проверка типов и реализация цикла
        # - Найти переменную цикла
        # - Проверить тип start/end/step (цел)
        # - Выполнить блок команд нужное количество раз, обновляя переменную цикла
        
        raise NotImplementedError(f"Цикл ДЛЯ для переменной '{loop_var_name}' пока не реализован.")
        

# --- Функция для запуска интерпретации ---

def interpret_kumir(input_string):
    """Парсит и интерпретирует строку с кодом Кумира."""
    from antlr4 import InputStream, CommonTokenStream
    # from .generated.KumirLexer import KumirLexer # Уже импортирован выше
    # from .generated.KumirParser import KumirParser # Уже импортирован выше
    # Импортируем наш Visitor
    # from .interpreter import KumirInterpreterVisitor # Определен выше

    print(f"\n--- Запуск интерпретации для: ---\n{input_string}\n----------------------------------")

    input_stream = InputStream(input_string)
    lexer = KumirLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = KumirParser(stream)

    # Удаляем стандартный консольный listener
    parser.removeErrorListeners()
    # Добавляем наш диагностический listener
    parser.addErrorListener(DiagnosticErrorListener())

    try:
        tree = parser.start() # Получаем дерево разбора
        
        # Проверяем наличие синтаксических ошибок ПОСЛЕ парсинга
        num_syntax_errors = parser.getNumberOfSyntaxErrors()
        if num_syntax_errors > 0:
            print(f"Обнаружено {num_syntax_errors} синтаксических ошибок. Интерпретация прервана.")
            return False # Возвращаем False при ошибках парсинга

        print("Парсинг успешен, начинаем обход дерева...")
        visitor = KumirInterpreterVisitor()
        # Убираем диагностический listener перед обходом (он нужен только для парсинга)
        # parser.removeErrorListeners() 
        # parser.addErrorListener(ErrorListener()) # Возвращаем стандартный, если нужно
        result = visitor.visit(tree)
        print("Обход дерева завершен.")
        return True
    
    except Exception as e:
        import traceback
        print(f"Ошибка во время парсинга или интерпретации: {e}")
        traceback.print_exc() 
        return False


class KumirLanguageInterpreter:
	"""Интерпретатор языка КУМИР с поддержкой вызова алгоритмов и ссылок."""

	# ... (Код __init__ и методов работы со стеком/ссылками остается тем же, что и в предыдущем ответе) ...
	def __init__(self, code, initial_field_state=None):
		"""Инициализирует интерпретатор."""
		self.code = code;
		self.global_env = {};
		self.algorithms = {};
		self.main_algorithm = None
		self.introduction = [];
		self.output = "";
		self.logger = logger;
		self.trace = []
		self.progress_callback = None;
		self.call_stack = []
		default_state = {'width': 7, 'height': 7, 'robotPos': {'x': 0, 'y': 0}, 'walls': set(), 'markers': {},
		                 'coloredCells': set(), 'symbols': {}, 'radiation': {}, 'temperature': {}}
		current_state = initial_field_state if initial_field_state else default_state
		self.width = current_state.get('width', default_state['width']);
		self.height = current_state.get('height', default_state['height'])
		if not isinstance(self.width, int) or self.width < 1: self.logger.warning(
			f"Invalid width: {self.width}. Using default."); self.width = default_state['width']
		if not isinstance(self.height, int) or self.height < 1: self.logger.warning(
			f"Invalid height: {self.height}. Using default."); self.height = default_state['height']
		self.robot = SimulatedRobot(width=self.width, height=self.height,
		                            initial_pos=current_state.get('robotPos', default_state['robotPos']),
		                            initial_walls=set(current_state.get('walls', [])),
		                            initial_markers=dict(current_state.get('markers', {})),
		                            initial_colored_cells=set(current_state.get('coloredCells', [])),
		                            initial_symbols=dict(current_state.get('symbols', {})),
		                            initial_radiation=dict(current_state.get('radiation', {})),
		                            initial_temperature=dict(current_state.get('temperature', {})))
		self.logger.info(
			f"Interpreter initialized. Field: {self.width}x{self.height}. Robot at: {self.robot.robot_pos}")

	def get_current_env_index(self):
		return len(self.call_stack) - 1

	def get_env_by_index(self, index):
		if index == -1:
			return self.global_env
		elif 0 <= index < len(self.call_stack):
			frame = self.call_stack[index];
			if 'env' in frame:
				return frame['env']
			else:
				self.logger.error(
					f"Internal error: 'env' key missing in call stack frame at index {index}"); raise KumirExecutionError(
					f"Внутренняя ошибка: отсутствует окружение в стеке вызовов ({index})")
		else:
			self.logger.error(f"Attempt to access invalid env index: {index}"); raise KumirExecutionError(
				f"Внутренняя ошибка: неверный индекс окружения {index}")

	def _resolve_reference(self, ref_info):
		if not isinstance(ref_info, dict) or ref_info.get('kind') != 'ref': self.logger.error(
			f"Invalid input to _resolve_reference: {ref_info}"); raise KumirExecutionError(
			"Внутренняя ошибка: неверные данные для разрешения ссылки.")
		visited_refs = set();
		current_info = ref_info;
		current_indices = ref_info.get('ref_indices')
		target_var_name = None  # Инициализируем
		target_env_index = None  # Инициализируем
		target_env = None  # Инициализируем
		while isinstance(current_info, dict) and current_info.get('kind') == 'ref':
			target_var_name = current_info.get('target_var_name');
			target_env_index = current_info.get('target_env_index')
			if target_var_name is None or target_env_index is None: raise KumirExecutionError(
				f"Внутренняя ошибка: некорректная структура ссылки для '{ref_info.get('target_var_name', '?')}'")
			ref_id = (target_env_index, target_var_name, current_indices)
			if ref_id in visited_refs: raise KumirExecutionError(
				f"Обнаружена циклическая ссылка на переменную '{target_var_name}'"); visited_refs.add(ref_id)
			try:
				target_env = self.get_env_by_index(target_env_index)
			except KumirExecutionError:
				raise KumirExecutionError(f"Ошибка разрешения ссылки: не найден контекст для '{target_var_name}'")
			if target_var_name not in target_env: raise KumirExecutionError(
				f"Ошибка разрешения ссылки: переменная '{target_var_name}' не найдена")
			next_info = target_env[target_var_name];
			next_ref_indices = next_info.get('ref_indices') if isinstance(next_info, dict) else None
			if next_info.get('kind') == 'ref' and next_ref_indices is not None: raise KumirExecutionError(
				f"Внутренняя ошибка: некорректная цепочка ссылок с индексами."); current_info = next_info
		if not isinstance(current_info, dict) or current_info.get('kind') != 'value': raise KumirExecutionError(
			f"Внутренняя ошибка: ссылка указывает на некорректный объект.")
		# target_env и target_var_name остались от последней итерации
		return target_env, target_var_name, current_indices

	def get_variable_info(self, var_name, env_index=None):
		if env_index is None: env_index = self.get_current_env_index()
		if env_index != -1:
			try:
				current_env = self.get_env_by_index(env_index);
				if var_name in current_env: return current_env[var_name]
			except KumirExecutionError:
				pass
		if var_name in self.global_env: return self.global_env[var_name]
		return None

	def resolve_variable_value(self, var_name, indices=None, env_index=None):
		if env_index is None: env_index = self.get_current_env_index()
		var_info = self.get_variable_info(var_name, env_index)
		if var_info is None: raise KumirExecutionError(f"Переменная '{var_name}' не найдена.")
		if not isinstance(var_info, dict): raise KumirExecutionError(
			f"Внутренняя ошибка: некорректная структура для переменной '{var_name}'.")
		if var_info.get('kind') == 'ref':
			try:
				target_env, target_var_name, ref_indices = self._resolve_reference(var_info)
				var_info_to_use = target_env.get(target_var_name)
				if var_info_to_use is None or var_info_to_use.get('kind') != 'value': raise KumirExecutionError(
					f"Внутренняя ошибка: целевая переменная '{target_var_name}' не найдена или некорректна после разрешения ссылки.")
				final_indices = indices if indices is not None else ref_indices
			except KumirExecutionError as e:
				raise e
		else:
			if indices is not None and var_info.get('kind') == 'ref': raise KumirExecutionError(
				"Внутренняя ошибка: некорректный доступ к элементу ссылки.")
			final_indices = indices;
			var_info_to_use = var_info
		final_var_info = var_info_to_use
		if final_indices is not None:
			if not final_var_info.get('is_table'): raise AssignmentError(
				f"Попытка доступа по индексу к не табличной переменной '{var_name}'.")
			dims = final_var_info.get('dimensions')
			if not dims or len(dims) != len(final_indices): raise AssignmentError(
				f"Неверное количество индексов ({len(final_indices)}) для таблицы '{var_name}', ожидалось {len(dims) if dims else '?'}.")
			for d_idx, idx_val in enumerate(final_indices):
				start, end = dims[d_idx];
				if not (start <= idx_val <= end): raise AssignmentError(
					f"Индекс #{d_idx + 1} ({idx_val}) вне диапазона [{start}:{end}] для '{var_name}'.")
			table_value_dict = final_var_info.get('value')
			if not isinstance(table_value_dict, dict): raise KumirExecutionError(
				f"Таблица '{var_name}' не инициализирована или повреждена.")
			element_value = table_value_dict.get(final_indices)
			if element_value is None: return get_default_value(final_var_info['type'])
			return element_value
		else:
			if final_var_info.get('is_table'):
				table_val = final_var_info.get('value'); return table_val if isinstance(table_val, dict) else {}
			else:
				scalar_val = final_var_info.get('value'); return get_default_value(
					final_var_info['type']) if scalar_val is None and final_var_info.get('type') else scalar_val

	def update_variable_value(self, var_name, value, indices=None, env_index=None):
		if env_index is None: env_index = self.get_current_env_index()
		var_info = self.get_variable_info(var_name, env_index)
		if var_info is None: raise KumirExecutionError(f"Переменная '{var_name}' не найдена для присваивания.")
		if not isinstance(var_info, dict): raise KumirExecutionError(
			f"Внутренняя ошибка: некорректная структура для переменной '{var_name}'.")
		if var_info.get('kind') == 'ref':
			try:
				target_env, target_var_name, ref_indices = self._resolve_reference(var_info)
				var_info_to_update = target_env.get(target_var_name)
				if var_info_to_update is None or var_info_to_update.get('kind') != 'value': raise KumirExecutionError(
					f"Внутренняя ошибка: целевая переменная '{target_var_name}' не найдена или некорректна после разрешения ссылки.")
				final_indices = indices if indices is not None else ref_indices;
				effective_var_name_for_error = target_var_name
			except KumirExecutionError as e:
				raise e
		else:
			if indices is not None and var_info.get('kind') == 'ref': raise KumirExecutionError(
				"Внутренняя ошибка: некорректное обновление элемента ссылки.")
			final_indices = indices;
			var_info_to_update = var_info;
			effective_var_name_for_error = var_name
		target_type = var_info_to_update['type'];
		is_table = var_info_to_update.get('is_table', False)
		try:
			if final_indices is None and is_table:
				if not isinstance(value, dict): raise AssignmentError(
					f"Попытка присвоить не таблицу (не словарь) табличной переменной '{effective_var_name_for_error}'")
				converted_value = value
			elif final_indices is not None and is_table:
				converted_value = _validate_and_convert_value(value, target_type,
				                                              f"{effective_var_name_for_error}[...]")
			elif not is_table:
				converted_value = _validate_and_convert_value(value, target_type, effective_var_name_for_error)
			else:
				raise KumirExecutionError(
					f"Неожиданное состояние при обновлении переменной '{effective_var_name_for_error}'")
		except (AssignmentError, TypeError) as e:
			raise AssignmentError(f"Ошибка типа при присваивании переменной '{effective_var_name_for_error}': {e}")
		if final_indices is not None:
			if not is_table: raise AssignmentError(
				f"Попытка присваивания по индексу не табличной переменной '{effective_var_name_for_error}'.")
			dims = var_info_to_update.get('dimensions')
			if not dims or len(dims) != len(final_indices): raise AssignmentError(
				f"Неверное количество индексов ({len(final_indices)}) для таблицы '{effective_var_name_for_error}', ожидалось {len(dims) if dims else '?'}.")
			for d_idx, idx_val in enumerate(final_indices):
				start, end = dims[d_idx];
				if not (start <= idx_val <= end): raise AssignmentError(
					f"Индекс #{d_idx + 1} ({idx_val}) вне диапазона [{start}:{end}] для '{effective_var_name_for_error}'.")
			if not isinstance(var_info_to_update.get('value'), dict): var_info_to_update['value'] = {}; logger.debug(
				f"Initialized table '{effective_var_name_for_error}' before setting element.")
			var_info_to_update['value'][final_indices] = converted_value;
			logger.debug(
				f"Updated table element {effective_var_name_for_error}{list(final_indices)} = {converted_value}")
		else:
			if is_table:
				var_info_to_update['value'] = converted_value; logger.debug(
					f"Updated entire table '{effective_var_name_for_error}'")
			else:
				var_info_to_update['value'] = converted_value; logger.debug(
					f"Updated scalar variable '{effective_var_name_for_error}' = {converted_value}")

	def push_call_stack(self, algo_name, local_env):
		caller_env_index = self.get_current_env_index()
		self.call_stack.append({'name': algo_name, 'env': local_env, 'caller_env_index': caller_env_index})
		self.logger.debug(
			f"Pushed '{algo_name}' onto call stack. Depth: {len(self.call_stack)}. Caller index: {caller_env_index}")

	def pop_call_stack(self):
		if not self.call_stack: self.logger.error("Attempted to pop from an empty call stack."); return None
		popped = self.call_stack.pop();
		self.logger.debug(f"Popped '{popped.get('name')}' from call stack. Depth: {len(self.call_stack)}");
		return popped

	def _get_env_for_frontend(self, env):
		resolved_env = {}
		if env:
			env_index = -1;
			if env is not self.global_env:
				for idx, frame in enumerate(self.call_stack):
					if frame.get('env') is env: env_index = idx; break
				if env_index == -1 and env: logger.warning(
					"_get_env_for_frontend received an unknown env object. Resolving from current scope."); env_index = self.get_current_env_index()
			for name in env.keys():
				try:
					value = self.resolve_variable_value(name, env_index=env_index); resolved_env[name] = value
				except KumirExecutionError as e:
					logger.warning(f"Skipping variable '{name}' for frontend state due to resolution error: {e}");
					resolved_env[name] = f"<ошибка: {e}>"
				except Exception as e:
					logger.error(f"Unexpected error resolving var '{name}' for frontend state: {e}"); resolved_env[
						name] = "<внутренняя ошибка>"
		return resolved_env

	def get_state(self):
		current_local_env_struct = self.call_stack[-1]['env'].copy() if self.call_stack else {};
		global_env_struct = self.global_env.copy()
		frontend_local_env = self._get_env_for_frontend(current_local_env_struct);
		frontend_global_env = self._get_env_for_frontend(global_env_struct)
		state = {"env": frontend_local_env, "global_env": frontend_global_env, "call_stack_depth": len(self.call_stack),
		         "width": self.width, "height": self.height, "robot": self.robot.robot_pos.copy(),
		         "walls": list(self.robot.walls),
		         "permanentWalls": list(self.robot.permanent_walls), "markers": self.robot.markers.copy(),
		         "coloredCells": list(self.robot.colored_cells),
		         "symbols": self.robot.symbols.copy(), "radiation": self.robot.radiation.copy(),
		         "temperature": self.robot.temperature.copy(), "output": self.output}
		return state

	def _get_resolved_env_for_evaluator(self):
		vars_only = {};
		current_env_index = self.get_current_env_index();
		current_env = self.get_env_by_index(current_env_index)
		env_keys_to_resolve = set(current_env.keys());
		if current_env_index != -1: env_keys_to_resolve.update(self.global_env.keys())
		for var_name in env_keys_to_resolve:
			try:
				value = self.resolve_variable_value(var_name); vars_only[var_name] = value
			except KumirExecutionError as e:
				logger.warning(f"Could not resolve value for variable '{var_name}' for evaluator: {e}. Skipping.")
			except Exception as e:
				logger.error(f"Unexpected error resolving variable '{var_name}' for evaluator: {e}. Skipping.",
				             exc_info=True)
		logger.debug(f"Resolved env vars for evaluator: {vars_only.keys()}")
		return vars_only

	def parse(self):
		# ... (код parse без изменений) ...
		self.logger.info("Starting code parsing...")
		try:
			lines = preprocess_code(self.code)
            if not lines: self.logger.warning(
				"Code is empty after preprocessing."); self.introduction = []; self.main_algorithm = None; self.algorithms = {}; return
			self.introduction, algo_sections = separate_sections(lines)
            self.logger.info(
				f"Separated into {len(self.introduction)} intro lines and {len(algo_sections)} algorithm sections.")
			if not algo_sections:
                self.logger.warning("No 'алг' sections found. Treating entire code as main algorithm body.")
				main_header = "алг main";
				self.main_algorithm = {"header": main_header, "body": self.introduction,
				                       "header_info": parse_algorithm_header(main_header)}
				self.introduction = [];
				self.algorithms = {}
			else:
				self.main_algorithm = algo_sections[0]
				try:
					self.main_algorithm["header_info"] = parse_algorithm_header(self.main_algorithm["header"])
					if not self.main_algorithm["header_info"].get("name"): self.main_algorithm["header_info"][
                        "name"] = "__main__"; self.logger.debug("Assigning default name '__main__' to main algorithm.")
				except ValueError as header_err:
					raise KumirExecutionError(f"Ошибка в заголовке основного алгоритма: {header_err}")
                self.logger.debug(f"Parsed main algorithm header: {self.main_algorithm['header_info']}")
				self.algorithms = {}
				for alg_dict in algo_sections[1:]:
					try:
						header_info = parse_algorithm_header(alg_dict["header"]);
						alg_name = header_info.get("name")
						if alg_name:
                            if alg_name in self.algorithms: self.logger.warning(f"Algorithm '{alg_name}' redefined.")
							self.algorithms[alg_name] = {"header_info": header_info, "body": alg_dict.get("body", [])}
                            self.logger.debug(f"Parsed auxiliary algorithm '{alg_name}'.")
						else:
                            self.logger.warning(
								f"Auxiliary algorithm without name found (header: '{header_info.get('raw', '')}'). Cannot be called.")
					except ValueError as header_err:
                        self.logger.error(
                            f"Error parsing aux algorithm header '{alg_dict.get('header', '')}': {header_err}"); self.logger.warning(
							f"Skipping aux algorithm due to header error.")
			self.logger.info("Code parsing completed successfully.")
		except (SyntaxError, KumirExecutionError) as e:
			self.logger.error(f"Parsing failed: {e}", exc_info=True); raise e
		except Exception as e:
			self.logger.error(f"Unexpected parsing error: {e}", exc_info=True); raise KumirExecutionError(
				f"Ошибка разбора программы: {e}")

	def interpret(self, progress_callback=None):
		"""Полный цикл: парсинг и выполнение кода Кумира."""
		# ... (код interpret без изменений, использует обновленные методы) ...
		self.trace = [];
		self.output = "";
		self.global_env = {};
		self.call_stack = []
		self.progress_callback = progress_callback;
		last_error_index = -1
		try:
			self.parse()
			if self.introduction:
				self.logger.info("Executing introduction (global scope)...")
				intro_indices = list(range(len(self.introduction)))
				execute_lines(self.introduction, self.global_env, self.robot, self, self.trace, self.progress_callback,
				              "introduction", intro_indices)
				self.logger.info("Introduction executed successfully.")
			else:
				self.logger.info("No introduction part to execute.")
			if self.main_algorithm and self.main_algorithm.get("body"):
				main_algo_name = self.main_algorithm.get("header_info", {}).get("name", "__main__")
				self.logger.info(f"Executing main algorithm '{main_algo_name}' (starting in global scope)...")
				main_body_indices = list(range(len(self.main_algorithm["body"])))
				execute_lines(self.main_algorithm["body"], self.global_env, self.robot, self, self.trace,
				              self.progress_callback, main_algo_name, main_body_indices)
				self.logger.info("Main algorithm executed successfully.")
			elif not self.main_algorithm:
                self.logger.warning("No main algorithm found after parsing.")
				if not self.introduction: raise KumirExecutionError("Программа не содержит исполняемого кода.")
			else:
                self.logger.info("Main algorithm body is empty.")
            if self.call_stack: self.logger.error(f"Execution finished but call stack is not empty: {self.call_stack}")
			self.logger.info("Interpretation completed successfully.")
			final_state = self.get_state();
			final_state["output"] = self.output
			return {"trace": self.trace, "finalState": final_state, "success": True}
		except KumirInputRequiredError as e:
			logger.info(f"Execution paused, input required for '{e.var_name}'.");
			self.output += f"Ожидание ввода для '{e.var_name}'...\n"
			state_at_input = self.get_state();
			state_at_input["output"] = self.output
			error_line_index = e.line_index if hasattr(e, 'line_index') else -1;
			last_error_index = error_line_index
			return {"trace": self.trace, "finalState": state_at_input, "success": False, "input_required": True,
			        "var_name": e.var_name, "prompt": e.prompt, "target_type": e.target_type,
			        "message": f"Требуется ввод для переменной '{e.var_name}'", "errorIndex": error_line_index}
		# Теперь обрабатываем все ожидаемые ошибки Кумира здесь
		except (
		KumirExecutionError, DeclarationError, AssignmentError, InputOutputError, KumirEvalError, RobotError) as e:
			error_msg = f"Ошибка выполнения: {str(e)}";
			error_line_index = getattr(e, 'line_index', -1);
			last_error_index = error_line_index
			self.logger.error(error_msg, exc_info=False);
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
                self.logger.error(f"Failed to get state after error: {state_err}");
				current_env_struct = self.call_stack[-1]['env'] if self.call_stack else self.global_env
				state_on_error = {"env": self._get_env_for_frontend(current_env_struct.copy()),
				                  "global_env": self._get_env_for_frontend(self.global_env.copy()), "robot": None,
				                  "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": self.trace, "finalState": state_on_error, "success": False, "message": error_msg,
			        "errorIndex": error_line_index}
		except Exception as e:
			error_msg = f"Критическая внутренняя ошибка: {type(e).__name__} - {e}";
			self.logger.exception(error_msg);
			self.output += f"{error_msg}\n"
			try:
				state_on_error = self.get_state()
			except Exception as state_err:
                self.logger.error(f"Failed to get state after critical error: {state_err}");
				current_env_struct = self.call_stack[-1]['env'] if self.call_stack else self.global_env
				state_on_error = {"env": self._get_env_for_frontend(current_env_struct.copy()),
				                  "global_env": self._get_env_for_frontend(self.global_env.copy()), "robot": None,
				                  "output": self.output}
			state_on_error["output"] = self.output
			return {"trace": self.trace, "finalState": state_on_error, "success": False, "message": error_msg,
			        "errorIndex": last_error_index}

# FILE END: interpreter.py