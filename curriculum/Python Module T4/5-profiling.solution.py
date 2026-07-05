import cProfile
import io
import pstats
import timeit


def profile_workload(fn, *args) -> str:
    profiler = cProfile.Profile()
    profiler.enable()
    fn(*args)
    profiler.disable()
    buf = io.StringIO()
    pstats.Stats(profiler, stream=buf).sort_stats("cumulative").print_stats(10)
    return buf.getvalue()


def compare(snippet_a: str, snippet_b: str, number: int) -> tuple[float, float]:
    return (
        timeit.timeit(snippet_a, number=number),
        timeit.timeit(snippet_b, number=number),
    )


def slow_search(target: str, items: list[str]) -> bool:
    for item in items:
        if item == target:
            return True
    return False


def fast_search(target: str, items: list[str]) -> bool:
    return target in set(items)


if __name__ == "__main__":
    output = profile_workload(slow_search, "z", ["a"] * 10_000)
    print(output[:300])

    ta, tb = compare("sum(range(1000))", "500 * 999 // 2", number=10_000)
    print(f"loop: {ta:.4f}s  arithmetic: {tb:.4f}s")

    print(fast_search("b", ["a", "b", "c"]))
    print(fast_search("z", ["a", "b", "c"]))
