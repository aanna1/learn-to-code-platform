import timeit as _timeit
from submission import profile_workload, compare, slow_search, fast_search


def test_profile_workload_returns_string():
    """profile_workload returns a string."""
    result = profile_workload(slow_search, "z", ["a"] * 100)
    assert isinstance(result, str), (
        f"profile_workload should return a str, got {type(result).__name__}. "
        "Capture pstats output to io.StringIO and return buf.getvalue()."
    )


def test_profile_workload_contains_stats():
    """profile_workload output contains cProfile column headers."""
    result = profile_workload(slow_search, "z", ["a"] * 100)
    assert "ncalls" in result or "cumtime" in result or "tottime" in result, (
        f"profile_workload output should contain cProfile stats headers, got: {result[:200]!r}. "
        "Make sure you call pstats.Stats(...).sort_stats('cumulative').print_stats(10)."
    )


def test_profile_workload_ran_the_function():
    """profile_workload actually ran the function (slow_search appears in stats)."""
    result = profile_workload(slow_search, "z", ["a"] * 500)
    assert "slow_search" in result, (
        f"'slow_search' should appear in the profile output since it was profiled, "
        f"but it's not in: {result[:300]!r}."
    )


def test_compare_returns_tuple_of_floats():
    """compare returns a tuple of two floats."""
    result = compare("1+1", "2", number=100)
    assert isinstance(result, tuple) and len(result) == 2, (
        f"compare should return a tuple of length 2, got {result!r}."
    )
    assert all(isinstance(v, float) for v in result), (
        f"Both values should be floats, got {result!r}."
    )


def test_compare_times_are_positive():
    """compare returns positive times."""
    ta, tb = compare("sum(range(100))", "50 * 99 // 2", number=100)
    assert ta > 0 and tb > 0, (
        f"Both times should be positive, got ta={ta}, tb={tb}."
    )


def test_compare_order():
    """compare returns (time_a, time_b) matching snippet order."""
    # The loop-based sum should take longer than the arithmetic formula
    ta, tb = compare("sum(range(10_000))", "10_000 * 9_999 // 2", number=500)
    assert ta > tb, (
        f"sum(range(10_000)) should be slower than arithmetic, "
        f"but ta={ta:.4f} tb={tb:.4f}. Check you're returning (time_a, time_b) in order."
    )


def test_fast_search_found():
    """fast_search returns True when target is in items."""
    assert fast_search("b", ["a", "b", "c"]) is True, (
        "fast_search('b', ['a','b','c']) should return True. "
        "Convert items to a set and use 'target in set(items)'."
    )


def test_fast_search_not_found():
    """fast_search returns False when target is not in items."""
    assert fast_search("z", ["a", "b", "c"]) is False, (
        "fast_search('z', ['a','b','c']) should return False."
    )


def test_fast_search_empty():
    """fast_search returns False for an empty list."""
    assert fast_search("x", []) is False, (
        "fast_search('x', []) should return False — empty set has no members."
    )


def test_fast_search_single_match():
    """fast_search returns True when list has exactly one matching element."""
    assert fast_search("only", ["only"]) is True, (
        "fast_search('only', ['only']) should return True."
    )


def test_fast_search_agrees_with_slow():
    """fast_search and slow_search return the same result on the same inputs."""
    cases = [
        ("x", ["a", "b", "x", "d"]),
        ("z", ["a", "b", "c"]),
        ("a", ["a"]),
        ("q", []),
    ]
    for target, items in cases:
        slow = slow_search(target, items)
        fast = fast_search(target, items)
        assert slow == fast, (
            f"fast_search({target!r}, {items}) returned {fast} "
            f"but slow_search returned {slow}."
        )


if __name__ == "__main__":
    from submission import profile_workload, compare, fast_search, slow_search
    output = profile_workload(slow_search, "z", ["a"] * 500)
    print(output[:300])
    ta, tb = compare("sum(range(1000))", "500*999//2", number=5000)
    print(f"loop={ta:.4f}  arith={tb:.4f}")
    print(fast_search("b", ["a", "b", "c"]))
