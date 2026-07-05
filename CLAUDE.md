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

Other possible follow-ups (not active): a live browser QA pass of the interactive runtime +
nav. (The "second language to exercise the abstraction" follow-up is now an active workstream —
see **C language build** below.)

## C language build — second language (in progress)

Adding **C** as the platform's second language. This both proves the language abstraction and
ships a real new course. **Decision: C is browser-first** — every teaching module and checkpoint
project runs in the in-browser `<Ide>` (compile + run C client-side, same model as Pyodide),
**except** two optional, post-course **Advanced Tracks (a C compiler targeting x86-64; a small
OS)** which are **local by design** (real toolchain/editor/gdb) as a "graduate to a real
environment" capstone. Rationale: keep beginners install-free where it matters; reserve local
setup for learners who've finished the course. Status: planning + runtime spike done; no C
content or runtime built yet; **C is intentionally NOT in the registry** (see skeleton below).

### Source-of-truth docs (read these first when resuming)

- `docs/c-curriculum-map.md` — the curriculum: 11 core browser modules + 2 local Advanced
  Tracks, checkpoint projects, browser-first decision. **Open TODO:** its "sanitizer-backed
  leak grading" wording over-promises — soften per the C0 spike (UBSan only; no heap/leak).
- `docs/c-in-browser-runtime-options.md` — runtime engine research. Recommends **clang+lld→WASM**
  (Option A, real diagnostics; ~tens-of-MB cold-load, service-worker cached) over TinyCC→WASM
  (Option B, tiny but no sanitizers); `v86` full-Linux (Option D) is the only path to real
  gdb/valgrind/ASan.
- `docs/c-integration-plan.md` — the engineering plan: phases **C0→C1→C2→C3→C4**, how C slots
  into the registry/loader/`<Runnable>` with zero component changes, the test-harness contract,
  deploy/COOP-COEP/CDN notes.
- `docs/c0-spike-report.md` — the C0 findings (below).

### Module list (final) — 11 core (browser) + 2 advanced (local)

01 The C Environment · 02 Types, Variables & Operators · 03 Control Flow · 04 Functions
*(Checkpoint A: Calculator)* · 05 Arrays & Strings *(B: Tic-Tac-Toe)* · 06 Pointers ·
07 Dynamic Memory · 08 Structs *(C: Linked List)* · 09 File I/O *(D: Grade Book)* ·
10 Standard Library/Scope/Preprocessor/Multi-file *(E: Word Frequency Counter)* ·
11 Debugging & Memory Tools *(Capstone: Toy Allocator)* · 12 Advanced Track: C Compiler
(x86-64, LOCAL) · 13 Advanced Track: Small OS (LOCAL). Order chosen so each checkpoint lands
right after the module that completes its prerequisites.

### Authoring tooling — the `c-curriculum-builder` skill

A standalone skill at `c-curriculum-builder/` (also packaged as `c-curriculum-builder.skill`)
expands ONE master file (`curriculum/c-curriculum-master.md`) into per-module lecture docs
(`curriculum/C Curriculum Module NN.md`), one at a time with a checkpoint each, in the course
voice. **Pipeline:** master → (this skill) → module docs → (a C-adapted `curriculum-converter`)
→ platform bundles. It ships a fill-in master **skeleton** (`assets/c-curriculum-master.SKELETON.md`,
all 13 modules pre-stubbed), a per-module **template**, a **voice guide** distilled from two
reference course transcripts (warm, second-person, analogy-first, "press Run" framing), and a
`reference/master-format.md` schema. The two transcripts confirmed the topic order/tone and that
`argc`/`argv`, macros, linked lists, and function pointers are stretch-beyond-typical-intro.

### Code skeleton — `src/lib/languages/c/` (Phase-C1 stubs, typecheck-clean)

Mirrors `python/`. **Real:** `config.ts` (id `c`, Monaco `c`, `.c`), `errorExplainer.ts` (friendly
text for a fixed set of C `RuntimeError.type`s — CompileError, SegmentationFault, StackOverflow,
FloatingPointError, AssertionFailed, UndefinedBehavior, OutOfMemory, Timeout, NonZeroExit),
`runtimeProtocol.ts` (reuses the **exact Python SAB stdin layout** so Terminal/Ide plumbing
carries over; pins are `TBD` until C0 engine pick). **Shells:** `runtime.ts` (interface-conformant,
methods throw a clear marker, server-import-safe), `linter.ts` (returns `[]` gracefully),
`c.worker.ts` (documents the compile/run/test pipeline + test-harness contract, stubbed).
`index.ts` assembles the `Language` but is **deliberately not registered**. To go live (once the
runtime works): add `import { c } from "@/lib/languages/c"` and `c` to the `LANGUAGES` array in
`src/lib/languages/registry.ts` — that one line lights up homepage/nav/outline/cheat-sheet/
`<Runnable>` with no other changes. Recommend first proving it on a temp `/dev/ide-c` route, the
way Python's IDE was proven on `/dev/ide`.

### C0 spike — DONE (validated headlessly; see `docs/c0-spike-report.md`)

Ran in the Linux sandbox with real **Clang 21 + wasi-libc** (via the `ziglang` pip wheel, no
root) compiling to `wasm32-wasi`, run under **Node WASI**. Engine-independent mechanics all
work: **compile→run→stream stdout→exit code ✅**, **`scanf`/stdin ✅** (validates the SAB read
path), **hidden-test grading ✅** (compile submission + `tests.c`, parse `__T__|name|PASS/FAIL`
lines → `TestCaseResult[]`). Numbers: warm compile ~20 ms, instantiate+run ~1–2 ms, per-run
artifact ~9 KB–310 KB gzipped, sysroot ~3 MB. **Sanitizer reach (key result):** UBSan **works**
and catches signed overflow + fixed-size local-array OOB; **non-trap UBSan prints a readable
message** ("signed integer overflow: …") → feed it to `errorExplainer`. **ASan is unavailable on
`wasm32-wasi`** (link error on `__asan_*`) and a **heap OOB write was NOT caught**. Conclusions:
**keep Clang** (TinyCC would lose UBSan too); **grading = `-Wall -Wextra` markers + hidden tests +
non-trap UBSan**, with NO heap/leak/UAF detection on the core path (only `v86` gives that);
**test-harness = separate-compile model** (harness declares the submission's prototypes + owns
`main()`) — mirror it in a C `scripts/grade_check` to keep browser ⟺ grade_check in lock-step.

### C2 — DONE (test-harness contract + headless C grader; validated in sandbox)

Built and **headlessly verified** the C grading pipeline ahead of C1 (the grader is fully
verifiable here; the runtime needs a browser), so content authoring is unblocked and C1 has a
locked contract to mirror.

- **Contract doc:** `docs/c-test-harness-contract.md` — the canonical, locked spec.
  Separate-compile model: `tests.c` owns `main()` + declares the submission's prototypes + prints
  one `__T__|<name>|PASS` / `__T__|<name>|FAIL|<msg>` line per case; the submission is compiled
  with **`-Dmain=__student_main__`** (applied to the **submission TU only**) to neutralize any
  student `main()` — the C mirror of Python's "import as module, skip the `__main__` block." (A
  global `-Dmain` renames the harness's `main` too → duplicate-symbol link error; that's why
  compilation is separate, not one `cc a.c b.c`.)
- **Flags (worker ⟺ grader must match):** `-target wasm32-wasi -std=c11 -Wall -Wextra -O0
  -fsanitize=undefined -fno-sanitize-trap=undefined`. The `-fno-sanitize-trap` makes UBSan print a
  readable line (`signed integer overflow: …`) to stderr before aborting → fed to `errorExplainer`
  as `UndefinedBehavior`.
- **Grader:** `scripts/c/grade_check.py` (+ `scripts/c/run_wasi.mjs` Node WASI runner). C analogue
  of the Python skill's `grade_check.py`: compiles {submission, tests} via **`zig cc`** (a Clang
  driver, `pip install --break-system-packages ziglang`) → `wasm32-wasi` → runs under Node WASI →
  parses `__T__` lines. Solution must pass all; starter must fail ≥1. Verdict handles
  compile-failure, trap/non-zero-exit (surfaces the UBSan/diagnostic line), and a 10 s timeout
  (infinite loops). Worked example + fixtures in `scripts/c/example/`.
- **Verified in sandbox:** example solution 4/4 PASS + starter 1/4 → `RESULT: OK` (discriminates);
  non-compiling → fail w/ first `error:` line; signed-overflow → fail w/ readable UB message;
  infinite loop → timeout fail. Node v22 WASI; zig 0.16 / Clang.
- **Note:** the grader is the C0-spike proxy (zig cc = Clang). When C1 picks the actual browser
  bundle (clang-wasm vs tinycc), keep `c.worker.ts` compiling/parsing the **same** way; tinycc has
  no UBSan, so choosing it drops the non-trap UB message path.

### Cold-load measurement — DONE (`docs/c1-coldload-measurement.md`)

Static (GitHub tree API) AND live (Chrome DevTools Network, cache disabled) both measured. **Live
result: clang-wasm (`binji/wasm-clang`) cold-loads 19.4 MB over the wire** (32 requests) — clang
10.7 MB + lld 6.8 MB + sysroot.tar 1.87 MB transferred (GitHub Pages gzips the wasm to ~34% of the
~60 MB on-disk). One-time + service-worker cached. Hello-world compiled→linked→ran cleanly →
compilation is not the bottleneck. (DevTools "121 MB resources" is a double-count artifact — each
artifact fetched twice via `worker.js` and `service_worker.js`; ignore it.)

### C1 — IN PROGRESS (engine LOCKED = Clang; runtime implemented, typecheck-clean, browser pass owed)

User gave the formal go to **Clang** (over TinyCC). Implemented the real C runtime against the
actual toolchain API, mounted on a temp `/dev/ide-c` harness. Full detail: `docs/c1-runtime-notes.md`.

- **`runtimeProtocol.ts`** — engine pins (`C_ENGINE="clang-wasm"`, `C_CLANG_VERSION="8.0.1"`,
  `C_TOOLCHAIN_CDN_BASE` = jsDelivr gh `binji/wasm-clang@master`), the `clang -cc1 -x c` C2 flag
  set (`C_CC1_BASE_ARGS`), UBSan flags + `C_SUPPORTS_UBSAN` gate, `C_NEUTRALIZE_MAIN`
  (`-Dmain=__student_main__`), reused SAB stdin layout.
- **`runtime.ts`** — full main-thread adapter (port of Python's): owns worker + input SAB,
  idempotent `load()` w/ progress, serialized `run()`/`runTests()`. Cancel = **terminate the
  worker** (WASM has no cooperative interrupt — the one deliberate divergence from Python).
- **`c.worker.ts`** — loads binji's `API` (fetch+eval `shared.js`, capture the global), then
  `clang -cc1 -x c` → `wasm-ld` → run, streaming stdout + buffering diagnostics, mapping faults to
  `errorExplainer` types. `runTests` = the C2 separate-compile harness, parsing `__T__` lines the
  SAME way as the verified `scripts/c/grade_check.py`.
- **`/dev/ide-c`** — temp harness; mounts `<Ide>` against C via a new optional `language` override
  prop (keeps C out of the public registry until verified). Seed exercise = `sum_to`.
- **KEY FINDING (reading binji's `shared.js`):** the engine isn't just "Clang", it's "which Clang
  bundle". binji's stock bundle is a C++ demo (clang 8) that **lacks compiler-rt UBSan** (so
  `-fsanitize=undefined` won't link → `C_SUPPORTS_UBSAN=false` for now), reads **stdin from a
  preset string** (no interactive blocking yet — v1 feeds EOF), and leaves `clock_time_get`
  unimplemented. It's a great cold-load proxy + plumbing prover but **not** a drop-in for the C2
  contract. **PROD bundle = a purpose-built clang+lld + wasi-libc + compiler-rt sysroot + SAB
  stdin shim** (an offline LLVM-to-WASM build) — the real remaining C1 work. When ready, only the
  protocol constants + CDN base change.
- **Verified:** `npm run typecheck` clean. **BROWSER-VERIFIED (2026-06-07, user-driven on
  `/dev/ide-c`):** the dev bundle compiles our exact `clang -cc1 -x c` C2 flags, surfaces a real
  clang diagnostic (`warning: unused parameter 'n'`), links via `wasm-ld`, runs, and streams
  stdout (`sum_to(10) = 0` for the starter). So binji's clang-8 bundle DOES handle `-x c` + our
  flags + link + run — the key open question, answered yes (UBSan still gated off).
  - **CDN fix (found in that pass):** jsDelivr **403s the ~31 MB `clang`** (exceeds its ~20 MB
    file limit; memfs/sysroot load fine — the tell). binji's Pages host serves it but sets no
    CORP → blocked under our COEP. Fix: **self-host same-origin** from `public/c-toolchain/`
    (exempt from COEP/CORP + no size cap). `C_TOOLCHAIN_CDN_BASE` is now
    `${NEXT_PUBLIC_BASE_PATH}/c-toolchain/`; the folder is gitignored (~60 MB), populated from
    binji's Pages host (one-liner in `runtimeProtocol.ts`). Prod = the custom bundle, still
    self-hosted, + service-worker cache (C4).
  - Also filter binji's `> clang …`/`> wasm-ld …` command echoes out of the terminal (worker
    `extractDiagnostics`) so learners see only real diagnostics + program output.
- **STILL being confirmed in-browser:** Submit/grading path (starter ≥1 fail, solution 4/4) and
  the friendly-CompileError-on-syntax-error case. **NOT verified:** `npm run build` (Monaco-heavy
  compile exceeds the build sandbox's time budget — run locally). Added `distDir` override
  (`NEXT_DISTDIR`) to `next.config.mjs` for building when `.next` is locked.

### What's next (resume here)

- **Browser-verify `/dev/ide-c`** (the owed pass): load under COOP/COEP, Run + Submit the seed,
  confirm friendly compile errors. **Decide early** whether binji's bundle is usable at all for
  real lessons or whether the **production clang bundle** (UBSan + interactive stdin + newer clang)
  must be built first — that build is the gating item before C3.
- Then **C3** (C-adapt `curriculum-converter`, author Module 1 as the fixture, create
  `src/content/languages/c/`, register C) → **C4** (cheat sheet, render Advanced Tracks as
  lecture-only LOCAL guides, CDN/COOP-COEP + service-worker cache, remove `/dev/ide-c`;
  `rm -rf .next` after deleting the route).
- **Housekeeping TODO:** soften the sanitizer-grading wording in `docs/c-curriculum-map.md` to
  match the C0 finding (UBSan only).

## SQL language build — third language (planning stage)

Adding **SQL** as the platform's third language. Source material: `Language Information/4_SQL/`
(a MySQL-dialect tutorial transcript). **Requirement (locked 2026-07-02):** the course is
**security-focused**, scoped so a learner who finishes it can pass Purdue's **CNIT 27200
(Database Fundamentals)** test-out exam (2 hr, handwritten/hand-graded, 70% to pass, one
attempt, no study guide provided). This is a real, verified Purdue policy, not a stretch goal —
see the sources in `docs/sql-curriculum-map.md`.

- **Curriculum plan:** `docs/sql-curriculum-map.md` — 12 modules + capstone, tagged `[27200]`
  (test-out-required) vs. `[SEC]` (security throughline beyond 27200: SQL injection/parameterized
  queries, GRANT/REVOKE/least privilege, auditing). Includes a topic-by-topic transcript-coverage
  table — normalization, the identifying/non-identifying FK distinction, transactions
  (COMMIT/ROLLBACK), and the entire security track have **no source material in the transcript**
  and need fresh authoring, the same kind of gap the Python build hit with exercises and the C
  build hit with the master curriculum doc.
- **Engineering plan:** `docs/sql-integration-plan.md` (engine = `sql.js`/SQLite-WASM, the new
  results-grid `outputMode` needed in `<Ide>`, the `schema.sql`/`tests.json` exercise contract,
  phases S0→S4) and `docs/language-expansion-plan.md` §4 (SQL's entry in the 9-language plan).
  Both docs' curriculum-outline sections now point at `sql-curriculum-map.md` instead of
  duplicating an outline — **do not edit a curriculum list into either of those two docs again**,
  they're engineering-only now.
- **Status:** content authoring started; runtime code not written, SQL not registered. Content
  authoring (the module-list gaps above) can proceed in parallel with the S0 runtime spike once
  that's kicked off — they only need to agree on the exercise-bundle shape.
- **Module 01 drafted** — `curriculum/SQL Curriculum Module 01.md` ("Databases, RDBMS & Why
  Attackers Care"), written directly against the module-doc template/voice guide in
  `c-curriculum-builder/` (no SQL-specific authoring skill exists yet — this was hand-authored
  as the first module, mirroring that template's structure: hook → prerequisites → objectives →
  concepts → predict/try-it → recap → quiz seeds → up-next). Content is transcript-sourced
  (databases, DBMS, CRUD, relational vs. non-relational, RDBMS/SQL definitions all pulled from
  `SQL Tutorial Full Course.txt` lines ~1–540, including its own Amazon-vs-shopping-list
  security aside) plus fresh material for the CIA-triad framing and the "two goals" (27200 +
  security) framing that has no transcript source. Includes the Oracle-vs-SQLite dialect-note
  convention and a first "press Run → see a results grid, not a terminal" preview (no SQL
  syntax taught yet — that starts Module 05/06) to set expectations for the results-grid
  `outputMode` once it's built. **Not yet reviewed against a real syllabus/exam** — same
  caveat as the module list itself.
- **Module 02 drafted** — `curriculum/SQL Curriculum Module 02.md` ("The Relational Model &
  Keys"): columns vs. rows, primary keys (the "two Jacks" disambiguation example), surrogate
  vs. natural keys, foreign keys (the employee/branch example, straight from the transcript's
  own Office-characters walkthrough at lines ~682-960), a self-referencing foreign key
  (`supervisor_id`), and — fresh content, no transcript source — why real schemas split into
  several small tables instead of one (the informal seed for Module 04's normalization). Same
  hand-authored process as Module 01; not yet reviewed against a syllabus.
- **Module 05 drafted (out of order, at user's request)** —
  `curriculum/SQL Curriculum Module 05.md` ("Defining the Schema (DDL)"): data types (`INT`,
  `DECIMAL(M,N)`, `VARCHAR(n)`, `DATE`/`TIMESTAMP`, `BLOB`), `CREATE TABLE`, constraints
  (`NOT NULL`, `UNIQUE`, `DEFAULT`, `PRIMARY KEY`, `CHECK`), `ALTER TABLE`/`DROP TABLE`. Mostly
  transcript-sourced (`SQL Tutorial Full Course.txt` lines ~2076–2950 — CREATE TABLE, data
  types, NOT NULL/UNIQUE/DEFAULT, AUTO_INCREMENT, ALTER/DROP). Two pieces are fresh, no
  transcript source: `FOREIGN KEY ... REFERENCES` constraint syntax (the transcript only ever
  covered foreign keys conceptually, never the DDL) and the MySQL/SQLite/Oracle
  auto-increment-syntax dialect table — flagged in-module as the single biggest syntax gap
  between this course's IDE and the exam's environment. **Modules 03 (ER modeling) and 04
  (normalization) are still unwritten** — Module 05 references them by number for readers who
  jump straight here, same as it will read fine as a standalone DDL reference.
- **What's next:** get the module list in `sql-curriculum-map.md` (and now Modules 01-02 and 05's content)
  reviewed/sanity-checked (Purdue provides no official study guide, so it leans on a catalog
  description + Course Hero lecture-slide titles + general DB-fundamentals convention — flagged
  in that doc), decide the exercise format for the ER-modeling/normalization modules (they
  don't fit the query-in/result-set-out grading model), then either keep hand-authoring modules
  02+ the same way or build a proper `sql-curriculum-builder` skill (mirrors
  `c-curriculum-builder`) once the pattern is proven out over a few more modules.

### S3 — Module 01 converted to a live platform bundle + SQL registered (DONE this session)

Rather than adapt `curriculum-converter` for SQL, Module 01 was authored directly into the
platform tree (converter changes were heavier than a drop-in for a single module). What shipped
under `src/content/languages/sql/`: `course.json`, module `01-databases-and-security`
(`module.json`), the lecture (`lecture/lecture.mdx` + `quiz.json`, 3 MCQs from the doc's quiz
seeds), a `cheatsheet.mdx`, and **two graded query-contract exercises** — `ex-see-the-table`
(`SELECT *`) and `ex-pick-columns` (`SELECT name, major`). Module 01 teaches no syntax (that
starts Module 05/06), so both exercises are deliberately gentle, heavily-hinted "press Run /
one-line change" previews that mirror the lecture's own `SELECT * FROM students` demo and carry
the `[SEC]` throughline (Read = confidentiality; least-data = don't `SELECT *`).

Key engineering decisions locked in:

- **Loader now reads the SQL exercise bundle** (`src/lib/content/loader.ts`, `readSqlExercise`),
  detected by the presence of `starter.sql` (branches on files, never on language id). On-disk
  files are the S2 grader's contract: separate `schema.sql`, **query-only** `starter.sql`/
  `solution.sql`, and `tests.json` as a **bare array** of cases. The loader **prepends
  `schema.sql` to the editor code** and builds the worker payload as `{ cases }` with **no
  schema** — because the S1 worker's `run()` path does NOT seed `schema.sql` separately, so the
  fixture has to reach the DB via the editor for **Run** to work. Schema lives in exactly one
  place per path (editor code, not the payload) so grading never double-seeds ("table already
  exists").
- **Lock-step verified headlessly.** For SELECT-only exercises the two execution models converge:
  `scripts/sql/grade_check.mjs` (seeds `schema.sql` separately, runs the query-only file) and the
  browser path (loader prepends schema, worker execs schema+query and compares the *last* result
  set) return the **same** verdict. Confirmed: `grade_check` → `RESULT: OK` for both exercises
  (solution passes all, starter fails ≥1), and a loader+worker simulation agrees. `npm run
  typecheck` clean; all four SQL `.mdx` files compile under the route's `@mdx-js/mdx` pipeline.
- **SQL is now REGISTERED** — `registry.ts` `LANGUAGES = [python, sql]`. Homepage card, nav,
  course outline, `/cheatsheet/sql` (why the cheat sheet was needed now — the route pre-renders
  per registered language), and inline `<Runnable>` all light up. `/dev/ide-sql` still exists.

Caveats / owed follow-ups: (1) **No live browser pass yet** — the sql.js runtime + results grid
have never been click-tested in a browser (the standing S1 debt). Open `/dev/ide-sql` and a real
Module 01 exercise to confirm Run shows the grid and Submit grades. (2) **`<Runnable>` can't
render grids** — it only shows streamed stdout, which SQL never emits, so the lecture's "Try it"
is a *static* fenced preview, not a live `<Runnable>`. Wiring `<Runnable>` to the grid is a real
S3/S4 task if inline live SQL in lectures is wanted. (3) `docs/sql-test-harness-contract.md` (the
canonical spec the grader header cites) still doesn't exist — worth writing to pin the bare-array
tests.json + prepend-schema decision above. (4) `npm run build` not run here (Monaco-heavy;
exceeds the sandbox budget) — run locally.

### S3 (cont.) — Module 02 converted + flat staging folders backfilled (DONE this session)

**Module 02 ("The Relational Model & Keys") is now a live platform bundle.** Same hand-authored
approach as Module 01 (no `curriculum-converter` adaptation — heavier than a drop-in per module).
Source was the existing `curriculum/SQL Curriculum Module 02.md` (content used verbatim where the
doc had it; exercises authored fresh, since the SQL curriculum docs are lectures-only — same gap
Python/C hit). What shipped under `src/content/languages/sql/modules/02-relational-model-and-keys/`:
`module.json`, the lecture (`lecture/lecture.mdx` + `quiz.json`, 3 MCQs from the doc's quiz seeds
expanded to 4 options each), and **two graded query-contract exercises** — `ex-name-the-primary-key`
(add the PK column so the lecture's "two Jacks" rows become distinguishable) and
`ex-follow-the-foreign-key` (pull the `branch_id` FK onto the grid, employee→branch). Both stay
inside the SELECT-only syntax taught so far (DDL/WHERE are Modules 05/06), so they're the same
gentle, heavily-hinted previews as Module 01. `course.json` gains the Module 02 entry; SQL was
already registered, so no `registry.ts` change was needed. Verified: `grade_check.mjs` →
`RESULT: OK` for both (solution passes, starter fails ≥1), loader browser-path converges with the
grader, all `.mdx` compile, all JSON valid, `npm run typecheck` clean. Same standing caveat: **no
live browser pass** of the sql.js runtime/results grid yet, and `npm run build` not run here.

**Flat staging folders now exist for SQL, matching the Python layout.** Previously the SQL
conversion only emitted the nested `src/content` live tree and skipped the flat staging mirror that
`curriculum-converter` produces for Python (`curriculum/Python Module N/`). Backfilled both:
`curriculum/SQL Module 1/` and `curriculum/SQL Module 2/`. **Convention** (mirror of Python's):
flat files named `<lessonOrder>-<slug>.<ext>` with the `ex-` prefix stripped — lecture =
`1-lecture.mdx` + `1-lecture.quiz.json`; each exercise = `N-<slug>.{prompt.mdx,schema.sql,
starter.sql,solution.sql,tests.json,hints.json}` (Python uses `.py` where SQL uses `.sql`, and SQL
adds `.schema.sql`). The staging `module.json` carries a **top-level `"order"`** field that the
live-tree `module.json` omits — otherwise identical. These folders are a human-readable staging
mirror, NOT read by the app (the loader only reads `src/content`); keep them in sync by hand when a
module changes, or regenerate from the live tree.

**Curriculum-doc status correction.** The earlier "Modules 03/04 still unwritten" notes are stale:
`curriculum/` now contains **SQL Curriculum Module 01–12 + Capstone** as authored markdown lecture
docs. So the full SQL curriculum is mapped out on disk. **What's *converted to platform bundles* is
now Modules 01–06 + Checkpoint A** (see the S3 subsections below for 03, 04, Checkpoint A, 05, and 06).
Next conversion target: Module 07 (aggregates: `COUNT`/`SUM`/`AVG`, `GROUP BY`, `HAVING`).

### S3 (cont.) — Modules 03 + 04 converted, and the Track-2 structured renderer built (DONE this session)

**Modules 03 (ER modeling) and 04 (normalization) are now live bundles**, same hand-authored
approach as 01–02. Because both teach *no SQL syntax yet* (DDL is Module 05), each ships a lecture +
4-question quiz + **two gentle single-table `SELECT`-preview exercises** whose seed data embodies the
concept: 03 = `ex-see-the-associative-table` (query the junction table that resolves an N:M) +
`ex-read-the-composite-key`; 04 = `ex-see-the-redundancy` (denormalized table, repetition visible) +
`ex-one-fact-one-place` (normalized table, fact stored once). `course.json` updated; staging mirrors
at `curriculum/SQL Module 3|4/`. All four `grade_check.mjs` → `RESULT: OK`.

**Track-2 "structured" (modeling) exercises now exist end-to-end** — the previously-unbuilt renderer
from `docs/sql-integration-plan.md` §"Modeling & normalization exercises". This is the format for the
non-query answers (FD lists, normal-form judgments, ERD structure) that the SELECT-preview stopgap
can't really grade. What shipped:

- **Pure grader** `src/lib/structured/{types.ts,grade.ts}` — canonical-form comparators for all six
  field types: `single-select`, `multi-select`, `token-set` (with `grammar:"fd"` — sorts LHS, splits
  composite RHS into atoms), `matching`, `partition` (groups compared as item-sets, labels ignored
  unless `matchLabels`), `erd-spec` (entities+attrs+PKs and relationships with **unordered endpoints**
  + normalized cardinality `1:1`/`1:n`/`n:n` + identifying flag). `gradeStructured()` returns the
  shared `SubmitResult`, so each field is one `TestCaseResult`.
- **Renderer** `src/components/lesson/StructuredExercise.tsx` (client) — draft box (ungraded,
  autosaved), an input per field type (incl. a structured, dependency-free ERD editor — no canvas, no
  Mermaid), Submit → `gradeStructured` → the existing `<TestResults>`, progressive hints,
  mark-complete on all-pass. No engine/worker/network — grading is synchronous pure JS.
- **Wiring** — `LessonType` gains `"modeling"`; `ModelingContent` + `getModeling()` in the loader
  (reads `question.json`/`answer.json`/`hints.json` from the same `exercise/` folder); the lesson
  route branches on `type==="modeling"` (never on language id) and mounts `<StructuredExercise>` in a
  single-column, mobile-OK layout. Additive — Python/C/SQL query exercises untouched.
- **Headless grader** `scripts/sql/grade_check_structured.mjs` — **verbatim port** of `grade.ts`
  (same hand-kept-mirror discipline as the query grader vs. `sql.worker.ts`). Reads
  `question.json`+`answer.json`(+`wrong.json`); discriminator = canonical all-pass, wrong ≥1-fail.
- **Contract** locked in `docs/sql-test-harness-contract.md` §7 (updated to match the built code:
  comparator options live on the field in `question.json`, `answer.json` is pure values, `wrong.json`
  is the discriminator).
- **Two fixture modeling lessons authored** (order 4 in each module): Module 03
  `model-identifying-relationships` (single-select cardinality + matching identifying/non-identifying
  + erd-spec resolving the N:M) and Module 04 `normalize-the-orders-table` (single-select which-NF +
  multi-select partial-deps + token-set FDs + partition into 3NF tables). Together they exercise all
  six field types.
- **Verified (2026-07-03, headless):** both fixtures `grade_check_structured` → `RESULT: OK`;
  **true lock-step confirmed** by emitting `grade.ts` via `tsc` and running the *actual TS code path*
  over both fixtures — identical per-field verdicts to the `.mjs` (04: `1111`/`0000`, 03: `111`/`000`).
  `npm run typecheck` clean; both new `prompt.mdx` compile; all JSON valid.
- **NOT browser-verified** (no browser here): the `<StructuredExercise>` UI (field inputs, ERD editor,
  Submit/hints/mark-complete) has never been click-tested. Open `/learn/sql/03…/model-identifying-relationships`
  and the Module 04 one in a browser. `npm run build` not run here (Monaco-heavy; run locally).
- **Follow-ups:** (1) ~~no flat staging mirror for modeling lessons~~ — the modeling-staging
  convention is now defined (see Checkpoint A below): flat files `N-<slug>.{prompt.mdx,question.json,
  answer.json,wrong.json,hints.json}`. The two Module 03/04 modeling fixtures still need their staging
  backfilled to match (Checkpoint A has it). (2) ~~Checkpoint A can now be built~~ — DONE (below).
  (3) An optional read-only Mermaid render of `erd-spec` answers can be layered on without touching
  grading.

### S3 (cont.) — Checkpoint A (Design & Normalize) built (DONE this session)

The first checkpoint, a **two-part lesson** exercising Modules 02–05 on one messy dataset (a
registrar's denormalized `enrollments` spreadsheet → student/department/course/enrollment 3NF).
Lives in its own module `checkpoint-a-design-and-normalize`. **Decision (user, 2026-07-03):**
Part 2 stays **pure DDL** and the checkpoint is **sequenced AFTER Module 05 (DDL)** so DDL is a real
prerequisite — `course.json` gives it **`order: 6`, leaving `order: 5` free for the not-yet-converted
Module 05**. (The curriculum-map lists Checkpoint A before Module 05; this build intentionally
diverges so Part 2 doesn't front-run DDL syntax.)

- **Part 1 `design-the-erd`** (`type: "modeling"`, Track-2): a `token-set` (`grammar:"fd"`) listing the
  sheet's functional dependencies + an `erd-spec` modeling the four entities (PK-only attributes; FKs
  represented via relationships) and three relationships (department→course non-identifying;
  student→enrollment and course→enrollment identifying; the student–course N:M resolved by the
  `enrollment` associative entity).
- **Part 2 `build-the-3nf-schema`** (`type: "exercise"`, Track-1 **DDL**, probe-graded): learner writes
  the `CREATE TABLE`s; `tests.json` cases probe **structure, not data** via
  `sqlite_master`/`pragma_table_info`/`pragma_foreign_key_list` — the first DDL/probe exercise in the
  SQL content. Verified these TVFs work in sql.js 1.14.1 before authoring. Starter builds
  student+department, leaves course (no FK) and enrollment (single-col PK, no FKs) broken →
  discriminates. `schema.sql` is intentionally comment-only (nothing pre-seeded; building the tables
  IS the exercise).
- **Verified headless (2026-07-03):** Part 1 `grade_check_structured` → canonical all-pass / wrong
  ≥1-fail → `RESULT: OK`; Part 2 `grade_check.mjs` → solution 4/4, starter passes only the
  "tables exist" case and fails the other 3 → `RESULT: OK`. `npm run typecheck` clean (no new TS —
  reuses the Track-2 renderer + query loader); both `prompt.mdx` compile; all JSON valid. Flat staging
  mirror at `curriculum/SQL Checkpoint A/`.
- **NOT browser-verified / owed:** the live `<StructuredExercise>` UI and the results-grid Submit path
  (standing S1 debt). `npm run build` not run here. When **Module 05 (DDL)** is converted, give it
  `order: 5` so it sorts immediately before this checkpoint.

### S3 (cont.) — Module 05 (Defining the Schema / DDL) converted (DONE this session)

**Module 05 ("Defining the Schema (DDL)") is now a live platform bundle**, same hand-authored approach
as Modules 01–04 (no `curriculum-converter` adaptation). Source was the existing
`curriculum/SQL Curriculum Module 05.md` (content used ~verbatim where the doc had it; exercises
authored fresh, as always — the SQL curriculum docs are lectures-only). What shipped under
`src/content/languages/sql/modules/05-defining-the-schema-ddl/`: `module.json`, the lecture
(`lecture/lecture.mdx` + `quiz.json`, 4 MCQs from the doc's 3 quiz seeds + one DROP TABLE question,
all expanded to 4 options), and **three graded DDL exercises**. `course.json` gains Module 05 at
**`order: 5`** — sorting immediately before Checkpoint A (`order: 6`), exactly as that checkpoint's
note asked. SQL was already registered, so no `registry.ts` change.

- **This is the first module where learners actually WRITE DDL** (Modules 01–04 were gentle
  `SELECT`-preview exercises because no syntax was taught yet). The three exercises are Track-1
  query-contract bundles, **probe-graded on structure** (the same model as Checkpoint A Part 2 —
  `sqlite_master` / `pragma_table_info` / `pragma_foreign_key_list`, not data):
  - `ex-create-the-student-table` (order 2): write `CREATE TABLE` with `PRIMARY KEY`, `NOT NULL`,
    `DEFAULT`. Probes: table exists; `pk > 0` column; `"notnull" = 1` column; `dflt_value`
    (note SQLite stores the default's literal *text*, so the expected value is `'undecided'` **with**
    the quotes).
  - `ex-add-the-foreign-key` (order 3): add `FOREIGN KEY (branch_id) REFERENCES branch(branch_id)`.
    Both tables are built in the learner SQL (schema.sql comment-only), mirroring
    `build-the-3nf-schema`.
  - `ex-alter-the-table` (order 4): the one exercise whose **`schema.sql` is NOT comment-only** — it
    pre-creates `student`, and the learner writes `ALTER TABLE ... ADD COLUMN`. Confirmed this
    converges across the two execution models: the loader prepends `schema.sql` to the editor
    (so Run sees `CREATE` + the learner's `ALTER`), while `grade_check.mjs` seeds `schema.sql`
    separately then runs the raw `starter/solution.sql` (`ALTER` only) — same net DB, because each
    case runs on a fresh in-memory DB.
- **Verified headless (2026-07-03):** all three `grade_check.mjs` → **`RESULT: OK`** (solution passes
  every case, starter fails ≥1). Ran the actual sql.js 1.14.1 engine first to confirm the pragma-probe
  outputs (pk / `"notnull"` — must be quoted, it's a reserved-ish pragma column / `dflt_value` literal
  quoting / `pragma_foreign_key_list` column order) before authoring the `expected` blocks.
  `npm run typecheck` clean (no new TS — reuses the query loader); all 8 new `.mdx` compile under the
  route's `@mdx-js/mdx` pipeline; all 16 JSON valid. Flat staging mirror at `curriculum/SQL Module 5/`
  (top-level `order: 5` in its `module.json`, per the staging convention).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path (standing S1 debt —
  no browser here). `npm run build` not run here (Monaco-heavy; run locally).

### S3 (cont.) — Module 06 (SELECT, Filtering & Sorting) converted (DONE this session)

**Module 06 ("SELECT, Filtering & Sorting") is now a live platform bundle** — the **first module whose
exercises are genuine query-in/result-set-out**, the format the loader/grader were originally built for
(Modules 01–04 were gentle `SELECT`-previews; Module 05 + Checkpoint A Part 2 were probe-graded DDL).
Same hand-authored approach; source was `curriculum/SQL Curriculum Module 06.md`. What shipped under
`src/content/languages/sql/modules/06-select-filtering-sorting/`: `module.json`, the lecture
(`lecture/lecture.mdx` + `quiz.json`, 4 MCQs from the doc's 4 quiz seeds, each expanded to 4 options),
and **five graded query exercises**. `course.json` gains Module 06 at **`order: 7`** — placed *after*
Checkpoint A (`order: 6`), i.e. the sequence is DDL (05) → design/normalize checkpoint (A) → start
querying (06). SQL was already registered, so no `registry.ts` change.

- **All five exercises share one seeded `employee` table** (`schema.sql`, the doc's exact 8 Dunder
  Mifflin rows, including Ryan with `branch_id NULL`). These are result-set-graded (no `probe`): the
  case's `expected {columns, rows}` is compared to the learner query's own result set, with
  `orderMatters` per case.
  - `ex-choose-columns` (order 2): `SELECT` named columns instead of `*` (data-minimization framing).
    orderMatters false; starter is `SELECT *` (fails on column mismatch).
  - `ex-filter-with-where` (order 3): `WHERE branch_id = 2 AND salary > 55000`. Starter omits the
    salary condition → Pam leaks in → fails.
  - `ex-match-a-pattern` (order 4): `WHERE last_name LIKE 'S%'`. Starter uses `LIKE 'S'` (no wildcard)
    → 0 rows → fails.
  - `ex-handle-null` (order 5): `WHERE branch_id IS NULL` (teaches the `= NULL` trap). Starter uses
    `= NULL` → 0 rows → fails.
  - `ex-sort-and-limit` (order 6): `ORDER BY salary DESC LIMIT 3`, **`orderMatters: true`** (the first
    ordered-comparison exercise in the SQL content). Starter omits `LIMIT` → 8 rows → fails.
- **Verified headless (2026-07-03):** all five `grade_check.mjs` → **`RESULT: OK`** (solution passes,
  starter fails ≥1) — the grader runs the real sql.js 1.14.1 binary, so the `expected` blocks are
  engine-confirmed. `npm run typecheck` clean (no new TS — plain result-set query bundles, the loader's
  original path); all 6 new `.mdx` compile; all 12 JSON valid. Flat staging mirror at
  `curriculum/SQL Module 6/` (top-level `order: 7`).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path (standing S1 debt).
  `npm run build` not run here. **Next conversion target: Module 07** (aggregates: `COUNT`/`SUM`/`AVG`,
  `GROUP BY`, `HAVING`).

### S3 (cont.) — Module 07 (Functions & Aggregates) converted (DONE this session)

**Module 07 ("Functions & Aggregates") is now a live platform bundle**, same hand-authored approach as
01–06. Source was `curriculum/SQL Curriculum Module 07.md`. What shipped under
`src/content/languages/sql/modules/07-functions-and-aggregates/`: `module.json`, the lecture
(`lecture/lecture.mdx` + `quiz.json`, 4 MCQs from the doc's 4 quiz seeds, each expanded to 4 options),
and **three graded query exercises**, all reusing the doc's exact 8-row `employee` table (same rows as
Module 06, including Ryan's `branch_id NULL`).

- **Note on module numbering:** at the start of this conversion, `course.json` and
  `src/content/languages/sql/modules/` only went up through Module 06 + Checkpoint A — the "Module 06
  not yet converted" state this file previously documented. Partway through this session Module 06 (and
  later Module 08) appeared on disk and in `course.json`, converted by a concurrent process in the same
  workspace without a corresponding CLAUDE.md update at the time. **Module 07 was authored against
  `order: 8`**, immediately after Module 06's `order: 7` and before Module 08's `order: 9` — confirmed
  by re-reading `course.json` right before finalizing. If a future session finds the ordering surprising,
  this is why: three modules landed in close succession from more than one source in one sitting.
- **Exercises** (result-set-graded, no `probe`, same model as Module 06):
  - `ex-payroll-snapshot` (order 2): one query computing `COUNT(*)`, `SUM(salary)`, `AVG(salary)`,
    `MIN(salary)`, `MAX(salary)` in one row (the lecture's opening example verbatim). Starter has only
    `COUNT(*)` → column-set mismatch → fails.
  - `ex-average-salary-per-branch` (order 3): `GROUP BY branch_id` with `COUNT(*)` + `AVG(salary)` per
    branch, 4 rows including the `NULL`-branch group for Ryan (`orderMatters: false`, since `GROUP BY`
    row order isn't guaranteed). Confirmed via `grade_check.mjs` that sql.js's own `NULL` grouping
    round-trips correctly against a JSON `null` in `expected.rows`. Starter is the ungrouped
    company-wide average → 1 row instead of 4 → fails.
  - `ex-filter-the-groups` (order 4): adds `HAVING COUNT(*) > 1` to the same shape, narrowing to the one
    branch (Scranton) with more than one employee — ties directly into the lecture's inference/minimum-
    group-size security lens. Starter has no `HAVING` → 4 rows instead of 1 → fails.
  - Scalar functions (`UPPER`/`LENGTH`/`||`/`ROUND`/date functions) are covered in the lecture and quiz
    but not given a dedicated graded exercise — consistent with earlier modules not exercising every
    single lecture topic (e.g. Module 05's lecture covered `CHECK` without a `CHECK`-specific exercise).
- **Verified headless (2026-07-03):** all three `grade_check.mjs` → **`RESULT: OK`** (solution passes,
  starter fails ≥1), using the real sql.js 1.14.1 binary. `npm run typecheck` clean (no new TS — plain
  result-set query bundles); all 4 new `.mdx` compile under `@mdx-js/mdx`; all 8 JSON valid. Flat staging
  mirror at `curriculum/SQL Module 7/` (top-level `order: 8`, `ex-` prefix stripped per convention).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path (standing S1 debt).
  `npm run build` not run here. **Next conversion target: Module 08 (Joins)** — already appears
  partially staged by the concurrent process noted above; worth checking its state before starting fresh
  work there.

### S3 (cont.) — Module 08 (Joins) converted **out of order**, ahead of 06/07 (DONE this session, concurrent with the above)

**Module 08 ("Joins") is now a live platform bundle.** This was authored in a separate session running
concurrently with the Module 06/07 work documented just above — hence the "partially staged" note that
session left for whoever hit Module 08 next. The user was asked explicitly first (Module 8 depends on
06/07's `SELECT`/`GROUP BY` content, which weren't converted yet at the time) and chose "convert Module 8
only, out of order" over doing 06/07 first. Source was `curriculum/SQL Curriculum Module 08.md`, same
hand-authored approach as every other SQL module.

What shipped under `src/content/languages/sql/modules/08-joins/`: `module.json`, the lecture
(`lecture/lecture.mdx` + `quiz.json`, 5 MCQs from the doc's 5 quiz seeds, each expanded to 4 options), and
**four graded query exercises** — deliberately the doc's highest-depth module ("the single most heavily
tested topic on the real exam"), covering `INNER JOIN`, `LEFT JOIN`, self-join, and `UNION`. The doc's
`RIGHT`/`FULL OUTER JOIN` sections stay lecture-only prose (no graded exercise), per the doc's own
portability caveat that they need a newer SQLite build than this course's engine may have. `course.json`
gains Module 08 at **`order: 9`** — after Checkpoint A (`6`), 06 (`7`), and 07 (`8`), so it sorts correctly
without renumbering now that all three have landed.

- **All four exercises share one seeded `employee`/`branch` schema** (the doc's exact Dunder Mifflin rows:
  8 employees incl. unassigned Ryan, 4 branches incl. managerless/employee-less Buffalo; the self-join
  exercise adds a `supervisor_id` column with the doc's own supervisor chain). Each is result-set-graded
  with 2 cases: one direct check, one `setup`-based generalization check (a new hire, a new empty branch)
  proving the query isn't hardcoded to the seed rows.
  - `ex-inner-join-employees-and-branches` (order 2): `JOIN ... ON employee.branch_id = branch.branch_id`.
    Starter selects `branch_id` instead of joining → wrong columns → fails.
  - `ex-left-join-find-the-unassigned` (order 3): `LEFT JOIN` so Ryan survives with a `NULL` branch name.
    Starter uses a plain `JOIN` (drops Ryan) → wrong row count → fails.
  - `ex-self-join-supervisors` (order 4): `JOIN employee s ON e.supervisor_id = s.employee_id`. Starter
    joins on `e.employee_id = s.employee_id` (matches everyone to themselves, including Jan who should be
    absent) → wrong row count and values → fails.
  - `ex-union-branch-ids` (order 5): `UNION` of `branch_id` from both tables (NULL + 1–4, doc's exact
    example). Starter uses `UNION ALL` → duplicates survive → wrong row count → fails.
- **Verified headless (2026-07-03):** all four `grade_check.mjs` → **`RESULT: OK`** (solution passes every
  case, starter fails ≥1) — ran the real sql.js 1.14.1 engine first to confirm every expected result set
  (including NULL-sorts-first behavior in the `UNION ... ORDER BY` case) before authoring the `expected`
  blocks. `npm run typecheck` clean (no new TS); all 5 new `.mdx` files (1 lecture + 4 prompts) compile via
  `@mdx-js/mdx`; all 10 new JSON files valid. Flat staging mirror at `curriculum/SQL Module 8/` (top-level
  `order: 9`, matching `course.json`).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path (standing S1 debt).
  `npm run build` not run here. **Next conversion target: Checkpoint B (Multi-Table Report)**, then Module
  09 (Subqueries) — the curriculum map's own suggested order after Joins.

### S3 (cont.) — Module 09 (Subqueries) converted (DONE this session)

**Module 09 ("Subqueries") is now a live platform bundle**, same hand-authored approach as 01–08. Source
was `curriculum/SQL Curriculum Module 09.md` (converted ahead of Checkpoint B, at the user's request —
Module 09 depends only on 06/07/08, all already converted). What shipped under
`src/content/languages/sql/modules/09-subqueries/`: `module.json`, the lecture (`lecture/lecture.mdx` +
`quiz.json`, 5 MCQs from the doc's 5 quiz seeds, each expanded to 4 options), and **five graded query
exercises** — one per headline subquery shape. `course.json` gains Module 09 at **`order: 10`** (after
Module 08's `order: 9`). SQL was already registered, so no `registry.ts` change.

- All five reuse one seeded `employee`/`branch` schema (the doc's 8 employees incl. Ryan `branch_id NULL`,
  4 branches incl. Buffalo `mgr_id NULL` — the NULLs are what several exercises turn on). Result-set-graded,
  2 cases each (one direct, one `setup`-based generalization proving the query isn't hardcoded):
  - `ex-scalar-above-average` (order 2): `WHERE salary > (SELECT AVG(salary) FROM employee)`. Starter
    hardcodes `> 60000` → extra rows → fails.
  - `ex-in-managers` (order 3): `WHERE employee_id IN (SELECT mgr_id FROM branch)`. Starter lists everyone.
  - `ex-not-in-null-trap` (order 4): the `NOT IN` NULL trap + its `IS NOT NULL` fix. Starter is the buggy
    `NOT IN (SELECT mgr_id FROM branch)` → **0 rows** (the trap) → fails. The pedagogical centerpiece.
  - `ex-correlated-branch-average` (order 5): correlated subquery, beat your own branch's average
    (`WHERE x.branch_id = e.branch_id`). Starter uses the company-wide average → extra rows.
  - `ex-not-exists-empty-branches` (order 6): `NOT EXISTS` anti-join for branches with no employees.
    Starter is the fragile `NOT IN (SELECT branch_id FROM employee)` → NULL trap → 0 rows → fails.
- **Verified headless (2026-07-04):** all five `grade_check.mjs` → **`RESULT: OK`** (solution passes,
  starter fails ≥1) on the real sql.js 1.14.1 binary. `npm run typecheck` clean (no new TS — plain
  result-set query bundles); all 6 new `.mdx` compile via `@mdx-js/mdx`; all 12 JSON valid. Flat staging
  mirror at `curriculum/SQL Module 9/`. **NOTE:** Module 09 was originally registered at `order: 10`, but
  Checkpoint B (below) was then inserted at `order: 10` and **Module 09 renumbered to `order: 11`** in both
  `course.json` and its staging `module.json` — so the live sequence is now …08 (9) → Checkpoint B (10) →
  09 Subqueries (11). The live-tree `module.json` omits `order`, so only those two files changed.
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path (standing S1 debt).
  `npm run build` not run here.

### S3 (cont.) — Checkpoint B (Multi-Table Report) built (DONE this session)

The second checkpoint, a **query checkpoint** tying Modules 05–08 together on one seeded four-table store
schema — the join analogue of Checkpoint A's design/DDL focus. Lives in its own module
`checkpoint-b-multi-table-report`. **Sequencing decision:** placed at **`order: 10`, right after Module 08
(Joins)** and **before Module 09 (Subqueries)**, matching the curriculum map's order (map lists B between
08 and 09). Because Module 09 had already been converted at `order: 10`, inserting B **renumbered Module 09
to `order: 11`** (see the Module 09 note above). Like Checkpoint A, it has **no lecture** — the scenario
intro ("Welcome to the store…") lives in the first exercise's prompt.

- **Schema (shared across all 4 exercises, `schema.sql` identical in each):** `customer` /
  `product` / `sales_order` / `order_item` (the reserved word `order` avoided by naming it `sales_order`),
  4 customers incl. **Dave with no orders**, 4 products incl. **Doohickey never ordered** — the two edge
  rows the LEFT-JOIN exercises turn on. All four exercises are result-set-graded (no `probe`), 2 cases each
  (one direct, one `setup`-based generalization proving the query isn't hardcoded):
  - `ex-orders-with-customer` (order 1): 2-table `INNER JOIN` `sales_order`→`customer` for name+city.
    Starter selects bare `customer_id` (no join) → wrong columns → fails.
  - `ex-revenue-per-order` (order 2): 3-table — `JOIN order_item→product`, `SUM(quantity*price)`,
    `GROUP BY order_id`. Starter does `COUNT(*)` and never touches price → wrong values → fails.
  - `ex-customer-total-spend` (order 3): 4-table **`LEFT JOIN`** from `customer` outward +
    `COALESCE(SUM(...),0)` so **Dave shows a true 0** instead of vanishing. Starter uses `INNER JOIN` →
    Dave dropped (3 rows not 4) → fails. The "true zero" idea from Module 08's `COUNT` lesson.
  - `ex-never-ordered-products` (order 4): **anti-join** via `LEFT JOIN ... WHERE oi.product_id IS NULL`
    (no subqueries — those are Module 09). Returns Doohickey. Starter's `INNER JOIN` returns ordered
    products (6 rows) → fails. Prompt forward-references `NOT EXISTS` (Module 09) as the cleaner form.
- **Verified headless (2026-07-04):** ran the real sql.js 1.14.1 engine first to capture every exact result
  set (whole-number sums come back as ints — `24`/`25`/`33`/`0`, not `24.0`), then authored the `expected`
  blocks from that output. All four `grade_check.mjs` → **`RESULT: OK`** (solution passes both cases,
  starter fails ≥1). `npm run typecheck` clean (exit 0, no new TS — plain result-set query bundles); all 4
  `prompt.mdx` compile via `@mdx-js/mdx`; all JSON valid. Flat staging mirror at
  `curriculum/SQL Checkpoint B/` (top-level `order: 10`).
- **`npm run build` PASSED (2026-07-04, user-run locally):** the full static export succeeded with
  Checkpoint B (`order: 10`) and the renumbered Module 09 (`order: 11`) in the tree — so the new routes
  build and `generateStaticParams` picks them up. This clears the standing "build not run here" caveat for
  the current content tree (through Checkpoint B / Module 09).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path (standing S1 debt — needs
  a real browser).

### S3 (cont.) — Module 10 (Data Manipulation & Transactions) converted (DONE this session)

**Module 10 ("Data Manipulation & Transactions") is now a live platform bundle** — the **first module
whose exercises mutate data** (`INSERT`/`UPDATE`/`DELETE`/transactions), so it's the first content use of
the grader's **`probe`-after-mutation** path outside the DDL probes in Module 05 / Checkpoint A Part 2.
Same hand-authored approach as 01–09; source was `curriculum/SQL Curriculum Module 10.md`. Shipped under
`src/content/languages/sql/modules/10-data-manipulation-and-transactions/`: `module.json`, the lecture
(`lecture/lecture.mdx` + `quiz.json`, 5 MCQs from the doc's 5 quiz seeds, each expanded to 4 options), and
**five graded DML exercises**. `course.json` gains Module 10 at **`order: 12`** (after Module 09's
`order: 11`). SQL was already registered, so no `registry.ts` change.

- **All five reuse the doc's 8-employee / 4-branch `employee`+`branch` schema** (Ryan `branch_id NULL`,
  Buffalo `mgr_id NULL`). Every case is **probe-graded** (run the learner's mutation for effect, then a
  `SELECT`/`COUNT(*)` probe supplies the compared result set), and **each exercise carries a mandatory
  "should-be-unchanged" probe** so a learner who forgets a `WHERE` is caught — exactly the contract's
  §3 DML pattern (`docs/sql-test-harness-contract.md`, and `scripts/sql/example-dml/`):
  - `ex-insert-a-new-hire` (order 2): column-list `INSERT` (Kelly Kapoor → branch 2). Starter inserts the
    wrong `branch_id` → new-row probe fails; count probe (9) passes for both.
  - `ex-update-one-row` (order 3): targeted `UPDATE ... WHERE employee_id = 107`. Starter omits `WHERE`
    → reassigns everyone → the "Jan still in branch 1" probe fails.
  - `ex-give-a-raise` (order 4): computed multi-row `UPDATE salary = salary + 3000 WHERE branch_id = 2`.
    Starter omits `WHERE` → the "Jan still 110000" probe fails.
  - `ex-delete-a-row` (order 5): `DELETE ... WHERE employee_id = 107`. Starter is `DELETE FROM employee;`
    → the "seven remain" count probe fails.
  - `ex-rollback-a-mistake` (order 6): the **transaction** exercise. Starter is an open
    `BEGIN; UPDATE employee SET salary = 0;` (no undo); solution adds `ROLLBACK;`. Confirmed sql.js
    semantics work end-to-end in the grader: the starter's **uncommitted** change is visible to the
    probe within the same connection (both probes fail), and the solution's `ROLLBACK` restores the
    pre-transaction state (both pass). This is the first exercise to grade `BEGIN`/`ROLLBACK`.
- **Verified headless (2026-07-04):** all five `grade_check.mjs` → **`RESULT: OK`** (solution passes every
  case, starter fails ≥1) on the real sql.js 1.14.1 binary. `npm run typecheck` clean (no new TS — plain
  probe-graded query bundles, the loader's existing path); all 6 new `.mdx` compile under the route's
  `@mdx-js/mdx` pipeline; all JSON valid. Flat staging mirror at `curriculum/SQL Module 10/` (top-level
  `order: 12`, `ex-` prefix stripped per convention).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path (standing S1 debt).
  `npm run build` not run here (Monaco-heavy; run locally).

### S3 (cont.) — Module 11 (SQL Injection & Secure Query Practices) converted (DONE this session)

**Module 11 ("SQL Injection & Secure Query Practices") is now a live platform bundle** — the security
heart of the course (`[SEC]`). Source was `curriculum/SQL Curriculum Module 11.md`. What shipped under
`src/content/languages/sql/modules/11-sql-injection-and-secure-queries/`: `module.json`, the lecture
(`lecture/lecture.mdx` + `quiz.json`, 5 MCQs from the doc's 5 quiz seeds, each expanded to 4 options),
and **four graded exercises**. `course.json` gains Module 11 at **`order: 13`** (after Module 10's
`order: 12`). SQL was already registered, so no `registry.ts` change.

- **This is the first module with a HYBRID exercise mix** (user-approved format decision, 2026-07-04),
  because injection lives in *application code* gluing strings — the doc itself frames the module as
  "read-and-reason rather than run-in-the-IDE," and the browser has no application tier. So instead of
  forcing the query-in/result-out mold, it ships **2 Track-1 IDE exercises + 2 Track-2 structured
  exercises**:
  - `ex-witness-the-breach` (order 2, `exercise`): learner rewrites a normal login query into the one
    the app builds from `' OR '1'='1' --` and *runs it* against a seeded `users` table — every account
    comes back. Result-set-graded, 2 cases (base + a `setup` adding a CEO row proving it dumps whatever's
    in the table, not a hardcoded 3). Starter is the normal 1-row login → fails.
  - `ex-union-exfiltration` (order 3, `exercise`): learner writes the `... LIKE '%none%' UNION SELECT
    username, password FROM users` query and watches credentials render into a `product` grid (columns
    still labelled `name, price`). `orderMatters: false`, 2 cases (base + `setup` adding a user). Starter
    is a real product search → fails. The UNION structure is forced because the output must have columns
    `[name, price]` (a bare `SELECT username, password` gives the wrong column names).
  - `spot-and-fix-the-injection` (order 4, `modeling`): Track-2 structured — root cause (single-select),
    the login-bypass payload (single-select), why `--` matters (single-select), and a **multi-select
    where only "parameterized query" is in the answer set** (teaches that escaping/blocklists don't
    remove the hole).
  - `defense-in-depth` (order 5, `modeling`): Track-2 structured — why identifiers can't be
    parameterized + allowlist (single-select), why parameterizing beats escaping, why a blocklist is
    weak, and a `matching` field pairing each defense (parameterized query / least privilege / safe error
    handling / allowlist) to the job it does (only one "removes the vulnerability entirely").
- **Lecture adaptations:** dropped the duplicate `# Module 11` H1 (renderer prints the title); converted
  the doc's `<details>` predict-then-reveal "Try it" into a pointer to the two IDE exercises + a Callout
  on the browser's no-application-tier honesty limit; wrapped every bare `<input>`/`<guess>` in inline
  code so the MDX parser doesn't read them as JSX; turned the dialect note into a `<Callout type="warning">`.
- **Verified headless (2026-07-04):** both query exercises → `grade_check.mjs` **`RESULT: OK`** (real
  sql.js 1.14.1 binary); both structured exercises → `grade_check_structured.mjs` **`RESULT: OK`**
  (canonical all-pass, `wrong.json` all-fail). `npm run typecheck` clean (no new TS — reuses the query
  loader + the Track-2 `<StructuredExercise>` renderer); all 5 `.mdx` compile under the route's
  `@mdx-js/mdx` pipeline; all JSON valid (28 files across live tree + staging). Flat staging mirror at
  `curriculum/SQL Module 11/` (top-level `order: 13`, `ex-` prefix stripped, modeling lessons use the
  `N-<slug>.{prompt.mdx,question.json,answer.json,wrong.json,hints.json}` convention).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path AND the
  `<StructuredExercise>` UI (both standing S1/S3 debts — no browser here). `npm run build` not run here
  (Monaco-heavy; run locally).

### S3 (cont.) — Module 12 (Access Control, Views & Auditing) converted (DONE this session)

**Module 12 ("Access Control, Views & Auditing") is now a live platform bundle** — the `[SEC]` module that
**closes the SQL course** (only the Capstone remains in the curriculum map). Source was
`curriculum/SQL Curriculum Module 12.md`. Shipped under
`src/content/languages/sql/modules/12-access-control-views-and-auditing/`: `module.json`, the lecture
(`lecture/lecture.mdx` + `quiz.json`, 5 MCQs from the doc's 5 quiz seeds, each expanded to 4 options), and
**four graded exercises**. `course.json` gains Module 12 at **`order: 14`** (after Module 11's `order: 13`).
SQL was already registered, so no `registry.ts` change.

- **HYBRID exercise mix again** (like Module 11), and here the split is *forced by the engine*: the doc is
  explicit that `GRANT`/`REVOKE`/`CREATE ROLE` are **syntax errors** in the browser's SQLite (it has no user
  accounts) — so the access-control half can't be an IDE exercise — while **`CREATE VIEW` runs everywhere**,
  including sql.js. So it ships **2 Track-1 IDE view exercises + 2 Track-2 structured reasoning exercises**:
  - `ex-column-view` (order 2, `exercise`): learner rewrites a `SELECT *` view into `employee_public`
    selecting only the four safe columns, hiding `salary`. Result-set-graded (the view's column *list* is the
    point — a leaked `salary` column fails the column check), 2 cases (base 8 rows + a `setup` new-hire → 9
    rows, still no salary). Starter is `CREATE VIEW ... AS SELECT * FROM employee` → includes salary → fails.
  - `ex-row-view` (order 3, `exercise`): learner adds `WHERE branch_id = 2` to a `scranton_roster` view (row
    filtering). Result-set-graded, 2 cases (base 5 Scranton rows + a `setup` adding one Scranton + one
    Stamford hire, proving only the Scranton one appears → 6 rows). Starter has no `WHERE` → whole company →
    fails. Both view exercises are `CREATE VIEW ...; SELECT * FROM view;` — the loader prepends `schema.sql`
    to the editor and the grader's no-`probe` path compares the last returning result set (the `SELECT`).
  - `least-privilege-and-dcl` (order 4, `modeling`): Track-2 structured — the DCL sublanguage (single-select),
    least privilege vs. `GRANT ALL` (single-select), a role-level `REVOKE` hitting every member (single-select),
    and why `GRANT` is a *syntax error* in SQLite (single-select). Pure reasoning, because none of it runs in
    the browser.
  - `views-and-the-cia-triad` (order 5, `modeling`): Track-2 structured — the team-lead/salary control
    (single-select: view, not UI-hide or column-delete), why a view is an access-control boundary
    (single-select), what auditing adds (single-select), and a `matching` field mapping views→Confidentiality,
    auditing→Integrity, backup/recovery→Availability (the CIA triad from Module 01).
- **Lecture adaptations:** dropped the duplicate `# Module 12` H1; converted the doc's `<details>`
  predict-then-reveal "Try it" into a pointer to the two view exercises; turned the two `>` dialect-note
  blockquotes and the security-lens blockquote into `<Callout>`s (`warning` for the engine caveats, `note`
  for the security lens); everything else is close to verbatim.
- **Verified headless (2026-07-04):** both view exercises → `grade_check.mjs` **`RESULT: OK`** (real sql.js
  1.14.1 binary — confirms `CREATE VIEW` + `SELECT` grade correctly via the last-returning-result-set path);
  both structured exercises → `grade_check_structured.mjs` **`RESULT: OK`** (canonical all-pass, `wrong.json`
  all-fail). `npm run typecheck` clean (no new TS — reuses the query loader + the Track-2 `<StructuredExercise>`
  renderer); all 5 `.mdx` compile under the route's `@mdx-js/mdx` pipeline; all 28 JSON valid (live tree +
  staging). Flat staging mirror at `curriculum/SQL Module 12/` (top-level `order: 14`, `ex-` prefix stripped,
  modeling lessons use the `N-<slug>.{prompt.mdx,question.json,answer.json,wrong.json,hints.json}` convention).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path AND the
  `<StructuredExercise>` UI (standing S1/S3 debts — no browser here). `npm run build` not run here
  (Monaco-heavy; run locally).

### S3 (cont.) — Capstone (Design, Build & Secure a Small Database) converted — SQL COURSE COMPLETE (DONE this session)

**The Capstone is now a live platform bundle** — the final item in the SQL curriculum. With it, **all 12
modules + Checkpoints A/B + the Capstone are converted**; the SQL course is content-complete end to end.
Source was `curriculum/SQL Curriculum Capstone.md`. Module id `capstone-design-build-secure` at **`order: 15`**
in `course.json` (after Module 12's `order: 14`). SQL was already registered, so no `registry.ts` change.

- **Structured as a checkpoint (NO lecture)** — like Checkpoints A/B, the scenario/stage framing lives in each
  exercise's `prompt.mdx`. It's the biggest bundle yet: **8 graded lessons mapping the doc's six stages** on the
  one **Inkwell Books** bookstore scenario (author/book/customer/book_order/order_line). Hybrid tracks again,
  chosen per stage:
  - `model-the-erd` (order 1, `modeling`): order↔book cardinality (single-select N:M), how to resolve the N:M
    (single-select: associative entity), and an `erd-spec` of all 5 entities + 4 relationships (author→book and
    customer→book_order non-identifying 1:N; both edges into `order_line` identifying 1:N).
  - `normalize-to-3nf` (order 2, `modeling`): which-NF the fat spreadsheet violates (single-select **2NF** — the
    key is the composite `(order_id, book_title)`), the partial deps (multi-select: everything except
    `quantity`), the FDs (`token-set` grammar fd), and a `partition` of each descriptive fact into its 3NF home
    table (labels ignored, groupings graded).
  - `build-the-schema` (order 3, `exercise`, **probe-graded DDL**): write the 5 `CREATE TABLE`s; `tests.json`
    probes structure via `sqlite_master` / `pragma_table_info` / `pragma_foreign_key_list` (five tables exist;
    `book`→`author` FK; `order_line` 2-col composite PK; `order_line` 2 FKs). `schema.sql` is comment-only.
    Starter builds author+customer, leaves the other three under-constrained → discriminates.
  - `customer-spend` (order 4, `exercise`, query): 3-join chain → `ROUND(SUM(price*qty),2)`, `GROUP BY`, ORDER
    DESC. Inner join (Leo, no orders, correctly absent). Starter sums `quantity` not money → fails.
  - `never-sold-books` (order 5, `exercise`, query): `NOT IN` subquery. Starter lists all books → fails.
  - `revenue-by-author` (order 6, `exercise`, query): `LEFT JOIN` ×2 + `COALESCE(...,0)` so Butler shows 0.
    Starter uses inner joins (drops Butler) → fails.
  - `secure-the-catalog` (order 7, `exercise`, **CREATE VIEW**): build `catalog_public` (title + author-name
    join + price). Starter is `SELECT *` (leaks book_id/genre/author_id) → column mismatch → fails.
  - `security-review` (order 8, `modeling`): why the concatenated title search is injectable, the fix
    (parameterize — single-select), why least-privilege GRANTs still matter, and a `matching` of
    parameterize→removes-hole / least-privilege→caps-blast-radius / view→exposes-only-safe-columns.
- **All five query/DDL exercises share the canonical Inkwell `schema.sql`** (DDL + seed from the doc: 5 authors,
  4 customers incl. order-less **Leo**, 7 books incl. never-sold **Kindred**, 4 orders, 8 order lines). Each
  query exercise has **2 cases** (base + a `setup`-based generalization proving the query isn't hardcoded — a
  new Leo order, a new never-ordered book, a bookless new author, a new catalog book). Every `expected` block
  was **captured from the real sql.js 1.14.1 engine first** (a scratch runner), then authored — so they match
  the doc's predicted grids exactly (Maya 59 / Sara 55 / Devon 18; Kindred; Herbert 54…Butler 0; the 7-book
  catalog).
- **Verified headless (2026-07-04):** all 5 query/DDL → `grade_check.mjs` **`RESULT: OK`**; all 3 modeling →
  `grade_check_structured.mjs` **`RESULT: OK`** (canonical all-pass, `wrong.json` ≥1-fail). `npm run typecheck`
  clean (no new TS — reuses the query loader + `<StructuredExercise>`); all 8 `.mdx` compile under the route's
  `@mdx-js/mdx` pipeline; all 46 JSON valid (live tree + staging). Flat staging mirror at
  `curriculum/SQL Capstone/` (top-level `order: 15`; modeling lessons use the
  `N-<slug>.{prompt.mdx,question.json,answer.json,wrong.json,hints.json}` convention, query/DDL use
  `N-<slug>.{prompt.mdx,schema.sql,starter.sql,solution.sql,tests.json,hints.json}`).
- **NOT browser-verified / owed:** the sql.js runtime + results-grid Submit path AND the
  `<StructuredExercise>` UI (standing S1/S3 debts — no browser here). `npm run build` not run here
  (Monaco-heavy; run locally). **The SQL curriculum is now fully converted** — no conversion targets remain.
  The live browser QA pass is now DONE (next subsection); remaining SQL work is a local `npm run build` and the
  minor order-message fix noted below.

### S3 (cont.) — First live browser QA pass + setup-grading fix (DONE 2026-07-04)

First real in-browser pass of the SQL runtime (sql.js results grid + Submit + the Track-2 structured/ERD UI),
driven through Chrome against `npm run dev`. Full report: `docs/sql-browser-qa-2026-07-04.md`.

- **What works live (retires most of the standing S1 debt):** results grid renders (single/multi-column,
  computed aggregates, NULL group in italic, multi-row breach dump); friendly SQLite errors (syntax error →
  `errorExplainer` message + "how to fix", not a stack trace); DDL/DML/transaction (`BEGIN`/`ROLLBACK`) grading;
  and all six Track-2 field types incl. the hand-built ERD editor (03 → 3/3, 04 → 4/4). Non-setup query
  exercises: starter fails, solution passes — browser matches grade_check.
- **CRITICAL bug found + FIXED same day:** per-case `setup` SQL was silently ignored by the browser grader —
  `sql.worker.ts` `runCase()` never ran `tc.setup`, and the loader fused `schema+query` into the editor code so
  there was no seam to insert it. **21 of 47 query exercises** (every one with a `setup` generalization case:
  modules 08, 09, 11, 12, Checkpoint B, Capstone) had a *correct* solution stuck at "N‑1 of N" and thus
  un-completable. `grade_check.mjs` runs setup as a separate step, so it passed headlessly → the
  "passes grade_check ⟺ passes Submit" invariant was broken specifically for setup cases.
- **Fix:** grading now runs **schema → setup → query** per case (matching grade_check). `runCase()` peels the
  fixture-schema prefix off the editor `code` (`code.indexOf(schema)` → slice) to recover the learner's query,
  seeds `schema` explicitly, runs `tc.setup`, then the query; the `Run` path (`handleRun`) is untouched. Loader
  `readSqlExercise()` now emits `JSON.stringify({ schema, cases })` (was `{ cases }`); `SqlTestCase` gained the
  `setup?: string` field (it was on disk + carried by the loader but had no type and no worker handler).
  `scripts/sql/grade_check.mjs` unchanged (it was already correct — it's the reference). Contract comments in
  `loader.ts` updated to match.
- **Verified:** `npm run typecheck` clean; the `grade_check` sweep is still 57/57; a headless sim of the *new*
  `runCase` against the real sql.js 1.14.1 binary over 19 exercises (incl. 14 setup cases) → all OK; live
  browser — 08/ex-inner-join, 08/ex-left-join, checkpoint-b/ex-customer-total-spend, capstone/revenue-by-author
  setup solutions now **2/2** (were 1/2), starters still fail; live regression on 05/ex-alter-the-table (the
  peel edge case: schema pre-creates the table, learner ALTERs) and 06/ex-choose-columns → pass.
- **Message wording fixed (2026-07-04):** `compareResultSets` in `sql.worker.ts` was claiming "not in the
  order the question asks for" any time an `orderMatters` case failed, even when the row *values* were wrong
  (verdict was always correct, wording was misleading). Fixed by checking, on failure, whether the same rows
  are present as a set (sorted-serialized comparison) — only then does it say "wrong order"; otherwise it
  says "Your rows didn't match the expected results." `npm run typecheck` clean after the change. This was
  the last known SQL item; a local `npm run build` (Monaco-heavy) still hasn't been run against the current
  tree.

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
