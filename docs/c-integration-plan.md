# C Integration Plan

How C becomes a first-class language on the platform, mapped onto the existing
architecture. The guiding fact from `CLAUDE.md`: the app was built so that **adding a
language = implement the `Language` interface + register it + drop in content**, with **zero
component or route changes**. That holds here. The only genuinely new engineering is the C
**runtime** (compile + run C in the browser); everything else reuses machinery already proven
for Python.

Related docs: `docs/c-curriculum-map.md` (content/curriculum), `docs/c-in-browser-runtime-options.md`
(runtime engine research), and the `c-curriculum-builder` skill (authoring module docs).

---

## What already exists (this session)

`src/lib/languages/c/` is scaffolded as a **Phase-C1 skeleton**, mirroring `python/`:

| File | State | Notes |
|---|---|---|
| `config.ts` | **real** | id `c`, Monaco `c`, `.c`, accent, icon. |
| `errorExplainer.ts` | **real** | Friendly text for a fixed set of C error `type`s (compile error, segfault, UB, divide-by-zero, stack overflow, OOM, assert, timeout, non-zero exit). |
| `runtimeProtocol.ts` | **real** | Pinned-engine placeholders, the **reused SAB stdin layout**, status codes, worker message types. |
| `runtime.ts` | **shell** | Interface-conformant; methods throw a clear marker. Server-import-safe. Full intended worker design in comments. |
| `linter.ts` | **shell** | Returns `[]` gracefully (never breaks editing). Intended design = compiler `-fsyntax-only -Wall -Wextra` → `Diagnostic[]`. |
| `c.worker.ts` | **skeleton** | Documents the compile/run/test pipeline and the **test-harness contract**; stubbed to refuse running. |
| `index.ts` | **real** | Assembles the `Language`. **Deliberately NOT registered** (see below). |

`npm run typecheck` is clean with these added.

### Why C is not yet in the registry
The homepage, nav, and course routes are registry-driven, so adding `c` to
`registry.ts` would instantly show a C card whose Run/Submit throw. Register it only when the
runtime works — or first mount it on a temporary `/dev/ide-c` route, exactly how Python's IDE
was proven on `/dev/ide` before going live. The one-line change, when ready:

```ts
// src/lib/languages/registry.ts
import { c } from "@/lib/languages/c";
const LANGUAGES: readonly Language[] = [python, c];
```

---

## Phases

### C0 — Runtime engine spike (decides everything downstream)
Time-boxed prototype before committing. Stand up the candidate engine behind a throwaway
page and **measure three numbers**: cold-load download size, warm-Run latency, and whether a
sanitizer catches a deliberate buffer overflow.

- **Primary candidate:** clang + lld compiled to WASM (+ WASI memfs + C sysroot). Real clang
  diagnostics — the big win for `errorExplainer` and `linter`. Cost: large one-time download.
- **Fallback:** TinyCC-to-WASM — tiny/fast, weaker diagnostics, no sanitizers.
- **Wildcard:** `v86` (real Linux) only if real gdb/valgrind/ASan in-browser proves worth the
  weight.

**Exit criteria:** pick the engine; pin `C_TOOLCHAIN*` constants and `C_TOOLCHAIN_CDN_BASE` in
`runtimeProtocol.ts`; confirm the CDN serves `access-control-allow-origin: *` **and**
`cross-origin-resource-policy: cross-origin` (the same check that made Pyodide/Monaco work
under our `require-corp` policy).

### C1 — Real runtime + linter (the core build)
Implement against the shells already in place, porting `python/pyodide.worker.ts` +
`runtime.ts` structure:

1. **`c.worker.ts`** — load the toolchain from CDN (stream `loadProgress`); `handleRun`
   compiles `main.c` → wasm, runs under WASI, streams stdout/stderr as raw bytes (so unflushed
   `printf` prompts show), and blocks stdin on the SAB for `scanf`/`fgets`/`getchar`. Map traps
   / non-zero exits to the `RuntimeError.type` strings the explainer knows.
2. **`runtime.ts`** — own the worker + input SAB; idempotent `load()`; `run()` routes input via
   `onInput`; honor `signal` (STATUS_CANCELLED for input waits, worker terminate for CPU-bound).
3. **`linter.ts`** — compiler syntax-only pass → `Diagnostic[]` (clamped 1-based, like Ruff).
4. **Mount on a temporary `/dev/ide-c`** route and **browser-verify** (this environment has no
   browser; the live runtime must be click-tested, same caveat as Python Phase 2).

### C2 — Test-harness contract + headless grader
Define the C analogue of Python's `test_*` contract and lock it so **"passes grade_check ⟺
passes in the browser."**

- Hidden `tests.c` provides `main()`, calls the submission's functions, and prints one
  machine-readable line per case (`__T__|name|PASS` / `__T__|name|FAIL|msg`).
- Decide **include-vs-separate-compile** of `submission.c` + `tests.c` and codify it.
- Build test runs with `-fsanitize=undefined` (UBSan) where supported; full AddressSanitizer
  is a **stretch** (ASan on the WASI target is an open gap — see the runtime-options doc), so
  v1 grading = compiler warnings + hidden tests + UBSan. Don't over-promise leak grading.
- Port `scripts/grade_check` to compile/run tests the **same** way the worker does.

### C3 — Content pipeline + go live
1. Adapt `curriculum-converter` to C: `.c` files, the C test harness, browser framing (the C
   module docs are already browser-first). Author the `c-curriculum-builder` master, then build
   Module 1 as the validation fixture (lecture + quiz + a couple of graded exercises).
2. Create `src/content/languages/c/` (`course.json`, modules, lessons) mirroring Python's tree.
   The content loader and MDX path are already language-agnostic.
3. **Register C** in `registry.ts` (the one-liner above). The homepage card, nav link, course
   outline, and `<Runnable>` light up automatically; `<Runnable>` already calls
   `language.runtime.run` via `LessonLanguageProvider`, so inline C runs with no component
   change.

### C4 — Cheat sheet, advanced tracks, polish, deploy
- Add `src/content/languages/c/cheatsheet.mdx` (the route is generic over the registry).
- **Advanced Tracks (Compiler, OS) are LOCAL** — render them as **lecture-type lessons** (no
  `<Ide>`, no runtime): setup-and-build guides clearly flagged local, ideally gated behind
  course completion, with downloadable starter files. They are not browser-run content.
- Deploy: add the toolchain CDN host to the COOP/COEP allowlist; add a **service-worker cache**
  for the large compiler download (first-visit cost, not per-exercise). The GitHub-Pages
  "no headers → stdin degrades to EOF" caveat is identical to Python's and already documented.
- Remove the temporary `/dev/ide-c` route (as `/dev/ide` was removed in Phase 6). After
  deleting a route, `rm -rf .next` before typecheck (stale route types — a known gotcha).

---

## Risks & open decisions

- **Compiler download weight** (clang is large) — mitigated by service-worker cache; the C0
  numbers decide clang-vs-TinyCC.
- **Sanitizer reach** — UBSan yes, ASan/valgrind only guaranteed on the heavy `v86` path; the
  grading plan must not assume full leak detection in v1.
- **Advanced-track target** — compiler track is **x86-64** (not 32-bit) to avoid the
  Apple-Silicon wall; OS track documents ARM-Mac cross-compiler pain.
- **Cross-origin isolation on the host** — required for SAB stdin; verify per deploy target.

## Definition of done
C registered; homepage/nav/outline/cheat-sheet show C with no per-language code; a learner can
Run and Submit C exercises in-browser with friendly errors; `grade_check` and the browser agree
on every seed exercise; advanced tracks render as local guides; typecheck + static export green;
and a real browser pass confirms the live runtime (the one thing not verifiable in this env).
