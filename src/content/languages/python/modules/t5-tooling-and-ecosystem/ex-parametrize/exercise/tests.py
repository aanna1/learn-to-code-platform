"""
Grader for ex-parametrize.

Checks:
1. cases list has all four correct (c, expected) pairs.
2. check_celsius_to_fahrenheit passes with the correct function and catches a wrong one.
3. test_celsius_to_fahrenheit_invalid catches a function that omits the validation.
4. test_parse_temp_invalid catches a function that accepts any string.
"""

import submission as sub


# ── Good / broken implementations ────────────────────────────────────────────

def _good_c2f(c):
    if c < -273.15:
        raise ValueError(f"{c} below absolute zero")
    return c * 9 / 5 + 32


def _broken_c2f_wrong_result(c):
    """Returns the wrong formula — catches assertion errors in check_celsius_to_fahrenheit."""
    if c < -273.15:
        raise ValueError()
    return c * 9 / 5  # missing +32


def _broken_c2f_no_validation(c):
    """No validation — should cause test_celsius_to_fahrenheit_invalid to catch it."""
    return c * 9 / 5 + 32


def _broken_parse_no_validation(s):
    """Accepts any string — should cause test_parse_temp_invalid to catch it."""
    return 0.0


# ── Helpers ───────────────────────────────────────────────────────────────────

def _patch(name, replacement):
    """Context manager to temporarily replace a name in the submission module."""
    import contextlib
    @contextlib.contextmanager
    def _ctx():
        original = getattr(sub, name)
        setattr(sub, name, replacement)
        try:
            yield
        finally:
            setattr(sub, name, original)
    return _ctx()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_cases_has_four_entries():
    """cases list has exactly 4 entries."""
    assert hasattr(sub, "cases"), "Define a 'cases' list at module level."
    assert len(sub.cases) == 4, (
        f"cases should have 4 entries, got {len(sub.cases)}. "
        "Include (0,32.0), (100,212.0), (-40,-40.0), (37,98.6)."
    )


def test_cases_contains_correct_values():
    """cases contains the correct (c, expected) pairs."""
    assert hasattr(sub, "cases"), "Define a 'cases' list at module level."
    expected_map = {0: 32.0, 100: 212.0, -40: -40.0, 37: 98.6}
    for c, expected in sub.cases:
        if expected is None:
            assert False, (
                f"cases entry ({c}, None) still has a placeholder None. "
                "Replace None with the correct Fahrenheit value."
            )
        assert c in expected_map, f"Unexpected c value {c!r} in cases."
        correct = expected_map[c]
        assert abs(expected - correct) < 0.01, (
            f"cases entry ({c!r}, {expected!r}): expected value should be ~{correct}, "
            f"got {expected}."
        )


def test_check_celsius_to_fahrenheit_passes_good_impl():
    """check_celsius_to_fahrenheit passes with a correct implementation."""
    with _patch("celsius_to_fahrenheit", _good_c2f):
        for c, expected in sub.cases:
            if expected is None:
                continue
            try:
                sub.check_celsius_to_fahrenheit(c, expected)
            except AssertionError as e:
                assert False, (
                    f"check_celsius_to_fahrenheit({c!r}, {expected!r}) should pass "
                    f"with a correct implementation, but failed: {e}"
                )


def test_check_celsius_to_fahrenheit_catches_wrong_formula():
    """check_celsius_to_fahrenheit catches an implementation that returns the wrong value."""
    caught = False
    with _patch("celsius_to_fahrenheit", _broken_c2f_wrong_result):
        for c, expected in sub.cases:
            if expected is None:
                continue
            try:
                sub.check_celsius_to_fahrenheit(c, expected)
            except AssertionError:
                caught = True
                break
    assert caught, (
        "check_celsius_to_fahrenheit should FAIL when celsius_to_fahrenheit returns wrong results "
        "(c * 9/5 with no +32), but all cases passed. "
        "Make sure you assert abs(result - expected) < 0.01."
    )


def test_test_celsius_to_fahrenheit_invalid_exists():
    """test_celsius_to_fahrenheit_invalid is defined."""
    assert callable(getattr(sub, "test_celsius_to_fahrenheit_invalid", None)), (
        "Define test_celsius_to_fahrenheit_invalid()."
    )


def test_test_celsius_to_fahrenheit_invalid_passes_good_impl():
    """test_celsius_to_fahrenheit_invalid passes when validation is present."""
    with _patch("celsius_to_fahrenheit", _good_c2f):
        try:
            sub.test_celsius_to_fahrenheit_invalid()
        except AssertionError as e:
            assert False, (
                f"test_celsius_to_fahrenheit_invalid should pass when ValueError is raised "
                f"for c=-300, but got: {e}"
            )


def test_test_celsius_to_fahrenheit_invalid_catches_missing_validation():
    """test_celsius_to_fahrenheit_invalid catches an implementation with no validation."""
    with _patch("celsius_to_fahrenheit", _broken_c2f_no_validation):
        try:
            sub.test_celsius_to_fahrenheit_invalid()
            assert False, (
                "test_celsius_to_fahrenheit_invalid should FAIL when the function does not "
                "raise ValueError for c=-300, but it passed. "
                "Use try/except ValueError and add assert False after the risky call."
            )
        except AssertionError as e:
            # This AssertionError is the expected failure — but re-raise if it came from us
            if "should FAIL" in str(e):
                raise


def test_parse_temp_invalid_exists():
    """test_parse_temp_invalid is defined."""
    assert callable(getattr(sub, "test_parse_temp_invalid", None)), (
        "Define test_parse_temp_invalid()."
    )


def test_parse_temp_invalid_passes_good_impl():
    """test_parse_temp_invalid passes when parse_temp raises ValueError for 'hot'."""
    try:
        sub.test_parse_temp_invalid()
    except AssertionError as e:
        assert False, (
            f"test_parse_temp_invalid should pass when parse_temp('hot') raises ValueError, "
            f"but got: {e}"
        )


def test_parse_temp_invalid_catches_missing_validation():
    """test_parse_temp_invalid catches a parse_temp that accepts any string."""
    with _patch("parse_temp", _broken_parse_no_validation):
        try:
            sub.test_parse_temp_invalid()
            assert False, (
                "test_parse_temp_invalid should FAIL when parse_temp accepts 'hot' without "
                "raising, but it passed. "
                "Use try/except ValueError and add assert False after the risky call."
            )
        except AssertionError as e:
            if "should FAIL" in str(e):
                raise


if __name__ == "__main__":
    print(celsius_to_fahrenheit(0))
    print(celsius_to_fahrenheit(100))
    print(parse_temp("23.5C"))
    print(parse_temp("74.3F"))
