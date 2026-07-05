def deposit(balance, amount):
    # Raise ValueError if amount <= 0, otherwise return balance + amount
    pass


def withdraw(balance, amount):
    # Raise ValueError if amount <= 0
    # Raise ValueError if amount > balance
    # Otherwise return balance - amount
    pass


def transfer(from_balance, to_balance, amount):
    # Call withdraw then deposit; return (new_from, new_to)
    # Don't catch exceptions — let them propagate
    pass


if __name__ == "__main__":
    print(deposit(100, 50))           # 150
    print(withdraw(100, 30))          # 70
    print(transfer(100, 50, 40))      # (60, 90)
    try:
        withdraw(100, 150)
    except ValueError as e:
        print(f"Error: {e}")          # Error: insufficient funds: balance is 100
