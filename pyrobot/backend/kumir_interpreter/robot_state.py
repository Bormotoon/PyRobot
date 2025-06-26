# FILE START: robot_state.py
import logging

# Импортируем RobotError из нового файла
from .kumir_exceptions import RobotError

logger = logging.getLogger('SimulatedRobot')
# ... (остальной код логгера без изменений) ...
logger.propagate = False
if not logger.handlers:
	h = logging.StreamHandler()
	h.setFormatter(logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'))
	logger.addHandler(h)
logger.setLevel(logging.INFO)  # Уровень можно настроить


# Определение RobotError УДАЛЕНО

class SimulatedRobot:
	""" Состояние и действия симулированного робота на поле. """

	def __init__(self, width, height, initial_pos=None, initial_walls=None, initial_markers=None,
	             initial_colored_cells=None, initial_symbols=None, initial_radiation=None,
	             initial_temperature=None):
		# Проверяем ограничения размеров поля согласно документации КуМир
		# Столбцы: 1-255, Строки: 1-128
		if not isinstance(width, int) or not (1 <= width <= 255): 
			raise ValueError("Width must be an integer between 1 and 255 (Kumir spec)")
		if not isinstance(height, int) or not (1 <= height <= 128): 
			raise ValueError("Height must be an integer between 1 and 128 (Kumir spec)")
		
		self.width = width
		self.height = height
		self.logger = logger
		# Используем _clamp_pos для инициализации, чтобы гарантировать корректность
		self.robot_pos = self._clamp_pos(initial_pos or {'x': 0, 'y': 0})
		# Гарантируем, что это множества
		self.walls = set(initial_walls) if initial_walls is not None else set()
		self.colored_cells = set(initial_colored_cells) if initial_colored_cells is not None else set()
		# Гарантируем, что это словари
		self.markers = dict(initial_markers) if initial_markers is not None else {}
		self.symbols = dict(initial_symbols) if initial_symbols is not None else {}
		self.radiation = dict(initial_radiation) if initial_radiation is not None else {}
		self.temperature = dict(initial_temperature) if initial_temperature is not None else {}
		
		# Направление ошибки движения для визуализации (left, right, up, down или None)
		self.error_direction = None

		self.permanent_walls = self._setup_permanent_walls()
		self.logger.info(
			f"Robot initialized: {width}x{height} at {self.robot_pos}. Walls: {len(self.walls)}, Markers: {len(self.markers)}, Colored: {len(self.colored_cells)}")

	def _clamp_pos(self, pos):
		# Гарантирует, что координаты находятся в пределах поля
		x = 0
		y = 0
		if isinstance(pos, dict):
			# Проверяем тип перед доступом
			raw_x = pos.get('x', 0)
			raw_y = pos.get('y', 0)
			try:
				x = int(raw_x)
			except (ValueError, TypeError):
				self.logger.warning(f"Invalid initial X position '{raw_x}', using 0.")
				x = 0
			try:
				y = int(raw_y)
			except (ValueError, TypeError):
				self.logger.warning(f"Invalid initial Y position '{raw_y}', using 0.")
				y = 0
		else:
			self.logger.warning(f"Invalid initial_pos format: {pos}. Using (0,0).")

		clamped_x = min(max(0, x), self.width - 1)
		clamped_y = min(max(0, y), self.height - 1)
		return {'x': clamped_x, 'y': clamped_y}

	def _setup_permanent_walls(self):
		# Создает множество строк, представляющих границы поля
		w = set()
		# Горизонтальные
		for x in range(self.width):
			w.add(f"{x},0,{x + 1},0")  # Верхняя граница
			w.add(f"{x},{self.height},{x + 1},{self.height}")  # Нижняя граница
		# Вертикальные
		for y in range(self.height):
			w.add(f"0,{y},0,{y + 1}")  # Левая граница
			w.add(f"{self.width},{y},{self.width},{y + 1}")  # Правая граница
		return w

	def reset(self, new_width=None, new_height=None):
		""" Resets robot state, optionally resizes. """
		# ... (код reset без изменений) ...
		if new_width is not None and isinstance(new_width, int) and new_width >= 1: self.width = new_width
		if new_height is not None and isinstance(new_height, int) and new_height >= 1: self.height = new_height
		self.robot_pos = {'x': 0, 'y': 0}
		self.walls.clear();
		self.markers.clear();
		self.colored_cells.clear()
		self.symbols.clear();
		self.radiation.clear();
		self.temperature.clear()
		self.permanent_walls = self._setup_permanent_walls()
		self.logger.info(f"Robot Reset: Field size {self.width}x{self.height}, Position {self.robot_pos}.")

	def reset_position(self):
		"""Сбрасывает только позицию робота (для совместимости)."""
		self.robot_pos = {'x': 0, 'y': 0}
		self.logger.info("Robot position reset to (0,0).")

	def _is_wall_between(self, x1, y1, x2, y2):
		""" Проверяет наличие стены (пользовательской или границы) между двумя соседними клетками. """
		wall_key = None
		# Определяем ключ стены в зависимости от направления
		if x2 > x1:  # Движение вправо
			wall_key = f"{x2},{y1},{x2},{y1 + 1}"  # Правая стена клетки (x1, y1)
		elif x1 > x2:  # Движение влево
			wall_key = f"{x1},{y1},{x1},{y1 + 1}"  # Левая стена клетки (x1, y1)
		elif y2 > y1:  # Движение вниз
			wall_key = f"{x1},{y2},{x1 + 1},{y2}"  # Нижняя стена клетки (x1, y1)
		elif y1 > y2:  # Движение вверх
			wall_key = f"{x1},{y1},{x1 + 1},{y1}"  # Верхняя стена клетки (x1, y1)

		if wall_key:
			# Проверяем наличие стены в пользовательских стенах и границах
			return wall_key in self.walls or wall_key in self.permanent_walls
		return False  # Нет движения или не соседние клетки

	def is_move_allowed(self, target_x, target_y):
		""" Проверяет, разрешено ли движение в целевую клетку. """
		# 1. Проверка выхода за границы поля
		if not (0 <= target_x < self.width and 0 <= target_y < self.height):
			self.logger.debug(
				f"Move denied: Target ({target_x},{target_y}) is outside field bounds (0..{self.width - 1}, 0..{self.height - 1}).")
			return False

		# 2. Проверка наличия стены между текущей и целевой клетками
		current_x, current_y = self.robot_pos["x"], self.robot_pos["y"]
		if self._is_wall_between(current_x, current_y, target_x, target_y):
			self.logger.debug(
				f"Move denied: Wall detected between ({current_x},{current_y}) and ({target_x},{target_y}).")
			return False

		# Если прошли все проверки - движение разрешено
		return True

	# --- Методы движения (используют is_move_allowed) ---
	def go_right(self):
		nx, ny = self.robot_pos["x"] + 1, self.robot_pos["y"]
		if self.is_move_allowed(nx, ny):
			self.robot_pos["x"] = nx
			self.error_direction = None  # Очищаем ошибку движения при успешном движении
			self.logger.info(f"Moved Right -> ({nx},{ny})")
		else:
			self.error_direction = "right"  # Устанавливаем направление ошибки
			raise RobotError("Стена/граница справа!")

	def go_left(self):
		nx, ny = self.robot_pos["x"] - 1, self.robot_pos["y"]
		if self.is_move_allowed(nx, ny):
			self.robot_pos["x"] = nx
			self.error_direction = None  # Очищаем ошибку движения при успешном движении
			self.logger.info(f"Moved Left -> ({nx},{ny})")
		else:
			self.error_direction = "left"  # Устанавливаем направление ошибки
			raise RobotError("Стена/граница слева!")

	def go_up(self):
		nx, ny = self.robot_pos["x"], self.robot_pos["y"] - 1
		if self.is_move_allowed(nx, ny):
			self.robot_pos["y"] = ny
			self.error_direction = None  # Очищаем ошибку движения при успешном движении
			self.logger.info(f"Moved Up -> ({nx},{ny})")
		else:
			self.error_direction = "up"  # Устанавливаем направление ошибки
			raise RobotError("Стена/граница сверху!")

	def go_down(self):
		nx, ny = self.robot_pos["x"], self.robot_pos["y"] + 1
		if self.is_move_allowed(nx, ny):
			self.robot_pos["y"] = ny
			self.error_direction = None  # Очищаем ошибку движения при успешном движении
			self.logger.info(f"Moved Down -> ({nx},{ny})")
		else:
			self.error_direction = "down"  # Устанавливаем направление ошибки
			raise RobotError("Стена/граница снизу!")

	# --- Метод закраски (без ошибки при повторе) ---
	def do_paint(self):
		""" Закрашивает текущую клетку. Не генерирует ошибку, если уже закрашена. """
		k = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		if k in self.colored_cells:
			self.logger.debug(f"Cell {k} is already painted. No action taken.")  # Используем debug или info
		else:
			self.colored_cells.add(k)
			self.logger.info(f"Cell {k} painted.")

	# --- Сенсоры ---
	def check_direction(self, direction, status_to_check):
		"""
		Проверяет состояние в указанном направлении ('wall' или 'free').
		Использует _is_wall_between для проверки стен.
		"""
		cx, cy = self.robot_pos['x'], self.robot_pos['y']
		tx, ty = cx, cy  # Координаты целевой клетки

		if direction == "left":
			tx -= 1
		elif direction == "right":
			tx += 1
		elif direction == "up":
			ty -= 1
		elif direction == "down":
			ty += 1
		else:
			raise ValueError(f"Unknown direction for check: {direction}")

		# Проверяем, находится ли целевая клетка вне поля
		is_outside = not (0 <= tx < self.width and 0 <= ty < self.height)

		# Проверяем стену между текущей и целевой (если целевая в пределах поля)
		has_wall = False
		if not is_outside:
			has_wall = self._is_wall_between(cx, cy, tx, ty)

		# Определяем результат в зависимости от того, что проверяем
		if status_to_check == "wall":
			# Стена есть, если она существует ИЛИ если вышли за границу
			result = has_wall or is_outside
			self.logger.debug(
				f"Check '{direction} wall' from ({cx},{cy}): outside={is_outside}, wall_exists={has_wall} -> {result}")
			return result
		elif status_to_check == "free":
			# Свободно, только если НЕ вышли за границу И НЕТ стены
			result = not is_outside and not has_wall
			self.logger.debug(
				f"Check '{direction} free' from ({cx},{cy}): outside={is_outside}, wall_exists={has_wall} -> {result}")
			return result
		else:
			raise ValueError(f"Unknown status for check_direction: {status_to_check}")

	def check_cell(self, status_to_check):
		""" Проверяет состояние текущей клетки ('painted' или 'clear'). """
		k = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		is_painted = k in self.colored_cells

		if status_to_check == "painted":
			self.logger.debug(f"Check 'cell painted' at {k}: {is_painted}")
			return is_painted
		elif status_to_check == "clear":
			self.logger.debug(f"Check 'cell clear' at {k}: {not is_painted}")
			return not is_painted
		else:
			raise ValueError(f"Unknown status for check_cell: {status_to_check}")

	def do_measurement(self, measure_type):
		""" Возвращает значение радиации или температуры в текущей клетке. """
		pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		self.logger.debug(f"Measure '{measure_type}' at {pos_key}")
		if measure_type == "radiation":
			value = self.radiation.get(pos_key, 0.0)  # Default to 0.0
			# Ограничиваем значение радиации в соответствии с документацией (0-99)
			value = max(0.0, min(99.0, float(value)))
			self.logger.info(f"Radiation at {pos_key}: {value}")
			return value
		elif measure_type == "temperature":
			value = self.temperature.get(pos_key, 0)  # Default to 0
			# Ограничиваем температуру в соответствии с документацией (-273 до +233)
			value = max(-273, min(233, int(value)))
			self.logger.info(f"Temperature at {pos_key}: {value}")
			return value
		else:
			self.logger.warning(f"Unknown measurement type requested: {measure_type}. Returning 0.")
			# В оригинальном Кумире может быть ошибка, но возврат 0 безопаснее.
			# raise RobotError(f"Неизвестный тип измерения: {measure_type}")
			return 0

	def put_marker(self):
		""" Поставить маркер в текущей клетке. """
		pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		self.logger.debug(f"Attempting to put marker at {pos_key}")
		
		# Проверяем, есть ли уже маркер в этой клетке
		if pos_key in self.markers and self.markers[pos_key] > 0:
			self.logger.warning(f"Marker already exists at {pos_key}")
			raise RobotError(f"В клетке ({self.robot_pos['x']},{self.robot_pos['y']}) уже есть маркер")
		
		# Ставим маркер
		self.markers[pos_key] = 1
		self.logger.info(f"Marker placed at {pos_key}")

	def pick_marker(self):
		""" Убрать маркер из текущей клетки. """
		pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		self.logger.debug(f"Attempting to pick marker at {pos_key}")
		
		# Проверяем, есть ли маркер в этой клетке
		if pos_key not in self.markers or self.markers[pos_key] <= 0:
			self.logger.warning(f"No marker found at {pos_key}")
			raise RobotError(f"В клетке ({self.robot_pos['x']},{self.robot_pos['y']}) нет маркера")
		
		# Убираем маркер
		del self.markers[pos_key]
		self.logger.info(f"Marker picked from {pos_key}")

	def is_marker_here(self):
		""" Проверить, есть ли маркер в текущей клетке. """
		pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		has_marker = pos_key in self.markers and self.markers[pos_key] > 0
		self.logger.debug(f"Check marker at {pos_key}: {has_marker}")
		return has_marker

# FILE END: robot_state.py