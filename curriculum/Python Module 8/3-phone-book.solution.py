def add_contact(book, name, number):
    """Add or update name -> number in book. Return the modified book."""
    book[name] = number
    return book


def lookup(book, name):
    """Return the number for name, or None if not found."""
    return book.get(name)


def remove_contact(book, name):
    """Remove name from book if present; do nothing if not. Return the book."""
    book.pop(name, None)
    return book


def all_names(book):
    """Return a sorted list of all names in the book."""
    return sorted(book.keys())


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
