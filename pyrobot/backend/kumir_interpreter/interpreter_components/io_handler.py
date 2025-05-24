# Functions for handling input and output operations
from typing import Callable, Optional

class IOHandler:
    def __init__(self, visitor, input_stream: Optional[Callable[[], str]] = None, output_stream: Optional[Callable[[str], None]] = None):
        self.visitor = visitor
        self.input_stream = input_stream
        self.output_stream = output_stream
        # TODO: Implement input/output methods (ввод, вывод)

    def get_input_line(self, prompt: str) -> str:
        # Сначала выводим подсказку, если она есть и есть куда выводить
        if prompt and self.output_stream:
            self.output_stream(prompt)
        
        if self.input_stream:
            return self.input_stream()
        else:
            # Если input_stream не предоставлен, можно либо вызвать исключение,
            # либо вернуть какое-то значение по умолчанию, либо запросить ввод через stdin.
            # Для тестов и CLI это может быть input().
            # print(f"[IOHandler DEBUG] input_stream is None, falling back to input(). Prompt: {prompt}", file=__import__('sys').stderr)
            try:
                return input(prompt if not self.output_stream else "") # Если prompt уже вывели, не дублируем
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
                raise self.visitor.kumir_exceptions.InputOutputError(
                    f"Ошибка при попытке чтения ввода: {e}",
                    # line_index, column_index, line_content можно будет получить из visitor, если нужно
                )

    def write_output(self, text: str) -> None:
        if self.output_stream:
            self.output_stream(text)
        else:
            # Если output_stream не предоставлен, выводим в stdout.
            # print(f"[IOHandler DEBUG] output_stream is None, falling back to print(). Text: {text[:50]}...", file=__import__('sys').stderr)
            print(text, end='') # end='' чтобы имитировать потоковый вывод, если текст не содержит \\n
    def show_message(self, message: str) -> None:
        """Отображает сообщение пользователю (например, для команды ПАУЗА)."""
        # Пока что просто выводим в output_stream или stdout
        self.write_output(message + "\n") # Добавляем перевод строки для сообщений

    def show_message_and_wait(self, message: str) -> None:
        """Отображает сообщение и ждет реакции пользователя (например, Enter)."""
        self.show_message(message)
        self.get_input_line("") # Просто ждем Enter, подсказка не нужна или уже в message