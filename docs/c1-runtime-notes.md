# C1 Runtime Notes — engine locked, bundle gap, what's verified

Phase C1 status: the C runtime is **implemented against the real toolchain API and is
typecheck-clean**, mounted on a temporary `/dev/ide-c` harness. It has **not** been browser-run
in this environment (no browser; same caveat Python's Phase 2 carried), and the dev compiler
bundle has known gaps versus the C2 contract. Read this before the browser-verification pass or
before swapping in the production bundle.

## Engine decision — LOCKED: clang + lld → WASM

Confirmed by the C0 spike (real diagnostics + working UBSan) and the C1 cold-load measurement
(`docs/c1-coldload-measurement.md`: ~19 MB transferred, one-time + service-worker cached). TinyCC
was rejected — it has no sanitizers, which the whole C2 grading/error-explainer story leans on.

## Two bundles: dev (binji) vs prod (purpose-built)

The runtime loads a clang/lld/sysroot bundle from a CDN (`C_TOOLCHAIN_CDN_BASE` in
`runtimeProtocol.ts`), exactly as Python loads Pyodide from jsDelivr.

**Dev/spike bundle = `binji/wasm-clang`** (what the cold-load was measured on, what
`/dev/ide-c` loads today). It proves the worker plumbing end-to-end, but reading its `shared.js`
source surfaced gaps that mean it is **not** a drop-in for the C2 contract:

| Gap | Detail | How the worker copes today |
|---|---|---|
| C++ default | its `compile()` hardcodes `-x c++ -O2` | we bypass it and call `clang -cc1 -x c` with the C2 flags directly |
| Old clang | clang 8.0.1 | include path pinned to `/lib/clang/8.0.1/include` via `C_CLANG_VERSION` |
| **No UBSan runtime** | sysroot almost certainly lacks compiler-rt; `-fsanitize=undefined` would fail to link | `C_SUPPORTS_UBSAN = false` gates the UBSan flags off, so basic C still runs |
| Non-interactive stdin | its `App` reads stdin from a preset string (no blocking) | v1 feeds EOF; the SAB-backed `host_read` upgrade is stubbed (`resetMemfsStdin`) |
| `clock_time_get` unimplemented | throws in its WASI shim | programs using `clock()`/`time()` will fault — note in content |
| CDN size | jsDelivr must serve the ~31 MB `clang` blob | verify on first deploy; self-host/mirror if rejected |

**Prod bundle = a purpose-built clang+lld + wasi-libc + compiler-rt (UBSan) sysroot**, plus the
interactive SAB stdin shim. Building it is an offline LLVM-to-WASM task — the real remaining C1
engineering. When it exists, flip `C_SUPPORTS_UBSAN = true`, point `C_TOOLCHAIN_CDN_BASE` at it,
adjust `C_CLANG_VERSION` + the link args, and wire `resetMemfsStdin`/`host_read` to block on the
input SAB. No other code changes — the worker/runtime are written to that target.

## What's implemented (this session)

- `runtimeProtocol.ts` — engine pins, CDN base, the `clang -cc1` C flag set, UBSan gate, the
  `-Dmain=__student_main__` neutralizer, reused SAB layout.
- `runtime.ts` — full main-thread adapter (port of Python's): owns the worker + input SAB,
  idempotent `load()` with progress, serialized `run()`/`runTests()`, cancel = terminate the
  worker (WASM has no cooperative interrupt). Server-import-safe.
- `c.worker.ts` — loads binji's `API` (fetch+eval `shared.js`, capture the global), then
  compiles (`clang -cc1 -x c`) → links (`wasm-ld`) → runs, streaming stdout and buffering
  compile diagnostics. Maps faults to the `errorExplainer` types. `runTests` does the C2
  separate-compile harness and parses `__T__` lines — the same model as the verified
  `scripts/c/grade_check.py`.
- `/dev/ide-c` — temporary harness mounting `<Ide>` against C via the new `language` override
  prop (so C stays out of the public registry until verified). Seed exercise = `sum_to`.

`npm run typecheck` passes. A full `npm run build` could not run in the build sandbox (the
Monaco-heavy compile exceeds the available time budget there); run it locally to confirm the
static export of `/dev/ide-c`.

## Browser-verification checklist (owed — needs a real browser)

1. `/dev/ide-c` loads the compiler under COOP/COEP (network panel shows the ~19 MB one-time
   fetch from the CDN, then cached).
2. **Run** the seed solution → compiles, links, prints `sum_to(10) = 55`.
3. **Submit** the seed solution → 4/4 pass; the starter → ≥1 fail (matches `grade_check.py`).
4. A deliberate syntax error → a friendly `CompileError` (clang diagnostic surfaced).
5. Confirm whether binji's bundle links our flags at all; if UBSan/stdin/clock gaps block real
   lessons, prioritize the production bundle build before C3.
