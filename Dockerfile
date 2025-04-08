# FILE START: Dockerfile

# --- Stage 1: Frontend Builder ---
# Используем официальный образ Node.js как основу для сборки фронтенда
FROM node:20-alpine as frontend-builder

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app/frontend

# Копируем package.json и package-lock.json (или yarn.lock)
# Копируем их отдельно, чтобы использовать кэширование слоев Docker
COPY pyrobot/frontend/package.json ./
COPY pyrobot/frontend/package-lock.json ./
# Если используете yarn:
# COPY pyrobot/frontend/yarn.lock ./

# Устанавливаем зависимости фронтенда
# Используйте npm ci для более надежной установки по lock-файлу
RUN npm ci
# Если используете yarn:
# RUN yarn install --frozen-lockfile

# Копируем остальной код фронтенда
COPY pyrobot/frontend/ ./

# Собираем production-сборку React-приложения
# Переменные окружения для сборки можно передать здесь через ARG/ENV, если нужно
RUN npm run build
# Если используете yarn:
# RUN yarn build

# --- Stage 2: Python Backend Runner ---
# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения (можно переопределить при запуске контейнера)
ENV PYTHONUNBUFFERED=1 \
    # Устанавливаем порт, на котором будет слушать Gunicorn внутри контейнера
    PORT=5000 \
    # Устанавливаем среду Flask (production или development)
    FLASK_ENV=production \
    # Устанавливаем Log Level по умолчанию
    LOG_LEVEL=INFO \
    # Настройки сессии (в production лучше переопределять через переменные окружения при запуске)
    SESSION_COOKIE_SAMESITE=Lax \
    SESSION_COOKIE_SECURE=False \
    REDIS_HOST=redis \
    # Имя хоста Redis (если Redis в другом контейнере в той же Docker сети)
    REDIS_PORT=6379 \
    REDIS_DB=0 \
    # CORS Origins (замените * или localhost на ваш домен в production)
    CORS_ALLOWED_ORIGINS=http://localhost:3000 \
    # Секретный ключ Flask - **ОБЯЗАТЕЛЬНО ПЕРЕОПРЕДЕЛИТЕ ПРИ ЗАПУСКЕ!**
    FLASK_SECRET_KEY=this-is-a-default-unsafe-key-change-it

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы, если нужны (например, для Redis клиента)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Создаем непривилегированного пользователя и группу
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --shell /bin/sh appuser

# Копируем зависимости бэкенда
# Предполагается, что у вас есть requirements.txt в корне папки backend
COPY requirements.txt ./
# Если используете poetry:
# COPY pyrobot/backend/pyproject.toml pyrobot/backend/poetry.lock* ./
# RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Устанавливаем зависимости бэкенда
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бэкенда
COPY ./pyrobot/backend ./pyrobot/backend

# Копируем собранный фронтенд из первого стейджа
# Статические файлы React обычно попадают в папку build
COPY --from=frontend-builder /app/frontend/build ./pyrobot/backend/static

# Создаем каталог для песочницы и даем права пользователю
# Путь должен совпадать с тем, что используется в file_functions.py
RUN mkdir -p /app/pyrobot/backend/kumir_sandbox && chown -R appuser:appgroup /app/pyrobot/backend/kumir_sandbox
# Даем права на все скопированное приложение
RUN chown -R appuser:appgroup /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт, на котором будет работать приложение
EXPOSE ${PORT}

# Команда для запуска приложения с использованием Gunicorn + eventlet
# Используйте python -m ... для разработки/отладки
# Gunicorn рекомендуется для production
CMD ["gunicorn", \
     "--worker-class", "eventlet", \
     "-w", "1", \
     # Количество воркеров (1 для eventlet обычно достаточно, если нет CPU-bound задач)
     "--bind", "0.0.0.0:${PORT}", \
     # Таймаут запроса (увеличьте, если выполнение Кумира может быть долгим)
     "--timeout", "120", \
     # Модуль и переменная Flask app
     "pyrobot.backend.server:app"]

# Альтернатива для разработки:
# CMD ["python", "-m", "pyrobot.backend.server"]

# FILE END: Dockerfile
