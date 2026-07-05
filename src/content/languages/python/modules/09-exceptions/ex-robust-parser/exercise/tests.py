import sys
import os
import importlib


def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


_SAMPLE = [
    "Alice:88",
    "Bob:not-a-number",
    "Charlie",
    "Dana:95",
    "",
    "Eve:72:extra",
]


def test_records_count():
    """parse_records returns exactly 2 successful records for the sample."""
    m = _load()
    result = m.parse_records(_SAMPLE)
    assert len(result["records"]) == 2, (
        f"Expected 2 records but got {len(result['records'])}: {result['records']}"
    )


def test_records_content():
    """parse_records returns the correct name/score dicts."""
    m = _load()
    result = m.parse_records(_SAMPLE)
    assert {"name": "Alice", "score": 88} in result["records"], (
        f"Expected Alice:88 in records but got {result['records']}"
    )
    assert {"name": "Dana", "score": 95} in result["records"], (
        f"Expected Dana:95 in records but got {result['records']}"
    )


def test_errors_count():
    """parse_records returns exactly 3 errors for the sample."""
    m = _load()
    result = m.parse_records(_SAMPLE)
    assert len(result["errors"]) == 3, (
        f"Expected 3 errors but got {len(result['errors'])}: {result['errors']}"
    )


def test_error_bad_score():
    """parse_records flags a non-integer score with the right message."""
    m = _load()
    result = m.parse_records(_SAMPLE)
    assert any("score must be an integer" in e for e in result["errors"]), (
        f"Expected 'score must be an integer' in errors: {result['errors']}"
    )


def test_error_bad_format():
    """parse_records flags lines with wrong number of colons."""
    m = _load()
    result = m.parse_records(_SAMPLE)
    assert any("expected 'name:score' format" in e for e in result["errors"]), (
        f"Expected format error in errors: {result['errors']}"
    )


def test_error_line_numbers():
    """parse_records includes 1-indexed line numbers in error messages."""
    m = _load()
    result = m.parse_records(_SAMPLE)
    # Bob is line 2
    assert any("Line 2" in e for e in result["errors"]), (
        f"Expected 'Line 2' (Bob) in errors: {result['errors']}"
    )
    # Charlie is line 3
    assert any("Line 3" in e for e in result["errors"]), (
        f"Expected 'Line 3' (Charlie) in errors: {result['errors']}"
    )
    # Eve is line 6
    assert any("Line 6" in e for e in result["errors"]), (
        f"Expected 'Line 6' (Eve) in errors: {result['errors']}"
    )


def test_blank_lines_skipped():
    """parse_records silently skips blank and whitespace-only lines."""
    m = _load()
    result = m.parse_records(["", "   ", "Alice:88"])
    assert len(result["records"]) == 1, (
        f"Blank lines should be skipped, not counted as errors: {result}"
    )
    assert len(result["errors"]) == 0, (
        f"Blank lines should not produce errors: {result['errors']}"
    )


def test_all_valid():
    """parse_records handles a list with no errors."""
    m = _load()
    lines = ["Alice:88", "Bob:72", "Charlie:95"]
    result = m.parse_records(lines)
    assert len(result["records"]) == 3, f"Expected 3 records, got {result['records']}"
    assert len(result["errors"]) == 0, f"Expected 0 errors, got {result['errors']}"


def test_all_invalid():
    """parse_records handles a list with no valid records."""
    m = _load()
    lines = ["bad", "also:bad:format", "notanint:xyz"]
    result = m.parse_records(lines)
    assert len(result["records"]) == 0, f"Expected 0 records, got {result['records']}"
    assert len(result["errors"]) == 3, f"Expected 3 errors, got {result['errors']}"


def test_return_keys():
    """parse_records returns a dict with 'records' and 'errors' keys."""
    m = _load()
    result = m.parse_records([])
    assert "records" in result, f"Missing 'records' key: {result}"
    assert "errors" in result, f"Missing 'errors' key: {result}"


def test_summary_format():
    """summary returns the exact formatted string."""
    m = _load()
    result = m.parse_records(_SAMPLE)
    s = m.summary(result)
    assert s == "Parsed 2 records, 3 errors.", (
        f"Expected 'Parsed 2 records, 3 errors.' but got {s!r}"
    )


def test_summary_all_good():
    """summary works when there are no errors."""
    m = _load()
    result = {"records": [1, 2, 3], "errors": []}
    s = m.summary(result)
    assert s == "Parsed 3 records, 0 errors.", (
        f"Expected 'Parsed 3 records, 0 errors.' but got {s!r}"
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
            except Exception as e:
                print(f"ERR   {name}: {e}")
