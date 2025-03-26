import logging

# Configure logger for this module
logger = logging.getLogger('SimulatedRobot')
# Prevent duplicate logging if root logger is also configured
logger.propagate = False
if not logger.handlers:
	handler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - SimulatedRobot - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
logger.setLevel(logging.INFO)  # Default level, can be changed


class RobotError(Exception):
	"""Custom exception for robot-specific errors (e.g., hitting a wall)."""
	pass


class SimulatedRobot:
	"""
	Состояние и действия симулированного робота на поле.
	Отвечает за перемещение, взаимодействие с клетками и стенами.
	Не занимается парсингом или выполнением языка КУМИР.
	"""

	def __init__(self, width, height, initial_pos=None, initial_walls=None, initial_markers=None,
				 initial_colored_cells=None):
		"""
		Инициализирует робота с заданными размерами поля и начальным состоянием.

		Args:
			width (int): Ширина поля.
			height (int): Высота поля.
			initial_pos (dict, optional): Начальная позиция {'x': int, 'y': int}. Defaults to {'x': 0, 'y': 0}.
			initial_walls (set, optional): Множество стен в формате "x1,y1,x2,y2". Defaults to empty set.
			initial_markers (dict, optional): Словарь маркеров { "x,y": value }. Defaults to empty dict.
			initial_colored_cells (set, optional): Множество закрашенных клеток "x,y". Defaults to empty set.
		"""
		if not isinstance(width, int) or width < 1:
			raise ValueError("Width must be a positive integer.")
		if not isinstance(height, int) or height < 1:
			raise ValueError("Height must be a positive integer.")

		self.width = width
		self.height = height
		self.logger = logger  # Use the module's logger

		# Set initial position, ensuring it's clamped within new bounds
		default_pos = {'x': 0, 'y': 0}
		pos = initial_pos if initial_pos else default_pos
		self.robot_pos = self._clamp_pos(pos)

		self.walls = initial_walls if initial_walls is not None else set()
		self.markers = initial_markers if initial_markers is not None else {}
		self.colored_cells = initial_colored_cells if initial_colored_cells is not None else set()

		# Generate permanent boundary walls based on dimensions
		self.permanent_walls = self._setup_permanent_walls()

		self.logger.info(f"Robot initialized on {width}x{height} field at {self.robot_pos}")

	def _clamp_pos(self, pos):
		"""Ensure position is within the valid field bounds."""
		clamped_x = min(max(0, pos.get('x', 0)), self.width - 1)
		clamped_y = min(max(0, pos.get('y', 0)), self.height - 1)
		return {'x': clamped_x, 'y': clamped_y}

	def _setup_permanent_walls(self):
		"""Generates the set of permanent boundary walls."""
		new_walls = set()
		# Top border
		for x in range(self.width):
			new_walls.add(f"{x},0,{x + 1},0")
		# Bottom border
		for x in range(self.width):
			new_walls.add(f"{x},{self.height},{x + 1},{self.height}")
		# Left border
		for y in range(self.height):
			new_walls.add(f"0,{y},0,{y + 1}")
		# Right border
		for y in range(self.height):
			new_walls.add(f"{self.width},{y},{self.width},{y + 1}")
		self.logger.debug(f"Generated {len(new_walls)} permanent boundary walls.")
		return new_walls

	def reset(self, new_width=None, new_height=None):
		"""
		Сбрасывает состояние робота к начальному (позиция 0,0)
		и опционально изменяет размеры поля.
		Args:
		    new_width (int, optional): Новая ширина поля.
            new_height (int, optional): Новая высота поля.
		"""
		if new_width is not None and isinstance(new_width, int) and new_width >= 1:
			self.width = new_width
		if new_height is not None and isinstance(new_height, int) and new_height >= 1:
			self.height = new_height

		self.robot_pos = {'x': 0, 'y': 0}  # Reset position
		self.walls.clear()  # Clear user walls
		self.markers.clear()
		self.colored_cells.clear()
		self.permanent_walls = self._setup_permanent_walls()  # Regenerate boundary walls
		self.logger.info(f"Robot state reset. Field size {self.width}x{self.height}. Position {self.robot_pos}.")

	def is_move_allowed(self, target_x, target_y):
		"""
		Проверяет, разрешено ли движение из текущей позиции в целевую (target_x, target_y),
		учитывая границы поля и все стены (пользовательские и постоянные).

		Args:
			target_x (int): Целевая координата X.
			target_y (int): Целевая координата Y.

		Returns:
			bool: True, если движение разрешено, иначе False.
		"""
		self.logger.debug(f"Checking move from {self.robot_pos} to ({target_x}, {target_y})")

		# 1. Check Field Bounds
		if not (0 <= target_x < self.width and 0 <= target_y < self.height):
			self.logger.debug(
				f"Move disallowed: Target ({target_x}, {target_y}) is out of bounds ({self.width}x{self.height}).")
			return False

		# 2. Determine Wall Key to Check
		current_x = self.robot_pos["x"]
		current_y = self.robot_pos["y"]
		wall_key = None

		if target_x > current_x:  # Moving right
			wall_key = f"{target_x},{current_y},{target_x},{current_y + 1}"  # Vertical wall at x=target_x
		elif target_x < current_x:  # Moving left
			wall_key = f"{current_x},{current_y},{current_x},{current_y + 1}"  # Vertical wall at x=current_x
		elif target_y > current_y:  # Moving down
			wall_key = f"{current_x},{target_y},{current_x + 1},{target_y}"  # Horizontal wall at y=target_y
		elif target_y < current_y:  # Moving up
			wall_key = f"{current_x},{current_y},{current_x + 1},{current_y}"  # Horizontal wall at y=current_y
		else:
			# No movement, technically allowed but shouldn't happen in move methods
			self.logger.debug("No actual movement detected.")
			return True  # Or False? Let's say True, no wall to block staying put.

		# 3. Check Against Permanent and User Walls
		# === FIX HERE: Use 'in' operator for set membership check ===
		if wall_key in self.permanent_walls:
			self.logger.debug(f"Move disallowed: Permanent wall detected at {wall_key}.")
			return False
		if wall_key in self.walls:
			self.logger.debug(f"Move disallowed: User wall detected at {wall_key}.")
			return False
		# ===========================================================

		# If no bounds or walls block, move is allowed
		self.logger.debug("Move allowed.")
		return True

	def go_right(self):
		"""Пытается переместить робота на одну клетку вправо."""
		new_x = self.robot_pos["x"] + 1
		target_y = self.robot_pos["y"]
		self.logger.debug(f"Attempting to move right to ({new_x}, {target_y})")
		if self.is_move_allowed(new_x, target_y):
			self.robot_pos["x"] = new_x
			self.logger.info(f"Robot moved right. New position: {self.robot_pos}")
		else:
			raise RobotError("Робот упёрся в стену или границу справа.")

	def go_left(self):
		"""Пытается переместить робота на одну клетку влево."""
		new_x = self.robot_pos["x"] - 1
		target_y = self.robot_pos["y"]
		self.logger.debug(f"Attempting to move left to ({new_x}, {target_y})")
		if self.is_move_allowed(new_x, target_y):
			self.robot_pos["x"] = new_x
			self.logger.info(f"Robot moved left. New position: {self.robot_pos}")
		else:
			raise RobotError("Робот упёрся в стену или границу слева.")

	def go_up(self):
		"""Пытается переместить робота на одну клетку вверх."""
		target_x = self.robot_pos["x"]
		new_y = self.robot_pos["y"] - 1
		self.logger.debug(f"Attempting to move up to ({target_x}, {new_y})")
		if self.is_move_allowed(target_x, new_y):
			self.robot_pos["y"] = new_y
			self.logger.info(f"Robot moved up. New position: {self.robot_pos}")
		else:
			raise RobotError("Робот упёрся в стену или границу сверху.")

	def go_down(self):
		"""Пытается переместить робота на одну клетку вниз."""
		target_x = self.robot_pos["x"]
		new_y = self.robot_pos["y"] + 1
		self.logger.debug(f"Attempting to move down to ({target_x}, {new_y})")
		if self.is_move_allowed(target_x, new_y):
			self.robot_pos["y"] = new_y
			self.logger.info(f"Robot moved down. New position: {self.robot_pos}")
		else:
			raise RobotError("Робот упёрся в стену или границу снизу.")

	def do_paint(self):
		"""Закрашивает текущую клетку робота."""
		pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		self.logger.debug(f"Attempting to paint cell: {pos_key}")
		if pos_key in self.colored_cells:
			self.logger.warning(f"Cell {pos_key} is already painted. Command 'закрасить' had no effect.")
		else:
			self.colored_cells.add(pos_key)
			self.logger.info(f"Cell {pos_key} painted.")

	# --- Sensor Methods ---

	def check_direction(self, direction, status):
		"""
		Проверяет наличие стены ('wall') или свободного пространства ('free')
        в указанном направлении от текущей позиции робота.

		Args:
			direction (str): Направление ("left", "right", "up", "down").
			status (str): Ожидаемый статус ("wall" или "free").

		Returns:
			bool: True, если условие выполнено, иначе False.
		Raises:
		    ValueError: If direction or status is invalid.
		"""
		self.logger.debug(f"Checking condition: {direction} {status}")
		current_x, current_y = self.robot_pos['x'], self.robot_pos['y']
		wall_key = None
		target_x, target_y = current_x, current_y  # Position of the cell being checked (for bounds check in 'free')

		if direction == "left":
			wall_key = f"{current_x},{current_y},{current_x},{current_y + 1}"
			target_x = current_x - 1
		elif direction == "right":
			wall_key = f"{current_x + 1},{current_y},{current_x + 1},{current_y + 1}"
			target_x = current_x + 1
		elif direction == "up":
			wall_key = f"{current_x},{current_y},{current_x + 1},{current_y}"
			target_y = current_y - 1
		elif direction == "down":
			wall_key = f"{current_x},{current_y + 1},{current_x + 1},{current_y + 1}"
			target_y = current_y + 1
		else:
			raise ValueError(f"Неизвестное направление для проверки: {direction}")

		# === FIX HERE: Use 'in' operator for set membership check ===
		has_perm_wall = wall_key in self.permanent_walls
		has_user_wall = wall_key in self.walls
		# ===========================================================
		is_wall_present = has_perm_wall or has_user_wall

		if status == "wall":
			result = is_wall_present
			self.logger.debug(
				f"Check [{direction} wall]: {'Exists' if result else 'Does not exist'} ({'Perm' if has_perm_wall else ''}{'User' if has_user_wall else ''}) at {wall_key}")
			return result
		elif status == "free":
			is_within_bounds = (0 <= target_x < self.width and 0 <= target_y < self.height)
			result = is_within_bounds and not is_wall_present
			self.logger.debug(
				f"Check [{direction} free]: {'Yes' if result else 'No'} (Bounds: {is_within_bounds}, Wall: {is_wall_present})")
			return result
		else:
			raise ValueError(f"Неизвестный статус для проверки: {status}")

	def check_cell(self, status):
		"""
		Проверяет, закрашена ('painted') или чистая ('clear') текущая клетка.

		Args:
			status (str): Ожидаемый статус ("painted" или "clear").
		Returns:
			bool: True, если условие выполнено, иначе False.
        Raises:
            ValueError: If status is invalid.
		"""
		pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
		self.logger.debug(f"Checking cell state: {pos_key} - expected {status}")
		is_painted = pos_key in self.colored_cells

		if status == "painted":
			result = is_painted
			self.logger.debug(f"Check [cell painted]: {'Yes' if result else 'No'}")
			return result
		elif status == "clear":
			result = not is_painted
			self.logger.debug(f"Check [cell clear]: {'Yes' if result else 'No'}")
			return result
		else:
			raise ValueError(f"Неизвестный статус клетки для проверки: {status}")

	def do_measurement(self, measure):
		"""
		Выполняет фиктивное измерение (для примера).
		Args:
			measure (str): Тип измерения ('temperature', 'radiation').
		Returns:
			float: Результат измерения.
        Raises:
            ValueError: If measure type is unknown.
		"""
		self.logger.debug(f"Performing measurement: {measure}")
		if measure == "temperature":
			return 25.0
		elif measure == "radiation":
			return 10.5
		else:
			self.logger.warning(f"Неизвестный тип измерения: {measure}. Возвращено 0.0")
			return 0.0
