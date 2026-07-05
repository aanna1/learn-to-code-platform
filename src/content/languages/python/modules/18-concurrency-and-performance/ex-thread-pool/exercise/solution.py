from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def slow_task(task_id: int) -> str:
    time.sleep(0.05)
    if task_id % 7 == 0 and task_id != 0:
        raise ValueError(f"task {task_id} is unlucky")
    return f"done-{task_id}"


def run_all(tasks: list[int], max_workers: int) -> list[str]:
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(slow_task, tasks))


def run_with_errors(tasks: list[int], max_workers: int) -> dict[int, str]:
    results: dict[int, str] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_id = {pool.submit(slow_task, tid): tid for tid in tasks}
        for future in as_completed(future_to_id):
            tid = future_to_id[future]
            try:
                results[tid] = future.result()
            except Exception:
                results[tid] = "error"
    return results


if __name__ == "__main__":
    print(run_all(list(range(5)), max_workers=5))
    results = run_with_errors(list(range(10)), max_workers=5)
    print(results)
