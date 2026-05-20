# Module 12: Regular Expressions

## Why this matters

Imagine you've just been handed a file with five thousand lines like this:

```
2026-03-14 09:14:22 INFO  user=alice ip=10.0.0.5 path=/login status=200
2026-03-14 09:14:23 ERROR user=bob   ip=10.0.0.9 path=/admin status=403
```

Your job: pull out every line where the status starts with 4, grab the IP, and count which IPs got rejected the most. The string methods you know from Module 3 can technically do this. You'd split on spaces, then split each chunk on `=`, then check whether `status[0]` is `"4"`. Forty lines of code. Brittle. Breaks the day someone changes the log format.

The same job in regex is one pattern and a `for` loop. That's the trade. You learn a small, dense language for describing patterns in text, and you get to skip the forty lines of slicing-and-checking forever after. Validating that something looks like an email. Pulling phone numbers out of a paragraph. Replacing every four-digit year in a document with `[REDACTED]`. Anything where the answer is "find the things that look like *this* in some text" is what regex is for.

Two warnings up front. Regex looks like punctuation soup; a pattern like `^[\w.+-]+@[\w-]+\.[\w.-]+$` takes practice before it stops looking hostile. And regex is the wrong tool for anything with nested structure: HTML, JSON, source code. If you've heard the joke that "now you have two problems," it's about people who tried to parse HTML with regex. Use it for flat patterns. For nested data, use a real parser.

## What you'll be able to do by the end

- Read and write regex patterns using the core building blocks: `.`, `*`, `+`, `?`, `\d`, `\w`, `\s`, `[]`, `^`, `$`, `()`.
- Pick the right function from the `re` module for the job: `search`, `match`, `findall`, or `sub`.
- Always use raw strings (`r"..."`) for patterns and explain why.
- Pull captured values out of a match with `.group(1)` and `.groups()`.
- Recognize when regex is the wrong tool and reach for `.split()`, `csv`, or `json` instead.

## Prerequisites

You need strings (Module 3), conditionals (Module 4), loops (Module 5), and imports (Module 10). File I/O from Module 11 shows up in the mini-project, since regex earns its keep on file contents you've loaded. If string methods like `.split()`, `.strip()`, and `.find()` aren't reflexive, work the Module 3 exercises again before continuing. Regex is a sharper tool for the same kind of work, and it helps to know what the blunter tool looks like.

## Core concepts

### Why the string methods aren't enough

Suppose you want to check whether a user typed in something that looks like an email address. Your first instinct is reasonable:

```python
email = input("Email: ").strip()
if "@" in email:
    print("Valid")
else:
    print("Invalid")
```

Run it. Type `alice@example.com`. It says `Valid`. Type `not-an-email`. It says `Invalid`. So far so good. Now type `@`. Just the single `@` character.

It says `Valid`.

That's wrong. There's nothing in front of the `@` and nothing after it; it's not an email. So you patch:

```python
email = input("Email: ").strip()
if "@" in email and email.count("@") == 1:
    local, domain = email.split("@")
    if local and domain and "." in domain:
        print("Valid")
    else:
        print("Invalid")
else:
    print("Invalid")
```

Now type `a@b.c`. It says `Valid`. Then `alice@@example.com`. `Invalid`, good. Then `.@.`. `Valid`. Wait, no.

Every fix uncovers another edge case. After half an hour you've got thirty lines of code and a queasy feeling that you're missing something. You are. The shape "letters and a few symbols, then `@`, then letters and dots and a top-level domain" is a *pattern*, and the string methods don't speak pattern. They speak position and substring. Regex speaks pattern.

### The `re` module and `re.search`

Python's regex library is built into the standard library as `re`. The first function to learn is `re.search`.

```python
import re

email = "alice@example.com"
if re.search(r"@", email):
    print("Has an @")
```

Three things going on. `re.search(pattern, string)` looks for the pattern anywhere in the string. It returns a *match object* (which is truthy) if it finds one, and `None` (which is falsy) if it doesn't. The pattern is `r"@"`, just the literal character `@`. At this point we're no better off than `if "@" in email`. The power comes when the pattern is something other than literal text.

### Raw strings, and why you'll forget once

You may have noticed the `r` in front of the pattern: `r"@"`. That `r` makes it a raw string. In a normal Python string, the backslash starts an escape sequence: `"\n"` is a newline, `"\t"` is a tab. In a raw string, the backslash is just a backslash. The string `"\d"` and the string `r"\d"` print the same way, so right now the `r` looks pointless. It isn't.

Regex uses backslashes for its own special sequences (`\d` for digit, `\b` for word boundary, and so on). If you write a pattern in a non-raw string, Python sees the backslash first and tries to interpret it before the `re` module ever gets a look. Sometimes Python doesn't recognize the sequence and passes it through, so the pattern works by accident. Sometimes Python does recognize it (`"\b"` is a backspace character in a regular Python string) and you get a pattern that silently means something different from what you intended.

Always use raw strings for regex. `r"\d+"`, not `"\d+"`. Burn this in. It will save you an hour of debugging at least once.

### Special symbols: matching things that aren't literal

Regex patterns mostly look like text with a few special symbols sprinkled in. The symbols you'll use 95% of the time:

| Symbol | Meaning |
|---|---|
| `.` | Any single character except a newline |
| `\d` | Any digit (0-9) |
| `\w` | Any word character (letter, digit, underscore) |
| `\s` | Any whitespace (space, tab, newline) |
| `[abc]` | Any one of the characters `a`, `b`, or `c` |
| `[^abc]` | Any character *except* `a`, `b`, or `c` |
| `[a-z]` | Any lowercase letter |
| `*` | The thing before it, zero or more times |
| `+` | The thing before it, one or more times |
| `?` | The thing before it, zero or one time |
| `{3}` | The thing before it, exactly three times |
| `{2,4}` | The thing before it, between two and four times |
| `^` | Start of the string |
| `$` | End of the string |
| `\|` | Or (either the thing on the left or the right) |
| `(...)` | A group (more on this soon) |

You won't memorize this table on one read. Keep it open while you work the exercises. You'll know the common ones (`\d`, `+`, `*`, `[]`) reflexively within a few days.

### Building up the email validator

Back to the email problem. We want something with characters, then `@`, then characters, then `.`, then more characters.

A first try:

```python
import re

email = input("Email: ").strip()
if re.search(r".+@.+", email):
    print("Valid")
else:
    print("Invalid")
```

`.+` means "one or more of any character." So this pattern says: one or more characters, then `@`, then one or more characters. Let's run it.

- `alice@example.com` → Valid. Good.
- `@` → Invalid. Good (no characters before or after).
- `a@b` → Valid. Hmm, that has no dot.
- `my email is alice@example.com please reply` → Valid. But we wanted just an email, not a sentence containing one.

Two problems. We're not requiring a dot in the domain, and we're not requiring the whole input to be an email. The first fix is to change the pattern to `r".+@.+\..+"`. `\.` is a literal dot. (Remember, `.` by itself means any character; `\.` means an actual period.) So now we require: stuff, `@`, stuff, `.`, stuff. Better. But `my email is alice@example.com` still matches, because `re.search` looks for the pattern *anywhere*. The fix for that is anchors: `r"^.+@.+\..+$"`. `^` says the match has to start at the beginning of the string; `$` says it has to end at the end. Now `my email is alice@example.com` fails, because the leading "my email is " isn't part of the pattern. Run it again on the test cases and most look right.

Still, this is permissive. Spaces inside the local part would still match. Email validation goes deep, and we'll stop at "good enough." Here's a respectable version:

```python
PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

def is_valid_email(email):
    return bool(PATTERN.match(email))
```

Reading left to right:

- `^`: match starts at the beginning.
- `[\w.+-]+`: one or more characters from the set: word characters, dot, plus, or hyphen. (Inside `[]`, most special characters lose their special meaning, including the dot.)
- `@`: a literal `@`.
- `[\w-]+`: one or more word characters or hyphens.
- `\.`: a literal dot.
- `[\w.-]+`: one or more word characters, dots, or hyphens.
- `$`: match ends at the end.

`re.compile` builds the pattern once and lets you reuse it. If you're going to use the same pattern many times (in a loop, in a function called repeatedly), compile it; it's faster. Otherwise the inline `re.search(r"...", text)` form is fine.

Full RFC-compliant email validation is famously unwinnable. The canonical regex is over six thousand characters and still doesn't cover everything. The pattern above catches the addresses that look like addresses to a human. For real applications, send the user a verification email; the only true test is whether mail to that address gets read.

**Try it.** Sketch a pattern that matches a US zip code, which is exactly five digits (e.g., `78664`), optionally followed by a hyphen and four more digits (e.g., `78664-1234`).

<details>
<summary>Answer</summary>

```python
import re

PATTERN = re.compile(r"^\d{5}(-\d{4})?$")

print(bool(PATTERN.match("78664")))       # True
print(bool(PATTERN.match("78664-1234")))  # True
print(bool(PATTERN.match("786")))         # False
print(bool(PATTERN.match("78664-12")))    # False
```

`\d{5}` means exactly five digits. `(-\d{4})?` is a group containing a hyphen and four digits, and the `?` after the group makes the whole group optional. The `^` and `$` anchors keep extra characters from sneaking in.

</details>

### `search` vs `match`

The `re` module gives you two similar functions, and the difference catches people:

- `re.search(pattern, string)` looks for the pattern *anywhere* in the string.
- `re.match(pattern, string)` only matches at the *beginning* of the string.

```python
import re

print(re.match(r"world", "hello world"))   # None
print(re.search(r"world", "hello world"))  # <re.Match object>
```

`re.match` doesn't anchor at the end, just the start. So `re.match(r"hello", "hello world")` succeeds even though the string keeps going. If you want the pattern to cover the *whole* string, use `re.fullmatch` or put `^` and `$` around the pattern and use `search`.

A common bug: writing `re.match(r"world", text)` expecting it to find `world` somewhere in `text`, and not understanding why it returns `None` when `text` contains `world` in the middle. The fix is `re.search`. If you remember only one thing about these two: use `search` by default. Reach for `match` only when you want to require the pattern at the start.

### `findall`: pull out every match

`re.search` gives you the first match. When you want all of them, use `re.findall`. It returns a list of strings.

```python
import re

text = "Reach me at 512-555-0102 or 800-555-0199 or even 212-555-0123."
matches = re.findall(r"\d{3}-\d{3}-\d{4}", text)
print(matches)
# ['512-555-0102', '800-555-0199', '212-555-0123']
```

The pattern is three digits, hyphen, three digits, hyphen, four digits. `findall` walks the string and pulls out every chunk that matches.

Real phone numbers come in a dozen formats. `(512) 555-0102`. `512.555.0102`. `+1 512 555 0102`. A more forgiving pattern uses character classes for the separators:

```python
pattern = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
```

Reading it: an optional opening paren, three digits, an optional closing paren, an optional separator (hyphen, dot, or whitespace), three more digits, another optional separator, four more digits. The `?` after each separator section is what makes them optional.

This is the part of regex that takes practice. You don't write a complete pattern from the top of your head. You write a rough one, run it on sample data, find what it misses, and tweak. The cycle is: pattern, test, refine. Treat it like debugging.

### Groups: capturing pieces of a match

Often you don't want the whole match; you want a piece of it. Say you've matched a phone number and you want just the area code. Parentheses around part of a pattern create a *group* you can pull out later.

```python
import re

text = "Reach me at 512-555-0102."
match = re.search(r"(\d{3})-(\d{3})-(\d{4})", text)

print(match.group(0))   # 512-555-0102  (the whole match)
print(match.group(1))   # 512           (first group)
print(match.group(2))   # 555           (second group)
print(match.group(3))   # 0102          (third group)
print(match.groups())   # ('512', '555', '0102')
```

`.group(0)` (or just `.group()`) is the whole match. `.group(1)` is whatever the first parenthesized group captured. `.groups()` returns all of them as a tuple.

When you use `findall` with a pattern that contains groups, the return value changes shape. Instead of a list of full matches, you get a list of tuples, one tuple per match, with the groups in order.

```python
matches = re.findall(r"(\d{3})-(\d{3})-(\d{4})", "Call 512-555-0102 or 800-555-0199.")
print(matches)
# [('512', '555', '0102'), ('800', '555', '0199')]
```

If you didn't want groups in the result but you did want to *group* part of the pattern for `?` or `+` to apply to (the way we did with `(-\d{4})?` in the zip code), use a non-capturing group: `(?:...)`. It looks weird, but it does the same job as a regular group without showing up in `findall` or `.groups()`.

### `re.sub`: find and replace with patterns

`re.sub` takes a pattern, a replacement string, and the text to operate on. It returns a new string with every match replaced.

```python
import re

text = "I was born in 1985, started school in 1990, and graduated in 2007."
result = re.sub(r"\b(19|20)\d{2}\b", "[YEAR]", text)
print(result)
# I was born in [YEAR], started school in [YEAR], and graduated in [YEAR].
```

Two new things. `\b` is a word boundary, an invisible position between a word character and a non-word character. It keeps the pattern from matching inside a longer number; without it, a string like `19850` would match `1985`. The `(19|20)` is a group with an alternation: match `19` or `20`. So the whole pattern reads: a word boundary, then `19` or `20`, then two more digits, then another word boundary.

You can reference captured groups in the replacement string with `\1`, `\2`, and so on. Handy for reformatting:

```python
text = "John Smith, Alice Jones, Bob Brown"
result = re.sub(r"(\w+) (\w+)", r"\2, \1", text)
print(result)
# Smith, John, Jones, Alice, Brown, Bob
```

The pattern captures first name and last name into groups 1 and 2; the replacement flips them. Notice the replacement is also a raw string, for the same reason patterns are.

**Try it.** Given the text `"Order #1042 shipped on 2026-03-14. Order #1085 shipped on 2026-04-02."`, write code that prints every order number along with the date it shipped, in the format `1042: 2026-03-14`.

<details>
<summary>Answer</summary>

```python
import re

text = "Order #1042 shipped on 2026-03-14. Order #1085 shipped on 2026-04-02."
pattern = re.compile(r"#(\d+) shipped on (\d{4}-\d{2}-\d{2})")

for order, date in pattern.findall(text):
    print(f"{order}: {date}")

# 1042: 2026-03-14
# 1085: 2026-04-02
```

Two capture groups: the digits after `#`, and the date in `YYYY-MM-DD` form. Because the pattern has groups, `findall` returns tuples, which unpack cleanly into `order, date` in the loop.

</details>

### When regex is the wrong tool

Regex is for flat, predictable patterns. It falls apart on anything with nested or recursive structure.

- **HTML.** Tags can be nested arbitrarily deep. Regex can't count nesting. Use a parser like `BeautifulSoup`.
- **JSON.** Same problem: nested braces and brackets. Use the `json` module from Module 11.
- **CSV.** Quoted fields can contain commas. Use the `csv` module.
- **Source code.** Parsing programming languages needs context regex doesn't have.

A useful rule: if a `.split()` would solve your problem, use `.split()`. If the data has a parser in the standard library, use the parser. Regex is for the gap between "trivial to split" and "needs a real parser."

## Common pitfalls

**1. Forgetting the raw string.**

```python
pattern = "\d+"   # works by accident
pattern = "\b\w+\b"   # broken: \b is a backspace character in a regular string
```

The first happens to work because Python doesn't recognize `\d` and leaves it alone. The second breaks because Python *does* recognize `\b` and turns it into a single backspace character before `re` ever sees it. Always use `r"..."`.

**2. Using `match` when you wanted `search`.**

```python
re.match(r"error", "log line with error in middle")  # None
re.search(r"error", "log line with error in middle")  # match
```

`match` anchors at the start. `search` looks anywhere. Use `search` unless you need start-anchoring.

**3. Forgetting to escape the dot.**

```python
re.search(r".com", "shopping at example.com")   # matches
re.search(r".com", "Wescom Bank")                # also matches!
```

The unescaped `.` matches any character, including the `s` in "Wescom." Use `\.` when you want a literal period.

**4. Greedy quantifiers swallowing too much.**

```python
text = "<b>hello</b> and <b>world</b>"
re.findall(r"<b>(.*)</b>", text)
# ['hello</b> and <b>world']
```

`.*` is *greedy*; it grabs as many characters as possible before giving up just enough to let the rest of the pattern match. Use `.*?` (lazy) to grab as few as possible:

```python
re.findall(r"<b>(.*?)</b>", text)
# ['hello', 'world']
```

And then notice we're parsing HTML with regex, which is the thing you weren't supposed to do. The point stands for any greedy-vs-lazy situation in real flat text.

**5. Forgetting that `findall` changes shape when there are groups.**

```python
re.findall(r"\d{3}-\d{4}", "call 555-0102 or 555-0199")
# ['555-0102', '555-0199']  (list of strings)

re.findall(r"(\d{3})-(\d{4})", "call 555-0102 or 555-0199")
# [('555', '0102'), ('555', '0199')]  (list of tuples)
```

No groups: list of matches. One or more groups: list of tuples. Two groups in the pattern means you'll be unpacking two-tuples in your loop.

**6. Trying to validate something with `re.search` and no anchors.**

```python
re.search(r"\d{5}", "78664 Main St, apt 12")   # matches "78664"
```

If you wanted to validate that the input *is* a five-digit number and nothing else, you needed `^\d{5}$`. Without anchors, you're asking "does it contain a five-digit number," not "is it a five-digit number." Use `^...$` or `re.fullmatch` for validation.

## How this connects

Looking back, regex is the natural sequel to two earlier modules. Module 3's string methods (`.split()`, `.find()`, `.replace()`) are the tool for simple, predictable text work; regex is what you reach for when "predictable" gets too vague. Module 11's file I/O is what regex usually operates on: log files, CSVs with messy fields, plain text exports. The mini-project for this module ties both together, since you'll open a log file and parse its lines with a pattern.

Looking forward, Module 13's classes will sometimes hold compiled patterns as class attributes for repeated use. Module 14's tests are a good place to pin down regex behavior with explicit examples (regex bugs are sneaky, and a test that says "this pattern matches *these* inputs and rejects *those*" is worth its weight). In real-world Python code, you'll see regex in form validators, in `pandas` string operations, in template renderers, and in any tool that takes user input or processes log output. It's one of the highest-leverage skills in the language.

## Recap

- Regex is a small language for describing patterns in text. Reach for it when the pattern is too varied for plain string methods and too flat for a dedicated parser.
- Always write patterns as raw strings: `r"\d+"`. The `r` keeps Python from interpreting backslashes before regex sees them.
- The core building blocks: `.` (any char), `\d` (digit), `\w` (word char), `\s` (whitespace), `[...]` (character set), `*` (zero or more), `+` (one or more), `?` (zero or one), `{n}` and `{n,m}` (counts), `^` and `$` (anchors), `(...)` (capture group), `|` (alternation).
- The functions: `re.search` finds anywhere, `re.match` only at the start, `re.findall` returns every match, `re.sub` replaces matches. Use `search` by default.
- `match.group(n)` pulls out captured groups; `.groups()` returns them as a tuple.
- `re.findall` returns a list of strings when the pattern has no groups, and a list of tuples when it has groups.
- Don't use regex for HTML, JSON, or anything with nested structure. Use a real parser.

## Up next

Module 13 introduces object-oriented programming: defining your own data types with `class`, attaching behavior to them with methods, and using inheritance to share code between related types. It's a shift in how you organize a program, and it's the foundation for almost every larger Python codebase you'll touch.

Now go work the exercises and mini-project for Module 12 in the curriculum doc. The log parser is where every piece of this lecture comes together: opening a file, applying a pattern, capturing groups, and counting results.
