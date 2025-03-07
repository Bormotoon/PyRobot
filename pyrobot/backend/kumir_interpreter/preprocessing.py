"""
Модуль preprocessing.py
@description Выполняет предварительную обработку исходного кода программы на языке KUMIR.
Модуль содержит функции для разделения исходного кода на строки, удаления комментариев,
разделения кода на вступительную часть и секции алгоритмов, а также парсинг заголовков алгоритмов.
"""


def preprocess_code(code):
	lines = []
	for line in code.splitlines():
		# Удаляем всё, что идёт после символа '|' или '#'
		if '|' in line:
			line = line.split('|')[0]
		if '#' in line:
			line = line.split('#')[0]
		line = line.strip()
		if not line:
			continue
		# Если строка равна "использовать робот" (без учета регистра), пропускаем её
		if line.lower() == "использовать робот":
			continue
		# Разбиваем строку по символу ';' (если их несколько)
		parts = [part.strip() for part in line.split(';') if part.strip()]
		lines.extend(parts)
	return lines


def separate_sections(lines):
	"""
	Разделяет список строк кода на вступительную часть (до первого алгоритма)
	и секции алгоритмов.

	Алгоритм определяется строкой, начинающейся со слова "алг".
	Вступительная часть — это строки, которые находятся до первого объявления алгоритма.

	Параметры:
	  lines (list of str): Список строк исходного кода.

	Возвращаемое значение:
	  tuple:
		- introduction (list of str): Строки вступительной части.
		- algorithms (list of dict): Список алгоритмов, где каждый алгоритм представлен словарем с ключами:
			 "header" – заголовок алгоритма,
			 "body" – список строк тела алгоритма.

	Исключения:
	  Генерируется Exception, если встречается "нач" без предшествующего "алг" или "кон" без "нач".
	"""
	introduction = []
	algorithms = []
	current_algo = None  # Текущий алгоритм, который собирается из строк
	in_algo = False  # Флаг, указывающий, что мы находимся внутри блока алгоритма (между "нач" и "кон")

	# Проходим по каждой строке кода
	for line in lines:
		lower_line = line.lower()
		if lower_line.startswith("алг"):
			# Если уже собирался предыдущий алгоритм, добавляем его в список
			if current_algo is not None:
				algorithms.append(current_algo)
			# Начинаем новый алгоритм: заголовок – текущая строка, тело пустое
			current_algo = {"header": line, "body": []}
			in_algo = False
		elif lower_line == "нач":
			# Если "нач" встречается без объявления алгоритма, генерируем ошибку
			if current_algo is None:
				raise Exception("Ошибка: 'нач' без 'алг'")
			in_algo = True  # Начинаем сбор строк тела алгоритма
		elif lower_line == "кон":
			# Если "кон" встречается без активного блока алгоритма, генерируем ошибку
			if current_algo is None or not in_algo:
				raise Exception("Ошибка: 'кон' без 'нач'")
			in_algo = False  # Завершаем сбор строк тела алгоритма
		else:
			if current_algo is None:
				# Если алгоритм еще не начат, строка относится ко вступительной части
				introduction.append(line)
			else:
				if in_algo:
					# Если находимся внутри блока алгоритма, добавляем строку в его тело
					current_algo["body"].append(line)
				else:
					# Если строка находится до начала тела алгоритма, дополняем заголовок
					current_algo["header"] += " " + line
	# Если остался не добавленный алгоритм, добавляем его
	if current_algo is not None:
		algorithms.append(current_algo)
	return introduction, algorithms


def parse_algorithm_header(header_line):
	"""
	Разбирает заголовок алгоритма, извлекая имя алгоритма и описание параметров (если они заданы).

	Пример заголовка:
	  алг тест (рез цел m, n, лит т, арг вещ y)

	Возвращает словарь с ключами:
	  - "raw": исходный заголовок (без слова "алг").
	  - "name": имя алгоритма (если указано).
	  - "params": список кортежей (режим, тип, имя) для параметров алгоритма.

	Параметры:
	  header_line (str): Строка заголовка алгоритма.

	Возвращаемое значение:
	  dict: Словарь с разобранной информацией о заголовке алгоритма.
	"""
	# Убираем лишние пробелы в начале и конце строки
	header_line = header_line.strip()
	# Если строка начинается со слова "алг" (без учета регистра), удаляем его
	if header_line.lower().startswith("алг"):
		header_line = header_line[3:].strip()
	params = []
	# Изначально всё содержимое заголовка считаем именем алгоритма
	name_part = header_line
	# Если в заголовке присутствуют параметры, они находятся в круглых скобках
	if "(" in header_line:
		parts = header_line.split("(", 1)
		name_part = parts[0].strip()  # Имя алгоритма
		# Извлекаем часть с параметрами, удаляя закрывающую скобку
		params_part = parts[1].rsplit(")", 1)[0]
		# Разбиваем параметры на токены
		tokens = params_part.split()
		mode = "арг"  # Режим параметров по умолчанию
		current_type = None  # Текущий тип параметра
		current_names = []  # Список имен для текущей группы параметров
		i = 0
		# Обрабатываем токены по порядку
		while i < len(tokens):
			token = tokens[i]
			# Если токен соответствует одному из режимов ("арг", "рез", "аргрез")
			if token in ["арг", "рез", "аргрез"]:
				# Если ранее были собраны имена и тип, добавляем их в список параметров
				if current_names and current_type is not None:
					for n in current_names:
						params.append((mode, current_type, n))
					current_names = []
				mode = token  # Обновляем режим параметра
				i += 1
				if i < len(tokens):
					current_type = tokens[i]  # Следующий токен задает тип
					i += 1
					# Собираем все последующие токены, которые не являются новыми режимами, как имена параметров
					while i < len(tokens) and tokens[i] not in ["арг", "рез", "аргрез"]:
						name = tokens[i].strip(",")
						current_names.append(name)
						i += 1
				else:
					break
			else:
				# Если режим не указан, то предполагается, что токен является либо типом, либо именем
				if current_type is None:
					current_type = token
				else:
					current_names.append(token.strip(","))
				i += 1
		# Если остались собранные имена и тип, добавляем их в список параметров
		if current_names and current_type is not None:
			for n in current_names:
				params.append((mode, current_type, n))
	# Формируем итоговую информацию о заголовке алгоритма
	header_info = {"raw": header_line, "name": name_part if name_part else None, "params": params}
	return header_info
