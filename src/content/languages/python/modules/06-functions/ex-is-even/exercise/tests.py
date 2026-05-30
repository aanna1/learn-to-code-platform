def test_even_positive():
    "is_even returns True for a positive even number"
    assert is_even(4) == True, (
        f"is_even(4) should return True, got {is_even(4)!r}"
    )
    assert is_even(100) == True, (
        f"is_even(100) should return True, got {is_even(100)!r}"
    )


def test_odd_positive():
    "is_even returns False for a positive odd number"
    assert is_even(7) == False, (
        f"is_even(7) should return False, got {is_even(7)!r}"
    )
    assert is_even(1) == False, (
        f"is_even(1) should return False, got {is_even(1)!r}"
    )


def test_zero():
    "is_even returns True for zero"
    assert is_even(0) == True, (
        f"is_even(0) should return True — zero is even, got {is_even(0)!r}"
    )


def test_negative_even():
    "is_even returns True for a negative even number"
    assert is_even(-4) == True, (
        f"is_even(-4) should return True, got {is_even(-4)!r}"
    )


def test_negative_odd():
    "is_even returns False for a negative odd number"
    assert is_even(-3) == False, (
        f"is_even(-3) should return False, got {is_even(-3)!r}"
    )


def test_returns_bool():
    "is_even returns a bool, not a string or int"
    result = is_even(2)
    assert isinstance(result, bool), (
        f"is_even should return a bool (True or False), got {type(result).__name__!r}. "
        "Make sure you're returning the result of the comparison, not printing it or returning a string."
    )
