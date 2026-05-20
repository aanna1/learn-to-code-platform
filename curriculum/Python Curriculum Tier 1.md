# Tier 1: Make Your Existing Code Better

## Why this matters

You finished the fundamentals. Your code runs and you can read most Python you encounter. You've probably built a small CLI or two by stitching pieces together.

Now open a real Python project. Browse the source of `requests` on GitHub. Look at a teammate's automation script that has been in production for two years. Then look at one of your own scripts from fundamentals. The gap you notice has little to do with algorithms. The pro code uses `pathlib` where yours uses string concatenation on file paths. It logs to a real logger where yours sprinkles `print()`. A dataclass in three lines replaces the thirty lines of `__init__` and `__repr__` you wrote. Number formatting that took you a helper function fits inside one f-string.

None of this requires a new mental model. It is the same Python with the rough edges sanded off. Each piece takes an afternoon to learn. Together, they separate "I know Python" from "I write Python that other people want to maintain."

For automation work the polish is load-bearing, because your code has to survive. It runs unattended at 3am. It gets handed to whoever is on-call after you leave the team. Your `print()` calls vanish into `/dev/null` when `systemd` runs your script. A logger configured to write to syslog does not. Your hardcoded `/tmp/data.txt` breaks on Windows. `Path.home() / "data.txt"` does not.

## What you'll be able to do by the end

- Write list, set, dict, and generator comprehensions, and recognize when a regular `for` loop is clearer.
- Add type hints to functions and dataclasses, then catch bugs by running `mypy` over the file.
- Replace dictionary-as-pseudo-object code with `@dataclass`-decorated classes.
- Use `pathlib` for filesystem work: build paths with `/`, read and write text, walk trees with `rglob`.
- Format numbers, percentages, hex, and binary inside f-strings without a single helper function.
- Replace string constants with `Enum` members so typos turn into errors instead of silent bugs.
- Reach for `match`/`case` when branching on the *shape* of data, and for `if`/`elif` otherwise.
- Decide when the walrus operator clarifies code and when it just confuses readers.
- Configure `logging` for any script you'd run unattended, with levels, timestamps, and full exception tracebacks.

## Prerequisites

You should be comfortable with everything in the fundamentals: variables, types, control flow, functions, basic classes, dictionaries, lists, file I/O with `open()`, and basic exception handling. If `for line in open(filename):` looks normal to you, you're ready. If you've never written a class with `__init__`, review Module 11 of fundamentals before continuing. The dataclass section assumes that knowledge.

## Core concepts

### What's wrong with this code?

```python
import os

def find_python_files(directory):
    result = []
    for filename in os.listdir(directory):
        full_path = directory + "/" + filename
        if os.path.isfile(full_path) and filename.endswith(".py"):
            result.append(full_path)
    return result

files = find_python_files("./src")
print("Found " + str(len(files)) + " Python files")
for f in files:
    print(f)
```

Nothing's wrong, exactly. It runs. Given a `src/` directory with some `.py` files, it does what the name promises.

But every line here is the kind of thing experienced Python programmers stopped writing years ago. Over the next nine sections we'll rewrite this function piece by piece, and at the end you'll see the same behavior in twelve cleaner lines with type hints, cross-platform paths, a logger, and output that other people can read. None of those changes adds capability. They make the code something you wouldn't mind a coworker reviewing.

Start with the path handling.

### `pathlib`: stop concatenating strings

Look at `directory + "/" + filename`. What goes wrong?

On Linux and macOS, that "/" works fine. On Windows, paths use backslashes (`\`), so `"./src" + "/" + "main.py"` produces a string some Windows tools misinterpret. The old fix was `os.path.join`:

```python
import os
full_path = os.path.join(directory, filename)
```

It works. But `os.path` is a flat module of functions, and you end up writing `os.path.dirname(os.path.basename(os.path.splitext(filename)[0]))` for anything composite. Every operation takes a string and returns a string.

`pathlib` replaces the whole approach with `Path` objects:

```python
from pathlib import Path

directory = Path("./src")
full_path = directory / "main.py"
```

The `/` operator is overloaded on `Path` to mean "append this segment." That removes most of the friction. The real win is the methods that come for free:

```python
from pathlib import Path

p = Path("/var/log/myapp/2024-01-15.log")

print(p.name)        # 2024-01-15.log
print(p.stem)        # 2024-01-15
print(p.suffix)      # .log
print(p.parent)      # /var/log/myapp
print(p.parents[1])  # /var/log
print(p.exists())    # True or False
print(p.is_file())   # True or False
```

You stop reaching for `os.path.basename(p)` followed by `os.path.splitext(...)`. The path knows what it is.

Reading and writing collapses to one line each:

```python
config_path = Path.home() / ".myapp" / "config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)

config_path.write_text('{"theme": "dark"}')
content = config_path.read_text()
```

`Path.home()` gives you the user's home directory across platforms. `mkdir(parents=True, exist_ok=True)` is the equivalent of `mkdir -p`: create the directory along with any missing parents, don't raise if it already exists.

For walking a tree:

```python
for py_file in Path("src").rglob("*.py"):
    print(py_file, py_file.stat().st_size)
```

`rglob` is recursive glob. It walks the entire tree under `src/` and yields every file matching `*.py`. Non-recursive is `glob`. Use `iterdir()` if you want one level only.

Now rewrite the opening example's first half:

```python
from pathlib import Path

def find_python_files(directory: Path) -> list[Path]:
    return [p for p in Path(directory).rglob("*.py") if p.is_file()]
```

Two changes landed at once: `pathlib` replaced the string surgery, and a comprehension replaced the explicit loop. The comprehension deserves its own section.

**What could go wrong:** `Path("/foo") / "/bar"` does not produce `/foo/bar`. The second segment starts with `/`, which `pathlib` treats as absolute, so the result is `Path("/bar")`. Watch for this when joining variables that might already start with a slash. Strip leading slashes first if you need to be defensive: `directory / segment.lstrip("/")`.

### Comprehensions: four flavors

You met list comprehensions in fundamentals. Refresher:

```python
squares = [x ** 2 for x in range(10)]
```

The basic shape is `[expression for variable in iterable]`. Add a filter with `if`:

```python
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
```

What you may not have learned is that the same syntax produces sets, dicts, and generators, depending on the brackets:

```python
# List — square brackets
squares_list = [x ** 2 for x in range(5)]                  # [0, 1, 4, 9, 16]

# Set — curly braces
squares_set = {x ** 2 for x in [-2, -1, 1, 2]}              # {1, 4}

# Dict — curly braces with key: value
word_lengths = {w: len(w) for w in ["a", "bb", "ccc"]}      # {'a': 1, 'bb': 2, 'ccc': 3}

# Generator — parentheses
squares_gen = (x ** 2 for x in range(10 ** 9))              # lazy
```

The generator expression is the one worth pausing on. A list comprehension builds the whole list in memory before you can use it. A generator builds nothing. It stores instructions, and each value is computed when you ask for it.

What does that buy you? Watch:

```python
# This would allocate gigabytes and freeze your machine:
# squares = [x ** 2 for x in range(10 ** 9)]

# This uses constant memory:
squares = (x ** 2 for x in range(10 ** 9))

for sq in squares:
    if sq > 1000:
        break
    print(sq)
```

The generator is a great fit for streaming through large data. Reading every line of a 50 GB log file and counting errors? Generator. Building a 200-element list of formatted strings for display? List comprehension. Pick the shape that matches the size of the data.

**A rule for when to stop:** comprehensions express transformations. The moment you find yourself nesting two filters, adding an `if`/`else`, or wrapping onto a third line, write a regular `for` loop. Comprehensions are at their best when they fit on one line and the intent is obvious at a glance. The five-line `for` loop often reads faster than the dense one-liner that replaced it.

**Try it yourself:** given a list `words = ["alpha", "beta", "gamma", "delta", "epsilon"]`, build a dict mapping each word to its length, but only for words longer than 4 characters. Try it before reading on.

<details>
<summary>Answer</summary>

```python
words = ["alpha", "beta", "gamma", "delta", "epsilon"]
result = {w: len(w) for w in words if len(w) > 4}
# {'alpha': 5, 'gamma': 5, 'delta': 5, 'epsilon': 7}
```
</details>

### F-strings beyond `{value}`

You've written f-strings like `f"Hello, {name}!"`. That's interpolation. F-strings also have a small formatting language living after a colon, and it eliminates a whole category of helper functions you'd otherwise write.

```python
price = 3.14159
print(f"Price: {price}")          # Price: 3.14159
```

You probably want two decimal places. Without f-strings you'd reach for `round()` and `str()`. With them:

```python
print(f"Price: {price:.2f}")      # Price: 3.14
```

`:.2f` is a format spec. The `f` means "fixed-point" and `.2` means "two digits after the decimal." You can pad and align:

```python
print(f"|{price:>10.2f}|")        # |      3.14|     right-aligned in 10 chars
print(f"|{price:<10.2f}|")        # |3.14      |     left-aligned
print(f"|{price:^10.2f}|")        # |   3.14   |     centered
```

Comma separators for large numbers:

```python
print(f"{1234567:,}")             # 1,234,567
print(f"{1234567.89:,.2f}")       # 1,234,567.89
```

Percentages (Python multiplies by 100 for you):

```python
ratio = 0.847
print(f"{ratio:.1%}")             # 84.7%
```

Hex and binary, with optional padding:

```python
print(f"{255:x}")                 # ff
print(f"{255:#x}")                # 0xff
print(f"{255:08b}")               # 11111111   (binary, padded to 8 digits)
```

And the form that earns its keep in debugging:

```python
x = 42
y = [1, 2, 3]
print(f"{x=}")                    # x=42
print(f"{y=}")                    # y=[1, 2, 3]
```

The trailing `=` prints both the expression and its value. That replaces every `print("x is", x)` line you've ever written. Added in Python 3.8 for exactly this case.

**What could go wrong:** `f"Total: {total:.2f}"` raises `ValueError: Unknown format code 'f' for object of type 'str'` if `total` is a string. Format specs apply to the type of the value. `.2f` requires a number. Cast or fix the source.

### Type hints: documentation that gets checked

Python is dynamically typed. Pass a string to a function expecting an integer, and you find out at runtime when something explodes. Type hints are annotations that document the expected types and let a tool verify them:

```python
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times
```

Read that as: `greet` takes a `name` that is a string, a `times` that is an integer with default 1, and returns a string. The annotations are not enforced at runtime. Python will let you call `greet(42, "three")` and produce gibberish. The point is that `mypy` won't.

Install `mypy` and run it on your file:

```
pip install mypy
mypy myfile.py
```

`mypy` reads the annotations, traces the code, and reports any call that disagrees with the declared types. It is the single highest-leverage thing you can add to a Python codebase. It catches bugs that integration tests would otherwise have to.

The basics you'll use daily:

```python
from typing import Optional

# A name that might be None:
def find_user(user_id: int) -> Optional[dict]:
    ...

# Python 3.10+ shorthand for the same thing:
def find_user(user_id: int) -> dict | None:
    ...

# Lists, dicts, etc.
def parse_lines(lines: list[str]) -> dict[str, int]:
    ...

# A function passed as a value:
from typing import Callable
def retry(operation: Callable[[], str], times: int = 3) -> str:
    ...
```

The `dict | None` syntax (PEP 604) is the modern style on Python 3.10+. Before 3.10 you wrote `Optional[dict]` from the `typing` module. If you're starting a new codebase today, target 3.10+ and skip the old syntax.

When do you add types? On function signatures and dataclass fields, every time. On local variables, only when the type is non-obvious. `count: int = 0` is noise. `connections: dict[str, list[Connection]] = {}` earns its keep.

**What could go wrong:** annotations look like assignments but they aren't. `name: str` declares the type of `name`; it does not give it a value. Writing `name: str` at the top of a function body and never assigning to `name` produces a `NameError` later if you try to read it. The annotation is not enough. You still need `name: str = "default"` or an assignment somewhere.

**Try it yourself:** add type hints to this function and decide whether `count` should accept `None`.

```python
def repeat_word(word, count):
    if count is None:
        return ""
    return word * count
```

<details>
<summary>Answer</summary>

```python
def repeat_word(word: str, count: int | None) -> str:
    if count is None:
        return ""
    return word * count
```

Because the function handles `None`, the right annotation is `int | None`. If `count` were never `None`, drop that part.
</details>

### Dataclasses: classes for data

Here's a pattern from fundamentals. You want to group related fields into an object, so you write:

```python
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return (self.name, self.email, self.age) == (other.name, other.email, other.age)
```

You wrote three methods. All three are mechanical. `@dataclass` writes them for you:

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int
```

That's the entire class. The decorator generates `__init__`, `__repr__`, and `__eq__` from the type-annotated attributes. You construct, print, and compare instances:

```python
u = User("Alice", "alice@example.com", 30)
print(u)
# User(name='Alice', email='alice@example.com', age=30)

u2 = User("Alice", "alice@example.com", 30)
print(u == u2)  # True
```

A few features you'll reach for:

```python
from dataclasses import dataclass, field

@dataclass
class ServerConfig:
    host: str
    port: int = 8080                                  # default value
    tags: list[str] = field(default_factory=list)     # mutable default needs a factory

@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float
```

Two things to notice. First, writing `tags: list[str] = []` would be a bug, because default values are shared across instances, so every `ServerConfig` would share the same list. `field(default_factory=list)` builds a fresh list per instance. The dataclass decorator catches the naive form and raises an error if you try it.

Second, `frozen=True` makes instances immutable. Assigning `coord.latitude = 5` raises `FrozenInstanceError`. Use this for values that should never change after construction (configuration, coordinates, anything you'll use as a dict key, since frozen dataclasses are hashable).

When *not* to reach for a dataclass: if your class has real behavior beyond storing data (methods that mutate state, complex business logic), a regular class is clearer. Dataclasses are for data.

**What could go wrong:** field order matters. Fields with defaults have to come after fields without defaults. Writing `@dataclass class C: x: int = 0; y: int` raises `TypeError: non-default argument 'y' follows default argument`. Reorder so `y` comes before `x`, or give `y` a default.

### `Enum`: stop using string constants

Look at this code:

```python
def update_order(order, status):
    if status == "pending":
        ...
    elif status == "approved":
        ...
    elif status == "rejcted":  # typo
        ...
```

That typo in `"rejcted"` won't show up until the rejection branch actually runs. Could be in production. Could be never, because that branch only triggers on the third Tuesday of the month. String constants are a quiet source of bugs.

`Enum` fixes it:

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def update_order(order, status: Status):
    if status is Status.PENDING:
        ...
    elif status is Status.APPROVED:
        ...
    elif status is Status.REJCTED:  # typo
        ...
```

Now the typo is an `AttributeError` the moment Python loads the file. There is no `Status.REJCTED`. The bug surfaces immediately, not on the third Tuesday.

Use `is` to compare enum members rather than `==`. Both work for `Enum`, but `is` is the idiomatic choice, since you're asking "is this the same singleton object?", which is the truer question.

A useful variant for integer-valued flags:

```python
from enum import IntEnum

class HttpStatus(IntEnum):
    OK = 200
    NOT_FOUND = 404
    SERVER_ERROR = 500

if response.status_code == HttpStatus.OK:  # IntEnum members behave as integers
    ...
```

`IntEnum` members are real integers. Use this when you need to interoperate with code that produces or consumes plain integers (HTTP status codes, file modes, signal numbers).

### Pattern matching with `match`/`case`

Python 3.10 added `match`/`case`. The shallow read is "Python finally got a `switch` statement." That sells it short. `match` deconstructs values.

Start with the boring case to build intuition:

```python
def describe(value):
    match value:
        case 0:
            return "zero"
        case 1:
            return "one"
        case _:
            return "other"
```

The `_` is the wildcard. Equivalent to an `if`/`elif`/`else`. Not yet interesting.

Here is where it gets interesting. `match` can deconstruct collections and check types:

```python
def classify(value):
    match value:
        case int(n) if n < 0:
            return f"negative integer: {n}"
        case int(n):
            return f"non-negative integer: {n}"
        case [x, y]:
            return f"pair: {x}, {y}"
        case [x, *rest]:
            return f"list starting with {x}, then {rest}"
        case {"type": "user", "name": name}:
            return f"user named {name}"
        case _:
            return "something else"
```

Read those one at a time:

- `case int(n) if n < 0` matches if `value` is an `int`, binds it to `n`, and requires the guard `n < 0` to hold.
- `case [x, y]` matches a list or tuple with exactly two elements, binding them to `x` and `y`.
- `case [x, *rest]` matches a list with at least one element. `x` is the first, `rest` is everything else.
- `case {"type": "user", "name": name}` matches a dict containing those keys, binding the value of `"name"` to `name`. The dict can have other keys; the pattern only requires these.

This is what makes `match` worth the syntactic cost. For dispatch on the *shape* of structured data (JSON-like payloads, AST nodes, message types), `match` is cleaner than chains of `isinstance` and dict lookups. For simple value comparison, regular `if`/`elif` is the right choice. Reach for `match` when you're destructuring.

**What could go wrong:** in `match`, a bare name like `case foo:` binds the matched value to a new variable `foo`. It does not check whether the value equals an existing `foo`. To compare against a named constant, qualify it: `case Status.PENDING:`. The error message when this bites you (something like "name capture pattern can't have an existing name") will not tell you what to do about it. Linters catch it. Bare-name patterns are a trap if you don't know to expect them.

### The walrus operator `:=`

The walrus assigns inside an expression. It exists because of one common pattern:

```python
# Without walrus:
while True:
    chunk = file.read(1024)
    if not chunk:
        break
    process(chunk)

# With walrus:
while chunk := file.read(1024):
    process(chunk)
```

The expression `chunk := file.read(1024)` reads a chunk and assigns it to `chunk`, and the whole expression evaluates to that chunk. The `while` loops while that value is truthy.

Where else is it useful?

```python
# Avoiding a function call twice in a comprehension:
results = [y for x in data if (y := transform(x)) is not None]

# Reading lines until a sentinel:
while (line := input("> ")) != "quit":
    print(f"You said: {line}")
```

Where is it not useful?

```python
# Don't:
if (n := len(items)) > 0:
    print(f"Got {n} items")

# Do:
n = len(items)
if n > 0:
    print(f"Got {n} items")
```

Both run. The second reads faster. The walrus earns its place when it removes a duplicated call or eliminates a `while True / break` pattern. It hurts when it saves you one line at the cost of denser code.

### `logging`: stop using `print` for anything serious

This is the section that pays the most dividends on an automation/DevOps path, so we'll take time.

You've been using `print` for everything. For an interactive script (output meant for a human reading the terminal), that's fine. For scripts that run unattended (cron jobs, systemd services, CI steps), `print` falls apart for several reasons:

1. **No timestamps.** When something failed three hours ago, "Error: connection refused" tells you nothing.
2. **No levels.** Debug noise and critical errors look identical.
3. **No routing.** Everything goes to stdout. You can't send errors to a file and info to syslog without rewriting every call.
4. **No tracebacks.** When an exception fires, you printed a string. The traceback that would have told you which line is gone.

The `logging` module solves all four. Here's the minimal setup to put at the top of any non-trivial script:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)
```

Then everywhere you would have written `print`:

```python
log.debug("Starting connection to %s", host)
log.info("Processed %d records", count)
log.warning("Disk usage at %d%%", pct)
log.error("Failed to write %s", path)
log.critical("Cannot recover; exiting")
```

Five levels, in order of severity. `basicConfig(level=logging.INFO)` sets a threshold: `DEBUG` messages are filtered out, `INFO` and above print. Bump to `DEBUG` when you're troubleshooting and you get more detail without changing any code.

Notice the `%s` and `%d` style. That is not an f-string, and the choice is deliberate. Logger methods accept lazy formatting: the string is only interpolated if the message will actually be emitted. With f-strings you pay the formatting cost on every call regardless of level, which adds up when DEBUG calls are scattered through a hot loop.

When you catch an exception, log it with the traceback:

```python
try:
    do_risky_thing()
except Exception:
    log.exception("Risky thing failed")
    # log.exception() is shorthand for log.error(..., exc_info=True)
```

`log.exception` includes the full traceback in the log output. This is the difference between "Error: something went wrong" and a usable bug report.

**What could go wrong:** every script writer's first mistake is calling `logging.info(...)` on the module instead of `log.info(...)` on a named logger. The module-level function works, but it configures a default handler the first time you call it, and that handler may not be what you want. Always create a logger via `logging.getLogger(__name__)` and call methods on it. This pattern also lets users of your code control logging behavior per-module from outside.

**What could also go wrong:** calling `basicConfig` in a library. `basicConfig` configures the *root* logger. If your library does it, you're hijacking the logging configuration of any application that imports you. Libraries should only call `logging.getLogger(__name__)` and emit logs. Applications (top-level scripts) own `basicConfig`.

### Putting it together

We opened with this:

```python
import os

def find_python_files(directory):
    result = []
    for filename in os.listdir(directory):
        full_path = directory + "/" + filename
        if os.path.isfile(full_path) and filename.endswith(".py"):
            result.append(full_path)
    return result

files = find_python_files("./src")
print("Found " + str(len(files)) + " Python files")
for f in files:
    print(f)
```

Here it is with every Tier 1 idea applied:

```python
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def find_python_files(directory: Path) -> list[Path]:
    """Return every .py file under `directory`, recursively."""
    return [p for p in directory.rglob("*.py") if p.is_file()]


def main() -> None:
    files = find_python_files(Path("./src"))
    log.info("Found %d Python files", len(files))
    for f in files:
        log.info("%s (%d bytes)", f, f.stat().st_size)


if __name__ == "__main__":
    main()
```

Same behavior. Twelve lines doing what twelve lines used to do, with timestamps, cross-platform paths, a return type that `mypy` can check, and logging output you can pipe through syslog or silence with a flag. None of the individual changes is dramatic. The aggregate is what readable Python looks like.

## Common pitfalls

1. **Reaching for a comprehension when a loop is clearer.** If you've added an `if`/`else`, a nested `for`, and the line wraps, write a loop. Code that other people have to read is not a place to flex.

2. **Comparing enum members with `==`.** It works, but every Python codebase that uses enums uses `is Status.PENDING`. Don't fight the idiom.

3. **Forgetting that mutable default arguments are shared.** `def f(items=[]):` reuses the same list across calls. The dataclass equivalent (`tags: list[str] = []`) is so wrong the decorator refuses it outright. Use `field(default_factory=list)`.

4. **Writing type hints without running `mypy`.** Hints are a contract. Unchecked annotations drift, the types slowly disagree with what the code does, and you can't tell. Run `mypy` (or `pyright`) in `pre-commit` or CI. Otherwise the annotations are decoration.

5. **Catching `Exception` and logging without the traceback.** `except Exception as e: log.error(e)` prints the message but throws away the traceback. Use `log.exception("...")` or `log.error("...", exc_info=True)`. The traceback is the most valuable line in your log; don't discard it.

6. **Joining paths with `+` after importing `pathlib`.** `Path("/var/log") + "/" + "app.log"` raises `TypeError`. You have to use `/`. The error is clear when you hit it, but the muscle memory takes a week to retrain.

## Try it yourself

Take this function and apply every Tier 1 idea you can: type hints, `pathlib`, f-string formatting, logging instead of print.

```python
import os
import time

def report_old_files(directory, days):
    now = time.time()
    cutoff = now - (days * 86400)
    found = 0
    for f in os.listdir(directory):
        full = directory + "/" + f
        if os.path.isfile(full):
            mtime = os.path.getmtime(full)
            if mtime < cutoff:
                size_mb = os.path.getsize(full) / (1024 * 1024)
                print("Old file: " + full + " (" + str(round(size_mb, 2)) + " MB)")
                found = found + 1
    print(str(found) + " old files found")
```

<details>
<summary>One possible answer</summary>

```python
import logging
import time
from pathlib import Path

log = logging.getLogger(__name__)


def report_old_files(directory: Path, days: int) -> int:
    """Log every file older than `days` and return the count."""
    cutoff = time.time() - days * 86400
    found = 0
    for p in directory.iterdir():
        if not p.is_file():
            continue
        stat = p.stat()
        if stat.st_mtime < cutoff:
            size_mb = stat.st_size / (1024 * 1024)
            log.info("Old file: %s (%.2f MB)", p, size_mb)
            found += 1
    log.info("%d old files found", found)
    return found


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    report_old_files(Path.home() / "Downloads", days=30)
```

Type hints on the signature. `pathlib` for paths. `iterdir` replaces `os.listdir` + `isfile`. `log.info` with lazy `%s`/`%.2f` formatting. A return value so callers can act on the count. `if __name__ == "__main__":` for clean import behavior. One `p.stat()` call cached because filesystem syscalls aren't free.
</details>

## How this connects

Everything here builds directly on the fundamentals. Modules 7 (lists and comprehensions), 10 (file I/O), 11 (classes), and 12 (exceptions) are the prerequisites for the polish in this lecture. Comprehensions deepen what Module 7 introduced. Dataclasses extend Module 11's classes. `pathlib` replaces the `os.path` and string-based file work from Module 10. `logging` replaces the `print`-based debugging you've leaned on since Module 1.

Looking forward, every module of the automation/DevOps curriculum assumes you have these. Module 1 (CLI tools with `click`) uses dataclasses for config objects and `logging` for output. Module 3 (files at scale) is `pathlib` cranked up, with `rglob`, `stat`, atomic writes, and file locking. Module 6 (logging and observability) extends what we covered here into structured logging, log aggregation, and metrics. Type hints become load-bearing in Module 7's testing work because `mypy` lets `pytest` skip a whole category of test you'd otherwise need to write. Treat this lecture as the floor of every later one.

## Recap

- `pathlib.Path` replaces `os.path`. Build with `/`, read with `.read_text()`, walk with `rglob`. Forget about string concatenation on paths.
- Comprehensions come in four shapes: list `[...]`, set `{...}`, dict `{k: v ...}`, generator `(...)`. Use generators for large or streaming data. Drop back to a `for` loop when the comprehension stops fitting on one line.
- F-strings have a format mini-language: `:.2f`, `:,`, `:.1%`, `:08b`, `:#x`. Use `f"{var=}"` for debug prints.
- Type hints are documentation `mypy` can verify. Annotate function signatures and dataclass fields. Use `dict | None` syntax on Python 3.10+.
- `@dataclass` writes `__init__`, `__repr__`, and `__eq__` for you. Use `field(default_factory=list)` for mutable defaults. Use `frozen=True` for value types you want to hash.
- `Enum` replaces string constants. Compare with `is`. Reach for `IntEnum` when integer interop matters.
- `match`/`case` shines for destructuring structured data. Use `if`/`elif` for plain value comparison. Watch out for bare-name capture patterns.
- The walrus `:=` belongs in `while`-read patterns and a few comprehensions. Skip it when a normal assignment is clearer.
- `logging` replaces `print` for anything that runs unattended. Set up `log = logging.getLogger(__name__)`, then call `log.info(...)` and `log.exception(...)`. Configure `basicConfig` once at the application entry point, never in a library.

## Up next

Tier 2 covers iterators, generators, context managers, decorators, and the `collections` and `functools` libraries: the features that change how you write Python, not just how it looks. After that, Module 1 of the Phase 2 curriculum picks up with building real CLI tools using `argparse`, `click`, `typer`, and `rich`.
