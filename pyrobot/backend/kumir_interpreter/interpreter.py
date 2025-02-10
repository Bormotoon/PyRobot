# interpreter.py

from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .execution import execute_lines, execute_line, process_algorithm_call
from .robot_interpreter import KumirInterpreter


class KumirLanguageInterpreter:
    def __init__(self, code):
        self.code = code
        # Environment for variables: { var_name: {"type": ..., "value": ..., "kind": ..., "is_table": ...} }
        self.env = {}
        self.algorithms = {}  # Dictionary for auxiliary algorithms by name
        self.main_algorithm = None
        # Create an instance of the robot executor
        self.robot = KumirInterpreter()
        # Buffer for capturing output from the "вывод" command
        self.output = ""

    def parse(self):
        """
        Processes the source code: removes comments, splits into introduction and algorithms,
        and parses algorithm headers.
        """
        lines = preprocess_code(self.code)
        introduction, algo_sections = separate_sections(lines)
        self.introduction = introduction
        self.algo_sections = algo_sections

        if algo_sections:
            # The first algorithm is considered the main algorithm
            self.main_algorithm = algo_sections[0]
            header_info = parse_algorithm_header(self.main_algorithm["header"])
            self.main_algorithm["header_info"] = header_info
            # Save the rest of the algorithms in the dictionary if they have a name
            for alg in algo_sections[1:]:
                info = parse_algorithm_header(alg["header"])
                alg["header_info"] = info
                if info["name"]:
                    self.algorithms[info["name"]] = alg
        else:
            raise Exception("No algorithms in the program.")

    def execute_introduction(self):
        """Executes the introduction (commands before the first algorithm)."""
        for line in self.introduction:
            execute_line(line, self.env, self.robot)

    def execute_algorithm(self, algorithm):
        """Executes the body of an algorithm (the lines between 'нач' and 'кон')."""
        for line in algorithm["body"]:
            execute_line(line, self.env, self.robot)

    def interpret(self):
        """Full interpretation of the program: parsing, executing the introduction, and the main algorithm."""
        self.parse()
        self.execute_introduction()
        print("Выполнение основного алгоритма:")
        self.execute_algorithm(self.main_algorithm)
        # Return the updated environment, robot position, and list of painted cells
        return {
            "env": self.env,
            "robot": self.robot.robot_pos,
            "coloredCells": list(self.robot.colored_cells)
        }


# Example usage (if run directly)
if __name__ == "__main__":
    sample_code = r'''
    | Это вступление
    цел длина, ширина, лог условие, лит мой текст
    длина := 10
    ширина := 15
    условие := да
    мой текст := "Пример текста"
    вывод "Вступление выполнено. Текст: " + мой текст

    | Это основной алгоритм (без имени)
    алг
    нач
      вывод "Площадь равна: " + (длина * ширина)
      вправо
      вниз
      вправо
      закрасить
    кон

    | Это вспомогательный алгоритм (пока не вызывается)
    алг цел площадь
    нач
      знач := длина * ширина
      вывод "Вспомогательный алгоритм: Площадь = " + знач
    кон
    '''
    interpreter = KumirLanguageInterpreter(sample_code)
    result = interpreter.interpret()
    print("Результат:", result)
