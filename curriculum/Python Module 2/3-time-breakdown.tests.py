from submission import format_time


def test_basic_case():
    """format_time(200) returns '3:20'"""
    assert format_time(200) == "3:20", (
        f"format_time(200) should return '3:20', got {format_time(200)!r}. "
        "200 // 60 is 3 minutes; 200 % 60 is 20 seconds."
    )


def test_exact_minute():
    """format_time(60) returns '1:00'"""
    assert format_time(60) == "1:00", (
        f"format_time(60) should return '1:00', got {format_time(60)!r}. "
        "60 seconds is exactly 1 minute with 0 seconds left over."
    )


def test_zero_seconds():
    """format_time(0) returns '0:00'"""
    assert format_time(0) == "0:00", (
        f"format_time(0) should return '0:00', got {format_time(0)!r}."
    )


def test_single_digit_seconds_padded():
    """format_time(9) returns '0:09', not '0:9'"""
    assert format_time(9) == "0:09", (
        f"format_time(9) should return '0:09', got {format_time(9)!r}. "
        "Single-digit seconds must be padded with a leading zero. Use :02d in your f-string."
    )


def test_minutes_not_capped():
    """format_time(3661) returns '61:01' — minutes are not capped at 60"""
    assert format_time(3661) == "61:01", (
        f"format_time(3661) should return '61:01', got {format_time(3661)!r}. "
        "This function only splits into minutes and seconds — it does not split hours out."
    )


def test_returns_string():
    """format_time returns a string"""
    result = format_time(200)
    assert isinstance(result, str), (
        f"format_time should return a string, got {type(result).__name__}. "
        "Use an f-string to build the return value."
    )


if __name__ == "__main__":
    for s in [200, 60, 0, 9, 3661]:
        print(f"format_time({s}) -> {format_time(s)!r}")
