import json


def to_json(data):
    # Serialize data to a JSON string with indent=2
    pass


def from_json(text):
    # Parse a JSON string back to a Python dict
    pass


def safe_serialize(data):
    # Try json.dumps(data). If it raises TypeError, return "not serializable"
    pass


if __name__ == "__main__":
    person = {"name": "Ada", "age": 25, "active": True}
    text = to_json(person)
    print(text)
    print(from_json(text))
    print(safe_serialize({"ok": [1, 2, 3]}))
    print(safe_serialize({"bad": {1, 2, 3}}))
