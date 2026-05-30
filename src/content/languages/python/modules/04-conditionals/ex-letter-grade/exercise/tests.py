from submission import letter_grade


def test_high_a():
    """letter_grade(95) returns 'A'"""
    assert letter_grade(95) == "A", (
        f"letter_grade(95) should return 'A', got {letter_grade(95)!r}. "
        "If you got 'C' or 'D', your elif order is wrong — check the highest "
        "threshold first."
    )


def test_boundary_90_is_a():
    """letter_grade(90) returns 'A' — boundary lands in the higher grade"""
    assert letter_grade(90) == "A", (
        f"letter_grade(90) should return 'A', got {letter_grade(90)!r}. "
        "Use >= 90, not > 90, so 90 itself counts as an A."
    )


def test_b():
    """letter_grade(82) returns 'B'"""
    assert letter_grade(82) == "B", (
        f"letter_grade(82) should return 'B', got {letter_grade(82)!r}."
    )


def test_boundary_80_is_b():
    """letter_grade(80) returns 'B'"""
    assert letter_grade(80) == "B", (
        f"letter_grade(80) should return 'B', got {letter_grade(80)!r}. "
        "Boundaries belong to the higher grade — use >= 80."
    )


def test_c():
    """letter_grade(75) returns 'C'"""
    assert letter_grade(75) == "C", (
        f"letter_grade(75) should return 'C', got {letter_grade(75)!r}."
    )


def test_d():
    """letter_grade(60) returns 'D'"""
    assert letter_grade(60) == "D", (
        f"letter_grade(60) should return 'D', got {letter_grade(60)!r}. "
        "60 through 69 is a D; use >= 60 for the D branch."
    )


def test_f():
    """letter_grade(45) returns 'F'"""
    assert letter_grade(45) == "F", (
        f"letter_grade(45) should return 'F', got {letter_grade(45)!r}. "
        "Anything below 60 is an F — that's the else branch."
    )


def test_f_at_zero():
    """letter_grade(0) returns 'F'"""
    assert letter_grade(0) == "F", (
        f"letter_grade(0) should return 'F', got {letter_grade(0)!r}."
    )
