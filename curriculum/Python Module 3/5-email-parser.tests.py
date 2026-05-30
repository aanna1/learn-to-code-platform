import sys
import importlib


def _load():
    if "submission" in sys.modules:
        importlib.reload(sys.modules["submission"])
        return sys.modules["submission"]
    import submission
    return submission


_sub = _load()


def test_basic_valid_email():
    """parse_email('  Ada.Lovelace@Example.COM  ') returns the correct summary"""
    result = _sub.parse_email("  Ada.Lovelace@Example.COM  ")
    expected = "username: ada.lovelace | domain: example.com | tld: com"
    assert result == expected, (
        f"Expected {expected!r}, got {result!r}. "
        "Make sure you strip whitespace and lowercase before splitting."
    )


def test_subdomain_email():
    """parse_email('user@subdomain.example.org') extracts tld 'org'"""
    result = _sub.parse_email("user@subdomain.example.org")
    expected = "username: user | domain: subdomain.example.org | tld: org"
    assert result == expected, (
        f"Expected {expected!r}, got {result!r}. "
        "The TLD is everything after the *last* dot — use domain.split('.')[-1]."
    )


def test_no_at_sign():
    """parse_email('notanemail') returns 'invalid'"""
    result = _sub.parse_email("notanemail")
    assert result == "invalid", (
        f"'notanemail' has no '@', so parse_email should return 'invalid', got {result!r}. "
        "Use .count('@') to check for exactly one '@'."
    )


def test_multiple_at_signs():
    """parse_email('two@@ats.com') returns 'invalid'"""
    result = _sub.parse_email("two@@ats.com")
    assert result == "invalid", (
        f"'two@@ats.com' has two '@' signs, so parse_email should return 'invalid', got {result!r}. "
        "Check that .count('@') == 1, not just > 0."
    )


def test_no_dot_in_domain():
    """parse_email('user@nodomain') returns 'invalid'"""
    result = _sub.parse_email("user@nodomain")
    assert result == "invalid", (
        f"'user@nodomain' has no '.' in the domain, so it should return 'invalid', got {result!r}. "
        "Check that '.' is in the domain before trying to extract the TLD."
    )


def test_strips_whitespace():
    """Leading/trailing whitespace is stripped before processing"""
    result = _sub.parse_email("   hello@world.net   ")
    expected = "username: hello | domain: world.net | tld: net"
    assert result == expected, (
        f"Expected {expected!r} after stripping spaces, got {result!r}. "
        "Call .strip() before anything else."
    )


def test_lowercases():
    """Uppercase input is lowercased in the output"""
    result = _sub.parse_email("USER@EXAMPLE.COM")
    assert "username: user" in result, (
        f"Username should be lowercased. Got {result!r}."
    )
    assert "domain: example.com" in result, (
        f"Domain should be lowercased. Got {result!r}."
    )


def test_returns_string():
    """parse_email returns a string, not None"""
    result = _sub.parse_email("a@b.com")
    assert result is not None, (
        "parse_email returned None. Use 'return', not 'print', inside the function."
    )
    assert isinstance(result, str), (
        f"parse_email should return a str, got {type(result).__name__!r}."
    )
