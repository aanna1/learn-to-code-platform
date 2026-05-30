def identify_type(value):
    """
    Return a string naming the type of value.

    Returns one of: "string", "integer", "float", "boolean"

    Hint: use type(value) to get the type, then compare it to str, int, float, bool.
    Important: check for bool BEFORE int (bool is a subtype of int in Python).
    """
    # TODO: return "boolean" if value is a bool
    # TODO: return "string"  if value is a str
    # TODO: return "integer" if value is an int
    # TODO: return "float"   if value is a float


if __name__ == "__main__":
    # Quick manual checks — these run when you press Run but are skipped by the grader.
    print(identify_type("hello"))   # should print: string
    print(identify_type(42))        # should print: integer
    print(identify_type(3.14))      # should print: float
    print(identify_type(True))      # should print: boolean
    print(identify_type("99"))      # should print: string (not integer!)
