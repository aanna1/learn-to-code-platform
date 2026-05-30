def test_a_grade():
    "scores of 90 and above return 'A'"
    assert letter_grade(90) == "A", (
        f"letter_grade(90) should return 'A', got {letter_grade(90)!r}. "
        "The boundary belongs to the higher grade."
    )
    assert letter_grade(95) == "A", (
        f"letter_grade(95) should return 'A', got {letter_grade(95)!r}"
    )
    assert letter_grade(100) == "A", (
        f"letter_grade(100) should return 'A', got {letter_grade(100)!r}"
    )


def test_b_grade():
    "scores of 80–89 return 'B'"
    assert letter_grade(80) == "B", (
        f"letter_grade(80) should return 'B', got {letter_grade(80)!r}"
    )
    assert letter_grade(85) == "B", (
        f"letter_grade(85) should return 'B', got {letter_grade(85)!r}"
    )
    assert letter_grade(89) == "B", (
        f"letter_grade(89) should return 'B', got {letter_grade(89)!r}"
    )


def test_c_grade():
    "scores of 70–79 return 'C'"
    assert letter_grade(70) == "C", (
        f"letter_grade(70) should return 'C', got {letter_grade(70)!r}"
    )
    assert letter_grade(75) == "C", (
        f"letter_grade(75) should return 'C', got {letter_grade(75)!r}"
    )


def test_d_grade():
    "scores of 60–69 return 'D'"
    assert letter_grade(60) == "D", (
        f"letter_grade(60) should return 'D', got {letter_grade(60)!r}"
    )
    assert letter_grade(65) == "D", (
        f"letter_grade(65) should return 'D', got {letter_grade(65)!r}"
    )


def test_f_grade():
    "scores below 60 return 'F'"
    assert letter_grade(59) == "F", (
        f"letter_grade(59) should return 'F', got {letter_grade(59)!r}"
    )
    assert letter_grade(0) == "F", (
        f"letter_grade(0) should return 'F', got {letter_grade(0)!r}"
    )


def test_returns_string():
    "letter_grade returns a string, not None"
    result = letter_grade(75)
    assert result is not None, (
        "letter_grade returned None. Did you forget to return the grade? "
        "Make sure you use return, not print."
    )
    assert isinstance(result, str), (
        f"letter_grade should return a string like 'A' or 'B', got {type(result).__name__!r}"
    )
