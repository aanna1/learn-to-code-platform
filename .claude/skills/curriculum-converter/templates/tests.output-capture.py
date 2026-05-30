"""Output-capture grader template.

Use this when the exercise task is to PRINT specific output. The learner's code is imported as
a module named `submission`; importing it runs its top-level code, and we capture everything it
prints. Each test_*() asserts on the captured lines.

The FIRST LINE of each test's docstring is the name shown to the learner — write it as a clear
statement of what's being checked. Keep assertion messages friendly: say what was expected, what
happened, and hint at the fix.

Replace the placeholders (EXPECTED_LINE_COUNT, the expected strings) and add/remove tests to fit.
"""

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


def test_line_count():
    """Output has the expected number of non-empty lines."""
    lines = [l for l in _get_output() if l.strip()]
    expected = 3  # EXPECTED_LINE_COUNT
    assert len(lines) == expected, (
        f"Expected exactly {expected} lines of output, got {len(lines)}. "
        "Check how many print() calls you have."
    )


def test_first_line():
    """First line is correct."""
    lines = [l for l in _get_output() if l.strip()]
    assert lines[0] == "EXPECTED FIRST LINE", (
        f"First line should be 'EXPECTED FIRST LINE' but got: {lines[0]!r}. "
        "Check capitalization and punctuation."
    )


# Add more test_*() functions for the remaining lines / requirements.


if __name__ == "__main__":
    # Lets you eyeball the captured output while authoring. Not run during grading.
    for line in _get_output():
        print(line)
