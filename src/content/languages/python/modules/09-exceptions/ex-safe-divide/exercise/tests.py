import sys
import os
import importlib


def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


def test_safe_divide_normal():
    """safe_divide returns the correct float for normal division."""
    m = _load()
    assert m.safe_divide(10, 2) == 5.0, (
        f"Expected 5.0 but got {m.safe_divide(10, 2)!r}. "
        "Return a / b inside a try block."
    )


def test_safe_divide_zero():
    """safe_divide returns 'undefined' when b is zero."""
    m = _load()
    result = m.safe_divide(10, 0)
    assert result == "undefined", (
        f"Expected 'undefined' but got {result!r}. "
        "Catch ZeroDivisionError and return the string 'undefined'."
    )


def test_safe_divide_negative():
    """safe_divide handles negative numbers."""
    m = _load()
    assert m.safe_divide(-6, 3) == -2.0, (
        f"Expected -2.0 but got {m.safe_divide(-6, 3)!r}."
    )


def test_safe_divide_float_result():
    """safe_divide returns a float, not an int."""
    m = _load()
    result = m.safe_divide(7, 2)
    assert result == 3.5, (
        f"Expected 3.5 but got {result!r}. Use / (true division), not // (floor division)."
    )


def test_safe_divide_zero_numerator():
    """safe_divide(0, 5) returns 0.0, not 'undefined'."""
    m = _load()
    result = m.safe_divide(0, 5)
    assert result == 0.0, (
        f"Expected 0.0 when numerator is 0 but got {result!r}. "
        "Only return 'undefined' when the *denominator* is zero."
    )


def test_message_normal():
    """safe_divide_message returns the correct string for normal division."""
    m = _load()
    result = m.safe_divide_message(10, 2)
    assert result == "10 / 2 = 5.0", (
        f"Expected '10 / 2 = 5.0' but got {result!r}."
    )


def test_message_zero():
    """safe_divide_message returns the correct string for zero division."""
    m = _load()
    result = m.safe_divide_message(10, 0)
    assert result == "10 / 0 is undefined", (
        f"Expected '10 / 0 is undefined' but got {result!r}."
    )


def test_message_negative():
    """safe_divide_message works with negative values."""
    m = _load()
    result = m.safe_divide_message(-6, 3)
    assert result == "-6 / 3 = -2.0", (
        f"Expected '-6 / 3 = -2.0' but got {result!r}."
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
