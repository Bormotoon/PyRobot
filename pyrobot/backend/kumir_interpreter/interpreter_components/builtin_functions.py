# Built-in functions, their handlers, and the BUILTIN_FUNCTIONS dictionary 
import math
import random
from typing import TYPE_CHECKING, Any, Optional, List, Dict
from antlr4 import ParserRuleContext

if TYPE_CHECKING:
    from pyrobot.backend.kumir_interpreter.interpreter_components.main_visitor import KumirInterpreterVisitor # Для аннотации типов, избегаем циклического импорта

from ..kumir_exceptions import KumirArgumentError, KumirEvalError
from ..kumir_datatypes import KumirValue, KumirType
from ..math_functions import irand as kumir_irand, rand as kumir_rand # Импортируем с псевдонимами

# --- Математические функции ---

def handle_sqrt(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> float:
    if not isinstance(arg, (int, float)): # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Функция 'sqrt' ожидает числовой аргумент, получено: {type(arg).__name__}",
            line_index=ctx.start.line -1 if ctx else None, 
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    if arg < 0:
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirEvalError(
            "Арифметическая ошибка: корень из отрицательного числа.",
            line_index=ctx.start.line -1 if ctx else None, 
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    return math.sqrt(float(arg))

def handle_sin(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> float:
    if not isinstance(arg, (int, float)): # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Функция 'sin' ожидает числовой аргумент, получено: {type(arg).__name__}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    return math.sin(float(arg))

def handle_cos(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> float:
    if not isinstance(arg, (int, float)): # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Функция 'cos' ожидает числовой аргумент, получено: {type(arg).__name__}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    return math.cos(float(arg))

def handle_tan(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> float:
    if not isinstance(arg, (int, float)): # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Функция 'tan' ожидает числовой аргумент, получено: {type(arg).__name__}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    return math.tan(float(arg))

def handle_arctan(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> float:
    if not isinstance(arg, (int, float)): # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Функция 'arctan' ожидает числовой аргумент, получено: {type(arg).__name__}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    return math.atan(float(arg))

def handle_sign(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> int:
    if not isinstance(arg, (int, float)): # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Функция 'sign' ожидает числовой аргумент, получено: {type(arg).__name__}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    if arg > 0: return 1
    if arg < 0: return -1
    return 0

def handle_random_integer(visitor: 'KumirInterpreterVisitor', a: int, b: int, ctx: Optional[ParserRuleContext]) -> int:
    if a > b:
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"В функции 'случайноецелое' первый аргумент ({a}) не должен превышать второй ({b}).",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    return random.randint(a, b)

def handle_random_real(visitor: 'KumirInterpreterVisitor', a: Any, b: Any, ctx: Optional[ParserRuleContext]) -> float:
    val_a = float(a)
    val_b = float(b)
    if val_a > val_b:
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"В функции 'случайноевещественное' первый аргумент ({val_a}) не должен превышать второй ({val_b}).",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    return random.uniform(val_a, val_b)

# --- Функции из math_functions, которые раньше были _handle_... методами ---
def handle_irand(visitor: 'KumirInterpreterVisitor', a: int, b: int, ctx: Optional[ParserRuleContext]) -> int:
    try:
        return kumir_irand(a,b)
    except KumirArgumentError as e:
        e.line_index = ctx.start.line - 1 if ctx else None
        e.column_index = ctx.start.column if ctx else None
        e.line_content = visitor.get_line_content_from_ctx(ctx)
        raise e
    except Exception as e_gen: # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirEvalError(
            f"Ошибка при вызове irand: {e_gen}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )

def handle_rand(visitor: 'KumirInterpreterVisitor', a: Any, b: Any, ctx: Optional[ParserRuleContext]) -> float:
    try:
        return kumir_rand(a,b)
    except (KumirArgumentError, KumirEvalError) as e: 
        e.line_index = ctx.start.line - 1 if ctx else None
        e.column_index = ctx.start.column if ctx else None
        e.line_content = visitor.get_line_content_from_ctx(ctx)
        raise e
    except Exception as e_gen: # pragma: no cover
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirEvalError(
            f"Ошибка при вызове rand: {e_gen}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )

# --- Строковые функции ---
def handle_lit_to_int(visitor: 'KumirInterpreterVisitor', s_val: str, ctx: Optional[ParserRuleContext]) -> int:
    if s_val.startswith('$'):
        hex_val = s_val[1:]
        if not hex_val: 
            l_content = visitor.get_line_content_from_ctx(ctx)
            raise KumirEvalError(
                f"Неверный формат шестнадцатеричного числа: '{s_val}'. Отсутствуют цифры после '$'.",
                line_index=ctx.start.line -1 if ctx else None, 
                column_index=ctx.start.column if ctx else None,
                line_content=l_content
            )
        try:
            return int(hex_val, 16)
        except ValueError:
            l_content = visitor.get_line_content_from_ctx(ctx)
            raise KumirEvalError(
                f"Неверный формат шестнадцатеричного числа: '{s_val}'. Содержит недопустимые символы.",
                line_index=ctx.start.line -1 if ctx else None, 
                column_index=ctx.start.column if ctx else None,
                line_content=l_content
            )
    try:
        cleaned_s_val = s_val.strip()
        if not cleaned_s_val: 
            l_content = visitor.get_line_content_from_ctx(ctx)
            raise KumirEvalError(
                f"Невозможно преобразовать пустую или содержащую только пробелы строку в целое число.",
                line_index=ctx.start.line -1 if ctx else None,
                column_index=ctx.start.column if ctx else None,
                line_content=l_content
            )
        return int(cleaned_s_val)
    except ValueError:
        l_content = visitor.get_line_content_from_ctx(ctx)
        details = "содержит нечисловые символы"
        if "." in s_val or "," in s_val:
            details = "похоже на вещественное число, а не целое"
        raise KumirEvalError(
            f"Невозможно преобразовать строку '{s_val}' в целое число: {details}.",
            line_index=ctx.start.line -1 if ctx else None, 
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )

def handle_int_conversion(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> int:
    return int(arg)

def handle_abs(visitor: 'KumirInterpreterVisitor', arg: Any, ctx: Optional[ParserRuleContext]) -> Any:
    return abs(arg)

def handle_length(visitor: 'KumirInterpreterVisitor', arg: str, ctx: Optional[ParserRuleContext]) -> int:
    return len(arg)

def handle_position(visitor: 'KumirInterpreterVisitor', sub_string: str, main_string: str, ctx: Optional[ParserRuleContext]) -> int:
    if not sub_string:
        return 1 if main_string else 0
    find_result = main_string.find(sub_string)
    if find_result != -1:
        return find_result + 1
    else:
        return 0

# --- Строковые функции преобразования ---

def handle_lit_to_int_with_success(visitor: 'KumirInterpreterVisitor', s_val: str, success_var, ctx: Optional[ParserRuleContext]) -> int:
    """Обработчик для функции лит_в_цел(строка, рез лог успех)."""
    try:
        result = int(s_val.strip())
        # Устанавливаем успех в True
        success_value = KumirValue(True, KumirType.BOOL.value)
        visitor.scope_manager.update_variable(success_var, success_value, 
                                           ctx.start.line - 1 if ctx else 0, 
                                           ctx.start.column if ctx else 0)
        return result
    except ValueError:
        # Устанавливаем успех в False
        success_value = KumirValue(False, KumirType.BOOL.value)
        visitor.scope_manager.update_variable(success_var, success_value,
                                           ctx.start.line - 1 if ctx else 0, 
                                           ctx.start.column if ctx else 0)
        return 0

def handle_lit_to_real(visitor: 'KumirInterpreterVisitor', s_val: str, ctx: Optional[ParserRuleContext]) -> float:
    """Обработчик для функции лит_в_вещ(строка)."""
    try:
        # В КуМире может быть запятая как десятичный разделитель
        cleaned_s = s_val.strip().replace(',', '.')
        return float(cleaned_s)
    except ValueError:
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirEvalError(
            f"Невозможно преобразовать строку '{s_val}' в вещественное число.",
            line_index=ctx.start.line -1 if ctx else None, 
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )

def handle_lit_to_real_with_success(visitor: 'KumirInterpreterVisitor', s_val: str, success_var, ctx: Optional[ParserRuleContext]) -> float:
    """Обработчик для функции лит_в_вещ(строка, рез лог успех)."""
    try:
        cleaned_s = s_val.strip().replace(',', '.')
        result = float(cleaned_s)
        # Устанавливаем успех в True
        success_value = KumirValue(True, KumirType.BOOL.value)
        visitor.scope_manager.update_variable(success_var, success_value,
                                           ctx.start.line - 1 if ctx else 0, 
                                           ctx.start.column if ctx else 0)
        return result
    except ValueError:
        # Устанавливаем успех в False
        success_value = KumirValue(False, KumirType.BOOL.value)
        visitor.scope_manager.update_variable(success_var, success_value,
                                           ctx.start.line - 1 if ctx else 0, 
                                           ctx.start.column if ctx else 0)
        return 0.0

def handle_int_to_lit(visitor: 'KumirInterpreterVisitor', int_val: int, ctx: Optional[ParserRuleContext]) -> str:
    """Обработчик для функции цел_в_лит(число)."""
    return str(int_val)

def handle_real_to_lit(visitor: 'KumirInterpreterVisitor', real_val: float, ctx: Optional[ParserRuleContext]) -> str:
    """Обработчик для функции вещ_в_лит(число)."""
    return str(real_val)

# --- Функции модуля "Строки" ---

def handle_delete_substring(visitor: 'KumirInterpreterVisitor', target_str: str, start_pos: int, count: int, ctx: Optional[ParserRuleContext]) -> str:
    """Обработчик для процедуры удалить(аргрез лит строка, арг цел начало, арг цел количество)."""
    if start_pos < 1:
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Начальная позиция должна быть >= 1, получено: {start_pos}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    
    if start_pos > len(target_str):
        return target_str  # Ничего не удаляем, если позиция за концом строки
        
    # Преобразуем в 0-based индексы
    start_idx = start_pos - 1
    end_idx = min(start_idx + count, len(target_str))
    
    # Возвращаем строку без удаленной части
    return target_str[:start_idx] + target_str[end_idx:]

def handle_insert_substring(visitor: 'KumirInterpreterVisitor', fragment: str, target_str: str, start_pos: int, ctx: Optional[ParserRuleContext]) -> str:
    """Обработчик для процедуры вставить(лит фрагмент, аргрез лит строка, арг цел начало)."""
    if start_pos < 1:
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Позиция для вставки должна быть >= 1, получено: {start_pos}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    
    if start_pos > len(target_str) + 1:
        l_content = visitor.get_line_content_from_ctx(ctx)
        raise KumirArgumentError(
            f"Позиция для вставки не может быть больше длины строки + 1. Длина: {len(target_str)}, позиция: {start_pos}",
            line_index=ctx.start.line -1 if ctx else None,
            column_index=ctx.start.column if ctx else None,
            line_content=l_content
        )
    
    # Преобразуем в 0-based индекс
    insert_idx = start_pos - 1
    
    # Вставляем фрагмент
    return target_str[:insert_idx] + fragment + target_str[insert_idx:]

# --- Новые обработчики процедур ---

def handle_delete_substring_procedure(visitor: 'KumirInterpreterVisitor', analyzed_args: List[Dict[str, Any]], ctx: Optional[ParserRuleContext]) -> None:
    """Обработчик процедуры удалить(аргрез лит строка, арг цел начало, арг цел количество)."""
    # analyzed_args[0] - строка (аргрез)
    # analyzed_args[1] - начало (арг) 
    # analyzed_args[2] - количество (арг)
    
    if len(analyzed_args) != 3:
        raise KumirArgumentError(f"Процедура 'удалить' ожидает 3 аргумента, получено {len(analyzed_args)}")
    
    # Извлекаем аргументы
    string_arg = analyzed_args[0]
    start_arg = analyzed_args[1] 
    count_arg = analyzed_args[2]
    
    # Получаем значения
    if string_arg['mode'] != 'аргрез':
        raise KumirArgumentError("Первый параметр процедуры 'удалить' должен быть 'аргрез'")
    
    current_string = string_arg['variable_info']['current_value']
    start_pos = start_arg['value']
    count = count_arg['value']
    
    # Валидируем типы и извлекаем значения из KumirValue, если необходимо
    if hasattr(current_string, 'value'):  # KumirValue
        current_string = current_string.value
    if not isinstance(current_string, str):
        current_string = str(current_string)
        
    if hasattr(start_pos, 'value'):  # KumirValue
        start_pos = start_pos.value
    if not isinstance(start_pos, int):
        start_pos = int(start_pos)
        
    if hasattr(count, 'value'):  # KumirValue
        count = count.value
    if not isinstance(count, int):
        count = int(count)
    
    # Выполняем удаление
    result_string = handle_delete_substring(visitor, current_string, start_pos, count, ctx)
    
    # Обновляем исходную переменную (оборачиваем в KumirValue)
    kumir_result = KumirValue(result_string, KumirType.STR.value)
    var_name = string_arg['variable_info']['name']
    visitor.scope_manager.update_variable(
        var_name,
        kumir_result,
        line_index=ctx.start.line - 1 if ctx and ctx.start else 0,
        column_index=ctx.start.column if ctx and ctx.start else 0
    )

def handle_insert_substring_procedure(visitor: 'KumirInterpreterVisitor', analyzed_args: List[Dict[str, Any]], ctx: Optional[ParserRuleContext]) -> None:
    """Обработчик процедуры вставить(лит фрагмент, аргрез лит строка, арг цел начало)."""
    # analyzed_args[0] - фрагмент (арг)
    # analyzed_args[1] - строка (аргрез)
    # analyzed_args[2] - начало (арг)
    
    if len(analyzed_args) != 3:
        raise KumirArgumentError(f"Процедура 'вставить' ожидает 3 аргумента, получено {len(analyzed_args)}")
    
    # Извлекаем аргументы
    fragment_arg = analyzed_args[0]
    string_arg = analyzed_args[1]
    start_arg = analyzed_args[2]
    
    # Получаем значения
    if string_arg['mode'] != 'аргрез':
        raise KumirArgumentError("Второй параметр процедуры 'вставить' должен быть 'аргрез'")
    
    fragment = fragment_arg['value']
    current_string = string_arg['variable_info']['current_value']
    start_pos = start_arg['value']
    
    # Валидируем типы и извлекаем значения из KumirValue, если необходимо
    if hasattr(fragment, 'value'):  # KumirValue
        fragment = fragment.value
    if not isinstance(fragment, str):
        fragment = str(fragment)
        
    if hasattr(current_string, 'value'):  # KumirValue
        current_string = current_string.value
    if not isinstance(current_string, str):
        current_string = str(current_string)
        
    if hasattr(start_pos, 'value'):  # KumirValue
        start_pos = start_pos.value
    if not isinstance(start_pos, int):
        start_pos = int(start_pos)
    
    # Выполняем вставку
    result_string = handle_insert_substring(visitor, fragment, current_string, start_pos, ctx)
    
    # Обновляем исходную переменную (оборачиваем в KumirValue)
    kumir_result = KumirValue(result_string, KumirType.STR.value)
    var_name = string_arg['variable_info']['name']
    visitor.scope_manager.update_variable(
        var_name,
        kumir_result,
        line_index=ctx.start.line - 1 if ctx and ctx.start else 0,
        column_index=ctx.start.column if ctx and ctx.start else 0
    )