#!/usr/bin/env python3
"""
Специализированный процессор для задач с роботом.

Обрабатывает задачи исполнителя Робот:
- Движение по полю
- Закраска клеток
- Проверка условий
- Навигация в лабиринте
"""

from pathlib import Path
from typing import List, Dict, Any


class RobotTaskProcessor:
    """Процессор для задач с роботом."""
    
    def __init__(self):
        """Инициализация процессора робота."""
        self.robot_operations = {
            'simple_movement': self._generate_simple_movement,
            'field_painting': self._generate_field_painting,
            'maze_navigation': self._generate_maze_navigation,
            'conditional_movement': self._generate_conditional_movement,
            'pattern_drawing': self._generate_pattern_drawing,
            'area_filling': self._generate_area_filling,
        }
    
    def process_tasks(self, tasks: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает список задач с роботом.
        
        Args:
            tasks: Список задач с роботом
            output_dir: Выходная директория
            
        Returns:
            Результаты обработки
        """
        results = {
            'processor_type': 'robot',
            'total_tasks': len(tasks),
            'processed_tasks': 0,
            'generated_files': {
                'python': [],
                'kumir': []
            },
            'task_details': []
        }
        
        # Создаем поддиректории
        py_dir = output_dir / "py" / "robot"
        kum_dir = output_dir / "kum" / "robot"
        py_dir.mkdir(parents=True, exist_ok=True)
        kum_dir.mkdir(parents=True, exist_ok=True)
        
        for i, task in enumerate(tasks, 1):
            try:
                task_result = self.process_single_task(task, i, py_dir, kum_dir)
                results['task_details'].append(task_result)
                results['processed_tasks'] += 1
                
                if task_result['python_file']:
                    results['generated_files']['python'].append(task_result['python_file'])
                if task_result['kumir_file']:
                    results['generated_files']['kumir'].append(task_result['kumir_file'])
                    
            except Exception as e:
                error_details = {
                    'task_id': f"robot_{i}",
                    'error': str(e),
                    'title': task.get('title', 'Без названия')
                }
                results['task_details'].append(error_details)
        
        return results
    
    def process_single_task(self, task: Dict[str, Any], task_num: int, py_dir: Path, kum_dir: Path) -> Dict[str, Any]:
        """
        Обрабатывает одну задачу с роботом.
        
        Args:
            task: Данные задачи
            task_num: Номер задачи
            py_dir: Директория для Python файлов
            kum_dir: Директория для KUM файлов
            
        Returns:
            Результат обработки задачи
        """
        # Анализируем тип операции робота
        operation_type = self._detect_robot_operation(task)
        
        # Генерируем базовое имя файла
        base_name = f"robot_{task_num:02d}_{operation_type}"
        
        # Генерируем Python код
        python_code = self._generate_python_solution(task, operation_type)
        python_file = py_dir / f"{base_name}.py"
        
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        # Сохраняем KUM код
        kumir_code = task.get('student_code', '')
        kumir_file = kum_dir / f"{base_name}.kum"
        
        with open(kumir_file, 'w', encoding='utf-8') as f:
            f.write(kumir_code)
        
        return {
            'task_id': base_name,
            'title': task.get('title', 'Робот'),
            'operation_type': operation_type,
            'python_file': str(python_file.relative_to(py_dir.parent.parent)),
            'kumir_file': str(kumir_file.relative_to(kum_dir.parent.parent)),
            'status': 'success'
        }
    
    def _detect_robot_operation(self, task: Dict[str, Any]) -> str:
        """Определяет тип операции робота."""
        
        title = task.get('title', '').lower()
        code = task.get('student_code', '').lower()
        combined_text = f"{title} {code}"
        
        # Паттерны для определения операций
        if any(pattern in combined_text for pattern in ['закрасить', 'закраска', 'рисование']):
            if any(pattern in combined_text for pattern in ['узор', 'pattern', 'фигура']):
                return 'pattern_drawing'
            elif any(pattern in combined_text for pattern in ['область', 'заливка', 'fill']):
                return 'area_filling'
            else:
                return 'field_painting'
        elif any(pattern in combined_text for pattern in ['лабиринт', 'maze', 'навигация']):
            return 'maze_navigation'
        elif any(pattern in combined_text for pattern in ['если', 'пока', 'условие', 'свободно', 'стена']):
            return 'conditional_movement'
        elif any(pattern in combined_text for pattern in ['движение', 'перемещение', 'move']):
            return 'simple_movement'
        else:
            return 'generic_robot'
    
    def _generate_python_solution(self, task: Dict[str, Any], operation_type: str) -> str:
        """Генерирует Python решение для задачи с роботом."""
        
        if operation_type in self.robot_operations:
            return self.robot_operations[operation_type](task)
        else:
            return self._generate_generic_robot_solution(task)
    
    def _generate_simple_movement(self, task: Dict[str, Any]) -> str:
        """Генерирует код простого движения робота."""
        return '''#!/usr/bin/env python3
"""
Простое движение робота.
"""

class SimpleRobot:
    """Простая модель робота для демонстрации движения."""
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.path = [(x, y)]
    
    def move_up(self):
        """Движение вверх."""
        self.y += 1
        self.path.append((self.x, self.y))
        print(f"Робот переместился вверх: ({self.x}, {self.y})")
    
    def move_down(self):
        """Движение вниз."""
        self.y -= 1
        self.path.append((self.x, self.y))
        print(f"Робот переместился вниз: ({self.x}, {self.y})")
    
    def move_left(self):
        """Движение влево."""
        self.x -= 1
        self.path.append((self.x, self.y))
        print(f"Робот переместился влево: ({self.x}, {self.y})")
    
    def move_right(self):
        """Движение вправо."""
        self.x += 1
        self.path.append((self.x, self.y))
        print(f"Робот переместился вправо: ({self.x}, {self.y})")
    
    def get_position(self):
        """Возвращает текущую позицию."""
        return self.x, self.y
    
    def show_path(self):
        """Показывает пройденный путь."""
        print("Пройденный путь:")
        for i, (x, y) in enumerate(self.path):
            print(f"{i}: ({x}, {y})")

def main():
    # Создаем робота
    robot = SimpleRobot()
    
    # Демонстрация движения
    print("Начальная позиция:", robot.get_position())
    
    # Последовательность движений
    robot.move_right()
    robot.move_right()
    robot.move_up()
    robot.move_up()
    robot.move_left()
    robot.move_down()
    
    print("Финальная позиция:", robot.get_position())
    robot.show_path()

if __name__ == "__main__":
    main()
'''
    
    def _generate_field_painting(self, task: Dict[str, Any]) -> str:
        """Генерирует код закраски поля."""
        return '''#!/usr/bin/env python3
"""
Закраска поля роботом.
"""

class PaintingRobot:
    """Робот для закраски клеток."""
    
    def __init__(self, field_width=10, field_height=10):
        self.x = 0
        self.y = 0
        self.field_width = field_width
        self.field_height = field_height
        self.painted_cells = set()
    
    def paint_cell(self):
        """Закрашивает текущую клетку."""
        self.painted_cells.add((self.x, self.y))
        print(f"Закрашена клетка ({self.x}, {self.y})")
    
    def is_painted(self, x=None, y=None):
        """Проверяет, закрашена ли клетка."""
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        return (x, y) in self.painted_cells
    
    def move_and_paint(self, direction):
        """Перемещается и закрашивает клетку."""
        if direction == "up" and self.y < self.field_height - 1:
            self.y += 1
        elif direction == "down" and self.y > 0:
            self.y -= 1
        elif direction == "left" and self.x > 0:
            self.x -= 1
        elif direction == "right" and self.x < self.field_width - 1:
            self.x += 1
        
        self.paint_cell()
    
    def paint_line(self, direction, length):
        """Закрашивает линию в заданном направлении."""
        self.paint_cell()  # Закрашиваем стартовую клетку
        
        for _ in range(length):
            self.move_and_paint(direction)
    
    def paint_rectangle(self, width, height):
        """Закрашивает прямоугольник."""
        start_x, start_y = self.x, self.y
        
        for row in range(height):
            # Закрашиваем строку
            for col in range(width):
                self.paint_cell()
                if col < width - 1:  # Не двигаемся после последней клетки в ряду
                    self.move_and_paint("right")
            
            # Переходим к следующему ряду
            if row < height - 1:
                self.x = start_x
                self.y += 1
    
    def show_field(self):
        """Отображает поле с закрашенными клетками."""
        print("\\nПоле (X - закрашено, . - пусто):")
        for y in range(self.field_height - 1, -1, -1):
            row = ""
            for x in range(self.field_width):
                if (x, y) in self.painted_cells:
                    row += "X "
                else:
                    row += ". "
            print(f"{y:2d} {row}")
        
        # Показываем координаты X
        print("   ", end="")
        for x in range(self.field_width):
            print(f"{x} ", end="")
        print()

def main():
    # Создаем робота-художника
    robot = PaintingRobot(8, 6)
    
    print("Демонстрация закраски поля")
    print(f"Робот находится в позиции ({robot.x}, {robot.y})")
    
    # Рисуем линию
    robot.paint_line("right", 3)
    
    # Перемещаемся и рисуем прямоугольник
    robot.x, robot.y = 1, 2
    robot.paint_rectangle(3, 2)
    
    # Показываем результат
    robot.show_field()
    print(f"Всего закрашено клеток: {len(robot.painted_cells)}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_maze_navigation(self, task: Dict[str, Any]) -> str:
        """Генерирует код навигации в лабиринте."""
        return '''#!/usr/bin/env python3
"""
Навигация робота в лабиринте.
"""

class MazeRobot:
    """Робот для навигации в лабиринте."""
    
    def __init__(self, maze):
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0]) if maze else 0
        self.x = 0
        self.y = 0
        self.path = [(0, 0)]
        
        # Находим стартовую позицию (первая свободная клетка)
        self.find_start_position()
    
    def find_start_position(self):
        """Находит стартовую позицию в лабиринте."""
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 0:  # 0 - свободная клетка
                    self.x = x
                    self.y = y
                    self.path = [(x, y)]
                    return
    
    def is_free(self, direction):
        """Проверяет, свободна ли клетка в заданном направлении."""
        dx, dy = 0, 0
        if direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        elif direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1
        
        new_x, new_y = self.x + dx, self.y + dy
        
        # Проверяем границы
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            return False
        
        # Проверяем, нет ли стены
        return self.maze[new_y][new_x] == 0
    
    def move(self, direction):
        """Перемещает робота в заданном направлении."""
        if not self.is_free(direction):
            return False
        
        if direction == "up":
            self.y -= 1
        elif direction == "down":
            self.y += 1
        elif direction == "left":
            self.x -= 1
        elif direction == "right":
            self.x += 1
        
        self.path.append((self.x, self.y))
        return True
    
    def find_exit(self, target_x, target_y):
        """Ищет путь к выходу методом правой руки."""
        directions = ["up", "right", "down", "left"]
        current_direction = 0
        visited = set()
        
        while (self.x, self.y) != (target_x, target_y):
            if (self.x, self.y) in visited and len(visited) > 10:
                print("Робот зашел в тупик или зациклился")
                break
            
            visited.add((self.x, self.y))
            
            # Пробуем повернуть направо
            right_direction = (current_direction + 1) % 4
            if self.is_free(directions[right_direction]):
                current_direction = right_direction
                self.move(directions[current_direction])
            # Пробуем идти прямо
            elif self.is_free(directions[current_direction]):
                self.move(directions[current_direction])
            # Поворачиваем налево
            else:
                current_direction = (current_direction - 1) % 4
        
        return (self.x, self.y) == (target_x, target_y)
    
    def show_maze_with_path(self):
        """Отображает лабиринт с пройденным путем."""
        print("\\nЛабиринт (# - стена, . - свободно, * - путь, R - робот):")
        
        path_set = set(self.path[:-1])  # Путь без текущей позиции
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if (x, y) == (self.x, self.y):
                    row += "R "
                elif (x, y) in path_set:
                    row += "* "
                elif self.maze[y][x] == 1:
                    row += "# "
                else:
                    row += ". "
            print(row)

def main():
    # Пример лабиринта (0 - свободно, 1 - стена)
    maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0]
    ]
    
    # Создаем робота
    robot = MazeRobot(maze)
    
    print(f"Робот стартует с позиции ({robot.x}, {robot.y})")
    
    # Ищем путь к выходу
    target_x, target_y = 4, 0
    print(f"Цель: ({target_x}, {target_y})")
    
    success = robot.find_exit(target_x, target_y)
    
    if success:
        print(f"Путь найден! Робот достиг цели за {len(robot.path)} шагов.")
    else:
        print("Путь не найден.")
    
    robot.show_maze_with_path()

if __name__ == "__main__":
    main()
'''
    
    def _generate_conditional_movement(self, task: Dict[str, Any]) -> str:
        """Генерирует код условного движения."""
        return '''#!/usr/bin/env python3
"""
Условное движение робота.
"""

class ConditionalRobot:
    """Робот с условным движением."""
    
    def __init__(self, field_map):
        self.field_map = field_map
        self.height = len(field_map)
        self.width = len(field_map[0]) if field_map else 0
        self.x = 0
        self.y = 0
        self.steps = 0
    
    def is_wall(self, direction):
        """Проверяет наличие стены в направлении."""
        dx, dy = self._get_direction_offset(direction)
        new_x, new_y = self.x + dx, self.y + dy
        
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            return True  # За границей поля - считаем стеной
        
        return self.field_map[new_y][new_x] == 1
    
    def is_free(self, direction):
        """Проверяет, свободно ли в направлении."""
        return not self.is_wall(direction)
    
    def _get_direction_offset(self, direction):
        """Возвращает смещение для направления."""
        offsets = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }
        return offsets.get(direction, (0, 0))
    
    def move_if_free(self, direction):
        """Двигается в направлении, если свободно."""
        if self.is_free(direction):
            dx, dy = self._get_direction_offset(direction)
            self.x += dx
            self.y += dy
            self.steps += 1
            print(f"Шаг {self.steps}: движение {direction} -> ({self.x}, {self.y})")
            return True
        else:
            print(f"Шаг {self.steps + 1}: движение {direction} невозможно - стена")
            return False
    
    def move_until_wall(self, direction):
        """Двигается в направлении до стены."""
        moved_steps = 0
        while self.is_free(direction):
            if self.move_if_free(direction):
                moved_steps += 1
            else:
                break
        
        print(f"Прошел {moved_steps} шагов до стены")
        return moved_steps
    
    def find_free_direction(self):
        """Находит первое свободное направление."""
        directions = ["up", "right", "down", "left"]
        for direction in directions:
            if self.is_free(direction):
                return direction
        return None
    
    def navigate_smartly(self, max_steps=20):
        """Умная навигация с условиями."""
        for step in range(max_steps):
            # Приоритет направлений: право, вверх, лево, вниз
            preferred_directions = ["right", "up", "left", "down"]
            
            moved = False
            for direction in preferred_directions:
                if self.is_free(direction):
                    self.move_if_free(direction)
                    moved = True
                    break
            
            if not moved:
                print("Робот заблокирован со всех сторон!")
                break
    
    def show_field(self):
        """Показывает поле с позицией робота."""
        print("\\nПоле (# - стена, . - свободно, R - робот):")
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if (x, y) == (self.x, self.y):
                    row += "R "
                elif self.field_map[y][x] == 1:
                    row += "# "
                else:
                    row += ". "
            print(row)

def main():
    # Пример поля (0 - свободно, 1 - стена)
    field = [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1],
        [1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0]
    ]
    
    # Создаем робота
    robot = ConditionalRobot(field)
    
    print(f"Робот начинает с позиции ({robot.x}, {robot.y})")
    robot.show_field()
    
    # Демонстрация различных типов движения
    print("\\n1. Проверка направлений:")
    for direction in ["up", "down", "left", "right"]:
        if robot.is_free(direction):
            print(f"  {direction}: свободно")
        else:
            print(f"  {direction}: стена")
    
    print("\\n2. Умная навигация:")
    robot.navigate_smartly(10)
    
    robot.show_field()
    print(f"\\nРобот завершил навигацию в позиции ({robot.x}, {robot.y})")
    print(f"Всего шагов: {robot.steps}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_pattern_drawing(self, task: Dict[str, Any]) -> str:
        """Генерирует код рисования узоров."""
        return '''#!/usr/bin/env python3
"""
Рисование узоров роботом.
"""

class PatternRobot:
    """Робот для рисования узоров."""
    
    def __init__(self, field_width=15, field_height=15):
        self.x = 0
        self.y = 0
        self.field_width = field_width
        self.field_height = field_height
        self.painted_cells = set()
    
    def paint(self):
        """Закрашивает текущую клетку."""
        self.painted_cells.add((self.x, self.y))
    
    def move_to(self, x, y):
        """Перемещается в заданную позицию."""
        if 0 <= x < self.field_width and 0 <= y < self.field_height:
            self.x = x
            self.y = y
    
    def draw_square(self, size, start_x=None, start_y=None):
        """Рисует квадрат заданного размера."""
        if start_x is not None and start_y is not None:
            self.move_to(start_x, start_y)
        
        start_x, start_y = self.x, self.y
        
        # Верхняя и нижняя стороны
        for i in range(size):
            self.move_to(start_x + i, start_y)
            self.paint()
            self.move_to(start_x + i, start_y + size - 1)
            self.paint()
        
        # Левая и правая стороны
        for i in range(size):
            self.move_to(start_x, start_y + i)
            self.paint()
            self.move_to(start_x + size - 1, start_y + i)
            self.paint()
    
    def draw_filled_square(self, size, start_x=None, start_y=None):
        """Рисует заполненный квадрат."""
        if start_x is not None and start_y is not None:
            self.move_to(start_x, start_y)
        
        start_x, start_y = self.x, self.y
        
        for y in range(size):
            for x in range(size):
                self.move_to(start_x + x, start_y + y)
                self.paint()
    
    def draw_cross(self, size, start_x=None, start_y=None):
        """Рисует крест."""
        if start_x is not None and start_y is not None:
            self.move_to(start_x, start_y)
        
        start_x, start_y = self.x, self.y
        center = size // 2
        
        # Вертикальная линия
        for i in range(size):
            self.move_to(start_x + center, start_y + i)
            self.paint()
        
        # Горизонтальная линия
        for i in range(size):
            self.move_to(start_x + i, start_y + center)
            self.paint()
    
    def draw_diagonal(self, size, direction="main", start_x=None, start_y=None):
        """Рисует диагональ."""
        if start_x is not None and start_y is not None:
            self.move_to(start_x, start_y)
        
        start_x, start_y = self.x, self.y
        
        for i in range(size):
            if direction == "main":
                # Главная диагональ (сверху-слева в низ-справа)
                self.move_to(start_x + i, start_y + i)
            else:
                # Побочная диагональ (сверху-справа в низ-слева)
                self.move_to(start_x + size - 1 - i, start_y + i)
            self.paint()
    
    def draw_checkerboard(self, size, start_x=None, start_y=None):
        """Рисует шахматную доску."""
        if start_x is not None and start_y is not None:
            self.move_to(start_x, start_y)
        
        start_x, start_y = self.x, self.y
        
        for y in range(size):
            for x in range(size):
                # Закрашиваем клетки в шахматном порядке
                if (x + y) % 2 == 0:
                    self.move_to(start_x + x, start_y + y)
                    self.paint()
    
    def draw_border(self):
        """Рисует границу поля."""
        # Верхняя и нижняя границы
        for x in range(self.field_width):
            self.move_to(x, 0)
            self.paint()
            self.move_to(x, self.field_height - 1)
            self.paint()
        
        # Левая и правая границы
        for y in range(self.field_height):
            self.move_to(0, y)
            self.paint()
            self.move_to(self.field_width - 1, y)
            self.paint()
    
    def show_pattern(self):
        """Отображает нарисованный узор."""
        print("\\nУзор (X - закрашено, . - пусто):")
        for y in range(self.field_height - 1, -1, -1):
            row = ""
            for x in range(self.field_width):
                if (x, y) in self.painted_cells:
                    row += "X"
                else:
                    row += "."
            print(f"{y:2d} {row}")
        
        # Показываем координаты X
        print("   ", end="")
        for x in range(self.field_width):
            print(f"{x % 10}", end="")
        print()

def main():
    # Создаем робота-художника
    robot = PatternRobot(12, 10)
    
    print("Демонстрация рисования узоров")
    
    # Рисуем различные узоры
    robot.draw_border()
    robot.draw_square(4, 2, 2)
    robot.draw_filled_square(2, 8, 3)
    robot.draw_cross(5, 4, 6)
    robot.draw_checkerboard(3, 7, 6)
    
    # Показываем результат
    robot.show_pattern()
    print(f"\\nВсего закрашено клеток: {len(robot.painted_cells)}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_area_filling(self, task: Dict[str, Any]) -> str:
        """Генерирует код заливки области."""
        return '''#!/usr/bin/env python3
"""
Заливка области роботом.
"""

class AreaFillingRobot:
    """Робот для заливки областей."""
    
    def __init__(self, field_map):
        self.field_map = [row[:] for row in field_map]  # Копия поля
        self.height = len(field_map)
        self.width = len(field_map[0]) if field_map else 0
        self.x = 0
        self.y = 0
        self.filled_cells = set()
    
    def is_fillable(self, x, y):
        """Проверяет, можно ли заливать клетку."""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.field_map[y][x] == 0  # 0 - свободная клетка
    
    def fill_cell(self, x, y):
        """Заливает клетку."""
        if self.is_fillable(x, y):
            self.field_map[y][x] = 2  # 2 - залитая клетка
            self.filled_cells.add((x, y))
            return True
        return False
    
    def flood_fill(self, start_x, start_y):
        """Заливка области методом заливки (flood fill)."""
        if not self.is_fillable(start_x, start_y):
            return
        
        # Используем стек для итеративной реализации
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            
            if not self.is_fillable(x, y):
                continue
            
            # Заливаем текущую клетку
            self.fill_cell(x, y)
            
            # Добавляем соседние клетки в стек
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            for nx, ny in neighbors:
                if self.is_fillable(nx, ny):
                    stack.append((nx, ny))
    
    def fill_rectangle(self, x1, y1, x2, y2):
        """Заливает прямоугольную область."""
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if self.is_fillable(x, y):
                    self.fill_cell(x, y)
    
    def fill_line(self, x1, y1, x2, y2):
        """Заливает линию между двумя точками."""
        # Простая реализация для горизонтальных и вертикальных линий
        if x1 == x2:  # Вертикальная линия
            min_y, max_y = min(y1, y2), max(y1, y2)
            for y in range(min_y, max_y + 1):
                if self.is_fillable(x1, y):
                    self.fill_cell(x1, y)
        elif y1 == y2:  # Горизонтальная линия
            min_x, max_x = min(x1, x2), max(x1, x2)
            for x in range(min_x, max_x + 1):
                if self.is_fillable(x, y1):
                    self.fill_cell(x, y1)
    
    def smart_fill(self):
        """Умная заливка всех доступных областей."""
        for y in range(self.height):
            for x in range(self.width):
                if self.is_fillable(x, y):
                    print(f"Заливаем область начиная с ({x}, {y})")
                    cells_before = len(self.filled_cells)
                    self.flood_fill(x, y)
                    cells_after = len(self.filled_cells)
                    print(f"Залито {cells_after - cells_before} клеток")
    
    def show_field(self):
        """Отображает поле с залитыми областями."""
        print("\\nПоле (# - стена, . - свободно, X - залито, R - робот):")
        for y in range(self.height - 1, -1, -1):
            row = ""
            for x in range(self.width):
                if (x, y) == (self.x, self.y):
                    row += "R "
                elif self.field_map[y][x] == 1:
                    row += "# "
                elif self.field_map[y][x] == 2:
                    row += "X "
                else:
                    row += ". "
            print(f"{y:2d} {row}")
        
        # Показываем координаты X
        print("   ", end="")
        for x in range(self.width):
            print(f"{x % 10} ", end="")
        print()

def main():
    # Пример поля (0 - свободно, 1 - стена)
    field = [
        [0, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1],
        [0, 1, 0, 0, 0, 0]
    ]
    
    # Создаем робота
    robot = AreaFillingRobot(field)
    
    print("Демонстрация заливки областей")
    print("Исходное поле:")
    robot.show_field()
    
    # Заливаем конкретную область
    print("\\nЗаливка области, начиная с (0, 0):")
    robot.flood_fill(0, 0)
    robot.show_field()
    
    # Заливаем прямоугольник
    print("\\nЗаливка прямоугольника (3, 2) - (5, 4):")
    robot.fill_rectangle(3, 2, 5, 4)
    robot.show_field()
    
    print(f"\\nВсего залито клеток: {len(robot.filled_cells)}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_generic_robot_solution(self, task: Dict[str, Any]) -> str:
        """Генерирует общее решение для робота."""
        return '''#!/usr/bin/env python3
"""
Общая задача с роботом.
"""

class GenericRobot:
    """Универсальный робот для различных задач."""
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.commands_executed = []
    
    def execute_command(self, command):
        """Выполняет команду робота."""
        if command == "up":
            self.y += 1
        elif command == "down":
            self.y -= 1
        elif command == "left":
            self.x -= 1
        elif command == "right":
            self.x += 1
        elif command == "paint":
            print(f"Закрашена клетка ({self.x}, {self.y})")
        
        self.commands_executed.append(command)
        print(f"Выполнена команда: {command}, позиция: ({self.x}, {self.y})")
    
    def get_position(self):
        """Возвращает текущую позицию."""
        return self.x, self.y
    
    def get_command_history(self):
        """Возвращает историю команд."""
        return self.commands_executed[:]

def main():
    # Создаем универсального робота
    robot = GenericRobot()
    
    print("Универсальный робот готов к работе")
    print(f"Начальная позиция: {robot.get_position()}")
    
    # Демонстрация команд
    commands = ["right", "right", "up", "paint", "left", "up", "paint"]
    
    for command in commands:
        robot.execute_command(command)
    
    print(f"\\nФинальная позиция: {robot.get_position()}")
    print(f"История команд: {robot.get_command_history()}")

if __name__ == "__main__":
    main()
'''
