import sys
import os
import importlib
import json
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


def _tmppath(suffix=".json"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    os.unlink(path)   # remove so tests start from a non-existent file
    return path


def test_save_notes_creates_file():
    """save_notes creates the JSON file."""
    m = _load()
    path = _tmppath()
    try:
        m.save_notes(["hello", "world"], path)
        assert Path(path).exists(), "save_notes did not create the file"
    finally:
        Path(path).unlink(missing_ok=True)


def test_save_notes_content():
    """save_notes writes the correct list to the file."""
    m = _load()
    path = _tmppath()
    try:
        notes = ["buy milk", "call mom", "pay rent"]
        m.save_notes(notes, path)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded == notes, f"Expected {notes!r} but file contains {loaded!r}"
    finally:
        Path(path).unlink(missing_ok=True)


def test_save_notes_overwrites():
    """save_notes replaces the file contents on a second call."""
    m = _load()
    path = _tmppath()
    try:
        m.save_notes(["first"], path)
        m.save_notes(["second", "third"], path)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded == ["second", "third"], (
            f"Expected ['second', 'third'] after overwrite, got {loaded!r}"
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_save_notes_uses_indent():
    """save_notes writes indented JSON (indent=2)."""
    m = _load()
    path = _tmppath()
    try:
        m.save_notes(["a", "b"], path)
        raw = Path(path).read_text()
        assert "\n" in raw, (
            "save_notes should write indented JSON (indent=2), but got a single-line string. "
            "Pass indent=2 to json.dump."
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_load_notes_basic():
    """load_notes returns the saved list."""
    m = _load()
    path = _tmppath()
    try:
        notes = ["item one", "item two"]
        with open(path, "w") as f:
            json.dump(notes, f)
        result = m.load_notes(path)
        assert result == notes, f"Expected {notes!r} but got {result!r}"
    finally:
        Path(path).unlink(missing_ok=True)


def test_load_notes_missing_file():
    """load_notes returns [] when the file does not exist."""
    m = _load()
    missing = _tmppath()  # path was unlinked — definitely does not exist
    result = m.load_notes(missing)
    assert result == [], (
        f"Expected [] for a missing file, got {result!r}. "
        "Check Path(filepath).exists() before opening."
    )


def test_roundtrip():
    """save then load returns the same list."""
    m = _load()
    path = _tmppath()
    try:
        original = ["alpha", "beta", "gamma"]
        m.save_notes(original, path)
        result = m.load_notes(path)
        assert result == original, (
            f"Round-trip failed: saved {original!r}, loaded {result!r}"
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_load_returns_list():
    """load_notes returns a list."""
    m = _load()
    path = _tmppath()
    try:
        with open(path, "w") as f:
            json.dump(["x"], f)
        result = m.load_notes(path)
        assert isinstance(result, list), (
            f"Expected list, got {type(result).__name__}"
        )
    finally:
        Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
