# safe_eval.py

import math
from identifiers import convert_hex_constants


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
    }
    return eval(expr, safe_globals, eval_env)


def get_eval_env(env):
    """
    Формирует словарь для вычисления выражений из нашего окружения,
    где каждое объявление имеет формат: env[var_name] = {"type": ..., "value": ...}
    """
    result = {}
    for var, info in env.items():
        result[var] = info.get("value")
    return result
