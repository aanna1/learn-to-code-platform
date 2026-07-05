from pathlib import Path


def append_log(message, filepath):
    """Append a [LOG] entry to the log file.
    Creates the file if it doesn't exist.
    Format: [LOG] message
    """
    with open(filepath, "a") as f:
        f.write(f"[LOG] {message}\n")


def read_log(filepath):
    """Return all log entries as a list of stripped strings.
    Return [] if the file does not exist.
    """
    if not Path(filepath).exists():
        return []
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == "__main__":
    append_log("server started", "app.log")
    append_log("user logged in", "app.log")
    append_log("request handled", "app.log")
    print(read_log("app.log"))
    # ['[LOG] server started', '[LOG] user logged in', '[LOG] request handled']
    print(read_log("missing.log"))
    # []
