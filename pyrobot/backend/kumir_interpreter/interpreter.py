# interpreter.py

from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .execution import execute_lines, execute_line, process_algorithm_call
from .robot_interpreter import KumirInterpreter


class KumirLanguageInterpreter:
    def __init__(self, code):
        self.code = code
        # Окружение для переменных: { var_name: {"type": ..., "value": ..., "kind": ..., "is_table": ...} }
        self.env = {}
        self.algorithms = {}  # Словарь для вспомогательных алгоритмов по имени
        self.main_algorithm = None
        # Создаем экземпляр исполнителя "Робот"
        self.robot = KumirInterpreter()
        # Буфер для захвата вывода команды "вывод"
        self.output = ""

    def parse(self):
        """
        Обрабатывает исходный код: удаление комментариев, разделение на вступление и алгоритмы,
        разбор заголовков алгоритмов.
        """
        lines = preprocess_code(self.code)
        introduction, algo_sections = separate_sections(lines)
        self.introduction = introduction
        self.algo_sections = algo_sections

        if algo_sections:
            # Первый алгоритм считается основным
            self.main_algorithm = algo_sections[0]
            header_info = parse_algorithm_header(self.main_algorithm["header"])
            self.main_algorithm["header_info"] = header_info
            # Остальные алгоритмы сохраняем в таблице, если они имеют имя
            for alg in algo_sections[1:]:
                info = parse_algorithm_header(alg["header"])
                alg["header_info"] = info
                if info["name"]:
                    self.algorithms[info["name"]] = alg
        else:
            raise Exception("Нет алгоритмов в программе.")

    def execute_introduction(self):
        """Исполняет вступление (команды до первого алгоритма)."""
        for line in self.introduction:
            execute_line(line, self.env, self.robot)

    def execute_algorithm(self, algorithm):
        """Исполняет тело алгоритма (строки между 'нач' и 'кон')."""
        for line in algorithm["body"]:
            execute_line(line, self.env, self.robot)

    def interpret(self):
        """Полная интерпретация программы: парсинг, исполнение вступления и основного алгоритма."""
        self.parse()
        self.execute_introduction()
        print("Выполнение основного алгоритма:")
        self.execute_algorithm(self.main_algorithm)
        # Возвращаем обновленное окружение, позицию робота и список закрашенных клеток
        return {
            "env": self.env,
            "robot": self.robot.robot_pos,
            "coloredCells": list(self.robot.colored_cells)
        }


# Пример использования (если запускается напрямую)
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
