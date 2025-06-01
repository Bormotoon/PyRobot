# FILE START: system_functions.py
import logging
import time

logger = logging.getLogger('KumirSystemFunctions')


def sleep_ms(x):
    """
    Имитирует паузу. На сервере НЕ выполняет реальную задержку time.sleep(),
    чтобы не блокировать процесс. Просто логирует и возвращает None.
    Реальная пауза должна быть реализована на фронтенде при анимации трассировки.

    Параметры:
      x (int или число): Количество миллисекунд (игнорируется на бэкенде).

    Возвращаемое значение:
      None
    """
    try:
        ms = int(x)
        if ms < 0:
            ms = 0  # Отрицательная пауза не имеет смысла
    except Exception as e:
        # Если аргумент некорректен, логируем и считаем паузу нулевой
        logger.warning(f"sleep_ms: invalid argument '{x}', treating as 0ms. Error: {e}")
        ms = 0

    # НЕ ДЕЛАЕМ time.sleep() НА СЕРВЕРЕ
    logger.info(
        f"Kumir command 'ждать'/'sleep_ms'({ms}ms) encountered. "
        f"Backend does nothing (handled by frontend animation)."
    )

    # В Кумире это процедура, она ничего не возвращает
    return None


def current_time():
    """
    Возвращает текущее время в миллисекундах, прошедших с полуночи (локальное время).

    Возвращаемое значение:
      int: Количество миллисекунд с начала текущего дня.
    """
    try:
        now = time.time()
        local = time.localtime(now)        # Вычисляем секунды с полуночи
        seconds_since_midnight = (local.tm_hour * 3600 + local.tm_min * 60
                                  + local.tm_sec + (now - int(now)))
        # Переводим в миллисекунды
        ms = int(seconds_since_midnight * 1000)
        return ms
    except Exception as e:
        logger.error(f"Error getting current time: {e}")
        return 0  # Возвращаем 0 в случае ошибки


# Алиасы для обратной совместимости (русские имена):
ждать = sleep_ms
время = current_time

# FILE END: system_functions.py
