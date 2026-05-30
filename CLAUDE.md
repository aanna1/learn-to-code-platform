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
- Curriculum→platform conversion context (read before converting lessons):
  `docs/curriculum-conversion-context.md`.
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
5. **Homepage + course outline + cheat sheet** (polished). ✅ DONE
6. **Polish**: theme, mobile (hide IDE < 768px), shortcuts overlay, README, deploy docs.
   ✅ DONE. (Theme toggle landed in Phase 5; mobile IDE-hide in Phase 3; shortcuts overlay in
   Phase 2. Phase 6 added the mobile hamburger nav, the README + deploy docs, and removed the
   temp `/dev/ide` route.)

**All six phases are complete.** The app is feature-complete against the brief for the
Python build.

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
  `if __name__ == "__main__":` — the test runner imports the submission with
  `__name__ == "submission"` (non-`"__main__"`) so that block is skipped during Submit
  (avoids `input()` EOF crashes).
- **Test-harness namespace contract (fixed 2026-05-30 — was a live bug).** `handleRunTests`
  in `pyodide.worker.ts` writes the learner's code to `/home/pyodide/_submission/submission.py`,
  imports it as a real module `submission`, and runs `tests.py` **inside that module's own
  `__dict__`** (`__sub_ns__`). This makes all test styles work at once: `import submission` /
  `from submission import x` / `importlib.reload(...)`, direct calls to the submission's
  functions without importing, and monkeypatching via `globals()[name] = fake` (the test and the
  submission share one namespace). The earlier runtime execed code+tests into a bare namespace and
  created **no** `submission` module, so every exercise using `from submission import …` /
  `importlib.reload(…)` / `__file__` crashed live with `ModuleNotFoundError: submission` —
  modules 03–08 were broken; 01–02 happened to use the direct-call style and worked. The skill's
  `scripts/grade_check.py` now runs tests the **same** way, so "passes grade_check" ⟺ "passes in
  the browser" — keep the two in lock-step. Re-validated headlessly across all 8 modules (every
  solution passes, every starter fails ≥1).
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

## Phase 5 — COMPLETE (polished homepage, outline, cheat sheet, global nav)

`npm run typecheck` clean; `npm run build` exports 10 routes including the new
`/cheatsheet/python`. Browser-verified by the user after Phase 3; Phase 5 adds the chrome.

### What exists now (Phase 5)

- **Global nav** — `src/components/nav/SiteHeader.tsx` (server), mounted in the root layout
  on every page. Registry-driven: brand → `/`, one link per language → `/learn/<id>`, and a
  "Cheat sheet" link **only while exactly one language is registered** (it's per-language;
  with several, each course outline links its own — keeps the global header from hardcoding a
  language). Fixed `h-14` / `3.5rem`, `sticky top-0`.
- **Theme toggle** — `src/components/nav/ThemeToggle.tsx` (client), in the nav. Uses
  `useTheme().toggleTheme`. Renders a neutral placeholder until mounted, then sun/moon, to
  avoid a hydration mismatch (server can't read the saved theme). **This was Phase 6 work,
  pulled forward** because the nav needed it.
- **Homepage** — `src/app/page.tsx` rewritten: hero + CTA (to the first registered
  language's course + its cheat sheet), a 3-step "how it works" strip, and the
  registry-driven language-card grid. No hardcoded language.
- **Cheat sheet** — route `src/app/cheatsheet/[language]/page.tsx` (async server,
  `generateStaticParams` over the registry) + content
  `src/content/languages/python/cheatsheet.mdx` (the 8 brief sections) + loader
  `getCheatsheet(languageId)`. Reuses `compileMdx` + `mdxComponents`, wrapped in
  `LessonLanguageProvider` so any `<Runnable>` in it works.
- **Outline polish** — `CourseOutlineView` gained a per-language cheat-sheet link and a
  completion progress bar (`completedCount / totalLessons`, read client-side).

### Phase 5 decisions / facts

- **Layout interaction with the fixed header**: the global header reserves `3.5rem`. The
  full-height exercise lesson layout was changed from `md:h-screen` to
  `md:h-[calc(100vh-3.5rem)]` so the IDE fills exactly the space below the header. If the
  header height ever changes, update that calc.
- **SSR text split**: interpolated text like `Start with {name}` renders as
  `Start with <!-- -->Python` in the static HTML (a React text-boundary comment) — that's
  normal, not a bug; grep with the literal full string will "miss" it.
- **NOT browser-verified this phase** (no browser here): verified typecheck, static export of
  all 10 routes, and that exported HTML contains the homepage hero/CTA, the global header +
  theme toggle on every page, all 8 cheat-sheet sections, and the outline progress bar. The
  theme toggle's live light/dark switch and nav interactions still want a real browser pass.

## Phase 6 — COMPLETE (mobile nav, docs, cleanup)

`npm run typecheck` clean; `npm run build` exports 9 routes (the `/dev/ide` harness is
gone). This was the last planned phase — the Python build is feature-complete.

### What changed (Phase 6)

- **Mobile hamburger nav** — `src/components/nav/MobileNav.tsx` (client island). Below `md`
  the desktop links in `SiteHeader` are hidden (`hidden md:flex`) and collapse into a
  hamburger that opens a dropdown panel of the same registry-driven links. Closes on Esc,
  outside click (a `fixed inset-0` backdrop button), and after navigating. Links are passed
  in as plain `{href,label}` data so the nav bundle never imports the language modules. The
  `ThemeToggle` stays visible in the bar at all widths.
- **README** — rewritten from the Phase 1 stub into full docs: features, stack, commands,
  structure, the content-authoring contract, how to add a language, and **deploy/COOP-COEP
  docs per host** (Vercel/local done; Netlify, Cloudflare/nginx, and GitHub Pages — the
  latter can't set headers so interactive `input()` degrades to EOF; notes the
  `coi-serviceworker` shim).
- **Removed** `src/app/dev/` (the Phase 2 IDE harness route). The `<Ide>` component itself
  stays — it's used by exercise lessons. Nothing imported the deleted page.

### Phase 6 decisions / facts

- **MobileNav stacking**: the dropdown panel is `absolute right-2 top-14` and anchors to the
  sticky `<header>` (which establishes the positioning/stacking context). Panel `z-50` sits
  above the `z-40` outside-click backdrop. NOT browser-verified here — the open/close,
  Esc, and outside-click behavior want a real browser pass.
- **`.next` cache + removed routes**: after deleting a route, `npm run typecheck` failed on a
  stale `.next/types/app/dev/ide/page.ts`. Fix is `rm -rf .next` then rebuild (build
  regenerates the route types). Worth remembering whenever a route is deleted/renamed.
- **NOT browser-verified this phase** (no browser here): verified typecheck, the 9-route
  static export, the hamburger button + `hidden md:flex` desktop links in exported HTML, and
  that `/dev/ide` is no longer exported.

## Current focus: converting the real curriculum (in progress)

All six build phases are done and the Python build is feature-complete. The live work now is
**replacing the 3 seed lessons with the real curriculum** (`curriculum/` Modules 01–14). The
**user is authoring** the converted lessons; this session's role is gap analysis + review.

Full handoff context: `docs/curriculum-conversion-context.md`. The gap, in brief — the
curriculum docs are **lectures only** (no graded exercises; the referenced "curriculum doc"
of exercises does not exist in the repo), **one mega-doc per module** (the platform wants a
trimmed lecture lesson + several exercise lessons), lead with a duplicate `# Module N` H1
(the renderer already prints the lesson title), use a **predict-then-reveal `<details>`**
pattern + raw Markdown that isn't valid MDX (bare `{ } < >` break the build), and assume a
**laptop environment** — local install, terminal, `python file.py`, a nonexistent "Module 0",
and especially Module 10 (`pip`/`venv`/third-party `requests`), Module 11 (real-file
`open()` ×31), Module 14 (terminal `pytest`) — none of which exist in the browser runtime.
Conversion = re-map into the lesson-bundle tree, translate interactivity to
`<Runnable>`/`quiz.json`, author the missing exercises/quizzes, re-root env assumptions to
"press Run." Review checklist when lessons come back: valid MDX, the `test_*` grading
convention, quiz schema, and browser-context fit.

Other possible follow-ups (not active): a second language to exercise the abstraction; a live
browser QA pass of the interactive runtime + nav.

## Known warnings (benign)

- `next build` warns "headers will not work with output: export" — expected; prod headers
  come from `vercel.json`, dev headers from `next.config.mjs`. Other static hosts (e.g.
  GitHub Pages) need their own header config — documented in the README's Deployment section.
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
