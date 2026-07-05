def square_evens(nums: list[int]) -> list[int]:
    return [x ** 2 for x in nums if x % 2 == 0]


def word_lengths(words: list[str]) -> dict[str, int]:
    return {w: len(w) for w in words}


def unique_squares(nums: list[int]) -> set[int]:
    return {x ** 2 for x in nums}


def first_n_squares(n: int):
    return (x ** 2 for x in range(n))


if __name__ == "__main__":
    print(square_evens([1, 2, 3, 4, 5]))
    print(word_lengths(["cat", "elephant", "ox"]))
    print(unique_squares([-2, -1, 0, 1, 2]))
    print(list(first_n_squares(5)))
