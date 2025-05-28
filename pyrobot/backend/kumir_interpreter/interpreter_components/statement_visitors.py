# Visitor methods for general statements (assignment, I/O calls, etc.)

import sys
from typing import Any, List, Dict, Optional, TYPE_CHECKING, cast
from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import KumirRuntimeError, KumirTypeError
from ..kumir_datatypes import KumirType

if TYPE_CHECKING:
    from .main_visitor import KumirInterpreterVisitor

class StatementVisitorMixin:
    def visitIoStatement(self, ctx: KumirParser.IoStatementContext) -> None:
        """Обработка операторов ВВОД и ВЫВОД"""
        kiv_self = cast('KumirInterpreterVisitor', self)
        
        if ctx.OUTPUT():
            # Обработка аргументов вывода
            current_output = ""
            for i, arg_ctx in enumerate(ctx.ioArgumentList().ioArgument()):
                if arg_ctx.expression(): # Вывод выражения
                    expressions = arg_ctx.expression()
                    # expression() может вернуть список выражений, берем первое
                    first_expression = expressions[0] if isinstance(expressions, list) else expressions
                    print(f"!!! [DEBUG] About to evaluate expression: {first_expression.getText()} !!!", file=sys.stderr)
                    value_to_print = kiv_self.expression_evaluator.visit(first_expression)
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
                    
                    # Дополнительная отладка для сравнения типов
                    print(f"!!! [DEBUG] Comparing: value_to_print.kumir_type ('{value_to_print.kumir_type}') with KumirType.STR.value ('{KumirType.STR.value}') !!!", file=sys.stderr)
                    print(f"!!! [DEBUG] Types: type(value_to_print.kumir_type) is {type(value_to_print.kumir_type)}, type(KumirType.STR.value) is {type(KumirType.STR.value)} !!!", file=sys.stderr)
                    print(f"!!! [DEBUG] Equality check (value_to_print.kumir_type == KumirType.STR.value): {value_to_print.kumir_type == KumirType.STR.value} !!!", file=sys.stderr)
                    print(f"!!! [DEBUG] Equality check (repr(value_to_print.kumir_type) == repr(KumirType.STR.value)): {repr(value_to_print.kumir_type) == repr(KumirType.STR.value)} !!!", file=sys.stderr)
                    print(f"!!! [DEBUG] KumirType.INT.value: '{KumirType.INT.value}', KumirType.REAL.value: '{KumirType.REAL.value}', KumirType.BOOL.value: '{KumirType.BOOL.value}', KumirType.CHAR.value: '{KumirType.CHAR.value}' !!!", file=sys.stderr)                    # Преобразование значения к строке с учетом типа
                    if value_to_print.kumir_type == KumirType.INT.value:
                        current_output += str(value_to_print.value)
                    elif value_to_print.kumir_type == KumirType.REAL.value:
                        current_output += str(value_to_print.value)
                    elif value_to_print.kumir_type == KumirType.BOOL.value:
                        current_output += "истина" if value_to_print.value else "ложь"
                    elif value_to_print.kumir_type == KumirType.CHAR.value:
                        current_output += value_to_print.value # Символы выводим как есть
                    elif value_to_print.kumir_type == KumirType.STR.value:
                        # Строки выводим без кавычек (в отличие от старой реализации)
                        current_output += value_to_print.value
                    elif value_to_print.kumir_type == "NEWLINE_CONST":
                        # 'нс' - добавляем перенос строки
                        current_output += "\n"
                    elif value_to_print.kumir_type == "ЛИТ":  # Дополнительная проверка на русский тип
                        current_output += value_to_print.value
                    else:                        raise KumirTypeError(
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
                        # Команда 'нс' добавляет перевод строки
                        current_output += "\n"
                    elif io_val.lower() == "переход": # Пример другой команды
                        current_output += "\n"
                    # Можно добавить другие команды
            
            # В КУМИР команда вывод НЕ добавляет автоматический перевод строки
            # Переводы строк добавляются только явно через 'нс'
            
            print(f"[DEBUG statement_visitors.visitIoStatement] About to call io_handler.write_output. current_output length: {len(current_output)}. current_output: >>>{current_output}<<<", file=sys.stderr)
            kiv_self.io_handler.write_output(current_output)

        elif ctx.INPUT():
            # Реализация операции ВВОД
            print(f"[DEBUG statement_visitors.visitIoStatement] Обработка оператора ВВОД", file=sys.stderr)
            
            # Получаем список аргументов (переменных для ввода)
            input_variables = []
            for arg_ctx in ctx.ioArgumentList().ioArgument():
                if arg_ctx.expression():
                    # Для ввода аргумент должен быть именем переменной (ID)
                    expressions = arg_ctx.expression()
                    # expression() может вернуть список выражений, берем первое
                    first_expression = expressions[0] if isinstance(expressions, list) else expressions
                    
                    # Проверяем, что это простое имя переменной
                    if hasattr(first_expression, 'getText'):
                        var_name = first_expression.getText().strip()
                        input_variables.append(var_name)
                        print(f"[DEBUG] Переменная для ввода: {var_name}", file=sys.stderr)
                    else:
                        raise KumirRuntimeError(
                            f"Неверный аргумент для ВВОД. Ожидается имя переменной.",
                            line_index=arg_ctx.start.line - 1,
                            column_index=arg_ctx.start.column
                        )
            
            if not input_variables:
                raise KumirRuntimeError(
                    "Оператор ВВОД должен содержать хотя бы одну переменную для ввода.",
                    line_index=ctx.start.line - 1,
                    column_index=ctx.start.column
                )            # Читаем значения - по одному из каждой строки
            values = []
            echo_output = ""  # Для сбора эхо-вывода
            
            for i in range(len(input_variables)):
                try:
                    input_str = kiv_self.io_handler.get_input_line("")
                    value = input_str.strip()
                    if value:
                        values.append(value)
                        print(f"[DEBUG] Прочитано значение {i+1}: '{value}'", file=sys.stderr)
                        
                        # Логика эхо-ввода (как в старом интерпретаторе)
                        if kiv_self.echo_input:
                            is_last_arg = (i == len(input_variables) - 1)
                            if is_last_arg:
                                echo_output += value + "\n"  # Последний аргумент с переносом строки
                            else:
                                echo_output += value + " "   # Не последний аргумент с пробелом
                    else:
                        raise ValueError("Пустая строка ввода")
                except Exception as e:
                    raise KumirRuntimeError(
                        f"Ошибка при чтении значения {i+1}: {e}",
                        line_index=ctx.start.line - 1,
                        column_index=ctx.start.column
                    )
            
            if len(values) != len(input_variables):
                raise KumirRuntimeError(
                    f"Количество прочитанных значений ({len(values)}) не совпадает с количеством переменных ({len(input_variables)}).",
                    line_index=ctx.start.line - 1,
                    column_index=ctx.start.column
                )
            
            # Выводим эхо введённых значений (если включено)
            if kiv_self.echo_input and echo_output:
                print(f"[DEBUG] Вывод эхо ввода: '{echo_output.rstrip()}'", file=sys.stderr)
                kiv_self.io_handler.write_output(echo_output)
            
            # Присваиваем значения переменным
            from ..kumir_datatypes import KumirValue
            for i, (var_name, value_str) in enumerate(zip(input_variables, values)):
                try:
                    # Получаем информацию о переменной для определения её типа
                    var_info, scope = kiv_self.scope_manager.find_variable(var_name)
                    if not var_info:
                        raise KumirRuntimeError(
                            f"Переменная '{var_name}' не найдена.",
                            line_index=ctx.start.line - 1,
                            column_index=ctx.start.column
                        )                    # Преобразуем строковое значение в соответствующий тип
                    target_type = var_info['kumir_type']
                    if target_type == KumirType.INT:
                        parsed_value = int(value_str)
                        kumir_value = KumirValue(parsed_value, KumirType.INT.value)
                    elif target_type == KumirType.REAL:
                        parsed_value = float(value_str)
                        kumir_value = KumirValue(parsed_value, KumirType.REAL.value)
                    elif target_type == KumirType.BOOL:
                        # Ожидаем "да"/"нет" или "истина"/"ложь"
                        if value_str.lower() in ["да", "истина", "true", "1"]:
                            parsed_value = True
                        elif value_str.lower() in ["нет", "ложь", "false", "0"]:
                            parsed_value = False
                        else:                            raise ValueError(f"Неверное логическое значение: {value_str}")
                        kumir_value = KumirValue(parsed_value, KumirType.BOOL.value)
                    elif target_type == KumirType.CHAR:
                        if len(value_str) != 1:
                            raise ValueError(f"Символьное значение должно содержать ровно один символ: {value_str}")
                        kumir_value = KumirValue(value_str, KumirType.CHAR.value)
                    elif target_type == KumirType.STR:
                        kumir_value = KumirValue(value_str, KumirType.STR.value)
                    else:
                        raise ValueError(f"Неподдерживаемый тип переменной: {target_type}")
                    
                    # Присваиваем значение переменной
                    kiv_self.scope_manager.update_variable(
                        var_name, 
                        kumir_value, 
                        line_index=ctx.start.line - 1,
                        column_index=ctx.start.column
                    )
                    print(f"[DEBUG] Присвоено {var_name} = {kumir_value.value} (тип: {kumir_value.kumir_type})", file=sys.stderr)
                    
                except ValueError as e:
                    raise KumirRuntimeError(
                        f"Ошибка преобразования значения '{value_str}' для переменной '{var_name}': {e}",
                        line_index=ctx.start.line - 1,
                        column_index=ctx.start.column
                    )