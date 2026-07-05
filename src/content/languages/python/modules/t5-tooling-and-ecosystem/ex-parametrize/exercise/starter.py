ABSOLUTE_ZERO = -273.15


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit. Raise ValueError if c < -273.15 (absolute zero)."""
    if c < ABSOLUTE_ZERO:
        raise ValueError(f"{c} is below absolute zero ({ABSOLUTE_ZERO}°C)")
    return c * 9 / 5 + 32


def parse_temp(s: str) -> float:
    """Parse '23.5C' or '74.3F' into a Celsius float.

    Raises ValueError if the string does not end with 'C' or 'F',
    or if the numeric part cannot be parsed.
    """
    if not s or s[-1] not in ("C", "F"):
        raise ValueError(f"expected a string ending in 'C' or 'F', got {s!r}")
    try:
        value = float(s[:-1])
    except ValueError:
        raise ValueError(f"could not parse numeric part of {s!r}")
    if s[-1] == "F":
        value = (value - 32) * 5 / 9
    return value


# ── Helpers ──────────────────────────────────────────────────────────────────

def assert_raises(exc_type, fn, *args, **kwargs):
    """Call fn(*args, **kwargs) and assert it raises exc_type."""
    try:
        fn(*args, **kwargs)
        assert False, f"Expected {exc_type.__name__} but no exception was raised"
    except exc_type:
        pass


# ── Write your tests below ────────────────────────────────────────────────────

# Cases for Part 1 — fill in the expected values
cases = [
    (0,    None),   # replace None with the expected Fahrenheit value
    (100,  None),
    (-40,  None),
    (37,   None),
]

def check_celsius_to_fahrenheit(c, expected):
    # assert that celsius_to_fahrenheit(c) is close to expected
    # hint: use abs(result - expected) < 0.01 to handle floating-point noise
    pass


def test_celsius_conversions():
    # loop over cases and call check_celsius_to_fahrenheit(c, expected) for each
    pass


def test_celsius_to_fahrenheit_invalid():
    # c = -300 is below absolute zero — should raise ValueError
    pass


def test_parse_temp_invalid():
    # "hot" has no unit suffix — should raise ValueError
    pass


# ── Runner (do not edit) ──────────────────────────────────────────────────────
if __name__ == "__main__":
    for c, expected in cases:
        label = f"check_celsius_to_fahrenheit[{c}]"
        try:
            check_celsius_to_fahrenheit(c, expected)
            print(f"PASS  {label}")
        except AssertionError as e:
            print(f"FAIL  {label}: {e}")
        except Exception as e:
            print(f"ERROR {label}: {type(e).__name__}: {e}")

    for fn in [test_celsius_to_fahrenheit_invalid, test_parse_temp_invalid]:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            print(f"FAIL  {fn.__name__}: {e}")
        except Exception as e:
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
