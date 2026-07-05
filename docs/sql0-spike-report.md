# SQL S0 Spike — Findings

**Goal (from `docs/sql-integration-plan.md`, phase S0):** before building the SQL runtime,
prove `sql.js` end to end — load the WASM engine, seed a fixture schema, run a query, read back
`{columns, rows}`, and diff against an expected result set — then confirm multi-statement scripts
and INSERT/UPDATE round-trips, measure cold-load size and warm-run latency, and check the jsDelivr
CDN path. This de-risks the two things SQL does differently from every prior language: it has **no
stdout/stdin model** (queries return *tables*, which drives the new results-grid output mode) and
it grades by **result-set comparison**, not `__T__` stdout lines.

**How this was run.** Same approach as the C0 spike — headlessly in the Node sandbox
(Node v22.22.3), no browser. Unlike C0, there is essentially **no native-proxy gap here**: the
browser and Node both run the *same* `sql-wasm.wasm` binary through the same `sql.js` loader, so
the pipeline mechanics validated below are exactly what the in-browser worker will run. The one
thing Node cannot show is the real over-the-wire download and the COOP/COEP + CORS handshake — the
items marked 🌐 below. The engine tested is `sql.js` **1.14.1** (current release), installed from
npm; the CDN section confirms that npm tarball is byte-identical to what jsDelivr serves.

---

## Result: the pipeline works end to end

A single harness (`scripts/sql/spike.mjs`, reproduced below) ran **21 assertions, all passing**.
Each row here is one or more of those assertions.

| Step | Result |
|---|---|
| Load WASM engine (`initSqlJs({ locateFile })`) | ✅ engine up, **cold init ~5 ms** (compile + instantiate; bytes already local) |
| Seed schema (`CREATE TABLE` + multi-row `INSERT`) | ✅ runs before the "learner" SQL, re-seedable per case |
| Run a `SELECT`, read back `{columns, rows}` | ✅ `db.exec()` → `[{ columns, values }]` maps 1:1 to the plan's `QueryResultSet` |
| Diff vs an expected result set (ordered) | ✅ correct set passes; **a wrong set is rejected** by the same diff (discriminator holds) |
| Ordered vs set comparison (`orderMatters`) | ✅ set-compare ignores row order; ordered-compare catches wrong order |
| Multi-statement script → several result sets | ✅ one `exec()` of two `SELECT`s returns **two** result sets (`resultSets[]`) |
| Multi-statement `CREATE`+`INSERT` script persists | ✅ DDL+DML in one `run()`, read back correctly |
| INSERT / UPDATE / DELETE round-trips (probe pattern) | ✅ post-mutation probe query sees the change; `getRowsModified()` gives the "N rows" summary |
| Per-case isolation (fresh re-seeded DB) | ✅ a mutation in one `Database` does not leak into a freshly seeded one |
| Error surface (bad table/column/syntax/constraint) | ✅ all throw with clean, mappable messages (see below) |

So the runtime design in the SQL plan is sound: a worker loads `sql.js`, seeds the fixture,
`exec()`s the learner's SQL, and returns `resultSets` (columns + rows) for `<ResultsGrid>`; the
grader seeds a fresh DB per case and compares result sets with per-case `orderMatters`. **No
stdin/stdout, no SAB** — that plumbing is simply unused for SQL, one less thing to wire.

## The numbers

**1. Cold-load size — the headline, and it's tiny.** The two assets a page must fetch are the
loader glue (`sql-wasm.js`) and the WASM binary (`sql-wasm.wasm`):

| Asset | Raw | Gzipped (over the wire) |
|---|---|---|
| `sql-wasm.wasm` | 659,730 B (≈644 KB) | 323,009 B (≈315 KB) |
| `sql-wasm.js` (loader) | 46,406 B (≈45 KB) | 16,772 B (≈16 KB) |
| **Cold-load total** | **706,136 B (≈690 KB)** | **339,781 B (≈332 KB)** |

That's **lighter than the plan's "~1 MB" estimate** (≈0.69 MB raw, ≈0.33 MB gzipped served), and
about **57× smaller over the wire than C's ~19.4 MB** clang bundle. There is no self-host drama:
one WASM file, one JS loader, both on a public CDN. Service-worker caching (S4) makes it a
first-visit-only cost, but even uncached this is a sub-second download on any normal connection.

**2. Warm-run latency — not a concern.** With the engine loaded and a seeded DB, a representative
`SELECT ... WHERE ... ORDER BY` averaged **~0.029 ms/query** (≈29 µs) over 2,000 runs. Building a
**fresh in-memory DB and re-seeding the fixture** — the per-test-case isolation cost the grader
pays for every case — averaged **~0.137 ms/case** (≈137 µs) over 500 cycles. Both are negligible;
a Submit that runs a dozen isolated cases costs single-digit milliseconds of compute.

**3. Cold init — ~5 ms.** Time from `initSqlJs()` to a usable engine, with the WASM bytes
already in memory (i.e. compile + instantiate only, excluding download; measured 4.9–5.9 ms
across runs). Browser numbers will
differ slightly but compilation is clearly not the bottleneck; the real cold-load knob is the
~332 KB network fetch above, which is small.

## Error surface (feeds `errorExplainer`)

Every failure path throws a JS `Error` whose `.message` is SQLite's native text — clean, stable,
and easy to pattern-match into friendly `RuntimeError` types. Captured live:

| Trigger | `error.message` |
|---|---|
| Query a missing table | `no such table: nope` |
| Reference a missing column | `no such column: nope` |
| Malformed SQL | `near "SELEKT": syntax error` |
| Duplicate a `UNIQUE` value | `UNIQUE constraint failed: products.name` |
| Insert `NULL` into `NOT NULL` | `NOT NULL constraint failed: products.name` |

These map directly onto the `errorExplainer` cases the S1 plan names (`no such table`, `no such
column`, `syntax error near`, `UNIQUE constraint failed`, …). Unlike C's UBSan question, there is
**no sanitizer/detection gap** to worry about here — SQLite reports its own errors precisely.

## CDN / headers (jsDelivr)

- **Published & pinned.** `sql.js@1.14.1` is live on jsDelivr; its `dist/sql-wasm.wasm`
  (659,730 B) and `dist/sql-wasm.js` (46,406 B) are **byte-identical** to the npm tarball measured
  above (confirmed via the jsDelivr metadata API — exact size match), so the gzip/size numbers
  apply to the served asset. Load path mirrors Pyodide/Monaco:
  `https://cdn.jsdelivr.net/npm/sql.js@1.14.1/dist/sql-wasm.{js,wasm}`, with the loader's
  `locateFile` pointing at the `.wasm`.
- **COOP/COEP fit — inherits the Phase 2 verification.** This is the **same jsDelivr CDN** already
  proven in Phase 2 to serve `access-control-allow-origin: *` **and**
  `cross-origin-resource-policy: cross-origin`, which is exactly what lets a resource load under our
  `require-corp` COEP policy (that's how Pyodide + Monaco already load). sql.js needs no different
  treatment; add its path to the allowlist + service-worker cache in S4.
- 🌐 **Live header HEAD check is the one browser-panel item.** Confirming the actual response
  headers on the wire (and that cross-origin isolation stays green with sql.js added) can only be
  done in a browser Network panel — the same browser-only caveat the C0/C1 spikes carried. Given
  the byte-identical asset on an already-verified CDN, this is a confirmation, not a risk.

## What this means for the plan

- **Green-light S1 as written.** The runtime shape in `docs/sql-integration-plan.md` is validated:
  `run()` returns `resultSets` (an array — one entry per returning statement, proven by the
  multi-statement test), errors flow through `errorExplainer`, and there's no stdin/stdout to wire.
  The `outputMode: "grid"` + `RunResult.resultSets` seam is the right (and only necessary) shape.
- **Lock the grader's diff to what the spike used.** The comparison logic proven here — compare
  column names (with an optional case/alias-lenient flag), then compare rows **ordered** or as a
  **multiset** per the case's `orderMatters` — is exactly what `scripts/sql/grade_check.mjs` and the
  worker must share for the "passes grade_check ⟺ passes in the browser" invariant. The
  discriminator (right set passes, wrong set fails) already holds.
- **DML/DDL grading via probe is confirmed.** `getRowsModified()` gives the "N rows affected"
  summary, and a post-mutation probe query observes INSERT/UPDATE/DELETE effects — so mutation
  exercises grade by querying the post-state, and the Track-1 modeling exercises can grade DDL via
  `PRAGMA`/`sqlite_master` probes the same way (S2). No "diff stdout" anywhere.
- **Isolation is cheap and real.** A fresh `new SQL.Database()` + re-seed per case (~0.137 ms)
  guarantees cases don't leak into each other, so case order never matters — bake per-case
  re-seeding into the grader/worker rather than resetting state by hand.
- **Cold-load is a non-issue.** At ≈332 KB gzipped, SQL sidesteps C's entire cold-load saga; the
  S4 service-worker cache is a nicety, not a gate.

## Still requires a real browser (🌐)

1. **Live jsDelivr response headers + cross-origin isolation** with sql.js added (CORS/CORP on the
   wire, COOP/COEP stays green) — a Network-panel confirmation.
2. **`<ResultsGrid>` rendering** of `resultSets` and the first-load feel on the temp `/dev/ide-sql`
   route (S1) — the new UI, untestable headlessly.
3. **Real over-the-wire cold-load time** (vs. the compile-only ~5 ms measured here) — expected to
   be small given ≈332 KB gzipped, but only a browser shows the true first-load number.

## Suggested next step

Proceed to **S1**: scaffold `src/lib/languages/sql/` (`config.ts` with `outputMode: "grid"`,
`runtimeProtocol.ts` pinning `sql.js@1.14.1` + the jsDelivr base, `sql.worker.ts` loading the
engine and returning `resultSets`, `errorExplainer.ts` seeded with the five messages above), add
the additive `RunResult.resultSets` + `outputMode` seam to `types.ts`/`<Ide>`, build
`<ResultsGrid>`, and mount `/dev/ide-sql` for the first browser pass. The engine itself is no
longer a question.

---

### Repro (sandbox)

```
mkdir sql0-spike && cd sql0-spike && npm init -y && npm install sql.js   # 1.14.1
node spike.mjs                                                           # 21/21 asserts, "RESULT: OK"
```

`spike.mjs` derives the `.wasm` path from `require.resolve("sql.js")` (the package blocks
`package.json` subpath access via its `exports` map, so resolve the loader and join
`sql-wasm.wasm`), loads it via `initSqlJs({ locateFile })`, seeds a `products` fixture, and runs
the ten checks in the result table — reading result sets with `db.exec()`, mutating with
`db.run()` + `db.getRowsModified()`, and diffing with the shared ordered/set comparator. It exits
non-zero on any failed assertion, so a clean re-run doubles as a reproducibility check. sql.js
1.14.1, Node v22.22.3.
