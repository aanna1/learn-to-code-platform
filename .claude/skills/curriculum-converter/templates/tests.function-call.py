"""Function-call grader template.

Use this when the exercise task is to DEFINE A FUNCTION. The learner's code is imported as a
module named `submission`; tests call the function directly and assert on its return value.

Keep any input()/print() demo in the learner's file under `if __name__ == "__main__":` so that
importing `submission` does NOT run it (importing sets __name__ to "submission", not "__main__").

The FIRST LINE of each test's docstring is the name shown to the learner. Replace FUNC_NAME and
the cases below.
"""

import importlib
import sys


def _submission():
    """Import (or reload) the learner's submission module."""
    if "submission" in sys.modules:
        return importlib.reload(sys.modules["submission"])
    import submission
    return submission


def test_function_exists():
    """A function named FUNC_NAME is defined."""
    sub = _submission()
    assert hasattr(sub, "FUNC_NAME") and callable(sub.FUNC_NAME), (
        "Define a function named FUNC_NAME at the top level of your file."
    )


def test_basic_case():
    """FUNC_NAME(2, 3) returns 5."""
    sub = _submission()
    result = sub.FUNC_NAME(2, 3)
    assert result == 5, f"FUNC_NAME(2, 3) should return 5 but returned {result!r}."


def test_edge_case():
    """FUNC_NAME handles the edge case."""
    sub = _submission()
    result = sub.FUNC_NAME(0, 0)
    assert result == 0, f"FUNC_NAME(0, 0) should return 0 but returned {result!r}."


if __name__ == "__main__":
    sub = _submission()
    print(sub.FUNC_NAME(2, 3))
