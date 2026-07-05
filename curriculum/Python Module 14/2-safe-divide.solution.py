def safe_divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


# Assert 1: basic division
assert safe_divide(10, 2) == 5.0, "10 / 2 should be 5.0"

# Assert 2: float result
assert safe_divide(7, 2) == 3.5, "7 / 2 should be 3.5"

# Assert 3: zero numerator
assert safe_divide(0, 5) == 0.0, "0 / 5 should be 0.0"

# Assert 4: ValueError for zero denominator
raised = False
try:
    safe_divide(10, 0)
except ValueError:
    raised = True
assert raised, "safe_divide(10, 0) should raise ValueError"


if __name__ == "__main__":
    print(safe_divide(10, 2))
    print(safe_divide(7, 2))
    print(safe_divide(0, 5))
    try:
        safe_divide(10, 0)
    except ValueError as e:
        print(f"Caught: {e}")
