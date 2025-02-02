# file_functions.py

import os
import sys
import errno
import codecs

# Словарь открытых файлов: { абсолютный_путь: file_object }
_open_files = {}

# Глобальные настройки
_default_encoding = "UTF-8"  # кодировка по умолчанию
_default_input = None  # если не None, используется вместо ввода с клавиатуры
_default_output = None  # если не None, используется вместо стандартного вывода


# Функции для работы с файлами

def _normalize_encoding(enc):
    """
    Приводит имя кодировки к стандартному виду.
    Допустимые кодировки (без учёта регистра и дефиса):
      cp1251, windows1251, windows, cp866, ibm866, dos, koi8r, koi8, koi8-р, utf8, utf, linux
    Возвращает нормализованное имя кодировки (например, "cp1251", "cp866", "koi8-r", "utf-8") или None, если неизвестно.
    """
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


def установить_кодировку(имя_кодировки):
    """
    Устанавливает глобальную кодировку для работы с текстовыми файлами.
    Принимает имя кодировки (литерал). Если имя некорректно, возбуждает исключение.
    """
    global _default_encoding
    norm = _normalize_encoding(имя_кодировки)
    if norm is None:
        raise Exception(f"Неверное имя кодировки: {имя_кодировки}")
    _default_encoding = norm
    return


def открыть_на_чтение(имя_файла):
    """
    Открывает текстовый файл с именем (литерал) для чтения с использованием текущей кодировки.
    Если файл не существует или недоступен для чтения, возбуждается ошибка.
    Если файл уже открыт, возбуждается ошибка.
    Возвращает файловый объект.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(имя_файла)
    if path in _open_files:
        raise Exception(f"Файл '{имя_файла}' уже открыт.")
    if not os.path.exists(path):
        raise Exception(f"Файл '{имя_файла}' не существует.")
    if not os.access(path, os.R_OK):
        raise Exception(f"Нет прав на чтение файла '{имя_файла}'.")
    try:
        f = open(path, "r", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Ошибка открытия файла '{имя_файла}' для чтения: {e}")
    _open_files[path] = f
    return f


def открыть_на_запись(имя_файла):
    """
    Открывает текстовый файл с именем для записи (режим "w") с использованием текущей кодировки.
    Если файл существует, его содержимое очищается.
    Если файл уже открыт, возбуждается ошибка.
    Возвращает файловый объект.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(имя_файла)
    if path in _open_files:
        raise Exception(f"Файл '{имя_файла}' уже открыт.")
    # Проверяем, если файл существует, то проверяем права на запись;
    # если не существует, проверяем возможность создания.
    if os.path.exists(path):
        if not os.access(path, os.W_OK):
            raise Exception(f"Нет прав на запись в файл '{имя_файла}'.")
    else:
        parent = os.path.dirname(path)
        if not os.access(parent, os.W_OK):
            raise Exception(f"Нет прав на создание файла в каталоге '{parent}'.")
    try:
        f = open(path, "w", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Ошибка открытия файла '{имя_файла}' для записи: {e}")
    _open_files[path] = f
    return f


def открыть_на_добавление(имя_файла):
    """
    Открывает текстовый файл с именем для записи в режиме добавления (режим "a") с использованием текущей кодировки.
    Если файл уже открыт, возбуждается ошибка.
    Возвращает файловый объект.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(имя_файла)
    if path in _open_files:
        raise Exception(f"Файл '{имя_файла}' уже открыт.")
    # Если файла не существует, проверяем возможность создания
    parent = os.path.dirname(path)
    if not os.path.exists(path) and not os.access(parent, os.W_OK):
        raise Exception(f"Нет прав на создание файла в каталоге '{parent}'.")
    try:
        f = open(path, "a", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Ошибка открытия файла '{имя_файла}' для добавления: {e}")
    _open_files[path] = f
    return f


def закрыть(f):
    """
    Закрывает ранее открытый файл и удаляет его из глобального списка открытых файлов.
    Если файл не является открытым, возбуждается ошибка.
    """
    global _open_files
    path = os.path.abspath(f.name)
    try:
        f.close()
    except Exception as e:
        raise Exception(f"Ошибка закрытия файла '{f.name}': {e}")
    if path in _open_files:
        del _open_files[path]
    else:
        raise Exception(f"Файл '{f.name}' не найден среди открытых файлов.")


def начать_чтение(f):
    """
    Сбрасывает указатель чтения файла f на его начало.
    """
    try:
        f.seek(0)
    except Exception as e:
        raise Exception(f"Ошибка установки указателя в начало файла '{f.name}': {e}")


def конец_файла(f):
    """
    Возвращает "да", если текущая позиция f находится в самом конце файла,
    иначе – "нет".
    """
    cur = f.tell()
    f.seek(0, os.SEEK_END)
    end = f.tell()
    f.seek(cur)
    return "да" if cur >= end else "нет"


def есть_данные(f):
    """
    Возвращает "да", если после текущей позиции чтения в файле f есть хотя бы один видимый символ,
    иначе – "нет". Для упрощения проверяем, что не достигнут конец файла.
    """
    cur = f.tell()
    char = f.read(1)
    f.seek(cur)
    if char == "":
        return "нет"
    # Можно добавить проверку на пробелы, но для простоты считаем, что любой символ – видимый.
    return "да"


def можно_открыть_на_чтение(имя_файла):
    """
    Возвращает "да", если файл с указанным именем существует и доступен для чтения, иначе "нет".
    Не открывает файл.
    """
    path = os.path.abspath(имя_файла)
    if os.path.exists(path) and os.access(path, os.R_OK):
        return "да"
    return "нет"


def можно_открыть_на_запись(имя_файла):
    """
    Возвращает "да", если файл с указанным именем либо существует и доступен для записи, либо может быть создан,
    иначе "нет".
    """
    path = os.path.abspath(имя_файла)
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


def существует(имя):
    """
    Возвращает "да", если с заданным именем существует файл или каталог, иначе "нет".
    """
    return "да" if os.path.exists(имя) else "нет"


def является_каталогом(имя):
    """
    Возвращает "да", если с заданным именем существует каталог, иначе "нет".
    """
    return "да" if os.path.isdir(имя) else "нет"


def создать_каталог(имя_каталога):
    """
    Создает каталог с заданным именем (абсолютным или относительным).
    Если создание прошло успешно, возвращает "да", иначе возбуждает исключение.
    """
    try:
        os.makedirs(имя_каталога, exist_ok=False)
        return "да"
    except Exception as e:
        raise Exception(f"Ошибка создания каталога '{имя_каталога}': {e}")


def удалить_файл(имя_файла):
    """
    Удаляет файл с заданным именем.
    Если удаление прошло успешно, возвращает "да", иначе возбуждает исключение.
    """
    try:
        os.remove(имя_файла)
        return "да"
    except Exception as e:
        raise Exception(f"Ошибка удаления файла '{имя_файла}': {e}")


def удалить_каталог(имя_каталога):
    """
    Удаляет пустой каталог с заданным именем.
    Если удаление прошло успешно, возвращает "да", иначе возбуждает исключение.
    """
    try:
        os.rmdir(имя_каталога)
        return "да"
    except Exception as e:
        raise Exception(f"Ошибка удаления каталога '{имя_каталога}': {e}")


def полный_путь(имя):
    """
    Возвращает абсолютный путь для заданного имени файла или каталога.
    """
    return os.path.abspath(имя)


def РАБОЧИЙ_КАТАЛОГ():
    """
    Возвращает абсолютный путь текущего рабочего каталога.
    """
    return os.getcwd()


def КАТАЛОГ_ПРОГРАММЫ():
    """
    Возвращает абсолютный путь каталога, в котором находится выполняемая программа.
    Если программа не сохранена, возвращает "./".
    """
    if hasattr(sys, 'argv') and sys.argv and os.path.isfile(sys.argv[0]):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        return "./"


def НАЗНАЧИТЬ_ВВОД(имя_файла):
    """
    Если имя_файла не пустое и файл существует и доступен для чтения,
    устанавливает его в качестве источника ввода для оператора "ввод".
    Если имя_файла – пустая строка, восстанавливает ввод с клавиатуры.
    Возвращает "да" при успехе.
    """
    global _default_input
    if имя_файла.strip() == "":
        _default_input = None
        return "да"
    # Проверяем возможность открытия
    if можно_открыть_на_чтение(имя_файла) == "да":
        try:
            _default_input = open(имя_файла, "r", encoding=_default_encoding)
            return "да"
        except Exception as e:
            raise Exception(f"Ошибка открытия файла '{имя_файла}' для ввода: {e}")
    else:
        raise Exception(f"Файл '{имя_файла}' недоступен для чтения.")


def НАЗНАЧИТЬ_ВЫВОД(имя_файла):
    """
    Если имя_файла не пустое и файл существует и доступен для записи (или может быть создан),
    устанавливает его в качестве приемника вывода для оператора "вывод".
    Если имя_файла – пустая строка, восстанавливает вывод на экран.
    Возвращает "да" при успехе.
    """
    global _default_output
    if имя_файла.strip() == "":
        _default_output = None
        return "да"
    if можно_открыть_на_запись(имя_файла) == "да":
        try:
            _default_output = open(имя_файла, "w", encoding=_default_encoding)
            return "да"
        except Exception as e:
            raise Exception(f"Ошибка открытия файла '{имя_файла}' для вывода: {e}")
    else:
        raise Exception(f"Файл '{имя_файла}' недоступен для записи.")


class ConsoleFile:
    """
    Псевдо-файл, связанный с терминалом.
    Попытка закрыть такой файл приводит к ошибке.
    Чтение вызывает ввод с клавиатуры, запись выводит текст на экран.
    """

    def __init__(self):
        self.name = "консоль"
        self.closed = False

    def write(self, s):
        if self.closed:
            raise Exception("Ошибка: попытка записи в закрытый файл 'консоль'.")
        print(s, end="")  # вывод без добавления перевода строки

    def read(self, n=-1):
        if self.closed:
            raise Exception("Ошибка: попытка чтения из закрытого файла 'консоль'.")
        return input()

    def close(self):
        raise Exception("Нельзя закрыть файл 'консоль'.")


def консоль():
    """
    Возвращает псевдо-файл, связанный с терминалом.
    """
    return ConsoleFile()


# Функции для получения текущих настроек ввода/вывода
def get_default_input():
    global _default_input
    return _default_input


def get_default_output():
    global _default_output
    return _default_output
