# FILE START: kumir_exceptions.py
"""
Модуль для определения кастомных исключений интерпретатора Кумир.
Вынесен в отдельный файл для предотвращения циклических импортов.
"""


# Базовый класс для ошибок во время выполнения кода Кумира
class KumirExecutionError(Exception):
	def __init__(self, message, line_index=None, line_content=None):
		super().__init__(message)
		self.line_index = line_index
		self.line_content = line_content

	def __str__(self):
		base_message = super().__str__()
		context = ""
		if self.line_index is not None:
			context += f"строка {self.line_index + 1}"
		if self.line_content is not None:
			if self.line_index is not None:
				context += ":"
			context += f" '{self.line_content}'"
		return f"{base_message} ({context.strip()})" if context else base_message


# Ошибка, связанная с объявлениями
class DeclarationError(KumirExecutionError):
	pass


# Ошибка, связанная с присваиванием
class AssignmentError(KumirExecutionError):
	pass


# Ошибка, связанная с вводом/выводом
class InputOutputError(KumirExecutionError):
	pass


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
	pass


# Ошибка, связанная с командами или состоянием робота
class RobotError(KumirExecutionError):
	pass

# Можно добавить другие специфичные ошибки при необходимости

# FILE END: kumir_exceptions.py