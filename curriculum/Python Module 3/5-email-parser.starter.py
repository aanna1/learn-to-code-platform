def parse_email(raw):
    # TODO: Strip whitespace and lowercase
    clean = raw

    # TODO: Return "invalid" if there is not exactly one "@"

    # TODO: Split on "@" to get username and domain

    # TODO: Return "invalid" if the domain has no "."

    # TODO: Extract the TLD (part after the last ".")

    # TODO: Return the formatted string
    pass


# You can test your function by pressing Run
print(parse_email("  Ada.Lovelace@Example.COM  "))
print(parse_email("user@subdomain.example.org"))
print(parse_email("notanemail"))
print(parse_email("two@@ats.com"))
