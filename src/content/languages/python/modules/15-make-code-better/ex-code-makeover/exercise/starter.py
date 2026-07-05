from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    ACTIVE = ...    # fill in the string value
    INACTIVE = ...


@dataclass
class Item:
    name: str
    value: float
    status: Status


def generate_report(items: list[Item]) -> str:
    # 1. Build per-item lines with a list comprehension
    #    Format: f"{item.name}: ${item.value:,.2f} ({item.status.value})"
    lines = []

    # 2. Sum active items with a generator expression inside sum()
    #    Compare: item.status is Status.ACTIVE
    total = 0.0

    # 3. Append the summary line
    #    Format: f"Total active: ${total:,.2f}"

    return "\n".join(lines)


if __name__ == "__main__":
    items = [
        Item("Alice", 1234.56, Status.ACTIVE),
        Item("Bob", 89.0, Status.INACTIVE),
        Item("Carol", 500.0, Status.ACTIVE),
    ]
    print(generate_report(items))
