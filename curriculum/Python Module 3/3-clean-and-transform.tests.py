import sys
import importlib


def _load():
    if "submission" in sys.modules:
        importlib.reload(sys.modules["submission"])
        return sys.modules["submission"]
    import submission
    return submission


_sub = _load()


def test_basic_strip_and_lower():
    """normalize('  Ada_Lovelace  ') returns 'ada lovelace'"""
    result = _sub.normalize("  Ada_Lovelace  ")
    assert result == "ada lovelace", (
        f"normalize('  Ada_Lovelace  ') should return 'ada lovelace', got {result!r}. "
        "Make sure you strip whitespace, replace underscores, and lowercase."
    )


def test_multiple_underscores():
    """normalize('HELLO___WORLD') returns 'hello world'"""
    result = _sub.normalize("HELLO___WORLD")
    assert result == "hello world", (
        f"normalize('HELLO___WORLD') should return 'hello world', got {result!r}. "
        "replace('_', ' ') turns each underscore into a space; "
        "splitting on whitespace then rejoining collapses the extras."
    )


def test_collapse_spaces():
    """normalize('  too   many   spaces  ') returns 'too many spaces'"""
    result = _sub.normalize("  too   many   spaces  ")
    assert result == "too many spaces", (
        f"normalize('  too   many   spaces  ') should return 'too many spaces', got {result!r}. "
        "Calling .split() with no argument collapses any run of whitespace into a split point. "
        "Then ' '.join(...) stitches the words back with single spaces."
    )


def test_already_clean():
    """normalize('already clean') returns 'already clean'"""
    result = _sub.normalize("already clean")
    assert result == "already clean", (
        f"normalize('already clean') should return 'already clean' unchanged, got {result!r}."
    )


def test_returns_string():
    """normalize returns a string, not None"""
    result = _sub.normalize("test")
    assert result is not None, (
        "normalize returned None. Make sure you use 'return', not 'print', inside the function."
    )
    assert isinstance(result, str), (
        f"normalize should return a str, got {type(result).__name__!r}."
    )


def test_strips_only_ends():
    """normalize does not remove spaces inside the string"""
    result = _sub.normalize("hello world")
    assert result == "hello world", (
        f"normalize('hello world') should return 'hello world', got {result!r}. "
        "Only strip the ends — internal spaces (collapsed to one) should stay."
    )
