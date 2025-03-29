import logging
import re

logger = logging.getLogger('SimulatedRobot')
logger.propagate = False
if not logger.handlers:
    h = logging.StreamHandler();
    h.setFormatter(logging.Formatter('%(asctime)s-SR-%(levelname)s-%(message)s'));
    logger.addHandler(h)
logger.setLevel(logging.INFO)


class RobotError(Exception): pass


class SimulatedRobot:
    """ Состояние и действия симулированного робота на поле. """

    def __init__(self, width, height, initial_pos=None, initial_walls=None,
                 initial_markers=None, initial_colored_cells=None, initial_symbols=None,
                 initial_radiation=None, initial_temperature=None):  # <-- Add new initial states
        if not isinstance(width, int) or width < 1: raise ValueError("Width>0")
        if not isinstance(height, int) or height < 1: raise ValueError("Height>0")
        self.width = width;
        self.height = height;
        self.logger = logger
        self.robot_pos = self._clamp_pos(initial_pos or {'x': 0, 'y': 0})
        self.walls = initial_walls if initial_walls is not None else set()
        self.markers = initial_markers if initial_markers is not None else {}
        self.colored_cells = initial_colored_cells if initial_colored_cells is not None else set()
        self.symbols = initial_symbols if initial_symbols is not None else {}
        # --- NEW: Initialize radiation and temperature state ---
        self.radiation = initial_radiation if initial_radiation is not None else {}  # { "x,y": float_value }
        self.temperature = initial_temperature if initial_temperature is not None else {}  # { "x,y": int_value }
        # -------------------------------------------------------
        self.permanent_walls = self._setup_permanent_walls()
        self.logger.info(f"Robot init: {width}x{height} @ {self.robot_pos}")

    def _clamp_pos(self, pos):
        /

        *... * / x = min(max(0, pos.get('x', 0)), self.width - 1);
    y = min(max(0, pos.get('y', 0)), self.height - 1);
    return {'x': x, 'y': y}

    def _setup_permanent_walls(self):
        /

        *... * / w = set();
    for x in range(self.width): w.add(f"{x},0,{x + 1},0");w.add(f"{x},{self.height},{x + 1},{self.height}"); for
    y in range(self.height): w.add(f"0,{y},0,{y + 1}");
    w.add(f"{self.width},{y},{self.width},{y + 1}");
    return w

    def reset(self, new_width=None, new_height=None):
        """ Resets robot state, optionally resizes. """
        if new_width is not None and isinstance(new_width, int) and new_width >= 1: self.width = new_width
        if new_height is not None and isinstance(new_height, int) and new_height >= 1: self.height = new_height
        self.robot_pos = {'x': 0, 'y': 0};
        self.walls.clear();
        self.markers.clear();
        self.colored_cells.clear();
        self.symbols.clear()
        self.radiation.clear();
        self.temperature.clear()  # <-- Clear new states on reset
        self.permanent_walls = self._setup_permanent_walls();
        self.logger.info(f"Reset: {self.width}x{self.height}, Pos {self.robot_pos}.")

    def is_move_allowed(self, tx, ty):
        /

        *...
    unchanged... * /
    if not (0 <= tx < self.width and 0 <= ty < self.height): return False; cx, cy = self.robot_pos["x"], self.robot_pos[
        "y"]; wk = None; if
    tx > cx: wk = f"{tx},{cy},{tx},{cy + 1}"; elif tx < cx: wk = f"{cx},{cy},{cx},{cy + 1}"; elif ty > cy: wk = f"{cx},{ty},{cx + 1},{ty}"; elif ty < cy: wk = f"{cx},{cy},{cx + 1},{cy}"; else:return True;
    if wk and (wk in self.permanent_walls or wk in self.walls): return False; return True

    # Movement methods - unchanged
    def go_right(self):
        nx, ty = self.robot_pos["x"] + 1, self.robot_pos["y"]; if

    self.is_move_allowed(nx, ty): self.robot_pos["x"] = nx;
    self.logger.info(f"Moved R->{self.robot_pos}") else: raise RobotError("Стена/граница R")

    def go_left(self):
        nx, ty = self.robot_pos["x"] - 1, self.robot_pos["y"]; if

    self.is_move_allowed(nx, ty): self.robot_pos["x"] = nx;
    self.logger.info(f"Moved L->{self.robot_pos}") else: raise RobotError("Стена/граница L")

    def go_up(self):
        tx, ny = self.robot_pos["x"], self.robot_pos["y"] - 1; if

    self.is_move_allowed(tx, ny): self.robot_pos["y"] = ny;
    self.logger.info(f"Moved U->{self.robot_pos}") else: raise RobotError("Стена/граница U")

    def go_down(self):
        tx, ny = self.robot_pos["x"], self.robot_pos["y"] + 1; if

    self.is_move_allowed(tx, ny): self.robot_pos["y"] = ny;
    self.logger.info(f"Moved D->{self.robot_pos}") else: raise RobotError("Стена/граница D")

    def do_paint(self):
        k = f"{self.robot_pos['x']},{self.robot_pos['y']}"; if

    k in self.colored_cells: self.logger.warning(f"Cell {k} уже.") else: self.colored_cells.add(k);
    self.logger.info(f"Cell {k} закр.")

    # Sensor methods - unchanged check_direction, check_cell
    def check_direction(self, d, s):
        /

        *... * / cx, cy = self.robot_pos['x'], self.robot_pos['y'];
    wk, tx, ty = None, cx, cy;
    if d == "left": wk = f"{cx},{cy},{cx},{cy + 1}";tx -= 1; elif
    d == "right": wk = f"{cx + 1},{cy},{cx + 1},{cy + 1}";
    tx += 1; elif d == "up": wk = f"{cx},{cy},{cx + 1},{cy}";
    ty -= 1; elif d == "down": wk = f"{cx},{cy + 1},{cx + 1},{cy + 1}";
    ty += 1; else:raise ValueError(f"Dir?{d}");
    iw = wk in self.permanent_walls or wk in self.walls;
    if s == "wall": return iw; elif
    s == "free":
    return (0 <= tx < self.width and 0 <= ty < self.height) and not iw; else:raise ValueError(f"Status?{s}")

    def check_cell(self, s):
        k = f"{self.robot_pos['x']},{self.robot_pos['y']}"; i = k in self.colored_cells; if

    s == "painted":
    return i; elif s == "clear":
    return not i; else:raise ValueError(f"Cell Status?{s}")

    # Measurement method - updated
    def do_measurement(self, measure):
        """ Возвращает значение радиации или температуры в текущей клетке. """
        pos_key = f"{self.robot_pos['x']},{self.robot_pos['y']}"
        self.logger.debug(f"Measure '{measure}' at {pos_key}")
        if measure == "radiation":
            value = self.radiation.get(pos_key, 0.0)  # Default to 0.0 if not set
            self.logger.info(f"Radiation at {pos_key}: {value}")
            return float(value)  # Ensure float
        elif measure == "temperature":
            value = self.temperature.get(pos_key, 0)  # Default to 0 if not set
            self.logger.info(f"Temperature at {pos_key}: {value}")
            return int(value)  # Ensure int
        else:
            self.logger.warning(f"Unknown measurement: {measure}. Return 0")
            return 0  # Return 0 for unknown measurements