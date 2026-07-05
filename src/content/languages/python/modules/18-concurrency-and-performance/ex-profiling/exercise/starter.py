import cProfile
import io
import pstats
import timeit


def profile_workload(fn, *args) -> str:
    # TODO: run fn(*args) under cProfile.Profile
    # capture the stats as a string using pstats.Stats with a io.StringIO stream
    # sort by "cumulative", print top 10, return the string
    pass


def compare(snippet_a: str, snippet_b: str, number: int) -> tuple[float, float]:
    # TODO: time each snippet with timeit.timeit(snippet, number=number)
    # return (time_a, time_b)
    pass


def slow_search(target: str, items: list[str]) -> bool:
    for item in items:
        if item == target:
            return True
    return False


def fast_search(target: str, items: list[str]) -> bool:
    # TODO: convert items to a set and use the 'in' operator
    pass


if __name__ == "__main__":
    output = profile_workload(slow_search, "z", ["a"] * 10_000)
    print(output[:300])

    ta, tb = compare("sum(range(1000))", "500 * 999 // 2", number=10_000)
    print(f"loop: {ta:.4f}s  arithmetic: {tb:.4f}s")

    print(fast_search("b", ["a", "b", "c"]))
    print(fast_search("z", ["a", "b", "c"]))
