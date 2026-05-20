def greet_user(name):
    return f"Hi, {name}! Nice to meet you."


if __name__ == "__main__":
    name = input("What's your name? ")
    print(greet_user(name))
