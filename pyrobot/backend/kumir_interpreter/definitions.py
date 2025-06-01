"""
Структуры данных для представления пользовательских функций и процедур в КуМире.

Этот модуль содержит классы для хранения определений алгоритмов,
их параметров и всей необходимой информации для выполнения.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from antlr4 import ParserRuleContext


@dataclass
class Parameter:
    """Представляет один параметр алгоритма (функции или процедуры)."""
    
    name: str                    # Имя параметра
    param_type: str             # Тип данных КуМира ('цел', 'вещ', 'лог', 'лит', 'сим')
    mode: str                   # Режим передачи параметра ('арг', 'рез', 'аргрез')
    is_table: bool = False      # Является ли параметр массивом (таблицей)
    
    def is_input(self) -> bool:
        """Проверяет, является ли параметр входным (арг или аргрез)."""
        return self.mode in ['арг', 'аргрез']
    
    def is_output(self) -> bool:
        """Проверяет, является ли параметр выходным (рез или аргрез)."""
        return self.mode in ['рез', 'аргрез']
    
    def is_input_output(self) -> bool:
        """Проверяет, является ли параметр входно-выходным (аргрез)."""
        return self.mode == 'аргрез'


@dataclass
class AlgorithmDefinition:
    """Представляет определение пользовательского алгоритма (функции или процедуры)."""
    
    name: str                           # Имя алгоритма
    return_type: Optional[str]         # Тип возвращаемого значения (None для процедур)
    parameters: List[Parameter]        # Список параметров
    body_context: Optional[ParserRuleContext]    # Ссылка на контекст тела алгоритма из ANTLR
    local_declarations: List[ParserRuleContext]  # Локальные объявления переменных
    
    @property
    def is_function(self) -> bool:
        """Проверяет, является ли алгоритм функцией (возвращает значение)."""
        return self.return_type is not None
    
    @property
    def is_procedure(self) -> bool:
        """Проверяет, является ли алгоритм процедурой (не возвращает значение)."""
        return self.return_type is None
    
    def get_parameter_by_name(self, name: str) -> Optional[Parameter]:
        """Находит параметр по имени."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def validate_argument_count(self, arg_count: int) -> bool:
        """Проверяет соответствие количества переданных аргументов количеству параметров."""
        return len(self.parameters) == arg_count


@dataclass
class FunctionCallFrame:
    """Представляет фрейм вызова функции/процедуры для управления контекстом выполнения."""
    
    algorithm: AlgorithmDefinition     # Определение вызываемого алгоритма
    local_variables: Dict[str, Any]    # Локальные переменные и параметры
    output_variable_mapping: Dict[str, str]  # Мапинг параметров рез/аргрез на переменные вызывающего кода
    return_value: Optional[Any] = None       # Возвращаемое значение (для функций)
    has_returned: bool = False               # Флаг, что функция вернула значение через 'знач'
    
    def set_return_value(self, value: Any):
        """Устанавливает возвращаемое значение функции."""
        self.return_value = value
        self.has_returned = True
    
    def get_local_variable(self, name: str) -> Any:
        """Получает значение локальной переменной или параметра."""
        return self.local_variables.get(name)
    
    def set_local_variable(self, name: str, value: Any):
        """Устанавливает значение локальной переменной или параметра."""
        self.local_variables[name] = value


class FunctionReturnException(Exception):
    """
    Исключение для реализации немедленного возврата из функции при выполнении 'знач := выражение'.
    
    Это исключение используется для прерывания выполнения тела функции и передачи
    возвращаемого значения обратно в место вызова.
    """
    
    def __init__(self, return_value: Any):
        self.return_value = return_value
        super().__init__(f"Function returned value: {return_value}")


class AlgorithmManager:
    """
    Менеджер для хранения и управления пользовательскими алгоритмами.
    
    Этот класс отвечает за:
    - Регистрацию определений алгоритмов
    - Поиск алгоритмов по имени
    - Валидацию определений
    """
    
    def __init__(self):
        self.algorithms: Dict[str, AlgorithmDefinition] = {}
    
    def register_algorithm(self, algorithm: AlgorithmDefinition):
        """
        Регистрирует новый алгоритм.
        
        Args:
            algorithm: Определение алгоритма для регистрации
            
        Raises:
            ValueError: Если алгоритм с таким именем уже существует
        """
        if algorithm.name in self.algorithms:
            raise ValueError(f"Алгоритм '{algorithm.name}' уже определён")
        
        self.algorithms[algorithm.name] = algorithm
    
    def get_algorithm(self, name: str) -> Optional[AlgorithmDefinition]:
        """
        Получает определение алгоритма по имени.
        
        Args:
            name: Имя алгоритма
            
        Returns:
            Определение алгоритма или None, если не найден
        """
        return self.algorithms.get(name)
    
    def has_algorithm(self, name: str) -> bool:
        """Проверяет, существует ли алгоритм с данным именем."""
        return name in self.algorithms
    
    def is_function(self, name: str) -> bool:
        """Проверяет, является ли алгоритм с данным именем функцией."""
        algorithm = self.get_algorithm(name)
        return algorithm is not None and algorithm.is_function
    
    def is_procedure(self, name: str) -> bool:
        """Проверяет, является ли алгоритм с данным именем процедурой."""
        algorithm = self.get_algorithm(name)
        return algorithm is not None and algorithm.is_procedure
    
    def get_all_algorithms(self) -> List[AlgorithmDefinition]:
        """Возвращает список всех зарегистрированных алгоритмов."""
        return list(self.algorithms.values())
    
    def clear(self):
        """Очищает все зарегистрированные алгоритмы."""
        self.algorithms.clear()
