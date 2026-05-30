import random


def roll_die():
    return random.randint(1, 6)


def roll_n(n):
    total = 0
    for _ in range(n):
        total += roll_die()
    return total


def play_round(player_name, num_dice):
    total = roll_n(num_dice)
    print(f"{player_name} rolled {num_dice} dice and got {total}")
    return total


def main():
    alice_total = play_round("Alice", 3)
    bob_total = play_round("Bob", 3)

    if alice_total > bob_total:
        print("Alice wins!")
    elif bob_total > alice_total:
        print("Bob wins!")
    else:
        print("It's a tie!")


if __name__ == "__main__":
    main()
