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


def test_single_word():
    """Single word returns count of 1."""
    m = _load()
    assert m.word_count("hello") == {"hello": 1}, (
        "A single word should map to 1. Got: " + repr(m.word_count("hello"))
    )


def test_repeated_words():
    """Repeated words are counted correctly."""
    m = _load()
    result = m.word_count("the quick brown fox the lazy fox")
    assert result == {"the": 2, "quick": 1, "brown": 1, "fox": 2, "lazy": 1}, (
        f"Expected correct counts but got {result!r}. "
        "Make sure you're using counts.get(word, 0) + 1 for each word."
    )


def test_case_insensitive():
    """Case is ignored — 'Hello', 'hello', and 'HELLO' all count as 'hello'."""
    m = _load()
    result = m.word_count("Hello hello HELLO")
    assert result == {"hello": 3}, (
        f"Expected {{'hello': 3}} but got {result!r}. "
        "Call text.lower() before splitting so all cases collapse to lowercase."
    )


def test_mixed_case():
    """Mixed-case sentence is counted case-insensitively."""
    m = _load()
    result = m.word_count("The cat sat on the mat")
    assert result.get("the") == 2, (
        f"'The' and 'the' should both count as 'the' (total 2), but got {result!r}."
    )
    assert result.get("cat") == 1 and result.get("sat") == 1, (
        f"Unexpected counts in {result!r}."
    )


def test_empty_string():
    """Empty string returns an empty dict."""
    m = _load()
    result = m.word_count("")
    assert result == {}, (
        f"Expected {{}} for an empty string but got {result!r}. "
        "str.split() on an empty string returns [] — the loop body never runs."
    )


def test_all_lowercase_keys():
    """All keys in the result are lowercase."""
    m = _load()
    result = m.word_count("Python Is Fun")
    for key in result:
        assert key == key.lower(), (
            f"Key {key!r} is not lowercase. Apply .lower() to the text before splitting."
        )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
