import random

RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes, definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]


def ask(question):
    # Return a random response from RESPONSES using random.choice
    pass


def positive(question):
    # Return True if ask(question) returns one of the first 10 responses
    pass


if __name__ == "__main__":
    print(ask("Will it rain tomorrow?"))
    print(positive("Am I lucky?"))
