import re

# TODO: write a pattern with three capture groups: (YYYY), (MM), (DD).
# Match the ISO date format: four digits, hyphen, two digits, hyphen, two digits.
DATE_PATTERN = re.compile(r"")  # replace with your pattern

def reformat_dates(text):
    """Replace every YYYY-MM-DD date in text with MM/DD/YYYY."""
    # TODO: use re.sub with DATE_PATTERN to replace each date.
    # In the replacement string, \1 is the year, \2 is the month, \3 is the day
    # (based on the order of your groups). Rearrange them as month/day/year.
    pass


if __name__ == "__main__":
    samples = [
        "Invoice dated 2026-03-14, due 2026-04-01.",
        "Born on 1990-07-22.",
        "No dates here.",
    ]
    for s in samples:
        print(reformat_dates(s))
