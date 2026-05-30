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


def test_adds_names():
    """Names in to_add are included in the result."""
    m = _load()
    result = m.manage_roster([], to_add=["Alice", "Bob"], to_remove=[])
    assert "Alice" in result and "Bob" in result, (
        f"Expected both 'Alice' and 'Bob' in result but got {result!r}. "
        "Use result.append(name) for each name in to_add."
    )


def test_removes_names():
    """Names in to_remove are not in the result."""
    m = _load()
    result = m.manage_roster(["Ada", "Grace", "Linus"], to_add=[], to_remove=["Linus"])
    assert "Linus" not in result, (
        f"'Linus' should have been removed but got {result!r}. "
        "Check whether the name is in the list before calling .remove()."
    )


def test_skips_missing_names():
    """Names in to_remove that aren't in the roster are silently skipped."""
    m = _load()
    try:
        result = m.manage_roster(["Ada"], to_add=[], to_remove=["Nobody"])
    except ValueError as e:
        raise AssertionError(
            "Got a ValueError when trying to remove a name that isn't in the roster. "
            "Check with 'if name in result' before calling result.remove(name)."
        ) from e
    assert result == ["Ada"], (
        f"Expected ['Ada'] but got {result!r}."
    )


def test_returns_sorted():
    """Result is sorted alphabetically."""
    m = _load()
    result = m.manage_roster(
        ["Ada", "Grace", "Linus"],
        to_add=["Guido", "Margaret"],
        to_remove=["Linus"]
    )
    assert result == sorted(result), (
        f"Expected result sorted alphabetically but got {result!r}. "
        "Use sorted(result) as your return value."
    )
    assert result == ["Ada", "Grace", "Guido", "Margaret"], (
        f"Expected ['Ada', 'Grace', 'Guido', 'Margaret'] but got {result!r}."
    )


def test_does_not_modify_original():
    """The original roster list is unchanged after the call."""
    m = _load()
    original = ["Ada", "Grace", "Linus"]
    original_copy = original[:]
    m.manage_roster(original, to_add=["Guido"], to_remove=["Ada"])
    assert original == original_copy, (
        f"The original roster was modified. Expected {original_copy!r} but it's now {original!r}. "
        "Copy the roster at the start: result = roster.copy()."
    )


def test_empty_roster():
    """Works when the starting roster is empty."""
    m = _load()
    result = m.manage_roster([], to_add=["Zara", "Alice"], to_remove=[])
    assert result == ["Alice", "Zara"], (
        f"Expected ['Alice', 'Zara'] but got {result!r}."
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
