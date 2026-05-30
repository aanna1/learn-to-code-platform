

def test_basic_receipt():
    """format_receipt(10.0, 3, 0.1) returns the correct three-line string"""
    result = format_receipt(10.0, 3, 0.1)
    expected = "Subtotal: 30.00\nTax: 3.00\nTotal: 33.00"
    assert result == expected, (
        f"Expected:\n{expected!r}\nGot:\n{result!r}\n"
        "Check that each value uses :.2f and lines are joined with \\n."
    )


def test_zero_tax():
    """format_receipt with 0% tax has Tax: 0.00 and Total equals Subtotal"""
    result = format_receipt(5.0, 4, 0.0)
    expected = "Subtotal: 20.00\nTax: 0.00\nTotal: 20.00"
    assert result == expected, (
        f"Expected:\n{expected!r}\nGot:\n{result!r}"
    )


def test_fractional_tax():
    """format_receipt(1.0, 1, 0.5) with 50% tax"""
    result = format_receipt(1.0, 1, 0.5)
    expected = "Subtotal: 1.00\nTax: 0.50\nTotal: 1.50"
    assert result == expected, (
        f"Expected:\n{expected!r}\nGot:\n{result!r}"
    )


def test_returns_string():
    """format_receipt returns a string, not None"""
    result = format_receipt(10.0, 1, 0.1)
    assert isinstance(result, str), (
        f"format_receipt should return a string, got {type(result).__name__}. "
        "Use return, not print()."
    )


def test_three_lines():
    """format_receipt output has exactly three lines"""
    result = format_receipt(10.0, 3, 0.1)
    lines = result.split("\n")
    assert len(lines) == 3, (
        f"Expected 3 lines separated by \\n, got {len(lines)}: {lines!r}"
    )


def test_line_labels():
    """each line starts with the correct label"""
    result = format_receipt(10.0, 3, 0.1)
    lines = result.split("\n")
    assert lines[0].startswith("Subtotal: "), (
        f"First line should start with 'Subtotal: ', got {lines[0]!r}"
    )
    assert lines[1].startswith("Tax: "), (
        f"Second line should start with 'Tax: ', got {lines[1]!r}"
    )
    assert lines[2].startswith("Total: "), (
        f"Third line should start with 'Total: ', got {lines[2]!r}"
    )


if __name__ == "__main__":
    print(format_receipt(10.0, 3, 0.1))
    print()
    print(format_receipt(5.0, 4, 0.0))
