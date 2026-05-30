def parse_number(text):
    """Return int if text has no decimal point, float if it does."""
    if "." in text:
        return float(text)
    return int(text)


if __name__ == "__main__":
    print(parse_number("42"))     # 42
    print(parse_number("3.14"))   # 3.14
    print(parse_number("-7"))     # -7
    print(parse_number("0.0"))    # 0.0
