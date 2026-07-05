import logging
from io import StringIO
from unittest.mock import patch, MagicMock

from submission import log_calls, repeat


# ---------------------------------------------------------------------------
# log_calls tests
# ---------------------------------------------------------------------------

def test_log_calls_preserves_name():
    """log_calls preserves the wrapped function's __name__."""
    @log_calls
    def my_func():
        pass

    assert my_func.__name__ == "my_func", (
        f"log_calls must use @functools.wraps(func). "
        f"my_func.__name__ is {my_func.__name__!r}, expected 'my_func'."
    )


def test_log_calls_preserves_doc():
    """log_calls preserves the wrapped function's docstring."""
    @log_calls
    def my_func():
        """My docstring."""
        pass

    assert my_func.__doc__ == "My docstring.", (
        f"log_calls must use @functools.wraps(func) to preserve __doc__. "
        f"Got {my_func.__doc__!r}."
    )


def test_log_calls_returns_result():
    """log_calls does not change the return value."""
    @log_calls
    def add(a, b):
        return a + b

    result = add(2, 3)
    assert result == 5, (
        f"log_calls wrapper must return the original function's result. "
        f"add(2, 3) returned {result!r}, expected 5."
    )


def test_log_calls_logs_at_info():
    """log_calls logs at INFO level."""
    calls = []

    @log_calls
    def add(a, b):
        return a + b

    handler = logging.Handler()
    handler.emit = lambda record: calls.append(record)
    logger = logging.getLogger("submission")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    try:
        add(2, 3)
    finally:
        logger.removeHandler(handler)

    assert any(r.levelno == logging.INFO for r in calls), (
        "log_calls must log at INFO level. "
        "Use log.info(...) — not print(), log.debug(), or log.warning()."
    )


def test_log_calls_includes_function_name():
    """log_calls message includes the function name."""
    messages = []

    @log_calls
    def my_special_function(x):
        return x * 2

    handler = logging.Handler()
    handler.emit = lambda record: messages.append(record.getMessage())
    logger = logging.getLogger("submission")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    try:
        my_special_function(5)
    finally:
        logger.removeHandler(handler)

    assert any("my_special_function" in m for m in messages), (
        f"log_calls must include the function name in the log message. "
        f"Log messages were: {messages}"
    )


def test_log_calls_includes_args():
    """log_calls message includes the positional arguments."""
    messages = []

    @log_calls
    def add(a, b):
        return a + b

    handler = logging.Handler()
    handler.emit = lambda record: messages.append(record.getMessage())
    logger = logging.getLogger("submission")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    try:
        add(7, 11)
    finally:
        logger.removeHandler(handler)

    combined = " ".join(messages)
    assert "7" in combined and "11" in combined, (
        f"log_calls must include the arguments in the log message. "
        f"Called add(7, 11) but messages were: {messages}"
    )


def test_log_calls_includes_result():
    """log_calls message includes the return value."""
    messages = []

    @log_calls
    def add(a, b):
        return a + b

    handler = logging.Handler()
    handler.emit = lambda record: messages.append(record.getMessage())
    logger = logging.getLogger("submission")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    try:
        add(2, 3)
    finally:
        logger.removeHandler(handler)

    combined = " ".join(messages)
    assert "5" in combined, (
        f"log_calls must include the return value in the log message. "
        f"add(2, 3) returns 5 but messages were: {messages}"
    )


# ---------------------------------------------------------------------------
# repeat tests
# ---------------------------------------------------------------------------

def test_repeat_calls_function_n_times():
    """repeat(times=n) calls the function exactly n times."""
    call_count = 0

    @repeat(times=4)
    def inc():
        nonlocal call_count
        call_count += 1

    inc()
    assert call_count == 4, (
        f"@repeat(times=4) should call the function 4 times, but it ran {call_count} times."
    )


def test_repeat_returns_last_result():
    """repeat returns the result of the last call."""
    counter = [0]

    @repeat(times=3)
    def next_val():
        counter[0] += 1
        return counter[0]

    result = next_val()
    assert result == 3, (
        f"@repeat(times=3) should return the result of the last (third) call. "
        f"Got {result!r}, expected 3."
    )


def test_repeat_preserves_name():
    """repeat preserves __name__ via functools.wraps."""
    @repeat(times=2)
    def my_func():
        pass

    assert my_func.__name__ == "my_func", (
        f"@repeat must use @functools.wraps(func). "
        f"Got __name__ = {my_func.__name__!r}."
    )


def test_repeat_passes_args():
    """repeat passes arguments through to the wrapped function."""
    received = []

    @repeat(times=2)
    def record(x, y):
        received.append((x, y))

    record(1, 2)
    assert received == [(1, 2), (1, 2)], (
        f"@repeat must pass the same arguments to the function on every call. "
        f"Got {received}."
    )


def test_repeat_times_one():
    """repeat(times=1) calls the function exactly once."""
    call_count = 0

    @repeat(times=1)
    def inc():
        nonlocal call_count
        call_count += 1

    inc()
    assert call_count == 1, (
        f"@repeat(times=1) should call the function once, got {call_count}."
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    @log_calls
    def add(a, b):
        """Add two numbers."""
        return a + b

    add(2, 3)
    print(add.__name__, "|", add.__doc__)

    @repeat(times=3)
    def greet(name):
        print(f"Hello, {name}!")
        return name

    result = greet("world")
    print("last result:", result)
