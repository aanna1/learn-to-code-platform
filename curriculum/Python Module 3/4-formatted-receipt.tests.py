import io
import sys
import importlib


def _run_submission():
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        if "submission" in sys.modules:
            importlib.reload(sys.modules["submission"])
        else:
            import submission  # noqa: F401
    finally:
        sys.stdout = old_stdout
    return buf.getvalue().splitlines()


_LINES = _run_submission()


def test_line_count():
    """Output has exactly 7 lines"""
    assert len(_LINES) == 7, (
        f"Expected exactly 7 lines of output, got {len(_LINES)}. "
        "The receipt should have: header, separator, 3 items, separator, total."
    )


def test_header():
    """First line contains 'Item' and 'Price'"""
    assert len(_LINES) >= 1, "No output produced."
    line = _LINES[0]
    assert "Item" in line and "Price" in line, (
        f"First line should be the header with 'Item' and 'Price', got {line!r}."
    )
    assert line.startswith("Item"), (
        f"'Item' should be left-aligned (starts at position 0), got {line!r}."
    )
    assert line.endswith("Price"), (
        f"'Price' should be right-aligned (at the end of the line), got {line!r}."
    )


def test_separators():
    """Lines 2 and 6 are exactly 30 dashes"""
    assert len(_LINES) >= 6, "Not enough output lines to check separators."
    sep1 = _LINES[1]
    sep2 = _LINES[5]
    assert sep1 == "-" * 30, (
        f"Second line should be exactly 30 dashes, got {sep1!r} ({len(sep1)} chars). "
        "Use \"-\" * 30."
    )
    assert sep2 == "-" * 30, (
        f"Sixth line should be exactly 30 dashes, got {sep2!r} ({len(sep2)} chars)."
    )


def test_coffee_line():
    """Coffee line shows 3.50 right-aligned"""
    assert len(_LINES) >= 3, "Not enough output lines."
    line = _LINES[2]
    assert "Coffee" in line, (
        f"Third line should contain 'Coffee', got {line!r}."
    )
    assert "3.50" in line, (
        f"Coffee line should show the price '3.50', got {line!r}. "
        "Use the :>8.2f format specifier."
    )
    assert line.startswith("Coffee"), (
        f"'Coffee' should be left-aligned, got {line!r}."
    )


def test_avocado_line():
    """Avocado toast line shows 12.75 right-aligned"""
    assert len(_LINES) >= 4, "Not enough output lines."
    line = _LINES[3]
    assert "Avocado toast" in line, (
        f"Fourth line should contain 'Avocado toast', got {line!r}."
    )
    assert "12.75" in line, (
        f"Avocado toast line should show '12.75', got {line!r}."
    )


def test_orange_juice_line():
    """Orange juice line shows 4.00 right-aligned"""
    assert len(_LINES) >= 5, "Not enough output lines."
    line = _LINES[4]
    assert "Orange juice" in line, (
        f"Fifth line should contain 'Orange juice', got {line!r}."
    )
    assert "4.00" in line, (
        f"Orange juice line should show '4.00' (two decimal places), got {line!r}. "
        "Use the :>8.2f format specifier — it always shows exactly 2 decimal places."
    )


def test_total_line():
    """Total line shows 20.25 calculated from the three prices"""
    assert len(_LINES) >= 7, "Not enough output lines."
    line = _LINES[6]
    assert "Total" in line, (
        f"Last line should contain 'Total', got {line!r}."
    )
    assert "20.25" in line, (
        f"Total should be 20.25 (3.50 + 12.75 + 4.00), got {line!r}. "
        "Add the three price variables together rather than hardcoding the total."
    )


def test_prices_right_aligned():
    """Prices are right-aligned (price column ends at same position)"""
    assert len(_LINES) >= 7, "Not enough output lines."
    item_lines = [_LINES[2], _LINES[3], _LINES[4], _LINES[6]]
    lengths = [len(line) for line in item_lines]
    assert len(set(lengths)) == 1, (
        f"All item and total lines should be the same width (columns aligned), "
        f"but got widths {lengths}. Use the same format specifier on every line."
    )
