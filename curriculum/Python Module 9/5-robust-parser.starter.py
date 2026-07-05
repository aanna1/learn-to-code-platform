def parse_records(lines):
    records = []
    errors = []

    for i, line in enumerate(lines, 1):
        # Skip blank lines
        if not line.strip():
            continue

        # Split on ":" and check the format
        parts = line.split(":")
        if len(parts) != 2:
            # Add to errors: "Line N: expected 'name:score' format"
            pass
            continue

        name, score_str = parts
        # Try to convert score_str to int; use else to append the record
        try:
            pass  # convert score_str
        except ValueError:
            pass  # add to errors: "Line N: score must be an integer"
        else:
            pass  # append {"name": name, "score": score} to records

    return {"records": records, "errors": errors}


def summary(result):
    # Return "Parsed N records, M errors."
    pass


if __name__ == "__main__":
    lines = ["Alice:88", "Bob:bad", "Charlie", "Dana:95", "", "Eve:72:extra"]
    result = parse_records(lines)
    for r in result["records"]:
        print(r)
    for e in result["errors"]:
        print(e)
    print(summary(result))
