# interpreter.py
"""
Главный интерфейс интерпретатора КуМир.
Обеспечивает совместимость с server.py и инкапсулирует новую модульную архитектуру.
"""

import logging
from typing import Optional, Dict, Any, Callable, List
from io import StringIO
import sys

# ANTLR
from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

# Наши компоненты
from .generated.KumirLexer import KumirLexer
from .generated.KumirParser import KumirParser
from .interpreter_components.main_visitor import KumirInterpreterVisitor
from .kumir_exceptions import (
    KumirSyntaxError, KumirInputRequiredError, KumirRuntimeError, 
    ExitSignal, StopExecutionSignal
)
from .robot_state import SimulatedRobot
from .robot_integration import integrate_robot_with_visitor


logger = logging.getLogger(__name__)


class DiagnosticErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_msg = f"Синтаксическая ошибка: {msg}"
        raise KumirSyntaxError(error_msg, line_index=line - 1, column_index=column)


class KumirLanguageInterpreter:
    """
    Главный класс интерпретатора языка КуМир.
    Обеспечивает совместимость с server.py и управляет выполнением программ.
    """
    
    def __init__(self, code: str, initial_field_state: Optional[Dict[str, Any]] = None):
        """
        Инициализация интерпретатора.
        
        Args:
            code: Исходный код программы КуМир
            initial_field_state: Начальное состояние поля (ширина, высота, позиция робота и т.д.)
        """
        self.code = code
        self.program_lines = code.splitlines()
        
        # Инициализация состояния поля и робота
        self._init_field_state(initial_field_state)
        
        # Буферы для ввода/вывода
        self.output = ""
        self.input_buffer = ""
        self.input_requests = []
        
        # Флаги состояния
        self.is_running = False
        self.requires_input = False
        self.current_input_request = None
        
        # Callback для прогресса выполнения
        self.progress_callback: Optional[Callable] = None
        
        # Трассировка выполнения
        self.trace = []
        
        logger.debug(f"KumirLanguageInterpreter initialized with code length: {len(code)}")

    def _init_field_state(self, initial_state: Optional[Dict[str, Any]]):
        """Инициализация состояния поля и робота."""
        if initial_state:
            self.width = initial_state.get('width', 7)
            self.height = initial_state.get('height', 7)
            robot_pos = initial_state.get('robotPos', {'x': 0, 'y': 0})
            
            # Создаем симулированного робота
            self.robot = SimulatedRobot(
                width=self.width,
                height=self.height,
                initial_pos=robot_pos
            )
            
            # Применяем состояние поля
            walls = initial_state.get('walls', [])
            for wall in walls:
                # Парсим стену в формате "x1,y1,x2,y2"
                try:
                    coords = wall.split(',')
                    if len(coords) == 4:
                        x1, y1, x2, y2 = map(int, coords)
                        # Добавляем стену в множество walls робота
                        self.robot.walls.add(f"{x1},{y1},{x2},{y2}")
                except (ValueError, IndexError):
                    logger.warning(f"Invalid wall format: {wall}")
            
            # Маркеры
            markers = initial_state.get('markers', {})
            for pos_key, count in markers.items():
                try:
                    # Устанавливаем маркеры напрямую
                    self.robot.markers[pos_key] = count
                except (ValueError, IndexError):
                    logger.warning(f"Invalid marker position: {pos_key}")
            
            # Закрашенные клетки
            colored_cells = initial_state.get('coloredCells', [])
            for cell in colored_cells:
                try:
                    # Добавляем в множество закрашенных клеток
                    self.robot.colored_cells.add(cell)
                except (ValueError, IndexError):
                    logger.warning(f"Invalid colored cell: {cell}")
                    
        else:
            # Значения по умолчанию
            self.width = 7
            self.height = 7
            self.robot = SimulatedRobot(
                width=self.width,
                height=self.height,
                initial_pos={'x': 0, 'y': 0}
            )

    def interpret(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Выполнение программы КуМир.
        
        Args:
            progress_callback: Функция для отправки прогресса выполнения
            
        Returns:
            Словарь с результатами выполнения
        """
        self.progress_callback = progress_callback
        self.is_running = True
        self.trace = []
        
        try:
            # Парсинг кода
            tree = self._parse_code()
            
            # Выполнение программы
            result = self._execute_program(tree)
            
            return result
            
        except KumirInputRequiredError as e:
            return {
                'success': False,
                'input_required': True,
                'var_name': getattr(e, 'var_name', 'unknown'),
                'prompt': getattr(e, 'prompt', 'Введите значение:'),
                'target_type': getattr(e, 'target_type', 'лит'),
                'trace': self.trace
            }
            
        except (KumirSyntaxError, KumirRuntimeError) as e:
            return {
                'success': False,
                'message': str(e),
                'errorIndex': getattr(e, 'line_index', -1),
                'finalState': self.get_state(),
                'trace': self.trace
            }
            
        except Exception as e:
            logger.exception("Unexpected error during interpretation")
            return {
                'success': False,
                'message': f"Внутренняя ошибка: {type(e).__name__}: {str(e)}",
                'finalState': self.get_state(),
                'trace': self.trace
            }
            
        finally:
            self.is_running = False

    def _parse_code(self):
        """Парсинг исходного кода."""
        input_stream = InputStream(self.code)
        lexer = KumirLexer(input_stream)
        lexer.removeErrorListeners()
        
        error_listener = DiagnosticErrorListener()
        lexer.addErrorListener(error_listener)
        
        token_stream = CommonTokenStream(lexer)
        parser = KumirParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        return parser.program()

    def _execute_program(self, tree) -> Dict[str, Any]:
        """Выполнение программы с использованием visitor."""
        # Перехват вывода
        original_stdout = sys.stdout
        captured_output = StringIO()
        
        def output_fn(text: str):
            self.output += text
            captured_output.write(text)
            # Отправляем прогресс через callback если есть
            if self.progress_callback:
                try:
                    progress_data = {
                        'output': self.output,
                        'robotPos': self.robot.robot_pos.copy() if self.robot else {'x': 0, 'y': 0}
                    }
                    self.progress_callback(progress_data)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")
            
        def input_fn():
            # В данный момент просто возвращаем пустую строку
            # В будущем здесь будет обработка ввода
            return ""
            
        def error_fn(text: str):
            sys.stderr.write(text)

        try:
            # Создаем visitor
            visitor = KumirInterpreterVisitor(
                input_stream=input_fn,
                output_stream=output_fn,
                error_stream=error_fn,
                program_lines=self.program_lines
            )
            
            # Интегрируем робота с visitor
            integrate_robot_with_visitor(visitor, self.robot)
            
            # Выполняем программу
            visitor.visitProgram(tree)
            
            # Ищем главный алгоритм и выполняем
            if hasattr(visitor, 'procedure_manager') and visitor.procedure_manager.procedures:
                algorithm_to_run = self._find_main_algorithm(visitor.procedure_manager.procedures)
                if algorithm_to_run and hasattr(visitor, 'execute_algorithm_node'):
                    visitor.execute_algorithm_node(algorithm_to_run)
            return {
                'success': True,
                'message': 'Программа выполнена успешно',
                'finalState': self.get_state(),
                'trace': self.trace
            }
            
        except (ExitSignal, StopExecutionSignal):
            # Нормальное завершение программы
            return {
                'success': True,
                'message': 'Программа завершена',
                'finalState': self.get_state(),
                'trace': self.trace
            }
            
        finally:
            sys.stdout = original_stdout

    def _find_main_algorithm(self, procedures: Dict[str, Any]) -> Optional[str]:
        """Поиск главного алгоритма для выполнения."""
        # Ищем алгоритм с именем "главный"
        if "главный" in procedures:
            return "главный"
        
        # Если нет "главного", берем первую процедуру (не функцию)
        for name, data in procedures.items():
            if not data.get('is_function', False):
                return name
        
        return None

    def get_state(self) -> Dict[str, Any]:
        """Получение текущего состояния интерпретатора."""
        state = {
            'output': self.output,
            'robot': {
                'x': self.robot.robot_pos['x'],
                'y': self.robot.robot_pos['y']
            } if self.robot else {'x': 0, 'y': 0},
            'walls': [],
            'markers': {},
            'coloredCells': [],
            'symbols': {},
            'radiation': {},
            'temperature': {},
            'robotErrorDirection': None
        }
        
        if self.robot:
            # Собираем стены
            if hasattr(self.robot, 'walls'):
                state['walls'] = [f"{x1},{y1},{x2},{y2}" for (x1, y1, x2, y2) in self.robot.walls]
            
            # Собираем маркеры
            if hasattr(self.robot, 'markers'):
                state['markers'] = {pos: count for pos, count in self.robot.markers.items() if count > 0}
            
            # Собираем закрашенные клетки
            if hasattr(self.robot, 'colored_cells'):
                state['coloredCells'] = list(self.robot.colored_cells)
            
            # Собираем направление ошибки движения
            if hasattr(self.robot, 'error_direction'):
                state['robotErrorDirection'] = self.robot.error_direction
        
        return state

    def provide_input(self, input_value: str):
        """Предоставление входных данных программе."""
        self.input_buffer += input_value + "\n"
        self.requires_input = False
        self.current_input_request = None

    def stop(self):
        """Остановка выполнения программы."""
        self.is_running = False

    def reset(self):
        """Сброс состояния интерпретатора."""
        self.output = ""
        self.input_buffer = ""
        self.input_requests = []
        self.trace = []
        self.is_running = False
        self.requires_input = False
        self.current_input_request = None
        
        # Сброс робота
        if self.robot:
            self.robot.reset()
