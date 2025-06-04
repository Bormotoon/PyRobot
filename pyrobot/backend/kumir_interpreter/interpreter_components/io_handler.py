# Functions for handling input and output operations
from typing import Callable, Optional
# Импортируем kumir_exceptions как модуль, чтобы передавать его
from .. import kumir_exceptions # Относительный импорт

class IOHandler:
    def __init__(self, kumir_exceptions_module, visitor = None, input_stream: Optional[Callable[[], str]] = None, output_stream: Optional[Callable[[str], None]] = None, error_stream: Optional[Callable[[str], None]] = None):
        self.kumir_exceptions = kumir_exceptions_module
        self.visitor = visitor
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.error_stream = error_stream # Добавляем error_stream
        # TODO: Implement input/output methods (ввод, вывод)
        print(f"[DEBUG IOHandler.__init__] Initialized. self.output_stream type: {type(self.output_stream)}, id: {id(self.output_stream)}, self.error_stream type: {type(self.error_stream)}", file=__import__('sys').stderr)

    def get_input_line(self, prompt: str) -> str:
        # Сначала выводим подсказку, если она есть и есть куда выводить
        if prompt and self.output_stream:
            self.output_stream(prompt)
        
        if self.input_stream:
            input_value = self.input_stream()
            return input_value
        else:
            # Если input_stream не предоставлен, можно либо вызвать исключение,
            # либо вернуть какое-то значение по умолчанию, либо запросить ввод через stdin.
            # Для тестов и CLI это может быть input().
            # print(f"[IOHandler DEBUG] input_stream is None, falling back to input(). Prompt: {prompt}", file=__import__('sys').stderr)
            try:
                input_value = input(prompt if not self.output_stream else "") # Если prompt уже вывели, не дублируем
                return input_value
            except EOFError:
                # print("[IOHandler DEBUG] EOFError during input()", file=__import__('sys').stderr)
                # В случае EOF (например, если ввод перенаправлен из пустого файла)
                # можно вернуть пустую строку или вызвать специфическое исключение КуМира.
                # Пока вернем пустую строку, как это часто делают REPL.
                return ""
            except RuntimeError as e:
                # print(f"[IOHandler DEBUG] RuntimeError during input(): {e}", file=__import__('sys').stderr)
                # Это может случиться, если stdin не доступен (например, в некоторых средах без консоли)
                # TODO: Решить, какое исключение КуМир должно быть здесь. InputOutputError?
                raise self.kumir_exceptions.InputOutputError(
                    f"Ошибка при попытке чтения ввода: {e}",
                    # line_index, column_index, line_content можно будет получить из visitor, если нужно
                )

    def write_output(self, text: str) -> None:
        """Записывает текст в выходной поток."""
        print(f"[DEBUG IOHandler.write_output] CALLED. Text length: {len(text)}. Text: >>>{text}<<<", file=__import__('sys').stderr)
        try:
            if self.output_stream:
                self.output_stream(text) # Просто вызываем output_stream как функцию
            # flush здесь не нужен, если output_stream - это, например, print или sys.stdout.write, 
            # которые обычно буферизуются по строкам или принудительно сбрасываются при \n.
            # Если бы мы использовали файловый объект, flush был бы актуален.
        except Exception as e:
            # print(f"[IOHandler DEBUG] Exception during write_output: {e}", file=__import__('sys').stderr)
            # Если произошла ошибка при записи, можно вызвать специфическое исключение КуМира.
            raise self.kumir_exceptions.OutputError(
                f"Ошибка при попытке записи вывода: {e}",
                # Дополнительные параметры ошибки можно передать при необходимости
            )

    def show_message(self, message: str) -> None:
        """Отображает сообщение пользователю (например, для команды ПАУЗА)."""
        # Пока что просто выводим в output_stream или stdout
        self.write_output(message + "\n") # Добавляем перевод строки для сообщений

    def show_message_and_wait(self, message: str) -> None:
        """Отображает сообщение и ждет реакции пользователя (например, Enter)."""
        self.show_message(message)
        self.get_input_line("") # Просто ждем Enter, подсказка не нужна или уже в message

    def set_echo_input(self, echo: bool):
        """Включает или отключает эхо ввода (по умолчанию включено)."""
        self.echo_input = echo
        if not echo:
            # Если эхо отключено, можно очистить буфер ввода, если нужно
            # Но это зависит от конкретной реализации ввода
            pass
        print(f"[DEBUG IOHandler.set_echo_input] Echo input set to {echo}.", file=__import__('sys').stderr)

    def set_visitor(self, visitor):
        """Устанавливает visitor после инициализации IOHandler."""
        self.visitor = visitor
        print(f"[DEBUG IOHandler.set_visitor] Visitor set in IOHandler.", file=__import__('sys').stderr)