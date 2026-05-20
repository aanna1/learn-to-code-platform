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
3. **Lesson renderer** (both layouts) + generic content loader + quiz + inline `<Runnable>`. ← **NEXT**
4. **Seed lessons** (the 3 from the brief) + end-to-end wire-up.
5. **Homepage + course outline + cheat sheet** (polished).
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

## Next session: start Phase 3 (lesson renderer + content loader)

1. Implement the content loader (`src/lib/content/loader.ts`, currently Phase-3 stubs):
   fs+JSON reads for course.json/module.json; load `lecture.mdx`/`prompt.mdx` + `.py` +
   quiz.json/hints.json. Decide MDX compile strategy (e.g. `next-mdx-remote` or compiling
   with `@mdx-js/mdx`) — these run at build time in server components for static export.
2. Build the lesson renderer (`src/app/learn/[language]/[module]/[lesson]/page.tsx`) with
   `generateStaticParams` from the registry + content. Two layouts: lecture (MDX + inline
   `<Runnable>` + end-of-lecture quiz + mark-complete) and exercise (prompt + `<Ide>`).
3. Build the inline `<Runnable>` MDX component (reuses `language.runtime.run`, no tests),
   the quiz component (from quiz.json, contributes to completion via `src/lib/progress`),
   and MDX custom components.
4. Wire completion + last-visited through `src/lib/progress` (already implemented).

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
