# string_utils.py
"""
Модуль для алгоритмов обработки строк в языке Кумир.
Реализованы следующие функции:
  - верхний регистр(строка): возвращает строку, все символы которой приведены к верхнему регистру.
  - нижний регистр(строка): возвращает строку, все символы которой приведены к нижнему регистру.
  - позиция(фрагмент, строка) или поз(фрагмент, строка): возвращает позицию (1-based) первого символа подстроки,
      если не найдено — возвращает 0.
  - позиция после(начало, фрагмент, строка) или поз после(начало, фрагмент, строка): поиск подстроки начиная с указанной позиции.
  - вставить(фрагмент, строка, начало): вставляет фрагмент в строку начиная с указанной позиции (1-based).
  - заменить(строка, старый фрагмент, новый фрагмент, каждый): заменяет в строке старый фрагмент на новый;
      если параметр "каждый" равен "да" (без учета регистра) — заменяются все вхождения, если "нет" — только первое.
  - удалить(строка, начало, количество): удаляет из строки указанное количество символов, начиная с позиции (1-based).
"""


def upper_case(text):
    """Возвращает строку с приведёнными к верхнему регистру символами."""
    return str(text).upper()


def lower_case(text):
    """Возвращает строку с приведёнными к нижнему регистру символами."""
    return str(text).lower()


def position(substring, text):
    """
    Возвращает позицию первого символа подстроки substring в строке text (индексация с 1).
    Если подстрока не найдена, возвращает 0.
    """
    s = str(text)
    sub = str(substring)
    idx = s.find(sub)
    return idx + 1 if idx != -1 else 0


# Сокращённый вариант:
pos = position


def position_after(start, substring, text):
    """
    Возвращает позицию первого символа подстроки substring в строке text,
    начиная поиск с позиции start (индексация с 1).
    Если подстрока не найдена, возвращает 0.
    """
    try:
        s_start = int(start)
    except Exception:
        raise ValueError("position_after: 'start' должно быть целым числом")
    s = str(text)
    sub = str(substring)
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("position_after: 'start' вне допустимого диапазона")
    idx = s.find(sub, s_start - 1)
    return idx + 1 if idx != -1 else 0


def pos_after(start, substring, text):
    """Сокращённый вариант функции 'position_after'."""
    return position_after(start, substring, text)


def insert(substring, text, start):
    """
    Вставляет substring в text, начиная с позиции start (индексация с 1).
    Если start равно длине(text)+1, то substring добавляется в конец строки.
    Если start < 1 или start > длина(text)+1, возбуждается ошибка.
    """
    s = str(text)
    sub = str(substring)
    try:
        s_start = int(start)
    except Exception:
        raise ValueError("insert: 'start' должно быть целым числом")
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("insert: 'start' вне допустимого диапазона")
    return s[:s_start - 1] + sub + s[s_start - 1:]


def replace(text, old_sub, new_sub, every):
    """
    Заменяет в строке text все вхождения подстроки old_sub на new_sub, если параметр every равен "да"
    (без учета регистра). Если every равен "нет", заменяет только первое вхождение.
    """
    s = str(text)
    old = str(old_sub)
    new = str(new_sub)
    if str(every).strip().lower() == "да":
        return s.replace(old, new)
    elif str(every).strip().lower() == "нет":
        return s.replace(old, new, 1)
    else:
        raise ValueError("replace: параметр 'every' должен быть 'да' или 'нет'")


def delete(text, start, count):
    """
    Удаляет из строки text указанное количество символов, начиная с позиции start (индексация с 1).
    Если start + count > длина(text)+1, то удаляется текст до конца строки.
    Если start < 1 или start > длина(text)+1, возбуждается ошибка.
    """
    s = str(text)
    try:
        s_start = int(start)
        cnt = int(count)
    except Exception:
        raise ValueError("delete: 'start' и 'count' должны быть целыми числами")
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("delete: 'start' вне допустимого диапазона")
    if s_start + cnt - 1 >= len(s) + 1:
        return s[:s_start - 1]
    else:
        return s[:s_start - 1] + s[s_start - 1 + cnt:]
