def unique_tags(tag_list):
    """Return a sorted list of unique tags from tag_list."""
    return sorted(set(tag_list))


def shared_tags(tags_a, tags_b):
    """Return a sorted list of tags that appear in both collections."""
    return sorted(set(tags_a) & set(tags_b))


def all_tags(tags_a, tags_b):
    """Return a sorted list of all tags from either collection."""
    return sorted(set(tags_a) | set(tags_b))


def only_in_first(tags_a, tags_b):
    """Return a sorted list of tags in tags_a but not in tags_b."""
    return sorted(set(tags_a) - set(tags_b))


if __name__ == "__main__":
    print(unique_tags(["python", "web", "python", "data", "web"]))
    # ['data', 'python', 'web']
    print(shared_tags(["python", "web", "data"], ["web", "ml", "python"]))
    # ['python', 'web']
    print(all_tags(["python", "web"], ["web", "ml"]))
    # ['ml', 'python', 'web']
    print(only_in_first(["python", "web", "data"], ["web", "ml"]))
    # ['data', 'python']
