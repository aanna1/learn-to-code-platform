def format_receipt(price, quantity, tax_rate):
    """Return a formatted receipt string with subtotal, tax, and total."""
    # TODO: compute subtotal, tax, and total
    # TODO: return a string with three lines, each value formatted to 2 decimal places
    # Hint: use :.2f inside f-strings, and \n to join lines
    pass


if __name__ == "__main__":
    print(format_receipt(10.0, 3, 0.1))
    # should print:
    # Subtotal: 30.00
    # Tax: 3.00
    # Total: 33.00
