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


def test_basic():
    """Filters and lowercases correctly."""
    m = _load()
    result = m.filter_words(["Hello", "WORLD", "Python", "hi", "OK"], min_length=2)
    assert result == ["hello", "python", "world"], (
        f"Expected ['hello', 'python', 'world'] but got {result!r}. "
        "Keep words longer than min_length (len > min_length), lowercase them, and sort."
    )


def test_sorted_alphabetically():
    """Result is sorted alphabetically."""
    m = _load()
    result = m.filter_words(["Zebra", "apple", "Mango"], min_length=0)
    assert result == sorted(result), (
        f"Result is not sorted: {result!r}. Wrap your comprehension in sorted(...)."
    )
    assert result == ["apple", "mango", "zebra"], (
        f"Expected ['apple', 'mango', 'zebra'] but got {result!r}."
    )


def test_lowercase():
    """All returned words are lowercase."""
    m = _load()
    result = m.filter_words(["UPPER", "MiXeD", "lower"], min_length=0)
    assert all(w == w.lower() for w in result), (
        f"Not all words are lowercase: {result!r}. Use word.lower() in your comprehension."
    )


def test_strictly_greater_than():
    """min_length=3 excludes words of length exactly 3."""
    m = _load()
    result = m.filter_words(["cat", "dog", "elephant", "ox"], min_length=3)
    assert result == ["elephant"], (
        f"Expected ['elephant'] but got {result!r}. "
        "Words must be strictly longer than min_length (len(word) > min_length, not >=)."
    )


def test_empty_input():
    """Returns an empty list for an empty input."""
    m = _load()
    result = m.filter_words([], min_length=0)
    assert result == [], (
        f"Expected [] for empty input but got {result!r}."
    )


def test_nothing_passes_filter():
    """Returns an empty list when no words are long enough."""
    m = _load()
    result = m.filter_words(["apple", "fig", "kiwi"], min_length=10)
    assert result == [], (
        f"Expected [] when no words pass the filter but got {result!r}."
    )


def test_min_length_zero():
    """min_length=0 keeps all words (since any non-empty word has len > 0)."""
    m = _load()
    result = m.filter_words(["b", "aa", "ccc"], min_length=0)
    assert result == ["aa", "b", "ccc"], (
        f"Expected ['aa', 'b', 'ccc'] but got {result!r}."
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
