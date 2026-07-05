from enum import Enum

from submission import Priority, Task


def test_priority_is_enum():
    """Priority is an Enum subclass."""
    assert issubclass(Priority, Enum), (
        "Priority must be defined as 'class Priority(Enum):'. "
        "Import Enum from the enum module and use it as the base class."
    )


def test_priority_members_exist():
    """Priority has LOW, MEDIUM, and HIGH members."""
    for name in ("LOW", "MEDIUM", "HIGH"):
        assert hasattr(Priority, name), (
            f"Priority is missing the '{name}' member. "
            "Define it as an attribute inside the class: LOW = 'low'."
        )


def test_priority_values():
    """Priority member values are lowercase strings."""
    assert Priority.LOW.value == "low", (
        f"Priority.LOW.value should be 'low', got {Priority.LOW.value!r}."
    )
    assert Priority.MEDIUM.value == "medium", (
        f"Priority.MEDIUM.value should be 'medium', got {Priority.MEDIUM.value!r}."
    )
    assert Priority.HIGH.value == "high", (
        f"Priority.HIGH.value should be 'high', got {Priority.HIGH.value!r}."
    )


def test_task_repr_includes_fields():
    """Task __repr__ shows all field names and values."""
    t = Task("Fix bug", Priority.HIGH)
    r = repr(t)
    assert "Fix bug" in r and "HIGH" in r, (
        f"repr(Task('Fix bug', Priority.HIGH)) should include 'Fix bug' and 'HIGH', "
        f"got: {r!r}. Make sure @dataclass is applied to the Task class."
    )


def test_task_equality():
    """Two Tasks with identical fields are equal."""
    t1 = Task("Write docs", Priority.LOW, ["docs"])
    t2 = Task("Write docs", Priority.LOW, ["docs"])
    assert t1 == t2, (
        "Two Task instances with the same fields should be equal. "
        "@dataclass generates __eq__ automatically — check that the decorator is applied."
    )


def test_task_inequality():
    """Tasks with different priorities are not equal."""
    t1 = Task("Deploy", Priority.LOW)
    t2 = Task("Deploy", Priority.HIGH)
    assert t1 != t2, (
        "Tasks with different priorities should not be equal."
    )


def test_tags_not_shared_between_instances():
    """Each Task gets its own independent tags list."""
    t1 = Task("Task A", Priority.LOW)
    t2 = Task("Task B", Priority.MEDIUM)
    t1.tags.append("urgent")
    assert "urgent" not in t2.tags, (
        "Appending to t1.tags should not affect t2.tags. "
        "Use field(default_factory=list) instead of tags: list[str] = []."
    )


def test_summary_with_tags():
    """summary() formats correctly when tags are present."""
    t = Task("Write tests", Priority.HIGH, ["testing", "ci"])
    result = t.summary()
    assert result == "[HIGH] Write tests (tags: testing, ci)", (
        f"summary() should return '[HIGH] Write tests (tags: testing, ci)', got {result!r}. "
        "Use self.priority.value.upper() for the priority label."
    )


def test_summary_no_tags():
    """summary() shows 'none' when the tags list is empty."""
    t = Task("Read docs", Priority.LOW)
    result = t.summary()
    assert result == "[LOW] Read docs (tags: none)", (
        f"summary() should return '[LOW] Read docs (tags: none)', got {result!r}. "
        "When self.tags is empty, the tags section should read '(tags: none)'."
    )


def test_summary_medium_priority():
    """summary() works for MEDIUM priority."""
    t = Task("Review PR", Priority.MEDIUM, ["review"])
    result = t.summary()
    assert result == "[MEDIUM] Review PR (tags: review)", (
        f"summary() should return '[MEDIUM] Review PR (tags: review)', got {result!r}."
    )


if __name__ == "__main__":
    t1 = Task("Write tests", Priority.HIGH, ["testing", "ci"])
    t2 = Task("Read docs", Priority.LOW)
    print(t1)
    print(t1.summary())
    print(t2.summary())
    print("Equal?", t1 == Task("Write tests", Priority.HIGH, ["testing", "ci"]))
