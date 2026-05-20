# Module 11: File Input and Output

## Why this matters

Every program you've written so far has had the same fatal flaw. The moment you close it, everything it computed vanishes. The to-do list from Module 7 forgets every task. The dice game from Module 4 forgets your high score. The expense tracker we're about to build would be useless if it couldn't remember a single expense between Tuesday and Wednesday.

Memory is volatile. Disk is not. That's the whole point of this module: take the data your program built up while running, write it somewhere the operating system will keep around, and read it back next time the program starts. With that one capability, your programs stop being throwaway calculators and start being software.

Files are also how programs talk to each other and to the outside world. The grades you'll process tomorrow come from a CSV someone exported from a spreadsheet. The configuration your script reads on startup lives in a JSON file. The log your web server writes will be a text file you'll need to parse. By the end of this lecture, all of those become workable.

## What you'll be able to do by the end

- Open files using the `with` statement and explain why you'd never go back to opening them any other way.
- Pick the right mode for the job (read, write, or append) and recognize what happens when you pick wrong.
- Read a file three ways (all at once, as a list of lines, or line by line) and choose the right one for the file's size.
- Parse CSV files with `csv.reader` for positional rows and `csv.DictReader` for named columns.
- Save Python lists and dictionaries to JSON files and load them back into Python.
- Use `pathlib` to build file paths that work on Windows, Mac, and Linux without surgery.

## Prerequisites

You should be solid on Modules 1 through 10. This module leans hard on lists and dictionaries from Module 7, because most file content ends up in one or the other. Exceptions from Module 8 matter too, because every line of file code can fail (the file might not exist, the disk might be full, the user might not have permission). Imports from Module 10 are the price of admission to the `csv`, `json`, and `pathlib` modules we'll lean on throughout.

If "iterate over a list of dictionaries" or "catch a `FileNotFoundError`" feels unfamiliar, pause and review before continuing. Nothing here is hard on its own; the difficulty is that we're combining most of what you've learned.

## Core concepts

### The problem we're solving

Picture this. You run your to-do app, add "buy milk," "call mom," and "pay rent." You quit. You restart it. The list is empty. That isn't because you did anything wrong; the only place those three strings ever existed was inside a Python list, and Python's lists live in memory. When the program exits, that memory goes back to the operating system. Your list is gone.

For the list to survive, you need to write it onto the disk before quitting and read it back when starting. The mechanism for doing that is files.

### Opening a file: the manual way, then the right way

Here's the most direct way to write a string to a file in Python. We won't use it past this paragraph, but it's worth seeing the moving parts.

```python
f = open("greeting.txt", "w")
f.write("Hello from Python\n")
f.close()
```

Three steps. `open()` returns something called a file object. You call methods on that object: `.write()` to put data in, `.close()` to flush it to disk and release the file.

Now ask yourself: what happens if the program crashes between `open()` and `close()`? Or you forget the `close()` because you added an early `return`? The file might be left open. The data might not be flushed. On Windows, you might not even be able to open the file in another program until your Python process exits.

The fix is the `with` statement.

```python
with open("greeting.txt", "w") as f:
    f.write("Hello from Python\n")
```

Same effect, but `close()` is guaranteed. The `with` statement says: open the file, bind it to the name `f` for the duration of this indented block, and the moment the block ends (whether normally or because of an exception), close the file. You write the open. You don't write the close. Python handles it.

From here on, we'll always use `with`. There is no situation in this curriculum, or in any modern Python codebase, where the bare `open()` form is preferable. If you see code without `with`, treat it as old code that hasn't been updated.

### Modes: read, write, append

The second argument to `open` is the mode. The three you'll use 95% of the time:

- `"r"` opens an existing file for reading. The file must exist or you get a `FileNotFoundError`. This is the default if you skip the mode argument.
- `"w"` opens a file for writing. If the file doesn't exist, it gets created. If it already exists, **its contents are erased.**
- `"a"` opens a file for appending. New content goes at the end. Existing content stays.

That second one bites everyone exactly once. Let's get bitten now so it doesn't happen later.

```python
# Run this script, then type "Alice"
name = input("Name: ")
with open("names.txt", "w") as f:
    f.write(name + "\n")
```

Run it. Type `Alice`. Run it again, type `Bob`. Run it again, type `Carol`. Now open `names.txt`. What do you see?

You see `Carol`. Just `Carol`. Where did Alice and Bob go?

They got erased. `"w"` mode doesn't add to the file; it replaces the file. Every time the script ran, it opened `names.txt` with mode `"w"`, which truncated the file to zero bytes, wrote one name, and closed.

The fix is one character. Change `"w"` to `"a"`:

```python
name = input("Name: ")
with open("names.txt", "a") as f:
    f.write(name + "\n")
```

Now Alice, Bob, and Carol all stick around, each on its own line.

> **What could go wrong:** When you want to *replace* a file's contents (saving a fresh version of a to-do list after editing), `"w"` is correct, because you're overwriting the old version with a complete new one. When you want to *add to* a file (a log line, a new journal entry), `"a"` is correct. The mistake is using `"w"` for additive work.

A useful habit: if losing the existing file would ruin your day, look at the mode one more time before running the script.

### The newline you forgot to add

Notice the `\n` at the end of `f.write(name + "\n")`. `f.write()` does not add a newline for you. If you wrote four names without `\n`, they'd land in the file as `AliceBobCarolDave`, one continuous string. `print()` adds newlines for you; `write()` does not. This trips up nearly everyone the first time.

### A word on encoding

Text files store bytes. To turn those bytes back into characters, Python needs to know an encoding. Modern Python defaults to UTF-8 on most systems, which handles every character you're likely to use, including accented letters and emoji. If you ever need to be explicit:

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    contents = f.read()
```

For this curriculum, you can rely on the default. The case where this comes up is reading a file someone else made with a different encoding (a CSV exported from an older Windows Excel, for instance). The symptom is a `UnicodeDecodeError` halfway through reading the file. The fix is passing the right `encoding=` value, usually `"utf-8"`, `"utf-16"`, or `"cp1252"`.

### Reading a file three ways

You have a file with names in it:

```
Alice
Bob
Carol
```

You want those names in your Python program. There are three approaches, and the right one depends on how big the file is.

**Approach 1: read the whole thing as one string.**

```python
with open("names.txt", "r") as f:
    contents = f.read()
print(contents)
```

`contents` is now a single string: `"Alice\nBob\nCarol\n"`. Convenient for small files, terrible for a 10-gigabyte log file (you'd run out of memory).

**Approach 2: read all lines into a list.**

```python
with open("names.txt", "r") as f:
    lines = f.readlines()
print(lines)
```

`lines` is `['Alice\n', 'Bob\n', 'Carol\n']`. Notice the `\n` at the end of each entry. `readlines` keeps the newline characters; if you don't want them, you'll need to strip them.

```python
with open("names.txt", "r") as f:
    lines = [line.strip() for line in f.readlines()]
print(lines)  # ['Alice', 'Bob', 'Carol']
```

**Approach 3: iterate line by line.**

```python
with open("names.txt", "r") as f:
    for line in f:
        print(line.strip())
```

This is the one to reach for by default. It reads one line at a time. It works on files of any size, because at no point does the whole file have to fit in memory. Iterating over a file object yields lines, each ending in `\n` (which you'll usually strip).

A common bug: forgetting `.strip()` when you print or compare. If your output has extra blank lines between every name, you're double-printing newlines: once from the file's `\n`, once from `print()`. Either strip the line first, or pass `end=""` to `print`.

**Try it.** Without running it, what does this print?

```python
with open("names.txt", "r") as f:
    first_line = f.readline()
    second_line = f.readline()
print(first_line)
print(second_line.strip())
```

<details>
<summary>Answer</summary>

```
Alice

Bob
```

The first `print` outputs `"Alice\n"`, which prints `Alice` followed by the newline already in the string, then `print` adds *its own* newline on top. So you see `Alice` and a blank line under it. The second `print` uses `.strip()`, so just `Bob`. This is why so many file-reading tutorials look like they have phantom blank lines: forgotten strips.

</details>

### CSV: when commas have meaning

A lot of real-world data lives in CSV files. Commas separate columns; newlines separate rows. The first row is usually a header.

```
name,grade
Alice,92
Bob,77
Carol,88
```

Your first instinct will be to read each line and split on the comma:

```python
with open("students.csv", "r") as f:
    for line in f:
        parts = line.strip().split(",")
        print(parts)
```

That works. Until it doesn't. Consider this row:

```
"Smith, John",88
```

A name with a comma inside it, wrapped in quotes to mark it as one field. `line.split(",")` doesn't know about the quotes; it sees commas and gives you three pieces: `'"Smith'`, `' John"'`, and `'88'`. The name has been destroyed.

The `csv` module knows the rules. Use it.

```python
import csv

with open("students.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

`csv.reader` iterates over the file and gives you each row as a list of fields, with all the quoting and escaping handled for you.

```
['name', 'grade']
['Alice', '92']
['Bob', '77']
['Carol', '88']
```

Two things worth noticing. First, the header row comes through like any other row; you'll usually `next(reader)` to skip it, or use `DictReader` instead (next paragraph). Second, every value is a string. Even `92`. CSV is plain text; the reader doesn't know which columns are numbers, so it hands you everything as a string. Cast with `int()` or `float()` when you need to do math.

`csv.DictReader` is friendlier when the file has headers:

```python
import csv

with open("students.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], int(row["grade"]))
```

Each row arrives as a dictionary keyed by the header names. No counting commas. No remembering that "the name was column zero." If someone reorders the columns in the spreadsheet later, your code still works.

**Writing CSV.** Use `csv.writer`. One quirk worth flagging: pass `newline=""` to `open()`, or on Windows you'll get an extra blank line between every row.

```python
import csv

rows = [["name", "grade"], ["Alice", 92], ["Bob", 77]]
with open("students_out.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)
```

`writerow` writes one row; `writerows` writes a list of them.

**Try it.** You have `students.csv` from above. Write code that reads it with `csv.DictReader`, casts each grade to an integer, and prints the average. Aim for under 10 lines.

<details>
<summary>Answer</summary>

```python
import csv

with open("students.csv") as f:
    grades = [int(row["grade"]) for row in csv.DictReader(f)]

print(f"Average: {sum(grades) / len(grades):.1f}")
```

A list comprehension over `DictReader` pulls just the grades, casting each to `int` as it goes. Then `sum / len` for the average. The `:.1f` in the f-string rounds to one decimal place. If you wrote a `for` loop with a running total, that's fine too; the comprehension is just shorter.

</details>

### JSON: structure that survives

CSV is great for flat rectangular data: rows and columns. JSON is what you reach for when your data has shape. Lists inside dicts, dicts inside lists, anything nested.

The two functions you need are `json.dumps` (Python object to JSON string) and `json.loads` (JSON string to Python object). The variants `json.dump` and `json.load` (no `s`) work directly with file objects.

```python
import json

todos = [
    {"title": "buy milk", "done": False},
    {"title": "call mom", "done": True},
]

with open("todos.json", "w") as f:
    json.dump(todos, f, indent=2)
```

That writes:

```json
[
  {
    "title": "buy milk",
    "done": false
  },
  {
    "title": "call mom",
    "done": true
  }
]
```

The `indent=2` argument makes it human-readable. Skip it and you get one long line, which the computer reads just as well but you can't.

Reading it back:

```python
import json

with open("todos.json", "r") as f:
    todos = json.load(f)

print(todos[0]["title"])  # buy milk
```

`todos` is now a list of dictionaries with exactly the shape it had when you wrote it. This is the standard way to persist a Python data structure: dump it on the way out, load it on the way in.

> **What could go wrong:** JSON is strict about types. Python `True` becomes JSON `true`, `None` becomes `null`, and only basic types (strings, numbers, lists, dicts, booleans, `None`) survive the round trip. A Python `datetime` object can't be JSON-encoded without telling it how. Custom classes can't either. We'll address that in Module 13 when we talk about converting objects to dicts before saving.

**Try it.** Sketch (before peeking) a program that asks the user for one favorite thing per run (a movie, a song, a color, whatever they want) and saves all the answers across runs into `favorites.json`. The file starts empty. After three runs, it should hold all three answers.

<details>
<summary>Answer</summary>

```python
import json
from pathlib import Path

FILE = Path("favorites.json")

# Load existing list, or start with an empty one
if FILE.exists():
    favorites = json.loads(FILE.read_text())
else:
    favorites = []

# Add the new entry
favorites.append(input("Favorite: "))

# Save the updated list
FILE.write_text(json.dumps(favorites, indent=2))

print(f"You now have {len(favorites)} favorites saved.")
```

The pattern is *load, mutate, save*. You'll use it for every persistent program in the rest of the curriculum. We're using `pathlib` here, which is what the next section is about.

</details>

### File paths: stop concatenating strings

Where does `open("notes.txt")` look for the file? In the current working directory, which is wherever your terminal was when you ran `python script.py`. Move the terminal somewhere else and the same script can't find the file.

You'll often want absolute paths, or paths relative to the script itself. The instinct is to build them with string concatenation:

```python
folder = "/Users/me/projects/data"
filename = "notes.txt"
path = folder + "/" + filename
```

That breaks on Windows, where the separator is a backslash. It breaks again if `folder` already ends with a slash and you add another. It breaks in subtle ways you won't catch until your code runs on someone else's machine.

`pathlib` is the modern fix. A `Path` object knows how to combine pieces correctly on any operating system.

```python
from pathlib import Path

folder = Path("/Users/me/projects/data")
path = folder / "notes.txt"
```

The `/` operator on `Path` objects builds paths. It uses the right separator for the OS. It collapses double slashes. It handles edge cases you don't want to think about.

`Path` also has methods that save you the open/read/close dance for simple cases:

```python
from pathlib import Path

p = Path("notes.txt")

# Read the whole thing as a string
contents = p.read_text()

# Write a string, replacing existing contents
p.write_text("Hello\n")

# Check whether a file exists
if p.exists():
    print("Found it.")
```

For more involved reading (line by line, large files), stick with `with open(...)`. For one-shot reads and writes, `pathlib` is shorter.

A handy idiom: `Path(__file__).parent` gives you the folder containing the currently running script, regardless of where the user ran it from. Combine with `/` for files that live next to your script:

```python
from pathlib import Path

CONFIG = Path(__file__).parent / "config.json"
```

`__file__` is a built-in variable Python sets to the path of the script being executed. `.parent` is the folder it's in. This pattern fixes the "works from the project root, breaks from anywhere else" bug we'll discuss in pitfalls.

## Common pitfalls

**1. Forgetting `with` and forgetting to close.**

```python
f = open("data.txt", "w")
f.write("important data")
# script ends here without f.close()
```

On most systems, the data eventually flushes when Python garbage-collects the file object, but "eventually" is the wrong word for persistence. Use `with`.

**2. Using `"w"` when you meant `"a"`.**

```python
with open("log.txt", "w") as f:   # wipes the log every time
    f.write(message)
```

Every run nukes the previous content. For logs, journals, any additive work, use `"a"`.

**3. Forgetting `.strip()` on lines read from a file.**

```python
with open("names.txt") as f:
    for line in f:
        if line == "Alice":   # always False
            print("Found Alice")
```

The line is `"Alice\n"`, with the newline. The comparison fails. Fix: `if line.strip() == "Alice":`. Same trap when stuffing lines into a set or using them as dict keys.

**4. Forgetting that CSV values are strings.**

```python
with open("scores.csv") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    total = 0
    for row in reader:
        total += row[1]   # TypeError
```

CSV hands you strings. Cast before doing math: `total += int(row[1])`.

**5. CSV writer producing blank lines on Windows.**

```python
with open("out.csv", "w") as f:   # missing newline=""
    csv.writer(f).writerow(["a", "b"])
```

You'll see every other row blank. Fix: `open("out.csv", "w", newline="")`. The `newline=""` looks pointless, but it tells `open` to leave newline translation to the `csv` module, which knows what it's doing.

**6. Relative path confusion.**

```python
with open("config.json") as f:   # works from project root, fails from elsewhere
    ...
```

If your script needs to find a file next to itself regardless of where it's run from, use `Path(__file__).parent / "config.json"`.

## How this connects

This module is the bridge between programs that run once and programs that have a life over time. Every persistent program you'll write from now on uses what's here.

Looking back: Module 7's lists and dictionaries finally have a way to outlast a single run. Module 8's exception handling stops being optional, because a missing file or a permission error is a normal part of file work, not an exotic edge case. The journal you're about to build will throw `FileNotFoundError` on its first run, before any journal file exists, and you'll handle it by checking `.exists()` first or catching the exception. Module 10's imports were the warmup for the `csv`, `json`, and `pathlib` libraries you used here.

Looking forward: Module 12 (regex) gives you tools to parse the messy text inside log files. Module 13 (classes) will use JSON persistence to make objects survive across runs, with a small twist: classes need a conversion step to plain dicts on the way out. Module 14's testing module will ask you to write tests for functions that touch files, which forces a useful habit of separating "the logic" from "the file plumbing."

## Recap

- `with open(path, mode) as f:` is the right way to open a file. The file closes when the block ends, even on exceptions.
- Modes: `"r"` reads, `"w"` writes and erases, `"a"` appends. Pick wrong and you lose data.
- Three ways to read: `.read()` for the whole file, `.readlines()` for a list of lines, or `for line in f:` for one line at a time. Default to the third unless the file is small.
- Lines from a file end in `\n`. Call `.strip()` before comparing or printing them.
- `csv.reader` and `csv.DictReader` handle commas-inside-quotes and other CSV quirks that a naive `.split(",")` botches. CSV values come in as strings; cast them.
- `json.dump` and `json.load` round-trip Python lists and dicts to disk through JSON files. Use `indent=2` for readability.
- `pathlib.Path` builds paths that work on any OS and offers `.read_text()` and `.write_text()` for one-shot work.

## Up next

Module 12 takes on regular expressions: the small, dense language inside Python's `re` module for matching patterns in text. The log files you just learned to open are where regex earns its keep, pulling IP addresses, timestamps, and error codes out of lines of text that have just enough structure to be parseable.

Now go work the exercises and mini-project for Module 11 in the curriculum doc. The expense tracker is where everything in this lecture has to fit together: opening, reading, writing, appending, CSV, paths, and the exception handling from Module 8, all in one program.
