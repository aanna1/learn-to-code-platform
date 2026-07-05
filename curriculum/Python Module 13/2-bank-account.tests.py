def test_initial_balance_zero():
    "default starting balance is 0"
    acc = BankAccount("Alice")
    assert acc.balance == 0, (
        f"BankAccount('Alice').balance should be 0, got {acc.balance!r}. "
        "Make sure the default value for balance in __init__ is 0."
    )

def test_initial_balance_given():
    "starting balance uses the provided value"
    acc = BankAccount("Bob", 500)
    assert acc.balance == 500, (
        f"BankAccount('Bob', 500).balance should be 500, got {acc.balance!r}."
    )

def test_deposit_adds_to_balance():
    "deposit increases the balance correctly"
    acc = BankAccount("Alice", 100)
    acc.deposit(50)
    assert acc.balance == 150, (
        f"After depositing 50 into balance of 100, expected 150, got {acc.balance!r}."
    )

def test_withdraw_reduces_balance():
    "withdraw decreases the balance correctly"
    acc = BankAccount("Alice", 200)
    acc.withdraw(80)
    assert acc.balance == 120, (
        f"After withdrawing 80 from balance of 200, expected 120, got {acc.balance!r}."
    )

def test_deposit_nonpositive_raises():
    "deposit raises ValueError for zero or negative amount"
    import traceback
    acc = BankAccount("Alice", 100)
    for bad in [0, -10]:
        try:
            acc.deposit(bad)
            assert False, f"deposit({bad}) should raise ValueError but did not."
        except ValueError:
            pass
        except Exception as e:
            assert False, f"deposit({bad}) raised {type(e).__name__} instead of ValueError."

def test_withdraw_nonpositive_raises():
    "withdraw raises ValueError for zero or negative amount"
    acc = BankAccount("Alice", 100)
    for bad in [0, -5]:
        try:
            acc.withdraw(bad)
            assert False, f"withdraw({bad}) should raise ValueError but did not."
        except ValueError:
            pass
        except Exception as e:
            assert False, f"withdraw({bad}) raised {type(e).__name__} instead of ValueError."

def test_withdraw_insufficient_funds_raises():
    "withdraw raises ValueError when amount exceeds balance"
    acc = BankAccount("Alice", 50)
    try:
        acc.withdraw(100)
        assert False, "withdraw(100) on a balance of 50 should raise ValueError."
    except ValueError:
        pass
    except Exception as e:
        assert False, f"Expected ValueError, got {type(e).__name__}."

def test_balance_is_property():
    "balance is accessible as an attribute, not a method call"
    acc = BankAccount("Alice", 75)
    result = acc.balance
    assert result == 75, (
        f"acc.balance should return 75, got {result!r}. "
        "Make sure balance is decorated with @property."
    )

def test_str_contains_owner_and_balance():
    "str() includes the owner name and current balance"
    acc = BankAccount("Alice", 120)
    s = str(acc)
    assert "Alice" in s and "120" in s, (
        f"str(acc) should contain 'Alice' and '120', got: {s!r}"
    )
