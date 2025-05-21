# FILE START: kumir_exceptions.py
"""
Модуль для определения кастомных исключений интерпретатора Кумир.
Вынесен в отдельный файл для предотвращения циклических импортов.
"""


# Базовый класс для ошибок во время выполнения кода Кумира
class KumirExecutionError(Exception):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message)
		self.line_index = line_index
		self.column_index = column_index
		self.line_content = line_content

	def __str__(self):
		base_message = super().__str__()
		context = ""
		if self.line_index is not None:
			context += f"строка {self.line_index + 1}"
			if self.column_index is not None:
				context += f", столбец {self.column_index + 1}"

		if self.line_content is not None:
			if self.line_index is not None or self.column_index is not None:
				context += ":"
			context += f" '{self.line_content}'"
		return f"{base_message} ({context.strip()})" if context else base_message


# Ошибка, связанная с объявлениями
class DeclarationError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с присваиванием
class AssignmentError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с вводом/выводом
class InputOutputError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Специальное исключение для запроса ввода
class KumirInputRequiredError(Exception):  # Не наследуем от KumirExecutionError, т.к. это не ошибка, а запрос
	def __init__(self, var_name, prompt, target_type):
		self.var_name = var_name
		self.prompt = prompt
		self.target_type = target_type
		message = f"Требуется ввод для переменной '{var_name}' (тип: {target_type}). Подсказка: {prompt}"
		# Сохраним line_index и line_content, если они будут добавлены
		self.line_index = None
		self.line_content = None
		super().__init__(message)


# Ошибка во время вычисления выражения (AST или safe_eval)
class KumirEvalError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Синтаксическая ошибка в коде Кумира
class KumirSyntaxError(SyntaxError, KumirExecutionError): # Наследуем от SyntaxError и нашего базового
	def __init__(self, message, line_index=None, column_index=None, line_content=None, offset=None):
		# Сначала инициализируем наш базовый класс для line_index, column_index, line_content
		KumirExecutionError.__init__(self, message, line_index, column_index, line_content)
		# Затем инициализируем SyntaxError (он принимает только msg, filename, lineno, offset, text, print_file_and_line)
		# Мы передадим основные параметры, которые он может использовать. filename и text у нас нет в явном виде здесь.
		SyntaxError.__init__(self, message)
		# Устанавливаем атрибуты SyntaxError вручную, если они не установились через конструктор
		self.msg = message
		self.lineno = line_index + 1 if line_index is not None else None
		self.offset = offset # offset - это позиция в строке (1-based)
		self.text = line_content

	def __str__(self):
		# Используем __str__ от KumirExecutionError для форматирования
		return KumirExecutionError.__str__(self)


# Ошибка, связанная с командами или состоянием робота
class RobotError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Ошибка для функциональности, которая еще не реализована
class KumirNotImplementedError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с именами (например, переменная не найдена)
class KumirNameError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с типами данных
class KumirTypeError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с индексами массивов (таблиц)
class KumirIndexError(KumirExecutionError):
	def __init__(self, message, line_index=None, column_index=None, line_content=None):
		super().__init__(message, line_index, column_index, line_content)


# Ошибка, связанная с некорректным вводом пользователя (ошибка преобразования)
class KumirInputError(KumirExecutionError):
	def __init__(self, message, line_index=None, line_content=None, original_type=None, input_value=None):
		super().__init__(message, line_index, line_content)
		self.original_type = original_type
		self.input_value = input_value
		# Сохраняем оригинальное сообщение для возможного использования
		# (хотя оно уже должно быть в self.args[0] от KumirExecutionError)
		self.original_message = message 


# Ошибка, связанная с неверным количеством или типом аргументов функции/процедуры
class KumirArgumentError(KumirEvalError):
	pass


# Можно добавить другие специфичные ошибки при необходимости

class ProcedureExitCalled(KumirExecutionError):
	pass

# FILE END: kumir_exceptions.py