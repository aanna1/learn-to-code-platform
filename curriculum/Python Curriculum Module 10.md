# Module 10: Libraries, Modules, and Packages

## Why this matters

So far you've written every piece of every program by hand. Loops, conditionals, dictionaries, your own functions. That's been the right way to learn. But it's the wrong way to actually work.

Imagine you want to know how many days until your birthday. With what you know now, you'd have to write code that knows which months have 30 days, which have 31, that February has 29 in leap years, that a leap year is divisible by 4 except divisible by 100 unless also divisible by 400. That's maybe sixty lines of code, and there's a 95% chance you'll get it wrong in some subtle way that doesn't surface until 2100.

Or you could write this:

```python
from datetime import date
days = (date(2026, 11, 14) - date.today()).days
print(days)
```

Three lines. Correct in every year. Already tested by the millions of Python programs that depend on it. The leap-year logic is in there. You don't have to think about it.

That's the bargain this module is about. Python ships with a *standard library* of around two hundred modules covering dates, math, randomness, files, networking, compression, and a hundred other things you'd otherwise have to build yourself. On top of that, hundreds of thousands of third-party packages exist for the cases the standard library doesn't cover. The mark of a working Python programmer isn't writing more code; it's knowing what's already been written so you can write less.

This module also covers writing your own modules. The to-do list from Module 7 fit in one file. The weather app you'll build at the end of this module starts to strain at one file. Sooner or later every project outgrows a single file, and Python has a clean way to split work across many.

## What you'll be able to do by the end

- Import a module from the standard library and call its functions correctly.
- Tell the difference between `import x`, `from x import y`, and `from x import *`, and explain why the third one is a trap.
- Use `random`, `datetime`, `json`, `pathlib`, and `sys` for their most common jobs.
- Install a third-party package with `pip` and explain what a virtual environment is for.
- Split your own code across multiple `.py` files and import between them.
- Read a module's documentation well enough to use a function you've never seen before.

## Prerequisites

Module 6 (functions) is the big one. Most of what a library does is hand you functions to call, so calling functions has to be second nature. Module 8 (dictionaries) matters because almost all data returned by libraries is dict-shaped, especially anything that came from JSON. Module 9 (exceptions) is here too: many library functions raise specific exceptions you'll want to catch.

## Core concepts

### Module, package, library: the words

Three terms that often get used interchangeably. Worth pinning down before we go further.

A **module** is a single `.py` file containing Python code. The file `math.py` (which ships with Python) is the `math` module.

A **package** is a folder of related modules grouped together. The `urllib` package contains modules `urllib.request`, `urllib.parse`, and so on, each one a separate file in a `urllib/` folder.

A **library** is informal English for either of the above. People say "the `requests` library" when they mean a package. They say "the `math` library" when they mean a module. The word means "a chunk of code someone else wrote that you import." Don't overthink it.

### `import`: three flavors

The basic version:

```python
import math
print(math.sqrt(16))   # 4.0
print(math.pi)         # 3.141592653589793
```

`import math` makes the whole `math` module available under the name `math`. You access anything in it with `math.something`. This is the safest, clearest form, and it's what you should use 90% of the time.

Now the second flavor:

```python
from math import sqrt, pi
print(sqrt(16))        # 4.0
print(pi)              # 3.141592653589793
```

`from math import sqrt, pi` pulls just those two names directly into your file. You can then call `sqrt` without the `math.` prefix. This is fine when you're using one or two names from a module a lot and the abbreviation makes the code more readable. The risk is that `sqrt` could collide with a variable named `sqrt` in your own code. Not usually a problem for famous names like `pi`; more of a problem for generic names like `path` or `open`.

Now the third flavor, which is the one you should not write:

```python
from math import *
print(sqrt(16))
print(pi)
```

`from math import *` imports every public name from `math` into your file. It feels convenient. Watch what goes wrong:

```python
from math import *
from cmath import *      # complex math
print(sqrt(-1))          # what does this print?
```

The second import overwrote `sqrt` with the complex-number version. Now `sqrt(-1)` returns `1j` (an imaginary number) instead of raising a `ValueError`. If you didn't know `cmath` had a `sqrt`, you'd have no idea why the answer suddenly turned weird. With explicit `math.sqrt` and `cmath.sqrt`, the namespace collision is visible.

Bigger problem: when you read someone else's code that uses `import *`, you can't tell where a name came from. `sqrt` could be defined in this file, or imported from `math`, or imported from `cmath`. You'd have to read the whole file to find out.

Rule of thumb. Use `import module`. Sometimes use `from module import specific_name`. Almost never use `from module import *`. (Some libraries are *designed* to be star-imported. The Python community will warn you specifically when that's the case. If nobody warned you, don't.)

### Aliasing with `as`

You can rename a module or an imported name on the way in:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

These three aliases are conventions so deeply baked into the data-science world that you'll see them in every tutorial. `np`, `pd`, and `plt` are universal. If you wrote `import numpy as numpy` it would be correct but it would mark you as a beginner.

For libraries that aren't in some convention, leave the name alone. `import math as m` saves three characters and confuses every reader. Don't.

### Tour: `random`

The `random` module gives you randomness. The two functions you'll use most:

```python
import random

random.randint(1, 6)            # an integer in [1, 6], inclusive on both ends
random.choice(["yes", "no"])    # a random element from a list
```

Notice the inclusive endpoints on `randint`. This is one of the few places in Python where a range is inclusive of the upper bound, and it's a frequent source of off-by-one bugs because every other range in Python is upper-exclusive. Watch:

```python
import random
for _ in range(10000):
    n = random.randint(1, 6)
    assert 1 <= n <= 6
```

That asserts what `randint` actually promises. `randint(1, 6)` will produce any integer from 1 to 6, including both 1 and 6. If you wanted "1 through 5," you'd write `randint(1, 5)`, not `randint(1, 6)`.

Compare to the other function for the same kind of job:

```python
random.randrange(1, 6)          # integer in [1, 6), exclusive on upper end
```

`randrange(1, 6)` produces 1, 2, 3, 4, or 5. Never 6. This matches `range(1, 6)` from Module 5, which also stops at 5. The naming is consistent with the rest of Python. `randint` is the odd one out, and it's the one people misuse.

Use `randint` when the spec literally says "a number from 1 to 6, like a die." Use `randrange` when you're picking an index, where you want it consistent with `range()`. Use `random.choice` when you can express the choice as a list.

A few other useful ones:

```python
random.random()                 # float in [0.0, 1.0)
random.shuffle(my_list)         # shuffles in place, returns None (Module 7 rule)
random.sample([1, 2, 3, 4, 5], 3)   # 3 unique items, doesn't modify the list
```

### Tour: `datetime`

Dates and times in Python come from the `datetime` module. The module's name is also the name of one of the classes inside it, which is confusing the first time you meet it. To make the confusion worse, the module also contains `date`, `time`, and `timedelta` classes.

For days-and-no-times work, the `date` class is enough.

```python
from datetime import date

today = date.today()
print(today)                # 2026-05-18
print(today.year)           # 2026
print(today.month)          # 5
print(today.day)            # 18
```

Want to know how many days between two dates? Subtract them.

```python
from datetime import date

birthday = date(2026, 11, 14)
today = date.today()
delta = birthday - today
print(delta.days)           # 180 (or whatever the actual difference is)
```

Subtracting two dates produces a `timedelta`, which represents a span of time. Its `.days` attribute is the integer number of days. This is the right way to compute "days between." The wrong way that beginners reach for:

```python
# DON'T DO THIS
months_diff = birthday.month - today.month
days_diff = birthday.day - today.day
total = months_diff * 30 + days_diff
```

That assumes every month has 30 days. February exists. Leap years exist. Even ignoring those, what if the birthday is next year? `months_diff` goes negative. The `timedelta` version handles every case automatically and uses the actual calendar.

The other catch: `date(2026, 13, 1)` raises `ValueError`. There is no month 13. Python is strict about dates being real dates. Same for `date(2026, 2, 30)` (February doesn't have 30 days, even in leap years).

For dates *with* times, use `datetime` (the class, inside the `datetime` module):

```python
from datetime import datetime
now = datetime.now()
print(now)              # 2026-05-18 14:32:01.123456
```

Same arithmetic rules. Subtracting two `datetime` values gives a `timedelta` that includes hours, minutes, and seconds.

### Tour: `json`

JSON ("JavaScript Object Notation") is a text format for structured data. It looks like Python dicts and lists, because it inspired their syntax:

```
{"name": "Ada", "age": 25, "skills": ["python", "math"]}
```

That's a JSON string. Notice it's a *string*: keys and string values in double quotes, no Python-style single quotes, no trailing commas, no `True`/`False` (JSON uses lowercase `true`/`false`), and `None` becomes `null`.

The `json` module converts between Python objects and JSON strings.

```python
import json

# Python -> JSON string
person = {"name": "Ada", "age": 25, "is_student": False}
text = json.dumps(person)
print(text)
# {"name": "Ada", "age": 25, "is_student": false}

# JSON string -> Python
parsed = json.loads(text)
print(parsed["name"])    # Ada
```

`json.dumps` is "dump string" (serialize to a string). `json.loads` is "load string" (parse a string). The cousins without the `s` (`json.dump` and `json.load`) work directly on files; we'll meet those in Module 11.

For human-readable output, pass `indent`:

```python
print(json.dumps(person, indent=2))
```

```
{
  "name": "Ada",
  "age": 25,
  "is_student": false
}
```

That's the formatting you want when saving config files or anything a human might open.

What goes wrong: JSON doesn't support every Python type. It can't represent tuples (they come back as lists), sets, dates, or custom objects. If you try to serialize one, `json.dumps` raises `TypeError: Object of type X is not JSON serializable`. The fix is to convert your data to JSON-friendly shapes before serializing: lists, dicts, strings, numbers, booleans, `None`.

### Tour: `pathlib`

For working with file paths, `pathlib` is the modern, sane API.

```python
from pathlib import Path

p = Path("data/users.json")
print(p.exists())            # True or False
print(p.parent)              # data
print(p.name)                # users.json
print(p.stem)                # users
print(p.suffix)              # .json
```

A `Path` object is a path with methods attached. To build paths up, use `/`:

```python
from pathlib import Path

base = Path("/home/user/projects")
config = base / "myapp" / "config.json"
print(config)    # /home/user/projects/myapp/config.json
```

That `/` is the path-joining operator on `Path` objects. It works on Windows and Mac and Linux. It does the right thing with separators (backslash vs forward slash) on each platform.

Compare to the old way:

```python
# Don't do this
config = "/home/user/projects" + "/" + "myapp" + "/" + "config.json"
```

Or even with `os.path.join`, which works but is fiddlier than the `/` operator. `pathlib` is what you reach for in any code written this decade.

Read and write are one-liners:

```python
p = Path("notes.txt")
content = p.read_text()
p.write_text("new content")
```

These do `open` and `close` for you. No `with` block needed. (You'll still want `with` for big files you read line by line, which is Module 11.)

### Tour: `sys`

The `sys` module gives you access to the running Python interpreter. The most-used feature: command-line arguments.

```python
# script.py
import sys

print(sys.argv)
```

Run it:

```
$ python script.py hello world
['script.py', 'hello', 'world']
```

`sys.argv` is the list of command-line arguments. `argv[0]` is the script name itself. `argv[1]`, `argv[2]`, and so on are the arguments you passed.

Useful for writing scripts that take input from the command line instead of from `input()`:

```python
import sys

if len(sys.argv) != 2:
    print("Usage: python greet.py <name>")
    sys.exit(1)

name = sys.argv[1]
print(f"Hello, {name}!")
```

`sys.exit(code)` ends the program with the given exit code. A non-zero code means "something went wrong." Other programs that run yours look at the exit code to know whether you succeeded.

For anything fancier (flags like `--verbose`, optional arguments, defaults), the standard library has `argparse`. Worth looking up when you need it.

### Tour: `math` and `statistics`

`math` you've seen. It has `sqrt`, `pi`, `floor`, `ceil`, `log`, and the trig functions. One quirk worth flagging: `round` is a built-in, not from `math`, and it uses "banker's rounding" (round-half-to-even). So `round(2.5)` is 2, not 3. If you need predictable always-round-up-on-halves behavior, write it yourself: `math.floor(x + 0.5)` for positive numbers.

`statistics` is for summaries you'd otherwise compute by hand:

```python
import statistics
scores = [85, 92, 78, 95, 88, 76]
print(statistics.mean(scores))      # 85.66666...
print(statistics.median(scores))    # 86.5
```

For bigger data work, `numpy` and `pandas` are what you'll actually use. `statistics` is fine for small data.

### Third-party packages: `pip` and virtual environments

The standard library is generous, but not exhaustive. To talk to a real web server, you want `requests`. To work with tabular data, you want `pandas`. To run tests, you want `pytest`. These don't ship with Python. You install them.

The tool is `pip` (Pip Installs Packages). From your terminal, outside of Python:

```
pip install requests
```

That downloads `requests` from the Python Package Index (PyPI) and installs it so you can `import requests` in your scripts. The answer to the curriculum's checkpoint is exactly that: `pip install <name>`.

The problem with installing packages globally is that different projects want different versions. Project A needs `requests` 2.28; Project B needs `requests` 2.31. If you install everything globally, the projects fight, and upgrading one breaks the other.

The fix is a **virtual environment**: a self-contained folder of Python and its packages, separate from the system's Python. Each project gets its own.

```
python -m venv venv          # create a folder called venv
source venv/bin/activate     # activate it (Mac/Linux)
venv\Scripts\activate        # activate it (Windows)
pip install requests         # installs into the venv, not the system
```

After `activate`, your shell uses the venv's Python and pip. `pip install` puts packages in the venv. You're isolated from the rest of your system. When you're done:

```
deactivate
```

For the curriculum's checkpoint: a virtual environment isolates a project's dependencies so different projects can have different versions of the same package without conflict.

Tools like `poetry`, `pipenv`, and `uv` do roughly the same thing with more features. Plain `venv` is enough until you have a reason for something else.

### Writing your own module

Once a script outgrows one file, you split it. Suppose you have:

```
my_project/
    main.py
    dice.py
```

In `dice.py`:

```python
# dice.py
import random

def roll():
    return random.randint(1, 6)

def roll_many(n):
    return [roll() for _ in range(n)]
```

In `main.py`:

```python
# main.py
import dice

print(dice.roll())
print(dice.roll_many(5))
```

Running `python main.py` from inside the `my_project/` folder runs the program. The `import dice` line finds `dice.py` in the same folder and pulls it in.

A subtlety. When you `import dice`, every top-level statement in `dice.py` runs once. Function definitions get registered. Anything else also happens. If you wrote `print("loading dice")` at the top of `dice.py`, that prints the first time anyone imports it. This is occasionally useful, more often a source of surprise.

The convention for "code that should only run when this file is the main script, not when it's imported" is:

```python
# dice.py
import random

def roll():
    return random.randint(1, 6)

if __name__ == "__main__":
    # only runs when you do `python dice.py`
    # doesn't run when another file does `import dice`
    for _ in range(5):
        print(roll())
```

`__name__` is a special variable. When a file is run directly, its `__name__` is `"__main__"`. When it's imported, `__name__` is the name of the module. The `if __name__ == "__main__":` block is a guard that lets you both `import dice` (without running test code) and `python dice.py` (which does run it). You'll see this pattern in nearly every Python project.

### Reading documentation

The most useful skill in this module isn't memorizing function signatures. It's getting comfortable with the official docs and `help`.

In a Python REPL:

```python
import random
help(random.randint)
```

```
Help on method randint in module random:

randint(a, b) method of random.Random instance
    Return random integer in range [a, b], including both end points.
```

That's the documentation. Inclusive on both ends, as we discussed.

For a tour of everything a module offers:

```python
import random
print(dir(random))
```

`dir` returns a list of every name in the module. Most of them are functions you can `help()` to learn about.

The web documentation at `docs.python.org` is the canonical reference. Searching for "python random" almost always lands you on the official page.

## Common pitfalls

1. **`from module import *`.** Collides names, hides where things come from, and breaks readers' ability to follow your code. Use `import module` or `from module import specific_name`.

2. **`random.randint(1, 6)` for an index.** It's inclusive on both ends. If you wanted "an index into a list of 6 items," you wanted `random.randrange(6)`, which gives 0 through 5. Mixing them up causes off-by-one bugs.

3. **String math on dates.** `"2026-11-14"[:4]` for the year is fragile and ignores time zones, leap years, and validation. Use `datetime.date` and arithmetic on it.

4. **Treating `json.dumps` like it can serialize anything.** Tuples become lists. Sets, dates, and custom objects raise `TypeError`. Convert to JSON-friendly shapes first.

5. **Installing packages globally without a virtual environment.** Sooner or later, two projects need conflicting versions and you spend an afternoon untangling it. Make a habit of `python -m venv venv` at the start of every project.

6. **Forgetting `if __name__ == "__main__":` in a script that gets imported.** Your test code runs every time someone imports the file, with surprising results. The guard is one line; use it.

## Try it yourself

**Problem 1.** Use `random.choice` to pick a random word from the list `["python", "java", "rust", "go"]`. Then use `random.sample` to pick two different ones.

<details>
<summary>Answer</summary>

```python
import random

languages = ["python", "java", "rust", "go"]
print(random.choice(languages))
print(random.sample(languages, 2))
```

`random.choice` returns one element. `random.sample(seq, k)` returns a list of `k` distinct elements. If you used `random.choices` (note the `s`) instead, you could get duplicates, which is not what we wanted here.

</details>

**Problem 2.** Without running it, predict what this prints today (assume today is May 18, 2026):

```python
from datetime import date

d1 = date(2026, 1, 1)
d2 = date(2026, 12, 31)
print((d2 - d1).days)
```

<details>
<summary>Answer</summary>

```
364
```

`d2 - d1` is a `timedelta`. There are 364 days between January 1 and December 31 of the same year. Off by one from your gut answer of 365? That's because we're counting the days *between* the two dates, not the days *in* the year. Jan 1 to Jan 2 is 1 day, not 2.

</details>

**Problem 3.** Convert this Python dictionary to a JSON string and back. What do you notice about the value of `coords` after the round trip?

```python
import json
data = {"name": "checkpoint", "coords": (3, 4)}
text = json.dumps(data)
back = json.loads(text)
print(type(back["coords"]))
```

<details>
<summary>Answer</summary>

```
<class 'list'>
```

`coords` started as a tuple. JSON has no tuple type, only arrays, so it serialized as `[3, 4]`. When loaded back, JSON arrays become Python lists. The round trip lost the "tuple" type. If your code downstream assumes `coords` is a tuple (and tries to use it as a dict key, for instance), it'll break.

This is one of the reasons JSON is great for interchange but not great for preserving every Python detail. For round-tripping arbitrary Python objects, look at `pickle` instead, but be aware `pickle` is unsafe to load from untrusted sources.

</details>

## How this connects

This module is the bridge between "writing Python from scratch" and "writing real programs." From here on:

- **Module 11 (files and CSV)** uses `pathlib` and `json` constantly. The `with open(...)` pattern you'll meet there is the file equivalent of `try`/`finally`, and it pairs naturally with the path-handling vocabulary from this module.
- **Module 12 (the internet)** uses `requests` (third-party) and `urllib` (standard library) to fetch data from the web. The mini-project for this module (the weather app) is your first taste.
- **Module 13 (object-oriented programming)** lets you split your modules into classes within them. The `datetime.date` class you've been using is itself a class inside a module. You'll write your own.
- **Module 14 (testing)** uses `pytest`, the most popular third-party Python library after `requests`. Knowing how to install and import it is the entire setup.
- **Anything you build from here on** will be a mix of your own code and library calls. The split-files pattern with `if __name__ == "__main__":` is how every real project is structured.

If anything feels shaky after this module, it's most likely the venv workflow. The first time it pays off is the third or fourth project you start, when you realize you didn't have to clean up your global Python install. Make the venv every time and the habit sticks.

## Recap

- A module is a `.py` file. A package is a folder of modules. A library is informal English for either.
- `import module` is the safe default. `from module import specific_name` is fine. `from module import *` is a trap.
- `import x as y` renames on the way in. Use conventional aliases (`np`, `pd`, `plt`); don't invent your own.
- `random.randint(a, b)` is inclusive on both ends. `random.randrange(a, b)` is exclusive on the upper end, matching `range`.
- `datetime.date` for calendar dates, `datetime.datetime` for date-plus-time, `timedelta` for spans. Subtraction is the right way to compute differences.
- `json.dumps` and `json.loads` for converting between Python and JSON. Tuples become lists; sets, dates, and custom objects don't survive.
- `pathlib.Path` is the modern API for filesystem paths. Use `/` to join. `read_text` and `write_text` are one-liners.
- `sys.argv` is the list of command-line arguments. `sys.exit(code)` ends the program with an exit code.
- `pip install <name>` installs a third-party package from PyPI. Always inside a virtual environment (`python -m venv venv`, then activate).
- Splitting code across files uses `import filename` (no `.py`). The `if __name__ == "__main__":` guard separates "imported" from "run directly."

## Up next

Module 11 is files and persistent data. You'll read and write text files, CSVs, and JSON files, using the `with` statement and the `pathlib` API you just met. The phone book from Module 8 and the weather app's responses both become things you can save to disk and load back next time.

Now go work the exercises and mini-project for Module 10 in the curriculum doc. The Magic 8-Ball is a five-minute warmup. The days-until-birthday exercise is the one that locks in `datetime` arithmetic. The weather app is the capstone: your first Python program that talks to the internet, parses real JSON, and produces output a human would actually read.
