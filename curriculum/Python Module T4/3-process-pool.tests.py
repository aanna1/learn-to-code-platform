from submission import count_factors, factor_counts


def test_count_factors_composite():
    """count_factors(12) returns 6 (factors: 1,2,3,4,6,12)."""
    result = count_factors(12)
    assert result == 6, (
        f"count_factors(12) should be 6, got {result}. "
        "Count integers i in [1, 12] where 12 % i == 0."
    )


def test_count_factors_prime():
    """count_factors of a prime returns 2 (only 1 and itself)."""
    result = count_factors(13)
    assert result == 2, (
        f"count_factors(13) should be 2 (13 is prime), got {result}."
    )


def test_count_factors_one():
    """count_factors(1) returns 1."""
    result = count_factors(1)
    assert result == 1, (
        f"count_factors(1) should be 1, got {result}. "
        "The only factor of 1 is 1 itself."
    )


def test_count_factors_perfect_square():
    """count_factors(36) returns 9 (factors: 1,2,3,4,6,9,12,18,36)."""
    result = count_factors(36)
    assert result == 9, (
        f"count_factors(36) should be 9, got {result}."
    )


def test_count_factors_100():
    """count_factors(100) returns 9."""
    result = count_factors(100)
    assert result == 9, (
        f"count_factors(100) should be 9, got {result}."
    )


def test_factor_counts_returns_dict():
    """factor_counts returns a dict."""
    result = factor_counts([12, 13], max_workers=2)
    assert isinstance(result, dict), (
        f"factor_counts should return a dict, got {type(result).__name__}."
    )


def test_factor_counts_correct_values():
    """factor_counts maps each number to its factor count."""
    result = factor_counts([12, 13, 36, 100], max_workers=2)
    assert result[12] == 6, f"result[12] should be 6, got {result.get(12)}"
    assert result[13] == 2, f"result[13] should be 2, got {result.get(13)}"
    assert result[36] == 9, f"result[36] should be 9, got {result.get(36)}"
    assert result[100] == 9, f"result[100] should be 9, got {result.get(100)}"


def test_factor_counts_all_keys_present():
    """factor_counts includes every input number as a key."""
    numbers = [2, 4, 6, 8, 10]
    result = factor_counts(numbers, max_workers=2)
    for n in numbers:
        assert n in result, (
            f"{n} is missing from result dict. "
            "Use zip(numbers, pool.map(...)) to build the dict."
        )


def test_factor_counts_single_item():
    """factor_counts works with a one-element list."""
    result = factor_counts([7], max_workers=1)
    assert result == {7: 2}, (
        f"factor_counts([7]) should be {{7: 2}}, got {result}."
    )


if __name__ == "__main__":
    from submission import count_factors, factor_counts
    print(count_factors(12))
    print(factor_counts([12, 13, 36, 100], max_workers=4))
