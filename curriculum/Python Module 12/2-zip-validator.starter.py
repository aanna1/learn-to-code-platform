import re

# TODO: compile a pattern that matches a valid US zip code.
# A valid zip is exactly 5 digits, optionally followed by a hyphen and 4 more digits.
# Hint: \d{5} matches exactly five digits; (?:-\d{4})? makes the extension optional.
ZIP_PATTERN = re.compile(r"")  # replace with your pattern

def is_valid_zip(code):
    """Return True if code is a valid US zip code, False otherwise."""
    # TODO: use ZIP_PATTERN to check whether code matches exactly.
    # Hint: re.fullmatch or anchors (^ and $) ensure nothing extra is allowed.
    pass


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
