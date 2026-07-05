def safe_divide(a, b):
    # Try the division; catch ZeroDivisionError and return "undefined"
    pass


def safe_divide_message(a, b):
    # Return a formatted string like "10 / 2 = 5.0" or "10 / 0 is undefined"
    pass


if __name__ == "__main__":
    print(safe_divide(10, 2))          # 5.0
    print(safe_divide(10, 0))          # undefined
    print(safe_divide_message(10, 2))  # 10 / 2 = 5.0
    print(safe_divide_message(10, 0))  # 10 / 0 is undefined
