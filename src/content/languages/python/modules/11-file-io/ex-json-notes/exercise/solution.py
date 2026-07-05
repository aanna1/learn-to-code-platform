import json
from pathlib import Path


def save_notes(notes, filepath):
    """Write the list of notes to filepath as JSON (indent=2)."""
    with open(filepath, "w") as f:
        json.dump(notes, f, indent=2)


def load_notes(filepath):
    """Load and return the list of notes from filepath.
    Return [] if the file does not exist.
    """
    if not Path(filepath).exists():
        return []
    with open(filepath, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    save_notes(["buy milk", "call mom"], "notes.json")
    print(load_notes("notes.json"))   # ['buy milk', 'call mom']
    print(load_notes("missing.json")) # []
