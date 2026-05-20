# Module 6: Functions

## Why this matters

If you worked through Module 5, you probably noticed something annoying. The number-guessing game asked you to track guesses, prompt the user, compare against the target, and print a message. The FizzBuzz checkpoint did three things in five lines. Both worked. Both also lived as one long blob of code at the top level of your file.

Now suppose you want two players to take turns guessing. Or three rounds of FizzBuzz with different ranges. With what you know so far, your only option is copy-paste. Copy the guessing loop. Change a few variable names. Paste it again for player two. Find a bug, fix it in one copy, forget to fix the other. Welcome to the world before functions.

A function is a named, parameterized chunk of code you can call as many times as you want. Write the loop once, give it a name, and from then on you say `guess_round(player_name)` and the whole loop runs. Found a bug? Fix it in one place. Want a third player? Call the function a third time.

You've actually been using functions since Module 1. `print`, `input`, `int`, `len`, `range`: all functions. Someone else wrote them and you've been calling them by name. This module is where you start writing your own.

## What you'll be able to do by the end

- Define a function with `def`, give it parameters, and call it with arguments.
- Tell the difference between a function that prints and a function that returns, and pick the right one for the job.
- Use default and keyword arguments to make function calls clearer.
- Recognize when a variable is local to a function versus visible everywhere.
- Spot a function that's doing too much, and split it into smaller ones.
- Read a function call and predict what it does without running the code.

## Prerequisites

You need to be solid on variables and types (Module 1), `if`/`else` (Module 4), and both kinds of loops (Module 5). If `for n in range(10)` doesn't have an obvious meaning to you, go back. Functions will frequently contain loops and conditionals, and a wobbly grasp of either of those makes everything in this module worse.

You don't need anything from Modules 7 onward.

## Core concepts

### The motivation: I keep writing the same thing

Here's the kind of code that hurts. Say you're writing a dice game. You want two players to each roll three dice.

```python
import random

# Player 1
r1 = random.randint(1, 6)
r2 = random.randint(1, 6)
r3 = random.randint(1, 6)
print(f"Alice rolled {r1}, {r2}, {r3}")
alice_total = r1 + r2 + r3
print(f"Alice's total: {alice_total}")

# Player 2
r1 = random.randint(1, 6)
r2 = random.randint(1, 6)
r3 = random.randint(1, 6)
print(f"Bob rolled {r1}, {r2}, {r3}")
bob_total = r1 + r2 + r3
print(f"Bob's total: {bob_total}")
```

It works. Look at it. The two blocks are nearly identical, and there are only two players. Add a third and you copy the block again. Decide each player should roll five dice instead of three? Now you have to change it in two places. Three. Probably miss one.

The signal that you need a function is this exact feeling: *I have seen this shape of code before in my own file.* When that happens, package the shape up, give it a name, and let your future self call it.

### Defining your first function

A function definition has four parts: the keyword `def`, a name, parentheses, and a colon. Then the body of the function is indented underneath.

```python
def greet():
    print("Hello!")
```

Read that like this: *define* a function called `greet`. It takes no inputs (the parentheses are empty). When called, it runs the indented block, which prints `Hello!`.

The function now exists, but it hasn't done anything yet. Defining a function is not running it. Running it is a separate step:

```python
def greet():
    print("Hello!")

greet()
```

That last line is the function *call*. The parentheses are what trigger it. Without them, the function just sits there:

```python
def greet():
    print("Hello!")

greet     # this is not a call. Nothing prints.
```

A common new-programmer experience: you write a function, run the file, see no output, and assume the function is broken. It isn't. You forgot to call it.

**What could go wrong:** Missing the colon at the end of the `def` line. Missing the indentation on the body. Or, mostly, forgetting that defining a function doesn't run it.

### Parameters: making the function take input

A function that always says `"Hello!"` is only a little useful. What we want is a function that can greet anyone.

```python
def greet(name):
    print(f"Hello, {name}!")

greet("Ada")
greet("Grace")
```

The variable `name` inside the parentheses is a *parameter*. It's a placeholder. When you call `greet("Ada")`, Python binds `name` to the value `"Ada"` for the duration of that one call. Call it again with `"Grace"`, and `name` becomes `"Grace"`.

A small vocabulary distinction that will save you confusion when reading docs:

- A **parameter** is the variable in the function definition: `def greet(name):`.
- An **argument** is the value passed at the call site: `greet("Ada")`.

Same thing at runtime. Different word depending on which side of the function call you're standing on.

A function can take more than one parameter:

```python
def greet(greeting, name):
    print(f"{greeting}, {name}!")

greet("Hi", "Ada")        # Hi, Ada!
greet("Howdy", "Bob")     # Howdy, Bob!
```

Order matters. The first argument fills the first parameter, the second fills the second. Swap them and you get nonsense:

```python
greet("Ada", "Hi")   # Ada, Hi!
```

That output is wrong but Python has no idea. It just plugs in values in order. We'll see a way to defend against this (keyword arguments) shortly.

**Try it:** Predict what this prints before running it.

```python
def describe(animal, sound):
    print(f"The {animal} goes {sound}")

describe("cow", "moo")
describe("dog", "woof")
describe("woof", "dog")
```

<details>
<summary>Answer</summary>

```
The cow goes moo
The dog goes woof
The woof goes dog
```

The third line is what makes the point. Python doesn't know that "woof" is a sound and "dog" is an animal. It plugs in whatever you give it, in order. Argument order is your responsibility.

</details>

### `return` vs `print`: the most important distinction in this module

This is the concept that separates people who write working scripts from people who write code that can be reused. Pay attention.

A function that *prints* shows something on the screen and gives back nothing. A function that *returns* hands a value back to whoever called it, so the caller can do something with it.

```python
def double_print(x):
    print(x * 2)

def double_return(x):
    return x * 2
```

These look similar. They behave completely differently. Watch.

```python
result1 = double_print(5)
print(result1)
```

What gets printed? Two things. First, `double_print(5)` runs and prints `10`. Then `print(result1)` runs. But what is `result1`? The function `double_print` doesn't have a `return` statement. A function with no explicit return hands back the special value `None`. So `result1` is `None`, and the second line prints `None`.

```
10
None
```

Now the other one:

```python
result2 = double_return(5)
print(result2)
```

`double_return(5)` computes `5 * 2`, gets `10`, and *returns* it. Nothing prints from inside the function. The `10` is now stored in `result2`. Then `print(result2)` displays it.

```
10
```

One line of output, not two. And the crucial difference: `result2` actually holds `10`, the way `result1` did not hold anything useful.

Why does this matter? Because the point of a function is to be a building block you can compose with other building blocks. Watch what happens when you try to use these in a bigger expression:

```python
print(double_return(5) + 3)   # works, prints 13
print(double_print(5) + 3)    # TypeError
```

The second line crashes. `double_print(5)` returns `None`, and Python won't let you add `3` to `None`. The error:

```
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```

That cryptic message is Python's way of saying *you tried to do math on the result of a function that doesn't return anything*.

A rough rule: if a function exists to *compute a value*, it should `return` that value. If it exists to *cause a side effect* (print to the screen, write to a file, send a message), then doing the side effect is its whole job and a return isn't needed. Most functions you write should fall in the first category. Print at the top level of your script, not inside reusable functions.

**What could go wrong:** Mixing `print` and `return` in the same function and getting confused about which one feeds the caller. The function does both, but only the `return` value is usable by the caller. The `print` is purely a side effect.

### Multiple returns and early exit

A function can have more than one `return`. The first one that runs ends the function. Everything after it is skipped.

```python
def letter_grade(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
```

Notice there's no `elif`. We don't need one. Once `return "A"` fires, the function is done. Nothing below runs. The remaining `if` statements only get evaluated if the earlier ones were false.

This pattern, called *early return*, is one of the cleanest ways to express a chain of conditions. The alternative is uglier:

```python
def letter_grade(score):
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    return grade
```

Same result. More noise. Use whichever you find clearer, but be aware both patterns are common in the wild.

### Default arguments

Sometimes a parameter has a sensible default and you'd like callers to be able to skip it.

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Ada")              # Hello, Ada!
greet("Ada", "Howdy")     # Howdy, Ada!
```

The `greeting="Hello"` in the definition says *if the caller doesn't pass this argument, use "Hello"*. Defaults must come after non-default parameters. This is illegal:

```python
def greet(greeting="Hello", name):    # SyntaxError
    ...
```

Python's reason is practical. If `greeting` has a default and `name` doesn't, and someone calls `greet("Ada")`, does `"Ada"` fill `greeting` or `name`? Ambiguous. Python sidesteps the question by requiring all defaulted parameters to come last.

**What could go wrong:** Using a mutable object (like a list) as a default. This is one of the famous Python footguns. Skip it for now if it's confusing, but file it away:

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket

print(add_item("apple"))     # ['apple']
print(add_item("banana"))    # ['apple', 'banana']  <- surprise!
```

The default `basket=[]` is created *once* when the function is defined, not each time it's called. Every caller who skips the argument shares the same list. The fix is to use `basket=None` and create a new list inside the function. We'll come back to this in Module 7 when lists get a proper introduction.

### Keyword arguments at the call site

You can pass arguments by name, not just by position:

```python
def greet(greeting, name):
    print(f"{greeting}, {name}!")

greet(name="Ada", greeting="Hi")      # Hi, Ada!
greet(greeting="Hi", name="Ada")      # Hi, Ada!
```

When you name them, order stops mattering. Keyword arguments earn their keep when a function has several parameters and a reader would otherwise have to remember which is which:

```python
send_email("ada@example.com", "Hello", "Body of the message", True)
```

Versus:

```python
send_email(
    to="ada@example.com",
    subject="Hello",
    body="Body of the message",
    urgent=True,
)
```

Both calls are valid Python. The second one tells you what each argument is for.

### Scope: where variables live

A variable created inside a function lives only inside that function. The moment the function returns, the variable disappears.

```python
def compute_total(prices):
    total = sum(prices)
    tax = total * 0.0825
    return total + tax

result = compute_total([10, 20, 30])
print(result)
print(total)   # NameError: name 'total' is not defined
```

`total` and `tax` are *local* to `compute_total`. They don't exist at the top level. This is a feature, not a bug. It means functions don't accidentally clobber each other's variables. You can use `total` in one function and `total` in another, and they're completely separate boxes.

The reverse direction is more subtle. A function can *read* variables from outside itself:

```python
TAX_RATE = 0.0825

def compute_total(prices):
    total = sum(prices)
    return total * (1 + TAX_RATE)
```

That works. `TAX_RATE` is defined at the top level (we call this *module scope* or, loosely, *global scope*), and the function can see it. Reading a global from inside a function is fine. Using all-caps for constants like `TAX_RATE` is a convention so readers know it's meant to be set once and never changed.

What you can't do is *reassign* a global from inside a function without an explicit signal.

```python
count = 0

def increment():
    count = count + 1   # UnboundLocalError

increment()
```

Wait, why? It looks like it should just read `count`, add one, and write it back. The trap is this: Python sees the assignment `count = ...` on the left and decides *this function has a local variable called `count`*. Then on the right, `count + 1` tries to read the local `count`, which hasn't been assigned yet. Hence the error: *local variable referenced before assignment*.

You can fix this by telling Python explicitly that you mean the global one:

```python
count = 0

def increment():
    global count
    count = count + 1

increment()
print(count)   # 1
```

But mostly, don't. Reassigning globals from inside functions is a common source of bugs in larger programs because it lets a function quietly change state that anyone could be reading. The cleaner pattern is to take the value as a parameter and return the new value:

```python
def increment(count):
    return count + 1

count = 0
count = increment(count)
print(count)   # 1
```

The function does one thing, takes its input explicitly, and returns its output explicitly. No hidden dependencies on the outside world.

### `*args` and `**kwargs`: when you don't know how many

Most functions take a fixed number of arguments. Sometimes you want a function that takes *any* number. Python has syntax for that.

```python
def total(*numbers):
    return sum(numbers)

print(total(1, 2, 3))           # 6
print(total(1, 2, 3, 4, 5))     # 15
print(total())                   # 0
```

The `*numbers` in the definition collects every positional argument into a tuple called `numbers`. The name `args` is the convention, but `numbers` is more descriptive here. Inside the function, you treat it like any other sequence.

`**kwargs` is the same trick for keyword arguments. They get collected into a dictionary:

```python
def describe(**facts):
    for key, value in facts.items():
        print(f"{key}: {value}")

describe(name="Ada", age=25, role="engineer")
```

Don't reach for `*args` and `**kwargs` by default. They're useful when you genuinely don't know how many arguments will arrive, or when you're writing a wrapper function that should forward whatever it got to another function. For your day-to-day code, named parameters with sensible defaults are clearer.

### One function, one job

The last idea in this module is more taste than mechanics. A function should do one thing, and its name should say what.

A function called `process_data` that reads a file, cleans the data, computes statistics, and writes a report is technically valid Python. It's also miserable to read, hard to test, and impossible to reuse. The fix is to split it:

```python
def read_data(path):
    ...

def clean(rows):
    ...

def summary(rows):
    ...

def write_report(stats, path):
    ...
```

Each function has a clear name. Each one can be tested separately. When something breaks, the error message points at one of them, not at a 200-line monster.

Rough heuristic: if you can't summarize what a function does in one sentence without using the word "and," it's probably doing too much.

## Common pitfalls

1. **Calling without parentheses.** `greet` is the function. `greet()` calls it. Forgetting the parens silently does nothing. If your function "doesn't seem to run," check this first.

2. **Confusing `return` with `print`.** A function that prints can't have its output fed into another function. A function that returns can. When you find yourself writing `result = my_function(...)` and `result` keeps coming back as `None`, you probably forgot to `return`.

3. **Trying to use a local variable outside the function.** Local variables stop existing when the function returns. If you want a value to escape, `return` it and have the caller catch it.

4. **Reassigning a global without `global`.** `UnboundLocalError` is Python telling you it sees an assignment somewhere in the function, so it's treating that name as local everywhere in the function body, even on lines before the assignment. The cleanest fix is usually to refactor away from the global, not to add the `global` keyword.

5. **Mutable default arguments.** `def f(items=[])` reuses the same list across every call that doesn't pass `items`. Use `items=None` and create the list inside the function:

    ```python
    def f(items=None):
        if items is None:
            items = []
        ...
    ```

6. **Functions that take everything and do nothing.** `def process(data, config, options, mode, flag, callback, retries=3):` is the signature of a function trying to be everything to everyone. Break it up.

## Try it yourself

**Problem 1.** Write a function `is_even(n)` that returns `True` if `n` is even and `False` otherwise. Don't use an `if` statement.

<details>
<summary>Answer</summary>

```python
def is_even(n):
    return n % 2 == 0
```

`n % 2` is `0` for even numbers and `1` for odd. The comparison `== 0` already produces a boolean. No `if` needed.

</details>

**Problem 2.** What does this print, and why?

```python
def add(a, b):
    a + b

result = add(2, 3)
print(result)
```

<details>
<summary>Answer</summary>

It prints `None`. The function computes `a + b` and then throws the result away. There's no `return`. So `add(2, 3)` hands back `None`, which is what `result` ends up holding. The fix is to change the function's only meaningful line to `return a + b`.

</details>

**Problem 3.** Write a function `clamp(value, low, high)` that returns `value` if it's between `low` and `high`, otherwise returns `low` or `high`, whichever is closer. So `clamp(7, 0, 10)` returns `7`, `clamp(-3, 0, 10)` returns `0`, and `clamp(15, 0, 10)` returns `10`.

<details>
<summary>Answer</summary>

```python
def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value
```

Three returns, no `elif`. Each one ends the function the moment it fires.

A one-liner with built-ins also works:

```python
def clamp(value, low, high):
    return max(low, min(value, high))
```

Less obvious at a glance, more compact. Both are fine. Pick the version your future self will understand faster.

</details>

## How this connects

Functions are the first big leap in this curriculum. Variables (Module 1), conditionals (Module 4), and loops (Module 5) gave you the raw machinery. Functions give you a way to package that machinery, name it, and reuse it. From this point on, almost every piece of code you write will live inside some function, even if the function is just `def main():`.

Looking forward:

- **Module 7 (lists and tuples)** is where functions start taking and returning collections. Many of the most useful functions you'll write take a list, transform it, and hand back a new one.
- **Module 9 (exceptions)** introduces the idea that functions can fail. You'll learn how to handle that gracefully both inside the function and at the call site.
- **Module 10 (modules and packages)** is functions taken to the next level. A *module* is a file full of functions you can import. The `random.randint` you use in the dice game lives in someone else's module.
- **Module 13 (object-oriented programming)** introduces *methods*, which are functions attached to objects. The mechanics are mostly the same. The packaging changes.
- **Module 14 (testing)** is where small, single-purpose functions earn their keep. A function that does one thing is a function you can write a test for.

If anything in this lecture feels shaky, especially `return` versus `print` or the scope rules, practice the exercises before moving on. Module 7 will assume you can write a function that takes a list and returns something useful, without thinking about it.

## Recap

- A function definition is `def name(parameters):` followed by an indented body. Defining a function does not run it.
- Call a function with `name(arguments)`. The parentheses are what trigger execution.
- `return` hands a value back to the caller. `print` displays something on the screen. They are not interchangeable.
- A function with no explicit `return` returns `None`.
- Default arguments let callers skip parameters that have sensible defaults. Mutable defaults are a trap.
- Keyword arguments at the call site make code self-documenting when the function takes several parameters.
- Variables defined inside a function are local. They vanish when the function returns. Functions can read globals but should rarely reassign them.
- `*args` and `**kwargs` collect variable numbers of positional and keyword arguments. Use them when you need them, not by default.
- One function, one job. If you can't describe what it does in one sentence, split it.

## Up next

Module 7 introduces lists and tuples, Python's ordered collections. You'll start writing functions that take collections of values and hand back new ones, the most common shape of function you'll encounter in real code.

Now go work the exercises and mini-project for Module 6 in the curriculum doc. The dice game in particular is where the ideas in this lecture lock in: you'll write `roll_die`, `roll_n`, and `play_round`, and the main script will be three lines of function calls. That's the goal.
