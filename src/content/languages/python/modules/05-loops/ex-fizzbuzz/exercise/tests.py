from submission import fizzbuzz


def test_full_sequence_to_15():
    """fizzbuzz(15) returns the classic FizzBuzz sequence"""
    expected = [
        "1", "2", "Fizz", "4", "Buzz",
        "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]
    result = fizzbuzz(15)
    assert result == expected, (
        f"fizzbuzz(15) returned wrong output.\n"
        f"Expected: {expected}\n"
        f"Got:      {result}"
    )


def test_length():
    """fizzbuzz(10) returns exactly 10 items"""
    result = fizzbuzz(10)
    assert len(result) == 10, (
        f"fizzbuzz(10) should return 10 items, got {len(result)}. "
        "Make sure range(1, n + 1) includes n itself."
    )


def test_fizzbuzz_at_15():
    """15 is 'FizzBuzz' — the combined case must be checked first"""
    result = fizzbuzz(15)
    assert result[14] == "FizzBuzz", (
        f"Position 15 (index 14) should be 'FizzBuzz', got {result[14]!r}. "
        "If you got 'Fizz', you checked divisibility-by-3 before the combined case."
    )


def test_fizz_multiples():
    """Multiples of 3 that aren't multiples of 5 are 'Fizz'"""
    result = fizzbuzz(15)
    assert result[2] == "Fizz", (
        f"Position 3 (index 2) should be 'Fizz', got {result[2]!r}."
    )
    assert result[8] == "Fizz", (
        f"Position 9 (index 8) should be 'Fizz', got {result[8]!r}."
    )


def test_buzz_multiples():
    """Multiples of 5 that aren't multiples of 3 are 'Buzz'"""
    result = fizzbuzz(15)
    assert result[4] == "Buzz", (
        f"Position 5 (index 4) should be 'Buzz', got {result[4]!r}."
    )
    assert result[9] == "Buzz", (
        f"Position 10 (index 9) should be 'Buzz', got {result[9]!r}."
    )


def test_plain_numbers_are_strings():
    """Non-Fizz-Buzz values are strings, not integers"""
    result = fizzbuzz(5)
    assert result[0] == "1", (
        f"Position 1 should be the string '1', not the integer 1. "
        f"Got {result[0]!r}. Use str(i) to convert."
    )
    assert isinstance(result[0], str), (
        "The list must contain strings. Use str(i) for numbers that don't map to Fizz or Buzz."
    )
