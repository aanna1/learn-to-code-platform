def unique_tags(tag_list):
    """Return a sorted list of unique tags from tag_list."""
    # TODO: convert to a set to drop duplicates, then return sorted(...)
    pass


def shared_tags(tags_a, tags_b):
    """Return a sorted list of tags that appear in both collections."""
    # TODO: intersection — set(tags_a) & set(tags_b)
    # Wrap the result in sorted() before returning.
    pass


def all_tags(tags_a, tags_b):
    """Return a sorted list of all tags from either collection."""
    # TODO: union — set(tags_a) | set(tags_b)
    pass


def only_in_first(tags_a, tags_b):
    """Return a sorted list of tags in tags_a but not in tags_b."""
    # TODO: difference — set(tags_a) - set(tags_b)
    pass


if __name__ == "__main__":
    print(unique_tags(["python", "web", "python", "data", "web"]))
    # ['data', 'python', 'web']
    print(shared_tags(["python", "web", "data"], ["web", "ml", "python"]))
    # ['python', 'web']
    print(all_tags(["python", "web"], ["web", "ml"]))
    # ['ml', 'python', 'web']
    print(only_in_first(["python", "web", "data"], ["web", "ml"]))
    # ['data', 'python']
