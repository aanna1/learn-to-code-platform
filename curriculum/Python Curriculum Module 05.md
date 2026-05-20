# Module 5: Loops

## Why this matters

Suppose you want to print the numbers 1 through 5. You could write five `print` statements:

```python
print(1)
print(2)
print(3)
print(4)
print(5)
```

Annoying, but tolerable. Now print 1 through 100. Or 1 through 10,000. Or the contents of a file you haven't seen yet, which might have one line or might have a million. Or every character in whatever string the user typed. The copy-paste approach doesn't scale, and more importantly, it doesn't work at all when you don't know how many times to repeat.

Loops are how you tell the computer "do this thing again." They're the second of the two universal control-flow tools — conditionals were the first. Conditionals let your code branch based on what it sees; loops let your code repeat itself. Put those two together and you can write essentially any algorithm.

What goes wrong without loops? You can't read a file of unknown length. You can't iterate over a user's input. You can't keep asking for a guess until they get it right. You can't compute a running total over a list. You can't validate every character in a password. You're stuck writing programs where everything you need to do is enumerated by hand at the time you write the code. That's almost never how the real world works.

A note on what loops introduce. They're the first construct in this curriculum that can actually crash your terminal — an infinite loop runs forever, eats CPU, and won't stop until you kill it. We'll cover how. Don't let it scare you off. Everyone writes their first infinite loop within ten minutes of learning loops, and that's fine.

## What you'll be able to do by the end

- Write a `while` loop with a clear exit condition, and recognize the most common infinite-loop bugs.
- Write a `for` loop over a string, a range, or a list.
- Use `range(stop)`, `range(start, stop)`, and `range(start, stop, step)` correctly.
- Use `break` to exit a loop early and `continue` to skip to the next iteration.
- Read and write nested loops, with rough intuition for how the work grows.
- Use the `else` clause on a loop and explain when it actually runs.

## Prerequisites

Everything from Modules 1 through 4. You need to be solid on conditionals especially — every loop has a condition that decides whether to keep going, and that condition is the same kind of expression you wrote in Module 4. If `if`, `elif`, `else`, and truthy/falsy aren't reflexive yet, go back. You'll fight every loop in this module otherwise.

## Core concepts

### `while` loops

A `while` loop runs a block of code over and over as long as some condition stays true. Syntactically, it looks just like an `if`:

```python
count = 1
while count <= 5:
    print(count)
    count += 1
```

That prints 1, 2, 3, 4, 5 and then stops.

Let's walk through it. Python checks the condition (`count <= 5`). True. Runs the block: prints `1`, then `count += 1` makes count `2`. Goes back to the top, checks the condition again. Still true. Prints `2`, count becomes `3`. And so on. When count reaches `6`, the condition is finally false, and Python skips past the loop entirely.

Three pieces have to be there for any `while` loop to work:

1. **An initialization** — `count = 1` before the loop. The variable being tested has to exist before you test it.
2. **A condition** — `count <= 5`. Anything that produces a boolean.
3. **A change inside the loop body** — `count += 1`. Something that moves the variable toward making the condition false. Without this, the loop runs forever.

Forget the change, and:

```python
count = 1
while count <= 5:
    print(count)
# missing: count += 1
```

This is the canonical *infinite loop*. It prints `1` forever. `count` never changes, the condition is never false, and the only way out is to kill the program — `Ctrl+C` in your terminal. Get used to that keystroke; you'll need it.

You can write an intentional infinite loop too. Sometimes you want one, especially when the exit happens via `break` (coming up):

```python
while True:
    answer = input("Type 'quit' to exit: ")
    if answer == "quit":
        break
```

`while True` reads as "loop forever." The exit isn't the condition; it's the `break` statement inside. This is a common Python idiom for "keep asking until the user gives a valid answer."

`+= 1` is shorthand for `count = count + 1`. Python has the same shortcut for the other arithmetic operators: `-=`, `*=`, `/=`, `//=`, `%=`, `**=`. They all mean "do this operation and reassign."

```python
total = 0
total += 5   # total is now 5
total *= 2   # total is now 10
total -= 3   # total is now 7
```

#### A practical `while` example

Sum the numbers from 1 to 100, using `while`:

```python
total = 0
n = 1
while n <= 100:
    total += n
    n += 1
print(total)   # 5050
```

Walk through what's happening. `total` starts at 0. `n` starts at 1. Each pass through the loop adds the current `n` to `total`, then advances `n`. After the loop, `total` holds the sum.

This works. It's also the kind of thing `for` does more cleanly, which is the next section.

### `for` loops

A `for` loop iterates over a *sequence* — a string, a list, a range — and gives you each element in turn. You don't have to manage a counter; the loop does it for you.

```python
for char in "hello":
    print(char)
```

Output:

```
h
e
l
l
o
```

The variable `char` takes on each character in `"hello"` in turn. The loop body runs five times — once per character. When the sequence is exhausted, the loop ends.

The variable name (`char` here) is yours to pick. Use whatever describes the items:

```python
for letter in "Python":
    print(letter)

for fruit in ["apple", "banana", "cherry"]:
    print(fruit)
```

The second example uses a *list* — we'll cover those properly in Module 7, but the iteration syntax is identical: `for thing in sequence`.

#### `range()` — iterating over numbers

Most loops over numbers use `range()`, a built-in function that generates a sequence of integers without storing them all in memory at once.

```python
for i in range(5):
    print(i)
```

Output:

```
0
1
2
3
4
```

Look at what's there and what isn't. `range(5)` produces 0, 1, 2, 3, 4 — five values, but starting at 0, not 1, and stopping *before* 5, not at it. The `5` is exclusive, same as with slicing back in Module 3.

This causes about a third of all off-by-one errors in Python. If you want 1 through 5 inclusive, you have to write `range(1, 6)`:

```python
for i in range(1, 6):
    print(i)        # 1 2 3 4 5
```

`range(start, stop)` gives you start through stop minus 1. Inclusive lower bound, exclusive upper bound. Mathematicians call this a *half-open interval* — it's the same convention slicing uses, and it's the same convention Python uses everywhere. Once you internalize "the stop is exclusive," you stop fighting it.

A third argument adds a step:

```python
for i in range(0, 11, 2):
    print(i)        # 0 2 4 6 8 10

for i in range(10, 0, -1):
    print(i)        # 10 9 8 7 6 5 4 3 2 1
```

A negative step counts down. Use it for countdowns, reverse iteration, anything that goes backward.

Want to redo the 1-to-100 sum from earlier with `for`?

```python
total = 0
for n in range(1, 101):
    total += n
print(total)   # 5050
```

Same answer, less bookkeeping. No initial `n = 1`, no `n += 1` inside, no off-by-one risk. This is the typical pattern: when you know exactly how many times to loop, `for range(...)` is cleaner than `while`. When the number of iterations depends on something happening inside the loop (user input, file content, search results), `while` is usually the right shape.

#### Iterating with the index

What if you need both the index and the value? Two options. The clumsy way:

```python
words = ["apple", "banana", "cherry"]
for i in range(len(words)):
    print(f"{i}: {words[i]}")
```

That works. It's also a tell that you're new to Python. The clean way uses `enumerate()`:

```python
words = ["apple", "banana", "cherry"]
for i, word in enumerate(words):
    print(f"{i}: {word}")
```

`enumerate(seq)` pairs each element with its index. You assign both at once: `for i, word in enumerate(words)`. Output:

```
0: apple
1: banana
2: cherry
```

Use `enumerate` whenever you find yourself reaching for `range(len(...))`.

**Try it:** Predict what each of these prints. Then run them.

```python
# A
for i in range(3):
    print(i)

# B
for i in range(1, 4):
    print(i)

# C
for i in range(10, 0, -2):
    print(i)
```

<details>
<summary>Answer</summary>

**A:** `0 1 2` (three values, starting at 0, stopping before 3)

**B:** `1 2 3` (start at 1, stop before 4)

**C:** `10 8 6 4 2` (start at 10, count down by 2, stop before 0)

If you predicted C as `10 8 6 4 2 0`, you fell into the "stop is exclusive" trap. `0` is the stop value; it's not included. If you wanted to include 0, you'd write `range(10, -1, -2)`.

</details>

### `break` and `continue`

Sometimes you want to bail out of a loop early, or skip the rest of one iteration and move on. `break` and `continue` are the two tools for that.

`break` exits the loop immediately. Nothing after `break` in the loop body runs; the loop is done.

```python
for n in range(1, 11):
    if n == 6:
        break
    print(n)
# prints 1 2 3 4 5
```

Once `n` reaches 6, `break` fires, and Python jumps to the line after the loop. The numbers 7 through 10 never print.

`continue` skips the rest of the current iteration and jumps back to the top of the loop for the next one.

```python
for n in range(1, 11):
    if n % 2 == 0:
        continue
    print(n)
# prints 1 3 5 7 9 — even numbers are skipped
```

When `n` is even, `continue` fires, and Python goes back to grab the next value of `n` without running `print(n)`. So only odd numbers make it through.

A real-world use of `break`. The "keep asking until valid" pattern:

```python
while True:
    answer = input("yes or no? ").lower()
    if answer == "yes":
        print("Got it.")
        break
    elif answer == "no":
        print("Okay.")
        break
    else:
        print("Please type 'yes' or 'no'.")
```

The loop is intentionally infinite, and `break` is the exit. Every valid answer triggers a break; an invalid one falls through to the else, prints the reminder, and loops back to the top.

A real-world use of `continue`. Processing items but skipping the broken ones:

```python
lines = ["apple", "", "banana", "", "cherry"]
for line in lines:
    if not line:        # empty string is falsy
        continue
    print(line.upper())
# prints APPLE, BANANA, CHERRY — the empty strings are skipped
```

`continue` keeps you from nesting your real logic one level deeper inside an `if`. Some style guides argue against it; I find it makes code easier to read when used sparingly. The rule of thumb: if `continue` lets you avoid wrapping the entire rest of the loop body in `if good:`, use it.

### The loop `else` clause

This is a Python feature you won't see in most other languages. You can attach `else` to a `for` or `while` loop, and it runs when — and only when — the loop completes *without* hitting `break`.

```python
for n in range(2, 10):
    if n == 5:
        break
else:
    print("loop finished without break")
# nothing prints — we broke out at 5
```

Versus:

```python
for n in range(2, 10):
    if n == 99:
        break
else:
    print("loop finished without break")
# prints: loop finished without break
```

The exact name is a bit unfortunate — most people read "else" as "otherwise," which doesn't quite fit. Mentally translate `else` on a loop to "no break." Then it makes sense.

When is this useful? Search-style loops, where you're looking for something and have to handle the case where you didn't find it:

```python
target = 7
numbers = [1, 4, 5, 9, 11]
for n in numbers:
    if n == target:
        print("found it")
        break
else:
    print("not found")
```

This says "look through the list; if you find it, print 'found it' and stop; if you finish the loop without finding it, print 'not found'." Without loop `else`, you'd need a sentinel variable:

```python
target = 7
numbers = [1, 4, 5, 9, 11]
found = False
for n in numbers:
    if n == target:
        found = True
        break
if not found:
    print("not found")
```

Both work. The loop-`else` version is one line shorter and arguably clearer once you know the pattern. The sentinel-variable version is more readable to anyone who hasn't seen loop `else` before. Use whichever fits your codebase's audience.

You'll also see loop `else` used with `while`:

```python
attempts = 0
max_attempts = 3
while attempts < max_attempts:
    answer = input("Password: ")
    if answer == "secret":
        print("Welcome.")
        break
    attempts += 1
else:
    print("Locked out.")
```

If the user guesses correctly within three tries, `break` fires and the `else` is skipped. If they exhaust the attempts, the `while` condition becomes false naturally, no `break` happens, and the `else` runs to print the lockout message.

### Nested loops

A loop inside a loop is a *nested loop*. The inner one runs in full for every iteration of the outer one.

```python
for row in range(3):
    for col in range(3):
        print(f"({row}, {col})")
```

Output:

```
(0, 0)
(0, 1)
(0, 2)
(1, 0)
(1, 1)
(1, 2)
(2, 0)
(2, 1)
(2, 2)
```

Nine prints from two loops of three. That's the math: if the outer loop runs `m` times and the inner one runs `n` times, the inner body runs `m × n` times total. Two nested loops over a thousand items is a million iterations. Three nested loops over a thousand items is a *billion*. This is where slow programs come from.

You won't usually be writing performance-critical code in this course, but the habit of noticing nested loops and asking "how big does this get?" is worth building now. The answer is sometimes "it doesn't matter, the lists are tiny," and sometimes "if this list ever grows to 10,000 items, the program will take an hour." Both are fine answers — what's not fine is not knowing which one applies.

A more typical use of nesting — building a 2D pattern:

```python
for row in range(1, 6):
    for col in range(row):
        print("*", end="")
    print()
```

Output:

```
*
**
***
****
*****
```

Two things to notice. `print("*", end="")` overrides print's default newline-after — it just prints the asterisk and stays on the same line. Then the bare `print()` at the bottom of the outer loop produces the line break. This is how you build text-art shapes in Python, more or less.

For the same triangle without a nested loop, lean on string multiplication:

```python
for row in range(1, 6):
    print("*" * row)
```

That's one line shorter and easier to read. When you can avoid nesting, do.

`break` and `continue` only affect the loop they're in directly — the innermost one. To break out of an outer loop from inside an inner one, you usually set a flag and check it after the inner loop ends. Or, often cleaner: pull the nested logic into a function (Module 6) and `return` from it.

**Try it:** Without running it, what does this print?

```python
for i in range(3):
    for j in range(2):
        if j == 1:
            break
        print(f"{i},{j}")
```

<details>
<summary>Answer</summary>

```
0,0
1,0
2,0
```

The `break` exits only the inner loop, not both. Each time the outer loop advances `i`, the inner loop restarts from `j = 0`, prints, then hits `j == 1` and breaks. If you predicted the loop would stop entirely after one print, you guessed `break` exits both loops. It doesn't.

</details>

### A complete example: the guessing game

Putting almost everything together — `while`, `if`/`elif`/`else`, `break`, and `import` from Module 2:

```python
import random

target = random.randint(1, 100)
attempts = 0

print("I'm thinking of a number between 1 and 100.")

while True:
    guess = int(input("Your guess: "))
    attempts += 1

    if guess < target:
        print("Too low.")
    elif guess > target:
        print("Too high.")
    else:
        print(f"Got it in {attempts} attempts!")
        break
```

`random.randint(1, 100)` picks a random integer from 1 to 100 *inclusive* — note that `randint` is one of the few functions where both bounds are inclusive, unlike `range`. The `while True` keeps asking forever; the `break` in the `else` branch is the exit. `attempts += 1` tracks the count.

This program covers conditional branching, infinite loops, `break`, `import`, type conversion, and `input` — everything from Modules 2 through 5 working together. It's three dozen lines short, and yet it's a complete interactive game.

## Common pitfalls

**1. The infinite loop that forgot to advance the counter.**

```python
n = 1
while n <= 5:
    print(n)
# forgot to increment n
```

Runs forever, prints `1` over and over. Kill with `Ctrl+C`. Fix by adding `n += 1` inside the loop. If you find yourself reaching for `while` more than `for`, ask whether `for range(...)` would do the job — it bakes the counter management in for you.

**2. Off-by-one with `range`.**

```python
for i in range(1, 5):
    print(i)    # 1 2 3 4 — but you wanted 1 2 3 4 5
```

`range(1, 5)` produces 1 through 4. To include 5, use `range(1, 6)`. Stop is exclusive. Every time.

**3. Modifying the loop variable inside a `for` loop and expecting it to matter.**

```python
for i in range(5):
    print(i)
    i = 100      # changes nothing on the next iteration
```

This prints 0, 1, 2, 3, 4. The `i = 100` is overwritten at the top of the next iteration when `for` gives `i` the next value from `range`. Don't try to control a `for` loop by reassigning its variable inside — use `break`, `continue`, or restructure with `while`.

**4. Using `continue` where you wanted `break`, or vice versa.**

```python
for n in range(1, 11):
    if n == 6:
        continue    # bug: meant to break
    print(n)
# prints 1 2 3 4 5 7 8 9 10 — 6 was skipped, not the end
```

`continue` skips one iteration. `break` ends the loop. They're not interchangeable.

**5. Comparing wrong types in the loop condition.**

```python
count = "5"   # from input() somewhere
while count > 0:
    print(count)
    count -= 1
# TypeError on Python 3 — can't compare str and int
```

`while` conditions are the same as `if` conditions — they have to be valid expressions. If `count` came from `input()`, convert it first with `int()` or `float()`.

**6. Nesting deeper than necessary.**

```python
for n in numbers:
    if n > 0:
        if n < 100:
            if n % 2 == 0:
                print(n)
```

Three nested `if`s do what one `and` does:

```python
for n in numbers:
    if n > 0 and n < 100 and n % 2 == 0:
        print(n)
```

Or, using chained comparison:

```python
for n in numbers:
    if 0 < n < 100 and n % 2 == 0:
        print(n)
```

Code with three levels of indentation is hard to read. If you find yourself going past three, look for a way to flatten — combine conditions, use `continue` to handle the "skip" case at the top, or break the inner work out into a function (Module 6).

## How this connects

Loops are the second great control-flow construct, sitting alongside conditionals from Module 4. Most loops have an `if` inside them; most non-trivial `if`s show up inside loops. You'll see this combination everywhere from here forward:

- **Module 6** (functions) turns reusable loop-and-conditional bundles into named, parameterized chunks of code. You'll write `def find(target, items)` and never re-implement a search by hand again.
- **Module 7** (lists and dicts) is the natural home of `for` loops. Iterating over a list is the most common thing `for` ever does.
- **Module 9** (exceptions) gives you a way to handle errors inside a loop without aborting the whole thing — the loop catches, recovers, continues.
- **Module 11** (file I/O) reads files line by line with a `for` loop: `for line in file:`. Same syntax, new source.

If anything in this lecture is shaky, especially `range`'s off-by-one behavior, drill the exercises before moving on. Module 7 and beyond assume loops are reflexive.

## Recap

- `while condition:` repeats a block as long as the condition is true. Without something inside that changes the condition, you get an infinite loop. `Ctrl+C` is the escape hatch.
- `for var in sequence:` iterates once per element of the sequence. The sequence can be a string, a list, a `range`, or several other things you'll meet later.
- `range(stop)`, `range(start, stop)`, `range(start, stop, step)` generate integer sequences. Stop is exclusive. A negative step counts down.
- `break` exits the enclosing loop. `continue` skips to the next iteration.
- `enumerate(seq)` pairs items with their indices — use it instead of `range(len(seq))`.
- `for ... else:` and `while ... else:` run the `else` block only if the loop completed without hitting `break`. Read "else" as "no break."
- Nested loops multiply iteration counts. Two nested loops of N items each run N² times. Notice when N could get big.

## Up next

Module 6 introduces functions: how to define your own, how to pass arguments and return values, and why short, single-purpose functions beat sprawling ones. After functions, you have all four building blocks — variables, types, conditionals, loops, functions — for writing genuine programs.

Now go work the exercises and mini-project for Module 5 in the curriculum doc. The multiplication-table and even-sum exercises drill `range`; the guessing game extends what you just saw; the asterisk triangle drills nesting and string tricks. FizzBuzz is the checkpoint — and yes, the classic interview question.
