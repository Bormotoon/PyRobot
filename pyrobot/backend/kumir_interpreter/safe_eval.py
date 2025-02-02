# safe_eval.py
import math
from identifiers import convert_hex_constants
from builtins import цел_в_лит, вещ_в_лит, лит_в_вещ, лит_в_цел, Цел, Вещ, Лог
from math_functions import (
    sqrt, abs_val, iabs, sign,
    sin_val, cos_val, tg, ctg, arcsin_val, arccos_val, arctg, arcctg,
    ln, lg, exp_val,
    min_val, max_val, imin, imax, div, mod, int_part,
    rnd, rand, irnd, irand, МАКСЦЕЛ, МАКСВЕЩ
)
from text_functions import длин, код, юникод, символ, юнисимвол


def safe_eval(expr, eval_env):
    """
    Вычисляет выражение с использованием безопасного окружения.
    Перед вычислением заменяет шестнадцатеричные константы.
    """
    expr = convert_hex_constants(expr)
    safe_globals = {
        "__builtins__": None,
        # Математические функции
        "sin": sin_val,
        "cos": cos_val,
        "sqrt": sqrt,
        "int": int_part,  # для языка Кумир функция int возвращает целую часть
        "float": float,
        # Функции преобразования чисел (из builtins.py)
        "цел_в_лит": цел_в_лит,
        "вещ_в_лит": вещ_в_лит,
        "лит_в_вещ": лит_в_вещ,
        "лит_в_цел": лит_в_цел,
        "Цел": Цел,
        "Вещ": Вещ,
        "Лог": Лог,
        # Дополнительные математические функции из math_functions.py
        "abs": abs_val,
        "iabs": iabs,
        "sign": sign,
        "tg": tg,
        "ctg": ctg,
        "arcsin": arcsin_val,
        "arccos": arccos_val,
        "arctg": arctg,
        "arcctg": arcctg,
        "ln": ln,
        "lg": lg,
        "exp": exp_val,
        "min": min_val,
        "max": max_val,
        "imin": imin,
        "imax": imax,
        "div": div,
        "mod": mod,
        "rnd": rnd,
        "rand": rand,
        "irnd": irnd,
        "irand": irand,
        "МАКСЦЕЛ": МАКСЦЕЛ,
        "МАКСВЕЩ": МАКСВЕЩ,
        # Функции обработки текста из text_functions.py
        "длин": длин,
        "код": код,
        "юникод": юникод,
        "символ": символ,
        "юнисимвол": юнисимвол,
    }
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    """
    Формирует словарь для вычисления выражений из окружения.
    Окружение представлено в виде: env[var_name] = {"type": ..., "value": ...}
    """
    result = {}
    for var, info in env.items():
        result[var] = info.get("value")
    return result
