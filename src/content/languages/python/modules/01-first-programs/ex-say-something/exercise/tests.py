import io
import contextlib


def _output():
    """Run the learner's main() and capture the lines it prints."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main()
    return [line for line in buf.getvalue().splitlines() if line.strip()]


def test_prints_three_lines():
    "prints exactly three lines"
    lines = _output()
    assert len(lines) == 3, (
        f"Expected exactly 3 lines of output, got {len(lines)}. "
        "Make sure you have three separate print() calls inside main()."
    )


def test_first_line():
    "the first line is 'Hello, world!'"
    lines = _output()
    assert len(lines) >= 1 and lines[0] == "Hello, world!", (
        f"First line should be 'Hello, world!' but got: {(lines[0] if lines else '<nothing>')!r}. "
        "Check your capitalization and punctuation."
    )


def test_second_line():
    "the second line is 'I am learning Python.'"
    lines = _output()
    assert len(lines) >= 2 and lines[1] == "I am learning Python.", (
        f"Second line should be 'I am learning Python.' but got: "
        f"{(lines[1] if len(lines) >= 2 else '<nothing>')!r}."
    )


def test_third_line():
    "the third line is \"Let's go!\""
    lines = _output()
    assert len(lines) >= 3 and lines[2] == "Let's go!", (
        f"Third line should be \"Let's go!\" but got: "
        f"{(lines[2] if len(lines) >= 3 else '<nothing>')!r}. "
        "Check the apostrophe and the exclamation mark."
    )
