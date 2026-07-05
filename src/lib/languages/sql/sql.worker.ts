/**
 * SQL runtime Web Worker — S1 (engine = sql.js / SQLite-WASM).
 *
 * Loads sql.js from the jsDelivr CDN (the loader glue via `importScripts`, then the
 * `.wasm` via the loader's `locateFile` hook), instantiates a fresh in-memory
 * SQLite database per operation, executes the learner's SQL, and returns result
 * sets. The SQL analogue of `python/pyodide.worker.ts` / `c/c.worker.ts`, but much
 * simpler: SQL has **no stdout/stdin and no SharedArrayBuffer** — a program's
 * output is a table (or a rows-affected summary), handed back as `resultSets`.
 *
 * jsDelivr serves `access-control-allow-origin: *` + `cross-origin-resource-policy:
 * cross-origin`, so `importScripts` + the wasm fetch load cleanly under our COEP
 * `require-corp` policy (the same path Pyodide + Monaco already use).
 *
 * The worker is loosely typed at the boundary on purpose (sql.js has no bundled
 * types and mixing the "webworker" lib with "dom" causes global type conflicts):
 * the worker scope is `any`, with strong types kept on the message payloads.
 *
 * Grading (runTests) compares result sets, mirroring the S0 spike's proven diff
 * (docs/sql0-spike-report.md). S2 will lift the same comparator into
 * `scripts/sql/grade_check.mjs` so "passes grade_check" ⟺ "passes in the browser".
 */

import {
  SQLJS_CDN_BASE,
  SQLJS_LOADER_FILE,
} from "@/lib/languages/sql/runtimeProtocol";
import type {
  SqlTestCase,
  SqlTestsPayload,
  WorkerInbound,
  WorkerOutbound,
} from "@/lib/languages/sql/runtimeProtocol";
import type { QueryResultSet, RuntimeError, TestCaseResult } from "@/lib/languages/types";

const ctx: any = self;

function post(message: WorkerOutbound): void {
  ctx.postMessage(message);
}

// sql.js `SQL` namespace (from initSqlJs). Cached after the first load.
let SQL: any = null;
let loadPromise: Promise<void> | null = null;

async function ensureLoaded(): Promise<void> {
  if (SQL) return;
  if (!loadPromise) {
    loadPromise = (async () => {
      post({ type: "loadProgress", message: "Loading the SQL engine (one-time)…" });
      // UMD loader attaches `self.initSqlJs`. Runtime-concatenated URL, so the
      // bundler leaves this importScripts alone (same idiom as the Pyodide worker).
      ctx.importScripts(SQLJS_CDN_BASE + SQLJS_LOADER_FILE);
      if (typeof ctx.initSqlJs !== "function") {
        throw new Error("Could not load the SQL engine (initSqlJs missing).");
      }
      SQL = await ctx.initSqlJs({ locateFile: (file: string) => SQLJS_CDN_BASE + file });
    })();
  }
  await loadPromise;
}

// ---------------------------------------------------------------------------
// Result-set mapping + error classification
// ---------------------------------------------------------------------------

/** Map a sql.js exec() entry ({ columns, values }) to the interface's QueryResultSet. */
function toResultSet(entry: any): QueryResultSet {
  if (!entry) return { columns: [], rows: [] };
  return {
    columns: (entry.columns ?? []) as string[],
    rows: (entry.values ?? []) as unknown[][],
  };
}

/**
 * Run a full SQL script and collect every result set it produces. When the script
 * returns no rows (pure DDL/DML), synthesize a single summary entry so the grid
 * still shows feedback ("N rows affected").
 */
function execToResultSets(db: any, code: string): QueryResultSet[] {
  const raw = db.exec(code) as any[];
  const sets = raw.map(toResultSet);
  if (sets.length === 0) {
    const modified = db.getRowsModified();
    const summary =
      modified > 0
        ? `${modified} row${modified === 1 ? "" : "s"} affected.`
        : "Statement executed successfully.";
    sets.push({ columns: [], rows: [], summary });
  }
  return sets;
}

/** Turn a thrown SQLite error into a stable RuntimeError type the errorExplainer knows. */
function classify(exn: any): RuntimeError {
  const message = String(exn?.message ?? exn ?? "Database error").trim();
  const lower = message.toLowerCase();
  let type = ""; // unknown ⇒ ErrorCallout shows a generic title + this raw message
  if (lower.includes("no such table")) type = "NoSuchTable";
  else if (lower.includes("no such column")) type = "NoSuchColumn";
  else if (lower.includes("syntax error")) type = "SyntaxError";
  else if (lower.includes("unique constraint")) type = "UniqueConstraint";
  else if (lower.includes("not null constraint")) type = "NotNullConstraint";
  else if (lower.includes("foreign key constraint")) type = "ForeignKeyConstraint";
  else if (lower.includes("check constraint")) type = "CheckConstraint";
  else if (lower.includes("datatype mismatch")) type = "DatatypeMismatch";
  return { type, message, traceback: message };
}

// ---------------------------------------------------------------------------
// Run
// ---------------------------------------------------------------------------

function handleRun(code: string): void {
  let db: any = null;
  try {
    db = new SQL.Database();
    let sets: QueryResultSet[];
    try {
      sets = execToResultSets(db, code);
    } catch (exn) {
      post({ type: "runResult", ok: false, error: classify(exn) });
      return;
    }
    post({ type: "runResult", ok: true, resultSets: sets });
  } catch (exn: any) {
    post({
      type: "runResult",
      ok: false,
      error: { type: "", message: String(exn?.message ?? exn), traceback: "" },
    });
  } finally {
    db?.close();
  }
}

// ---------------------------------------------------------------------------
// Result-set comparison (the grader's diff — S2's grade_check.mjs mirrors this)
// ---------------------------------------------------------------------------

function normColumns(cols: string[], lenient: boolean): string[] {
  return cols.map((c) => (lenient ? String(c).toLowerCase() : String(c)));
}

function fmtCols(cols: string[]): string {
  return `[${cols.join(", ")}]`;
}

interface CompareOpts {
  orderMatters: boolean;
  caseLenient: boolean;
}

/** Compare two result sets; return whether they match and a learner-friendly reason if not. */
function compareResultSets(
  got: QueryResultSet,
  expected: QueryResultSet,
  opts: CompareOpts,
): { equal: boolean; reason?: string } {
  const gCols = normColumns(got.columns, opts.caseLenient);
  const eCols = normColumns(expected.columns, opts.caseLenient);
  if (gCols.length !== eCols.length || !gCols.every((c, i) => c === eCols[i])) {
    return {
      equal: false,
      reason: `Expected columns ${fmtCols(expected.columns)} but got ${fmtCols(got.columns)}.`,
    };
  }
  if (got.rows.length !== expected.rows.length) {
    return {
      equal: false,
      reason: `Expected ${expected.rows.length} row${
        expected.rows.length === 1 ? "" : "s"
      } but your query returned ${got.rows.length}.`,
    };
  }
  const ser = (r: unknown[]) => JSON.stringify(r);
  if (opts.orderMatters) {
    const ok = got.rows.every((r, i) => ser(r) === ser(expected.rows[i] ?? []));
    if (ok) return { equal: true };
    // Only claim it's an ordering issue if the same rows are present as a set —
    // otherwise the row values themselves are wrong, and that message would mislead.
    const a = got.rows.map(ser).sort();
    const b = expected.rows.map(ser).sort();
    const sameSet = a.every((v, i) => v === b[i]);
    return {
      equal: false,
      reason: sameSet
        ? "The right rows are there, but not in the order the question asks for."
        : "Your rows didn't match the expected results.",
    };
  }
  const a = got.rows.map(ser).sort();
  const b = expected.rows.map(ser).sort();
  const ok = a.every((v, i) => v === b[i]);
  return ok ? { equal: true } : { equal: false, reason: "Your rows didn't match the expected results." };
}

// ---------------------------------------------------------------------------
// Submit / grade
// ---------------------------------------------------------------------------

function runCase(code: string, schema: string | undefined, tc: SqlTestCase): TestCaseResult {
  let db: any = null;
  try {
    db = new SQL.Database();

    // The editor `code` is the fixture schema prepended to the learner's query
    // (loader: `${schema}\n\n${query}`). Peel the schema prefix off and seed it
    // explicitly, so a per-case `setup` can run BETWEEN the schema and the query —
    // i.e. schema → setup → query, the exact order scripts/sql/grade_check.mjs uses
    // ("passes grade_check" ⟺ "passes Submit"). Each case gets a fresh DB, so the
    // re-seed + per-case setup never leak between cases.
    let query = code;
    if (schema && schema.trim()) {
      const idx = code.indexOf(schema);
      if (idx >= 0) query = code.slice(idx + schema.length); // strip the fixture prefix
      db.run(schema); // re-seed a fresh fixture per case
    }
    if (tc.setup && tc.setup.trim()) db.run(tc.setup); // per-case fixture variation

    let got: QueryResultSet;
    try {
      const learnerSets = db.exec(query) as any[];
      if (tc.probe && tc.probe.trim()) {
        // DML/DDL exercise: compare the post-mutation state a probe query observes.
        const probeSets = db.exec(tc.probe) as any[];
        got = probeSets.length ? toResultSet(probeSets[probeSets.length - 1]) : { columns: [], rows: [] };
      } else {
        // Query exercise: compare the learner's last returned result set.
        got = learnerSets.length ? toResultSet(learnerSets[learnerSets.length - 1]) : { columns: [], rows: [] };
      }
    } catch (exn) {
      // The learner's SQL itself errored — surface SQLite's message for this case.
      return { name: tc.name, passed: false, message: classify(exn).message };
    }

    const expected: QueryResultSet = { columns: tc.expected.columns, rows: tc.expected.rows };
    const cmp = compareResultSets(got, expected, {
      orderMatters: tc.orderMatters ?? false,
      caseLenient: tc.caseLenientColumns ?? false,
    });
    return cmp.equal
      ? { name: tc.name, passed: true }
      : { name: tc.name, passed: false, message: cmp.reason };
  } catch (exn: any) {
    return { name: tc.name, passed: false, message: String(exn?.message ?? exn) };
  } finally {
    db?.close();
  }
}

function handleRunTests(code: string, testsRaw: string): void {
  let payload: SqlTestsPayload;
  try {
    payload = JSON.parse(testsRaw) as SqlTestsPayload;
  } catch {
    post({
      type: "testResult",
      results: [],
      allPassed: false,
      error: { type: "", message: "Could not read this exercise's test definition (invalid JSON).", traceback: "" },
    });
    return;
  }
  const cases = Array.isArray(payload?.cases) ? payload.cases : [];
  if (cases.length === 0) {
    post({
      type: "testResult",
      results: [],
      allPassed: false,
      error: { type: "", message: "This exercise has no test cases.", traceback: "" },
    });
    return;
  }
  const results = cases.map((tc) => runCase(code, payload.schema, tc));
  post({ type: "testResult", results, allPassed: results.every((r) => r.passed) });
}

// ---------------------------------------------------------------------------
// Message loop
// ---------------------------------------------------------------------------

ctx.onmessage = async (event: MessageEvent<WorkerInbound>) => {
  const msg = event.data;
  switch (msg.type) {
    case "load":
      try {
        await ensureLoaded();
        post({ type: "loaded" });
      } catch (error) {
        post({ type: "loadError", message: String((error as Error)?.message ?? error) });
      }
      break;
    case "run":
      try {
        await ensureLoaded();
      } catch (error) {
        post({
          type: "runResult",
          ok: false,
          error: { type: "", message: String((error as Error)?.message ?? error), traceback: "" },
        });
        break;
      }
      handleRun(msg.code);
      break;
    case "runTests":
      try {
        await ensureLoaded();
      } catch (error) {
        post({
          type: "testResult",
          results: [],
          allPassed: false,
          error: { type: "", message: String((error as Error)?.message ?? error), traceback: "" },
        });
        break;
      }
      handleRunTests(msg.code, msg.tests);
      break;
  }
};

export {};
