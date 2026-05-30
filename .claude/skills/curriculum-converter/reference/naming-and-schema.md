# Naming & schema reference

Everything here is reverse-engineered from the Module 1 gold reference. Match it exactly; the
build-time content loader and the renderer both depend on these names.

## The number appears in three different forms

For source "Module N", you will write the number three ways. Getting these right is the most
common place to slip:

| Where | Form | Module 3 example |
|---|---|---|
| Source filename | zero-padded, with "Curriculum" | `Python Curriculum Module 03.md` |
| Staging folder | un-padded, no "Curriculum" | `Python Module 3` |
| Module `id` / live folder | zero-padded + kebab slug | `03-control-flow` |
| `order` fields | plain integer | `3` |

The **module slug** comes from the module's short title — the part of the source H1 before the
em-dash/colon detail. Source `# Module 1: First Programs — Print, Comments, Variables, Types`
→ short title "First Programs" → slug `first-programs` → id `01-first-programs`.

## Two output layouts

### Flat staging — `curriculum/Python Module N/`
A single flat folder. Files are named `<order>-<slug>.<role>.<ext>`:

```
curriculum/Python Module 3/
  module.json
  1-lecture.mdx
  1-lecture.quiz.json
  2-<slug>.prompt.mdx
  2-<slug>.starter.py
  2-<slug>.solution.py
  2-<slug>.tests.py
  2-<slug>.hints.json
  3-<slug>.{prompt.mdx,starter.py,solution.py,tests.py,hints.json}
  ... (one set per exercise)
```

The lecture's slug is always literally `lecture` (so `1-lecture.mdx`). Exercise order starts
at **2**.

### Nested live — `src/content/languages/python/modules/NN-slug/`
The layout the app actually loads. Lecture and each exercise get their own subfolder:

```
src/content/languages/python/modules/03-control-flow/
  module.json
  lecture/
    lecture.mdx
    quiz.json
  ex-<slug>/
    exercise/
      prompt.mdx
      starter.py
      solution.py
      tests.py
      hints.json
  ... (one ex-<slug>/ per exercise)
```

### Name mapping between the two trees

| Flat staging file | Nested live path |
|---|---|
| `1-lecture.mdx` | `lecture/lecture.mdx` |
| `1-lecture.quiz.json` | `lecture/quiz.json` |
| `k-<slug>.prompt.mdx` | `ex-<slug>/exercise/prompt.mdx` |
| `k-<slug>.starter.py` | `ex-<slug>/exercise/starter.py` |
| `k-<slug>.solution.py` | `ex-<slug>/exercise/solution.py` |
| `k-<slug>.tests.py` | `ex-<slug>/exercise/tests.py` |
| `k-<slug>.hints.json` | `ex-<slug>/exercise/hints.json` |

File **contents are identical** across the two trees with **one exception**: the live
`.mdx` files are compiled as MDX/JSX, so inside `<Runnable code={`...`}>` template literals any
literal `${` must be escaped as `\${` in the live copy (see `reference/lecture-and-quiz.md`,
"MDX safety"). Module 1's staging copy leaves it bare; its live copy escapes it. `.py` and
`.json` files are byte-identical across trees.

## `module.json` schema

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

## `course.json` registration (live tree only)

`src/content/languages/python/course.json` enumerates modules:

```json
{
  "language": "python",
  "displayName": "Python",
  "tagline": "...",
  "modules": [
    { "id": "01-first-programs", "title": "First Programs", "order": 1 },
    { "id": "01-fundamentals",   "title": "Fundamentals",   "order": 2 }
  ]
}
```

Add `{ "id": "NN-slug", "title": "<short title>", "order": <N> }` for the new module.

**Ordering caveat:** orders here are not guaranteed to equal the module number — e.g. the
original seed `01-fundamentals` sits at `order: 2`. Before writing, read the current
`modules[]`, choose an `order` that places the new module correctly in the learner's sequence,
and if it collides with an existing entry, **stop and ask the user** how to renumber rather
than guessing.
