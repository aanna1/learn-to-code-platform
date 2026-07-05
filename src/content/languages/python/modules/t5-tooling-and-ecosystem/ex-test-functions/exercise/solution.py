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


def test_add_item():
    cart = make_cart()
    cart.add("apple", 1.50)
    assert cart.total() == 1.50, f"Expected 1.50, got {cart.total()}"


def test_add_multiple_items():
    cart = make_cart()
    cart.add("apple", 1.50)
    cart.add("banana", 0.75)
    assert cart.total() == 2.25, f"Expected 2.25, got {cart.total()}"


def test_remove_item():
    cart = make_cart()
    cart.add("apple", 1.50)
    cart.add("banana", 0.75)
    cart.remove("apple")
    assert cart.count() == 1, f"Expected 1 item after remove, got {cart.count()}"


def test_add_invalid_price():
    cart = make_cart()
    try:
        cart.add("apple", 0)
        assert False, "Expected ValueError for price=0"
    except ValueError:
        pass


def test_remove_missing_item():
    cart = make_cart()
    try:
        cart.remove("ghost")
        assert False, "Expected KeyError for missing item"
    except KeyError:
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
