def format_receipt(price, quantity, tax_rate):
    """Return a formatted receipt string with subtotal, tax, and total."""
    subtotal = price * quantity
    tax = subtotal * tax_rate
    total = subtotal + tax
    return f"Subtotal: {subtotal:.2f}\nTax: {tax:.2f}\nTotal: {total:.2f}"


if __name__ == "__main__":
    print(format_receipt(10.0, 3, 0.1))
    print()
    print(format_receipt(5.0, 4, 0.0))
    print()
    print(format_receipt(1.0, 1, 0.5))
