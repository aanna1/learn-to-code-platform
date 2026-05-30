def parse_email(raw):
    # Clean first: strip whitespace, then lowercase
    clean = raw.strip().lower()

    # Validate: exactly one "@" required
    if clean.count("@") != 1:
        return "invalid"

    # Split into username and domain at the "@"
    # The second argument caps the split at 1, even if there were somehow more "@"s
    username, domain = clean.split("@", 1)

    # Validate: domain must contain at least one "." for there to be a TLD
    if "." not in domain:
        return "invalid"

    # TLD is everything after the last "." — split on "." and take the last element
    tld = domain.split(".")[-1]

    return f"username: {username} | domain: {domain} | tld: {tld}"


if __name__ == "__main__":
    print(parse_email("  Ada.Lovelace@Example.COM  "))  # username: ada.lovelace | domain: example.com | tld: com
    print(parse_email("user@subdomain.example.org"))    # username: user | domain: subdomain.example.org | tld: org
    print(parse_email("notanemail"))                    # invalid
    print(parse_email("two@@ats.com"))                  # invalid
