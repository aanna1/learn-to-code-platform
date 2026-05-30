def add_contact(book, name, number):
    """Add or update name -> number in book. Return the modified book."""
    # TODO: assign book[name] = number, then return book
    pass


def lookup(book, name):
    """Return the number for name, or None if not found."""
    # TODO: use book.get(name) so a missing name returns None instead of crashing
    pass


def remove_contact(book, name):
    """Remove name from book if present; do nothing if not. Return the book."""
    # TODO: use book.pop(name, None) — the second argument makes it silent when missing
    pass


def all_names(book):
    """Return a sorted list of all names in the book."""
    # TODO: return sorted(book.keys())
    pass


if __name__ == "__main__":
    book = {}
    book = add_contact(book, "Ada",   "555-0101")
    book = add_contact(book, "Grace", "555-0102")
    book = add_contact(book, "Ada",   "555-9999")
    print(lookup(book, "Ada"))    # 555-9999
    print(lookup(book, "Linus"))  # None
    print(all_names(book))        # ['Ada', 'Grace']
    book = remove_contact(book, "Grace")
    print(all_names(book))        # ['Ada']
