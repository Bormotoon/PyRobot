# text_functions.py
"""
Module for text processing functions in the Kumir language.
Implemented functions:
  - length(text): returns the number of characters in the string.
  - char_code(c): returns the code (ordinal number) of the character c in the CP-1251 encoding.
  - unicode_code(c): returns the Unicode code of the character c.
  - char(n): returns the character corresponding to the CP-1251 code n.
  - unicode_char(n): returns the character corresponding to the Unicode code n.
"""


def length(text):
    """
    Returns the number of characters in the string.

    Example:
      length("Привет") → 6
    """
    return len(str(text))


# Alias for backward compatibility:
длин = length


def char_code(c):
    """
    Returns the ordinal number of the character c in the CP-1251 encoding.
    If c is not a string of length 1, raises an exception.

    Example:
      char_code("А") → 192   (in CP-1251, the letter А has code 192)
    """
    s = str(c)
    if len(s) != 1:
        raise ValueError("Function 'char_code' expects a string of length 1")
    try:
        encoded = s.encode('cp1251')
    except Exception as e:
        raise ValueError(f"Error encoding character '{s}' in CP-1251: {e}")
    return encoded[0]


# Alias for backward compatibility:
код = char_code


def unicode_code(c):
    """
    Returns the Unicode code of the character c.

    Example:
      unicode_code("А") → 1040
    """
    s = str(c)
    if len(s) != 1:
        raise ValueError("Function 'unicode_code' expects a string of length 1")
    return ord(s)


# Alias for backward compatibility:
юникод = unicode_code


def char(n):
    """
    Returns the character corresponding to the CP-1251 code n.
    If the number n is not a valid byte, raises an exception.

    Example:
      char(192) → "А"
    """
    try:
        n_int = int(n)
        b = bytes([n_int])
        return b.decode('cp1251')
    except Exception as e:
        raise ValueError(f"Error converting number {n} to a CP-1251 character: {e}")


# Alias for backward compatibility:
символ = char


def unicode_char(n):
    """
    Returns the character corresponding to the Unicode code n.

    Example:
      unicode_char(1040) → "А"
    """
    try:
        return chr(int(n))
    except Exception as e:
        raise ValueError(f"Error converting number {n} to a Unicode character: {e}")


# Alias for backward compatibility:
юнисимвол = unicode_char
