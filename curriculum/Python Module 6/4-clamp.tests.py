def test_in_range():
    "values already in range are returned unchanged"
    assert clamp(7, 0, 10) == 7, (
        f"clamp(7, 0, 10) should return 7, got {clamp(7, 0, 10)!r}"
    )
    assert clamp(5, 1, 9) == 5, (
        f"clamp(5, 1, 9) should return 5, got {clamp(5, 1, 9)!r}"
    )


def test_below_low():
    "values below low are clamped to low"
    assert clamp(-3, 0, 10) == 0, (
        f"clamp(-3, 0, 10) should return 0 (the low boundary), got {clamp(-3, 0, 10)!r}"
    )
    assert clamp(-100, 0, 10) == 0, (
        f"clamp(-100, 0, 10) should return 0, got {clamp(-100, 0, 10)!r}"
    )


def test_above_high():
    "values above high are clamped to high"
    assert clamp(15, 0, 10) == 10, (
        f"clamp(15, 0, 10) should return 10 (the high boundary), got {clamp(15, 0, 10)!r}"
    )
    assert clamp(999, 0, 10) == 10, (
        f"clamp(999, 0, 10) should return 10, got {clamp(999, 0, 10)!r}"
    )


def test_on_low_boundary():
    "a value equal to low is in range and returned as-is"
    assert clamp(0, 0, 10) == 0, (
        f"clamp(0, 0, 10) should return 0 — the boundary is inclusive, got {clamp(0, 0, 10)!r}"
    )


def test_on_high_boundary():
    "a value equal to high is in range and returned as-is"
    assert clamp(10, 0, 10) == 10, (
        f"clamp(10, 0, 10) should return 10 — the boundary is inclusive, got {clamp(10, 0, 10)!r}"
    )


def test_returns_number():
    "clamp returns a number, not None"
    result = clamp(5, 0, 10)
    assert result is not None, (
        "clamp returned None. Did you forget to return the value? Make sure you use return, not print."
    )
    assert isinstance(result, (int, float)), (
        f"clamp should return a number, got {type(result).__name__!r}"
    )
