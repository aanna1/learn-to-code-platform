from submission import format_report


def test_returns_five_lines():
    """format_report returns exactly five lines."""
    result = format_report(1.0, 1000, 0.5, 200, 42)
    lines = result.splitlines()
    assert len(lines) == 5, (
        f"Expected exactly 5 lines, got {len(lines)}. "
        "Return '\\n'.join([line1, line2, line3, line4, line5])."
    )


def test_price_two_decimal_places():
    """Price line is formatted to 2 decimal places with a $ prefix."""
    result = format_report(3.14159, 1000, 0.5, 200, 0)
    lines = result.splitlines()
    assert "$3.14" in lines[0], (
        f"First line should contain '$3.14', got: {lines[0]!r}. "
        "Use f\"${price:.2f}\" — the $ is a literal prefix, :.2f formats to 2 decimal places."
    )


def test_population_comma_separated():
    """Population line uses comma-separated thousands."""
    result = format_report(1.0, 1234567, 0.5, 200, 0)
    lines = result.splitlines()
    assert "1,234,567" in lines[1], (
        f"Second line should contain '1,234,567', got: {lines[1]!r}. "
        "Use f\"{population:,}\" for comma-separated thousands."
    )


def test_ratio_percentage():
    """Ratio line uses percentage with 1 decimal place."""
    result = format_report(1.0, 1000, 0.847, 200, 0)
    lines = result.splitlines()
    assert "84.7%" in lines[2], (
        f"Third line should contain '84.7%', got: {lines[2]!r}. "
        "Use f\"{ratio:.1%}\" — Python multiplies by 100 and appends % automatically."
    )


def test_status_code_hex_with_prefix():
    """Status code line uses lowercase hex with 0x prefix."""
    result = format_report(1.0, 1000, 0.5, 255, 0)
    lines = result.splitlines()
    assert "0xff" in lines[3], (
        f"Fourth line should contain '0xff', got: {lines[3]!r}. "
        "Use f\"{status_code:#x}\" — the # flag adds the '0x' prefix."
    )


def test_flags_binary_padded():
    """Flags line uses binary padded to 8 digits with leading zeros."""
    result = format_report(1.0, 1000, 0.5, 200, 42)
    lines = result.splitlines()
    assert "00101010" in lines[4], (
        f"Fifth line should contain '00101010' (42 in binary, padded to 8 digits), got: {lines[4]!r}. "
        "Use f\"{flags:08b}\" — 0 means pad with zeros, 8 is the minimum width, b is binary."
    )


if __name__ == "__main__":
    report = format_report(
        price=3.14159,
        population=1234567,
        ratio=0.847,
        status_code=255,
        flags=42,
    )
    print(report)
