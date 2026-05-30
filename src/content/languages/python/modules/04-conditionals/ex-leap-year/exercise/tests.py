from submission import is_leap_year


def test_divisible_by_4():
    """is_leap_year(2024) is True — divisible by 4, not by 100"""
    assert is_leap_year(2024) is True, (
        f"is_leap_year(2024) should be True, got {is_leap_year(2024)!r}. "
        "2024 is divisible by 4 and not by 100, so it's a leap year."
    )


def test_not_divisible_by_4():
    """is_leap_year(2023) is False — not divisible by 4"""
    assert is_leap_year(2023) is False, (
        f"is_leap_year(2023) should be False, got {is_leap_year(2023)!r}. "
        "2023 % 4 is not 0, so it can't be a leap year."
    )


def test_divisible_by_100_not_400():
    """is_leap_year(1900) is False — divisible by 100 but not 400"""
    assert is_leap_year(1900) is False, (
        f"is_leap_year(1900) should be False, got {is_leap_year(1900)!r}. "
        "1900 is divisible by 100 but not by 400, so it is NOT a leap year. "
        "This is the century exception — make sure your condition handles it."
    )


def test_divisible_by_400():
    """is_leap_year(2000) is True — divisible by 400"""
    assert is_leap_year(2000) is True, (
        f"is_leap_year(2000) should be True, got {is_leap_year(2000)!r}. "
        "2000 is divisible by 400, so the century rule is overridden and it IS "
        "a leap year. If you got False, your 400 case is missing."
    )


def test_another_century_non_leap():
    """is_leap_year(2100) is False — divisible by 100 but not 400"""
    assert is_leap_year(2100) is False, (
        f"is_leap_year(2100) should be False, got {is_leap_year(2100)!r}."
    )


def test_returns_bool():
    """is_leap_year returns an actual boolean"""
    result = is_leap_year(2024)
    assert isinstance(result, bool), (
        f"is_leap_year should return a bool (True/False), got "
        f"{type(result).__name__}. A comparison like year % 4 == 0 already "
        "produces a bool — return that directly rather than 1 or 0."
    )
