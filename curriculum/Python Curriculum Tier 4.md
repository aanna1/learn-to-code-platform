# Tier 4: Concurrency and Performance

## Why this matters

You wrote a script that fetches the status of 100 servers from an internal API. Each request takes about one second. The script takes 100 seconds. Your boss asks why it's so slow.

You wrote a second script that processes 100 video files, applying a CPU-intensive transformation to each. Each one takes a minute. The script takes 100 minutes on a 16-core machine that should be doing 16 of them at once.

Both scripts are doing one thing at a time when they don't have to. The fix for the first is concurrency: 100 requests at once, all waiting for the network in parallel, finishing in roughly the time of one. The fix for the second is parallelism: 16 cores doing 16 transformations at once, finishing in roughly 1/16th of the time.

Concurrency and parallelism are different things. Python has separate tools for each because Python has a feature that makes the difference matter: the Global Interpreter Lock. Until you understand the GIL, you'll reach for threading when you needed multiprocessing, or asyncio when threading would have been simpler, or all three when none of them was the actual bottleneck.

Automation work is full of both shapes of problem. Health-check a fleet of services? Network-bound, throw threading at it. Render 10,000 PDFs from templates? CPU-bound, throw multiprocessing at it. Maintain 5,000 idle WebSocket connections from one process? Asyncio territory; threading would die under the memory cost.

Honest framing: most automation scripts don't need any of this. The script that runs once a day at 3am can take five minutes instead of ten and nobody cares. Reach for concurrency when latency or throughput is the actual constraint. Don't reach for it because it sounds fast.

## What you'll be able to do by the end

- Diagnose whether a slow program is I/O-bound or CPU-bound, and pick the right concurrency model.
- Explain what the GIL is, why it doesn't matter for I/O-bound work, and why it crushes thread-based CPU work.
- Use `ThreadPoolExecutor` to parallelize I/O-bound work with real timeouts and per-task error handling.
- Use `ProcessPoolExecutor` to parallelize CPU-bound work, and know which functions can and can't be sent to a worker.
- Read and write `async`/`await` code, run an event loop with `asyncio.run`, and use `asyncio.gather` for concurrent tasks.
- Profile a slow function with `cProfile` to find the actual hot spot before optimizing.

## Prerequisites

You should be solid on Tier 2: generators, context managers, decorators. The `with` statement is everywhere here, and `async`/`await` is generators with extra syntax under the hood. You should also be comfortable with the basics of HTTP requests using `requests` (the synchronous library you've used elsewhere) and command-line scripts that take a few arguments.

If "I/O-bound" and "CPU-bound" don't have concrete meanings for you yet, the GIL section below makes them concrete.

## Core concepts

### The GIL: what it is and why it's a fact about your code

CPython (the standard Python implementation) has a lock called the **Global Interpreter Lock**. Only one thread can execute Python bytecode at a time. If you start ten threads, they take turns running on a single CPU core. They do not run in parallel on ten cores.

The first question this raises: why have threading at all then?

Because the GIL is released during I/O. When a thread calls `requests.get(url)`, that call blocks waiting for the network. Before it blocks, it releases the GIL. Other threads can run during the wait. The same is true for disk reads, database queries, and `time.sleep()`. Anything that waits on the operating system releases the GIL while waiting.

For I/O-bound work (threads spending most of their time waiting), the GIL is invisible. Ten threads each waiting on a network response finish in roughly the time of one. The GIL is a non-issue.

For CPU-bound work (threads doing pure Python computation: parsing, math, encoding), the GIL is everything. Ten threads each computing a checksum take the same wall-clock time as one, because the threads take turns on one core. Threading buys nothing here. To use multiple cores for Python code, you need multiple *processes*.

The decision tree, once and for all:

- **I/O-bound work**: threading (`ThreadPoolExecutor`) or asyncio. Pick threading for simpler code or to parallelize calls to a library that doesn't support async. Pick asyncio when you need to handle thousands of concurrent connections cheaply.
- **CPU-bound work**: multiprocessing (`ProcessPoolExecutor`). Each worker is its own Python interpreter, so each gets its own GIL, so all of them can run Python bytecode simultaneously on different cores.

Python 3.13 introduced an experimental free-threaded build with no GIL. It's behind a build flag, libraries are catching up, and it's not yet the default. Plan around the GIL for any code you ship.

### Establishing the baseline: sequential is honest

Before any concurrency, write the slow version. You need a baseline.

```python
import logging
import time
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

URLS = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]


def fetch(url: str) -> int:
    """Fetch the URL and return its status code."""
    response = requests.get(url, timeout=10)
    return response.status_code


def main() -> None:
    start = time.monotonic()
    results = [fetch(url) for url in URLS]
    elapsed = time.monotonic() - start
    log.info("Fetched %d URLs in %.2fs: %s", len(results), elapsed, results)


if __name__ == "__main__":
    main()
```

`httpbin.org/delay/1` waits one second on the server before responding. Five URLs, one second each, takes about five seconds. Run it. Note the time. That's your baseline.

Now you have a target: five URLs in roughly one second instead of five.

The `timeout=10` on `requests.get` is not optional. A request without a timeout can hang forever if the server stops responding. In a sequential script that means the whole script hangs. In a threaded script it means a worker thread is stuck and the pool can starve. Always set a timeout. This is one of the most common bugs in production Python.

### Threading: when the work is waiting

The simplest path to concurrency in Python is `concurrent.futures.ThreadPoolExecutor`. It manages a pool of worker threads and gives you a clean API to submit work to them.

A first attempt at parallelizing the fetches:

```python
from concurrent.futures import ThreadPoolExecutor

def main() -> None:
    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(fetch, URLS))
    elapsed = time.monotonic() - start
    log.info("Fetched %d URLs in %.2fs: %s", len(results), elapsed, results)
```

Run that. Five URLs in roughly one second. The pool starts five worker threads. Each one calls `fetch(url)`. All five threads are simultaneously waiting on the network, which is the GIL-released part. They finish at about the same time.

`pool.map` is fine when you want all results in order and you're happy to fail the whole batch if any one task raises. Most real automation code wants something more nuanced: per-task error handling, the ability to handle results as they complete, and a clear story about timeouts. That's what `submit` and `as_completed` give you.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def fetch(url: str) -> int:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.status_code


def fetch_all(urls: list[str], max_workers: int = 10) -> dict[str, int | str]:
    results: dict[str, int | str] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_url = {pool.submit(fetch, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except requests.HTTPError as e:
                log.warning("HTTP error on %s: %s", url, e)
                results[url] = f"http_error:{e.response.status_code}"
            except requests.RequestException as e:
                log.warning("Request failed for %s: %s", url, e)
                results[url] = f"error:{type(e).__name__}"
    return results
```

Walk through it. `pool.submit(fetch, url)` schedules `fetch(url)` on a worker and returns a `Future` immediately, without waiting. We build a dict mapping each future to its URL so we can report which URL each result came from. `as_completed` yields futures as they finish, in completion order (not submission order). For each completed future, `future.result()` either returns the function's return value or raises the exception the function raised. Catching exceptions per task lets one URL fail without taking the others down.

`max_workers=10` is a tuning knob. Too few and you don't parallelize enough. Too many and you swamp the target server or your own CPU with context switching. Ten to thirty is a reasonable starting point for HTTP fetches. Profile with the real workload to find the sweet spot.

**What could go wrong:** sharing mutable state across threads. The example above is safe because each thread writes to a distinct key in `results`, and we only mutate `results` from the main thread (inside the `for` loop), not from the worker threads. If you have workers that mutate shared state, you need a `threading.Lock` to coordinate. The simpler fix is usually to have workers return their results and aggregate on the main thread. Avoid shared mutable state when you can.

**What could also go wrong:** threading CPU-bound work. If `fetch` were `compute_sha256_of_huge_string`, the threaded version above would run no faster than the sequential one, because nothing releases the GIL. The fix isn't more threads; it's the wrong tool. Use processes instead.

### Multiprocessing: when the work is computing

For CPU-bound work, you want multiple Python processes. `ProcessPoolExecutor` has the same API as `ThreadPoolExecutor`, which makes switching between them easy.

```python
from concurrent.futures import ProcessPoolExecutor
import hashlib
import os
import time

def compute_checksum(path: str) -> tuple[str, str]:
    """Compute SHA-256 of a file and return (path, hex_digest)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return path, h.hexdigest()


def hash_all(paths: list[str]) -> dict[str, str]:
    results: dict[str, str] = {}
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for path, digest in pool.map(compute_checksum, paths):
            results[path] = digest
    return results
```

`os.cpu_count()` returns the number of cores. One worker per core is a good default for CPU-bound work; more than that wastes time on context switching with no parallelism gain.

What's different from the threading version? Three things matter, all consequences of "each worker is a separate process":

1. **Communication is expensive.** Arguments and return values get serialized (pickled) and sent through a pipe between processes. For small inputs and outputs this is fast. For sending a 500 MB DataFrame to each worker, the pickling dominates. Send filenames, not file contents, when you can.

2. **Functions must be picklable.** The pickle protocol can serialize top-level functions (defined with `def` at module level), but it cannot serialize lambdas, nested functions, or methods bound to local objects. If your task function is `lambda x: x * 2` or defined inside another function, the pool can't ship it to a worker. Make it a regular top-level function.

3. **Workers don't share memory.** Each process has its own copy of every global. Setting a module-level variable in the main process does not affect workers. If you need workers to access shared data, pass it as an argument, or use `multiprocessing.shared_memory` for the rare large case.

There's a guard you have to remember on Windows and macOS:

```python
if __name__ == "__main__":
    paths = ["/tmp/file1", "/tmp/file2", "/tmp/file3"]
    hash_all(paths)
```

The `if __name__ == "__main__":` guard prevents an infinite loop. On Windows, the multiprocessing module starts workers by re-importing your script. Without the guard, each worker would itself spawn workers, recursively, until you ran out of RAM. The guard makes the bootstrapping code run only in the main process.

**What could go wrong:** sending a huge object as an argument. `pool.map(transform, [big_object] * 100)` sends 100 pickled copies of `big_object` across processes. If `big_object` is 100 MB, that's 10 GB of pickling. Pass references (filenames, indices into a shared file) and let workers load what they need.

### `asyncio`: a different model for "thousands of waits"

Threading works. Why does asyncio exist?

Each thread costs memory: roughly 8 MB of stack on Linux by default. Run 10,000 threads and you've used 80 GB of address space before any actual work. Threads also pay context-switching costs that the OS imposes on every switch. For a use case like "maintain 50,000 idle connections to a chat server," threading doesn't scale.

Asyncio runs one thread that switches between many tasks cooperatively. A task runs until it hits something that would block (a network read, a sleep, a database call), at which point it explicitly yields control back to the event loop. The event loop picks the next task that's ready to make progress. All of this happens in one OS thread.

The cost: the model is different from threading, and it spreads through your codebase. Every function that does I/O must be declared `async`. Every call to an async function must use `await`. Sync code can't directly call async code without bridging through the event loop. People call this "function coloring": async and sync are different colors and don't easily mix.

Smallest meaningful example:

```python
import asyncio
import logging
import time

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

URLS = ["https://httpbin.org/delay/1"] * 5


async def fetch(client: httpx.AsyncClient, url: str) -> int:
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    return response.status_code


async def main() -> None:
    start = time.monotonic()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(fetch(client, url) for url in URLS))
    elapsed = time.monotonic() - start
    log.info("Fetched %d URLs in %.2fs: %s", len(results), elapsed, results)


if __name__ == "__main__":
    asyncio.run(main())
```

Things to look at, top to bottom. `httpx` is the modern HTTP client with both sync and async APIs; here we use the async one. `AsyncClient` is an async context manager (note `async with`), so it's entered and exited with `await` under the hood. `fetch` is declared `async def`, which makes calling it produce a coroutine, not a result. `await client.get(...)` yields control to the event loop until the response arrives; meanwhile, other tasks run.

The key call is `asyncio.gather(*coroutines)`. It schedules all the coroutines to run concurrently and returns when all of them are done. The generator expression `(fetch(client, url) for url in URLS)` produces five coroutines, which `gather` runs concurrently.

`asyncio.run(main())` creates the event loop, runs the `main` coroutine until it completes, and closes the loop. That's the standard entry point for an async program.

Run the script. Five URLs in roughly one second, same as the threaded version. The difference would show at 5,000 URLs: the threaded version would struggle with the thread count; the async version keeps using one thread.

Three rules that prevent the most common asyncio mistakes:

1. **Awaiting a coroutine vs scheduling it.** `await fetch(client, url)` runs it now and waits for the result. `asyncio.create_task(fetch(client, url))` schedules it and returns a Task object you can `await` later. To run many things concurrently, you need them scheduled before you start awaiting. That's what `gather` does internally.

2. **Don't `time.sleep()` in async code.** That's a synchronous, blocking sleep. It freezes the event loop, blocking every other task. Use `await asyncio.sleep(seconds)`, which yields control while the sleep runs.

3. **Don't call sync libraries that do I/O.** If you call `requests.get(url)` (sync) inside an async function, the entire event loop blocks during the request. The async-ness is gone for the duration. Use `httpx.AsyncClient`, `aiohttp`, `aiofiles`, etc., or push the sync call out to a thread pool with `await asyncio.to_thread(...)`.

**What could go wrong:** forgetting `await`. Writing `client.get(url)` instead of `await client.get(url)` produces a coroutine object that's never run. Your code returns immediately, results are weird, and no error fires because creating a coroutine is legal. Static analyzers like `mypy` and `pyright` catch this. Run one of them in CI.

**Try it yourself:** rewrite this sync function to run three I/O-bound calls concurrently using asyncio.

```python
import requests

def fetch_all_sync(urls):
    return [requests.get(url, timeout=10).status_code for url in urls]
```

<details>
<summary>One possible answer</summary>

```python
import asyncio
import httpx

async def fetch_one(client: httpx.AsyncClient, url: str) -> int:
    r = await client.get(url, timeout=10.0)
    return r.status_code


async def fetch_all_async(urls: list[str]) -> list[int]:
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(fetch_one(client, url) for url in urls))


if __name__ == "__main__":
    urls = ["https://httpbin.org/delay/1"] * 3
    results = asyncio.run(fetch_all_async(urls))
    print(results)
```

`asyncio.gather` runs the three fetches concurrently. Total wall time is about one second, not three. The client lives in an `async with` so it cleans up regardless of errors.
</details>

### When to choose which

A practical decision guide:

- **Sequential** is fine for fewer than ten items unless latency matters. Don't add concurrency for the sake of it.
- **Threading (`ThreadPoolExecutor`)** for tens to hundreds of I/O-bound tasks. Simple code, works with any blocking library.
- **Multiprocessing (`ProcessPoolExecutor`)** for CPU-bound work, scaled to `os.cpu_count()` workers.
- **Asyncio** for thousands of concurrent connections or when you're already in an async framework (FastAPI, aiohttp servers). Requires async-compatible libraries throughout.

Mixing is allowed. You can run a `ThreadPoolExecutor` inside an async program using `asyncio.to_thread` to bridge a blocking library into async code. You can use `concurrent.futures` from sync code with either threads or processes interchangeably. Pick the simplest tool that solves the problem and only escalate when you measure a real bottleneck.

### Profiling: don't optimize without measuring

Your script is slow. Where is the time going?

Don't guess. Run a profiler. Python's standard library has two useful ones.

`cProfile` for "where does this whole program spend its time":

```python
import cProfile
import pstats

def my_script() -> None:
    # ... whatever the slow thing does ...
    ...


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    my_script()
    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(20)   # top 20 by cumulative time
```

Read the output. `ncalls` is how many times each function ran. `tottime` is time spent inside that function, excluding subcalls. `cumtime` is time including subcalls. Sort by `cumulative` to find the high-level functions that account for the most time; sort by `tottime` to find the leaf functions doing the actual work.

`timeit` for "how fast is this small piece of code":

```python
import timeit

elapsed = timeit.timeit("sum(range(1000))", number=10000)
print(f"sum(range(1000)) x 10000 took {elapsed:.3f}s")
```

`timeit` runs the snippet many times and reports total wall-clock time, with overhead controlled to give a fair measurement. Use it to compare two implementations of a small function. Don't use it on whole programs; that's `cProfile`'s job.

Once you have a profile, the rule is: optimize the hot spot. The function eating 60% of the time gets the attention. The function eating 0.2% does not, even if it looks ugly. Optimization without a profile is guesswork, and human intuition about Python performance is usually wrong (string concatenation, dictionary lookups, attribute access are all faster than people guess; `try/except` in tight loops, regex compilation in a loop, and repeated I/O are slower).

When pure Python isn't fast enough and you've actually proven it with a profile: `numpy` for numerical arrays (orders of magnitude faster than Python loops over lists), `Cython` or `mypyc` to compile Python-ish code to C, `PyPy` as a drop-in alternative interpreter for some workloads, or `PyO3` to write hot paths in Rust and call them from Python.

## Common pitfalls

1. **Using threads for CPU-bound work.** Doesn't speed anything up. Switch to `ProcessPoolExecutor`.

2. **Making network calls without a timeout.** `requests.get(url)` with no `timeout` can hang forever. Always pass `timeout=N`. Same for `httpx`, `socket.connect`, and any other network call.

3. **Forgetting the `if __name__ == "__main__":` guard with multiprocessing.** On Windows and macOS, workers re-import your script, and without the guard each worker spawns workers recursively. The script will exhaust your RAM before printing anything useful.

4. **Calling sync I/O from async code.** `requests.get()` inside an async function blocks the whole event loop. Use the async library (`httpx.AsyncClient`, `aiohttp`, `aiofiles`) or wrap the sync call with `await asyncio.to_thread(blocking_function, args)`.

5. **Forgetting `await`.** `coro = some_async_function()` creates a coroutine but doesn't run it. `result = await some_async_function()` runs it. A coroutine that's never awaited gives a runtime warning at program exit, easy to miss.

6. **Shared mutable state in threads without locks.** Two threads incrementing the same counter race against each other. Use `threading.Lock` if you must share state. Better, have workers return values and aggregate on the main thread.

7. **Optimizing without profiling.** Time spent rewriting cleverer code is almost always time wasted. Profile first; the bottleneck is usually somewhere you didn't expect.

## Try it yourself

Take a small sequential function and make it concurrent. Here's the starting point: a function that reads each `.txt` file in a directory and returns a dict mapping filename to line count. Make it parallel using `ProcessPoolExecutor`, with one worker per CPU core. Then think about whether threading or processes is the right choice and why.

```python
from pathlib import Path

def count_lines(path: Path) -> int:
    with path.open() as f:
        return sum(1 for _ in f)


def count_all(directory: Path) -> dict[Path, int]:
    return {p: count_lines(p) for p in directory.rglob("*.txt")}
```

<details>
<summary>One possible answer, with the reasoning</summary>

```python
from concurrent.futures import ProcessPoolExecutor
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


def count_lines(path: Path) -> tuple[Path, int]:
    """Return (path, line count). Returns the path too so callers can match results."""
    with path.open() as f:
        return path, sum(1 for _ in f)


def count_all(directory: Path) -> dict[Path, int]:
    paths = list(directory.rglob("*.txt"))
    results: dict[Path, int] = {}
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for path, count in pool.map(count_lines, paths):
            results[path] = count
    return results
```

Reasoning: counting lines is mostly I/O (reading bytes from disk) but also touches the CPU for each iteration (incrementing a counter, parsing newlines). For files that fit easily in the OS page cache, disk reads are fast and the work is closer to CPU-bound. Processes give you real parallelism. For files on slow remote storage, threading might do as well or better. The honest answer: try both, measure with `time` on your actual workload. The wrong move is to pick one based on a guess.
</details>

## How this connects

Tier 4 is where the patterns from Tiers 1 and 2 pay off in production. The `with` statement (Tier 2) is what manages pool lifecycles cleanly. The decorators (Tier 2) you'll use to time and retry. The logging (Tier 1) is what makes a concurrent program debuggable when a worker fails at 3am.

Looking forward to the Phase 2 curriculum: Module 5 (HTTP and APIs) leans on threading or asyncio for bulk requests with retries via `tenacity`. Module 6 (concurrency for I/O-bound work) is this lecture made concrete with real automation problems. Module 8 (cloud SDKs) uses threading heavily because `boto3` is a sync library, and the AWS API rewards parallel calls. Module 7 (testing) covers how to test concurrent code without flakiness, which is its own discipline. The decisions made here (process vs thread vs async) will recur in nearly every Phase 2 module.

For the path you're on, threading and `ProcessPoolExecutor` are the daily tools. Asyncio is the specialist's tool: powerful when the use case fits, overkill when it doesn't. Most automation scripts get by on threads.

## Recap

- The GIL serializes Python bytecode execution within one process. It releases during I/O, so threads help with I/O-bound work; it doesn't release during pure-Python computation, so threads don't help with CPU-bound work.
- I/O-bound work → `ThreadPoolExecutor` (simple) or asyncio (high scale). CPU-bound work → `ProcessPoolExecutor`.
- Always pass `timeout=` to network calls. Always use `if __name__ == "__main__":` with multiprocessing on Windows/macOS. Always handle per-task exceptions when using `as_completed`.
- `asyncio` runs many tasks cooperatively on one thread; tasks yield control at `await` points. Functions that do I/O are declared `async def`, calls to them use `await`, and the program runs under `asyncio.run(main())`. Don't call blocking sync libraries from async code without `asyncio.to_thread`.
- Profile before optimizing. `cProfile` for whole programs, `timeit` for snippets. Optimize the actual hot spot, not the function you guess is slow.
- Reach for `numpy`, `Cython`/`mypyc`, `PyPy`, or `Rust+PyO3` only after you've proven Python itself is the bottleneck. The fix is almost never your first guess.

## Up next

Tier 5 covers tooling and ecosystem: `pytest`, `uv`, `ruff`, `mypy`, `pre-commit`, packaging, publishing. The Phase 2 curriculum then begins with Module 1: building production CLI tools with `argparse`, `click`, `typer`, and `rich`. Most of what you learned in Tiers 1 through 4 starts paying for itself the moment you start writing tools other people will use.
