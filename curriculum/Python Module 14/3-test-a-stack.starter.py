import unittest


class Stack:
    """A simple last-in, first-out stack."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def size(self):
        return len(self._items)

    def is_empty(self):
        return len(self._items) == 0


class TestStack(unittest.TestCase):
    def test_push_increases_size(self):
        # TODO: arrange a new Stack, push one item, assert size() == 1
        pass

    def test_pop_returns_last_pushed(self):
        # TODO: push two items, pop once, assert you get the second item back
        pass

    def test_pop_empty_raises(self):
        # TODO: assert that popping an empty stack raises IndexError
        pass

    def test_peek_does_not_remove(self):
        # TODO: push an item, peek, assert size is still 1
        pass


if __name__ == "__main__":
    unittest.main(argv=[""], exit=False, verbosity=2)
