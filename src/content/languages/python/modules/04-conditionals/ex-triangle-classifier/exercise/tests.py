from submission import classify_triangle


def test_equilateral():
    """classify_triangle(3, 3, 3) is 'equilateral'"""
    assert classify_triangle(3, 3, 3) == "equilateral", (
        f"classify_triangle(3, 3, 3) should be 'equilateral', got "
        f"{classify_triangle(3, 3, 3)!r}. All three sides equal."
    )


def test_isosceles():
    """classify_triangle(5, 5, 8) is 'isosceles'"""
    assert classify_triangle(5, 5, 8) == "isosceles", (
        f"classify_triangle(5, 5, 8) should be 'isosceles', got "
        f"{classify_triangle(5, 5, 8)!r}. Exactly two sides equal."
    )


def test_isosceles_other_pair():
    """classify_triangle(7, 4, 7) is 'isosceles' — equal pair isn't a and b"""
    assert classify_triangle(7, 4, 7) == "isosceles", (
        f"classify_triangle(7, 4, 7) should be 'isosceles', got "
        f"{classify_triangle(7, 4, 7)!r}. Check all three pairs (a==b, b==c, "
        "a==c), not just the first two sides."
    )


def test_scalene():
    """classify_triangle(3, 4, 5) is 'scalene'"""
    assert classify_triangle(3, 4, 5) == "scalene", (
        f"classify_triangle(3, 4, 5) should be 'scalene', got "
        f"{classify_triangle(3, 4, 5)!r}. No sides equal."
    )


def test_invalid_inequality():
    """classify_triangle(1, 1, 5) is 'invalid' — fails triangle inequality"""
    assert classify_triangle(1, 1, 5) == "invalid", (
        f"classify_triangle(1, 1, 5) should be 'invalid', got "
        f"{classify_triangle(1, 1, 5)!r}. 1 + 1 is not greater than 5, so these "
        "lengths can't form a triangle. Check validity before classifying."
    )


def test_invalid_zero_side():
    """classify_triangle(0, 4, 5) is 'invalid' — zero side"""
    assert classify_triangle(0, 4, 5) == "invalid", (
        f"classify_triangle(0, 4, 5) should be 'invalid', got "
        f"{classify_triangle(0, 4, 5)!r}. A side of 0 can't form a triangle — "
        "every side must be positive."
    )


def test_invalid_negative_side():
    """classify_triangle(-3, 4, 5) is 'invalid' — negative side"""
    assert classify_triangle(-3, 4, 5) == "invalid", (
        f"classify_triangle(-3, 4, 5) should be 'invalid', got "
        f"{classify_triangle(-3, 4, 5)!r}. Negative lengths are invalid."
    )


def test_degenerate_is_invalid():
    """classify_triangle(2, 3, 5) is 'invalid' — sum equals the third side"""
    assert classify_triangle(2, 3, 5) == "invalid", (
        f"classify_triangle(2, 3, 5) should be 'invalid', got "
        f"{classify_triangle(2, 3, 5)!r}. 2 + 3 equals 5 exactly, which is a "
        "flat line, not a triangle. The inequality must be strict (>), so the "
        "invalid test is a + b <= c."
    )


def test_equilateral_not_isosceles():
    """An equilateral triangle is not reported as isosceles"""
    assert classify_triangle(6, 6, 6) == "equilateral", (
        f"classify_triangle(6, 6, 6) should be 'equilateral', got "
        f"{classify_triangle(6, 6, 6)!r}. Check the all-three-equal case BEFORE "
        "the two-equal case, or every equilateral will match isosceles first."
    )
