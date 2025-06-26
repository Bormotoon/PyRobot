# 📝 Грамматики КуМир для ANTLR v4

Этот каталог содержит грамматики ANTLR v4 (лексер и парсер) для языка программирования КуМир. КуМир — российский алгоритмический язык, используемый в основном для обучения программированию в школах.

## 🎯 Поддерживаемые языковые возможности

### 🔧 Основные элементы языка

- **Ключевые слова**: `алг`, `нач`, `кон`, `если`, `то`, `иначе`, `все`, `нц`, `кц`, `для`, `пока` и др.
- **Типы данных**: `цел`, `вещ`, `лог`, `сим`, `лит` и табличные типы (`целтаб`, `вещтаб` и др.)
- **Исполнители**: `файл`, `цвет`, `Робот` (другие могут быть добавлены при необходимости)
- **Переменные**: объявление переменных (включая инициализацию с `=`)
- **Присваивание**: `:=` включая присваивание результата функции (`знач := ...`)

### 🔄 Выражения и операторы

- **Арифметические**: `+`, `-`, `*`, `/`, `div`, `mod`, `**`
- **Логические**: `и`, `или`, `не`
- **Сравнения**: `=`, `<>`, `<`, `>`, `<=`, `>=`
- **Приоритет операций**: соответствует стандарту КуМир

### 🎮 Управляющие конструкции

- **Условные операторы**: `если-то-иначе-все`, `выбор-при-иначе-все`
- **Циклы**: 
  - `нц для ... от ... до ... [шаг ...]` (цикл "для")
  - `нц пока ...` (цикл "пока")
  - `нц ... раз` (цикл "N раз")
  - `нц ... кц` (простой цикл)

### 🔧 Алгоритмы и модули

- **Процедуры и функции**: включая параметры (`арг`, `рез`, `аргрез`)
- **Имена алгоритмов**: поддержка многословных имен, включая содержащие числа или ключевые слова
- **Модульная структура**: `использовать`, `модуль`, `конец модуля`
- **Комментарии**: поддержка `|` и `#`

### 📚 Литералы и константы

- **Числа**: целые, вещественные
- **Строки**: в кавычках с поддержкой escape-последовательностей
- **Символы**: одиночные символы в апострофах
- **Логические**: `да`/`нет`
- **Массивы**: литералы массивов `{...}`
- **Цвета**: константы цветов

## 📁 Файлы грамматик

### `KumirLexer.g4`

Определяет токены для языка КуМир:

- **Кодировка**: UTF-8 без BOM (рекомендуется)
- **Регистронезависимость**: для кириллических ключевых слов
- **Литералы**: числа, строки, символы, логические значения
- **Операторы**: арифметические, логические, сравнения
- **Разделители**: пробелы, переводы строк, комментарии

### `KumirParser.g4`

Определяет правила парсинга на основе токенов лексера:

- **tokenVocab**: использует токены из `KumirLexer`
- **algorithmNameTokens**: обработка сложных имен алгоритмов
- **Структура программы**: алгоритмы, модули, вступление
- **Выражения**: с правильными приоритетами операций
- **Операторы**: все управляющие конструкции КуМир

## 🔧 Интеграция с PyRobot

### Генерация парсера

```bash
# Генерация Python классов из грамматик
antlr4 -Dlanguage=Python3 KumirLexer.g4
antlr4 -Dlanguage=Python3 KumirParser.g4

# Файлы будут созданы:
# - KumirLexer.py
# - KumirParser.py
# - KumirLexer.tokens
# - KumirParser.tokens
```

### Использование в коде

```python
from antlr4 import *
from KumirLexer import KumirLexer
from KumirParser import KumirParser

def parse_kumir_code(code: str):
    # Создание потока символов
    input_stream = InputStream(code)
    
    # Лексический анализ
    lexer = KumirLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    
    # Синтаксический анализ
    parser = KumirParser(token_stream)
    tree = parser.program()  # Начальное правило
    
    return tree
```

## 📋 Примеры программ

### Простая программа

```kumir
алг
нач
    цел a, b, сумма
    ввод a, b
    сумма := a + b
    вывод "Сумма:", сумма
кон
```

### Программа с функцией

```kumir
алг цел факториал(цел n)
нач
    если n <= 1
    то
        знач := 1
    иначе
        знач := n * факториал(n - 1)
    все
кон

алг
нач
    цел число, результат
    ввод число
    результат := факториал(число)
    вывод результат
кон
```

### Программа с Роботом

```kumir
использовать Робот
алг
нач
    нц 4 раза
        вправо
        закрасить
    кц
кон
```

## 🧪 Тестирование грамматик

### Валидация синтаксиса

```python
def validate_kumir_syntax(code: str) -> bool:
    try:
        tree = parse_kumir_code(code)
        return tree is not None
    except Exception:
        return False

# Тестовые случаи
test_cases = [
    "алг\nнач\nкон",  # Минимальная программа
    "алг\nнач\n    цел x := 5\nкон",  # С переменной
    "алг\nнач\n    нц 5 раз\n        вывод \"привет\"\n    кц\nкон"  # С циклом
]

for i, code in enumerate(test_cases):
    result = validate_kumir_syntax(code)
    print(f"Тест {i+1}: {'✅' if result else '❌'}")
```

### Проверка токенизации

```python
def tokenize_kumir(code: str):
    input_stream = InputStream(code)
    lexer = KumirLexer(input_stream)
    tokens = []
    
    while True:
        token = lexer.nextToken()
        if token.type == Token.EOF:
            break
        tokens.append((token.text, lexer.symbolicNames[token.type]))
    
    return tokens

# Пример использования
tokens = tokenize_kumir("алг\nнач\n    цел x := 5\nкон")
for text, type_name in tokens:
    print(f"{text:10} -> {type_name}")
```

## 🔧 Настройка и конфигурация

### Параметры лексера

- **Чувствительность к регистру**: Кириллические ключевые слова регистронезависимы
- **Пропуск символов**: Пробелы, табуляции, переводы строк
- **Комментарии**: Автоматически пропускаются

### Обработка ошибок

```python
class KumirErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_msg = f"Синтаксическая ошибка в строке {line}:{column} - {msg}"
        raise SyntaxError(error_msg)

# Использование
parser.addErrorListener(KumirErrorListener())
```

## 📚 Дополнительные ресурсы

### Документация КуМир

- **[Официальная документация КуМир](http://www.niisi.ru/kumir/)**
- **[Примеры программ](examples/)** - готовые программы для тестирования
- **[Спецификация языка](desc.xml)** - XML описание языка

### ANTLR ресурсы

- **[ANTLR4 Documentation](https://github.com/antlr/antlr4/blob/master/doc/index.md)**
- **[Grammar Repository](https://github.com/antlr/grammars-v4)**
- **[Python Target](https://github.com/antlr/antlr4/blob/master/doc/python-target.md)**

## 🚀 Планы развития

### Краткосрочные улучшения

- ✅ **Поддержка всех операторов** - завершено
- ✅ **Многословные имена** - реализовано  
- 🔄 **Улучшенная обработка ошибок** - в разработке
- 📝 **Документирующие комментарии** - планируется

### Долгосрочные цели

- 🎯 **Семантический анализ** - типизированное AST
- 🔧 **IDE поддержка** - Language Server Protocol
- 📊 **Статический анализ** - поиск потенциальных ошибок
- 🌐 **Web playground** - онлайн редактор с подсветкой

---

**Грамматики ANTLR обеспечивают надежную основу для парсинга языка КуМир в PyRobot!** 📝

* `desc.xml`: This file is provided for integration with the `antlr/grammars-v4` testing infrastructure. It specifies Python 3 as the target language for this grammar and points to the example files located in the `examples/` directory.

## Origin and Testing

The grammar was developed based on:

1. Official Kumir documentation (DocBook XML format).
2. Extensive iterative testing against a suite of 60 example programs (from K.Y. Polyakov's collection).
3. Analysis of the behavior of the reference Kumir 2.1.0 IDE's parser/interpreter.
4. Collaborative refinement process.

The final version successfully parses all 60 provided test examples.

## Usage

These grammars are intended for use with the standard ANTLR v4 toolchain.

Target language example (Python 3):

```bash
antlr4 -Dlanguage=Python3 KumirLexer.g4 KumirParser.g4 -visitor -o output_dir