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
                        file=sys.stderr)  # stdout -> stderr
                    self.visit(item)  # Посещаем определение, что приведет к выполнению тела
                    break  # Выполняем только первый найденный основной алгоритм
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
        # Сбор процедур уже выполнен в visitProgram
        print("[DEBUG][Visit] Обработка procedureDefinition", file=sys.stderr)  # stdout -> stderr
        # print(f"[DEBUG][VisitAlgDef] Processing algorithm: {ctx.algorithmHeader().algorithmName().getText()}", file=sys.stderr)
        # Этот метод теперь отвечает за *выполнение* алгоритма,
        # когда его вызывают для основного алгоритма.
        # Сбор определений уже произошел.
        name = ctx.algorithmHeader().algorithmNameTokens().getText().strip()
        print(f"[DEBUG][VisitAlgDef] Выполнение алгоритма '{name}'", file=sys.stderr)  # stdout -> stderr

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
        return None  # Определение алгоритма само по себе ничего не возвращает

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
        if is_return_value_assignment:
            if not hasattr(self, 'return_value') or self.return_value is None:
                self.return_value = {}
            self.return_value['value'] = value_to_assign
            print(f"[DEBUG][visitAssignmentStatement] Присвоено ЗНАЧ = {value_to_assign}", file=sys.stderr)
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

        # --- ОТЛАДКА --- Добавляем вывод о том, что возвращает ioArgument() --- #
        io_args_list_candidate = ctx.ioArgumentList().ioArgument()
        print(f"[DEBUG][visitIoStatement] ctx.ioArgumentList().ioArgument() is of type: {type(io_args_list_candidate)}", file=sys.stderr)
        if isinstance(io_args_list_candidate, list):
            print(f"[DEBUG][visitIoStatement] It's a list with {len(io_args_list_candidate)} elements.", file=sys.stderr)
            for i, arg_item_debug in enumerate(io_args_list_candidate):
                print(f"[DEBUG][visitIoStatement]   Arg {i}: {arg_item_debug.getText()} (type: {type(arg_item_debug)})", file=sys.stderr)
        # --- КОНЕЦ ОТЛАДКИ ---

        for i_loop, arg_ctx in enumerate(io_args_list_candidate): # Используем enumerate для индекса
            print(f"[DEBUG][visitIoStatement_Loop] Iteration {i_loop}, START processing arg_ctx: {arg_ctx.getText()}", file=sys.stderr)
            if is_output_operation:
                value_to_output = None
                if arg_ctx.expression():
                        # --- ОТЛАДКА ТИПА И ЗНАЧЕНИЯ arg_ctx.expression() ---
                        expr_node_to_eval = arg_ctx.expression()
                        print(f"[DEBUG][VisitIoStmt_Pre_Eval] Тип expr_node_to_eval: {type(expr_node_to_eval)}, Значение: {expr_node_to_eval!r}", file=sys.stderr)
                        if isinstance(expr_node_to_eval, list):
                            print(f"[DEBUG][VisitIoStmt_Pre_Eval] ВНИМАНИЕ! expr_node_to_eval - это СПИСОК! Длина: {len(expr_node_to_eval)}. Первый элемент текста: {'N/A' if not expr_node_to_eval else (expr_node_to_eval[0].getText() if hasattr(expr_node_to_eval[0], 'getText') else 'NO_GETTEXT')}", file=sys.stderr)
                        # --- КОНЕЦ ОТЛАДКИ ---
                        actual_expr_to_visit = expr_node_to_eval[0] if isinstance(expr_node_to_eval, list) and expr_node_to_eval else expr_node_to_eval
                        print(f"[DEBUG][VisitIoStmt_Pre_Eval2] Тип actual_expr_to_visit: {type(actual_expr_to_visit)}, Текст: {actual_expr_to_visit.getText() if hasattr(actual_expr_to_visit, 'getText') else 'NOT_A_CONTEXT_NODE'}", file=sys.stderr)
                        value_to_output = self.evaluator.visitExpression(actual_expr_to_visit)
                        # Также исправим следующий print, чтобы он не падал, если expr_node_to_eval - список
                        expr_text_for_debug = expr_node_to_eval.getText() if hasattr(expr_node_to_eval, 'getText') else f"LIST_OF_NODES_LEN_{len(expr_node_to_eval) if isinstance(expr_node_to_eval, list) else 'Unknown'}"
                        print(f"[DEBUG][visitIoStatement_Output] Выражение: {expr_text_for_debug}, Значение: {repr(value_to_output)}", file=sys.stderr)

                elif arg_ctx.STRING(): 
                    str_literal = arg_ctx.STRING().getText()
                    value_to_output = str_literal[1:-1].replace('\\\"', '"').replace("\\\\'", "'").replace('\\\\\\\\', '\\')
                    print(f"[DEBUG][visitIoStatement_Output] Строковый литерал: {str_literal}, Значение: {repr(value_to_output)}", file=sys.stderr)
                elif arg_ctx.NEWLINE_CONST(): 
                    print() 
                    print(f"[DEBUG][visitIoStatement_Output] нс - перевод строки", file=sys.stderr)
                    continue 
                else:
                    print(f"[ERROR][visitIoStatement_Output] Неподдерживаемый тип аргумента для ВЫВОД: {arg_ctx.getText()}", file=sys.stderr)
                    raise KumirEvalError(f"Неподдерживаемый тип аргумента для ВЫВОД: {arg_ctx.getText()}", arg_ctx.start.line, arg_ctx.start.column)

                formatted_value = self._format_output_value(value_to_output, arg_ctx)
                print(formatted_value, end='')

            elif is_input_operation:
                # Шаг 1: Получаем результат arg_ctx.expression()
                raw_expr_node_or_list = arg_ctx.expression()

                # Убедимся, что initial_expr_ctx_from_argument - это один узел контекста
                if isinstance(raw_expr_node_or_list, list):
                    if raw_expr_node_or_list:  # Если список не пустой
                        initial_expr_ctx_from_argument = raw_expr_node_or_list[0]
                    else: # Пустой список выражений - это ошибка
                        raise KumirEvalError(f"Строка {arg_ctx.start.line}: Отсутствует выражение для оператора ВВОД (получен пустой список выражений).", arg_ctx.start.line, arg_ctx.start.column)
                else: # Это уже один узел или None
                    initial_expr_ctx_from_argument = raw_expr_node_or_list
                
                # Теперь проверяем, не None ли initial_expr_ctx_from_argument
                if not initial_expr_ctx_from_argument:
                    raise KumirEvalError(f"Строка {arg_ctx.start.line}: Для оператора ВВОД ожидается имя переменной или элемент массива, получено: {arg_ctx.getText()}", arg_ctx.start.line, arg_ctx.start.column)

                # --- Начало блока is_input_operation --- 
                target_is_simple_var = False
                target_is_table_element = False
                var_name = None
                indices_ctx_list = None 
                kumir_target_type = None
                qualified_identifier_node = None
                index_list_node = None 
                
                # Определение get_child_safely должно быть здесь, до его использования
                def get_child_safely(parent_ctx, attr_name_str):
                    if hasattr(parent_ctx, attr_name_str):
                        child_attr_method = getattr(parent_ctx, attr_name_str)
                        if callable(child_attr_method):
                            child_node_or_list = child_attr_method()
                            if isinstance(child_node_or_list, list):
                                return child_node_or_list[0] if child_node_or_list else None
                            return child_node_or_list
                    return None

                current_drill_ctx = initial_expr_ctx_from_argument
                expression_drill_path = [
                    'logicalOrExpression', 'logicalAndExpression', 'equalityExpression',
                    'relationalExpression', 'additiveExpression', 'multiplicativeExpression',
                    'powerExpression', 'unaryExpression', 'postfixExpression'
                ]
                drilled_context = current_drill_ctx
                for method_name_str in expression_drill_path:
                    next_node_candidate = get_child_safely(drilled_context, method_name_str)
                    if next_node_candidate:
                        drilled_context = next_node_candidate
                    else:
                        break 
                temp_expr_ctx = drilled_context 
                debug_text_for_original_expr = initial_expr_ctx_from_argument.getText() if hasattr(initial_expr_ctx_from_argument, 'getText') else "N/A"
                print(f"[DEBUG][visitIoStatement_Input] Исходное выражение: {debug_text_for_original_expr}, тип после спуска: {type(temp_expr_ctx).__name__}", file=sys.stderr)
                if isinstance(temp_expr_ctx, KumirParser.PostfixExpressionContext):
                    if temp_expr_ctx.primaryExpression() and temp_expr_ctx.primaryExpression().qualifiedIdentifier():
                        qualified_identifier_node = temp_expr_ctx.primaryExpression().qualifiedIdentifier()
                    raw_index_list_node_or_list = temp_expr_ctx.indexList()
                    if isinstance(raw_index_list_node_or_list, list):
                        index_list_node = raw_index_list_node_or_list[0] if raw_index_list_node_or_list else None
                    else:
                        index_list_node = raw_index_list_node_or_list
                elif isinstance(temp_expr_ctx, KumirParser.PrimaryExpressionContext):
                    if temp_expr_ctx.qualifiedIdentifier():
                        qualified_identifier_node = temp_expr_ctx.qualifiedIdentifier()
                else:
                    raise KumirEvalError(f"Строка {initial_expr_ctx_from_argument.start.line}: Некорректное выражение для ввода: {initial_expr_ctx_from_argument.getText()}", initial_expr_ctx_from_argument.start.line, initial_expr_ctx_from_argument.start.column)
                if qualified_identifier_node:
                    var_name = qualified_identifier_node.getText()
                    var_info, var_scope = self.find_variable(var_name)
                    if var_info is None:
                        raise KumirEvalError(f"Строка {qualified_identifier_node.start.line}: Переменная '{var_name}' не объявлена.", qualified_identifier_node.start.line, qualified_identifier_node.start.column)
                    kumir_target_type = var_info.get('type')
                    is_target_table_from_var_info = var_info.get('is_table', False)
                    if index_list_node: 
                        if not is_target_table_from_var_info:
                            raise KumirEvalError(f"Строка {qualified_identifier_node.start.line}: Переменная '{var_name}' не таблица.", qualified_identifier_node.start.line)
                        target_is_table_element = True
                        # --- DEBUG PRINT ДЛЯ ПРОВЕРКИ index_list_node (оставляем на всякий случай) ---
                        print(f"[DEBUG_CULPRIT_CHECK] Перед index_list_node.expression(). Тип index_list_node: {type(index_list_node)}, Текст: {index_list_node.getText() if hasattr(index_list_node, 'getText') else 'N/A'}", file=sys.stderr)
                        # --- КОНЕЦ DEBUG PRINT ---
                        indices_ctx_list = index_list_node.expression() 
                    else: # No indices
                        if is_target_table_from_var_info:
                            raise KumirEvalError(f"Строка {qualified_identifier_node.start.line}: Ввод в целую таблицу '{var_name}' невозможен.", qualified_identifier_node.start.line)
                        # print(f"[DEBUG_IO_INPUT_FLAG] Перед target_is_simple_var=True. var_name='{var_name}'. target_is_simple_var={target_is_simple_var}, target_is_table_element={target_is_table_element}", file=sys.stderr) # УДАЛЕНО
                        target_is_simple_var = True
                        # print(f"[DEBUG_IO_INPUT_FLAG] После target_is_simple_var=True. var_name='{var_name}'. target_is_simple_var={target_is_simple_var}, target_is_table_element={target_is_table_element}", file=sys.stderr) # УДАЛЕНО
                else:
                    raise KumirEvalError(f"Строка {initial_expr_ctx_from_argument.start.line}: Не удалось определить имя переменной для ввода: {initial_expr_ctx_from_argument.getText()}", initial_expr_ctx_from_argument.start.line, initial_expr_ctx_from_argument.start.column)
                
                if not var_name or not kumir_target_type:
                    raise KumirEvalError(f"Строка {initial_expr_ctx_from_argument.start.line}: Внутренняя ошибка: цель ввода не определена для '{initial_expr_ctx_from_argument.getText()}'.", initial_expr_ctx_from_argument.start.line, initial_expr_ctx_from_argument.start.column)
                
                try:
                    input_str = self.get_input_line()
                    if self.echo_input: print(input_str) 
                except KumirInputRequiredError as e_input: raise e_input
                except Exception as e_get_line:
                    raise KumirInputRequiredError(f"Ошибка чтения ввода: {e_get_line}", initial_expr_ctx_from_argument.start.line, initial_expr_ctx_from_argument.start.column) from e_get_line
                
                converted_value = self._convert_input_to_type(input_str, kumir_target_type, initial_expr_ctx_from_argument)

                # print(f"[DEBUG_IO_INPUT_FLAG] Перед if/elif/else для присваивания. var_name='{var_name}'. target_is_simple_var={target_is_simple_var}, target_is_table_element={target_is_table_element}", file=sys.stderr) # УДАЛЕНО
                if target_is_simple_var:
                    var_info_to_update, scope_to_update = self.find_variable(var_name)
                    if var_info_to_update is None: raise KumirEvalError(f"Внутренняя ошибка: переменная '{var_name}' не найдена.")
                    var_info_to_update['value'] = converted_value
                    if var_name == 'N': print(f"[DEBUG][IO_Input_N_Check] N = {var_info_to_update['value']}", file=sys.stderr)
                elif target_is_table_element:
                    var_info_table, scope_table = self.find_variable(var_name)
                    if var_info_table is None or not var_info_table.get('is_table'): raise KumirEvalError(f"Внутренняя ошибка: таблица '{var_name}' не найдена.")
                    kumir_table_var_obj = var_info_table['value']
                    if not isinstance(kumir_table_var_obj, KumirTableVar): raise KumirEvalError(f"Переменная '{var_name}' не KumirTableVar.")
                    indices = []
                    if not indices_ctx_list: raise KumirEvalError(f"Нет индексов для таблицы '{var_name}'.")
                    for i_ctx_idx in indices_ctx_list:
                        idx_val = self.evaluator.visitExpression(i_ctx_idx)
                        if not isinstance(idx_val, int): raise KumirEvalError(f"Индекс для '{var_name}' не целое: {idx_val}", i_ctx_idx.start.line)
                        indices.append(idx_val)
                    expected_dims_info = var_info_table.get('dimensions_info')
                    if expected_dims_info is None: raise KumirEvalError(f"Нет информации о размерностях для '{var_name}'.")
                    if len(indices) != len(expected_dims_info):
                        raise KumirEvalError(f"Неверное кол-во индексов для '{var_name}'. Ожидалось {len(expected_dims_info)}, получено {len(indices)}.")
                    try:
                        error_source_ctx_for_set = index_list_node if index_list_node else initial_expr_ctx_from_argument
                        kumir_table_var_obj.set_value(tuple(indices), converted_value, error_source_ctx_for_set)
                    except IndexError as e_idx:
                        error_source_ctx_for_idx_err = index_list_node if index_list_node else initial_expr_ctx_from_argument
                        raise KumirEvalError(f"Индекс выходит за границы '{var_name}': {e_idx}", error_source_ctx_for_idx_err.start.line) from e_idx
                    except Exception as e_setval:
                        error_source_ctx_for_set_err = index_list_node if index_list_node else initial_expr_ctx_from_argument
                        raise KumirEvalError(f"Ошибка присвоения элементу таблицы '{var_name}': {e_setval}", error_source_ctx_for_set_err.start.line) from e_setval
                else:
                    raise KumirEvalError(f"Внутренняя ошибка: цель ввода не определена: {arg_ctx.getText()}", arg_ctx.start.line)
            else:
                print(f"[ERROR][visitIoStatement] Оператор не является INPUT или OUTPUT: {ctx.getText()}", file=sys.stderr)
                raise KumirSyntaxError(f"Оператор ввода/вывода не определен: {ctx.getText()}", ctx.start.line, ctx.start.column)
            print(f"[DEBUG][visitIoStatement_Loop] Iteration {i_loop}, END processing arg_ctx: {arg_ctx.getText()}", file=sys.stderr) # Отладочный вывод в конце итерации
        
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

        if arg_ctx.COLON():
            format_specs = arg_ctx.INTEGER() 
            if len(format_specs) == 1:
                width = int(format_specs[0].getText())
                if self.debug: print(f"[DEBUG][Format] Ширина: {width}", file=sys.stderr)
            elif len(format_specs) >= 2:
                width = int(format_specs[0].getText())
                precision = int(format_specs[1].getText())
                if self.debug: print(f"[DEBUG][Format] Ширина: {width}, Точность: {precision}", file=sys.stderr)

        if isinstance(value, (int, float)):
            if precision is not None: 
                if not isinstance(value, float): value = float(value)
                format_string = f"{'{'}{width}.{precision}f{'}'}" if width is not None else f"{'{'}{precision}f{'}'}"
                formatted = format_string.format(value)
                return formatted
            elif width is not None: 
                format_string = f"{'{'}{width}{'}'}"
                return format_string.format(str(value))
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