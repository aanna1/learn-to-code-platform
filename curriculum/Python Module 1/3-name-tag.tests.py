import io
import contextlib
import importlib
import sys


def _load():
    """Import or reload the submission, returning the module and its stdout."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if "submission" in sys.modules:
            mod = importlib.reload(sys.modules["submission"])
        else:
            import submission as mod  # noqa: F401
    return mod, buf.getvalue().splitlines()


def test_variables_are_strings():
    """first_name, last_name, and city are all strings."""
    mod, _ = _load()
    assert isinstance(mod.first_name, str), (
        f"first_name should be a string, got {type(mod.first_name).__name__}. "
        "Assign it like: first_name = \"Ada\""
    )
    assert isinstance(mod.last_name, str), (
        f"last_name should be a string, got {type(mod.last_name).__name__}."
    )
    assert isinstance(mod.city, str), (
        f"city should be a string, got {type(mod.city).__name__}."
    )


def test_variables_are_non_empty():
    """All three variables hold non-empty values."""
    mod, _ = _load()
    assert mod.first_name.strip(), "first_name is empty — assign it a real first name."
    assert mod.last_name.strip(), "last_name is empty — assign it a real last name."
    assert mod.city.strip(), "city is empty — assign it a real city name."


def test_first_name_is_single_word():
    """first_name contains only a first name (no spaces)."""
    mod, _ = _load()
    assert " " not in mod.first_name, (
        f"first_name should be just a first name with no spaces, got: {mod.first_name!r}"
    )


def test_last_name_is_single_word():
    """last_name contains only a last name (no spaces)."""
    mod, _ = _load()
    assert " " not in mod.last_name, (
        f"last_name should be just a last name with no spaces, got: {mod.last_name!r}"
    )


def test_all_three_values_printed():
    """The output contains all three variable values on separate lines."""
    mod, lines = _load()
    non_empty = [l for l in lines if l.strip()]
    assert len(non_empty) >= 3, (
        f"Expected at least 3 lines of output (one per variable), got {len(non_empty)}. "
        "Make sure you print each variable."
    )
    values = {mod.first_name, mod.last_name, mod.city}
    for val in values:
        assert val in non_empty, (
            f"Expected to find {val!r} in the output, but it wasn't there. "
            "Print each variable with print(variable_name)."
        )


if __name__ == "__main__":
    mod, lines = _load()
    for line in lines:
        print(line)
