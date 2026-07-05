from collections import Counter, defaultdict


PUNCTUATION = '.,!?;:\"\''


def word_counts(text: str) -> Counter:
    """Return a Counter of word frequencies in text (lowercased, punctuation-stripped).

    word_counts("Hello, hello! World.") -> Counter({'hello': 2, 'world': 1})
    """
    words = []
    for raw in text.split():
        word = raw.lower().strip(PUNCTUATION)
        if word:
            words.append(word)
    return Counter(words)


def group_by_length(words: list[str]) -> defaultdict:
    """Return a defaultdict mapping word length -> sorted list of words.

    group_by_length(["cat", "ox", "ant"]) -> {3: ['ant', 'cat'], 2: ['ox']}
    """
    groups: defaultdict[int, list[str]] = defaultdict(list)
    for word in words:
        groups[len(word)].append(word)
    for key in groups:
        groups[key].sort()
    return groups


def top_n_words(text: str, n: int) -> list[tuple[str, int]]:
    """Return the n most common words as [(word, count), ...], most frequent first.

    top_n_words("the cat sat on the mat the cat", 2) -> [('the', 3), ('cat', 2)]
    """
    return word_counts(text).most_common(n)


def safe_append(item, items=None):
    """Append item to items and return the list.

    If items is None, create a fresh list. Never use a mutable default argument.
    """
    if items is None:
        items = []
    items.append(item)
    return items


if __name__ == "__main__":
    text = "the cat sat on the mat the cat"
    print(word_counts(text))
    print(top_n_words(text, 2))

    words = ["cat", "dog", "ox", "ant", "be"]
    print(dict(group_by_length(words)))

    a = safe_append("x")
    b = safe_append("y")
    print(a, b)
