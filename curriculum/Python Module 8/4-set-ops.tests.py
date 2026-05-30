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


def test_unique_tags_removes_duplicates():
    """unique_tags drops duplicates."""
    m = _load()
    result = m.unique_tags(["python", "web", "python", "data", "web"])
    assert result == ["data", "python", "web"], (
        f"Expected ['data', 'python', 'web'] but got {result!r}. "
        "Convert to a set to drop duplicates, then wrap in sorted()."
    )


def test_unique_tags_already_unique():
    """unique_tags works when there are no duplicates."""
    m = _load()
    result = m.unique_tags(["web", "data", "ml"])
    assert result == sorted(["web", "data", "ml"]), (
        f"Expected alphabetically sorted list but got {result!r}."
    )


def test_unique_tags_empty():
    """unique_tags returns [] for an empty list."""
    m = _load()
    assert m.unique_tags([]) == [], (
        "unique_tags([]) should return []. Got: " + repr(m.unique_tags([]))
    )


def test_shared_tags():
    """shared_tags returns tags present in both lists."""
    m = _load()
    result = m.shared_tags(["python", "web", "data"], ["web", "ml", "python"])
    assert result == ["python", "web"], (
        f"Expected ['python', 'web'] but got {result!r}. "
        "Use set(tags_a) & set(tags_b) for intersection."
    )


def test_shared_tags_no_overlap():
    """shared_tags returns [] when there are no common tags."""
    m = _load()
    result = m.shared_tags(["python", "data"], ["web", "ml"])
    assert result == [], (
        f"Expected [] (no overlap) but got {result!r}."
    )


def test_all_tags():
    """all_tags returns the union of both collections."""
    m = _load()
    result = m.all_tags(["python", "web"], ["web", "ml"])
    assert result == ["ml", "python", "web"], (
        f"Expected ['ml', 'python', 'web'] but got {result!r}. "
        "Use set(tags_a) | set(tags_b) for union."
    )


def test_all_tags_no_overlap():
    """all_tags works when there is no overlap between the two lists."""
    m = _load()
    result = m.all_tags(["python"], ["ml"])
    assert result == ["ml", "python"], (
        f"Expected ['ml', 'python'] but got {result!r}."
    )


def test_only_in_first():
    """only_in_first returns tags in tags_a but not in tags_b."""
    m = _load()
    result = m.only_in_first(["python", "web", "data"], ["web", "ml"])
    assert result == ["data", "python"], (
        f"Expected ['data', 'python'] but got {result!r}. "
        "Use set(tags_a) - set(tags_b) for difference."
    )


def test_only_in_first_all_shared():
    """only_in_first returns [] when every tag in tags_a is also in tags_b."""
    m = _load()
    result = m.only_in_first(["python", "web"], ["python", "web", "ml"])
    assert result == [], (
        f"Expected [] when all of tags_a is contained in tags_b, but got {result!r}."
    )


def test_results_are_sorted():
    """All four functions return sorted lists."""
    m = _load()
    tags = ["zebra", "apple", "mango"]
    assert m.unique_tags(tags) == sorted(tags), (
        "unique_tags result must be sorted alphabetically."
    )
    assert m.all_tags(["zebra"], ["apple"]) == ["apple", "zebra"], (
        "all_tags result must be sorted alphabetically."
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
