def word_count(text):
    """
    Return a dict mapping each word in text to its frequency.
    Count case-insensitively: treat 'The' and 'the' as the same word.
    """
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


if __name__ == "__main__":
    print(word_count("the quick brown fox the lazy fox"))
    # {'the': 2, 'quick': 1, 'brown': 1, 'fox': 2, 'lazy': 1}
    print(word_count("Hello hello HELLO"))
    # {'hello': 3}
