# In-Browser C: Runtime Options & Recommendation

**Question this answers:** Can we compile and run learner-written C *entirely client-side*
(no backend), the way Pyodide runs Python today — and which approach should we build the C
`runtime`/`linter` adapters on?

**Short answer:** Yes, it's feasible and it's been done in production. The realistic choice
is between (A) a real **clang+lld compiled to WebAssembly** ("compile in the browser") and
(D) a full **x86 Linux emulator** (`v86`) running a real compiler. A recommends itself for
the beginner course; D is the wildcard that could even pull the advanced tracks back
in-browser. TinyCC-to-WASM (B) is a lighter middle option. Emscripten precompilation (C) is
*not* viable for arbitrary learner code without a server.

---

## What we already have working in our favor

Our Phase-2 IDE infrastructure transfers almost directly:

- **Cross-origin isolation (COOP/COEP) is already configured** (we set it up for Pyodide's
  SharedArrayBuffer). The clang-WASM and emulator approaches want the same isolation.
- **The worker + SAB-blocked stdin model** we built for Python's `input()` is exactly what C
  needs for `scanf`/`fgets` reading from xterm.
- **The `Language` interface** already abstracts `runtime`/`linter`/`errorExplainer`, so C
  slots in as another adapter without touching components.

So this is "build a new runtime adapter," not "re-architect the site."

---

## Option A — clang + lld compiled to WebAssembly (RECOMMENDED)

Ship the real LLVM toolchain (clang front-end + lld linker) as WASM modules plus a WASI
in-memory filesystem and a C sysroot. On "Run," the learner's source is compiled **in the
browser** to a WASM module, which is then instantiated and executed in a worker with stdio
wired to the terminal.

- **Proven:** `binji/wasm-clang` is the canonical demo (clang+lld+memfs, runs fully
  client-side). **Playcode's C compiler runs this in production** ("browsercc": compiles
  Clang/LLVM to WASM; clicking Run compiles your C locally in-browser, then executes via a
  WASI runtime). The same lineage produced several C/C++ online compilers.
- **Pros:** *Real clang diagnostics* — which is gold for our friendly-error explainer (we map
  real compiler messages, not a toy compiler's). Standards-correct C. Fully static-hostable.
  Mirrors the Pyodide mental model one-to-one.
- **Cons:** **Large one-time download** (LLVM is big — tens of MB). Mitigate with a service
  worker cache (wasm-clang already does this) so it's a first-visit cost, not per-exercise.
  `binji/wasm-clang` itself is "alpha demoware," so we'd harden/pin a known-good build rather
  than depend on the demo repo.
- **Sanitizers:** see the caveat section — UBSan is reachable; ASan on the WASI target is not
  guaranteed. Don't hard-depend on ASan here until a spike confirms it.

**Verdict:** Best fit for the beginner course. Realest errors, static hosting, reuses our
worker/stdin/COOP-COEP stack.

---

## Option B — TinyCC (TCC) compiled to WebAssembly

Fabrice Bellard's tiny C compiler (~100 KB native; preprocessor + compiler + assembler +
linker in one) ported to WASM (e.g. via the Zig toolchain).

- **Pros:** *Tiny and fast* — compiles hundreds of lines in tens of ms, so near-instant Run
  and a download orders of magnitude smaller than LLVM. Full enough C for everything in
  Units 1–10.
- **Cons:** **Weaker diagnostics** than clang (worse for beginners and for our error
  explainer). The WASM sandbox imposes **standard-library/header and file-access
  limitations** that need a custom libc/FS shim. No sanitizers.

**Verdict:** Strong fallback if the LLVM download proves too heavy in testing. Trade real
diagnostics + safety tooling for size/speed.

---

## Option C — Emscripten, precompiled per exercise (NOT for the interactive IDE)

Emscripten compiles C→WASM at *build time*. It can't compile arbitrary code the learner
types unless we run a build step — which means a backend, breaking the "fully static, no
server" constraint.

- **Where it's still useful:** building the **fixed test-harness binary** for an exercise at
  *our* build time, and Emscripten *does* support **UBSan** (and ASan) for code we compile
  ourselves. So Emscripten may serve grading-harness needs even though it can't be the live
  "compile what the user typed" engine.

**Verdict:** Rule out as the interactive compiler. Keep in mind for prebuilt test harnesses /
sanitizer instrumentation.

---

## Option D — Full x86 Linux in the browser via `v86` (the wildcard)

`v86` emulates an x86 CPU, JIT-translating machine code to WASM, and boots a real Linux image
entirely in the browser. Inside it you get a **real compiler** (TCC compiles ~300 lines in
~50 ms; gcc also runs), a **real terminal, real `gdb`, real `valgrind`, real sanitizers** —
i.e. the actual local environment, in a tab.

- **Pros:** Maximum authenticity. Could give C the genuine memory-tooling we wanted for
  grading (valgrind/ASan for real), and could even let the **Compiler and OS advanced tracks
  run in-browser** (QEMU-like emulation, a real toolchain) if we ever wanted to drop the
  local requirement.
- **Cons:** **Heavy** — download a Linux disk image; ~100 MIPS so compiles/programs run
  noticeably slower than native; **32-bit only** (no 64-bit kernel), which collides with our
  decision to target x86-64 for the compiler track; statefulness and reproducible grading are
  harder to wire than a clean compile-per-run model.

**Verdict:** Don't build the core course on it, but **prototype it** — it's the only path
that delivers real valgrind/gdb/sanitizers in-browser, and it's the lever if we ever want the
advanced tracks to not require a local install after all.

---

## The sanitizer caveat (affects the grading plan in the curriculum map)

The v2 curriculum map leans on "sanitizer-backed tests so leaks/UB *fail* a submission." Be
careful here:

- **UBSan** works under Emscripten (`-fsanitize=undefined`) and is reachable.
- **ASan on the `wasm32-wasi` target has been an open gap** — it works well under Emscripten,
  but the WASI/clang-in-browser path (Option A's runtime) historically lacked it. Also, in
  WASM a null-pointer deref doesn't trap the way it does natively (address 0 is just memory),
  so some "classic" crashes won't reproduce.
- **Implication:** treat full ASan-style leak/OOB grading as *verify-before-promising*. A
  realistic v1 grading stack = real compiler **warnings** (`-Wall -Wextra`) surfaced as Monaco
  markers + a hidden **test harness** + **UBSan where available**, with full
  AddressSanitizer/valgrind as a stretch (and the place it's guaranteed is Option D's real
  Linux). Soften the curriculum-map wording accordingly.

---

## Recommendation

1. **Build the C runtime on Option A (clang+lld → WASM)**, pinned/hardened from the
   `wasm-clang` lineage, cached via service worker. Reuse our worker + SAB-stdin + COOP/COEP
   stack. This gives real clang errors to feed the `errorExplainer`.
2. **Keep Option B (TinyCC-WASM) as the fallback** if the LLVM payload is too heavy in real
   testing — same adapter shape, smaller/faster, weaker errors.
3. **Grade with:** compiler warnings → markers, a hidden `test_*`-style harness, and UBSan
   where the toolchain supports it. Mark full ASan/valgrind leak-grading as a spike, not a
   guarantee.
4. **Run a time-boxed `v86` prototype** in parallel. If it performs acceptably, it's a way to
   give real memory tooling now — and a possible future route to make the advanced
   Compiler/OS tracks browser-optional.

### Suggested next step
A one-day spike: stand up `binji/wasm-clang` (or Playcode's browsercc approach) behind a tiny
test page, compile-and-run three of our seed exercises, measure the cold-load size and
warm-Run latency, and probe whether UBSan/ASan flags a deliberate buffer overflow. That single
measurement (download weight + Run latency + sanitizer reach) decides A-vs-B and how hard we
can lean on sanitizer grading.

---

## Sources
- binji/wasm-clang (clang+lld+memfs in WASM, live demo): https://github.com/binji/wasm-clang
- Playcode C compiler (browsercc — Clang/LLVM→WASM, compiles in-browser, WASI runtime): https://playcode.io/c-compiler
- Running Clang in the browser using WebAssembly (Wasmer): https://wasmer.io/posts/clang-in-browser
- Compiling C to WebAssembly without Emscripten (Depth-First): https://depth-first.com/articles/2019/10/16/compiling-c-to-webassembly-and-running-it-without-emscripten/
- TinyCC homepage (Bellard): https://bellard.org/tcc/
- TCC RISC-V compiled to WASM with Zig (in-browser compile): https://lupyuen.codeberg.page/articles/tcc.html
- webc86 — compile/run C in browser via TCC / x86 emulation: https://github.com/pixeltris/webc86
- Linux + TinyCC in the browser (VM approach): https://ja.nsommer.dk/articles/linux-and-tiny-c-compiler-in-the-browser-part-one.html
- copy/v86 — x86 emulator + x86-to-WASM JIT in the browser: https://github.com/copy/v86
- JSLinux technical notes (Bellard): https://bellard.org/jslinux/tech.html
- Emscripten sanitizers (UBSan/ASan) docs: https://emscripten.org/docs/debugging/Sanitizers.html
- wasi-sdk "Sanitizer support?" issue: https://github.com/WebAssembly/wasi-sdk/issues/81
- WASI SDK (WebAssembly C/C++ toolchain): https://github.com/WebAssembly/wasi-sdk
- MDN — Compiling a new C/C++ module to WebAssembly: https://developer.mozilla.org/en-US/docs/WebAssembly/Guides/C_to_Wasm
