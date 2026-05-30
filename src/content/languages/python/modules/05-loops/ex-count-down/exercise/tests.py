import io
import contextlib
from submission import count_down


def _capture(n):
    """Run count_down(n) and return its printed lines."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        count_down(n)
    return buf.getvalue().splitlines()


def test_counts_down_from_five():
    """count_down(5) prints 5, 4, 3, 2, 1"""
    lines = _capture(5)
    assert lines == ["5", "4", "3", "2", "1"], (
        f"count_down(5) should print 5, 4, 3, 2, 1 (one per line), got {lines}. "
        "Make sure you're decrementing n inside the loop."
    )


def test_counts_down_from_three():
    """count_down(3) prints 3, 2, 1"""
    lines = _capture(3)
    assert lines == ["3", "2", "1"], (
        f"count_down(3) should print 3, 2, 1, got {lines}."
    )


def test_counts_down_from_one():
    """count_down(1) prints exactly one line: 1"""
    lines = _capture(1)
    assert lines == ["1"], (
        f"count_down(1) should print just '1', got {lines}. "
        "The loop should run exactly once when n == 1."
    )


def test_no_extra_lines():
    """count_down(3) prints exactly 3 lines — stops at 1, not 0"""
    lines = _capture(3)
    assert len(lines) == 3, (
        f"count_down(3) should produce exactly 3 lines, got {len(lines)}. "
        "Make sure the loop condition is n >= 1, not n > 0 (they're the same) "
        "or that you're not accidentally printing 0."
    )


def test_descending_order():
    """count_down(4) prints values in descending order"""
    lines = _capture(4)
    values = [int(x) for x in lines]
    assert values == sorted(values, reverse=True), (
        f"Values should be in descending order, got {values}. "
        "Print n before decrementing: print(n) then n -= 1."
    )
