import types

from submission import square_evens, word_lengths, unique_squares, first_n_squares


def test_square_evens_basic():
    """square_evens returns squares of even numbers only."""
    result = square_evens([1, 2, 3, 4, 5])
    assert result == [4, 16], (
        f"square_evens([1, 2, 3, 4, 5]) should return [4, 16], got {result!r}. "
        "Filter for even numbers with 'if x % 2 == 0', then square with x ** 2."
    )


def test_square_evens_preserves_order():
    """square_evens preserves the order of even numbers."""
    result = square_evens([0, 7, 8, -2])
    assert result == [0, 64, 4], (
        f"square_evens([0, 7, 8, -2]) should return [0, 64, 4], got {result!r}. "
        "Even numbers in order: 0, 8, -2. Their squares: 0, 64, 4."
    )


def test_square_evens_empty():
    """square_evens returns an empty list when no evens are present."""
    result = square_evens([1, 3, 5])
    assert result == [], (
        f"square_evens([1, 3, 5]) should return [], got {result!r}. "
        "There are no even numbers in [1, 3, 5]."
    )


def test_word_lengths_basic():
    """word_lengths maps each word to its character count."""
    result = word_lengths(["cat", "elephant", "ox"])
    assert result == {"cat": 3, "elephant": 8, "ox": 2}, (
        f"word_lengths([\"cat\", \"elephant\", \"ox\"]) should return "
        f"{{'cat': 3, 'elephant': 8, 'ox': 2}}, got {result!r}. "
        "Use a dict comprehension: {w: len(w) for w in words}."
    )


def test_word_lengths_empty():
    """word_lengths returns an empty dict for an empty list."""
    result = word_lengths([])
    assert result == {}, (
        f"word_lengths([]) should return {{}}, got {result!r}."
    )


def test_unique_squares_deduplicates():
    """unique_squares removes duplicate squares from negatives and positives."""
    result = unique_squares([-2, -1, 0, 1, 2])
    assert result == {0, 1, 4}, (
        f"unique_squares([-2, -1, 0, 1, 2]) should return {{0, 1, 4}}, got {result!r}. "
        "Note that (-2)² == 2² == 4, so 4 appears only once in a set."
    )


def test_unique_squares_returns_set():
    """unique_squares returns a set, not a list."""
    result = unique_squares([1, 2, 3])
    assert isinstance(result, set), (
        f"unique_squares should return a set, got {type(result).__name__}. "
        "Use curly braces: {x ** 2 for x in nums}."
    )


def test_first_n_squares_values():
    """first_n_squares yields 0², 1², 2², ... up to n values."""
    result = list(first_n_squares(5))
    assert result == [0, 1, 4, 9, 16], (
        f"list(first_n_squares(5)) should return [0, 1, 4, 9, 16], got {result!r}. "
        "Use (x ** 2 for x in range(n))."
    )


def test_first_n_squares_is_generator():
    """first_n_squares returns a generator, not a list."""
    result = first_n_squares(3)
    assert isinstance(result, types.GeneratorType), (
        f"first_n_squares should return a generator, got {type(result).__name__}. "
        "Use parentheses: (x ** 2 for x in range(n)), not square brackets."
    )


def test_first_n_squares_zero():
    """first_n_squares(0) yields nothing."""
    result = list(first_n_squares(0))
    assert result == [], (
        f"list(first_n_squares(0)) should return [], got {result!r}."
    )


if __name__ == "__main__":
    print("square_evens:", square_evens([1, 2, 3, 4, 5]))
    print("word_lengths:", word_lengths(["cat", "elephant", "ox"]))
    print("unique_squares:", unique_squares([-2, -1, 0, 1, 2]))
    print("first_n_squares:", list(first_n_squares(5)))
