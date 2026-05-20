# Programming Education Platform — Project Brief

## Overview

Build a free, fully static educational website for teaching programming to complete beginners. The site combines in-depth lectures with interactive, terminal-style coding exercises that run entirely in the browser.

**For this initial build, implement only the homepage and the Python course.** However, the entire architecture must be designed so that adding a new language (JavaScript, Rust, etc.) later is a matter of writing a runtime adapter and dropping in lesson content — *not* a refactor of components, routes, or core logic. Treat language extensibility as a first-class architectural concern from line one.

The audience is complete beginners with no prior programming background. The tone of any seed content you write should be friendly, concrete, and assume zero prior knowledge.

## Tech Stack

- **Framework:** Next.js 14+ (App Router) with TypeScript, configured for static export (`output: "export"`) so the entire site can be served from any static host
- **Styling:** Tailwind CSS, with CSS custom properties for theming
- **Code Editor:** Monaco Editor via `@monaco-editor/react`
- **Terminal:** xterm.js for code output display and interactive input
- **Python Runtime:** Pyodide (loaded from CDN to avoid bloating the bundle)
- **Linting:** Ruff via `@astral-sh/ruff-wasm-web` (or the closest working equivalent) for real-time static analysis in the editor
- **Lecture Content:** MDX via `@next/mdx`, so lectures can mix prose with React components
- **Deployment Target:** Vercel free tier as primary; static export must also work on GitHub Pages

**Hard constraints:** No backend. No database. No accounts. No paid services. Everything runs in the user's browser.

## Core Architectural Principle: Language Extensibility

The system must treat "the language being taught" as a parameter, not a hardcoded assumption. Concretely:

1. Define a `Language` interface in `src/lib/languages/types.ts` that captures everything language-specific: runtime adapter, linter adapter, error explainer, display config (name, color, icon, Monaco language ID, file extension).
2. Implement Python as the first concrete `Language` in `src/lib/languages/python/`.
3. Register all languages in `src/lib/languages/registry.ts`. The homepage and nav read from this registry — no hardcoded language lists in components.
4. All routes use `[language]` as a URL parameter. Components operate against the `Language` interface only.
5. Lesson content lives in a per-language directory under `src/content/languages/<lang>/` and is loaded by a generic content loader that works the same for every language.
6. **Never** scatter `if (language === 'python')` checks through the codebase. All language-specific behavior must go through the interface.

Adding JavaScript later should mean: write a JS runtime adapter (e.g., using a sandboxed iframe or a JS interpreter library), add MDX lesson files, register the language in the registry. Zero changes to components or routes.

## Directory Structure

```
/
├── public/
├── src/
│   ├── app/
│   │   ├── page.tsx                          # Homepage
│   │   ├── layout.tsx                        # Root layout (nav, theme provider)
│   │   ├── learn/
│   │   │   └── [language]/
│   │   │       ├── page.tsx                  # Language course outline
│   │   │       └── [module]/
│   │   │           └── [lesson]/
│   │   │               └── page.tsx          # Lesson page (lecture or exercise)
│   │   └── cheatsheet/
│   │       └── [language]/
│   │           └── page.tsx
│   ├── components/
│   │   ├── ide/                              # Code editor, terminal, resizable split
│   │   ├── lesson/                           # Lecture renderer, inline runnable code, quiz, hints
│   │   ├── nav/                              # Top bar, sidebar, theme toggle, shortcuts overlay
│   │   └── ui/                               # Buttons, modals, callouts, etc.
│   ├── lib/
│   │   ├── languages/
│   │   │   ├── types.ts                      # Language interface
│   │   │   ├── registry.ts                   # Language registration
│   │   │   └── python/
│   │   │       ├── runtime.ts                # Pyodide adapter
│   │   │       ├── linter.ts                 # Ruff adapter
│   │   │       ├── errorExplainer.ts         # Friendly error translations
│   │   │       └── config.ts                 # Display config
│   │   ├── progress/                         # localStorage progress + autosave
│   │   ├── content/                          # Lesson loader
│   │   └── theme/                            # Theme tokens, provider
│   └── content/
│       └── languages/
│           └── python/
│               ├── course.json
│               ├── cheatsheet.mdx
│               └── modules/
│                   └── 01-fundamentals/
│                       ├── module.json
│                       └── 01-hello-world/
│                           ├── lecture.mdx
│                           ├── quiz.json
│                           └── exercise/
│                               ├── prompt.mdx
│                               ├── starter.py
│                               ├── solution.py
│                               ├── tests.py
│                               └── hints.json
```

## Routing

- `/` — Homepage
- `/learn/[language]` — Course outline for a language
- `/learn/[language]/[module]/[lesson]` — Specific lesson
- `/cheatsheet/[language]` — Cheat sheet for a language

Top nav contains: **Home** and a **Languages** entry. For now Languages only contains Python, but it must be data-driven from the language registry so adding more is automatic.

## Features

### 1. Homepage
A minimal, welcoming landing page. Project name, one-paragraph intro for absolute beginners, and a grid of "language cards" — each card links to that language's course outline. Only Python is shown for now, but the grid layout supports more. Theme toggle in the top right.

### 2. Course outline page (`/learn/python`)
Hierarchical view of modules and the lessons inside each. **Free navigation** — every lesson is accessible at any time, no gating, no required order. Completion checkmarks pulled from localStorage are shown next to completed lessons. A "Continue where you left off" button surfaces the last-visited lesson if any.

### 3. Lesson page
Each lesson has a `type` in its config: `"lecture"` or `"exercise"`. The page renders accordingly.

**Lecture lessons:**
- MDX content rendered with custom components
- Inline runnable code blocks — any code block in the MDX marked as runnable becomes a small, editable, runnable mini-IDE using the same runtime as full exercises (see Feature 4)
- End-of-lecture quiz (see Feature 5)
- "Mark as complete" button at the bottom

**Exercise lessons:**
- Problem statement (rendered from `prompt.mdx`) on the left or top
- Full IDE on the right or bottom: Monaco editor + xterm.js terminal in a **resizable split** (user can drag the divider)
- **Run** button: executes the user's code in Pyodide, streams stdout/stderr to the terminal, handles `input()` calls interactively so the terminal feels like a real shell
- **Submit** button: runs hidden test cases against the user's code and reports pass/fail per test, with a friendly summary
- **Real-time linting**: Ruff (or the chosen WASM linter) surfaces syntax errors and warnings inline in the Monaco gutter as the user types
- **Friendly error explanations**: when Pyodide reports an error, look up the error type in a Python error explainer module and render a plain-English explanation below the traceback (see Feature 6)
- **Progressive hints**: a "Stuck?" button reveals hints one at a time. After all hints are revealed (or at the user's choice), a "Show solution" option appears
- **Reset to starter code** button (with a confirmation prompt)
- **Code autosave** to localStorage as the user types
- **Show solution** option, available after passing or on demand

### 4. Inline runnable code in lectures
An MDX component (e.g., `<Runnable>`) that wraps a code block to make it editable and runnable inline. It uses the same Pyodide runtime as full exercises but has no tests or submission flow — just edit and run. Should be small, unobtrusive, and visually distinct from regular code blocks.

### 5. End-of-lecture mini quiz
2–3 multiple choice questions per lecture, loaded from `quiz.json`. Each option shows an explanation of why it's right or wrong when selected. Users can retry. Quiz completion contributes to the lesson's completion state in localStorage.

### 6. Friendly error explanations
A module (`src/lib/languages/python/errorExplainer.ts`) maps Python error types — `NameError`, `IndentationError`, `TypeError`, `IndexError`, `KeyError`, `ZeroDivisionError`, `AttributeError`, `ValueError`, `SyntaxError`, etc. — to short, beginner-friendly plain-English explanations of what the error usually means and how to fix it. When Pyodide reports an error, parse the type, look up the explanation, and render it in a callout below the traceback. The explainer must be its own module so it's easy to expand and so other languages can implement their own.

### 7. Progress tracking via localStorage
Track per-language, per-lesson:
- Completion status (lecture viewed + quiz passed, or exercise tests passed)
- Quiz attempts and best score
- Saved code per exercise (autosaved)
- Last-visited lesson

Wrap all localStorage access in a small `progress` module so the storage key schema is centralized and easy to migrate later.

### 8. Cheat sheet
A dedicated page per language at `/cheatsheet/[language]`, content loaded from `cheatsheet.mdx`. For Python, include sections for: variables and types, control flow, common string methods, list operations, dict operations, common built-in functions, basic file I/O, and basic error handling. Linked from the top nav and from a small "?" button inside the IDE.

### 9. Keyboard shortcuts
- `Ctrl/Cmd + Enter` — Run code
- `Ctrl/Cmd + Shift + Enter` — Submit (on exercise pages)
- `Ctrl/Cmd + /` — Toggle line comment (Monaco default)
- `Esc` — Close any open modal (hints, solution, shortcuts overlay)

A small "?" or keyboard icon in the IDE opens a shortcuts overlay listing all of these.

### 10. Theme
Light/dark toggle in the top nav, preference saved in localStorage. The palette uses warm and cool tones rather than pure white/black:

- **Light mode:** Warm off-white background (cream or parchment feel), deep slate text, soft teal/sage accents, warm amber for highlights and call-to-action
- **Dark mode:** Deep navy or warm charcoal background (never pure black), warm off-white text, muted teal accents, soft amber highlights

Drive everything through CSS custom properties so every component picks up theme changes automatically. Overall feel should be minimal but a little playful: gentle rounded corners, soft shadows, a touch of personality in hover states and transitions. Avoid sterile-corporate or aggressively-modern aesthetics.

### 11. Mobile / responsive layout
On screens narrower than ~768px:
- Lecture content renders in a clean, readable layout
- **Hide the IDE entirely** on exercise pages. Show a friendly message in its place: something like "Coding exercises need a wider screen — switch to a laptop or desktop to try this one. The lecture above is fully readable on mobile."
- Top nav collapses to a hamburger menu
- Cheat sheet remains accessible and readable

Mobile is for reading only. Don't try to make the IDE work on small screens.

## Content Schema

### `course.json` (per language)
```json
{
  "language": "python",
  "displayName": "Python",
  "tagline": "...",
  "modules": [
    { "id": "01-fundamentals", "title": "Fundamentals", "order": 1 }
  ]
}
```

### `module.json` (per module)
```json
{
  "id": "01-fundamentals",
  "title": "Fundamentals",
  "description": "...",
  "lessons": [
    { "id": "01-hello-world", "title": "Hello, World", "type": "exercise", "order": 1 }
  ]
}
```

### Lesson folder contents
- Lecture lessons: `lecture.mdx`, `quiz.json`
- Exercise lessons: `prompt.mdx`, `starter.py`, `solution.py`, `tests.py`, `hints.json`

### `quiz.json`
```json
{
  "questions": [
    {
      "question": "...",
      "options": [
        { "text": "...", "correct": true, "explanation": "..." },
        { "text": "...", "correct": false, "explanation": "..." }
      ]
    }
  ]
}
```

### `hints.json`
```json
{ "hints": ["First hint.", "Second hint.", "Third hint."] }
```

### `tests.py`
Use a simple test format runnable inside Pyodide — either a list of assertion functions or pytest-style if pytest works cleanly in Pyodide. Pick whichever is most reliable. Tests should be hidden from the user by default but the **results** (which passed, which failed, and a short message per failure) are shown.

The content loader should make adding a new module a matter of creating a folder, adding it to the parent JSON, and writing the files. No code changes required.

## Out of Scope

- Accounts, logins, databases, anything server-side
- Implementing languages other than Python (architecture must accommodate them; do not build them)
- Producing the full real curriculum — that comes from external lesson plans I will provide later. Only the seed content listed in Deliverables should be written now.
- LLM-based feedback
- Anything paid

## Deliverables (Phase 1)

1. Full project scaffold per the directory structure above
2. Homepage with one Python language card
3. Course outline page for Python
4. Lesson page renderer supporting both lecture and exercise layouts
5. Full IDE: Monaco + xterm.js + resizable split + run + submit + autosave + progressive hints + reset + friendly errors + keyboard shortcuts + shortcuts overlay
6. Pyodide runtime integration with working interactive `input()` (configure any required headers — e.g., COOP/COEP for SharedArrayBuffer — in `next.config.js` and `vercel.json` as needed; use whichever approach gives the cleanest interactive terminal experience)
7. Ruff (or equivalent) integration for real-time linting in the editor gutter
8. Theme system with light/dark toggle and the palette described
9. Mobile responsive layout with the IDE hidden on small screens
10. localStorage progress tracking and code autosave, wrapped in a clean `progress` module
11. Python cheat sheet page with starter content (you write it)
12. **Three seed lessons** to prove the end-to-end flow works. These are scaffolds — the real content comes later. Don't worry about pedagogical depth:
    - **Module 1, Lesson 1 (lecture):** Introduction to variables. Include one inline runnable code example. Two-question quiz.
    - **Module 1, Lesson 2 (exercise):** Write a function `greet(name)` that returns `"Hello, <name>!"`. Include starter code, tests, hints, solution.
    - **Module 1, Lesson 3 (exercise):** Read a name with `input()` and print a greeting. Exercises the interactive terminal end-to-end.
13. README with setup, local dev, and deployment instructions for both Vercel and static export to any host

## Conventions

- TypeScript strict mode
- Components in PascalCase; hooks prefixed with `use`
- All language-aware code goes through the `Language` interface — no scattered `if (language === 'python')` checks
- Lesson content loaded at build time where possible (Next.js static generation)
- Pyodide loaded lazily — only on pages that actually need it (don't slow down the homepage or pure lecture pages with no inline runnables)
- Components co-located with their styles where Tailwind isn't enough

## Suggested Workflow

I'd recommend tackling this roughly in this order:

1. Scaffold the project, the `Language` interface, and the Python language adapter
2. Build the IDE in isolation (you can mount it on a temporary `/dev/ide` route during development)
3. Build the lesson page renderer with both layouts
4. Wire it all together via the three seed lessons
5. Build the homepage, course outline, and cheat sheet pages
6. Polish theming, mobile layout, keyboard shortcuts, and the shortcuts overlay last

Feel free to ask clarifying questions before you start if anything in this spec is ambiguous.
