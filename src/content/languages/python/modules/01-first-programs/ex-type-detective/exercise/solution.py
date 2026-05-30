def identify_type(value):
    """Return a string naming the type of value."""
    # bool must come before int — bool is a subtype of int in Python,
    # so type(True) == int would be True if we checked int first.
    if type(value) == bool:
        return "boolean"
    if type(value) == str:
        return "string"
    if type(value) == int:
        return "integer"
    if type(value) == float:
        return "float"


if __name__ == "__main__":
    print(identify_type("hello"))   # string
    print(identify_type(42))        # integer
    print(identify_type(3.14))      # float
    print(identify_type(True))      # boolean
    print(identify_type("99"))      # string
