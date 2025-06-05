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
    'поз': { # Сокращенный вариант для "позиция"
        'min_args': 2, 'max_args': 2,
        'arg_types': [['лит', 'лит']],
        'handler': lambda visitor_self, args, ctx: bf.handle_position(visitor_self, args[0], args[1], ctx)
    },
    'лит_в_цел': {
        'min_args': 1, 'max_args': 2, # может быть с параметром успех или без
        'arg_types': [['лит'], ['лит', 'лог']], # TODO: нужно уточнить формат для рез параметров
        'handler': lambda visitor_self, args, ctx: bf.handle_lit_to_int(visitor_self, args[0], ctx) if len(args) == 1 else bf.handle_lit_to_int_with_success(visitor_self, args[0], args[1], ctx)
    },
    'лит_в_вещ': {
        'min_args': 1, 'max_args': 2,
        'arg_types': [['лит'], ['лит', 'лог']], 
        'handler': lambda visitor_self, args, ctx: bf.handle_lit_to_real(visitor_self, args[0], ctx) if len(args) == 1 else bf.handle_lit_to_real_with_success(visitor_self, args[0], args[1], ctx)
    },
    'цел_в_лит': {
        'min_args': 1, 'max_args': 1,
        'arg_types': [['цел']],
        'handler': lambda visitor_self, args, ctx: bf.handle_int_to_lit(visitor_self, args[0], ctx)
    },
    'вещ_в_лит': {
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ']],
        'handler': lambda visitor_self, args, ctx: bf.handle_real_to_lit(visitor_self, args[0], ctx)
    },
    # --- Строковые функции (конец) ---

    # --- Функции модуля "Строки" (начало) ---
    # TODO: эти функции нужно добавить при подключении "использовать Строки"
    # ПРИМЕЧАНИЕ: удалить и вставить перенесены в BUILTIN_PROCEDURES
    # --- Функции модуля "Строки" (конец) ---

    # --- Математические функции (начало) ---
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

# Словарь встроенных процедур Кумира
BUILTIN_PROCEDURES = {
    # --- Процедуры модуля "Строки" (начало) ---
    'удалить': {
        'params': [
            {'name': 'строка', 'type': 'лит', 'mode': 'аргрез'},
            {'name': 'начало', 'type': 'цел', 'mode': 'арг'},
            {'name': 'количество', 'type': 'цел', 'mode': 'арг'}
        ],
        'handler': 'handle_delete_substring_procedure'
    },
    'вставить': {
        'params': [
            {'name': 'фрагмент', 'type': 'лит', 'mode': 'арг'},
            {'name': 'строка', 'type': 'лит', 'mode': 'аргрез'},
            {'name': 'начало', 'type': 'цел', 'mode': 'арг'}
        ],
        'handler': 'handle_insert_substring_procedure'
    }
    # --- Процедуры модуля "Строки" (конец) ---
}

class BuiltinProcedureHandler:
    def __init__(self, visitor: 'KumirInterpreterVisitor'):
        self.visitor = visitor
        self.procedures = BUILTIN_PROCEDURES

    def call_procedure(self, proc_name: str, analyzed_args: List[Dict], ctx: Optional['ParserRuleContext']) -> None:
        """Вызывает встроенную процедуру с проанализированными аргументами."""
        proc_name_lower = proc_name.lower()
        
        if proc_name_lower not in self.procedures:
            raise NameError(f"Встроенная процедура '{proc_name}' не найдена.")
        
        proc_info = self.procedures[proc_name_lower]
        handler_name = proc_info['handler']
        
        # Импортируем модуль с обработчиками
        from . import builtin_functions as bf
        
        # Получаем функцию-обработчик
        if hasattr(bf, handler_name):
            handler_func = getattr(bf, handler_name)
            
            # Вызываем обработчик с проанализированными аргументами
            handler_func(self.visitor, analyzed_args, ctx)
        else:
            raise NotImplementedError(f"Обработчик '{handler_name}' для процедуры '{proc_name}' не реализован.")

    def is_builtin_procedure(self, proc_name: str) -> bool:
        """Проверяет, является ли процедура встроенной."""
        return proc_name.lower() in self.procedures
        
    def get_procedure_info(self, proc_name: str) -> Dict:
        """Возвращает информацию о встроенной процедуре."""
        proc_name_lower = proc_name.lower()
        if proc_name_lower in self.procedures:
            return self.procedures[proc_name_lower]
        return {}