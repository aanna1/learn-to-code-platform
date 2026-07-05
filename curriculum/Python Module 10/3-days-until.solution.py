from datetime import date


def days_between(year, month, day):
    target = date(year, month, day)
    return (target - date.today()).days


def is_future(year, month, day):
    return days_between(year, month, day) > 0


if __name__ == "__main__":
    print(days_between(2026, 6, 30))   # positive — future date
    print(days_between(2026, 1, 1))    # negative — past date
    print(is_future(2026, 6, 30))      # True
    print(is_future(2026, 1, 1))       # False
