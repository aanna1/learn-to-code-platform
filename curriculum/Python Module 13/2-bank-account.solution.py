class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount

    @property
    def balance(self):
        return self._balance

    def __str__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self._balance})"


if __name__ == "__main__":
    acc = BankAccount("Alice", 100)
    acc.deposit(50)
    acc.withdraw(30)
    print(acc)          # BankAccount(owner='Alice', balance=120)
    print(acc.balance)  # 120
