import logging
import re


class KumirInterpreterError(Exception):
    """Кастомное исключение для ошибок интерпретатора."""
    pass


class KumirInterpreter:
    def __init__(self):
        self.robot_pos = {"x": 0, "y": 0}
        self.walls = set()
        self.markers = {}
        self.colored_cells = set()

        # Настройка логирования
        self.logger = logging.getLogger('KumirInterpreter')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - KumirInterpreter - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def reset(self):
        """Сбрасывает состояние симулятора."""
        self.logger.info("Состояние интерпретатора сброшено.")
        self.robot_pos = {"x": 0, "y": 0}
        self.walls.clear()
        self.markers.clear()
        self.colored_cells.clear()

    def interpret(self, code):
        """
        Интерпретирует и выполняет код на языке КУМИР.

        :param code: Строка с кодом на языке КУМИР
        :return: Результат выполнения или сообщение об ошибке
        """
        self.logger.info("Начало интерпретации кода.")
        self.logger.debug(f"Входной код:\n{code}")
        try:
            tokens = self.tokenize(code)
            self.logger.debug(f"Токены: {tokens}")
            ast = self.parse(tokens)
            self.logger.debug(f"AST: {ast}")
            result = self.execute(ast)
            self.logger.info("Интерпретация завершена успешно.")
            self.logger.debug(f"Результат выполнения: {result}")
            return {"success": True, "result": result}
        except KumirInterpreterError as e:
            self.logger.error(f"Ошибка интерпретатора: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            self.logger.exception("Неизвестная ошибка при интерпретации кода.")
            return {"success": False, "message": f"Неизвестная ошибка: {str(e)}"}

    def tokenize(self, code):
        """
        Разбивает код на токены (по строкам), пропуская комментарии (#) и пустые строки.
        """
        tokens = []
        lines = code.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Пропускаем пустые и комментарии
            if not line or line.startswith('#'):
                continue
            tokens.append(line)
        self.logger.debug(f"Токенизированный код: {tokens}")
        return tokens

    def parse(self, tokens):
        """
        Преобразует список токенов в AST (абстрактное синтаксическое дерево).
        """
        ast = []
        current_algorithm = None
        for token in tokens:
            token_lower = token.lower()
            self.logger.debug(f"Парсинг токена: {token_lower}")

            if token_lower == "использовать робот":
                # Это команда, которая сбрасывает состояние (use_robot)
                ast.append({"type": "use_robot"})
                self.logger.debug("Добавлена команда 'use_robot' в AST.")
            elif token_lower == "алг":
                # Начало алгоритма
                current_algorithm = {"type": "algorithm", "commands": []}
                ast.append(current_algorithm)
                self.logger.debug("Начат блок алгоритма 'алг'.")
            elif token_lower == "нач":
                # Начало тела алгоритма
                if not current_algorithm:
                    raise KumirInterpreterError("Синтаксическая ошибка: 'нач' без 'алг'")
                current_algorithm["in_block"] = True
                self.logger.debug("Начало блока 'нач'.")
            elif token_lower == "кон":
                # Конец тела алгоритма
                if not current_algorithm or not current_algorithm.get("in_block"):
                    raise KumirInterpreterError("Синтаксическая ошибка: 'кон' без 'нач'")
                current_algorithm["in_block"] = False
                self.logger.debug("Конец блока 'кон'.")
            else:
                # Остальные команды должны быть внутри блока 'нач ... кон'
                if not current_algorithm or not current_algorithm.get("in_block"):
                    raise KumirInterpreterError(f"Синтаксическая ошибка: Команда '{token}' вне блока алгоритма")
                command = self.parse_command(token)
                current_algorithm["commands"].append(command)
                self.logger.debug(f"Добавлена команда в алгоритм: {command}")

        self.logger.debug(f"Сформированный AST: {ast}")
        return ast

    def parse_command(self, command_str):
        """
        Разбирает строку на конкретную команду (действие, проверка, измерение).
        """
        command_str_lower = command_str.lower().strip()
        self.logger.debug(f"Парсинг команды: {command_str_lower}")

        # --- Команды-действия ---
        if command_str_lower == "влево":
            return {"type": "action", "command": "влево"}
        elif command_str_lower == "вправо":
            return {"type": "action", "command": "вправо"}
        elif command_str_lower == "вверх":
            return {"type": "action", "command": "вверх"}
        elif command_str_lower == "вниз":
            return {"type": "action", "command": "вниз"}
        elif command_str_lower == "закрасить":
            return {"type": "action", "command": "закрасить"}

        # --- Команды проверки условий (слева/справа/сверху/снизу) (стена/свободно) ---
        if re.match(r'^(слева|справа|сверху|снизу)\s+(стена|свободно)$', command_str_lower):
            # Пример: "слева свободно", "справа стена" и т.д.
            direction, status = command_str_lower.split()
            return {"type": "condition", "direction": direction, "status": status}

        # --- Команды проверки клетки (клетка закрашена/чистая) ---
        if re.match(r'^клетка\s+(закрашена|чистая)$', command_str_lower):
            # Пример: "клетка закрашена", "клетка чистая"
            parts = command_str_lower.split()
            return {"type": "condition_cell", "status": parts[1]}

        # --- Команды измерения (температура, радиация) ---
        if command_str_lower in ["температура", "радиация"]:
            # Считаем это командами-функциями, возвращающими число (float)
            return {"type": "measurement", "command": command_str_lower}

        # Если не подходит ни под один шаблон — «Неизвестная команда»
        raise KumirInterpreterError(f"Неизвестная команда: {command_str}")

    def execute(self, ast):
        """
        Выполняет AST и формирует результирующее состояние.
        """
        self.logger.info("Начало выполнения AST.")
        for node in ast:
            self.logger.debug(f"Выполнение узла AST: {node}")
            if node["type"] == "use_robot":
                # Сброс обстановки/состояния
                self.reset()
            elif node["type"] == "algorithm":
                # Внутри алгоритма — набор команд
                for command in node["commands"]:
                    self.execute_command(command)
        self.logger.info("Выполнение AST завершено.")
        return {"robotPos": self.robot_pos, "walls": list(self.walls), "markers": self.markers,
            "coloredCells": list(self.colored_cells)}

    def execute_command(self, command):
        """
        Выполняет отдельную команду (действие, проверка или измерение).
        """
        self.logger.debug(f"Выполнение команды: {command}")
        cmd_type = command["type"]

        if cmd_type == "action":
            # Команда-действие: влево/вправо/вверх/вниз/закрасить
            action = command["command"]
            if action == "влево":
                self.go_left()
            elif action == "вправо":
                self.go_right()
            elif action == "вверх":
                self.go_up()
            elif action == "вниз":
                self.go_down()
            elif action == "закрасить":
                self.do_paint()
            else:
                raise KumirInterpreterError(f"Неизвестная команда действия: {action}")

        elif cmd_type == "condition":
            # Команда-проверка вида «слева стена», «справа свободно» и т.п.
            direction = command["direction"]
            status = command["status"]
            condition_result = self.check_direction(direction, status)
            self.logger.info(f"Условие [{direction} {status}]: {condition_result}")

        elif cmd_type == "condition_cell":
            # Команда-проверка вида «клетка закрашена», «клетка чистая»
            status = command["status"]
            condition_result = self.check_cell(status)
            self.logger.info(f"Условие [клетка {status}]: {condition_result}")

        elif cmd_type == "measurement":
            # Команда-измерение: «температура» или «радиация»
            measure = command["command"]
            value = self.do_measurement(measure)
            # В КуМире обычно результат куда-то присваивают или проверяют
            # Здесь мы просто залогируем
            self.logger.info(f"Измерение '{measure}': результат = {value}")

        else:
            raise KumirInterpreterError(f"Неизвестный тип команды: {cmd_type}")

    # ---------------------------------------------------------------------
    # Методы ДЕЙСТВИЙ робота
    # ---------------------------------------------------------------------
    def go_left(self):
        """Перемещает робота на одну клетку влево (если там нет стены/края)."""
        new_x = self.robot_pos["x"] - 1
        self.logger.debug(f"Попытка перемещения влево к X={new_x}, Y={self.robot_pos['y']}")
        if self.is_move_allowed(new_x, self.robot_pos["y"]):
            self.robot_pos["x"] = new_x
            self.logger.info(f"Робот переместился влево. Новая позиция: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Робот не может пойти влево (стена или край).")

    def go_right(self):
        """Перемещает робота на одну клетку вправо."""
        new_x = self.robot_pos["x"] + 1
        self.logger.debug(f"Попытка перемещения вправо к X={new_x}, Y={self.robot_pos['y']}")
        if self.is_move_allowed(new_x, self.robot_pos["y"]):
            self.robot_pos["x"] = new_x
            self.logger.info(f"Робот переместился вправо. Новая позиция: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Робот не может пойти вправо (стена или край).")

    def go_up(self):
        """Перемещает робота на одну клетку вверх."""
        new_y = self.robot_pos["y"] - 1
        self.logger.debug(f"Попытка перемещения вверх к X={self.robot_pos['x']}, Y={new_y}")
        if self.is_move_allowed(self.robot_pos["x"], new_y):
            self.robot_pos["y"] = new_y
            self.logger.info(f"Робот переместился вверх. Новая позиция: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Робот не может пойти вверх (стена или край).")

    def go_down(self):
        """Перемещает робота на одну клетку вниз."""
        new_y = self.robot_pos["y"] + 1
        self.logger.debug(f"Попытка перемещения вниз к X={self.robot_pos['x']}, Y={new_y}")
        if self.is_move_allowed(self.robot_pos["x"], new_y):
            self.robot_pos["y"] = new_y
            self.logger.info(f"Робот переместился вниз. Новая позиция: {self.robot_pos}")
        else:
            raise KumirInterpreterError("Робот не может пойти вниз (стена или край).")

    def do_paint(self):
        """Закрашивает текущую клетку, если она ещё не закрашена."""
        pos_str = f"{self.robot_pos['x']},{self.robot_pos['y']}"
        self.logger.debug(f"Попытка закрасить клетку: {pos_str}")
        if pos_str not in self.colored_cells:
            self.colored_cells.add(pos_str)
            self.logger.info(f"Клетка {pos_str} закрашена.")
        else:
            raise KumirInterpreterError("Клетка уже закрашена.")

    # ---------------------------------------------------------------------
    # Методы ПРОВЕРОК
    # ---------------------------------------------------------------------
    def check_direction(self, direction, status):
        """
        Проверяет, есть ли «стена» или «свободно» в указанном направлении (слева/справа/сверху/снизу).
        Возвращает True/False.
        """
        self.logger.debug(f"Проверка условия: {direction} {status}")
        dx, dy = 0, 0
        if direction == "слева":
            dx = -1
        elif direction == "справа":
            dx = 1
        elif direction == "сверху":
            dy = -1
        elif direction == "снизу":
            dy = 1
        else:
            raise KumirInterpreterError(f"Неизвестное направление: {direction}")

        target_x = self.robot_pos["x"] + dx
        target_y = self.robot_pos["y"] + dy

        # Формируем строку вида "x1,y1,x2,y2" для проверки стены
        wall = f"{min(self.robot_pos['x'], target_x)},{min(self.robot_pos['y'], target_y)}," \
               f"{max(self.robot_pos['x'], target_x)},{max(self.robot_pos['y'], target_y)}"

        if status == "стена":
            # True, если между текущей и соседней клеткой есть стена
            result = (wall in self.walls)
            self.logger.debug(f"Стена {'есть' if result else 'нет'} по пути {wall}.")
            return result

        elif status == "свободно":
            # True, если нет стены и клетка в пределах поля (по умолчанию 0..10)
            in_bounds = (0 <= target_x <= 10 and 0 <= target_y <= 10)
            no_wall = (wall not in self.walls)
            result = (in_bounds and no_wall)
            self.logger.debug(f"Свободно: {'да' if result else 'нет'}.")
            return result

        else:
            raise KumirInterpreterError(f"Неизвестный статус: {status}")

    def check_cell(self, status):
        """
        Проверяет, закрашена ли клетка, где стоит Робот, или нет.
        Возвращает True/False.
        """
        pos_str = f"{self.robot_pos['x']},{self.robot_pos['y']}"
        self.logger.debug(f"Проверка состояния клетки: {pos_str} - {status}")

        if status == "закрашена":
            result = (pos_str in self.colored_cells)
            self.logger.debug(f"Клетка закрашена: {'да' if result else 'нет'}.")
            return result
        elif status == "чистая":
            result = (pos_str not in self.colored_cells)
            self.logger.debug(f"Клетка чистая: {'да' if result else 'нет'}.")
            return result
        else:
            raise KumirInterpreterError(f"Неизвестный статус клетки: {status}")

    # ---------------------------------------------------------------------
    # Методы ИЗМЕРЕНИЙ
    # ---------------------------------------------------------------------
    def do_measurement(self, measure):
        """
        Выполняет команду измерения (температура, радиация).
        Возвращает число (float).
        """
        self.logger.debug(f"Выполнение измерения: {measure}")
        # Для примера — фиктивные постоянные значения
        if measure == "температура":
            return 25.0  # некое условное значение
        elif measure == "радиация":
            return 10.5  # некое условное значение
        else:
            raise KumirInterpreterError(f"Неизвестное измерение: {measure}")

    # ---------------------------------------------------------------------
    # Вспомогательные методы
    # ---------------------------------------------------------------------
    def is_move_allowed(self, x, y):
        """
        Проверяет, можно ли переместиться в клетку (x, y).
        Возвращает True, если не вышли за границы (0..10) и нет стены.
        """
        self.logger.debug(f"Проверка возможности перемещения в X={x}, Y={y}")
        if x < 0 or y < 0 or x > 10 or y > 10:
            self.logger.debug("Перемещение запрещено: выход за границы поля.")
            return False

        current_x = self.robot_pos["x"]
        current_y = self.robot_pos["y"]
        wall = f"{min(current_x, x)},{min(current_y, y)},{max(current_x, x)},{max(current_y, y)}"
        if wall in self.walls:
            self.logger.debug(f"Перемещение запрещено: стена обнаружена по пути {wall}.")
            return False

        self.logger.debug("Перемещение разрешено.")
        return True
