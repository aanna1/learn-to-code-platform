# Tier 3: Advanced Language Features

## Why this matters

Open the source code of `pydantic`. Open `sqlalchemy`. Open `django`. You'll see things you don't recognize. Classes that inherit from `type`. Attributes that aren't really attributes. Methods marked `@abstractmethod`. Tiny classes with `__slots__` at the top. Class bodies that read like configuration files but are clearly Python.

None of that is fundamentals. None of it is the polish from Tier 1 or the composition tools from Tier 2. It's the layer underneath: the machinery Python exposes for building frameworks, the seams the language gives you to bend its own semantics.

Honest framing for the path you're on. You're heading toward automation and DevOps. You probably won't write a metaclass this year. You probably won't write your own descriptor. The recommended order in the curriculum tells you so, and the curriculum is right. Most production automation code uses regular classes, dataclasses, and protocols at most. The deep features sit on the shelf.

So why this lecture? Two reasons. First, you read code written by people who use these features heavily. The fields on a `pydantic` model are descriptors. The base class of a Django model is built by a metaclass. The interfaces in `boto3` lean on abstract base classes and registries. When this code surprises you, the surprise should be "I haven't read about that yet" and not "Python is doing something impossible." Second, a few of these (`__slots__`, `Protocol`, `ABC`) earn their place even in straightforward application code. The rest is for when you cross from writing application code to writing libraries.

We'll treat each feature the same way: what problem does it solve, what does the wrong code look like, what does the right code look like, and when (honestly) should you reach for it.

## What you'll be able to do by the end

- Write an abstract base class with `abc.ABC` and `@abstractmethod`, and explain why an `ABC`-violating subclass fails earlier than a duck-typed one.
- Define a `Protocol` for structural typing that `mypy` checks, without forcing a class hierarchy.
- Recognize where descriptors live in real libraries (Django fields, SQLAlchemy columns, pydantic fields) and write a simple validating descriptor of your own.
- Read a class with multiple inheritance, compute its MRO, and predict what `super().method()` resolves to.
- Use `__slots__` to cut per-instance memory and prevent accidental attribute assignment, and explain the restrictions it adds.
- Read a class that uses a metaclass and explain in one sentence what the metaclass is doing.
- Decide, for each feature, whether to reach for it in your own code or recognize it on sight in someone else's.

## Prerequisites

You need a solid grasp of classes: `__init__`, `__repr__`, inheritance with a single parent, `super()` in the single-inheritance case, and `@property`. You should be comfortable reading code that uses `@dataclass`. Familiarity with type hints (`list[str]`, `Optional`, `Callable`) is required because the `Protocol` section uses them everywhere.

If you can't sketch what `super().__init__()` does in a constructor of a class that inherits from one parent, review the classes module of fundamentals before continuing.

## Core concepts

### Abstract base classes: making "you must implement this" enforceable

You're building a small reporting library. Different report types share a method called `render()`. You sketch it like this:

```python
class Report:
    def __init__(self, data):
        self.data = data

    def render(self):
        raise NotImplementedError("subclasses must implement render()")


class CsvReport(Report):
    def render(self):
        return "\n".join(",".join(map(str, row)) for row in self.data)


class JsonReport(Report):
    # oops, forgot to implement render
    pass
```

The `JsonReport` author forgot to write `render`. When does anyone find out?

```python
r = JsonReport([[1, 2], [3, 4]])
print(r.render())   # NotImplementedError, finally
```

At call time. Not at class definition time. Not at instantiation. Possibly in production, when a customer asks for a JSON report and the request handler crashes. The `NotImplementedError` pattern is the duck-typed approach to interfaces: the contract is documented by code that fails when you violate it, but only when the violating method is invoked.

Abstract base classes move the failure forward in time:

```python
from abc import ABC, abstractmethod

class Report(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def render(self) -> str:
        ...


class CsvReport(Report):
    def render(self) -> str:
        return "\n".join(",".join(map(str, row)) for row in self.data)


class JsonReport(Report):
    pass


r = JsonReport([[1, 2], [3, 4]])
# TypeError: Can't instantiate abstract class JsonReport
# with abstract method render
```

The error happens at instantiation, not at the first call to `render`. You catch the bug the moment someone tries to use `JsonReport`, which in tests is a few seconds after writing the class. The contract is now enforced by the language.

A few details that matter. The class must inherit from `ABC` (or have `ABCMeta` as its metaclass, which `ABC` arranges for you). Any method decorated with `@abstractmethod` makes the class abstract. You can have non-abstract methods too: shared code lives in the base class, the contract lives in the abstract methods.

```python
class Report(ABC):
    def __init__(self, data):
        self.data = data

    def summary(self) -> str:
        return f"Report with {len(self.data)} rows"

    @abstractmethod
    def render(self) -> str:
        ...
```

Subclasses inherit `__init__` and `summary` for free. They must implement `render` to be instantiable.

**What could go wrong:** decorating `__init__` with `@abstractmethod`. The decorator works on `__init__`, but the pattern is weird and rarely what you want. Use it on the methods that represent the contract (the things callers will invoke), not on construction.

### Protocols: duck typing with type checking

ABCs require inheritance. To participate in the `Report` contract above, you have to inherit from `Report`. That's fine when you control all the classes. It's painful when you don't.

Picture this. You're writing a function that takes anything with a `render()` method that returns a string. You don't care whether the object inherits from `Report` or `Foo` or nothing at all. In dynamic Python you'd just write:

```python
def save_report(obj, path):
    Path(path).write_text(obj.render())
```

That works. Pass anything with `render()` and it runs. `mypy` has no way to verify that the caller actually passed something with `render()`. The type annotation you'd want is "anything that has `render() -> str`."

`Protocol` is the answer.

```python
from typing import Protocol
from pathlib import Path

class Renderable(Protocol):
    def render(self) -> str: ...


def save_report(obj: Renderable, path: Path) -> None:
    path.write_text(obj.render())
```

A class is a `Renderable` if it has a `render` method returning a string. It does not need to inherit from `Renderable`. The class doesn't even need to know `Renderable` exists.

```python
class CsvReport:
    def __init__(self, data):
        self.data = data
    def render(self) -> str:
        return "\n".join(",".join(map(str, row)) for row in self.data)


save_report(CsvReport([[1, 2]]), Path("out.csv"))   # mypy: ok
save_report("hello", Path("out.csv"))                # mypy: error, str has no render
```

`mypy` checks the contract structurally: does the type passed in have the right methods with the right signatures? Yes or no. This is duck typing the language has finally caught up with.

When to choose ABC versus Protocol? ABCs win when you also want to share base-class behavior (the `summary` method above). Protocols win when you only want to declare an interface, especially for types you don't own. For new code you write today, default to Protocol. Reach for ABC when there's actual shared implementation to inherit.

**Try it yourself:** write a Protocol called `Closeable` that requires a `close() -> None` method. Then write a function `cleanup(things: list[Closeable]) -> None` that closes everything.

<details>
<summary>Answer</summary>

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None: ...


def cleanup(things: list[Closeable]) -> None:
    for thing in things:
        thing.close()
```

Files, sockets, database connections, and anything with `close()` satisfy `Closeable` without inheriting from anything. That's why this matters in real code: most resources you'd want to clean up come from third-party libraries you can't subclass.
</details>

### `__slots__`: cutting memory and tightening contracts

By default, every Python instance carries a `__dict__` that maps attribute names to values. That dict is what makes `instance.anything = value` work at any time. It's also what makes Python objects heavier than they need to be.

Measure it. Here's a Point class with a million instances:

```python
import sys

class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


p = Point(1.0, 2.0)
print(sys.getsizeof(p))           # 48 bytes (the object header)
print(sys.getsizeof(p.__dict__))  # 296 bytes on Python 3.12
```

So each instance costs about 344 bytes. A million Points is roughly 344 MB.

Add `__slots__`:

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


p = Point(1.0, 2.0)
print(sys.getsizeof(p))   # 48 bytes
# No __dict__ at all
print(hasattr(p, "__dict__"))   # False
```

Per-instance memory drops to about 48 bytes. The million Points fit in roughly 48 MB. The gain is real when instances are numerous.

A second benefit shows up immediately. Try assigning an undeclared attribute:

```python
p = Point(1.0, 2.0)
p.color = "red"
# AttributeError: 'Point' object has no attribute 'color'
```

Without slots, that line silently creates a new attribute. With slots, it raises. Typos in attribute names become errors at the assignment, not silent bugs that show up two function calls later.

The restrictions: no dynamic attributes (which is the point), no multiple inheritance from two slotted classes (because the slot layouts can't combine), and `weakref.ref(instance)` won't work unless `"__weakref__"` is in the slots tuple. For automation code, the second restriction is what you'll hit. Single inheritance, no mixins.

Dataclasses have an opt-in for this. `@dataclass(slots=True)` (Python 3.10+) generates the slots tuple for you from the type-annotated fields. Use it when you'd otherwise have a hand-written slotted class.

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: float
    y: float
```

Same memory savings, no boilerplate.

### Method resolution order: how `super()` finds the next method

Single inheritance is simple. `super().method()` calls the parent's version of `method`. Multiple inheritance gets weird, and most learners stop here. We'll keep going.

Consider this:

```python
class A:
    def greet(self) -> None:
        print("A")

class B(A):
    def greet(self) -> None:
        print("B")
        super().greet()

class C(A):
    def greet(self) -> None:
        print("C")
        super().greet()

class D(B, C):
    def greet(self) -> None:
        print("D")
        super().greet()


D().greet()
```

Predict the output before reading on. Most learners predict `D B A` (D calls super, which goes to B, which calls super, which goes to A) or `D B A C A` (B and C are both parents, both run). Both are wrong.

The actual output:

```
D
B
C
A
```

Each class appears exactly once. The order is `D, B, C, A`. Python computes this using the C3 linearization algorithm and stores it on the class as `__mro__`:

```python
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

`super()` walks the MRO. From `D`, the next class is `B`. From `B`, in the context of an instance of `D`, the next class is *not* `A` (B's only parent) but `C` (the next class in D's MRO). This is the part that surprises people: `super()` in `B` is context-dependent. When `B` is called on its own, `super()` is `A`. When `B` is called as part of `D`, `super()` is `C`.

That property is what makes the **mixin** pattern work. A mixin is a small class that adds one piece of behavior, designed to be combined with others. Each mixin calls `super()` in its methods so the chain flows through every class in the MRO.

Real example, a logging mixin:

```python
import logging

log = logging.getLogger(__name__)


class LoggingMixin:
    def save(self) -> None:
        log.info("Saving %s", self.__class__.__name__)
        super().save()


class TimedMixin:
    def save(self) -> None:
        import time
        start = time.monotonic()
        super().save()
        log.info("Save took %.3fs", time.monotonic() - start)


class Record:
    def save(self) -> None:
        print(f"Persisting {self}")


class TimedLoggedRecord(LoggingMixin, TimedMixin, Record):
    pass


TimedLoggedRecord().save()
```

`super().save()` in `LoggingMixin` doesn't call `Record.save()`. It calls whatever's next in the MRO of the instance's actual class. For a `TimedLoggedRecord` instance, the chain is `TimedLoggedRecord -> LoggingMixin -> TimedMixin -> Record`. Each mixin contributes its piece. The terminal class (`Record`) does the actual work and doesn't call `super()` further.

**What could go wrong:** mixing classes where one calls `super().save()` and another doesn't. The chain breaks at the silent one. Mixin classes intended for composition should always call `super()`, even though it looks pointless when you read them in isolation.

**What could also go wrong:** an MRO that can't be linearized. Try `class Bad(B, A, C): pass` for the classes above and Python raises `TypeError: Cannot create a consistent method resolution order`. This means the parent order you specified is contradictory. The fix is usually to re-examine your inheritance: if you can't sequence the classes consistently, you probably want composition instead of inheritance.

### Descriptors: the machinery under `@property`

You've used `@property`. It looks like magic.

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32


t = Temperature(100)
print(t.fahrenheit)   # 212.0
```

`t.fahrenheit` doesn't look like a method call. There are no parentheses. Yet the function ran. How?

The answer is the descriptor protocol. A descriptor is any object with `__get__`, `__set__`, or `__delete__` methods. When an instance attribute lookup finds a descriptor on the class, Python calls the descriptor's `__get__` instead of returning it directly. `@property` is itself a descriptor. Decorating a method with `@property` produces a `property` object, which has `__get__`, and that's what executes when you access the attribute.

You can write your own descriptors. Here's a validating field that rejects negative numbers:

```python
class Positive:
    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"must be positive, got {value!r}")
        setattr(instance, self.private_name, value)


class Account:
    balance = Positive()
    deposit_amount = Positive()

    def __init__(self, balance: float) -> None:
        self.balance = balance


a = Account(100)
print(a.balance)        # 100
a.balance = 50          # ok
a.balance = -10         # ValueError: must be positive, got -10
```

Walk through it. `balance = Positive()` puts a `Positive` instance on the class. `__set_name__` runs when the class body finishes, telling the descriptor what name it's bound to (here, `"balance"`), so it can store the actual value under `_balance` on each instance. When you write `a.balance = 100`, Python sees the descriptor on the class and calls `Positive.__set__(self_of_descriptor, a, 100)`, which validates and stores. When you read `a.balance`, Python calls `Positive.__get__(self_of_descriptor, a, Account)`, which fetches `a._balance`.

Two descriptor properties matter. First, the descriptor instance is shared across all instances of `Account` (it lives on the class), which is why we store the actual value on `instance` with a different name. Second, validation runs in `__init__` too, because `self.balance = balance` triggers `__set__`. You get free input validation on construction without writing anything in `__init__`.

This pattern is everywhere in libraries. A Django model field is a descriptor: `models.CharField(max_length=100)` returns a descriptor that validates on set and lazy-fetches on get. A SQLAlchemy `Column` is a descriptor that lets you write `User.name == "Alice"` and produces a SQL expression instead of a boolean. A pydantic `Field` is a descriptor with validation, coercion, and serialization wired in.

When should you write your own? When you have the same kind of validation, lazy computation, or attribute behavior repeated across many class attributes. For a one-off, `@property` is simpler. For a pattern that repeats four or more times, a descriptor saves real code.

**What could go wrong:** putting the descriptor on the instance instead of the class. `self.balance = Positive()` inside `__init__` does not work, because the descriptor protocol only triggers when the descriptor is found on the *class*. Always assign the descriptor at class level. This is one of the most confusing bugs in the language when it happens, because the code looks fine and the descriptor's methods just never run.

### Metaclasses: the class of a class

Everything in Python is an object. Including classes.

```python
class Foo:
    pass

print(type(Foo()))   # <class '__main__.Foo'>
print(type(Foo))     # <class 'type'>
```

`Foo()` is an instance of `Foo`. `Foo` is an instance of `type`. `type` is the **metaclass**: the class whose instances are classes.

This isn't an analogy. You can use `type` directly to create classes at runtime:

```python
Foo = type("Foo", (), {})
# Same as:
# class Foo:
#     pass
```

`type` takes three arguments: the name of the class, a tuple of base classes, and a dict of attributes. The `class` statement is sugar for calling `type` with those three things.

A custom metaclass subclasses `type` and overrides class creation. The textbook example is auto-registration:

```python
class PluginMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "Plugin":   # don't register the base
            PluginMeta.registry[name] = cls
        return cls


class Plugin(metaclass=PluginMeta):
    def run(self) -> None:
        ...


class AuthPlugin(Plugin):
    def run(self) -> None:
        print("authenticating")


class LogPlugin(Plugin):
    def run(self) -> None:
        print("logging")


print(PluginMeta.registry)
# {'AuthPlugin': <class 'AuthPlugin'>, 'LogPlugin': <class 'LogPlugin'>}
```

Every class that uses `PluginMeta` is automatically added to a registry as it's defined. No call to `register()`, no decorator, no import-side-effect plumbing. You define the class and it's registered.

That's what Django does when you write `class MyModel(models.Model):`. The metaclass walks the class body, inspects the `Field` descriptors, builds SQL schema, registers the model. That's what SQLAlchemy's declarative base does. That's what pydantic does to build validators from your type annotations.

Should you write a metaclass? Almost never. The cases where a metaclass is the right tool are vanishingly rare in application code. `__init_subclass__` (added in Python 3.6) covers most of what custom metaclasses used to do, and class decorators cover the rest:

```python
class Plugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[cls.__name__] = cls


class AuthPlugin(Plugin):
    ...


print(Plugin.registry)   # same result, no metaclass needed
```

`__init_subclass__` runs whenever the class is subclassed. Same registration effect, half the conceptual cost. For new code, prefer `__init_subclass__` over a metaclass.

Tim Peters, one of Python's earliest contributors, wrote: "Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don't." That's still true thirty years later. Recognize them when you see them. Don't write them.

## Common pitfalls

1. **Mistaking an ABC for runtime type enforcement.** `@abstractmethod` only fires when someone tries to instantiate an incomplete subclass. It does not check the return type of `render()`, the argument types, or anything else at runtime. Use `mypy` for type checking. The ABC is for "must implement," not "must implement correctly."

2. **Inheriting from `Protocol` thinking it's required.** It isn't. The whole point of Protocol is structural: a class satisfies the protocol if it has the right methods, no inheritance needed. Subclassing a Protocol is for the cases where you want the methods to *also* be inherited (a runtime-checkable protocol via `@runtime_checkable`), which is a smaller niche.

3. **Adding `__slots__` to a dataclass without `slots=True`.** Writing `__slots__ = ("x", "y")` manually inside a `@dataclass` body fights the decorator. Use `@dataclass(slots=True)` instead and let the decorator generate the tuple.

4. **Reaching for multiple inheritance instead of composition.** Multiple inheritance has legitimate uses (mixins), but most cases that "feel like" multiple inheritance are better solved by composition (the class owns an instance that does the work). The MRO and `super()` chain become hard to reason about when you have three or four parents.

5. **Putting a descriptor on `self` in `__init__`.** Descriptors must live on the class to function. `self.x = SomeDescriptor()` produces a regular attribute, not a descriptor. The descriptor protocol simply doesn't activate.

6. **Writing a metaclass when `__init_subclass__` or a class decorator would do.** Metaclasses interact poorly with other metaclasses (a class can have only one). They make subclassing surprising. They make tooling slower. If you can phrase the problem without one, do.

## Try it yourself

Write an abstract base class `Storage` with abstract methods `read(key: str) -> bytes` and `write(key: str, value: bytes) -> None`. Then write a concrete subclass `MemoryStorage` that uses a dict, with proper type hints. The `Storage` class should be impossible to instantiate.

<details>
<summary>One possible answer</summary>

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def read(self, key: str) -> bytes:
        ...

    @abstractmethod
    def write(self, key: str, value: bytes) -> None:
        ...


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}

    def read(self, key: str) -> bytes:
        return self._data[key]

    def write(self, key: str, value: bytes) -> None:
        self._data[key] = value


# Storage()   # TypeError: Can't instantiate abstract class
s = MemoryStorage()
s.write("hello", b"world")
print(s.read("hello"))   # b'world'
```

Now any code that takes a `Storage` parameter accepts `MemoryStorage`, a future `S3Storage`, a future `DiskStorage`, all without changing the consumer. That's the value of the abstraction.
</details>

## How this connects

Tier 1 polished. Tier 2 composed. Tier 3 is the floor under both.

`@dataclass` is built using descriptors (for default factories) and class introspection. `@property` is a descriptor. ABCs use a metaclass behind the scenes (`ABCMeta`). Slots interact with inheritance via the MRO. The features in this lecture are how Python builds the features you use daily.

Looking forward to the Phase 2 curriculum: most modules touch this material lightly, if at all. Module 1's `click` library uses decorators heavily and one custom class type for its `Context`, no descriptors. Module 4's config work might use a small Protocol for source interfaces. Module 7's testing relies on ABCs implicitly (pytest's plugin protocol). Module 9's `boto3` is built on metaclasses internally; you read it, you don't write it. The path forward uses these features by recognition, not by writing them from scratch.

If you skip Tier 3 entirely and head to Phase 2, you'll be fine. Come back here when you read a library and the source surprises you. That's the right time.

## Recap

- `abc.ABC` plus `@abstractmethod` enforces that subclasses implement required methods, failing at instantiation rather than at first call. Use it when there's also shared base-class behavior to inherit.
- `typing.Protocol` declares an interface structurally. Classes satisfy it by having the right methods, with no inheritance required. Prefer Protocol over ABC for pure interface declarations and for types you don't own.
- `__slots__` removes per-instance `__dict__`, saving memory and catching typo-style attribute assignments. Use `@dataclass(slots=True)` to get it without the boilerplate.
- Method resolution order is the C3 linearization of a class's parents. `super()` walks the MRO, not just the immediate parent. The MRO is what makes the mixin pattern work; mixins must call `super()` for the chain to flow.
- Descriptors (`__get__`, `__set__`, `__set_name__`) are how `@property`, Django fields, SQLAlchemy columns, and pydantic fields work. Write one when you have validation or computed-attribute behavior repeated across four-plus attributes. Reach for `@property` for one-offs.
- Metaclasses customize class creation itself. They power ORMs and serialization libraries. For new application code, `__init_subclass__` and class decorators cover the same ground with less cost. Don't write a metaclass unless you genuinely need one.

## Up next

Tier 4 covers concurrency: the GIL, `threading`, `multiprocessing`, and `asyncio`. Where Tier 3 was about the structure of code, Tier 4 is about the structure of execution. The Phase 2 curriculum then begins in earnest with Module 1 (CLI tools), where everything from Tiers 1 and 2 starts paying for itself.
