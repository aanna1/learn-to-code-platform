# Module 9: Exceptions and Defensive Coding

## Why this matters

Every program you've written so far has assumed the world is well-behaved. The user types a number when you ask for one. The file you open exists. The list you index into has enough items. The dictionary has the key you want.

Run any of those programs against a real human for thirty seconds and they'll crash. Watch:

```python
age = int(input("Age: "))
```

You ask for an age. They type "twenty-five." Python raises `ValueError: invalid literal for int() with base 10: 'twenty-five'`, your program ends mid-conversation, and whatever else you were going to do (compute their birth year, look up their record, send a confirmation) never happens. The user sees a wall of red text and concludes your software is broken.

The frustrating thing is that *you knew* this could happen. You had no way to handle it. So far, every error has been a wall: the program hits it and stops. This module gives you the tool to wrap a piece of risky code, catch the failure, and decide what to do next. The same tool also lets you signal failures of your own when something is wrong with the inputs to your functions.

Defensive coding isn't about anticipating every possible disaster. Code that tries to handle every edge case ends up unreadable, and worse, hides real bugs by silently swallowing them. The trick is to handle the failures you expect (bad user input, missing files, network hiccups) and let the unexpected ones propagate so you find them. We'll spend most of the module on telling those two apart.

## What you'll be able to do by the end

- Read a Python traceback and identify what failed, where, and why.
- Wrap risky code in `try` / `except` to catch specific failure types.
- Pick the right exception class to catch and explain why bare `except:` is a trap.
- Use `else` and `finally` for the "ran cleanly" and "always run" cases.
- Raise your own exceptions when input violates a function's preconditions.
- Write an input-validation loop that keeps prompting until the input is usable.
- Recognize the EAFP style ("ask forgiveness, not permission") that Python culture prefers.

## Prerequisites

Solid grasp of functions (Module 6), loops with `break`/`continue` (Module 5), and dictionaries (Module 8) is enough. The chapter leans on `int()`, `input()`, and file opening, all of which you've used before. We'll touch files briefly as a preview of Module 11 but won't go deep.

## Core concepts

### What an exception actually is

An exception is an event Python raises when it can't continue. The interpreter stops what it was doing, walks back up through whatever called it, and looks for code that's prepared to handle that kind of failure. If nothing handles it, the program crashes and prints a traceback.

Watch a traceback up close:

```python
def compute_average(numbers):
    return sum(numbers) / len(numbers)

result = compute_average([])
print(result)
```

Run that and you get:

```
Traceback (most recent call last):
  File "avg.py", line 4, in <module>
    result = compute_average([])
  File "avg.py", line 2, in compute_average
    return sum(numbers) / len(numbers)
ZeroDivisionError: division by zero
```

Read it from the bottom up. The actual error: `ZeroDivisionError: division by zero`. Where it happened: line 2, inside `compute_average`. How it got there: from line 4, where you called `compute_average([])`. The empty list had length zero, so the division blew up.

Most error messages tell you exactly what's wrong if you read them carefully. Newer programmers tend to skim and panic. Slow down and read the last line first. It almost always names the problem.

### The exceptions you'll meet first

A short list of the common ones, with the kind of code that causes each:

- **`ValueError`**: wrong value for the right type. `int("twenty")` is the textbook case.
- **`TypeError`**: wrong type entirely. `"3" + 5` (you can't add a string and a number).
- **`ZeroDivisionError`**: division (or modulo) by zero.
- **`IndexError`**: list index out of range. `[1, 2, 3][5]`.
- **`KeyError`**: dictionary key doesn't exist. `{"a": 1}["b"]`.
- **`FileNotFoundError`**: opening a file that isn't there.
- **`AttributeError`**: calling a method or accessing an attribute the object doesn't have. `"hello".doesnt_exist()`.
- **`NameError`**: using a variable that's never been defined.
- **`IndentationError`** / **`SyntaxError`**: these happen *before* the program runs, so you can't catch them. They're Python rejecting your source code.

You don't need to memorize all of them. You need to recognize them by name when they come up so you can google them effectively.

### `try` and `except`: the basics

The shape:

```python
try:
    # risky code
except SomeSpecificError:
    # what to do if it failed
```

Concretely:

```python
try:
    age = int(input("Age: "))
    print(f"Next year you'll be {age + 1}")
except ValueError:
    print("That wasn't a number.")
```

What's happening: Python runs the body of `try`. If `int(input(...))` raises a `ValueError`, control jumps to the `except` block. If no exception is raised, the `except` block is skipped.

A few questions you might have.

**Does the `try` block stop the moment an exception fires, or does it finish?** It stops. The instant `int()` raises `ValueError`, the `print` line below it never runs. Control jumps straight to `except`.

**Can I have multiple `except` clauses?** Yes, one per exception type:

```python
try:
    a = float(input("Numerator: "))
    b = float(input("Denominator: "))
    print(a / b)
except ValueError:
    print("Both inputs must be numbers.")
except ZeroDivisionError:
    print("Can't divide by zero.")
```

If `float()` fails, `ValueError` handler runs. If the division fails because `b` is zero, `ZeroDivisionError` handler runs. Only one of them fires per pass through the `try`.

**Can one `except` catch multiple types?** Yes, with a tuple:

```python
try:
    do_stuff()
except (ValueError, TypeError):
    print("Bad input.")
```

This is fine when the recovery is the same for both. If you'd handle them differently, use two separate clauses.

### What goes wrong without `try`: the naïve version

Here's the kind of bug that makes new programmers reach for `try` too aggressively. The grade calculator from Module 4:

```python
score = int(input("Score: "))
if score >= 90:
    print("A")
elif score >= 80:
    print("B")
else:
    print("Below B")
```

The user types "ninety." Crash. So you wrap it:

```python
try:
    score = int(input("Score: "))
except ValueError:
    print("That wasn't a number.")

if score >= 90:
    print("A")
```

Now the user types "ninety" and you get a *different* crash:

```
NameError: name 'score' is not defined
```

What happened? The `try` block raised before `score` got assigned. The `except` block printed a message but didn't assign `score` either. Then the code below tried to use `score`, which doesn't exist.

The fix is to put the *whole* dependent computation inside the loop, and keep retrying until the input is good:

```python
while True:
    try:
        score = int(input("Score: "))
        break
    except ValueError:
        print("That wasn't a number. Try again.")

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
else:
    print("Below B")
```

`while True:` keeps prompting. The `try` succeeds, `break` exits the loop, and `score` is now defined. If the `try` fails, the `except` runs, the loop goes around again. This input-validation pattern is one of the most common shapes of real Python code. Memorize it.

**Try it:** Predict what this prints if the user types "abc" the first time and "5" the second.

```python
while True:
    try:
        n = int(input("Number: "))
        break
    except ValueError:
        print("Try again.")
print(n * 2)
```

<details>
<summary>Answer</summary>

```
Number: abc
Try again.
Number: 5
10
```

First iteration: `int("abc")` raises, `Try again.` prints, the loop goes back. Second iteration: `int("5")` succeeds, `break` exits the loop, `print(n * 2)` runs.

</details>

### The bare-`except` trap

A tempting pattern, especially for beginners who just want the crashes to stop:

```python
try:
    do_something_risky()
except:
    print("Something went wrong.")
```

Don't. A bare `except:` catches *every* exception, including ones it has no business catching. Worst offender: `KeyboardInterrupt`, which is what Python raises when the user hits Ctrl+C. With a bare `except`, your program can't be cleanly stopped because every Ctrl+C gets swallowed by your "something went wrong" handler.

Worse: a bare `except` will catch your own bugs. Typos in variable names raise `NameError`. Calling a method that doesn't exist raises `AttributeError`. Forgetting an import raises `NameError`. If you're swallowing those, your program will run "successfully" while producing wrong answers, which is the kind of bug you spend days hunting down.

So: catch only what you're prepared to handle. If the user's input might be bad, catch `ValueError`. If a file might be missing, catch `FileNotFoundError`. Let unknown exceptions propagate. They're trying to tell you something.

The narrow legitimate use is logging-and-reraising in a top-level handler:

```python
try:
    main()
except Exception as e:
    log_to_file(e)
    raise
```

Even there, `except Exception:` is preferred over bare `except:` because `Exception` doesn't catch `KeyboardInterrupt` or `SystemExit`. The `raise` at the end re-raises the exception after logging, so the program still crashes and you can see the traceback. You're not silencing the error; you're observing it on its way out.

That's the curriculum's checkpoint, by the way. *When is bare `except:` appropriate?* Almost never. When you think you need it, you actually want `except Exception:` plus a `raise` at the end.

### Capturing the exception with `as`

You can grab the exception object itself and use it:

```python
try:
    int("not a number")
except ValueError as e:
    print(f"Couldn't parse: {e}")
```

`e` is the exception object. Printing it gives you the message Python attached to it. This is useful when you want to log the specific failure or include it in a user-facing message:

```
Couldn't parse: invalid literal for int() with base 10: 'not a number'
```

### `else` and `finally`

`try` blocks have two more optional parts.

`else` runs only if the `try` block succeeded with no exception. Why bother, when you could just put more code at the end of `try`? Because `else` is *not* covered by the `except` clauses. Code in `else` that fails will not be caught by the same handler:

```python
try:
    n = int(input("Number: "))
except ValueError:
    print("Not a number.")
else:
    print(f"Square: {n ** 2}")
```

Read that as "if parsing the input worked, compute the square." If `int()` raises, `else` is skipped. If you'd put `print(n ** 2)` inside the `try` instead, an unrelated `TypeError` during the squaring would get caught by your `except ValueError:` clause, which is wrong. `else` keeps the success path separate from the risky-parse path.

`finally` runs always, exception or not, return-statement or not. It's for cleanup that must happen no matter what:

```python
def read_user_data(filename):
    f = open(filename)
    try:
        return f.read()
    finally:
        f.close()
```

The `return` inside `try` looks like it should exit the function and skip the `finally`. It doesn't. Python runs the `finally` block first, *then* completes the return. The file gets closed whether the read succeeded or raised.

In practice you almost never write this exact pattern for files, because the `with` statement (Module 11) handles it more cleanly. But `finally` exists for cases where you've acquired a resource (a file, a network connection, a database transaction) and need to release it regardless of what happens.

### Raising your own exceptions

Catching isn't the only use of exceptions. You can also raise them, which is how you signal that something is wrong with what your caller asked you to do.

```python
def withdraw(balance, amount):
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if amount > balance:
        raise ValueError(f"insufficient funds: {balance} < {amount}")
    return balance - amount
```

Watch this from the caller's side:

```python
try:
    new_balance = withdraw(100, 150)
except ValueError as e:
    print(f"Couldn't withdraw: {e}")
```

```
Couldn't withdraw: insufficient funds: 100 < 150
```

Why is `raise` better than just returning a sentinel like `None` or `-1`?

Three reasons. First, return values can be ignored; exceptions can't. If your caller forgets to check `result == -1`, the bad value silently propagates. An uncaught exception crashes loudly. Second, exceptions carry a message, so the failure mode is self-describing. Third, exceptions cross function boundaries cleanly. A function eight levels deep can raise, and the top-level caller can catch it. Returning sentinels means every level in between has to check and forward the error manually.

The rule of thumb: if a function can't do its job because of bad inputs or unmet preconditions, raise. Don't return `None` and hope the caller notices.

**What could go wrong:** `raise ValueError("...")` is a function call. Don't forget the parentheses:

```python
raise ValueError       # this is not raising. it's referencing the class.
```

Actually that *does* raise, because Python is permissive about it. But the version with parentheses lets you attach a message, and is what people expect to see.

### LBYL vs. EAFP

Two philosophies for handling things that might fail.

**LBYL** is "Look Before You Leap." Check whether the operation is going to work, then do it.

```python
if "city" in person:
    print(person["city"])
else:
    print("no city on file")
```

**EAFP** is "Easier to Ask Forgiveness than Permission." Just try the operation; handle the failure.

```python
try:
    print(person["city"])
except KeyError:
    print("no city on file")
```

Both work. Both produce the same output. Python culture leans EAFP, and the reason is subtle: the LBYL version has a *race condition* baked in. Consider opening a file:

```python
import os
if os.path.exists(filename):
    f = open(filename)        # might still fail!
```

Between the `os.path.exists` check and the `open` call, another process could delete the file. Your "safe" check guaranteed nothing. The EAFP version doesn't have this problem:

```python
try:
    f = open(filename)
except FileNotFoundError:
    print("not there")
```

You don't check first. You just try. If the file vanished a microsecond before you opened it, you handle the same exception you would have handled if it never existed.

This isn't just about race conditions. EAFP also tends to produce less duplicated logic. The LBYL `if "city" in person:` and the dictionary lookup both have to know about the same key. The EAFP version mentions the key once. For a single check, the difference is trivial; in a deeply nested structure, it matters more.

That said, LBYL is fine for simple, fast checks where there's no concurrency: dictionary keys, list bounds, "is this number positive." Pick whichever is more readable for the situation. Just know that Pythonistas reach for `try` more often than other languages would.

### Don't use exceptions for control flow

A counterweight to the EAFP enthusiasm: exceptions should describe *exceptional* situations, not the normal control flow of your program.

```python
# bad: using exceptions to stop a loop
def first_negative(numbers):
    try:
        for n in numbers:
            if n < 0:
                raise StopIteration
    except StopIteration:
        return n
```

That works, but it's weird. The normal "found what I wanted, stop now" mechanism is `return` or `break`. Using `raise`/`except` here makes the code harder to read for no benefit. Exceptions are for *unexpected* events, not for replacing `if` and `return`.

Rough rule: if the situation is something a function's caller would routinely cause, return a value indicating it. If the situation is something that means the function couldn't do its job at all, raise.

## Common pitfalls

1. **Bare `except:`.** Catches everything including Ctrl+C and your own bugs. Use a specific exception class. If you really need a catch-all, use `except Exception:` and re-raise after logging.

2. **`try` block too big.** Wrapping fifty lines in one `try` makes it impossible to tell which line you were guarding against. Keep `try` blocks short. Ideally, one or two operations. Move setup and post-processing outside.

3. **Using the variable from a failed `try`.** If the `try` block didn't finish, the variables it tried to assign aren't defined. Either retry until success (the `while True:` pattern) or use a default value.

4. **Catching too much and swallowing it.** `except Exception: pass` is the second-worst thing you can write in Python (after bare `except: pass`). It silently eats every error. If you genuinely don't care about the error, at least log it. Usually you do care.

5. **Forgetting that exceptions cross function boundaries.** If function `a` calls function `b` calls function `c`, and `c` raises, the exception travels back up through `b` and `a` until something catches it (or nothing does and the program crashes). You don't need to catch in every function; catch at the level where you actually have enough context to recover.

6. **Using exceptions as flow control.** Don't `raise` to break out of a loop. Use `break`. Don't `raise` to return early. Use `return`. Exceptions are for genuinely exceptional situations.

## Try it yourself

**Problem 1.** What does this code print? Walk through it before running.

```python
def parse_count(s):
    try:
        n = int(s)
    except ValueError:
        return -1
    else:
        return n

print(parse_count("42"))
print(parse_count("forty-two"))
print(parse_count("3.14"))
```

<details>
<summary>Answer</summary>

```
42
-1
-1
```

`"42"` parses cleanly, no exception, `else` runs and returns 42. `"forty-two"` raises `ValueError`, caught, returns -1. `"3.14"` also raises `ValueError` (because `int()` rejects strings with decimal points, even though `float()` would accept them), caught, returns -1.

That last one is the kind of thing the lecture warned about. `int("3.14")` does not silently truncate. If you want truncation, you'd do `int(float("3.14"))`, which gives 3.

</details>

**Problem 2.** Write a function `safe_divide(a, b)` that returns `a / b` if it can, and returns the string `"undefined"` if `b` is zero. Don't check `b == 0` directly. Use `try` / `except`.

<details>
<summary>Answer</summary>

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "undefined"

print(safe_divide(10, 2))    # 5.0
print(safe_divide(10, 0))    # undefined
```

This is the EAFP version. The LBYL version (`if b == 0: return "undefined"`) is also fine here because there's no race condition. Use whichever you find clearer.

</details>

**Problem 3.** Write `prompt_int(message, low, high)` that prompts the user with `message`, keeps reprompting until they enter an integer in `[low, high]`, and returns it. Handle non-numeric input *and* out-of-range numbers.

<details>
<summary>Answer</summary>

```python
def prompt_int(message, low, high):
    while True:
        try:
            value = int(input(message))
        except ValueError:
            print("Please enter a whole number.")
            continue
        if value < low or value > high:
            print(f"Must be between {low} and {high}.")
            continue
        return value
```

Two layers. The `try` catches the parse failure. The range check, *outside* the `try`, catches the out-of-range case. Both use `continue` to loop back to the prompt. `return` exits the loop only when both conditions are satisfied.

You could put the range check inside the `try` too. The result is the same; the structure is slightly less clear because two unrelated failure modes are tangled together.

</details>

## How this connects

Exceptions are the connective tissue between the modules you've already learned and the messy real world coming up:

- **Module 10 (standard library)** introduces modules whose functions raise exceptions you'll need to handle. `json.loads` raises `JSONDecodeError`. `requests` raises `ConnectionError`. The vocabulary you built in this module is the vocabulary for handling those.
- **Module 11 (files and JSON)** is where exceptions earn their keep daily. Files might not exist (`FileNotFoundError`), might not be readable (`PermissionError`), might contain malformed data (`UnicodeDecodeError`, `JSONDecodeError`). The `with` statement also shows up there, and it's basically `try`/`finally` with friendlier syntax.
- **Module 13 (object-oriented programming)** lets you define your own exception classes by inheriting from `Exception`. Code like `class InsufficientFunds(Exception): pass` gives your application its own custom failure types.
- **Module 14 (testing)** is where you write tests that *expect* exceptions. `pytest.raises(ValueError)` lets you assert that a function raises the right exception on the right input.

For now, the goal is to make your existing programs survive contact with real users. Take the dice game from Module 6, the to-do list from Module 7, the phone book from Module 8, and wrap their input prompts in the validation pattern. That's how you find out where your code was secretly fragile.

## Recap

- An exception is an event Python raises when it can't continue. Uncaught, it crashes the program and prints a traceback.
- Read tracebacks bottom-up: the last line names the failure, the lines above show where it came from.
- Wrap risky code in `try` / `except SpecificError:`. Skip the bare `except:`. It catches Ctrl+C and your own bugs.
- The input-validation loop is `while True:` + `try` + `break` on success.
- `else` runs only if `try` succeeded. `finally` runs always.
- `raise ValueError("message")` signals a failure from your own code. Use it when a function can't do its job because of bad inputs.
- Python culture prefers EAFP ("try and catch") over LBYL ("check and then act"). Use whichever is clearer, but reach for `try` more often than you would in other languages.
- Don't use exceptions for normal control flow. They're for exceptional situations, not for replacing `break` and `return`.
- `except Exception:` catches almost everything but spares `KeyboardInterrupt` and `SystemExit`. That's the right pattern for top-level catch-and-log handlers.

## Up next

Module 10 is the standard library tour: `random`, `datetime`, `json`, `pathlib`, and friends. You'll stop reinventing functions Python already ships with, and start writing real scripts that fetch data, parse it, and save it back. Many of those library functions raise exceptions, so the habits from this module come along for the ride.

Now go work the exercises and mini-project for Module 9 in the curriculum doc. The grade calculator and divider exercises drill the `while True` / `try` / `break` pattern. The dice game rewrite is where you'll write a reusable validation helper (`get_int(prompt, low, high)`) and watch how much cleaner the main script gets when bulletproof input is one function call away.
