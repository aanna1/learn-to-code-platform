import inspect
import time
from contextlib import contextmanager
from io import StringIO
from typing import Any
from unittest.mock import patch

from submission import managed_list, timed


def test_timed_is_contextmanager():
    """timed must be decorated with @contextmanager."""
    # A @contextmanager-decorated function returns a GeneratorContextManager
    # when called; verify by checking it has __enter__ and __exit__
    cm = timed("test")
    assert hasattr(cm, "__enter__") and hasattr(cm, "__exit__"), (
        "timed() must return a context manager. "
        "Decorate timed with @contextmanager from contextlib."
    )


def test_timed_prints_label():
    """timed prints a line that starts with the given label."""
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
        with timed("my label"):
            pass
        output = mock_out.getvalue()
    assert output.startswith("my label:"), (
        f"timed('my label') should print a line starting with 'my label:', "
        f"got: {output!r}"
    )


def test_timed_prints_seconds():
    """timed output contains a time value ending with 's'."""
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
        with timed("x"):
            pass
        output = mock_out.getvalue().strip()
    assert output.endswith("s"), (
        f"timed output should end with 's' (for seconds), got: {output!r}. "
        "Format: f\"{label}: {elapsed:.4f}s\""
    )


def test_timed_measures_time():
    """timed reports a plausible elapsed time for a sleep."""
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
        with timed("sleep"):
            time.sleep(0.05)
        output = mock_out.getvalue()

    # Extract the number after the colon
    try:
        time_str = output.split(":")[1].strip().rstrip("s")
        elapsed = float(time_str)
    except (IndexError, ValueError):
        assert False, f"Could not parse elapsed time from output: {output!r}"

    assert elapsed >= 0.04, (
        f"timed should report at least ~0.05s for a 0.05s sleep, got {elapsed:.4f}s. "
        "Use time.monotonic() to measure the elapsed time."
    )


def test_managed_list_enter_returns_self():
    """managed_list.__enter__ returns the managed_list instance."""
    ml = managed_list()
    result = ml.__enter__()
    assert result is ml, (
        f"__enter__ should return self so 'with managed_list() as ml' gives the instance. "
        f"Got {result!r} instead."
    )


def test_managed_list_sorts_on_exit():
    """managed_list sorts self.items on __exit__."""
    with managed_list() as ml:
        ml.items.extend([3, 1, 4, 1, 5])
    assert ml.items == [1, 1, 3, 4, 5], (
        f"managed_list should sort self.items on exit. "
        f"Got {ml.items!r}, expected [1, 1, 3, 4, 5]."
    )


def test_managed_list_sorts_even_on_exception():
    """managed_list sorts self.items even when the with body raises."""
    ml = managed_list()
    try:
        with ml:
            ml.items.extend([5, 2, 8])
            raise ValueError("deliberate error")
    except ValueError:
        pass
    assert ml.items == [2, 5, 8], (
        f"managed_list should sort items on exit even if an exception was raised. "
        f"Got {ml.items!r}. "
        "Put self.items.sort() in a finally block or always run it in __exit__."
    )


def test_managed_list_does_not_suppress_exceptions():
    """managed_list.__exit__ must not suppress exceptions."""
    ml = managed_list()
    raised = False
    try:
        with ml:
            raise RuntimeError("should propagate")
    except RuntimeError:
        raised = True
    assert raised, (
        "managed_list.__exit__ must not suppress exceptions. "
        "Return None or False from __exit__, not True."
    )


def test_managed_list_empty():
    """managed_list works when no items are added."""
    with managed_list() as ml:
        pass
    assert ml.items == [], (
        f"managed_list with no items appended should leave self.items as []. "
        f"Got {ml.items!r}."
    )


if __name__ == "__main__":
    with timed("summing"):
        total = sum(range(500_000))
        print(f"total = {total}")

    with managed_list() as ml:
        ml.items.extend([3, 1, 4, 1, 5, 9])
    print("sorted:", ml.items)
