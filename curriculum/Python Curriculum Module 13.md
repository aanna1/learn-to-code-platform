# Module 13: Object-Oriented Programming

## Why this matters

Picture this. You're building a course management system. You have two hundred students, each with a name, an ID, a list of grades, and a major. You want to print transcripts, compute GPAs, send reminder emails, and check who's failing.

You start with parallel lists:

```python
names = ["Alice", "Bob", "Carol"]
ids = [101, 102, 103]
grades = [[88, 92], [77, 85], [99, 96]]
majors = ["CS", "Math", "Physics"]
```

To get Alice's full info, you index all four lists at position 0. To add a student, you remember to append to all four. To drop one, you pop from all four. Miss one update and your data goes out of sync; suddenly Alice has Bob's grades. Bug. Hard to spot.

You upgrade to dicts:

```python
students = [
    {"name": "Alice", "id": 101, "grades": [88, 92], "major": "CS"},
    {"name": "Bob",   "id": 102, "grades": [77, 85], "major": "Math"},
]
```

Better. Each student is one thing. But every function that does something useful takes a student-shaped dict: `compute_gpa(student)`, `send_reminder(student)`, `is_failing(student)`. The functions and the data are related but kept in separate places. To find every operation defined on students, you grep the codebase for `student` in parameter lists. Nothing tells the reader (or Python) that these functions belong together.

Classes solve this. A class is a way to bundle data and the operations on that data into one shape. You define a `Student` class once. Each student is an instance of that class. Methods on the class live with the data they need. Adding a new operation means adding a method, not yet another floating function.

OOP is one of the bigger ideas in programming. It changes how you organize code. You can ignore the deep end (multiple inheritance, metaclasses, descriptors) for years. The shallow end you'll start using today.

## What you'll be able to do by the end

- Define a class with `class`, set up instance attributes in `__init__`, and explain what `self` is in plain English.
- Write methods that read and modify an object's state.
- Customize how your objects print, compare, and behave under common Python operations using "dunder" methods.
- Use inheritance to share code between related classes and `super()` to call the parent's behavior from a subclass.
- Recognize when to reach for `@property` to expose a method as an attribute.
- Read code with `@classmethod` and `@staticmethod` even if you don't reach for them often yet.

## Prerequisites

You should be solid on Modules 6 (functions), 7 (lists and dicts), and 8 (exceptions). Module 11 (file I/O) and Module 12 (regex) show up in the mini-project but aren't conceptual prerequisites.

This module introduces no new syntax for control flow or data types; it's all about organizing what you already know. If functions still feel shaky (especially the distinction between defining one and calling one), revisit Module 6 first. Methods are functions with extra rules, and the rules don't help if the basics aren't reflexive.

## Core concepts

### From dicts to classes

Here's the dict version of a student:

```python
alice = {"name": "Alice", "house": "Ravenclaw", "grades": [88, 92, 95]}

def gpa(student):
    return sum(student["grades"]) / len(student["grades"])

print(gpa(alice))  # 91.66...
```

Works fine. But notice that `gpa` only makes sense if the dict it's given has a `"grades"` key. Pass in any old dict and it crashes with `KeyError`. Nothing in the code says "this function expects a student-shaped dict." The connection between data shape and operations is held together by your hopes.

A class makes the connection explicit.

```python
class Student:
    def __init__(self, name, house, grades):
        self.name = name
        self.house = house
        self.grades = grades

    def gpa(self):
        return sum(self.grades) / len(self.grades)


alice = Student("Alice", "Ravenclaw", [88, 92, 95])
print(alice.gpa())  # 91.66...
```

Same information, same computation. New structure: the function lives inside the class. To compute Alice's GPA, you ask her: `alice.gpa()`. The function knows it operates on a `Student` because it lives in the `Student` class.

Now let's pick this apart.

### `class`, `__init__`, and `self`

The keyword `class` starts a class definition. By convention, class names are in CapWords: `Student`, `BankAccount`, `LogEntry`. Compare with function names, which are `snake_case`. Mixing the two conventions is one of the fastest ways to make Python code look unprofessional.

```python
class Student:
    pass
```

The colon and indentation work the same way they do for `if` and `def`. Everything indented under `class` is part of the class. (`pass` is a placeholder; it lets you define an empty class without a syntax error.)

`__init__` is a method (a function defined inside a class) with a special name. Python calls it automatically when you create an instance. Its job is to set up the new object's starting state. The double-underscore names ("dunders") are reserved by Python for methods that hook into the language's built-in operations. You don't call `__init__` yourself; Python calls it for you when you write `Student(...)`.

```python
class Student:
    def __init__(self, name, house, grades):
        self.name = name
        self.house = house
        self.grades = grades
```

Now `self`. Every method's first parameter is `self`, by convention. When you write:

```python
alice = Student("Alice", "Ravenclaw", [88, 92, 95])
```

Python:

1. Creates a new empty `Student` object.
2. Calls `Student.__init__(new_object, "Alice", "Ravenclaw", [88, 92, 95])`.
3. Inside `__init__`, `self` is the new object.

So `self.name = name` stores the value of the parameter `name` onto the new object as an attribute called `name`. After `__init__` finishes, the object has three attributes (`name`, `house`, `grades`) and you can read them with dot notation: `alice.name`.

If `self` still feels like magic, here's the demystified version. `self` is just "the object the method was called on." `alice.gpa()` is Python's nicer way of writing `Student.gpa(alice)`. The `alice` in front of the dot gets passed in as the first parameter. Always. That parameter conventionally gets named `self`, but the name isn't enforced; what's enforced is the position.

> **What could go wrong:** A near-universal beginner mistake is forgetting `self.` inside `__init__`:
>
> ```python
> def __init__(self, name):
>     name = name   # wrong: assigns the parameter to itself, attribute never set
> ```
>
> This creates no error, just a Student with no `name` attribute. The first time you access `alice.name` you'll get `AttributeError: 'Student' object has no attribute 'name'`. The fix is `self.name = name`. The `self.` prefix is how you tell Python "store this on the object," as opposed to "this is a local variable."

### Methods

Methods are functions defined inside a class. Their first parameter is `self`, and they can read or modify the object's attributes through `self`.

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def gpa(self):
        return sum(self.grades) / len(self.grades)

    def add_grade(self, score):
        self.grades.append(score)
        return self.gpa()


alice = Student("Alice", [88, 92, 95])
print(alice.gpa())          # 91.66...
print(alice.add_grade(80))  # 88.75
print(alice.grades)         # [88, 92, 95, 80]
```

Three things to notice. First, `add_grade` mutates `self.grades`; the change persists in the object. Second, `add_grade` calls `self.gpa()` to use another method on the same object. Methods can call each other through `self`. Third, when you call `alice.add_grade(80)`, you pass *one* argument from outside, but the method's signature has *two* parameters (`self` and `score`). Python supplies `self` for you.

> **What could go wrong:** Define a method without `self`:
>
> ```python
> class Student:
>     def gpa():
>         return sum(self.grades) / len(self.grades)
> ```
>
> Now `alice.gpa()` blows up: `TypeError: gpa() takes 0 positional arguments but 1 was given`. Python is trying to pass `alice` as the first argument, and your method doesn't accept any. Add `self`.

### `__str__` and `__repr__`: make your objects printable

Try printing a `Student` with the class as defined above:

```python
print(alice)  # <__main__.Student object at 0x10b1c2f50>
```

That's the default. Useless. The fix is `__str__`, the dunder method Python calls when something asks for a human-readable version of the object (like `print` or `str()`).

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def __str__(self):
        average = sum(self.grades) / len(self.grades)
        return f"{self.name} (GPA: {average:.2f})"


print(Student("Alice", [88, 92, 95]))   # Alice (GPA: 91.67)
```

`__str__` returns a string. `print` uses that string. You can also force the conversion with `str(alice)`.

There's a sibling method called `__repr__` that's used in debugging contexts: the REPL, lists of objects, error messages. The rule of thumb: `__str__` is for end users; `__repr__` is for you, the programmer. If you only define one, define `__repr__`. If you define both, Python uses each in its right context.

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def __repr__(self):
        return f"Student(name={self.name!r}, grades={self.grades!r})"

    def __str__(self):
        return self.name


alice = Student("Alice", [88, 92, 95])
print(alice)        # Alice
print([alice])      # [Student(name='Alice', grades=[88, 92, 95])]
```

The `!r` inside the f-string calls `repr()` on the value, which wraps strings in quotes. Notice that printing a *list* of students uses `__repr__` for each one. That's why a useful `__repr__` makes debugging so much easier; you can dump a list of objects and read what they are.

### `__eq__`, `__lt__`, `__len__`: hooking into operators

By default, two `Student` objects are equal only if they're the same object in memory:

```python
a = Student("Alice", [88, 92])
b = Student("Alice", [88, 92])
print(a == b)   # False
```

Why? Without `__eq__`, Python falls back to comparing by identity (the equivalent of `a is b`). To make two students with the same data compare equal, define `__eq__`:

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def __eq__(self, other):
        return self.name == other.name and self.grades == other.grades
```

Now `a == b` returns `True`. Same idea for `<`, `>`, `<=`, `>=` via `__lt__`, `__gt__`, and so on. If you only define `__lt__`, Python can sort instances based on it.

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def gpa(self):
        return sum(self.grades) / len(self.grades)

    def __lt__(self, other):
        return self.gpa() < other.gpa()

    def __repr__(self):
        return f"{self.name}({self.gpa():.1f})"


students = [
    Student("Alice", [88, 92, 95]),
    Student("Bob", [77, 85]),
    Student("Carol", [99, 96, 92]),
]
print(sorted(students))
# [Bob(81.0), Alice(91.7), Carol(95.7)]
```

`sorted()` works because Python uses `__lt__` under the hood. The same applies to `min` and `max`.

`__len__` lets your objects respond to `len()`:

```python
class Roster:
    def __init__(self, students):
        self.students = students

    def __len__(self):
        return len(self.students)


print(len(Roster([alice, bob, carol])))  # 3
```

A useful rule: define dunder methods that match how you'd describe the object in plain English. A roster has a length. A student has an ordering by GPA. A package has a weight. When the rest of Python's syntax fits your object, dunders are how you make it work.

**Try it.** Define a `Money` class that stores an amount in cents (an integer) and a currency code. Make two `Money` instances with the same amount and currency compare equal with `==`. Make `Money(100, "USD") + Money(50, "USD")` return a new `Money(150, "USD")`. (Hint: the dunder for `+` is `__add__`.)

<details>
<summary>Answer</summary>

```python
class Money:
    def __init__(self, cents, currency):
        self.cents = cents
        self.currency = currency

    def __eq__(self, other):
        return self.cents == other.cents and self.currency == other.currency

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies.")
        return Money(self.cents + other.cents, self.currency)

    def __repr__(self):
        return f"Money({self.cents}, {self.currency!r})"


a = Money(100, "USD")
b = Money(50, "USD")
print(a + b)         # Money(150, 'USD')
print(a == Money(100, "USD"))   # True
```

`__add__` returns a *new* `Money` rather than mutating `self`. That's the convention; `+` on numbers also returns a new value rather than changing the original. Raising on mismatched currencies prevents silently adding dollars and yen.

</details>

### Inheritance and `super()`

Suppose you've built a `Rectangle` class:

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def __str__(self):
        return f"Rectangle({self.width} x {self.height})"
```

Now you want a `Square`. A square is a rectangle where both sides are equal. You could rewrite the whole class:

```python
class Square:
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

    def perimeter(self):
        return 4 * self.side

    def __str__(self):
        return f"Square({self.side})"
```

But you've duplicated everything `Rectangle` does. Fix a bug in `Rectangle`, you have to fix it in `Square` too. Add a method, ditto. Inheritance lets you say "a `Square` is a `Rectangle` with this small difference":

```python
class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    def __str__(self):
        return f"Square({self.width})"
```

That's the whole class. `class Square(Rectangle):` says `Square` *inherits from* `Rectangle` (its parent). `Square` gets `area`, `perimeter`, and everything else `Rectangle` defines, for free. The two methods `Square` defines either override the parent's version (`__str__`) or extend it (`__init__`).

`super()` is how a subclass calls back to the parent's version of a method. Here, `super().__init__(side, side)` calls `Rectangle.__init__(self, side, side)`, which sets `self.width = side` and `self.height = side`. Then `Square`'s `__init__` is done.

```python
s = Square(5)
print(s.area())       # 25 (inherited from Rectangle)
print(s.perimeter())  # 20 (inherited from Rectangle)
print(s)              # Square(5)  (overridden)
```

Inheritance is powerful and easy to overdo. A rule that's served many programmers well: prefer composition (one object holding another as an attribute) over inheritance unless the child is genuinely a *kind of* the parent. A `Square` is a `Rectangle`, fine. A `Car` is not an `Engine`; a `Car` *has* an `Engine`.

### Polymorphism, briefly

When different classes implement the same method name in their own way, code that uses that method works on instances of any of them. That's polymorphism.

```python
class Dog:
    def speak(self):
        return "Woof"


class Cat:
    def speak(self):
        return "Meow"


class Cow:
    def speak(self):
        return "Moo"


for animal in [Dog(), Cat(), Cow()]:
    print(animal.speak())
```

The loop doesn't know or care what type each `animal` is. It calls `.speak()` and trusts each class to do its thing. This is how `sorted` works on your students: it calls `__lt__` and trusts each implementation.

### `_private` and the underscore convention

Python has no real private attributes. You can read and write any attribute from outside the class. But there's a convention: a leading underscore signals "this is internal; outside code shouldn't touch it."

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance   # internal

    def deposit(self, amount):
        self._balance += amount

    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount
```

The leading underscore on `_balance` says: go through `deposit` and `withdraw`; don't reach in and modify `_balance` directly. Python won't stop you, but other programmers reading the code will know you didn't mean for them to.

This is a contract, not a wall. Other languages enforce privacy with the compiler; Python relies on convention. The Python phrase for this is "we're all consenting adults here."

### `@property`: methods that look like attributes

Something has been awkward. `gpa` is information that depends on `grades`, but you have to call it as `alice.gpa()`. From the outside, why isn't it just `alice.gpa`, the same way `alice.name` works?

`@property` makes that work:

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    @property
    def gpa(self):
        return sum(self.grades) / len(self.grades)


alice = Student("Alice", [88, 92, 95])
print(alice.gpa)   # no parens
```

Putting `@property` above a method turns it into a read-only computed attribute. From the outside, `alice.gpa` looks like a stored value. Inside, the method runs every time you access it.

The `@something` syntax above a function is called a decorator. You'll see decorators a lot in Python (`@staticmethod` and `@classmethod` are next). A decorator wraps the function with extra behavior. Writing your own decorators is a topic for later study; for now, just use them.

### `@classmethod` and `@staticmethod`: a light touch

Two more decorators worth recognizing, even if you reach for them less often.

`@classmethod` defines a method that receives the *class itself* as its first argument, conventionally named `cls`, instead of an instance. The most common use is alternate constructors:

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    @classmethod
    def from_string(cls, csv_line):
        name, *grade_strs = csv_line.strip().split(",")
        return cls(name, [int(g) for g in grade_strs])


alice = Student.from_string("Alice,88,92,95")
print(alice.name, alice.grades)
```

`from_string` gets called on the class, not an instance: `Student.from_string(...)`. Inside, `cls` is `Student`, so `cls(name, [...])` is equivalent to `Student(name, [...])`. Why use `cls` instead of hardcoding `Student`? If a subclass inherits `from_string`, `cls` will be the subclass, and the alternate constructor will still build the right type.

`@staticmethod` is a function that lives inside a class for organizational reasons but doesn't take `self` or `cls`. It's a plain function, namespaced under the class.

```python
class TempConverter:
    @staticmethod
    def c_to_f(celsius):
        return celsius * 9 / 5 + 32


print(TempConverter.c_to_f(100))  # 212.0
```

You can write Python for a long time without reaching for either. Recognize them when you read other people's code.

### Persisting objects with JSON

Module 11 showed you how to save lists and dicts to JSON. Custom objects don't go through that pipeline directly: JSON has no idea what a `Student` is. The standard pattern is a `to_dict` method that converts your object to a plain dict, and a `from_dict` classmethod that rebuilds it.

```python
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def to_dict(self):
        return {"name": self.name, "grades": self.grades}

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["grades"])
```

To save a list of students:

```python
import json

data = [s.to_dict() for s in students]
with open("students.json", "w") as f:
    json.dump(data, f, indent=2)
```

And to load:

```python
import json

with open("students.json") as f:
    data = json.load(f)
students = [Student.from_dict(d) for d in data]
```

Convert to dict, save; load, convert back. This pattern scales to any class whose attributes are themselves JSON-friendly. The mini-project's library catalog uses exactly this approach.

**Try it.** Write a `Timer` class with three methods: `start()`, `stop()`, and `elapsed()`. After `start()` and `stop()` have both been called, `elapsed()` returns the number of seconds between them. Use `time.time()` from the `time` module.

<details>
<summary>Answer</summary>

```python
import time

class Timer:
    def __init__(self):
        self._start = None
        self._end = None

    def start(self):
        self._start = time.time()

    def stop(self):
        self._end = time.time()

    def elapsed(self):
        if self._start is None or self._end is None:
            raise ValueError("Timer must be started and stopped first.")
        return self._end - self._start


t = Timer()
t.start()
time.sleep(0.5)
t.stop()
print(f"{t.elapsed():.3f} seconds")  # ~0.500 seconds
```

The underscore on `_start` and `_end` signals that callers shouldn't touch those directly. `__init__` sets both to `None`, which lets `elapsed()` detect the "not yet started and stopped" case and raise a clear error instead of returning a nonsense number.

</details>

## Common pitfalls

**1. Forgetting `self.` inside `__init__`.**

```python
def __init__(self, name):
    name = name   # not an attribute, just a local
```

No error, just an object missing the attribute. Add `self.`: `self.name = name`.

**2. Forgetting `self` in the method signature.**

```python
def gpa():
    return sum(self.grades) / len(self.grades)
```

`TypeError` the moment you call it on an instance. Every instance method takes `self` as its first parameter.

**3. Mutable default arguments (the most famous Python gotcha).**

```python
class Student:
    def __init__(self, name, grades=[]):
        self.name = name
        self.grades = grades
```

That `grades=[]` is created *once*, when the class is defined, and then shared across every `Student` created without an explicit `grades` argument. Add a grade to one, and every other default-constructed Student sees it too.

```python
a = Student("Alice")
b = Student("Bob")
a.grades.append(95)
print(b.grades)   # [95]  -- Bob got Alice's grade
```

The fix is to use `None` as the default and assign a fresh list inside the body:

```python
def __init__(self, name, grades=None):
    self.name = name
    self.grades = grades if grades is not None else []
```

**4. Defining mutable state on the class instead of the instance.**

```python
class Student:
    grades = []   # shared by every instance

    def __init__(self, name):
        self.name = name
```

Same problem, different shape. `grades` here is a *class attribute*, shared by all instances. Use class attributes for true constants (`SCHOOL_NAME = "Hogwarts"`), never for per-instance mutable data. For per-instance data, assign inside `__init__`.

**5. Overriding `__init__` without calling `super().__init__`.**

```python
class Square(Rectangle):
    def __init__(self, side):
        self.side = side   # forgot to set up width and height
```

Now `Square(5).area()` fails because `area` reads `self.width`, which was never set. Call `super().__init__(side, side)` to let the parent set up its share.

**6. Confusing `==` with `is`.**

```python
a = Student("Alice", [88])
b = Student("Alice", [88])
print(a == b)   # depends on __eq__
print(a is b)   # always False -- different objects
```

`is` checks whether two names refer to the same object. `==` checks whether they're equal. Without `__eq__`, `==` falls back to `is`, which is why two freshly-built equivalent students aren't considered equal by default.

## How this connects

Looking back, classes are the natural home for everything you've been building. Module 7's lists and dicts gave you ways to group data; classes go further by attaching behavior to that data. Module 8's exceptions plug into class design through custom exception subclasses (`class InsufficientFundsError(Exception): pass`). Module 11's JSON round-tripping is what `to_dict` and `from_dict` answer. Module 12's regex patterns sometimes live as class attributes on validators.

Looking forward, Module 14 closes the curriculum with testing, style, and a capstone. Unit tests fit classes naturally: each test class corresponds to a class under test, each test method exercises one behavior. The capstone projects all involve classes (`Habit`, `Transaction`, game entities), and the test suite is what tells you the classes do what they claim. Past fundamentals, every major Python library you'll use (`requests`, `pandas`, `Flask`) is built on classes. Reading their docs and source becomes accessible once class syntax stops being noise.

## Recap

- A class bundles related data and the operations on that data into one shape. Instances are particular objects built from the class.
- `__init__` runs when you create an instance. Its job is to set up starting state. The first parameter is `self`, which refers to the new object.
- Methods are functions defined inside a class. Their first parameter is `self`. Python passes the instance as `self` automatically when you call `instance.method()`.
- Dunder methods hook into Python's syntax: `__str__` for printing, `__repr__` for debugging, `__eq__` and `__lt__` for comparison, `__len__` for `len()`, `__add__` for `+`.
- Inheritance lets a child class reuse a parent's code. `super().__init__(...)` calls the parent's setup from the child's `__init__`.
- A leading underscore (`_balance`) signals "internal; please don't touch from outside." It's a convention, not a wall.
- `@property` turns a method into a read-only computed attribute, accessed without parentheses.
- `@classmethod` defines alternate constructors and methods that act on the class itself. `@staticmethod` is a plain function namespaced inside a class.
- Mutable default arguments (`grades=[]`) and class-level mutable attributes are the two biggest beginner traps. Use `None` defaults and assign fresh containers inside `__init__`.

## Up next

Module 14 covers testing (`assert`, `unittest`, `pytest`), code style (PEP 8, `black`, `ruff`), the paradigms you've already used without naming them, and a capstone project that pulls everything together. After that, you'll have a credible foundation in Python and a clear set of paths forward (web, data, automation, ML).

Now go work the exercises and mini-project for Module 13 in the curriculum doc. The library catalog is where every concept in this lecture earns its keep: classes for the entities, `__str__` for printing them, methods for the operations, custom exceptions for the error cases, and `to_dict` and `from_dict` for persistence.
