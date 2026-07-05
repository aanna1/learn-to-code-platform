import re

# TODO: write a pattern that matches US phone numbers in various formats.
# The pattern should handle:
#   - Optional opening paren before the area code
#   - Three digits (area code)
#   - Optional closing paren after the area code
#   - An optional separator: hyphen, dot, or space
#   - Three more digits
#   - An optional separator
#   - Four more digits
# Use NO capture groups so findall returns a list of full matched strings.
PHONE_PATTERN = re.compile(r"")  # replace with your pattern

def find_phones(text):
    """Return a list of all phone numbers found in text."""
    # TODO: use PHONE_PATTERN.findall(text) to return every match
    pass


if __name__ == "__main__":
    sample = "Call us at 512-555-0102, (800)555-0199, 212.555.0123, or 9005550100."
    print(find_phones(sample))
    # Expected: ['512-555-0102', '(800)555-0199', '212.555.0123', '9005550100']
