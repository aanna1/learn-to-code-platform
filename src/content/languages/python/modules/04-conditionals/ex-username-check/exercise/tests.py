from submission import check_username


def test_empty():
    """check_username('') reports empty"""
    assert check_username("") == "Username cannot be empty.", (
        f"check_username('') should return 'Username cannot be empty.', got "
        f"{check_username('')!r}. Check the empty case first — an empty string "
        "is falsy, so 'if not name:' catches it."
    )


def test_too_short():
    """check_username('ab') reports too short"""
    assert check_username("ab") == "Username is too short.", (
        f"check_username('ab') should return 'Username is too short.', got "
        f"{check_username('ab')!r}. Use len(name) < 3."
    )


def test_boundary_length_three_ok():
    """check_username('abc') is valid — 3 characters passes"""
    assert check_username("abc") == "Username is valid.", (
        f"check_username('abc') should return 'Username is valid.', got "
        f"{check_username('abc')!r}. Three characters is allowed — use < 3, "
        "not <= 3, for the too-short check."
    )


def test_contains_space():
    """check_username('a b c') reports spaces"""
    assert check_username("a b c") == "Username cannot contain spaces.", (
        f"check_username('a b c') should return 'Username cannot contain "
        f"spaces.', got {check_username('a b c')!r}. Use ' ' in name."
    )


def test_valid():
    """check_username('ada') is valid"""
    assert check_username("ada") == "Username is valid.", (
        f"check_username('ada') should return 'Username is valid.', got "
        f"{check_username('ada')!r}."
    )


def test_empty_takes_priority_over_length():
    """An empty string reports empty, not too short"""
    assert check_username("") == "Username cannot be empty.", (
        f"check_username('') should report empty, got {check_username('')!r}. "
        "An empty string is also shorter than 3, so the empty check must come "
        "FIRST in the chain to win."
    )


def test_short_with_space_reports_short_first():
    """'a ' is checked for length before spaces"""
    assert check_username("a ") == "Username is too short.", (
        f"check_username('a ') should return 'Username is too short.', got "
        f"{check_username('a ')!r}. 'a ' is 2 characters, so the length check "
        "fires before the space check — order in the chain decides which "
        "message wins."
    )
