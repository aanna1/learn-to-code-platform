def test_single_date():
    "reformats a single ISO date"
    result = reformat_dates("Event on 2026-03-14.")
    assert "03/14/2026" in result, \
        f"Expected '03/14/2026' in result but got {result!r}. " \
        "The pattern (\\d{{4}})-(\\d{{2}})-(\\d{{2}}) captures year, month, day; " \
        "the replacement r'\\2/\\3/\\1' puts month first."

def test_multiple_dates():
    "reformats multiple ISO dates in one string"
    result = reformat_dates("Invoice dated 2026-03-14, due 2026-04-01.")
    assert "03/14/2026" in result and "04/01/2026" in result, \
        f"Expected both dates reformatted but got {result!r}. " \
        "re.sub replaces *all* matches, not just the first one."

def test_no_dates_unchanged():
    "strings without dates are returned unchanged"
    original = "No dates here."
    result = reformat_dates(original)
    assert result == original, \
        f"Expected {original!r} unchanged but got {result!r}. " \
        "re.sub returns the original string when there are no matches."

def test_surrounding_text_preserved():
    "text around the date is not modified"
    result = reformat_dates("Born on 1990-07-22, died 2055-12-31.")
    assert result.startswith("Born on ") and ", died " in result, \
        f"Non-date text should be preserved but got {result!r}."

def test_correct_field_order():
    "month comes before day, day before year in the output"
    result = reformat_dates("2026-11-05")
    assert result == "11/05/2026", \
        f"Expected '11/05/2026' but got {result!r}. " \
        "Check that your replacement is r'\\2/\\3/\\1' (month/day/year), not another order."

def test_returns_string():
    "function returns a string"
    result = reformat_dates("2026-01-01")
    assert isinstance(result, str), \
        f"reformat_dates should return a string, but got {type(result).__name__!r}. " \
        "Return DATE_PATTERN.sub(r'\\2/\\3/\\1', text) directly."
