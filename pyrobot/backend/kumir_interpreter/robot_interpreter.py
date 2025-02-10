import logging
import re


class KumirInterpreterError(Exception):
    """Custom exception for interpreter errors."""
    pass


class KumirInterpreter:
    def __init__(self):
        self.robot_pos = {"x": 0, "y": 0}
        self.walls = set()
        self.markers = {}
        self.colored_cells = set()

        # Logging configuration
        self.logger = logging.getLogger('KumirInterpreter')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - KumirInterpreter - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def reset(self):
        """Resets the state of the simulator."""
        self.logger.info("Interpreter state has been reset.")
        self.robot_pos = {"x": 0, "y": 0}
        self.walls.clear()
        self.markers.clear()
        self.colored_cells.clear()

    def interpret(self, code):
        """
        Interprets and executes the given Kumir code.

        :param code: String containing Kumir code.
        :return: Execution result or error message.
        """
        self.logger.info("Starting code interpretation.")
        self.logger.debug(f"Input code:\n{code}")
        try:
            tokens = self.tokenize(code)
            self.logger.debug(f"Tokens: {tokens}")
            ast = self.parse(tokens)
            self.logger.debug(f"AST: {ast}")
            result = self.execute(ast)
            self.logger.info("Interpretation completed successfully.")
            self.logger.debug(f"Execution result: {result}")
            return {"success": True, "result": result}
        except KumirInterpreterError as e:
            self.logger.error(f"Interpreter error: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            self.logger.exception("Unknown error during code interpretation.")
            return {"success": False, "message": f"Unknown error: {str(e)}"}

    def tokenize(self, code):
        """
        Splits the code into tokens (lines), skipping comments (#) and empty lines.
        """
        tokens = []
        lines = code.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            tokens.append(line)
        self.logger.debug(f"Tokenized code: {tokens}")
        return tokens

    def parse(self, tokens):
        """
        Converts the list of tokens into an AST (abstract syntax tree).
        """
        ast = []
        current_algorithm = None
        for token in tokens:
            token_lower = token.lower()
            self.logger.debug(f"Parsing token: {token_lower}")

            if token_lower == "использовать робот":
                # This command resets the state (use_robot)
                ast.append({"type": "use_robot"})
                self.logger.debug("Added 'use_robot' command to AST.")
            elif token_lower == "алг":
                # Start of an algorithm
                current_algorithm = {"type": "algorithm", "commands": []}
                ast.append(current_algorithm)
                self.logger.debug("Started algorithm block ('алг').")
            elif token_lower == "нач":
                if not current_algorithm:
                    raise KumirInterpreterError("Syntax error: 'нач' without 'алг'")
                current_algorithm["in_block"] = True
                self.logger.debug("Beginning of algorithm body ('нач').")
            elif token_lower == "кон":
                if not current_algorithm or not current_algorithm.get("in_block"):
                    raise KumirInterpreterError("Syntax error: 'кон' without 'нач'")
                current_algorithm["in_block"] = False
                self.logger.debug("End of algorithm body ('кон').")
            else:
                if not current_algorithm or not current_algorithm.get("in_block"):
                    raise KumirInterpreterError(f"Syntax error: Command '{token}' outside of algorithm block")
                command = self.parse_command(token)
                current_algorithm["commands"].append(command)
                self.logger.debug(f"Added command to algorithm: {command}")

        self.logger.debug(f"Constructed AST: {ast}")
        return ast

    def parse_command(self, command_str):
        """
        Parses a single command string into a command dictionary.
        """
        command_str_lower = command_str.lower().strip()
        self.logger.debug(f"Parsing command: {command_str_lower}")

        # --- Action commands ---
        if command_str_lower == "влево":
            return {"type": "action", "command": "left"}
        elif command_str_lower == "вправо":
            return {"type": "action", "command": "right"}
        elif command_str_lower == "вверх":
            return {"type": "action", "command": "up"}
        elif command_str_lower == "вниз":
            return {"type": "action", "command": "down"}
        elif command_str_lower == "закрасить":
            return {"type": "action", "command": "paint"}

        # --- Condition commands for directions ---
        if re.match(r'^(слева|справа|сверху|снизу)\s+(стена|свободно)$', command_str_lower):
            # Example: "слева свободно", "справа стена", etc.
            direction, status = command_str_lower.split()
            # Map Russian words to English internal names:
            direction_map = {"слева": "left", "справа": "right", "сверху": "up", "снизу": "down"}
            status_map = {"стена": "wall", "свободно": "free"}
            return {"type": "condition", "direction": direction_map.get(direction, direction),
                    "status": status_map.get(status, status)}

        # --- Condition commands for cell state ---
        if re.match(r'^клетка\s+(закрашена|чистая)$', command_str_lower):
            # Example: "клетка закрашена", "клетка чистая"
            parts = command_str_lower.split()
            cell_status_map = {"закрашена": "painted", "чистая": "clear"}
            return {"type": "condition_cell", "status": cell_status_map.get(parts[1], parts[1])}

        # --- Measurement commands ---
        if command_str_lower in ["температура", "радиация"]:
            measurement_map = {"температура": "temperature", "радиация": "radiation"}
            return {"type": "measurement", "command": measurement_map.get(command_str_lower, command_str_lower)}

        raise KumirInterpreterError(f"Unknown command: {command_str}")

    def execute(self, ast):
        """
        Executes the AST and returns the final state.
        """
        self.logger.info("Starting AST execution.")
        for node in ast:
            self.logger.debug(f"Executing AST node: {node}")
            if node["type"] == "use_robot":
                self.reset()
            elif node["type"] == "algorithm":
                for command in node["commands"]:
                    self.execute_command(command)
        self.logger.info("AST execution completed.")
        return {
            "robotPos": self.robot_pos,
            "walls": list(self.walls),
            "markers": self.markers,
            "coloredCells": list(self.colored_cells)
        }

    def execute_command(self, command):
        """
        Executes a single command (action, condition or measurement).
        """
        self.logger.debug(f"Executing command: {command}")
        cmd_type = command["type"]

        if cmd_type == "action":
            action = command["command"]
            if action == "left":
                self.go_left()
            elif action == "right":
                self.go_right()
            elif action == "up":
                self.go_up()
            elif action == "down":
                self.go_down()
            elif action == "paint":
                self.do_paint()
            else:
                raise KumirInterpreterError(f"Unknown action command: {action}")

        elif cmd_type == "condition":
            direction = command["direction"]
            status = command["status"]
            condition_result = self.check_direction(direction, status)
            self.logger.info(f"Condition [{direction} {status}]: {condition_result}")

        elif cmd_type == "condition_cell":
            status = command["status"]
            condition_result = self.check_cell(status)
            self.logger.info(f"Condition [cell {status}]: {condition_result}")

        elif cmd_type == "measurement":
            measure = command["command"]
            value = self.do_measurement(measure)
            self.logger.info(f"Measurement '{measure}': result = {value}")

        else:
            raise KumirInterpreterError(f"Unknown command type: {cmd_type}")

    # --- Robot action methods ---
    def go_left(self):
        """Moves the robot one cell to the left (if no wall/border)."""
        new_x = self.robot_pos["x"] - 1
        self.logger.debug(f"Attempting to move left to X={new_x}, Y={self.robot_pos['y']}")
        if self.is_move_allowed(new_x, self.robot_pos["y"]):
            self.robot_pos["x"] = new_x
            self.logger.info(f"Robot moved left. New position: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Robot cannot move left (wall or border).")

    def go_right(self):
        """Moves the robot one cell to the right."""
        new_x = self.robot_pos["x"] + 1
        self.logger.debug(f"Attempting to move right to X={new_x}, Y={self.robot_pos['y']}")
        if self.is_move_allowed(new_x, self.robot_pos["y"]):
            self.robot_pos["x"] = new_x
            self.logger.info(f"Robot moved right. New position: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Robot cannot move right (wall or border).")

    def go_up(self):
        """Moves the robot one cell upward."""
        new_y = self.robot_pos["y"] - 1
        self.logger.debug(f"Attempting to move up to X={self.robot_pos['x']}, Y={new_y}")
        if self.is_move_allowed(self.robot_pos["x"], new_y):
            self.robot_pos["y"] = new_y
            self.logger.info(f"Robot moved up. New position: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Robot cannot move up (wall or border).")

    def go_down(self):
        """Moves the robot one cell downward."""
        new_y = self.robot_pos["y"] + 1
        self.logger.debug(f"Attempting to move down to X={self.robot_pos['x']}, Y={new_y}")
        if self.is_move_allowed(self.robot_pos["x"], new_y):
            self.robot_pos["y"] = new_y
            self.logger.info(f"Robot moved down. New position: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Robot cannot move down (wall or border).")

    def do_paint(self):
        """Paints the current cell if it is not already painted."""
        pos_str = f"{self.robot_pos['x']},{self.robot_pos['y']}"
        self.logger.debug(f"Attempting to paint cell: {pos_str}")
        if pos_str not in self.colored_cells:
            self.colored_cells.add(pos_str)
            self.logger.info(f"Cell {pos_str} painted.")
        else:
            raise KumirInterpreterError("Cell is already painted.")

    # --- Condition checking methods ---
    def check_direction(self, direction, status):
        """
        Checks if there is a wall or the cell is free in the specified direction (left/right/up/down).
        Returns True/False.
        """
        self.logger.debug(f"Checking condition: {direction} {status}")
        dx, dy = 0, 0
        if direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1
        elif direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        else:
            raise KumirInterpreterError(f"Unknown direction: {direction}")

        target_x = self.robot_pos["x"] + dx
        target_y = self.robot_pos["y"] + dy

        # Construct a string "x1,y1,x2,y2" to check for a wall
        wall = f"{min(self.robot_pos['x'], target_x)},{min(self.robot_pos['y'], target_y)},{max(self.robot_pos['x'], target_x)},{max(self.robot_pos['y'], target_y)}"

        if status == "wall":
            result = (wall in self.walls)
            self.logger.debug(f"Wall {'exists' if result else 'does not exist'} along path {wall}.")
            return result

        elif status == "free":
            # True if no wall and cell is within bounds (default: 0..10)
            in_bounds = (0 <= target_x <= 10 and 0 <= target_y <= 10)
            no_wall = (wall not in self.walls)
            result = (in_bounds and no_wall)
            self.logger.debug(f"Free: {'yes' if result else 'no'}.")
            return result

        else:
            raise KumirInterpreterError(f"Unknown status: {status}")

    def check_cell(self, status):
        """
        Checks if the cell where the robot stands is painted or not.
        Returns True/False.
        """
        pos_str = f"{self.robot_pos['x']},{self.robot_pos['y']}"
        self.logger.debug(f"Checking cell state: {pos_str} - {status}")

        if status == "painted":
            result = (pos_str in self.colored_cells)
            self.logger.debug(f"Cell painted: {'yes' if result else 'no'}.")
            return result
        elif status == "clear":
            result = (pos_str not in self.colored_cells)
            self.logger.debug(f"Cell clear: {'yes' if result else 'no'}.")
            return result
        else:
            raise KumirInterpreterError(f"Unknown cell status: {status}")

    # --- Measurement methods ---
    def do_measurement(self, measure):
        """
        Executes a measurement command ("temperature" or "radiation").
        Returns a float.
        """
        self.logger.debug(f"Performing measurement: {measure}")
        if measure == "temperature":
            return 25.0  # Some fixed value
        elif measure == "radiation":
            return 10.5  # Some fixed value
        else:
            raise KumirInterpreterError(f"Unknown measurement: {measure}")

    # --- Helper methods ---
    def is_move_allowed(self, x, y):
        """
        Checks if the robot can move to the cell (x, y).
        Returns True if the coordinates are within bounds (0..10) and there is no wall.
        """
        self.logger.debug(f"Checking if move is allowed to X={x}, Y={y}")
        if x < 0 or y < 0 or x > 10 or y > 10:
            self.logger.debug("Move disallowed: out of field bounds.")
            return False

        current_x = self.robot_pos["x"]
        current_y = self.robot_pos["y"]
        wall = f"{min(current_x, x)},{min(current_y, y)},{max(current_x, x)},{max(current_y, y)}"
        if wall in self.walls:
            self.logger.debug(f"Move disallowed: wall detected along path {wall}.")
            return False

        self.logger.debug("Move allowed.")
        return True
