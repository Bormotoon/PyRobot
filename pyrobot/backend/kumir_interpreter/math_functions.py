import math
import random
import sys

"""
Модуль math_functions.py
@description Реализует математические функции для языка KUMIR.
В модуле представлены функции для вычисления квадратного корня, абсолютного значения, тригонометрических функций,
логарифмов, экспоненты, функций сравнения, целочисленного деления, генерации случайных чисел и другие.
Все функции снабжены подробными комментариями и докстрингами на русском языке.
"""


def sqrt(x):
    """
    Вычисляет квадратный корень числа x (при условии, что x >= 0).

    Параметры:
      x (float): Число, для которого необходимо вычислить квадратный корень.

    Возвращаемое значение:
      float: Квадратный корень числа x.

    Исключения:
      ValueError: Если x < 0, так как квадратный корень для отрицательных чисел не определён.
    """
    if x < 0:
        # Если аргумент отрицательный, генерируем ошибку
        raise ValueError("sqrt: argument must be non-negative")
    return math.sqrt(x)  # Вычисляем квадратный корень с использованием стандартной функции math.sqrt


def abs_val(x):
    """
    Вычисляет абсолютное значение числа x (подходит для чисел с плавающей точкой).

    Параметры:
      x (float): Число, для которого вычисляется абсолютное значение.

    Возвращаемое значение:
      float: Абсолютное значение x.
    """
    # Если x больше или равно 0, возвращаем его, иначе возвращаем -x
    return x if x >= 0 else -x


def iabs(x):
    """
    Вычисляет абсолютное значение целого числа x.

    Параметры:
      x (int): Число, для которого требуется вычислить абсолютное значение.

    Возвращаемое значение:
      int: Абсолютное значение числа x.
    """
    # Приводим значение к целому типу
    x = int(x)
    return x if x >= 0 else -x


def sign(x):
    """
    Определяет знак числа x.

    Параметры:
      x (float или int): Число, знак которого нужно определить.

    Возвращаемое значение:
      int: -1, если x < 0; 0, если x == 0; 1, если x > 0.
    """
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1


def sin_val(x):
    """
    Вычисляет синус угла x (где x задается в радианах).

    Параметры:
      x (float): Значение угла в радианах.

    Возвращаемое значение:
      float: Синус угла x.
    """
    return math.sin(x)


def cos_val(x):
    """
    Вычисляет косинус угла x (где x задается в радианах).

    Параметры:
      x (float): Значение угла в радианах.

    Возвращаемое значение:
      float: Косинус угла x.
    """
    return math.cos(x)


def tan_val(x):
    """
    Вычисляет тангенс угла x (где x задается в радианах).

    Параметры:
      x (float): Значение угла в радианах.

    Возвращаемое значение:
      float: Тангенс угла x.
    """
    return math.tan(x)


def cot(x):
    """
    Вычисляет котангенс угла x (определён, если sin(x) != 0).

    Параметры:
      x (float): Значение угла в радианах.

    Возвращаемое значение:
      float: Котангенс угла x.

    Исключения:
      ValueError: Если sin(x) равен 0, так как операция не определена.
    """
    s = math.sin(x)
    if s == 0:
        raise ValueError("cot: sin(x) is 0, operation undefined")
    # Котангенс равен cos(x) / sin(x)
    return math.cos(x) / s


def arcsin_val(x):
    """
    Вычисляет арксинус числа x (при условии, что x принадлежит интервалу [-1, 1]).

    Параметры:
      x (float): Число, для которого вычисляется арксинус.

    Возвращаемое значение:
      float: Арксинус x в радианах.

    Исключения:
      ValueError: Если x не принадлежит интервалу [-1, 1].
    """
    if x < -1 or x > 1:
        raise ValueError("arcsin: x must belong to [-1,1]")
    return math.asin(x)


def arccos_val(x):
    """
    Вычисляет арккосинус числа x (при условии, что x принадлежит интервалу [-1, 1]).

    Параметры:
      x (float): Число, для которого вычисляется арккосинус.

    Возвращаемое значение:
      float: Арккосинус x в радианах.

    Исключения:
      ValueError: Если x не принадлежит интервалу [-1, 1].
    """
    if x < -1 or x > 1:
        raise ValueError("arccos: x must belong to [-1,1]")
    return math.acos(x)


def arctan_val(x):
    """
    Вычисляет арктангенс числа x.

    Параметры:
      x (float): Число, для которого вычисляется арктангенс.

    Возвращаемое значение:
      float: Арктангенс x в радианах.
    """
    return math.atan(x)


def arccot(x):
    """
    Вычисляет арккотангенс числа x.
    Для x = 0 возвращает π/2.

    Параметры:
      x (float): Число, для которого вычисляется арккотангенс.

    Возвращаемое значение:
      float: Арккотангенс x в радианах.
    """
    if x == 0:
        # При x == 0, определяем arccot как π/2
        return math.pi / 2
    if x > 0:
        # Для положительных x используем арктангенс обратного значения
        return math.atan(1 / x)
    else:
        # Для отрицательных x добавляем π, чтобы получить корректное значение
        return math.atan(1 / x) + math.pi


def ln(x):
    """
    Вычисляет натуральный логарифм числа x (x > 0).

    Параметры:
      x (float): Число, для которого вычисляется логарифм.

    Возвращаемое значение:
      float: Натуральный логарифм x.

    Исключения:
      ValueError: Если x <= 0.
    """
    if x <= 0:
        raise ValueError("ln: x must be > 0")
    return math.log(x)


def lg(x):
    """
    Вычисляет логарифм числа x по основанию 10 (x > 0).

    Параметры:
      x (float): Число, для которого вычисляется логарифм.

    Возвращаемое значение:
      float: Логарифм x по основанию 10.

    Исключения:
      ValueError: Если x <= 0.
    """
    if x <= 0:
        raise ValueError("lg: x must be > 0")
    return math.log10(x)


def exp_val(x):
    """
    Вычисляет экспоненту (e) в степени x.

    Параметры:
      x (float): Показатель степени.

    Возвращаемое значение:
      float: Значение exp(x), то есть e^x.
    """
    return math.exp(x)


def min_val(x, y):
    """
    Возвращает меньшее из двух чисел (с плавающей точкой).

    Параметры:
      x (float): Первое число.
      y (float): Второе число.

    Возвращаемое значение:
      float: Меньшее значение из x и y.
    """
    return x if x < y else y


def max_val(x, y):
    """
    Возвращает большее из двух чисел (с плавающей точкой).

    Параметры:
      x (float): Первое число.
      y (float): Второе число.

    Возвращаемое значение:
      float: Большее значение из x и y.
    """
    return x if x > y else y


def imin(x, y):
    """
    Возвращает меньшее из двух целых чисел.

    Параметры:
      x (int): Первое число.
      y (int): Второе число.

    Возвращаемое значение:
      int: Меньшее целое число из x и y.
    """
    return int(x) if int(x) < int(y) else int(y)


def imax(x, y):
    """
    Возвращает большее из двух целых чисел.

    Параметры:
      x (int): Первое число.
      y (int): Второе число.

    Возвращаемое значение:
      int: Большее целое число из x и y.
    """
    return int(x) if int(x) > int(y) else int(y)


def div(x, y):
    """
    Выполняет целочисленное деление x на y.

    Параметры:
      x (int или float): Делимое.
      y (int или float): Делитель.

    Возвращаемое значение:
      int: Результат целочисленного деления.

    Исключения:
      ZeroDivisionError: Если y равно 0.
    """
    if y == 0:
        raise ZeroDivisionError("div: division by zero")
    # Приводим аргументы к целому типу и выполняем целочисленное деление
    return int(x) // int(y)


def mod(x, y):
    """
    Вычисляет остаток от деления x на y.

    Параметры:
      x (int или float): Делимое.
      y (int или float): Делитель.

    Возвращаемое значение:
      int: Остаток от деления.

    Исключения:
      ZeroDivisionError: Если y равно 0.
    """
    if y == 0:
        raise ZeroDivisionError("mod: division by zero")
    return int(x) % int(y)


def int_part(x):
    """
    Возвращает целую часть числа x, то есть наибольшее целое число, не превышающее x.

    Параметры:
      x (float): Число, для которого требуется целая часть.

    Возвращаемое значение:
      int: Целая часть x.
    """
    return math.floor(x)


def rnd(x):
    """
    Возвращает случайное число с плавающей точкой из интервала [0, x].

    Параметры:
      x (float): Верхняя граница интервала.

    Возвращаемое значение:
      float: Случайное число от 0 до x.
    """
    # Функция random.random() возвращает число в диапазоне [0.0, 1.0)
    return random.random() * x


def rand(x, y):
    """
    Возвращает случайное число с плавающей точкой из интервала [x, y].

    Параметры:
      x (float): Нижняя граница интервала.
      y (float): Верхняя граница интервала.

    Возвращаемое значение:
      float: Случайное число от x до y.
    """
    return random.uniform(x, y)


def irnd(x):
    """
    Возвращает случайное целое число из интервала [0, x].

    Параметры:
      x (int или float): Верхняя граница интервала.

    Возвращаемое значение:
      int: Случайное целое число от 0 до x.
    """
    return random.randint(0, int(x))


def irand(x, y):
    """
    Возвращает случайное целое число из интервала [x, y].

    Параметры:
      x (int или float): Нижняя граница интервала.
      y (int или float): Верхняя граница интервала.

    Возвращаемое значение:
      int: Случайное целое число от x до y.
    """
    return random.randint(int(x), int(y))


def max_int():
    """
    Возвращает максимальное целое число, доступное в языке KUMIR.

    Возвращаемое значение:
      int: Максимальное значение 2147483647.
    """
    return 2147483647


def max_float():
    """
    Возвращает максимальное значение типа float, доступное в Python.

    Возвращаемое значение:
      float: Максимальное значение float из sys.float_info.max.
    """
    return sys.float_info.max
