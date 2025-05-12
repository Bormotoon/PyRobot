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
                               RobotError, KumirSyntaxError, KumirNotImplementedError)
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
from .kumir_datatypes import KumirTableVar # <--- Вот он, наш новый импорт
# Добавляем ExpressionEvaluator
from .expression_evaluator import ExpressionEvaluator 

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
        self.evaluator = ExpressionEvaluator(self) # <--- СОЗДАЕМ ЭКЗЕМПЛЯР EVALUATOR
        # --- DEBUG PRINT --- 
        print(f"[DEBUG][INIT] KumirInterpreterVisitor initialized. Available methods starting with '_handle': {[name for name in dir(self) if callable(getattr(self, name)) and name.startswith('_handle')]}", file=sys.stderr) #stdout -> stderr
        # --- END DEBUG PRINT ---
        self.loop_depth = 0
        self.exit_flags = []

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
        print(f"[DEBUG][VisitVarDecl] Обработка variableDeclaration: {ctx.getText()}", file=sys.stderr)
        type_ctx = ctx.typeSpecifier()
        base_kumir_type = None
        is_table_type = False
        
        if type_ctx.basicType():
            type_token = type_ctx.basicType().start
            base_kumir_type = TYPE_MAP.get(type_token.type)
            if not base_kumir_type:
                raise DeclarationError(f"Строка {type_token.line}: Неизвестный базовый тип: {type_token.text}", type_token.line, type_token.column)
            is_table_type = bool(type_ctx.TABLE_SUFFIX())
            if is_table_type:
                 print(f"[DEBUG][VisitVarDecl] Тип определен как basicType + TABLE_SUFFIX: {base_kumir_type} таб", file=sys.stderr)

        elif type_ctx.arrayType():
            is_table_type = True
            array_type_node = type_ctx.arrayType()
            if array_type_node.INTEGER_ARRAY_TYPE():
                base_kumir_type = INTEGER_TYPE
            elif array_type_node.REAL_ARRAY_TYPE():
                base_kumir_type = FLOAT_TYPE
            elif array_type_node.BOOLEAN_ARRAY_TYPE():
                base_kumir_type = BOOLEAN_TYPE
            elif array_type_node.CHAR_ARRAY_TYPE():
                base_kumir_type = CHAR_TYPE
            elif array_type_node.STRING_ARRAY_TYPE():
                base_kumir_type = STRING_TYPE
            else:
                raise DeclarationError(f"Строка {array_type_node.start.line}: Неизвестный тип таблицы (arrayType): {array_type_node.getText()}", array_type_node.start.line, array_type_node.start.column)
            print(f"[DEBUG][VisitVarDecl] Тип определен как arrayType: {base_kumir_type} (слитно)", file=sys.stderr)
        
        elif type_ctx.actorType():
            # Пока не поддерживаем таблицы исполнителей
            actor_type_text = type_ctx.actorType().getText()
            raise DeclarationError(f"Строка {type_ctx.start.line}: Таблицы для типов исполнителей ('{actor_type_text}') пока не поддерживаются.", type_ctx.start.line, type_ctx.start.column)
        else:
            raise DeclarationError(f"Строка {type_ctx.start.line}: Не удалось определить тип переменной: {type_ctx.getText()}", type_ctx.start.line, type_ctx.start.column)

        if not base_kumir_type: # Дополнительная проверка, если логика выше не установила тип
             raise DeclarationError(f"Строка {type_ctx.start.line}: Не удалось определить базовый тип для: {type_ctx.getText()}", type_ctx.start.line, type_ctx.start.column)

        current_scope = self.scopes[-1]

        for var_decl_item_ctx in ctx.variableList().variableDeclarationItem():
            var_name = var_decl_item_ctx.ID().getText()
            print(f"[DEBUG][VisitVarDecl] Обработка переменной/таблицы: {var_name}", file=sys.stderr)

            if var_name in current_scope:
                raise DeclarationError(f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Переменная '{var_name}' уже объявлена в этой области.", var_decl_item_ctx.ID().getSymbol().line, var_decl_item_ctx.ID().getSymbol().column)

            if is_table_type:
                if not var_decl_item_ctx.LBRACK(): # Проверяем наличие квадратных скобок
                    raise DeclarationError(f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Для таблицы '{var_name}' ({base_kumir_type} таб) должны быть указаны границы в квадратных скобках.", var_decl_item_ctx.ID().getSymbol().line, var_decl_item_ctx.ID().getSymbol().column)
                
                dimension_bounds_list = []
                # В KumirParser.g4 variableDeclarationItem -> (LBRACK arrayBounds (COMMA arrayBounds)* RBRACK)?
                # arrayBounds существует как метод у var_decl_item_ctx и возвращает список, если они есть.
                array_bounds_nodes = var_decl_item_ctx.arrayBounds() 
                if not array_bounds_nodes: 
                     raise DeclarationError(f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Отсутствуют определения границ для таблицы '{var_name}'.", var_decl_item_ctx.LBRACK().getSymbol().line, var_decl_item_ctx.LBRACK().getSymbol().column)

                for i, bounds_ctx in enumerate(array_bounds_nodes): # bounds_ctx это ArrayBoundsContext
                    print(f"[DEBUG][VisitVarDecl] Обработка границ измерения {i+1} для '{var_name}': {bounds_ctx.getText()}", file=sys.stderr)
                    # У ArrayBoundsContext есть два expression() и COLON()
                    if not (bounds_ctx.expression(0) and bounds_ctx.expression(1) and bounds_ctx.COLON()):
                        raise DeclarationError(f"Строка {bounds_ctx.start.line}: Некорректный формат границ для измерения {i+1} таблицы '{var_name}'. Ожидается [нижняя:верхняя].", bounds_ctx.start.line, bounds_ctx.start.column)
                    
                    min_idx_val = self.evaluator.visitExpression(bounds_ctx.expression(0))
                    max_idx_val = self.evaluator.visitExpression(bounds_ctx.expression(1))

                    min_idx = min_idx_val # Убрали self._get_value()
                    max_idx = max_idx_val # Убрали self._get_value()

                    if not isinstance(min_idx, int) or not isinstance(max_idx, int):
                        raise KumirEvalError(f"Строка {bounds_ctx.expression(0).start.line}: Нижняя граница измерения {i+1} для таблицы '{var_name}' должна быть целым числом, получено: {min_idx} (тип: {type(min_idx).__name__}).", bounds_ctx.expression(0).start.line, bounds_ctx.expression(0).start.column)
                    if not isinstance(max_idx, int):
                        raise KumirEvalError(f"Строка {bounds_ctx.expression(1).start.line}: Верхняя граница измерения {i+1} для таблицы '{var_name}' должна быть целым числом, получено: {max_idx} (тип: {type(max_idx).__name__}).", bounds_ctx.expression(1).start.line, bounds_ctx.expression(1).start.column)
                    
                    dimension_bounds_list.append((min_idx, max_idx))
                
                if not dimension_bounds_list:
                     raise DeclarationError(f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Не удалось определить границы для таблицы '{var_name}'.", var_decl_item_ctx.ID().getSymbol().line, var_decl_item_ctx.ID().getSymbol().column)

                try:
                    # Передаем var_decl_item_ctx как контекст объявления для KumirTableVar
                    table_var = KumirTableVar(base_kumir_type, dimension_bounds_list, var_decl_item_ctx) 
                    current_scope[var_name] = {'type': base_kumir_type, 'value': table_var, 'is_table': True, 'dimensions_info': dimension_bounds_list}
                    print(f"[DEBUG][VisitVarDecl] Создана таблица '{var_name}' тип {base_kumir_type}, границы: {dimension_bounds_list}", file=sys.stderr)
                except KumirEvalError as e: 
                    raise KumirEvalError(f"Ошибка при объявлении таблицы '{var_name}': {e.args[0]}", var_decl_item_ctx.start.line, var_decl_item_ctx.start.column)

                if var_decl_item_ctx.expression(): 
                    raise NotImplementedError(f"Строка {var_decl_item_ctx.expression().start.line}: Инициализация таблиц при объявлении ('{var_name} = ...') пока не поддерживается.", var_decl_item_ctx.expression().start.line, var_decl_item_ctx.expression().start.column)

            else: # Обычная (скалярная) переменная
                if var_decl_item_ctx.LBRACK(): 
                    raise DeclarationError(f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Скалярная переменная '{var_name}' (тип {base_kumir_type}) не может иметь указания границ массива.", var_decl_item_ctx.LBRACK().getSymbol().line, var_decl_item_ctx.LBRACK().getSymbol().column)

                default_value = get_default_value(base_kumir_type)
                current_scope[var_name] = {'type': base_kumir_type, 'value': default_value, 'is_table': False, 'dimensions_info': None}
                print(f"[DEBUG][VisitVarDecl] Объявлена переменная '{var_name}' тип {base_kumir_type}, значение по умолчанию: {default_value}", file=sys.stderr)
                
                if var_decl_item_ctx.expression():
                    value_to_assign = self.evaluator.visitExpression(var_decl_item_ctx.expression())
                    # value_to_assign = self._get_value(value_to_assign)  # УДАЛЕНО как избыточное

                    try:
                        validated_value = self._validate_and_convert_value_for_assignment(value_to_assign, base_kumir_type, var_name)
                        current_scope[var_name]['value'] = validated_value
                        print(f"[DEBUG][VisitVarDecl] Переменной '{var_name}' присвоено значение при инициализации: {validated_value}", file=sys.stderr)
                    except (AssignmentError, DeclarationError, KumirEvalError) as e:
                        line = var_decl_item_ctx.expression().start.line
                        column = var_decl_item_ctx.expression().start.column
                        raise type(e)(f"Строка {line}, столбец {column}: Ошибка при инициализации переменной '{var_name}': {e.args[0]}", line, column) from e
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
        print(f"[DEBUG][visitAssignmentStatement] Called for ctx: {ctx.getText()}", file=sys.stderr)
        
        l_value_ctx = ctx.lvalue() # Получаем lvalue
        expression_ctx = ctx.expression() # Получаем правую часть (выражение)

        if not expression_ctx:
            # Это может быть случай, когда assignmentStatement является просто expression (например, вызов процедуры)
            # В КуМире это не должно приводить к ошибке здесь, такие statement обрабатываются как expressionStatement
            # Но если у нас есть ASSIGN, то expression должен быть.
            if ctx.ASSIGN(): # Если есть оператор присваивания, но нет выражения
                raise KumirSyntaxError("Отсутствует выражение после оператора присваивания ':='", ctx.ASSIGN().symbol.line, ctx.ASSIGN().symbol.column)
            # Если это просто expression (например, вызов процедуры без присваивания), то lvalue не будет.
            # Такая ситуация обрабатывается в visitStatement, который решает, вызывать visitAssignmentStatement или visitProcedureCallStatement.
            # Если мы здесь и нет lvalue, то это ошибка в логике visitStatement или грамматике.
            # Однако, грамматика `assignmentStatement: lvalue ASSIGN expression | expression;`.
            # Если это вторая альтернатива (просто expression), то lvalue() вернет None.
            if not l_value_ctx and not ctx.ASSIGN():
                print(f"[DEBUG][visitAssignmentStatement] Interpreting as expression statement: {ctx.getText()}", file=sys.stderr)
                # Это вызов процедуры или функция, значение которой не используется
                # Просто вычисляем выражение (это вызовет нужные visit методы для процедуры)
                self.evaluator.visitExpression(ctx.expression(0)) # expression(0), т.к. это единственное выражение в этой альтернативе
                return None 
            # Если мы здесь, что-то пошло не так, должен быть lvalue или это не assignment
            raise KumirSyntaxError(f"Некорректный оператор присваивания: {ctx.getText()}", ctx.start.line, ctx.start.column)

        value_to_assign = self.evaluator.visitExpression(expression_ctx)

        is_return_value_assignment = False
        if l_value_ctx and l_value_ctx.RETURN_VALUE():
            is_return_value_assignment = True
        
        if is_return_value_assignment:
            # Присваивание 'знач'
            if not self.current_algorithm_is_function:
                raise KumirEvalError("Присваивание 'знач' допустимо только внутри функции", l_value_ctx.RETURN_VALUE().symbol.line, l_value_ctx.RETURN_VALUE().symbol.column)
            
            # Проверяем тип возвращаемого значения (если он был объявлен для функции)
            # self.return_value должен быть словарем с ключом 'value' и опционально 'type'
            if self.return_value is None: # Должно быть инициализировано в visitAlgorithmDefinition
                 self.return_value = {} 

            # TODO: Проверка типа присваиваемого значения с ожидаемым типом функции, если он есть
            # func_return_type_name = self.procedures[self.current_algorithm_name].get('return_type_name')
            # if func_return_type_name:
            #     value_to_assign = self._validate_and_convert_value_for_assignment(value_to_assign, func_return_type_name, "знач")

            self.return_value['value'] = value_to_assign
            print(f"[DEBUG][visitAssignmentStatement] Присвоено ЗНАЧ = {value_to_assign}", file=sys.stderr)
        else:
            # Присваивание переменной или элементу массива
            if not l_value_ctx or not l_value_ctx.qualifiedIdentifier():
                 raise KumirSyntaxError("Отсутствует имя переменной в операторе присваивания", ctx.start.line, ctx.start.column)

            var_name = l_value_ctx.qualifiedIdentifier().getText()
            var_info, var_scope = self.find_variable(var_name) 

            if var_info is None:
                raise KumirEvalError(f"Переменная '{var_name}' не объявлена", l_value_ctx.qualifiedIdentifier().start.line, l_value_ctx.qualifiedIdentifier().start.column)

            kumir_target_type = var_info.get('kumir_type', 'неизвестен')
            is_table = var_info.get('is_table', False)

            if l_value_ctx.LBRACK(): # Это присваивание элементу массива/таблицы
                if not is_table:
                    raise KumirEvalError(f"Переменная '{var_name}' не является таблицей, но используется с индексами", l_value_ctx.qualifiedIdentifier().start.line)
                
                if not var_info.get('value') or not isinstance(var_info['value'], KumirTableVar):
                    raise KumirEvalError(f"Таблица '{var_name}' не инициализирована правильно (отсутствует KumirTableVar)", l_value_ctx.start.line)
                
                kumir_table_var = var_info['value']
                table_element_type = kumir_table_var.base_kumir_type_name # ИСПРАВЛЕНО

                # Вычисляем индексы
                index_ctx_list = l_value_ctx.indexList().expression()
                indices = []
                for i_ctx in index_ctx_list:
                    idx_val = self.evaluator.visitExpression(i_ctx)
                    if not isinstance(idx_val, int):
                        raise KumirEvalError(f"Индекс таблицы '{var_name}' должен быть целым числом, получено: {idx_val}", i_ctx.start.line)
                    indices.append(idx_val)
                
                # Проверяем количество индексов
                if len(indices) != len(var_info.get('dimensions_info', [])):
                    raise KumirEvalError(f"Неверное количество индексов для таблицы '{var_name}'. Ожидалось {len(var_info.get('dimensions_info', []))}, получено {len(indices)}.", l_value_ctx.start.line)

                # Преобразуем значение к типу элемента таблицы
                value_to_set_in_table = self._validate_and_convert_value_for_assignment(value_to_assign, table_element_type, f"{var_name}[{','.join(map(str, indices))}]")
                
                # Присваиваем значение элементу таблицы
                try:
                    kumir_table_var.set_value(tuple(indices), value_to_set_in_table, l_value_ctx) # ИЗМЕНЕНО: добавлен l_value_ctx и tuple() для indices
                    print(f"[DEBUG][visitAssignmentStatement] Присвоено {var_name}[{','.join(map(str, indices))}] = {value_to_set_in_table}", file=sys.stderr)
                except IndexError as e:
                    raise KumirEvalError(f"Индекс выходит за границы таблицы '{var_name}': {e}", l_value_ctx.start.line)
                except TypeError as e: # От KumirTableVar, если что-то не так с индексами/значением
                    raise KumirEvalError(f"Ошибка присваивания элементу таблицы '{var_name}': {e}", l_value_ctx.start.line)

            else: # Присваивание простой переменной
                if is_table:
                     raise KumirEvalError(f"Попытка присвоить значение всей таблице '{var_name}' без указания индексов. Такое присваивание не поддерживается.", l_value_ctx.start.line)

                # Преобразуем значение к типу переменной
                validated_value = self._validate_and_convert_value_for_assignment(value_to_assign, kumir_target_type, var_name)
                var_info['value'] = validated_value
                print(f"[DEBUG][visitAssignmentStatement] Присвоено {var_name} = {validated_value} (тип {kumir_target_type})", file=sys.stderr)
        return None

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
                
                # printed_non_literal = False # <--- УДАЛЕНО

                for i, arg_ctx in enumerate(args):
                    arg_text_debug = arg_ctx.getText()
                    if self.debug: print(f"[DEBUG][OUTPUT] Обработка аргумента {i}: {arg_text_debug}", file=sys.stderr)
                    try:
                        if arg_ctx.NEWLINE_CONST():
                            if self.debug: print(f"[DEBUG][OUTPUT] Печать НС", file=sys.stderr)
                            sys.stdout.write('\n')
                            # printed_non_literal = True # <--- УДАЛЕНО
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
                                value = self.evaluator.visitExpression(expr_ctx) # ИЗМЕНЕНИЕ 1
                                if self.debug: print(f"[DEBUG][OUTPUT][VISIT_STATEMENT] После вызова self.visit, value = {repr(value)} (type: {type(value).__name__}) для выражения: {expr_ctx.getText()}", file=sys.stderr)
                                value = self._get_value(value) if hasattr(self, '_get_value') else value # Добавлено для консистентности
                                if self.debug: print(f"[DEBUG][OUTPUT] Аргумент {i}: Вычислено value={repr(value)} ({type(value).__name__})", file=sys.stderr)
                                
                                if value is None:
                                    expr_text = expr_ctx.getText() if hasattr(expr_ctx, 'getText') else '[Unknown Expression]'
                                    line = expr_ctx.start.line
                                    column = expr_ctx.start.column
                                    raise KumirEvalError(f"Строка {line}, столбец {column}: Попытка вывести неинициализированное значение (выражение: {expr_text})")

                                formatted_value = self._format_output_value(value, arg_ctx)
                                # printed_non_literal = True # <--- УДАЛЕНО
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
                # ends_with_newline_const = args and args[-1].NEWLINE_CONST() # <--- УДАЛЕНО
                # if printed_non_literal and not ends_with_newline_const: # <--- УДАЛЕНО
                #      sys.stdout.write('\n') # <--- УДАЛЕНО
                # ------------------------------------------- # <--- УДАЛЕНО
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
            self.evaluator.visitExpression(ctx.expression()) # ИЗМЕНЕНИЕ 2. Выполняем, игнорируем результат
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
            raw_arg_value = self.evaluator.visitExpression(expr_ctx) # ИЗМЕНЕНИЕ
            if self.debug: print(f"[DEBUG][ArgList Proc] For {func_name_debug}, Arg {i} ({expr_ctx.getText()}): evaluated to {repr(raw_arg_value)} ({type(raw_arg_value).__name__})", file=sys.stderr)
            args.append(raw_arg_value)
        if self.debug: print(f"[Exit] visitArgumentList for {func_name_debug}({ctx.getText()}) -> returns {repr(args)}", file=sys.stderr)
        return args

    def visitPrimaryExpression(self, ctx:KumirParser.PrimaryExpressionContext):
        # print(f"[DEBUG][visitPrimaryExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        # if ctx.literal():
        #     result = self.visit(ctx.literal())
        return None 
    # --- Конец visitLiteral (УДАЛЕН, т.к. в ExpressionEvaluator) ---

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
    # --- Конец visitLiteral (УДАЛЕН, т.к. в ExpressionEvaluator) ---

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        """Обработка цикла"""
        loop_spec = ctx.loopSpecifier() # Может быть None
        end_loop_cond = ctx.endLoopCondition() # Может быть None
        statement_sequence_ctx = ctx.statementSequence()

        # Устанавливаем флаг, что мы внутри цикла (для оператора ВЫХОД)
        self.loop_depth += 1
        self.exit_flags.append(False)

        try:
            if loop_spec:
                # --- Циклы со спецификатором: ДЛЯ, ПОКА, N РАЗ ---
                if loop_spec.FOR():
                    var_name_node = loop_spec.ID()
                    if not var_name_node:
                        raise KumirSyntaxError("Отсутствует имя переменной в цикле ДЛЯ", loop_spec.FOR().symbol.line, loop_spec.FOR().symbol.column)
                    var_name = var_name_node.getText()
                    self.enter_scope() 
                    print(f"[DEBUG][Scope] Вошли в локальную область для цикла ДЛЯ (переменная '{var_name}')", file=sys.stderr)
                    try:
                        # Вычисляем начальное, конечное значения и шаг
                        from_expr_ctx = loop_spec.expression(0)
                        to_expr_ctx = loop_spec.expression(1)
                        step_expr_ctx = loop_spec.expression(2) if len(loop_spec.expression()) > 2 and loop_spec.STEP() else None

                        start_value = self.evaluator.visitExpression(from_expr_ctx)
                        end_value = self.evaluator.visitExpression(to_expr_ctx)
                        
                        if not isinstance(start_value, int) or not isinstance(end_value, int):
                            raise KumirEvalError("Границы цикла ДЛЯ должны быть целыми числами", from_expr_ctx.start.line)

                        step_value = 1
                        if loop_spec.STEP() and step_expr_ctx:
                            step_val_eval = self.evaluator.visitExpression(step_expr_ctx)
                            if not isinstance(step_val_eval, int):
                                raise KumirEvalError("Шаг в цикле ДЛЯ должен быть целым числом", step_expr_ctx.start.line)
                            step_value = step_val_eval
                        elif start_value > end_value: 
                            step_value = -1
                        
                        if step_value == 0:
                            raise KumirEvalError("Шаг в цикле ДЛЯ не может быть равен нулю", loop_spec.STEP().symbol.line if loop_spec.STEP() else from_expr_ctx.start.line)

                        self.scopes[-1][var_name] = {'type': INTEGER_TYPE, 'value': start_value, 'is_table': False, 'kumir_type': 'цел'} 
                        print(f"[DEBUG][Loop] Цикл ДЛЯ '{var_name}' от {start_value} до {end_value} шаг {step_value}", file=sys.stderr)

                        current_val = start_value
                        
                        loop_executed_once = False
                        while (step_value > 0 and current_val <= end_value) or \
                              (step_value < 0 and current_val >= end_value):
                            self.scopes[-1][var_name]['value'] = current_val
                            loop_executed_once = True
                            self.visit(statement_sequence_ctx)
                            if self.exit_flags[-1]: 
                                print(f"[DEBUG][Loop] Обнаружен ВЫХОД из цикла ДЛЯ", file=sys.stderr)
                                break
                            current_val += step_value
                    finally:
                        self.exit_scope() 
                        print(f"[DEBUG][Scope] Вышли из локальной области цикла ДЛЯ (переменная '{var_name}')", file=sys.stderr)
                elif loop_spec.WHILE():
                    condition_ctx = loop_spec.expression(0)
                    print(f"[DEBUG][Loop] Цикл ПОКА, условие: {condition_ctx.getText()}", file=sys.stderr)
                    condition_value = self.evaluator.visitExpression(condition_ctx)
                    if not isinstance(condition_value, bool):
                        raise KumirEvalError("Условие в цикле ПОКА должно быть логического типа", condition_ctx.start.line)
                    while condition_value:
                        self.visit(statement_sequence_ctx)
                        if self.exit_flags[-1]:
                            print(f"[DEBUG][Loop] Обнаружен ВЫХОД из цикла ПОКА", file=sys.stderr)
                            break
                        condition_value = self.evaluator.visitExpression(condition_ctx)
                        if not isinstance(condition_value, bool):
                            raise KumirEvalError("Условие в цикле ПОКА должно быть логического типа", condition_ctx.start.line)
                elif loop_spec.TIMES(): 
                    count_expr_ctx = loop_spec.expression(0)
                    print(f"[DEBUG][Loop] Цикл N РАЗ, выражение для кол-ва: {count_expr_ctx.getText()}", file=sys.stderr)
                    count_value = self.evaluator.visitExpression(count_expr_ctx)
                    if not isinstance(count_value, int):
                        raise KumirEvalError("Количество повторений в цикле ...РАЗ должно быть целым числом", count_expr_ctx.start.line)
                    if count_value < 0:
                        print(f"[DEBUG][Loop] Цикл N РАЗ: N={count_value} < 0, не будет выполнен.", file=sys.stderr)
                        count_value = 0
                    for _ in range(count_value):
                        self.visit(statement_sequence_ctx)
                        if self.exit_flags[-1]: 
                            print(f"[DEBUG][Loop] Обнаружен ВЫХОД из цикла N РАЗ", file=sys.stderr)
                            break
                else:
                    raise KumirNotImplementedError(f"Неизвестный или неподдерживаемый тип loopSpecifier: {loop_spec.getText() if loop_spec else 'None'}", ctx.start.line)
            elif end_loop_cond:
                condition_ctx = end_loop_cond.expression()
                print(f"[DEBUG][Loop] Цикл ДО (нц...кц при), условие выхода: {condition_ctx.getText()}", file=sys.stderr)
                while True:
                    self.visit(statement_sequence_ctx)
                    if self.exit_flags[-1]: 
                        print(f"[DEBUG][Loop] Обнаружен ВЫХОД из цикла ДО", file=sys.stderr)
                        break
                    condition_value = self.evaluator.visitExpression(condition_ctx)
                    if not isinstance(condition_value, bool):
                        raise KumirEvalError("Условие в 'кц при' (цикл ДО) должно быть логического типа", condition_ctx.start.line)
                    if condition_value:
                        break
            else:
                print(f"[DEBUG][Loop] Простой цикл НЦ...КЦ (без явного условия)", file=sys.stderr)
                while True:
                    self.visit(statement_sequence_ctx)
                    if self.exit_flags[-1]:
                        print(f"[DEBUG][Loop] Обнаружен ВЫХОД из простого цикла НЦ...КЦ", file=sys.stderr)
                        break
        finally:
            if self.exit_flags:
                self.exit_flags.pop()
            self.loop_depth -= 1

        return None

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext):
        # ... existing code ...
        pass

    def visitIfStatement(self, ctx:KumirParser.IfStatementContext):
        """Обработка условного оператора."""
        print("[DEBUG][visitIfStatement] Called for ctx: {ctx.getText()}", file=sys.stderr)
        
        # Вычисляем условие
        condition_ctx = ctx.expression()
        try:
            condition_value = self.evaluator.visitExpression(condition_ctx) # ИЗМЕНЕНО
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
            if ctx.statementSequence(): # В грамматике ifStatement -> expression THEN statementSequence (ELSE statementSequence)? ENDIF
                                      # поэтому первый statementSequence это ветка "то"
                return self.visit(ctx.statementSequence(0))
        else:
            # Ветвь "иначе", если есть
            if len(ctx.statementSequence()) > 1: # Если есть второй statementSequence, это "иначе"
                return self.visit(ctx.statementSequence(1))
                
        return None

    def _handle_input(self, arg_ctx):
        """Вспомогательный метод для обработки ввода значения."""
        # Получаем контекст expression
        if arg_ctx.expression():
            return self.evaluator.visitExpression(arg_ctx.expression())
        elif arg_ctx.STRING():
            return arg_ctx.STRING().getText()
        elif arg_ctx.INTEGER():
            return int(arg_ctx.INTEGER().getText())
        elif arg_ctx.REAL():
            return float(arg_ctx.REAL().getText().replace(',', '.'))
        elif arg_ctx.BOOLEAN():
            return arg_ctx.BOOLEAN().getText().lower() == 'true'
        elif arg_ctx.CHAR_LITERAL():
            return arg_ctx.CHAR_LITERAL().getText()
        else:
            raise KumirEvalError(f"Неизвестный формат ввода для переменной: {arg_ctx.getText()}")

    def push_scope(self):
        """Алиас для enter_scope (для совместимости)."""
        self.enter_scope()

    def pop_scope(self):
        """Алиас для exit_scope (для совместимости)."""
        self.exit_scope()

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