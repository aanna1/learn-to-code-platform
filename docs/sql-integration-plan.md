# SQL Integration Plan

How SQL becomes the platform's next language, mapped onto the existing architecture. The
guiding fact (same as Python and C): **adding a language = implement the `Language`
interface + register it + drop in content**, with zero route changes. SQL is special in one
way that no prior language was — it has **no stdout/stdin model**. Queries return *tables*,
so SQL is the first language that needs a **new output mode** in `<Ide>` (a results grid
instead of the xterm terminal). That grid is the only genuinely new UI engineering here;
everything else reuses machinery already proven for Python.

Related docs: `docs/language-expansion-plan.md` (SQL is language #4 there — engine choice,
risks, harness sketch, curriculum outline; this doc is the detailed build plan),
`docs/c-integration-plan.md` (the template these phases mirror).

**Strategic note (sequencing).** Doing SQL before finishing C is a low-risk choice and a
good one. SQL's engine (SQLite→WASM, ~1 MB) is trivial next to C's ~60 MB self-hosted clang
bundle, its remaining C work is the harder, still-open item (production toolchain bundle
decision — see the last section). SQL also stress-tests the language abstraction against a
non-stdout language, which is exactly the kind of proof the architecture was built for. This
matches the expansion plan's own "fastest value for least risk" resequencing advice.

---

## Where the platform actually stands today (verified against the tree, 2026-07-01)

This differs from the older "Current focus" notes in `CLAUDE.md`, which predate the bulk of
the content work. Ground truth from the filesystem:

- **Python is the one registered, live language** (`src/lib/languages/registry.ts` lists only
  `python`). The full build (Phases 1–6) is done, and the curriculum is **largely converted,
  not "3 seed lessons"** — `src/content/languages/python/` now has ~18 modules wired into
  `course.json` (01-first-programs → 14-testing-and-quality, plus advanced 15–18 and a
  `t5-tooling-and-ecosystem` module). Each exercise on disk follows the contract
  `prompt.mdx · starter.py · solution.py · tests.py · hints.json`, lectures are
  `lecture/` + `quiz.json`.
- **C is a runtime skeleton with no content.** `src/lib/languages/c/` exists (config +
  errorExplainer + runtimeProtocol real; runtime/linter/worker implemented per C1), the temp
  `/dev/ide-c` route exists, `scripts/c/grade_check.py` is built and headless-verified, and
  `public/c-toolchain/` holds the self-hosted bundle. **C is not registered**, and
  `src/content/languages/c/` **does not exist** — zero C lessons. C's open work is summarized
  in the final section.
- **`<Ide>` is terminal-only.** `src/components/ide/Ide.tsx` hardcodes an editor + `Terminal`
  split and drives execution through `onStdout`/`onStderr`. Nothing renders tabular results
  yet. This is the component SQL must extend.

---

## The one new thing SQL needs: a results-grid output mode

Every prior language produces a stream of text into the terminal. SQL produces a **result
set** (columns + rows). Two small, **additive** changes carry this — neither touches Python
or C:

1. **Interface (`src/lib/languages/types.ts`).** Extend `RunResult` with an optional
   structured payload, e.g.

   ```ts
   export interface QueryResultSet {
     columns: string[];
     rows: unknown[][];
     /** e.g. "3 rows" / "0 rows affected" for DDL/DML. */
     summary?: string;
   }
   export interface RunResult {
     ok: boolean;
     error?: RuntimeError;
     resultSets?: QueryResultSet[]; // NEW — present for tabular languages
   }
   ```

   A script can hold several statements, so `resultSets` is an array (one per statement that
   returns rows). Text-streaming languages simply never set it.

2. **`<Ide>` output pane.** Choose the second pane by language rather than hardcoding
   `<Terminal>`. Cleanest seam: add an optional `outputMode?: "terminal" | "grid"` to
   `LanguageDisplayConfig` (defaults to `"terminal"`), and in `Ide.tsx` render a new
   `<ResultsGrid results={...}/>` when it's `"grid"`. `handleRun` then reads
   `result.resultSets` instead of relying on streamed stdout. Errors still flow through the
   existing `ErrorCallout` + `errorExplainer`; `Submit`/`TestResults` are unchanged (see
   harness below). Keep the change additive: `outputMode` unset ⇒ today's terminal behavior,
   so Python/C are untouched.

`<ResultsGrid>` is a plain HTML table (sticky header, monospace cells, null/blank styling,
"N rows" footer, empty-set and error states). No new dependency required.

**Reuse note:** R (language #8) will later need a **plot-pane** mode. Build the pane-selection
seam generically now (`outputMode` union) so R adds `"plot"` without re-plumbing `<Ide>`.

---

## Engine decision

**`sql.js`** — SQLite compiled to WASM (~1 MB), fully client-side, extremely mature. Load
lazily from CDN, same pattern as Pyodide/Monaco. It gives an in-memory database per run;
seed it with the exercise's fixture schema, execute the learner's SQL, read back result sets.

- *Alternative considered:* **DuckDB-WASM** (columnar/OLAP, better for analytics SQL) — heavier
  and overkill for a beginner course. Stay on sql.js for teaching; DuckDB is a later option if
  an analytics track is ever added.
- **Cold-load / headers:** ~1 MB is trivial (no self-host drama like C). sql.js is published on
  jsDelivr, which already serves `access-control-allow-origin: *` + `cross-origin-resource-policy:
  cross-origin` (verified for Pyodide/Monaco in Phase 2), so it loads under our `require-corp`
  COOP/COEP policy. Add its CDN path to the allowlist and service-worker cache in S4.
- **No stdin/stdout:** the SAB interactive-input plumbing is simply unused for SQL — one less
  thing to wire. Cross-origin isolation is still fine to keep on.

---

## Test-harness contract (result-set comparison, not `__T__` stdout)

C and Python print `__T__|name|PASS/FAIL` lines to stdout. SQL has no stdout, so grading is
**structured result-set comparison** instead. The `SubmitResult` / `TestCaseResult[]` shape
already fits — only *how* pass/fail is decided changes, and that lives inside the runtime.

Proposed exercise bundle (SQL analogue of the Python/C exercise folder):

```
<lessonId>/exercise/
  prompt.mdx        # the task
  schema.sql        # fixture: CREATE TABLE + INSERT seed rows (runs before the learner's SQL)
  starter.sql       # starter query (fails ≥1 test)
  solution.sql      # reference query (passes all tests)
  tests.json        # array of test cases (see below)
  hints.json        # same shape as Python/C
```

`tests.json` — each case runs the learner's SQL against a fresh fixture DB and compares:

```json
[
  {
    "name": "returns the three most expensive products, priciest first",
    "orderMatters": true,
    "expected": {
      "columns": ["name", "price"],
      "rows": [["Desk", 210], ["Chair", 95], ["Lamp", 40]]
    }
  }
]
```

- **Comparison rules:** compare column names (optionally lenient on case/alias) and row
  contents; `orderMatters` toggles ordered vs. set comparison per case (ORDER BY exercises set
  it `true`; membership exercises `false`). For INSERT/UPDATE/DELETE/DDL exercises, the
  "expected" is the **post-mutation state of a queried table**, so a case can carry an optional
  `probe` query run after the learner's statement.
- **Isolation:** each case gets its own freshly seeded in-memory DB (re-run `schema.sql`), so
  mutations don't leak between cases and order of cases doesn't matter.
- **Lock-step rule (the Python/C invariant):** build `scripts/sql/grade_check.mjs` that seeds
  the fixture, runs the query under sql.js in Node, and diffs result sets the **exact same way**
  the worker does — so "passes grade_check" ⟺ "passes in the browser." Discriminator check:
  `solution.sql` passes every case; `starter.sql` fails ≥1.

Lock the contract in `docs/sql-test-harness-contract.md` (the canonical spec, like
`docs/c-test-harness-contract.md`).

---

## Modeling & normalization exercises (Modules 03–04) — the non-query grading format

**Decision (2026-07-02, resolves the open question in `docs/sql-curriculum-map.md`).** Modules
03 (ER modeling) and 04 (normalization) — and the design half of Checkpoint A and the Capstone —
have outputs that are *not* result sets: functional-dependency lists, "which normal form and
why," partial/transitive-dependency identification, cardinality, the identifying vs.
non-identifying distinction, an ERD's structure, and decomposition of a wide table into several
narrower ones. The `schema.sql`/`tests.json` query contract can't grade these. Rather than fall
back to un-gradable free-text prose (impossible to auto-grade on a static, backend-less site
with no LLM at grade time), the platform grades them **two ways, both deterministic and fully
in-browser**:

### Track 1 — prefer DDL grading whenever the answer has a canonical SQL artifact

Much of "modeling" reduces to SQL once you commit to it. Any task whose real deliverable is a
schema — the normalized 3NF tables, the associative table that resolves an N:M relationship, the
foreign-key column that makes a relationship identifying — is authored as an ordinary
**query-contract exercise** and graded by the existing harness above via **structural probe
queries** instead of data queries:

- `SELECT ... FROM sqlite_master WHERE type='table'` → the learner created the expected tables.
- `PRAGMA table_info(<t>)` → expected columns, types, NOT NULL, PK flags.
- `PRAGMA foreign_key_list(<t>)` → expected FK edges (this is how identifying/non-identifying
  and N:M resolution are checked).

So "write the `CREATE TABLE`s that fix this 2NF violation" and Checkpoint A's "produce the
normalized 3NF schema" stay entirely inside the query contract — `starter.sql`/`solution.sql`
become DDL scripts, `tests.json` cases carry the probe queries, and `grade_check.mjs` needs no
change. **This is the default; reach for Track 2 only for the parts that have no SQL artifact.**

### Track 2 — a `structured` exercise kind for the genuinely non-SQL answers

For FD lists, normal-form judgments, dependency identification, cardinality, identifying-ness,
and ERD structure, add a second exercise kind graded by **canonical-form comparison** — answers
are constrained to structured fields so grading is exact set/string equality, never NLP. New
bundle (sibling of the query bundle, same folder position):

```
<lessonId>/exercise/
  prompt.mdx        # the scenario + the task; may include an ungraded "draft it first" area
  question.json     # ordered list of answer fields (the interactive spec)
  answer.json       # canonical answer + per-field comparison mode
  hints.json        # same shape as the query/Python/C bundles
```

`question.json` field types (each maps to one deterministic comparator):

| Field type | Learner does | Graded by | Example prompt |
|---|---|---|---|
| `single-select` | pick one option | exact match | "Which normal form is this table in?" (Not-1NF / 1NF / 2NF / 3NF / BCNF) |
| `multi-select` | check all that apply | set equality | "Select every partial dependency in this table." |
| `token-set` | type items in a fixed mini-grammar (FDs as `a, b -> c`) | normalize (trim, case-fold identifiers, split composite RHS, sort) → set equality | "List all functional dependencies." |
| `matching` | pair left items to right options | exact per-pair | "Mark each relationship identifying or non-identifying." |
| `partition` | drop each attribute into one of N named target tables | partition equality by column-set (table names matched canonically) | "Split this un-normalized table into its 3NF tables." |
| `erd-spec` | fill a small structured ERD editor: entities (name + attributes, PK flag) and relationships (two endpoints + cardinality + identifying flag) | structural equality — entity set with attribute sets & PKs, relationship set as unordered endpoint pairs + cardinality + identifying-ness | "Model this business scenario as an ERD." |

The `erd-spec` field is deliberately **not a free-draw canvas** — it captures exactly what the
exam tests (entities, attributes, keys, cardinality, identifying relationships) as structured
data that grades exactly, and can be *rendered read-only* as a Mermaid ER diagram for visual
feedback without being graded pixel-wise. `answer.json` gives the canonical value + comparator
per field; a field may also carry `orderMatters`-style flags where relevant (e.g. a `token-set`
is always set-compared; a `partition` ignores table-label naming by default).

### Grading mechanics, seams, and lock-step (all additive)

- **Pure, engine-free grading.** Track-2 comparison is pure JavaScript over `answer.json` — no
  sql.js, no worker, no network. Structured exercises don't load the runtime at all.
- **Reuse the existing result shape + UI.** Each field (or assertion) becomes one
  `TestCaseResult`, so `Submit` → `TestResults` renders unchanged; `onAllPassed` → mark-complete
  works exactly as for query exercises. Hints reuse `hints.json`.
- **Additive lesson seam (mirrors `outputMode`).** Lesson `type` gains **`"modeling"`** alongside
  `"lecture"`/`"exercise"` in `module.json`. The lesson renderer already switches on lesson type;
  `"modeling"` mounts a new **`<StructuredExercise>`** client component (the Track-2 field
  renderer + grader) instead of `<Ide>`/`ExercisePane`. Nothing branches on
  `language === "sql"`; Track-1 DDL exercises stay `type:"exercise"`. `<StructuredExercise>` is
  the only new UI Track 2 needs, parallel to `<ResultsGrid>` for the query side.
- **Lock-step (the Python/C/SQL invariant).** `scripts/sql/grade_check_structured.mjs` runs the
  **same** comparators over `question.json`/`answer.json` that `<StructuredExercise>` runs in the
  browser, so "passes grade_check" ⟺ "passes in the browser." Discriminator: the canonical
  answer passes every field; an authored wrong-answer fixture fails ≥1.
- **Handwritten-exam skill.** Because the real CNIT 27200 exam is handwritten, each Track-2
  exercise keeps an **ungraded "draft it on paper / in this box first" area** ahead of the graded
  fields (the predict-then-reveal convention from the Python/C curriculum), so learners practice
  producing ERDs and FDs without autocomplete.

**Checkpoint A** ("Design & Normalize") is therefore a two-part lesson: an `erd-spec` Track-2
part plus a Track-1 DDL part (the normalized 3NF schema, probe-graded) — both auto-checkable. The
Capstone's design/normalize stage reuses the same two tracks.

Lock the Track-2 field grammar and comparator defaults in `docs/sql-test-harness-contract.md`
alongside the query contract (one canonical spec, two exercise kinds).

---

## Curriculum outline

**Superseded by `docs/sql-curriculum-map.md`.** The ten-module outline originally here was
written before the course's actual requirement was known: teach SQL from a cybersecurity
angle, scoped so a learner can pass Purdue's **CNIT 27200 (Database Fundamentals)** test-out
exam. `sql-curriculum-map.md` has the real module list (12 modules + capstone, with ER
modeling/normalization/transactions/injection/access-control added and content-gap flags
against the source transcript) — read that doc for curriculum. Everything below this point in
*this* doc (engine choice, results-grid output mode, test-harness contract, phases) is
unaffected and still the plan of record; exercises for the new module list should still target
the `schema.sql`/`starter.sql`/`solution.sql`/`tests.json` contract defined below so content
and runtime meet cleanly at S3.

---

## Phases (mirror C's C0→C4)

### S0 — Runtime spike (headless)
Prove sql.js end-to-end in the Node sandbox: load WASM → seed a schema → run a query → read
`{columns, rows}` → diff against an expected set. Confirm multi-statement scripts and
INSERT/UPDATE round-trips. Measure cold-load size and warm-run latency. Confirm the jsDelivr
CDN headers. **Output:** `docs/sql0-spike-report.md`.

### S1 — Runtime + results-grid (the core build)
1. `src/lib/languages/sql/` mirroring `python/`: `config.ts` (id `sql`, Monaco `sql`, `.sql`,
   accent/icon, **`outputMode: "grid"`**), `runtimeProtocol.ts` (engine pins + CDN base),
   `runtime.ts` (main-thread adapter: idempotent `load()`, `run()` returns `resultSets`,
   cancel = terminate worker), `sql.worker.ts` (load sql.js, seed DB, exec, map SQLite errors
   to `errorExplainer` types), `linter.ts` (minimal — return `[]` or a light syntax check),
   `errorExplainer.ts` (friendly text for common SQLite errors: `no such table`, `no such
   column`, `syntax error near`, `UNIQUE constraint failed`, etc.), `index.ts` (assemble,
   **not registered yet**).
2. Interface + `<Ide>` changes from the "results-grid output mode" section (additive).
3. Build `<ResultsGrid>` in `src/components/ide/`.
4. Mount a temp **`/dev/ide-sql`** route (via `<Ide>`'s existing `language` override prop, the
   way `/dev/ide-c` works) and **browser-verify** Run + grid rendering. Seed exercise = a simple
   `SELECT`.

### S2 — Test-harness contract + headless grader
Lock `docs/sql-test-harness-contract.md` covering **both** exercise kinds: the query contract
(result-set comparison) and the Track-2 `structured` contract (field grammar + comparator
defaults, per "Modeling & normalization exercises" above). Build `scripts/sql/grade_check.mjs`
(query, + a small fixture under `scripts/sql/example/`) **and**
`scripts/sql/grade_check_structured.mjs` (Track-2, reusing the same comparators the browser
uses). Verify the discriminator (solution/canonical all-pass, starter/wrong-answer ≥1 fail)
headlessly for both. Keep worker ⟺ grader diff logic identical in each.

### S3 — Content + go live
1. Adapt `curriculum-converter` for SQL (`.sql` files, the `schema.sql` + `tests.json`
   bundle, browser framing) — or author directly if the converter changes are heavier than a
   drop-in. Author **Module 1 as the validation fixture** (lecture + quiz + a couple graded
   exercises).
2. Create `src/content/languages/sql/` (`course.json`, modules, lessons) mirroring Python's tree.
   Loader + MDX path are already language-agnostic. **Add the `"modeling"` lesson type + the
   `<StructuredExercise>` renderer** (per "Modeling & normalization exercises" above) so Modules
   03–04 and Checkpoint A can be authored; author at least one Track-2 exercise as the fixture.
3. **Register SQL** — one line in `src/lib/languages/registry.ts`
   (`import { sql } ...; const LANGUAGES = [python, sql]`). Homepage card, nav link, course
   outline, cheat-sheet route, and inline `<Runnable>` light up automatically. `<Runnable>`
   drives `language.runtime.run`; confirm it renders the grid too (or falls back to a compact
   table) for inline SQL in lectures.

### S4 — Cheat sheet, polish, deploy
- `src/content/languages/sql/cheatsheet.mdx` (route is generic over the registry).
- Add sql.js CDN to COOP/COEP allowlist + service-worker cache (light — ~1 MB).
- Remove the temp `/dev/ide-sql` route; `rm -rf .next` before typecheck (stale route types —
  the known gotcha after deleting a route).
- Mobile: the grid must scroll horizontally; confirm the `< md` reading-only fallback still
  applies to SQL exercises.

**Definition of done:** SQL registered; homepage/nav/outline/cheat-sheet show SQL with no
per-language component code; a learner can Run a query and see a results grid, and Submit
against hidden result-set tests with friendly errors; `grade_check` and the browser agree on
every seed exercise; typecheck + static export green; a real browser pass confirms the live
runtime + grid (the one thing not verifiable in this env).

---

## Risks & open decisions (SQL)

- **Output-model change is the crux.** It's small and additive, but it's the first deviation
  from the stdout model — get the `RunResult.resultSets` + `outputMode` seam right so R's
  plot-pane reuses it. Don't special-case `if (language === "sql")` in `<Ide>`; branch on
  `config.outputMode`.
- **Result-set comparison semantics.** Decide per-exercise ordered vs. set comparison, and how
  strict to be on column names/aliases and numeric types (SQLite is loosely typed). Encode
  these as flags in `tests.json`; document defaults in the contract.
- **DML/DDL grading** needs the post-mutation `probe` pattern — spell it out so authors don't
  try to "diff stdout."
- **`<Runnable>` in lectures** currently assumes streamed text. Inline SQL needs the grid (or a
  compact table) there too — verify during S3.
- **Modeling/normalization (Modules 03–04) can't be query-graded.** Resolved above ("Modeling &
  normalization exercises"): Track 1 grades any canonical-schema answer as DDL via `PRAGMA`/
  `sqlite_master` probes inside the existing query contract; Track 2 adds a `structured` exercise
  kind (`question.json`/`answer.json`, a new `"modeling"` lesson type + `<StructuredExercise>`
  renderer) graded by pure canonical-form comparison. Both keep the grade_check ⟺ browser
  lock-step. Don't special-case these lessons in the renderer — branch on lesson `type`.

---

## After SQL ships: resuming the C course

C is further from done than a first read of `CLAUDE.md` suggests, and its remaining work is
heavier than SQL's. Resume in this order:

1. **Browser-verify `/dev/ide-c`** (the owed pass): load under COOP/COEP, Run + Submit the seed
   exercise, confirm friendly compile errors. Submit/grading and the friendly-CompileError case
   are the specific still-unverified paths.
2. **Decide the C toolchain bundle — the gating item.** The dev bundle (binji's clang-8) proved
   plumbing but **lacks UBSan and interactive stdin** and is a C++ demo bundle, not a match for
   the C2 harness contract. The real decision: ship on it with reduced grading, or **build the
   production clang+lld + wasi-libc + compiler-rt + SAB-stdin bundle** (UBSan + interactive
   input). This build is the true gate before C content; make the call explicitly.
3. **C3 — content.** Adapt `curriculum-converter` for C (the `c-curriculum-builder` skill
   already authors the module docs), author Module 1 as fixture, create
   `src/content/languages/c/` (does not exist yet), register C.
4. **C4 — polish.** Cheat sheet, render the two Advanced Tracks (Compiler, OS) as **local
   lecture-only guides** (no `<Ide>`), COOP/COEP + service-worker cache for the ~60 MB bundle,
   remove `/dev/ide-c` (`rm -rf .next` after).
5. **Housekeeping:** soften the "sanitizer-backed leak grading" wording in
   `docs/c-curriculum-map.md` to match the C0 finding (UBSan only; no heap/leak detection).

**What SQL leaves behind for C (and everyone after):** the `/dev/ide-<lang>` proving pattern
and grade_check lock-step are reused as-is. The results-grid work is SQL-specific but the
generic `outputMode` seam it adds to `<Ide>` is what R's plot pane will build on.
