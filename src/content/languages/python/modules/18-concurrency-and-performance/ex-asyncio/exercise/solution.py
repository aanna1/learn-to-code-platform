import asyncio


async def slow_task(task_id: int) -> str:
    await asyncio.sleep(0.05)
    return f"done-{task_id}"


async def slow_task_maybe_fail(task_id: int) -> str:
    await asyncio.sleep(0.05)
    if task_id % 7 == 0 and task_id != 0:
        raise ValueError(f"task {task_id} is unlucky")
    return f"done-{task_id}"


async def run_all(task_ids: list[int]) -> list[str]:
    return list(await asyncio.gather(*(slow_task(tid) for tid in task_ids)))


async def run_with_errors(task_ids: list[int]) -> dict[int, str]:
    coros = [slow_task_maybe_fail(tid) for tid in task_ids]
    outcomes = await asyncio.gather(*coros, return_exceptions=True)
    return {
        tid: ("error" if isinstance(outcome, Exception) else outcome)
        for tid, outcome in zip(task_ids, outcomes)
    }


if __name__ == "__main__":
    print(asyncio.run(run_all(list(range(5)))))
    print(asyncio.run(run_with_errors(list(range(10)))))
