from submission import filter_numbers


def test_skips_negatives():
    """Negative values are skipped with continue"""
    result = filter_numbers([-1, -5, -100])
    assert result == [], (
        f"All-negative input should return [], got {result}. "
        "Negative values should be skipped with continue."
    )


def test_stops_at_over_100():
    """Stops when a value > 100 is encountered; that value is not included"""
    result = filter_numbers([10, 200, 20])
    assert result == [10], (
        f"filter_numbers([10, 200, 20]) should return [10]. "
        f"200 triggers break; 20 is never reached. Got {result}."
    )


def test_basic_mixed():
    """Skips negatives and stops at > 100 in a mixed list"""
    result = filter_numbers([3, -1, 7, -4, 200, 9])
    assert result == [3, 7], (
        f"filter_numbers([3, -1, 7, -4, 200, 9]) should return [3, 7], got {result}. "
        "-1 and -4 are skipped; 200 stops the loop; 9 is never reached."
    )


def test_no_negatives_no_large():
    """Keeps all values when none are negative or > 100"""
    result = filter_numbers([10, 20, 30])
    assert result == [10, 20, 30], (
        f"filter_numbers([10, 20, 30]) should return [10, 20, 30], got {result}."
    )


def test_empty_list():
    """Empty input returns empty list"""
    result = filter_numbers([])
    assert result == [], (
        f"filter_numbers([]) should return [], got {result}."
    )


def test_exactly_100_is_kept():
    """100 itself is included — the stop condition is > 100, not >= 100"""
    result = filter_numbers([50, 100, 200])
    assert result == [50, 100], (
        f"filter_numbers([50, 100, 200]) should return [50, 100]. "
        f"100 is not > 100, so it's included. Got {result}."
    )
