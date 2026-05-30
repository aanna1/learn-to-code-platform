def filter_words(words, min_length):
    """
    Return words longer than min_length, lowercased and sorted alphabetically.
    """
    return sorted([word.lower() for word in words if len(word) > min_length])


if __name__ == "__main__":
    print(filter_words(["Hello", "WORLD", "Python", "hi", "OK"], min_length=2))
    # ["hello", "python", "world"]
