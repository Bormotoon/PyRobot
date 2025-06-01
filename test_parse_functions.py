#!/usr/bin/env python3
"""
Тест парсинга функций и процедур из файла КуМир
"""

from antlr4 import InputStream, CommonTokenStream
from pyrobot.backend.kumir_interpreter.generated.KumirLexer import KumirLexer
from pyrobot.backend.kumir_interpreter.generated.KumirParser import KumirParser
from pyrobot.backend.kumir_interpreter.interpreter_components.main_visitor import KumirInterpreterVisitor

def test_parse_functions_file():
    print("🧪 Тестирую парсинг файла с функциями...")
    
    # Читаем файл с кодом КуМир
    with open("test_functions.kum", "r", encoding="utf-8") as f:
        code = f.read()
    
    print(f"📄 Код для разбора:\n{code}")
    
    # Создаем лексер и парсер
    input_stream = InputStream(code)
    lexer = KumirLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = KumirParser(token_stream)
    
    # Разбираем программу
    tree = parser.program()
      # Создаем интерпретатор
    with open("test_functions.kum", "r", encoding="utf-8") as f:
        program_lines = f.readlines()
    
    interpreter = KumirInterpreterVisitor(program_lines=program_lines)
    
    print("🔍 Запускаю первый проход (сбор определений)...")
    
    # Запускаем первый проход для сбора определений (без выполнения тел алгоритмов)
    try:
        interpreter.collect_definitions_only(tree)
        print("✅ Первый проход завершен успешно!")
        
        # Проверяем, что алгоритмы зарегистрированы
        all_algorithms = interpreter.algorithm_manager.get_all_algorithms()
        print(f"📊 Найдено алгоритмов: {len(all_algorithms)}")
        
        for algo in all_algorithms:
            print(f"   - {algo.name} ({'функция' if algo.is_function else 'процедура'})")
            if algo.parameters:
                for param in algo.parameters:
                    print(f"     * {param.name}: {param.param_type} ({param.mode})")
            if algo.return_type:
                print(f"     → возвращает: {algo.return_type}")
        
        # Проверяем конкретные функции
        suma_func = interpreter.algorithm_manager.get_algorithm("сумма")
        if suma_func:
            print(f"✅ Функция 'сумма' найдена: {suma_func.is_function}")
            print(f"   Параметры: {len(suma_func.parameters)}")
            print(f"   Тип возврата: {suma_func.return_type}")
        else:
            print("❌ Функция 'сумма' не найдена")
        
        output_proc = interpreter.algorithm_manager.get_algorithm("вывести_сумму")
        if output_proc:
            print(f"✅ Процедура 'вывести_сумму' найдена: {output_proc.is_procedure}")
            print(f"   Параметры: {len(output_proc.parameters)}")
        else:
            print("❌ Процедура 'вывести_сумму' не найдена")
            
    except Exception as e:
        print(f"❌ Ошибка при разборе: {e}")
        import traceback
        traceback.print_exc()
    
    print("🎉 Тест завершен!")

if __name__ == "__main__":
    test_parse_functions_file()
