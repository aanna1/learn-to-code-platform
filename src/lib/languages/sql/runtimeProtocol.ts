import type { QueryResultSet, RuntimeError, TestCaseResult } from "@/lib/languages/types";

/**
 * Pinned engine for the in-browser SQL runtime: **sql.js** — SQLite compiled to
 * WASM. The worker loads the loader glue + the `.wasm` from jsDelivr (the same CDN
 * already proven under our COOP/COEP `require-corp` policy for Pyodide + Monaco:
 * it serves `access-control-allow-origin: *` and `cross-origin-resource-policy:
 * cross-origin`), instantiates an in-memory database per run, executes the
 * learner's SQL, and reads back result sets.
 *
 * Validated end-to-end headlessly in the S0 spike (docs/sql0-spike-report.md,
 * 21/21 asserts): cold-load ≈332 KB gzipped, warm query ≈0.03 ms. Unlike Python/C
 * there is **no stdin/stdout model and no SharedArrayBuffer** — queries return
 * tables, so none of the interactive-input plumbing is used here.
 */
export const SQLJS_VERSION = "1.14.1";
/** jsDelivr base for `sql-wasm.js` (loader) + `sql-wasm.wasm` (engine). */
export const SQLJS_CDN_BASE = `https://cdn.jsdelivr.net/npm/sql.js@${SQLJS_VERSION}/dist/`;
/** UMD loader glue; `importScripts`-ed in the worker, then `self.initSqlJs(...)`. */
export const SQLJS_LOADER_FILE = "sql-wasm.js";
/** The WASM binary; sql.js fetches it via the loader's `locateFile` hook. */
export const SQLJS_WASM_FILE = "sql-wasm.wasm";

// ---------------------------------------------------------------------------
// Test-harness payload (result-set comparison, not `__T__` stdout lines).
//
// SQL has no stdout, so grading is structured result-set comparison. The
// RuntimeAdapter's `runTests({ code, tests })` keeps `tests` as a plain string
// (the shared interface is unchanged); for SQL that string is JSON in the shape
// below. S2 formalizes this as the on-disk `tests.json` contract + the Node
// `scripts/sql/grade_check.mjs` mirror; the comparison logic in `sql.worker.ts`
// and that grader must stay identical ("passes grade_check" ⟺ "passes in the
// browser"), exactly like the Python/C `__T__` invariant.
// ---------------------------------------------------------------------------

export interface SqlExpectedResultSet {
  columns: string[];
  rows: unknown[][];
}

export interface SqlTestCase {
  /** Shown to the learner (test source stays hidden). */
  name: string;
  /**
   * ORDER BY exercises set this `true` (rows compared in order); membership
   * exercises leave it `false`/absent (rows compared as a multiset). Default: false.
   */
  orderMatters?: boolean;
  /** Compare column *names* case-insensitively (lenient on aliases). Default: false. */
  caseLenientColumns?: boolean;
  /**
   * Optional per-case fixture variation, run *after* `schema` and *before* the
   * learner's SQL — e.g. INSERT a fresh row so a "generalizes to a new hire" case
   * proves the answer isn't hardcoded to the seed data. Mirrors the schema → setup →
   * query order in scripts/sql/grade_check.mjs (keep the two in lock-step). Absent
   * for the base case.
   */
  setup?: string;
  /**
   * Optional probe query run *after* the learner's SQL, against the same DB — for
   * INSERT/UPDATE/DELETE/DDL exercises whose "output" is the post-mutation state of
   * a table. When present, its result set (not the learner's) is compared to
   * `expected`. When absent, the learner statement's own last result set is compared.
   */
  probe?: string;
  expected: SqlExpectedResultSet;
}

export interface SqlTestsPayload {
  /**
   * Fixture SQL seeded into each case's fresh in-memory DB *before* the learner's
   * SQL runs. Optional: S1's self-contained seed exercises put the fixture in the
   * editor itself, so they omit this; the S2/S3 `schema.sql` bundle sets it so the
   * editor can be query-only. Each case re-seeds from scratch, so cases never leak.
   */
  schema?: string;
  cases: SqlTestCase[];
}

// ---------------------------------------------------------------------------
// Worker message protocol
// ---------------------------------------------------------------------------

export type WorkerInbound =
  | { type: "load" }
  | { type: "run"; code: string }
  | { type: "runTests"; code: string; tests: string };

export type WorkerOutbound =
  | { type: "loadProgress"; message: string }
  | { type: "loaded" }
  | { type: "loadError"; message: string }
  | { type: "runResult"; ok: boolean; error?: RuntimeError; resultSets?: QueryResultSet[] }
  | { type: "testResult"; results: TestCaseResult[]; allPassed: boolean; error?: RuntimeError };
