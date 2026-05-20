# Module 8: Dictionaries and Sets

## Why this matters

Lists got you a long way. Any time you had a bunch of similar things in a row (students, prices, log lines), a list was the right shape. But lists put values *in order*, and order is often the wrong way to find things.

Here's what that looks like. Say you're tracking people's ages. With lists, you'd do this:

```python
names = ["Ada", "Grace", "Linus", "Guido"]
ages = [25, 30, 40, 35]
```

Two lists. The implicit promise is that `ages[i]` is the age of `names[i]`. Now suppose you want Grace's age. You'd write:

```python
i = names.index("Grace")
age = ages[i]
```

That works, but it's already fragile. Sort `names` alphabetically without sorting `ages` to match, and the entire structure is silently corrupted: every age is now attached to the wrong person and Python has no way to notice. Add a new person and forget to add their age in both lists, same problem. Delete one entry from `names` and forget to delete the matching index from `ages`, same problem.

The fix is a data structure that lets you look up values *by name* instead of by position. That's a dictionary. With a dictionary, the two lists collapse into one thing:

```python
ages = {"Ada": 25, "Grace": 30, "Linus": 40, "Guido": 35}
print(ages["Grace"])   # 30
```

One variable. One source of truth. No way for the names and ages to drift apart. And `"Grace"` is a meaningful name, not a fragile index that has to be hunted down.

Dictionaries are also the shape of basically all structured data you'll meet outside Python. JSON, the format used by almost every web API, is dictionaries (and lists of dictionaries) all the way down. Once you've learned dictionaries, you've learned the shape of the world's data.

Sets, the other half of this module, are the answer to a smaller but constant problem: "give me the unique values" and "is this value in the collection, yes or no, fast." We'll get there.

## What you'll be able to do by the end

- Create a dictionary, read from it, write to it, and delete from it.
- Use `.get()` to read a key safely without crashing on missing data.
- Iterate over a dictionary's keys, values, or both at once.
- Build a word-frequency counter or any other "count things up by category" pattern.
- Recognize the JSON-shaped layout of lists of dictionaries and nested dictionaries.
- Use a set for deduplication and fast membership tests.
- Explain why a list can't be a dictionary key but a tuple can.

## Prerequisites

You need Module 7 fluent: lists, tuples, indexing, iteration, and the difference between mutable and immutable values. The "why can't a list be a dict key" question (which is the curriculum's checkpoint) leans hard on understanding that tuples can't change after creation and lists can.

You also need functions from Module 6, because most exercises ask you to write a function that takes a dictionary and returns something derived from it.

## Core concepts

### Creating a dictionary

A dictionary is written with curly braces, and each entry is a `key: value` pair, separated by commas.

```python
person = {"name": "Ada", "age": 25, "is_student": False}
empty = {}
```

Keys are usually strings, but they can also be numbers, tuples, and a few other things we'll get to. Values can be anything: strings, numbers, lists, other dictionaries.

You read a value by putting its key in square brackets:

```python
person = {"name": "Ada", "age": 25}
print(person["name"])   # Ada
print(person["age"])    # 25
```

That syntax looks a lot like list indexing. The difference is that you're indexing by a meaningful key (a name) instead of by position (a number).

You write to a key the same way:

```python
person = {"name": "Ada", "age": 25}
person["age"] = 26              # update existing key
person["is_student"] = False    # add new key
print(person)   # {'name': 'Ada', 'age': 26, 'is_student': False}
```

The same syntax adds a key if it doesn't exist and updates it if it does. That's convenient but worth knowing about, because there's no warning when you create a new key by accident with a typo.

### KeyError: the first thing that bites you

Try to read a key that doesn't exist:

```python
person = {"name": "Ada", "age": 25}
print(person["address"])
```

What do you expect? `None`? An empty string? Nope:

```
KeyError: 'address'
```

Python refuses to guess. If you ask for a key that isn't there, the program crashes. This is one of the most common errors when working with dictionaries, especially if your data comes from somewhere unpredictable (user input, a file, an API).

Two ways to handle it. The first is to check before reading:

```python
person = {"name": "Ada", "age": 25}
if "address" in person:
    print(person["address"])
else:
    print("(no address on file)")
```

`in` on a dictionary checks whether a key exists. It works just like `in` on a list, but it checks keys, not values.

The second way is cleaner for "give me this or a default" patterns: the `.get()` method.

```python
person = {"name": "Ada", "age": 25}
print(person.get("address"))                # None
print(person.get("address", "unknown"))     # unknown
```

`.get(key)` returns `None` if the key is missing instead of raising. `.get(key, default)` lets you specify what to return when the key is missing.

Use `.get()` whenever a missing key isn't a programming bug, just an expected absence. Use `d[key]` when the key absolutely should be there and a missing one means something is wrong (so a crash is appropriate).

### The classic: counting things

Here's a problem you'll run into in your first week of writing real Python: given a sentence, count how many times each word appears. The natural first attempt:

```python
sentence = "the quick brown fox the lazy fox"
counts = {}
for word in sentence.split():
    counts[word] += 1
```

What do you expect? Maybe `{'the': 2, 'quick': 1, 'brown': 1, 'fox': 2, 'lazy': 1}`. What you get:

```
KeyError: 'the'
```

The very first iteration crashes. Why? Because `counts[word] += 1` is shorthand for `counts[word] = counts[word] + 1`, and on the first iteration `counts["the"]` doesn't exist yet. You're trying to read a key that hasn't been written yet, then add one to it.

The fix is `.get()` with a default of zero:

```python
sentence = "the quick brown fox the lazy fox"
counts = {}
for word in sentence.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)
# {'the': 2, 'quick': 1, 'brown': 1, 'fox': 2, 'lazy': 1}
```

`counts.get(word, 0)` returns the current count if we've seen the word before, or zero if we haven't. Then we add one and store it back. Same shape, works on the first iteration.

This "look up with a default, modify, store back" pattern shows up constantly: counting words, tallying votes, grouping items by category, building a histogram. Memorize it.

**Try it:** Without running the code, what does this print?

```python
votes = {"yes": 3, "no": 1}
votes["yes"] += 1
votes["maybe"] = votes.get("maybe", 0) + 1
print(votes)
```

<details>
<summary>Answer</summary>

```
{'yes': 4, 'no': 1, 'maybe': 1}
```

The first update works because `"yes"` already exists, so `+= 1` reads the current value and stores it back as 4. The second line uses `.get("maybe", 0)` because `"maybe"` doesn't exist yet, so it returns 0, we add 1, and store it. If you'd written `votes["maybe"] += 1`, the program would have crashed with a `KeyError`.

</details>

### Removing keys

Two ways to remove a key:

```python
person = {"name": "Ada", "age": 25, "city": "London"}
del person["age"]
print(person)   # {'name': 'Ada', 'city': 'London'}
```

`del` deletes by key. It raises `KeyError` if the key doesn't exist, same as a missing read.

```python
person = {"name": "Ada", "city": "London"}
city = person.pop("city")
print(city)     # London
print(person)   # {'name': 'Ada'}
```

`.pop(key)` removes the key and returns its value. Useful when you want to both delete and use the value. Like `del`, it raises `KeyError` if the key is missing. Like `.get()`, you can pass a second argument as a default to make the missing case silent:

```python
person = {"name": "Ada"}
person.pop("city", None)   # silently does nothing
```

That two-argument form is the easy way to write "delete this key if it exists, otherwise leave it alone."

### Iterating over a dictionary

Here's a confusion that catches almost everyone. What does this print?

```python
person = {"name": "Ada", "age": 25, "city": "London"}
for x in person:
    print(x)
```

Maybe you guessed it prints the key-value pairs. Or just the values. What it actually prints:

```
name
age
city
```

Just the keys. When you iterate over a dictionary with the plain `for x in d` syntax, Python loops over the keys. The values come along for the ride but aren't part of the loop variable.

If you want just the keys, you can be more explicit (and it's the same result):

```python
for key in person.keys():
    print(key)
```

If you want just the values:

```python
for value in person.values():
    print(value)
```

If you want both at once, which is what you usually want, use `.items()`:

```python
for key, value in person.items():
    print(f"{key}: {value}")
```

```
name: Ada
age: 25
city: London
```

`.items()` produces pairs of `(key, value)`, and the `key, value` on the left side of `for` is just tuple unpacking from Module 7. This pattern is everywhere in real Python code. The moment you find yourself doing `for k in d: ... d[k] ...`, switch to `for k, v in d.items()` and your code gets shorter and faster in one move.

### `.update()` and merging

Two dictionaries can be merged with `.update()`:

```python
defaults = {"theme": "dark", "font_size": 12, "autosave": True}
user_settings = {"font_size": 14, "language": "en"}
defaults.update(user_settings)
print(defaults)
# {'theme': 'dark', 'font_size': 14, 'autosave': True, 'language': 'en'}
```

`defaults` gets every key from `user_settings`. New keys (`language`) are added. Existing keys (`font_size`) are overwritten. This is the classic "defaults plus user overrides" pattern.

Note that `defaults` was mutated. If you want a new dict instead, use the `|` operator (Python 3.9+) or `dict()`:

```python
merged = defaults | user_settings   # new dict, both originals untouched
```

### Lists of dictionaries: the JSON shape

Most real-world data is a list of dictionaries. Each dictionary is one record; the list is a collection of records.

```python
todos = [
    {"title": "Buy milk", "done": False, "priority": 2},
    {"title": "Fix server", "done": True, "priority": 1},
    {"title": "Write Module 8", "done": False, "priority": 1},
]
```

That shape is what an API typically returns. It's also what you'd save to a JSON file (Module 11). Iterating over it is a `for` loop where the loop variable is a whole dictionary:

```python
for task in todos:
    status = "[x]" if task["done"] else "[ ]"
    print(f"{status} {task['title']}")
```

```
[ ] Buy milk
[x] Fix server
[ ] Write Module 8
```

Filtering down to incomplete tasks is a list comprehension where the test reaches into each dictionary:

```python
incomplete = [t for t in todos if not t["done"]]
```

Sorting works the same way, with a `key` function that pulls out the field you want to sort by:

```python
todos.sort(key=lambda t: t["priority"])
```

The `lambda` is a Module 14 topic. For now, read it as "a tiny anonymous function that takes one task and returns its priority." `sort` calls it on each item and uses the result to compare. You'll see this pattern in nearly every script that processes structured data.

### Nested dictionaries

Values can be dictionaries too, which gives you nested structure:

```python
users = {
    "ada": {"age": 25, "city": "London"},
    "grace": {"age": 30, "city": "NYC"},
}
print(users["ada"]["city"])   # London
users["ada"]["age"] = 26
```

The double-bracket lookup is "get the dict at key `'ada'`, then get the key `'city'` from that dict." If either lookup fails, you get a `KeyError`. For deeply nested data with optional fields, chained `.get()` calls help:

```python
city = users.get("margaret", {}).get("city", "unknown")
```

That reads as "if `margaret` exists, look up her city; otherwise treat her record as an empty dict and look up city in that, which produces `unknown`." Ugly but safe.

### Why can't a list be a dictionary key?

Try this:

```python
d = {[1, 2]: "first"}
```

```
TypeError: unhashable type: 'list'
```

You can use strings, numbers, tuples, and booleans as keys. You can't use lists, other dictionaries, or sets. The rule is that keys have to be *hashable*.

Hashable means Python can compute a stable numeric fingerprint from the value, called its *hash*. The dictionary uses that fingerprint to find the value in memory fast. The dictionary computes the hash once, when you put a key in, and looks it up by hash every time you read from it.

The problem with using a list as a key is that lists can change. Imagine:

```python
key = [1, 2]
d = {key: "first"}     # Python stores it under hash([1, 2])
key.append(3)          # the list has now changed
d[key]                 # what does this even mean?
```

The list you used as a key has mutated into a different list. Should the lookup still work? Should the entry move? Should it disappear? Python avoids the question by refusing to let you do it in the first place.

Tuples don't have this problem because they can't change after creation. Once you make `(1, 2)`, it's `(1, 2)` forever, so its hash is stable, and the dictionary can use it as a key without worry.

```python
locations = {
    (0, 0): "origin",
    (1, 0): "east of origin",
    (0, 1): "north of origin",
}
print(locations[(1, 0)])   # east of origin
```

This is one of the most common reasons to use tuples in real code: as compound keys for dictionaries. A pair of coordinates, a pair of IDs, a date plus a category. Any time you want to look something up by a combination of values, a tuple key is the move.

### Sets: when you only care about uniqueness

A set is a collection that holds each value at most once, and doesn't remember the order they were added in. Written with curly braces, like a dictionary, but with single values instead of `key: value` pairs:

```python
seen = {1, 2, 3, 2, 1}
print(seen)   # {1, 2, 3}
```

The duplicates were dropped automatically.

The most common use is deduplicating a list. The natural first instinct is to write a loop:

```python
names = ["Alice", "Bob", "Alice", "Charlie", "Bob"]
unique = []
for name in names:
    if name not in unique:
        unique.append(name)
print(unique)   # ['Alice', 'Bob', 'Charlie']
```

That works. It's also six lines of code where one line would do:

```python
unique = list(set(names))
print(unique)   # ['Alice', 'Bob', 'Charlie']
```

`set(names)` turns the list into a set, dropping duplicates. `list(...)` turns it back into a list. Done. (One catch: a set doesn't preserve order, so the deduplicated list might come out in a different order than the input. If order matters, the explicit loop is still the right choice.)

The other big reason to reach for a set is fast membership testing. `x in some_list` has to scan the list until it finds `x` or runs out. `x in some_set` uses the hash trick from earlier and is effectively instant, regardless of how big the set is. If you're going to check membership many times against the same collection, building a set first pays off:

```python
banned_users = set(load_banned_user_ids())   # build once
for request in incoming_requests:
    if request.user_id in banned_users:      # fast every time
        reject(request)
```

Empty set has a syntax catch worth flagging:

```python
not_a_set = {}        # this is an empty DICTIONARY, not a set!
real_set = set()      # THIS is an empty set
```

`{}` was claimed by dictionaries first, so Python uses `set()` for an empty set. Putting any value inside the braces (`{1}`, `{"a"}`) makes it a set; leaving it empty makes it a dict.

### Set operations

Sets support mathematical set operations directly:

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)   # union: everything in either set        {1, 2, 3, 4, 5, 6}
print(a & b)   # intersection: things in both           {3, 4}
print(a - b)   # difference: in a but not b             {1, 2}
print(a ^ b)   # symmetric difference: in one but not both  {1, 2, 5, 6}
```

These come up more than you might think. "Users who clicked X but didn't click Y" is `clicked_X - clicked_Y`. "Tags shared between two posts" is `tags_a & tags_b`. "All distinct visitors today" is `morning_visitors | afternoon_visitors`. Whenever you find yourself writing nested loops to compute these by hand, ask whether a set operation would say the same thing in one line.

### Dict and set comprehensions

We met list comprehensions in Module 7. The same syntax works for dictionaries and sets.

```python
# build a dict from a sequence
squares = {n: n ** 2 for n in range(5)}
print(squares)   # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# build a set with deduplication baked in
words = ["Alice", "bob", "ALICE", "Bob"]
unique_lower = {w.lower() for w in words}
print(unique_lower)   # {'alice', 'bob'}
```

The first uses `key: value` inside the braces, which makes it a dict comprehension. The second uses a single expression, which makes it a set comprehension. Both are idiomatic Python, both are worth recognizing on sight.

## Common pitfalls

1. **`KeyError` on a missing read.** `d[key]` raises if the key isn't there. Use `d.get(key)` or `d.get(key, default)` when missing is okay, or `if key in d:` when you need to branch on it.

2. **`counts[word] += 1` on a fresh key.** That shorthand expands to `counts[word] = counts[word] + 1`, and the read on the right side fails before the write happens. Use `counts[word] = counts.get(word, 0) + 1`.

3. **`for x in d` only loops over keys.** If you need both, use `.items()`. If you need only values, use `.values()`. Writing `for k in d: ... d[k] ...` is a tell that you should be using `.items()`.

4. **Trying to use a list (or another mutable) as a key.** `TypeError: unhashable type: 'list'`. Convert to a tuple first: `d[tuple(my_list)] = ...`. Same problem if you try to put a list in a set.

5. **`{}` for an empty set.** It's an empty dictionary. The empty set is `set()`. (This is one of the most Python-specific surprises in the whole language.)

6. **Mutating a dictionary while iterating over it.** Same family of bug as mutating a list during iteration. Python will sometimes raise `RuntimeError: dictionary changed size during iteration` and sometimes just give wrong results. If you need to delete keys while iterating, iterate over `list(d.keys())` (a snapshot) or build a new dictionary.

## Try it yourself

**Problem 1.** Write a function `word_count(text)` that returns a dictionary mapping each word in `text` to how many times it appears. Treat words case-insensitively, so "The" and "the" count as the same word.

<details>
<summary>Answer</summary>

```python
def word_count(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts

print(word_count("The quick brown fox the lazy fox"))
# {'the': 2, 'quick': 1, 'brown': 1, 'fox': 2, 'lazy': 1}
```

`text.lower()` collapses cases before splitting. The `.get(word, 0) + 1` pattern handles the first-encounter case without crashing.

</details>

**Problem 2.** Given two lists of names, return the names that appear in both, deduplicated. Bonus: do it in one line.

<details>
<summary>Answer</summary>

```python
def shared_names(a, b):
    return set(a) & set(b)

print(shared_names(
    ["Alice", "Bob", "Charlie", "Alice"],
    ["Bob", "Charlie", "Diana"],
))   # {'Bob', 'Charlie'}
```

Convert both to sets, intersect. The result is a set; wrap with `sorted(...)` if you want a list in alphabetical order.

</details>

**Problem 3.** What's wrong with this code, and how would you fix it?

```python
inventory = {"apples": 5, "bananas": 0, "cherries": 3}
for item in inventory:
    if inventory[item] == 0:
        del inventory[item]
print(inventory)
```

<details>
<summary>Answer</summary>

It mutates `inventory` while iterating over it, which on most Python versions raises:

```
RuntimeError: dictionary changed size during iteration
```

Fix by iterating over a snapshot of the keys:

```python
inventory = {"apples": 5, "bananas": 0, "cherries": 3}
for item in list(inventory.keys()):
    if inventory[item] == 0:
        del inventory[item]
print(inventory)   # {'apples': 5, 'cherries': 3}
```

Or build a new dictionary with a comprehension:

```python
inventory = {item: qty for item, qty in inventory.items() if qty != 0}
```

The comprehension is the cleanest version, and it makes "throw out the zero-quantity items" obvious at a glance.

</details>

## How this connects

Dictionaries and sets sit at the center of practical Python:

- **Module 9 (exceptions)** is where you'll learn to catch `KeyError` properly when you can't avoid it with `.get()`. The two work together: prevention with `.get()`, fallback with `try/except`.
- **Module 10 (modules and packages)** uses dictionaries internally for namespaces, and the `collections` module gives you specialized variants (`Counter`, `defaultdict`) that are dictionaries with the patterns from this module pre-baked.
- **Module 11 (files and JSON)** is where dictionaries earn their reputation. The `json` module converts between Python dictionaries and JSON text. The shape on disk is the shape you've been working with here.
- **Module 13 (object-oriented programming)** is in some sense a friendlier wrapper around dictionaries. Every Python object stores its attributes in an internal dictionary called `__dict__`. Classes give that dictionary a name, a type, and a set of behaviors.

If the JSON-shape (list of dicts, dicts of dicts) feels unfamiliar, take the time to do the phone book exercise and the concession stand mini-project before moving on. The "build something out of nested dicts and lists" reflex is what makes Module 11 (and the entire rest of your Python life) easy.

## Recap

- A dictionary is an unordered collection of `key: value` pairs. Look up values by key with `d[key]`.
- `d[key]` raises `KeyError` on a missing key. `d.get(key, default)` returns the default instead. Use `.get` when missing is fine and the bracket form when missing means a bug.
- `counts[word] = counts.get(word, 0) + 1` is the canonical "count things up" pattern.
- `for k in d` iterates keys only. Use `.items()` for `(key, value)` pairs, `.values()` for values.
- `.update(other)` merges another dict in, overwriting existing keys.
- Keys must be hashable. Strings, numbers, tuples, and booleans work. Lists, sets, and other dictionaries don't.
- Lists of dictionaries are the shape of JSON and the shape of most real data. Get comfortable iterating, filtering, and sorting them.
- A set is an unordered collection of unique values. `set(my_list)` deduplicates a list in one operation, and `x in some_set` is fast no matter how big the set.
- Sets support `|` (union), `&` (intersection), `-` (difference), and `^` (symmetric difference).
- Empty dict is `{}`. Empty set is `set()`. `{}` is never a set.

## Up next

Module 9 is exceptions. So far, when something has gone wrong (`KeyError` on a missing dict key, `ValueError` on `int("abc")`, `IndexError` on a list overshoot), your program has crashed. Module 9 is where you learn to catch those failures, recover from them, and raise your own when something is wrong with your inputs.

Now go work the exercises and mini-project for Module 8 in the curriculum doc. The word-frequency exercise drills the `.get(word, 0) + 1` pattern. The phone book exercise drills add/update/lookup/delete against a single dictionary. The concession stand mini-project is where you start combining a menu dictionary with a list of ordered items, which is the first real taste of the JSON-shaped multi-collection programs you'll be writing from now on.
