#!/usr/bin/env python3
"""
Простой тест для проверки текущего состояния интерпретатора.
"""

import sys
import os

# Добавляем путь к проекту в PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from pyrobot.backend.kumir_interpreter.interpreter_components.main_visitor import KumirInterpreterVisitor
    print("✓ Импорт KumirInterpreterVisitor успешен")
except ImportError as e:
    print(f"✗ Ошибка импорта KumirInterpreterVisitor: {e}")

try:
    from pyrobot.backend.kumir_interpreter.generated.KumirLexer import KumirLexer
    from pyrobot.backend.kumir_interpreter.generated.KumirParser import KumirParser
    print("✓ Импорт лексера и парсера успешен")
except ImportError as e:
    print(f"✗ Ошибка импорта лексера/парсера: {e}")

try:
    from antlr4 import InputStream, CommonTokenStream
    print("✓ Импорт ANTLR4 успешен")
except ImportError as e:
    print(f"✗ Ошибка импорта ANTLR4: {e}")

def test_simple_program():
    """Тестируем простую программу"""
    print("\n=== Тестируем программу ===")
      # Простая программа для тестирования
    code = """алг Оператор вывода
нач
    вывод '2+'
    вывод '2=?', нс
    вывод 'Ответ: 4'
кон"""
    
    try:
        # Создаем лексер и парсер
        input_stream = InputStream(code)
        lexer = KumirLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = KumirParser(token_stream)
        
        # Парсим программу
        tree = parser.program()
        print("✓ Парсинг программы успешен")        # Создаем visitor и выполняем
        visitor = KumirInterpreterVisitor()
        # Сначала парсим и регистрируем алгоритмы
        result = visitor.visit(tree)
        print("✓ Регистрация алгоритмов завершена")
        
        # Теперь выполняем главный алгоритм
        print("Запускаем алгоритм 'Операторвывода'...")
        visitor.execute_algorithm_node("Операторвывода")
        print("✓ Выполнение алгоритма завершено")
        
    except Exception as e:
        print(f"✗ Ошибка при выполнении программы: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_program()
