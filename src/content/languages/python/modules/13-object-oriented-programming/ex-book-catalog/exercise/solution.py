import json


class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def __repr__(self):
        return f"Book({self.title!r}, {self.author!r}, {self.year})"

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.title == other.title and self.author == other.author and self.year == other.year

    def to_dict(self):
        return {"title": self.title, "author": self.author, "year": self.year}

    @classmethod
    def from_dict(cls, d):
        return cls(d["title"], d["author"], d["year"])


class Library:
    def __init__(self):
        self.books = []

    def add(self, book):
        self.books.append(book)

    def find_by_author(self, author):
        return [b for b in self.books if b.author == author]

    def __len__(self):
        return len(self.books)

    def to_dict(self):
        return {"books": [b.to_dict() for b in self.books]}

    @classmethod
    def from_dict(cls, d):
        lib = cls()
        for book_dict in d["books"]:
            lib.add(Book.from_dict(book_dict))
        return lib


if __name__ == "__main__":
    lib = Library()
    lib.add(Book("Dune", "Frank Herbert", 1965))
    lib.add(Book("Dune Messiah", "Frank Herbert", 1969))
    lib.add(Book("Foundation", "Isaac Asimov", 1951))

    print(len(lib))                           # 3
    print(lib.find_by_author("Frank Herbert"))

    data = json.dumps(lib.to_dict())
    lib2 = Library.from_dict(json.loads(data))
    print(len(lib2))                          # 3
