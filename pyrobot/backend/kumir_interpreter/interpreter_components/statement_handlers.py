from typing import TYPE_CHECKING, Any, Optional, Tuple, List, Dict
from antlr4 import ParserRuleContext, Token
from antlr4.tree.Tree import TerminalNode

# Импортируем ТОЛЬКО KumirParser. Контексты будут доступны через него.
from ..generated.KumirParser import KumirParser
# Исправляем путь к KumirParserVisitor
from ..generated.KumirParserVisitor import KumirParserVisitor as KumirVisitor

from ..kumir_exceptions import (
    BreakException, ContinueException, DeclarationError, KumirTypeError,
    KumirArgumentError
)


class StatementHandlerMixin(KumirVisitor):  # Используем KumirVisitor
    def __init__(self, interpreter_variables, output_buffer, input_buffer_handler):
        super().__init__()
        self.variables = interpreter_variables
        self.output_buffer = output_buffer
        self.input_buffer_handler = input_buffer_handler

    # оператор присваивания
    # Аннотацию типа оставляем KumirParser.AssignmentStatementContext, т.к. контексты определены в KumirParser.py
    def visitAssignmentStatement(self, ctx: KumirParser.AssignmentStatementContext):
        var_name_ctx = ctx.lvalue().qualifiedIdentifier()
        var_name = var_name_ctx.getText()
        
        if not self.variables.exists(var_name):
            pass 

        value_ctx = ctx.expression()
        value = self.visit(value_ctx)

        current_var_info = self.variables.get_variable(var_name)
        if current_var_info and current_var_info.type is not None:
            if current_var_info.type == 'цел' and not isinstance(value, int):
                try:
                    value = int(value)
                except ValueError:
                    raise KumirTypeError(f"Невозможно привести значение '{value}' к типу 'цел' для переменной '{var_name}'", ctx.start.line, ctx.start.column)
            elif current_var_info.type == 'вещ' and not isinstance(value, float):
                try:
                    value = float(value)
                except ValueError:
                    raise KumirTypeError(f"Невозможно привести значение '{value}' к типу 'вещ' для переменной '{var_name}'", ctx.start.line, ctx.start.column)
            elif current_var_info.type == 'лог' and not isinstance(value, bool):
                raise KumirTypeError(f"Несовместимость типов для '{var_name}'. Ожидался 'лог', получен '{type(value)}'", ctx.start.line, ctx.start.column)
            elif current_var_info.type == 'сим' and not isinstance(value, str): 
                if not (isinstance(value, str) and len(value) == 1):
                    raise KumirTypeError(f"Несовместимость типов для '{var_name}'. Ожидался 'сим', получен '{type(value)}' со значением '{value}'", ctx.start.line, ctx.start.column)
            elif current_var_info.type == 'лит' and not isinstance(value, str):
                 raise KumirTypeError(f"Несовместимость типов для '{var_name}'. Ожидался 'лит', получен '{type(value)}'", ctx.start.line, ctx.start.column)

        self.variables.set_variable(var_name, value, type(value).__name__)
        return value

    # объявление переменной
    # Аннотацию типа оставляем KumirParser.VariableDeclarationStatementContext
    def visitVariableDeclarationStatement(self, ctx: KumirParser.VariableDeclarationStatementContext):
        var_type_ctx = ctx.variableDeclaration().type_()
        if var_type_ctx is None:
            raise SyntaxError("Тип переменной не указан в объявлении.")

        var_type_str = var_type_ctx.getText()

        for var_decl in ctx.variableDeclaration().variableDeclarationEntry():
            var_name = var_decl.qualifiedIdentifier().getText()
            if self.variables.exists(var_name):
                raise DeclarationError(f"Переменная '{var_name}' уже объявлена.", var_decl.start.line, var_decl.start.column)

            initial_value = None
            if var_decl.expression():
                initial_value_ctx = var_decl.expression()
                initial_value = self.visit(initial_value_ctx)
                if var_type_str == 'цел' and not isinstance(initial_value, int):
                    try:
                        initial_value = int(initial_value)
                    except ValueError:
                        raise KumirTypeError(f"Невозможно привести инициализирующее значение '{initial_value}' к типу 'цел' для переменной '{var_name}'", var_decl.start.line, var_decl.start.column)
                elif var_type_str == 'вещ' and not isinstance(initial_value, float):
                    try:
                        initial_value = float(initial_value)
                    except ValueError:
                        raise KumirTypeError(f"Невозможно привести инициализирующее значение '{initial_value}' к типу 'вещ' для переменной '{var_name}'", var_decl.start.line, var_decl.start.column)
                elif var_type_str == 'лог' and not isinstance(initial_value, bool):
                     raise KumirTypeError(f"Несовместимость типов при инициализации '{var_name}'. Ожидался 'лог', получен '{type(initial_value)}'", var_decl.start.line, var_decl.start.column)
                elif var_type_str == 'сим':
                    if not (isinstance(initial_value, str) and len(initial_value) == 1):
                        raise KumirTypeError(f"Несовместимость типов при инициализации '{var_name}'. Ожидался 'сим' (строка длины 1), получен '{type(initial_value)}' со значением '{initial_value}'", var_decl.start.line, var_decl.start.column)
                elif var_type_str == 'лит' and not isinstance(initial_value, str):
                    raise KumirTypeError(f"Несовместимость типов при инициализации '{var_name}'. Ожидался 'лит', получен '{type(initial_value)}'", var_decl.start.line, var_decl.start.column)
            else:
                if var_type_str == 'цел':
                    initial_value = 0
                elif var_type_str == 'вещ':
                    initial_value = 0.0
                elif var_type_str == 'лог':
                    initial_value = False
                elif var_type_str == 'сим':
                    initial_value = ' '
                elif var_type_str == 'лит':
                    initial_value = ""
            self.variables.declare_variable(var_name, var_type_str, initial_value)
        return None # Объявление переменных обычно не возвращает значение

