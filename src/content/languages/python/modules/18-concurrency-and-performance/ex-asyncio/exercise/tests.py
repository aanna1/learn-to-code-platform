import asyncio
from submission import slow_task, run_all, run_with_errors


def test_slow_task_returns_correct_string():
    """slow_task(n) returns 'done-n'."""
    result = asyncio.run(slow_task(3))
    assert result == "done-3", (
        f"slow_task(3) should return 'done-3', got {result!r}. "
        "Return f'done-{task_id}' after awaiting asyncio.sleep(0.05)."
    )


def test_slow_task_is_coroutine():
    """slow_task is an async function (calling it returns a coroutine)."""
    import inspect
    assert inspect.iscoroutinefunction(slow_task), (
        "slow_task must be declared with 'async def', not plain 'def'."
    )
    coro = slow_task(0)
    coro.close()  # clean up unawaited coroutine


def test_run_all_returns_list():
    """run_all returns a list."""
    result = asyncio.run(run_all([0, 1, 2]))
    assert isinstance(result, list), (
        f"run_all should return a list, got {type(result).__name__}."
    )


def test_run_all_correct_results():
    """run_all returns done-N for each ID in order."""
    result = asyncio.run(run_all(list(range(5))))
    assert result == ["done-0", "done-1", "done-2", "done-3", "done-4"], (
        f"Expected ['done-0', ..., 'done-4'], got {result!r}. "
        "asyncio.gather preserves submission order."
    )


def test_run_all_single_task():
    """run_all works with a single task."""
    result = asyncio.run(run_all([4]))
    assert result == ["done-4"], f"Expected ['done-4'], got {result!r}."


def test_run_with_errors_success_tasks():
    """run_with_errors returns correct strings for tasks that succeed."""
    result = asyncio.run(run_with_errors([0, 1, 2, 3]))
    for tid in [0, 1, 2, 3]:
        assert result[tid] == f"done-{tid}", (
            f"result[{tid}] should be 'done-{tid}', got {result.get(tid)!r}."
        )


def test_run_with_errors_failing_task():
    """run_with_errors stores 'error' for tasks that raise."""
    result = asyncio.run(run_with_errors([7, 14, 1]))
    assert result[7] == "error", (
        f"result[7] should be 'error', got {result.get(7)!r}. "
        "Use return_exceptions=True and check isinstance(outcome, Exception)."
    )
    assert result[14] == "error", (
        f"result[14] should be 'error', got {result.get(14)!r}."
    )
    assert result[1] == "done-1", (
        f"result[1] should still be 'done-1', got {result.get(1)!r}."
    )


def test_run_with_errors_all_keys_present():
    """run_with_errors has an entry for every task ID."""
    task_ids = list(range(10))
    result = asyncio.run(run_with_errors(task_ids))
    assert set(result.keys()) == set(task_ids), (
        f"Expected keys {set(task_ids)}, got {set(result.keys())}."
    )


def test_run_with_errors_no_exception_propagates():
    """run_with_errors never raises even when tasks fail."""
    try:
        asyncio.run(run_with_errors([7, 14, 21]))
    except Exception as e:
        assert False, (
            f"run_with_errors should never raise, but got {type(e).__name__}: {e}. "
            "Pass return_exceptions=True to asyncio.gather."
        )


if __name__ == "__main__":
    print(asyncio.run(run_all(list(range(5)))))
    print(asyncio.run(run_with_errors(list(range(10)))))
