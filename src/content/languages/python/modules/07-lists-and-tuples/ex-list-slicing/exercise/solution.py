def first_and_last(items):
    """Return a tuple of (first_element, last_element)."""
    return (items[0], items[-1])


def middle(items):
    """Return all elements except the first and last."""
    return items[1:-1]


if __name__ == "__main__":
    print(first_and_last(["Ada", "Grace", "Linus", "Guido"]))
    print(middle(["Ada", "Grace", "Linus", "Guido"]))
