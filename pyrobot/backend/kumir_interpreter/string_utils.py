"""
Модуль string_utils.py
@description Модуль для обработки строк в языке KUMIR.
Реализованы функции для преобразования регистра, поиска подстроки, вставки, замены и удаления символов в строках.
Функции соответствуют требованиям языка KUMIR и используются, например, в безопасном вычислении выражений.
"""


def upper_case(text):
    """
    Преобразует строку к верхнему регистру.

    Параметры:
      text (str): Исходная строка.

    Возвращаемое значение:
      str: Строка, в которой все символы приведены к верхнему регистру.
    """
    # Преобразуем текст в строку и вызываем метод upper() для получения строки в верхнем регистре
    return str(text).upper()


def lower_case(text):
    """
    Преобразует строку к нижнему регистру.

    Параметры:
      text (str): Исходная строка.

    Возвращаемое значение:
      str: Строка, в которой все символы приведены к нижнему регистру.
    """
    # Преобразуем текст в строку и вызываем метод lower() для получения строки в нижнем регистре
    return str(text).lower()


def position(substring, text):
    """
    Возвращает позицию (1-based) первого вхождения подстроки в текст.

    Если подстрока не найдена, возвращает 0.

    Параметры:
      substring (str): Искомая подстрока.
      text (str): Текст, в котором выполняется поиск.

    Возвращаемое значение:
      int: Позиция первого вхождения подстроки (начиная с 1) или 0, если подстрока не найдена.
    """
    # Преобразуем оба аргумента в строки
    s = str(text)
    sub = str(substring)
    # Используем метод find для поиска подстроки; возвращает индекс (начиная с 0) или -1, если не найдено
    idx = s.find(sub)
    # Если индекс не равен -1, прибавляем 1 для перехода к 1-based индексированию, иначе возвращаем 0
    return idx + 1 if idx != -1 else 0


# Alias для обратной совместимости: pos – альтернативное имя функции position
pos = position


def position_after(start, substring, text):
    """
    Ищет первое вхождение подстроки в тексте, начиная с заданной позиции (1-based).

    Если подстрока не найдена, возвращает 0.

    Параметры:
      start (int): Позиция, с которой начинается поиск (нумерация с 1).
      substring (str): Искомая подстрока.
      text (str): Текст, в котором выполняется поиск.

    Возвращаемое значение:
      int: Позиция первого вхождения подстроки (начиная с 1) после указанной позиции или 0, если подстрока не найдена.

    Исключения:
      ValueError: Если параметр start не является целым числом или выходит за пределы допустимого диапазона.
    """
    try:
        s_start = int(start)
    except Exception:
        raise ValueError("position_after: 'start' must be an integer")
    s = str(text)
    sub = str(substring)
    # Проверяем, что стартовая позиция находится в допустимом диапазоне
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("position_after: 'start' is out of allowed range")
    # Метод find принимает второй аргумент – позицию, с которой начинать поиск (0-based)
    idx = s.find(sub, s_start - 1)
    return idx + 1 if idx != -1 else 0


def pos_after(start, substring, text):
    """
    Алиас для функции position_after.

    Параметры:
      start (int): Позиция, с которой начинается поиск.
      substring (str): Искомая подстрока.
      text (str): Текст, в котором выполняется поиск.

    Возвращаемое значение:
      int: Результат функции position_after.
    """
    return position_after(start, substring, text)


def insert(substring, text, start):
    """
    Вставляет подстроку в заданный текст, начиная с указанной позиции (1-based).

    Если значение start равно длине текста + 1, подстрока будет добавлена в конец.
    Генерирует ошибку, если значение start выходит за допустимый диапазон.

    Параметры:
      substring (str): Строка, которая будет вставлена.
      text (str): Исходный текст.
      start (int): Позиция (1-based), с которой начинается вставка.

    Возвращаемое значение:
      str: Результирующая строка после вставки.
    """
    s = str(text)
    sub = str(substring)
    try:
        s_start = int(start)
    except Exception:
        raise ValueError("insert: 'start' must be an integer")
    # Проверяем корректность позиции вставки: от 1 до len(s)+1
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("insert: 'start' is out of allowed range")
    # Вставляем подстроку, разбивая исходный текст на две части
    return s[:s_start - 1] + sub + s[s_start - 1:]


def replace(text, old_sub, new_sub, every):
    """
    Заменяет подстроку old_sub на new_sub в тексте.

    Если параметр every (строка) равен "да" (без учета регистра) – заменяются все вхождения,
    если "нет" – заменяется только первое вхождение.

    Параметры:
      text (str): Исходный текст.
      old_sub (str): Подстрока, которую нужно заменить.
      new_sub (str): Подстрока-замена.
      every (str): Параметр, определяющий, заменять все вхождения ("да") или только первое ("нет").

    Возвращаемое значение:
      str: Результирующая строка после замены.

    Исключения:
      ValueError: Если параметр every не равен "да" или "нет".
    """
    s = str(text)
    old = str(old_sub)
    new = str(new_sub)
    # Приводим параметр every к нижнему регистру и убираем пробелы для сравнения
    if str(every).strip().lower() == "да":
        return s.replace(old, new)
    elif str(every).strip().lower() == "нет":
        return s.replace(old, new, 1)
    else:
        raise ValueError("replace: parameter 'every' must be 'да' or 'нет'")


def delete(text, start, count):
    """
    Удаляет указанное количество символов из текста, начиная с заданной позиции (1-based).

    Если сумма start и count превышает длину текста, удаляются все символы до конца строки.
    Генерирует ошибку, если значение start выходит за допустимый диапазон.

    Параметры:
      text (str): Исходный текст.
      start (int): Позиция (1-based), с которой начинается удаление.
      count (int): Количество символов для удаления.

    Возвращаемое значение:
      str: Результирующая строка после удаления.

    Исключения:
      ValueError: Если start или count не являются целыми числами или start выходит за допустимый диапазон.
    """
    s = str(text)
    try:
        s_start = int(start)
        cnt = int(count)
    except Exception:
        raise ValueError("delete: 'start' and 'count' must be integers")
    if s_start < 1 or s_start > len(s) + 1:
        raise ValueError("delete: 'start' is out of allowed range")
    # Если start+count превышает длину текста, возвращаем строку до start-1
    if s_start + cnt - 1 >= len(s) + 1:
        return s[:s_start - 1]
    else:
        # Удаляем count символов, объединяя оставшиеся части строки
        return s[:s_start - 1] + s[s_start - 1 + cnt:]


# Aliases для соответствия именам, ожидаемым в safe_eval.py
to_upper = upper_case
to_lower = lower_case
replace_str = replace
delete_str = delete
