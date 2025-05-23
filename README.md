# PyRobot 🤖 - Онлайн-симулятор Робота КУМИР

Веб-приложение, которое позволяет писать, выполнять и визуализировать код на языке КУМИР для исполнителя Робот прямо в браузере. Создано с использованием Python (Flask, Socket.IO) для бэкенда и React для фронтенда.

## ✨ Возможности

*   **Онлайн-редактор кода:** Пишите код КУМИР с подсветкой синтаксиса.
*   **Визуализация поля:** Наблюдайте за перемещениями Робота, установкой стен, маркеров, закраской клеток в реальном времени.
*   **Пошаговая трассировка:** Анимированное отображение выполнения команд (скорость настраивается).
*   **Режим редактирования поля:**
    *   Рисуйте и стирайте стены (ЛКМ на границах клеток).
    *   Закрашивайте и очищайте клетки (ЛКМ в центре клетки).
    *   Ставьте и убирайте маркеры (ПКМ).
    *   Перетаскивайте Робота в нужную стартовую позицию (ЛКМ на роботе и тащить).
    *   Изменяйте размеры поля.
    *   Масштабируйте поле колесом мыши.
*   **Поддержка команд Робота:** `вверх`, `вниз`, `влево`, `вправо`, `закрасить`, `стены?`, `клетка_чистая?`, `клетка_закрашена?`, `маркер?` (через сенсоры Робота).
*   **Поддержка конструкций Кумира:** Объявление переменных (`цел`, `вещ`, `лог`, `сим`, `лит`), присваивание (`:=`), арифметика, логические операции, команды `ввод`/`вывод`, условия (`если`, `выбор`), циклы (`нц для`, `нц пока`, `нц N раз`, `нц`).
*   **Файловые операции:** Поддержка команд работы с файлами (`откр_...`, `закр`, `сущ`, `папка`, `создать_папку`, `удалить_файл` и т.д.) в безопасной "песочнице" на сервере.
*   **Импорт обстановки:** Загрузка состояния поля из стандартных файлов `.fil`.
*   **Интерактивная панель управления:** Удобные кнопки для управления Роботом и полем вручную.
*   **Встроенная справка:** Краткое руководство по командам и использованию.

## 🛠️ Технологии

*   **Фронтенд:** React, Material UI (MUI), Socket.IO Client
*   **Бэкенд:** Python 3.11+, Flask, Flask-SocketIO, Flask-Session, Eventlet, Gunicorn
*   **Сессии:** Redis
*   **Интерпретатор:** Самописный интерпретатор Кумира (на базе трансляции выражений в AST Python)
*   **Контейнеризация:** Docker
*   **CI/CD:** GitHub Actions (для сборки Docker-образа)

## 🚀 Начало работы (Локальный запуск для разработки)

Если вы хотите запустить проект на своем компьютере для разработки или тестирования, выполните следующие шаги:

### 1. Предварительные требования

Убедитесь, что у вас установлены:

*   **Node.js и npm (или yarn):** Для сборки и запуска фронтенда. Рекомендуется LTS-версия Node.js. ([nodejs.org](https://nodejs.org/))
*   **Python:** Версия 3.11 или выше. ([python.org](https://www.python.org/))
*   **pip:** Менеджер пакетов Python (обычно идет вместе с Python).
*   **Docker:** Для простого запуска Redis. ([docker.com](https://www.docker.com/products/docker-desktop/))
*   **Git:** Для клонирования репозитория. ([git-scm.com](https://git-scm.com/))

### 2. Установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/Bormotoon/PyRobot.git
    cd PyRobot
    ```

2.  **Установите зависимости фронтенда:**
    ```bash
    cd pyrobot/frontend
    npm install
    # или если используете yarn:
    # yarn install
    cd ../.. # Вернитесь в корень проекта
    ```

3.  **Настройте и установите зависимости бэкенда:**
    *   Перейдите в корень проекта (если вы не там).
    *   Создайте виртуальное окружение Python (рекомендуется):
        ```bash
        python -m venv .venv
        ```
    *   Активируйте виртуальное окружение:
        *   **Windows (cmd/powershell):** `.\.venv\Scripts\activate`
        *   **macOS/Linux (bash/zsh):** `source .venv/bin/activate`
    *   Установите зависимости Python из файла `requirements.txt`, который находится в корне проекта:
        ```bash
        pip install -r requirements.txt
        ```

### 3. Запуск

Для работы приложения нужно запустить Redis, бэкенд (Flask) и фронтенд (React).

1.  **Запустите Redis:**
    Самый простой способ — использовать Docker:
    ```bash
    docker run -d -p 6379:6379 --name pyrobot-redis redis:latest
    ```
    Эта команда скачает образ Redis (если его нет) и запустит контейнер в фоновом режиме, доступный на порту 6379.

2.  **Запустите бэкенд (Flask):**
    *   Убедитесь, что ваше виртуальное окружение Python активировано (в терминале должно быть что-то вроде `(.venv)`).
    *   Запустите сервер из **корня проекта**:
        ```bash
        python -m pyrobot.backend.server
        ```
    *   Сервер должен запуститься (обычно на `http://0.0.0.0:5000/`) и вывести логи в консоль.

3.  **Запустите фронтенд (React):**
    *   Откройте **новый терминал**.
    *   Перейдите в папку фронтенда:
        ```bash
        cd pyrobot/frontend
        ```
    *   Запустите сервер разработки React:
        ```bash
        npm start
        # или если используете yarn:
        # yarn start
        ```
    *   В вашем браузере автоматически должна открыться страница приложения (обычно `http://localhost:3000`). Если нет, откройте ее вручную.

Теперь вы можете пользоваться симулятором локально!

## 📖 Как пользоваться

1.  **Редактор кода:** В левой части находится редактор. Введите сюда ваш код на языке КУМИР для Робота.
2.  **Кнопки управления кодом:**
    *   **Старт:** Запускает выполнение текущего кода.
    *   **Стоп:** Прерывает выполнение или анимацию.
    *   **Сброс:** Сбрасывает состояние поля и робота к начальному (тому, что было загружено или установлено по умолчанию), очищает переменные и вывод. *Не сбрасывает код в редакторе.*
    *   **Очистить:** Стирает код в редакторе.
    *   **Слайдер скорости:** Управляет скоростью анимации трассировки.
3.  **Панель управления (Справа):**
    *   **Стрелки:** Перемещают робота вручную.
    *   **Маркер +/-:** Ставит/убирает маркер в текущей клетке робота.
    *   **Клетка +/-:** Закрашивает/очищает текущую клетку робота.
    *   **Режим ред.:** Включает/выключает режим редактирования поля мышкой.
    *   **Ширина/Высота +/-:** Изменяет размеры поля (только в режиме редактирования).
    *   **Помощь:** Открывает окно справки.
    *   **Импорт .fil:** Позволяет загрузить обстановку из файла `.fil`.
4.  **Поле:**
    *   **Обычный режим:** Просто отображает состояние.
    *   **Режим редактирования:**
        *   **ЛКМ на границе клетки:** Поставить/убрать стену.
        *   **ЛКМ в центре клетки:** Закрасить/очистить клетку.
        *   **ПКМ на клетке:** Поставить/убрать маркер.
        *   **ЛКМ на роботе и перетащить:** Изменить стартовую позицию робота.
        *   **Колесо мыши:** Изменить масштаб поля.
5.  **Строка статуса (Под полем):** Отображает подсказки, сообщения о действиях, ошибки и вывод программы (`вывод ...`).

## 🐳 Запуск с помощью Docker (из готового образа GHCR)

Если вы не хотите настраивать окружение локально, вы можете использовать готовый Docker-образ, который автоматически собирается из этого репозитория и публикуется в GitHub Container Registry (GHCR).

1.  **Установите Docker:** Если еще не установлен ([docker.com](https://www.docker.com/products/docker-desktop/)).

2.  **Скачайте образ:**
    ```bash
    docker pull ghcr.io/bormotoon/pyrobot:latest
    ```
    *(Замените `bormotoon/pyrobot` на правильный путь, если репозиторий переименован)*

3.  **Запустите контейнер:**

    Вам нужно запустить контейнер с приложением и, если у вас нет внешнего Redis, контейнер с Redis. Проще всего их связать через Docker-сеть.

    *   **Создайте сеть (если еще нет):**
        ```bash
        docker network create pyrobot-net
        ```
    *   **Запустите Redis в этой сети:**
        ```bash
        docker run -d --name pyrobot-redis --network pyrobot-net redis:latest
        ```
    *   **Запустите контейнер PyRobot:**
        ```bash
        docker run -d \
          -p 5000:5000 \
          --name pyrobot-app \
          --network pyrobot-net \
          # --- ВАЖНО: Установите безопасный секретный ключ! ---
          -e FLASK_SECRET_KEY='ВАШ_СЛУЧАЙНЫЙ_СУПЕР_СЕКРЕТНЫЙ_КЛЮЧ_из_многих_символов_123!@#' \
          # --- Укажите хост Redis (имя контейнера Redis в той же сети) ---
          -e REDIS_HOST='pyrobot-redis' \
          # --- Укажите разрешенный origin для CORS (ваш фронтенд) ---
          # Для локального теста: -e CORS_ALLOWED_ORIGINS='http://localhost:3000'
          # Для production:      -e CORS_ALLOWED_ORIGINS='https://ваш-сайт.com'
          -e CORS_ALLOWED_ORIGINS='http://localhost:3000' \
          # --- Установите True, если используете HTTPS ---
          -e SESSION_COOKIE_SECURE=False \
          # --- Уровень логирования (DEBUG, INFO, WARNING, ERROR) ---
          -e LOG_LEVEL=INFO \
          # --- Укажите тег образа ---
          ghcr.io/bormotoon/pyrobot:latest
        ```

4.  **Доступ к приложению:**
    *   Бэкенд будет доступен на порту `5000` вашего хоста (`http://localhost:5000`).
    *   Если вы запускаете стандартный фронтенд React локально (`npm start`), он должен автоматически подключиться к бэкенду.
    *   Если вы разворачиваете фронтенд отдельно (например, как статический сайт), убедитесь, что он настроен на обращение к вашему бэкенду (через переменную окружения `REACT_APP_BACKEND_URL` при сборке фронтенда или через прокси-сервер вроде Nginx).

## ⚙️ Конфигурация (Переменные окружения)

Поведение бэкенда можно настроить с помощью переменных окружения при запуске (особенно важно при использовании Docker):

*   `FLASK_SECRET_KEY` (**Обязательно!**): Секретный ключ для подписи сессий Flask. Должен быть длинной, случайной строкой.
*   `PORT` (По умолчанию: `5000`): Порт, на котором Gunicorn будет слушать внутри контейнера.
*   `FLASK_ENV` (По умолчанию: `production`): Режим работы Flask (`production` или `development`).
*   `LOG_LEVEL` (По умолчанию: `INFO`): Уровень детализации логов (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
*   `REDIS_HOST` (По умолчанию: `redis`): Имя хоста или IP-адрес сервера Redis.
*   `REDIS_PORT` (По умолчанию: `6379`): Порт сервера Redis.
*   `REDIS_DB` (По умолчанию: `0`): Номер базы данных Redis для сессий.
*   `CORS_ALLOWED_ORIGINS` (По умолчанию: `http://localhost:3000`): Список URL (через запятую), с которых разрешены запросы к бэкенду. В production укажите домен вашего фронтенда.
*   `SESSION_COOKIE_SAMESITE` (По умолчанию: `Lax`): Атрибут `SameSite` для cookie сессии (`Lax`, `Strict`, `None`). Для `None` требуется `SESSION_COOKIE_SECURE=True`.
*   `SESSION_COOKIE_SECURE` (По умолчанию: `False`): Установите в `True`, если ваше приложение работает по HTTPS.

## 🙌 Содействие

Если вы нашли ошибку или у вас есть идеи по улучшению, пожалуйста, создайте [Issue](https://github.com/Bormotoon/PyRobot/issues). Pull request'ы также приветствуются!

## 📜 Лицензия

GPL
