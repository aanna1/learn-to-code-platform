import json


def test_book_repr_format():
    "Book repr includes title, author, and year"
    b = Book("Dune", "Frank Herbert", 1965)
    r = repr(b)
    assert "Dune" in r and "Frank Herbert" in r and "1965" in r, (
        f"repr(Book(...)) should contain title, author, and year. Got: {r!r}"
    )

def test_book_eq_same():
    "Two Books with identical data are equal"
    a = Book("Dune", "Frank Herbert", 1965)
    b = Book("Dune", "Frank Herbert", 1965)
    assert a == b, "Two Books with the same title, author, and year should be equal."

def test_book_eq_different_year():
    "Books with different years are not equal"
    a = Book("Dune", "Frank Herbert", 1965)
    b = Book("Dune", "Frank Herbert", 1969)
    assert a != b, "Books with different years should not be equal."

def test_book_to_dict():
    "Book.to_dict() returns the correct keys and values"
    b = Book("Foundation", "Isaac Asimov", 1951)
    d = b.to_dict()
    assert d == {"title": "Foundation", "author": "Isaac Asimov", "year": 1951}, (
        f"Book.to_dict() returned unexpected value: {d!r}"
    )

def test_book_from_dict():
    "Book.from_dict() rebuilds an equivalent Book"
    d = {"title": "Foundation", "author": "Isaac Asimov", "year": 1951}
    b = Book.from_dict(d)
    assert b.title == "Foundation" and b.author == "Isaac Asimov" and b.year == 1951, (
        f"Book.from_dict(d) did not set attributes correctly: {b!r}"
    )

def test_library_add_and_len():
    "Library.add() and __len__ work together"
    lib = Library()
    lib.add(Book("Dune", "Frank Herbert", 1965))
    lib.add(Book("Foundation", "Isaac Asimov", 1951))
    assert len(lib) == 2, f"After adding 2 books, len(lib) should be 2, got {len(lib)!r}."

def test_library_find_by_author_found():
    "find_by_author returns all books by the given author"
    lib = Library()
    lib.add(Book("Dune", "Frank Herbert", 1965))
    lib.add(Book("Dune Messiah", "Frank Herbert", 1969))
    lib.add(Book("Foundation", "Isaac Asimov", 1951))
    results = lib.find_by_author("Frank Herbert")
    assert len(results) == 2, (
        f"find_by_author('Frank Herbert') should return 2 books, got {len(results)}."
    )

def test_library_find_by_author_not_found():
    "find_by_author returns an empty list when no books match"
    lib = Library()
    lib.add(Book("Foundation", "Isaac Asimov", 1951))
    results = lib.find_by_author("Unknown Author")
    assert results == [], (
        f"find_by_author for an unknown author should return [], got {results!r}."
    )

def test_library_round_trip():
    "Library survives a to_dict / from_dict round-trip"
    lib = Library()
    lib.add(Book("Dune", "Frank Herbert", 1965))
    lib.add(Book("Foundation", "Isaac Asimov", 1951))

    data = json.dumps(lib.to_dict())
    lib2 = Library.from_dict(json.loads(data))

    assert len(lib2) == 2, (
        f"After round-trip, library should have 2 books, got {len(lib2)}."
    )
    assert lib2.books[0] == lib.books[0], (
        f"First book after round-trip should equal the original. Got: {lib2.books[0]!r}"
    )
