def test_hyphen_format():
    "finds a hyphen-separated phone number"
    result = find_phones("Call 512-555-0102 for help.")
    assert "512-555-0102" in result, \
        f"Expected '512-555-0102' in results but got {result}. " \
        "Make sure your pattern matches three digits, hyphen, three digits, hyphen, four digits."

def test_paren_area_code():
    "finds a number with parenthesized area code"
    result = find_phones("Dial (800)555-0199 now.")
    assert any("800" in r and "555" in r and "0199" in r for r in result), \
        f"Expected a match containing '(800)555-0199' in {result}. " \
        "Use \\(? and \\)? to make the parentheses optional in your pattern."

def test_dot_separators():
    "finds a dot-separated phone number"
    result = find_phones("My number is 212.555.0123.")
    assert any("212" in r and "555" in r and "0123" in r for r in result), \
        f"Expected a match for '212.555.0123' but got {result}. " \
        "Include '.' in your separator character class: [-.\\ s]?"

def test_no_separators():
    "finds a phone number with no separators"
    result = find_phones("Text 9005550100 anytime.")
    assert any("9005550100" in r for r in result), \
        f"Expected a match for '9005550100' but got {result}. " \
        "Make sure the separator is optional (use ? after the character class)."

def test_multiple_numbers():
    "finds all numbers when several appear in one string"
    text = "Call 512-555-0102 or (800)555-0199."
    result = find_phones(text)
    assert len(result) >= 2, \
        f"Expected at least 2 matches but got {len(result)}: {result}. " \
        "Use re.findall — it returns every match, not just the first."

def test_returns_list():
    "function returns a list"
    result = find_phones("No numbers here.")
    assert isinstance(result, list), \
        f"find_phones should return a list, but got {type(result).__name__!r}. " \
        "Return PHONE_PATTERN.findall(text) directly."

def test_no_match_returns_empty_list():
    "returns an empty list when no phone numbers are present"
    result = find_phones("Hello, world!")
    assert result == [], \
        f"Expected [] but got {result}. findall returns [] when there are no matches."
