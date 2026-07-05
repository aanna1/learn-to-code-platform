def read_lines(filepath):
    """Read a file and return a list of non-empty stripped lines."""
    lines = []
    with open(filepath, "r") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
    return lines


def count_lines(filepath):
    """Return the number of non-empty lines in the file."""
    return len(read_lines(filepath))


if __name__ == "__main__":
    from pathlib import Path

    Path("sample.txt").write_text("apple\nbanana\n\ncherry\n")

    print(read_lines("sample.txt"))   # ['apple', 'banana', 'cherry']
    print(count_lines("sample.txt"))  # 3
