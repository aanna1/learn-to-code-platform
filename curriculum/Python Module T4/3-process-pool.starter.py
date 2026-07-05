from concurrent.futures import ProcessPoolExecutor


def count_factors(n: int) -> int:
    # TODO: count how many integers in [1, n] divide n evenly
    # Hint: use sum(1 for i in range(1, n + 1) if n % i == 0)
    pass


def factor_counts(numbers: list[int], max_workers: int) -> dict[int, int]:
    # TODO: use ProcessPoolExecutor(max_workers=max_workers) with pool.map
    # to call count_factors on every number in the list.
    # Return a dict mapping each number to its factor count.
    pass


if __name__ == "__main__":
    print(factor_counts([12, 13, 36, 100], max_workers=4))
