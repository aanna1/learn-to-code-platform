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
   errors, hints, reset, autosave, keyboard shortcuts + overlay. ← **NEXT**
3. **Lesson renderer** (both layouts) + generic content loader + quiz + inline `<Runnable>`.
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

## Next session: start Phase 2 (IDE on `/dev/ide`)

1. Add deps: `@monaco-editor/react`, `xterm` (+ `xterm-addon-fit`), Pyodide loader,
   `@astral-sh/ruff-wasm-web` (or closest working equivalent).
2. Implement `python/runtime.ts` for real: load Pyodide from CDN (idempotent), capture
   stdout/stderr to callbacks, and pause on `input()` — the hard part. The COOP/COEP
   headers (already configured in `next.config.mjs` for dev and `vercel.json` for prod)
   support a worker + SharedArrayBuffer approach; use whichever yields the cleanest
   interactive terminal. Also implement `runTests()` (run user code + tests.py, collect
   per-case results).
3. Implement `python/linter.ts` (Ruff → `Diagnostic[]` for the Monaco gutter).
4. Build IDE components under `src/components/ide/` (editor + terminal + resizable split,
   Run/Submit, hints, reset-with-confirm, friendly-error callout via `errorExplainer`,
   keyboard shortcuts + overlay) and mount them on a temporary `src/app/dev/ide/page.tsx`
   with a hardcoded exercise to validate end-to-end (incl. interactive input).

## Known warnings (benign)

- `next build` warns "headers will not work with output: export" — expected; prod headers
  come from `vercel.json`, dev headers from `next.config.mjs`. Other static hosts (e.g.
  GitHub Pages) need their own header config — to be documented in the Phase 6 README.
- `npm install` reports a few vulnerabilities in build-time transitives (eslint 8, glob).
  They don't ship in the static output. Don't `npm audit fix --force` (breaks majors).
- The three folders `agent-skills/`, `skills/`, `ui-ux-pro-max-skill/` are unrelated
  Claude Code skill repos that happen to live in this directory — gitignored, not part of
  this project. Leave them alone.

## Commands

- `npm run dev` — local dev (http://localhost:3000)
- `npm run build` — static export to `out/`
- `npm run typecheck` — `tsc --noEmit`
- `npm run lint` — Next ESLint
