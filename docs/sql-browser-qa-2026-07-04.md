# SQL course — live browser QA pass (2026-07-04)

First real browser pass of the SQL runtime (sql.js results grid + Submit grading + the
Track-2 structured/ERD UI), driven through the connected Chrome against `npm run dev`
on `http://localhost:3000`. This retires part of the standing "S1 debt: never
click-tested in a browser" note — and surfaced **one critical, shipping-blocking bug**.

> **STATUS: the critical bug was fixed and re-verified live the same day (2026-07-04).
> See "Resolution" at the end of this doc.**

## Headline

- **Results grid, Run, friendly SQLite errors, DDL/DML/transaction grading, and the
  entire Track-2 structured/ERD modeling UI all work.** Verified live, not just headless.
- **CRITICAL: per-case `setup` SQL is silently ignored by the browser grader.** Any
  exercise whose `tests.json` has a `setup`-based generalization case cannot be completed
  in the browser even with the correct solution — Submit sticks at "N‑1 of N checks
  passed." **21 of 47 query/DDL exercises are affected.** These same exercises pass
  `grade_check` headlessly, so the "passes grade_check ⟺ passes in the browser" invariant
  is **broken for setup cases**.
- Everything else checked shows grade_check and the browser in agreement.

## Method

- Headless ground truth first: `grade_check.mjs` + `grade_check_structured.mjs` over **all
  57 exercises → 57/57 OK** (solution passes every case, starter fails ≥1; modeling
  canonical passes, wrong answer fails).
- Live browser: a representative subset (~1 per distinct runtime/grading path). For each,
  Submit the **starter** (expect fail) and the **solution** (expect pass); verdicts read
  straight from the DOM. Solutions were loaded into Monaco via its API; structured answers
  were entered through the real field controls (including hand-building the ERD).

## What passed (browser == grade_check)

| Exercise | Path exercised | Starter | Solution |
|---|---|---|---|
| 01 / ex-see-the-table | plain `SELECT *`, results grid | 0/1 ✓fail | 1/1 ✓pass |
| 06 / ex-handle-null | `IS NULL` vs `= NULL` trap | 0/1 ✓fail | 1/1 ✓pass |
| 06 / ex-sort-and-limit | `ORDER BY … LIMIT`, order-sensitive | 0/1 ✓fail | 1/1 ✓pass |
| 07 / ex-average-salary-per-branch | `GROUP BY` + NULL group, computed cols | 0/1 ✓fail | 1/1 ✓pass |
| 05 / ex-create-the-student-table | DDL, structural **probe** (pragma) | 1/4 ✓fail | 4/4 ✓pass |
| 10 / ex-update-one-row | DML **probe** + unchanged-probe | 1/2 ✓fail | 2/2 ✓pass |
| 10 / ex-rollback-a-mistake | transaction `BEGIN … ROLLBACK` | 0/2 ✓fail | 2/2 ✓pass |
| 04 / normalize-the-orders-table | structured: single/multi/token-set/partition | — | 4/4 ✓pass |
| 03 / model-identifying-relationships | structured: single-select/matching/**ERD editor** | — | 3/3 ✓pass |

Also confirmed live:

- **Results grid** renders correctly across shapes: single column, multi-column, computed
  aggregate columns with right-aligned numbers, the **NULL group shown in italic**, and a
  multi-row "breach" dump. Column headers and row counts correct.
- **Friendly SQLite errors**: a syntax error (`FORM` for `FROM`) renders "SQL couldn't
  understand your statement", the raw `near "FORM": syntax error`, a plain-English
  explanation, and a "How to fix it" line — the `errorExplainer` path, not a raw stack
  trace.
- **All six structured field types** grade correctly in-browser (single-select,
  multi-select, token-set FDs, partition, matching, erd-spec). The custom **ERD editor**
  builds entities/attributes/PKs and relationships and serializes to a passing answer.
- Completion banner + "Show solution" appear on pass; per-check ✓/✗ with expected/got
  detail on fail.

## CRITICAL bug — per-case `setup` is ignored by the browser grader

### Symptom

The correct solution to an exercise with a `setup` case stalls at partial pass. Verified
live in three different modules:

- **08 / ex-inner-join** → solution **1/2** ("generalizes to a newly hired employee… still
  drops unassigned Ryan" — *Expected 8 rows but your query returned 7*).
- **09 / ex-not-in-null-trap** → solution **1/2** (*Expected 6 rows but your query returned 5*).
- **11 / ex-witness-the-breach** → solution **1/2** ("a newly added CEO account leaks too"
  — *Expected 4 rows but your query returned 3*).

In each, the base case passes; only the `setup`-based generalization case fails, and it
fails by exactly the row(s) the `setup` was supposed to INSERT — i.e. the setup mutation
never reached the DB the query ran against.

### Root cause

`src/lib/languages/sql/sql.worker.ts`, `runCase()` (~L194): it makes a fresh DB, runs
`schema` (which the loader deliberately leaves **undefined**), runs the learner `code`,
then an optional `probe`. **It never references `tc.setup`.** The word `setup` does not
appear in the worker at all.

It isn't a one-line add, because of the loader design. `src/lib/content/loader.ts`,
`readSqlExercise()` **fuses `schema.sql` + the query into the editor `code`** (so Run works
without a separate seed) and passes `tests` as `JSON.stringify({ cases })` **with schema
omitted**. So per case the worker runs the fused `schema+query` blob as one unit — there is
no seam at which to insert `setup` between table-creation and the query. Even if the worker
called `db.run(tc.setup)` before `db.exec(code)`, the setup INSERT would fail (tables don't
exist yet); after `code`, the query has already run.

`scripts/sql/grade_check.mjs` keeps the three steps separate — fresh DB → `schema.sql` →
`setup` → learner query — so it applies setup correctly. **That is why headless grade_check
passes while the browser does not.** The two are no longer in lock-step for setup cases.

### Blast radius — 21 of 47 query/DDL exercises

```
08-joins:        ex-inner-join-employees-and-branches, ex-left-join-find-the-unassigned,
                 ex-self-join-supervisors, ex-union-branch-ids
09-subqueries:   ex-scalar-above-average, ex-in-managers, ex-not-in-null-trap,
                 ex-correlated-branch-average, ex-not-exists-empty-branches
11-injection:    ex-witness-the-breach, ex-union-exfiltration
12-access-ctrl:  ex-column-view, ex-row-view
checkpoint-b:    ex-orders-with-customer, ex-revenue-per-order, ex-customer-total-spend,
                 ex-never-ordered-products
capstone:        customer-spend, never-sold-books, revenue-by-author, secure-the-catalog
```

3 verified live; the other 18 share the identical root cause (a `setup` case the worker
drops). Every affected exercise is a learner dead-end: a correct answer can never reach
100%, so the lesson can't be marked complete.

Not affected: the 26 query/DDL exercises without a `setup` case (all single-case or
probe/unchanged-probe multi-case), and all structured/modeling exercises (graded by pure
`grade.ts`, no worker). Those were spot-checked and agree.

### Suggested fix (not applied — QA pass only)

Restore the grade_check execution model in the browser: per case run **schema → setup →
query** as three steps. Concretely, for the Submit path, carry the fixture `schema`
separately (set `payload.schema` to `schema.sql`) and grade the **query only** (the editor
content minus the prepended schema prefix), so `runCase` can do `db.run(schema)` →
`db.run(tc.setup)` → `db.exec(query)`. Keep the fused editor content for the **Run** button
so Run still works standalone. Then re-confirm lock-step: solution 100% and starter <100%
in the browser for all 21, matching grade_check. (Alternatively, split the fused `code` at
the known schema boundary inside the worker — same three-step effect.)

## Minor issue — misleading order-mismatch message

On order-sensitive probe/query failures, `compareResultSets` (worker) reports "The right
rows are there, but not in the order the question asks for" whenever column-count and
row-count match but the ordered comparison fails — even when the **values** differ, not
just the order (seen on 10/ex-update-one-row and 10/ex-rollback-a-mistake starters). The
verdict (fail) is correct; only the explanation is imprecise and could send a learner
chasing an ORDER BY they don't need. Low severity, learner-facing.

## Status of the standing caveats

- "grade_check ⟺ browser" — **holds for non-setup exercises; broken for the 21 setup
  exercises** until the fix above lands.
- Results grid + friendly errors + structured/ERD UI — **now browser-verified** (were owed).
- `npm run build` — not re-run in this pass (a prior local run through Checkpoint B/Module 09
  passed; unaffected here).

## Suggested next steps

1. Fix the worker/loader `setup` handling (above) and re-run the live pass on the 21.
2. Fix the order-mismatch message to only claim "wrong order" when the row multiset matches.
3. Optionally extend the live pass to the remaining non-setup exercises for completeness
   (they're expected to agree; the risk is concentrated in the setup path).

## Resolution (2026-07-04) — implemented & re-verified

The setup bug is fixed. Grading now runs **schema → setup → query** per case, matching
`grade_check.mjs`.

### Changes

- **`src/lib/languages/sql/sql.worker.ts`** — `runCase()` now peels the fixture schema
  prefix off the editor `code` (`code.indexOf(schema)` → slice) to recover the learner's
  query, seeds `schema` explicitly, runs `tc.setup` (the previously-ignored field), then
  the query. The `Run` path (`handleRun`) is untouched.
- **`src/lib/content/loader.ts`** — `readSqlExercise()` now includes the fixture in the
  tests payload: `JSON.stringify({ schema, cases })` (was `{ cases }`). Contract notes at
  the top of the file and above the function updated to match.
- **`src/lib/languages/sql/runtimeProtocol.ts`** — added the `setup?: string` field to
  `SqlTestCase` (it was carried on disk and by the loader but had no type + no worker
  handler). `SqlTestsPayload.schema` already existed.
- No change to `scripts/sql/grade_check.mjs` (the reference grader was already correct).

### Verification

- `npm run typecheck` — clean.
- Reference `grade_check` sweep — still **57/57**.
- **Headless sim of the new `runCase`** against the real sql.js 1.14.1 binary (peel +
  schema + setup + query + probe/compare), 19 exercises incl. 14 setup cases → **ALL OK**
  (every solution passes all cases, every starter fails ≥1).
- **Live browser** (recompiled dev bundle), previously-broken setup exercises now pass:
  08/ex-inner-join **2/2**, 08/ex-left-join **0/2 → 2/2**, checkpoint-b/ex-customer-total-spend
  **0/2 → 2/2**, capstone/revenue-by-author **0/2 → 2/2** — starters still fail.
- **Live regression**, non-setup: 05/ex-alter-the-table (peel edge case: schema pre-creates
  the table, learner ALTERs) **0/1 → 1/1**; 06/ex-choose-columns (plain SELECT) **0/1 → 1/1**.

The "grade_check ⟺ browser" invariant now holds for setup cases too. The order-mismatch
message (minor issue above) was left as-is — not part of this fix.
