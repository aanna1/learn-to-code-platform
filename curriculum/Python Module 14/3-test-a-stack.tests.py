"""
Grader for the Test a Stack exercise.

Strategy:
1. Verify structural requirements (class exists, inherits correctly, has all 4 methods).
2. Run each required test method against the CORRECT Stack — all must pass.
3. Run each required test method against a BROKEN Stack — all must fail.
   If a test passes against a broken Stack, it's not checking anything.
"""

import io
import unittest


from submission import TestStack


# ---------------------------------------------------------------------------
# A correct Stack implementation (same as provided in starter/solution)
# ---------------------------------------------------------------------------
class _CorrectStack:
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


# ---------------------------------------------------------------------------
# A deliberately broken Stack — wrong on every behavior
# ---------------------------------------------------------------------------
class _BrokenStack:
    """All behaviors are wrong so a real test suite must catch them."""
    def __init__(self):
        self._items = []
    def push(self, item):
        self._items.append(item)
    def pop(self):
        # Never raises, always returns wrong value
        if not self._items:
            return None
        self._items.pop()
        return "WRONG"
    def peek(self):
        # Destroys the item (should not remove)
        if self._items:
            self._items.pop()
        return "WRONG"
    def size(self):
        return 0   # always reports empty
    def is_empty(self):
        return True


# ---------------------------------------------------------------------------
# Helper: run one test method with a specific Stack class injected
# ---------------------------------------------------------------------------
def _run_method_with_stack(method_name, stack_class):
    """
    Patch the submission's 'Stack' name to stack_class, run the method,
    restore, return (passed, message).
    """
    import submission as sub
    original = getattr(sub, "Stack", None)
    setattr(sub, "Stack", stack_class)
    try:
        suite = unittest.TestLoader().loadTestsFromName(method_name, TestStack)
        buf = io.StringIO()
        runner = unittest.TextTestRunner(stream=buf, verbosity=0)
        result = runner.run(suite)
        if result.wasSuccessful():
            return True, ""
        failures = result.failures + result.errors
        msg = failures[0][1].strip().splitlines()[-1] if failures else "unknown"
        return False, msg
    except Exception as e:
        return False, str(e)
    finally:
        if original is not None:
            setattr(sub, "Stack", original)
        elif hasattr(sub, "Stack"):
            delattr(sub, "Stack")


# ---------------------------------------------------------------------------
# Structural tests
# ---------------------------------------------------------------------------

def test_has_required_methods():
    """TestStack defines all four required test methods."""
    required = [
        "test_push_increases_size",
        "test_pop_returns_last_pushed",
        "test_pop_empty_raises",
        "test_peek_does_not_remove",
    ]
    missing = [m for m in required if not callable(getattr(TestStack, m, None))]
    assert not missing, (
        f"TestStack is missing: {missing}. "
        "Add a method for each one listed in the exercise."
    )


def test_inherits_from_test_case():
    """TestStack inherits from unittest.TestCase."""
    assert issubclass(TestStack, unittest.TestCase), (
        "TestStack must inherit from unittest.TestCase: "
        "class TestStack(unittest.TestCase): ..."
    )


# ---------------------------------------------------------------------------
# Correctness tests: each method must PASS against the correct Stack
# ---------------------------------------------------------------------------

def test_push_increases_size_passes_on_correct_stack():
    """test_push_increases_size passes when the Stack works correctly."""
    ok, msg = _run_method_with_stack("test_push_increases_size", _CorrectStack)
    assert ok, (
        "test_push_increases_size failed on a correct Stack.\n" + msg +
        "\nHint: create a Stack, push one item, self.assertEqual(s.size(), 1)."
    )


def test_pop_returns_last_pushed_passes_on_correct_stack():
    """test_pop_returns_last_pushed passes when the Stack works correctly."""
    ok, msg = _run_method_with_stack("test_pop_returns_last_pushed", _CorrectStack)
    assert ok, (
        "test_pop_returns_last_pushed failed on a correct Stack.\n" + msg +
        "\nHint: push two items, pop once, assertEqual the result to the second item."
    )


def test_pop_empty_raises_passes_on_correct_stack():
    """test_pop_empty_raises passes when the Stack works correctly."""
    ok, msg = _run_method_with_stack("test_pop_empty_raises", _CorrectStack)
    assert ok, (
        "test_pop_empty_raises failed on a correct Stack.\n" + msg +
        "\nHint: with self.assertRaises(IndexError): s.pop() on an empty Stack."
    )


def test_peek_does_not_remove_passes_on_correct_stack():
    """test_peek_does_not_remove passes when the Stack works correctly."""
    ok, msg = _run_method_with_stack("test_peek_does_not_remove", _CorrectStack)
    assert ok, (
        "test_peek_does_not_remove failed on a correct Stack.\n" + msg +
        "\nHint: push one item, peek, assertEqual(s.size(), 1)."
    )


# ---------------------------------------------------------------------------
# Discrimination tests: each method must FAIL against the broken Stack
# ---------------------------------------------------------------------------

def test_push_increases_size_catches_broken_stack():
    """test_push_increases_size fails when size() always returns 0."""
    ok, _ = _run_method_with_stack("test_push_increases_size", _BrokenStack)
    assert not ok, (
        "test_push_increases_size passed on a broken Stack — it's not checking size(). "
        "Make sure the test calls self.assertEqual(s.size(), 1) after pushing one item."
    )


def test_pop_returns_last_pushed_catches_broken_stack():
    """test_pop_returns_last_pushed fails when pop() returns the wrong value."""
    ok, _ = _run_method_with_stack("test_pop_returns_last_pushed", _BrokenStack)
    assert not ok, (
        "test_pop_returns_last_pushed passed on a broken Stack — it's not checking the return value. "
        "Make sure the test asserts that pop() returns the last item you pushed."
    )


def test_pop_empty_raises_catches_broken_stack():
    """test_pop_empty_raises fails when pop() never raises on an empty stack."""
    ok, _ = _run_method_with_stack("test_pop_empty_raises", _BrokenStack)
    assert not ok, (
        "test_pop_empty_raises passed on a broken Stack that never raises — the test is not checking for IndexError. "
        "Use self.assertRaises(IndexError) as a context manager."
    )


def test_peek_does_not_remove_catches_broken_stack():
    """test_peek_does_not_remove fails when peek() removes the item."""
    ok, _ = _run_method_with_stack("test_peek_does_not_remove", _BrokenStack)
    assert not ok, (
        "test_peek_does_not_remove passed on a broken Stack where peek() removes items — the test is not checking size after peek(). "
        "Make sure the test calls self.assertEqual(s.size(), 1) after peek()."
    )


if __name__ == "__main__":
    pass
