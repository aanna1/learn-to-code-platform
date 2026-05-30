# Lecture & quiz reference

How to turn the source module doc's lecture into `lecture.mdx`, and how to author the
`quiz.json` that the source doesn't have. Compare the source `curriculum/Python Curriculum
Module 01.md` against the result `curriculum/Python Module 1/1-lecture.mdx` to see every rule
below applied for real.

## Lecture transformation rules

### Sections: keep, drop, add
- **Drop the `# Module N: ...` H1.** The renderer prints the lesson title from `module.json`;
  a duplicate H1 would show twice. Start the file at the first `##` (usually `## Why this matters`).
- **Drop `## Prerequisites` entirely.** It assumes a Python install, an IDE, a terminal, and a
  "Module 0" — none of which exist here.
- **Keep** these sections, lightly edited: `## Why this matters`, `## What you'll be able to do
  by the end`, `## Core concepts` (with its `###` subsections), `## Common pitfalls`,
  `## How this connects`, `## Recap`, `## Up next`.
- **Add**, right after the objectives list, the no-install note:

  ```mdx
  <Callout type="info">
  No installation needed. Every code block on this platform has a **Run** button — press it and
  your code executes instantly in the browser. You don't need Python on your machine; you don't
  need a terminal.
  </Callout>
  ```

### Re-root laptop-era language to the browser
Scan the prose and fix every assumption that the learner is on a laptop:
- "We saw this in Module 0" / any "Module 0" reference → delete the clause (there is no Module 0).
- "open a terminal", "run `python file.py`", "save the file", "your editor/VS Code/PyCharm" →
  rephrase to "press **Run**" or delete.
- "in the checkpoint", "work the exercises in the curriculum doc", "the mini-project" → "in the
  exercises in this module" (the exercises now live in this module, as lessons).
- Cross-references to other modules by number ("in Module 2") are fine — keep them.

### Convert "predict-then-reveal" into Run-it-yourself
The source teaches interactivity with a **`<details><summary>Answer</summary>`** block the
reader expands. The platform has no `<details>`; it has a real **Run** button and tip callouts.
Convert each one:

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

Becomes:
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

The expected-output fenced block from the `<details>` is dropped (the learner now gets it by
running); its explanatory prose moves into the `<Callout type="tip">`.

### When to use `<Runnable>` vs. a static code fence
- **`<Runnable code={`...`} />`** for code the learner should run: demos that produce
  interesting output, "predict before you run", "spot the bug", anything the source framed with
  "Try it". Also use it for the small illustrative demos the source showed as plain output
  (e.g. the `type(...)` demo, the f-string demos).
- **Static ```python fence** for code that *should not* run because it's deliberately broken or
  is a fragment (mismatched quotes, `name = Ada` with no quotes, `print(name)` before
  assignment). Exception: if the source explicitly says "Run this and see," make it a
  `<Runnable>` even when the point is that it misbehaves (e.g. the missing-`f` f-string).

### `<Callout>` types
`info` (orientation / "no install"), `tip` (the reveal after a prediction; gentle nudges),
`warning` (gotchas, invalid-on-purpose examples, things that error). Use prose inside; no lists
of bare symbols.

## MDX safety pass (do this before every lecture checkpoint)
MDX parses `{`, `}`, `<`, `>` in **prose** as JSX/expressions and the build breaks. Rules:
- In prose, wrap any `{`, `}`, `<`, `>`, or `${...}` in **inline code backticks**: write
  `` `{name}` `` and `` `<class 'str'>` ``, never bare. Fenced code blocks and inline code are
  exempt — you don't escape inside them.
- **Inside `<Runnable code={`...`} />` template literals (compiled live tree):** escape every
  literal `` ${ `` as `` \${ `` — otherwise JavaScript reads it as template interpolation and
  the build fails. (Example: the "Cost: \${price}" bug demo.) Likewise escape any literal
  backtick inside the code as `` \` ``.
  - The **staging** copy of the lecture may leave `${` bare (staging is never compiled), matching
    Module 1. The **live** copy must escape it. Safest is to escape in both; required in live.
- Don't leave a stray `<details>`, `<summary>`, or other raw HTML tag — they were all converted.
- Quick check after writing: grep the live `.mdx` for bare `{`/`}`/`<`/`>` on prose lines and for
  unescaped `${` inside `code={`...`}`.

## quiz.json — authored from the lecture (source has none)

A JSON **object** with a single `"questions"` key holding an array of 2–3 question objects.
One correct option per question.

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
- Pull questions straight from the lecture's hardest-to-internalize points (for Module 1: quotes
  vs. variable lookup, the missing-`f` f-string, illegal variable names). Don't test trivia.
- 4 options is typical; exactly one `correct: true`.
- Every **distractor** should encode a real beginner misconception, and its `explanation` should
  correct that misconception — wrong answers teach as much as right ones.
- The `explanation` on the **correct** option restates the rule so a learner who guessed still
  learns the "why."
- Keep code in `text`/`explanation` as plain strings (escape quotes and `\n`); this is JSON, not
  MDX, so no `<Runnable>` here.
