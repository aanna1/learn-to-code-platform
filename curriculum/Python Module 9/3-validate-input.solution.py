def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a whole number.")


def get_int_in_range(prompt, low, high):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Please enter a whole number.")
            continue
        if value < low or value > high:
            print(f"Please enter a number between {low} and {high}.")
            continue
        return value


if __name__ == "__main__":
    n = get_int("Enter a number: ")
    print(f"You entered: {n}")
    m = get_int_in_range("Enter 1–10: ", 1, 10)
    print(f"In range: {m}")
