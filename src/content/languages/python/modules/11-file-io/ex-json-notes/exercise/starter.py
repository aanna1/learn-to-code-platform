import json
from pathlib import Path


def save_notes(notes, filepath):
    """Write the list of notes to filepath as JSON (indent=2)."""
    # Open the file for writing and use json.dump
    pass


def load_notes(filepath):
    """Load and return the list of notes from filepath.
    Return [] if the file does not exist.
    """
    # Check if the file exists first; if not, return []
    # Otherwise open and json.load it
    pass


if __name__ == "__main__":
    save_notes(["buy milk", "call mom"], "notes.json")
    print(load_notes("notes.json"))   # ['buy milk', 'call mom']
    print(load_notes("missing.json")) # []
