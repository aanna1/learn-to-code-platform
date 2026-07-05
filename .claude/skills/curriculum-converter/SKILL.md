---
name: curriculum-converter
description: Convert a "<Language> Curriculum Module NN.md" lecture document — for any registered or in-progress course language (Python, C, SQL, and future languages) — into a complete platform lesson bundle: module.json, the lecture MDX + quiz, and fully authored graded exercises. Emits BOTH the flat curriculum/<Language> Module N/ staging folder and the nested src/content/languages/<lang-id>/modules/ live tree. Use when the user asks to convert a curriculum module, turn a curriculum module doc into platform lessons, generate lessons from the curriculum, rebuild a module's lessons, or "convert/do Module N" for any language.
---

# Curriculum Converter

Turn one source lecture doc — `curriculum/<Language> Curriculum Module NN.md` — into a
complete platform lesson bundle that matches the format established by the platform's gold
references. A bundle is a trimmed lecture lesson + a quiz + several **fully authored** graded
exercises (prompt, starter, solution, hidden tests, hints). This works for **any course
language on the platform** — Python, C, SQL, and whatever gets added later — because the
lesson-bundle shape (`module.json`, `lecture.mdx`, `quiz.json`, the exercise five-file-ish
bundle) is the same for every language; only the exercise file **extensions** and the **test
harness convention** change per language. See the language table below and
`reference/naming-and-schema.md` for the full matrix.

The source docs were written for a local-install course (open a terminal, run a compiler/
interpreter by hand). This platform runs code **in the browser** with a **Run** button, has
**no exercises of its own**, and renders **MDX**, not plain Markdown. Conversion is therefore
real authoring work, not cleanup: re-map the doc into the lesson tree, translate the
interactive bits into platform components, and **write the exercises and quiz from scratch**.

## Which language?

If the user doesn't say (just "convert Module 3"), **ask which language** — module numbers
overlap across curricula (there's a Python Module 3, and a SQL Module 3 covers different
content entirely). Once you know the language, look it up here:

| Language | id (registry / `course.json`) | Source doc | Staging folder | Live tree | Exercise ext(s) | Test harness | Grader |
|---|---|---|---|---|---|---|---|
| Python | `python` | `Python Curriculum Module NN.md` | `Python Module N` | `src/content/languages/python/modules/NN-slug/` | `.py` | `tests.py`, `test_*()` functions, submission imported as a module | this skill's `scripts/grade_check.py` |
| C | `c` | `C Curriculum Module NN.md` | `C Module N` | `src/content/languages/c/modules/NN-slug/` | `.c` | `tests.c`, separate-compile, `__T__\|name\|PASS/FAIL` lines | project root `scripts/c/grade_check.py` |
| SQL | `sql` | `SQL Curriculum Module NN.md` | `SQL Module N` | `src/content/languages/sql/modules/NN-slug/` | `.sql` + `schema.sql` + `tests.json` (no `tests.sql`) | query-contract result-set diff | project root `scripts/sql/grade_check.mjs` |

**C is not yet registered** in `src/lib/languages/registry.ts` (see `CLAUDE.md`) — that's
expected; author its content tree anyway, just don't expect it to appear on the live site until
someone flips that registration on separately. This skill's job stops at authoring the lesson
bundle.

If a fourth language is added later and isn't in this table, derive its row the same way this
table was built: read that language's integration-plan / test-harness-contract doc under
`docs/`, find its worked example under `scripts/<lang>/example*` if one exists, and add a row —
don't guess.

## Before you start — read these

1. `CLAUDE.md` (project state) and, for the target language, its "\<Language\> language build"
   section in `CLAUDE.md` plus its integration-plan / test-harness-contract doc under `docs/`
   (e.g. `docs/c-test-harness-contract.md`, `docs/sql-test-harness-contract.md`). Skip this for
   Python — its contract is fully inlined in this skill's references.
2. Gold references — study them, mimic them exactly:
   - **Always** study `curriculum/Python Module 1/` and
     `src/content/languages/python/modules/01-first-programs/` — Python is the platform's most
     mature, most-reviewed example and sets the prose voice, checkpoint discipline, and quiz
     style every language should match.
   - **Also** study the most recently converted module **in the target language**, if one
     exists (e.g. `curriculum/SQL Module 2/` +
     `src/content/languages/sql/modules/02-relational-model-and-keys/`) — it shows the
     language-specific exercise contract in a real, shipped example. If none exists yet (true
     for C as of this writing), lean on the worked example under `scripts/<lang>/example*` and
     the contract doc instead.
3. This skill's reference files (load as needed, don't dump all at once):
   - `reference/naming-and-schema.md` — every file/folder name for every language, `module.json`
     schema, `course.json` wiring.
   - `reference/lecture-and-quiz.md` — the source→`lecture.mdx` transformation and `quiz.json`
     authoring (shared across languages, with per-language notes called out).
   - `reference/exercises-and-tests.md` — designing exercises + each language's test-harness
     convention, dispatched by language.
   - `templates/` — copyable test-harness starting points, one set per language.
     `scripts/README.md` explains which grader script to run for which language.

## Input

The **language** and the module number **N** (e.g. "convert SQL Module 3", "do C Module 2").
The source file is `curriculum/<Language> Curriculum Module NN.md` where **NN is zero-padded**
(`03`) and `<Language>` is that language's display name from the table above (`Python`, `C`,
`SQL`). If it's missing, stop and tell the user.

## What you produce — BOTH trees

Every lesson is emitted twice, in two layouts (full mapping, with per-language exceptions, in
`reference/naming-and-schema.md`):

| Piece | Flat staging (`curriculum/<Language> Module N/`) | Nested live (`src/content/languages/<lang-id>/modules/NN-slug/`) |
|---|---|---|
| Module manifest | `module.json` (has top-level `order`) | `module.json` (NO top-level `order`) |
| Lecture | `1-lecture.mdx`, `1-lecture.quiz.json` | `lecture/lecture.mdx`, `lecture/quiz.json` |
| Exercise (order k, slug s) | `k-s.prompt.mdx` + the language's exercise files (below) | `ex-s/exercise/{prompt.mdx, ...same files}` |
| Course registration | — | add `{id,title,order}` to `src/content/languages/<lang-id>/course.json` (create this file, matching the Python/SQL pattern, if this is the language's first converted module) |

Per-language exercise files (order-`k`, slug `s`; the `.prompt.mdx` + `.hints.json` pair is
universal, the middle files vary — see `reference/exercises-and-tests.md`):
- **Python:** `k-s.prompt.mdx`, `k-s.starter.py`, `k-s.solution.py`, `k-s.tests.py`, `k-s.hints.json`
- **C:** `k-s.prompt.mdx`, `k-s.starter.c`, `k-s.solution.c`, `k-s.tests.c`, `k-s.hints.json`
- **SQL:** `k-s.prompt.mdx`, `k-s.schema.sql`, `k-s.starter.sql`, `k-s.solution.sql`, `k-s.tests.json`, `k-s.hints.json`

Folder is **un-padded** (`<Language> Module 3`); the module `id` is **zero-padded kebab**
(`03-control-flow`) — this pattern is identical across languages.

## Operating mode — CHECKPOINT AT EACH STAGE

Do **not** generate the whole module in one shot. After each stage below, **stop, show the
user what you produced, and wait for explicit approval (or edits) before continuing.** This is
a deliberate, user-chosen workflow — respect it even when the next stage seems obvious.

Stages that each end in a checkpoint: **(1)** plan + `module.json` → **(2)** lecture → **(3)**
quiz → **(4)** each exercise, one at a time → **(5)** mirror to the live tree + `course.json`.
Final verification (6) runs before you hand back stage 5.

## Procedure

### S0 — Read and map (no checkpoint)
Read the source module doc end to end and the gold-reference trees (Python's, plus the target
language's most recent module if one exists). Note the module's short title, the lecture's
concepts, and every local-install-era assumption you'll need to re-root (see
`reference/lecture-and-quiz.md`).

### S1 — Plan the module + write `module.json`  ⟶ CHECKPOINT
Derive the module `id` (`NN-slug`), `title`, one-sentence `description`, and the lesson list:
the lecture plus **3–4 exercises** you design to drill the lecture's skills, in increasing
difficulty, the last one a small combining "project" (for languages/modules where a
result-comparison exercise makes sense — see per-language notes in
`reference/exercises-and-tests.md` for exceptions, e.g. SQL's ER-modeling modules). Each
exercise gets a human title, a kebab slug, an `ex-<slug>` id, and an order (lecture = 1). Write
the **staging** `module.json` (with top-level `order: N`). Present the plan + the exercise
concepts and get approval before authoring anything. See `reference/naming-and-schema.md`.

### S2 — Convert the lecture ⟶ CHECKPOINT
Produce `1-lecture.mdx` by transforming the source per `reference/lecture-and-quiz.md`: drop
the `# Module N` H1 and any `## Prerequisites`-style section, add the "no install — press Run"
`<Callout type="info">`, turn every "predict-then-reveal" block into either a live `<Runnable>`
(Python, C — anything whose output is stdout text) or a static fenced preview + explanatory
callout (SQL — until `<Runnable>` can render a results grid, see
`reference/lecture-and-quiz.md`), promote key demos the same way, re-root local-install
language, and run the **MDX-safety pass** (no bare `{ } < >` in prose). Then **run the
humanizer** (see below) on the prose. Show the result and get approval.

### S3 — Author the quiz ⟶ CHECKPOINT
Write `1-lecture.quiz.json`: 2–3 multiple-choice questions drawn from the lecture, one correct
option each, every distractor mapping to a real beginner misconception with a teaching
`explanation`. Schema in `reference/lecture-and-quiz.md` (identical for every language). Show
and get approval.

### S4 — Author each exercise, one at a time ⟶ CHECKPOINT per exercise
For each planned exercise, write `prompt.mdx` + `hints.json` plus that language's specific
files (starter/solution/tests, or schema/starter/solution/tests.json for SQL) per
`reference/exercises-and-tests.md`'s section for the target language. Pick the right harness
template from `templates/`. **Run the humanizer** on `prompt.mdx`. Then **headless-verify**
with that language's grader (see `scripts/README.md` for which command): the solution must
pass all tests/cases and the starter must fail at least one (proof the grader discriminates).
Show the exercise + the grader output; get approval before the next exercise.

### S5 — Mirror to the live tree + register ⟶ CHECKPOINT
Copy the approved files into the nested layout under
`src/content/languages/<lang-id>/modules/NN-slug/` (rename per the mapping table; the nested
`module.json` drops the top-level `order`). Add the module to
`src/content/languages/<lang-id>/course.json` with the correct `order` — if this is the
language's first converted module, create `course.json` following the Python/SQL pattern
(`{ "language": "<lang-id>", "displayName": "<Language>", "tagline": "...", "modules": [...] }`).
If the new order collides with existing modules, **surface the conflict to the user** rather
than silently renumbering. Show the final file tree.

### S6 — Final verification (before handing back S5)
Run the full checklist below. Fix anything that fails before presenting.

## Humanizer — required
This skill must use the **humanizer** skill (invoke the `humanizer` Skill) on all authored
prose — the lecture body and every exercise `prompt.mdx` — before those files are finalized at
their checkpoint. Humanize the prose, not code blocks, JSON, or `<Runnable>`/`<Callout>` tags.
Keep the source's strong teaching voice; strip AI tells.

## Verification — required gate
Before presenting the finished module, confirm:
- **Run `scripts/validate_content_shapes.py` on BOTH trees** for the module and it prints `OK`
  (this script is language-agnostic — it walks any directory tree looking for `hints.json` /
  `quiz.json` by filename, so it works unchanged for Python/C/SQL):
  `python scripts/validate_content_shapes.py "src/content/languages/<lang-id>/modules/NN-slug" "curriculum/<Language> Module N"`.
  This checks SHAPE, not just parseability — `json.load` passing is **not** sufficient. A bare-array
  `hints.json`/`quiz.json` parses fine but breaks the build (`Cannot read properties of undefined`),
  and a quiz whose prompt uses `text` instead of `question` parses fine but renders a **blank**
  question. The script catches both. Every other `.json` (`module.json`, `course.json`,
  SQL's `tests.json`) must still parse.
- (Enforced by the script, stated here so you author it right the first time) `hints.json` is
  `{ "hints": string[] }`; `quiz.json` is `{ "questions": [...] }` with each question keyed
  **`question`** (the per-option label key is `text`) — matches `Hints`/`Quiz`/`QuizQuestion` in
  `src/lib/content/types.ts`. Both are identical across every language.
- Every `.mdx` prose line is MDX-safe: no bare `{ } < >` outside fenced/inline code.
- The on-disk file set exactly matches `module.json`'s `lessons[]` (count, ids, order) in **both** trees.
- For **every** exercise: the language's grader (`scripts/README.md`) shows solution = all pass,
  starter = ≥1 fail.
- `course.json` (in the target language's `src/content/languages/<lang-id>/` folder) lists the
  new module with a non-colliding `order`.
- Run `npm run typecheck` if you touched the live tree (the loader is build-time) — this holds
  regardless of language, since it's the shared Next.js loader that reads all of them.