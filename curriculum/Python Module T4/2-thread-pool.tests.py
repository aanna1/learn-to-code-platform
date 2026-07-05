from submission import run_all, run_with_errors


def test_run_all_returns_correct_results():
    """run_all returns done-N for each task ID in order."""
    result = run_all(list(range(5)), max_workers=5)
    assert result == ["done-0", "done-1", "done-2", "done-3", "done-4"], (
        f"Expected ['done-0', ..., 'done-4'] but got {result!r}. "
        "Use pool.map(slow_task, tasks) and convert to a list."
    )


def test_run_all_preserves_order():
    """run_all preserves submission order regardless of completion order."""
    result = run_all([3, 1, 4, 1, 5], max_workers=5)
    assert result == ["done-3", "done-1", "done-4", "done-1", "done-5"], (
        f"Expected order to match input order, got {result!r}. "
        "pool.map() returns results in the same order as its input."
    )


def test_run_all_single_task():
    """run_all works with a single task."""
    result = run_all([2], max_workers=1)
    assert result == ["done-2"], (
        f"Expected ['done-2'], got {result!r}."
    )


def test_run_with_errors_success_tasks():
    """run_with_errors stores results for tasks that succeed."""
    result = run_with_errors([0, 1, 2], max_workers=3)
    assert result[0] == "done-0", (
        f"result[0] should be 'done-0', got {result[0]!r}."
    )
    assert result[1] == "done-1", (
        f"result[1] should be 'done-1', got {result[1]!r}."
    )
    assert result[2] == "done-2", (
        f"result[2] should be 'done-2', got {result[2]!r}."
    )


def test_run_with_errors_failing_task():
    """run_with_errors stores 'error' for task IDs divisible by 7 (except 0)."""
    result = run_with_errors([7, 14, 1], max_workers=3)
    assert result[7] == "error", (
        f"result[7] should be 'error' (task 7 raises), got {result[7]!r}. "
        "Catch Exception inside the as_completed loop and store 'error'."
    )
    assert result[14] == "error", (
        f"result[14] should be 'error', got {result[14]!r}."
    )
    assert result[1] == "done-1", (
        f"result[1] should still be 'done-1' — one task failing shouldn't affect others, got {result[1]!r}."
    )


def test_run_with_errors_returns_all_keys():
    """run_with_errors returns an entry for every submitted task."""
    tasks = list(range(10))
    result = run_with_errors(tasks, max_workers=5)
    assert set(result.keys()) == set(tasks), (
        f"Expected keys {set(tasks)}, got {set(result.keys())}. "
        "Every task ID must appear in the result dict."
    )


def test_run_with_errors_all_success():
    """run_with_errors works when no task raises."""
    result = run_with_errors([1, 2, 3, 4, 5, 6], max_workers=6)
    for tid in [1, 2, 3, 4, 5, 6]:
        assert result[tid] == f"done-{tid}", (
            f"result[{tid}] should be 'done-{tid}', got {result[tid]!r}."
        )


if __name__ == "__main__":
    from submission import slow_task
    print(run_all(list(range(5)), max_workers=5))
    results = run_with_errors(list(range(10)), max_workers=5)
    print(results)
