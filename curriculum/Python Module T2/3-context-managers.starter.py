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
    # TODO: record start time, yield, then print elapsed time
    ...
    yield
    ...


class managed_list:
    """Context manager that holds a list and sorts it on exit."""

    def __init__(self) -> None:
        self.items: list = []

    def __enter__(self) -> "managed_list":
        # TODO: return self so callers can do 'with managed_list() as ml'
        ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # TODO: sort self.items and return None (don't suppress exceptions)
        ...


if __name__ == "__main__":
    with timed("summing"):
        total = sum(range(500_000))
        print(f"total = {total}")

    with managed_list() as ml:
        ml.items.extend([3, 1, 4, 1, 5, 9])
    print("sorted:", ml.items)
