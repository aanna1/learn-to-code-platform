import json


def to_json(data):
    return json.dumps(data, indent=2)


def from_json(text):
    return json.loads(text)


def safe_serialize(data):
    try:
        return json.dumps(data)
    except TypeError:
        return "not serializable"


if __name__ == "__main__":
    person = {"name": "Ada", "age": 25, "active": True}
    text = to_json(person)
    print(text)
    print(from_json(text))
    print(safe_serialize({"ok": [1, 2, 3]}))
    print(safe_serialize({"bad": {1, 2, 3}}))
