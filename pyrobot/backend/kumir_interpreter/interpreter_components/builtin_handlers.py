# Этот файл будет содержать словарь BUILTIN_FUNCTIONS и, возможно, некоторые из их хендлеров.

# Пока что оставим импорты пустыми, добавим по мере необходимости
# from ..kumir_exceptions import ...
# from . import builtin_functions as bf # Если хендлеры в другом файле
# import math

# TODO: Перенести сюда импорты KumirLexer, типы (INTEGER_TYPE и т.д.) и bf, если он не будет импортироваться извне
# TODO: Также перенести сюда math_functions (div, mod, irand, rand), если они используются напрямую в лямбдах

import sys # Для print отладки в будущем, если понадобится
from typing import TYPE_CHECKING, Any, Optional, Callable, Dict, List, Tuple, Union

# Импортируем хендлеры из соседнего модуля
from . import builtin_functions as bf
# Импортируем напрямую используемые функции
from ..math_functions import div, mod 

if TYPE_CHECKING:
    from ..interpreter import KumirInterpreterVisitor # Для аннотации типов visitor_self
    from antlr4 import ParserRuleContext

# Типы, которые могут понадобиться для словаря, если решим его типизировать позже
# ArgTypes = List[List[str]]
# HandlerFunc = Callable[['KumirInterpreterVisitor', List[Any], Optional['ParserRuleContext']], Any]
# BuiltinFunctionInfo = Dict[str, Union[int, ArgTypes, HandlerFunc]]
# BuiltinFunctionsDict = Dict[str, BuiltinFunctionInfo]

BUILTIN_FUNCTIONS = {
    # --- Математические функции (начало) ---
    'sqrt': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']], 
        'handler': lambda visitor_self, args, ctx: bf.handle_sqrt(visitor_self, args[0], ctx)
    },
    'sin': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_sin(visitor_self, args[0], ctx)
    },
    'cos': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_cos(visitor_self, args[0], ctx)
    },
    'tan': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_tan(visitor_self, args[0], ctx)
    },
    'arctan': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_arctan(visitor_self, args[0], ctx)
    },
    'int': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_int_conversion(visitor_self, args[0], ctx)
    },
    'abs': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_abs(visitor_self, args[0], ctx)
    },
    'sign': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_sign(visitor_self, args[0], ctx)
    },
    'случайноецелое': { 
         'min_args': 2, 'max_args': 2,
         'arg_types': [['цел', 'цел']],
         'handler': lambda visitor_self, args, ctx: bf.handle_random_integer(visitor_self, args[0], args[1], ctx)
    },
    'случайноевещественное': { 
         'min_args': 2, 'max_args': 2,
         'arg_types': [['вещ', 'вещ'], ['цел', 'цел'], ['вещ', 'цел'], ['цел', 'вещ']],
         'handler': lambda visitor_self, args, ctx: bf.handle_random_real(visitor_self, args[0], args[1], ctx)
    },
    'div': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['цел', 'цел']],
        'handler': lambda visitor_self, args, ctx: div(args[0], args[1]) 
    },
    'mod': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['цел', 'цел']],
        'handler': lambda visitor_self, args, ctx: mod(args[0], args[1]) 
    },
    'irand': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['цел', 'цел']], 
        'handler': lambda visitor_self, args, ctx: bf.handle_irand(visitor_self, args[0], args[1], ctx) 
    },
    'rand': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['вещ', 'цел'], ['вещ', 'цел']], # Оригинал был [['вещ', 'цел'], ['вещ', 'цел']], уточнил по math_functions.rand, он принимает (Any, Any)
        'handler': lambda visitor_self, args, ctx: bf.handle_rand(visitor_self, args[0], args[1], ctx)
    },
    # --- Математические функции (конец) ---

    # --- Функции для работы с символами (начало) ---
    # \'симвкод\': {
    #     \'min_args\': 1, \'max_args\': 1,
    #     \'arg_types\': [[\'сим\']],
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_char_code(visitor_self, args[0], ctx)
    # },
    # \'кодсимв\': {
    #     \'min_args\': 1, \'max_args\': 1,
    #     \'arg_types\': [[\'цел\']],
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_code_char(visitor_self, args[0], ctx)
    # },
    # --- Функции для работы с символами (конец) ---

    # --- Функции для работы со строками (начало) ---
    # \'длина\': {
    #     \'min_args\': 1, \'max_args\': 1,
    #     \'arg_types\': [[\'лит\']],
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_length(visitor_self, args[0], ctx)
    # },
    # \'копировать\': {
    #     \'min_args\': 3, \'max_args\': 3,
    #     \'arg_types\': [[\'лит\', \'цел\', \'цел\']],
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_copy(visitor_self, args[0], args[1], args[2], ctx)
    # },
    # \'найти\': {
    #     \'min_args\': 2, \'max_args\': 2, # TODO: Проверить, есть ли вариант с 3 аргументами (начальная позиция)
    #     \'arg_types\': [[\'лит\', \'лит\']], # TODO: Добавить [[\'лит\', \'лит\', \'цел\']] если есть
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_find(visitor_self, args[0], args[1], ctx) # TODO: Добавить args[2] если есть
    # },
    # \'удалить\': { # Это процедура, а не функция. Должна быть в BUILTIN_PROCEDURES
    #     \'min_args\': 3, \'max_args\': 3,
    #     \'arg_types\': [[\'лит\', \'цел\', \'цел\']], # Первый аргумент - переменная, тип \'лит арг рез\'
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_delete_string_part(visitor_self, args[0], args[1], args[2], ctx)
    # },
    # \'вставить\': { # Это процедура, а не функция. Должна быть в BUILTIN_PROCEDURES
    #     \'min_args\': 3, \'max_args\': 3,
    #     \'arg_types\': [[\'лит\', \'лит\', \'цел\']], # Первый аргумент - переменная, тип \'лит арг рез\'
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_insert_string_part(visitor_self, args[0], args[1], args[2], ctx)
    # },
    # --- Функции для работы со строками (конец) ---

    # --- Функции для работы с таблицами (начало) ---
    # \'размер\': { # Может быть и для строк, и для таблиц
    #     \'min_args\': 1, \'max_args\': 2, # Для таблиц может быть 2 аргумента (имя таблицы, номер измерения)
    #     \'arg_types\': [[\'лит\'], [\'таб\'], [\'таб\', \'цел\']], # TODO: Уточнить типы для таблиц
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_size(visitor_self, args, ctx) # args будет списком
    # },
    # \'нразм\': { # Для таблиц
    #     \'min_args\': 1, \'max_args\': 1,
    #     \'arg_types\': [[\'таб\']], # TODO: Уточнить тип для таблиц
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_dimensions_count(visitor_self, args[0], ctx)
    # },
    # \'максиндекс\': { # Для таблиц
    #     \'min_args\': 1, \'max_args\': 2,
    #     \'arg_types\': [[\'таб\'], [\'таб\', \'цел\']], # TODO: Уточнить типы
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_max_index(visitor_self, args, ctx)
    # },
    # \'мининдекс\': { # Для таблиц
    #     \'min_args\': 1, \'max_args\': 2,
    #     \'arg_types\': [[\'таб\'], [\'таб\', \'цел\']], # TODO: Уточнить типы
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_min_index(visitor_self, args, ctx)
    # },
    # --- Функции для работы с таблицами (конец) ---

    # --- Функции для работы с файлами (начало) ---
    # \'eof\': { # End Of File
    #     \'min_args\': 1, \'max_args\': 1,
    #     \'arg_types\': [[\'файл\']], # TODO: Уточнить тип "файл"
    #     \'handler\': lambda visitor_self, args, ctx: bf.handle_eof(visitor_self, args[0], ctx)
    # },
    # --- Функции для работы с файлами (конец) ---
}


# TODO: Создать аналогичный словарь BUILTIN_PROCEDURES для встроенных процедур
# например, \'ввод\', \'вывод\', \'нс\', \'кс\', \'открыть для чтения\', \'закрыть для чтения\' и т.д.
# \'удалить\' и \'вставить\' для строк тоже должны быть здесь.

class BuiltinFunctionHandler:
    def __init__(self, visitor: 'KumirInterpreterVisitor'):
        self.visitor = visitor
        self.functions = BUILTIN_FUNCTIONS

    def call_function(self, func_name: str, args: List[Any], ctx: Optional['ParserRuleContext']) -> Any:
        # TODO: Реализовать логику вызова встроенной функции,
        # включая проверку имени, количества и типов аргументов.
        # Сейчас это просто заглушка.
        if func_name.lower() in self.functions:
            func_info = self.functions[func_name.lower()]
            # Здесь должна быть проверка аргументов и вызов func_info['handler']
            # Пока что просто вернем None или вызовем ошибку
            # raise NotImplementedError(f"Builtin function \'{func_name}\' handler not fully implemented yet.")
            # Для примера, если handler есть:
            if 'handler' in func_info and callable(func_info['handler']):
                 # Проверка количества аргументов (упрощенная)
                min_args = func_info.get('min_args', 0)
                max_args = func_info.get('max_args', float('inf'))
                if not (min_args <= len(args) <= max_args):
                    raise RuntimeError(f"Функция \'{func_name}\' ожидает от {min_args} до {max_args} аргументов, получено {len(args)}.") # Заменить на KumirArgumentError
                
                # TODO: Проверка типов аргументов (arg_types)
                
                return func_info['handler'](self.visitor, args, ctx)
            else:
                raise NotImplementedError(f"Handler for builtin function \'{func_name}\' is not callable or defined.")

        raise NameError(f"Встроенная функция \'{func_name}\' не найдена.") # Заменить на KumirNameError

class BuiltinProcedureHandler:
    def __init__(self, visitor: 'KumirInterpreterVisitor'):
        self.visitor = visitor
        # self.procedures = BUILTIN_PROCEDURES # Когда будет создан

    def call_procedure(self, proc_name: str, args: List[Any], ctx: Optional['ParserRuleContext']) -> None:
        # TODO: Реализовать логику вызова встроенной процедуры.
        # Сейчас это просто заглушка.
        # raise NotImplementedError(f"Builtin procedure \'{proc_name}\' handler not implemented yet.")
        # Пример:
        # if proc_name.lower() == "вывод":
        #     self.visitor.io_handler.handle_output(args, ctx) # Предполагая, что io_handler есть у visitor
        # else:
        #     raise NameError(f"Встроенная процедура \'{proc_name}\' не найдена.") # Заменить на KumirNameError
        pass # Пока заглушка