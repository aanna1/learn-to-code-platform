import sys
import os
import importlib
import json as _json
import re

def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


def test_make_snapshot_returns_dict():
    """make_snapshot() returns a dict."""
    m = _load()
    result = m.make_snapshot()
    assert isinstance(result, dict), (
        f"Expected a dict but got {type(result).__name__!r}."
    )


def test_make_snapshot_has_required_keys():
    """make_snapshot() dict has exactly the required keys."""
    m = _load()
    result = m.make_snapshot()
    required = {"date", "temperature", "condition", "humidity"}
    assert set(result.keys()) == required, (
        f"Expected keys {required} but got {set(result.keys())}."
    )


def test_date_format():
    """'date' value is a string in YYYY-MM-DD format."""
    m = _load()
    result = m.make_snapshot()
    d = result.get("date", "")
    assert isinstance(d, str), (
        f"'date' should be a string, got {type(d).__name__!r}. "
        "Use date.today().isoformat()."
    )
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", d), (
        f"'date' should be in YYYY-MM-DD format, got {d!r}. "
        "Use date.today().isoformat()."
    )


def test_temperature_is_int_in_range():
    """'temperature' is an int in [-10, 40]."""
    m = _load()
    for _ in range(50):
        result = m.make_snapshot()
        t = result["temperature"]
        assert isinstance(t, int), (
            f"'temperature' should be an int, got {type(t).__name__!r}."
        )
        assert -10 <= t <= 40, (
            f"'temperature' should be in [-10, 40], got {t}."
        )


def test_condition_is_valid():
    """'condition' is one of the five allowed strings."""
    m = _load()
    valid = {"sunny", "cloudy", "rainy", "stormy", "snowy"}
    for _ in range(50):
        result = m.make_snapshot()
        c = result["condition"]
        assert c in valid, (
            f"'condition' {c!r} is not in {valid}."
        )


def test_humidity_is_int_in_range():
    """'humidity' is an int in [0, 100]."""
    m = _load()
    for _ in range(50):
        result = m.make_snapshot()
        h = result["humidity"]
        assert isinstance(h, int), (
            f"'humidity' should be an int, got {type(h).__name__!r}."
        )
        assert 0 <= h <= 100, (
            f"'humidity' should be in [0, 100], got {h}."
        )


def test_snapshot_to_json_returns_string():
    """snapshot_to_json() returns a str."""
    m = _load()
    result = m.snapshot_to_json()
    assert isinstance(result, str), (
        f"Expected a str but got {type(result).__name__!r}."
    )


def test_snapshot_to_json_is_valid_json():
    """snapshot_to_json() output parses back to a dict with the right keys."""
    m = _load()
    text = m.snapshot_to_json()
    parsed = _json.loads(text)
    required = {"date", "temperature", "condition", "humidity"}
    assert set(parsed.keys()) == required, (
        f"Parsed JSON missing keys. Got {set(parsed.keys())}."
    )


def test_snapshot_to_json_is_indented():
    """snapshot_to_json() output is multi-line (indent=2)."""
    m = _load()
    text = m.snapshot_to_json()
    assert "\n" in text, (
        "snapshot_to_json() output should be indented. "
        "Pass `indent=2` to json.dumps."
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
                print(f"ERROR {name}: {e}")
