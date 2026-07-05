import sys
import os
import importlib
from datetime import date as _date
import unittest.mock as mock

def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)

# Pin today to a fixed date so tests are deterministic
_TODAY = _date(2026, 5, 30)

def _with_fixed_today(fn):
    """Run fn with date.today() pinned to _TODAY."""
    import datetime as _dt
    class _FakeDate(_date):
        @classmethod
        def today(cls):
            return _TODAY
    with mock.patch("datetime.date", _FakeDate):
        return fn()


def test_days_between_future():
    """days_between returns a positive int for a future date."""
    m = _load()
    result = _with_fixed_today(lambda: m.days_between(2026, 6, 30))
    assert result == 31, (
        f"Expected 31 days between 2026-05-30 and 2026-06-30, got {result!r}. "
        "Use (date(year, month, day) - date.today()).days."
    )


def test_days_between_past():
    """days_between returns a negative int for a past date."""
    m = _load()
    result = _with_fixed_today(lambda: m.days_between(2026, 5, 1))
    assert result == -29, (
        f"Expected -29 for 2026-05-01 (29 days before 2026-05-30), got {result!r}."
    )


def test_days_between_today():
    """days_between returns 0 for today's date."""
    m = _load()
    result = _with_fixed_today(lambda: m.days_between(2026, 5, 30))
    assert result == 0, (
        f"Expected 0 for today's date, got {result!r}."
    )


def test_days_between_returns_int():
    """days_between returns an int, not a timedelta."""
    m = _load()
    result = _with_fixed_today(lambda: m.days_between(2026, 6, 1))
    assert isinstance(result, int), (
        f"Expected an int but got {type(result).__name__!r}. "
        "Make sure you access `.days` on the timedelta, not return the timedelta itself."
    )


def test_is_future_true():
    """is_future returns True for a strictly future date."""
    m = _load()
    result = _with_fixed_today(lambda: m.is_future(2026, 6, 30))
    assert result is True, (
        f"Expected True for a future date but got {result!r}."
    )


def test_is_future_false_past():
    """is_future returns False for a past date."""
    m = _load()
    result = _with_fixed_today(lambda: m.is_future(2026, 1, 1))
    assert result is False, (
        f"Expected False for a past date but got {result!r}."
    )


def test_is_future_false_today():
    """is_future returns False for today (not strictly future)."""
    m = _load()
    result = _with_fixed_today(lambda: m.is_future(2026, 5, 30))
    assert result is False, (
        f"Expected False for today's date but got {result!r}. "
        "is_future should be strictly greater than zero."
    )


def test_is_future_returns_bool():
    """is_future returns a bool."""
    m = _load()
    result = _with_fixed_today(lambda: m.is_future(2026, 6, 1))
    assert isinstance(result, bool), (
        f"Expected a bool but got {type(result).__name__!r}."
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
            except Exception as e:
                print(f"ERROR {name}: {e}")
