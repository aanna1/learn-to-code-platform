from typing import Iterable, Iterator


def running_sum(numbers: Iterable[float]) -> Iterator[float]:
    """Yield the cumulative sum after each element.

    running_sum([1, 2, 3, 4]) -> yields 1, 3, 6, 10
    """
    total = 0.0
    for n in numbers:
        total += n
        yield total


def first_n(iterable: Iterable, n: int) -> list:
    """Return the first n items from iterable as a list.

    Works on infinite generators — stop as soon as you have n items.
    """
    result = []
    for item in iterable:
        if len(result) >= n:
            break
        result.append(item)
    return result


def fibonacci() -> Iterator[int]:
    """Yield Fibonacci numbers indefinitely: 0, 1, 1, 2, 3, 5, 8, ..."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


if __name__ == "__main__":
    print("running_sum:", list(running_sum([1, 2, 3, 4])))
    print("first_n:    ", first_n(running_sum([1, 2, 3, 4, 5]), 3))
    print("fibonacci:  ", first_n(fibonacci(), 8))
