def parse_records(lines):
    records = []
    errors = []

    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue

        parts = line.split(":")
        if len(parts) != 2:
            errors.append(f"Line {i}: expected 'name:score' format")
            continue

        name, score_str = parts
        try:
            score = int(score_str)
        except ValueError:
            errors.append(f"Line {i}: score must be an integer")
        else:
            records.append({"name": name, "score": score})

    return {"records": records, "errors": errors}


def summary(result):
    n = len(result["records"])
    m = len(result["errors"])
    return f"Parsed {n} records, {m} errors."


if __name__ == "__main__":
    lines = ["Alice:88", "Bob:bad", "Charlie", "Dana:95", "", "Eve:72:extra"]
    result = parse_records(lines)
    for r in result["records"]:
        print(r)
    for e in result["errors"]:
        print(e)
    print(summary(result))
