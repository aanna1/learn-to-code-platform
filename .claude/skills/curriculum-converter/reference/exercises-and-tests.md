# Exercises & tests reference

The source curriculum has **no exercises**, in any language — you author them. Each exercise is
a small multi-file bundle: `prompt.mdx` + `hints.json` (identical shape for every language) plus
that language's own starter/solution/tests files (the part that differs — see the dispatch
below). Study the closest gold-reference exercises for your target language before writing new
ones: Python's `curriculum/Python Module 1/2-…` through `5-…`; SQL's
`curriculum/SQL Module 1/` and `curriculum/SQL Module 2/`; C has no converted exercises yet, so
use `scripts/c/example/` (`tests.c`/`solution.c`/`starter.c`) plus
`docs/c-test-harness-contract.md` as the reference instead.

## Designing the exercise set (same rules, every language)
- **3–4 exercises per module**, ordered by increasing difficulty, the last one a small
  "project" that combines the module's concepts (Python Module 1 ends with "Profile Card" /
  "Type Detective"; SQL's early modules keep this gentler since no query syntax is taught yet).
- Each exercise drills a **specific skill from the lecture**. Map them to the lecture's
  `## What you'll be able to do` list so coverage is complete.
- Give each a memorable human title → kebab slug → `ex-<slug>` id (see `reference/naming-and-schema.md`).
- **Exception — non-executable answers.** Some modules (SQL's ER-modeling and normalization
  modules are the known case) ask for answers that aren't a runnable query or program — an ERD,
  a functional-dependency list, a normal-form judgment. Don't force those into the query/code
  contract below. `docs/sql-test-harness-contract.md` §7 specs a separate `"modeling"` lesson
  type with `question.json`/`answer.json` canonical-form comparison for exactly this case; if
  you hit a module like this for any language, raise it with the user rather than authoring a
  contrived executable exercise just to fit the mold.

## The two universal files

### `prompt.mdx`
Keep this one's **H1 title** (unlike the lecture, which drops its H1 — the exercise pane shows
the prompt verbatim). Structure, for every language:
```mdx
# <Exercise Title>

One or two sentences of framing that connect to the lecture.

## Your task

What to build, stated concretely. If exact output/results are required, say so precisely (e.g.
Python: "prints **exactly** these lines"; SQL: "the results grid shows exactly these rows, in
this order") and show them in a fenced block.

## Requirements

- Bullet list of must-haves the grader checks (exact strings, number of lines, a function name
  and signature, a table/column name, etc. — whatever the language's contract actually grades).

## Example output

​```
The literal expected output/result, if applicable.
​```
```
This is MDX — apply the same safety rules as the lecture (no bare `{ } < >` in prose; use
inline code). Most prompts need no live component; Python/C may include a `<Runnable>` for a
worked warm-up (SQL: use a static fence — see `reference/lecture-and-quiz.md`).

### `hints.json`
A JSON **object** with a single `"hints"` key whose value is an **array of 3–4 strings**,
progressively more specific — first a nudge, last nearly the answer. Escape quotes. Identical
shape for every language.

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

## Which language's test harness? — dispatch

Jump to the section for the target language. **Do not mix conventions** — e.g. don't write a
Python-style `test_*()` function for a C exercise. Each language's harness is lock-stepped with
that language's actual browser runtime worker; deviating breaks "passes the grader ⟺ passes in
the browser."

- **Python** → `## Python` below (this skill's original, most detailed convention).
- **C** → `## C` below, full spec in `docs/c-test-harness-contract.md`.
- **SQL** → `## SQL` below, full spec in `docs/sql-test-harness-contract.md`.
- Anything else → read that language's `docs/*-test-harness-contract.md` or
  `docs/*-integration-plan.md` first; don't improvise a new grading convention inside a
  conversion.

---

## Python

### `starter.py`
Runnable (no syntax errors) but **intentionally incomplete**, so it *fails* the tests. Use
`# TODO:` comments to scaffold. For an output exercise, TODOs that print nothing; for a function
exercise, define the required function with a placeholder body (`pass` or a wrong return).

### `solution.py`
A clean, idiomatic reference that **passes every test**. Comment it the way the lecture taught
(explain *why*, not *what*). This is also the answer revealed by the "Solution" button.

### `tests.py` — the grader
**How the grader runs (the contract, mirrored by `scripts/grade_check.py` and the browser
runtime):** the learner's code is imported as a real module named **`submission`**, and the test
file is then executed *inside that module's own namespace*. Because of that single fact, any of
these test styles work — use whichever is clearest:
- `import submission` / `from submission import func` / `importlib.reload(sys.modules["submission"])`
  (the file-module style the templates use);
- call the submission's functions **directly** by name, no import (`func(...)`), since the test
  shares the submission's namespace;
- **monkeypatch** a name with `globals()[name] = fake` and the submission's own functions will pick
  it up (same namespace) — handy for faking `roll_die`, `input`, `random`, etc.

`scripts/grade_check.py` runs tests the exact same way, so "passes grade_check" means "passes in
the browser." If you ever change one, change the other.

Conventions the runtime enforces (do not deviate):
- The learner's submission is importable as a module named **`submission`** (and its names are in
  scope directly, per above).
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

### Headless verification
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

---

## C

Full spec: `docs/c-test-harness-contract.md` — read it before authoring the first C exercise;
this section summarizes it.

### `starter.c` / `solution.c`
Same intent as Python's: the starter compiles and runs but **fails ≥1 test**; the solution
**passes every test**. Both may keep their own `main()` for the learner's "press Run"
experience — the harness neutralizes it (below), so it never collides with grading.

### `tests.c` — the grader
Unlike Python's shared-namespace import, C uses a **separate-compile model**:
1. `tests.c` **owns `main()`**. It declares the prototypes of whatever the exercise asks the
   learner to implement, calls them, and checks results — it does not import or `#include` the
   submission's source.
2. It prints **one machine-readable line per case**:
   ```
   __T__|<name>|PASS
   __T__|<name>|FAIL|<short, beginner-friendly message>
   ```
3. The submission is compiled with **`-Dmain=__student_main__`** (applied to the submission's
   translation unit *only*), which renames any `main()` the learner kept so it can't collide
   with the harness's `main()`. This is the C mirror of Python's "import as a module, skip
   `__main__`."

Minimal harness (from the contract doc):
```c
#include <stdio.h>
int sum_to(int n);   /* implemented by submission.c */

static void expect_eq(const char *name, int got, int want) {
    if (got == want) printf("__T__|%s|PASS\n", name);
    else printf("__T__|%s|FAIL|expected %d but your code returned %d\n", name, want, got);
}

int main(void) {
    expect_eq("sum_to(5) is 15", sum_to(5), 15);
    return 0;
}
```
Use `templates/tests.c` as the copyable starting point; adapt the prototypes/cases per exercise.

### Build model (must match the worker exactly)
Separate-compile, then link:
```
cc <CFLAGS> -Dmain=__student_main__ -c submission.c -o submission.o
cc <CFLAGS>                          -c tests.c      -o tests.o
cc -target wasm32-wasi <SANITIZE> submission.o tests.o -o out.wasm
```
`<CFLAGS>` = `-target wasm32-wasi -std=c11 -Wall -Wextra -O0 -fsanitize=undefined
-fno-sanitize-trap=undefined`. `grade_check.py` (project root `scripts/c/`) and the browser
worker (`src/lib/languages/c/c.worker.ts`) must both compile exactly this way — if you ever
need to change the flags, change both.

### Sanitizer reach — don't over-promise
UBSan catches signed overflow, shifts, fixed-size local-array OOB, misalignment, div-by-zero —
and prints a readable line before aborting (fed to `errorExplainer` as `UndefinedBehavior`).
**No heap/leak/use-after-free detection** on this path (ASan doesn't link on `wasm32-wasi`).
Don't author an exercise whose grading *depends on* catching a heap bug — grade via `__T__`
case results and compiler warnings instead.

### Headless verification
```bash
python3 scripts/c/grade_check.py <tests.c> <solution.c> [<starter.c>]
```
(Note: this is the **project root's** `scripts/c/`, not this skill's `scripts/` — see
`scripts/README.md`.) Verdict rules: compile failure → fail with the first `error:` line; every
`__T__` line `PASS` and exit 0 → pass; a trap/non-zero exit surfaces the UBSan/diagnostic line;
no output within 10s → timeout fail. Exits 0 only if the solution passes everything and the
starter fails ≥1 case.

---

## SQL

Full spec: `docs/sql-test-harness-contract.md` — read it before authoring the first SQL
exercise in a new module; this section summarizes the common "query contract" (§1–§6). §7's
`"modeling"` contract is a different, rarer shape — see "Exception — non-executable answers"
above.

SQL is the platform's first **non-stdout** language: queries return *tables*, so grading is
**structured result-set comparison**, not line-parsing.

### `schema.sql`
Fixture: `CREATE TABLE` + seed `INSERT`s. Runs before the learner's SQL on a **fresh, in-memory
database per test case** — mutations in one case never leak into another. May contain multiple
statements; runs as one `db.run(...)`.

### `starter.sql` / `solution.sql`
**Query-only** files — no schema, no `CREATE TABLE`. The solution's query/statement must make
every case in `tests.json` pass; the starter must fail at least one. Keep both strictly inside
the SQL syntax the course has taught up to this module (e.g. Module 1 teaches no `WHERE`/DDL
yet, so its exercises stay to `SELECT` column lists).

### `tests.json` — the grader
An array of case objects (a **bare array**, unlike `hints.json`/`quiz.json` which are objects —
this is SQL's one schema-shape exception, and it's intentional; don't "fix" it to `{ "cases":
[...] }`, that would break the loader/grader's actual contract):
```json
[
  {
    "name": "returns the three priciest products, most expensive first",
    "setup": "INSERT INTO products (id, name, price, category) VALUES (6, 'Vault', 999, 'home');",
    "probe": "SELECT name, price FROM products WHERE category = 'office' ORDER BY name;",
    "orderMatters": true,
    "caseLenient": false,
    "expected": {
      "columns": ["name", "price"],
      "rows": [["Desk", 210], ["Chair", 95], ["Lamp", 40]]
    }
  }
]
```
Field meanings (full detail in the contract doc):
- `name` (required) — shown in the results panel.
- `expected` (required) — `{ columns: string[], rows: unknown[][] }`, the correct result set.
- `setup` (optional) — extra SQL run after `schema.sql`, before the learner's SQL (per-case
  fixture variation).
- `probe` (optional) — SQL run **after** the learner's SQL; when present, compare **its**
  result set instead of the learner's own (the pattern for grading `INSERT`/`UPDATE`/`DELETE`/
  DDL, whose own return value isn't the answer). For a mutation exercise, always add a second
  case whose probe checks a row/table that should be **unchanged** — otherwise a learner who
  forgets a `WHERE` clause can still pass.
- `orderMatters` (default `true`) — `false` compares rows as a multiset (order-independent).
- `caseLenient` (default `false`) — case-insensitive **column name** comparison only, never
  values.

Comparison rules: columns compared first (count + names), then row count, then cell-by-cell via
JSON serialization (SQLite's loose typing means `210` and `210.0` unify as one JS number — give
computed columns a stable `AS alias` so the expected name is deterministic).

### Headless verification
```bash
node scripts/sql/grade_check.mjs <exercise-dir>
```
(Note: this is the **project root's** `scripts/sql/`, not this skill's `scripts/` — see
`scripts/README.md`. Requires `sql.js@1.14.1` installed — same engine the browser loads, so
unlike C's `zig cc` proxy there's no engine gap here.) `<exercise-dir>` must contain `schema.sql`,
`tests.json`, `solution.sql`, and optionally `starter.sql`. Exit 0 only if the solution passes
every case and (no starter, or the starter fails ≥1). Worked examples:
`scripts/sql/example/` (a `SELECT` exercise) and `scripts/sql/example-dml/` (an `UPDATE` graded
by probe, demonstrating the "unchanged rows" case).

### Loader quirk to know about
The live-tree loader (`src/lib/content/loader.ts`) **prepends `schema.sql` to the editor code**
for Run, and sends the worker only `{ cases }` (no separate schema) — because the browser
worker's `run()` path doesn't seed `schema.sql` on its own. This means the grader (which seeds
`schema.sql` separately from the query file) and the browser (which gets schema+query
concatenated) are two different code paths that happen to converge for query-contract
exercises. If you ever see them diverge, that's a real bug to flag, not something to
paper over in content — see `CLAUDE.md`'s S3 notes for how this was originally verified in
lock-step.