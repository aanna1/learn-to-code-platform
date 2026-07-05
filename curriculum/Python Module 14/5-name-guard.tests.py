import inspect
from submission import celsius_to_fahrenheit, fahrenheit_to_celsius, main


# ---------------------------------------------------------------------------
# celsius_to_fahrenheit
# ---------------------------------------------------------------------------

def test_c_to_f_freezing():
    """celsius_to_fahrenheit(0) returns 32.0."""
    result = celsius_to_fahrenheit(0)
    assert result == 32.0, (
        f"celsius_to_fahrenheit(0) should be 32.0, got {result!r}. "
        "Formula: c * 9/5 + 32"
    )


def test_c_to_f_boiling():
    """celsius_to_fahrenheit(100) returns 212.0."""
    result = celsius_to_fahrenheit(100)
    assert result == 212.0, (
        f"celsius_to_fahrenheit(100) should be 212.0, got {result!r}."
    )


def test_c_to_f_negative_forty():
    """celsius_to_fahrenheit(-40) returns -40.0 — the crossover point."""
    result = celsius_to_fahrenheit(-40)
    assert result == -40.0, (
        f"celsius_to_fahrenheit(-40) should be -40.0, got {result!r}. "
        "-40 is where Celsius and Fahrenheit are equal."
    )


# ---------------------------------------------------------------------------
# fahrenheit_to_celsius
# ---------------------------------------------------------------------------

def test_f_to_c_freezing():
    """fahrenheit_to_celsius(32) returns 0.0."""
    result = fahrenheit_to_celsius(32)
    assert result == 0.0, (
        f"fahrenheit_to_celsius(32) should be 0.0, got {result!r}. "
        "Formula: (f - 32) * 5/9"
    )


def test_f_to_c_boiling():
    """fahrenheit_to_celsius(212) returns 100.0."""
    result = fahrenheit_to_celsius(212)
    assert result == 100.0, (
        f"fahrenheit_to_celsius(212) should be 100.0, got {result!r}."
    )


def test_f_to_c_body_temperature():
    """fahrenheit_to_celsius(98.6) is approximately 37.0."""
    result = fahrenheit_to_celsius(98.6)
    assert abs(result - 37.0) < 0.01, (
        f"fahrenheit_to_celsius(98.6) should be ~37.0, got {result!r}."
    )


# ---------------------------------------------------------------------------
# Inverse relationship
# ---------------------------------------------------------------------------

def test_roundtrip_celsius():
    """Converting C->F->C returns the original value."""
    for c in [0, 37, 100, -10]:
        roundtrip = fahrenheit_to_celsius(celsius_to_fahrenheit(c))
        assert abs(roundtrip - c) < 0.0001, (
            f"Round-trip failed for {c}°C: got {roundtrip!r} after C->F->C. "
            "The two functions should be inverses of each other."
        )


# ---------------------------------------------------------------------------
# main() and the guard
# ---------------------------------------------------------------------------

def test_main_is_callable():
    """main() exists and can be called without error."""
    # We call it and just make sure it doesn't raise
    try:
        main()
    except Exception as e:
        assert False, f"main() raised an exception: {e}"


def test_name_guard_present():
    """The module contains an if __name__ == '__main__': guard."""
    import submission
    source = inspect.getsource(submission)
    assert '__name__' in source and '__main__' in source, (
        "The module must include: if __name__ == \"__main__\": main()\n"
        "This guard prevents main() from running when the module is imported by the grader."
    )


if __name__ == "__main__":
    print(celsius_to_fahrenheit(100))
    print(fahrenheit_to_celsius(32))
