# Lecture & quiz reference

How to turn the source module doc's lecture into `lecture.mdx`, and how to author the
`quiz.json` that the source doesn't have. These rules apply to **every course language**
(Python, C, SQL, ...) — the transformation logic doesn't change; only which live component you
use for interactive demos does (Python/C get a real `<Runnable>`; SQL doesn't yet — see below).
Compare the source `curriculum/Python Curriculum Module 01.md` against the result
`curriculum/Python Module 1/1-lecture.mdx` to see every rule below applied for real; when
converting C or SQL, also check whichever module of that language has already been converted,
if any (see `SKILL.md`'s "Before you start").

## Lecture transformation rules

### Sections: keep, drop, add
- **Drop the `# Module N: ...` H1.** The renderer prints the lesson title from `module.json`;
  a duplicate H1 would show twice. Start the file at the first `##` (usually `## Why this matters`).
- **Drop any `## Prerequisites`-style section entirely.** It assumes a local toolchain install
  (a Python interpreter, a C compiler, a local MySQL/Postgres server), an IDE, a terminal, and a
  "Module 0" — none of which exist here, for any language.
- **Keep** these sections, lightly edited: `## Why this matters`, `## What you'll be able to do
  by the end`, `## Core concepts` (with its `###` subsections), `## Common pitfalls`,
  `## How this connects`, `## Recap`, `## Up next`.
- **Add**, right after the objectives list, the no-install note. Word it for the language's
  actual runtime — the shape is the same, only the second sentence's specifics change:

  ```mdx
  <Callout type="info">
  No installation needed. Every code block on this platform has a **Run** button — press it and
  your code executes instantly in the browser. You don't need Python on your machine; you don't
  need a terminal.
  </Callout>
  ```

  For C: "You don't need a C compiler or `gcc` on your machine." For SQL: "You don't need a
  local database server or a `mysql` client — the database lives in your browser tab."

### Re-root local-install-era language to the browser
Scan the prose and fix every assumption that the learner is on a laptop with a local toolchain.
The specific phrases differ by source language, but the fix pattern is the same everywhere —
delete the "Module 0" / local-setup framing, and replace "do X on your machine" with "press
Run":
- "We saw this in Module 0" / any "Module 0" reference → delete the clause (there is no Module 0
  in any language's course).
- Python: "open a terminal", "run `python file.py`", "save the file", "your editor/VS Code/
  PyCharm" → rephrase to "press **Run**" or delete.
- C: "compile with `gcc`", "run `./a.out`", "your Makefile", "link the object files by hand" →
  rephrase to "press **Run**" (the platform compiles+links+runs on Run) or delete; keep concepts
  the compiler still performs (e.g. what a compile error *means*) since those are real and
  happen in-browser too, just without the manual `gcc` invocation.
- SQL: "open a MySQL client", "connect to your local server", "`mysql -u root -p`", "your
  `.sql` script file" → rephrase to "press **Run**" / "**Submit**" or delete. Keep the
  dialect note (this course's IDE is SQLite-flavored; the source transcript may be MySQL —
  flag syntax differences inline as the existing SQL modules do, don't silently paper over them).
- "in the checkpoint", "work the exercises in the curriculum doc", "the mini-project" → "in the
  exercises in this module" (the exercises now live in this module, as lessons).
- Cross-references to other modules by number ("in Module 2") are fine — keep them.

### Convert "predict-then-reveal" into Run-it-yourself
The source teaches interactivity with a **`<details><summary>Answer</summary>`** block the
reader expands. The platform has no `<details>`; it has tip callouts, and — for languages whose
`<Runnable>` component exists (Python, C) — a real **Run** button. Convert each one:

Source:
```markdown
**Try it:** Predict what each of these prints *before* running it. Then run the code to check.

​```python
city = "Austin"
state = "Texas"
print(city)
print("city")
print(f"{city}, {state}")
​```

<details>
<summary>Answer</summary>

​```
Austin
city
Austin, Texas
​```

The first prints the value of the variable `city`. ...
</details>
```

**For Python or C** (stdout-based `<Runnable>`), becomes:
```mdx
**Predict before you run.** What will this print? Make a guess, then press Run:

<Runnable code={`city = "Austin"
state = "Texas"
print(city)
print("city")
print(f"{city}, {state}")`} />

<Callout type="tip">
The first line prints the *value* of `city` — `Austin`. The second prints the literal four
characters `city` because of the quotes. ...
</Callout>
```

**For SQL** (no live grid component yet — see below), becomes a static fenced preview instead
of a `<Runnable>`, with the same predict-first framing and the explanation moved to the callout:
```mdx
**Predict before you run.** What will this query's results grid show? Make a guess:

​```sql
SELECT name, price FROM products WHERE category = 'office' ORDER BY name;
​```

<Callout type="tip">
Running this shows a grid with two columns, `name` and `price`, one row per office product,
alphabetical by name. ...
</Callout>
```
Note the SQL version keeps the *expected-output* description in the callout (unlike Python/C,
where the learner gets it for free by pressing Run) — since there's no live grid to press Run
on yet, don't leave the learner with no way to check their prediction.

The expected-output fenced block from the `<details>` is dropped for Python/C (the learner now
gets it by running); its explanatory prose moves into the `<Callout type="tip">`. For SQL, the
description of the output stays in prose since there's nothing to run yet.

### When to use `<Runnable>` vs. a static code fence
**Python, C** (or any future language with a working stdout `<Runnable>`):
- **`<Runnable code={`...`} />`** for code the learner should run: demos that produce
  interesting output, "predict before you run", "spot the bug", anything the source framed with
  "Try it". Also use it for small illustrative demos the source showed as plain output.
- **Static ```<lang> fence** for code that *should not* run because it's deliberately broken or
  is a fragment (e.g. Python: mismatched quotes, `name = Ada` with no quotes; C: a snippet
  missing a semicolon shown purely to illustrate a compiler error message). Exception: if the
  source explicitly says "Run this and see," make it a `<Runnable>` even when the point is that
  it misbehaves.

**SQL** (until a live results-grid component exists — check `docs/sql-integration-plan.md` and
`CLAUDE.md`'s SQL section for current status before assuming this is still true):
- Every "try it" and demo becomes a **static ```sql fence** with the expected results grid
  described in prose or an ASCII/markdown table underneath — never a `<Runnable>`, since it
  would render nothing (no stdout is produced). If a live `<Runnable>`-for-grids ships later,
  this rule flips to match Python/C and this doc should be updated (a real S3/S4 task noted in
  `CLAUDE.md`, not a silent assumption to make mid-conversion).

### `<Callout>` types
`info` (orientation / "no install"), `tip` (the reveal after a prediction; gentle nudges),
`warning` (gotchas, invalid-on-purpose examples, things that error). Use prose inside; no lists
of bare symbols. Same set, same meanings, for every language.

## MDX safety pass (do this before every lecture checkpoint, every language)
MDX parses `{`, `}`, `<`, `>` in **prose** as JSX/expressions and the build breaks. Rules:
- In prose, wrap any `{`, `}`, `<`, `>`, or `${...}` in **inline code backticks**: write
  `` `{name}` `` and `` `<class 'str'>` ``, never bare. Fenced code blocks and inline code are
  exempt — you don't escape inside them. This matters more for C (`{`/`}` are everywhere in
  block syntax) and generic type-notation prose than for SQL, but check every language's prose
  the same way.
- **Inside `<Runnable code={`...`} />` template literals (compiled live tree, Python/C only):**
  escape every literal `` ${ `` as `` \${ `` — otherwise JavaScript reads it as template
  interpolation and the build fails. Likewise escape any literal backtick inside the code as
  `` \` ``.
  - The **staging** copy of the lecture may leave `${` bare (staging is never compiled). The
    **live** copy must escape it. Safest is to escape in both; required in live.
- Don't leave a stray `<details>`, `<summary>`, or other raw HTML tag — they were all converted.
- Quick check after writing: grep the live `.mdx` for bare `{`/`}`/`<`/`>` on prose lines and for
  unescaped `${` inside `code={`...`}`.

## quiz.json — authored from the lecture (source has none, any language)

A JSON **object** with a single `"questions"` key holding an array of 2–3 question objects.
One correct option per question. **This schema is identical for every language** — nothing
below changes based on whether the module is Python, C, or SQL.

**The top-level value MUST be an object `{ "questions": [...] }`, never a bare array**, and the
question prompt key is **`question`** (not `text`). These match the loader's `Quiz` /
`QuizQuestion` interfaces in `src/lib/content/types.ts`; a bare array or a `text`-keyed prompt
makes the lecture page crash at prerender (`Cannot read properties of undefined (reading 'length')`).
Schema:

```json
{
  "questions": [
    {
      "question": "Question text. May contain \n newlines and inline code like print(\"x\").",
      "options": [
        { "text": "an answer", "correct": false, "explanation": "Why it's wrong — and what's actually true." },
        { "text": "the right answer", "correct": true, "explanation": "Why it's right; reinforce the concept." }
      ]
    }
  ]
}
```

Authoring guidance:
- Pull questions straight from the lecture's hardest-to-internalize points (for Python Module 1:
  quotes vs. variable lookup, the missing-`f` f-string, illegal variable names; for a C module:
  pointer-vs-value semantics, undefined behavior vs. a compile error; for a SQL module: primary
  vs. foreign key, `SELECT *` vs. named columns). Don't test trivia.
- 4 options is typical; exactly one `correct: true`.
- Every **distractor** should encode a real beginner misconception, and its `explanation` should
  correct that misconception — wrong answers teach as much as right ones.
- The `explanation` on the **correct** option restates the rule so a learner who guessed still
  learns the "why."
- Keep code in `text`/`explanation` as plain strings (escape quotes and `\n`); this is JSON, not
  MDX, so no `<Runnable>` here, for any language.