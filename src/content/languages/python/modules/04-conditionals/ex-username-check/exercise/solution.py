def check_username(name):
    if not name:
        return "Username cannot be empty."
    elif len(name) < 3:
        return "Username is too short."
    elif " " in name:
        return "Username cannot contain spaces."
    else:
        return "Username is valid."
