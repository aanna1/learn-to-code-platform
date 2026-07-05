ABSOLUTE_ZERO = -273.15


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit. Raise ValueError if c < -273.15 (absolute zero)."""
    if c < ABSOLUTE_ZERO:
        raise ValueError(f"{c} is below absolute zero ({ABSOLUTE_ZERO}°C)")
    return c * 9 / 5 + 32


def parse_temp(s: str) -> float:
    """Parse '23.5C' or '74.3F' into a Celsius float."""
    if not s or s[-1] not in ("C", "F"):
        raise ValueError(f"expected a string ending in 'C' or 'F', got {s!r}")
    try:
        value = float(s[:-1])
    except ValueError:
        raise ValueError(f"could not parse numeric part of {s!r}")
    if s[-1] == "F":
        value = (value - 32) * 5 / 9
    return value


def assert_raises(exc_type, fn, *args, **kwargs):
    """Call fn(*args, **kwargs) and assert it raises exc_type."""
    try:
        fn(*args, **kwargs)
        assert False, f"Expected {exc_type.__name__} but no exception was raised"
    except exc_type:
        pass


cases = [
    (0,    32.0),
    (100,  212.0),
    (-40,  -40.0),
    (37,   98.6),
]


def check_celsius_to_fahrenheit(c, expected):
    result = celsius_to_fahrenheit(c)
    assert abs(result - expected) < 0.01, (
        f"celsius_to_fahrenheit({c}) returned {result}, expected {expected}"
    )


def test_celsius_conversions():
    for c, expected in cases:
        check_celsius_to_fahrenheit(c, expected)


def test_celsius_to_fahrenheit_invalid():
    assert_raises(ValueError, celsius_to_fahrenheit, -300)


def test_parse_temp_invalid():
    assert_raises(ValueError, parse_temp, "hot")


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
