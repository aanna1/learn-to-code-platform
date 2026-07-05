import json


class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def __repr__(self):
        # TODO: return something like Book('Dune', 'Frank Herbert', 1965)
        pass

    def __eq__(self, other):
        # TODO: return True if title, author, and year all match
        pass

    def to_dict(self):
        # TODO: return {"title": ..., "author": ..., "year": ...}
        pass

    @classmethod
    def from_dict(cls, d):
        # TODO: build and return a Book from the dict d
        pass


class Library:
    def __init__(self):
        self.books = []

    def add(self, book):
        # TODO: append book to self.books
        pass

    def find_by_author(self, author):
        # TODO: return a list of books where book.author == author
        pass

    def __len__(self):
        # TODO: return the number of books
        pass

    def to_dict(self):
        # TODO: return {"books": [each book as a dict]}
        pass

    @classmethod
    def from_dict(cls, d):
        # TODO: build a Library from {"books": [...]}
        pass


if __name__ == "__main__":
    lib = Library()
    lib.add(Book("Dune", "Frank Herbert", 1965))
    lib.add(Book("Dune Messiah", "Frank Herbert", 1969))
    lib.add(Book("Foundation", "Isaac Asimov", 1951))

    print(len(lib))
    print(lib.find_by_author("Frank Herbert"))

    data = json.dumps(lib.to_dict())
    lib2 = Library.from_dict(json.loads(data))
    print(len(lib2))
