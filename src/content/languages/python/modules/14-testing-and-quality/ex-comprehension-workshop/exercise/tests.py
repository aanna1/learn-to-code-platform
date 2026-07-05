from submission import squares_of_evens, word_lengths, long_words


# ---------------------------------------------------------------------------
# squares_of_evens
# ---------------------------------------------------------------------------

def test_squares_of_evens_basic():
    """squares_of_evens returns squares of only the even numbers."""
    result = squares_of_evens([1, 2, 3, 4, 5, 6])
    assert result == [4, 16, 36], (
        f"squares_of_evens([1,2,3,4,5,6]) should be [4, 16, 36], got {result!r}. "
        "Filter for even numbers (n % 2 == 0) then square each one (n ** 2)."
    )


def test_squares_of_evens_all_odd():
    """squares_of_evens returns [] when all inputs are odd."""
    result = squares_of_evens([1, 3, 5])
    assert result == [], (
        f"squares_of_evens([1,3,5]) should be [], got {result!r}. "
        "No even numbers means no output."
    )


def test_squares_of_evens_empty():
    """squares_of_evens returns [] for an empty list."""
    result = squares_of_evens([])
    assert result == [], (
        f"squares_of_evens([]) should be [], got {result!r}."
    )


def test_squares_of_evens_negatives():
    """squares_of_evens handles negative even numbers."""
    result = squares_of_evens([-4, -3, -2, 1])
    assert result == [16, 4], (
        f"squares_of_evens([-4,-3,-2,1]) should be [16, 4], got {result!r}. "
        "Negative even numbers (-4, -2) still pass the even filter."
    )


# ---------------------------------------------------------------------------
# word_lengths
# ---------------------------------------------------------------------------

def test_word_lengths_basic():
    """word_lengths returns the length of each word in order."""
    result = word_lengths(["apple", "kiwi", "banana"])
    assert result == [5, 4, 6], (
        f"word_lengths(['apple','kiwi','banana']) should be [5, 4, 6], got {result!r}. "
        "Use len(w) for each word in the list."
    )


def test_word_lengths_empty():
    """word_lengths returns [] for an empty list."""
    result = word_lengths([])
    assert result == [], (
        f"word_lengths([]) should be [], got {result!r}."
    )


def test_word_lengths_preserves_order():
    """word_lengths preserves the order of the input."""
    result = word_lengths(["hi", "hello", "hey"])
    assert result == [2, 5, 3], (
        f"word_lengths(['hi','hello','hey']) should be [2, 5, 3], got {result!r}. "
        "The output order must match the input order."
    )


# ---------------------------------------------------------------------------
# long_words
# ---------------------------------------------------------------------------

def test_long_words_basic():
    """long_words returns only words meeting the minimum length."""
    result = long_words(["apple", "kiwi", "banana", "fig"], 5)
    assert result == ["apple", "banana"], (
        f"long_words([...], 5) should be ['apple', 'banana'], got {result!r}. "
        "Keep words where len(w) >= min_len."
    )


def test_long_words_none_qualify():
    """long_words returns [] when no words meet the minimum length."""
    result = long_words(["hi", "ok"], 5)
    assert result == [], (
        f"long_words(['hi','ok'], 5) should be [], got {result!r}."
    )


def test_long_words_all_qualify():
    """long_words returns all words when all meet the minimum length."""
    result = long_words(["python", "testing"], 3)
    assert result == ["python", "testing"], (
        f"long_words(['python','testing'], 3) should be ['python','testing'], got {result!r}."
    )


def test_long_words_boundary():
    """long_words includes words exactly at the minimum length."""
    result = long_words(["cat", "dog", "elephant"], 3)
    assert result == ["cat", "dog", "elephant"], (
        f"long_words(['cat','dog','elephant'], 3) should include all three (len >= 3), got {result!r}. "
        "min_len is inclusive — use >= not >."
    )


if __name__ == "__main__":
    print(squares_of_evens([1, 2, 3, 4, 5, 6]))
    print(word_lengths(["apple", "kiwi", "banana"]))
    print(long_words(["apple", "kiwi", "banana", "fig"], 5))
