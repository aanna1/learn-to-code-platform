import re

DATE_PATTERN = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

def reformat_dates(text):
    """Replace every YYYY-MM-DD date in text with MM/DD/YYYY."""
    return DATE_PATTERN.sub(r"\2/\3/\1", text)


if __name__ == "__main__":
    samples = [
        "Invoice dated 2026-03-14, due 2026-04-01.",
        "Born on 1990-07-22.",
        "No dates here.",
    ]
    for s in samples:
        print(reformat_dates(s))
