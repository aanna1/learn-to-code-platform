from datetime import date


def days_between(year, month, day):
    # Return the number of days from today until the given date.
    # Use date.today() and date(year, month, day), then subtract.
    pass


def is_future(year, month, day):
    # Return True if the given date is strictly in the future, False otherwise.
    pass


if __name__ == "__main__":
    print(days_between(2026, 6, 30))   # some positive number
    print(days_between(2026, 1, 1))    # some negative number
    print(is_future(2026, 6, 30))      # True
    print(is_future(2026, 1, 1))       # False
