def manage_roster(roster, to_add, to_remove):
    """
    Add names in to_add, remove names in to_remove (only if present),
    and return the result sorted alphabetically.
    Does not modify the original roster.
    """
    # TODO: make a copy of roster so the original is untouched
    result = ...

    # TODO: append each name in to_add

    # TODO: remove each name in to_remove, but only if it's in result

    # TODO: return the sorted result
    pass


if __name__ == "__main__":
    original = ["Ada", "Grace", "Linus"]
    output = manage_roster(original, to_add=["Guido"], to_remove=["Linus"])
    print(output)          # ["Ada", "Grace", "Guido"]
    print(original)        # ["Ada", "Grace", "Linus"]  — unchanged
