def read_lines(filepath):
    """Read a file and return a list of non-empty stripped lines."""
    # Open the file with a `with` statement
    # For each line: strip it, skip it if empty, otherwise add to list
    pass


def count_lines(filepath):
    """Return the number of non-empty lines in the file."""
    pass


if __name__ == "__main__":
    from pathlib import Path

    # Create a test file to try your functions
    Path("sample.txt").write_text("apple\nbanana\n\ncherry\n")

    print(read_lines("sample.txt"))   # ['apple', 'banana', 'cherry']
    print(count_lines("sample.txt"))  # 3
