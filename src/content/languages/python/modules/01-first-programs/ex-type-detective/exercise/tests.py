def test_identifies_string():
    "identify_type returns 'string' for str values"
    assert identify_type("hello") == "string", (
        f"identify_type(\"hello\") should return 'string', got {identify_type('hello')!r}"
    )
    assert identify_type("") == "string", (
        "identify_type(\"\") should return 'string' — an empty string is still a string."
    )
    assert identify_type("99") == "string", (
        "identify_type(\"99\") should return 'string' — the quotes make it text, not a number."
    )


def test_identifies_integer():
    "identify_type returns 'integer' for int values"
    assert identify_type(42) == "integer", (
        f"identify_type(42) should return 'integer', got {identify_type(42)!r}"
    )
    assert identify_type(0) == "integer", (
        f"identify_type(0) should return 'integer', got {identify_type(0)!r}"
    )
    assert identify_type(-7) == "integer", (
        f"identify_type(-7) should return 'integer', got {identify_type(-7)!r}"
    )


def test_identifies_float():
    "identify_type returns 'float' for float values"
    assert identify_type(3.14) == "float", (
        f"identify_type(3.14) should return 'float', got {identify_type(3.14)!r}"
    )
    assert identify_type(0.0) == "float", (
        f"identify_type(0.0) should return 'float', got {identify_type(0.0)!r}"
    )


def test_identifies_boolean():
    "identify_type returns 'boolean' for bool values"
    assert identify_type(True) == "boolean", (
        f"identify_type(True) should return 'boolean', got {identify_type(True)!r}. "
        "Remember: check bool BEFORE int, since True and False are also integers in Python."
    )
    assert identify_type(False) == "boolean", (
        f"identify_type(False) should return 'boolean', got {identify_type(False)!r}."
    )


def test_bool_not_confused_with_int():
    "True and False return 'boolean', not 'integer'"
    assert identify_type(True) == "boolean" and identify_type(False) == "boolean", (
        "True and False should return 'boolean', not 'integer'. "
        "In Python, bool is a subtype of int, so you must check for bool BEFORE int."
    )


def test_quoted_number_is_string():
    "'42' (a string) returns 'string', not 'integer'"
    assert identify_type("42") == "string", (
        "identify_type(\"42\") should return 'string' — the quotes make it a string, "
        "not a number. Only the bare integer 42 (no quotes) is an integer."
    )
