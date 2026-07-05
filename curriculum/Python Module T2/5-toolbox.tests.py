from collections import Counter, defaultdict

from submission import group_by_length, safe_append, top_n_words, word_counts


# ---------------------------------------------------------------------------
# word_counts
# ---------------------------------------------------------------------------

def test_word_counts_basic():
    """word_counts counts word frequencies correctly."""
    result = word_counts("the cat sat on the mat the cat")
    assert result["the"] == 3 and result["cat"] == 2, (
        f"word_counts('the cat sat on the mat the cat') should give "
        f"the=3 and cat=2, got {dict(result)}."
    )


def test_word_counts_returns_counter():
    """word_counts returns a Counter instance."""
    result = word_counts("hello world")
    assert isinstance(result, Counter), (
        f"word_counts must return a Counter, got {type(result).__name__}. "
        "Import Counter from collections and return Counter(words)."
    )


def test_word_counts_lowercases():
    """word_counts lowercases words."""
    result = word_counts("Hello HELLO hello")
    assert result["hello"] == 3, (
        f"word_counts should lowercase all words. "
        f"'Hello HELLO hello' should give hello=3, got {dict(result)}."
    )


def test_word_counts_strips_punctuation():
    """word_counts strips leading and trailing punctuation."""
    result = word_counts("Hello, hello! World.")
    assert result["hello"] == 2 and result["world"] == 1, (
        f"word_counts should strip punctuation like commas, exclamation marks, and periods. "
        f"Got {dict(result)}."
    )


def test_word_counts_empty_string():
    """word_counts of an empty string returns an empty Counter."""
    result = word_counts("")
    assert len(result) == 0, (
        f"word_counts('') should return an empty Counter, got {dict(result)}."
    )


# ---------------------------------------------------------------------------
# group_by_length
# ---------------------------------------------------------------------------

def test_group_by_length_basic():
    """group_by_length groups words by their length."""
    result = group_by_length(["cat", "dog", "ox", "ant", "be"])
    assert set(result[3]) == {"cat", "dog", "ant"} and set(result[2]) == {"ox", "be"}, (
        f"group_by_length should group words by length. "
        f"Got {dict(result)}."
    )


def test_group_by_length_returns_defaultdict():
    """group_by_length returns a defaultdict."""
    result = group_by_length(["cat"])
    assert isinstance(result, defaultdict), (
        f"group_by_length must return a defaultdict, got {type(result).__name__}. "
        "Use defaultdict(list) from collections."
    )


def test_group_by_length_sorted():
    """group_by_length sorts words alphabetically within each group."""
    result = group_by_length(["dog", "ant", "cat"])
    assert result[3] == ["ant", "cat", "dog"], (
        f"Words within each length group should be sorted alphabetically. "
        f"For length 3: expected ['ant', 'cat', 'dog'], got {result[3]}."
    )


def test_group_by_length_empty():
    """group_by_length of an empty list returns a defaultdict with no entries."""
    result = group_by_length([])
    assert len(result) == 0, (
        f"group_by_length([]) should return an empty defaultdict, got {dict(result)}."
    )


# ---------------------------------------------------------------------------
# top_n_words
# ---------------------------------------------------------------------------

def test_top_n_words_basic():
    """top_n_words returns the n most common words in order."""
    result = top_n_words("the cat sat on the mat the cat", 2)
    assert result == [("the", 3), ("cat", 2)], (
        f"top_n_words('the cat sat...', 2) should return [('the', 3), ('cat', 2)], "
        f"got {result}."
    )


def test_top_n_words_returns_list_of_tuples():
    """top_n_words returns a list of (word, count) tuples."""
    result = top_n_words("hello world hello", 1)
    assert isinstance(result, list) and len(result) == 1, (
        f"top_n_words with n=1 should return a list with one tuple, got {result}."
    )
    word, count = result[0]
    assert word == "hello" and count == 2, (
        f"top_n_words('hello world hello', 1) should return [('hello', 2)], got {result}."
    )


def test_top_n_words_respects_punctuation_stripping():
    """top_n_words counts 'hello' and 'hello,' as the same word."""
    result = top_n_words("hello, hello! hello", 1)
    assert result[0] == ("hello", 3), (
        f"top_n_words should strip punctuation before counting. "
        f"'hello,' and 'hello!' should both count as 'hello'. Got {result}."
    )


# ---------------------------------------------------------------------------
# safe_append
# ---------------------------------------------------------------------------

def test_safe_append_basic():
    """safe_append appends to an existing list and returns it."""
    lst = [1, 2]
    result = safe_append(3, lst)
    assert result == [1, 2, 3], (
        f"safe_append(3, [1, 2]) should return [1, 2, 3], got {result}."
    )
    assert result is lst, (
        "safe_append should modify and return the same list object when one is provided."
    )


def test_safe_append_creates_fresh_list():
    """safe_append creates a fresh list each time items is omitted."""
    a = safe_append("x")
    b = safe_append("y")
    assert a == ["x"] and b == ["y"], (
        f"safe_append('x') and safe_append('y') should create separate lists. "
        f"Got a={a}, b={b}. "
        "Use 'items=None' as the default, not 'items=[]'."
    )


def test_safe_append_no_mutable_default():
    """safe_append does not share state between calls."""
    a = safe_append(1)
    safe_append(2)
    c = safe_append(3)
    assert a == [1], (
        f"safe_append must not use a mutable default argument. "
        f"After calling safe_append(1), safe_append(2), safe_append(3) separately, "
        f"the first result should still be [1], got {a}. "
        "Use 'if items is None: items = []' inside the function."
    )


def test_safe_append_returns_list():
    """safe_append returns the list."""
    result = safe_append("hello")
    assert isinstance(result, list) and result == ["hello"], (
        f"safe_append('hello') should return ['hello'], got {result}."
    )


if __name__ == "__main__":
    text = "the cat sat on the mat the cat"
    print(word_counts(text))
    print(top_n_words(text, 2))

    words = ["cat", "dog", "ox", "ant", "be"]
    print(dict(group_by_length(words)))

    a = safe_append("x")
    b = safe_append("y")
    print(a, b)
