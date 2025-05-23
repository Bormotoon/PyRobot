# Utility functions for type checking, conversion, and validation 

from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

# Assuming KumirParser is in pyrobot.backend.kumir_interpreter.generated
from ..generated.KumirParser import KumirParser
from ..kumir_exceptions import DeclarationError

if TYPE_CHECKING:
    # Assuming interpreter is in pyrobot.backend.kumir_interpreter
    from ..interpreter import KumirInterpreterVisitor

def get_type_info_from_specifier(
    visitor: KumirInterpreterVisitor,
    type_spec_ctx: KumirParser.TypeSpecifierContext
) -> Tuple[str, bool]:
    """
    Определяет базовый тип КуМир и является ли он таблицей на основе TypeSpecifierContext.

    Args:
        visitor: Экземпляр KumirInterpreterVisitor для доступа к TYPE_MAP, константам и get_line_content_from_ctx.
        type_spec_ctx: Узел TypeSpecifierContext из дерева разбора ANTLR.

    Returns:
        Кортеж (base_kumir_type: str, is_table_type: bool).

    Raises:
        DeclarationError: Если тип не может быть определен или он неизвестен.
    """
    base_kumir_type = None
    is_table_type = False

    # Доступ к константам и картам через visitor, который их содержит или импортирует
    TYPE_MAP = visitor.TYPE_MAP
    INTEGER_TYPE = visitor.INTEGER_TYPE
    FLOAT_TYPE = visitor.FLOAT_TYPE
    BOOLEAN_TYPE = visitor.BOOLEAN_TYPE
    CHAR_TYPE = visitor.CHAR_TYPE
    STRING_TYPE = visitor.STRING_TYPE
    # ACTOR_TYPE = visitor.ACTOR_TYPE # Если такая константа есть у visitor

    specific_error_ctx = type_spec_ctx # Контекст по умолчанию для сообщения об ошибке

    if type_spec_ctx.basicType():
        specific_error_ctx = type_spec_ctx.basicType()
        type_token = specific_error_ctx.start # type: ignore
        base_kumir_type = TYPE_MAP.get(type_token.type)
        if not base_kumir_type:
            lc = visitor.get_line_content_from_ctx(specific_error_ctx)
            raise DeclarationError(
                f"Строка {type_token.line}: Неизвестный базовый тип: {type_token.text}",
                line_index=type_token.line - 1, column_index=type_token.column, line_content=lc
            )
        is_table_type = bool(type_spec_ctx.TABLE_SUFFIX())
    elif type_spec_ctx.arrayType():
        specific_error_ctx = type_spec_ctx.arrayType()
        is_table_type = True
        # Проверяем, какой конкретно тип массива указан
        if specific_error_ctx.INTEGER_ARRAY_TYPE(): base_kumir_type = INTEGER_TYPE
        elif specific_error_ctx.REAL_ARRAY_TYPE(): base_kumir_type = FLOAT_TYPE
        elif specific_error_ctx.BOOLEAN_ARRAY_TYPE(): base_kumir_type = BOOLEAN_TYPE
        elif specific_error_ctx.CHAR_ARRAY_TYPE(): base_kumir_type = CHAR_TYPE
        elif specific_error_ctx.STRING_ARRAY_TYPE(): base_kumir_type = STRING_TYPE
        else:
            lc = visitor.get_line_content_from_ctx(specific_error_ctx)
            raise DeclarationError(
                f"Строка {specific_error_ctx.start.line}: Неизвестный тип таблицы (в arrayType): {specific_error_ctx.getText()}", # type: ignore
                line_index=specific_error_ctx.start.line - 1, column_index=specific_error_ctx.start.column, line_content=lc # type: ignore
            )
    elif type_spec_ctx.actorType():
        specific_error_ctx = type_spec_ctx.actorType()
        lc = visitor.get_line_content_from_ctx(specific_error_ctx)
        raise DeclarationError(
            f"Строка {specific_error_ctx.start.line}: Типы исполнителей ('{specific_error_ctx.getText()}') не могут быть использованы в этом контексте.", # type: ignore
            line_index=specific_error_ctx.start.line - 1, column_index=specific_error_ctx.start.column, line_content=lc # type: ignore
        )
    else:
        # specific_error_ctx остается type_spec_ctx
        lc = visitor.get_line_content_from_ctx(specific_error_ctx)
        raise DeclarationError(
            f"Строка {specific_error_ctx.start.line}: Не удалось определить тип из typeSpecifier: {specific_error_ctx.getText()}", # type: ignore
            line_index=specific_error_ctx.start.line - 1, column_index=specific_error_ctx.start.column, line_content=lc # type: ignore
        )

    if not base_kumir_type: # Дополнительная проверка на всякий случай
        lc = visitor.get_line_content_from_ctx(type_spec_ctx) # Используем оригинальный ctx для этой общей ошибки
        raise DeclarationError(
            f"Строка {type_spec_ctx.start.line}: Не удалось определить базовый тип для: {type_spec_ctx.getText()}", # type: ignore
            line_index=type_spec_ctx.start.line - 1, column_index=type_spec_ctx.start.column, line_content=lc # type: ignore
        )
    return base_kumir_type, is_table_type 