# FILE START: file_functions.py
"""
Модуль file_functions.py
@description Реализует функции для работы с текстовыми файлами ВНУТРИ ПЕСОЧНИЦЫ.
Все пути, передаваемые в функции, проверяются и разрешаются относительно
безопасного базового каталога (песочницы).
"""

import logging
import os
import sys
from pathlib import Path  # Используем pathlib для удобной работы с путями

logger = logging.getLogger('KumirFileFunctions')

# --- Настройка Песочницы ---

# Определяем базовый каталог для песочницы.
# Путь строится относительно текущего файла (__file__) -> backend/kumir_interpreter -> backend -> kumir_sandbox
try:
	# Получаем абсолютный путь к каталогу, где находится этот файл
	current_dir = Path(__file__).parent.absolute()
	# Поднимаемся на один уровень (к каталогу backend)
	backend_dir = current_dir.parent
	# Создаем путь к каталогу песочницы
	SANDBOX_BASE_DIR = backend_dir / "kumir_sandbox"
	# Убедимся, что каталог существует, создаем его, если нет
	SANDBOX_BASE_DIR.mkdir(parents=True, exist_ok=True)
	# Сохраняем абсолютный путь как строку для сравнения префиксов
	SANDBOX_BASE_PATH_STR = str(SANDBOX_BASE_DIR)
	logger.info(f"File sandbox initialized at: {SANDBOX_BASE_PATH_STR}")
except Exception as e:
	logger.exception(f"CRITICAL: Failed to initialize file sandbox directory: {e}")
	# Если песочница не создана, дальнейшая работа опасна.
	# Можно либо остановить приложение, либо установить SANDBOX_BASE_DIR в None
	# и проверять это в _resolve_sandbox_path. Установим в None для явной ошибки.
	SANDBOX_BASE_DIR = None
	SANDBOX_BASE_PATH_STR = None  # raise RuntimeError(f"Failed to initialize file sandbox: {e}") # Можно раскомментировать для остановки


class SandboxError(Exception):
	"""Исключение для ошибок, связанных с выходом из песочницы."""
	pass


def _resolve_sandbox_path(user_path):
	"""
    Преобразует пользовательский путь в абсолютный путь внутри песочницы.
    Проверяет, что результирующий путь не выходит за пределы песочницы.

    Args:
        user_path (str): Путь, указанный пользователем (может быть относительным).

    Returns:
        Path: Объект Path с абсолютным путем внутри песочницы.

    Raises:
        SandboxError: Если путь выходит за пределы песочницы или песочница не инициализирована.
        TypeError: Если user_path не является строкой.
    """
	if SANDBOX_BASE_DIR is None or SANDBOX_BASE_PATH_STR is None:
		logger.critical("Sandbox base directory is not configured. File operations denied.")
		raise SandboxError("Файловая песочница не инициализирована.")

	if not isinstance(user_path, str):
		raise TypeError(f"Путь должен быть строкой, получен {type(user_path)}")

	# Создаем путь относительно базового каталога песочницы
	combined_path = SANDBOX_BASE_DIR / user_path

	# Получаем канонический абсолютный путь (разрешает '..', '.', симлинки)
	try:
		# Используем resolve() для получения реального пути в файловой системе
		# strict=True вызовет ошибку, если путь не существует (может быть не нужно для создания)
		# Поэтому используем abspath() для начального разрешения, а потом проверим префикс
		abs_path = combined_path.absolute()
		abs_path_str = str(abs_path)
	except Exception as e:
		# Ошибки могут возникнуть из-за слишком длинного имени, некорректных символов и т.д.
		logger.error(f"Error resolving path '{user_path}' relative to sandbox: {e}")
		raise SandboxError(f"Некорректный путь: '{user_path}'")

	# ГЛАВНАЯ ПРОВЕРКА: Убеждаемся, что абсолютный путь начинается с пути к песочнице
	# Это предотвращает выход из песочницы через '..' или абсолютные пути.
	if not abs_path_str.startswith(SANDBOX_BASE_PATH_STR):
		logger.warning(
			f"Path traversal attempt detected: User path '{user_path}' resolved to '{abs_path_str}', which is outside sandbox '{SANDBOX_BASE_PATH_STR}'.")
		raise SandboxError(f"Доступ запрещен: путь '{user_path}' выходит за пределы песочницы.")

	logger.debug(f"Resolved sandboxed path for '{user_path}' -> '{abs_path}'")
	return abs_path  # Возвращаем объект Path


# --- Глобальные настройки (без изменений) ---
_open_files = {}
_default_encoding = "UTF-8"
_default_input = None
_default_output = None


# Функция _normalize_encoding остается без изменений
def _normalize_encoding(enc):
	"""Нормализует имя кодировки."""
	# ... (код без изменений) ...
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


# Функция set_encoding остается без изменений
def set_encoding(encoding_name):
	"""Устанавливает глобальную кодировку."""
	# ... (код без изменений) ...
	global _default_encoding
	norm = _normalize_encoding(encoding_name)
	if norm is None:
		raise Exception(f"Invalid encoding name: {encoding_name}")
	_default_encoding = norm
	logger.info(f"Default file encoding set to: {_default_encoding}")
	return "да"  # Возвращаем "да" для совместимости с Кумиром


# --- Модифицированные файловые функции ---

def open_for_reading(filename):
	"""
    Открывает текстовый файл ВНУТРИ ПЕСОЧНИЦЫ для чтения.
    """
	global _open_files, _default_encoding
	try:
		# Разрешаем путь внутри песочницы
		path_obj = _resolve_sandbox_path(filename)
		path_str = str(path_obj)
	except (SandboxError, TypeError) as e:
		raise Exception(f"Ошибка открытия файла для чтения '{filename}': {e}")

	if path_str in _open_files:
		raise Exception(f"Файл '{filename}' уже открыт.")
	# Используем path_obj для проверок и открытия
	if not path_obj.exists():
		raise Exception(f"Файл '{filename}' не найден в песочнице.")
	if not path_obj.is_file():
		raise Exception(f"Путь '{filename}' указывает на директорию, а не на файл.")
	if not os.access(path_str, os.R_OK):  # os.access все еще нужен для проверки прав
		raise Exception(f"Нет прав на чтение файла '{filename}'.")

	try:
		# Открываем файл с использованием path_obj (или path_str)
		f = open(path_obj, "r", encoding=_default_encoding)
		logger.info(f"Opened file '{filename}' (path: {path_str}) for reading.")
	except Exception as e:
		raise Exception(f"Ошибка при открытии файла '{filename}' для чтения: {e}")

	_open_files[path_str] = f
	return f


def open_for_writing(filename):
	"""
    Открывает текстовый файл ВНУТРИ ПЕСОЧНИЦЫ для записи ("w").
    """
	global _open_files, _default_encoding
	try:
		path_obj = _resolve_sandbox_path(filename)
		path_str = str(path_obj)
	except (SandboxError, TypeError) as e:
		raise Exception(f"Ошибка открытия файла для записи '{filename}': {e}")

	if path_str in _open_files:
		raise Exception(f"Файл '{filename}' уже открыт.")

	# Проверяем права на запись (или создание)
	parent_dir = path_obj.parent
	if path_obj.exists():
		if not path_obj.is_file():
			raise Exception(f"Путь '{filename}' указывает на директорию, запись невозможна.")
		if not os.access(path_str, os.W_OK):
			raise Exception(f"Нет прав на запись в файл '{filename}'.")
	elif not parent_dir.exists() or not os.access(str(parent_dir), os.W_OK):
		# Проверяем существование родительской директории и права на запись в нее
		raise Exception(
			f"Нет прав на создание файла '{filename}' в директории '{parent_dir.relative_to(SANDBOX_BASE_DIR)}'.")

	try:
		# Открываем файл в режиме записи
		f = open(path_obj, "w", encoding=_default_encoding)
		logger.info(f"Opened file '{filename}' (path: {path_str}) for writing.")
	except Exception as e:
		raise Exception(f"Ошибка при открытии файла '{filename}' для записи: {e}")

	_open_files[path_str] = f
	return f


def open_for_append(filename):
	"""
    Открывает текстовый файл ВНУТРИ ПЕСОЧНИЦЫ для добавления ("a").
    """
	global _open_files, _default_encoding
	try:
		path_obj = _resolve_sandbox_path(filename)
		path_str = str(path_obj)
	except (SandboxError, TypeError) as e:
		raise Exception(f"Ошибка открытия файла для добавления '{filename}': {e}")

	if path_str in _open_files:
		raise Exception(f"Файл '{filename}' уже открыт.")

	# Проверяем права на запись/создание (аналогично open_for_writing)
	parent_dir = path_obj.parent
	if path_obj.exists():
		if not path_obj.is_file():
			raise Exception(f"Путь '{filename}' указывает на директорию, добавление невозможно.")
		if not os.access(path_str, os.W_OK):
			raise Exception(f"Нет прав на запись (добавление) в файл '{filename}'.")
	elif not parent_dir.exists() or not os.access(str(parent_dir), os.W_OK):
		raise Exception(
			f"Нет прав на создание файла '{filename}' для добавления в директории '{parent_dir.relative_to(SANDBOX_BASE_DIR)}'.")

	try:
		# Открываем файл в режиме добавления
		f = open(path_obj, "a", encoding=_default_encoding)
		logger.info(f"Opened file '{filename}' (path: {path_str}) for appending.")
	except Exception as e:
		raise Exception(f"Ошибка при открытии файла '{filename}' для добавления: {e}")

	_open_files[path_str] = f
	return f


# Функция close_file остается почти без изменений, но использует имя файла из объекта f
def close_file(f):
	"""Закрывает ранее открытый файл."""
	global _open_files
	if not hasattr(f, 'name') or not f.name:
		raise Exception("Некорректный файловый объект передан для закрытия.")

	# Получаем абсолютный путь файла по его имени
	# Важно: имя файла в f.name уже должно быть абсолютным путем, который мы сохранили
	path_str = f.name
	if path_str not in _open_files:
		# Это может случиться, если файл был открыт не нашими функциями
		# или был закрыт ранее. Проверяем, начинается ли путь с песочницы для безопасности.
		if SANDBOX_BASE_PATH_STR and path_str.startswith(SANDBOX_BASE_PATH_STR):
			logger.warning(f"Attempting to close file '{f.name}' which was not tracked as open. Closing anyway.")
		else:
			# Попытка закрыть файл вне песочницы или некорректный путь
			logger.error(f"Attempting to close untracked or potentially unsafe file: '{f.name}'")
			raise Exception(f"Файл '{f.name}' не был найден среди открытых или находится вне песочницы.")

	try:
		f.close()
		logger.info(f"Closed file '{os.path.relpath(path_str, SANDBOX_BASE_PATH_STR)}' (path: {path_str}).")
	except Exception as e:
		# Удаляем из _open_files даже если закрытие вызвало ошибку,
		# чтобы не блокировать повторное открытие
		if path_str in _open_files:
			del _open_files[path_str]
		raise Exception(f"Ошибка при закрытии файла '{f.name}': {e}")

	# Удаляем запись об открытом файле только при успешном закрытии
	if path_str in _open_files:
		del _open_files[path_str]


# Функции reset_reading, eof, has_data остаются без изменений (работают с файловым объектом)
def reset_reading(f):
	"""Сбрасывает указатель файла f в начало файла."""
	# ... (код без изменений) ...
	try:
		f.seek(0)
	except Exception as e:
		raise Exception(f"Error resetting file pointer for '{f.name}': {e}")


def eof(f):
	"""Проверяет, достигнут ли конец файла."""
	# ... (код без изменений) ...
	try:
		cur = f.tell()
		f.seek(0, os.SEEK_END)
		end = f.tell()
		f.seek(cur)
		return "да" if cur >= end else "нет"
	except Exception as e:
		raise Exception(f"Error checking EOF for '{f.name}': {e}")


def has_data(f):
	"""Проверяет, имеется ли хотя бы один видимый символ после текущей позиции."""
	# ... (код без изменений) ...
	try:
		cur = f.tell()
		char = f.read(1)
		f.seek(cur)
		return "да" if char else "нет"
	except Exception as e:
		raise Exception(f"Error checking has_data for '{f.name}': {e}")


# --- Функции проверки ---

def can_open_for_reading(filename):
	"""Проверяет, существует ли файл ВНУТРИ ПЕСОЧНИЦЫ и доступен ли он для чтения."""
	try:
		path_obj = _resolve_sandbox_path(filename)
		# Проверяем существование, что это файл, и права на чтение
		if path_obj.exists() and path_obj.is_file() and os.access(str(path_obj), os.R_OK):
			return "да"
		else:
			return "нет"
	except (SandboxError, TypeError):
		return "нет"  # Если путь некорректен или вне песочницы, то открыть нельзя
	except Exception as e:
		logger.warning(f"Error in can_open_for_reading for '{filename}': {e}")
		return "нет"


def can_open_for_writing(filename):
	"""
    Проверяет, существует ли файл ВНУТРИ ПЕСОЧНИЦЫ и доступен ли для записи,
    либо может ли быть создан.
    """
	try:
		path_obj = _resolve_sandbox_path(filename)
		path_str = str(path_obj)
		parent_dir = path_obj.parent

		if path_obj.exists():
			# Файл существует: проверяем, что это файл и есть права на запись
			if path_obj.is_file() and os.access(path_str, os.W_OK):
				return "да"
			else:
				return "нет"
		else:
			# Файл не существует: проверяем, что родительская папка существует и есть права на запись в нее
			if parent_dir.exists() and parent_dir.is_dir() and os.access(str(parent_dir), os.W_OK):
				return "да"
			else:
				return "нет"
	except (SandboxError, TypeError):
		return "нет"
	except Exception as e:
		logger.warning(f"Error in can_open_for_writing for '{filename}': {e}")
		return "нет"


def exists(name):
	"""Проверяет, существует ли файл или директория с заданным именем ВНУТРИ ПЕСОЧНИЦЫ."""
	try:
		path_obj = _resolve_sandbox_path(name)
		return "да" if path_obj.exists() else "нет"
	except (SandboxError, TypeError):
		return "нет"
	except Exception as e:
		logger.warning(f"Error in exists for '{name}': {e}")
		return "нет"


def is_directory(name):
	"""Проверяет, является ли объект с заданным именем директорией ВНУТРИ ПЕСОЧНИЦЫ."""
	try:
		path_obj = _resolve_sandbox_path(name)
		# Проверяем существование перед проверкой на директорию
		return "да" if path_obj.exists() and path_obj.is_dir() else "нет"
	except (SandboxError, TypeError):
		return "нет"
	except Exception as e:
		logger.warning(f"Error in is_directory for '{name}': {e}")
		return "нет"


# --- Функции модификации ---

def create_directory(dirname):
	"""Создает директорию с заданным именем ВНУТРИ ПЕСОЧНИЦЫ."""
	try:
		path_obj = _resolve_sandbox_path(dirname)
		# exist_ok=True: не вызывать ошибку, если папка уже существует
		# parents=True: создавать родительские директории при необходимости
		path_obj.mkdir(parents=True, exist_ok=True)
		logger.info(f"Directory '{dirname}' (path: {path_obj}) created or already exists.")
		return "да"
	except (SandboxError, TypeError) as e:
		raise Exception(f"Ошибка создания директории '{dirname}': {e}")
	except Exception as e:
		raise Exception(f"Ошибка при создании директории '{dirname}': {e}")


def delete_file(filename):
	"""Удаляет файл с заданным именем ВНУТРИ ПЕСОЧНИЦЫ."""
	try:
		path_obj = _resolve_sandbox_path(filename)
		path_str = str(path_obj)

		# Дополнительная проверка перед удалением
		if not path_obj.exists():
			raise FileNotFoundError(f"Файл '{filename}' не найден для удаления.")
		if not path_obj.is_file():
			raise IsADirectoryError(f"Путь '{filename}' указывает на директорию, а не файл.")
		if path_str in _open_files:
			raise Exception(f"Нельзя удалить файл '{filename}', так как он открыт.")

		path_obj.unlink()  # Используем unlink для удаления файла
		logger.info(f"File '{filename}' (path: {path_obj}) deleted.")
		return "да"
	except (SandboxError, TypeError, FileNotFoundError, IsADirectoryError) as e:
		raise Exception(f"Ошибка удаления файла '{filename}': {e}")
	except Exception as e:
		raise Exception(f"Ошибка при удалении файла '{filename}': {e}")


def delete_directory(dirname):
	"""Удаляет ПУСТУЮ директорию с заданным именем ВНУТРИ ПЕСОЧНИЦЫ."""
	try:
		path_obj = _resolve_sandbox_path(dirname)

		if not path_obj.exists():
			raise FileNotFoundError(f"Директория '{dirname}' не найдена для удаления.")
		if not path_obj.is_dir():
			raise NotADirectoryError(f"Путь '{dirname}' указывает на файл, а не директорию.")

		# Проверяем, что директория пуста
		if any(path_obj.iterdir()):
			raise OSError(f"Директория '{dirname}' не пуста, удаление невозможно.")

		path_obj.rmdir()  # Удаляем директорию
		logger.info(f"Directory '{dirname}' (path: {path_obj}) deleted.")
		return "да"
	except (SandboxError, TypeError, FileNotFoundError, NotADirectoryError, OSError) as e:
		raise Exception(f"Ошибка удаления директории '{dirname}': {e}")
	except Exception as e:
		raise Exception(f"Ошибка при удалении директории '{dirname}': {e}")


# --- Функции получения путей (теперь возвращают пути внутри песочницы) ---

def full_path(name):
	"""
    Возвращает 'песочный' относительный путь для заданного имени.
    Показывает путь относительно базы песочницы.
    """
	try:
		path_obj = _resolve_sandbox_path(name)
		# Возвращаем путь относительно базы песочницы
		relative_path = path_obj.relative_to(SANDBOX_BASE_DIR)
		# Возвращаем как строку в стиле Unix (с '/')
		return str(relative_path).replace('\\', '/')
	except (SandboxError, TypeError) as e:
		# В случае ошибки возвращаем исходное имя или пустую строку?
		# Вернем исходное имя, как если бы разрешение не удалось.
		logger.warning(f"Could not resolve sandboxed full_path for '{name}': {e}")
		return name
	except Exception as e:
		logger.warning(f"Error in full_path for '{name}': {e}")
		return name


def WORKING_DIRECTORY():
	"""Возвращает путь к корневому каталогу песочницы."""
	if SANDBOX_BASE_PATH_STR:
		# Возвращаем просто '/', обозначая корень песочницы
		return "/"
	else:
		logger.error("Working directory requested but sandbox is not initialized.")
		return "./"  # Запасной вариант


def PROGRAM_DIRECTORY():
	"""Возвращает путь к корневому каталогу песочницы (аналогично WORKING_DIRECTORY)."""
	# В контексте песочницы нет разницы между рабочей папкой и папкой программы.
	return WORKING_DIRECTORY()


# --- Функции стандартного ввода/вывода ---

def set_input(filename):
	"""
    Устанавливает файл (ВНУТРИ ПЕСОЧНИЦЫ) или консоль в качестве источника ввода.
    """
	global _default_input, _default_encoding
	filename_strip = filename.strip()

	# Специальное имя для консоли
	if filename_strip.lower() == "консоль":
		if _default_input and _default_input is not sys.stdin:
			try:
				# Закрываем предыдущий файл, если он был открыт нами
				# Используем путь из f.name для удаления из _open_files
				close_file(_default_input)  # close_file обработает _open_files
			except Exception as e:
				logger.warning(f"Could not close previous default input '{_default_input.name}': {e}")
		_default_input = sys.stdin  # Стандартный ввод Python (input())
		logger.info("Default input set to console (stdin).")
		return "да"

	# Пустая строка - сброс на stdin
	if filename_strip == "":
		if _default_input and _default_input is not sys.stdin:
			try:
				close_file(_default_input)
			except Exception as e:
				logger.warning(f"Could not close previous default input '{_default_input.name}': {e}")
		_default_input = sys.stdin  # input()
		logger.info("Default input reset to console (stdin).")
		return "да"

	# Иначе - это имя файла в песочнице
	try:
		path_obj = _resolve_sandbox_path(filename_strip)
		path_str = str(path_obj)
	except (SandboxError, TypeError) as e:
		raise Exception(f"Ошибка установки файла ввода '{filename}': {e}")

	# Проверяем возможность чтения
	if can_open_for_reading(filename_strip) != "да":
		raise Exception(f"Файл '{filename}' не найден или недоступен для чтения в песочнице.")

	# Закрываем предыдущий файл ввода, если он был
	if _default_input and _default_input is not sys.stdin:
		try:
			close_file(_default_input)
		except Exception as e:
			logger.warning(f"Could not close previous default input '{_default_input.name}': {e}")

	try:
		# Открываем новый файл
		new_input_file = open(path_obj, "r", encoding=_default_encoding)
		_open_files[path_str] = new_input_file  # Регистрируем как открытый
		_default_input = new_input_file
		logger.info(f"Default input set to file '{filename_strip}' (path: {path_str}).")
		return "да"
	except Exception as e:
		raise Exception(f"Ошибка при открытии файла '{filename}' для ввода: {e}")


def set_output(filename):
	"""
    Устанавливает файл (ВНУТРИ ПЕСОЧНИЦЫ) или консоль в качестве места вывода.
    """
	global _default_output, _default_encoding
	filename_strip = filename.strip()

	# Специальное имя для консоли
	if filename_strip.lower() == "консоль":
		if _default_output and _default_output is not sys.stdout:
			try:
				close_file(_default_output)
			except Exception as e:
				logger.warning(f"Could not close previous default output '{_default_output.name}': {e}")
		_default_output = sys.stdout  # Стандартный вывод Python (print())
		logger.info("Default output set to console (stdout).")
		return "да"

	# Пустая строка - сброс на stdout
	if filename_strip == "":
		if _default_output and _default_output is not sys.stdout:
			try:
				close_file(_default_output)
			except Exception as e:
				logger.warning(f"Could not close previous default output '{_default_output.name}': {e}")
		_default_output = sys.stdout
		logger.info("Default output reset to console (stdout).")
		return "да"

	# Иначе - это имя файла в песочнице
	try:
		path_obj = _resolve_sandbox_path(filename_strip)
		path_str = str(path_obj)
	except (SandboxError, TypeError) as e:
		raise Exception(f"Ошибка установки файла вывода '{filename}': {e}")

	# Проверяем возможность записи
	if can_open_for_writing(filename_strip) != "да":
		raise Exception(f"Файл '{filename}' не может быть открыт или создан для записи в песочнице.")

	# Закрываем предыдущий файл вывода, если он был
	if _default_output and _default_output is not sys.stdout:
		try:
			close_file(_default_output)
		except Exception as e:
			logger.warning(f"Could not close previous default output '{_default_output.name}': {e}")

	try:
		# Открываем новый файл для записи (перезаписи!)
		new_output_file = open(path_obj, "w", encoding=_default_encoding)
		_open_files[path_str] = new_output_file  # Регистрируем
		_default_output = new_output_file
		logger.info(f"Default output set to file '{filename_strip}' (path: {path_str}).")
		return "да"
	except Exception as e:
		raise Exception(f"Ошибка при открытии файла '{filename}' для вывода: {e}")


# --- ConsoleFile и get_default_* остаются без изменений ---
class ConsoleFile:
	"""Псевдо-файл, связанный с терминалом (sys.stdin/sys.stdout)."""

	def __init__(self):
		self.name = "консоль"  # Имя для идентификации
		self.closed = False
		self._input_buffer = ""  # Для возможной буферизации ввода

	def write(self, s):
		"""Записывает строку в стандартный вывод."""
		if self.closed:
			raise Exception("Ошибка: Попытка записи в закрытый файл 'консоль'.")
		# Используем стандартный вывод
		# В веб-сервере это может не отображаться пользователю напрямую,
		# а перехватываться логгером или буферизироваться.
		# Если _default_output перенаправлен, запись пойдет туда.
		# Мы должны писать в sys.stdout, если хотим именно на консоль сервера.
		# print(s, end="", file=sys.stdout) # Явно в stdout сервера
		# Или используем текущий _default_output
		output_stream = get_default_output() or sys.stdout
		try:
			print(s, end="", file=output_stream, flush=True)
		except Exception as e:
			logger.error(
				f"Error writing to console/default output: {e}")  # Не бросаем исключение наверх, чтобы не прерывать программу из-за ошибки вывода

	def read(self, n=-1):
		"""
        Читает данные из стандартного ввода.
        ПРЕДУПРЕЖДЕНИЕ: Блокирует выполнение в ожидании ввода! Не использовать на сервере.
        """
		if self.closed:
			raise Exception("Ошибка: Попытка чтения из закрытого файла 'консоль'.")

		input_stream = get_default_input() or sys.stdin
		if input_stream is sys.stdin:
			# Чтение из реальной консоли (блокирующее!)
			logger.warning("Reading from console (stdin) requested. This is blocking!")
			try:
				line = input()  # Блокирующий вызов
				# В Кумире обычно читают построчно, добавим \n
				return line + "\n" if n == -1 or n >= len(line) + 1 else line[:n]
			except EOFError:
				return ""  # Конец ввода
		else:
			# Чтение из файла, установленного через set_input
			try:
				if n == -1:
					return input_stream.read()
				else:
					return input_stream.read(n)
			except Exception as e:
				logger.error(f"Error reading from default input file '{input_stream.name}': {e}")
				raise Exception(f"Ошибка чтения из файла ввода '{input_stream.name}': {e}")

	def seek(self, offset, whence=os.SEEK_SET):
		# Перемещение указателя для консоли не имеет смысла или невозможно
		logger.warning("Attempted to seek on console file. Operation ignored.")
		if whence == os.SEEK_SET and offset == 0: return  # Разрешим seek(0)
		raise OSError("Cannot seek on console file object.")

	def tell(self):
		# Позиция для консоли не определена
		logger.warning("Attempted to tell() on console file. Returning 0.")
		return 0

	def close(self):
		"""Закрытие 'консоли' невозможно."""
		# Мы не должны закрывать sys.stdin/sys.stdout
		# self.closed = True # Можно установить флаг, но лучше бросить ошибку
		raise Exception("Нельзя закрыть стандартный файл 'консоль'.")

	def __iter__(self):
		# Позволяет читать консоль построчно в цикле for (например)
		return self

	def __next__(self):
		# Читает следующую строку
		line = self.read()  # Используем наш read, который может читать из файла или stdin
		if line:
			# Убираем \n в конце, если он был добавлен нашим read() для stdin
			if (get_default_input() or sys.stdin) is sys.stdin and line.endswith('\n'):
				return line[:-1]
			return line
		else:
			raise StopIteration


def console_file():
	"""Возвращает объект, представляющий консоль."""
	return ConsoleFile()


def get_default_input():
	"""Возвращает текущий источник ввода по умолчанию (файл или sys.stdin)."""
	global _default_input
	return _default_input


def get_default_output():
	"""Возвращает текущий выходной поток по умолчанию (файл или sys.stdout)."""
	global _default_output
	return _default_output

# FILE END: file_functions.py
