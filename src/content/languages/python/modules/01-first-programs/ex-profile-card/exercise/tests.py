import io
import contextlib


def _output():
    """Run the learner's main() and capture the lines it prints."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main()
    return [line for line in buf.getvalue().splitlines() if line.strip()]


def test_name_line():
    "prints 'Name: Ada Lovelace'"
    assert "Name: Ada Lovelace" in _output(), (
        "Expected a line exactly equal to 'Name: Ada Lovelace'. "
        "Use an f-string: f\"Name: {first_name} {last_name}\"."
    )


def test_age_line():
    "prints 'Age: 36'"
    assert "Age: 36" in _output(), (
        "Expected a line exactly equal to 'Age: 36'. Use an f-string: f\"Age: {age}\"."
    )


def test_language_line():
    "prints 'Language: Python'"
    assert "Language: Python" in _output(), (
        "Expected a line exactly equal to 'Language: Python'. "
        "Use an f-string: f\"Language: {language}\"."
    )


def test_bio_line():
    "prints the full Bio line with all three substitutions"
    expected = "Bio: Ada Lovelace has been coding in Python for years."
    assert expected in _output(), (
        f"Expected a line exactly equal to: {expected!r}. "
        "Reference first_name, last_name, and language in one f-string."
    )
