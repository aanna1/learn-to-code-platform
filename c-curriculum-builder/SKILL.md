---
name: c-curriculum-builder
description: Expand one master C-curriculum markdown file into a complete set of per-module lecture docs ("C Curriculum Module NN.md") — one file per module, each fully written in the course's beginner voice and browser-first framing. Use when the user asks to build the C curriculum, split the C master doc into modules, generate the C module docs, author C Module N from the master, or regenerate the C lecture docs. This is the upstream authoring step; the downstream `curriculum-converter` then turns each module doc into the platform lesson bundle.
---

# C Curriculum Builder

Turn **one** master spec — `curriculum/c-curriculum-master.md` — into the full set of
**per-module lecture docs**, one Markdown file per module:
`curriculum/C Curriculum Module NN.md` (NN zero-padded).

The master holds *terse* information per module (objectives, concept seeds, analogies,
example ideas, common mistakes, predict-then-reveal seeds, quiz seeds, and any checkpoint
project brief). This skill **expands** that shorthand into a fully written lecture doc in the
course's teaching voice. It is real authoring, not a copy-paste split: the master is the
outline, the module doc is the finished lesson.

Pipeline position:
`c-curriculum-master.md` → **(this skill)** → `C Curriculum Module NN.md` → (`curriculum-converter`) → platform bundle.

## Before you start — read these

1. `CLAUDE.md` and `docs/c-curriculum-map.md` (the agreed module list, browser-first decision,
   and which modules carry a checkpoint project).
2. `docs/c-in-browser-runtime-options.md` — why C runs in the browser (so framing says
   "press **Run**", never "open a terminal" for the core modules).
3. This skill's reference files (load as needed, don't dump all at once):
   - `reference/master-format.md` — the exact schema the master file must follow, and how each
     field maps into the output doc.
   - `templates/module-template.md` — the required structure of every output module doc.
   - `reference/voice-and-tone.md` — the beginner voice to write in, distilled from the two
     reference course transcripts. **Match this voice; it is the point of the skill.**

## Input

Either "build all modules" or a specific "build Module N". The source is always
`curriculum/c-curriculum-master.md`. If it's missing, stop and tell the user (offer to
generate the skeleton from `assets/c-curriculum-master.SKELETON.md`).

## Output

For each module section in the master, one file:
`curriculum/C Curriculum Module NN.md`, NN zero-padded (`01`, `02`, …). The file follows
`templates/module-template.md` exactly and is written in `reference/voice-and-tone.md`.

## Operating mode — CHECKPOINT PER MODULE

Do **not** generate every module in one shot. Build **one module at a time**; after each,
stop, show the user the finished doc, and wait for approval or edits before the next. If the
user said "build Module N", do only that one.

## Procedure

### S0 — Read and map (no checkpoint)
Read the master file end to end. Confirm the module list and order match
`docs/c-curriculum-map.md`. For the target module, pull its section and note: title,
objectives, concept seeds, analogies, example ideas, common-mistake/UB notes,
predict-then-reveal seeds, quiz seeds, and checkpoint-project brief (if any).

### S1 — Draft the module doc ⟶ CHECKPOINT
Write `curriculum/C Curriculum Module NN.md` per `templates/module-template.md`:
- Open with a short hook in the course voice — no boring preamble (see voice guide).
- Expand each concept seed into plain-language explanation + the master's analogy + a small,
  runnable `c` example. Keep examples short and self-contained.
- Frame execution as pressing **Run** (browser), not a local terminal — except in any module
  explicitly marked as an Advanced Track in the master, which is local by design.
- Turn each predict-then-reveal seed into a `c` code block followed by a
  `<details><summary>Predict the output</summary> … </details>` block.
- Surface every common-mistake / undefined-behavior seed as a clearly marked warning aside.
- Include the `## Quiz seeds` and (if present) `## Checkpoint project` sections so the
  downstream converter has them.
- Run the **humanizer** (below) on the prose.
Show the finished doc and get approval before moving on.

### S2 — Repeat per module / Final pass
Move to the next module only after approval. When all requested modules are done, run the
verification gate.

## Humanizer — required
Invoke the `humanizer` skill on the lecture prose of each module doc before its checkpoint.
Humanize prose only — not `c` code blocks, not `<details>` contents' code, not quiz JSON-ish
seeds. Keep the strong, warm teaching voice; strip AI tells (inflated symbolism, rule-of-three
padding, em-dash overuse, "in conclusion" filler).

## Verification — required gate
Before presenting a module doc, confirm:
- The H1 is `# Module NN — Title` and matches the master's title and order.
- Every section required by `templates/module-template.md` is present and non-empty.
- Every code block is valid, compilable C and is short enough to read at a glance.
- Core (non-Advanced-Track) modules frame execution as **Run**, with no stray "open a
  terminal / run `gcc`" instructions.
- Each predict-then-reveal block has both the code and a `<details>` reveal with the correct
  output.
- Prose contains no bare TODO/placeholder text; the doc is publishable as-is.
- Checkpoint-project and quiz-seed sections are present exactly when the master says they are.
