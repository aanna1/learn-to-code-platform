def squares_of_evens(numbers):
    """Return a list of squares of even numbers in `numbers`."""
    return [n ** 2 for n in numbers if n % 2 == 0]


def word_lengths(words):
    """Return a list of the length of each word in `words`."""
    return [len(w) for w in words]


def long_words(words, min_len):
    """Return words from `words` whose length is >= min_len."""
    return [w for w in words if len(w) >= min_len]


if __name__ == "__main__":
    print(squares_of_evens([1, 2, 3, 4, 5, 6]))
    print(word_lengths(["apple", "kiwi", "banana"]))
    print(long_words(["apple", "kiwi", "banana", "fig"], 5))
