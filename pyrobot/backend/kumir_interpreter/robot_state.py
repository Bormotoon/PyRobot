import logging
import re  # Keep re for potential future use in checks

# Configure logger for this module
logger = logging.getLogger('SimulatedRobot')
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - SimulatedRobot - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RobotError(Exception):
    """Custom exception for robot-specific errors."""
    pass


class SimulatedRobot:
    """ Состояние и действия симулированного робота на поле. """

    def __init__(self, width, height, initial_pos=None, initial_walls=None,
                 initial_markers=None, initial_colored_cells=None, initial_symbols=None):  # <-- Add initial_symbols
        if not isinstance(width, int) or width < 1: raise ValueError("Width must be positive.")
        if not isinstance(height, int) or height < 1: raise ValueError("Height must be positive.")

        self.width = width
        self.height = height
        self.logger = logger

        default_pos = {'x': 0, 'y': 0}
        pos = initial_pos if initial_pos else default_pos
        self.robot_pos = self._clamp_pos(pos)

        self.walls = initial_walls if initial_walls is not None else set()
        self.markers = initial_markers if initial_markers is not None else {}
        self.colored_cells = initial_colored_cells if initial_colored_cells is not None else set()
        self.symbols = initial_symbols if initial_symbols is not None else {}  # <-- Initialize symbols

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
        for x in range(self.width): new_walls.add(f"{x},0,{x + 1},0"); new_walls.add(
            f"{x},{self.height},{x + 1},{self.height}")
        for y in range(self.height): new_walls.add(f"0,{y},0,{y + 1}"); new_walls.add(
            f"{self.width},{y},{self.width},{y + 1}")
        return new_walls

    def reset(self, new_width=None, new_height=None):
        """ Resets robot state and optionally resizes field. """
        if new_width is not None and isinstance(new_width, int) and new_width >= 1: self.width = new_width
        if new_height is not None and isinstance(new_height, int) and new_height >= 1: self.height = new_height
        self.robot_pos = {'x': 0, 'y': 0}
        self.walls.clear();
        self.markers.clear();
        self.colored_cells.clear();
        self.symbols.clear()  # <-- Clear symbols on reset
        self.permanent_walls = self._setup_permanent_walls()
        self.logger.info(f"Robot state reset. Field {self.width}x{self.height}. Pos {self.robot_pos}.")

    def is_move_allowed(self, target_x, target_y):
        """ Checks if move is allowed considering bounds and walls. """
        if not (0 <= target_x < self.width and 0 <= target_y < self.height): return False
        current_x, current_y = self.robot_pos["x"], self.robot_pos["y"]
        wall_key = None
        if target_x > current_x:
            wall_key = f"{target_x},{current_y},{target_x},{current_y + 1}"
        elif target_x < current_x:
            wall_key = f"{current_x},{current_y},{current_x},{current_y + 1}"
        elif target_y > current_y:
            wall_key = f"{current_x},{target_y},{current_x + 1},{target_y}"
        elif target_y < current_y:
            wall_key = f"{current_x},{current_y},{current_x + 1},{current_y}"
        else:
            return True  # No move
        if wall_key and (wall_key in self.permanent_walls or wall_key in self.walls): return False
        return True

    # Movement methods (go_right, go_left, go_up, go_down) - unchanged
    def go_right(self):
        new_x, target_y = self.robot_pos["x"] + 1, self.robot_pos["y"]
        if self.is_move_allowed(new_x, target_y):
            self.robot_pos["x"] = new_x; self.logger.info(f"Moved right -> {self.robot_pos}")
        else:
            raise RobotError("Стена/граница справа.")

    def go_left(self):
        new_x, target_y = self.robot_pos["x"] - 1, self.robot_pos["y"]
        if self.is_move_allowed(new_x, target_y):
            self.robot_pos["x"] = new_x; self.logger.info(f"Moved left -> {self.robot_pos}")
        else:
            raise RobotError("Стена/граница слева.")

    def go_up(self):
        target_x, new_y = self.robot_pos["x"], self.robot_pos["y"] - 1
        if self.is_move_allowed(target_x, new_y):
            self.robot_pos["y"] = new_y; self.logger.info(f"Moved up -> {self.robot_pos}")
        else:
            raise RobotError("Стена/граница сверху.")

    def go_down(self):
        target_x, new_y = self.robot_pos["x"], self.robot_pos["y"] + 1
        if self.is_move_allowed(target_x, new_y):
            self.robot_pos["y"] = new_y; self.logger.info(f"Moved down -> {self.robot_pos}")
        else:
            raise RobotError("Стена/граница снизу.")

    def do_paint(self):
        """ Paints the current cell. """
        pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
        if pos_key in self.colored_cells:
            self.logger.warning(f"Cell {pos_key} уже закрашена.")
        else:
            self.colored_cells.add(pos_key); self.logger.info(f"Cell {pos_key} закрашена.")

    # Sensor methods (check_direction, check_cell, do_measurement) - unchanged
    def check_direction(self, direction, status):
        current_x, current_y = self.robot_pos['x'], self.robot_pos['y']
        wall_key, target_x, target_y = None, current_x, current_y
        if direction == "left":
            wall_key = f"{current_x},{current_y},{current_x},{current_y + 1}"; target_x -= 1
        elif direction == "right":
            wall_key = f"{current_x + 1},{current_y},{current_x + 1},{current_y + 1}"; target_x += 1
        elif direction == "up":
            wall_key = f"{current_x},{current_y},{current_x + 1},{current_y}"; target_y -= 1
        elif direction == "down":
            wall_key = f"{current_x},{current_y + 1},{current_x + 1},{current_y + 1}"; target_y += 1
        else:
            raise ValueError(f"Неизвестное направление: {direction}")
        is_wall = wall_key in self.permanent_walls or wall_key in self.walls
        if status == "wall":
            return is_wall
        elif status == "free":
            return (0 <= target_x < self.width and 0 <= target_y < self.height) and not is_wall
        else:
            raise ValueError(f"Неизвестный статус: {status}")

    def check_cell(self, status):
        pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
        is_painted = pos_key in self.colored_cells
        if status == "painted":
            return is_painted
        elif status == "clear":
            return not is_painted
        else:
            raise ValueError(f"Неизвестный статус клетки: {status}")

    def do_measurement(self, measure):
        if measure == "temperature":
            return 25.0
        elif measure == "radiation":
            return 10.5
        else:
            self.logger.warning(f"Неизвестное измерение: {measure}. Возврат 0.0"); return 0.0