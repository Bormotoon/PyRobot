# file_functions.py

import os
import sys
import errno
import codecs

# Dictionary of open files: { absolute_path: file_object }
_open_files = {}

# Global settings
_default_encoding = "UTF-8"  # default encoding
_default_input = None  # if not None, used instead of keyboard input
_default_output = None  # if not None, used instead of standard output


# Functions for working with files

def _normalize_encoding(enc):
    """
    Normalizes the encoding name.
    Allowed encodings (case- and hyphen-insensitive):
      cp1251, windows1251, windows, cp866, ibm866, dos, koi8r, koi8, koi8-р, utf8, utf, linux
    Returns the normalized encoding name (e.g., "cp1251", "cp866", "koi8-r", "utf-8") or None if unknown.
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


def set_encoding(encoding_name):
    """
    Sets the global encoding for text file operations.
    Takes an encoding name (string). If the name is incorrect, raises an exception.
    """
    global _default_encoding
    norm = _normalize_encoding(encoding_name)
    if norm is None:
        raise Exception(f"Invalid encoding name: {encoding_name}")
    _default_encoding = norm
    return


def open_for_reading(filename):
    """
    Opens the text file with the given filename for reading using the current encoding.
    If the file does not exist or is not readable, raises an error.
    If the file is already open, raises an error.
    Returns the file object.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(filename)
    if path in _open_files:
        raise Exception(f"File '{filename}' is already open.")
    if not os.path.exists(path):
        raise Exception(f"File '{filename}' does not exist.")
    if not os.access(path, os.R_OK):
        raise Exception(f"No read permission for file '{filename}'.")
    try:
        f = open(path, "r", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Error opening file '{filename}' for reading: {e}")
    _open_files[path] = f
    return f


def open_for_writing(filename):
    """
    Opens the text file with the given filename for writing ("w" mode) using the current encoding.
    If the file exists, its contents are cleared.
    If the file is already open, raises an error.
    Returns the file object.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(filename)
    if path in _open_files:
        raise Exception(f"File '{filename}' is already open.")
    if os.path.exists(path):
        if not os.access(path, os.W_OK):
            raise Exception(f"No write permission for file '{filename}'.")
    else:
        parent = os.path.dirname(path)
        if not os.access(parent, os.W_OK):
            raise Exception(f"No permission to create file in directory '{parent}'.")
    try:
        f = open(path, "w", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Error opening file '{filename}' for writing: {e}")
    _open_files[path] = f
    return f


def open_for_append(filename):
    """
    Opens the text file with the given filename for appending ("a" mode) using the current encoding.
    If the file is already open, raises an error.
    Returns the file object.
    """
    global _open_files, _default_encoding
    path = os.path.abspath(filename)
    if path in _open_files:
        raise Exception(f"File '{filename}' is already open.")
    parent = os.path.dirname(path)
    if not os.path.exists(path) and not os.access(parent, os.W_OK):
        raise Exception(f"No permission to create file in directory '{parent}'.")
    try:
        f = open(path, "a", encoding=_default_encoding)
    except Exception as e:
        raise Exception(f"Error opening file '{filename}' for appending: {e}")
    _open_files[path] = f
    return f


def close_file(f):
    """
    Closes the previously opened file and removes it from the global open files dictionary.
    If the file is not open, raises an error.
    """
    global _open_files
    path = os.path.abspath(f.name)
    try:
        f.close()
    except Exception as e:
        raise Exception(f"Error closing file '{f.name}': {e}")
    if path in _open_files:
        del _open_files[path]
    else:
        raise Exception(f"File '{f.name}' not found among open files.")


def reset_reading(f):
    """
    Resets the file pointer of file f to the beginning.
    """
    try:
        f.seek(0)
    except Exception as e:
        raise Exception(f"Error resetting file pointer for '{f.name}': {e}")


def eof(f):
    """
    Returns "да" if the current position in f is at the end of the file, otherwise "нет".
    """
    cur = f.tell()
    f.seek(0, os.SEEK_END)
    end = f.tell()
    f.seek(cur)
    return "да" if cur >= end else "нет"


def has_data(f):
    """
    Returns "да" if there is at least one visible character after the current file pointer position in f,
    otherwise "нет". For simplicity, checks that the end of file has not been reached.
    """
    cur = f.tell()
    char = f.read(1)
    f.seek(cur)
    if char == "":
        return "нет"
    return "да"


def can_open_for_reading(filename):
    """
    Returns "да" if the file with the given filename exists and is readable, otherwise "нет".
    Does not open the file.
    """
    path = os.path.abspath(filename)
    if os.path.exists(path) and os.access(path, os.R_OK):
        return "да"
    return "нет"


def can_open_for_writing(filename):
    """
    Returns "да" if the file with the given filename either exists and is writable, or can be created,
    otherwise "нет".
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
    Returns "да" if a file or directory with the given name exists, otherwise "нет".
    """
    return "да" if os.path.exists(name) else "нет"


def is_directory(name):
    """
    Returns "да" if a directory with the given name exists, otherwise "нет".
    """
    return "да" if os.path.isdir(name) else "нет"


def create_directory(dirname):
    """
    Creates a directory with the given name (absolute or relative).
    Returns "да" if successful, otherwise raises an exception.
    """
    try:
        os.makedirs(dirname, exist_ok=False)
        return "да"
    except Exception as e:
        raise Exception(f"Error creating directory '{dirname}': {e}")


def delete_file(filename):
    """
    Deletes the file with the given filename.
    Returns "да" if successful, otherwise raises an exception.
    """
    try:
        os.remove(filename)
        return "да"
    except Exception as e:
        raise Exception(f"Error deleting file '{filename}': {e}")


def delete_directory(dirname):
    """
    Deletes the empty directory with the given name.
    Returns "да" if successful, otherwise raises an exception.
    """
    try:
        os.rmdir(dirname)
        return "да"
    except Exception as e:
        raise Exception(f"Error deleting directory '{dirname}': {e}")


def full_path(name):
    """
    Returns the absolute path for the given file or directory name.
    """
    return os.path.abspath(name)


def WORKING_DIRECTORY():
    """
    Returns the absolute path of the current working directory.
    """
    return os.getcwd()


def PROGRAM_DIRECTORY():
    """
    Returns the absolute path of the directory containing the running program.
    If the program is not saved, returns "./".
    """
    if hasattr(sys, 'argv') and sys.argv and os.path.isfile(sys.argv[0]):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        return "./"


def set_input(filename):
    """
    If the filename is non-empty and the file exists and is readable,
    sets it as the input source for the "ввод" operator.
    If the filename is an empty string, restores keyboard input.
    Returns "да" on success.
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
    If the filename is non-empty and the file exists and is writable (or can be created),
    sets it as the output destination for the "вывод" operator.
    If the filename is an empty string, restores output to the screen.
    Returns "да" on success.
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
    A pseudo-file associated with the terminal.
    Attempting to close such a file raises an error.
    Reading triggers keyboard input; writing prints text to the screen.
    """

    def __init__(self):
        self.name = "консоль"
        self.closed = False

    def write(self, s):
        if self.closed:
            raise Exception("Error: Attempt to write to closed file 'консоль'.")
        print(s, end="")  # Print without adding a newline

    def read(self, n=-1):
        if self.closed:
            raise Exception("Error: Attempt to read from closed file 'консоль'.")
        return input()

    def close(self):
        raise Exception("Cannot close file 'консоль'.")


def console_file():
    """
    Returns a pseudo-file associated with the terminal.
    """
    return ConsoleFile()


# Functions to get the current input/output settings

def get_default_input():
    global _default_input
    return _default_input


def get_default_output():
    global _default_output
    return _default_output
