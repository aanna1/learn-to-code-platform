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


def _tmppath(suffix=".log"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    os.unlink(path)
    return path


def test_append_log_creates_file():
    """append_log creates the log file if it doesn't exist."""
    m = _load()
    path = _tmppath()
    try:
        m.append_log("hello", path)
        assert Path(path).exists(), "append_log did not create the file"
    finally:
        Path(path).unlink(missing_ok=True)


def test_append_log_format():
    """append_log writes entries in '[LOG] message' format."""
    m = _load()
    path = _tmppath()
    try:
        m.append_log("test message", path)
        content = Path(path).read_text().strip()
        assert content == "[LOG] test message", (
            f"Expected '[LOG] test message' but got {content!r}. "
            "Format must be exactly '[LOG] ' followed by the message."
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_append_log_multiple_entries():
    """append_log preserves earlier entries when called multiple times."""
    m = _load()
    path = _tmppath()
    try:
        m.append_log("first", path)
        m.append_log("second", path)
        m.append_log("third", path)
        lines = [l.strip() for l in Path(path).read_text().splitlines() if l.strip()]
        assert lines == ["[LOG] first", "[LOG] second", "[LOG] third"], (
            f"Expected three entries but got {lines!r}. "
            "Make sure you're using 'a' (append) mode, not 'w' (write) mode."
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_append_log_does_not_erase():
    """append_log does not erase existing entries (must use 'a' mode)."""
    m = _load()
    path = _tmppath()
    try:
        m.append_log("entry one", path)
        m.append_log("entry two", path)
        content = Path(path).read_text()
        assert "[LOG] entry one" in content, (
            "First entry was erased. Use open(filepath, 'a') not open(filepath, 'w')."
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_append_log_newline():
    """append_log writes each entry on its own line."""
    m = _load()
    path = _tmppath()
    try:
        m.append_log("alpha", path)
        m.append_log("beta", path)
        lines = Path(path).read_text().splitlines()
        assert len(lines) >= 2, (
            f"Expected at least 2 lines but got {len(lines)}. "
            "Each entry must end with '\\n' so entries don't run together."
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_read_log_basic():
    """read_log returns entries as a list of stripped strings."""
    m = _load()
    path = _tmppath()
    try:
        Path(path).write_text("[LOG] one\n[LOG] two\n[LOG] three\n")
        result = m.read_log(path)
        assert result == ["[LOG] one", "[LOG] two", "[LOG] three"], (
            f"Expected three entries but got {result!r}"
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_read_log_missing_file():
    """read_log returns [] when the file does not exist."""
    m = _load()
    missing = _tmppath()  # already unlinked
    result = m.read_log(missing)
    assert result == [], (
        f"Expected [] for missing file but got {result!r}. "
        "Check Path(filepath).exists() before opening."
    )


def test_read_log_after_appending():
    """read_log round-trips correctly with append_log."""
    m = _load()
    path = _tmppath()
    try:
        m.append_log("server started", path)
        m.append_log("user logged in", path)
        result = m.read_log(path)
        assert result == ["[LOG] server started", "[LOG] user logged in"], (
            f"Round-trip failed: got {result!r}"
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
