from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    LOW = ...     # fill in the string value
    MEDIUM = ...
    HIGH = ...


@dataclass
class Task:
    title: str
    priority: Priority
    tags: list[str] = ...  # use field(default_factory=list) here

    def summary(self) -> str:
        # Return "[PRIORITY] title (tags: tag1, tag2)"
        # or    "[PRIORITY] title (tags: none)" when there are no tags
        pass


if __name__ == "__main__":
    t1 = Task("Write tests", Priority.HIGH, ["testing", "ci"])
    t2 = Task("Read docs", Priority.LOW)
    print(t1)
    print(t1.summary())
    print(t2.summary())
