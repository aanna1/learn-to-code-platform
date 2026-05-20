# Module 7: Lists and Tuples

## Why this matters

So far, every variable you've made holds one thing. One name, one age, one score. That works for tiny programs. It falls apart the moment you have thirty students, or a hundred prices, or a thousand log lines.

Try it without lists. You want to track four people's names. You write:

```python
name_1 = "Ada"
name_2 = "Grace"
name_3 = "Linus"
name_4 = "Guido"
```

Now print all of them. Four lines of `print`. Now sort them. Now ask the user for a name to search for. By the time you've got ten students, you have forty-something lines of repetitive code, and adding an eleventh student means editing the program. That's not a program. That's a manuscript.

A *list* lets you say *here are four names* in one variable, and from then on you operate on the group with a single loop. Same code handles four students or four thousand. Lists are how almost every real program keeps track of multiple things: rows in a database, items in a shopping cart, tasks in a queue, frames in a video, characters in a game.

This module is also where you start to feel a particular kind of Python weirdness: the difference between *the value* and *the name that points at the value*. Two names can point at the same list. Change the list through one name, the other name sees the change too. This trips up every new Python programmer at least once, and we're going to walk straight into the trap so you can recognize it later.

## What you'll be able to do by the end

- Create a list, index into it, slice it, and iterate over it.
- Add and remove items using the right method for the job.
- Tell which list operations mutate the list and which return a new value.
- Recognize and avoid the alias trap (`b = a` versus `b = a.copy()`).
- Build a 2D list (a grid) without the multiplication footgun.
- Use tuples for fixed-shape data and explain why immutability matters.
- Read a list comprehension well enough to use one when it's the cleanest option.

## Prerequisites

You should be solid on variables (Module 1), string indexing and slicing (Module 3), `for` and `while` loops (Module 5), and writing your own functions (Module 6). List slicing uses the exact same syntax as string slicing, so if `"abc"[::-1]` doesn't have an obvious meaning to you, go review Module 3 first.

Functions matter here because most of the practice problems will ask you to write a function that takes a list and returns something. If `def` and `return` still feel shaky, work the Module 6 exercises before continuing.

## Core concepts

### Creating a list

A list is written with square brackets and comma-separated values.

```python
students = ["Ada", "Grace", "Linus", "Guido"]
primes = [2, 3, 5, 7, 11, 13]
empty = []
mixed = ["Ada", 25, True, 1.7]
```

That last one (`mixed`) is legal Python but usually a sign your data is shaped wrong. Real lists in practice hold one kind of thing: a list of strings, a list of numbers, a list of dictionaries (Module 8 will show you those). When you find yourself mixing types, you usually want a dictionary or a class (Module 13) instead.

The built-in `len` function tells you how many items are in a list:

```python
students = ["Ada", "Grace", "Linus", "Guido"]
print(len(students))   # 4
```

### Indexing: same as strings

Lists are indexed from zero, just like strings.

```python
students = ["Ada", "Grace", "Linus", "Guido"]
print(students[0])    # Ada
print(students[1])    # Grace
print(students[-1])   # Guido (last item)
print(students[-2])   # Linus (second to last)
```

So far so good. Now, a question: what does this print?

```python
students = ["Ada", "Grace", "Linus", "Guido"]
print(students[4])
```

If you said "Guido," you got bitten by the off-by-one. The list has four items at positions 0, 1, 2, and 3. There is no position 4. Python raises `IndexError: list index out of range`.

This is the most common runtime error you'll hit when working with lists. The fix is almost always to use `len(students) - 1` for the last index, or `students[-1]`, which sidesteps the question entirely.

### Slicing returns a new list

Slicing uses the same `start:stop:step` syntax as strings, and `stop` is exclusive.

```python
students = ["Ada", "Grace", "Linus", "Guido"]
print(students[1:3])    # ['Grace', 'Linus']
print(students[:2])     # ['Ada', 'Grace']
print(students[2:])     # ['Linus', 'Guido']
print(students[::-1])   # ['Guido', 'Linus', 'Grace', 'Ada']  (reversed)
```

An important property: slicing returns a *new* list. The original is untouched.

```python
students = ["Ada", "Grace", "Linus", "Guido"]
first_two = students[:2]
first_two.append("Margaret")
print(first_two)    # ['Ada', 'Grace', 'Margaret']
print(students)     # ['Ada', 'Grace', 'Linus', 'Guido']  (unchanged)
```

Hold onto that fact. We'll come back to it.

### Adding to a list

The most common way to grow a list is `.append`, which adds one item to the end.

```python
students = ["Ada", "Grace"]
students.append("Linus")
print(students)   # ['Ada', 'Grace', 'Linus']
```

`.insert(i, x)` inserts `x` at position `i`, shifting everything after it down.

```python
students = ["Ada", "Grace", "Linus"]
students.insert(1, "Margaret")
print(students)   # ['Ada', 'Margaret', 'Grace', 'Linus']
```

What if you want to add multiple items at once? Here's where new programmers reach for `.append` and get a surprise.

```python
students = ["Ada", "Grace"]
students.append(["Linus", "Guido"])
print(students)
```

What do you expect?

```
['Ada', 'Grace', ['Linus', 'Guido']]
```

`.append` adds *one item*. You gave it a list. So it added the list as a single item, and now you have a list of two strings and a list. Almost certainly not what you wanted.

Two ways to actually add the contents:

```python
students = ["Ada", "Grace"]
students.extend(["Linus", "Guido"])
print(students)   # ['Ada', 'Grace', 'Linus', 'Guido']
```

Or concatenation, which produces a new list:

```python
students = ["Ada", "Grace"]
students = students + ["Linus", "Guido"]
print(students)   # ['Ada', 'Grace', 'Linus', 'Guido']
```

Both work. `.extend` modifies in place. `+` builds a new list and rebinds the name. In a loop adding one item at a time, `.append` is the right tool. To merge two existing lists, use `.extend` or `+`.

### Removing from a list

A few options, each with a different intent.

`.remove(value)` removes the first item equal to `value`.

```python
students = ["Ada", "Grace", "Ada", "Linus"]
students.remove("Ada")
print(students)   # ['Grace', 'Ada', 'Linus']
```

Notice only the first "Ada" was removed. If you wanted to remove all of them, you'd need a loop, or better, a list comprehension (we'll get there).

`.pop()` removes and *returns* the last item. `.pop(i)` removes and returns the item at index `i`.

```python
students = ["Ada", "Grace", "Linus"]
last = students.pop()
print(last)        # Linus
print(students)    # ['Ada', 'Grace']
```

`del students[i]` deletes by index without returning anything.

```python
students = ["Ada", "Grace", "Linus"]
del students[0]
print(students)    # ['Grace', 'Linus']
```

Picking between them is mostly a matter of intent. If you need the value you're removing, use `.pop`. If you don't care, `del` or `.remove` is fine.

### The "returns None" trap

This is one of the most common surprises in Python. Try to guess what this prints.

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_numbers = numbers.sort()
print(sorted_numbers)
```

You'd be forgiven for guessing `[1, 1, 2, 3, 4, 5, 6, 9]`. What actually prints is:

```
None
```

What just happened? `.sort()` is a *mutating* method. It sorts the list in place. It does not return the sorted list. It returns `None`, which is Python's way of saying "I did something for you; there's no value to give back."

Two fixes. First, sort in place and use the original variable:

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
numbers.sort()
print(numbers)   # [1, 1, 2, 3, 4, 5, 6, 9]
```

Second, use the built-in `sorted` function, which returns a new sorted list and leaves the original alone:

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_numbers = sorted(numbers)
print(sorted_numbers)   # [1, 1, 2, 3, 4, 5, 6, 9]
print(numbers)          # [3, 1, 4, 1, 5, 9, 2, 6]  (unchanged)
```

Bake this rule in: **methods that mutate a list usually return `None`.** That covers `.sort()`, `.reverse()`, `.append()`, `.extend()`, `.insert()`, and `.remove()`. The non-mutating versions (`sorted()`, `reversed()`, slicing, `+`) give you back a new list. The next time you write `x = some_list.something()` and `x` mysteriously holds `None`, this is why.

**Try it:** Without running the code, predict what each line prints.

```python
nums = [5, 2, 8, 1]
a = nums.sort()
b = sorted(nums)
print(a)
print(b)
print(nums)
```

<details>
<summary>Answer</summary>

```
None
[1, 2, 5, 8]
[1, 2, 5, 8]
```

`nums.sort()` mutated `nums` in place and returned `None`, so `a` is `None`. `sorted(nums)` then ran on the already-sorted list and returned a new sorted list. By the time both lines have run, `nums` itself has been sorted (by the first call), so the third `print` also shows the sorted version. If the order of the first two lines were swapped, the answers would be different. Order matters when one of the operations mutates.

</details>

### Iterating

The whole point of a list is to do something to each item. The `for` loop is the obvious tool.

```python
students = ["Ada", "Grace", "Linus"]
for student in students:
    print(f"Hello, {student}!")
```

When you need the index alongside the item, the wrong instinct is to write:

```python
for i in range(len(students)):
    print(f"{i}: {students[i]}")
```

This works. It's also Python's signal to use `enumerate` instead:

```python
for i, student in enumerate(students):
    print(f"{i}: {student}")
```

`enumerate` produces pairs of `(index, value)` as you loop. Same output, cleaner code, no `len` and no `[i]` lookup. A small thing, but reading idiomatic Python is part of writing it.

### One thing you should not do: mutate while iterating

This is the kind of bug that produces wrong answers without an error message, which is the worst kind.

```python
numbers = [1, 2, 2, 3, 4]
for n in numbers:
    if n % 2 == 0:
        numbers.remove(n)
print(numbers)
```

What do you expect? "Remove every even number," so `[1, 3]`. What you get:

```
[1, 2, 3]
```

A `2` survived. Here's why. The `for` loop walks the list by an internal index counter. On the second iteration the counter is at position 1, sees the first `2`, removes it. Now everything shifts left: the second `2` slides into position 1, the `3` into position 2. But the counter doesn't know about the shift. It moves on to position 2 next, which is now the `3`, and the second `2` gets silently skipped.

Two safe options. Iterate over a copy:

```python
numbers = [1, 2, 2, 3, 4]
for n in numbers[:]:           # slice creates a copy
    if n % 2 == 0:
        numbers.remove(n)
print(numbers)   # [1, 3]
```

Or, better, build a new list:

```python
numbers = [1, 2, 2, 3, 4]
numbers = [n for n in numbers if n % 2 != 0]
print(numbers)   # [1, 3]
```

That second version uses a list comprehension, which is the topic of a section in a moment.

### Membership with `in`

To check whether a value is in a list, use `in`:

```python
students = ["Ada", "Grace", "Linus"]
if "Ada" in students:
    print("Found Ada")
```

`in` reads like English and is a clear win over writing a manual search loop. Use it.

### Concatenation and repetition

You can stick two lists together with `+`:

```python
print([1, 2] + [3, 4])    # [1, 2, 3, 4]
```

And repeat a list with `*`:

```python
print([0] * 5)            # [0, 0, 0, 0, 0]
```

Repetition is useful for initializing a fixed-size list. It's also the setup for the next pitfall, which is one of the most famous in Python.

### The 2D list footgun

A 2D list is a list of lists. People use them for game boards, grids, spreadsheets, anything two-dimensional.

The temptation is to build one like this:

```python
board = [[" "] * 3] * 3
```

Looks elegant. Three rows, each of three spaces. Now mark a move:

```python
board = [[" "] * 3] * 3
board[0][0] = "X"
for row in board:
    print(row)
```

You're expecting:

```
['X', ' ', ' ']
[' ', ' ', ' ']
[' ', ' ', ' ']
```

You get:

```
['X', ' ', ' ']
['X', ' ', ' ']
['X', ' ', ' ']
```

Three X's. From one assignment.

Here's what's happening. `[" "] * 3` creates one list: `[" ", " ", " "]`. Then `[that_list] * 3` creates a new outer list with *three references to the same inner list*. Modifying `board[0][0]` modifies the only inner list there is, and all three names in the outer list see it because they're all pointing at the same place.

The fix is to create a fresh inner list each time:

```python
board = [[" "] * 3 for _ in range(3)]
board[0][0] = "X"
for row in board:
    print(row)
```

```
['X', ' ', ' ']
[' ', ' ', ' ']
[' ', ' ', ' ']
```

That `[... for _ in range(3)]` syntax is a list comprehension, which runs the expression once per iteration. Each iteration creates a separate `[" "] * 3`. (The single underscore `_` is a convention for "I'm not going to use this loop variable.")

You'll meet this bug for real when you build the tic-tac-toe exercise. Now you'll recognize it.

### Aliasing: the b = a trap

We've been dancing around this issue all module. Here it is head-on.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
print(b)
```

What does this print?

If you said `[1, 2, 3]` and `[1, 2, 3, 4]`, that's the natural guess. What actually prints is:

```
[1, 2, 3, 4]
[1, 2, 3, 4]
```

`a` changed. We never touched `a`. We touched `b`. What gives?

`a = [1, 2, 3]` creates a list and gives it the name `a`. `b = a` does not copy the list. It gives the same list a second name. From that line on, `a` and `b` are two names for one list. Mutating through `b` is the same as mutating through `a`, because there's only one list.

The fix is to make an actual copy:

```python
a = [1, 2, 3]
b = a.copy()
b.append(4)
print(a)   # [1, 2, 3]
print(b)   # [1, 2, 3, 4]
```

`a.copy()`, `a[:]`, and `list(a)` all build a new list with the same contents. Use any of them.

Why is this so important? Because functions get bitten by it constantly.

```python
def add_zero(items):
    items.append(0)
    return items

original = [1, 2, 3]
result = add_zero(original)
print(result)      # [1, 2, 3, 0]
print(original)    # [1, 2, 3, 0]
```

The function looks like it builds and returns a new list. It doesn't. It mutates the caller's list, then returns the same list under a new name. The caller's `original` got modified as a side effect. That's a recipe for a bug that's hard to track down because the function's signature doesn't warn you.

A safer pattern: copy at the boundary, or build a new list and return it.

```python
def add_zero(items):
    items = items + [0]    # creates a new list; `items` now points at it
    return items

original = [1, 2, 3]
result = add_zero(original)
print(result)      # [1, 2, 3, 0]
print(original)    # [1, 2, 3]   (untouched)
```

If you remember one thing from this module besides "lists exist," remember this: **two names can point at the same list, and mutating through one shows up in the other.**

### Tuples: like lists, but frozen

A tuple is an ordered sequence of values, like a list, except you can't change it after it's created.

```python
point = (3, 4)
print(point[0])     # 3
print(point[1])     # 4
point[0] = 5        # TypeError: 'tuple' object does not support item assignment
```

That looks like a feature loss. Why would you want a thing you can't change? Three reasons.

First, safety. A tuple you pass to a function is guaranteed to come back unchanged. No aliasing surprises. If a function needs a fixed-shape pair of numbers, take a tuple and you've ruled out a whole class of bug.

Second, expressiveness. A tuple says "these values belong together as one thing." A list says "this is a collection that might grow or shrink." A `(latitude, longitude)` pair is a tuple. A list of points is a list. Using the right one signals intent to the next person reading your code.

Third, tuples can be dictionary keys and set members. Lists can't. We'll see why in Module 8, when we get to dictionaries.

One syntactic catch. To create a one-element tuple, you need a trailing comma.

```python
x = (5)     # not a tuple. Just the integer 5 in parentheses.
y = (5,)    # tuple with one element
print(type(x))   # <class 'int'>
print(type(y))   # <class 'tuple'>
```

The parentheses don't make it a tuple. The comma does. The parens are mostly for readability.

### Unpacking

Tuples (and lists) can be split into individual variables in one line.

```python
point = (3, 4)
x, y = point
print(x)    # 3
print(y)    # 4
```

This is *unpacking*. The shapes have to match: a 2-tuple on the right, two names on the left. Mismatch and you get an error.

```python
point = (3, 4)
x, y, z = point     # ValueError: not enough values to unpack
```

Unpacking is everywhere in Python. The `enumerate` example earlier used it: `for i, student in enumerate(students)` is unpacking each `(index, value)` pair into two names per iteration. Functions that return multiple values are doing the same trick:

```python
def stats(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

low, high, avg = stats([5, 2, 8, 3, 9])
print(f"min={low}, max={high}, avg={avg}")
```

A function can only return one object. When you write `return a, b, c`, Python wraps those values into a tuple and returns that. The caller unpacks the tuple back into three names. Multiple return values is unpacking in disguise.

### List comprehensions: a preview

You've seen the syntax a few times in this module. Let's name it.

A list comprehension builds a list by transforming each item of another iterable, optionally filtering.

```python
# squares of 0 through 9
squares = [x ** 2 for x in range(10)]
print(squares)   # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# only the positives from a list
numbers = [-3, 5, -1, 0, 8, -2]
positives = [n for n in numbers if n > 0]
print(positives)   # [5, 8]
```

Read left to right: `[expression for variable in iterable if condition]`. The `if` part is optional. The result is a new list.

Comprehensions are the idiomatic Python answer to "I have a list, I want to make a new list out of it." Almost any time you find yourself writing:

```python
result = []
for x in items:
    if some_condition(x):
        result.append(transform(x))
```

A comprehension would say the same thing in one line:

```python
result = [transform(x) for x in items if some_condition(x)]
```

Don't go overboard with them. A short comprehension is a delight. A comprehension that spans three lines with two filters and a nested loop is harder to read than the explicit loop it replaces. The rule of thumb: if you'd struggle to explain it out loud, write the loop.

**Try it:** Rewrite this loop as a list comprehension.

```python
words = ["hello", "WORLD", "Python", "RULES"]
lowered = []
for w in words:
    if len(w) >= 5:
        lowered.append(w.lower())
```

<details>
<summary>Answer</summary>

```python
words = ["hello", "WORLD", "Python", "RULES"]
lowered = [w.lower() for w in words if len(w) >= 5]
print(lowered)   # ['hello', 'world', 'python', 'rules']
```

One line. Same result. Once you can read these fluently, you'll write them constantly.

</details>

## Common pitfalls

1. **Off-by-one with indexing.** A list of length `n` has valid indices `0` through `n-1`. `students[len(students)]` is always an `IndexError`. Use `students[-1]` for the last item.

2. **`.sort()` returns `None`.** And so do `.append`, `.reverse`, `.extend`, `.insert`, `.remove`. If you wrote `x = lst.sort()` and `x` is `None`, that's why. Use `sorted(lst)` if you want a new list back.

3. **Modifying a list while iterating over it.** This produces wrong answers, not errors, which makes it worse. Iterate over a copy (`for x in lst[:]`) or build a new list with a comprehension.

4. **The `[[...] * n] * m` 2D-list bug.** This creates `m` references to the same inner list, not `m` independent inner lists. Use `[[...] * n for _ in range(m)]` instead.

5. **Aliasing two variables to the same list.** `b = a` does not copy. Use `b = a.copy()`, `b = a[:]`, or `b = list(a)`. Same applies to passing a list into a function: the function can mutate the caller's list unless you copy first.

6. **One-element tuple missing the comma.** `(5)` is the integer 5. `(5,)` is a tuple of one. The comma is what makes it a tuple, not the parens.

## How this connects

Lists are the workhorse data structure of Python, and from this point on they'll show up in every module:

- **Module 8 (dictionaries and sets)** introduces collections that aren't ordered, are indexed by keys instead of positions, and are often used alongside lists. You'll see lists of dictionaries constantly. That's the shape JSON data takes.
- **Module 9 (exceptions)** is where you'll learn to handle the `IndexError` and `ValueError` cases that come from operating on lists with bad input, without crashing your program.
- **Module 11 (files and CSV)** treats each row of a file as a list. Reading a CSV gives you a list of lists. Reading JSON gives you nested lists and dictionaries.
- **Module 13 (object-oriented programming)** is where you'll bundle lists into objects, and where you'll write methods that operate on collections.
- **Module 14 (testing)** is where the aliasing rules come back to bite you in tests that pass once and then fail on the second run, because some setup function mutated a list the second test wasn't expecting to be different.

If the alias trap or the 2D-list trap still feels mysterious, slow down and work through the exercises before moving on. Module 8 is going to assume lists are second nature.

## Recap

- A list is an ordered, mutable collection of values, written with square brackets.
- Indexing and slicing on lists work the same way as on strings. Indices are zero-based.
- Mutating methods (`.sort`, `.reverse`, `.append`, `.extend`, `.insert`, `.remove`) modify the list in place and return `None`. Non-mutating alternatives (`sorted`, `reversed`, slicing, `+`) return a new list.
- Iterate with `for`. Use `enumerate` when you need the index too.
- `[[" "] * n] * m` creates aliased inner lists. Use `[[" "] * n for _ in range(m)]` for a true 2D grid.
- `b = a` does not copy a list. Use `a.copy()`, `a[:]`, or `list(a)` for an independent copy.
- Tuples are immutable lists. Use them for fixed-shape data, for safety, and (Module 8) for dictionary keys.
- Unpacking lets you split a tuple or list into separate variables in one statement. Multiple return values from a function are unpacking in disguise.
- List comprehensions are a compact, idiomatic way to build a list from another iterable.

## Up next

Module 8 introduces dictionaries (key-value storage) and sets (unordered, unique collections). Dictionaries are how you store data that's looked up by name instead of position, and they're the most common data structure in real Python code outside of lists themselves.

Now go work the exercises and mini-project for Module 7 in the curriculum doc. The tic-tac-toe board exercise is where the 2D-list footgun gets real, and the to-do list mini-project is the first time you'll keep persistent state in a single list across many user actions. Those two are the ones that lock the module in.
