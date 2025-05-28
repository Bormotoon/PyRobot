# Visitor methods for general statements (assignment, I/O calls, etc.)

import sys
from typing import Any, List, Dict, Optional
from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import KumirRuntimeError, KumirTypeError
from ..kumir_datatypes import KumirType

class StatementVisitorMixin:
    def visitIoStatement(self, ctx: KumirParser.IoStatementContext) -> None:
        """Обработка операторов ВВОД и ВЫВОД"""
        print(f"\n!!! [DEBUG statement_visitors.visitIoStatement] CALLED! Context: {ctx.getText()} !!!", file=sys.stderr)
        print(f"!!! [DEBUG] Current class: {self.__class__.__name__} !!!", file=sys.stderr)
        if ctx.OUTPUT():
            # Обработка аргументов вывода
            current_output = ""
            for i, arg_ctx in enumerate(ctx.ioArgumentList().ioArgument()):
                if arg_ctx.expression(): # Вывод выражения
                    expressions = arg_ctx.expression()
                    # expression() может вернуть список выражений, берем первое
                    first_expression = expressions[0] if isinstance(expressions, list) else expressions
                    print(f"!!! [DEBUG] About to evaluate expression: {first_expression.getText()} !!!", file=sys.stderr)
                    value_to_print = self.expression_evaluator.visit(first_expression)
                    if value_to_print is None:
                        raise KumirRuntimeError(
                            f"Не удалось вычислить значение для вывода аргумента {i+1} процедуры ВЫВОД.",
                            line_index=arg_ctx.start.line -1,
                            column_index=arg_ctx.start.column
                        )
                      # Отладочный вывод для диагностики
                    print(f"!!! [DEBUG] value_to_print.kumir_type = {value_to_print.kumir_type}, type = {type(value_to_print.kumir_type)} !!!", file=sys.stderr)
                    print(f"!!! [DEBUG] value_to_print.value = {repr(value_to_print.value)} !!!", file=sys.stderr)
                    print(f"!!! [DEBUG] value_to_print object = {value_to_print} !!!", file=sys.stderr)
                      # Преобразование значения к строке с учетом типа
                    if value_to_print.kumir_type == KumirType.INT.value:
                        current_output += str(value_to_print.value)
                    elif value_to_print.kumir_type == KumirType.REAL.value:
                        current_output += str(value_to_print.value)
                    elif value_to_print.kumir_type == KumirType.BOOL.value:
                        current_output += "истина" if value_to_print.value else "ложь"
                    elif value_to_print.kumir_type == KumirType.CHAR.value:
                        current_output += value_to_print.value # Символы выводим как есть                    elif value_to_print.kumir_type == KumirType.STR.value:
                        # Строки выводим без кавычек (в отличие от старой реализации)
                        current_output += value_to_print.value
                    elif value_to_print.kumir_type == "NEWLINE_CONST":
                        # 'нс' - не выводим ничего, но это сигнал для подавления автоматического перевода строки
                        pass # value.value уже пустая строка
                    else:
                        raise KumirTypeError(
                            f"Неизвестный тип значения для вывода: {value_to_print.kumir_type}",
                            line_index=arg_ctx.start.line -1,
                            column_index=arg_ctx.start.column
                        )
                else:
                    # Это литерал (например, строка) или управляющая команда (нс и др.)
                    io_val = arg_ctx.getText()
                    if io_val.startswith('"') and io_val.endswith('"'):
                        # Литерал строки, убираем кавычки
                        current_output += io_val[1:-1]
                    elif io_val.lower() == "нс":
                        # Команда 'нс' - отменяем будущий перенос строки
                        pass # Мы не добавляем \n в current_output
                    elif io_val.lower() == "переход": # Пример другой команды
                        current_output += "\n" 
                    # Можно добавить другие команды            # После обработки всех аргументов, если последний не был 'нс', добавляем перенос строки
            io_args = ctx.ioArgumentList().ioArgument()
            if not (io_args and io_args[-1].getText().lower() == 'нс'):
                current_output += '\n'
            
            print(f"[DEBUG statement_visitors.visitIoStatement] About to call io_handler.write_output. current_output length: {len(current_output)}. current_output: >>>{current_output}<<<", file=sys.stderr)
            self.io_handler.write_output(current_output)

        elif ctx.INPUT():
            # TODO: Реализовать логику для ВВОД
            raise KumirRuntimeError(
                "Операция ВВОД пока не реализована",
                line_index=ctx.start.line - 1,
                column_index=ctx.start.column
            )