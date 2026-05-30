def normalize(text):
    # Chain the methods: each returns a new string, so we call the next directly on it.
    # strip() removes leading/trailing whitespace.
    # replace("_", " ") turns underscores into spaces.
    # lower() lowercases the result.
    # split() with no argument splits on any whitespace AND collapses runs of spaces —
    #   "too   many   spaces" becomes ["too", "many", "spaces"].
    # " ".join(...) stitches the words back together with single spaces.
    return " ".join(text.strip().replace("_", " ").lower().split())


if __name__ == "__main__":
    print(normalize("  Ada_Lovelace  "))       # "ada lovelace"
    print(normalize("HELLO___WORLD"))           # "hello world"
    print(normalize("  too   many   spaces  ")) # "too many spaces"
    print(normalize("already clean"))           # "already clean"
