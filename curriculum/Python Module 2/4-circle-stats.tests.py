import math
from submission import circle_stats


def test_radius_five():
    """circle_stats(5) returns (78.54, 31.42)"""
    area, circ = circle_stats(5)
    assert area == 78.54, (
        f"Area for radius 5 should be 78.54, got {area!r}. "
        "Formula: round(math.pi * 5 ** 2, 2)"
    )
    assert circ == 31.42, (
        f"Circumference for radius 5 should be 31.42, got {circ!r}. "
        "Formula: round(2 * math.pi * 5, 2)"
    )


def test_radius_one():
    """circle_stats(1) returns (3.14, 6.28)"""
    area, circ = circle_stats(1)
    assert area == 3.14, (
        f"Area for radius 1 should be 3.14, got {area!r}."
    )
    assert circ == 6.28, (
        f"Circumference for radius 1 should be 6.28, got {circ!r}."
    )


def test_radius_zero():
    """circle_stats(0) returns (0.0, 0.0)"""
    area, circ = circle_stats(0)
    assert area == 0.0, f"Area for radius 0 should be 0.0, got {area!r}."
    assert circ == 0.0, f"Circumference for radius 0 should be 0.0, got {circ!r}."


def test_float_radius():
    """circle_stats(2.5) returns (19.63, 15.71)"""
    area, circ = circle_stats(2.5)
    assert area == 19.63, (
        f"Area for radius 2.5 should be 19.63, got {area!r}."
    )
    assert circ == 15.71, (
        f"Circumference for radius 2.5 should be 15.71, got {circ!r}."
    )


def test_returns_tuple():
    """circle_stats returns a tuple of two values"""
    result = circle_stats(5)
    assert isinstance(result, tuple) and len(result) == 2, (
        f"circle_stats should return a tuple of (area, circumference), got {result!r}."
    )


def test_uses_math_pi():
    """area and circumference are computed with math.pi, not 3.14"""
    area, circ = circle_stats(10)
    expected_area = round(math.pi * 100, 2)
    assert area == expected_area, (
        f"Area for radius 10 should be {expected_area} (using math.pi), got {area!r}. "
        "Make sure you're using math.pi, not an approximation like 3.14."
    )


if __name__ == "__main__":
    for r in [5, 1, 0, 2.5, 10]:
        print(f"circle_stats({r}) -> {circle_stats(r)}")
