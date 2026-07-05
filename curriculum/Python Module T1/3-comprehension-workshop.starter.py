def square_evens(nums: list[int]) -> list[int]:
    # Return a list of squares of even numbers using a list comprehension
    # Hint: x % 2 == 0 checks if x is even
    pass


def word_lengths(words: list[str]) -> dict[str, int]:
    # Return a dict mapping each word to its length using a dict comprehension
    pass


def unique_squares(nums: list[int]) -> set[int]:
    # Return a set of squares using a set comprehension
    # Sets remove duplicates automatically
    pass


def first_n_squares(n: int):
    # Return a generator that yields the first n perfect squares (0², 1², 2², ...)
    # Use parentheses, not square brackets
    pass


if __name__ == "__main__":
    print(square_evens([1, 2, 3, 4, 5]))
    print(word_lengths(["cat", "elephant", "ox"]))
    print(unique_squares([-2, -1, 0, 1, 2]))
    print(list(first_n_squares(5)))
