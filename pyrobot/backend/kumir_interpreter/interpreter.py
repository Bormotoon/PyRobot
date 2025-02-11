from .execution import execute_line
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header
from .robot_interpreter import KumirInterpreter


class KumirLanguageInterpreter:
    """
    Интерпретатор языка KUMIR.

    Обеспечивает полный цикл обработки исходного кода:
      - Предварительную обработку (удаление комментариев, разделение на вступление и алгоритмы).
      - Парсинг заголовков алгоритмов.
      - Выполнение вступительной части (команды до основного алгоритма).
      - Выполнение основного алгоритма.

    Атрибуты:
      code (str): Исходный код программы.
      env (dict): Окружение переменных, где ключи – имена переменных, а значения – словари с информацией:
                  {"type": ..., "value": ..., "kind": ..., "is_table": ...}.
      algorithms (dict): Словарь вспомогательных алгоритмов по имени.
      main_algorithm (dict): Основной алгоритм (первый из секций алгоритмов).
      robot (KumirInterpreter): Экземпляр интерпретатора робота, отвечающий за выполнение команд робота.
      output (str): Буфер для захвата вывода команды "вывод".
    """

    def __init__(self, code):
        """
        Инициализирует интерпретатор с заданным исходным кодом.

        Параметры:
          code (str): Исходный код программы на языке KUMIR.
        """
        self.code = code
        # Окружение для переменных: словарь, где каждый ключ – имя переменной,
        # а значение – словарь с типом, значением, областью видимости и флагом таблицы.
        self.env = {}
        self.algorithms = {}  # Словарь для хранения вспомогательных алгоритмов по имени
        self.main_algorithm = None  # Основной алгоритм (будет определён при парсинге)
        # Создаем экземпляр интерпретатора для управления роботом
        self.robot = KumirInterpreter()
        # Буфер для захвата вывода, осуществляемого через команду "вывод"
        self.output = ""

    def parse(self):
        """
        Обрабатывает исходный код: выполняет предварительную обработку, разделение на вступительную часть
        и секции алгоритмов, а также парсинг заголовков алгоритмов.

        Процесс:
          1. Удаляются комментарии и лишние пробелы (с помощью preprocess_code).
          2. Исходный код разделяется на вступление и алгоритмы (с помощью separate_sections).
          3. Первый найденный алгоритм считается основным, остальные сохраняются в словарь вспомогательных алгоритмов,
             если у них задано имя (парсинг заголовков производится с помощью parse_algorithm_header).

        Исключения:
          Генерируется Exception, если в программе отсутствуют алгоритмы.
        """
        # Предобработка исходного кода: удаление комментариев и лишних пробелов
        lines = preprocess_code(self.code)
        # Разделение кода на вступление и секции алгоритмов
        introduction, algo_sections = separate_sections(lines)
        self.introduction = introduction
        self.algo_sections = algo_sections

        if algo_sections:
            # Первый алгоритм считается основным
            self.main_algorithm = algo_sections[0]
            header_info = parse_algorithm_header(self.main_algorithm["header"])
            self.main_algorithm["header_info"] = header_info
            # Остальные алгоритмы сохраняются в словарь, если у них есть имя
            for alg in algo_sections[1:]:
                info = parse_algorithm_header(alg["header"])
                alg["header_info"] = info
                if info["name"]:
                    self.algorithms[info["name"]] = alg
        else:
            raise Exception("No algorithms in the program.")

    def execute_introduction(self):
        """
        Выполняет вступительную часть программы (команды, расположенные до первого алгоритма).

        Каждая строка вступления обрабатывается с помощью функции execute_line,
        которая обновляет окружение (env) и управляет роботом.
        """
        for line in self.introduction:
            execute_line(line, self.env, self.robot)

    def execute_algorithm(self, algorithm):
        """
        Выполняет тело алгоритма (строки между командами 'нач' и 'кон').

        Параметры:
          algorithm (dict): Секция алгоритма, содержащая ключ "body" с перечнем строк кода.
        """
        for line in algorithm["body"]:
            execute_line(line, self.env, self.robot)

    def interpret(self):
        """
        Полностью интерпретирует программу:
          1. Парсит исходный код.
          2. Выполняет вступительную часть.
          3. Выполняет основной алгоритм.

        После выполнения возвращает обновленное окружение, позицию робота и список закрашенных клеток.

        Возвращаемое значение:
          dict: Содержит ключи "env" (окружение переменных), "robot" (позиция робота)
                и "coloredCells" (список закрашенных клеток).
        """
        self.parse()
        self.execute_introduction()
        print("Выполнение основного алгоритма:")
        self.execute_algorithm(self.main_algorithm)
        # Возвращаем результаты выполнения
        return {"env": self.env, "robot": self.robot.robot_pos, "coloredCells": list(self.robot.colored_cells)}


# Пример использования (если модуль запущен напрямую)
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
    # Создаем интерпретатор с примером кода
    interpreter = KumirLanguageInterpreter(sample_code)
    # Интерпретируем код и получаем результат выполнения
    result = interpreter.interpret()
    print("Результат:", result)
