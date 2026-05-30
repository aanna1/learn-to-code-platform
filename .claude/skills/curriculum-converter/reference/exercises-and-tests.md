# Exercises & tests reference

The source curriculum has **no exercises** — you author them. Each exercise is a five-file
bundle. Study Module 1's four exercises (`curriculum/Python Module 1/2-…` through `5-…`) as the
gold reference.

## Designing the exercise set
- **3–4 exercises per module**, ordered by increasing difficulty, the last one a small
  "project" that combines the module's concepts (Module 1 ends with "Profile Card" /
  "Type Detective").
- Each exercise drills a **specific skill from the lecture**. Map them to the lecture's
  `## What you'll be able to do` list so coverage is complete.
- Give each a memorable human title → kebab slug → `ex-<slug>` id (see naming reference).

## The five files

### `prompt.mdx`
Keep this one's **H1 title** (unlike the lecture, which drops its H1 — the exercise pane shows
the prompt verbatim). Structure, mirroring Module 1:
```mdx
# <Exercise Title>

One or two sentences of framing that connect to the lecture.

## Your task

What to build, stated concretely. If exact output is required, say "prints **exactly** these
lines" and show them in a fenced block.

## Requirements

- Bullet list of must-haves the grader checks (exact strings, number of lines, a function name
  and signature, etc.).

## Example output

​```
The literal expected output, if applicable.
​```
```
This is MDX — apply the same safety rules (no bare `{ } < >` in prose; use inline code). Most
prompts need no `<Runnable>`, but you may include one for a worked warm-up.

### `starter.py`
Runnable (no syntax errors) but **intentionally incomplete**, so it *fails* the tests. Use
`# TODO:` comments to scaffold. For an output exercise, TODOs that print nothing; for a function
exercise, define the required function with a placeholder body (`pass` or a wrong return).

### `solution.py`
A clean, idiomatic reference that **passes every test**. Comment it the way the lecture taught
(explain *why*, not *what*). This is also the answer revealed by the "Solution" button.

### `hints.json`
A JSON **object** with a single `"hints"` key whose value is an **array of 3–4 strings**,
progressively more specific — first a nudge, last nearly the answer. Escape quotes.

**The top-level value MUST be an object, never a bare array.** The loader types this file as
`{ "hints": string[] }` (`src/lib/content/types.ts` -> `interface Hints`); a bare `[ "..." ]`
array breaks the build. Example shape:
```json
{
  "hints": [
    "Start by deciding which print() calls you need.",
    "Each line of output comes from its own print() call.",
    "Watch the apostrophe in \"Let's go!\" — wrap that string in double quotes.",
    "A comment goes on the line above the code it describes, starting with #."
  ]
}
```

### `tests.py` — the grader
Conventions the runtime enforces (do not deviate):
- The learner's submission is importable as a module named **`submission`**.
- Define one or more **`test_*()`** functions. The **first line of each docstring** is the
  human-readable name shown to the learner — write it as a clear assertion ("Output's first line
  is 'Hello, world!'").
- Each test `assert`s with a **friendly failure message** that tells the learner what was
  expected vs. what happened and hints at the fix.
- Put any interactive/demo code under `if __name__ == "__main__":`. Importing `submission` sets
  its `__name__` to `"submission"` (not `"__main__"`), so a learner's own `__main__` block is
  skipped during grading — rely on that to avoid `input()` EOF crashes.

Pick a harness from `templates/`:

**A. Output-capture** (`templates/tests.output-capture.py`) — for "print exactly this" tasks.
The submission's top-level code runs on import; a helper captures stdout and tests assert on the
printed lines. This is the Module 1 style.

**B. Function-call** (`templates/tests.function-call.py`) — for "write a function that
returns/does X" tasks. Tests do `import submission`, call `submission.func(...)`, and assert on
return values. Prefer this whenever grading should be deterministic.

### Handling `input()` (Module 2 and beyond)
The browser runtime supports interactive `input()`, but the grader runs headless. Two options:
- **Preferred:** put the gradeable logic in a **pure function** (no `input()`/`print()` inside)
  and call it from tests with arguments. Keep the `input()`+`print()` shell under
  `if __name__ == "__main__":`. Clean and deterministic.
- **If you must grade an interactive script end-to-end:** monkeypatch input in the test —
  ```python
  import builtins
  def test_with_scripted_input(monkeypatch=None):
      answers = iter(["Ada", "25"])
      builtins.input = lambda prompt="": next(answers)
      # import/reload submission, capture stdout, assert
  ```
  (Restore `builtins.input` afterward if other tests need real behavior.)

## Headless verification — `scripts/grade_check.py`
After writing each exercise, prove the grader discriminates:
```bash
python scripts/grade_check.py <tests.py> <solution.py> <starter.py>
```
It runs every `test_*` against the solution (expects **all pass**) and against the starter
(expects **≥1 fail**), printing a per-test report. It does **not** require pytest. A passing
solution that the starter also passes means the tests are too weak — tighten them. A failing
solution means the test or the solution is wrong — fix before the checkpoint.

If an exercise uses `input()`, either grade the pure function (option above) or pass scripted
input; `grade_check.py` feeds EOF to stdin by default, so a script that calls `input()` at top
level will error — which is exactly why interactive code belongs under `__main__`.
