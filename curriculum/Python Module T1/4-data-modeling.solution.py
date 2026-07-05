from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    title: str
    priority: Priority
    tags: list[str] = field(default_factory=list)

    def summary(self) -> str:
        tag_str = ", ".join(self.tags) if self.tags else "none"
        return f"[{self.priority.value.upper()}] {self.title} (tags: {tag_str})"


if __name__ == "__main__":
    t1 = Task("Write tests", Priority.HIGH, ["testing", "ci"])
    t2 = Task("Read docs", Priority.LOW)
    print(t1)
    print(t1.summary())
    print(t2.summary())
