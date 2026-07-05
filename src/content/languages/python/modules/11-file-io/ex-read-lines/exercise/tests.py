import sys
import os
import importlib
import tempfile
from pathlib import Path


def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


def _tmp(content):
    """Write content to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write(content)
    f.close()
    return f.name


def test_read_lines_basic():
    """read_lines returns stripped non-empty lines in order."""
    m = _load()
    path = _tmp("apple\nbanana\ncherry\n")
    try:
        result = m.read_lines(path)
        assert result == ["apple", "banana", "cherry"], (
            f"Expected ['apple', 'banana', 'cherry'] but got {result!r}"
        )
    finally:
        os.unlink(path)


def test_read_lines_skips_blank():
    """read_lines drops blank lines."""
    m = _load()
    path = _tmp("apple\n\nbanana\n\n\ncherry\n")
    try:
        result = m.read_lines(path)
        assert result == ["apple", "banana", "cherry"], (
            f"Blank lines should be dropped; got {result!r}"
        )
    finally:
        os.unlink(path)


def test_read_lines_strips_whitespace():
    """read_lines strips leading and trailing whitespace from each line."""
    m = _load()
    path = _tmp("  apple  \n  banana\ncherry  \n")
    try:
        result = m.read_lines(path)
        assert result == ["apple", "banana", "cherry"], (
            f"Expected stripped lines but got {result!r}"
        )
    finally:
        os.unlink(path)


def test_read_lines_empty_file():
    """read_lines returns an empty list for an empty file."""
    m = _load()
    path = _tmp("")
    try:
        result = m.read_lines(path)
        assert result == [], (
            f"Expected [] for empty file but got {result!r}"
        )
    finally:
        os.unlink(path)


def test_read_lines_returns_list():
    """read_lines returns a list, not a generator or tuple."""
    m = _load()
    path = _tmp("hello\n")
    try:
        result = m.read_lines(path)
        assert isinstance(result, list), (
            f"Expected list but got {type(result).__name__}"
        )
    finally:
        os.unlink(path)


def test_count_lines_basic():
    """count_lines returns the number of non-empty lines."""
    m = _load()
    path = _tmp("apple\nbanana\ncherry\n")
    try:
        result = m.count_lines(path)
        assert result == 3, f"Expected 3 but got {result!r}"
    finally:
        os.unlink(path)


def test_count_lines_skips_blank():
    """count_lines excludes blank lines from the count."""
    m = _load()
    path = _tmp("apple\n\nbanana\n\ncherry\n")
    try:
        result = m.count_lines(path)
        assert result == 3, (
            f"Expected 3 (ignoring 2 blank lines) but got {result!r}"
        )
    finally:
        os.unlink(path)


def test_count_lines_empty_file():
    """count_lines returns 0 for an empty file."""
    m = _load()
    path = _tmp("")
    try:
        result = m.count_lines(path)
        assert result == 0, f"Expected 0 for empty file but got {result!r}"
    finally:
        os.unlink(path)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
