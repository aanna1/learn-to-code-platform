import re

PHONE_PATTERN = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")

def find_phones(text):
    """Return a list of all phone numbers found in text."""
    return PHONE_PATTERN.findall(text)


if __name__ == "__main__":
    sample = "Call us at 512-555-0102, (800)555-0199, 212.555.0123, or 9005550100."
    print(find_phones(sample))
    # Expected: ['512-555-0102', '(800)555-0199', '212.555.0123', '9005550100']
