# Master file format — `curriculum/c-curriculum-master.md`

One file is the single source of truth for the whole C curriculum. It has a **course header**
block, then one **module section** per module. The builder reads this and expands each module
section into a full `C Curriculum Module NN.md` lecture doc.

The master is meant to be **terse** — seeds, not finished prose. The skill does the writing.

---

## 1. Course header (top of the file, once)

```
# C Curriculum — Master Spec

## Course meta
- Audience: complete beginners (recommended after the Python course)
- Runtime: browser (press Run); Advanced Tracks are local by design
- Voice: see reference/voice-and-tone.md

## Module list
| NN | Title | Checkpoint project | Track |
|----|-------|--------------------|-------|
| 01 | The C Environment | — | core |
| 02 | Types, Variables & Operators | — | core |
| ... | ... | ... | ... |
```

The **Module list** table is authoritative for module count, order, titles, which modules
carry a checkpoint project, and whether a module is `core` (browser) or `advanced` (local).
The builder cross-checks this against `docs/c-curriculum-map.md`.

---

## 2. Module section (repeat per module)

Each module is one `## Module NN — Title` section containing these labelled fields. Use short
bullets; the builder expands them.

```
## Module 06 — Pointers

### Description
One sentence on what this module is about.

### Prerequisites
- Module 05 (arrays & strings)

### Learning objectives
- Explain what a pointer is (address vs. value)
- Use & and * correctly
- Pass a variable to a function by pointer
- ...

### Concepts
For each concept: a name, a plain-language seed, an analogy, an example idea, and a gotcha.

- name: Address vs. value
  seed: A variable lives at an address in memory; a pointer stores that address.
  analogy: A pointer is like a house address written on paper — not the house itself.
  example: declare int x; print &x; make int *p = &x; print *p.
  gotcha: Reading *p before p points at anything valid is undefined behavior.

- name: Pass by pointer
  seed: Passing &x lets a function change the caller's variable.
  analogy: Handing someone your address so they can deliver to your house, not a photocopy of it.
  example: void addOne(int *n){ (*n)++; } called on &score.
  gotcha: Forgetting the * inside the function changes the address, not the value.

### Predict-then-reveal seeds
- code: int x = 5; int *p = &x; *p = 9; printf("%d", x);
  reveal: 9   (writing through the pointer changed x)

### Quiz seeds
- q: What does & do?
  correct: Gives the address of a variable
  distractors:
    - Dereferences a pointer  (why wrong: that's *)
    - Allocates memory        (why wrong: that's malloc)

### Checkpoint project        # include ONLY if the Module list marks one
- name: (only if this module ends in a checkpoint project)
- brief: what the learner builds, the skills it drills, and what "done" looks like.
```

### Field → output mapping

| Master field | Where it goes in the module doc |
|---|---|
| Description | the one-line subtitle under the H1 |
| Prerequisites | `## Prerequisites` |
| Learning objectives | `## What you'll learn` (bulleted) |
| Concepts[].seed + analogy + example | a `##`/`###` concept section with prose + a `c` example |
| Concepts[].gotcha | a **Watch out** warning aside near that concept |
| Predict-then-reveal seeds | `c` code block + `<details>` reveal |
| Quiz seeds | `## Quiz seeds` (kept for the converter) |
| Checkpoint project | `## Checkpoint project` (kept for the converter) |

---

## 3. Rules

- **NN is zero-padded** everywhere (`01`, `06`, `10`).
- A module gets a `### Checkpoint project` field **only** if the Module list table marks it.
- Keep seeds terse. If a seed is already a full paragraph, the builder still rewrites it into
  the course voice for consistency.
- Advanced-Track modules (`advanced` in the table) are framed as **local** (real toolchain,
  terminal, editor) — the only place the "press Run" framing does not apply.
- Don't put finished lecture prose in the master. The master is the outline; the module doc is
  the lesson. This keeps one source of truth and makes regeneration cheap.
