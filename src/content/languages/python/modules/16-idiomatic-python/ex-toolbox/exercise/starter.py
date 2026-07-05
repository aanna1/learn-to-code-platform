from collections import Counter, defaultdict


PUNCTUATION = '.,!?;:\"\''


def word_counts(text: str) -> Counter:
    """Return a Counter of word frequencies in text (lowercased, punctuation-stripped).

    word_counts("Hello, hello! World.") -> Counter({'hello': 2, 'world': 1})
    """
    # TODO: split text, lowercase and strip punctuation from each word, count them
    ...


def group_by_length(words: list[str]) -> defaultdict:
    """Return a defaultdict mapping word length -> sorted list of words.

    group_by_length(["cat", "ox", "ant"]) -> {3: ['ant', 'cat'], 2: ['ox']}
    """
    # TODO: build a defaultdict(list), group words by len, sort each group
    ...


def top_n_words(text: str, n: int) -> list[tuple[str, int]]:
    """Return the n most common words as [(word, count), ...], most frequent first.

    top_n_words("the cat sat on the mat the cat", 2) -> [('the', 3), ('cat', 2)]
    """
    # TODO: use word_counts(), then call .most_common(n)
    ...


def safe_append(item, items=None):
    """Append item to items and return the list.

    If items is None, create a fresh list. Never use a mutable default argument.
    """
    # TODO: create a fresh list when items is None, append item, return list
    ...


if __name__ == "__main__":
    text = "the cat sat on the mat the cat"
    print(word_counts(text))
    print(top_n_words(text, 2))

    words = ["cat", "dog", "ox", "ant", "be"]
    print(dict(group_by_length(words)))

    a = safe_append("x")
    b = safe_append("y")
    print(a, b)
