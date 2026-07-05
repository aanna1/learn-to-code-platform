from concurrent.futures import ProcessPoolExecutor


def count_factors(n: int) -> int:
    return sum(1 for i in range(1, n + 1) if n % i == 0)


def factor_counts(numbers: list[int], max_workers: int) -> dict[int, int]:
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        counts = list(pool.map(count_factors, numbers))
    return dict(zip(numbers, counts))


if __name__ == "__main__":
    print(factor_counts([12, 13, 36, 100], max_workers=4))
