#!/usr/bin/env python3
"""
Отладочный скрипт для проверки парсинга цикла
"""

import sys
import os

# Добавляем пути к модулям проекта
sys.path.insert(0, os.path.dirname(__file__))

from antlr4 import *
from pyrobot.backend.kumir_interpreter.generated.KumirLexer import KumirLexer
from pyrobot.backend.kumir_interpreter.generated.KumirParser import KumirParser
from pyrobot.backend.kumir_interpreter.generated.KumirParserVisitor import KumirParserVisitor

class ParseTreePrinter(KumirParserVisitor):
    def __init__(self):
        self.indent = 0
    
    def visitChildren(self, node):
        print("  " * self.indent + f"Visiting: {type(node).__name__} - {node.getText()[:50]}...")
        self.indent += 1
        result = super().visitChildren(node)
        self.indent -= 1
        return result

def test_parsing():
    """Тестируем парсинг цикла"""
    
    # Простая программа с циклом
    program_text = """
алг Тест цикл downto
нач
цел n, k, M
M := 5
нц для k от M до 1 шаг -1
    вывод k
кц
кон
"""
    
    print("=== Тестируем парсинг цикла ===")
    print("Программа:")
    print(program_text)
    print("\n=== Парсинг ===")
    
    try:
        # Создаем лексер и парсер
        input_stream = InputStream(program_text)
        lexer = KumirLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = KumirParser(token_stream)
        
        # Парсим программу
        tree = parser.program()
        
        print("Дерево разбора:")
        printer = ParseTreePrinter()
        printer.visit(tree)
        
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parsing()
