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


_STUDENTS = [
    {"name": "Ada",      "score": 88},
    {"name": "Grace",    "score": 95},
    {"name": "Linus",    "score": 72},
    {"name": "Margaret", "score": 91},
    {"name": "Guido",    "score": 60},
]


def test_passing_students_basic():
    """passing_students returns names at or above the threshold."""
    m = _load()
    result = m.passing_students(_STUDENTS, threshold=75)
    assert result == ["Ada", "Grace", "Margaret"], (
        f"Expected ['Ada', 'Grace', 'Margaret'] but got {result!r}. "
        "Filter with s['score'] >= threshold, collect s['name'], then sort."
    )


def test_passing_students_none_pass():
    """passing_students returns [] when no student meets the threshold."""
    m = _load()
    result = m.passing_students(_STUDENTS, threshold=100)
    assert result == [], (
        f"Expected [] when threshold=100 but got {result!r}."
    )


def test_passing_students_all_pass():
    """passing_students returns all names when every student passes."""
    m = _load()
    result = m.passing_students(_STUDENTS, threshold=0)
    assert result == sorted([s["name"] for s in _STUDENTS]), (
        f"Expected all names sorted but got {result!r}."
    )


def test_passing_students_sorted():
    """passing_students returns names in alphabetical order."""
    m = _load()
    result = m.passing_students(_STUDENTS, threshold=75)
    assert result == sorted(result), (
        f"Names must be sorted alphabetically but got {result!r}. "
        "Wrap the filtered list in sorted()."
    )


def test_class_average_basic():
    """class_average computes the correct average."""
    m = _load()
    result = m.class_average(_STUDENTS)
    expected = round((88 + 95 + 72 + 91 + 60) / 5, 2)
    assert result == expected, (
        f"Expected {expected} but got {result!r}. "
        "Compute sum(scores) / len(students), then round(..., 2)."
    )


def test_class_average_rounding():
    """class_average rounds to exactly 2 decimal places."""
    m = _load()
    students = [{"name": "A", "score": 100}, {"name": "B", "score": 99}, {"name": "C", "score": 99}]
    result = m.class_average(students)
    assert result == 99.33, (
        f"Expected 99.33 (rounded to 2 places) but got {result!r}. "
        "Use round(sum / len, 2)."
    )


def test_class_average_single_student():
    """class_average works for a single student."""
    m = _load()
    result = m.class_average([{"name": "Ada", "score": 88}])
    assert result == 88.0, (
        f"Expected 88.0 for a single student but got {result!r}."
    )


def test_top_student_basic():
    """top_student returns the name of the highest scorer."""
    m = _load()
    students = [
        {"name": "Ada",   "score": 88},
        {"name": "Grace", "score": 95},
        {"name": "Linus", "score": 72},
    ]
    result = m.top_student(students)
    assert result == "Grace", (
        f"Expected 'Grace' (score 95) but got {result!r}. "
        "Loop through students and track the one with the highest score."
    )


def test_top_student_first_in_list():
    """top_student works when the top scorer is first in the list."""
    m = _load()
    students = [
        {"name": "Grace", "score": 95},
        {"name": "Ada",   "score": 88},
        {"name": "Linus", "score": 72},
    ]
    result = m.top_student(students)
    assert result == "Grace", (
        f"Expected 'Grace' but got {result!r}. Make sure your loop checks all students."
    )


def test_top_student_last_in_list():
    """top_student works when the top scorer is last in the list."""
    m = _load()
    students = [
        {"name": "Ada",   "score": 72},
        {"name": "Linus", "score": 88},
        {"name": "Grace", "score": 95},
    ]
    result = m.top_student(students)
    assert result == "Grace", (
        f"Expected 'Grace' but got {result!r}."
    )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
