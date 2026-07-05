def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "undefined"


def safe_divide_message(a, b):
    result = safe_divide(a, b)
    if result == "undefined":
        return f"{a} / {b} is undefined"
    return f"{a} / {b} = {result}"


if __name__ == "__main__":
    print(safe_divide(10, 2))          # 5.0
    print(safe_divide(10, 0))          # undefined
    print(safe_divide_message(10, 2))  # 10 / 2 = 5.0
    print(safe_divide_message(10, 0))  # 10 / 0 is undefined
