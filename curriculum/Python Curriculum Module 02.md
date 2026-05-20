# Module 2: Type Conversion, Input, and Arithmetic

## Why this matters

The programs in Module 1 had a problem you probably noticed but didn't have the words for: they always did the same thing. Run them twice, get the same output twice. The "input" was hardcoded — you typed it into the source file, and the only way to change what the program saw was to edit the program itself.

That's not how real software works. Real software takes input from somewhere outside its own code — a user at the keyboard, a file on disk, a request over the network — and does something useful with it. Module 2 is where your programs stop being static and start being responsive.

Once you have input, you almost always want to compute something with it. Add it up, calculate a tax, find a square root, round it to two decimals for a receipt. So input and arithmetic come together in the same module, and they share a problem: Python is strict about types, and the value you got from the user is almost certainly not the type you want for math. The whole module is about negotiating that mismatch.

What goes wrong without this knowledge? You write `int(input("Age: ")) + 5` and it works for `25` and crashes on `twenty-five`. You write `7 / 2` and get `3.5` when you wanted `3`. You write `0.1 + 0.2` and get `0.30000000000000004` and briefly question your life choices. These aren't exotic bugs. They're the daily mistakes new Python programmers make for their first six months. We're going to hit each one head-on so you have the reflexes before you have the bug.

## What you'll be able to do by the end

- Use `input()` to prompt for a value and capture the result, remembering that the result is *always* a string.
- Convert between strings, integers, floats, and booleans using `int()`, `float()`, `str()`, and `bool()`.
- Predict whether a given type conversion will succeed or raise `ValueError`.
- Apply Python's seven arithmetic operators (`+ - * / // % **`) and explain what `//` and `%` do without thinking about it.
- Use `math.pi`, `math.sqrt`, `math.ceil`, and `math.floor` from the standard library, after importing the module.
- Format numeric output to a specific number of decimal places using f-string format specifiers like `:.2f`.

## Prerequisites

You should be comfortable with everything from Module 1: creating variables, calling `print()`, using f-strings, and the conceptual difference between `"25"` (a string) and `25` (an integer). If that last one feels squishy, re-read the closing section of Module 1 before continuing. Module 2 is essentially an extended workout in that distinction.

## Core concepts

### Getting input from the user

Python comes with a built-in function called `input()`. Call it, and Python pauses your program, waits for the user to type something and hit Enter, and gives you back whatever they typed.

```python
name = input("What's your name? ")
print(f"Hello, {name}.")
```

A few things to notice. `input()` takes one argument — the prompt — which is just a string Python prints before pausing. The prompt is optional, but skipping it leaves the user staring at a blank cursor with no idea what you want, so always include one. The space at the end of `"What's your name? "` is deliberate: it gives a visual gap between the question and the cursor where the user types.

Whatever the user types gets returned as the value of `input()`. We capture it with `name = ...`. From that point on, `name` is just a variable like any other.

Run this. Type your name. The program greets you. Run it again with a different name. It greets that one instead. That's the leap from Module 1: same code, different behavior.

### The trap: `input()` always returns a string

Here's the part that bites everyone. Let me write a program that adds 5 to whatever number the user gives me, and let's pretend I haven't read this section yet:

```python
n = input("Enter a number: ")
print(n + 5)
```

Run it, type `10`, and watch what happens:

```
TypeError: can only concatenate str (not "int") to str
```

Python is telling us, in its slightly awkward way, that `n` is a string and `5` is an integer, and `+` doesn't know how to combine those. Why is `n` a string? Because `input()` returns a string. Always. Even when the user types something that *looks* like a number, Python hands it back as text. The `"10"` that came out of `input()` is the two-character string `1` followed by `0`, not the number ten.

Confirm it for yourself:

```python
n = input("Enter a number: ")
print(type(n))
```

Type `10`, and you'll see `<class 'str'>`. Type `3.14`, you'll see `<class 'str'>`. Type `hello`, also `<class 'str'>`. The user's input is text until you do something about it.

### Type conversion (casting)

Doing something about it means *converting* — also called *casting* — the string to the type you actually want. Python has a small set of built-in functions for this, each named after the type it produces:

```python
int("10")        # 10        (integer)
float("3.14")    # 3.14      (float)
str(42)          # "42"      (string)
bool(1)          # True      (boolean)
```

Each one takes a value and gives you back the same logical thing in a different type. Now we can fix our broken adder:

```python
n = int(input("Enter a number: "))
print(n + 5)
```

What's happening on that first line, reading inside-out: `input("Enter a number: ")` runs first and returns a string. That string gets passed straight into `int(...)`, which converts it to an integer. The integer gets stored in `n`. Now `n + 5` is integer plus integer, which Python is delighted to do.

You can keep the conversion as a separate step if you find the nested call confusing:

```python
raw = input("Enter a number: ")
n = int(raw)
print(n + 5)
```

Both styles are fine. The nested version is more compact. The two-step version is easier to debug because you can `print(raw)` between the steps and see exactly what came in. Use whichever is clearer for the program in front of you.

### When conversion fails

What if the user types `twenty-five` instead of `25`? `int()` can't make sense of that — there's no integer in the world spelled `twenty-five` — and it raises an error:

```
ValueError: invalid literal for int() with base 10: 'twenty-five'
```

A `ValueError` is Python's way of saying "you gave me the right *type* of thing, but I can't do anything with this specific *value*." The string was a string, sure, but it wasn't a string that looks like a number.

Other things that break `int()`:

```python
int("3.14")     # ValueError — it's a float-shaped string, not an int-shaped one
int(" 25 ")     # works! whitespace gets stripped
int("")         # ValueError — empty string has no number in it
int("twenty")   # ValueError — words aren't numbers
```

For now, we're going to write programs that assume the user cooperates. Module 9 is where you'll learn to catch these errors with `try`/`except` and handle them gracefully. Until then, when your program crashes because someone typed `cat` into an "Enter your age:" prompt, that's expected. Note it and move on.

`float()` is more forgiving than `int()` because it accepts everything `int()` accepts *and* decimal-looking strings:

```python
float("3.14")   # 3.14
float("3")      # 3.0 — note the .0
float("twenty") # ValueError
```

If you're not sure whether the user might type `3` or `3.5`, use `float()`. You can always round later.

**Try it:** Without running this, predict what each line prints (or whether it errors). Then run it to check.

```python
print(int("100"))
print(int("100.0"))
print(float("100"))
print(str(100) + str(200))
print(int("100") + int("200"))
```

<details>
<summary>Answer</summary>

```
100
ValueError
100.0
100200
300
```

- `int("100")` is the integer `100`.
- `int("100.0")` raises `ValueError` because `int()` won't accept a string with a decimal point. If you want an int from a decimal-looking string, do it in two steps: `int(float("100.0"))`.
- `float("100")` is the float `100.0`. Python prints it with a trailing `.0` to remind you it's a float.
- `str(100) + str(200)` first converts both to strings, then `+` between strings is concatenation: `"100" + "200"` is `"100200"`.
- `int("100") + int("200")` converts both to integers first, then `+` between integers is addition: `100 + 200` is `300`.

The fourth and fifth lines are the same logical "100 and 200 combined" idea producing wildly different results because of types. This is exactly why types matter.

</details>

### `type()` for inspection

`type()` is a built-in function that returns the type of any value. You won't use it in your final program — your final program should already know what types it's dealing with — but it's invaluable when something isn't behaving the way you expected.

```python
x = input("Enter something: ")
print(type(x))     # <class 'str'> — always
x = int(x)
print(type(x))     # <class 'int'> — after conversion
```

When you hit a `TypeError` and don't understand it, sprinkle `print(type(variable))` above the failing line and look at what you actually have versus what you thought you had. Three times out of four, the answer is "I thought I had an int and I actually have a string."

### Arithmetic operators

Once you have actual numbers, you can do arithmetic. Python has seven operators:

| Operator | Name | Example | Result |
|---|---|---|---|
| `+` | addition | `3 + 2` | `5` |
| `-` | subtraction | `3 - 2` | `1` |
| `*` | multiplication | `3 * 2` | `6` |
| `/` | true division | `7 / 2` | `3.5` |
| `//` | floor division | `7 // 2` | `3` |
| `%` | modulo (remainder) | `7 % 2` | `1` |
| `**` | exponentiation | `2 ** 10` | `1024` |

The first three behave the way you'd expect from a pocket calculator. The last four reward closer attention.

#### `/` always returns a float

```python
print(6 / 3)   # 2.0, not 2
```

Even when the division comes out clean, `/` returns a float. If you specifically need an integer, you'll need `//` or `int(6 / 3)`.

#### `//` is floor division

```python
print(7 / 2)   # 3.5
print(7 // 2)  # 3
```

`//` drops anything after the decimal point and returns just the integer part. Useful when you're counting whole things: how many full boxes you can fill, how many complete laps you've run, how many full minutes are in 200 seconds.

```python
total_seconds = 200
minutes = total_seconds // 60
print(f"{minutes} full minutes")   # 3 full minutes
```

One wrinkle worth knowing: `//` works on floats too, but the result is also a float. `7.0 // 2` is `3.0`, not `3`. The "floor" in floor division refers to dropping the fractional part, not to the return type.

#### `%` is the remainder

```python
print(7 % 2)   # 1 — because 7 ÷ 2 is 3 with 1 left over
print(8 % 2)   # 0 — because 8 ÷ 2 is 4 exactly
print(10 % 3)  # 1 — because 10 ÷ 3 is 3 with 1 left over
```

Modulo is the operator new programmers most often shrug at and then use constantly two weeks later. It answers the question "after dividing as much as I can, what's left over?" The most common use is checking divisibility:

```python
n = 14
if n % 2 == 0:
    print("even")
else:
    print("odd")
```

(We haven't covered `if` yet — that's Module 4 — but you can probably read it.)

Continuing the minutes example from a moment ago, what about the leftover seconds?

```python
total_seconds = 200
minutes = total_seconds // 60
seconds = total_seconds % 60
print(f"{minutes}:{seconds:02d}")   # 3:20
```

The `:02d` part is a format specifier — it pads single-digit numbers with a leading zero so `20` stays `20` but `5` becomes `05`. We'll cover format specifiers properly in a few sections.

#### `**` is exponentiation

```python
print(2 ** 10)   # 1024
print(3 ** 2)    # 9
print(2 ** 0.5)  # 1.4142... (the square root of 2)
```

The double asterisk is exponentiation. It works with floats too, which gives you roots: anything to the power of `0.5` is its square root. `math.sqrt()` does the same job with a clearer name; we'll meet it in a moment.

### Operator precedence

When an expression has multiple operators, Python applies them in a specific order: exponentiation first, then multiplication/division (including `//` and `%`), then addition/subtraction. Same as math class.

```python
print(2 + 3 * 4)   # 14, not 20 — 3 * 4 happens first
print(2 ** 3 * 2)  # 16 — 2 ** 3 happens first, then * 2
```

If you want a different order, wrap parts in parentheses:

```python
print((2 + 3) * 4)   # 20 — parens first
```

When in doubt, add parentheses. Python doesn't care that they're "redundant," and readers will thank you for the clarity:

```python
total = price + (price * tax_rate)   # clearer than: price + price * tax_rate
```

### The `math` module

The built-in operators handle the basics, but for square roots, ceilings, floors, pi, and friends, you reach for the `math` module. A *module* is just a file of Python code somebody else wrote and packaged up so you don't have to. Before you can use a module, you have to *import* it:

```python
import math

print(math.pi)           # 3.141592653589793
print(math.sqrt(16))     # 4.0
print(math.ceil(3.2))    # 4 — rounds up
print(math.floor(3.8))   # 3 — rounds down
print(math.pow(2, 10))   # 1024.0 — like 2 ** 10, but always returns a float
```

The `import math` line at the top of your file gives you access to everything inside the math module. Each function or constant inside it gets prefixed with `math.` when you use it. That prefix is how Python knows you want *its* `pi`, not some variable named `pi` you might define elsewhere.

A worked example using `math.pi`:

```python
import math

radius = float(input("Radius of the circle: "))
area = math.pi * radius ** 2
circumference = 2 * math.pi * radius

print(f"Area: {area}")
print(f"Circumference: {circumference}")
```

Run it with a radius of `5`, and you'll get area `78.53981633974483` and circumference `31.41592653589793`. Mathematically correct. Visually awful. Which brings us to rounding.

### Rounding and formatting numbers

You have two ways to control how many decimal places show up.

The first is the built-in `round()` function, which returns an actual rounded number:

```python
import math

area = math.pi * 5 ** 2
print(round(area, 2))   # 78.54
```

`round(value, digits)` rounds to that many decimal places. `round(value)` with no second argument rounds to the nearest integer.

The second is an f-string format specifier, which controls how a value gets *displayed* without changing the underlying value:

```python
area = math.pi * 5 ** 2
print(f"{area:.2f}")     # 78.54
print(area)              # 78.53981633974483 — original value unchanged
```

Inside an f-string, you can put a colon after the variable name and add formatting instructions. `.2f` means "format as a float with 2 decimal places." Other useful ones:

```python
price = 1234567.891

print(f"{price:.2f}")      # 1234567.89
print(f"{price:,.2f}")     # 1,234,567.89  — comma thousands separator
print(f"{price:>15.2f}")   # right-aligned in a 15-character-wide column
print(f"{price:<15.2f}")   # left-aligned in a 15-character-wide column
```

The format specifier reads like this: `[alignment][width].[precision][type]`. Don't memorize all of it. Remember `.2f` for "two decimal places, please," and look up the rest when you need it. The Python documentation calls these the "format specification mini-language," and yes, that name is as off-putting as it sounds.

When should you round versus format? Round when you need the rounded value for further math; format when you only need it to look right on screen. Most of the time you want to format. The full-precision number is more useful to keep around.

**Try it:** A user enters a price and a quantity. Print the total cost formatted to two decimal places, with a comma thousands separator. Don't worry yet about handling bad input — but identify where the program *would* crash.

<details>
<summary>Answer</summary>

```python
price = float(input("Price per item: "))
quantity = int(input("Quantity: "))
total = price * quantity
print(f"Total: ${total:,.2f}")
```

If the user types `9.99` and `1000`, you get `Total: $9,990.00`. If they type `nine` for the price, `float()` raises a `ValueError` on line 1. If they type `1.5` for the quantity, `int()` raises a `ValueError` on line 2. Both are fine for now. We'll fix them in Module 9.

</details>

### `bool()` and truthiness — a quick note

`bool()` converts values to `True` or `False`, but it's almost never used the way `int()` and `float()` are. You won't often write `bool(input(...))`. What's more useful is knowing what *counts* as `True` versus `False` when Python is implicitly checking — which matters in Module 4 when we get to `if`.

The short version: empty things and zero are False; everything else is True.

```python
bool(0)         # False
bool(0.0)       # False
bool("")        # False
bool(None)      # False
bool(1)         # True
bool(-1)        # True
bool("0")       # True — a non-empty string, even one containing "0"
bool("False")   # True — same reason; it's a non-empty string
```

That second-to-last one trips people up. The *string* `"0"` is truthy because it's a non-empty string. The *number* `0` is falsy. Same character on the screen, completely different behavior.

## Common pitfalls

**1. Forgetting that `input()` returns a string.**

```python
age = input("Age: ")
if age > 18:            # TypeError — can't compare str and int
    print("adult")
```

Convert the moment you receive it:

```python
age = int(input("Age: "))
```

**2. Using `/` when you wanted `//` (or the other way around).**

```python
total_pages = 500
pages_per_chapter = 50
chapters = total_pages / pages_per_chapter
print(f"You'll need {chapters} chapters.")
# Output: "You'll need 10.0 chapters." — that .0 looks wrong
```

If you're counting whole things, use `//`:

```python
chapters = total_pages // pages_per_chapter
print(f"You'll need {chapters} chapters.")
# Output: "You'll need 10 chapters."
```

**3. Calling `int()` on a string with a decimal point.**

```python
price = int(input("Price: "))   # user types 9.99
# ValueError: invalid literal for int() with base 10: '9.99'
```

`int()` only accepts integer-shaped strings. Use `float()` if decimals are valid, or `int(float("9.99"))` if you really do want an integer (it truncates toward zero, giving you `9`).

**4. Reaching for `math.sqrt(-1)` and being surprised.**

```python
import math
math.sqrt(-1)   # ValueError: math domain error
```

Square roots of negative numbers aren't real numbers, and `math.sqrt` only deals in real numbers. (Python's `cmath` module handles complex numbers if you ever need it — most beginners never do.) For everyday work, this error means your inputs are wrong. Verify them before calling `sqrt`.

**5. Floating-point arithmetic isn't exact.**

```python
print(0.1 + 0.2)         # 0.30000000000000004
print(0.1 + 0.2 == 0.3)  # False
```

This isn't a Python bug. Every language with floats has this quirk. Computers store floats in binary, and some decimal numbers (like 0.1) don't have exact binary representations, so tiny rounding errors creep in. For money or anything that needs exact decimals, the `decimal` module exists; we won't cover it here, but know it's there. For now: format your output with `:.2f` so the user never sees the messy version, and don't compare floats with `==`.

**6. Forgetting `import math` at the top of the file.**

```python
print(math.pi)   # NameError: name 'math' is not defined
```

If you use anything from a module, the `import` line must appear in that file, conventionally at the top, before any code that uses the module.

## How this connects

Module 1 introduced variables and types as static things. Values you'd hardcoded in your source file. Module 2 is where those types start having consequences. `input()` always hands you a string. Almost everything you'll want to *do* with that input — arithmetic, comparisons, looking it up in a list — requires you to convert it first. Every program from here on out will start by accepting some input, converting it to the right type, doing something with it, and printing a formatted result. That's the shape of roughly 70% of what you'll write in the next ten modules.

Module 3 picks up the other side of the same problem: now that you know `input()` gives you strings, what *else* can you do with strings besides convert them to numbers? Module 4 introduces conditionals, where comparison operators (`==`, `<`, `>`) start to look very useful in combination with the inputs you can now take. And `int()` raising `ValueError` when the user types `cat` — that's a thread you'll pick up in Module 9, where you'll finally learn how to keep your program running even when something goes wrong.

## Recap

- `input(prompt)` displays the prompt and returns whatever the user types, *as a string*. Always.
- Convert strings to numbers with `int()` or `float()`. Use `float()` when you don't know whether the input will be a whole number.
- Conversion can fail. `int("twenty")` raises `ValueError`. We'll handle that properly in Module 9.
- `type(value)` is a debugging tool for the question "what do I actually have here?"
- The arithmetic operators are `+ - * / // % **`. The traps: `/` always returns a float; `//` is floor division (drops the decimal); `%` is the remainder; `**` is exponentiation.
- `import math` gives you `math.pi`, `math.sqrt`, `math.ceil`, `math.floor`, and more.
- `round(value, digits)` rounds a number for use in further math. `f"{value:.2f}"` formats a number for display without changing it.
- Empty strings, `0`, `0.0`, and `None` are *falsy*. Almost everything else is *truthy*. We'll use this in Module 4.

## Up next

Module 3 treats strings as data you can slice, search, and reshape — picking out a domain from an email, splitting a full name into first and last, replacing every space in a sentence with an underscore.

Now go work the exercises and mini-project for Module 2 in the curriculum doc. The point of this lecture is to make those doable; the point of doing them is to make this lecture stick.
