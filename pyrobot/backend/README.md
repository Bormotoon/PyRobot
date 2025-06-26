# 🐍 PyRobot Backend

Backend компонент PyRobot - это Python-интерпретатор языка КуМир с веб-API и системой мониторинга.

## 📁 Структура

```text
backend/
├── server.py              # Flask/WebSocket сервер
├── monitoring.py          # Система мониторинга и логирования
├── kumir_interpreter/     # Ядро интерпретатора КуМир
│   ├── __init__.py
│   ├── runtime_utils.py   # Основные функции интерпретации
│   ├── safe_globals.py    # Безопасная среда выполнения
│   ├── builtin_functions.py  # Встроенные функции КуМир
│   ├── string_functions.py   # Строковые функции
│   ├── file_functions.py     # Файловые операции
│   └── robot_integration.py  # Интеграция с исполнителем Робот
└── kumir_sandbox/         # Песочница для безопасного выполнения
    ├── __init__.py
    └── security.py        # Система безопасности
```

## 🚀 Запуск

### Разработка

```bash
# Из корневой папки проекта
python -m pyrobot.backend.server

# Сервер запустится на http://localhost:5000
```

### Production

```bash
# С переменными окружения
export FLASK_ENV=production
export LOG_LEVEL=INFO
python -m pyrobot.backend.server
```

### Через VS Code Task

```bash
Ctrl/Cmd + Shift + P → "Tasks: Run Task" → "Start Backend"
```

## 🔧 API Endpoints

### 🏥 Health Check

```http
GET /health
# Возвращает: {"status": "ok", "timestamp": "..."}

GET /health/detailed  
# Возвращает: подробную информацию о системе

GET /metrics
# Возвращает: Prometheus-совместимые метрики
```

### 🎮 Интерпретация кода

```http
POST /api/interpret
Content-Type: application/json

{
    "code": "алг\nнач\n    вывод \"Привет!\"\nкон",
    "input_data": "",
    "robot_enabled": false
}
```

**Ответ:**
```json
{
    "success": true,
    "output": "Привет!",
    "error": null,
    "execution_time": 0.045,
    "robot_state": null
}
```

### 🤖 Команды Робота

```http
POST /api/robot/execute
Content-Type: application/json

{
    "command": "вправо",
    "robot_state": {...}
}
```

### 📊 WebSocket Events

Подключение: `ws://localhost:5000/socket.io/`

**События:**
- `execute_code` - выполнение программы
- `robot_command` - команда для робота
- `execution_result` - результат выполнения
- `robot_state_update` - обновление состояния робота

## 🛡️ Система безопасности

### Песочница выполнения

- **Ограниченные импорты**: Только безопасные модули
- **Контроль времени**: Таймаут выполнения программ
- **Изоляция памяти**: Ограничение использования RAM
- **Безопасные функции**: Только проверенные встроенные функции

### Встроенные функции

```python
# Математические функции
sin, cos, tan, ln, exp, sqrt, abs, min, max, rand

# Строковые функции  
длин, позиция, вставить, удалить, в_верхний_регистр

# Функции преобразования
цел_в_лит, лит_в_цел, вещ_в_лит, лит_в_вещ

# Системные функции
время, сущ, можно_откр_для_чт
```

## 📊 Мониторинг

### Логирование

```python
# Настройка в monitoring.py
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    }
}
```

### Метрики

- **Performance**: CPU, память, время ответа
- **Reliability**: Количество ошибок, uptime
- **Usage**: Количество запросов, активные сессии
- **Business**: Выполненные программы, популярные команды

### Health Checks

```python
# Простая проверка
GET /health

# Детальная проверка
GET /health/detailed
{
    "status": "healthy",
    "timestamp": "2025-06-26T10:30:00Z",
    "version": "1.0.0",
    "uptime": 3600,
    "system": {
        "cpu_percent": 15.2,
        "memory_percent": 45.8,
        "disk_percent": 23.1
    },
    "interpreter": {
        "test_execution": "ok",
        "builtin_functions": 47,
        "robot_commands": 17
    }
}
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
python -m pytest tests/ -v

# Только backend тесты
python -m pytest tests/test_polyakov_kum.py -v

# С покрытием кода
python -m pytest tests/ --cov=pyrobot.backend
```

### Тестовое покрытие

- **Интерпретатор**: 95%+ (56 тестов)
- **API endpoints**: 90%+
- **Робот команды**: 100%
- **Встроенные функции**: 95%+

## 🔧 Конфигурация

### Переменные окружения

```bash
# Основные настройки
FLASK_ENV=development|production
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Безопасность
EXECUTION_TIMEOUT=30          # Таймаут выполнения (сек)
MAX_MEMORY_MB=100            # Лимит памяти (МБ)
ALLOW_FILE_OPERATIONS=false  # Файловые операции

# Мониторинг
METRICS_ENABLED=true         # Включить метрики
HEALTH_CHECK_ENABLED=true    # Включить health checks
```

### Настройки в коде

```python
# В server.py
app.config.update({
    'SECRET_KEY': 'development-key',
    'TESTING': False,
    'DEBUG': False,
    'EXECUTION_TIMEOUT': 30,
    'MAX_MEMORY_MB': 100
})
```

## 🐛 Отладка

### Включение debug режима

```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
python -m pyrobot.backend.server
```

### Логи разработки

```python
# В runtime_utils.py добавлено логирование
import logging
logger = logging.getLogger(__name__)

def interpret_kumir(code, input_data="", robot=None):
    logger.debug(f"Интерпретация кода: {code[:100]}...")
    # ... выполнение
    logger.info(f"Код выполнен за {execution_time:.3f}s")
```

### Общие проблемы

1. **Ошибка импорта ANTLR**
   ```bash
   pip install antlr4-python3-runtime==4.13.1
   ```

2. **Проблемы с encoding**
   ```python
   # Убедитесь что файлы КуМир в UTF-8
   with open('program.kum', 'r', encoding='utf-8') as f:
       code = f.read()
   ```

3. **Timeout выполнения**
   ```bash
   # Увеличьте таймаут
   export EXECUTION_TIMEOUT=60
   ```

## 🚀 Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pyrobot/ pyrobot/
EXPOSE 5000

CMD ["python", "-m", "pyrobot.backend.server"]
```

### Systemd Service

```ini
[Unit]
Description=PyRobot Backend Server
After=network.target

[Service]
Type=simple
User=pyrobot
WorkingDirectory=/opt/pyrobot
Environment=FLASK_ENV=production
Environment=LOG_LEVEL=INFO
ExecStart=/opt/pyrobot/venv/bin/python -m pyrobot.backend.server
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Proxy

```nginx
server {
    listen 80;
    server_name pyrobot.school.edu;

    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io/ {
        proxy_pass http://localhost:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📈 Производительность

### Оптимизации

1. **AST кэширование**: Повторное использование парсенных деревьев
2. **Lazy loading**: Модули загружаются по требованию  
3. **Memory pooling**: Переиспользование объектов
4. **JIT compilation**: Планируется для будущих версий

### Бенчмарки

```text
Программа 100 строк:   ~50ms
Программа 500 строк:   ~200ms  
Программа 1000 строк:  ~800ms
Робот 50 команд:       ~100ms
Массив 1000 элементов: ~150ms
```

## 🔮 Планы развития

### Краткосрочные (3-6 месяцев)

- ✅ **Мониторинг системы** - завершено
- 🔄 **JIT компиляция** - для ускорения выполнения
- 📱 **GraphQL API** - для более гибких запросов
- 🔐 **OAuth2 аутентификация** - для многопользовательского режима

### Среднесрочные (6-12 месяцев)

- 🎯 **Микросервисная архитектура** - разделение на сервисы
- 🤖 **AI помощник** - интеграция с GPT для помощи в коде
- 📊 **Real-time analytics** - подробная аналитика использования
- 🌐 **Multi-tenant поддержка** - для облачного хостинга

### Долгосрочные (12+ месяцев)

- ☁️ **Cloud-native** - Kubernetes, auto-scaling
- 🔒 **Advanced security** - детальный аудит безопасности
- 🌍 **Интернационализация** - поддержка других языков
- 📱 **gRPC API** - для высокопроизводительных клиентов

---

**Backend PyRobot обеспечивает надежную и производительную основу для современного изучения языка КуМир!** 🚀
