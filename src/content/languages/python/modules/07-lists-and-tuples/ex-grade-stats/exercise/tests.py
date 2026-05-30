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


def test_returns_tuple():
    """grade_stats returns a tuple."""
    m = _load()
    result = m.grade_stats([80, 90, 70])
    assert isinstance(result, tuple), (
        f"Expected a tuple but got {type(result).__name__}. "
        "Return three values separated by commas: return (lowest, highest, average)."
    )


def test_lowest():
    """First element is the minimum grade."""
    m = _load()
    low, _, _ = m.grade_stats([85, 92, 78, 95, 88])
    assert low == 78, (
        f"Expected lowest=78 but got {low!r}. Use min(grades)."
    )


def test_highest():
    """Second element is the maximum grade."""
    m = _load()
    _, high, _ = m.grade_stats([85, 92, 78, 95, 88])
    assert high == 95, (
        f"Expected highest=95 but got {high!r}. Use max(grades)."
    )


def test_average():
    """Third element is the average rounded to two decimal places."""
    m = _load()
    _, _, avg = m.grade_stats([85, 92, 78, 95, 88])
    assert avg == 87.6, (
        f"Expected average=87.6 but got {avg!r}. "
        "Compute sum(grades) / len(grades), then round(..., 2)."
    )


def test_single_grade():
    """Works correctly for a one-element list."""
    m = _load()
    result = m.grade_stats([100])
    assert result == (100, 100, 100.0), (
        f"Expected (100, 100, 100.0) but got {result!r}."
    )


def test_two_grades():
    """Works correctly for a two-element list."""
    m = _load()
    result = m.grade_stats([70, 80])
    assert result == (70, 80, 75.0), (
        f"Expected (70, 80, 75.0) but got {result!r}."
    )


def test_rounding():
    """Average is rounded to exactly two decimal places."""
    m = _load()
    _, _, avg = m.grade_stats([100, 100, 99])
    assert avg == 99.67, (
        f"Expected 99.67 but got {avg!r}. "
        "Use round(sum(grades) / len(grades), 2)."
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
