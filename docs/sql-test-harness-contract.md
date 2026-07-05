# SQL Test-Harness Contract (Phase S2)

The SQL analogue of Python's `test_*` convention and C's `__T__` convention. It is the rule
that makes **"passes `scripts/sql/grade_check.mjs` ⟺ passes Submit in the browser"** true, so
author every SQL exercise to it and keep the headless grader and the browser worker
(`src/lib/languages/sql/sql.worker.ts`, phase S1) seeding/running/diffing submissions the *same*
way.

SQL is the platform's first **non-stdout** language: queries return *tables*, not text. So
grading is **structured result-set comparison**, not `__T__`/print-line parsing. The
`SubmitResult` / `TestCaseResult[]` result shape is unchanged — only *how* pass/fail is decided
changes, and that logic lives in the shared comparison helpers below.

Validated headlessly in the sandbox against the **same `sql.js` 1.14.1 WASM binary the browser
loads** (S0 spike, `docs/sql0-spike-report.md`; grader, `scripts/sql/grade_check.mjs`). Unlike
C's `zig cc` proxy there is **no engine gap** — Node and the browser run the identical engine.
Only the over-the-wire download and the COOP/COEP handshake are browser-only (🌐).

This doc locks **two exercise kinds**:

- **the query contract** (§1–§6) — result-set comparison; the default, and the one the S2 grader
  and fixtures cover. Use it for `SELECT`, for `INSERT`/`UPDATE`/`DELETE`/DDL (via a post-mutation
  probe), and for the Track-1 modeling exercises that have a canonical schema (probe with
  `PRAGMA`/`sqlite_master`).
- **the `structured` contract** (§7) — canonical-form comparison for the genuinely non-SQL
  modeling/normalization answers (FD lists, normal-form judgments, ERD structure). Specced here so
  the doc is canonical; its grader (`scripts/sql/grade_check_structured.mjs`) and the browser
  renderer (`<StructuredExercise>`, backed by the pure `src/lib/structured/grade.ts`) are **built
  and headless-verified (2026-07-03)**.

---

## 1. Files per exercise (query contract)

Mirrors the Python/C exercise layout, with SQL-shaped fixtures instead of a compiled harness:

```
<lessonId>/exercise/
  prompt.mdx      # the task, browser-framed ("press Run", "press Submit")
  schema.sql      # fixture: CREATE TABLE + seed INSERTs — runs before the learner's SQL
  starter.sql     # what the learner starts from — must FAIL >= 1 case
  solution.sql    # reference answer — must PASS every case
  tests.json      # hidden test cases (below) — never shown to the learner
  hints.json      # progressive hints (same array-of-strings shape as Python/C)
```

`schema.sql`, `tests.json`, `solution.sql` are required; `starter.sql` is what the learner edits
(and the grader's discriminator input). The grader also accepts `starter.sql` being absent (then it
only checks that the solution passes).

## 2. `tests.json` — the case shape

An array of cases. Each case runs against a **fresh, re-seeded** in-memory DB, so mutations never
leak between cases and case order is irrelevant.

```json
[
  {
    "name": "returns the three priciest products, most expensive first",
    "setup": "INSERT INTO products (id, name, price, category) VALUES (6, 'Vault', 999, 'home');",
    "probe": "SELECT name, price FROM products WHERE category = 'office' ORDER BY name;",
    "orderMatters": true,
    "caseLenient": false,
    "expected": {
      "columns": ["name", "price"],
      "rows": [["Desk", 210], ["Chair", 95], ["Lamp", 40]]
    }
  }
]
```

| Field | Required | Default | Meaning |
|---|---|---|---|
| `name` | yes | — | Display name shown in the results panel. |
| `expected` | yes | — | The correct result set: `{ columns: string[], rows: unknown[][] }`. |
| `setup` | no | *(none)* | SQL run **after** `schema.sql` and **before** the learner's SQL — per-case fixture variation (prove a query generalizes; set up a mutation's preconditions). |
| `probe` | no | *(none)* | SQL run **after** the learner's SQL; when present, **its** result set is what gets compared (see §3). |
| `orderMatters` | no | `true` | `true` → rows compared in order; `false` → rows compared as a multiset (row order ignored). |
| `caseLenient` | no | `false` | `true` → column-name comparison is case-insensitive (tolerates `Price` vs `price` aliases). Applies to **column names only**, never to values. |

## 3. Which result set is compared

Every case compares exactly one result set against `expected`:

- **No `probe` (the `SELECT` case).** Compare the **last returning result set produced by the
  learner's SQL**. The learner is expected to write a query that returns rows; if their SQL returns
  no result set at all, the case fails with *"your SQL returned no result set."* (Multi-statement
  learner SQL is allowed; the last returning statement is the answer.)
- **With a `probe` (the DML/DDL/modeling case).** Run the learner's SQL for its **effect** (an
  `INSERT`/`UPDATE`/`DELETE`, or `CREATE TABLE`), ignore whatever it returns, then run the `probe`
  query and compare **its** last result set. This is the *post-mutation / post-schema* pattern:
  - **DML:** probe the affected table (`SELECT ... FROM t WHERE ...`) to assert the new state — and,
    crucially, add a second case probing a table/rows that should be **unchanged**, so a learner who
    forgets a `WHERE` clause is caught.
  - **Track-1 modeling (DDL):** probe structure, not data —
    `SELECT name FROM sqlite_master WHERE type='table'` (tables created),
    `PRAGMA table_info(<t>)` (columns/types/NOT NULL/PK), `PRAGMA foreign_key_list(<t>)` (FK edges —
    how identifying/non-identifying and N:M resolution are checked). `starter.sql`/`solution.sql`
    become DDL scripts; nothing else changes.

## 4. Comparison rules (the shared diff)

The canonical comparison lives in `scripts/sql/grade_check.mjs` as `toResultSet` / `colsEqual` /
`resultSetsEqual` — the same helpers proven in the S0 spike. `sql.worker.ts` must diff result sets
**byte-for-byte the same way**. Rules:

1. **Columns first.** Column **count and names** must match `expected.columns` (case-insensitive iff
   `caseLenient`). Authors should give every computed column a stable alias
   (`SELECT COUNT(*) AS n`) so the expected column name is deterministic.
2. **Row count** must match.
3. **Row contents.** Each row is compared cell-by-cell via JSON serialization, so JS value identity
   governs: `NULL` ⟷ `null`, SQLite text ⟷ string, SQLite integers/reals ⟷ JS numbers (`210` and
   `210.0` unify — JS has one number type). If `orderMatters` is `false`, rows are sorted by their
   serialization before comparison (multiset equality).
4. **No leniency on values or types by default.** SQLite is loosely typed; if an exercise can return
   a real where an int is expected, author the `expected` value accordingly or `CAST`/`ROUND` in the
   reference query. Only column *names* have a leniency knob.

## 5. Isolation & fixtures

- **One fresh DB per case.** `new SQL.Database()` → `db.run(schema.sql)` → optional `setup` → learner
  SQL → optional `probe`. Re-seeding per case (~0.14 ms, per the S0 spike) is cheap; bake it in
  rather than resetting state by hand.
- `schema.sql` may hold many statements (multiple `CREATE TABLE` + multi-row `INSERT`); run it as a
  single `db.run(...)`.

## 6. Grading verdict

For a given submission (solution or starter), each case yields one `TestCaseResult`:

- **Learner SQL raises** (syntax error, `no such table/column`, constraint failure) → that case
  fails; the SQLite message is surfaced (and flows through `errorExplainer` in the browser). A
  genuine syntax error typically fails **every** case the same way — the SQL analogue of C's
  "does not compile."
- **`probe` raises** (e.g. the learner never created the table a structural probe expects) → the
  case fails with *"the check query failed to run after your SQL."*
- **Result set matches `expected`** under §4 → pass. Otherwise fail with a compact
  `expected N row(s), cols [...] but got M row(s), cols [...]` message.

**Discriminator (the ship gate).** `grade_check.mjs` exits **0 only if** the solution passes **every**
case **and** (no starter **or** the starter fails **≥ 1**). Anything else exits non-zero — a solution
that doesn't pass, or a starter that already passes everything (a rubber-stamp exercise), both block.
Run it on every exercise before it ships, exactly as Python/C exercises run their `grade_check`.

### Running the grader

```
node scripts/sql/grade_check.mjs [<exercise-dir>] [--verbose]
```

`<exercise-dir>` defaults to `scripts/sql/example/`. Requires `sql.js` resolvable from
`node_modules` (`npm install sql.js@1.14.1`; S1 adds it as a project dependency for the runtime).
Exit codes: `0` = OK (discriminates), `1` = solution failed or starter didn't discriminate, `2` =
bad invocation (missing file, malformed `tests.json`, sql.js not installed).

### Worked examples (headless-verified, S2)

- `scripts/sql/example/` — a **`SELECT`** exercise. Task: the three priciest products, priciest
  first. Two cases (default fixture + a `setup` that adds a new most-expensive row to prove the query
  generalizes rather than hardcodes). Solution passes both; the starter (`SELECT name, price FROM
  products;` — no `ORDER BY`/`LIMIT`) fails both. → `RESULT: OK`.
- `scripts/sql/example-dml/` — an **`UPDATE`** exercise graded by **probe**. Task: raise every
  `office` product's price by 10. Case 1 probes the office rows (should change); case 2 probes the
  home rows (should be untouched). Solution passes both; the starter (forgets `WHERE`) passes case 1
  but fails case 2 — demonstrating why a "should-be-unchanged" probe is mandatory for mutation
  exercises. → `RESULT: OK`.

Both, plus the negative cases (a wrong solution, a non-discriminating `starter == solution`, the
`orderMatters:false` multiset path, the `caseLenient` alias path, and missing-file → exit 2), were
verified headlessly on 2026-07-03 with `sql.js` 1.14.1 / Node v22.

---

## 7. The `structured` exercise kind (Track 2 — modeling/normalization)

Modules 03 (ER modeling) and 04 (normalization), plus the design halves of Checkpoint A and the
Capstone, have answers that are **not result sets** — functional-dependency lists, "which normal
form and why," partial/transitive-dependency identification, cardinality, the
identifying/non-identifying distinction, and ERD structure. When the answer has a **canonical SQL
artifact** (a schema), author it as an ordinary §1–§6 query exercise and probe it with
`PRAGMA`/`sqlite_master` (Track 1 — no new machinery). For the parts with **no SQL artifact**, use
this second kind, graded by **canonical-form comparison** — answers are constrained to structured
fields so grading is exact set/string equality, never NLP.

### 7.1 Files per structured exercise

```
<lessonId>/exercise/
  prompt.mdx        # scenario + task; may include an ungraded "draft it first" area
  question.json     # StructuredQuestion: { draft?, fields: [...] } — the interactive spec
  answer.json       # canonical answer, keyed by field id (pure values)
  hints.json        # same shape as the query/Python/C bundles
  wrong.json        # optional authored wrong answer — the grader's discriminator
```

Comparator options (`grammar`, `matchLabels`) live **on the field in `question.json`**;
`answer.json` (and `wrong.json`) are pure `fieldId → value` maps. Each field's value shape:
`single-select` → string, `multi-select`/`token-set` → string[], `matching` →
`Record<leftItem, option>`, `partition` → `Record<targetName, string[]>`, `erd-spec` → an
`ErdValue` (`{ entities: [{name, attributes:[{name, pk?}]}], relationships: [{from, to,
cardinality, identifying?}] }`).

The lesson `type` is **`"modeling"`** (alongside `"lecture"`/`"exercise"` in `module.json`); the
renderer mounts a `<StructuredExercise>` client component instead of `<Ide>`. No branch on
`language === "sql"`; branch on lesson `type`. Grading is **pure JavaScript over `answer.json`** — no
`sql.js`, no worker, no network; structured exercises don't load the runtime at all.

### 7.2 Field types and their comparators

`question.json` is an ordered list of fields; each maps to one deterministic comparator. `answer.json`
gives the canonical value + comparator per field.

| Field type | Learner does | Graded by |
|---|---|---|
| `single-select` | pick one option | exact match |
| `multi-select` | check all that apply | set equality |
| `token-set` | type items in a fixed mini-grammar (FDs as `a, b -> c`) | normalize (trim, case-fold identifiers, split composite RHS, sort) → set equality |
| `matching` | pair left items to right options | exact per-pair |
| `partition` | drop each attribute into one of N named target tables | partition equality by column-set (table labels matched canonically, ignored by default) |
| `erd-spec` | fill a small structured ERD editor: entities (name + attributes, PK flag) + relationships (two endpoints + cardinality + identifying flag) | structural equality — entity set with attribute sets & PKs; relationship set as unordered endpoint pairs + cardinality + identifying-ness |

Comparator defaults: `token-set` is always set-compared (with `grammar: "fd"`, LHS is sorted and a
composite RHS splits into atoms, so `a -> b, c` ≡ `a -> b` + `a -> c`); `partition` ignores
table-label naming unless `matchLabels: true`; `erd-spec` is compared as unordered sets (entities
with attribute-sets & PKs, relationship endpoint-pairs with cardinality + identifying-ness), with
**endpoints unordered** — `A 1:N B` equals `B N:1 A` — and cardinality normalized to `1:1`/`1:n`/`n:n`.
Nothing is graded pixel-wise. (The current `<StructuredExercise>` ERD editor captures entities and
relationships as structured form fields, not a drawn diagram — a dependency-free choice; a read-only
Mermaid render can be layered on later without changing grading.)

### 7.3 Result shape, lock-step, and the handwritten-exam nod

- **Reuse the existing result shape + UI.** Each field (or assertion) becomes one `TestCaseResult`,
  so `Submit` → `TestResults` renders unchanged and `onAllPassed` → mark-complete works exactly as
  for query exercises.
- **Lock-step.** `scripts/sql/grade_check_structured.mjs` is a **verbatim port** of the
  `src/lib/structured/grade.ts` comparators that `<StructuredExercise>` runs in the browser (the same
  hand-kept-mirror discipline the query grader uses vs. `sql.worker.ts`). Run it with
  `node scripts/sql/grade_check_structured.mjs <exercise-dir>`; it reads `question.json` + `answer.json`
  (+ optional `wrong.json`). Discriminator: the canonical answer passes every field; `wrong.json`
  fails ≥ 1 — the exact same gate as §6. If you change a comparator in `grade.ts`, change it in the
  `.mjs` too.
- **Handwritten-exam skill.** CNIT 27200 is handwritten, so each structured exercise keeps an
  **ungraded "draft it on paper / in this box first" area** ahead of the graded fields (the
  predict-then-reveal convention from the Python/C curriculum), so learners practice producing ERDs
  and FDs without autocomplete.

**Checkpoint A** ("Design & Normalize") is therefore two parts: an `erd-spec` structured part + a
Track-1 DDL part (the normalized 3NF schema, probe-graded) — both auto-checkable. The Capstone's
design/normalize stage reuses the same two tracks.

---

## 8. Relationship to the rest of the plan

- **Engine / runtime shape:** `docs/sql-integration-plan.md` (§ engine decision, results-grid output
  mode, phases). **S0 findings:** `docs/sql0-spike-report.md`.
- **Curriculum & where each exercise kind is used:** `docs/sql-curriculum-map.md`.
- **The lock-step precedent:** `docs/c-test-harness-contract.md` (C) and the Python `grade_check.py`.
  Same invariant, different comparison substrate: C/Python parse `__T__`/`test_*` stdout; SQL diffs
  result sets (query contract) or canonical forms (structured contract).
