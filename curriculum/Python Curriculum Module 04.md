# Module 4: Conditionals

## Why this matters

Every program you've written so far runs the same way every time. Top to bottom, line by line, no decisions. You take input, you do math, you print a result. Run the program twice with the same input and you get the same output, identical down to the byte.

That's a useful kind of program, but it's not most of them. Most programs need to do *different things in different situations*. An ATM checks whether your balance covers the withdrawal. A login form checks whether the password matches. A game checks whether the player guessed too high or too low. A traffic light decides whether to turn green, yellow, or red. None of those programs can be written as a straight line of instructions. They need to *branch*.

Conditionals are how you write branches. They're the part of programming where the language stops being a fancy calculator and starts being something that can make decisions. After this module, your programs can start being responsive to what they see — not just *that* the user typed something, but *what* they typed.

What goes wrong without this knowledge? Your programs can't validate input, can't check for errors, can't react to different inputs differently. You can't write a single useful application without conditionals. They're not optional knowledge.

## What you'll be able to do by the end

- Use the comparison operators `==`, `!=`, `<`, `>`, `<=`, `>=` and explain why `=` and `==` are different.
- Write `if`, `elif`, and `else` statements with correctly indented blocks.
- Combine conditions with `and`, `or`, and `not`, and predict the result of short-circuit evaluation.
- Identify which Python values are *truthy* and which are *falsy*, and use that to write shorter conditions.
- Use the `in` operator to check membership in a string (and, by extension, lists in Module 7).
- Decide when chained `elif` is clearer than nested `if`, and vice versa.

## Prerequisites

You need everything from Modules 1 through 3: variables, type conversion (especially `int(input(...))` and `float(input(...))`), and the difference between a string `"25"` and an integer `25`. Comparison operators behave differently across types, so if "type" still feels fuzzy, go back. You should also be comfortable with `bool` from Module 1 and the truthy/falsy quick note at the end of Module 2.

## Core concepts

### Comparison operators produce booleans

A *comparison operator* is a symbol that asks a yes/no question about two values. Python has six:

| Operator | Question | Example | Result |
|---|---|---|---|
| `==` | Are these equal? | `5 == 5` | `True` |
| `!=` | Are these not equal? | `5 != 6` | `True` |
| `<` | Is the left smaller? | `5 < 6` | `True` |
| `>` | Is the left bigger? | `5 > 6` | `False` |
| `<=` | Smaller or equal? | `5 <= 5` | `True` |
| `>=` | Bigger or equal? | `6 >= 5` | `True` |

Every comparison produces a *boolean* — `True` or `False`. That's it. There's no in-between answer.

```python
age = 20
print(age >= 18)    # True
print(age == 21)    # False
print(age < 13)     # False
```

You can compare strings too, with a couple of gotchas. Equality (`==`) checks character-by-character, case-sensitively:

```python
print("hello" == "hello")    # True
print("hello" == "Hello")    # False — case matters
print("hello" == " hello")   # False — whitespace matters
```

If you need case-insensitive comparison, lowercase both sides first (Module 3): `s1.lower() == s2.lower()`. If you need to ignore whitespace, `.strip()` both sides.

Order comparisons (`<`, `>`) on strings sort alphabetically — sort of. They use the underlying character codes, which means uppercase letters come before lowercase ones:

```python
print("apple" < "banana")    # True — alphabetical
print("Z" < "a")             # True — uppercase Z has a lower code than lowercase a
```

You won't lean on string `<` and `>` often. Just know that they exist and behave a little strangely with mixed case.

### `=` vs `==` — the one mistake everybody makes

Here's the bug you're going to write at least three times before it sticks. `=` is *assignment*. `==` is *equality*. They are completely different things, but they look almost identical, so they get mixed up constantly.

```python
age = 18      # assignment: put 18 into the variable `age`
age == 18     # comparison: is age equal to 18? returns True or False
```

In an `if` statement, you want a comparison. Watch what happens if you reach for `=` by reflex:

```python
age = 17
if age = 18:           # SyntaxError
    print("adult")
```

Python catches it for you. The interpreter rejects this with `SyntaxError: invalid syntax` because `=` doesn't produce a value `if` can use. That's friendlier than you might guess — in languages like C, `if (age = 18)` is legal, silently assigns 18 to `age`, and runs the `if` block every single time. Python won't let you do that. The error message is your friend.

Read `=` aloud as "gets" and `==` as "equals." `age = 18` is "age *gets* 18." `age == 18` is "*does* age equal 18?"

### `if` statements

The simplest conditional is `if`, which runs a block of code only when a condition is true:

```python
age = int(input("Age: "))
if age >= 18:
    print("You can vote.")
print("Done.")
```

Three pieces matter. The `if` keyword. The *condition* — anything that produces a boolean (or that Python can interpret as one — more on truthiness in a moment). And the *colon* at the end of the line, which says "the block below this is what to run conditionally."

Then comes the *block* itself — the indented code beneath. Python uses indentation to mark which lines belong to the `if`. Four spaces is the convention; your editor probably does it automatically when you hit Enter after a line ending in `:`. The indentation isn't decoration. It's how Python knows where the block starts and ends:

```python
age = int(input("Age: "))
if age >= 18:
    print("You can vote.")        # part of the if block — runs only if age >= 18
    print("You can also vote in primaries.")    # also part of the if block
print("Done.")                    # NOT part of the if block — always runs
```

The `print("Done.")` line is back at the original indentation level, so Python knows it's outside the `if`. Whether `age` is 17 or 71, that last line runs.

Indentation has to be consistent. Mix tabs and spaces, or use four spaces on one line and three on the next, and Python rejects the file:

```python
if age >= 18:
    print("You can vote.")
     print("You can also vote in primaries.")    # IndentationError
```

Most editors handle this for you — just pick "spaces" or "tabs" in your settings and let the editor be consistent. If you ever see an `IndentationError` and can't spot the problem, your editor might be mixing tabs and spaces in a way you can't see. Most editors have a "show whitespace" toggle.

### `else` for the other path

`else` covers the case where the `if` condition is false:

```python
age = int(input("Age: "))
if age >= 18:
    print("You can vote.")
else:
    print("Not yet — but soon.")
```

Notice the `else:` sits at the same indentation as `if`. The block under it is the "what to do if the condition was false." Exactly one of the two blocks runs. Never both, never neither.

### `elif` for multiple paths

What if you have more than two cases? You might think to write:

```python
score = int(input("Score: "))
if score >= 90:
    print("A")
if score >= 80:
    print("B")
if score >= 70:
    print("C")
else:
    print("Below C")
```

Run that with a score of `95`. What prints?

```
A
B
C
```

That's not what we want. Each `if` is independent — they all check their own conditions, and any that are true run. A score of 95 is greater than 90, *and* greater than 80, *and* greater than 70, so all three blocks fire.

The fix is `elif`, short for "else if." It chains conditions together so only the first true one runs:

```python
score = int(input("Score: "))
if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("Below C")
```

Now a score of 95 prints just `A`. Python checks `if score >= 90`, finds it true, runs that block, and skips the rest of the chain entirely. The other conditions don't even get evaluated.

Order matters in an `elif` chain. Look at what happens if we flip it:

```python
score = int(input("Score: "))
if score >= 70:
    print("C")
elif score >= 80:
    print("B")
elif score >= 90:
    print("A")
```

A score of 95 prints `C`. The first condition (`score >= 70`) is true, so we take that branch and never check the others. When you're using `elif` for a range of values, go from most-specific (narrowest) to least-specific (widest), or — equivalently — from highest threshold to lowest.

Because `elif` chains in order, you don't have to write upper bounds. By the time `elif score >= 80` runs, we already know `score >= 90` was false, so we know `score < 90` without having to write it. This is one of the small everyday pleasures of `elif`.

The structure as a whole is: one `if`, zero or more `elif`s, optional `else` at the end. The `else` is the catch-all. If you don't include one, and none of the conditions match, nothing happens — no error, just silence.

**Try it:** Predict what each chain prints when `x = 5`. Then run them.

```python
# Chain A
x = 5
if x > 0:
    print("positive")
if x > 3:
    print("more than 3")
if x > 10:
    print("more than 10")

# Chain B
x = 5
if x > 0:
    print("positive")
elif x > 3:
    print("more than 3")
elif x > 10:
    print("more than 10")
```

<details>
<summary>Answer</summary>

**Chain A** prints:
```
positive
more than 3
```

Each `if` is independent. The first two conditions are true, so both blocks run. The third is false, so it doesn't.

**Chain B** prints:
```
positive
```

The `if` matched, so the chain is done. None of the `elif`s are even checked. This is the key difference between independent `if` statements and an `elif` chain.

</details>

### Logical operators: `and`, `or`, `not`

Often you want to combine multiple conditions. Python has three logical operators for that:

```python
age = 20
has_id = True

if age >= 18 and has_id:
    print("Welcome.")
```

`and` is true only when *both* sides are true. `or` is true when *at least one* side is true. `not` flips a boolean:

```python
is_weekend = False
print(not is_weekend)        # True
print(True and False)        # False
print(True or False)         # True
print(False or False)        # False
```

You can chain them together. Operator precedence: `not` is evaluated first, then `and`, then `or`. If the order isn't obvious, add parentheses:

```python
age = 25
has_id = True
is_member = False

# These are equivalent — parentheses just make the intent clearer
if (age >= 18 and has_id) or is_member:
    print("Allowed in.")

if age >= 18 and has_id or is_member:
    print("Allowed in.")
```

Both work. The first is easier to read. Add parentheses whenever you have to pause to figure out what's going on. Future-you will thank you.

#### Short-circuit evaluation

`and` and `or` have a subtle feature called *short-circuiting*. They evaluate left to right and stop the moment they know the answer.

For `and`, if the left side is false, the right side is irrelevant — the whole expression is false. Python doesn't evaluate the right side at all.

For `or`, if the left side is true, the right side is irrelevant — the whole expression is true. Again, Python skips the right side.

This matters in two ways. First, performance: if the right side is expensive (a function call, a database query), `and`/`or` can save work. Second — and more important for now — short-circuiting lets you guard against errors. Suppose `input()` might return an empty string and you want to check whether its first character is a digit:

```python
text = input("Type something: ")
if text[0].isdigit():
    print("starts with a digit")
```

If the user hits enter without typing anything, `text` is `""`, `text[0]` is an `IndexError`, and the program crashes. Guard against it with `and`:

```python
text = input("Type something: ")
if text and text[0].isdigit():
    print("starts with a digit")
```

If `text` is `""` (an empty string is falsy), the `and` short-circuits — `text[0].isdigit()` never runs, no crash. This pattern shows up constantly.

#### A subtle thing `or` does

In Python, `and` and `or` don't strictly return `True` or `False`. They return one of the *operands*.

```python
print(0 or "hello")       # "hello"
print("a" or "b")         # "a"
print(0 or 0 or "found")  # "found"
print(0 and "hello")      # 0
print("a" and "b")        # "b"
```

The rule, restated: `or` returns the first truthy operand, or the last operand if all were falsy. `and` returns the first falsy operand, or the last operand if all were truthy.

This is the checkpoint question. `0 or "hello"` is `"hello"` because `0` is falsy, so `or` moves on to the next operand, finds `"hello"` (truthy), and returns it.

You'll mostly see this used as a default-value trick:

```python
name = input("Name (or blank): ") or "Anonymous"
print(name)
```

If the user types something, that's truthy, so `or` returns it. If they leave it blank, `""` is falsy, `or` moves on, and the result is `"Anonymous"`. Compact and idiomatic, once you get used to it.

### Truthy and falsy values

Inside an `if`, Python doesn't strictly require a boolean. It accepts anything, and converts it to a boolean using a fixed set of rules. The values that count as false — *falsy* — are:

- `False`
- `None`
- Zero of any numeric type: `0`, `0.0`
- Empty sequences: `""`, `[]`, `()`, `{}`

Everything else is *truthy*.

```python
name = input("Name: ")
if name:
    print(f"Hello, {name}.")
else:
    print("You didn't enter a name.")
```

`if name:` is shorthand for `if name != "":`. The empty string is falsy; any non-empty string is truthy. Reading it aloud as "if there's a name" makes the intent clear.

Same idea for numbers:

```python
count = 0
if count:
    print("we have some")
else:
    print("none")
```

`0` is falsy, so this prints `none`. If `count` were any other number — including negative numbers — it'd be truthy.

A trap to know about: `if name:` and `if name is not None:` are *not* the same. The first treats `""` as falsy and skips the block. The second only skips when `name` is literally `None`. If you're distinguishing "the variable hasn't been set" from "the variable holds an empty value," you need `is None` / `is not None`, not just truthiness.

### Chained comparisons

Python lets you chain comparisons in a way that looks mathematical:

```python
age = 25
if 18 <= age < 65:
    print("working age")
```

`18 <= age < 65` is the same as `18 <= age and age < 65`, but it reads more naturally and you only have to write `age` once. This is one of the few places where Python is unusually expressive — most other languages don't allow this.

It chains as long as you want:

```python
if 0 <= score <= 100:
    print("valid score")
```

### Nested conditionals

You can put an `if` inside another `if`:

```python
age = int(input("Age: "))
has_id = input("Do you have ID? (yes/no): ").lower() == "yes"

if age >= 18:
    if has_id:
        print("Welcome.")
    else:
        print("Come back with ID.")
else:
    print("Too young.")
```

Sometimes nesting is what you want. Sometimes it's clearer to combine with `and` instead:

```python
if age >= 18 and has_id:
    print("Welcome.")
elif age >= 18 and not has_id:
    print("Come back with ID.")
else:
    print("Too young.")
```

A rule of thumb: if each branch needs different follow-up actions, nest. If you can flatten it with `and`/`or`, flatten. Deeply nested conditionals get hard to read fast.

### The `in` operator

`in` checks whether one thing is contained inside another. For strings, it checks for a substring:

```python
sentence = "the quick brown fox"
print("fox" in sentence)        # True
print("zebra" in sentence)      # False
print("quick" in sentence)      # True
print("Quick" in sentence)      # False — case-sensitive
```

`in` is the right tool whenever your question is "does this contain that?":

```python
text = input("Type a sentence: ").lower()
if "python" in text:
    print("a Python fan!")
```

`in` works on lists, tuples, and sets too — same syntax, same intuition. We'll see those properly in Module 7. For now, just know the pattern carries forward.

You can negate with `not in`:

```python
if "@" not in email:
    print("That doesn't look like an email.")
```

Reads cleanly, behaves the way you'd guess.

**Try it:** Write a tiny program that asks for a username and rejects it if it doesn't meet these rules: at least 3 characters, no spaces, and must include a letter. Use what you know.

<details>
<summary>Answer</summary>

```python
username = input("Pick a username: ")

if len(username) < 3:
    print("Too short.")
elif " " in username:
    print("No spaces allowed.")
elif not any(c.isalpha() for c in username):
    print("Must include at least one letter.")
else:
    print(f"Username '{username}' accepted.")
```

A couple of things worth flagging. `len(s)` is a built-in function that returns the length of a string (or any sequence). `c.isalpha()` is a string method — true for letters, false for digits and symbols. `any(...)` returns True if any item in a sequence is truthy. The `c.isalpha() for c in username` part is a *generator expression* — a compact way to check each character. That last bit uses syntax from Module 5 (loops) and Module 7 (comprehensions), so it's getting ahead of where we are. A simpler version using only what we've covered:

```python
username = input("Pick a username: ")

has_letter = False
for c in username:
    if c.isalpha():
        has_letter = True
        break

if len(username) < 3:
    print("Too short.")
elif " " in username:
    print("No spaces allowed.")
elif not has_letter:
    print("Must include at least one letter.")
else:
    print(f"Username '{username}' accepted.")
```

That uses a `for` loop and `break`, which are next module's topic. If you can't read either version yet, that's fine — both are answers to a "Try it" that's deliberately reaching forward. The key takeaway is the structure of the `if`/`elif` chain, not the cleverness inside each condition.

</details>

## Common pitfalls

**1. Using `=` instead of `==`.**

```python
if age = 18:           # SyntaxError
    print("adult")
```

`=` assigns. `==` compares. Python catches the bare case as a syntax error, but the mistake can hide inside more complex code (especially when combined with the walrus operator `:=`, which we won't cover here). Read `=` as "gets" and `==` as "equals" until it's automatic.

**2. Comparing strings to numbers.**

```python
age = input("Age: ")    # always a string
if age >= 18:           # TypeError on Python 3
    print("adult")
```

`input()` returns a string. You can't compare `"17"` to `18` without converting first. This is the same trap as Module 2, just in a new outfit:

```python
age = int(input("Age: "))
if age >= 18:
    print("adult")
```

**3. Forgetting that `elif` chains short-circuit.**

```python
score = 95
if score >= 70:
    print("C")
elif score >= 80:
    print("B")
elif score >= 90:
    print("A")
```

Prints `C`, not `A`. The first matching condition wins, so order matters. Either reverse it (highest threshold first) or use independent `if`s if every condition really does need to be checked separately.

**4. Mixing tabs and spaces, or inconsistent indentation.**

```python
if age >= 18:
    print("Welcome.")
     print("Enjoy.")        # IndentationError
```

Pick spaces (4 of them, per Python convention), set your editor to do it automatically, and don't think about it again. If you're pasting code from the internet and getting `IndentationError`, suspect tabs.

**5. Treating `0` or `""` like `None`.**

```python
count = 0
if count:
    print("we have some")
else:
    print("nothing")
```

`0` is falsy, so this prints `nothing`. If `0` is a valid value that means "zero of something" and you want to distinguish it from "no value was set," use `is None` explicitly. The boolean coercion in `if` will conflate them.

**6. Writing redundant `== True` and `== False`.**

```python
is_admin = True
if is_admin == True:        # redundant
    print("admin")
```

`is_admin` is already a boolean. The `== True` adds nothing.

```python
if is_admin:                # clean
    print("admin")
if not is_admin:            # negation, clean
    print("not admin")
```

If you find yourself writing `== True`, the variable name probably wants to read as a yes/no question already (`is_admin`, `has_pet`, `was_paid`), and the `==` is just noise.

## How this connects

Module 1 gave you variables; Module 2 gave you input; Module 3 gave you string operations. Module 4 is where they finally cooperate. Now you can take input, check what it is, and do different things depending on what you saw. That's the shape of every interactive program.

- **Module 5** (loops) is conditionals' twin. A `while` loop is essentially an `if` that runs over and over until its condition becomes false. Most of what you learned here — comparisons, logical operators, truthiness — carries over identically.
- **Module 6** (functions) lets you bundle a chain of conditionals into a named, reusable test (`is_valid_email(text)`).
- **Module 9** (exceptions) gives you a second way to handle "what if something goes wrong" — sometimes cleaner than checking with `if` first.
- **Module 12** (regex) is what you reach for when your `if "X" in text` conditions get complicated enough that exact-match thinking falls apart.

If anything in this lecture is shaky — especially `elif` order and short-circuit evaluation — slow down and work through the exercises before moving on. Conditionals show up in every module from here.

## Recap

- Comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) produce booleans. `=` assigns; `==` compares.
- `if` runs a block when a condition is true. `else` covers the other case. `elif` chains additional conditions, short-circuiting at the first match.
- Python uses indentation (4 spaces by convention) to define which lines belong to a block. Indentation must be consistent.
- `and`, `or`, `not` combine booleans. `and`/`or` short-circuit: they stop evaluating once the answer is known.
- `or` returns the first truthy operand; `and` returns the first falsy one. Neither strictly returns `True`/`False`.
- Truthy values include any non-zero number and any non-empty string/list. Falsy values are `False`, `None`, `0`, `0.0`, `""`, `[]`, `()`, `{}`.
- Chained comparisons like `18 <= age < 65` are legal and clearer than `18 <= age and age < 65`.
- `in` tests membership: `"fox" in sentence`. `not in` negates it.

## Up next

Module 5 introduces loops — `for` and `while` — which let you run a block of code repeatedly. Combined with conditionals, loops are where programs really start doing serious work.

Now go do the exercises and mini-project for Module 4 in the curriculum doc. The grade calculator drills `elif` order; the leap year exercise drills logical operators; the triangle classifier drills the whole stack.
