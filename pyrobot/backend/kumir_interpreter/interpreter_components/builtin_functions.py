# Built-in functions, their handlers, and the BUILTIN_FUNCTIONS dictionary 
import math
import random
from typing import TYPE_CHECKING, Any, Optional
from antlr4 import ParserRuleContext

if TYPE_CHECKING:
    from ..interpreter import KumirInterpreterVisitor # Для аннотации типов, избегаем циклического импорта

from ..kumir_exceptions import KumirArgumentError, KumirEvalError
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


</rewritten_file> 