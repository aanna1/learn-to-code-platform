import sys
import os
import importlib
import tempfile


def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


def _tmp(content):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    f.write(content)
    f.close()
    return f.name


def test_load_grades_basic():
    """load_grades returns a list of dicts with name and score keys."""
    m = _load()
    path = _tmp("name,score\nAlice,92\nBob,77\n")
    try:
        result = m.load_grades(path)
        assert isinstance(result, list), f"Expected list, got {type(result).__name__}"
        assert len(result) == 2, f"Expected 2 rows, got {len(result)}"
        assert result[0] == {"name": "Alice", "score": 92}, (
            f"First row wrong: {result[0]!r}"
        )
        assert result[1] == {"name": "Bob", "score": 77}, (
            f"Second row wrong: {result[1]!r}"
        )
    finally:
        os.unlink(path)


def test_load_grades_score_is_int():
    """load_grades casts score to int, not leaving it as a string."""
    m = _load()
    path = _tmp("name,score\nCarol,88\n")
    try:
        result = m.load_grades(path)
        assert len(result) == 1
        score = result[0]["score"]
        assert isinstance(score, int), (
            f"score should be int, got {type(score).__name__}: {score!r}. "
            "Cast with int(row['score'])."
        )
    finally:
        os.unlink(path)


def test_load_grades_empty_csv():
    """load_grades returns an empty list when the CSV has only a header."""
    m = _load()
    path = _tmp("name,score\n")
    try:
        result = m.load_grades(path)
        assert result == [], f"Expected [], got {result!r}"
    finally:
        os.unlink(path)


def test_load_grades_preserves_order():
    """load_grades returns rows in the order they appear in the file."""
    m = _load()
    path = _tmp("name,score\nZara,70\nAnna,95\nMike,60\n")
    try:
        result = m.load_grades(path)
        names = [r["name"] for r in result]
        assert names == ["Zara", "Anna", "Mike"], (
            f"Expected order Zara, Anna, Mike but got {names}"
        )
    finally:
        os.unlink(path)


def test_average_score_basic():
    """average_score returns the correct average rounded to 1 decimal place."""
    m = _load()
    path = _tmp("name,score\nAlice,92\nBob,77\nCarol,88\n")
    try:
        result = m.average_score(path)
        assert result == 85.7, (
            f"Expected 85.7 but got {result!r}. "
            "(92 + 77 + 88) / 3 = 85.666... rounds to 85.7"
        )
    finally:
        os.unlink(path)


def test_average_score_single_student():
    """average_score works with a single student."""
    m = _load()
    path = _tmp("name,score\nAlex,90\n")
    try:
        result = m.average_score(path)
        assert result == 90.0, f"Expected 90.0 but got {result!r}"
    finally:
        os.unlink(path)


def test_average_score_empty():
    """average_score returns 0.0 when the CSV has no students."""
    m = _load()
    path = _tmp("name,score\n")
    try:
        result = m.average_score(path)
        assert result == 0.0, f"Expected 0.0 for empty file but got {result!r}"
    finally:
        os.unlink(path)


def test_average_score_returns_float():
    """average_score returns a float."""
    m = _load()
    path = _tmp("name,score\nAlex,100\nBen,100\n")
    try:
        result = m.average_score(path)
        assert isinstance(result, float), (
            f"Expected float, got {type(result).__name__}. Use round(..., 1) or divide with /."
        )
    finally:
        os.unlink(path)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
