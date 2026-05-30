def filter_words(words, min_length):
    """
    Return words longer than min_length, lowercased and sorted alphabetically.
    Use a single list comprehension for filtering and lowercasing.
    """
    # TODO: write a list comprehension that:
    #   - iterates over words
    #   - keeps only words where len(word) > min_length
    #   - converts each word to lowercase with word.lower()
    # Then wrap it in sorted() and return the result.
    pass


if __name__ == "__main__":
    print(filter_words(["Hello", "WORLD", "Python", "hi", "OK"], min_length=2))
    # ["hello", "python", "world"]
