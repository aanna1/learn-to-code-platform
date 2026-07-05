import sys
import os
import importlib
def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


# ── deposit ────────────────────────────────────────────────────────────────────

def test_deposit_normal():
    """deposit adds amount to balance and returns the new total."""
    m = _load()
    assert m.deposit(100, 50) == 150, "deposit(100, 50) should return 150."


def test_deposit_zero():
    """deposit raises ValueError for amount == 0."""
    m = _load()
    try:
        m.deposit(100, 0)
        assert False, "Expected ValueError for amount=0 but nothing was raised."
    except ValueError as e:
        assert "positive" in str(e), (
            f"Expected 'positive' in the error message but got: {e!r}"
        )


def test_deposit_negative():
    """deposit raises ValueError for negative amount."""
    m = _load()
    try:
        m.deposit(100, -10)
        assert False, "Expected ValueError for amount=-10 but nothing was raised."
    except ValueError as e:
        assert "positive" in str(e), f"Error message should mention 'positive': {e!r}"


def test_deposit_zero_balance():
    """deposit works when starting balance is 0."""
    m = _load()
    assert m.deposit(0, 50) == 50, "deposit(0, 50) should return 50."


# ── withdraw ───────────────────────────────────────────────────────────────────

def test_withdraw_normal():
    """withdraw subtracts amount from balance."""
    m = _load()
    assert m.withdraw(100, 30) == 70, "withdraw(100, 30) should return 70."


def test_withdraw_exact():
    """withdraw allows withdrawing exactly the full balance."""
    m = _load()
    assert m.withdraw(100, 100) == 0, "withdraw(100, 100) should return 0."


def test_withdraw_insufficient():
    """withdraw raises ValueError when amount exceeds balance."""
    m = _load()
    try:
        m.withdraw(100, 150)
        assert False, "Expected ValueError for overdraft but nothing was raised."
    except ValueError as e:
        assert "insufficient" in str(e).lower(), (
            f"Error message should mention 'insufficient': {e!r}"
        )
        assert "100" in str(e), (
            f"Error message should include the balance (100): {e!r}"
        )


def test_withdraw_zero():
    """withdraw raises ValueError for amount == 0."""
    m = _load()
    try:
        m.withdraw(100, 0)
        assert False, "Expected ValueError for amount=0 but nothing was raised."
    except ValueError as e:
        assert "positive" in str(e), f"Error should mention 'positive': {e!r}"


def test_withdraw_negative():
    """withdraw raises ValueError for negative amount."""
    m = _load()
    try:
        m.withdraw(100, -5)
        assert False, "Expected ValueError for amount=-5 but nothing was raised."
    except ValueError as e:
        assert "positive" in str(e), f"Error should mention 'positive': {e!r}"


# ── transfer ───────────────────────────────────────────────────────────────────

def test_transfer_normal():
    """transfer moves funds from one balance to another."""
    m = _load()
    result = m.transfer(100, 50, 40)
    assert result == (60, 90), f"transfer(100, 50, 40) should return (60, 90), got {result!r}."


def test_transfer_returns_tuple():
    """transfer returns a tuple of two values."""
    m = _load()
    result = m.transfer(200, 100, 50)
    assert isinstance(result, tuple) and len(result) == 2, (
        f"Expected a 2-tuple but got {result!r}."
    )


def test_transfer_propagates_insufficient():
    """transfer lets ValueError propagate when from_balance is too low."""
    m = _load()
    try:
        m.transfer(100, 50, 200)
        assert False, "Expected ValueError but nothing was raised."
    except ValueError as e:
        assert "insufficient" in str(e).lower(), (
            f"Expected insufficient-funds error, got: {e!r}"
        )


def test_transfer_propagates_negative():
    """transfer lets ValueError propagate for negative amount."""
    m = _load()
    try:
        m.transfer(100, 50, -10)
        assert False, "Expected ValueError but nothing was raised."
    except ValueError as e:
        assert "positive" in str(e), f"Expected 'positive' in message, got: {e!r}"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
            except Exception as e:
                print(f"ERR   {name}: {e}")
