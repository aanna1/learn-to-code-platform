import io
import contextlib
import importlib
import sys
import inspect


def _load():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if "submission" in sys.modules:
            mod = importlib.reload(sys.modules["submission"])
        else:
            import submission as mod  # noqa: F401
    return mod, buf.getvalue().splitlines()


def _source():
    import submission
    return inspect.getsource(submission)


def test_name_line():
    """Output contains 'Name: Ada Lovelace'."""
    _, lines = _load()
    assert "Name: Ada Lovelace" in lines, (
        f"Expected a line 'Name: Ada Lovelace' in the output. "
        f"Got: {lines}"
    )


def test_age_line():
    """Output contains 'Age: 36'."""
    _, lines = _load()
    assert "Age: 36" in lines, (
        f"Expected a line 'Age: 36' in the output. Got: {lines}"
    )


def test_language_line():
    """Output contains 'Language: Python'."""
    _, lines = _load()
    assert "Language: Python" in lines, (
        f"Expected a line 'Language: Python' in the output. Got: {lines}"
    )


def test_bio_line():
    """Output contains the Bio line with all three substitutions."""
    _, lines = _load()
    assert "Bio: Ada Lovelace has been coding in Python for years." in lines, (
        "Expected: 'Bio: Ada Lovelace has been coding in Python for years.' "
        f"Got: {lines}"
    )


def test_uses_fstrings():
    """Code uses f-strings (at least one f\" or f') rather than plain strings."""
    src = _source()
    has_fstring = 'f"' in src or "f'" in src
    assert has_fstring, (
        "No f-strings found. Use f-strings to embed variables: "
        "print(f\"Name: {first_name} {last_name}\")"
    )


def test_variables_not_modified():
    """The provided variables still hold their original values."""
    mod, _ = _load()
    assert mod.first_name == "Ada", "Do not change the value of first_name."
    assert mod.last_name == "Lovelace", "Do not change the value of last_name."
    assert mod.age == 36, "Do not change the value of age."
    assert mod.language == "Python", "Do not change the value of language."


if __name__ == "__main__":
    _, lines = _load()
    for line in lines:
        print(line)
