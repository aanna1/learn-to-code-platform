import sys
import os
import importlib
import types

# ---------------------------------------------------------------------------
# Submission loader
# ---------------------------------------------------------------------------

def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


# ---------------------------------------------------------------------------
# first_and_last tests
# ---------------------------------------------------------------------------

def test_first_and_last_basic():
    """first_and_last returns the first and last elements."""
    m = _load()
    result = m.first_and_last(["Ada", "Grace", "Linus", "Guido"])
    assert result == ("Ada", "Guido"), (
        f"Expected ('Ada', 'Guido') but got {result!r}. "
        "Use items[0] for the first element and items[-1] for the last."
    )


def test_first_and_last_returns_tuple():
    """first_and_last returns a tuple, not a list."""
    m = _load()
    result = m.first_and_last([1, 2, 3])
    assert isinstance(result, tuple), (
        f"Expected a tuple but got {type(result).__name__}. "
        "Wrap the two values in parentheses: return (items[0], items[-1])."
    )


def test_first_and_last_single_element():
    """first_and_last works on a one-element list."""
    m = _load()
    result = m.first_and_last([42])
    assert result == (42, 42), (
        f"Expected (42, 42) for a single-element list but got {result!r}. "
        "items[0] and items[-1] both refer to the only element when the list has one item."
    )


def test_first_and_last_numbers():
    """first_and_last works with a list of numbers."""
    m = _load()
    result = m.first_and_last([10, 20, 30, 40, 50])
    assert result == (10, 50), (
        f"Expected (10, 50) but got {result!r}."
    )


# ---------------------------------------------------------------------------
# middle tests
# ---------------------------------------------------------------------------

def test_middle_basic():
    """middle returns everything except the first and last elements."""
    m = _load()
    result = m.middle(["Ada", "Grace", "Linus", "Guido"])
    assert result == ["Grace", "Linus"], (
        f"Expected ['Grace', 'Linus'] but got {result!r}. "
        "The slice items[1:-1] gives everything except the first and last."
    )


def test_middle_returns_list():
    """middle returns a list, not a tuple."""
    m = _load()
    result = m.middle([1, 2, 3])
    assert isinstance(result, list), (
        f"Expected a list but got {type(result).__name__}. "
        "A slice like items[1:-1] already returns a list."
    )


def test_middle_three_elements():
    """middle of a three-element list returns a one-element list."""
    m = _load()
    result = m.middle([1, 2, 3])
    assert result == [2], (
        f"Expected [2] but got {result!r}. "
        "items[1:-1] on [1, 2, 3] gives [2] — just the middle item."
    )


def test_middle_preserves_order():
    """middle preserves the original order of elements."""
    m = _load()
    result = m.middle([5, 4, 3, 2, 1])
    assert result == [4, 3, 2], (
        f"Expected [4, 3, 2] but got {result!r}. "
        "The slice should return the inner elements in their original order."
    )


if __name__ == "__main__":
    import io, contextlib
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
