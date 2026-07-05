class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance

    def deposit(self, amount):
        # TODO: raise ValueError if amount is not positive
        # then add amount to self._balance
        pass

    def withdraw(self, amount):
        # TODO: raise ValueError if amount is not positive
        # TODO: raise ValueError if amount exceeds self._balance
        # then subtract amount from self._balance
        pass

    @property
    def balance(self):
        # TODO: return the current balance
        pass

    def __str__(self):
        # TODO: return a string like: BankAccount(owner='Alice', balance=120)
        pass


if __name__ == "__main__":
    acc = BankAccount("Alice", 100)
    acc.deposit(50)
    acc.withdraw(30)
    print(acc)          # BankAccount(owner='Alice', balance=120)
    print(acc.balance)  # 120
