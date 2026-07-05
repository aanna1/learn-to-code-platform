import asyncio


async def slow_task(task_id: int) -> str:
    # TODO: await asyncio.sleep(0.05), then return f"done-{task_id}"
    pass


async def slow_task_maybe_fail(task_id: int) -> str:
    await asyncio.sleep(0.05)
    if task_id % 7 == 0 and task_id != 0:
        raise ValueError(f"task {task_id} is unlucky")
    return f"done-{task_id}"


async def run_all(task_ids: list[int]) -> list[str]:
    # TODO: use asyncio.gather to run slow_task on every ID concurrently
    # Return the results as a list (gather preserves order)
    pass


async def run_with_errors(task_ids: list[int]) -> dict[int, str]:
    # TODO: call asyncio.gather(*coroutines, return_exceptions=True)
    # where each coroutine is slow_task_maybe_fail(tid)
    # For each result: if it's an Exception instance, store "error";
    # otherwise store the string result.
    # Return a dict mapping task_id -> result_or_"error"
    pass


if __name__ == "__main__":
    print(asyncio.run(run_all(list(range(5)))))
    print(asyncio.run(run_with_errors(list(range(10)))))
