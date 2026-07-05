from submission import safe_divide


def test_returns_correct_quotient():
    """safe_divide returns the correct numeric result."""
    assert safe_divide(10, 2) == 5.0, (
        f"safe_divide(10, 2) should be 5.0, got {safe_divide(10, 2)!r}"
    )
    assert safe_divide(9, 3) == 3.0, (
        f"safe_divide(9, 3) should be 3.0, got {safe_divide(9, 3)!r}"
    )


def test_returns_float_result():
    """safe_divide handles non-integer results."""
    result = safe_divide(7, 2)
    assert result == 3.5, (
        f"safe_divide(7, 2) should be 3.5, got {result!r}"
    )


def test_zero_numerator():
    """safe_divide(0, b) returns 0.0, not an error."""
    result = safe_divide(0, 5)
    assert result == 0.0, (
        f"safe_divide(0, 5) should be 0.0, got {result!r}. "
        "A zero numerator is valid — only a zero denominator raises ValueError."
    )


def test_raises_value_error_for_zero_denominator():
    """safe_divide raises ValueError when b is zero."""
    raised = False
    try:
        safe_divide(10, 0)
    except ValueError:
        raised = True
    assert raised, (
        "safe_divide(10, 0) should raise ValueError, but no exception was raised. "
        "Add: if b == 0: raise ValueError('Cannot divide by zero')"
    )


def test_error_message():
    """ValueError message is 'Cannot divide by zero'."""
    try:
        safe_divide(10, 0)
    except ValueError as e:
        assert str(e) == "Cannot divide by zero", (
            f"ValueError message should be 'Cannot divide by zero', got {str(e)!r}"
        )
        return
    assert False, "safe_divide(10, 0) should raise ValueError"


def test_negative_numbers():
    """safe_divide works with negative inputs."""
    assert safe_divide(-6, 2) == -3.0, (
        f"safe_divide(-6, 2) should be -3.0, got {safe_divide(-6, 2)!r}"
    )
    assert safe_divide(6, -2) == -3.0, (
        f"safe_divide(6, -2) should be -3.0, got {safe_divide(6, -2)!r}"
    )


if __name__ == "__main__":
    print(safe_divide(10, 2))
