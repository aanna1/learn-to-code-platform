def parse_number(text):
    """Return int if text has no decimal point, float if it does."""
    # TODO: check whether text contains a "." and convert accordingly
    pass


if __name__ == "__main__":
    print(parse_number("42"))     # should print 42
    print(parse_number("3.14"))   # should print 3.14
