from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class Item:
    name: str
    value: float
    status: Status


def generate_report(items: list[Item]) -> str:
    lines = [f"{item.name}: ${item.value:,.2f} ({item.status.value})" for item in items]
    total = sum(item.value for item in items if item.status is Status.ACTIVE)
    lines.append(f"Total active: ${total:,.2f}")
    return "\n".join(lines)


if __name__ == "__main__":
    items = [
        Item("Alice", 1234.56, Status.ACTIVE),
        Item("Bob", 89.0, Status.INACTIVE),
        Item("Carol", 500.0, Status.ACTIVE),
    ]
    print(generate_report(items))
