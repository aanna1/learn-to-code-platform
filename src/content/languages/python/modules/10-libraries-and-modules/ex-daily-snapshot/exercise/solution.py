import random
import json
from datetime import date

CONDITIONS = ["sunny", "cloudy", "rainy", "stormy", "snowy"]


def make_snapshot():
    return {
        "date": date.today().isoformat(),
        "temperature": random.randint(-10, 40),
        "condition": random.choice(CONDITIONS),
        "humidity": random.randint(0, 100),
    }


def snapshot_to_json():
    return json.dumps(make_snapshot(), indent=2)


if __name__ == "__main__":
    snap = make_snapshot()
    print(snap)
    print(snapshot_to_json())
