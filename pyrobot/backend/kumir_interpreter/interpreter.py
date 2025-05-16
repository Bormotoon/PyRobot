# FILE START: interpreter.py
import logging
import copy
import math  # Добавлено для pow
import operator  # Добавлено для операций
# Добавляем импорт TerminalNode
from antlr4.tree.Tree import TerminalNode
from antlr4.tree.Tree import TerminalNodeImpl # ДОБАВЛЯЮ ЭТОТ ИМПОРТ

# Импортируем все исключения из одного места
from .kumir_exceptions import (KumirExecutionError, DeclarationError, AssignmentError,
                               InputOutputError, KumirInputRequiredError, KumirEvalError,
                                RobotError, KumirSyntaxError, KumirNotImplementedError,
                                KumirNameError, KumirTypeError, KumirIndexError, KumirInputError)


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
from .generated.KumirLexer import KumirLexer  # Импортируем лексер для имен токенов
# Добавляем ErrorListener
from antlr4.error.ErrorListener import ErrorListener
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import sys
from typing import Any, Tuple, Optional, Dict
import random  # <-- Добавляем импорт random
import antlr4
from .kumir_datatypes import KumirTableVar  # <--- Вот он, наш новый импорт
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
    if kumir_type == 'лог': return False  # В Кумире логические по умолчанию могут быть не инициализированы, но False безопаснее
    if kumir_type == 'сим': return ''  # Или может быть ошибка?
    if kumir_type == 'лит': return ""
    return None  # Для таблиц или неизвестных типов


class KumirInterpreterVisitor(KumirParserVisitor):
    """Обходит дерево разбора Кумира и выполняет семантические действия."""

    # --- Словарь для встроенных функций/процедур ---
    # Используем строки для имен ключей, чтобы избежать путаницы с регистром
    BUILTIN_FUNCTIONS = {
        'rand': {
            0: lambda: random.random(),  # rand()
            2: lambda a, b: random.uniform(a, b)  # rand(A, B)
        },
        'irand': {
            0: lambda: random.randint(0, МАКСЦЕЛ),  # irand()
            1: lambda n: random.randint(0, n - 1) if n > 0 else 0,  # irand(N)
            2: lambda a, b: random.randint(min(a, b), max(a, b))  # irand(A, B) - Кумир требует min/max
        },
        'printbin': {  # Ключ теперь в нижнем регистре
            1: lambda n: print(format(n, '08b'), end='')  # Возвращаем на print, который будет использовать sys.stdout
        },
        'div': {
            2: lambda a, b: int(a) // int(b) if b != 0 else (_ for _ in ()).throw(
                KumirEvalError("Целочисленное деление на ноль"))
        },
        'mod': {
            2: lambda a, b: int(a) % int(b) if b != 0 else (_ for _ in ()).throw(
                KumirEvalError("Остаток от деления на ноль"))
        }
    }

    def __init__(self, output_stream=None, input_stream=None, error_stream=None):
        super().__init__()
        self.scopes = [{}]  # Глобальная область видимости
        self.procedures = {} # Словарь для хранения узлов AST процедур и функций
        self.return_value = {} # Для хранения значения, возвращаемого через ЗНАЧ
        self.current_procedure_args = None # Для временного хранения аргументов при вызове
        self.exit_flags = []  # Флаг для выхода из циклов (один на уровень вложенности)
        self.loop_depth = 0   # Глубина вложенности циклов для ВЫХОД
        self.debug = True  # Флаг для отладочного вывода (ВКЛЮЧЕН)
        self.echo_input = True # <--- ИЗМЕНЕНО: Включаем эхо ввода обратно
        self.logger = logging.getLogger(__name__)  # <--- ДОБАВЛЕНО
        self.evaluator = ExpressionEvaluator(self)  # <--- СОЗДАЕМ ЭКЗЕМПЛЯР EVALUATOR
        # --- DEBUG PRINT ---
        print(
            f"[DEBUG][INIT] KumirInterpreterVisitor initialized. Available methods starting with '_handle': {[name for name in dir(self) if callable(getattr(self, name)) and name.startswith('_handle')]}",
            file=sys.stderr)  # stdout -> stderr
        # --- END DEBUG PRINT ---

    # --- Управление областями видимости и символами ---

    def enter_scope(self):
        """Входит в новую локальную область видимости."""
        self.scopes.append({})  # Добавляем новый пустой словарь для локальной области
        print(f"[DEBUG][Scope] Вошли в область уровня {len(self.scopes)}", file=sys.stderr)

    def exit_scope(self):
        """Выходит из текущей локальной области видимости."""
        if len(self.scopes) > 1:
            print(f"[DEBUG][Scope] Вышли из области уровня {len(self.scopes) - 1}", file=sys.stderr)
            self.scopes.pop()
        else:  # <--- 8 пробелов
            print("[ERROR][Scope] Попытка выйти из глобальной области!", file=sys.stderr)

    def declare_variable(self, name, kumir_type, is_table=False, dimensions=None):
        """Объявляет переменную в текущей области видимости."""
        current_scope = self.scopes[-1]
        if name in current_scope:
            # TODO: Использовать KumirExecutionError или DeclarationError (используем DeclarationError)
            raise DeclarationError(f"Переменная '{name}' уже объявлена в этой области видимости.", -1, -1) # Указываем line/col как -1

        default_value = {} if is_table else get_default_value(kumir_type)
        current_scope[name] = {
            'type': kumir_type,
            'value': default_value,
            'is_table': is_table,
            'dimensions': dimensions if is_table else None
        }
        print(
            f"[DEBUG][Declare] Объявлена {'таблица' if is_table else 'переменная'} '{name}' тип {kumir_type} в области {len(self.scopes) - 1}",
            file=sys.stderr)  # stdout -> stderr

    def _get_type_info_from_specifier(self, type_ctx: KumirParser.TypeSpecifierContext,
                                      error_source_line: Optional[int] = None,
                                      error_source_col: Optional[int] = None) -> Tuple[str, bool]:
        """
        Извлекает базовое имя типа (строку) и флаг, является ли тип таблицей (bool),
        из узла typeSpecifier.
        `error_source_line` и `error_source_col` используются для более точного указания
        места ошибки, если они предоставлены. Иначе используются данные из type_ctx.
        """
        base_kumir_type: Optional[str] = None
        is_table_type: bool = False

        # Определяем источник для сообщения об ошибке
        err_line = error_source_line if error_source_line is not None else (
            type_ctx.start.line if type_ctx and type_ctx.start else -1)
        err_col = error_source_col if error_source_col is not None else (
            type_ctx.start.column if type_ctx and type_ctx.start else -1)

        if not type_ctx:
            raise DeclarationError("Контекст типа (typeSpecifier) отсутствует.", err_line, err_col)

        if type_ctx.basicType():
            type_token = type_ctx.basicType().start
            base_kumir_type = TYPE_MAP.get(type_token.type)
            if not base_kumir_type:
                raise DeclarationError(f"Неизвестный или неподдерживаемый базовый тип: {type_token.text}",
                                       type_token.line, type_token.column)
            is_table_type = bool(type_ctx.TABLE_SUFFIX())  # Проверяем наличие 'таб'

        elif type_ctx.arrayType():
            is_table_type = True  # arrayType всегда означает таблицу
            array_type_node = type_ctx.arrayType()
            # Определяем базовый тип таблицы из конкретного токена массива
            # Эти *_ARRAY_TYPE токены обычно представляют "ТИП таб" как единое целое, например 'целтаб'
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
            else: # <--- Проблемный else, теперь закомментирован
                raise DeclarationError(
                    f"Неизвестный или неподдерживаемый тип таблицы (из arrayType): {array_type_node.getText()}",
                    err_line, err_col)

        elif type_ctx.actorType():
            actor_name = type_ctx.actorType().getText()
            # Параметры типа "исполнитель" требуют особого рассмотрения.
            # Этот метод предназначен для базовых типов и таблиц, что может быть недостаточно для исполнителей.
            raise DeclarationError(
                f"Обработка параметров типа исполнитель ('{actor_name}') через _get_type_info_from_specifier не реализована полностью. "
                f"Требуется специальная логика.",
                err_line, err_col
            )

        else: # <--- УМЕНЬШЕН ОТСТУП ДО 8 ПРОБЕЛОВ
            raise DeclarationError(f"Не удалось определить тип из typeSpecifier: {type_ctx.getText()}", err_line,
                                   err_col)

        if base_kumir_type is None: # Важно! Эта проверка может сработать, если arrayType закомментирован
            print("[DEBUG] base_kumir_type is None ПОСЛЕ ЗАКОММЕНТИРОВАННОГО arrayType", file=sys.stderr) # Добавим отладку
            # Можно временно присвоить что-то, чтобы избежать ошибки здесь, если мы тестируем только SyntaxError
            # base_kumir_type = "TEMP_FIX_FOR_SYNTAX_ERROR_TEST" 
            raise DeclarationError(f"Внутренняя ошибка: базовый тип не был определен для '{type_ctx.getText()}'.",
                                   err_line, err_col)

        return base_kumir_type, is_table_type

    def _get_param_mode(self, param_decl_ctx: KumirParser.ParameterDeclarationContext) -> str:
        """Определяет режим параметра (арг, рез, арг рез)."""
        if param_decl_ctx.IN_PARAM():
            return 'арг'
        elif param_decl_ctx.OUT_PARAM():
            return 'рез'
        elif param_decl_ctx.INOUT_PARAM():
            return 'арг рез'
        else:
            return 'арг'  # По умолчанию 'арг'

    def find_variable(self, var_name: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Ищет переменную во всех областях видимости и возвращает её информацию и область видимости."""
        if self.debug: print(f"[DEBUG][FindVar] Поиск переменной '{var_name}'", file=sys.stderr)  # stdout -> stderr
        for i, scope in enumerate(reversed(self.scopes)):
            scope_level = len(self.scopes) - 1 - i
            if var_name in scope:
                if self.debug: print(f"[DEBUG][FindVar] Найдена '{var_name}' в области {scope_level}",
                                     file=sys.stderr)  # stdout -> stderr
                return scope[var_name], scope
        if self.debug: print(f"[DEBUG][FindVar] Переменная '{var_name}' НЕ найдена",
                             file=sys.stderr)  # stdout -> stderr
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
        print(f"[DEBUG][Update] Обновлено значение переменной '{var_name}' = {value}",
              file=sys.stderr)  # stdout -> stderr

    # --- Вспомогательные методы для проверки и конвертации типов при присваивании ---

    def _convert_input_to_type(self, input_str: str, target_kumir_type: str, error_source_ctx: antlr4.ParserRuleContext) -> Any:
        """
        Преобразует строку ввода в целевой тип КуМира.
        Выбрасывает KumirEvalError при ошибке преобразования.
        error_source_ctx используется для получения номера строки/колонки для ошибки.
        """
        line = error_source_ctx.start.line
        column = error_source_ctx.start.column
        original_input_repr = repr(input_str) # Для логов и сообщений об ошибках

        try:
            if target_kumir_type == INTEGER_TYPE:
                if not input_str.strip():
                    raise ValueError("Получена пустая строка для числового ввода.")
                return int(input_str)
            elif target_kumir_type == FLOAT_TYPE:
                if not input_str.strip():
                    raise ValueError("Получена пустая строка для числового ввода.")
                return float(input_str.replace(',', '.'))
            elif target_kumir_type == BOOLEAN_TYPE:
                value_str_lower = input_str.strip().lower()
                if value_str_lower == 'да':
                    return True
                elif value_str_lower == 'нет':
                    return False
                else:
                    raise ValueError("Ожидалось 'да' или 'нет'.")
            elif target_kumir_type == CHAR_TYPE:
                if len(input_str) == 1:
                    return input_str
                elif len(input_str) == 0:
                    raise ValueError("Получена пустая строка для символьного ввода (ожидался 1 символ).")
                else: # Длина > 1
                    raise ValueError(f"Ожидался один символ, получена строка длиной {len(input_str)}.")
            elif target_kumir_type == STRING_TYPE:
                return input_str
            else:
                raise KumirEvalError(
                    f"Строка {line}, столбец {column}: Внутренняя ошибка: Неподдерживаемый целевой тип '{target_kumir_type}' для ввода значения {original_input_repr}.",
                    line, column
                )
        except ValueError as ve:
            error_message = f"Строка {line}, столбец {column}: Ошибка преобразования типа при вводе значения {original_input_repr} в тип '{target_kumir_type}'. {ve}"
            print(f"[DEBUG][CONVERT_INPUT_ERROR] {error_message}", file=sys.stderr)
            raise KumirEvalError(error_message, line, column) from ve
        except Exception as e: # Обработка других неожиданных ошибок
            error_message = f"Строка {line}, столбец {column}: Неожиданная ошибка при преобразовании ввода {original_input_repr} в тип '{target_kumir_type}'. {e}"
            print(f"[DEBUG][CONVERT_INPUT_UNEXPECTED_ERROR] {error_message}", file=sys.stderr)
            raise KumirEvalError(error_message, line, column) from e


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
            else:  # <--- Эта строка должна иметь 12 пробелов отступа (3 уровня)
                # Другие типы тоже нельзя
                raise AssignmentError(
                    f"Нельзя присвоить значение типа {value_type.__name__} переменной типа ЦЕЛ.")  # <--- Эта 16 пробелов (4 уровня)
        # Строка 279, на которую ошибка ->
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
                raise AssignmentError(
                    f"Нельзя присвоить строку \"{value}\" (длина {len(value)}) переменной типа СИМ (требуется длина 1).")
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
            raise DeclarationError(
                f"Неизвестный или неподдерживаемый целевой тип '{target_type}' для переменной '{var_name}'.")

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
        self.procedures = {}  # Очищаем на всякий случай
        for item in ctx.children:
            if isinstance(item, (KumirParser.AlgorithmDefinitionContext, KumirParser.ModuleDefinitionContext)):
                # Если это определение алгоритма или модуля (модули могут содержать алгоритмы)
                self._collect_procedure_definitions(item)

        print(f"[DEBUG][VisitProgram] Собрано {len(self.procedures)} процедур/функций: {list(self.procedures.keys())}",
              file=sys.stderr)  # stdout -> stderr

        # Затем выполняем программу (посещаем всех детей)
        # Исполнение основного алгоритма произойдет при посещении его узла
        self.visitChildren(ctx)
        return None  # Программа ничего не возвращает

    def _collect_procedure_definitions(self, ctx):
        """Рекурсивно собирает все определения алгоритмов (процедур/функций)."""
        if isinstance(ctx, KumirParser.AlgorithmDefinitionContext):
            header = ctx.algorithmHeader()
            if header:
                name_ctx = header.algorithmNameTokens()
                if name_ctx:
                    name = name_ctx.getText().strip()
                    if not name:
                        line = header.start.line # header точно есть
                        raise DeclarationError(f"Строка {line}: Не удалось получить имя алгоритма.")

                    if name in self.procedures:
                        line = header.start.line # header точно есть
                        raise DeclarationError(f"Строка {line}: Алгоритм с именем '{name}' уже определен.")

                    print(f"[DEBUG][Collect] Найдено определение: '{name}'", file=sys.stderr)
                    self.procedures[name] = ctx
                else: # name_ctx is None, но header есть
                    line = header.start.line # header точно есть
                    raise DeclarationError(f"Строка {line}: Отсутствует или не удалось получить имя в заголовке алгоритма (name_ctx is None).", line, header.start.column)
            else: # header is None
                line = ctx.start.line # Берем строку из AlgorithmDefinitionContext
                raise DeclarationError(f"Строка {line}: Отсутствует заголовок (header) для определения алгоритма.", line, ctx.start.column)
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
        print("[DEBUG][Visit] Обработка implicitModuleBody", file=sys.stderr)  # stdout -> stderr
        # Просто выполняем содержимое
        for item in ctx.children:
            if isinstance(item, KumirParser.AlgorithmDefinitionContext):
                # Выполняем только *основной* алгоритм
                # Основным считаем тот, у которого нет параметров в заголовке
                header = item.algorithmHeader()
                if header and not header.parameterList():
                    print(
                        f"[DEBUG][ImplicitBody] Запуск основного алгоритма: {header.algorithmNameTokens().getText().strip()}",
                        file=sys.stderr)
                    self.enter_scope()
                    try:
                        self.visit(item)
                    finally:
                        self.exit_scope() # <--- ДОБАВЬ ЭТУ СТРОКУ
                    break
        return None

    def visitModuleDefinition(self, ctx: KumirParser.ModuleDefinitionContext):
        """Обработка определения модуля."""
        # Сбор процедур уже выполнен в visitProgram
        print("[DEBUG][Visit] Обработка moduleDefinition", file=sys.stderr)  # stdout -> stderr
        # Если это неявный модуль, делегируем visitImplicitModuleBody
        if ctx.implicitModuleBody():
            return self.visit(ctx.implicitModuleBody())
        else:
            # Для явных модулей пока ничего не делаем (только собираем процедуры)
            # В будущем здесь может быть выполнение инициализации модуля
            print("[DEBUG][ModuleDef] Явный модуль - выполнение пока не реализовано.",
                  file=sys.stderr)  # stdout -> stderr
            return None


    def visitAlgorithmDefinition(self, ctx: KumirParser.AlgorithmDefinitionContext):
        name = ctx.algorithmHeader().algorithmNameTokens().getText().strip()
        is_procedure_call_execution = hasattr(self, 'prepare_procedure_call_data') and self.prepare_procedure_call_data is not None
        
        if is_procedure_call_execution:
            print(f"[DEBUG][VisitAlgDef] Начало ВЫЗОВА процедуры/функции '{name}' через _execute_procedure_call", file=sys.stderr)
            # Получаем call_data ИЗ self.prepare_procedure_call_data
            call_data_for_execution = self.prepare_procedure_call_data 
            self.prepare_procedure_call_data = None # Очищаем сразу после получения
            return self._execute_procedure_call(call_data_for_execution, ctx) # Используем полученные данные

        else: # Это не вызов, а либо обход определения при разборе, либо основной блок программы
            header = ctx.algorithmHeader()
            # Проверяем, является ли это основным блоком программы (алгоритм без параметров)
            if header and not header.parameterList(): 
                print(f"[DEBUG][VisitAlgDef] Выполнение основного блока программы '{name}' (в текущем scope)", file=sys.stderr)
                # НЕ делаем здесь enter_scope/exit_scope
                if ctx.algorithmBody():
                    self.visit(ctx.algorithmBody())
                return None
            else:
                # Это определение процедуры/функции, но не ее вызов и не основной блок.
                # Просто пропускаем, так как оно уже было собрано в self.procedures.
                print(f"[DEBUG][VisitAlgDef] Пропуск определения процедуры/функции '{name}' (не вызов, не основной блок).", file=sys.stderr)
                return None
    
    def _execute_procedure_call(self, call_data: dict, alg_ctx: KumirParser.AlgorithmDefinitionContext) -> Any:
        """Выполняет вызов процедуры или функции."""
        name = alg_ctx.algorithmHeader().algorithmNameTokens().getText().strip()
        print(f"[DEBUG][ExecuteProcCall] Выполнение вызова '{name}'", file=sys.stderr)

        # Сохраняем и восстанавливаем current_procedure_output_mappings для вложенных вызовов
        # (prepare_procedure_call_data уже был очищен в visitAlgorithmDefinition)
        original_current_procedure_output_mappings = getattr(self, 'current_procedure_output_mappings', None)

        args_values = call_data['args_values_for_input_params']
        output_mappings_for_writeback = call_data['output_params_mapping']
        expected_params_info = call_data['expected_params_info']
        actual_arg_expr_nodes = call_data['actual_arg_expr_nodes'] # Для ошибок типизации

        self.current_procedure_output_mappings = output_mappings_for_writeback

        self.enter_scope()
        current_scope = self.scopes[-1]
        is_function_call = bool(alg_ctx.algorithmHeader().typeSpecifier())
        return_value_final = None

        try:
            # Шаг 1: Инициализация параметров в current_scope
            current_scope['__знач__'] = None 
            if is_function_call:
                func_return_type_spec = alg_ctx.algorithmHeader().typeSpecifier()
                if func_return_type_spec: # Доп. проверка, что typeSpecifier действительно есть
                    func_return_base_type, func_return_is_table = self._get_type_info_from_specifier(func_return_type_spec, alg_ctx.algorithmHeader().start.line)
                    if func_return_is_table:
                        # Пока не поддерживаем возврат таблиц напрямую, но место для ошибки есть
                        raise KumirNotImplementedError(f"Возврат таблиц из функций ('{name}') пока не поддерживается.", alg_ctx.algorithmHeader().start.line, alg_ctx.algorithmHeader().start.column)
                    
                    print(f"[DEBUG][ExecuteProcCall] Setting up return value '__знач__' for func '{name}'. Type: {func_return_base_type}", file=sys.stderr)
                    # Заменяем KumirSimpleVar на стандартную структуру переменной
                    current_scope['__знач__'] = {
                        'type': func_return_base_type,
                        'value': get_default_value(func_return_base_type),
                        'is_table': False, # Функции (пока) не возвращают таблицы
                        'dimensions': None
                    }
                    return_value_explicitly_set[0] = False # Изначально не установлено
                else: # Не должно происходить, если is_function_call is True
                    print(f"[WARNING][ExecuteProcCall] Функция '{name}' не имеет typeSpecifier, __знач__=None.", file=sys.stderr)


            actual_arg_iter_idx = 0
            for param_info in expected_params_info:
                p_name, p_type, p_mode, p_is_table, p_decl_ctx = \
                    param_info['name'], param_info['type'], param_info['mode'], param_info['is_table'], param_info['decl_ctx']

                if p_is_table:
                    # TODO: Реализовать инициализацию табличных параметров ('арг таб', 'арг рез таб', 'рез таб')
                    print(f"[DEBUG][ExecuteProcCall] TODO: Инициализация табличного параметра {p_mode} {p_name} ({p_type}) не реализована.", file=sys.stderr)
                    # Для 'арг' и 'арг рез' нужно инкрементировать actual_arg_iter_idx, если бы мы брали значение
                    if p_mode in ['арг', 'арг рез']:
                         if actual_arg_iter_idx < len(args_values):
                            actual_arg_iter_idx += 1 # Пропускаем аргумент-таблицу
                         else: # Не хватило аргументов (даже для пропуска)
                            raise KumirArgumentError(f"Недостаточно аргументов для '{name}', табличный параметр '{p_name}' ('{p_mode}').", alg_ctx.start.line, alg_ctx.start.column)
                    elif p_mode == 'рез':
                        # Для 'рез таб' параметр ссылается на переменную вызывающей стороны.
                        # Сама переменная уже существует в вызывающем scope. Здесь мы создаем локальное имя,
                        # которое будет ссылаться на тот же KumirTableVar объект.
                        # При выходе из процедуры, если были изменения, они отразятся на оригинале.
                        # Однако, КуМир обычно копирует таблицы при присвоении. 
                        # Если 'рез таб X', и в процедуре X := другая_таблица, то в вызывающей стороне должна быть копия другой_таблицы.
                        # Это значит, что для 'рез таб' мы должны создать НОВУЮ ПУСТУЮ таблицу с нужными размерами (если они известны)
                        # или отложить определение размеров до первого присваивания в процедуре.
                        # А при выходе - скопировать ее содержимое в исходную переменную.
                        # Пока для 'рез таб' создадим новую, независимую таблицу. 
                        # Размеры должны быть определены в объявлении параметра, если это поддерживается грамматикой.
                        # Грамматика КуМир: `тип ИМЯ` или `тип таб ИМЯ [границы]`. Границы обязательны для `рез таб`.
                        # Если границы параметра зависят от других параметров - это еще сложнее.
                        # Текущая `expected_params_info` не хранит вычисленные границы для параметров-таблиц.
                        # `p_decl_ctx` это `VariableDeclarationItemContext`.
                        # `parameterDeclaration : argOrRes? typeSpecifier variableList`
                        # `variableList : variableDeclarationItem (COMMA variableDeclarationItem)*`
                        # `variableDeclarationItem : ID ( LBRACK arrayBounds (COMMA arrayBounds)* RBRACK )?`
                        # Нам нужно будет вычислить arrayBounds для параметра.

                        # Упрощение: для 'рез таб' создаем новую таблицу. Размеры должны быть в p_decl_ctx.
                        # Это потребует вычисления выражений границ в текущем (уже процедурном) scope, что может быть проблемой, если границы зависят от 'арг' параметров.
                        # Для `22-swap.kum` нет таблиц, так что этот код пока не будет затронут.
                        # TODO: Реализовать правильное создание и обработку 'рез таб'.
                        # Пока заглушка, которая не будет работать для 'рез таб'.
                        # table_var_to_store = KumirTableVar(p_type, [], p_decl_ctx) # Пустые границы
                        raise KumirNotImplementedError(f"Параметры типа 'рез таб' ({p_name}) пока не полностью поддерживаются.", p_decl_ctx.start.line, p_decl_ctx.start.column)
                    
                    if table_var_to_store:
                        current_scope[p_name] = {'type': p_type, 'value': table_var_to_store, 'is_table': True, 'dimensions_info': table_var_to_store.dimension_bounds_list}
                        print(f"[DEBUG][ExecuteProcCall] Табличный параметр '{p_mode} {p_name}' ({p_type}) инициализирован.", file=sys.stderr)
                    # else: для 'рез таб' (пока ошибка выше)

                else: # Скалярный параметр
                    self.declare_variable(p_name, p_type, is_table=False) # Объявляем в current_scope
                    if p_mode in ['арг', 'арг рез']:
                        if actual_arg_iter_idx < len(args_values):
                            arg_value = args_values[actual_arg_iter_idx]
                            try:
                                converted_value = self._validate_and_convert_value_for_assignment(arg_value, p_type, p_name)
                                self.update_variable(p_name, converted_value) # Обновляем в current_scope
                            except KumirTypeError as e:
                                err_ctx = actual_arg_expr_nodes[actual_arg_iter_idx] if actual_arg_iter_idx < len(actual_arg_expr_nodes) else p_decl_ctx
                                raise KumirArgumentError(f"Строка {err_ctx.start.line if err_ctx else '??'}: Ошибка типа при передаче аргумента для параметра '{p_name}': {e.args[0]}", err_ctx.start.line if err_ctx else 0, err_ctx.start.column if err_ctx else 0) from e
                            actual_arg_iter_idx += 1
                        else: raise KumirArgumentError(f"Недостаточно аргументов для '{name}', скалярный параметр '{p_name}' ('{p_mode}').", alg_ctx.start.line, alg_ctx.start.column)
                    # Для 'рез' скалярных параметров - они просто объявлены со значением по умолчанию.
            
            # print(f"[DEBUG][ExecuteProcCall] Параметры для '{name}' инициализированы.", file=sys.stderr)

            self.visit(alg_ctx.algorithmBody()) # Выполнение тела процедуры/функции
            
            # TODO: Шаг 2: Получение __знач__ для функций из current_scope
            if is_function_call:
                print(f"[DEBUG][ExecuteProcCall] Получение __знач__ для функции '{name}' пока не реализовано.", file=sys.stderr)

                # ... (код выполнения тела процедуры) ...

                # Шаг 3: Получение __знач__ для функций из current_scope
                if is_function_call:
                    znach_entry = current_scope.get('__знач__') # current_scope это scope процедуры/функции
                    if znach_entry and znach_entry.get('type') is not None: # Проверяем, что 'type' существует и не None
                        if not znach_entry.get('is_assigned_in_body', False):
                            alg_header_ctx = alg_ctx.algorithmHeader()
                            err_line = alg_header_ctx.start.line
                            err_col = alg_header_ctx.start.column
                            func_sig_for_err = alg_header_ctx.algorithmNameTokens().getText().strip()
                            if alg_header_ctx.typeSpecifier():
                                 func_sig_for_err = alg_header_ctx.typeSpecifier().getText().strip() + " " + func_sig_for_err
                            raise KumirEvalError(f"Строка ~{err_line}: Функция '{func_sig_for_err}' не присвоила значение переменной 'знач'.", err_line, err_col)
                        return_value_final = znach_entry['value']
                        print(f"[DEBUG][ExecuteProcCall] Функция '{name}' возвращает (из __знач__): {repr(return_value_final)}", file=sys.stderr)
                    # Если is_function_call, но znach_entry некорректен (например, type is None), это проблема инициализации __знач__
                    elif not (znach_entry and znach_entry.get('type') is not None):
                         raise KumirExecutionError(f"Внутренняя ошибка: для функции '{name}' не удалось определить тип или получить информацию о __знач__.", alg_ctx.start.line)


                # Шаг 4: Обработка output_mappings_for_writeback (запись 'рез' и 'арг рез' обратно)
                if len(self.scopes) < 2: # Нужен вызывающий scope (self.scopes[-2]) и текущий (self.scopes[-1])
                    # Эта проверка должна быть перед попыткой доступа к self.scopes[-2]
                    # Если только один scope (глобальный), то это не вызов из другого scope, что странно для процедуры с параметрами
                    raise KumirExecutionError(f"Внутренняя ошибка: отсутствует вызывающий scope для возврата рез-параметров при вызове '{name}'. Текущая глубина scopes: {len(self.scopes)}", alg_ctx.start.line)
                
                caller_scope = self.scopes[-2] # Scope, из которого был вызов

                for mapping in output_mappings_for_writeback:
                    caller_var_name = mapping['caller_var_name']
                    proc_param_name = mapping['proc_param_name'] 

                    # Получаем информацию о параметре из текущего scope процедуры
                    param_entry_in_proc_scope = current_scope.get(proc_param_name)
                    if not param_entry_in_proc_scope:
                        raise KumirExecutionError(f"Внутренняя ошибка: параметр '{proc_param_name}' не найден в scope процедуры '{name}' при возврате.", alg_ctx.start.line)

                    final_value_from_proc = param_entry_in_proc_scope['value']
                    param_is_table_in_proc = param_entry_in_proc_scope.get('is_table', False)

                    # Находим переменную в вызывающем scope
                    caller_var_info_to_update = caller_scope.get(caller_var_name)
                    if not caller_var_info_to_update:
                        # Дополнительно проверим глобальный scope, если вложенность > 2
                        # Это не стандартное поведение для КуМира, но может помочь отловить ошибку scope
                        if len(self.scopes) > 2 and caller_var_name in self.scopes[0]:
                             caller_var_info_to_update = self.scopes[0].get(caller_var_name)
                             print(f"[WARNING][ExecuteProcCall] Переменная '{caller_var_name}' для возврата найдена в глобальном scope, а не в непосредственном вызывающем scope.", file=sys.stderr)
                        else:
                            raise KumirExecutionError(f"Внутренняя ошибка: переменная '{caller_var_name}' (для параметра '{proc_param_name}') не найдена в вызывающем scope procedures '{name}'.", alg_ctx.start.line)

                    caller_var_type = caller_var_info_to_update['type']
                    caller_var_is_table = caller_var_info_to_update.get('is_table', False)

                    if param_is_table_in_proc:
                        if not caller_var_is_table:
                            raise KumirTypeError(f"Ошибка при возврате из табличного параметра '{proc_param_name}' в скалярную переменную '{caller_var_name}'.", alg_ctx.start.line)
                        
                        source_table = final_value_from_proc # Это KumirTableVar из scope процедуры
                        target_table_in_caller = caller_var_info_to_update['value'] # Это KumirTableVar в вызывающем scope

                        if not isinstance(source_table, KumirTableVar) or not isinstance(target_table_in_caller, KumirTableVar):
                           raise KumirExecutionError(f"Внутренняя ошибка: неверные типы (не KumirTableVar) для копирования таблиц между '{proc_param_name}' и '{caller_var_name}'.", alg_ctx.start.line)
                        if source_table.base_kumir_type_name != target_table_in_caller.base_kumir_type_name:
                            raise KumirTypeError(f"Несовпадение базовых типов при копировании таблицы из '{proc_param_name}' ({source_table.base_kumir_type_name}) в '{caller_var_name}' ({target_table_in_caller.base_kumir_type_name}).", alg_ctx.start.line)
                        if source_table.dimension_bounds_list != target_table_in_caller.dimension_bounds_list:
                             raise KumirTypeError(f"Несовпадение размерностей при копировании таблицы из '{proc_param_name}' (границы: {source_table.dimension_bounds_list}) в '{caller_var_name}' (границы: {target_table_in_caller.dimension_bounds_list}).", alg_ctx.start.line)

                        target_table_in_caller.data = copy.deepcopy(source_table.data) # Глубокое копирование данных
                        print(f"[DEBUG][ExecuteProcCall] Данные таблицы '{proc_param_name}' скопированы в '{caller_var_name}'.", file=sys.stderr)
                    else: # Скалярный параметр для возврата
                        if caller_var_is_table:
                             raise KumirTypeError(f"Ошибка при возврате из скалярного параметра '{proc_param_name}' в табличную переменную '{caller_var_name}'.", alg_ctx.start.line)
                        try:
                            # final_value_from_proc - это уже извлеченное значение
                            converted_for_caller = self._validate_and_convert_value_for_assignment(
                                final_value_from_proc, 
                                caller_var_type, 
                                f"переменной '{caller_var_name}' при возврате из '{proc_param_name}'"
                            )
                            caller_var_info_to_update['value'] = converted_for_caller
                            print(f"[DEBUG][ExecuteProcCall] Скалярное значение из '{proc_param_name}' ({repr(final_value_from_proc)}) записано в '{caller_var_name}' (вызывающий scope) как {repr(converted_for_caller)}.", file=sys.stderr)
                        except KumirTypeError as e_type_assign:
                             raise KumirTypeError(f"Ошибка типа при возврате значения из параметра '{proc_param_name}' в переменную '{caller_var_name}': {e_type_assign.args[0]}", alg_ctx.start.line) from e_type_assign
                print(f"[DEBUG][ExecuteProcCall_POST_WRITEBACK] Содержимое caller_scope (self.scopes[-2]) ПОСЛЕ обновления рез-параметров для '{name}':", file=sys.stderr)
                if len(self.scopes) >= 2:
                    for var_name_cs, var_info_cs in self.scopes[-2].items():
                        print(f"  CallerScopeVar: {var_name_cs} = {var_info_cs.get('value')} (type: {var_info_cs.get('type')})", file=sys.stderr)
                else:
                    print("  CallerScope (self.scopes[-2]) недоступен для отладки.", file=sys.stderr)        
        
        finally:
            # Этот флаг показывает, что мы сейчас внутри finally блока _execute_procedure_call
            current_opm = call_data.get('output_params_mapping') # Определяем current_opm ПЕРЕД print
            print(f"[DEBUG][ExecuteProcCall_FINALLY_ENTER] Proc: '{name}'. OPM Exists: {current_opm is not None}", file=sys.stderr)

            # 1. Обработка выходных параметров (арг рез, рез)
            # Это должно произойти ДО выхода из области видимости процедуры
            if current_opm: # Проверяем, что current_opm не None и не пустой список
                print(f"[DEBUG][ExecuteProcCall_FINALLY] Processing output_params_mapping for '{name}'. Count: {len(current_opm)}", file=sys.stderr)
                for mapping_info in current_opm:
                    param_name_in_proc = mapping_info.get('param_name_in_proc')
                    # lvalue_detail = mapping_info.get('lvalue_detail_for_caller') # Этого ключа нет, используется caller_var_name и др.
                    caller_var_name = mapping_info.get('caller_var_name')
                    caller_var_primary_ctx = mapping_info.get('caller_var_primary_ctx') # Используется для определения строки ошибки
                    caller_var_indices_ctx = mapping_info.get('caller_var_indices_ctx')

                    if not param_name_in_proc or not caller_var_name:
                        print(f"[ERROR][ExecuteProcCall_FINALLY] Invalid mapping_info (missing param_name_in_proc or caller_var_name): {mapping_info}", file=sys.stderr)
                        continue

                    print(f"[DEBUG][ExecuteProcCall_FINALLY] Mapping detail: param_in_proc='{param_name_in_proc}', caller_var_name='{caller_var_name}', has_indices_ctx={'YES' if caller_var_indices_ctx else 'NO'}", file=sys.stderr)

                    # Получаем значение параметра из ТЕКУЩЕЙ (завершающейся) области видимости процедуры
                    param_var_info_in_proc, _ = self.find_variable(param_name_in_proc)

                    if param_var_info_in_proc:
                        param_value_to_assign = param_var_info_in_proc['value']
                        param_type_in_proc = param_var_info_in_proc['type']
                        param_is_table_in_proc = param_var_info_in_proc.get('is_table', False)
                        print(f"[DEBUG][ExecuteProcCall_FINALLY] Value of '{param_name_in_proc}' in proc scope is: {repr(param_value_to_assign)} (type: {param_type_in_proc}, is_table: {param_is_table_in_proc})", file=sys.stderr)

                        # Находим переменную в вызывающем scope (self.scopes[-2], так как текущий self.scopes[-1] это scope процедуры, который вот-вот будет удален)
                        # Важно: self.exit_scope() еще не был вызван!
                        if len(self.scopes) < 2:
                            print(f"[ERROR][ExecuteProcCall_FINALLY] Cannot access caller scope for '{caller_var_name}'. Scope depth: {len(self.scopes)}", file=sys.stderr)
                            continue
                        
                        caller_scope_dict = self.scopes[-2] # Это scope, из которого был вызов
                        caller_var_info = caller_scope_dict.get(caller_var_name)

                        if caller_var_info:
                            caller_target_type = caller_var_info['type']
                            caller_is_table = caller_var_info.get('is_table', False)
                            
                            if caller_var_indices_ctx: # Запись в элемент таблицы в вызывающей области
                                if not caller_is_table:
                                    err_line = caller_var_primary_ctx.start.line if caller_var_primary_ctx else -1
                                    print(f"[ERROR][ExecuteProcCall_FINALLY] Caller var '{caller_var_name}' is not a table, but indices provided for param '{param_name_in_proc}'. Line ~{err_line}", file=sys.stderr)
                                    continue
                                caller_table_obj = caller_var_info['value']
                                if not isinstance(caller_table_obj, KumirTableVar):
                                    err_line = caller_var_primary_ctx.start.line if caller_var_primary_ctx else -1
                                    print(f"[ERROR][ExecuteProcCall_FINALLY] Caller var '{caller_var_name}' is not a KumirTableVar instance. Line ~{err_line}", file=sys.stderr)
                                    continue
                                
                                indices_for_caller = []
                                for idx_expr_ctx_for_caller in caller_var_indices_ctx.expression():
                                    # Важно: индексы для ВЫЗЫВАЮЩЕЙ таблицы должны вычисляться в КОНТЕКСТЕ ВЫЗЫВАЮЩЕЙ стороны,
                                    # но эти выражения (ctx) были получены из ExpressionEvaluator, который работал с аргументами вызова.
                                    # Их значения уже должны были быть вычислены и сохранены, если бы они были сложными.
                                    # Однако, _get_lvalue_structure_for_arg возвращает КОНТЕКСТЫ выражений, а не значения.
                                    # Это означает, что их нужно вычислить ЗДЕСЬ, в scope ВЫЗЫВАЮЩЕГО.
                                    # Для этого нам нужен ExpressionEvaluator, который работает с вызывающим scope.
                                    # Создадим временный ExpressionEvaluator или используем существующий, но с правильным scope.
                                    # Пока что, если индексы - простые переменные или литералы, self.evaluator должен справиться, если он правильно переключает scope.
                                    # Но ExpressionEvaluator привязан к self.visitor, у которого scopes меняются.
                                    # Проблема: self.evaluator.visitExpression будет использовать self.visitor.scopes[-1], который сейчас является scope процедуры.
                                    # Решение: временно изменить scopes для evaluator.
                                    original_scopes = self.scopes
                                    self.scopes = original_scopes[:-1] # Временно убираем scope процедуры
                                    try:
                                        idx_val_for_caller = self.evaluator.visitExpression(idx_expr_ctx_for_caller)
                                    finally:
                                        self.scopes = original_scopes # Восстанавливаем scopes

                                    if not isinstance(idx_val_for_caller, int):
                                        err_line = idx_expr_ctx_for_caller.start.line
                                        print(f"[ERROR][ExecuteProcCall_FINALLY] Index for caller table '{caller_var_name}' is not int: {idx_val_for_caller}. Line ~{err_line}", file=sys.stderr)
                                        # TODO: break inner loop and continue outer
                                        break 
                                    indices_for_caller.append(idx_val_for_caller)
                                else: # Если внутренний цикл по индексам завершился без break
                                    if len(indices_for_caller) != caller_table_obj.dimensions:
                                        err_line = caller_var_indices_ctx.start.line
                                        print(f"[ERROR][ExecuteProcCall_FINALLY] Incorrect number of indices for caller table '{caller_var_name}'. Expected {caller_table_obj.dimensions}, got {len(indices_for_caller)}. Line ~{err_line}", file=sys.stderr)
                                        continue
                                    
                                    # Проверка и конвертация типа значения из процедуры для элемента таблицы в вызывающей стороне
                                    validated_val_for_caller_table_el = self._validate_and_convert_value_for_assignment(
                                        param_value_to_assign, 
                                        caller_table_obj.base_kumir_type_name, 
                                        f"элементу {caller_var_name}[{','.join(map(str, indices_for_caller))}]"
                                    )
                                    caller_table_obj.set_value(tuple(indices_for_caller), validated_val_for_caller_table_el, caller_var_indices_ctx)
                                    print(f"[SUCCESS][ExecuteProcCall_FINALLY] Updated TABLE ELEMENT '{caller_var_name}[{','.join(map(str, indices_for_caller))}]' in caller scope to {repr(validated_val_for_caller_table_el)}", file=sys.stderr)
                                    continue # Переходим к следующему mapping_info

                            else: # Запись в простую переменную в вызывающей области
                                if caller_is_table:
                                    err_line = caller_var_primary_ctx.start.line if caller_var_primary_ctx else -1
                                    print(f"[ERROR][ExecuteProcCall_FINALLY] Caller var '{caller_var_name}' IS a table, but no indices provided for param '{param_name_in_proc}'. Line ~{err_line}", file=sys.stderr)
                                    continue

                                # Отладочный print ПЕРЕД использованием proc_param_name в f-строке
                                print(f"[DEBUG_FINALLY_PRE_VALIDATE] proc_param_name='{param_name_in_proc}', caller_var_name='{caller_var_name}'", file=sys.stderr)
                                
                                description_for_validation = f"переменной '{caller_var_name}' при возврате из параметра '{param_name_in_proc}'"
                                validated_value_for_caller = self._validate_and_convert_value_for_assignment(
                                    param_value_to_assign, 
                                    caller_target_type, 
                                    description_for_validation
                                )
                                caller_var_info['value'] = validated_value_for_caller
                                print(f"[SUCCESS][ExecuteProcCall_FINALLY] Updated VAR '{caller_var_name}' in caller scope (index {len(self.scopes)-2}) to {repr(validated_value_for_caller)}", file=sys.stderr)
                        else:
                            print(f"[ERROR][ExecuteProcCall_FINALLY] Variable '{caller_var_name}' NOT FOUND in its designated caller scope (index {len(self.scopes)-2}) for update!", file=sys.stderr)
                    else:
                        print(f"[ERROR][ExecuteProcCall_FINALLY] Param '{param_name_in_proc}' not found in proc's scope ('{name}') upon exit!", file=sys.stderr)
            elif 'output_params_mapping' in call_data: # Проверяем наличие ключа, если current_opm был None или пуст
                 print(f"[DEBUG][ExecuteProcCall_FINALLY] output_params_mapping for '{name}' is present but empty or None.", file=sys.stderr)


            # 2. Теперь выходим из области видимости процедуры
            # exiting_scope_level_before_exit = len(self.scopes) # Уровень = количество областей
            self.exit_scope() # Этот метод уже печатает "[DEBUG][Scope] Вышли из области уровня X"
            # Можно добавить дополнительный лог, если нужно, специфичный для _execute_procedure_call
            # print(f"[DEBUG][ExecuteProcCall_FINALLY] Область процедуры '{name}' завершена. Текущий уровень scope: {len(self.scopes) -1}", file=sys.stderr)

            # Если это был вызов функции, которая должна была вернуть __знач__
            # if is_function_call and not return_value_explicitly_set[0] and not self.has_return_value(proc_def_ctx):
            #    print(f"[DEBUG][ExecuteProcCall_FINALLY] Function '{name}' did not set a return value explicitly and no '__знач__' in output params. Returning None.", file=sys.stderr)

            # print(f"[DEBUG][ExecuteProcCall_FINALLY_EXIT] Proc: '{name}'. Return prep: {repr(return_value_final)}", file=sys.stderr)
        
        # print(f"[DEBUG][ExecuteProcCall] Завершение вызова '{name}', возврат: {repr(return_value_final)}", file=sys.stderr)
        return return_value_final

    def visitAlgorithmBody(self, ctx: KumirParser.AlgorithmBodyContext):
        """Обработка тела алгоритма."""
        print(f"[DEBUG][VisitAlgorithmBody] ENTERED. Body text: {ctx.getText()[:100]}...", file=sys.stderr)
        # Выполнение последовательности операторов
        if ctx.statementSequence():
            print(f"[DEBUG][VisitAlgorithmBody] Visiting statementSequence.", file=sys.stderr)
            self.visit(ctx.statementSequence())
        else:
            print(f"[DEBUG][VisitAlgorithmBody] No statementSequence found in body.", file=sys.stderr)
        print(f"[DEBUG][VisitAlgorithmBody] EXITED.", file=sys.stderr)
        return None

    def visitStatementSequence(self, ctx: KumirParser.StatementSequenceContext):
        """Обработка последовательности операторов."""
        print(f"[DEBUG][VisitStatementSequence] ENTERED. Sequence text: {ctx.getText()[:100]}...", file=sys.stderr)
        statements = ctx.statement()
        if statements:
            print(f"[DEBUG][VisitStatementSequence] Found {len(statements)} statements.", file=sys.stderr)
            for i, stmt_ctx in enumerate(statements):
                print(f"[DEBUG][VisitStatementSequence] Visiting statement #{i}: {stmt_ctx.getText()[:100]}...", file=sys.stderr)
                self.visit(stmt_ctx)
        else:
            print(f"[DEBUG][VisitStatementSequence] No statements found in sequence.", file=sys.stderr)
        print(f"[DEBUG][VisitStatementSequence] EXITED.", file=sys.stderr)
        return None

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
                raise DeclarationError(f"Строка {type_token.line}: Неизвестный базовый тип: {type_token.text}",
                                       type_token.line, type_token.column)
            is_table_type = bool(type_ctx.TABLE_SUFFIX())
            if is_table_type:
                print(f"[DEBUG][VisitVarDecl] Тип определен как basicType + TABLE_SUFFIX: {base_kumir_type} таб",
                      file=sys.stderr)

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
                raise DeclarationError(
                    f"Строка {array_type_node.start.line}: Неизвестный тип таблицы (arrayType): {array_type_node.getText()}",
                    array_type_node.start.line, array_type_node.start.column)
            print(f"[DEBUG][VisitVarDecl] Тип определен как arrayType: {base_kumir_type} (слитно)", file=sys.stderr)

        elif type_ctx.actorType():
            # Пока не поддерживаем таблицы исполнителей
            actor_type_text = type_ctx.actorType().getText()
            raise DeclarationError(
                f"Строка {type_ctx.start.line}: Таблицы для типов исполнителей ('{actor_type_text}') пока не поддерживаются.",
                type_ctx.start.line, type_ctx.start.column)

        else:
            raise DeclarationError(f"Строка {type_ctx.start.line}: Не удалось определить тип переменной: {type_ctx.getText()}",
                                type_ctx.start.line, type_ctx.start.column)

        # Этот блок должен быть внутри метода visitVariableDeclaration
        if not base_kumir_type:  # Дополнительная проверка, если логика выше не установила тип
            raise DeclarationError(f"Строка {type_ctx.start.line}: Не удалось определить базовый тип для: {type_ctx.getText()}",
                                   type_ctx.start.line, type_ctx.start.column)

        current_scope = self.scopes[-1]

        for var_decl_item_ctx in ctx.variableList().variableDeclarationItem():
            var_name = var_decl_item_ctx.ID().getText()
            print(f"[DEBUG][VisitVarDecl] Обработка переменной/таблицы: {var_name}", file=sys.stderr)

            if var_name in current_scope:
                raise DeclarationError(
                    f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Переменная '{var_name}' уже объявлена в этой области.",
                    var_decl_item_ctx.ID().getSymbol().line, var_decl_item_ctx.ID().getSymbol().column)

            if is_table_type:
                if not var_decl_item_ctx.LBRACK():  # Проверяем наличие квадратных скобок
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Для таблицы '{var_name}' ({base_kumir_type} таб) должны быть указаны границы в квадратных скобках.",
                        var_decl_item_ctx.ID().getSymbol().line, var_decl_item_ctx.ID().getSymbol().column)

                dimension_bounds_list = []
                array_bounds_nodes = var_decl_item_ctx.arrayBounds()
                if not array_bounds_nodes:
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Отсутствуют определения границ для таблицы '{var_name}'.",
                        var_decl_item_ctx.LBRACK().getSymbol().line, var_decl_item_ctx.LBRACK().getSymbol().column)

                for i, bounds_ctx in enumerate(array_bounds_nodes):
                    print(f"[DEBUG][VisitVarDecl] Обработка границ измерения {i + 1} для '{var_name}': {bounds_ctx.getText()}",
                          file=sys.stderr)
                    
                    # --- НАЧАЛО ОТЛАДКИ N В VARDECL ---
                    if var_name == 'A': # Если это таблица A
                        expr0_text = bounds_ctx.expression(0).getText()
                        expr1_text = bounds_ctx.expression(1).getText()
                        print(f"[DEBUG][VarDecl_N_Check_Bounds] Table '{var_name}', Dim {i+1}, MinExpr: '{expr0_text}', MaxExpr: '{expr1_text}'", file=sys.stderr)
                        if expr1_text == 'N': # Если верхняя граница это N
                            n_info_check, _ = self.find_variable('N')
                            if n_info_check:
                                print(f"[DEBUG][VarDecl_N_Check_Value] ПЕРЕД вычислением MaxExpr ('N'), N = {n_info_check['value']}", file=sys.stderr)
                            else:
                                print(f"[DEBUG][VarDecl_N_Check_Value] ПЕРЕД вычислением MaxExpr ('N'), N не найдена!", file=sys.stderr)
                        if expr0_text == 'N': # Если нижняя граница это N (менее вероятно, но для полноты)
                            n_info_check, _ = self.find_variable('N')
                            if n_info_check:
                                print(f"[DEBUG][VarDecl_N_Check_Value] ПЕРЕД вычислением MinExpr ('N'), N = {n_info_check['value']}", file=sys.stderr)
                            else:
                                print(f"[DEBUG][VarDecl_N_Check_Value] ПЕРЕД вычислением MinExpr ('N'), N не найдена!", file=sys.stderr)
                    # --- КОНЕЦ ОТЛАДКИ N В VARDECL ---

                    if not (bounds_ctx.expression(0) and bounds_ctx.expression(1) and bounds_ctx.COLON()):
                        raise DeclarationError(
                            f"Строка {bounds_ctx.start.line}: Некорректный формат границ для измерения {i + 1} таблицы '{var_name}'. Ожидается [нижняя:верхняя].",
                            bounds_ctx.start.line, bounds_ctx.start.column)

                    min_idx_val = self.evaluator.visitExpression(bounds_ctx.expression(0))
                    max_idx_val = self.evaluator.visitExpression(bounds_ctx.expression(1))
                    min_idx = min_idx_val
                    max_idx = max_idx_val

                    if not isinstance(min_idx, int) or not isinstance(max_idx, int):
                        raise KumirEvalError(
                            f"Строка {bounds_ctx.expression(0).start.line}: Нижняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {min_idx} (тип: {type(min_idx).__name__}).",
                            bounds_ctx.expression(0).start.line, bounds_ctx.expression(0).start.column)
                    if not isinstance(max_idx, int):
                        raise KumirEvalError(
                            f"Строка {bounds_ctx.expression(1).start.line}: Верхняя граница измерения {i + 1} для таблицы '{var_name}' должна быть целым числом, получено: {max_idx} (тип: {type(max_idx).__name__}).",
                            bounds_ctx.expression(1).start.line, bounds_ctx.expression(1).start.column)

                    dimension_bounds_list.append((min_idx, max_idx))

                if not dimension_bounds_list:
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.ID().getSymbol().line}: Не удалось определить границы для таблицы '{var_name}'.",
                        var_decl_item_ctx.ID().getSymbol().line, var_decl_item_ctx.ID().getSymbol().column)

                try:
                    table_var = KumirTableVar(base_kumir_type, dimension_bounds_list, var_decl_item_ctx)
                    current_scope[var_name] = {'type': base_kumir_type, 'value': table_var, 'is_table': True,
                                               'dimensions_info': dimension_bounds_list}
                    print(
                        f"[DEBUG][VisitVarDecl] Создана таблица '{var_name}' тип {base_kumir_type}, границы: {dimension_bounds_list}",
                        file=sys.stderr)
                except KumirEvalError as e:
                    raise KumirEvalError(f"Ошибка при объявлении таблицы '{var_name}': {e.args[0]}",
                                         var_decl_item_ctx.start.line, var_decl_item_ctx.start.column)

                if var_decl_item_ctx.expression():
                    raise NotImplementedError(
                        f"Строка {var_decl_item_ctx.expression().start.line}: Инициализация таблиц при объявлении ('{var_name} = ...') пока не поддерживается.",
                        var_decl_item_ctx.expression().start.line, var_decl_item_ctx.expression().start.column)

            else:  # Обычная (скалярная) переменная
                if var_decl_item_ctx.LBRACK():
                    raise DeclarationError(
                        f"Строка {var_decl_item_ctx.LBRACK().getSymbol().line}: Скалярная переменная '{var_name}' (тип {base_kumir_type}) не может иметь указания границ массива.",
                        var_decl_item_ctx.LBRACK().getSymbol().line, var_decl_item_ctx.LBRACK().getSymbol().column)

                default_value = get_default_value(base_kumir_type)
                current_scope[var_name] = {'type': base_kumir_type, 'value': default_value, 'is_table': False,
                                           'dimensions_info': None}
                print(
                    f"[DEBUG][VisitVarDecl] Объявлена переменная '{var_name}' тип {base_kumir_type}, значение по умолчанию: {default_value}",
                    file=sys.stderr)

                if var_decl_item_ctx.expression():
                    value_to_assign = self.evaluator.visitExpression(var_decl_item_ctx.expression())

                    try:
                        validated_value = self._validate_and_convert_value_for_assignment(value_to_assign, base_kumir_type,
                                                                                          var_name)
                        current_scope[var_name]['value'] = validated_value
                        print(
                            f"[DEBUG][VisitVarDecl] Переменной '{var_name}' присвоено значение при инициализации: {validated_value}",
                            file=sys.stderr)
                    except (AssignmentError, DeclarationError, KumirEvalError) as e:
                        line = var_decl_item_ctx.expression().start.line
                        column = var_decl_item_ctx.expression().start.column
                        raise type(e)(
                            f"Строка {line}, столбец {column}: Ошибка при инициализации переменной '{var_name}': {e.args[0]}",
                            line, column) from e
        return None # Исправляем отступ для return None

    # Обработка узла многословного идентификатора (переименован)
    def visitQualifiedIdentifier(self, ctx: KumirParser.QualifiedIdentifierContext):
        # Возвращаем идентификатор
        return self.get_full_identifier(ctx)

    # Обработка узла переменной
    def visitLvalue(self, ctx: KumirParser.LvalueContext):
        if ctx.RETURN_VALUE():
            print(f"[DEBUG][Visit] Обращение к специальной переменной 'знач'", file=sys.stderr)
            return {'is_return_value': True}

        var_name = self.get_full_identifier(ctx.qualifiedIdentifier())
        print(f"[DEBUG][Visit] Обращение к переменной/таблице: '{var_name}'", file=sys.stderr)

        var_info, scope = self.find_variable(var_name)
        if var_info is None:
            line = ctx.start.line
            column = ctx.start.column
            raise KumirExecutionError(f"Строка {line}, столбец {column}: Переменная '{var_name}' не найдена.")

        if ctx.indexList():
            if not var_info['is_table']:
                line = ctx.start.line
                column = ctx.start.column
                raise KumirExecutionError(f"Строка {line}, столбец {column}: Попытка доступа по индексу к не табличной переменной '{var_name}'.")
            indices_ctx = ctx.indexList().expression()
            return {'var_name': var_name, 'is_table_element': True, 'indices_ctx': indices_ctx, 'context': ctx}
        else:
            if var_info['is_table']:
                return {'var_name': var_name, 'is_table': True, 'table_obj': var_info['value'], 'context': ctx}
            else:
                return {'var_name': var_name, 'is_table': False, 'context': ctx}

    # Обработка присваивания
    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        print(f"[DEBUG][visitAssignmentStatement] Called for ctx: {ctx.getText()}", file=sys.stderr)
        l_value_ctx = ctx.lvalue()
        r_value_expr_ctx = ctx.expression()
        l_value_text_for_debug = "ERROR_LVALUE_CTX_BECAME_NONE_UNEXPECTEDLY"
        qualified_identifier_text_for_debug = "ERROR_QUALIFIED_ID_CTX_BECAME_NONE_UNEXPECTEDLY"
        if l_value_ctx:
            l_value_text_for_debug = l_value_ctx.getText()
            if l_value_ctx.qualifiedIdentifier():
                qualified_identifier_text_for_debug = l_value_ctx.qualifiedIdentifier().getText()
            else:
                qualified_identifier_text_for_debug = "None (l_value_ctx.qualifiedIdentifier() is None)"
        else:
            l_value_text_for_debug = "None (l_value_ctx is None before debug prints)"
            qualified_identifier_text_for_debug = "N/A (l_value_ctx is None)"
        print(f"[DEBUG][AssignAttempt_Simple] l_value_ctx text: {l_value_text_for_debug}", file=sys.stderr)
        print(f"[DEBUG][AssignAttempt_Simple] l_value_ctx.qualifiedIdentifier text: {qualified_identifier_text_for_debug}", file=sys.stderr)
        if not l_value_ctx:
            if ctx.ASSIGN():
                raise KumirSyntaxError("Отсутствует выражение после оператора присваивания ':='", ctx.ASSIGN().symbol.line, ctx.ASSIGN().symbol.column)
            if not l_value_ctx and not ctx.ASSIGN():
                print(f"[DEBUG][visitAssignmentStatement] Interpreting as expression statement: {ctx.getText()}", file=sys.stderr)
                expr_node_or_list = ctx.expression()
                actual_expr_to_visit = None
                if isinstance(expr_node_or_list, list):
                    if expr_node_or_list:
                        actual_expr_to_visit = expr_node_or_list[0]
                elif expr_node_or_list:
                    actual_expr_to_visit = expr_node_or_list
                if actual_expr_to_visit:
                    self.evaluator.visitExpression(actual_expr_to_visit)
            else:
                raise KumirSyntaxError(f"Ошибка: отсутствует выражение в операторе '{ctx.getText()}'", ctx.start.line, ctx.start.column)
            return None
        value_to_assign = self.evaluator.visitExpression(r_value_expr_ctx)
        is_return_value_assignment = False
        if l_value_ctx and l_value_ctx.RETURN_VALUE():
            is_return_value_assignment = True
                    # Находим __знач__ в текущем scope (должен быть scope функции)
            current_scope_dict = self.scopes[-1]
            if '__знач__' not in current_scope_dict:
                # Попытка присвоить 'знач' вне тела функции или если __знач__ не было инициализировано
                # Это может случиться, если 'знач := ...' используется в процедуре (не функции)
                # или в глобальной области, что недопустимо для 'знач'.
                # Или если текущий scope почему-то не тот, что ожидался.
                err_line = l_value_ctx.RETURN_VALUE().symbol.line
                err_col = l_value_ctx.RETURN_VALUE().symbol.column
                raise KumirEvalError(
                    f"Строка {err_line}: Присваивание специальной переменной 'знач' возможно только внутри тела функции.",
                    err_line, err_col
                )

            znach_info = current_scope_dict['__знач__']
            if znach_info.get('type') is None: # 'type' is None означает, что это не функция (или ошибка инициализации)
                err_line = l_value_ctx.RETURN_VALUE().symbol.line
                err_col = l_value_ctx.RETURN_VALUE().symbol.column
                raise KumirEvalError(
                    f"Строка {err_line}: Присваивание 'знач' допустимо только в функциях, а не процедурах.",
                    err_line, err_col
                )

            # Проверяем тип присваиваемого значения относительно типа возврата функции
            try:
                validated_value_for_znach = self._validate_and_convert_value_for_assignment(
                    value_to_assign, 
                    znach_info['type'], 
                    "возвращаемому значению 'знач'"
                )
                znach_info['value'] = validated_value_for_znach
                znach_info['is_assigned_in_body'] = True # <--- ВАЖНЫЙ ФЛАГ
                print(f"[DEBUG][visitAssignmentStatement] Присвоено ЗНАЧ = {validated_value_for_znach} (тип {znach_info['type']})", file=sys.stderr)
            except KumirTypeError as e: # AssignmentError
                err_line = r_value_expr_ctx.start.line # Ошибка в типе ПРАВОЙ части
                err_col = r_value_expr_ctx.start.column
                raise KumirEvalError(
                    f"Строка {err_line}: Ошибка типа при присваивании значению 'знач': {e.args[0]}",
                    err_line, err_col
                ) from e
        else:
            if not l_value_ctx or not l_value_ctx.qualifiedIdentifier():
                l_value_text_for_err = l_value_ctx.getText() if l_value_ctx else "None"
                raise KumirSyntaxError(f"Отсутствует имя переменной в операторе присваивания (lvalue: '{l_value_text_for_err}')", ctx.start.line, ctx.start.column)
            var_name = l_value_ctx.qualifiedIdentifier().getText()
            var_info, var_scope = self.find_variable(var_name)
            if var_info is None:
                raise KumirEvalError(f"Переменная '{var_name}' не объявлена", l_value_ctx.qualifiedIdentifier().start.line, l_value_ctx.qualifiedIdentifier().start.column)
            kumir_target_type = var_info.get('type', 'неизвестен')
            is_table = var_info.get('is_table', False)
            if l_value_ctx.LBRACK():
                if not is_table:
                    raise KumirEvalError(f"Переменная '{var_name}' не является таблицей, но используется с индексами", l_value_ctx.qualifiedIdentifier().start.line)
                if not var_info.get('value') or not isinstance(var_info['value'], KumirTableVar):
                    raise KumirEvalError(f"Таблица '{var_name}' не инициализирована правильно (отсутствует KumirTableVar)", l_value_ctx.start.line)
                kumir_table_var = var_info['value']
                table_element_type = kumir_table_var.base_kumir_type_name
                index_ctx_list = l_value_ctx.indexList().expression()
                indices = []
                for i_ctx in index_ctx_list:
                    idx_val = self.evaluator.visitExpression(i_ctx)
                    if not isinstance(idx_val, int):
                        raise KumirEvalError(f"Индекс таблицы '{var_name}' должен быть целым числом, получено: {idx_val}", i_ctx.start.line)
                    indices.append(idx_val)
                if len(indices) != len(var_info.get('dimensions_info', [])):
                    raise KumirEvalError(f"Неверное количество индексов для таблицы '{var_name}'. Ожидалось {len(var_info.get('dimensions_info', []))}, получено {len(indices)}.", l_value_ctx.start.line)
                value_to_set_in_table = self._validate_and_convert_value_for_assignment(value_to_assign, table_element_type, f"{var_name}[{','.join(map(str, indices))}]")
                try:
                    kumir_table_var.set_value(tuple(indices), value_to_set_in_table, l_value_ctx)
                    print(f"[DEBUG][visitAssignmentStatement] Присвоено {var_name}[{','.join(map(str, indices))}] = {value_to_set_in_table}", file=sys.stderr)
                except IndexError as e:
                    raise KumirEvalError(f"Индекс выходит за границы таблицы '{var_name}': {e}", l_value_ctx.start.line, l_value_ctx.start.column)
                except TypeError as e:
                    raise KumirEvalError(f"Ошибка присваивания элементу таблицы '{var_name}': {e}", l_value_ctx.start.line, l_value_ctx.start.column)
            else:
                if is_table:
                    raise KumirEvalError(f"Попытка присвоить значение всей таблице '{var_name}' без указания индексов. Такое присваивание не поддерживается.", l_value_ctx.start.line)
                validated_value = self._validate_and_convert_value_for_assignment(value_to_assign, kumir_target_type, var_name)
                var_info['value'] = validated_value
                print(f"[DEBUG][visitAssignmentStatement] Присвоено {var_name} = {validated_value} (тип {kumir_target_type})", file=sys.stderr)
        return None

    def visitIoStatement(self, ctx: KumirParser.IoStatementContext):
        # stdout -> stderr для всех print()
        print(f"[DEBUG][visitIoStatement] ENTERED. ctx: {ctx.getText()}", file=sys.stderr)
        is_input_operation = bool(ctx.INPUT())
        is_output_operation = bool(ctx.OUTPUT())

        print(f"[DEBUG][visitIoStatement] is_input_operation: {is_input_operation}, is_output_operation: {is_output_operation}", file=sys.stderr)

        if not ctx.ioArgumentList() or not ctx.ioArgumentList().ioArgument():
            print(f"[WARNING][visitIoStatement] ioStatement без аргументов: {ctx.getText()}", file=sys.stderr)
            return None

        io_args_list_candidate = ctx.ioArgumentList().ioArgument()
        if self.debug:
            print(f"[DEBUG][visitIoStatement] ctx.ioArgumentList().ioArgument() is of type: {type(io_args_list_candidate)}", file=sys.stderr)
            if isinstance(io_args_list_candidate, list):
                print(f"[DEBUG][visitIoStatement] It's a list with {len(io_args_list_candidate)} elements.", file=sys.stderr)
                for i, arg_item_debug in enumerate(io_args_list_candidate):
                    print(f"[DEBUG][visitIoStatement]   Arg {i}: {arg_item_debug.getText()} (type: {type(arg_item_debug)})", file=sys.stderr)

        if is_output_operation:
            for i_loop, arg_ctx in enumerate(io_args_list_candidate):
                print(f"[DEBUG][visitIoStatement_Loop_Output] Iteration {i_loop}, START processing arg_ctx: {arg_ctx.getText()}", file=sys.stderr)
                value_to_output = None
                if arg_ctx.expression():
                        expr_node_to_eval = arg_ctx.expression()
                        actual_expr_to_visit = expr_node_to_eval[0] if isinstance(expr_node_to_eval, list) and expr_node_to_eval else expr_node_to_eval
                        value_to_output = self.evaluator.visitExpression(actual_expr_to_visit)
                        expr_text_for_debug = expr_node_to_eval.getText() if hasattr(expr_node_to_eval, 'getText') else f"LIST_OF_NODES_LEN_{len(expr_node_to_eval) if isinstance(expr_node_to_eval, list) else 'Unknown'}"
                        print(f"[DEBUG][visitIoStatement_Output] Выражение: {expr_text_for_debug}, Значение: {repr(value_to_output)}", file=sys.stderr)
                elif arg_ctx.STRING():
                    str_literal = arg_ctx.STRING().getText()
                    value_to_output = str_literal[1:-1].replace('\\\\"', '"').replace("\\\\'", "'").replace('\\\\\\\\', '\\\\')
                    print(f"[DEBUG][visitIoStatement_Output] Строковый литерал: {str_literal}, Значение: {repr(value_to_output)}", file=sys.stderr)
                elif arg_ctx.NEWLINE_CONST():
                    print() 
                    print(f"[DEBUG][visitIoStatement_Output] нс - перевод строки", file=sys.stderr)
                    print(f"[DEBUG][visitIoStatement_Loop_Output] Iteration {i_loop}, END processing arg_ctx (нс): {arg_ctx.getText()}", file=sys.stderr)
                    continue 
                else:
                    print(f"[ERROR][visitIoStatement_Output] Неподдерживаемый тип аргумента для ВЫВОД: {arg_ctx.getText()}", file=sys.stderr)
                    raise KumirEvalError(f"Неподдерживаемый тип аргумента для ВЫВОД: {arg_ctx.getText()}", arg_ctx.start.line, arg_ctx.start.column)

                formatted_value = self._format_output_value(value_to_output, arg_ctx)
                print(formatted_value, end='') 
                print(f"[DEBUG][visitIoStatement_Loop_Output] Iteration {i_loop}, END processing arg_ctx: {arg_ctx.getText()}", file=sys.stderr)
            
        elif is_input_operation:
            for i_loop, arg_ctx in enumerate(io_args_list_candidate):
                print(f"[DEBUG][visitIoStatement_Loop_Input] Iteration {i_loop}, START processing arg_ctx: {arg_ctx.getText()}", file=sys.stderr)
                raw_expr_node_or_list = arg_ctx.expression()
                if isinstance(raw_expr_node_or_list, list):
                    if raw_expr_node_or_list:
                        initial_expr_ctx_from_argument = raw_expr_node_or_list[0]
                    else:
                        raise KumirEvalError(f"Строка {arg_ctx.start.line}: Отсутствует выражение для оператора ВВОД (получен пустой список выражений).", arg_ctx.start.line, arg_ctx.start.column)
                else:
                    initial_expr_ctx_from_argument = raw_expr_node_or_list

                if not initial_expr_ctx_from_argument:
                    raise KumirEvalError(f"Строка {arg_ctx.start.line}: Для оператора ВВОД ожидается имя переменной или элемент массива, получено: {arg_ctx.getText()}", arg_ctx.start.line, arg_ctx.start.column)

                lvalue_expr_ctx = initial_expr_ctx_from_argument
                primary_expr_node = None
                postfix_expr_node = None
                q_ident_node = None
                var_name = None
                
                temp_node = lvalue_expr_ctx
                if hasattr(temp_node, 'logicalOrExpression') and temp_node.logicalOrExpression():
                    temp_node = temp_node.logicalOrExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]
                if hasattr(temp_node, 'logicalAndExpression') and temp_node.logicalAndExpression():
                    temp_node = temp_node.logicalAndExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]
                if hasattr(temp_node, 'equalityExpression') and temp_node.equalityExpression():
                    temp_node = temp_node.equalityExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]
                if hasattr(temp_node, 'relationalExpression') and temp_node.relationalExpression():
                    temp_node = temp_node.relationalExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]
                if hasattr(temp_node, 'additiveExpression') and temp_node.additiveExpression():
                    temp_node = temp_node.additiveExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]
                if hasattr(temp_node, 'multiplicativeExpression') and temp_node.multiplicativeExpression():
                    temp_node = temp_node.multiplicativeExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]
                if hasattr(temp_node, 'powerExpression') and temp_node.powerExpression():
                    temp_node = temp_node.powerExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]
                if hasattr(temp_node, 'unaryExpression') and temp_node.unaryExpression():
                    temp_node = temp_node.unaryExpression()
                    if isinstance(temp_node, list): temp_node = temp_node[0]

                if hasattr(temp_node, 'postfixExpression') and temp_node.postfixExpression():
                    postfix_expr_node = temp_node.postfixExpression()
                    if isinstance(postfix_expr_node, list): postfix_expr_node = postfix_expr_node[0]
                    if hasattr(postfix_expr_node, 'primaryExpression') and postfix_expr_node.primaryExpression():
                        primary_expr_node = postfix_expr_node.primaryExpression()
                        if isinstance(primary_expr_node, list): primary_expr_node = primary_expr_node[0]
                elif hasattr(temp_node, 'primaryExpression') and temp_node.primaryExpression():
                    primary_expr_node = temp_node.primaryExpression()
                    if isinstance(primary_expr_node, list): primary_expr_node = primary_expr_node[0]
                
                if primary_expr_node:
                    _q_ident_candidate = self.get_child_safely(primary_expr_node, 'qualifiedIdentifier')
                    if _q_ident_candidate:
                        q_ident_node = _q_ident_candidate
                        var_name = self.get_full_identifier(q_ident_node)
                        print(f"[DEBUG][IO] INPUT target var_name: '{var_name}' (извлечено из Primary -> QIdent)", file=sys.stderr)
                    elif hasattr(primary_expr_node, 'ID') and primary_expr_node.ID():
                        var_name = primary_expr_node.ID().getText()
                        print(f"[DEBUG][IO] INPUT target var_name: '{var_name}' (извлечено из Primary -> ID)", file=sys.stderr)
                    else:
                        raise KumirSyntaxError(f"Недопустимое выражение слева для ввода (нет QIdent или ID в PrimaryExpressionNode: '{primary_expr_node.getText()}')", primary_expr_node.start.line)
                else: 
                    if hasattr(lvalue_expr_ctx, 'qualifiedIdentifier') and callable(lvalue_expr_ctx.qualifiedIdentifier) and lvalue_expr_ctx.qualifiedIdentifier():
                         q_ident_node = lvalue_expr_ctx.qualifiedIdentifier()
                         var_name = self.get_full_identifier(q_ident_node)
                         print(f"[DEBUG][IO] INPUT target var_name: '{var_name}' (извлечено из lvalue_expr_ctx.qualifiedIdentifier() - FALLBACK 1)", file=sys.stderr)
                    elif hasattr(lvalue_expr_ctx, 'ID') and callable(lvalue_expr_ctx.ID) and lvalue_expr_ctx.ID(): 
                         var_name = lvalue_expr_ctx.ID().getText()
                         print(f"[DEBUG][IO] INPUT target var_name: '{var_name}' (извлечено из lvalue_expr_ctx.ID() - FALLBACK 2)", file=sys.stderr)
                    else:
                        raise KumirSyntaxError(f"Недопустимое выражение слева для ввода: {lvalue_expr_ctx.getText()}", lvalue_expr_ctx.start.line)

                target_var_info, _ = self.find_variable(var_name)
                if not target_var_info:
                    err_line = q_ident_node.start.line if q_ident_node else lvalue_expr_ctx.start.line
                    err_col = q_ident_node.start.column if q_ident_node else lvalue_expr_ctx.start.column
                    raise KumirNameError(f"Переменная '{var_name}' не найдена для ввода", err_line, err_col)

                input_str = self.get_input_line().strip()
                if self.echo_input:
                    print(input_str) 
                
                index_list_node = None
                if postfix_expr_node:
                    index_list_node = self.get_child_safely(postfix_expr_node, 'indexList')

                if index_list_node and hasattr(index_list_node, 'expression') and index_list_node.expression():
                    if not target_var_info.get('is_table', False):
                        err_line = q_ident_node.start.line if q_ident_node else lvalue_expr_ctx.start.line
                        raise KumirTypeError(f"Переменная '{var_name}' не является таблицей, но используется с индексами для ввода.", err_line)
                    kumir_table_var_obj = target_var_info['value']
                    if not isinstance(kumir_table_var_obj, KumirTableVar):
                        raise KumirEvalError(f"Внутренняя ошибка: переменная '{var_name}' ({target_var_info.get('type')}) помечена как таблица, но ее значение не является KumirTableVar.", lvalue_expr_ctx.start.line)
                    indices = []
                    idx_expr_list = index_list_node.expression()
                    if not isinstance(idx_expr_list, list):
                        idx_expr_list = [idx_expr_list]
                    for index_expr_ctx in idx_expr_list:
                        idx_val = self.evaluator.visitExpression(index_expr_ctx)
                        if not isinstance(idx_val, int):
                            raise KumirTypeError(f"Индекс таблицы '{var_name}' должен быть целым числом, получено: {idx_val} (тип {type(idx_val).__name__})", index_expr_ctx.start.line)
                        indices.append(idx_val)
                    print(f"[DEBUG][IO] INPUT table '{var_name}', indices: {indices}", file=sys.stderr)
                    if len(indices) != kumir_table_var_obj.dimensions:
                            raise KumirIndexError(f"Неверное число индексов для таблицы '{var_name}'. Ожидалось {kumir_table_var_obj.dimensions}, получено {len(indices)}.", index_list_node.start.line)
                    element_kumir_type = kumir_table_var_obj.base_kumir_type_name
                    try:
                        value_to_assign = self._convert_input_to_type(input_str, element_kumir_type, lvalue_expr_ctx)
                    except KumirInputError as e:
                        raise KumirInputError(f"Ошибка при вводе для элемента таблицы '{var_name}{''.join([f'[{i}]' for i in indices])}': {e.original_message}", lvalue_expr_ctx.start.line, original_type=e.original_type, input_value=e.input_value) from e
                    except KumirEvalError as e_eval:
                            raise KumirEvalError(f"Ошибка при вводе для элемента таблицы '{var_name}{''.join([f'[{i}]' for i in indices])}': {e_eval.args[0]}", lvalue_expr_ctx.start.line) from e_eval
                    try:
                        kumir_table_var_obj.set_value(tuple(indices), value_to_assign, index_list_node)
                        print(f"[IO] ВВОД (таблица): Прочитано \\\"{input_str}\\\", конвертировано в ({element_kumir_type}) {value_to_assign} для '{var_name}{''.join([f'[{i}]' for i in indices])}'", file=sys.stderr)
                    except (KumirIndexError, KumirTypeError, KumirEvalError) as e_table_set:
                        raise e_table_set
                    except Exception as e_generic_table_set:
                        raise KumirExecutionError(f"Неожиданная ошибка при присвоении элементу таблицы '{var_name}{''.join([f'[{i}]' for i in indices])}': {e_generic_table_set}", index_list_node.start.line) from e_generic_table_set
                else: 
                    if target_var_info.get('is_table', False):
                        raise KumirSyntaxError(f"Для ввода в таблицу '{var_name}' необходимо указать индекс(ы).", lvalue_expr_ctx.start.line)
                    variable_kumir_type = target_var_info.get('type')
                    if not variable_kumir_type:
                            raise KumirEvalError(f"Внутренняя ошибка: не определен тип для переменной '{var_name}'", lvalue_expr_ctx.start.line)
                    try:
                        value_to_assign = self._convert_input_to_type(input_str, variable_kumir_type, lvalue_expr_ctx)
                    except KumirInputError as e:
                        raise KumirInputError(f"Ошибка при вводе для переменной '{var_name}': {e.original_message}", lvalue_expr_ctx.start.line, original_type=e.original_type, input_value=e.input_value) from e
                    except KumirEvalError as e_eval: 
                            raise KumirEvalError(f"Ошибка при вводе для переменной '{var_name}': {e_eval.args[0]}", lvalue_expr_ctx.start.line) from e_eval
                    target_var_info['value'] = value_to_assign
                    print(f"[IO] ВВОД (переменная): Прочитано \\\"{input_str}\\\", конвертировано в ({variable_kumir_type}) {value_to_assign} для '{var_name}'", file=sys.stderr)
                    if var_name == 'N':
                        print(f"[DEBUG][IO_Input_N_Check_SimpleVar] N = {target_var_info['value']}", file=sys.stderr)
                print(f"[DEBUG][visitIoStatement_Loop_Input] Iteration {i_loop}, END processing arg_ctx: {arg_ctx.getText()}", file=sys.stderr)
        else: 
            print(f"[ERROR][visitIoStatement] Оператор не является INPUT или OUTPUT (общая проверка): {ctx.getText()}", file=sys.stderr)
            raise KumirSyntaxError(f"Оператор ввода/вывода не определен (общая проверка): {ctx.getText()}", ctx.start.line, ctx.start.column)

        if isinstance(io_args_list_candidate, list):
            print(f"[DEBUG][visitIoStatement] EXITED. Loop processed {len(io_args_list_candidate)} arguments.", file=sys.stderr)
        else:
            print(f"[DEBUG][visitIoStatement] EXITED. Processed 1 argument (not a list).", file=sys.stderr)
            return None
        print(f"[DEBUG][visitIoStatement] EXITED. Loop processed {len(io_args_list_candidate) if isinstance(io_args_list_candidate, list) else '1 (not a list)'} arguments.", file=sys.stderr)
        return None

    def get_input_line(self) -> str:
        """Читает строку из стандартного ввода и удаляет символы новой строки."""
        try:
            line = sys.stdin.readline().rstrip('\r\n')
            # print(f"[DEBUG][GET_INPUT_LINE] Read line: {repr(line)}", file=sys.stderr) # Можно добавить для отладки
            return line
        except EOFError:
            raise KumirInputRequiredError("Неожиданный конец ввода (EOF).")
        except Exception as e: # Более общий перехват на случай проблем с sys.stdin
            raise KumirInputRequiredError(f"Ошибка чтения ввода: {e}")


    def visitStatement(self, ctx: KumirParser.StatementContext):
        if ctx.variableDeclaration():
            return self.visit(ctx.variableDeclaration())
        elif ctx.assignmentStatement():
            return self.visit(ctx.assignmentStatement())
        elif ctx.ioStatement():
            return self.visit(ctx.ioStatement())
        elif ctx.ifStatement():
            return self.visit(ctx.ifStatement())
        elif ctx.switchStatement():
            return self.visit(ctx.switchStatement())
        elif ctx.loopStatement():
            return self.visit(ctx.loopStatement())
        elif ctx.exitStatement():
            return self.visit(ctx.exitStatement())
        elif ctx.pauseStatement():
            return self.visit(ctx.pauseStatement())
        elif ctx.stopStatement():
            return self.visit(ctx.stopStatement())
        elif ctx.assertionStatement():
            return self.visit(ctx.assertionStatement())
        else:
            num_children = ctx.getChildCount()
            if num_children == 1:
                child = ctx.getChild(0)
                if isinstance(child, KumirParser.ProcedureCallStatementContext):
                    if hasattr(self, 'visitProcedureCallStatement'):
                        return self.visit(child)
                    else:
                        # print(f"[WARNING][visitStatement] visitProcedureCallStatement not implemented for: {child.getText()}", file=sys.stderr)
                        raise KumirNotImplementedError(f"Вызов процедуры '{child.getText()}' пока не поддерживается.", child.start.line)
                elif isinstance(child, TerminalNodeImpl) and child.symbol.type == KumirParser.SEMICOLON:
                    return None # Пустой оператор
                else:
                    # print(f"[WARNING][visitStatement] Unhandled single child of StatementContext: {type(child).__name__} - {child.getText()[:80]}", file=sys.stderr)
                    return self.visitChildren(ctx) 
            elif num_children == 0:
                return None
            else:
                # print(f"[WARNING][visitStatement] StatementContext with {num_children} children but no direct method: {ctx.getText()[:80]}", file=sys.stderr)
                return self.visitChildren(ctx)

    def visitProcedureCallStatement(self, ctx: KumirParser.ProcedureCallStatementContext):
        # Для ProcedureCallStatementContext нужно будет реализовать visitProcedureCallStatement
        # или, если это выражение, его можно передать в expression_evaluator.
        # Пока что просто вызываем visitChildren, если visitProcedureCallStatement не реализован.
        if hasattr(self, 'visitProcedureCallStatement'):
            return self.visit(ctx)
        else:
            # Это старая заглушка, которая вызывала ошибку, т.к. ProcedureCallStatementContext не имеет expression()
            # self.evaluator.visit(child.expression()) 
            # Вместо этого, если нет спец. обработчика, можно просто обойти детей
            # или вызвать ошибку о нереализованной фиче.
            print(f"[WARNING][visitStatement] visitProcedureCallStatement not implemented for: {ctx.getText()}", file=sys.stderr)
            # return self.visitChildren(ctx) # Может быть небезопасно, если дети - не операторы
            raise KumirNotImplementedError(f"Вызов процедуры '{ctx.getText()}' пока не поддерживается.", ctx.start.line)

    # --- ИСПРАВЛЕНИЕ: Добавляем явный visitArgumentList как метод ---
    def visitArgumentList(self, ctx: KumirParser.ArgumentListContext):
        parent_ctx = ctx.parentCtx 
        func_name_debug = "UNKNOWN_FUNC"
        if isinstance(parent_ctx, KumirParser.PostfixExpressionContext) and parent_ctx.primaryExpression():
            func_name_debug = parent_ctx.primaryExpression().getText()

        if self.debug: print(f"[Enter] visitArgumentList for {func_name_debug}({ctx.getText()})", file=sys.stderr)
        args = []
        for i, expr_ctx in enumerate(ctx.expression()):
            raw_arg_value = self.evaluator.visitExpression(expr_ctx)
            if self.debug: print(
                f"[DEBUG][ArgList Proc] For {func_name_debug}, Arg {i} ({expr_ctx.getText()}): evaluated to {repr(raw_arg_value)} ({type(raw_arg_value).__name__})",
                file=sys.stderr)
            args.append(raw_arg_value)
        if self.debug: print(f"[Exit] visitArgumentList for {func_name_debug}({ctx.getText()}) -> returns {repr(args)}",
                             file=sys.stderr)
        return args

    def visitPrimaryExpression(self, ctx: KumirParser.PrimaryExpressionContext):
        # Логика этого метода должна быть в ExpressionEvaluator, 
        # но если он вызывается здесь, он должен что-то делать или быть удален.
        # Пока оставим как no-op, если он не должен обрабатываться здесь.
        # print(f"[DEBUG][visitPrimaryExpression] Called for ctx: {ctx.getText()}", file=sys.stderr)
        # if ctx.literal():
        #     # Обработка литералов должна быть в ExpressionEvaluator.visitLiteral
        #     # result = self.evaluator.visitLiteral(ctx.literal()) # Пример
        #     pass
        return None # Явный return

    # --- НОВЫЙ МЕТОД: Форматирование вывода (уже был, проверяем отступ)---
    def _format_output_value(self, value, arg_ctx: KumirParser.IoArgumentContext) -> str:
        """Форматирует значение для вывода с учетом спецификаторов :Ш:Т."""
        width = None
        precision = None

        # arg_ctx.expression() возвращает список всех выражений в ioArgument.
        # Первое expression (index 0) - это само выводимое значение (оно уже в 'value').
        # Если есть форматирование, то expression(1) - это ширина, expression(2) - точность.
        expressions_in_io_arg = arg_ctx.expression() # Это список

        num_colons = len(arg_ctx.COLON()) if arg_ctx.COLON() else 0

        if num_colons > 0:
            if len(expressions_in_io_arg) > 1: # Должно быть как минимум выражение для ширины
                width_expr_ctx = expressions_in_io_arg[1] # Второе выражение - это ширина
                width_val = self.evaluator.visitExpression(width_expr_ctx)
                if not isinstance(width_val, int):
                    raise KumirEvalError(f"Ширина в спецификаторе формата вывода должна быть целым числом, получено: {width_val}", width_expr_ctx.start.line)
                # --- ДОБАВЛЕНО НАЧАЛО ---
                if width_val < 0:
                    raise KumirEvalError(f"Ширина (Ш) в спецификаторе формата вывода не может быть отрицательной, получено: {width_val}", width_expr_ctx.start.line)
                # --- ДОБАВЛЕНО КОНЕЦ ---
                width = width_val
                if self.debug: print(f"[DEBUG][Format] Ширина: {width}", file=sys.stderr)

                if num_colons > 1 and len(expressions_in_io_arg) > 2: # Есть второе ':' и выражение для точности
                    precision_expr_ctx = expressions_in_io_arg[2] # Третье выражение - это точность
                    precision_val = self.evaluator.visitExpression(precision_expr_ctx)
                    if not isinstance(precision_val, int):
                        raise KumirEvalError(f"Точность в спецификаторе формата вывода должна быть целым числом, получено: {precision_val}", precision_expr_ctx.start.line)
                    # --- ДОБАВЛЕНО НАЧАЛО ---
                    if precision_val < 0:
                        raise KumirEvalError(f"Точность (Т) в спецификаторе формата вывода не может быть отрицательной, получено: {precision_val}", precision_expr_ctx.start.line)
                    # --- ДОБАВЛЕНО КОНЕЦ ---
                    precision = precision_val
                    if self.debug: print(f"[DEBUG][Format] Точность: {precision}", file=sys.stderr)
                elif num_colons > 1 and len(expressions_in_io_arg) <= 2:
                    # Есть второе двоеточие, но нет выражения для точности - ошибка
                    raise KumirSyntaxError("Отсутствует выражение для точности после второго ':' в спецификаторе формата.", arg_ctx.COLON(1).symbol.line if len(arg_ctx.COLON()) > 1 else arg_ctx.start.line)            
            else:
                # Есть двоеточие, но нет выражения для ширины - ошибка
                raise KumirSyntaxError("Отсутствует выражение для ширины после ':' в спецификаторе формата.", arg_ctx.COLON(0).symbol.line if arg_ctx.COLON() else arg_ctx.start.line)

        if isinstance(value, (int, float)):
            if precision is not None: 
                if not isinstance(value, float): value = float(value)
                # --- ИЗМЕНЕНО НАЧАЛО ---
                if width is not None:
                    format_string = "{" + f":{width}.{precision}f" + "}" # -> "{:width.precisionf}"
                else:
                    format_string = "{" + f":.{precision}f" + "}"    # -> "{:.precisionf}"
                # --- ИЗМЕНЕНО КОНЕЦ ---
                formatted = format_string.format(value)
                return formatted
            elif width is not None: 
                # --- ИЗМЕНЕНО НАЧАЛО ---
                s_value = str(value)
                if isinstance(value, (int, float)):
                    # Числа выравниваем по правому краю
                    return s_value.rjust(width)
                else:
                    # Строки (и все остальное) по левому
                    return s_value.ljust(width)
                # --- ИЗМЕНЕНО КОНЕЦ ---
            else: 
                return str(value)
        elif isinstance(value, bool):
            return 'да' if value else 'нет'
        else:
            return str(value)

    # --- Метод для visitLiteral (уже был, проверяем отступ, но он помечен как удаленный)---
    # Этот метод, скорее всего, не используется, так как visitLiteral есть в ExpressionEvaluator
    def visitLiteral(self, ctx: KumirParser.LiteralContext):
        # text_debug = ctx.getText()
        # print(f"[DEBUG][VisitLiteral] Processing literal: '{text_debug}' (Interpreter version - likely unused)", file=sys.stderr)
        # if ctx.INTEGER(): return int(ctx.INTEGER().getText().lstrip('$'), 16 if ctx.INTEGER().getText().startswith('$') else 10)
        # if ctx.REAL(): return float(ctx.REAL().getText().replace(',', '.'))
        # if ctx.STRING(): return ctx.STRING().getText()[1:-1].replace('\\\\"', '"').replace("\\\\'", "'").replace('\\\\\\\\', '\\\\')
        # if ctx.CHAR_LITERAL(): return ctx.CHAR_LITERAL().getText()[1:-1].replace('\\\\"', '"').replace("\\\\'", "'").replace('\\\\\\\\', '\\\\')
        # if ctx.TRUE(): return True
        # if ctx.FALSE(): return False
        # if ctx.colorLiteral(): return ctx.colorLiteral().getText()
        # if ctx.NEWLINE_CONST(): return '\\n'
        # return None 
        # Вместо этого, лучше явно указать, что он не должен вызываться здесь, если это так
        raise NotImplementedError("visitLiteral in KumirInterpreterVisitor should not be called directly; use ExpressionEvaluator.")

    def visitLoopStatement(self, ctx: KumirParser.LoopStatementContext):
        """Обработка цикла"""
        loop_spec = ctx.loopSpecifier()  # Может быть None
        end_loop_cond = ctx.endLoopCondition()  # Может быть None
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
                        raise KumirSyntaxError("Отсутствует имя переменной в цикле ДЛЯ", loop_spec.FOR().symbol.line,
                                               loop_spec.FOR().symbol.column)
                    var_name = var_name_node.getText()
                    self.enter_scope()
                    print(f"[DEBUG][Scope] Вошли в локальную область для цикла ДЛЯ (переменная '{var_name}')",
                          file=sys.stderr)
                    try:
                        # Вычисляем начальное, конечное значения и шаг
                        from_expr_ctx = loop_spec.expression(0)
                        to_expr_ctx = loop_spec.expression(1)
                        step_expr_ctx = loop_spec.expression(2) if len(
                            loop_spec.expression()) > 2 and loop_spec.STEP() else None

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
                            raise KumirEvalError("Шаг в цикле ДЛЯ не может быть равен нулю",
                                                 loop_spec.STEP().symbol.line if loop_spec.STEP() else from_expr_ctx.start.line)

                        self.scopes[-1][var_name] = {'type': INTEGER_TYPE, 'value': start_value, 'is_table': False,
                                                     'kumir_type': 'цел'}
                        print(f"[DEBUG][Loop] Цикл ДЛЯ '{var_name}' от {start_value} до {end_value} шаг {step_value}",
                              file=sys.stderr)

                        current_val = start_value

                        # ИСПРАВЛЕНИЕ ЗДЕСЬ: Объединяем условие while на одну строку
                        while (step_value > 0 and current_val <= end_value) or (step_value < 0 and current_val >= end_value):
                            self.scopes[-1][var_name]['value'] = current_val
                            self.visit(statement_sequence_ctx)
                            if self.exit_flags[-1]:
                                print(f"[DEBUG][Loop] Обнаружен ВЫХОД из цикла ДЛЯ", file=sys.stderr)
                                break
                            current_val += step_value
                    finally:
                        self.exit_scope()
                        print(f"[DEBUG][Scope] Вышли из локальной области цикла ДЛЯ (переменная '{var_name}')",
                              file=sys.stderr)
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
                            raise KumirEvalError("Условие в цикле ПОКА должно быть логического типа",
                                                 condition_ctx.start.line)
                elif loop_spec.TIMES():
                    count_expr_ctx = loop_spec.expression(0)
                    print(f"[DEBUG][Loop] Цикл N РАЗ, выражение для кол-ва: {count_expr_ctx.getText()}", file=sys.stderr)
                    count_value = self.evaluator.visitExpression(count_expr_ctx)
                    if not isinstance(count_value, int):
                        raise KumirEvalError("Количество повторений в цикле ...РАЗ должно быть целым числом",
                                             count_expr_ctx.start.line)
                    if count_value < 0:
                        print(f"[DEBUG][Loop] Цикл N РАЗ: N={count_value} < 0, не будет выполнен.", file=sys.stderr)
                        count_value = 0
                    for _ in range(count_value):
                        self.visit(statement_sequence_ctx)
                        if self.exit_flags[-1]:
                            print(f"[DEBUG][Loop] Обнаружен ВЫХОД из цикла N РАЗ", file=sys.stderr)
                            break
                # This 'else' was incorrectly placed in the previous version for TIMES loop,
                # it should be for the outer 'if loop_spec:'
                # else: # This applied to TIMES(), which is wrong.
                #     raise KumirNotImplementedError(
                #         f"Неизвестный или неподдерживаемый тип loopSpecifier: {loop_spec.getText() if loop_spec else 'None'}",
                #         ctx.start.line)
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
                        raise KumirEvalError("Условие в 'кц при' (цикл ДО) должно быть логического типа",
                                             condition_ctx.start.line)
                    if condition_value:
                        break
            else: # Простой цикл нц ... кц (бесконечный, выход только по ВЫХОД)
                  # This 'else' correctly corresponds to 'if loop_spec:' and 'elif end_loop_cond:'
                print(f"[DEBUG][Loop] Простой цикл НЦ...КЦ (без явного условия)", file=sys.stderr)
                while True:
                    self.visit(statement_sequence_ctx)
                    if self.exit_flags[-1]:
                        print(f"[DEBUG][Loop] Обнаружен ВЫХОД из простого цикла НЦ...КЦ", file=sys.stderr)
                        break
        finally:
            if self.exit_flags: # Проверка, что список не пуст
                self.exit_flags.pop()
            self.loop_depth -= 1
        return None

    def visitExitStatement(self, ctx: KumirParser.ExitStatementContext):
        if self.loop_depth > 0 and self.exit_flags:
            print(f"[DEBUG][VisitExit] Выполнение ВЫХОД из цикла. loop_depth={self.loop_depth}", file=sys.stderr)
            self.exit_flags[-1] = True
        else:
            print(f"[WARNING][VisitExit] ВЫХОД вызван вне активного цикла или exit_flags пуст. loop_depth={self.loop_depth}", file=sys.stderr)
        return None

    def visitIfStatement(self, ctx: KumirParser.IfStatementContext):
        """Обработка условного оператора."""
        print(f"[DEBUG][visitIfStatement] Called for ctx: {ctx.getText()} with id: {id(ctx)}", file=sys.stderr)

        # Попытка получить атрибуты СРАЗУ
        condition_expr_ctx = None
        statement_sequences_list = []
        has_else_kw = False

        try:
            condition_expr_ctx = ctx.expression()
            statement_sequences_list = ctx.statementSequence()
            # Проверяем наличие ELSE через ctx.ELSE(), который вернет TerminalNode или None
            has_else_kw = bool(ctx.ELSE()) # или ctx.ИНАЧЕ() если грамматика использует его
            print(f"[DEBUG][visitIfStatement] Successfully got expression and statementSequence. Condition type: {type(condition_expr_ctx).__name__}, Sequences count: {len(statement_sequences_list)}, Has ELSE: {has_else_kw}", file=sys.stderr)
        except AttributeError as e:
            print(f"[DEBUG][visitIfStatement] AttributeError CAUGHT IMMEDIATELY: {e}", file=sys.stderr)
            # Выведем dir() еще раз, если ошибка сразу
            print(f"[DEBUG][visitIfStatement] Attributes of ctx ({type(ctx).__name__}) AT POINT OF ERROR:", file=sys.stderr)
            for attr_name in dir(ctx):
                if not attr_name.startswith('__'):
                    try: print(f"  {attr_name}: {getattr(ctx, attr_name)}", file=sys.stderr)
                    except: print(f"  {attr_name}: <Error getting>", file=sys.stderr)
            raise # Перевыбрасываем ошибку, чтобы тест упал

        if condition_expr_ctx is None:
            raise KumirSyntaxError("Отсутствует условное выражение в операторе ЕСЛИ", ctx.start.line, ctx.start.column)
        
        condition_value = None 
        try:
            condition_value = self.evaluator.visitExpression(condition_expr_ctx) 
        except Exception as e:
            line = condition_expr_ctx.start.line 
            column = condition_expr_ctx.start.column 
            raise KumirEvalError(f"Строка {line}, столбец {column}: Ошибка вычисления условия: {e}", line, column) 

        if not isinstance(condition_value, bool):
            line = condition_expr_ctx.start.line
            column = condition_expr_ctx.start.column
            raise KumirEvalError(
                f"Строка {line}, столбец {column}: Условие должно быть логического типа, а не {type(condition_value).__name__}.", line, column)

        print(f"  -> Условие = {condition_value}", file=sys.stderr)

        if condition_value:
            if statement_sequences_list and len(statement_sequences_list) > 0: 
                then_branch_ctx = statement_sequences_list[0]
                if then_branch_ctx is not None: 
                    return self.visit(then_branch_ctx) 
        else:
            if has_else_kw and statement_sequences_list and len(statement_sequences_list) > 1: 
                else_branch_ctx = statement_sequences_list[1]
                if else_branch_ctx is not None: 
                    return self.visit(else_branch_ctx) 
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

    def get_child_safely(self, parent_ctx: antlr4.ParserRuleContext, child_name: str) -> Optional[antlr4.ParserRuleContext]:
        """
        Безопасно получает дочерний узел по имени его метода-аксессора.
        Если метод возвращает список, берет первый элемент.
        Возвращает None, если атрибут/метод отсутствует или список пуст.
        """
        # Используем sys.stderr для отладочных сообщений, если они нужны
        # import sys # Убедимся, что sys импортирован, если будем раскомментировать принты

        if not parent_ctx or not hasattr(parent_ctx, child_name):
            # print(f"[DEBUG][get_child_safely] Parent context is None or attribute '{child_name}' not found on {type(parent_ctx).__name__}.", file=sys.stderr)
            return None
        
        try:
            child_attr = getattr(parent_ctx, child_name)
            
            child_node_or_list = None
            if callable(child_attr):
                # print(f"[DEBUG][get_child_safely] Calling method '{child_name}()' on {type(parent_ctx).__name__}", file=sys.stderr)
                child_node_or_list = child_attr()
            else:
                # print(f"[DEBUG][get_child_safely] Accessing attribute '{child_name}' on {type(parent_ctx).__name__}", file=sys.stderr)
                child_node_or_list = child_attr

            if isinstance(child_node_or_list, list):
                # print(f"[DEBUG][get_child_safely] Method '{child_name}()' returned a list of length {len(child_node_or_list)}", file=sys.stderr)
                return child_node_or_list[0] if child_node_or_list else None
            # Проверим, что это экземпляр ParserRuleContext или None, прежде чем вернуть
            elif isinstance(child_node_or_list, antlr4.ParserRuleContext) or child_node_or_list is None:
                # print(f"[DEBUG][get_child_safely] Method '{child_name}()' returned: {type(child_node_or_list).__name__}", file=sys.stderr)
                return child_node_or_list
            else:
                # print(f"[DEBUG][get_child_safely] Method '{child_name}()' returned unexpected type: {type(child_node_or_list).__name__}. Value: {str(child_node_or_list)[:100]}", file=sys.stderr)
                # Если это не список и не ParserRuleContext (и не None), это может быть TerminalNode или что-то еще.
                # Для LValue разбора мы обычно ожидаем ParserRuleContext.
                # Если возвращается TerminalNodeImpl, это может быть ID, но get_full_identifier работает с QualifiedIdentifierContext.
                # Пока что вернем его, если это ANTLR дерево, иначе None.
                if hasattr(child_node_or_list, 'symbol'): # Признак TerminalNodeImpl
                    return child_node_or_list 
                return None # Не то, что мы обычно ищем как "узел контекста" для дальнейшего разбора lvalue
                
        except Exception as e:
            # print(f"[ERROR][get_child_safely] Exception while getting child '{child_name}' from {type(parent_ctx).__name__}: {e}", file=sys.stderr)
            return None

# Эта функция должна быть на верхнем уровне модуля, а не методом класса
def interpret_kumir(code: str):
    """
    Интерпретирует код на языке КуМир.

    Args:
        code (str): Исходный код программы

    Returns:
        str: Захваченный вывод программы
    """
    from antlr4 import InputStream, CommonTokenStream # УБРАН tree
    from .generated.KumirLexer import KumirLexer
    from .generated.KumirParser import KumirParser
    # DiagnosticErrorListener is defined in this file, so no relative import needed.

    input_stream = InputStream(code)
    lexer = KumirLexer(input_stream)
    lexer.removeErrorListeners()
    error_listener = DiagnosticErrorListener()  # Instantiate local class
    lexer.addErrorListener(error_listener)

    token_stream = CommonTokenStream(lexer)
    parser = KumirParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)  # Используем тот же слушатель для парсера

    tree = None
    try:
        tree = parser.program()  # Attempt to parse
    except KumirSyntaxError:  # Re-raise if DiagnosticErrorListener raised it
        raise
    except Exception as e:  # Catch other ANTLR or parsing-related exceptions
        raise KumirSyntaxError(f"Ошибка синтаксического анализа: {e}", 0, 0) from e

    visitor = KumirInterpreterVisitor() # Конструктор без аргументов

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    stdout_capture = StringIO()       # <--- Сначала объявляем
    sys.stdout = stdout_capture 
    
    # --- DEBUG ID ---    
    print(f"[DEBUG_INTERPRET_KUMIR_SETUP] id(sys.stdout) after assignment: {id(sys.stdout)}, id(stdout_capture): {id(stdout_capture)}", file=sys.stderr) # <--- Потом используем
    # --- END DEBUG ID ---

    try:
        visitor.visit(tree)
    except KumirInputRequiredError:
        raise
    except Exception as e:
        raise
    finally:
        # --- DEBUG ID ---    
        print(f"[DEBUG_INTERPRET_KUMIR_FINALLY] id(sys.stdout) before restore: {id(sys.stdout)}, id(stdout_capture): {id(stdout_capture)}", file=sys.stderr)
        # --- END DEBUG ID ---
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    print(
        f"[DEBUG_INTERPRET_KUMIR] About to return from interpret_kumir. stdout_capture type: {type(stdout_capture)}",
        file=sys.stderr)
    captured_content = stdout_capture.getvalue()

    # --- НОВОЕ: Добавляем \n в конец, если его нет --- 
    if captured_content and not captured_content.endswith('\n'):
        captured_content += '\n'
        print("[DEBUG_INTERPRET_KUMIR] Appended final newline to stdout_capture.", file=sys.stderr)
    # --- КОНЕЦ НОВОГО ---

    print(
        f"[DEBUG_INTERPRET_KUMIR] Content of stdout_capture ({len(captured_content)} chars):\n>>>\n{captured_content}\n<<<",
        file=sys.stderr)

    return captured_content