def test_greets_ada():
    "greet('Ada') returns 'Hello, Ada!'"
    assert greet("Ada") == "Hello, Ada!"


def test_greets_sam():
    "greet('Sam') returns 'Hello, Sam!'"
    assert greet("Sam") == "Hello, Sam!"


def test_ends_with_exclamation():
    "the greeting ends with an exclamation mark"
    assert greet("Lin").endswith("!")
