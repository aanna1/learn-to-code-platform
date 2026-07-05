import sys
import os
import importlib
import json as _json

def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


def test_to_json_returns_string():
    """to_json returns a str."""
    m = _load()
    result = m.to_json({"a": 1})
    assert isinstance(result, str), (
        f"Expected a str but got {type(result).__name__!r}."
    )


def test_to_json_is_valid_json():
    """to_json output can be parsed back by json.loads."""
    m = _load()
    data = {"name": "Ada", "age": 25, "active": True}
    text = m.to_json(data)
    parsed = _json.loads(text)
    assert parsed == data, (
        f"Round-tripping through to_json gave {parsed!r}, expected {data!r}."
    )


def test_to_json_uses_indent():
    """to_json output is indented (multi-line)."""
    m = _load()
    text = m.to_json({"x": 1})
    assert "\n" in text, (
        "to_json output should be indented (multi-line). "
        "Pass `indent=2` to json.dumps."
    )


def test_to_json_bool_serialization():
    """to_json converts Python True/False to JSON true/false."""
    m = _load()
    text = m.to_json({"flag": True})
    assert "true" in text and "True" not in text, (
        f"JSON should use lowercase 'true', not Python 'True'. Got: {text!r}"
    )


def test_from_json_returns_dict():
    """from_json returns a dict."""
    m = _load()
    result = m.from_json('{"a": 1}')
    assert isinstance(result, dict), (
        f"Expected a dict but got {type(result).__name__!r}."
    )


def test_from_json_parses_correctly():
    """from_json recovers the original data."""
    m = _load()
    original = {"name": "Ada", "age": 25, "active": True}
    text = _json.dumps(original)
    recovered = m.from_json(text)
    assert recovered == original, (
        f"Expected {original!r} but got {recovered!r}."
    )


def test_safe_serialize_valid():
    """safe_serialize returns a JSON string for serializable data."""
    m = _load()
    result = m.safe_serialize({"ok": [1, 2, 3]})
    assert isinstance(result, str) and result != "not serializable", (
        f"Expected a JSON string for serializable data, got {result!r}."
    )
    _json.loads(result)  # must be valid JSON


def test_safe_serialize_set():
    """safe_serialize returns 'not serializable' for a set value."""
    m = _load()
    result = m.safe_serialize({"bad": {1, 2, 3}})
    assert result == "not serializable", (
        f"Expected 'not serializable' for a dict containing a set, got {result!r}."
    )


def test_safe_serialize_custom_object():
    """safe_serialize returns 'not serializable' for a custom object."""
    m = _load()
    class Foo:
        pass
    result = m.safe_serialize({"obj": Foo()})
    assert result == "not serializable", (
        f"Expected 'not serializable' for a custom object, got {result!r}."
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
