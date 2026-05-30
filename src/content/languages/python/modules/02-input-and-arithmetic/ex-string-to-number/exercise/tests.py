

def test_returns_int_for_whole_number():
    """parse_number returns int for a string without a decimal point"""
    result = parse_number("42")
    assert result == 42, f"parse_number('42') should return 42, got {result!r}"
    assert isinstance(result, int), (
        f"parse_number('42') should return an int, got {type(result).__name__}. "
        "Use int() for strings without a decimal point, not float()."
    )


def test_returns_float_for_decimal_string():
    """parse_number returns float for a string with a decimal point"""
    result = parse_number("3.14")
    assert abs(result - 3.14) < 1e-9, f"parse_number('3.14') should return 3.14, got {result!r}"
    assert isinstance(result, float), (
        f"parse_number('3.14') should return a float, got {type(result).__name__}. "
        "Use float() for strings that contain a decimal point."
    )


def test_handles_negative_integer():
    """parse_number handles a negative integer string"""
    result = parse_number("-7")
    assert result == -7, f"parse_number('-7') should return -7, got {result!r}"
    assert isinstance(result, int), (
        f"parse_number('-7') should return an int, got {type(result).__name__}."
    )


def test_handles_negative_float():
    """parse_number handles a negative float string"""
    result = parse_number("-2.5")
    assert abs(result - (-2.5)) < 1e-9, f"parse_number('-2.5') should return -2.5, got {result!r}"
    assert isinstance(result, float), (
        f"parse_number('-2.5') should return a float, got {type(result).__name__}."
    )


def test_zero_without_decimal_is_int():
    """parse_number returns int for '0'"""
    result = parse_number("0")
    assert result == 0, f"parse_number('0') should return 0, got {result!r}"
    assert isinstance(result, int), (
        f"parse_number('0') should return an int, got {type(result).__name__}."
    )


def test_zero_with_decimal_is_float():
    """parse_number returns float for '0.0'"""
    result = parse_number("0.0")
    assert isinstance(result, float), (
        f"parse_number('0.0') should return a float, got {type(result).__name__}. "
        "A decimal point means float, even when the value is zero."
    )


if __name__ == "__main__":
    for s in ["42", "3.14", "-7", "-2.5", "0", "0.0"]:
        r = parse_number(s)
        print(f"parse_number({s!r}) -> {r!r} ({type(r).__name__})")
