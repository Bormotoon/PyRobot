# Этот файл будет содержать словарь BUILTIN_FUNCTIONS и, возможно, некоторые из их хендлеров.

# Пока что оставим импорты пустыми, добавим по мере необходимости
# from ..kumir_exceptions import ...
# from . import builtin_functions as bf # Если хендлеры в другом файле
# import math

# TODO: Перенести сюда импорты KumirLexer, типы (INTEGER_TYPE и т.д.) и bf, если он не будет импортироваться извне
# TODO: Также перенести сюда math_functions (div, mod, irand, rand), если они используются напрямую в лямбдах

from typing import TYPE_CHECKING, Any, Optional, Callable, Dict, List

# Импортируем хендлеры из соседнего модуля
from . import builtin_functions as bf
# Импортируем напрямую используемые функции
from ..math_functions import div, mod 

if TYPE_CHECKING:
    from pyrobot.backend.kumir_interpreter.interpreter_components.main_visitor import KumirInterpreterVisitor # Для аннотации типов visitor_self
    from antlr4 import ParserRuleContext

# Типы для лямбда-функций
HandlerFunc = Callable[['KumirInterpreterVisitor', List[Any], Optional['ParserRuleContext']], Any]

# Вспомогательные функции для создания типизированных лямбд
def make_handler_1arg(handler_func: Callable[['KumirInterpreterVisitor', Any, Optional['ParserRuleContext']], Any]) -> HandlerFunc:
    return lambda visitor_self, args, ctx: handler_func(visitor_self, args[0], ctx)

def make_handler_2arg(handler_func: Callable[['KumirInterpreterVisitor', Any, Any, Optional['ParserRuleContext']], Any]) -> HandlerFunc:
    return lambda visitor_self, args, ctx: handler_func(visitor_self, args[0], args[1], ctx)

def make_math_handler_2arg(math_func: Callable[[Any, Any], Any]) -> HandlerFunc:
    return lambda visitor_self, args, ctx: math_func(args[0], args[1])

def make_lit_to_int_handler(visitor_self: 'KumirInterpreterVisitor', args: List[Any], ctx: Optional['ParserRuleContext']) -> Any:
    if len(args) == 1:
        return bf.handle_lit_to_int(visitor_self, args[0], ctx)
    else:
        return bf.handle_lit_to_int_with_success(visitor_self, args[0], args[1], ctx)

def make_lit_to_real_handler(visitor_self: 'KumirInterpreterVisitor', args: List[Any], ctx: Optional['ParserRuleContext']) -> Any:
    if len(args) == 1:
        return bf.handle_lit_to_real(visitor_self, args[0], ctx)
    else:
        return bf.handle_lit_to_real_with_success(visitor_self, args[0], args[1], ctx)

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
        'handler': make_handler_1arg(bf.handle_sqrt)
    },
    'sin': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': make_handler_1arg(bf.handle_sin)
    },
    'cos': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': make_handler_1arg(bf.handle_cos)
    },
    'tan': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': make_handler_1arg(bf.handle_tan)
    },
    'arctan': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': make_handler_1arg(bf.handle_arctan)
    },
    'int': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': make_handler_1arg(bf.handle_int_conversion)
    },
    'abs': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': make_handler_1arg(bf.handle_abs)
    },
    'sign': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ', 'цел']],
        'handler': make_handler_1arg(bf.handle_sign)
    },
    'случайноецелое': { 
         'min_args': 2, 'max_args': 2,
         'arg_types': [['цел', 'цел']],
         'handler': make_handler_2arg(bf.handle_random_integer)
    },
    'случайноевещественное': { 
         'min_args': 2, 'max_args': 2,
         'arg_types': [['вещ', 'вещ'], ['цел', 'цел'], ['вещ', 'цел'], ['цел', 'вещ']],
         'handler': make_handler_2arg(bf.handle_random_real)
    },
    'div': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['цел', 'цел']],
        'handler': make_math_handler_2arg(div)
    },
    'mod': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['цел', 'цел']],
        'handler': make_math_handler_2arg(mod)
    },
    'irand': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['цел', 'цел']], 
        'handler': make_handler_2arg(bf.handle_irand)
    },
    'rand': { 
        'min_args': 2, 'max_args': 2,
        'arg_types': [['вещ', 'цел'], ['вещ', 'цел']], # Оригинал был [['вещ', 'цел'], ['вещ', 'цел']], уточнил по math_functions.rand, он принимает (Any, Any)
        'handler': make_handler_2arg(bf.handle_rand)
    },
    # --- Математические функции (конец) ---

    # --- Строковые функции (начало) ---
    'длин': { 
        'min_args': 1, 'max_args': 1,
        'arg_types': [['лит']],
        'handler': make_handler_1arg(bf.handle_length)
    },
    'позиция': {
        'min_args': 2, 'max_args': 2,
        'arg_types': [['лит', 'лит']],
        'handler': make_handler_2arg(bf.handle_position)
    },
    'поз': { # Сокращенный вариант для "позиция"
        'min_args': 2, 'max_args': 2,
        'arg_types': [['лит', 'лит']],
        'handler': make_handler_2arg(bf.handle_position)
    },
    'лит_в_цел': {
        'min_args': 1, 'max_args': 2, # может быть с параметром успех или без
        'arg_types': [['лит'], ['лит', 'лог']], 
        'param_modes': [['арг'], ['арг', 'рез']], # первый параметр - арг, второй (если есть) - рез
        'handler': make_lit_to_int_handler
    },
    'лит_в_вещ': {
        'min_args': 1, 'max_args': 2,
        'arg_types': [['лит'], ['лит', 'лог']], 
        'param_modes': [['арг'], ['арг', 'рез']], # первый параметр - арг, второй (если есть) - рез
        'handler': make_lit_to_real_handler
    },
    'цел_в_лит': {
        'min_args': 1, 'max_args': 1,
        'arg_types': [['цел']],
        'handler': make_handler_1arg(bf.handle_int_to_lit)
    },
    'вещ_в_лит': {
        'min_args': 1, 'max_args': 1,
        'arg_types': [['вещ']],
        'handler': make_handler_1arg(bf.handle_real_to_lit)
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
        # Создаем копию встроенных функций для возможности добавления новых
        self.functions = BUILTIN_FUNCTIONS.copy()
        self.custom_handlers = {}  # Для кастомных обработчиков

    def register_function(self, name: str, handler: Callable[[], Any]) -> None:
        """Регистрирует новую функцию с обработчиком."""
        name_lower = name.lower()
        
        def typed_handler(visitor_self: 'KumirInterpreterVisitor', args: List[Any], ctx: Optional['ParserRuleContext']) -> Any:
            return handler()
        
        self.functions[name_lower] = {
            'min_args': 0,
            'max_args': 0,
            'arg_types': [],
            'handler': typed_handler
        }

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
        # Создаем копию встроенных процедур для возможности добавления новых
        self.procedures = BUILTIN_PROCEDURES.copy()
        self.custom_handlers = {}  # Для кастомных обработчиков
    
    def register_procedure(self, name: str, handler: Callable[[], None]):
        """Регистрирует новую процедуру с обработчиком."""
        name_lower = name.lower()
        self.procedures[name_lower] = {
            'params': [],  # Роботные команды без параметров
            'handler': f'custom_{name_lower}'
        }
        self.custom_handlers[f'custom_{name_lower}'] = handler

    def call_procedure(self, proc_name: str, analyzed_args: List[Dict[str, Any]], ctx: Optional['ParserRuleContext']) -> None:
        """Вызывает встроенную процедуру с проанализированными аргументами."""
        proc_name_lower = proc_name.lower()
        
        if proc_name_lower not in self.procedures:
            raise NameError(f"Встроенная процедура '{proc_name}' не найдена.")
        
        proc_info = self.procedures[proc_name_lower]
        handler_name = proc_info['handler']
        
        # Проверяем, является ли это кастомным обработчиком
        if handler_name in self.custom_handlers:
            # Вызываем кастомный обработчик
            self.custom_handlers[handler_name]()
            return
        
        # Импортируем модуль с обработчиками для встроенных процедур
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
        
    def get_procedure_info(self, proc_name: str) -> Dict[str, Any]:
        """Возвращает информацию о встроенной процедуре."""
        proc_name_lower = proc_name.lower()
        if proc_name_lower in self.procedures:
            return self.procedures[proc_name_lower]
        return {}