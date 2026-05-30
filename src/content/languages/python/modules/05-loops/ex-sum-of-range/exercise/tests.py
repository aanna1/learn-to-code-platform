from submission import sum_range


def test_sum_one_to_five():
    """sum_range(1, 5) returns 15"""
    result = sum_range(1, 5)
    assert result == 15, (
        f"sum_range(1, 5) should return 15 (1+2+3+4+5), got {result}. "
        "If you got 10, you're missing 5 — check that stop is included."
    )


def test_sum_includes_stop():
    """sum_range(1, 4) returns 10 — confirming stop is included"""
    result = sum_range(1, 4)
    assert result == 10, (
        f"sum_range(1, 4) should return 10 (1+2+3+4), got {result}. "
        "If you got 6, your range stops before stop. Use range(start, stop + 1)."
    )


def test_single_value():
    """sum_range(3, 3) returns 3"""
    result = sum_range(3, 3)
    assert result == 3, (
        f"sum_range(3, 3) should return 3, got {result}. "
        "When start equals stop, the sum is just that one value."
    )


def test_sum_one_to_hundred():
    """sum_range(1, 100) returns 5050"""
    result = sum_range(1, 100)
    assert result == 5050, (
        f"sum_range(1, 100) should return 5050, got {result}."
    )


def test_non_one_start():
    """sum_range(5, 8) returns 26"""
    result = sum_range(5, 8)
    assert result == 26, (
        f"sum_range(5, 8) should return 26 (5+6+7+8), got {result}."
    )
