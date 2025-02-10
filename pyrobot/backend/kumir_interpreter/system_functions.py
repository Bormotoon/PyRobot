# system_functions.py
import time


def sleep_ms(x):
    """
    Pauses the program for x milliseconds.
    One millisecond is 1/1000 of a second.

    Example:
      sleep_ms(500)  # pauses execution for 0.5 seconds
    """
    try:
        ms = int(x)
    except Exception as e:
        raise ValueError(f"sleep_ms: argument x must be an integer, error: {e}")
    time.sleep(ms / 1000.0)


def current_time():
    """
    Returns the current time in milliseconds since midnight (local time).

    Example:
      t = current_time()  # t is the number of milliseconds since the start of the current day
    """
    now = time.time()
    local = time.localtime(now)
    # Calculate seconds since midnight:
    seconds_since_midnight = local.tm_hour * 3600 + local.tm_min * 60 + local.tm_sec + (now - int(now))
    ms = int(seconds_since_midnight * 1000)
    return ms


# Aliases for backward compatibility (Russian names as specified in the documentation):
ждать = sleep_ms
время = current_time
