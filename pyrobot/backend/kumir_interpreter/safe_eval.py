# safe_eval.py

import math
from identifiers import convert_hex_constants
# Импортируем наши встроенные функции
from builtins import цел_в_лит, вещ_в_лит, лит_в_вещ, лит_в_цел, Цел, Вещ, Лог


def safe_eval(expr, eval_env):
    """
    Вычисляет выражение с использованием безопасного окружения.
    Перед вычислением заменяет шестнадцатеричные константы.
    """
    expr = convert_hex_constants(expr)
    safe_globals = {
        "__builtins__": None,
        "sin": math.sin,
        "cos": math.cos,
        "sqrt": math.sqrt,
        "int": int,
        "float": float,
        # Добавляем встроенные функции языка КУМИР:
        "цел_в_лит": цел_в_лит,
        "вещ_в_лит": вещ_в_лит,
        "лит_в_вещ": лит_в_вещ,
        "лит_в_цел": лит_в_цел,
        "Цел": Цел,
        "Вещ": Вещ,
        "Лог": Лог,
    }
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    """
    Формирует словарь для вычисления выражений из нашего окружения.
    Окружение представлено в виде: env[var_name] = {"type": ..., "value": ...}
    """
    result = {}
    for var, info in env.items():
        result[var] = info.get("value")
    return result
