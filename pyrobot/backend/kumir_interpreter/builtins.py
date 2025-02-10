# builtins.py
"""
Implementation of the built-in functions for the KUMIR language for converting numbers to their
string representations and converting strings to numeric and logical values.
"""


# --- New internal (English) function names ---

def int_to_str(number):
    """
    Returns the string representation of an integer.

    KUMIR prototype:
      алг лит цел_в_лит(цел число)
    """
    return str(number)


def float_to_str(number):
    """
    Returns the string representation of a float.

    KUMIR prototype:
      алг лит вещ_в_лит(вещ число)
    """
    return str(number)


def str_to_float(string, success):
    """
    Converts the given string to a float.
    If the string contains a valid floating‐point number, returns (number, "да");
    otherwise returns (0.0, "нет").

    KUMIR prototype:
      алг вещ лит_в_вещ(лит строка, рез лог успех)

    Note: In this implementation, we do not modify the variable success in the environment,
    but return a tuple (value, success). User code should handle the returned tuple accordingly.
    """
    try:
        result = float(string)
        return result, "да"
    except:
        return 0.0, "нет"


def str_to_int(string, success):
    """
    Converts the given string to an integer.
    If the string contains a valid integer, returns (number, "да");
    otherwise returns (0, "нет").

    KUMIR prototype:
      алг цел лит_в_цел(лит строка, рез лог успех)

    Note: Similar to str_to_float, a tuple (value, success) is returned.
    """
    try:
        result = int(string)
        return result, "да"
    except:
        return 0, "нет"


def Int(string, default):
    """
    Converts the given string to an integer.
    If the string is not a valid integer, returns the default value.

    KUMIR prototype:
      алг цел Цел(лит строка, цел по умолчанию)
    """
    try:
        return int(string)
    except:
        return default


def Float(string, default):
    """
    Converts the given string to a float.
    If the string is not a valid float, returns the default value.

    KUMIR prototype:
      алг вещ Вещ(лит строка, вещ по умолчанию)
    """
    try:
        return float(string)
    except:
        return default


def Bool(string, default):
    """
    Converts the given string to a boolean.
    Recognizes the following strings as True: "да", "1", "истина";
    as False: "нет", "0", "ложь".
    If the string does not match any of these, returns the default value.

    KUMIR prototype:
      алг лог Лог(лит строка, лог по умолчанию)
    """
    s = str(string).strip().lower()
    if s in ["да", "1", "истина"]:
        return True
    elif s in ["нет", "0", "ложь"]:
        return False
    else:
        return default


# --- Aliases for backward compatibility (names as in the KUMIR documentation) ---

цел_в_лит = int_to_str
вещ_в_лит = float_to_str
лит_в_вещ = str_to_float
лит_в_цел = str_to_int
Цел = Int
Вещ = Float
Лог = Bool
