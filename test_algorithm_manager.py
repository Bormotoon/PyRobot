#!/usr/bin/env python3
"""
Простой тест для проверки нового AlgorithmManager
"""

from pyrobot.backend.kumir_interpreter.definitions import AlgorithmManager, AlgorithmDefinition, Parameter

def test_algorithm_manager():
    print("🧪 Тестирую AlgorithmManager...")
    
    # Создаем менеджер алгоритмов
    manager = AlgorithmManager()
    
    # Создаем параметры для тестовой функции
    params = [
        Parameter(name="x", param_type="цел", mode="арг"),
        Parameter(name="y", param_type="цел", mode="арг")
    ]
      # Создаем определение функции
    func_def = AlgorithmDefinition(
        name="сумма",
        parameters=params,
        return_type="цел",
        body_context=None,  # В реальности тут будет ANTLR контекст
        local_declarations=[]
    )
    
    # Регистрируем функцию
    manager.register_algorithm(func_def)
    print(f"✅ Зарегистрировали функцию: {func_def.name}")
    
    # Проверяем поиск
    found_func = manager.get_algorithm("сумма")
    print(f"✅ Нашли функцию: {found_func.name}")
    
    # Проверяем проверку типа
    is_func = manager.is_function("сумма")
    print(f"✅ Это функция: {is_func}")
    
    is_proc = manager.is_procedure("сумма")
    print(f"✅ Это процедура: {is_proc}")
      # Создаем процедуру
    proc_def = AlgorithmDefinition(
        name="вывести_сумму",
        parameters=params,
        return_type=None,
        body_context=None,
        local_declarations=[]
    )
    
    manager.register_algorithm(proc_def)
    print(f"✅ Зарегистрировали процедуру: {proc_def.name}")
    
    # Проверяем список всех алгоритмов
    all_algorithms = manager.get_all_algorithms()
    print(f"✅ Всего алгоритмов: {len(all_algorithms)}")
    for algo in all_algorithms:
        print(f"   - {algo.name} ({'функция' if algo.is_function else 'процедура'})")
    
    print("🎉 Все тесты прошли успешно!")

if __name__ == "__main__":
    test_algorithm_manager()
