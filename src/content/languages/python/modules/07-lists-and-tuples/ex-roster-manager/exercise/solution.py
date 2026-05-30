def manage_roster(roster, to_add, to_remove):
    """
    Add names in to_add, remove names in to_remove (only if present),
    and return the result sorted alphabetically.
    Does not modify the original roster.
    """
    result = roster.copy()

    for name in to_add:
        result.append(name)

    for name in to_remove:
        if name in result:
            result.remove(name)

    return sorted(result)


if __name__ == "__main__":
    original = ["Ada", "Grace", "Linus"]
    output = manage_roster(original, to_add=["Guido"], to_remove=["Linus"])
    print(output)          # ["Ada", "Grace", "Guido"]
    print(original)        # ["Ada", "Grace", "Linus"]  — unchanged
