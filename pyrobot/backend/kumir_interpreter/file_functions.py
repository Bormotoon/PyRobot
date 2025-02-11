"""
Модуль file_functions.py
@description Реализует функции для работы с текстовыми файлами:
открытие, чтение, запись, проверка существования, удаление файлов и директорий.
Также обеспечивает поддержку псевдо-файла консоли и настройку стандартных источников ввода/вывода.
"""

import os
import sys

# Словарь для отслеживания открытых файлов: { абсолютный путь: объект файла }
_open_files = {}

# Глобальные настройки по умолчанию:
_default_encoding = "UTF-8"  # Кодировка по умолчанию для операций с текстовыми файлами
_default_input = None  # Если не None, используется вместо ввода с клавиатуры
_default_output = None  # Если не None, используется вместо стандартного вывода


# Функции для работы с файлами

def _normalize_encoding(enc):
    """
    Нормализует имя кодировки.
    Допустимые кодировки (без учета регистра и дефисов):
      cp1251, windows1251, windows, cp866, ibm866, dos, koi8r, koi8, koi8-р, utf8, utf, linux.
    Возвращает нормализованное имя кодировки (например, "cp1251", "cp866", "koi8-r", "utf-8")
    или None, если кодировка неизвестна.

    Параметры:
      enc (str): Исходное имя кодировки.

    Возвращаемое значение:
      str или None: Нормализованное имя кодировки или None, если кодировка недопустима.
    """
    # Удаляем дефисы и приводим имя кодировки к нижнему регистру
    enc = enc.replace("-", "").lower()
    if enc in ["cp1251", "windows1251", "windows"]:
        return "cp1251"
    elif enc in ["cp866", "ibm866", "dos"]:
        return "cp866"
    elif enc in ["koi8r", "koi8", "кои8", "кои8р"]:
        return "koi8-r"
    elif enc in ["utf8", "utf", "linux"]:
        return "utf-8"
    else:
        return None


def set_encoding(encoding_name):
    """
    Устанавливает глобальную кодировку для операций с текстовыми файлами.
    Принимает имя кодировки (строка). Если имя некорректно, генерируется исключение.

    Параметры:
      encoding_name (str): Имя кодировки, которую необходимо установить.

    Возвращаемое значение:
      None

    Исключения:
      Exception: Если имя кодировки неверно.
    """
    global _default_encoding
    norm = _normalize_encoding(encoding_name)
    if norm is None:
        raise Exception(f"Invalid encoding name: {encoding_name}")
    _default_encoding = norm
    return


def open_for_reading(filename):
    """
    Открывает текстовый файл с указанным именем для чтения, используя текущую кодировку.
    Если файл не существует или недоступен для чтения, генерируется ошибка.
    Если файл уже открыт, генерируется ошибка.

    Параметры:
      filename (str): Имя файла для открытия.

    Возвращаемое значение:
      file object: Объект открытого файла.

    Исключения:
      Exception: Если файл не существует, недоступен для чтения или уже открыт.
    """
    global _open_files, _default_encoding
    # Получаем абсолютный путь к файлу
    path = os.path.abspath(filename)
    if path in _open_files:
        raise Exception(f"File '{filename}' is already open.")
    if not os.path.exists(path):
        raise Exception(f"File '{filename}' does not exist.")
    if not os.access(path, os.R_OK):
        raise Exception(f"No read permission for file '{filename}'.")
    try:
        # Открываем файл для чтения с использованием текущей кодировки
        f = open(path, "r", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Error opening file '{filename}' for reading: {e}")
    _open_files[path] = f  # Записываем файл в глобальный словарь открытых файлов
    return f


def open_for_writing(filename):
    """
    Открывает текстовый файл с указанным именем для записи ("w" режим) с использованием текущей кодировки.
    Если файл существует, его содержимое очищается.
    Если файл уже открыт, генерируется ошибка.

    Параметры:
      filename (str): Имя файла для открытия на запись.

    Возвращаемое значение:
      file object: Объект открытого файла.

    Исключения:
      Exception: Если файл уже открыт, недоступен для записи или возникла ошибка открытия.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(filename)
    if path in _open_files:
        raise Exception(f"File '{filename}' is already open.")
    if os.path.exists(path):
        if not os.access(path, os.W_OK):
            raise Exception(f"No write permission for file '{filename}'.")
    else:
        # Если файл не существует, проверяем возможность его создания в родительском каталоге
        parent = os.path.dirname(path)
        if not os.access(parent, os.W_OK):
            raise Exception(f"No permission to create file in directory '{parent}'.")
    try:
        # Открываем файл в режиме записи с заданной кодировкой
        f = open(path, "w", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Error opening file '{filename}' for writing: {e}")
    _open_files[path] = f  # Сохраняем файл в словаре открытых файлов
    return f


def open_for_append(filename):
    """
    Открывает текстовый файл с указанным именем для добавления ("a" режим) с использованием текущей кодировки.
    Если файл уже открыт, генерируется ошибка.

    Параметры:
      filename (str): Имя файла для открытия на добавление.

    Возвращаемое значение:
      file object: Объект открытого файла.

    Исключения:
      Exception: Если файл уже открыт или возникла ошибка открытия.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(filename)
    if path in _open_files:
        raise Exception(f"File '{filename}' is already open.")
    parent = os.path.dirname(path)
    # Если файл не существует, проверяем возможность создания файла
    if not os.path.exists(path) and not os.access(parent, os.W_OK):
        raise Exception(f"No permission to create file in directory '{parent}'.")
    try:
        # Открываем файл в режиме добавления с заданной кодировкой
        f = open(path, "a", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Error opening file '{filename}' for appending: {e}")
    _open_files[path] = f  # Сохраняем файл в словаре открытых файлов
    return f


def close_file(f):
    """
    Закрывает ранее открытый файл и удаляет его из глобального словаря открытых файлов.
    Если файл не открыт, генерируется ошибка.

    Параметры:
      f (file object): Объект файла, который необходимо закрыть.

    Возвращаемое значение:
      None

    Исключения:
      Exception: Если возникает ошибка при закрытии или файл не найден среди открытых.
    """
    global _open_files
    # Получаем абсолютный путь файла по его имени
    path = os.path.abspath(f.name)
    try:
        f.close()  # Пытаемся закрыть файл
    except Exception as e:
        raise Exception(f"Error closing file '{f.name}': {e}")
    if path in _open_files:
        del _open_files[path]  # Удаляем запись об открытом файле
    else:
        raise Exception(f"File '{f.name}' not found among open files.")


def reset_reading(f):
    """
    Сбрасывает указатель файла f в начало файла.

    Параметры:
      f (file object): Объект файла, для которого необходимо сбросить указатель.

    Возвращаемое значение:
      None

    Исключения:
      Exception: Если возникает ошибка при сбросе указателя.
    """
    try:
        f.seek(0)
    except Exception as e:
        raise Exception(f"Error resetting file pointer for '{f.name}': {e}")


def eof(f):
    """
    Проверяет, достигнут ли конец файла.
    Возвращает "да", если текущая позиция в файле равна или превышает конец файла, иначе "нет".

    Параметры:
      f (file object): Объект файла для проверки.

    Возвращаемое значение:
      str: "да", если конец файла достигнут, иначе "нет".
    """
    cur = f.tell()  # Сохраняем текущую позицию
    f.seek(0, os.SEEK_END)  # Переходим в конец файла
    end = f.tell()  # Получаем позицию конца файла
    f.seek(cur)  # Восстанавливаем исходную позицию
    return "да" if cur >= end else "нет"


def has_data(f):
    """
    Проверяет, имеется ли хотя бы один видимый символ после текущей позиции в файле.
    Для упрощения проверяет, не достигнут ли конец файла.

    Параметры:
      f (file object): Объект файла для проверки.

    Возвращаемое значение:
      str: "да", если данные имеются, иначе "нет".
    """
    cur = f.tell()  # Сохраняем текущую позицию
    char = f.read(1)  # Читаем один символ
    f.seek(cur)  # Возвращаемся к исходной позиции
    if char == "":
        return "нет"
    return "да"


def can_open_for_reading(filename):
    """
    Проверяет, существует ли файл с заданным именем и доступен ли он для чтения.
    Функция не открывает файл, а лишь проверяет его доступность.

    Параметры:
      filename (str): Имя файла для проверки.

    Возвращаемое значение:
      str: "да", если файл существует и доступен для чтения, иначе "нет".
    """
    path = os.path.abspath(filename)
    if os.path.exists(path) and os.access(path, os.R_OK):
        return "да"
    return "нет"


def can_open_for_writing(filename):
    """
    Проверяет, существует ли файл с заданным именем и доступен ли он для записи,
    либо может ли быть создан.

    Параметры:
      filename (str): Имя файла для проверки.

    Возвращаемое значение:
      str: "да", если файл существует и доступен для записи или может быть создан, иначе "нет".
    """
    path = os.path.abspath(filename)
    if os.path.exists(path):
        if os.access(path, os.W_OK):
            return "да"
        else:
            return "нет"
    else:
        parent = os.path.dirname(path)
        if os.access(parent, os.W_OK):
            return "да"
        else:
            return "нет"


def exists(name):
    """
    Проверяет, существует ли файл или директория с заданным именем.

    Параметры:
      name (str): Имя файла или директории для проверки.

    Возвращаемое значение:
      str: "да", если файл или директория существуют, иначе "нет".
    """
    return "да" if os.path.exists(name) else "нет"


def is_directory(name):
    """
    Проверяет, является ли объект с заданным именем директорией.

    Параметры:
      name (str): Имя для проверки.

    Возвращаемое значение:
      str: "да", если объект является директорией, иначе "нет".
    """
    return "да" if os.path.isdir(name) else "нет"


def create_directory(dirname):
    """
    Создает директорию с заданным именем (абсолютным или относительным).
    Возвращает "да" при успешном создании, иначе генерирует исключение.

    Параметры:
      dirname (str): Имя директории для создания.

    Возвращаемое значение:
      str: "да", если директория успешно создана.

    Исключения:
      Exception: Если возникает ошибка при создании директории.
    """
    try:
        os.makedirs(dirname, exist_ok=False)
        return "да"
    except Exception as e:
        raise Exception(f"Error creating directory '{dirname}': {e}")


def delete_file(filename):
    """
    Удаляет файл с заданным именем.
    Возвращает "да" при успешном удалении, иначе генерирует исключение.

    Параметры:
      filename (str): Имя файла для удаления.

    Возвращаемое значение:
      str: "да", если файл успешно удален.

    Исключения:
      Exception: Если возникает ошибка при удалении файла.
    """
    try:
        os.remove(filename)
        return "да"
    except Exception as e:
        raise Exception(f"Error deleting file '{filename}': {e}")


def delete_directory(dirname):
    """
    Удаляет пустую директорию с заданным именем.
    Возвращает "да" при успешном удалении, иначе генерирует исключение.

    Параметры:
      dirname (str): Имя директории для удаления.

    Возвращаемое значение:
      str: "да", если директория успешно удалена.

    Исключения:
      Exception: Если возникает ошибка при удалении директории.
    """
    try:
        os.rmdir(dirname)
        return "да"
    except Exception as e:
        raise Exception(f"Error deleting directory '{dirname}': {e}")


def full_path(name):
    """
    Возвращает абсолютный путь для заданного имени файла или директории.

    Параметры:
      name (str): Имя файла или директории.

    Возвращаемое значение:
      str: Абсолютный путь к файлу или директории.
    """
    return os.path.abspath(name)


def WORKING_DIRECTORY():
    """
    Возвращает абсолютный путь текущей рабочей директории.

    Возвращаемое значение:
      str: Абсолютный путь текущей рабочей директории.
    """
    return os.getcwd()


def PROGRAM_DIRECTORY():
    """
    Возвращает абсолютный путь директории, содержащей запущенную программу.
    Если программа не сохранена, возвращает "./".

    Возвращаемое значение:
      str: Абсолютный путь директории программы или "./", если путь не определен.
    """
    if hasattr(sys, 'argv') and sys.argv and os.path.isfile(sys.argv[0]):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        return "./"


def set_input(filename):
    """
    Устанавливает файл с заданным именем в качестве источника ввода для оператора "ввод".
    Если filename является пустой строкой, восстанавливает ввод с клавиатуры.
    Возвращает "да" при успешной установке.

    Параметры:
      filename (str): Имя файла для установки в качестве ввода.

    Возвращаемое значение:
      str: "да" при успешной установке ввода.

    Исключения:
      Exception: Если файл не существует или недоступен для чтения.
    """
    global _default_input
    if filename.strip() == "":
        _default_input = None
        return "да"
    if can_open_for_reading(filename) == "да":
        try:
            _default_input = open(filename, "r", encoding=_default_encoding)
            return "да"
        except Exception as e:
            raise Exception(f"Error opening file '{filename}' for input: {e}")
    else:
        raise Exception(f"File '{filename}' is not readable.")


def set_output(filename):
    """
    Устанавливает файл с заданным именем в качестве места вывода для оператора "вывод".
    Если filename является пустой строкой, вывод возвращается на экран.
    Возвращает "да" при успешной установке.

    Параметры:
      filename (str): Имя файла для установки в качестве вывода.

    Возвращаемое значение:
      str: "да" при успешной установке вывода.

    Исключения:
      Exception: Если файл недоступен для записи или не может быть создан.
    """
    global _default_output
    if filename.strip() == "":
        _default_output = None
        return "да"
    if can_open_for_writing(filename) == "да":
        try:
            _default_output = open(filename, "w", encoding=_default_encoding)
            return "да"
        except Exception as e:
            raise Exception(f"Error opening file '{filename}' for output: {e}")
    else:
        raise Exception(f"File '{filename}' is not writable.")


class ConsoleFile:
    """
    Псевдо-файл, связанный с терминалом.
    Попытка закрыть такой файл генерирует ошибку.
    Чтение инициирует ввод с клавиатуры; запись выводит текст на экран.
    """

    def __init__(self):
        # Задаем имя псевдо-файла
        self.name = "консоль"
        self.closed = False

    def write(self, s):
        """
        Записывает строку в псевдо-файл.
        Выводит текст на экран без автоматического перевода строки.

        Параметры:
          s (str): Строка для записи.
        """
        if self.closed:
            raise Exception("Error: Attempt to write to closed file 'консоль'.")
        # Выводим текст без добавления нового перевода строки
        print(s, end="")

    def read(self, n=-1):
        """
        Читает данные из псевдо-файла, инициируя ввод с клавиатуры.

        Параметры:
          n (int, опционально): Количество символов для чтения (по умолчанию -1, что означает чтение всего ввода).

        Возвращаемое значение:
          str: Введенная пользователем строка.
        """
        if self.closed:
            raise Exception("Error: Attempt to read from closed file 'консоль'.")
        return input()

    def close(self):
        """
        Закрытие псевдо-файла невозможно.
        Генерирует исключение при попытке закрытия.
        """
        raise Exception("Cannot close file 'консоль'.")


def console_file():
    """
    Возвращает псевдо-файл, связанный с терминалом.

    Возвращаемое значение:
      ConsoleFile: Объект псевдо-файла, ассоциированного с терминалом.
    """
    return ConsoleFile()


def get_default_input():
    """
    Возвращает текущий источник ввода по умолчанию.

    Возвращаемое значение:
      file object или None: Текущий источник ввода, если он установлен.
    """
    global _default_input
    return _default_input


def get_default_output():
    """
    Возвращает текущий выходной поток по умолчанию.

    Возвращаемое значение:
      file object или None: Текущий выходной поток, если он установлен.
    """
    global _default_output
    return _default_output
