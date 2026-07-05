from typing import Iterable, Iterator


def running_sum(numbers: Iterable[float]) -> Iterator[float]:
    """Yield the cumulative sum after each element.

    running_sum([1, 2, 3, 4]) -> yields 1, 3, 6, 10
    """
    # TODO: keep a running total and yield it after each element
    ...


def first_n(iterable: Iterable, n: int) -> list:
    """Return the first n items from iterable as a list.

    Works on infinite generators — stop as soon as you have n items.
    """
    # TODO: collect items one at a time until you have n of them
    ...


def fibonacci() -> Iterator[int]:
    """Yield Fibonacci numbers indefinitely: 0, 1, 1, 2, 3, 5, 8, ..."""
    # TODO: start with a=0, b=1 and keep yielding a while swapping
    ...


if __name__ == "__main__":
    print("running_sum:", list(running_sum([1, 2, 3, 4])))
    print("first_n:    ", first_n(running_sum([1, 2, 3, 4, 5]), 3))
    print("fibonacci:  ", first_n(fibonacci(), 8))
