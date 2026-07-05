class ShoppingCart:
    def __init__(self):
        self.items = {}

    def add(self, name: str, price: float) -> None:
        if price <= 0:
            raise ValueError(f"price must be positive, got {price}")
        self.items[name] = price

    def remove(self, name: str) -> None:
        if name not in self.items:
            raise KeyError(name)
        del self.items[name]

    def total(self) -> float:
        return sum(self.items.values())

    def count(self) -> int:
        return len(self.items)

    def clear(self) -> None:
        self.items.clear()


def make_cart() -> ShoppingCart:
    """Fixture: return a fresh empty cart."""
    return ShoppingCart()


# ── Write your tests below ─────────────────────────────────────────────────

def test_add_item():
    cart = make_cart()
    # add "apple" at price 1.50 and assert total() == 1.50
    pass


def test_add_multiple_items():
    cart = make_cart()
    # add two items and assert total() equals their combined price
    pass


def test_remove_item():
    cart = make_cart()
    # add two items, remove one, assert count() == 1
    pass


def test_add_invalid_price():
    cart = make_cart()
    # adding price=0 should raise ValueError — use try/except
    pass


def test_remove_missing_item():
    cart = make_cart()
    # removing a name that was never added should raise KeyError — use try/except
    pass


# ── Runner (do not edit) ────────────────────────────────────────────────────
if __name__ == "__main__":
    for fn in [
        test_add_item,
        test_add_multiple_items,
        test_remove_item,
        test_add_invalid_price,
        test_remove_missing_item,
    ]:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            print(f"FAIL  {fn.__name__}: {e}")
        except Exception as e:
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
