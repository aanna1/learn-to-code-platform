import time
from contextlib import contextmanager
from typing import Any


@contextmanager
def timed(label: str):
    """Print how long the with-block takes.

    Usage:
        with timed("my work"):
            do_something()
        # prints: my work: 0.0123s
    """
    start = time.monotonic()
    try:
        yield
    finally:
        elapsed = time.monotonic() - start
        print(f"{label}: {elapsed:.4f}s")


class managed_list:
    """Context manager that holds a list and sorts it on exit."""

    def __init__(self) -> None:
        self.items: list = []

    def __enter__(self) -> "managed_list":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.items.sort()
        return None


if __name__ == "__main__":
    with timed("summing"):
        total = sum(range(500_000))
        print(f"total = {total}")

    with managed_list() as ml:
        ml.items.extend([3, 1, 4, 1, 5, 9])
    print("sorted:", ml.items)
