# math_functions.py
import math
import random
import sys


def sqrt(x):
    """Возвращает квадратный корень из x (x ≥ 0)."""
    if x < 0:
        raise ValueError("sqrt: аргумент должен быть неотрицательным")
    return math.sqrt(x)


def abs_val(x):
    """Возвращает абсолютное значение x (для вещественных чисел)."""
    return x if x >= 0 else -x


def iabs(x):
    """Возвращает абсолютное значение целого числа x."""
    x = int(x)
    return x if x >= 0 else -x


def sign(x):
    """Возвращает знак числа x: -1, если x < 0; 0, если x = 0; 1, если x > 0."""
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1


def sin_val(x):
    """Возвращает синус числа x."""
    return math.sin(x)


def cos_val(x):
    """Возвращает косинус числа x."""
    return math.cos(x)


def tg(x):
    """Возвращает тангенс числа x."""
    return math.tan(x)


def ctg(x):
    """Возвращает котангенс числа x (определён, если sin(x) ≠ 0)."""
    s = math.sin(x)
    if s == 0:
        raise ValueError("ctg: sin(x) равен 0, операция не определена")
    return math.cos(x) / s


def arcsin_val(x):
    """Возвращает арксинус x (x ∈ [-1, 1])."""
    if x < -1 or x > 1:
        raise ValueError("arcsin: x должен принадлежать отрезку [-1,1]")
    return math.asin(x)


def arccos_val(x):
    """Возвращает арккосинус x (x ∈ [-1, 1])."""
    if x < -1 or x > 1:
        raise ValueError("arccos: x должен принадлежать отрезку [-1,1]")
    return math.acos(x)


def arctg(x):
    """Возвращает арктангенс x."""
    return math.atan(x)


def arcctg(x):
    """Возвращает арккотангенс x. Для x = 0 возвращает π/2."""
    if x == 0:
        return math.pi / 2
    # Можно определить как arctg(1/x) с корректировкой знака
    if x > 0:
        return math.atan(1 / x)
    else:
        return math.atan(1 / x) + math.pi


def ln(x):
    """Возвращает натуральный логарифм числа x (x > 0)."""
    if x <= 0:
        raise ValueError("ln: x должен быть > 0")
    return math.log(x)


def lg(x):
    """Возвращает десятичный логарифм числа x (x > 0)."""
    if x <= 0:
        raise ValueError("lg: x должен быть > 0")
    return math.log10(x)


def exp_val(x):
    """Возвращает значение e^x."""
    return math.exp(x)


def min_val(x, y):
    """Возвращает меньшее из вещественных значений x и y."""
    return x if x < y else y


def max_val(x, y):
    """Возвращает большее из вещественных значений x и y."""
    return x if x > y else y


def imin(x, y):
    """Возвращает меньшее из целых чисел x и y."""
    return int(x) if int(x) < int(y) else int(y)


def imax(x, y):
    """Возвращает большее из целых чисел x и y."""
    return int(x) if int(x) > int(y) else int(y)


def div(x, y):
    """Возвращает целую часть от деления x на y (целочисленное деление)."""
    if y == 0:
        raise ZeroDivisionError("div: деление на ноль")
    return int(x) // int(y)


def mod(x, y):
    """Возвращает остаток от деления x на y."""
    if y == 0:
        raise ZeroDivisionError("mod: деление на ноль")
    return int(x) % int(y)


def int_part(x):
    """Возвращает целую часть числа x (максимальное целое число, не превосходящее x)."""
    return math.floor(x)


def rnd(x):
    """Возвращает случайное вещественное число из интервала [0, x]."""
    return random.random() * x


def rand(x, y):
    """Возвращает случайное вещественное число из интервала [x, y]."""
    return random.uniform(x, y)


def irnd(x):
    """Возвращает случайное целое число из интервала [0, x]."""
    return random.randint(0, int(x))


def irand(x, y):
    """Возвращает случайное целое число из интервала [x, y]."""
    return random.randint(int(x), int(y))


def МАКСЦЕЛ():
    """Возвращает максимальное целое число, доступное в языке Кумир."""
    return 2147483647


def МАКСВЕЩ():
    """Возвращает максимальное вещественное число, доступное в языке Кумир."""
    return sys.float_info.max
