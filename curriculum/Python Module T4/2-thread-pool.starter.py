from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def slow_task(task_id: int) -> str:
    time.sleep(0.05)
    if task_id % 7 == 0 and task_id != 0:
        raise ValueError(f"task {task_id} is unlucky")
    return f"done-{task_id}"


def run_all(tasks: list[int], max_workers: int) -> list[str]:
    # TODO: use ThreadPoolExecutor and pool.map to run slow_task on every ID
    # Return the results as a list in the original order
    pass


def run_with_errors(tasks: list[int], max_workers: int) -> dict[int, str]:
    # TODO: use pool.submit to schedule each task
    # Build a dict mapping each future back to its task_id
    # Use as_completed to process futures as they finish
    # Catch any exception and store "error" for that task_id
    pass


if __name__ == "__main__":
    print(run_all(list(range(5)), max_workers=5))
    results = run_with_errors(list(range(10)), max_workers=5)
    print(results)
