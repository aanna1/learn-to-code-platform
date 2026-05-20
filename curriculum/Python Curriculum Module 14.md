# Module 14: Testing, Quality, and Where to Go Next

## Why this matters

You wrote a `square` function:

```python
def square(n):
    return n * n
```

You ran it. `square(2)` gave you `4`. `square(3)` gave you `9`. Looks good. You ship it.

Two weeks later, a colleague reports your function "doesn't work." They passed in `-5` and got `25` (correct, but they expected `-25`, because they misunderstood squaring). You explain. They move on. The next week, someone else passes in `"4"` (a string) and gets `"44"` (string repetition, which is what `*` does to strings and integers). That one's a real bug. You patch the function. In patching it, you accidentally break the negative-number case. Now `square(-5)` returns `5`. You ship the patch. The original colleague's code, which depended on `square(-5) == 25`, starts producing wrong results in a part of the codebase nobody's looked at for weeks.

This is the problem testing solves. Running your function once with a couple of inputs tells you it works *today*. A test suite tells you it still works *after every change you make for the rest of its life*. Every time you push a change, you re-run the tests; if anything you used to do correctly is now broken, the tests catch it before your colleague does.

This module also wraps up the curriculum. We'll cover testing, the style conventions that make Python code readable, and the paradigms you've already used without naming them. Then a tour of the libraries that will define the next chapter of your Python work, depending on where you're headed.

## What you'll be able to do by the end

- Use `assert` for quick sanity checks and explain when assertions are the wrong tool.
- Write a unit test in `unittest` with the arrange/act/assert pattern.
- Recognize `pytest`'s simpler syntax and run a test file with it.
- Apply PEP 8 conventions and use `black` and `ruff` to enforce style automatically.
- Identify procedural, object-oriented, and functional code in the wild, and use list/dict comprehensions and `lambda` confidently.
- Pick a credible next step (web, data, automation, ML, GUI) based on what you want to build.

## Prerequisites

Everything from Modules 1 through 13. Testing is where the rest of the curriculum gets used in anger, since you'll write tests for the functions and classes you defined earlier. Module 6 (functions), Module 8 (exceptions), and Module 13 (classes) are especially load-bearing here.

If you haven't done the capstone yet, you don't need to before reading this. The lecture stands on its own. The capstone is where you'll apply everything in one place, and the testing material here is what you'll lean on to know you've finished it.

## Core concepts

### Manual testing and why it stops scaling

Take the `square` function from above. The way most beginners "test" it is to run the program and eyeball the output:

```python
def square(n):
    return n * n

print(square(2))   # expect 4
print(square(3))   # expect 9
```

Run it. See `4` and `9`. Convince yourself it works. Move on.

A few problems. First, your eyes are checking the output, not the code; if you typo the expected value in the comment, you won't notice. Second, when you change `square` next month, will you remember to re-run this script? Probably not. Third, what about `square(0)`? `square(-5)`? `square(1.5)`? You tested two cases; there are infinite inputs.

The first upgrade is to stop printing and start asserting.

### `assert`: the simplest test

`assert` is a Python keyword. It takes a boolean expression. If the expression is true, nothing happens. If it's false, Python raises `AssertionError`.

```python
def square(n):
    return n * n

assert square(2) == 4
assert square(3) == 9
assert square(0) == 0
assert square(-5) == 25
```

Run it. If everything's right, the script ends silently. If something's wrong, you get a traceback pointing at the failing line. Add a message after the condition and you get more context when it fails:

```python
assert square(-5) == 25, f"square(-5) should be 25, got {square(-5)}"
```

This is already an enormous step up. You can re-run it any time. It checks behavior, not output. And it tests four cases instead of two.

But `assert` has limits. It's a single line, so it can't structure related tests into groups. When one fails, the script halts and you don't see whether the rest would have passed. And there's a sharp edge: Python's `-O` ("optimize") flag strips out `assert` statements at runtime, so anything you put in an `assert` that has side effects or that you depend on for correctness can silently vanish in production. Use `assert` for tests and sanity checks, never for control flow or input validation in real code.

### `unittest`: tests with structure

Python ships with a testing framework called `unittest`. It's built on the same `TestCase` class pattern Java's JUnit popularized, and it'll feel familiar if you've used a tested language before.

Suppose you've got a file `calculator.py`:

```python
def square(n):
    return n * n


def divide(a, b):
    return a / b
```

In a separate file `test_calculator.py`:

```python
import unittest
from calculator import square, divide


class TestCalculator(unittest.TestCase):
    def test_square_positive(self):
        self.assertEqual(square(3), 9)

    def test_square_zero(self):
        self.assertEqual(square(0), 0)

    def test_square_negative(self):
        self.assertEqual(square(-4), 16)

    def test_divide_basic(self):
        self.assertEqual(divide(10, 2), 5)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            divide(10, 0)


if __name__ == "__main__":
    unittest.main()
```

Run it with `python test_calculator.py`. You get output like:

```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.001s

OK
```

Each dot is a passing test. If something fails, you'd see an `F` instead, plus a detailed report of which assertion failed and what it got versus what it expected.

A few rules to internalize:

- The test class inherits from `unittest.TestCase`. That base class is what gives you `self.assertEqual`, `self.assertRaises`, and the other helpers.
- Method names that start with `test_` are auto-discovered as tests. Methods that don't start with `test_` are helpers, run only if you call them.
- Each test method should test one thing and have a name that describes that thing. `test_square_negative` tells you what's being checked. `test_1`, `test_other_case`, `test_stuff` don't.
- `self.assertRaises(ExpectedError)` used as a `with` block lets you check that the code inside raises a specific exception. Useful for testing error paths.

### Arrange, act, assert

A clean test has three phases. *Arrange* the inputs and any state. *Act*: call the function. *Assert*: check the result.

```python
def test_deposit_increases_balance(self):
    # Arrange
    account = BankAccount("Alice", balance=100)
    # Act
    account.deposit(50)
    # Assert
    self.assertEqual(account.balance, 150)
```

You won't always label the phases with comments, but they should be visually present. If a test crams all three together, or has multiple act/assert pairs, it's testing too much. Split it.

A common mistake is testing too many things in one test:

```python
def test_account(self):
    account = BankAccount("Alice", balance=100)
    account.deposit(50)
    self.assertEqual(account.balance, 150)
    account.withdraw(30)
    self.assertEqual(account.balance, 120)
    with self.assertRaises(InsufficientFundsError):
        account.withdraw(1000)
```

If `deposit` is broken, you never get to check `withdraw`. The test name doesn't tell you what failed. Split it into three: `test_deposit`, `test_withdraw`, `test_overdraw_raises`. When one fails, the others still run, and the name of the failing test tells you exactly which behavior is broken.

### `pytest`: less ceremony, same job

`unittest` is fine, but the community has largely shifted to `pytest`. Install it with `pip install pytest`. Then the same tests look like this:

```python
from calculator import square, divide
import pytest


def test_square_positive():
    assert square(3) == 9


def test_square_zero():
    assert square(0) == 0


def test_square_negative():
    assert square(-4) == 16


def test_divide_basic():
    assert divide(10, 2) == 5


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

No class, no `self`, no `assertEqual`. Just plain functions and plain `assert` statements. Run with `pytest` (or `python -m pytest`). When a test fails, `pytest` shows you the values on both sides of the assertion, not just "AssertionError":

```
>       assert square(-4) == 16
E       assert -16 == 16
E        +  where -16 = square(-4)
```

That's the kind of error message that pays for itself the first time you see it. The convention is the same as `unittest`: files named `test_*.py`, functions named `test_*`.

For this curriculum, either framework is fine. `pytest` is what you'll see in most real Python codebases. The capstone exercises use whichever you're comfortable with.

> **What could go wrong:** A test that doesn't check anything passes silently. `def test_foo(): pass` runs and reports success. So does `def test_foo(): square(2) == 4` (note the missing `assert`). That comparison runs, produces `True`, and gets thrown away. The test "passes" but checked nothing. If you ever see a suspiciously clean test run, double-check that each test ends in an `assert`.

### Test-driven development in one paragraph

Test-driven development (TDD) is the discipline of writing the test *first*, before the code. The cycle is:

1. Write a failing test for the behavior you want.
2. Run it. Confirm it fails (you haven't written the code yet).
3. Write the minimum code to make it pass.
4. Run again. Confirm it passes.
5. Refactor freely, re-run the tests to confirm you didn't break anything.

The discipline is harder than it sounds and worth trying for at least a week. Even when you don't strictly follow TDD, the habit of writing a test as soon as a function exists, rather than "later when I have time," is what separates code that survives change from code that doesn't.

**Try it.** Take the `current_streak` method from the capstone habit tracker (the answer key has the reference). Without looking at the test suite there, sketch out four tests that you'd want to run on it. Then check yours against the answer key.

<details>
<summary>Answer</summary>

The reference test suite covers six cases. The four most important:

1. A habit with no log entries has a streak of zero.
2. A habit marked done only today has a streak of one.
3. Three consecutive days produces a streak of three.
4. A gap in the middle breaks the streak.

If you also thought of the "old streak that's no longer current" case and the "duplicate marks on the same day" case, you've internalized the right instinct: think about boundaries and degenerate inputs, not just the happy path.

</details>

### What makes a good test

A few rules of thumb, learned through years of broken codebases:

- **Test behavior, not implementation.** `test_account_has_attribute_named_balance` is brittle; rename the attribute and the test fails for a reason that doesn't matter. `test_deposit_increases_reported_balance` tests the behavior callers care about.
- **One assertion per concept.** Some tests need multiple `assert` lines to check one concept (a class with multiple attributes, for example). That's fine. What's not fine is testing three unrelated behaviors in one test.
- **Tests should be fast.** Slow tests get skipped. If a test takes more than a second, ask whether it's doing too much.
- **Tests shouldn't depend on each other.** Each test sets up its own state. If `test_b` only passes when `test_a` ran first, you've got a fragile suite that breaks the moment someone runs the tests in a different order.
- **A test that has never failed is suspicious.** Write the test, then break the code on purpose to confirm the test catches the break. If it doesn't, the test wasn't testing what you thought.

### Code style: PEP 8, `black`, `ruff`

Python has an official style guide called PEP 8. It covers naming, spacing, line length, import ordering, and dozens of smaller decisions. Read it once, then never look at it again, because tools will enforce it for you.

`black` is an opinionated formatter. You run `black myfile.py` and it reformats the file in place to match a single canonical style. Tabs become spaces. Inconsistent quotes get normalized. Long lines get broken. You stop arguing about style because there's nothing to argue about; `black` decided.

`ruff` is a linter (and now also a formatter): a tool that reads your code and flags suspicious patterns, unused imports, undefined names, and stylistic violations. It's fast, written in Rust, and replaces a dozen older tools (`pylint`, `flake8`, `isort`, and others).

A common setup for a real project is `black` on save (formats automatically) and `ruff check` in your CI pipeline (catches issues before they merge). Neither tool is mandatory at the beginner stage, but learning to run them now will save you arguments with future colleagues.

Style aside, the names you pick matter more than any tool can enforce. `def get_data():` is meaningless. `def fetch_active_users():` tells you what the function does. `x` is fine for a loop counter. As a variable holding a user's email address, it's lazy. Read your code aloud; if a name forces you to also explain what it means, it's the wrong name.

### The Zen of Python

Try this at a Python prompt:

```python
import this
```

You'll see a short list of design principles for the language, written by Tim Peters. The full text:

```
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
...
```

It's a quick read. It won't make you a better programmer in one sitting. It will, over time, give you a vocabulary for why some Python code feels right and some doesn't.

### Paradigms you've already used

You've written code in three styles without naming them. Worth pinning down so you recognize them in the wild.

**Procedural** is the style of Modules 1-5. A program is a sequence of statements that the computer runs top to bottom. Functions group related statements, but the program's structure is the order in which things happen.

```python
def greet(name):
    print(f"Hello, {name}!")


name = input("Name: ")
greet(name)
```

**Object-oriented** is Module 13. Data and the operations on that data are bundled into classes. The program's structure is *what objects exist* and *what they can do*.

```python
class Greeter:
    def __init__(self, salutation):
        self.salutation = salutation

    def greet(self, name):
        print(f"{self.salutation}, {name}!")


g = Greeter("Hello")
g.greet("Alice")
```

**Functional** style emphasizes pure functions, immutable data, and treating functions as values you can pass around. You've used pieces of it: list comprehensions, `map`, `filter`. The fully functional version of "double every number in a list":

```python
numbers = [1, 2, 3, 4]
doubled = list(map(lambda n: n * 2, numbers))
print(doubled)   # [2, 4, 6, 8]
```

`map` takes a function and a list, applies the function to each element, and returns an iterator of results. `lambda n: n * 2` is an anonymous one-line function: takes `n`, returns `n * 2`. It's equivalent to:

```python
def double(n):
    return n * 2

doubled = list(map(double, numbers))
```

`filter` is the sibling that keeps only the elements for which a function returns true:

```python
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda n: n % 2 == 0, numbers))
print(evens)   # [2, 4, 6]
```

In Python, the same things read more idiomatically as comprehensions:

```python
doubled = [n * 2 for n in numbers]
evens = [n for n in numbers if n % 2 == 0]
```

Most Python programmers reach for a comprehension first. `map` and `filter` are fine; `lambda` is fine for one-line throwaways. When the lambda would be more than one line, give it a name with `def`.

Real Python codebases mix all three paradigms. A function-heavy data pipeline calls into a class-based ORM. A web framework uses classes for views and decorators (a functional idea) for routing. Pick the paradigm that fits the problem; don't apply one dogmatically.

**Try it.** Rewrite this loop as a list comprehension, then again with `filter` and `lambda`. Decide which version you find easiest to read.

```python
words = ["apple", "banana", "kiwi", "grape", "fig"]
short_words = []
for w in words:
    if len(w) <= 4:
        short_words.append(w)
```

<details>
<summary>Answer</summary>

```python
# Comprehension
short_words = [w for w in words if len(w) <= 4]

# filter + lambda
short_words = list(filter(lambda w: len(w) <= 4, words))
```

Most Python readers will prefer the comprehension; it reads almost like English ("w for w in words if len of w is at most four"). The `filter` version is fine but feels heavier for one of the language's most common operations.

</details>

### The `if __name__ == "__main__":` idiom

You'll see this at the bottom of well-organized Python files:

```python
def main():
    # the actual program
    ...


if __name__ == "__main__":
    main()
```

Here's what it means. Every Python file has a built-in variable called `__name__`. When you *run* a file directly with `python myfile.py`, Python sets `__name__` to the string `"__main__"`. When you *import* the file from another file, Python sets `__name__` to the module's name (in this case, `"myfile"`).

So `if __name__ == "__main__":` is a way of saying "run this block only when this file is the entry point, not when it's imported." The benefit: your test file can `from calculator import square` without accidentally triggering `calculator.py`'s main program. Get in the habit of putting your script's entry point inside a `main()` function and guarding it with this pattern.

### Where to go next

You've covered the fundamentals. From here, the language splits by what you want to build.

**Web.** Three frameworks dominate. *Flask* is small and great for learning; you can have a working web server in ten lines. *FastAPI* is the modern choice for JSON APIs; it leans hard on type hints and is fast. *Django* is the all-in-one for full-stack web apps with databases, admin panels, and authentication built in.

**Data.** *pandas* is the workhorse for tabular data; think of it as a programmable spreadsheet. *NumPy* is the foundation under pandas and provides fast numerical arrays. *matplotlib* and *seaborn* are for plotting. Together they're what most data scientists use day to day.

**Automation.** *Selenium* and *Playwright* drive web browsers programmatically (filling forms, scraping pages that need JavaScript). The standard-library *subprocess* module runs shell commands and external programs. *schedule* and *APScheduler* run jobs on a timer. For sysadmin work, *Ansible* uses Python under the hood.

**Machine learning.** *scikit-learn* is the entry point: classical algorithms (regression, decision trees, clustering) with a consistent API. *PyTorch* and *TensorFlow* are the deep-learning frameworks, and *PyTorch* has become the default in research. *Hugging Face's `transformers`* library is where most language-model work happens.

**GUIs.** *Tkinter* ships with Python and is enough for small desktop tools. *PyQt* and *PySide* are heavier and produce more polished native-feeling apps. For modern cross-platform desktop work, many developers also reach for *Electron* (JavaScript-based) or web-based UIs over native GUI toolkits.

**Security and systems.** Worth mentioning given the cybersecurity context: *Scapy* for packet manipulation, *paramiko* for SSH automation, *cryptography* for, well, cryptography, and *yara-python* for malware classification. Most security tools you'll meet in industry are Python-friendly.

Pick one, build something with it, and the next one becomes easier. The skill you've built in this curriculum (read the docs, write small experiments, debug from error messages, test your work) transfers to every library.

## Common pitfalls

**1. Using `assert` for input validation in real code.**

```python
def divide(a, b):
    assert b != 0, "b must not be zero"
    return a / b
```

Run that with `python -O divide.py` (the optimize flag) and the `assert` vanishes. Now your code happily attempts to divide by zero. Use `if b == 0: raise ValueError(...)` for runtime checks. `assert` is for tests and developer sanity checks.

**2. Writing tests that always pass because they don't assert.**

```python
def test_square(self):
    square(2) == 4   # missing self.assertEqual
```

The expression `square(2) == 4` evaluates to `True` and is thrown away. The test "passes" but checks nothing. Always end with an `assert` (or `self.assertEqual` / `self.assertTrue` in `unittest`).

**3. Tests that depend on each other.**

```python
class TestStuff(unittest.TestCase):
    def test_create(self):
        self.account = BankAccount("Alice", 100)
        self.assertEqual(self.account.balance, 100)

    def test_deposit(self):
        self.account.deposit(50)   # AttributeError if test_create didn't run
        self.assertEqual(self.account.balance, 150)
```

`unittest` doesn't guarantee tests run in the order you wrote them. Each test should set up its own state, often in a `setUp` method that runs before each test.

```python
class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = BankAccount("Alice", 100)

    def test_deposit(self):
        self.account.deposit(50)
        self.assertEqual(self.account.balance, 150)
```

**4. Bare `except:` blocks.**

```python
try:
    risky_thing()
except:
    pass   # swallows everything, including KeyboardInterrupt
```

A bare `except` catches every exception, including `KeyboardInterrupt` (Ctrl-C) and `SystemExit`. Now your program can't even be stopped. Always name the exception you mean to catch, or at least use `except Exception:` to leave the system-level exceptions alone.

**5. Lambdas that should have names.**

```python
sort_key = lambda x: x["created_at"]
records.sort(key=sort_key)
```

If you're assigning a lambda to a variable, just use `def`:

```python
def sort_key(x):
    return x["created_at"]

records.sort(key=sort_key)
```

You get a proper name in tracebacks and the option to add a docstring later. `lambda` is for *one-shot* anonymous functions, especially as arguments to other functions.

**6. Forgetting that style tools won't catch logic bugs.**

`black`-formatted code looks clean. `ruff`-passing code is free of common smells. Neither tool checks whether your code is *correct*. Tests are the only thing that does that. Run both, but don't mistake style cleanliness for correctness.

## How this connects

This module is where the curriculum's threads tie off. Module 6's functions become testable units. Module 8's exceptions become things tests check for (`assertRaises`). Module 11's file I/O becomes something tests have to work around (often by using temporary directories). Module 13's classes become natural test boundaries: one test class per real class, one method per behavior.

Looking forward, every direction you take from here builds on these habits. Web frameworks have their own test conventions (Flask's `test_client`, Django's `TestCase`, FastAPI's `TestClient`); they're variations on the same arrange-act-assert pattern. Data work in pandas tests data *contracts* (no nulls in this column, this range fits in memory) instead of unit-level behavior, but the discipline is the same. Production ML pipelines test that models stay within accuracy thresholds across training runs. The framework changes; the habit doesn't.

## Recap

- Manual testing (eyeballing output) stops working as your code grows. Automated tests check behavior on every change, catching regressions before users do.
- `assert` is the simplest test. Use it for sanity checks. Never use it for input validation in real code; the `-O` flag strips it out.
- `unittest` ships with Python: test classes inherit from `TestCase`, methods named `test_*` get auto-discovered, helpers like `assertEqual` and `assertRaises` make checks readable.
- `pytest` is what most real codebases use: plain functions, plain `assert`, better error output. Install with `pip install pytest`.
- A test follows arrange/act/assert and checks one behavior. Tests should be fast, independent, and named after what they verify.
- PEP 8 defines Python's style. `black` formats your code to match. `ruff` flags issues. Use them; they're free.
- The three paradigms you've used: procedural (modules 1-5), object-oriented (module 13), and functional (`map`, `filter`, `lambda`, comprehensions). Most real code mixes all three.
- `if __name__ == "__main__":` lets a file act as both a script and an importable module. Get in the habit.
- Where to go next depends on what you want to build: web (Flask/FastAPI/Django), data (pandas/NumPy), automation (Selenium/Playwright), ML (scikit-learn/PyTorch), GUIs (Tkinter/PyQt), or security (Scapy/paramiko/cryptography).

## Up next

There is no Module 15. You've finished the fundamentals. The capstone is where the curriculum ends and the rest of your Python life begins: pick one of the four project options, build it end to end, write tests for the non-trivial parts, format with `black`, lint with `ruff`, and write a README that lets a stranger run it. When that's done, you're not a beginner anymore.

Now go build something that didn't exist this morning.
