import random
import json
from datetime import date

CONDITIONS = ["sunny", "cloudy", "rainy", "stormy", "snowy"]


def make_snapshot():
    # Return a dict with keys: "date", "temperature", "condition", "humidity"
    pass


def snapshot_to_json():
    # Call make_snapshot() and return it as a JSON string with indent=2
    pass


if __name__ == "__main__":
    snap = make_snapshot()
    print(snap)
    print(snapshot_to_json())
