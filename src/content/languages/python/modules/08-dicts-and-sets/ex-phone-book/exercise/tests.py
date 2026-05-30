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


def test_add_new_contact():
    """add_contact stores a new entry in the book."""
    m = _load()
    book = {}
    result = m.add_contact(book, "Ada", "555-0101")
    assert "Ada" in result, (
        "After add_contact, 'Ada' should be a key in the returned dict. "
        f"Got {result!r}. Use book[name] = number."
    )
    assert result["Ada"] == "555-0101", (
        f"Expected '555-0101' for 'Ada' but got {result['Ada']!r}."
    )


def test_add_updates_existing():
    """add_contact overwrites an existing number."""
    m = _load()
    book = {"Ada": "555-0101"}
    result = m.add_contact(book, "Ada", "555-9999")
    assert result["Ada"] == "555-9999", (
        f"Calling add_contact on an existing name should update the number. "
        f"Expected '555-9999' but got {result['Ada']!r}."
    )


def test_lookup_found():
    """lookup returns the correct number when the name exists."""
    m = _load()
    book = {"Ada": "555-0101", "Grace": "555-0102"}
    assert m.lookup(book, "Grace") == "555-0102", (
        "lookup('Grace') should return '555-0102'. "
        "Use book.get(name) to retrieve the value."
    )


def test_lookup_missing():
    """lookup returns None for a name that isn't in the book."""
    m = _load()
    book = {"Ada": "555-0101"}
    result = m.lookup(book, "Linus")
    assert result is None, (
        f"lookup should return None for a missing name, not raise an error. "
        f"Got {result!r}. Use book.get(name) instead of book[name]."
    )


def test_remove_existing():
    """remove_contact deletes a name that is in the book."""
    m = _load()
    book = {"Ada": "555-0101", "Grace": "555-0102"}
    result = m.remove_contact(book, "Grace")
    assert "Grace" not in result, (
        f"'Grace' should have been removed but the book is still {result!r}. "
        "Use book.pop(name, None) to remove the entry."
    )


def test_remove_missing_no_crash():
    """remove_contact does not crash when the name isn't in the book."""
    m = _load()
    book = {"Ada": "555-0101"}
    try:
        result = m.remove_contact(book, "Linus")
    except KeyError:
        raise AssertionError(
            "remove_contact raised KeyError for a name not in the book. "
            "Use book.pop(name, None) — the second argument makes it silent."
        )
    assert result == {"Ada": "555-0101"}, (
        f"Book should be unchanged after removing a missing name. Got {result!r}."
    )


def test_all_names_sorted():
    """all_names returns names in sorted alphabetical order."""
    m = _load()
    book = {"Grace": "555-0102", "Ada": "555-0101", "Linus": "555-0103"}
    result = m.all_names(book)
    assert result == ["Ada", "Grace", "Linus"], (
        f"Expected ['Ada', 'Grace', 'Linus'] but got {result!r}. "
        "Use sorted(book.keys())."
    )


def test_all_names_empty_book():
    """all_names returns an empty list for an empty book."""
    m = _load()
    assert m.all_names({}) == [], (
        "all_names({}) should return []. Got: " + repr(m.all_names({}))
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
