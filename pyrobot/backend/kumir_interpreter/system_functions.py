# system_functions.py
import time


def ждать(x):
    """
    Приостанавливает выполнение программы на x миллисекунд.
    Одна миллисекунда равна 1/1000 секунды.

    Пример:
      ждать(500)  # приостанавливает выполнение на 0.5 секунды
    """
    try:
        ms = int(x)
    except Exception as e:
        raise ValueError(f"ждать: аргумент x должен быть целым числом, ошибка: {e}")
    time.sleep(ms / 1000.0)


def время():
    """
    Возвращает текущее время в миллисекундах, прошедших с начала суток по местному времени.

    Пример:
      t = время()  # t – количество миллисекунд от начала текущего дня
    """
    now = time.time()
    local = time.localtime(now)
    # Вычисляем число секунд с начала суток:
    seconds_since_midnight = local.tm_hour * 3600 + local.tm_min * 60 + local.tm_sec + (now - int(now))
    ms = int(seconds_since_midnight * 1000)
    return ms
