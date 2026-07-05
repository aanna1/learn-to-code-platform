import sys
import os
import importlib
from unittest.mock import patch

def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


# ── get_int tests ──────────────────────────────────────────────────────────────

def test_get_int_valid_first_try():
    """get_int returns the integer when the first input is valid."""
    m = _load()
    with patch("builtins.input", return_value="42"):
        result = m.get_int("Number: ")
    assert result == 42, (
        f"Expected 42 but got {result!r}. Return int(input(prompt)) on success."
    )


def test_get_int_retries_on_bad_input(capsys=None):
    """get_int keeps prompting after non-numeric input."""
    m = _load()
    inputs = iter(["abc", "5"])
    with patch("builtins.input", side_effect=inputs):
        result = m.get_int("Number: ")
    assert result == 5, (
        f"Expected 5 after retrying, but got {result!r}. "
        "Catch ValueError and loop back to input()."
    )


def test_get_int_prints_error_on_bad_input(capsys=None):
    """get_int prints 'Please enter a whole number.' on bad input."""
    import io, contextlib
    m = _load()
    inputs = iter(["xyz", "3"])
    buf = io.StringIO()
    with patch("builtins.input", side_effect=inputs):
        with contextlib.redirect_stdout(buf):
            m.get_int("Number: ")
    output = buf.getvalue()
    assert "Please enter a whole number." in output, (
        f"Expected 'Please enter a whole number.' in output but got: {output!r}"
    )


def test_get_int_returns_negative():
    """get_int accepts negative integers."""
    m = _load()
    with patch("builtins.input", return_value="-7"):
        result = m.get_int("Number: ")
    assert result == -7, f"Expected -7 but got {result!r}."


def test_get_int_rejects_float_string():
    """get_int rejects '3.14' (int() can't parse a decimal string)."""
    m = _load()
    inputs = iter(["3.14", "3"])
    with patch("builtins.input", side_effect=inputs):
        result = m.get_int("Number: ")
    assert result == 3, (
        f"Expected 3 after rejecting '3.14', got {result!r}. "
        "int('3.14') raises ValueError — make sure you catch it and retry."
    )


# ── get_int_in_range tests ─────────────────────────────────────────────────────

def test_range_valid_first_try():
    """get_int_in_range returns immediately when input is valid and in range."""
    m = _load()
    with patch("builtins.input", return_value="3"):
        result = m.get_int_in_range("Pick: ", 1, 5)
    assert result == 3, f"Expected 3 but got {result!r}."


def test_range_rejects_below():
    """get_int_in_range rejects values below low."""
    m = _load()
    inputs = iter(["0", "1"])
    with patch("builtins.input", side_effect=inputs):
        result = m.get_int_in_range("Pick: ", 1, 5)
    assert result == 1, (
        f"Expected 1 after rejecting 0, got {result!r}. "
        "Check value < low and loop back."
    )


def test_range_rejects_above():
    """get_int_in_range rejects values above high."""
    m = _load()
    inputs = iter(["6", "5"])
    with patch("builtins.input", side_effect=inputs):
        result = m.get_int_in_range("Pick: ", 1, 5)
    assert result == 5, (
        f"Expected 5 after rejecting 6, got {result!r}. "
        "Check value > high and loop back."
    )


def test_range_accepts_boundary_low():
    """get_int_in_range accepts exactly low."""
    m = _load()
    with patch("builtins.input", return_value="1"):
        result = m.get_int_in_range("Pick: ", 1, 5)
    assert result == 1, f"Expected 1 (boundary) but got {result!r}."


def test_range_accepts_boundary_high():
    """get_int_in_range accepts exactly high."""
    m = _load()
    with patch("builtins.input", return_value="5"):
        result = m.get_int_in_range("Pick: ", 1, 5)
    assert result == 5, f"Expected 5 (boundary) but got {result!r}."


def test_range_rejects_non_numeric():
    """get_int_in_range rejects non-numeric input before the range check."""
    m = _load()
    inputs = iter(["abc", "3"])
    with patch("builtins.input", side_effect=inputs):
        result = m.get_int_in_range("Pick: ", 1, 5)
    assert result == 3, (
        f"Expected 3 after rejecting 'abc', got {result!r}."
    )


def test_range_prints_range_error():
    """get_int_in_range prints the range message for out-of-range values."""
    import io, contextlib
    m = _load()
    inputs = iter(["0", "3"])
    buf = io.StringIO()
    with patch("builtins.input", side_effect=inputs):
        with contextlib.redirect_stdout(buf):
            m.get_int_in_range("Pick: ", 1, 5)
    output = buf.getvalue()
    assert "between 1 and 5" in output, (
        f"Expected range error message with 'between 1 and 5' but got: {output!r}"
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
                print(f"ERR   {name}: {e}")
