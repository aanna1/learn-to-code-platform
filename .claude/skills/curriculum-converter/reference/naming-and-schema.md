# Naming & schema reference

Everything here is reverse-engineered from the platform's shipped gold references (Python
Module 1; SQL Modules 1–2). Match it exactly; the build-time content loader and the renderer
both depend on these names — for **every** language, not just Python.

## The language-profile matrix

This is the one table to check before touching any file. Every other section in this doc
parametrizes on it.

| | Python | C | SQL |
|---|---|---|---|
| id (`course.json` `"language"`, live folder) | `python` | `c` | `sql` |
| Display name | Python | C | SQL |
| Registered in `src/lib/languages/registry.ts`? | yes | **no — intentionally, see `CLAUDE.md`** | yes |
| Source doc | `Python Curriculum Module NN.md` | `C Curriculum Module NN.md` | `SQL Curriculum Module NN.md` |
| Staging folder | `Python Module N` | `C Module N` | `SQL Module N` |
| Live tree root | `src/content/languages/python/modules/` | `src/content/languages/c/modules/` | `src/content/languages/sql/modules/` |
| Exercise file set | `.prompt.mdx`, `.starter.py`, `.solution.py`, `.tests.py`, `.hints.json` | `.prompt.mdx`, `.starter.c`, `.solution.c`, `.tests.c`, `.hints.json` | `.prompt.mdx`, `.schema.sql`, `.starter.sql`, `.solution.sql`, `.tests.json`, `.hints.json` |
| Test-harness style | `test_*()` functions; submission imported as a module named `submission` | separate-compile; `tests.c` owns `main()`, prints `__T__\|name\|PASS/FAIL` lines | query-contract: `tests.json` array of cases; result-set diff, no code execution inside the submission file itself |
| Headless grader | this skill's `scripts/grade_check.py` | project root `scripts/c/grade_check.py` | project root `scripts/sql/grade_check.mjs` |
| Full contract doc | inlined in `reference/exercises-and-tests.md` | `docs/c-test-harness-contract.md` | `docs/sql-test-harness-contract.md` |
| Worked example | `curriculum/Python Module 1/` exercises | `scripts/c/example/` | `scripts/sql/example/`, `scripts/sql/example-dml/` |
| Live component for interactive lecture demos | `<Runnable>` (streams stdout) | `<Runnable>` (streams stdout) | **no live component yet** — output is a results grid, which `<Runnable>` can't render; use a static fenced preview (see `reference/lecture-and-quiz.md`) |

`module.json` and `course.json` themselves are **not** in this table because their schema is
identical for every language — see below.

## The number appears in three different forms

For source "Module N" in language `<Language>` (`Python`/`C`/`SQL`/...), you will write the
number three ways. Getting these right is the most common place to slip:

| Where | Form | `<Language>` Module 3 example |
|---|---|---|
| Source filename | zero-padded, with "Curriculum" | `<Language> Curriculum Module 03.md` |
| Staging folder | un-padded, no "Curriculum" | `<Language> Module 3` |
| Module `id` / live folder | zero-padded + kebab slug | `03-control-flow` |
| `order` fields | plain integer | `3` |

This pattern is **identical across languages** — only `<Language>` changes. (Verified against
Python's `Python Curriculum Module 03.md` → `Python Module 3`, and SQL's
`SQL Curriculum Module 01.md` → `SQL Module 1`.)

The **module slug** comes from the module's short title — the part of the source H1 before the
em-dash/colon detail. Source `# Module 1: First Programs — Print, Comments, Variables, Types`
→ short title "First Programs" → slug `first-programs` → id `01-first-programs`. Same rule for
every language: SQL's `# Module 1: Databases, RDBMS & Why Attackers Care` → id
`01-databases-and-security` (a judgment call on a punchier slug — the mapping doesn't have to
be mechanical, but it must read as this module's short title).

## Two output layouts

### Flat staging — `curriculum/<Language> Module N/`
A single flat folder. Files are named `<order>-<slug>.<role>.<ext>`, where the middle files
depend on the language (see the matrix above):

```
curriculum/Python Module 3/            curriculum/C Module 3/                  curriculum/SQL Module 3/
  module.json                            module.json                             module.json
  1-lecture.mdx                          1-lecture.mdx                           1-lecture.mdx
  1-lecture.quiz.json                    1-lecture.quiz.json                     1-lecture.quiz.json
  2-<slug>.prompt.mdx                    2-<slug>.prompt.mdx                     2-<slug>.prompt.mdx
  2-<slug>.starter.py                    2-<slug>.starter.c                      2-<slug>.schema.sql
  2-<slug>.solution.py                   2-<slug>.solution.c                     2-<slug>.starter.sql
  2-<slug>.tests.py                      2-<slug>.tests.c                        2-<slug>.solution.sql
  2-<slug>.hints.json                    2-<slug>.hints.json                     2-<slug>.tests.json
  ... (one set per exercise)             ... (one set per exercise)              2-<slug>.hints.json
                                                                                  ... (one set per exercise)
```

The lecture's slug is always literally `lecture` (so `1-lecture.mdx`), for every language.
Exercise order starts at **2**, for every language.

### Nested live — `src/content/languages/<lang-id>/modules/NN-slug/`
The layout the app actually loads. Lecture and each exercise get their own subfolder — this
structure is **identical for every language**; only the files inside `ex-<slug>/exercise/`
differ per the matrix above:

```
src/content/languages/<lang-id>/modules/03-control-flow/
  module.json
  lecture/
    lecture.mdx
    quiz.json
  ex-<slug>/
    exercise/
      prompt.mdx
      <language's starter/solution/tests/schema files>
      hints.json
  ... (one ex-<slug>/ per exercise)
```

**Loader note (language detection):** the content loader (`src/lib/content/loader.ts`) detects
the SQL exercise bundle by the presence of `starter.sql` on disk — it branches on **files
present**, never on `language === "sql"`. Keep it that way: if you're authoring for a language
whose loader support doesn't exist yet, adding files alone won't make it render; that's a
separate engineering task (see the relevant `docs/*-integration-plan.md`), not this skill's job.

### Name mapping between the two trees

| Flat staging file | Nested live path |
|---|---|
| `1-lecture.mdx` | `lecture/lecture.mdx` |
| `1-lecture.quiz.json` | `lecture/quiz.json` |
| `k-<slug>.prompt.mdx` | `ex-<slug>/exercise/prompt.mdx` |
| `k-<slug>.hints.json` | `ex-<slug>/exercise/hints.json` |
| Python: `k-<slug>.starter.py` / `.solution.py` / `.tests.py` | `ex-<slug>/exercise/starter.py` / `solution.py` / `tests.py` |
| C: `k-<slug>.starter.c` / `.solution.c` / `.tests.c` | `ex-<slug>/exercise/starter.c` / `solution.c` / `tests.c` |
| SQL: `k-<slug>.schema.sql` / `.starter.sql` / `.solution.sql` / `.tests.json` | `ex-<slug>/exercise/schema.sql` / `starter.sql` / `solution.sql` / `tests.json` |

File **contents are identical** across the two trees with **one exception**, which applies to
every language that uses `<Runnable>` in its lecture (Python, C): the live `.mdx` files are
compiled as MDX/JSX, so inside `<Runnable code={`...`}>` template literals any literal `${`
must be escaped as `\${` in the live copy (see `reference/lecture-and-quiz.md`, "MDX safety").
The staging copy leaves it bare (staging is never compiled). Non-`.mdx` files (`.py`, `.c`,
`.sql`, `.json`) are byte-identical across trees for every language.

## `module.json` schema (identical for every language)

Lessons are listed in order; the lecture is always first.

```json
{
  "id": "03-control-flow",
  "title": "Control Flow",
  "description": "One-sentence summary of what the module teaches.",
  "order": 3,
  "lessons": [
    { "id": "lecture",        "title": "<lecture title>", "type": "lecture",  "order": 1 },
    { "id": "ex-<slug>",      "title": "<Exercise Title>", "type": "exercise", "order": 2 },
    { "id": "ex-<slug>",      "title": "<Exercise Title>", "type": "exercise", "order": 3 }
  ]
}
```

Field notes:
- `id` (module) = the zero-padded kebab slug, **matching the live folder name**.
- `title` (module) = the short title ("Control Flow"). The **lecture's** `title` is the
  descriptive concept list (e.g. "Print, Comments, Variables & Types") — it is usually
  different from the module title and is what the renderer prints atop the lecture page.
- Lesson `id`: the lecture is `"lecture"`; each exercise is `"ex-<slug>"`. These ids are NOT
  the flat-file prefixes — the prefix is the order number.
- **Critical difference between trees:** the **staging** `module.json` includes the top-level
  `"order": N`; the **nested live** `module.json` **omits** it (module order lives in
  `course.json` for the live tree). Everything else is identical.
- None of this varies by language. If a future language needs a non-`"lecture"`/`"exercise"`
  lesson `type` (SQL's design docs mention a `"modeling"` type for structured, non-query
  exercises — see `docs/sql-test-harness-contract.md` §7), that's a schema extension to raise
  with the user, not something to silently invent inside a conversion.

## `course.json` registration (live tree only, identical shape for every language)

`src/content/languages/<lang-id>/course.json` enumerates modules:

```json
{
  "language": "<lang-id>",
  "displayName": "<Language>",
  "tagline": "...",
  "modules": [
    { "id": "01-first-programs", "title": "First Programs", "order": 1 },
    { "id": "01-fundamentals",   "title": "Fundamentals",   "order": 2 }
  ]
}
```

Add `{ "id": "NN-slug", "title": "<short title>", "order": <N> }` for the new module. If
`src/content/languages/<lang-id>/course.json` doesn't exist yet (this is the language's first
converted module — true for C until someone converts its first module), create it fresh,
matching this shape and the tone of the Python/SQL `tagline`s.

**Ordering caveat:** orders here are not guaranteed to equal the module number — e.g. Python's
seed `01-fundamentals` sits at `order: 2`. Before writing, read the current `modules[]`, choose
an `order` that places the new module correctly in the learner's sequence, and if it collides
with an existing entry, **stop and ask the user** how to renumber rather than guessing. This
applies identically regardless of language.