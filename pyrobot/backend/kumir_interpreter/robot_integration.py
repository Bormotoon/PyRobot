# robot_integration.py
"""
Интеграция команд робота с новой архитектурой интерпретатора.
Обеспечивает связь между AST visitor и SimulatedRobot.
"""

import logging
from typing import Dict, Any, Optional
from .robot_state import SimulatedRobot
from .kumir_exceptions import RobotError

logger = logging.getLogger(__name__)

class RobotCommandHandler:
    """Обработчик команд робота для интеграции с AST visitor."""
    
    def __init__(self, robot: SimulatedRobot):
        self.robot = robot
        self.logger = logger
        
        # Маппинг команд КуМир на методы робота
        self.command_map = {
            'влево': self.robot.go_left,
            'вправо': self.robot.go_right,
            'вверх': self.robot.go_up,
            'вниз': self.robot.go_down,
            'закрасить': self.robot.do_paint,
            'поставить маркер': self.robot.put_marker,
            'убрать маркер': self.robot.pick_marker,
        }
        
        # Маппинг функций измерения
        self.measurement_map: Dict[str, Any] = {
            'радиация': lambda: self.robot.do_measurement('radiation'),
            'температура': lambda: self.robot.do_measurement('temperature'),
        }
        
        # Маппинг условий КуМир на методы робота
        self.condition_map: Dict[str, Any] = {
            'слева свободно': lambda: self.robot.check_direction('left', 'free'),
            'справа свободно': lambda: self.robot.check_direction('right', 'free'),
            'сверху свободно': lambda: self.robot.check_direction('up', 'free'),
            'снизу свободно': lambda: self.robot.check_direction('down', 'free'),
            'слева стена': lambda: self.robot.check_direction('left', 'wall'),
            'справа стена': lambda: self.robot.check_direction('right', 'wall'),
            'сверху стена': lambda: self.robot.check_direction('up', 'wall'),
            'снизу стена': lambda: self.robot.check_direction('down', 'wall'),
            'клетка закрашена': lambda: self.robot.check_cell('painted'),
            'клетка чистая': lambda: self.robot.check_cell('clear'),
            'маркер есть': lambda: bool(self.robot.is_marker_here()),
            'маркер нет': lambda: not bool(self.robot.is_marker_here()),
        }
    
    def execute_command(self, command: str) -> bool:
        """
        Выполняет команду робота.
        
        Args:
            command: Команда в виде строки (например, 'вправо')
            
        Returns:
            True если команда была выполнена, False если команда не распознана
            
        Raises:
            RobotError: При ошибке выполнения команды (стена, границы и т.п.)
        """
        command_lower = command.strip().lower()
        
        if command_lower in self.command_map:
            try:
                self.command_map[command_lower]()
                self.logger.debug(f"Robot command executed: {command}")
                return True
            except RobotError as e:
                self.logger.warning(f"Robot command failed: {command} - {e}")
                if hasattr(self.robot, 'error_direction'):
                    self.logger.info(f"Robot error_direction set to: {self.robot.error_direction}")
                raise
        
        return False
    
    def execute_measurement(self, measurement_type: str) -> float:
        """
        Выполняет команду измерения робота.
        
        Args:
            measurement_type: Тип измерения ('radiation' или 'temperature')
            
        Returns:
            Результат измерения (float или int)
            
        Raises:
            RobotError: При ошибке выполнения измерения
        """
        try:
            result = self.robot.do_measurement(measurement_type)
            self.logger.debug(f"Robot measurement executed: {measurement_type} = {result}")
            return result
        except Exception as e:
            self.logger.error(f"Robot measurement failed: {measurement_type} - {e}")
            raise RobotError(f"Ошибка измерения {measurement_type}: {e}")
    
    def check_condition(self, condition: str) -> Optional[bool]:
        """
        Проверяет условие робота.
        
        Args:
            condition: Условие в виде строки
            
        Returns:
            True/False если условие распознано и проверено, None если не распознано
        """
        condition_lower = condition.strip().lower()
        
        if condition_lower in self.condition_map:
            try:
                result = self.condition_map[condition_lower]()
                self.logger.debug(f"Robot condition checked: {condition} = {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error checking robot condition {condition}: {e}")
                return False
        
        return None
    
    def get_robot_functions(self) -> Dict[str, Any]:
        """
        Возвращает словарь функций робота для интеграции с visitor.
        
        Returns:
            Словарь с функциями робота
        """
        return {
            # Команды движения
            'влево': {'type': 'procedure', 'handler': lambda: self.execute_command('влево')},
            'вправо': {'type': 'procedure', 'handler': lambda: self.execute_command('вправо')},
            'вверх': {'type': 'procedure', 'handler': lambda: self.execute_command('вверх')},
            'вниз': {'type': 'procedure', 'handler': lambda: self.execute_command('вниз')},
            
            # Команды действий
            'закрасить': {'type': 'procedure', 'handler': lambda: self.execute_command('закрасить')},
            'поставить маркер': {'type': 'procedure', 'handler': lambda: self.execute_command('поставить маркер')},
            'убрать маркер': {'type': 'procedure', 'handler': lambda: self.execute_command('убрать маркер')},
            
            # Условия (функции)
            'слева свободно': {'type': 'function', 'handler': lambda: self.check_condition('слева свободно')},
            'справа свободно': {'type': 'function', 'handler': lambda: self.check_condition('справа свободно')},
            'сверху свободно': {'type': 'function', 'handler': lambda: self.check_condition('сверху свободно')},
            'снизу свободно': {'type': 'function', 'handler': lambda: self.check_condition('снизу свободно')},
            'слева стена': {'type': 'function', 'handler': lambda: self.check_condition('слева стена')},
            'справа стена': {'type': 'function', 'handler': lambda: self.check_condition('справа стена')},
            'сверху стена': {'type': 'function', 'handler': lambda: self.check_condition('сверху стена')},
            'снизу стена': {'type': 'function', 'handler': lambda: self.check_condition('снизу стена')},
            'клетка закрашена': {'type': 'function', 'handler': lambda: self.check_condition('клетка закрашена')},
            'клетка чистая': {'type': 'function', 'handler': lambda: self.check_condition('клетка чистая')},
            'маркер есть': {'type': 'function', 'handler': lambda: self.check_condition('маркер есть')},
            'маркер нет': {'type': 'function', 'handler': lambda: self.check_condition('маркер нет')},
        }

def integrate_robot_with_visitor(visitor, robot: SimulatedRobot):
    """
    Интегрирует робота с visitor интерпретатора.
    
    Args:
        visitor: Экземпляр KumirInterpreterVisitor
        robot: Экземпляр SimulatedRobot
    """
    handler = RobotCommandHandler(robot)
    
    # Устанавливаем робота и обработчик в visitor
    if hasattr(visitor, 'set_robot'):
        visitor.set_robot(robot)
    if hasattr(visitor, 'set_robot_command_handler'):
        visitor.set_robot_command_handler(handler)
    
    # Регистрируем команды и условия робота
    _register_robot_commands(visitor, handler)
    _register_robot_conditions(visitor, handler)
    
    logger.info("Robot integration completed")


def _register_robot_commands(visitor, handler):
    """Регистрирует команды робота как встроенные процедуры в visitor."""
    # Получаем builtin_procedure_handler из visitor
    if hasattr(visitor, 'builtin_procedure_handler'):
        builtin_handler = visitor.builtin_procedure_handler
        
        # Регистрируем команды движения
        if hasattr(builtin_handler, 'register_procedure'):
            def make_command_wrapper(cmd: str):
                def wrapper() -> bool:
                    return handler.execute_command(cmd)
                return wrapper
            
            builtin_handler.register_procedure('вправо', make_command_wrapper('вправо'))
            builtin_handler.register_procedure('влево', make_command_wrapper('влево'))
            builtin_handler.register_procedure('вверх', make_command_wrapper('вверх'))
            builtin_handler.register_procedure('вниз', make_command_wrapper('вниз'))
            builtin_handler.register_procedure('закрасить', make_command_wrapper('закрасить'))
            builtin_handler.register_procedure('поставить маркер', make_command_wrapper('поставить маркер'))
            builtin_handler.register_procedure('убрать маркер', make_command_wrapper('убрать маркер'))


def _register_robot_conditions(visitor, handler):
    """Регистрирует условия робота как встроенные функции в visitor."""
    # Получаем builtin_function_handler из visitor
    if hasattr(visitor, 'builtin_function_handler'):
        builtin_handler = visitor.builtin_function_handler
        
        # Регистрируем условия - исправляем, чтобы возвращали логический тип
        if hasattr(builtin_handler, 'register_function'):
            # Создаем обёртки, которые возвращают логический результат
            def make_robot_condition_wrapper(condition_name: str):
                def wrapper() -> bool:
                    result = handler.check_condition(condition_name)
                    # Возвращаем логическое значение для КуМир
                    return result if result is not None else False
                return wrapper
            
            builtin_handler.register_function('стена_справа', make_robot_condition_wrapper('справа стена'))
            builtin_handler.register_function('стена_слева', make_robot_condition_wrapper('слева стена'))
            builtin_handler.register_function('стена_сверху', make_robot_condition_wrapper('сверху стена'))
            builtin_handler.register_function('стена_снизу', make_robot_condition_wrapper('снизу стена'))
            builtin_handler.register_function('свободно_справа', make_robot_condition_wrapper('справа свободно'))
            builtin_handler.register_function('свободно_слева', make_robot_condition_wrapper('слева свободно'))
            builtin_handler.register_function('свободно_сверху', make_robot_condition_wrapper('сверху свободно'))
            builtin_handler.register_function('свободно_снизу', make_robot_condition_wrapper('снизу свободно'))
            builtin_handler.register_function('клетка_закрашена', make_robot_condition_wrapper('клетка закрашена'))
            builtin_handler.register_function('клетка_чистая', make_robot_condition_wrapper('клетка чистая'))
            
            # Добавляем команды измерения радиации и температуры
            def make_measurement_wrapper(measurement_type: str):
                def wrapper() -> float:
                    return handler.execute_measurement(measurement_type)
                return wrapper
            
            builtin_handler.register_function('радиация', make_measurement_wrapper('radiation'))
            builtin_handler.register_function('температура', make_measurement_wrapper('temperature'))
