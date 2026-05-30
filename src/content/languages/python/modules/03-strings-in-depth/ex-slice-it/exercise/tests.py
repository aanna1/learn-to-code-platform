import io
import sys
import importlib
import types


def _run_submission():
    """Import (or reimport) submission and return its printed lines."""
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


def test_first_character():
    """First line is 'e' (word[0])"""
    assert len(_LINES) >= 1, "Expected at least 1 line of output, got none."
    assert _LINES[0] == "e", (
        f"First line should be 'e' (word[0]), got {_LINES[0]!r}. "
        "Remember: string indexing starts at 0."
    )


def test_last_character():
    """Second line is 'y' (word[-1])"""
    assert len(_LINES) >= 2, "Expected at least 2 lines of output."
    assert _LINES[1] == "y", (
        f"Second line should be 'y' (the last character), got {_LINES[1]!r}. "
        "Use a negative index: word[-1]."
    )


def test_first_five():
    """Third line is 'extra' (word[:5])"""
    assert len(_LINES) >= 3, "Expected at least 3 lines of output."
    assert _LINES[2] == "extra", (
        f"Third line should be 'extra' (first five characters), got {_LINES[2]!r}. "
        "The stop index is exclusive, so word[:5] gives positions 0-4."
    )


def test_from_position_five():
    """Fourth line is 'ordinary' (word[5:])"""
    assert len(_LINES) >= 4, "Expected at least 4 lines of output."
    assert _LINES[3] == "ordinary", (
        f"Fourth line should be 'ordinary' (word[5:]), got {_LINES[3]!r}. "
        "Omitting the stop gives you everything from that position to the end."
    )


def test_reversed():
    """Fifth line is 'yranidroartxe' (word[::-1])"""
    assert len(_LINES) >= 5, "Expected at least 5 lines of output."
    assert _LINES[4] == "yranidroartxe", (
        f"Fifth line should be the reversed word, got {_LINES[4]!r}. "
        "Use word[::-1] — a step of -1 walks the string from end to start."
    )


def test_middle_slice():
    """Sixth line is 'rdin' (word[6:10])"""
    assert len(_LINES) >= 6, "Expected at least 6 lines of output."
    assert _LINES[5] == "rdin", (
        f"Sixth line should be 'rdin' (positions 6-9), got {_LINES[5]!r}. "
        "To include position 9, the stop must be 10 — stop is always exclusive. "
        "Try word[6:10]."
    )


def test_exactly_six_lines():
    """Output has exactly 6 lines"""
    assert len(_LINES) == 6, (
        f"Expected exactly 6 lines of output, got {len(_LINES)}. "
        "Check that you have exactly six print() calls."
    )


if __name__ == "__main__":
    for line in _LINES:
        print(repr(line))
