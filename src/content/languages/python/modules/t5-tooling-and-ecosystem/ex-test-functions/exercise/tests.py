"""
Grader for ex-test-functions.

The learner must write five test functions. We verify each one:
  1. Exists and is callable.
  2. Passes when the ShoppingCart implementation is correct (solution).
  3. Fails (raises AssertionError or catches no exception when one is expected)
     when given a deliberately broken cart.

We import the submission, run each test function with both a good and a bad
implementation, and check the outcomes.
"""

import importlib
import sys
import types


# ── Helpers ─────────────────────────────────────────────────────────────────

def _make_good_cart():
    class ShoppingCart:
        def __init__(self):
            self.items = {}

        def add(self, name, price):
            if price <= 0:
                raise ValueError(f"price must be positive, got {price}")
            self.items[name] = price

        def remove(self, name):
            if name not in self.items:
                raise KeyError(name)
            del self.items[name]

        def total(self):
            return sum(self.items.values())

        def count(self):
            return len(self.items)

        def clear(self):
            self.items.clear()

    return ShoppingCart()


def _make_broken_cart():
    """Cart with multiple bugs — every test should catch at least one."""
    class BrokenCart:
        def __init__(self):
            self.items = {}

        def add(self, name, price):
            self.items[name] = price  # no validation, allows price=0

        def remove(self, name):
            self.items.pop(name, None)  # silently ignores missing names

        def total(self):
            return 0  # always wrong

        def count(self):
            return 0  # always wrong

        def clear(self):
            self.items.clear()

    return BrokenCart()


def _run(fn, cart):
    """Call fn() with cart injected by monkey-patching submission.make_cart."""
    import submission as sub
    original = sub.make_cart
    sub.make_cart = lambda: cart
    try:
        fn()
        return "pass"
    except (AssertionError, KeyError, ValueError, AttributeError) as e:
        return f"fail:{e}"
    finally:
        sub.make_cart = original


# ── Tests ────────────────────────────────────────────────────────────────────

def test_test_add_item_exists():
    """test_add_item is defined."""
    import submission as sub
    assert callable(getattr(sub, "test_add_item", None)), (
        "Define a function named test_add_item."
    )


def test_test_add_item_passes_good_cart():
    """test_add_item passes with a correct ShoppingCart."""
    import submission as sub
    result = _run(sub.test_add_item, _make_good_cart())
    assert result == "pass", (
        f"test_add_item should pass with a correct cart, but got: {result}. "
        "Call cart.add('apple', 1.50) and assert cart.total() == 1.50."
    )


def test_test_add_item_catches_broken_total():
    """test_add_item catches a cart whose total() always returns 0."""
    import submission as sub
    result = _run(sub.test_add_item, _make_broken_cart())
    assert result != "pass", (
        "test_add_item should FAIL with a broken cart (total() returns 0), "
        "but it passed. Did you assert cart.total() == 1.50?"
    )


def test_test_add_multiple_items_passes_good_cart():
    """test_add_multiple_items passes with a correct cart."""
    import submission as sub
    result = _run(sub.test_add_multiple_items, _make_good_cart())
    assert result == "pass", (
        f"test_add_multiple_items should pass with a correct cart, but got: {result}. "
        "Add two items and assert total() equals their sum."
    )


def test_test_add_multiple_items_catches_broken():
    """test_add_multiple_items catches a cart whose total() is always 0."""
    import submission as sub
    result = _run(sub.test_add_multiple_items, _make_broken_cart())
    assert result != "pass", (
        "test_add_multiple_items should FAIL with a broken cart, but it passed."
    )


def test_test_remove_item_passes_good_cart():
    """test_remove_item passes with a correct cart."""
    import submission as sub
    result = _run(sub.test_remove_item, _make_good_cart())
    assert result == "pass", (
        f"test_remove_item should pass with a correct cart, but got: {result}. "
        "Add two items, remove one, assert count() == 1."
    )


def test_test_remove_item_catches_broken():
    """test_remove_item catches a cart whose count() always returns 0."""
    import submission as sub
    result = _run(sub.test_remove_item, _make_broken_cart())
    assert result != "pass", (
        "test_remove_item should FAIL with a broken cart (count() returns 0), but it passed."
    )


def test_test_add_invalid_price_passes_good_cart():
    """test_add_invalid_price passes when add(price=0) correctly raises ValueError."""
    import submission as sub
    result = _run(sub.test_add_invalid_price, _make_good_cart())
    assert result == "pass", (
        f"test_add_invalid_price should pass with a correct cart, but got: {result}. "
        "Use try/except ValueError around cart.add('apple', 0)."
    )


def test_test_add_invalid_price_catches_broken():
    """test_add_invalid_price catches a cart that accepts price=0 silently."""
    import submission as sub
    result = _run(sub.test_add_invalid_price, _make_broken_cart())
    assert result != "pass", (
        "test_add_invalid_price should FAIL with a broken cart (no validation), "
        "but it passed. Make sure you assert that ValueError IS raised, "
        "and that the test fails if it is not."
    )


def test_test_remove_missing_item_passes_good_cart():
    """test_remove_missing_item passes when remove() correctly raises KeyError."""
    import submission as sub
    result = _run(sub.test_remove_missing_item, _make_good_cart())
    assert result == "pass", (
        f"test_remove_missing_item should pass with a correct cart, but got: {result}. "
        "Use try/except KeyError around cart.remove('ghost')."
    )


def test_test_remove_missing_item_catches_broken():
    """test_remove_missing_item catches a cart that silently ignores missing removes."""
    import submission as sub
    result = _run(sub.test_remove_missing_item, _make_broken_cart())
    assert result != "pass", (
        "test_remove_missing_item should FAIL with a broken cart (remove is a no-op), "
        "but it passed. Make sure you assert that KeyError IS raised, "
        "and fail the test if no exception is thrown."
    )


if __name__ == "__main__":
    cart = _make_good_cart()
    cart.add("apple", 1.50)
    cart.add("banana", 0.75)
    print("total:", cart.total())
    print("count:", cart.count())
    cart.remove("apple")
    print("count after remove:", cart.count())
