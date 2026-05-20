# CLAUDE.md — project working notes

**Read this file first at the start of every session, before doing anything else.**
It's the handoff record: what's done, what's next, and the decisions a future session
needs to continue without re-deriving them.

## What this is

A free, fully static educational website for teaching programming to complete
beginners: in-depth lectures + interactive, browser-based coding exercises. **Python
only for this build**, but the architecture treats "the language being taught" as a
parameter so adding JavaScript/Rust later is an adapter + content drop-in, never a
refactor.

- Full spec: `docs/Claude Code Prompt.md` (the authoritative brief).
- Lesson-plan source for later content phases: `curriculum/` (Modules 01–14 =
  fundamentals; Tiers 1–5 = advanced, currently OUT of scope).
- Repo: https://github.com/aanna1/learn-to-code-platform (private, account `aanna1`).

## Tech stack

Next.js 14 (App Router) + TypeScript strict, `output: "export"` (static). Tailwind with
CSS-custom-property theming. Planned for later phases: Monaco editor, xterm.js terminal,
Pyodide (Python runtime, from CDN), Ruff WASM (linting), MDX via `@next/mdx` (lectures).
Hard constraints: no backend, no DB, no accounts, no paid services — everything runs in
the browser.

## Build plan (approved)

Phases follow the brief's "Suggested Workflow":

1. **Scaffold + language abstraction** ✅ DONE
2. **IDE in isolation** on a temp `/dev/ide` route — Monaco + xterm + resizable split,
   Run (Pyodide + interactive `input()`), Submit (hidden tests), Ruff linting, friendly
   errors, hints, reset, autosave, keyboard shortcuts + overlay. ✅ DONE
3. **Lesson renderer** (both layouts) + generic content loader + quiz + inline `<Runnable>`. ✅ DONE
4. **Seed lessons** (the 3 from the brief) + end-to-end wire-up. ✅ DONE (folded into Phase 3 —
   the renderer/loader are untestable with no content, so the 3 seed lessons were authored
   alongside them as the validation fixture).
5. **Homepage + course outline + cheat sheet** (polished). ← **NEXT** (a *functional* outline
   page already exists from Phase 3; Phase 5 is the polished homepage, outline, and the
   not-yet-built cheat sheet).
6. **Polish**: theme, mobile (hide IDE < 768px), shortcuts overlay, README, deploy docs.

## Decisions locked in (from kickoff Q&A)

- **Phase 1 content scope = the 3 seed lessons only.** The 14 curriculum modules become
  real content in a later content phase, not now.
- **Exercises**: the graded exercise specs (starter/solution/tests/hints) are NOT in the
  provided files — they're referenced as living in a separate "curriculum doc" the user
  will provide later. For now, author exercises only for the 3 seed lessons.
- **Quizzes**: the modules contain free-form "predict the output" blocks, not MCQs. We
  author fresh multiple-choice `quiz.json` from lecture content (seed lessons now).
- **Tier 1–5 files**: ignored for now.
- **Content/medium mismatch to handle during content phases**: lectures assume a local
  Python install + terminal + a "Module 0" that doesn't exist in a browser-only Pyodide
  platform. Adapt that prose to the browser context when converting content (not Phase 1).

## Current status — Phase 1 COMPLETE

App boots (`npm run dev` → 200), Python is registered, and the homepage is driven entirely
by the language registry. `npm run build` produces a working static export in `out/`.
`npm run typecheck` is clean.

### What exists now

- **Scaffold**: `package.json`, `tsconfig.json` (strict, `noUncheckedIndexedAccess`),
  `next.config.mjs` (`output: "export"` + `@next/mdx` + dev COOP/COEP headers),
  `tailwind.config.ts` + `src/app/globals.css` (CSS-var theme tokens, light + dark),
  `postcss.config.mjs`, `.eslintrc.json`, `vercel.json` (prod COOP/COEP headers).
- **Language abstraction** (the keystone — components must ONLY touch these):
  - `src/lib/languages/types.ts` — the `Language` interface: `config`, `runtime`,
    `linter`, `errorExplainer`, plus all sub-types (RunOptions, SubmitResult, Diagnostic,
    ErrorExplanation, …).
  - `src/lib/languages/registry.ts` — the ONLY place languages are listed;
    `getAllLanguages()`, `getLanguage(id)`, `hasLanguage(id)`, `getLanguageIds()`.
  - `src/lib/languages/python/` — `config.ts` (done), `errorExplainer.ts` (done, full
    lookup table), `runtime.ts` + `linter.ts` (interface-conformant **Phase 2 shells** —
    methods throw a clear marker), `index.ts` (assembles + the registry imports it).
- **lib skeletons**:
  - `src/lib/content/types.ts` (full content model) + `loader.ts` (signatures; impls are
    **Phase 3 stubs** that throw a marker).
  - `src/lib/progress/index.ts` — **fully implemented** localStorage wrapper (completion,
    quiz best-score/attempts, code autosave, last-visited). All keys namespaced
    `ltcp:v1:*`; SSR-safe. This is the single place storage keys live.
  - `src/lib/theme/` — `script.ts` (no-flash init script + storage key),
    `ThemeProvider.tsx` (`useTheme`, toggle), `index.ts`. Wired into the root layout.
    Toggle UI itself is Phase 6.
- **App**: `src/app/layout.tsx` (ThemeProvider + no-flash script), `src/app/page.tsx`
  (registry-driven homepage placeholder — proves the registry drives the UI; full
  homepage is Phase 5).

### Conventions to keep

- **Never** branch on `language === "python"`. All language behavior goes through the
  `Language` interface. Adding a language = implement the interface + add to the registry.
- TS strict; PascalCase components; hooks prefixed `use`.
- Pyodide/Monaco/Ruff load **lazily**, only on pages that need them.
- All localStorage access goes through `src/lib/progress`.

## Phase 2 — COMPLETE (IDE on `/dev/ide`)

Built the full IDE and mounted it on the temp route `/dev/ide` (exported as
`out/dev/ide.html`). Typecheck + static build are green.

### What exists now (Phase 2)

- **Real Pyodide runtime** — `src/lib/languages/python/`:
  - `pyodide.worker.ts` — web worker. Loads Pyodide from jsDelivr CDN via `importScripts`,
    streams stdout/stderr (raw byte writes, so unflushed `input()` prompts show), and
    implements synchronous `input()` by blocking the worker on `Atomics.wait` over a
    SharedArrayBuffer until the main thread writes a line. Has a JSON test runner
    (`test_*` functions; uses each function's docstring as the friendly name) and parses
    Python errors into `{type, message, traceback}`.
  - `runtimeProtocol.ts` — shared constants (Pyodide version `0.26.4`, SAB layout, status
    codes) + worker message types.
  - `runtime.ts` — main-thread adapter (replaces the Phase 1 shell). Owns the worker +
    SABs, serializes operations, routes input() to `onInput`, supports cancel (interrupt
    buffer for CPU-bound loops; cancel status for input waits; worker terminate when not
    isolated). Browser APIs touched only inside methods, so still server-import-safe.
  - `linter.ts` — real Ruff adapter (`@astral-sh/ruff-wasm-web`, dynamically imported);
    maps findings to `Diagnostic[]`.
- **IDE components** — `src/components/ide/`: `CodeEditor.tsx` (Monaco via
  `@monaco-editor/react`, diagnostics→markers, themes, Ctrl/Cmd+Enter / +Shift+Enter),
  `Terminal.tsx` (xterm + fit, line-editing `readLine()` for interactive input),
  `ResizableSplit.tsx` (draggable + keyboard-accessible separator), `Ide.tsx` (orchestrator:
  Run/Submit/Stop/Reset/Hints/Solution/Shortcuts + autosave + loading states), plus
  `ErrorCallout.tsx`, `TestResults.tsx`, `ShortcutsOverlay.tsx`.
- **UI primitives** — `src/components/ui/`: `Button.tsx` (focus ring, hover/active,
  loading=disabled), `Spinner.tsx`, `Modal.tsx` (Esc + focus trap + restore focus, portal).
- **Reusable IDE API**: `<Ide languageId exercise={{starter,solution,tests,hints}} autosave? onAllTestsPassed? />`.
  It looks the language up from the registry, so callers pass only serializable props —
  ready to drop into Phase 3 exercise lessons.

### Phase 2 decisions / facts

- **COEP path verified**: jsDelivr serves `access-control-allow-origin: *` AND
  `cross-origin-resource-policy: cross-origin`, so Pyodide (and Monaco, pinned to
  `monaco-editor@0.52.2` on jsDelivr) load under our `require-corp` policy. No
  `credentialless` or self-hosting needed.
- **Test convention** (Phase 4 seed exercises must follow): `tests.py` defines `test_*()`
  functions that call the user's code and `assert`; the first docstring line is the shown
  name. Interactive/demo code in an exercise's starter/solution goes under
  `if __name__ == "__main__":` — the test runner sets `__name__` to a non-`"__main__"`
  value so that block is skipped during Submit (avoids `input()` EOF crashes).
- **NOT browser-verified**: this environment has no browser, so the interactive runtime
  (actual Pyodide run, SAB-blocked `input()`, Monaco/xterm rendering, Ruff markers) was NOT
  click-tested. What WAS verified: typecheck, static build, worker chunk emitted, route
  serves with COOP/COEP headers, and the **Python test-harness logic headlessly via the
  `pyodide` npm package in Node** (pass/fail/syntax-error/`__main__`-guard all correct).
  **The user should open `/dev/ide` in a browser to confirm the live IDE behavior.**

## Phase 3 — COMPLETE (lesson renderer + content loader + seed content)

Built the generic content loader, the MDX compile path, both lesson layouts, the inline
`<Runnable>`, the quiz, a functional course-outline page, and authored the 3 seed lessons.
`npm run typecheck` is clean; `npm run build` statically exports all routes:
`/learn/python`, and `/learn/python/01-fundamentals/{01-variables,02-greet,03-greet-input}`.

### What exists now (Phase 3)

- **Content loader** — `src/lib/content/loader.ts` (real, replaces the Phase 1 stubs):
  `getCourse`, `getModule`, `getLessonRef`, `getLecture`, `getExercise`, plus nav helpers
  `getResolvedCourse`, `listLessonParams` (feeds `generateStaticParams`), and
  `getLessonNeighbors` (prev/next across module boundaries). Pure `node:fs` + JSON, runs at
  build time only. Modules/lessons are returned sorted by `order`.
- **MDX strategy** — `src/lib/content/mdx.tsx`: `compileMdx(source)` uses **`@mdx-js/mdx`**
  (`compile` → `outputFormat: "function-body"`, then `run` with `react/jsx-runtime`) to turn
  a raw MDX string into a component at build time, inside async server components. We compile
  *strings* (loader returns `mdxSource`) rather than importing `.mdx` modules, which is why
  `@next/mdx`'s loader isn't used for lesson content. `@mdx-js/mdx` was promoted from a
  transitive to a declared dependency in `package.json`.
- **MDX components** — `src/components/lesson/mdxComponents.tsx`: hand-styled prose elements
  (no `@tailwindcss/typography` dep) + the custom `<Runnable>` and `<Callout type>` tags.
- **Lesson client components** — `src/components/lesson/`:
  - `LessonLanguageProvider.tsx` — client context so `<Runnable>` inherits the lesson's
    language id without the MDX author repeating it.
  - `Runnable.tsx` — inline mini-IDE: a lightweight `<textarea>` (NOT Monaco, to keep lecture
    pages light and avoid many editor instances) + Run/Stop/Reset, streams via
    `language.runtime.run`, friendly errors via `ErrorCallout`. `input()` falls back to
    `window.prompt`.
  - `LessonQuiz.tsx` — MC quiz from quiz.json, instant per-option feedback, records attempts
    via `recordQuizResult`, fires `onPassed` at a perfect score.
  - `LectureFooter.tsx` — owns lecture completion state (shared by quiz + the
    mark-complete button so they stay in sync), records last-visited on mount.
  - `ExercisePane.tsx` — wraps `<Ide>` with autosave + `onAllTestsPassed` → mark complete,
    records last-visited, and hides the IDE `< md` with the reading-only message.
  - `CourseOutlineView.tsx` — interactive outline (checkmarks + "continue where you left
    off" read from `src/lib/progress` after mount to avoid hydration mismatch).
- **Routes** — `src/app/learn/[language]/page.tsx` (outline) and
  `src/app/learn/[language]/[module]/[lesson]/page.tsx` (renderer, both layouts), each with
  `generateStaticParams` driven by the registry + loader.
- **Seed content** — `src/content/languages/python/`: `course.json`, module
  `01-fundamentals`, and lessons `01-variables` (lecture + inline Runnable + 2-q quiz),
  `02-greet` (exercise), `03-greet-input` (exercise, interactive `input()`).

### Phase 3 decisions / conventions

- **On-disk content layout** (the contract for all future content): lecture files live
  directly in the lesson folder (`<lessonId>/lecture.mdx`, optional `<lessonId>/quiz.json`);
  exercise files live in an `exercise/` subfolder (`<lessonId>/exercise/{prompt.mdx,
  starter.py, solution.py, tests.py, hints.json}`). The loader enforces this and verifies
  the lesson `type` in `module.json` matches what's on disk.
- **MDX authoring**: prose is plain Markdown; avoid raw `{`, `}`, `<`, `>` in prose (MDX
  reads them as JSX/expressions) — fenced/inline code is exempt. Inline runnable code uses
  `<Runnable code={`...multiline...`} />`; asides use `<Callout type="note|tip|warning">`.
- **Lint gotcha**: `@next/next/no-assign-module-variable` forbids any variable/field named
  `module`. The loader's neighbor field is `moduleManifest` for this reason — don't
  reintroduce a `module` binding.
- **Browser-verified by the user (2026-05-20)**: `/learn/python` and the 3 lessons work
  end-to-end (lecture + inline Runnable, both exercises, quiz, completion), and `/dev/ide`
  (Phase 2) still works — no issues reported. Automated checks here also pass: typecheck,
  static export of all routes, and the exported HTML containing the rendered MDX prose, the
  Runnable's seeded code, the quiz, mark-complete, the exercise prompt, and the mobile
  fallback.

## Next session: Phase 5 (polished homepage, outline, cheat sheet)

1. Polish the homepage (`src/app/page.tsx`) — hero copy, nav (Home + registry-driven
   Languages), theme toggle (Phase 6 owns the toggle UI, coordinate).
2. Polish the course-outline page / `CourseOutlineView` (a functional version exists).
3. Build the cheat sheet: route `src/app/cheatsheet/[language]/page.tsx` + content
   `src/content/languages/python/cheatsheet.mdx` (reuse `compileMdx` + `mdxComponents`). The
   IDE already links to `/cheatsheet/<lang>` (currently a dead link until this lands).
4. Consider a shared top nav/`SiteHeader`; remove the temp `/dev/ide` route when ready.

## Known warnings (benign)

- `next build` warns "headers will not work with output: export" — expected; prod headers
  come from `vercel.json`, dev headers from `next.config.mjs`. Other static hosts (e.g.
  GitHub Pages) need their own header config — to be documented in the Phase 6 README.
- `npm install` reports a few vulnerabilities in build-time transitives (eslint 8, glob).
  They don't ship in the static output. Don't `npm audit fix --force` (breaks majors).
- The three folders `agent-skills/`, `skills/`, `ui-ux-pro-max-skill/` are unrelated
  Claude Code skill repos that happen to live in this directory — gitignored, not part of
  this project. Leave them alone. (They contain useful design/Vercel guidance used while
  building the UI: `ui-ux-pro-max-skill` has a Python search CLI; `agent-skills` has Vercel
  React best-practices + deploy skills; `skills` has `frontend-design`.)
- The IDE needs the page to be **cross-origin isolated** (COOP/COEP) for interactive
  `input()`, and needs network access to jsDelivr (Pyodide + Monaco). On a host without
  isolation, code still runs but `input()` yields EOF and Stop falls back to terminating
  the worker.

## Commands

- `npm run dev` — local dev (http://localhost:3000)
- `npm run build` — static export to `out/`
- `npm run typecheck` — `tsc --noEmit`
- `npm run lint` — Next ESLint
