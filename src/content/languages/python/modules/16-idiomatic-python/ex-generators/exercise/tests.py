import inspect

from submission import fibonacci, first_n, running_sum


def test_running_sum_basic():
    """running_sum yields the cumulative total after each element."""
    result = list(running_sum([1, 2, 3, 4]))
    assert result == [1, 3, 6, 10], (
        f"running_sum([1, 2, 3, 4]) should yield [1, 3, 6, 10], got {result}. "
        "Keep a 'total' variable, add each number to it, then yield total."
    )


def test_running_sum_is_generator():
    """running_sum must be a generator function (uses yield)."""
    assert inspect.isgeneratorfunction(running_sum), (
        "running_sum must use 'yield' inside the function body. "
        "Returning a list does not count as a generator."
    )


def test_running_sum_floats():
    """running_sum works on floats."""
    result = list(running_sum([0.5, 1.5, 2.0]))
    assert abs(result[0] - 0.5) < 1e-9 and abs(result[2] - 4.0) < 1e-9, (
        f"running_sum([0.5, 1.5, 2.0]) should give [0.5, 2.0, 4.0], got {result}."
    )


def test_running_sum_empty():
    """running_sum of an empty iterable yields nothing."""
    result = list(running_sum([]))
    assert result == [], (
        f"running_sum([]) should yield nothing (empty list), got {result}."
    )


def test_first_n_basic():
    """first_n returns exactly n items as a list."""
    result = first_n([10, 20, 30, 40, 50], 3)
    assert result == [10, 20, 30], (
        f"first_n([10, 20, 30, 40, 50], 3) should return [10, 20, 30], got {result}."
    )


def test_first_n_zero():
    """first_n with n=0 returns an empty list."""
    result = first_n([1, 2, 3], 0)
    assert result == [], (
        f"first_n([1, 2, 3], 0) should return [], got {result}."
    )


def test_first_n_on_infinite_generator():
    """first_n works correctly on an infinite generator."""
    def count_up():
        n = 0
        while True:
            yield n
            n += 1

    result = first_n(count_up(), 5)
    assert result == [0, 1, 2, 3, 4], (
        f"first_n(count_up(), 5) should return [0, 1, 2, 3, 4], got {result}. "
        "Make sure you stop iterating as soon as you have n items."
    )


def test_first_n_combined_with_running_sum():
    """first_n(running_sum(...), n) returns the first n cumulative totals."""
    result = first_n(running_sum([1, 2, 3, 4, 5]), 3)
    assert result == [1, 3, 6], (
        f"first_n(running_sum([1,2,3,4,5]), 3) should return [1, 3, 6], got {result}."
    )


def test_fibonacci_first_eight():
    """fibonacci() yields 0, 1, 1, 2, 3, 5, 8, 13 as its first eight values."""
    result = first_n(fibonacci(), 8)
    assert result == [0, 1, 1, 2, 3, 5, 8, 13], (
        f"first_n(fibonacci(), 8) should return [0, 1, 1, 2, 3, 5, 8, 13], got {result}. "
        "Start with a, b = 0, 1 and yield a, then swap: a, b = b, a + b."
    )


def test_fibonacci_is_generator():
    """fibonacci must be a generator function (uses yield)."""
    assert inspect.isgeneratorfunction(fibonacci), (
        "fibonacci must use 'yield' inside the function body. "
        "Returning a list does not qualify as a generator."
    )


def test_fibonacci_no_end():
    """fibonacci() does not stop after a fixed number of values."""
    result = first_n(fibonacci(), 15)
    assert len(result) == 15 and result[14] == 377, (
        f"fibonacci should run indefinitely. "
        f"The 15th value (index 14) should be 377, got: {result}."
    )


if __name__ == "__main__":
    print("running_sum:", list(running_sum([1, 2, 3, 4])))
    print("first_n:    ", first_n(running_sum([1, 2, 3, 4, 5]), 3))
    print("fibonacci:  ", first_n(fibonacci(), 8))
