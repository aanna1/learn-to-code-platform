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
        s = Stack()
        s.push(42)
        self.assertEqual(s.size(), 1)

    def test_pop_returns_last_pushed(self):
        s = Stack()
        s.push("first")
        s.push("second")
        result = s.pop()
        self.assertEqual(result, "second")

    def test_pop_empty_raises(self):
        s = Stack()
        with self.assertRaises(IndexError):
            s.pop()

    def test_peek_does_not_remove(self):
        s = Stack()
        s.push(99)
        s.peek()
        self.assertEqual(s.size(), 1)


if __name__ == "__main__":
    unittest.main(argv=[""], exit=False, verbosity=2)
