# string_utils.py
"""
Module for string processing functions in the Kumir language.
Implemented functions:
  - to_upper(text): returns the string with all characters converted to uppercase.
  - to_lower(text): returns the string with all characters converted to lowercase.
  - position(substring, text) or pos(substring, text): returns the 1-based position of the first occurrence of the substring;
      if not found – returns 0.
  - position_after(start, substring, text) or pos_after(start, substring, text): searches for the substring starting from the given position.
  - insert(substring, text, start): inserts substring into text starting at the given position (1-based).
  - replace_str(text, old_sub, new_sub, every): replaces occurrences of old_sub with new_sub;
      if the parameter every is "да" (case-insensitive) – all occurrences are replaced, if "нет" – only the first occurrence.
  - delete_str(text, start, count): deletes a specified number of characters from text starting at position (1-based).
"""


def upper_case(text):
    """Returns the string with all characters converted to uppercase."""
    return str(text).upper()


def lower_case(text):
    """Returns the string with all characters converted to lowercase."""
    return str(text).lower()


def position(substring, text):
    """
    Returns the 1-based position of the first occurrence of substring in text.
    If the substring is not found, returns 0.
    """
    s = str(text)
    sub = str(substring)
    idx = s.find(sub)
    return idx + 1 if idx != -1 else 0


# Alias for backward compatibility:
pos = position


def position_after(start, substring, text):
    """
    Returns the 1-based position of the first occurrence of substring in text,
    starting the search from position start.
    If the substring is not found, returns 0.
    """
    try:
        s_start = int(start)
    except Exception:
        raise ValueError("position_after: 'start' must be an integer")
    s = str(text)
    sub = str(substring)
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("position_after: 'start' is out of allowed range")
    idx = s.find(sub, s_start - 1)
    return idx + 1 if idx != -1 else 0


def pos_after(start, substring, text):
    """Alias for position_after."""
    return position_after(start, substring, text)


def insert(substring, text, start):
    """
    Inserts substring into text starting at position start (1-based).
    If start equals len(text)+1, the substring is appended to the end.
    Raises an error if start is out of the allowed range.
    """
    s = str(text)
    sub = str(substring)
    try:
        s_start = int(start)
    except Exception:
        raise ValueError("insert: 'start' must be an integer")
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("insert: 'start' is out of allowed range")
    return s[:s_start - 1] + sub + s[s_start - 1:]


def replace(text, old_sub, new_sub, every):
    """
    Replaces occurrences of old_sub with new_sub in text.
    If every equals "да" (ignoring case), replaces all occurrences.
    If every equals "нет", replaces only the first occurrence.
    """
    s = str(text)
    old = str(old_sub)
    new = str(new_sub)
    if str(every).strip().lower() == "да":
        return s.replace(old, new)
    elif str(every).strip().lower() == "нет":
        return s.replace(old, new, 1)
    else:
        raise ValueError("replace: parameter 'every' must be 'да' or 'нет'")


def delete(text, start, count):
    """
    Deletes 'count' characters from text starting at position start (1-based).
    If start + count > len(text)+1, deletes text until the end.
    Raises an error if start is out of the allowed range.
    """
    s = str(text)
    try:
        s_start = int(start)
        cnt = int(count)
    except Exception:
        raise ValueError("delete: 'start' and 'count' must be integers")
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("delete: 'start' is out of allowed range")
    if s_start + cnt - 1 >= len(s) + 1:
        return s[:s_start - 1]
    else:
        return s[:s_start - 1] + s[s_start - 1 + cnt:]


# Aliases to match the names expected by safe_eval.py:
to_upper = upper_case
to_lower = lower_case
replace_str = replace
delete_str = delete
