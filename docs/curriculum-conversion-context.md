# Curriculum conversion — project context

**Purpose:** read this first if you're converting the existing Python curriculum into
platform lessons. It explains what the project is, the constraints that shape it, and the
content format — so the conversion issues read as obvious consequences rather than a random
list. The companion is `CLAUDE.md` (build history/state) and `Claude Code Prompt.md` (the
original spec).

## The project, in one paragraph

A **free, beginner-focused "learn to code" website** that pairs in-depth written lessons with
a coding environment that runs **entirely in the browser** — no install, no account, no
server. A learner reads a short lecture, runs real code inline, and then does graded
exercises in a built-in editor + terminal that execute Python via Pyodide (CPython compiled
to WebAssembly). It currently teaches Python only, but the architecture treats *"the language
being taught"* as a swappable parameter.

## The constraints that shape everything

Three hard rules drive most of the design decisions:

1. **It's fully static.** The whole site is pre-built to flat HTML/JS (`next build` → an
   `out/` folder any dumb host can serve). There is no backend at request time — so anything
   dynamic (running code, grading, saving progress) happens **in the user's browser**.
2. **Code runs in the browser, not on a machine.** Python executes through Pyodide in a Web
   Worker. That means: no real filesystem (only an in-memory one that resets each run), no
   `pip install` of arbitrary packages, no terminal, no "save this file and run
   `python foo.py`." The runtime is real Python, but the *environment around it* is nothing
   like a laptop.
3. **Adding a language is a drop-in, never a rewrite.** All language-specific behavior (how
   to run code, lint it, explain errors) lives behind a single `Language` interface + a
   registry. No page ever says "if Python." Content is organized by language for the same
   reason.

## How content actually works (this is the crux)

The platform does **not** consume a lesson document. It reads a **directory tree** where
every *lesson* is a bundle of small files:

- A **lecture lesson** = `lecture.mdx` (the prose, written in MDX so it can embed interactive
  components) + an optional `quiz.json` (2–3 multiple-choice questions).
- An **exercise lesson** = `prompt.mdx` + `starter.py` + `solution.py` + `tests.py` (hidden
  auto-grader) + `hints.json` (progressive hints).
- Lessons are grouped into modules via `module.json`, and modules into a course via
  `course.json`.

Two platform-specific authoring facts matter most:

- **MDX is not plain Markdown.** Bare `{`, `}`, `<`, `>` in prose are parsed as code/JSX and
  break the build (fenced/inline code is exempt). Interactivity comes from specific
  components: `<Runnable>` (an editable, runnable mini-snippet) and `<Callout>` (an aside).
- **Grading is a single-file convention.** `tests.py` defines `test_*()` functions that call
  the learner's code and `assert`; the first docstring line is the test's shown name;
  interactive/demo code goes under `if __name__ == "__main__":` so it's skipped during
  grading.

## Where the project stands

The **engine is finished** (six build phases): the IDE, the Python runtime with interactive
`input()`, linting, friendly errors, the lesson renderer for both layouts, quizzes, progress
tracking, homepage, course outline, cheat sheet, theming, and mobile handling. To prove it
end-to-end, **3 hand-authored seed lessons** exist. The platform works; what it lacks is
*content at scale*.

## Where the curriculum came from, and the gap

There's a separate, pre-written **Python curriculum: 14 module documents** (`Module 01`–`14`
under `curriculum/`), each a polished 400–600-line Markdown lecture. They're genuinely good —
strong voice, anticipate beginner confusion, explain *why*. But they were written for a
**conventional, install-Python-on-your-laptop course**, not for this platform. So they don't
drop in, for reasons that all trace back to the constraints above:

- They're **lectures only** — every module says "do the exercises in the curriculum doc," but
  that doc doesn't exist, so the entire graded-exercise half of the platform has no source.
- They're **one big document per module**, whereas the platform wants a module split into a
  trimmed lecture lesson + several exercise lessons (each its own file bundle).
- They use mechanisms the platform expresses differently: "predict the output, then reveal a
  hidden answer" (vs. the platform's *run-it-yourself* `<Runnable>` and *MCQ* `quiz.json`),
  and raw HTML/Markdown that isn't valid MDX.
- They assume a **laptop environment** — install Python, open a terminal, use VS Code, run
  `python file.py`, a nonexistent "Module 0", `pip install`/`venv`/third-party packages
  (Module 10), real files with `open()` (Module 11), terminal `pytest` (Module 14) — none of
  which exist in a zero-install browser runtime.

So the conversion work isn't "clean up some prose." It's: re-map each module into the
platform's lesson-bundle tree, translate the interactive bits into the platform's components,
author the missing exercises and quizzes from scratch, and re-root the environment
assumptions from "your laptop" to "press Run in your browser."

## The one-line framing

**A finished browser-only teaching engine with a specific file-bundle content format, plus a
high-quality but laptop-era lecture set that has to be re-shaped to fit it.** Every conversion
issue is a point where the lecture set assumes something the platform deliberately doesn't
have.
