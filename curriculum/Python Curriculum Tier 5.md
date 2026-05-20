# Tier 5: Tooling and the Ecosystem

## Why this matters

Open your terminal and try this. Create a new project directory. Write a script that imports `requests` and prints something. Run it. It works on your machine. Send it to a colleague. Does it work on theirs?

Probably not. They don't have `requests` installed at the version you have. Or they have a different Python version. Or they're on Windows and you're on macOS and the path you hardcoded for "where my data lives" doesn't exist on their machine. Or they ran your script and it polluted their system Python with the same dependencies a different project of theirs is pinned to a different version of, and now both projects are broken.

These are not Python problems. They are operations problems on top of Python. The fundamentals taught you to write code. Tiers 1 through 4 taught you to write good code. Tier 5 is about everything around the code: how it gets installed, how it gets tested, how it gets formatted consistently, how it gets shipped to other people.

This is also the tier that separates "I write scripts on my laptop" from "I ship software." For automation and DevOps work the difference is load-bearing. The scripts you write at work will run on infrastructure you don't fully control, get edited by people who aren't you, and live longer than your tenure on the project. Tests catch regressions when the next person changes your code. Linters catch the bug class you make most often before code review wastes anyone's time. Lockfiles ensure that the script that worked in CI yesterday still works today. Type checkers catch the bug you'd otherwise find at 3am.

Honest framing: most of this tooling exists because the people who use it got tired of debugging the same class of problem repeatedly. Each tool is a calcified lesson. You can ignore the tools at the cost of relearning the lessons yourself.

## What you'll be able to do by the end

- Write `pytest` tests using plain `assert`, fixtures for shared setup, `parametrize` for input variations, and mocks for external systems.
- Set up an isolated environment for a project, lock its dependencies, and let a colleague reproduce it exactly.
- Configure `ruff`, `black`, and `mypy` for a project, and wire them into `pre-commit` so they run on every commit.
- Read a `pyproject.toml` file and explain what each section does.
- Build a Python package and publish it to PyPI (or a private index) when the time comes.
- Recognize the conventional layout of a Python project on sight.

## Prerequisites

You should have a project of your own to apply this to. Tooling without code to use it on is theater. If you don't have a project, fork one of yours from earlier modules and use it as a scratch space. A working knowledge of the command line (`cd`, `ls`, running a Python script) and Git (`git init`, `git commit`) is assumed.

You don't need anything specific from Tiers 1-4 for this lecture, but having a real-sized program (a few hundred lines, multiple files) makes the tools earn their keep.

## Core concepts

### `pytest`: tests as plain functions

`unittest` came with Python from the start. It works. The API was modeled on Java's JUnit, which is why everything is a method on a class that inherits from `TestCase`.

```python
import unittest

class TestMath(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)

    def test_division(self):
        self.assertAlmostEqual(1 / 3, 0.3333, places=4)


if __name__ == "__main__":
    unittest.main()
```

It works, but every line carries Java baggage. The class is a container, not behavior. The assertion methods (`assertEqual`, `assertAlmostEqual`, `assertIn`, `assertRaises`) replace Python operators that already exist.

`pytest` removed the ceremony.

```python
def test_addition():
    assert 1 + 1 == 2


def test_division():
    assert abs(1 / 3 - 0.3333) < 0.0001
```

Tests are functions whose names start with `test_`. Assertions are the `assert` keyword you already know. Run `pytest` in the directory and it discovers them.

```
$ pytest
============================= test session starts =============================
collected 2 items

test_math.py ..                                                          [100%]
============================= 2 passed in 0.01s ==============================
```

A test fails by raising. `assert 1 + 1 == 3` raises `AssertionError` with a message pytest formats helpfully:

```
>       assert 1 + 1 == 3
E       assert 2 == 3

test_math.py:2: AssertionError
```

The full expression and both sides are shown. No `assertEqual(a, b, msg=...)` ceremony.

Checking that code raises an expected exception:

```python
import pytest

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

`pytest.raises` is a context manager. The block must raise an exception of that type, or the test fails. If you want to check the message:

```python
def test_message():
    with pytest.raises(ValueError, match="must be positive"):
        raise ValueError("value must be positive")
```

`match` is a regex matched against the exception message.

#### Fixtures: shared setup

Many tests need the same setup. A temporary file, a fake database, a configured object. Repeating the setup in every test gets ugly fast. `unittest` had `setUp` and `tearDown` methods. `pytest` uses fixtures.

```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_config(tmp_path: Path) -> Path:
    """Write a sample config file to a temp directory and return its path."""
    config = tmp_path / "config.json"
    config.write_text('{"debug": true}')
    return config


def test_config_is_readable(temp_config: Path) -> None:
    assert temp_config.exists()
    assert "debug" in temp_config.read_text()
```

The fixture is a function decorated with `@pytest.fixture`. Tests that take a parameter with that name receive the fixture's return value. `tmp_path` is itself a built-in pytest fixture that gives you a fresh temp directory per test, automatically cleaned up afterward.

Fixtures can do teardown too, using `yield`:

```python
@pytest.fixture
def database_connection():
    conn = connect_to_test_db()
    yield conn
    conn.close()
```

That pattern should look familiar. It's the `@contextmanager` shape from Tier 2. Setup before `yield`, teardown after.

A fixture is reusable. Define it once in `conftest.py` (a pytest-special file at the project root or in any test directory) and every test in that scope can use it. That's how you build up a small set of test-domain primitives and reuse them across files.

#### Parametrize: one test, many inputs

You have a function `is_palindrome(s: str) -> bool`. You want to test it against ten inputs. Without parametrize:

```python
def test_palindrome_racecar():
    assert is_palindrome("racecar")

def test_palindrome_empty():
    assert is_palindrome("")

def test_palindrome_hello():
    assert not is_palindrome("hello")
```

Three tests, mostly copy-paste. `parametrize` collapses them:

```python
import pytest

@pytest.mark.parametrize("text,expected", [
    ("racecar", True),
    ("", True),
    ("a", True),
    ("hello", False),
    ("Aa", False),  # case-sensitive
])
def test_palindrome(text: str, expected: bool) -> None:
    assert is_palindrome(text) == expected
```

One function, five test cases, each reported separately. When the case-sensitivity case fails, the output names it specifically. Adding a new case is one line.

#### Mocks: standing in for the outside world

Your function calls an HTTP API. You don't want your test to actually make network requests: the test would be slow, flaky, and dependent on the API being up. You replace the network call with a mock that returns a fixed response.

```python
from unittest.mock import patch
import requests

def get_user_name(user_id: int) -> str:
    response = requests.get(f"https://api.example.com/users/{user_id}", timeout=5)
    response.raise_for_status()
    return response.json()["name"]


def test_get_user_name():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"name": "Alice"}
        mock_get.return_value.raise_for_status.return_value = None

        assert get_user_name(42) == "Alice"
        mock_get.assert_called_once_with(
            "https://api.example.com/users/42", timeout=5,
        )
```

`patch` replaces `requests.get` with a `MagicMock` for the duration of the `with` block. The mock is configured to return a fake response object whose `json()` method returns the dict you want. After the test, the patch is reversed and `requests.get` is itself again.

`mock_get.assert_called_once_with(...)` checks that the mocked function was called exactly once with the expected arguments. That's how you verify your code is talking to the API correctly without actually calling it.

A gotcha: you patch where the function is *used*, not where it's defined. If `myapp.users` does `from requests import get`, then in tests you patch `myapp.users.get`, not `requests.get`. The bound name in the module under test is what matters.

For real HTTP testing, libraries like `responses` and `pytest-httpx` are friendlier than `unittest.mock` for HTTP specifically. They let you set up canned responses for URLs and assert that requests were made.

#### Coverage

`pytest-cov` measures which lines your tests actually execute:

```
$ pip install pytest-cov
$ pytest --cov=mypackage --cov-report=term-missing
```

Output names every line that wasn't hit:

```
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
mypackage/api.py     45      8    82%   23-27, 41, 88-89
```

Coverage is a useful diagnostic, not a goal. 100% line coverage tells you every line ran during some test. It does not tell you the tests asserted anything meaningful, or that the right branches ran, or that the edge cases were considered. Use it to find code that has no tests at all. Don't game it.

**What could go wrong:** writing tests that import the real database. You did this without thinking; the test ran fine on your machine because your database is local; CI fails because there's no database there. Tests should be hermetic by default. Use fixtures with mocks for unit tests. Save real-database tests for an integration suite that runs separately.

### Virtual environments and dependency management

You install `requests` with `pip install requests`. Where does it go?

By default, into your system Python (or your user site-packages). Every project sharing that Python now shares `requests`. Upgrade one project's pin to `requests==2.31`, the other project that needed `requests==2.20` breaks silently. This is a known disaster, and the solution is to give every project its own isolated Python environment.

The built-in tool is `venv`:

```
$ python -m venv .venv
$ source .venv/bin/activate    # Linux/macOS
$ .venv\Scripts\activate       # Windows
(.venv) $ pip install requests
(.venv) $ python my_script.py
```

The `.venv` directory contains its own Python interpreter and its own `site-packages`. While the venv is activated, `python` and `pip` point to the ones inside it. Deactivate when you're done. Each project gets its own `.venv`, each can pin different versions, no project pollutes another.

`venv` + `pip` works. It's also slow, and managing dependencies across multiple environments by hand is a chore. The modern alternative is **`uv`** (from Astral).

```
$ uv init my_project
$ cd my_project
$ uv add requests
$ uv run python my_script.py
```

`uv init` creates a project with a `pyproject.toml` and a virtual environment. `uv add` resolves and installs the dependency, updates `pyproject.toml`, and writes (or updates) `uv.lock` with the exact versions chosen. `uv run` executes a command inside the project's environment without you needing to activate anything.

The two pieces that matter long-term: `pyproject.toml` declares what your project depends on at the loose level ("requests version 2.x or newer"). `uv.lock` records the exact versions installed when the resolver last ran ("requests 2.31.0, with these specific transitive dependencies at these exact versions"). Commit both. A colleague who clones the repo runs `uv sync` and gets the same versions you have, bit-for-bit.

Without a lockfile, a "works on my machine" bug is built in. `requests` might release a patch tomorrow that subtly breaks your code. CI catches it; you don't, because your local environment still has the old version. With a lockfile, both you and CI use the recorded version until you explicitly bump it.

A note on the other tools you'll hear about. **`poetry`** is the previous-generation answer to the same problem; it works, it's still maintained, but `uv` is faster and the community is shifting. **`pipx`** is a different niche: it installs CLI tools (like `black`, `ruff`, `pre-commit`, `pytest` itself when used standalone) into isolated environments so the tools themselves don't conflict with project dependencies. Use `pipx` for tools you run, not import.

#### A first `pyproject.toml`

The new standard for project metadata is `pyproject.toml`. A minimal one:

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "A short description"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31",
    "click>=8.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "ruff>=0.1.0",
    "mypy>=1.5",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

`[project]` is project metadata: name, version, what Python it needs, what it depends on. `[project.optional-dependencies]` groups extras that aren't always installed (here, the development tools). `[build-system]` tells `pip` and other installers how to build the package when someone installs it.

Tool configuration also lives here, in sections named for each tool. `ruff`'s config goes in `[tool.ruff]`. `mypy`'s in `[tool.mypy]`. `pytest`'s in `[tool.pytest.ini_options]`. One file, all the project's settings.

**What could go wrong:** installing into the system Python. If you run `pip install` and Python warns "externally-managed-environment" or you see things installed under `/usr/lib/python3`, you're polluting the system. Create a venv first. The error messages got more helpful on recent systems, but old habits ("just `pip install` it") die hard.

### Code quality tools

A formatter and a linter cost almost nothing to set up and pay off forever. Pick once, configure once, never think about it again.

**`ruff`** is a linter and formatter written in Rust. It's fast (milliseconds where older tools took seconds), it does almost everything older tools did combined (`flake8`, `pyflakes`, `pylint`, `isort`, `black`), and it's becoming the default for new projects. Install it and run it:

```
$ uv add --dev ruff
$ uv run ruff check .         # lint
$ uv run ruff format .        # format
```

Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]
# E: pycodestyle errors
# F: pyflakes
# I: isort (import sorting)
# B: bugbear (common bugs)
# UP: pyupgrade (modernize old syntax)
# SIM: code simplification hints
```

The `select` list is which rule families ruff applies. The whole list is in ruff's docs. Start small and add as you see fit.

`black` is the older formatter ruff's formatter is compatible with. If you're starting fresh, use ruff's formatter and skip `black`. If you're working in a codebase that already uses `black`, leave it; the formats are essentially identical.

**`mypy`** is the type checker. You wrote type hints in Tier 1 because they're documentation, but they're also a contract `mypy` can verify.

```
$ uv add --dev mypy
$ uv run mypy mypackage/
```

The first run will produce a lot of errors, especially in a codebase that's never had type hints. Don't try to fix them all at once. Configure mypy to start strict on new code and lenient on legacy code:

```toml
[tool.mypy]
python_version = "3.10"
warn_unused_ignores = true
warn_return_any = true
warn_unreachable = true

[[tool.mypy.overrides]]
module = "mypackage.new_module"
strict = true
```

That config enforces strict typing on `mypackage.new_module` (the new code you're writing now) and relaxed typing everywhere else. As old modules get touched, you migrate them to strict one at a time.

**`pre-commit`** is the wiring that runs these tools automatically. Without it, you remember to run them most of the time, forget once, push the unformatted code, get a CI failure, push a follow-up commit titled "fix formatting." With it, the git commit itself runs the tools and refuses to complete if anything fails.

Install and configure:

```
$ pipx install pre-commit
$ pre-commit install
```

Configuration in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```

Now every `git commit` runs ruff and mypy. If ruff would change files (because formatting is wrong), it changes them and aborts the commit. You `git add` the changes and try again. If mypy reports a type error, the commit is blocked until you fix it. This stops every formatting argument in code review, because the tool decided already.

**What could go wrong:** type-checking code that calls third-party libraries without stubs. `mypy` will complain that it can't find type information for the library. The fix is to install the stubs package (often named `types-<library>`, like `types-requests`) or to add `ignore_missing_imports = true` to mypy config for that module. Don't ignore globally; it hides real bugs.

### Project layout: src vs flat

Two conventions:

**Flat layout** puts your package next to your tests:

```
myproject/
├── mypackage/
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_core.py
└── pyproject.toml
```

**`src/` layout** nests the package one level deeper:

```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
└── pyproject.toml
```

The src layout is slightly more robust. Why? When you run tests from the flat layout's root, Python finds `mypackage` because the current directory is on `sys.path`. The tests pass even if your package isn't properly installed. With src layout, the only way to import `mypackage` is to install the project (`uv pip install -e .` for editable install), so the tests run against the installed version and catch packaging mistakes before users do.

For a new project, default to src layout. For a small script, flat is fine.

### Packaging and publishing

When your code becomes a library someone else will use, you need to package it. A package is a `.tar.gz` (source distribution) or `.whl` (wheel) file that `pip` can install.

Build it:

```
$ uv build           # or: python -m build
$ ls dist/
mypackage-0.1.0-py3-none-any.whl
mypackage-0.1.0.tar.gz
```

Publish to TestPyPI first (the staging instance), to make sure everything looks right:

```
$ uv publish --publish-url https://test.pypi.org/legacy/
```

Then to real PyPI when you're ready:

```
$ uv publish
```

You need a PyPI account and an API token for either. Both are free.

Semantic versioning is the convention you bump versions under: major version for breaking changes, minor for new features, patch for bug fixes. `1.4.7` → bug fix → `1.4.8`. Add a feature → `1.5.0`. Break the API → `2.0.0`. Stick to this and your users can tell from the version number alone whether upgrading is safe.

This whole section is what you do when your code transitions from "scripts in a repo" to "library on PyPI." Most automation scripts don't need it. Internal tools at work might publish to a private index instead of public PyPI. The mechanics are the same.

## Common pitfalls

1. **No virtual environment.** Installing dependencies globally creates conflicts between projects. Every project gets its own venv. If you don't yet have one, that's the first thing to fix.

2. **No lockfile.** Pinning ranges in `pyproject.toml` (`requests>=2.31`) is not the same as locking exact versions. Use `uv.lock` (or `poetry.lock`) and commit it. Without it, "works on my machine" is the only guarantee.

3. **Tests that hit real external services.** Tests should be hermetic. Mock the network, mock the database, use `tmp_path` for files. Save real-thing tests for a separate integration suite.

4. **100% coverage as the target.** Coverage measures execution, not correctness. A line can be covered by a test that doesn't actually assert anything useful. Aim for tests that catch the bugs you'd actually make. Coverage is a guide, not a grade.

5. **Patching the wrong place.** `patch("requests.get")` patches `requests.get` globally; if `myapp.users` did `from requests import get`, the patch must be `patch("myapp.users.get")`. Patch where the name is bound, not where it was defined.

6. **Forgetting `pre-commit install`.** A `.pre-commit-config.yaml` in the repo does nothing until each developer runs `pre-commit install` once to wire it into their local git hooks. CI should also run the hooks (`pre-commit run --all-files`) so the rule is enforced even when someone forgets.

7. **Ignoring mypy errors with `# type: ignore` without a reason.** Every `# type: ignore` should have a comment explaining why. `# type: ignore[arg-type]  # library has wrong stubs upstream, see issue #123` is useful. Bare `# type: ignore` is technical debt nobody will revisit.

## Try it yourself

Take any project from earlier in the curriculum. Set up: a virtual environment with `uv`, `pytest` with one passing test, `ruff` with a `pyproject.toml` config, `mypy` with at least one type-annotated function, and `pre-commit` running all of them. Commit the result. The tooling should run automatically on the next commit and pass.

<details>
<summary>What "done" looks like</summary>

Your repo should have:

- `pyproject.toml` with `[project]`, dependencies under `dev` extra, and `[tool.ruff]` and `[tool.mypy]` sections.
- `uv.lock` committed alongside it.
- `tests/test_something.py` with at least one `def test_...` function using plain `assert`.
- `.pre-commit-config.yaml` with ruff and mypy hooks.
- `.gitignore` excluding `.venv/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`.

Running `uv sync` on a fresh clone should set everything up. Running `git commit` should run ruff and mypy automatically. Running `uv run pytest` should run the tests.

If any of those don't work, fix the broken link before moving on. The goal of this lecture is not "I read about these tools" but "I have them running on at least one project."
</details>

## How this connects

Tier 5 is the layer underneath every Phase 2 module. The CLI tools you'll build in Module 1 will ship as packages with `pyproject.toml`. Module 2's shell interop scripts need tests because their bugs cause data loss. Module 4's configuration handling deserves type hints and a `mypy` run; the bugs there are subtle. Module 7 covers testing again in depth, with focus on testing automation specifically (mocking subprocess calls, simulating cloud APIs, testing idempotency).

Everything from Tiers 1 through 4 also feeds in: type hints (Tier 1) get checked by mypy here; decorators (Tier 2) get tested with pytest; concurrent code (Tier 4) gets traced with profiling tools you set up alongside these. The tooling is the harness that keeps the code in good shape over time.

For the automation/DevOps path: tests and types pay off the most. Linters are nice but secondary. Packaging is a Module-12 concern; you can skip the publishing details until you have something to publish.

## Recap

- `pytest` replaces `unittest`'s class-based ceremony with plain functions and `assert`. Fixtures share setup. `parametrize` runs one test against many inputs. `pytest.raises` checks for expected exceptions. Patch external systems with `unittest.mock.patch` or HTTP-specific libraries like `responses`.
- Always work inside a virtual environment. `uv` is the modern tool for project setup, dependency management, and execution. Commit `pyproject.toml` and `uv.lock` together. A colleague should be able to clone and `uv sync` to reproduce your environment.
- `ruff` lints and formats. `mypy` type-checks. `pre-commit` runs them on every commit. Configure once in `pyproject.toml`, forget about it after.
- `pyproject.toml` is the modern home for project metadata, dependencies, and tool configuration. One file, all settings.
- Prefer `src/` layout for new projects. It catches packaging mistakes that flat layout hides.
- Build with `uv build`. Publish with `uv publish`. Use semantic versioning. Test against TestPyPI before pushing to PyPI.

## Up next

That's the end of the foundational tiers. The next move is the Phase 2 curriculum: twelve modules taking you from "I can write Python" to "I can ship production automation." Module 1 starts with CLI tools using `argparse`, `click`, `typer`, and `rich`, which is where the dataclasses from Tier 1, the decorators from Tier 2, and the testing tools from this lecture all start earning their keep on the same project.
