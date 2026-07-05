import re

ZIP_PATTERN = re.compile(r"^\d{5}(?:-\d{4})?$")

def is_valid_zip(code):
    """Return True if code is a valid US zip code, False otherwise."""
    return bool(ZIP_PATTERN.fullmatch(code))


if __name__ == "__main__":
    tests = [
        ("78664",      True),
        ("78664-1234", True),
        ("786",        False),
        ("7866412",    False),
        ("78664-12",   False),
        ("ABCDE",      False),
        ("1234-56789", False),
    ]
    for code, expected in tests:
        result = is_valid_zip(code)
        status = "OK" if result == expected else "FAIL"
        print(f"{status}  is_valid_zip({code!r}) = {result}  (expected {expected})")
