# C0 Spike — Findings

**Goal (from `docs/c-integration-plan.md`):** before committing to the in-browser C runtime,
validate the compile→run→grade pipeline and answer three questions — cold-load size, Run
latency, and **does a sanitizer catch a buffer overflow** — so we can pick clang-vs-TinyCC and
size the grading plan.

**How this was run.** This environment has no browser, so the spike was done **headlessly in
the Linux sandbox** using a real Clang 21 + a bundled **wasi-libc** sysroot (via the
`ziglang` pip wheel — `zig cc` is a clang driver, no root needed), compiling to
`wasm32-wasi` and running under **Node's WASI**. That exercises the engine-independent parts
of the design — the WASI execution model, stdin, exit/trap mapping, sanitizer behavior,
artifact sizes, and the test harness — which are what the in-browser worker will rely on. The
numbers below are **native-proxy** measurements; the items marked 🌐 still need a real
browser to confirm, because they depend on Clang-compiled-to-WASM specifically.

---

## Result: the pipeline works end to end

| Step | Result |
|---|---|
| Compile `hello.c` → `wasm32-wasi` | ✅ |
| Run under WASI, stream stdout, exit code 0 | ✅ `hello 1/2/3`, instantiate+run **1.7 ms** |
| Interactive `scanf`/`fgets` from stdin | ✅ piped `Ada\n41\n` → correct output (validates the read path the browser SAB will back) |
| Hidden-test grading (compile submission + `tests.c`, parse results) | ✅ 3/3 parsed into per-case PASS/FAIL + `allPassed` |

So the `RuntimeAdapter` design in the C skeleton is sound: compile in a worker, run under
WASI, stream stdio, block stdin on the SAB, map faults to `RuntimeError`, parse `__T__` lines
into `TestCaseResult[]`.

## The three numbers

**1. Run latency — not a concern.**
Warm compile (wasi-libc cached) was **~20 ms** native for a small program; instantiate+run was
**~1–2 ms**. 🌐 In-browser Clang-WASM compiles slower than native, but compilation is clearly
not the bottleneck — expect well under a second for learner-sized programs. Confirm in a browser.

**2. Artifact / download size.**
- Per-run artifact (the learner's compiled `.wasm`): **~9 KB gzipped** (`-Os` hello) up to
  **~310 KB gzipped** (program that pulls in more libc via `scanf`/float formatting). Produced
  locally from the cached toolchain, so **per-run download cost is zero**; instantiate stays ~ms.
- wasi-libc **sysroot** (cached once): **~3 MB** (measured).
- 🌐 **The real cold-load is `clang.wasm` + `lld.wasm`** — on the order of **tens of MB** (per
  the Playcode/`wasm-clang` lineage; can't be built here since it means compiling LLVM to WASM).
  This is **the one number that still needs a browser measurement**, and the main risk knob.
  Mitigation already planned: service-worker cache → first-visit-only cost.

**3. Sanitizer reach — the important finding (sharpens the grading plan).**

| Bug | `-fsanitize=undefined` (UBSan) | `-fsanitize=address` (ASan) |
|---|---|---|
| Signed integer overflow | ✅ **caught** (trap; non-trap prints `signed integer overflow: 2147483647 + 1 …`) | n/a |
| Out-of-bounds read on a **fixed-size local array** | ✅ **caught** (trap) | n/a |
| **Heap** OOB write (`malloc`'d buffer) | ❌ **not caught** — ran to exit 0 | would catch |
| ASan availability on `wasm32-wasi` | — | ❌ **unavailable** — link fails: `undefined symbol: __asan_init`, `__asan_report_load4`, … |

Takeaways:
- **UBSan works on wasm and is genuinely useful.** It catches a meaningful UB subset — integer
  overflow, shifts, fixed-array bounds, misalignment — and **non-trap mode prints a
  human-readable message** we can pipe straight into the `errorExplainer` as `UndefinedBehavior`
  before the trap. Recommend compiling Run/Submit with `-fsanitize=undefined` (non-trap, so the
  message shows) for the friendly-error win.
- **AddressSanitizer is confirmed unavailable** on `wasm32-wasi`, so **heap errors, use-after-
  free, and leaks are NOT detectable** on the clang-WASM path. This is exactly the gap the
  integration plan flagged — now proven, not assumed.

## What this means for the plan

- **Engine choice — stay with Clang (Option A).** The spike confirms the two things clang buys
  over TinyCC are real and worth it: precise diagnostics and **working UBSan**. TinyCC has
  **no sanitizers at all**, so falling back to it means losing even UBSan grading — only choose
  it if the 🌐 browser cold-load measurement makes clang.wasm untenable. The decision now has a
  concrete tradeoff attached.
- **Grading plan — finalize as:** compiler warnings (`-Wall -Wextra`) → Monaco markers + hidden
  `test_*`-style harness + **UBSan (non-trap)**. Do **not** promise heap-leak/UAF grading on the
  core path; that authenticity exists only on the heavy `v86` route. Update the curriculum-map
  wording to match (it currently over-leans on "sanitizer-backed leak grading").
- **Test-harness contract — the separate-compile model works** (submission + `tests.c` linked;
  harness declares the submission's prototypes and `main()` prints `__T__|name|PASS|detail`).
  Recommend it as the C2 default; for exercises whose submission is itself a full program with
  `main()`, compile the submission without its `main` or use the include-model. Mirror this
  exactly in `scripts/grade_check` for C so browser ⟺ grade_check stay in lock-step.

## Still requires a real browser (🌐)
1. **Cold-load size + first-load time of the actual `clang.wasm`+`lld.wasm` bundle** — the
   decisive number for clang-vs-TinyCC.
2. In-browser **compile latency** under the WASM-compiled clang (vs. the native proxy here).
3. The **SAB-blocked stdin** path under COOP/COEP with a live xterm (mechanics validated here
   via Node WASI; the cross-origin-isolation wiring is browser-only).

## Suggested next step
Stand up `binji/wasm-clang` (or Playcode's browsercc bundle) on a throwaway page, load it once
with the network panel open, and record the transferred bytes + first-compile time for one of
our seed exercises. That single browser measurement closes items 1–2 and locks the engine
decision. Everything else in the pipeline is now validated.

---

### Repro (sandbox)
`pip install --break-system-packages ziglang` → `python3 -m ziglang cc -target wasm32-wasi
[-fsanitize=undefined] x.c -o x.wasm` → run via a small `node --experimental-wasi-unstable-preview1`
WASI harness. Clang 21.1.0, wasi-libc sysroot ~3 MB.
