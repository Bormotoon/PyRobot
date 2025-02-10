# system_functions.py
import time


def wait(x):
    """
    Pauses the program for x milliseconds.
    One millisecond is 1/1000 second.

    Пример:
      ждать(500)  # приостанавливает выполнение на 0.5 секунды
    """
    try:
        ms = int(x)
    except Exception as e:
        raise ValueError(f"wait: argument x must be an integer, error: {e}")
    time.sleep(ms / 1000.0)


def get_time():
    """
    Returns the current time in milliseconds since midnight (local time).

    Пример:
      t = время()  # t – количество миллисекунд от начала текущего дня
    """
    now = time.time()
    local = time.localtime(now)
    # Calculate the number of seconds since midnight:
    seconds_since_midnight = local.tm_hour * 3600 + local.tm_min * 60 + local.tm_sec + (now - int(now))
    ms = int(seconds_since_midnight * 1000)
    return ms


# Aliases to preserve the Russian names as specified in the documentation:
ждать = wait
время = get_time
