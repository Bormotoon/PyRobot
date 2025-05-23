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

    # --- Строковые функции (начало) ---
    'длин': {
        'min_args': 1, 'max_args': 1,
        'arg_types': [['лит']],
        'handler': lambda visitor_self, args, ctx: bf.handle_length(visitor_self, args[0], ctx)
    },
    'позиция': {
        'min_args': 2, 'max_args': 2,
        'arg_types': [['лит', 'лит']],
        'handler': lambda visitor_self, args, ctx: bf.handle_position(visitor_self, args[0], args[1], ctx)
    },
    'поз': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['лит', 'лит']],
        'handler': lambda visitor_self, args, ctx: bf.handle_position(visitor_self, args[0], args[1], ctx)
    },
    'лит_в_цел': {
        'min_args': 1, 'max_args': 1, 
        'arg_types': [['лит']],
        'handler': lambda visitor_self, args, ctx: bf.handle_lit_to_int(visitor_self, args[0], ctx)
    },
    # --- Строковые функции (конец) ---

    # --- Функции ввода/вывода (начало) ---
    # Эти хендлеры (_handle_input, _handle_output) являются методами KumirInterpreterVisitor
    # и сильно завязаны на его состояние (input_stream, output_stream, evaluator и т.д.)
    # Их перенос может быть сложнее, или их нужно будет вызывать через visitor_self.
    'input': {
        'min_args': 1, 'max_args': 1,
        'arg_types': [['лит']],
        'handler': lambda visitor_self, args, ctx: visitor_self._handle_input(args[0], ctx)
    },
    'output': {
        'min_args': 1, 'max_args': 1,
        'arg_types': [['лит']],
        'handler': lambda visitor_self, args, ctx: visitor_self._handle_output(args[0], ctx)
    },
    # --- Функции ввода/вывода (конец) ---
} 