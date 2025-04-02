# FILE START: declarations.py
"""
Модуль declarations.py
@description Обработка объявлений переменных, присваиваний, ввода/вывода.
"""
import logging
import math
import re
import sys  # Добавим sys для доступа к stdin/stdout по умолчанию

# Импортируем функции для определения потоков ввода/вывода по умолчанию
from .file_functions import get_default_output  # Убедитесь, что этот импорт корректен
from .identifiers import is_valid_identifier
from .safe_eval import safe_eval, KumirEvalError

logger = logging.getLogger('KumirDeclarations')

ALLOWED_TYPES = {"цел", "вещ", "лог", "сим", "лит"}
MAX_INT = 2147483647


class DeclarationError(Exception):
	pass


class AssignmentError(Exception):
	pass


class InputOutputError(Exception):
	pass


# --->>> НОВОЕ ИСКЛЮЧЕНИЕ ДЛЯ ЗАПРОСА ВВОДА <<<---
class KumirInputRequiredError(Exception):
	"""Сигнализирует, что для продолжения выполнения требуется ввод пользователя."""

	def __init__(self, var_name, prompt, target_type):
		self.var_name = var_name
		self.prompt = prompt
		self.target_type = target_type  # Сохраняем тип для возможной валидации на клиенте
		message = f"Требуется ввод для переменной '{var_name}' (тип: {target_type}). Подсказка: {prompt}"
		super().__init__(message)


# --- <<< КОНЕЦ НОВОГО ИСКЛЮЧЕНИЯ >>> ---


def _validate_and_convert_value(value, target_type, var_name_for_error):
	"""
	Проверяет и конвертирует значение к целевому типу KUMIR.
	Вспомогательная функция для присваивания и ввода.
	"""
	try:
		if target_type == "цел":
			converted_value = int(value)
			if not (-MAX_INT - 1 <= converted_value <= MAX_INT):
				raise ValueError(f"Значение {converted_value} выходит за допустимый диапазон для типа 'цел'.")
		elif target_type == "вещ":
			converted_value = float(value)
			if not math.isfinite(converted_value):
				raise ValueError(f"Значение {converted_value} не является конечным числом для типа 'вещ'.")
		elif target_type == "лог":
			# Сначала проверяем булевы и строки "да"/"нет"
			if isinstance(value, bool):
				converted_value = value
			elif isinstance(value, str):
				low_val = value.lower().strip()
				if low_val == "да":
					converted_value = True
				elif low_val == "нет":
					converted_value = False
				else:
					# Если строка не "да"/"нет", пытаемся конвертировать как число
					try:
						# Пытаемся как float сначала, чтобы обработать "1.0" и т.д.
						num_val = float(value)
						converted_value = (num_val != 0)
					except ValueError:
						# Если и как float не получилось, то ошибка
						raise ValueError(
							f"Недопустимое логическое значение: '{value}'. Ожидалось 'да', 'нет' или число.")
			elif isinstance(value, (int, float)):  # Числа тоже конвертируем (0 - ложь, остальное - истина)
				converted_value = (value != 0)
			else:  # Общий случай bool() для других типов (менее предсказуемо)
				converted_value = bool(value)
		elif target_type == "сим":
			converted_value = str(value)
			if len(converted_value) != 1:
				raise ValueError("Значение для типа 'сим' должно быть ровно одним символом.")
		elif target_type == "лит":
			converted_value = str(value)
		else:
			# Эта ветка не должна достигаться, если ALLOWED_TYPES проверен ранее
			raise TypeError(f"Неподдерживаемый целевой тип: {target_type}")

		return converted_value

	except (ValueError, TypeError) as e:
		# Перехватываем ошибки конвертации и добавляем контекст
		raise AssignmentError(  # Используем AssignmentError, т.к. чаще всего вызывается при присваивании/вводе
			f"Ошибка преобразования значения '{value}' к типу '{target_type}' для переменной '{var_name_for_error}': {e}")
	except Exception as e:  # Ловим другие неожиданные ошибки
		raise AssignmentError(f"Неожиданная ошибка при преобразовании значения для '{var_name_for_error}': {e}")


def process_declaration(line, env):
	"""
	Обрабатывает строку объявления переменной или таблицы.
	"""
	logger.debug(f"Processing declaration: '{line}'")
	tokens = line.split()
	if not tokens:
		raise DeclarationError("Пустая строка объявления.")

	decl_type_raw = tokens[0].lower()
	if decl_type_raw not in ALLOWED_TYPES:
		# Эта проверка может быть избыточна, если вызывающая функция уже проверила
		raise DeclarationError(f"Неизвестный тип переменной: '{tokens[0]}'")

	idx = 1
	is_table = False
	if idx < len(tokens) and tokens[idx].lower().startswith("таб"):
		is_table = True
		idx += 1
		logger.debug(f"Declaration is for a table (Type: {decl_type_raw}).")

	rest_of_line = " ".join(tokens[idx:])
	if not rest_of_line:
		raise DeclarationError(f"Отсутствуют имена переменных после типа '{tokens[0]}'.")

	# Разделяем идентификаторы по запятой
	identifiers_raw = [ident.strip() for ident in rest_of_line.split(",") if ident.strip()]
	if not identifiers_raw:
		raise DeclarationError(f"Не найдены имена переменных в строке объявления: '{line}'")

	for ident_raw in identifiers_raw:
		var_name = ident_raw
		dimensions = None  # Пока не парсим размерности

		# Проверяем синтаксис для таблиц (очень базово)
		if is_table and "[" in ident_raw and ident_raw.endswith("]"):
			match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", ident_raw)
			if match:
				var_name = match.group(1).strip()
				dim_spec = match.group(2).strip()
				# TODO: Реализовать парсинг dim_spec ('1:10, 1:5') в структуру данных
				dimensions = dim_spec  # Сохраняем как строку для информации
				logger.debug(f"Table '{var_name}' dimensions specified (raw): [{dimensions}]")
			else:
				# Синтаксис объявления таблицы некорректен
				raise DeclarationError(f"Некорректный синтаксис объявления таблицы: '{ident_raw}'")
		elif is_table:
			# Объявлена таблица без указания размерности (динамическая?)
			logger.warning(f"Объявлена таблица '{var_name}', но размеры не указаны (динамическое создание?).")
		# В зависимости от правил Кумира, это может быть разрешено или нет.
		# Пока разрешаем, но доступ к элементам потребует проверки.
		elif "[" in ident_raw:  # Скобки у не-таблицы - ошибка
			raise DeclarationError(f"Неожиданные скобки '[]' в объявлении переменной (не таблицы): '{ident_raw}'")

		# Проверяем корректность имени переменной
		if not is_valid_identifier(var_name, decl_type_raw):
			raise DeclarationError(f"Недопустимое имя переменной: '{var_name}'")
		# Проверяем, не объявлена ли уже переменная
		if var_name in env:
			raise DeclarationError(f"Переменная '{var_name}' уже объявлена.")

		# Добавляем переменную в окружение
		env[var_name] = {
			"type": decl_type_raw,
			"value": {} if is_table else None,  # Таблицы инициализируем пустым словарем
			"kind": "global",  # Уровень видимости - пока считаем глобальным
			"is_table": is_table,
			"dimensions": dimensions  # Сохраняем информацию о размерности (если была)
		}
		table_str = "таблица" if is_table else "переменная"
		logger.info(f"Declared {table_str} '{var_name}' type '{decl_type_raw}'.")

	return True  # Успешно обработано


def process_assignment(line, env, robot=None):
	"""
	Обрабатывает строку присваивания (:=).
	"""
	logger.debug(f"Processing assignment: '{line}'")
	parts = line.split(":=", 1)
	if len(parts) != 2:
		raise AssignmentError(f"Неверный синтаксис присваивания (отсутствует или несколько ':='): {line}")

	left_raw, right_expr = parts[0].strip(), parts[1].strip()
	if not left_raw:
		raise AssignmentError("Отсутствует переменная слева от ':='.")
	if not right_expr:
		raise AssignmentError("Отсутствует выражение справа от ':='.")

	# Вычисляем правую часть выражения
	try:
		rhs_value = safe_eval(right_expr, env, robot)
		logger.debug(f"Evaluated RHS '{right_expr}' -> {rhs_value} (type: {type(rhs_value)})")
	except KumirEvalError as e:
		raise KumirEvalError(f"Ошибка вычисления выражения '{right_expr}' в правой части присваивания: {e}")
	except Exception as e:
		logger.error(f"Unexpected error evaluating RHS '{right_expr}': {e}", exc_info=True)
		raise KumirEvalError(f"Неожиданная ошибка вычисления '{right_expr}': {e}")

	# Проверяем, является ли левая часть элементом таблицы
	table_match = re.match(r"^([a-zA-Zа-яА-ЯёЁ_][a-zA-Zа-яА-ЯёЁ0-9_\s]*?)\[(.+)\]$", left_raw)

	if table_match:
		# Присваивание элементу таблицы
		var_name = table_match.group(1).strip()
		indices_expr_str = table_match.group(2).strip()  # Строка с индексами "i, j+1"
		logger.debug(f"Assignment target is table '{var_name}' with indices expr '{indices_expr_str}'")

		if var_name not in env:
			raise DeclarationError(f"Таблица '{var_name}' не объявлена.")
		var_info = env[var_name]
		if not var_info.get("is_table"):
			raise AssignmentError(f"Переменная '{var_name}' не является таблицей, но используется с индексами.")

		# Вычисляем выражения индексов
		index_tokens = [token.strip() for token in indices_expr_str.split(",") if token.strip()]
		if not index_tokens:
			raise AssignmentError(f"Отсутствуют индексы для таблицы '{var_name}'.")

		try:
			indices = []
			for token in index_tokens:
				index_val = safe_eval(token, env, robot)
				# В Кумире индексы таблиц должны быть целыми
				try:
					indices.append(int(index_val))
				except (ValueError, TypeError):
					raise KumirEvalError(
						f"Индекс таблицы '{token}' (вычислен как '{index_val}') не является целым числом.")
			indices = tuple(indices)  # Кортеж можно использовать как ключ словаря
			logger.debug(f"Evaluated table indices -> {indices}")

		except KumirEvalError as e:
			raise KumirEvalError(f"Ошибка вычисления индексов '{indices_expr_str}' для таблицы '{var_name}': {e}")
		except Exception as e:
			logger.error(f"Unexpected error evaluating table indices '{indices_expr_str}': {e}", exc_info=True)
			raise KumirEvalError(f"Неожиданная ошибка вычисления индексов '{indices_expr_str}': {e}")

		# TODO: Проверить выход индексов за границы, если размерности были заданы

		# Конвертируем значение правой части к типу таблицы
		target_type = var_info["type"]
		try:
			converted_value = _validate_and_convert_value(rhs_value, target_type, f"{var_name}[{indices_expr_str}]")
		except AssignmentError as e:
			# Добавляем информацию про индексы к ошибке
			raise AssignmentError(f"Ошибка присваивания элементу {var_name}{list(indices)}: {e}")

		# Выполняем присваивание
		# Убеждаемся, что value - это словарь
		if var_info["value"] is None or not isinstance(var_info["value"], dict):
			var_info["value"] = {}  # Инициализируем, если нужно
		var_info["value"][indices] = converted_value
		logger.info(f"Assigned value {converted_value} to table element {var_name}{list(indices)}.")

	else:
		# Присваивание простой переменной
		var_name = left_raw
		logger.debug(f"Assignment target is simple variable '{var_name}'")

		if var_name not in env:
			raise DeclarationError(f"Переменная '{var_name}' не объявлена.")
		var_info = env[var_name]
		if var_info.get("is_table"):
			raise AssignmentError(f"Попытка присвоить значение всей таблице '{var_name}' без указания индексов.")

		# Конвертируем значение правой части к типу переменной
		target_type = var_info["type"]
		converted_value = _validate_and_convert_value(rhs_value, target_type, var_name)

		# Выполняем присваивание
		var_info["value"] = converted_value
		logger.info(f"Assigned value {converted_value} to variable '{var_name}'.")


def process_output(line, env, robot=None, interpreter=None):
	"""
	Обрабатывает команду 'вывод'.
	"""
	logger.debug(f"Processing output: '{line}'")
	content_part = line[len("вывод"):].strip()
	append_newline = True
	# Проверяем наличие " нс" в конце (с пробелом)
	if content_part.lower().endswith(" нс"):
		content_part = content_part[:-len(" нс")].strip()
		append_newline = False
	# Отдельный случай, если вся строка "вывод нс"
	elif content_part.lower() == "нс":
		content_part = ""
		append_newline = False

	output_str_parts = []
	if content_part:
		# TODO: Использовать более надежный парсинг для разделения по запятым вне строк
		# Пока используем простой split
		parts_to_eval = [part.strip() for part in content_part.split(",") if part.strip()]

		for part_expr in parts_to_eval:
			if not part_expr: continue  # Пропускаем пустые части (например, из-за двойных запятых)
			try:
				# Вычисляем каждую часть выражения
				value = safe_eval(part_expr, env, robot)

				# Форматируем результат для вывода
				if isinstance(value, bool):
					output_str_parts.append("да" if value else "нет")
				# Добавить форматирование для float, если нужно (например, количество знаков)
				# elif isinstance(value, float):
				#     output_str_parts.append(f"{value:.6f}") # Пример: 6 знаков после запятой
				else:
					output_str_parts.append(str(value))  # Преобразуем в строку

				logger.debug(f"Evaluated output part '{part_expr}' -> '{output_str_parts[-1]}'")

			except KumirEvalError as e:
				logger.error(f"Error evaluating output part '{part_expr}': {e}")
				raise InputOutputError(f"Ошибка вычисления выражения '{part_expr}' в команде 'вывод': {e}")
			except Exception as e:
				logger.error(f"Unexpected error evaluating output part '{part_expr}': {e}", exc_info=True)
				raise InputOutputError(f"Неожиданная ошибка в 'вывод' для '{part_expr}': {e}")

	# Собираем строку вывода
	output_str = "".join(output_str_parts)  # Части конкатенируются без пробелов
	if append_newline:
		output_str += "\n"

	# Добавляем в буфер интерпретатора или выводим напрямую
	if interpreter:
		# Убедимся, что атрибут output существует
		if not hasattr(interpreter, 'output') or interpreter.output is None:
			interpreter.output = ""
		interpreter.output += output_str
		# Логируем экранированную строку для читаемости
		output_str_escaped = output_str.replace('\n', '\\n').replace('\r', '\\r')
		logger.info(f"Appended to output buffer: '{output_str_escaped}'")
	else:
		# Если интерпретатор не передан, выводим в стандартный поток вывода
		# Используем get_default_output для поддержки перенаправления вывода Кумира
		output_stream = get_default_output() or sys.stdout
		try:
			print(output_str, end="", file=output_stream, flush=True)
			logger.warning("Interpreter context not provided for 'вывод', printed to default output.")
		except Exception as e:
			logger.error(f"Error writing to default output stream: {e}")


def process_input(line, env):
	"""
	Обрабатывает команду 'ввод'. Вместо блокирующего чтения, генерирует
	исключение KumirInputRequiredError для запроса ввода у пользователя.
	"""
	logger.debug(f"Processing 'ввод': '{line}'. Raising InputRequiredError.")
	var_name = line[len("ввод"):].strip()
	if not var_name:
		raise InputOutputError("Отсутствует имя переменной после 'ввод'.")

	# Проверяем корректность имени переменной
	if not is_valid_identifier(var_name, ""):  # Тип не важен для проверки имени
		raise InputOutputError(f"Недопустимое имя переменной для ввода: '{var_name}'")

	# Проверяем, объявлена ли переменная
	if var_name not in env:
		raise DeclarationError(f"Переменная '{var_name}' не объявлена перед использованием в 'ввод'.")

	var_info = env[var_name]
	# Проверяем, не таблица ли это
	if var_info.get("is_table"):
		# TODO: Добавить поддержку ввода элемента таблицы, если нужно
		# Потребуется парсинг вида "Таблица[индекс1, ...]" в имени переменной
		raise InputOutputError(
			f"Команда 'ввод' не поддерживается для таблиц ('{var_name}'). Введите элемент таблицы, если это возможно.")

	target_type = var_info["type"]
	# Формируем строку-подсказку для пользователя
	prompt = f"Введите значение для '{var_name}' (тип: {target_type}): "

	# Генерируем исключение для запроса ввода
	logger.info(f"Input required for variable '{var_name}' (type: {target_type}). Raising exception.")
	raise KumirInputRequiredError(var_name=var_name, prompt=prompt, target_type=target_type)
# Код ниже этой строки не будет выполнен

# FILE END: declarations.py
