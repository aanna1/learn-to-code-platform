def test_gpa_correct():
    "gpa property returns the correct average"
    s = Student("Alice", [80, 90, 100])
    assert s.gpa == 90.0, (
        f"Student('Alice', [80, 90, 100]).gpa should be 90.0, got {s.gpa!r}."
    )

def test_gpa_is_property():
    "gpa is a property, not a plain method"
    s = Student("Alice", [80, 90, 100])
    result = s.gpa
    assert isinstance(result, (int, float)), (
        f"s.gpa should return a number. Got {type(result).__name__!r}. "
        "Did you add @property above the gpa method?"
    )

def test_repr_contains_name_and_gpa():
    "repr includes the student name and rounded GPA"
    s = Student("Alice", [88, 92, 95])
    r = repr(s)
    assert "Alice" in r, f"repr(s) should contain 'Alice', got: {r!r}"
    assert "91.7" in r, (
        f"repr(s) should contain '91.7' (GPA rounded to 1 decimal), got: {r!r}"
    )

def test_sorted_lowest_to_highest():
    "sorted() orders students by GPA ascending"
    students = [
        Student("Alice", [88, 92, 95]),
        Student("Bob",   [77, 85]),
        Student("Carol", [99, 96, 92]),
    ]
    ordered = sorted(students)
    gpas = [s.gpa for s in ordered]
    assert gpas == sorted(gpas), (
        f"sorted(students) should go from lowest to highest GPA, got: {[repr(s) for s in ordered]}"
    )

def test_sorted_first_is_lowest():
    "first element after sorting is the student with the lowest GPA"
    students = [
        Student("Alice", [88, 92, 95]),
        Student("Bob",   [77, 85]),
        Student("Carol", [99, 96, 92]),
    ]
    ordered = sorted(students)
    assert ordered[0].name == "Bob", (
        f"After sorting, the first student should be Bob (lowest GPA), got: {ordered[0].name!r}"
    )

def test_add_grade_appends():
    "add_grade appends the score and updates gpa"
    s = Student("Alice", [80, 90])
    s.add_grade(100)
    assert 100 in s.grades, "add_grade(100) should add 100 to grades."
    assert len(s.grades) == 3, f"grades should have 3 elements after add_grade, got {len(s.grades)}."

def test_add_grade_updates_gpa():
    "gpa recalculates after add_grade"
    s = Student("Alice", [80, 90])
    s.add_grade(100)
    assert s.gpa == 90.0, (
        f"After adding 100 to [80, 90], gpa should be 90.0, got {s.gpa!r}."
    )
