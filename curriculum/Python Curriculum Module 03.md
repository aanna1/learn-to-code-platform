# Module 3: Strings in Depth

## Why this matters

Roughly everything that crosses the boundary of your program — user input, lines from files, JSON from APIs, command-line arguments, environment variables, log entries — arrives as a string. Module 2 dealt with the special case where what you actually want is a number, so you convert as fast as you can. Module 3 is the much bigger category: when you want the string itself, and you need to do something with it.

What "something" usually means: clean it up, pull part of it out, check whether it matches a pattern, glue it to other strings. Concrete examples you'll meet within a week of using Python in real life:

- A user typed `"  Ada Lovelace  "` with extra whitespace because they're on a phone. You need to strip it before storing.
- You have an email `"user@example.com"` and you need just the domain.
- A CSV line `"name,age,city,occupation"` needs to break into four pieces.
- A timestamp `"2024-11-15T14:30:00Z"` has a date and a time stuck together, and you need them apart.

What goes wrong without this: you can't tell the difference between `" Ada"` and `"Ada"` when comparing, so a login fails for no reason. You write `s.lower()` on a line and wonder why the original is still capitalized. You try to use `s[0]` to grab the first character of a name and crash when somebody enters an empty string. None of these are exotic. They're all going to happen, multiple times, this month.

## What you'll be able to do by the end

- Index into a string to grab any single character, using positive or negative positions.
- Slice strings to extract substrings, including reversing one with `s[::-1]`.
- Use the core string methods — `.lower()`, `.upper()`, `.strip()`, `.replace()`, `.split()`, `.join()`, `.find()`, `.count()`, `.startswith()`, `.endswith()` — without looking each one up.
- Choose between `+`, f-strings, and `.join()` for combining strings, and explain why.
- Read and write escape sequences (`\n`, `\t`, `\\`, `\"`), and know when to reach for a raw string.
- Align and pad strings inside f-strings using format specifiers like `{name:<20}` and `{value:>10.2f}`.

## Prerequisites

You need everything from Modules 1 and 2: variables, types, `input()`, f-strings, and the difference between `"25"` and `25`. If you can't yet explain why `input()` always returns a string, go back. If f-string syntax (`f"Hello, {name}"`) still feels weird, write five more by hand before continuing.

## Core concepts

### Strings are sequences of characters

A string in Python isn't an atomic blob of text. It's a *sequence* — an ordered collection of individual characters, each at a numbered position. Same way an array works, if you've seen one in another language.

```python
word = "Python"
```

That string has six characters: `P`, `y`, `t`, `h`, `o`, `n`. Each lives at a numbered slot, starting at zero:

```
position:   0   1   2   3   4   5
character:  P   y   t   h   o   n
```

Yes, zero. Every introductory programmer fights this for about a week. The first character is at position `0`, not `1`. The reasons are partly historical and partly mathematical, but the point isn't to argue with it. The point is to internalize it.

You grab a single character with square brackets:

```python
word = "Python"
print(word[0])   # P
print(word[1])   # y
print(word[5])   # n
```

You can also count backwards from the end with negative indices:

```python
print(word[-1])   # n — last character
print(word[-2])   # o — second to last
```

`word[-1]` is the most useful trick in this section. Need the last character of any string, no matter how long? `s[-1]`. Don't compute `len(s) - 1` like you're writing C from 1972. Python lets you skip that.

### What if you go past the end?

What happens if you ask for `word[10]` and the word is only six characters?

```python
word = "Python"
print(word[10])
# IndexError: string index out of range
```

You crash. `IndexError` is Python's standard "you asked for a slot that doesn't exist" error. The same applies to negative indices: `word[-100]` is also an error. There's no automatic wrap-around or default.

This is a real bug worth being paranoid about. If a string might be empty (and an `input()` call could always return `""`), then `s[0]` crashes. Module 4's conditionals will give you the tools to guard against that. For now, just remember the failure mode exists.

### Strings are immutable

Here's something that surprises people coming from languages like JavaScript. You cannot change a character inside a string in place.

```python
word = "hello"
word[0] = "J"
# TypeError: 'str' object does not support item assignment
```

Strings in Python are *immutable*. Once created, the actual sequence of characters can't be modified. Every operation that looks like it "changes" a string actually produces a new string and leaves the original alone.

This isn't just trivia. It's the source of one of the most common new-programmer bugs in Python:

```python
name = "  Ada  "
name.strip()        # returns "Ada" but throws it away
print(name)         # still "  Ada  ", spaces and all
```

`.strip()` did its job — it produced a new string with the whitespace removed — but we didn't capture the result, so it vanished. Fix it by grabbing the return value:

```python
name = "  Ada  "
name = name.strip()
print(name)         # "Ada"
```

Or:

```python
clean_name = name.strip()
```

The same pattern applies to every string method. They all return new strings; none modify the original. We'll see this maybe ten more times in this lecture, because it's that easy to forget.

### Slicing

Slicing is how you grab a *range* of characters instead of just one. The syntax is `s[start:stop]`:

```python
word = "Python"
print(word[0:3])    # "Pyt"
print(word[1:4])    # "yth"
print(word[2:6])    # "thon"
```

Notice what `word[0:3]` gave you: `"Pyt"` — three characters. Not four. The `stop` value is *exclusive*. The slice includes everything from `start` up to but not including `stop`. So `[0:3]` is positions 0, 1, 2.

This is the place to write deliberately wrong code first, then fix it. Suppose you want the first four characters of `"Python"`:

```python
word = "Python"
print(word[0:3])    # "Pyt"   ← what I might write if I wasn't paying attention
print(word[0:4])    # "Pyth"  ← correct
```

If you want N characters starting from position `start`, the stop is `start + N`, not `start + N - 1`. Eventually this becomes reflex. Until it does, the half-open convention burns everybody.

A few shortcuts. You can leave either side blank, and Python fills in the default — start of string for an empty `start`, end of string for an empty `stop`:

```python
word = "Python"
print(word[:3])     # "Pyt"     — first three, same as [0:3]
print(word[3:])     # "hon"     — from position 3 to the end
print(word[:])      # "Python"  — a full copy
```

Negative indices work in slices too:

```python
print(word[-3:])    # "hon"    — last three characters
print(word[:-1])    # "Pytho"  — everything except the last character
```

`word[:-1]` is a useful trick for stripping a trailing newline or similar.

And the third slice parameter is a `step`:

```python
word = "Python"
print(word[::2])    # "Pto"     — every second character
print(word[::-1])   # "nohtyP"  — every character, backward
```

That last one is the checkpoint question's answer. `[::-1]` says "start at the default (end, because the step is negative), stop at the default (beginning), step by -1." So it walks the string from end to beginning. It's the most common Pythonic way to reverse a string.

Slices, unlike single-index lookups, don't raise errors when you go out of bounds:

```python
print(word[0:100])    # "Python"   — silently clipped
print(word[100:200])  # ""         — empty string, no error
```

That's friendlier than indexing, but slightly more dangerous: a slice that returns `""` looks like it worked, so you may not notice the bug.

**Try it:** Predict what each of these prints. Then check.

```python
s = "automation"
print(s[0])
print(s[-1])
print(s[0:4])
print(s[4:])
print(s[::-1])
print(s[2:-2])
```

<details>
<summary>Answer</summary>

```
a
n
auto
mation
noitamotua
tomati
```

- `s[0]` is the first character: `a`.
- `s[-1]` is the last character: `n`.
- `s[0:4]` is positions 0, 1, 2, 3: `auto`.
- `s[4:]` is position 4 to the end: `mation`.
- `s[::-1]` is the reverse: `noitamotua`.
- `s[2:-2]` is position 2 (`t`) up to but not including position -2 (the `o` at index 8): positions 2, 3, 4, 5, 6, 7 — `t`, `o`, `m`, `a`, `t`, `i` — so `tomati`. Mixing positive and negative bounds is legal and sometimes very useful.

</details>

### String methods: the core dozen

A *method* is a function that belongs to an object and is called with a dot: `s.method()`. Strings come with dozens of methods built in. You don't need to memorize all of them. You need to know about a dozen well enough to recognize when one would help.

Every method we're about to see returns a *new* string. None modify the original. Worth saying twice because the bug we just saw with `.strip()` repeats for every other method too.

#### Case conversion: `.lower()`, `.upper()`, `.title()`

```python
greeting = "Hello, World"
print(greeting.lower())    # "hello, world"
print(greeting.upper())    # "HELLO, WORLD"
print(greeting.title())    # "Hello, World" — first letter of each word
print(greeting)            # "Hello, World" — unchanged
```

These are essential for case-insensitive comparison. Want to check if the user typed "yes" without caring about capitalization?

```python
answer = input("Continue? ").lower()
if answer == "yes":
    print("Continuing.")
```

Note the `.lower()` chained right onto the `input()` call. That's idiomatic: clean the input the moment you receive it, before you store it.

#### Whitespace cleanup: `.strip()`, `.lstrip()`, `.rstrip()`

`.strip()` removes whitespace (spaces, tabs, newlines) from both ends of a string. `.lstrip()` does the left side only; `.rstrip()` does the right.

```python
raw = "   Ada Lovelace\n"
print(raw.strip())     # "Ada Lovelace"
```

Anyone who has read user input or read a line from a file has hit a "why doesn't this match" bug caused by trailing whitespace. `.strip()` is your friend. Use it on user input by default unless you have a specific reason not to.

You can also pass `.strip()` a string of characters to strip, instead of just whitespace:

```python
url = "https://example.com/"
print(url.rstrip("/"))  # "https://example.com" — removes the trailing slash
```

#### Finding and counting: `.find()`, `.count()`, `.startswith()`, `.endswith()`, `in`

```python
sentence = "the quick brown fox jumps over the lazy dog"
print(sentence.find("fox"))        # 16 — position where "fox" starts
print(sentence.find("zebra"))      # -1 — not found, returns -1 (not an error)
print(sentence.count("the"))       # 2
print(sentence.startswith("the"))  # True
print(sentence.endswith("dog"))    # True
print("fox" in sentence)           # True
```

A subtle warning on `.find()`: it returns `-1` when nothing is found. Not `None` and not an error. So if you wrote:

```python
position = sentence.find("zebra")
print(sentence[position:position + 5])   # ?? — wrong, but won't crash
```

You'd silently get garbage, because `sentence[-1:4]` is a weird slice that happens to be valid. Always check the result of `.find()` before slicing with it, or use the `in` operator for "does it exist?" questions and `.find()` only when you need the actual position.

#### Replacing and splitting: `.replace()`, `.split()`, `.join()`

`.replace(old, new)` returns a new string with every occurrence of `old` swapped out:

```python
text = "I like cats. Cats are great."
print(text.replace("cats", "dogs"))    # "I like dogs. Cats are great."
print(text.replace("Cats", "Dogs"))    # "I like cats. Dogs are great."
```

Case sensitive. If you want to replace regardless of case, lowercase both sides first, or wait for Module 12 (regex), which handles this properly.

`.split()` breaks a string into a list of pieces. With no argument, it splits on any whitespace:

```python
sentence = "the quick brown fox"
parts = sentence.split()
print(parts)    # ['the', 'quick', 'brown', 'fox']
```

You can pass a separator:

```python
csv_line = "Ada,28,Engineer,Austin"
fields = csv_line.split(",")
print(fields)   # ['Ada', '28', 'Engineer', 'Austin']
```

And you can cap the number of splits with a second argument:

```python
full_name = "Mary Anne Smith"
first, last = full_name.split(" ", 1)
print(first)    # "Mary"
print(last)     # "Anne Smith"
```

That `1` says "split at most once, even if there are more spaces." Without it, `split(" ")` would give you three pieces, and `first, last = ...` would raise a `ValueError` because three things don't fit in two slots.

`.join()` is `.split()` running in reverse. It takes a sequence of strings and glues them with a separator:

```python
parts = ["the", "quick", "brown", "fox"]
sentence = " ".join(parts)
print(sentence)   # "the quick brown fox"

csv_row = ",".join(["Ada", "28", "Engineer", "Austin"])
print(csv_row)    # "Ada,28,Engineer,Austin"
```

The syntax reads backwards at first: the *separator* is the string you call `.join()` on, and the *pieces* are the argument. `" ".join(parts)` translates as "use `' '` to join up the elements of parts."

`.join()` is the right tool when you have several pieces and want to glue them with a consistent separator. It's much cleaner than concatenating with `+` repeatedly, and it handles edge cases (empty list, single element) without special-casing.

### Concatenation: `+`, f-strings, and `.join()`

You have three main ways to glue strings together. They're not interchangeable; each is best in a different situation.

**The `+` operator** works between two strings:

```python
first = "Ada"
last = "Lovelace"
full = first + " " + last
print(full)    # "Ada Lovelace"
```

The trap: `+` only works *between strings*. Mix a string and a number and you crash:

```python
age = 28
print("I am " + age + " years old.")
# TypeError: can only concatenate str (not "int") to str
```

Fix by converting the number with `str()`:

```python
print("I am " + str(age) + " years old.")
```

Or, much more readably, use an f-string:

```python
print(f"I am {age} years old.")
```

**f-strings** are usually the right answer when you're mixing text and variables. They're easier to read than concatenation, they don't require explicit `str()` calls, and they support format specifiers (coming up next). Use them by default.

**`.join()`** is the right answer when you have a *list* of strings (often built dynamically) and want one separator between each. Combining first/middle/last names where the middle name is sometimes missing? `.join()`. Building a comma-separated row for a CSV? `.join()`. Concatenating ten variables that you've named individually? f-string.

Don't reach for `+=` to build up a long string in a loop:

```python
result = ""
for word in ["one", "two", "three", "four"]:
    result += word + ", "   # works, but inefficient and clunky
```

`.join()` does this faster and more readably:

```python
result = ", ".join(["one", "two", "three", "four"])
```

(We haven't covered loops yet — that's Module 5 — but file this away for then.)

### Escape sequences

Sometimes you need a character in a string that's hard to type literally, either because it's invisible (a newline) or because it would confuse Python's parser (a quote inside a quoted string). Escape sequences are how you get them in.

An escape sequence is a backslash followed by another character. Python interprets the pair specially.

```python
print("Line 1\nLine 2")     # newline between them
print("Column1\tColumn2")   # tab between them
print("She said \"hi\"")    # literal double quote inside a double-quoted string
print("Path: C:\\Users")    # literal backslash
```

The common ones:

- `\n` — newline (line break)
- `\t` — tab
- `\"` — literal double quote (only needed inside `"..."`)
- `\'` — literal single quote (only needed inside `'...'`)
- `\\` — literal backslash

That last one matters more than it looks. A single backslash starts an escape sequence. If you actually want a backslash to appear in your string, you have to write `\\`. Forgetting this is a constant source of bugs with Windows file paths:

```python
path = "C:\new_folder\test.txt"   # broken: \n is a newline, \t is a tab
print(path)
# C:
# ew_folder       est.txt
```

Either escape the backslashes:

```python
path = "C:\\new_folder\\test.txt"
```

…or use forward slashes (which Python and Windows both accept in `open()`):

```python
path = "C:/new_folder/test.txt"
```

Or use a *raw string*, where `\` has no special meaning:

```python
path = r"C:\new_folder\test.txt"
```

The `r` prefix is the same idea as the `f` prefix on f-strings, just different behavior: it tells Python "don't interpret escape sequences in this string, treat the characters literally." Raw strings come back in Module 12 (regular expressions) where they're essential.

### Format specifiers: alignment, width, decimals

Back in Module 2, we saw `f"{price:.2f}"` for limiting a number to two decimal places. Format specifiers can do more. They control width, alignment, padding character, and the comma thousands separator.

The full syntax inside the braces is:

```
{value:[fill][align][width][.precision][type]}
```

That looks intimidating. In practice you'll only use a couple of pieces at a time.

```python
name = "Ada"
print(f"{name:<10}|")    # "Ada       |" — left-align in width 10
print(f"{name:>10}|")    # "       Ada|" — right-align in width 10
print(f"{name:^10}|")    # "   Ada    |" — center-align in width 10
```

The `<`, `>`, and `^` characters mean left-align, right-align, and center-align. The number after them is the field width. The `|` is just a literal character so you can see where the field ends.

Putting it together to build a tidy receipt:

```python
print(f"{'item':<20}{'price':>10}")
print(f"{'apples':<20}{2.49:>10.2f}")
print(f"{'bananas':<20}{0.99:>10.2f}")
print(f"{'total':<20}{3.48:>10.2f}")
```

Output:

```
item                     price
apples                    2.49
bananas                   0.99
total                     3.48
```

The left column is 20 characters wide, left-aligned. The right column is 10 characters wide, right-aligned, formatted as a float with 2 decimal places. We saw a version of this in Module 2's mini-project; now you know how the alignment characters work.

You can pad with a specific character instead of space, using the `[fill]` slot:

```python
print(f"{42:0>5}")      # "00042" — pad with zeros, right-aligned, width 5
print(f"{42:->5}")      # "---42" — pad with dashes, right-aligned, width 5
print("-" * 30)         # just print 30 dashes — a separator line
```

The zero-pad version is common when you want to format numbers as IDs or file names: `report_00042.csv`.

**Try it:** Given an email like `"  Ada.Lovelace@Example.COM  "`, write code that produces a clean username (`"ada.lovelace"`) and domain (`"example.com"`). Strip whitespace, lowercase everything, and split on the `@`.

<details>
<summary>Answer</summary>

```python
email = "  Ada.Lovelace@Example.COM  "
clean = email.strip().lower()
username, domain = clean.split("@")
print(username)   # "ada.lovelace"
print(domain)     # "example.com"
```

Three things to notice. First, method chaining: `email.strip().lower()` calls `.strip()` on the email, then `.lower()` on the result. Each method returns a new string, and you can call the next method directly on it. Second, the assignment `username, domain = clean.split("@")` unpacks the two-element list from `.split("@")` into two variables on one line. Third, `.split("@")` would fail if there were no `@` or more than one — we're trusting the input. Real email validation lives in Module 12.

</details>

## Common pitfalls

**1. Treating string methods as if they modified in place.**

```python
name = "ada"
name.upper()
print(name)   # "ada" — unchanged
```

`.upper()` returned a new string. We threw it away. Capture it:

```python
name = "ada"
name = name.upper()
print(name)   # "ADA"
```

Equivalently, use it inline: `print(name.upper())`.

**2. Forgetting that slice `stop` is exclusive.**

```python
word = "Python"
print(word[0:4])    # "Pyth" — 4 characters, positions 0 through 3
```

If you want N characters starting at position `start`, the stop is `start + N`, not `start + N - 1`.

**3. Indexing past the end of a string.**

```python
name = input("Name: ")    # user just hits enter
first_letter = name[0]
# IndexError: string index out of range
```

Always assume `input()` can return `""`. Defensive code checks `if name:` (Module 4) before slicing or indexing.

**4. Forgetting `()` when calling a method.**

```python
name = "ada"
print(name.upper)     # <built-in method upper of str object at 0x...>
print(name.upper())   # "ADA"
```

The first prints the method itself, like printing a phone number instead of dialing it. Always include the parentheses.

**5. Using `+` between a string and a number.**

```python
age = 30
print("Age: " + age)
# TypeError: can only concatenate str (not "int") to str
```

Convert with `str()`, or — better — use an f-string: `print(f"Age: {age}")`.

**6. Treating `.find()`'s `-1` return value as a found position.**

```python
text = "hello"
position = text.find("z")          # -1
print(text[position:position+3])   # "o" — almost certainly not what you want
```

Either check `if position != -1:` (Module 4), or just use `if "z" in text:` when you only care about presence.

## How this connects

In Module 1, strings were inert text you'd assign to a variable and print. In Module 2, they were the awkward intermediate form between the user's keystrokes and the numbers you wanted. Module 3 promotes strings to a full data type you can manipulate as deliberately as numbers. From here on, every module leans on this:

- **Module 4** (conditionals) will use `in`, `.startswith()`, and string equality to make decisions.
- **Module 5** (loops) will iterate over the characters of a string and over the lists produced by `.split()`.
- **Module 7** (lists and dictionaries) gives the lists you've been getting from `.split()` a proper introduction. Indexing and slicing carry over almost unchanged.
- **Module 11** (files) is mostly about reading lines of text from disk and feeding them straight into the string methods you learned here.
- **Module 12** (regular expressions) starts where `.find()` and `.replace()` give out — when patterns get complicated enough that exact-match tools don't cut it.

If the slicing syntax (`s[start:stop:step]`) feels wobbly, give it the most practice. It comes back for lists in Module 7 with the exact same rules.

## Recap

- Strings are zero-indexed sequences. `s[0]` is the first character; `s[-1]` is the last.
- Slicing is `s[start:stop:step]`. `stop` is exclusive. Missing values default to the start and end of the string. A negative step walks backward; `s[::-1]` reverses.
- Strings are immutable. Every string method returns a new string and leaves the original alone. If you want to keep the result, reassign it.
- The core methods worth knowing reflexively: `.lower()`, `.upper()`, `.strip()`, `.replace()`, `.split()`, `.join()`, `.find()`, `.count()`, `.startswith()`, `.endswith()`, and the `in` operator.
- Three ways to combine strings: `+` for two literals, f-strings for mixing text and variables, `.join()` for sequences of pieces.
- Escape sequences (`\n`, `\t`, `\\`, `\"`) embed special characters. Raw strings (`r"..."`) turn the escapes off — useful for file paths and regex.
- Format specifiers (`<`, `>`, `^` for alignment; a number for width; `.2f` for decimal places; `,` for thousands separators) let f-strings produce tidy aligned output.

## Up next

Module 4 introduces conditionals — `if`, `elif`, `else` — and the comparison operators that go with them. Your programs will start making decisions based on what the user typed, what the file contained, or what a calculation produced.

Now go work the exercises and mini-project for Module 3 in the curriculum doc. The exercises drill the methods one at a time; Mad Libs puts half a dozen of them together in a single program.
