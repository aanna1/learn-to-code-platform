# Tier 2: Idiomatic Python

## Why this matters

Tier 1 polished what you already wrote. Tier 2 changes what you can write at all.

Consider this problem. You have a 40 GB log file. You want every line that contains "ERROR", with timestamps reformatted, written to a new file. With what you know from fundamentals, you'd write something like:

```python
with open("huge.log") as f:
    lines = f.readlines()
errors = [reformat(line) for line in lines if "ERROR" in line]
with open("errors.log", "w") as out:
    out.writelines(errors)
```

That code crashes. `readlines()` loads the whole file into memory. 40 GB doesn't fit. You need to stream the file: read one line, decide whether to keep it, write it out, throw it away, read the next one. You need a generator.

Consider a second problem. You have a function that calls a flaky API. Half the time it raises `ConnectionError`. You want it to retry three times with a one-second pause between attempts. The naive fix wraps every call site in `try/except` with a loop. The Python fix is one line: `@retry(times=3, delay=1)`. To write that decorator yourself, you need closures and higher-order functions.

Consider databases. You open a connection, run queries, close the connection. If a query raises in the middle, do you close the connection? With `try/finally` you can. With a context manager you do it without thinking. Once you understand context managers, you can write your own for any setup/teardown pair: timing blocks of code, suppressing exceptions, changing directories temporarily, acquiring locks.

These features (iterators, generators, decorators, context managers, closures) share a common thread. They let you put behavior in one place and reuse it everywhere. The fundamentals taught you to write code. Tier 2 teaches you to write code that other code uses.

## What you'll be able to do by the end

- Explain what a `for` loop actually does, in terms of `__iter__`, `__next__`, and `StopIteration`.
- Write a generator function that produces values lazily, and use generators to stream-process files too large to fit in memory.
- Write a context manager (both the `@contextmanager` form and the class-based form with `__enter__`/`__exit__`) for any setup/teardown pattern.
- Write a decorator from scratch, including one that takes arguments, and explain why `@functools.wraps` matters.
- Read code that uses closures and recognize captured variables.
- Reach for the right tool from `functools` (`lru_cache`, `partial`), `collections` (`Counter`, `defaultdict`, `deque`), and `itertools` (`chain`, `groupby`, `islice`) instead of reinventing them.
- Spot and fix the mutable default argument bug on sight.

## Prerequisites

You need Tier 1 solid. Type hints, comprehensions, `pathlib`, and `@dataclass` will appear in every example without explanation. You should also be comfortable with classes, including `__init__` and at least one dunder method.

If higher-order functions feel foreign (functions that take or return functions), spend ten minutes on this warmup before continuing:

```python
def apply_twice(f, x):
    return f(f(x))

print(apply_twice(lambda n: n + 1, 5))  # 7
```

If that prints 7 and you can explain why, you're ready.

## Core concepts

### The iterator protocol: what `for` actually does

You've written hundreds of `for` loops. Have you ever asked what one does?

Consider:

```python
for item in [10, 20, 30]:
    print(item)
```

How does Python know how to get the values out of that list? Lists, sets, dicts, tuples, strings, files, generators, range objects: they all work with `for`. Some are nothing like lists. A file object isn't even storing the data. What unifies them?

A protocol. Two methods, by convention.

An **iterable** is any object with an `__iter__` method that returns an **iterator**.
An **iterator** is any object with a `__next__` method that returns the next value or raises `StopIteration` when it runs out.

A `for` loop is sugar for this:

```python
items = [10, 20, 30]
it = iter(items)            # calls items.__iter__()
while True:
    try:
        item = next(it)     # calls it.__next__()
    except StopIteration:
        break
    print(item)
```

Run that. It prints 10, 20, 30. Every `for` loop in every Python program ever written is shorthand for this pattern. Lists, files, generators (which we'll meet next) all implement the protocol. That's why `for` works uniformly across them.

Try the protocol by hand:

```python
it = iter([10, 20, 30])
print(next(it))   # 10
print(next(it))   # 20
print(next(it))   # 30
print(next(it))   # raises StopIteration
```

Now write a class that participates. A countdown:

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self.n = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        value = self.n
        self.n -= 1
        return value


for x in Countdown(3):
    print(x)  # 3, 2, 1
```

That works, but the class has a flaw. Look:

```python
c = Countdown(3)
list(c)   # [3, 2, 1]
list(c)   # []
```

Once you've iterated, the internal counter is at zero. You can't iterate again. The fix is to separate iterable from iterator: `__iter__` should return a *fresh* iterator each time. Here's a cleaner version using `yield`, which we're about to explain:

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self.start = start

    def __iter__(self):
        n = self.start
        while n > 0:
            yield n
            n -= 1
```

That `yield` keyword turns `__iter__` into a generator. The same `Countdown(3)` instance iterates multiple times correctly, because each call to `__iter__` builds a new generator object.

**What could go wrong:** confusing iterable and iterator. A list is iterable but not an iterator. You can `for x in mylist` repeatedly. The thing `iter(mylist)` returns is the iterator, and it's one-shot. Calling `next()` on a list doesn't work; calling `iter()` first does. Strings, files, ranges: same pattern.

### Generators: writing iterators the easy way

Writing `__iter__` and `__next__` and managing state by hand is fiddly. Generators let Python do the bookkeeping.

A generator is a function that contains `yield`. Calling it doesn't run it. It returns a generator object. Each call to `next()` on that object runs the function until the next `yield`, then pauses. The function's local variables stay alive between pauses.

Smallest possible example:

```python
def numbers():
    yield 1
    yield 2
    yield 3

g = numbers()
print(next(g))  # 1
print(next(g))  # 2
print(next(g))  # 3
print(next(g))  # StopIteration
```

The function ran from the top to `yield 1`, paused, then resumed at `yield 2` on the next `next()`. When it falls off the end without yielding, `StopIteration` fires.

You can use a generator anywhere you'd use an iterator:

```python
for n in numbers():
    print(n)
```

The payoff is laziness. Here's the log-streaming example from the opening:

```python
from pathlib import Path
from typing import Iterator

def errors_only(path: Path) -> Iterator[str]:
    with path.open() as f:
        for line in f:
            if "ERROR" in line:
                yield line


def main() -> None:
    in_path = Path("huge.log")
    out_path = Path("errors.log")
    with out_path.open("w") as out:
        for line in errors_only(in_path):
            out.write(line)
```

That code handles a 40 GB log on a laptop with 8 GB of RAM. The generator yields one line at a time. The file object itself is a generator over lines, so you're streaming twice over: read a line, check it, yield it, write it, forget it, repeat. Memory use stays flat.

Two patterns worth memorizing.

**Filter and transform:**

```python
def parse_errors(path: Path) -> Iterator[dict]:
    """Yield each ERROR line parsed into a dict."""
    with path.open() as f:
        for line in f:
            if "ERROR" not in line:
                continue
            timestamp, _, message = line.partition(" ERROR ")
            yield {"timestamp": timestamp, "message": message.strip()}
```

**Infinite sequences:**

```python
def fibonacci() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


from itertools import islice
print(list(islice(fibonacci(), 10)))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

`islice` cuts off an infinite generator at the count you want. Without it, `list(fibonacci())` would never return.

**What could go wrong:** "I called my generator function and got a generator object back instead of values." Yes. That's the design. Calling `numbers()` returns the generator. You iterate it with `for`, or pull values with `next()`, or materialize it with `list()`. The function body doesn't run until you start asking for values.

**Try it yourself:** write a generator `running_sum(numbers)` that yields the running total of an iterable.

```python
for s in running_sum([1, 2, 3, 4]):
    print(s)
# 1, 3, 6, 10
```

<details>
<summary>Answer</summary>

```python
from typing import Iterable, Iterator

def running_sum(numbers: Iterable[int]) -> Iterator[int]:
    total = 0
    for n in numbers:
        total += n
        yield total
```

The function holds `total` in its frame across yields. Each yield emits the latest sum without rebuilding anything.
</details>

### Context managers: bracketing setup and teardown

Why does `with open(...)` exist? Try this without it:

```python
f = open("data.txt", "w")
f.write(generate_content())  # what if this raises?
f.close()
```

If `generate_content()` raises an exception, `f.close()` never runs. The file stays open until the garbage collector gets to it, which might be a while. On Windows it might lock the file. The fix is `try/finally`:

```python
f = open("data.txt", "w")
try:
    f.write(generate_content())
finally:
    f.close()
```

Every time you read or write a file, you'd write that boilerplate. Python's answer is the context manager protocol: any object with `__enter__` and `__exit__` methods. The `with` statement calls them at the right times:

```python
with open("data.txt", "w") as f:
    f.write(generate_content())
# f.close() happens here, automatically, even if write raises
```

You can write your own. Two ways.

**The easy way: `@contextmanager`.** Decorate a generator that yields exactly once.

```python
from contextlib import contextmanager
import time

@contextmanager
def timed(label: str):
    start = time.monotonic()
    try:
        yield
    finally:
        elapsed = time.monotonic() - start
        print(f"{label}: {elapsed:.3f}s")


with timed("loading data"):
    data = expensive_load()
```

The code before `yield` runs on entry. The code after runs on exit, inside the `finally` block, so it runs even if the `with` body raises. The `yield` itself is where the body of the `with` block executes.

A note on the clock. `time.time()` measures wall-clock time and can jump backward (NTP adjustments, daylight saving). For measuring durations, use `time.monotonic()`, which never goes backward.

**The class form: `__enter__` and `__exit__`.** Use this when you have setup, teardown, and state to track.

```python
import os
from pathlib import Path
from typing import Any

class working_directory:
    """Temporarily cd into a directory; restore on exit."""

    def __init__(self, target: Path) -> None:
        self.target = target
        self.previous: Path | None = None

    def __enter__(self) -> Path:
        self.previous = Path.cwd()
        os.chdir(self.target)
        return self.target

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.previous is not None:
            os.chdir(self.previous)


with working_directory(Path("/tmp")):
    # current dir is /tmp here
    ...
# back to wherever you were
```

`__exit__` receives three arguments describing the exception (or three `None` values on clean exit). Return `True` to suppress the exception; return `None` or `False` to let it propagate. Suppressing exceptions silently is almost always wrong, so leave it returning `None`.

**What could go wrong:** writing `@contextmanager` and using `yield` twice. Generators decorated this way must yield exactly once. Two yields mean "ambiguous: where does the with-body go?" The decorator raises `RuntimeError`. One yield, always.

### Closures: functions that remember

Before decorators, you need closures. Closures are why decorators are possible.

A closure is a function that uses variables from the scope where it was defined, even after that scope has exited.

```python
def make_multiplier(factor: int):
    def multiply(x: int) -> int:
        return x * factor
    return multiply


double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
```

`make_multiplier(2)` returned a function. That function uses `factor`. But `make_multiplier` has already returned. How does `factor` still exist?

Python kept it alive. The inner function holds a reference to the variables it captured. Every call to `make_multiplier` creates a fresh enclosing scope, so `double` and `triple` capture different `factor` values.

Closures are how decorators carry configuration. They're how callbacks remember their context. They're how `partial` works.

One gotcha to watch for. Closures capture *variables*, not values:

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])  # [2, 2, 2]   not [0, 1, 2]
```

Each `lambda` captured the variable `i`, not the value `i` had at the moment of definition. By the time you call any of them, `i` is 2 (the final value). The fix is to bind the current value as a default argument:

```python
funcs = []
for i in range(3):
    funcs.append(lambda i=i: i)

print([f() for f in funcs])  # [0, 1, 2]
```

The `i=i` makes each lambda capture the current value of `i` at definition time, as a default argument. Ugly, but standard.

### Decorators: functions that wrap functions

A decorator is a function that takes a function and returns a function. That's the whole idea. The `@` syntax is sugar:

```python
@my_decorator
def my_function():
    ...

# is exactly the same as:

def my_function():
    ...
my_function = my_decorator(my_function)
```

Start with a useless decorator that adds nothing:

```python
def noop(func):
    return func

@noop
def greet(name: str) -> str:
    return f"Hello, {name}"
```

`noop` takes `greet` and returns it unchanged. The `@noop` line wires it up. Pointless, but it compiles. Now do something useful: time the wrapped function.

First attempt:

```python
import time

def timed(func):
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        print(f"took {time.monotonic() - start:.3f}s")
        return result
    return wrapper


@timed
def slow_function() -> int:
    time.sleep(0.5)
    return 42


print(slow_function())
# took 0.501s
# 42
```

Read carefully. `timed` takes `func`. It defines a new function `wrapper` that takes any arguments, calls `func`, times the call, and returns the result. Then it returns `wrapper`. The `@timed` line replaces `slow_function` with `wrapper`. From the outside, you still call `slow_function(...)`. Under the hood, you're calling `wrapper(...)`, which times and forwards.

The `*args, **kwargs` is what lets one decorator wrap functions with any signature. `args` is a tuple of positional arguments, `kwargs` is a dict of keyword arguments. The wrapper accepts whatever you throw at it and passes it through.

Look at what's wrong with this decorator:

```python
print(slow_function.__name__)   # 'wrapper', not 'slow_function'
print(slow_function.__doc__)    # None, not the original docstring
```

The decoration replaced `slow_function` with `wrapper`, and `wrapper`'s metadata is now the function's metadata. This breaks tracebacks, breaks `help()`, breaks Sphinx documentation. The fix is one line:

```python
import functools
import time

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.monotonic() - start:.3f}s")
        return result
    return wrapper
```

`@functools.wraps(func)` copies `func`'s name, docstring, and other metadata onto `wrapper`. Always use it on decorators. It's free; the cost of not using it is debugging pain six months later.

Now the real one. A retry decorator with arguments.

```python
import functools
import logging
import time
from typing import Callable, TypeVar

log = logging.getLogger(__name__)
T = TypeVar("T")


def retry(times: int = 3, delay: float = 1.0):
    """Retry the decorated function on exception, up to `times` times."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == times:
                        log.exception("%s failed after %d attempts",
                                      func.__name__, times)
                        raise
                    log.warning("%s attempt %d failed; retrying in %.1fs",
                                func.__name__, attempt, delay)
                    time.sleep(delay)
            raise RuntimeError("unreachable")
        return wrapper
    return decorator


@retry(times=3, delay=0.5)
def flaky_api_call(url: str) -> dict:
    ...
```

Three levels of function. `retry(times=3, delay=0.5)` runs first and returns `decorator`. `decorator(flaky_api_call)` runs next and returns `wrapper`. `flaky_api_call = wrapper`. When you call `flaky_api_call(url)`, you're calling `wrapper(url)`, which retries on exception.

That's the pattern for every decorator-with-arguments you'll ever write. Outer function takes the configuration. Middle function takes the decorated function. Inner function takes the actual call's arguments.

In production, don't catch a bare `Exception` for retry. Be specific about what's retryable (`ConnectionError`, `TimeoutError`, specific HTTP status codes). Retrying on `ValueError` from a programming bug means you wait three seconds before crashing instead of crashing instantly. The `tenacity` library handles this and exponential backoff and jitter correctly. The version above is for understanding, not production.

**What could go wrong:** forgetting `@functools.wraps`. Forgetting that decorators with arguments need three nesting levels. Calling a decorator without parentheses when it expects arguments: `@retry` instead of `@retry()`. The first form passes the function itself as the first positional argument to `retry`, which then thinks the function is `times`. Confusing error.

### `functools` highlights

You've met `functools.wraps`. Three more pull their weight daily.

**`lru_cache`** memoizes a function. The first call with given arguments runs the function and caches the result. Subsequent calls with the same arguments return the cached result.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(100))   # instant; without the cache, this takes longer than your life
```

Without the cache, `fib(100)` makes about 1.6 × 10²⁰ recursive calls. With the cache, every distinct value of `n` is computed once. Massive speedup, one line of code.

Caveats: arguments must be hashable (no lists or dicts). The function should be pure (same inputs always produce same outputs, no side effects), since the cache will hide any state changes.

**`partial`** pre-fills arguments to a function:

```python
from functools import partial

def power(base: float, exponent: float) -> float:
    return base ** exponent

cube = partial(power, exponent=3)
print(cube(4))   # 64
```

Useful when you need to pass a function as a callback but the API calls it with fewer arguments than you have configuration for. Comes up constantly when wiring up GUI handlers, signal handlers, or thread pool tasks.

**`reduce`** folds a sequence into a single value:

```python
from functools import reduce
import operator

total = reduce(operator.mul, [1, 2, 3, 4, 5])   # 120
```

Comprehensions and `sum` cover most cases. `reduce` earns its keep when the combining operation isn't a simple sum: building a single dict from many, intersecting sets, applying transformations in sequence.

### `collections` highlights

Four standouts.

**`Counter`** tallies anything:

```python
from collections import Counter

most_common = Counter("mississippi").most_common(2)
print(most_common)   # [('i', 4), ('s', 4)]
```

Drop in for "I need to count occurrences." Cleaner than `defaultdict(int)` and a manual loop.

**`defaultdict`** gives missing keys a default value, generated on demand:

```python
from collections import defaultdict

words = ["apple", "ant", "bear", "blue", "cat"]
by_letter = defaultdict(list)
for word in words:
    by_letter[word[0]].append(word)

print(dict(by_letter))
# {'a': ['apple', 'ant'], 'b': ['bear', 'blue'], 'c': ['cat']}
```

Without `defaultdict` you'd write `if key not in d: d[key] = []` before every append. The default factory is a function called with no arguments to produce the default: `list`, `set`, `int` (gives 0), or any callable.

**`deque`** is a double-ended queue. `append` and `pop` from either end run in constant time:

```python
from collections import deque

queue = deque([1, 2, 3])
queue.append(4)        # right end
queue.appendleft(0)    # left end
print(queue.popleft()) # 0
```

Use `deque` whenever you want FIFO queue semantics. `list.pop(0)` works but runs in linear time. `deque.popleft()` is constant time. The difference matters at scale.

**`namedtuple`** is largely obsolete now that `@dataclass` exists. Use dataclasses for new code.

### `itertools` highlights

The whole module is worth reading once. The functions you'll reach for most:

```python
from itertools import chain, islice, groupby, count

# chain: flatten one level of nesting without building an intermediate list
combined = list(chain([1, 2], [3, 4], [5]))   # [1, 2, 3, 4, 5]

# islice: lazy slice, works on infinite iterators where [:n] doesn't
first_five = list(islice(count(10, 2), 5))    # [10, 12, 14, 16, 18]

# groupby: group consecutive items by a key. The "consecutive" part bites people.
data = ["apple", "ant", "bear", "blue", "cat"]
for letter, group in groupby(sorted(data), key=lambda w: w[0]):
    print(letter, list(group))
# a ['ant', 'apple']
# b ['bear', 'blue']
# c ['cat']
```

The trap in `groupby` is the word *consecutive*. It groups runs, not all occurrences. If you forget to sort first, you get fragmented groups. Sort by the same key you group by.

### `map`, `filter`, `lambda`

These predate comprehensions. In Python, comprehensions win on readability for most cases:

```python
# map version:
shouting = list(map(str.upper, words))

# comprehension version:
shouting = [w.upper() for w in words]
```

The map form is shorter when you already have a named function to apply. The comprehension wins when you'd otherwise need a lambda:

```python
# map with a lambda. Comprehension is cleaner:
list(map(lambda x: x * 2, numbers))   # don't
[x * 2 for x in numbers]              # do
```

Use `map` when you have a named function. Use a comprehension otherwise. `filter` follows the same rule.

`lambda` itself is a one-expression anonymous function:

```python
sorted(students, key=lambda s: s.grade)
```

Use lambdas for tiny inline functions, mostly as `key=` arguments to `sorted`, `min`, `max`, and the like. If a lambda needs a statement (an `if` chain, multiple lines), define a real function instead.

### Mutable default arguments: the famous gotcha

Predict what this prints:

```python
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))
print(add_item("b"))
```

Most learners predict `['a']` then `['b']`. The actual output:

```
['a']
['a', 'b']
```

Why? The default value `[]` is evaluated once, when the function is defined, not every time the function is called. There's one list. Every call without an explicit `items` shares it.

This is one of the top three Python gotchas. The fix is to use `None` as the sentinel:

```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

The same rule applies to dicts, sets, and any other mutable default. The dataclass decorator catches the equivalent mistake at class definition time; regular functions don't, and the bug can hide for years.

## Common pitfalls

1. **Iterating an iterator twice.** A list can be looped over repeatedly. A generator or `map` object cannot. Once exhausted, it's empty. If you need to iterate twice, materialize with `list(...)` first. Watch out for code that "loses" data the second time through.

2. **Mutable defaults.** Covered above. The fix is `None` as sentinel. If a linter doesn't catch this in your codebase, add `ruff` or `pylint`.

3. **Forgetting `@functools.wraps`.** Your decorator works, but error messages point at "wrapper" instead of the real function name. Add `@functools.wraps(func)` on every wrapper.

4. **Late binding in closures inside loops.** `[lambda: i for i in range(3)]` builds three lambdas that all return 2. Use `lambda i=i: i` to capture the current value.

5. **`groupby` without sorting.** It groups consecutive identical keys. If the data is unsorted, you get fragments. Always `sorted(data, key=...)` before `groupby(data, key=...)`.

6. **Returning instead of yielding in a generator.** A `return` in a generator stops iteration (and the return value goes into `StopIteration`, where almost nobody looks). If you wanted to emit a value, you wanted `yield`.

7. **Using `lru_cache` on methods.** The `self` argument is part of the cache key, so the cache holds references to every instance ever created, preventing garbage collection. For per-instance caching, use `functools.cached_property` or write the cache explicitly.

## Try it yourself

Write a decorator `@log_calls` that logs every call with its arguments and return value, using `logging` (not `print`).

```python
@log_calls
def add(a, b):
    return a + b

add(2, 3)
# Expected log output, in some form:
# add(2, 3) -> 5
```

<details>
<summary>One possible answer</summary>

```python
import functools
import logging

log = logging.getLogger(__name__)


def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_repr = ", ".join(
            [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        log.info("%s(%s)", func.__name__, arg_repr)
        try:
            result = func(*args, **kwargs)
        except Exception:
            log.exception("%s raised", func.__name__)
            raise
        log.info("%s(%s) -> %r", func.__name__, arg_repr, result)
        return result
    return wrapper
```

It uses `functools.wraps`. It logs on exception with the traceback. It uses `repr` so strings show their quotes (helpful for debugging string vs bytes). It logs both arguments and result on a successful call.
</details>

## How this connects

Tier 1 made your code cleaner. Tier 2 made it composable. The two together are what most idiomatic Python looks like.

Every module of the Phase 2 curriculum leans on these patterns. CLI tools use decorators (`click` is decorators all the way down). Subprocess and HTTP work uses generators to stream output. Retry logic uses decorators with closures. Logging configuration uses context managers for scoped logging. Test fixtures in `pytest` are generators that `yield` the resource and clean up after. Once you've internalized "code that wraps code," half of what's confusing about third-party libraries stops being confusing.

Looking sideways, Tier 4's `asyncio` uses generators for its underlying machinery (async functions started as generator-coroutines before async/await syntax existed). Tier 3's descriptors and metaclasses build on the same protocol-based thinking that makes iterators and context managers work. The pattern, repeated: Python defines a protocol (a small set of methods), and any object that implements it participates in the language's built-in syntax.

## Recap

- A `for` loop is sugar for `iter()` + repeated `next()` until `StopIteration`. Any object with `__iter__` is iterable; the thing it returns has `__next__` and is the iterator.
- Generators (functions with `yield`) are the easy way to write iterators. They produce values lazily, hold state across yields, and let you stream-process data too large to fit in memory.
- Context managers bracket setup/teardown. Write them with `@contextmanager` decorating a single-yield generator, or with a class that has `__enter__` and `__exit__`. Use `time.monotonic()` for measuring durations.
- Closures are functions that capture variables from their defining scope. They're what makes decorators and callbacks work. Watch out for late-binding bugs in loops.
- Decorators wrap a function with new behavior without modifying it. Always use `@functools.wraps`. Decorators with arguments need three levels of nesting.
- `lru_cache` memoizes pure functions. `partial` pre-fills arguments. `Counter`, `defaultdict`, and `deque` from `collections` replace common manual patterns. `chain`, `islice`, and `groupby` from `itertools` compose iterators.
- Use comprehensions over `map`/`filter` unless you already have a named function. Use `lambda` only for tiny inline callbacks.
- Mutable default arguments are evaluated once at definition. Use `None` as a sentinel and assign a fresh value inside the function.

## Up next

Tiers 3 and 4 cover advanced language features (abstract base classes, protocols, descriptors) and concurrency (threading, multiprocessing, asyncio). The Phase 2 curriculum then picks up with Module 1: building real CLI tools using `argparse`, `click`, `typer`, and `rich`. The decorator patterns you just learned are the foundation of `click`; you'll be writing decorators on the second day.
