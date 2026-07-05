from enum import Enum

from submission import Status, Item, generate_report


def test_status_is_enum():
    """Status is an Enum subclass with ACTIVE and INACTIVE members."""
    assert issubclass(Status, Enum), (
        "Status must be defined as 'class Status(Enum):'. "
        "Import Enum from the enum module."
    )
    assert hasattr(Status, "ACTIVE") and hasattr(Status, "INACTIVE"), (
        "Status must have both ACTIVE and INACTIVE members."
    )


def test_status_values():
    """Status.ACTIVE.value is 'active' and Status.INACTIVE.value is 'inactive'."""
    assert Status.ACTIVE.value == "active", (
        f"Status.ACTIVE.value should be 'active', got {Status.ACTIVE.value!r}."
    )
    assert Status.INACTIVE.value == "inactive", (
        f"Status.INACTIVE.value should be 'inactive', got {Status.INACTIVE.value!r}."
    )


def test_item_is_dataclass():
    """Item is a dataclass with name, value, and status fields."""
    from dataclasses import fields as dc_fields
    try:
        f_names = {f.name for f in dc_fields(Item)}
    except TypeError:
        assert False, "Item does not appear to be a dataclass. Add the @dataclass decorator."
    assert {"name", "value", "status"} <= f_names, (
        f"Item is missing required fields. Found: {f_names}. "
        "Need: name, value, status."
    )


def test_report_item_lines():
    """generate_report formats each item as 'name: $value (status)'."""
    items = [
        Item("Alice", 100.0, Status.ACTIVE),
        Item("Bob", 200.0, Status.INACTIVE),
    ]
    result = generate_report(items)
    lines = result.splitlines()
    assert lines[0] == "Alice: $100.00 (active)", (
        f"First line should be 'Alice: $100.00 (active)', got {lines[0]!r}. "
        "Use f\"{item.name}: ${item.value:,.2f} ({item.status.value})\"."
    )
    assert lines[1] == "Bob: $200.00 (inactive)", (
        f"Second line should be 'Bob: $200.00 (inactive)', got {lines[1]!r}."
    )


def test_report_total_active_only():
    """generate_report totals only ACTIVE items."""
    items = [
        Item("Alice", 1000.0, Status.ACTIVE),
        Item("Bob", 999.0, Status.INACTIVE),
        Item("Carol", 500.0, Status.ACTIVE),
    ]
    result = generate_report(items)
    last_line = result.splitlines()[-1]
    assert last_line == "Total active: $1,500.00", (
        f"Last line should be 'Total active: $1,500.00' (Alice + Carol, not Bob), "
        f"got {last_line!r}. "
        "Filter with 'if item.status is Status.ACTIVE' in the generator expression."
    )


def test_report_comma_separator_in_large_values():
    """Values >= 1000 are formatted with comma separators."""
    items = [Item("X", 1234.56, Status.ACTIVE)]
    result = generate_report(items)
    assert "1,234.56" in result, (
        f"Value 1234.56 should be formatted as '1,234.56', got: {result!r}. "
        "Use :,.2f — the comma adds thousand separators."
    )


def test_report_empty_list():
    """generate_report handles an empty list — total is $0.00."""
    result = generate_report([])
    assert result == "Total active: $0.00", (
        f"generate_report([]) should return 'Total active: $0.00', got {result!r}."
    )


def test_report_line_count():
    """generate_report returns one line per item plus the summary line."""
    items = [
        Item("A", 10.0, Status.ACTIVE),
        Item("B", 20.0, Status.INACTIVE),
        Item("C", 30.0, Status.ACTIVE),
    ]
    lines = generate_report(items).splitlines()
    assert len(lines) == 4, (
        f"Expected 4 lines (3 items + summary), got {len(lines)}: {lines}"
    )


if __name__ == "__main__":
    items = [
        Item("Alice", 1234.56, Status.ACTIVE),
        Item("Bob", 89.0, Status.INACTIVE),
        Item("Carol", 500.0, Status.ACTIVE),
    ]
    print(generate_report(items))
