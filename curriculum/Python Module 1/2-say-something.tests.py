import io
import contextlib
import importlib
import sys


def _get_output():
    """Import (or reload) the submission and capture everything it prints."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if "submission" in sys.modules:
            importlib.reload(sys.modules["submission"])
        else:
            import submission  # noqa: F401
    return buf.getvalue().splitlines()


def test_prints_three_lines():
    """Output has exactly three non-empty lines."""
    lines = _get_output()
    non_empty = [l for l in lines if l.strip()]
    assert len(non_empty) == 3, (
        f"Expected exactly 3 lines of output, got {len(non_empty)}. "
        "Make sure you have three separate print() calls."
    )


def test_first_line():
    """First line is 'Hello, world!'"""
    lines = [l for l in _get_output() if l.strip()]
    assert lines[0] == "Hello, world!", (
        f"First line should be 'Hello, world!' but got: {lines[0]!r}. "
        "Check your capitalization and punctuation."
    )


def test_second_line():
    """Second line is 'I am learning Python.'"""
    lines = [l for l in _get_output() if l.strip()]
    assert lines[1] == "I am learning Python.", (
        f"Second line should be 'I am learning Python.' but got: {lines[1]!r}. "
        "Check capitalization, spacing, and the period at the end."
    )


def test_third_line():
    """Third line is \"Let's go!\""""
    lines = [l for l in _get_output() if l.strip()]
    assert lines[2] == "Let's go!", (
        f"Third line should be \"Let's go!\" but got: {lines[2]!r}. "
        "Check the apostrophe in \"Let's\" and the exclamation mark."
    )


if __name__ == "__main__":
    for line in _get_output():
        print(line)
