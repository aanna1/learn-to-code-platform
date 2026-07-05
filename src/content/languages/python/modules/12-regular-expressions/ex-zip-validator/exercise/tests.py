def test_five_digit_zip():
    "five-digit zip code is valid"
    assert is_valid_zip("78664") == True, \
        "is_valid_zip('78664') should return True — a plain 5-digit zip is always valid."

def test_zip_plus_four():
    "ZIP+4 format is valid"
    assert is_valid_zip("78664-1234") == True, \
        "is_valid_zip('78664-1234') should return True — the hyphen+4-digit extension is a valid ZIP+4."

def test_too_short():
    "three-digit code is invalid"
    assert is_valid_zip("786") == False, \
        "is_valid_zip('786') should return False — fewer than 5 digits is not a zip code."

def test_too_long_no_hyphen():
    "seven digits with no hyphen is invalid"
    assert is_valid_zip("7866412") == False, \
        "is_valid_zip('7866412') should return False — 7 consecutive digits is not a valid format."

def test_short_extension():
    "five digits, hyphen, two digits is invalid"
    assert is_valid_zip("78664-12") == False, \
        "is_valid_zip('78664-12') should return False — the +4 extension must be exactly 4 digits."

def test_letters():
    "alphabetic string is invalid"
    assert is_valid_zip("ABCDE") == False, \
        "is_valid_zip('ABCDE') should return False — zip codes contain only digits (and an optional hyphen)."

def test_wrong_layout():
    "four-digit base with five-digit extension is invalid"
    assert is_valid_zip("1234-56789") == False, \
        "is_valid_zip('1234-56789') should return False — the base must be exactly 5 digits."

def test_returns_bool():
    "function returns a bool, not a match object"
    result = is_valid_zip("78664")
    assert isinstance(result, bool), \
        f"is_valid_zip should return True or False, but got {type(result).__name__!r}. " \
        "Wrap your match check in bool(): return bool(ZIP_PATTERN.fullmatch(code))."
