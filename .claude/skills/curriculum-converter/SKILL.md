---
name: curriculum-converter
description: Convert a "Python Curriculum Module NN.md" lecture document into a complete platform lesson bundle — module.json, the lecture MDX + quiz, and fully authored graded exercises — emitting BOTH the flat curriculum/Python Module N/ staging folder and the nested src/content live tree. Use when the user asks to convert a curriculum module, turn a curriculum module doc into platform lessons, generate lessons from the curriculum, rebuild a module's lessons, or "convert/do Module N".
---

# Curriculum Converter

Turn one source lecture doc — `curriculum/Python Curriculum Module NN.md` — into a complete
platform lesson bundle that matches the format established for **Module 1**. A bundle is a
trimmed lecture lesson + a quiz + several **fully authored** graded exercises (prompt,
starter, solution, hidden tests, hints).

The source docs were written for a laptop course (install Python, open a terminal, run
`python file.py`). This platform runs Python **in the browser** with a **Run** button, has
**no exercises of its own**, and renders **MDX**, not plain Markdown. Conversion is therefore
real authoring work, not cleanup: re-map the doc into the lesson tree, translate the
interactive bits into platform components, and **write the exercises and quiz from scratch**.

## Before you start — read these

1. `CLAUDE.md` and `docs/curriculum-conversion-context.md` (project state + the gap this skill closes).
2. The gold reference — study it, mimic it exactly:
   - Flat staging: `curriculum/Python Module 1/`
   - Nested live: `src/content/languages/python/modules/01-first-programs/`
3. This skill's reference files (load as needed, don't dump all at once):
   - `reference/naming-and-schema.md` — every file/folder name, `module.json` schema, `course.json` wiring.
   - `reference/lecture-and-quiz.md` — the source→`lecture.mdx` transformation and `quiz.json` authoring.
   - `reference/exercises-and-tests.md` — designing exercises + the `tests.py` grading conventions.
   - `templates/` — copyable `tests.py` harnesses. `scripts/grade_check.py` — the headless verifier.

## Input

The module number **N** (e.g. "convert Module 3"). The source file is
`curriculum/Python Curriculum Module NN.md` where **NN is zero-padded** (`03`). If it's
missing, stop and tell the user.

## What you produce — BOTH trees

Every lesson is emitted twice, in two layouts (full mapping in `reference/naming-and-schema.md`):

| Piece | Flat staging (`curriculum/Python Module N/`) | Nested live (`src/content/languages/python/modules/NN-slug/`) |
|---|---|---|
| Module manifest | `module.json` (has top-level `order`) | `module.json` (NO top-level `order`) |
| Lecture | `1-lecture.mdx`, `1-lecture.quiz.json` | `lecture/lecture.mdx`, `lecture/quiz.json` |
| Exercise (order k, slug s) | `k-s.prompt.mdx`, `k-s.starter.py`, `k-s.solution.py`, `k-s.tests.py`, `k-s.hints.json` | `ex-s/exercise/{prompt.mdx,starter.py,solution.py,tests.py,hints.json}` |
| Course registration | — | add `{id,title,order}` to `src/content/languages/python/course.json` |

Folder is **un-padded** (`Python Module 3`); the module `id` is **zero-padded kebab**
(`03-control-flow`).

## Operating mode — CHECKPOINT AT EACH STAGE

Do **not** generate the whole module in one shot. After each stage below, **stop, show the
user what you produced, and wait for explicit approval (or edits) before continuing.** This is
a deliberate, user-chosen workflow — respect it even when the next stage seems obvious.

Stages that each end in a checkpoint: **(1)** plan + `module.json` → **(2)** lecture → **(3)**
quiz → **(4)** each exercise, one at a time → **(5)** mirror to the live tree + `course.json`.
Final verification (6) runs before you hand back stage 5.

## Procedure

### S0 — Read and map (no checkpoint)
Read the source module doc end to end and the two gold-reference Module 1 trees. Note the
module's short title, the lecture's concepts, and every laptop-era assumption you'll need to
re-root (see `reference/lecture-and-quiz.md`).

### S1 — Plan the module + write `module.json`  ⟶ CHECKPOINT
Derive the module `id` (`NN-slug`), `title`, one-sentence `description`, and the lesson list:
the lecture plus **3–4 exercises** you design to drill the lecture's skills, in increasing
difficulty, the last one a small combining "project." Each exercise gets a human title, a
kebab slug, an `ex-<slug>` id, and an order (lecture = 1). Write the **staging** `module.json`
(with top-level `order: N`). Present the plan + the exercise concepts and get approval before
authoring anything. See `reference/naming-and-schema.md`.

### S2 — Convert the lecture ⟶ CHECKPOINT
Produce `1-lecture.mdx` by transforming the source per `reference/lecture-and-quiz.md`: drop
the `# Module N` H1 and the `## Prerequisites` section, add the "no install — press Run"
`<Callout type="info">`, turn every "predict-then-reveal" block into a `<Runnable>` + a
`<Callout type="tip">`, promote key demos to `<Runnable>`, re-root laptop language, and run
the **MDX-safety pass** (no bare `{ } < >` in prose). Then **run the humanizer** (see below)
on the prose. Show the result and get approval.

### S3 — Author the quiz ⟶ CHECKPOINT
Write `1-lecture.quiz.json`: 2–3 multiple-choice questions drawn from the lecture, one correct
option each, every distractor mapping to a real beginner misconception with a teaching
`explanation`. Schema in `reference/lecture-and-quiz.md`. Show and get approval.

### S4 — Author each exercise, one at a time ⟶ CHECKPOINT per exercise
For each planned exercise, write all five files (`prompt.mdx`, `starter.py`, `solution.py`,
`tests.py`, `hints.json`) per `reference/exercises-and-tests.md`. Pick the right `tests.py`
harness from `templates/`. **Run the humanizer** on `prompt.mdx`. Then **headless-verify** with
`scripts/grade_check.py`: the solution must pass all tests and the starter must fail at least
one (proof the grader discriminates). Show the exercise + the grade_check output; get approval
before the next exercise.

### S5 — Mirror to the live tree + register ⟶ CHECKPOINT
Copy the approved files into the nested layout under
`src/content/languages/python/modules/NN-slug/` (rename per the mapping table; the nested
`module.json` drops the top-level `order`). Add the module to `course.json` with the correct
`order`. If the new order collides with existing modules, **surface the conflict to the user**
rather than silently renumbering. Show the final file tree.

### S6 — Final verification (before handing back S5)
Run the full checklist below. Fix anything that fails before presenting.

## Humanizer — required
This skill must use the **humanizer** skill (invoke the `humanizer` Skill) on all authored
prose — the lecture body and every exercise `prompt.mdx` — before those files are finalized at
their checkpoint. Humanize the prose, not code blocks, JSON, or `<Runnable>`/`<Callout>` tags.
Keep the source's strong teaching voice; strip AI tells.

## Verification — required gate
Before presenting the finished module, confirm:
- **Run `scripts/validate_content_shapes.py` on BOTH trees** for the module and it prints `OK`:
  `python scripts/validate_content_shapes.py "src/content/languages/python/modules/NN-slug" "curriculum/Python Module N"`.
  This checks SHAPE, not just parseability — `json.load` passing is **not** sufficient. A bare-array
  `hints.json`/`quiz.json` parses fine but breaks the build (`Cannot read properties of undefined`),
  and a quiz whose prompt uses `text` instead of `question` parses fine but renders a **blank**
  question. The script catches both. Every other `.json` (`module.json`, `course.json`) must still parse.
- (Enforced by the script, stated here so you author it right the first time) `hints.json` is
  `{ "hints": string[] }`; `quiz.json` is `{ "questions": [...] }` with each question keyed
  **`question`** (the per-option label key is `text`) — matches `Hints`/`Quiz`/`QuizQuestion` in
  `src/lib/content/types.ts`.
- Every `.mdx` prose line is MDX-safe: no bare `{ } < >` outside fenced/inline code.
- The on-disk file set exactly matches `module.json`'s `lessons[]` (count, ids, order) in **both** trees.
- For **every** exercise: `grade_check.py` shows solution = all pass, starter = ≥1 fail.
- `course.json` lists the new module with a non-colliding `order`.
- Run `npm run typecheck` if you touched the live tree (the loader is build-time).
