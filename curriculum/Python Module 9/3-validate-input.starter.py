def get_int(prompt):
    # This only tries once — your job is to add the loop so it keeps asking
    try:
        return int(input(prompt))
    except ValueError:
        print("Please enter a whole number.")
        # Missing: loop back and try again


def get_int_in_range(prompt, low, high):
    # This only tries once and doesn't check the range yet
    try:
        return int(input(prompt))
    except ValueError:
        print("Please enter a whole number.")
        # Missing: loop back, and add the range check


if __name__ == "__main__":
    n = get_int("Enter a number: ")
    print(f"You entered: {n}")
    m = get_int_in_range("Enter 1–10: ", 1, 10)
    print(f"In range: {m}")
