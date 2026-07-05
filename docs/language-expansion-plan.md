# Multi-Language Expansion Plan (post-C)

**Status: PLANNING ONLY — nothing in here is implemented.** This document plans the next
languages in the order requested, in the same spirit as the Python (Phases 1–6) and C
(C0→C4) planning in `CLAUDE.md` and the `docs/c-*.md` set. Each language gets a runtime/engine
decision, key risks, a test-harness contract, a curriculum outline, and a phased build
checklist. Read the **Shared foundation** section first — it defines the parts that are
identical for every language so the per-language sections only cover what differs.

**Scope rule (locked):** every language must be **fully client-side** — its compiler or
interpreter runs in the browser, no build server. Kotlin and Swift were considered and
**dropped** because neither can compile in the browser (their official playgrounds compile
server-side), which would require a backend and break the free/static constraint.

Order as requested (first to implement after C):
**1. Java · 2. TypeScript · 3. JavaScript · 4. SQL · 5. PHP · 6. C# · 7. C++ · 8. R · 9. OCaml.**

---

## Shared foundation (applies to every language)

### The one gating question: can it compile/run client-side?

A free, static (GitHub Pages / Vercel static export) site must **compile and run the
learner's code in the browser**. So the language's compiler *or* interpreter has to run
client-side (WASM or JS). All nine languages below satisfy this; they split into two tiers by
how much runtime has to ship:

- **Tier A — trivial client-side** (no heavy runtime to ship): TypeScript, JavaScript, SQL.
- **Tier B — feasible client-side** (ship a WASM runtime/compiler, sometimes large): PHP, C++,
  R, OCaml, and — heavier — Java and C#.

*(Kotlin and Swift would have been "Tier C — not client-side," which is why they're excluded.)*

### The integration contract (identical for all languages)

The language abstraction already exists, so for every language here the wiring is the same as
Python and C and requires **no component changes**:

- Implement `src/lib/languages/<lang>/`: `config.ts`, `runtime.ts`, `linter.ts`,
  `errorExplainer.ts`, `<lang>.worker.ts`, `runtimeProtocol.ts` — mirroring `python/` and
  `c/`.
- Reuse the **SAB stdin layout** from `runtimeProtocol.ts` so `Terminal`/`Ide` interactive
  `input()` plumbing carries over unchanged.
- Conform to the `Language` interface (`config`, `runtime`, `linter`, `errorExplainer`).
- **Register with one line** in `src/lib/languages/registry.ts` — that lights up
  homepage/nav/outline/cheat-sheet/`<Runnable>` automatically.
- **Prove it on a temp `/dev/ide-<lang>` route first** (the way Python used `/dev/ide` and C
  uses `/dev/ide-c`), gated out of the public registry until verified. Remove the temp route
  at the end (`rm -rf .next` after deleting it — stale route types, per the C/Phase-6 note).

Two languages break the uniform "stdout-in-a-terminal" output model and need a **new output
mode** in `<Ide>` (a shared prerequisite, build once, reused):

- **SQL** → a **results-grid** renderer (queries return tables, not stdout).
- **R** → a **plot pane** (R graphics output an image/SVG alongside text).

### The generic per-language phase template (mirrors C's C0→C4)

Every language follows the same five phases. Per-language sections below only note deviations.

- **L0 — Runtime spike (headless).** In the Linux sandbox, prove the engine end-to-end with
  no browser: compile/interpret → run → stream stdout → exit code; feed stdin; run a hidden
  test and parse pass/fail. Produces a `docs/<lang>0-spike-report.md`. (C's C0 is the model.)
- **L1 — Runtime implementation.** Real `runtime.ts` (main-thread adapter) + `<lang>.worker.ts`
  (loads the engine, streams output, maps errors to `errorExplainer` types) + `linter.ts`.
  Mount on `/dev/ide-<lang>`. Cancel = interrupt buffer if supported, else terminate worker.
- **L2 — Test-harness contract + headless grader.** Lock the `tests`↔submission contract and
  build `scripts/<lang>/grade_check.*` so "passes grade_check" ⟺ "passes in the browser"
  (the Python/C lock-step rule). Discriminator check: solution passes all, starter fails ≥1.
- **L3 — Content.** Adapt `curriculum-converter` for the language, author **Module 1 as the
  fixture**, create `src/content/languages/<lang>/`, then **register** the language.
- **L4 — Polish.** Cheat sheet, COOP/COEP + CDN/service-worker cache for the runtime, remove
  the temp route.

### Cross-cutting due-diligence (do once, applies to several)

- **Licensing**: confirm each engine's license permits free, hosted use (most are MIT/Apache/
  BSD/LGPL/MPL). **CheerpJ (Java) has commercial licensing terms** — verify the project's use
  qualifies for free use before committing. js_of_ocaml is LGPL; note attribution.
- **Cold-load budget + COOP/COEP**: every WASM runtime needs cross-origin isolation for SAB
  stdin and is subject to host header limits (the C build already hit jsDelivr's ~20 MB file
  cap → self-host same-origin). Measure cold-load per engine in L0, plan service-worker
  caching in L4.

---

## Implementation-order flag (recommendation)

The requested order is honored in the sections below, but the difficulty curve does **not**
match it, so flag this before starting:

| Order | Language | Tier | Build difficulty | Note |
|------|----------|------|------------------|------|
| 1 | Java | B (heavy) | High | One of the two heaviest builds — a steep first step after C |
| 2 | TypeScript | A | Low | Trivial — could ship in days |
| 3 | JavaScript | A | Lowest | Trivial — no runtime to ship |
| 4 | SQL | A | Low | Easy engine, but needs the results-grid output mode |
| 5 | PHP | B | Moderate | Interpreted, no compile server needed |
| 6 | C# | B (heavy) | High | Feasible client-side via Roslyn-on-Blazor, but a different runtime stack |
| 7 | C++ | B | Moderate | Reuses ~all of the C toolchain — cheapest big win |
| 8 | R | B | Moderate | Easy-ish engine, but needs the plot-pane output mode |
| 9 | OCaml | B | Moderate | Mature in-browser toplevel |

**Suggested resequence** (fastest value for least risk):
**TypeScript → JavaScript → SQL** (trivial, top industry value) → **C++** (reuses C) →
**R → PHP → OCaml** → **Java → C#** (the two heavy client-side builds last). The per-language
plans below remain in your requested order.

---

# Per-language plans

## 1. Java  — Tier B (heavy, client-side feasible)

**Engine recommendation.** **CheerpJ 4.x/5.0** — a WebAssembly JVM with a full OpenJDK
runtime (Java 8/11, 17 in preview; Java 21 targeted 2026). It runs *bytecode* in the browser.
To compile the learner's `.java` **source** without a server, run the **Eclipse Compiler for
Java (ECJ)** as a `.jar` *inside* CheerpJ's JVM: source → ECJ → bytecode → execute on the same
JVM. This keeps the whole compile+run loop client-side.
*Alternatives:* TeaVM (AOT Java→JS/WASM — great output, but AOT compilation itself isn't a
browser REPL); DoppioJVM (older, effectively unmaintained).

**Key risks.**
- **Cold-load**: a full OpenJDK runtime is tens of MB — biggest in the set. Self-host +
  service-worker cache mandatory.
- **Licensing**: CheerpJ has commercial terms — verify free hosted use **before** building.
- ECJ compile latency on top of JVM warm-up.
- Interactive `Scanner`/`System.in` must be wired to the SAB stdin path.

**Test-harness contract.** JUnit-lite: `Tests.java` declares `@Test`-style methods (or a tiny
custom runner) that call the submission's classes/methods and assert; print one
`__T__|<name>|PASS/FAIL` line per case. Neutralize a learner `main()` by having tests call
methods directly (don't invoke `main`). grade_check compiles {submission, tests} with ECJ
headlessly and parses `__T__` lines.

**Curriculum outline.** 01 The JVM & "press Run" · 02 Types & variables · 03 Control flow ·
04 Methods *(Checkpoint: Calculator)* · 05 Classes & objects · 06 Inheritance & interfaces ·
07 Collections & generics · 08 Exceptions · 09 Strings & I/O (browser-adapted) ·
10 Lambdas & streams *(Capstone)*.

**Phases.** L0 spike = ECJ-on-CheerpJ compile+run+stdin+grade headless (or via CheerpJ in a
headless harness). L1–L4 standard; budget extra time on cold-load (L4 caching) and the
licensing check (do it in L0).

---

## 2. TypeScript  — Tier A (trivial client-side)

**Engine recommendation.** Run the official **`typescript` compiler in the browser** for type
diagnostics + transpile to JS, then execute the JS in a sandboxed **Web Worker** with captured
`console`. Optionally use **`esbuild-wasm`** for fast transpile and keep `tsc` only for
diagnostics. No heavy WASM runtime required.

**Key risks.** Minimal. Need a JS execution sandbox (worker, no DOM access, terminate on
infinite loop). `input()` maps to a `readLine()` over the SAB (reuse plumbing) or
`window.prompt` fallback (as `<Runnable>` already does). Keep module resolution single-file.

**Test-harness contract.** Transpile submission TS→JS, run `test_*`-style functions (or a tiny
`assert`) in the worker, capture results. grade_check runs the same transpile+execute under
Node.

**Curriculum outline.** Assumes the JS course as a prerequisite. 01 Why types · 02 Primitive &
inferred types · 03 Functions & signatures · 04 Interfaces & object types · 05 Unions &
narrowing · 06 Generics · 07 Enums & literal types · 08 Working with arrays/records ·
09 Modules & tooling-free patterns.

**Phases.** L0 can be done in an afternoon (transpile+run under Node). No new output mode.

---

## 3. JavaScript  — Tier A (lowest difficulty in the entire set)

**Engine recommendation.** **Native** — execute user code in a sandboxed **Web Worker** with
captured `console`; no compiler or WASM runtime at all. Linting via an in-browser **ESLint**
build (or a lightweight linter) for `linter.ts`.

**Key risks.** Sandbox/security — run in a worker with no DOM/network, terminate on runaway
loops (no cooperative interrupt, like C). `input()` via SAB `readLine()` or `prompt`.

**Test-harness contract.** `test_*` functions or a tiny `assert`, run in the worker; capture
pass/fail. grade_check runs under Node.

**Curriculum outline.** 01 Running JS in the browser · 02 Variables & types · 03 Operators &
control flow · 04 Functions & scope *(Checkpoint)* · 05 Arrays · 06 Objects · 07 Strings ·
08 Higher-order functions · 09 Intro to async (promises) *(Capstone)*.

**Phases.** The natural **first** language to actually ship — it's the lightest and feeds TS.
No new output mode.

---

## 4. SQL  — Tier A (easy engine; needs results-grid output mode)

**Engine recommendation.** **`sql.js`** — SQLite compiled to WASM (~1 MB), fully client-side,
very mature. *Alternative:* **DuckDB-WASM** if you later want analytics/OLAP SQL (heavier).
Use sql.js for teaching.

**Key risks.** Different execution model — there is no stdout/stdin; you **run queries against
an in-memory DB and render a result table**. This requires the **results-grid output mode** in
`<Ide>` (shared prerequisite). Seed each exercise with a fixture DB.

**Test-harness contract.** A test runs the learner's query and **compares the returned result
set** (columns + rows, order-sensitive or not per exercise) to an expected set. grade_check
loads the fixture DB, runs the query, diffs the result set. No `__T__` stdout needed — compare
structured results.

**Curriculum outline.** Superseded by `docs/sql-curriculum-map.md` — SQL is now scoped as a
security-focused course aligned to Purdue CNIT 27200's test-out exam (12 modules + capstone:
relational model & keys, ER modeling, normalization, DDL, SELECT/filtering, aggregates,
joins, subqueries, DML & transactions, SQL injection & secure queries, access control/views/
auditing). The engine choice and phases below are unaffected.

**Phases.** L0 = sql.js query+result-diff under Node. **Extra work: build the results-grid
output mode** (shared with R's needs). Otherwise standard.

---

## 5. PHP  — Tier B (interpreted; no compile server needed)

**Engine recommendation.** **php-wasm** (WebReflection / Sean Morris build) — full PHP
interpreter in WASM, runs source directly, matches the official interpreter, ships the stdlib;
mature (powers WordPress Playground). Use **CLI mode** (run script, capture stdout), not CGI.

**Key risks.** Cold-load size; frame the course as **command-line PHP** (skip the web-server /
superglobals surface for beginners, or defer it). Interactive input via SAB stdin.

**Test-harness contract.** Run {submission, tests} via the PHP CLI; `tests.php` calls the
submission's functions and prints `__T__|name|PASS/FAIL`; neutralize top-level side effects by
having tests `require` the submission and call functions (guard any demo code). grade_check
runs php-wasm (or native PHP) headlessly and parses `__T__`.

**Curriculum outline.** 01 Running PHP · 02 Variables & types · 03 Strings · 04 Arrays
(indexed & associative) · 05 Control flow · 06 Functions *(Checkpoint)* · 07 Associative-array
patterns · 08 Classes & objects · 09 Error handling.

**Phases.** Standard L0→L4. No new output mode.

---

## 6. C#  — Tier B (heavy, but client-side feasible — different runtime stack)

**Engine recommendation.** **Blazor WebAssembly + Roslyn running client-side.** Roslyn can be
loaded into the .NET WASM runtime to **compile and execute C# entirely in the browser** (using
the **Webcil** assembly format) — proven by projects like BlazorCodeEditor. Note: the
high-level Roslyn *scripting* API is limited on Mono-WASM, but full compile-to-assembly works.
**The surprise of the set:** C# is *more* client-side-feasible than Java-source because Roslyn
itself runs on the .NET WASM runtime.

**Key risks.**
- **Integration wrinkle**: this is a **.NET/Blazor runtime**, not the clang/Pyodide
  Worker+WASI mold the other languages share. Expect a runtime-architecture spike — you load
  the .NET WASM runtime + Roslyn and call into it, rather than reusing the standard worker
  pattern verbatim. This is the main reason it's "heavy."
- Large cold-load (.NET runtime + Roslyn + Webcil); self-host + cache.
- Interactive `Console.ReadLine()` → SAB stdin bridge in the .NET host.

**Test-harness contract.** Compile {submission, tests} via in-browser Roslyn; run an
xUnit-lite runner that calls the submission and prints `__T__` lines (or compares results).
grade_check uses the .NET SDK headlessly with the same flags.

**Curriculum outline.** 01 Running C# · 02 Types & variables · 03 Control flow · 04 Methods
*(Checkpoint)* · 05 Classes & objects · 06 Inheritance & interfaces · 07 Collections &
generics · 08 LINQ basics · 09 Exceptions *(Capstone)*.

**Phases.** L0 must validate the Roslyn-on-Blazor compile+run+grade path specifically (this is
the riskiest spike of the Tier-B set). L1 likely diverges from the standard worker adapter.

---

## 7. C++  — Tier B (reuses ~all of the C toolchain — cheapest big win)

**Engine recommendation.** **Clang → WASM**, the **same toolchain as the in-progress C build**
(`clang -cc1` + `wasm-ld` + wasi-libc). Add **libc++** to the sysroot and C++ flags
(`-std=c++17`/`20`, `-x c++`). Reuse C's `runtime.ts`, worker, error mapping, and the
self-hosted bundle almost verbatim.

**Key risks.** Larger sysroot (libc++); longer compile times; **template/STL error verbosity**
— extend `errorExplainer` with C++-specific patterns. Same sanitizer story as C (UBSan works
on wasm32-wasi; **ASan does not** — no heap/leak/UAF detection on the core path).

**Test-harness contract.** **Identical to C's** separate-compile model: `tests.cpp` owns
`main()` + declares the submission's prototypes; compile the submission TU with
`-Dmain=__student_main__` to neutralize a student `main`; print `__T__` lines. Reuse
`scripts/c/grade_check.py` adapted to `clang++ -std=c++17`.

**Curriculum outline.** Builds on C. 01 From C to C++ · 02 References & `auto` · 03 Classes &
RAII · 04 Constructors/destructors *(Checkpoint)* · 05 Operator overloading · 06 Templates ·
07 The STL (`vector`/`string`/`map`) · 08 Smart pointers · 09 Exceptions *(Capstone)*.

**Phases.** Lowest marginal cost of any Tier-B language because C is done — L0/L1 are mostly
"add libc++ + C++ flags to the existing C runtime." No new output mode.

---

## 8. R  — Tier B (easy-ish engine; needs plot-pane output mode)

**Engine recommendation.** **WebR** — R compiled to WASM (Emscripten), mature, runs
client-side; interpreted, so no compile server. Packages load on demand from the WebR repo.

**Key risks.** **Large cold-load** (~30 MB+); network for on-demand packages. **Plotting** —
R graphics need a **plot-pane output mode** in `<Ide>` (image/SVG), the second new output mode
(shares the "non-terminal output" work with SQL). stdin is secondary (R is REPL/script).

**Test-harness contract.** Run {submission, tests} in WebR; tests use `stopifnot()`/asserts or
compare returned values/data frames; print `__T__` lines or compare structured results.
grade_check runs WebR (or native R) headlessly.

**Curriculum outline.** 01 Running R · 02 Vectors · 03 Indexing & subsetting · 04 Data frames
*(Checkpoint)* · 05 Functions · 06 The apply family · 07 Basic statistics · 08 Plotting (with
the plot pane) · 09 Intro to tidy data.

**Phases.** L0 = WebR run + value/data-frame diff. **Extra work: plot-pane output mode** (pair
with SQL's grid work). Plan cold-load caching carefully in L4.

---

## 9. OCaml  — Tier B (mature in-browser toplevel)

**Engine recommendation.** **js_of_ocaml** with an **in-browser toplevel** — TryOCaml
(`try.ocamlpro.com`) proves client-side compile+run: `ocamlc` bytecode → JS toplevel with
embedded `cmis`. Relatively light compared with Java/C#/.NET.

**Key risks.** Toplevel build setup (embedding `cmis`, linking `js_of_ocaml-toplevel`); error
message mapping into `errorExplainer`; niche → less off-the-shelf tooling; LGPL license note.
stdin handling through the toplevel.

**Test-harness contract.** Run {submission, tests} in the toplevel; assert-based tests that
call the submission's functions and print `__T__` lines. grade_check runs the same via a
js_of_ocaml toplevel under Node, or native `ocaml`/`dune` for parity.

**Curriculum outline.** 01 Running OCaml · 02 `let` & immutability · 03 Functions & currying ·
04 Pattern matching *(Checkpoint)* · 05 Variants & algebraic data types · 06 Recursion &
lists · 07 Higher-order functions · 08 Modules · 09 A tiny interpreter *(Capstone)*.

**Phases.** Standard L0→L4. No new output mode.

---

## Summary: what gates each language

| # | Language | Engine | Tier | New output mode? | Main gating item |
|---|----------|--------|------|------------------|------------------|
| 1 | Java | CheerpJ + ECJ | B | no | Cold-load + CheerpJ licensing check |
| 2 | TypeScript | `tsc`/esbuild in worker | A | no | None — trivial |
| 3 | JavaScript | native + worker | A | no | None — lightest; ship first |
| 4 | SQL | sql.js | A | **results grid** | Build the grid output mode |
| 5 | PHP | php-wasm (CLI) | B | no | Cold-load; frame as CLI |
| 6 | C# | Roslyn on Blazor WASM | B | no | .NET runtime-stack spike + cold-load |
| 7 | C++ | Clang→WASM (reuse C) | B | no | Add libc++ + C++ error mapping |
| 8 | R | WebR | B | **plot pane** | Build the plot output mode + cold-load |
| 9 | OCaml | js_of_ocaml toplevel | B | no | Toplevel build setup |

**Two shared prerequisites worth scheduling early:** the **results-grid** (SQL) and
**plot-pane** (R) output modes — both extend `<Ide>` beyond the xterm terminal and are the
only places these languages deviate from the otherwise-uniform integration. Every language
here is fully client-side, so none requires a backend.

---

## Sources (engine research)

- [CheerpJ 4.0 — WebAssembly JVM, Java 11 (Leaning Technologies)](https://labs.leaningtech.com/blog/cheerpj-4.0)
- [CheerpJ roadmap — modern Java in the browser](https://cheerpj.com/our-roadmap-for-modern-java-in-the-browser/)
- [BlazorCodeEditor — client-side C#/Roslyn in the browser (GitHub)](https://github.com/thatplatypus/BlazorCodeEditor)
- [Building a C# REPL in the browser with Blazor + Roslyn (Strathweb)](https://www.strathweb.com/2019/06/building-a-c-interactive-shell-in-a-browser-with-blazor-webassembly-and-roslyn/)
- [php-wasm (WebReflection, GitHub)](https://github.com/WebReflection/php-wasm)
- [js_of_ocaml (ocsigen, GitHub)](https://github.com/ocsigen/js_of_ocaml)
- [sql.js (SQLite compiled to WASM)](https://sql.js.org/)
- [WebR — R in the browser](https://docs.r-wasm.org/webr/latest/)
