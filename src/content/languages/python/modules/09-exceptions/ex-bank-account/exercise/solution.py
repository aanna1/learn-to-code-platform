def deposit(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    return balance + amount


def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError(f"insufficient funds: balance is {balance}")
    return balance - amount


def transfer(from_balance, to_balance, amount):
    new_from = withdraw(from_balance, amount)
    new_to = deposit(to_balance, amount)
    return (new_from, new_to)


if __name__ == "__main__":
    print(deposit(100, 50))           # 150
    print(withdraw(100, 30))          # 70
    print(transfer(100, 50, 40))      # (60, 90)
    try:
        withdraw(100, 150)
    except ValueError as e:
        print(f"Error: {e}")          # Error: insufficient funds: balance is 100
