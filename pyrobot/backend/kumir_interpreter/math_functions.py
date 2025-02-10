# math_functions.py
import math
import random
import sys


def sqrt(x):
    """Returns the square root of x (x >= 0)."""
    if x < 0:
        raise ValueError("sqrt: argument must be non-negative")
    return math.sqrt(x)


def abs_val(x):
    """Returns the absolute value of x (for float numbers)."""
    return x if x >= 0 else -x


def iabs(x):
    """Returns the absolute value of an integer x."""
    x = int(x)
    return x if x >= 0 else -x


def sign(x):
    """Returns the sign of x: -1 if x < 0; 0 if x == 0; 1 if x > 0."""
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1


def sin_val(x):
    """Returns the sine of x."""
    return math.sin(x)


def cos_val(x):
    """Returns the cosine of x."""
    return math.cos(x)


def tan_val(x):
    """Returns the tangent of x."""
    return math.tan(x)


def cot(x):
    """Returns the cotangent of x (defined if sin(x) != 0)."""
    s = math.sin(x)
    if s == 0:
        raise ValueError("cot: sin(x) is 0, operation undefined")
    return math.cos(x) / s


def arcsin_val(x):
    """Returns the arcsine of x (x ∈ [-1, 1])."""
    if x < -1 or x > 1:
        raise ValueError("arcsin: x must belong to [-1,1]")
    return math.asin(x)


def arccos_val(x):
    """Returns the arccosine of x (x ∈ [-1, 1])."""
    if x < -1 or x > 1:
        raise ValueError("arccos: x must belong to [-1,1]")
    return math.acos(x)


def arctan_val(x):
    """Returns the arctangent of x."""
    return math.atan(x)


def arccot(x):
    """Returns the arccotangent of x. For x = 0 returns π/2."""
    if x == 0:
        return math.pi / 2
    if x > 0:
        return math.atan(1 / x)
    else:
        return math.atan(1 / x) + math.pi


def ln(x):
    """Returns the natural logarithm of x (x > 0)."""
    if x <= 0:
        raise ValueError("ln: x must be > 0")
    return math.log(x)


def lg(x):
    """Returns the base-10 logarithm of x (x > 0)."""
    if x <= 0:
        raise ValueError("lg: x must be > 0")
    return math.log10(x)


def exp_val(x):
    """Returns e raised to the power of x."""
    return math.exp(x)


def min_val(x, y):
    """Returns the smaller of the float values x and y."""
    return x if x < y else y


def max_val(x, y):
    """Returns the larger of the float values x and y."""
    return x if x > y else y


def imin(x, y):
    """Returns the smaller of the integer values x and y."""
    return int(x) if int(x) < int(y) else int(y)


def imax(x, y):
    """Returns the larger of the integer values x and y."""
    return int(x) if int(x) > int(y) else int(y)


def div(x, y):
    """Returns the integer division of x by y."""
    if y == 0:
        raise ZeroDivisionError("div: division by zero")
    return int(x) // int(y)


def mod(x, y):
    """Returns the remainder of the division of x by y."""
    if y == 0:
        raise ZeroDivisionError("mod: division by zero")
    return int(x) % int(y)


def int_part(x):
    """Returns the integer part of x (largest integer not exceeding x)."""
    return math.floor(x)


def rnd(x):
    """Returns a random float from the interval [0, x]."""
    return random.random() * x


def rand(x, y):
    """Returns a random float from the interval [x, y]."""
    return random.uniform(x, y)


def irnd(x):
    """Returns a random integer from the interval [0, x]."""
    return random.randint(0, int(x))


def irand(x, y):
    """Returns a random integer from the interval [x, y]."""
    return random.randint(int(x), int(y))


def max_int():
    """Returns the maximum integer available in the Kumir language."""
    return 2147483647


def max_float():
    """Returns the maximum float available in the Kumir language."""
    return sys.float_info.max
