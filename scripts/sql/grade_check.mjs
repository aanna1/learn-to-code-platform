#!/usr/bin/env node
/*
 * Headless grader-discrimination check for SQL (query-contract) exercises.
 *
 * Usage:
 *     node grade_check.mjs [<exercise-dir>] [--verbose]
 *
 * <exercise-dir> defaults to the co-located ./example. It must contain the
 * query-contract bundle locked in docs/sql-test-harness-contract.md:
 *
 *     schema.sql     fixture DDL + seed INSERTs, run before the learner's SQL
 *     tests.json     array of test cases (see the contract for the shape)
 *     solution.sql   reference answer  — must PASS every case
 *     starter.sql    what the learner starts from — must FAIL >= 1 case (optional)
 *
 * The SQL analogue of scripts/c/grade_check.py. It runs the submission against
 * every case and checks that the tests actually DISCRIMINATE: the solution must
 * pass all cases, and (if present) the starter must fail at least one. That is
 * what makes an exercise a real checkpoint rather than a rubber stamp.
 *
 * LOCK-STEP INVARIANT ("passes grade_check" <=> "passes Submit in the browser").
 * The seed/run/diff pipeline below is exactly what the in-browser worker
 * (src/lib/languages/sql/sql.worker.ts, phase S1) must run:
 *
 *   * Per case, build a FRESH in-memory SQLite DB and re-run schema.sql, so
 *     mutations never leak between cases and case order is irrelevant.
 *   * Run the case's optional `setup` SQL (per-case fixture variation), then the
 *     learner's SQL.
 *   * Compare a result set to the case's `expected` {columns, rows}. If the case
 *     has a `probe` query, run it AFTER the learner's SQL and compare ITS result
 *     set (the DML/DDL post-mutation pattern — INSERT/UPDATE/DELETE and
 *     PRAGMA/sqlite_master structural checks). Otherwise compare the learner
 *     SQL's own last returning result set (the plain SELECT case).
 *   * `orderMatters` toggles ordered vs. multiset row comparison per case;
 *     `caseLenient` makes column-name matching case-insensitive (aliases).
 *
 * The comparison helpers (toResultSet / colsEqual / resultSetsEqual) are the same
 * ones proven in scripts/sql/spike.mjs (S0). Keep sql.worker.ts diffing result
 * sets byte-for-byte the same way; the contract doc is the source of truth.
 *
 * This runs the exact same sql.js WASM binary the browser loads, so — unlike the
 * C grader's zig-cc proxy — there is no engine gap here; only the download and
 * COOP/COEP handshake are browser-only.
 *
 * Requires sql.js (pinned 1.14.1) resolvable from node_modules:
 *     npm install sql.js@1.14.1
 * (S1 adds sql.js as a project dependency for the runtime; until then install it
 * locally to run this grader.)
 *
 * Exit code 0 only if the solution passes all cases AND (no starter OR the
 * starter fails >= 1). Any other outcome exits non-zero — fix it before shipping.
 */

import { createRequire } from "node:module";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// sql.js blocks package.json subpath access via its "exports" map, so derive the
// wasm path from the resolved loader (dist/sql-wasm.js) — same trick as the spike.
let LOADER_PATH;
try {
  LOADER_PATH = require.resolve("sql.js");
} catch {
  console.error(
    "ERROR: sql.js is not installed. Run `npm install sql.js@1.14.1` " +
      "(S1 will add it as a project dependency)."
  );
  process.exit(2);
}
const WASM_PATH = path.join(path.dirname(LOADER_PATH), "sql-wasm.wasm");
const initSqlJs = require("sql.js");

// ---------------------------------------------------------------------------
// result-set normalization + comparison  (mirror of spike.mjs / sql.worker.ts)
// ---------------------------------------------------------------------------
// sql.js exec() returns [{ columns:[...], values:[[...]] }, ...] — one entry per
// statement that returns rows. Normalize to the contract's { columns, rows }.
function toResultSet(execEntry) {
  if (!execEntry) return { columns: [], rows: [] };
  return { columns: execEntry.columns, rows: execEntry.values };
}

function colsEqual(a, b, { caseLenient = false } = {}) {
  if (a.length !== b.length) return false;
  const norm = (s) => (caseLenient ? String(s).toLowerCase() : String(s));
  return a.every((c, i) => norm(c) === norm(b[i]));
}

// orderMatters=true  => ordered deep-equal on rows.
// orderMatters=false => multiset (set) equality on rows (row order ignored).
function resultSetsEqual(got, expected, { orderMatters = true, caseLenient = false } = {}) {
  if (!colsEqual(got.columns, expected.columns, { caseLenient })) return false;
  if (got.rows.length !== expected.rows.length) return false;
  const ser = (r) => JSON.stringify(r);
  if (orderMatters) {
    return got.rows.every((r, i) => ser(r) === ser(expected.rows[i]));
  }
  const a = got.rows.map(ser).sort();
  const b = expected.rows.map(ser).sort();
  return a.every((v, i) => v === b[i]);
}

// A compact human-readable diff for FAIL messages.
function describeMismatch(got, expected) {
  const g = `${got.rows.length} row(s), cols ${JSON.stringify(got.columns)}`;
  const e = `${expected.rows.length} row(s), cols ${JSON.stringify(expected.columns)}`;
  return `expected ${e} but got ${g}`;
}

// ---------------------------------------------------------------------------
// grading one case against one submission
// ---------------------------------------------------------------------------
function gradeCase(SQL, schemaSql, submissionSql, testCase) {
  const {
    name,
    setup,
    probe,
    expected,
    orderMatters = true,
    caseLenient = false,
  } = testCase;

  if (!expected || !Array.isArray(expected.columns) || !Array.isArray(expected.rows)) {
    return [name, false, `malformed test case: "expected" must have {columns, rows}`];
  }

  const db = new SQL.Database();
  try {
    // Fresh fixture for isolation.
    db.run(schemaSql);
    if (setup) db.run(setup);

    // The learner's SQL. May be a SELECT (returns a set) or a mutation/DDL
    // (returns nothing — then a `probe` supplies the set to compare).
    let learnerSets;
    try {
      learnerSets = db.exec(submissionSql);
    } catch (e) {
      return [name, false, `your SQL raised an error: ${e.message}`];
    }

    let gotEntry;
    if (probe) {
      let probeSets;
      try {
        probeSets = db.exec(probe);
      } catch (e) {
        return [name, false, `the check query failed to run after your SQL: ${e.message}`];
      }
      gotEntry = probeSets[probeSets.length - 1];
    } else {
      if (!learnerSets || learnerSets.length === 0) {
        return [name, false, `your SQL returned no result set (expected a query that returns rows)`];
      }
      gotEntry = learnerSets[learnerSets.length - 1];
    }

    const got = toResultSet(gotEntry);
    const exp = { columns: expected.columns, rows: expected.rows };
    const ok = resultSetsEqual(got, exp, { orderMatters, caseLenient });
    return [name, ok, ok ? "" : describeMismatch(got, exp)];
  } finally {
    db.close();
  }
}

function grade(SQL, schemaSql, submissionSql, tests) {
  return tests.map((tc) => gradeCase(SQL, schemaSql, submissionSql, tc));
}

// ---------------------------------------------------------------------------
// reporting  (mirror of grade_check.py's _report / main)
// ---------------------------------------------------------------------------
function report(title, results, verbose) {
  console.log(`\n=== ${title} ===`);
  for (const [label, passed, msg] of results) {
    console.log(`  [${passed ? "PASS" : "FAIL"}] ${label}`);
    if (!passed && msg) console.log(`         ${msg}`);
    else if (verbose && msg) console.log(`         ${msg}`);
  }
  const nPass = results.filter(([, p]) => p).length;
  console.log(`  (${nPass}/${results.length} passed)`);
}

function readIfExists(p) {
  return existsSync(p) ? readFileSync(p, "utf8") : null;
}

async function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose");
  const positional = args.filter((a) => !a.startsWith("--"));
  const exerciseDir = path.resolve(positional[0] || path.join(__dirname, "example"));

  const schemaPath = path.join(exerciseDir, "schema.sql");
  const testsPath = path.join(exerciseDir, "tests.json");
  const solutionPath = path.join(exerciseDir, "solution.sql");
  const starterPath = path.join(exerciseDir, "starter.sql");

  for (const [label, p] of [["schema.sql", schemaPath], ["tests.json", testsPath], ["solution.sql", solutionPath]]) {
    if (!existsSync(p)) {
      console.error(`ERROR: required file ${label} not found in ${exerciseDir}`);
      process.exit(2);
    }
  }

  const schemaSql = readFileSync(schemaPath, "utf8");
  const solutionSql = readFileSync(solutionPath, "utf8");
  const starterSql = readIfExists(starterPath);
  let tests;
  try {
    tests = JSON.parse(readFileSync(testsPath, "utf8"));
  } catch (e) {
    console.error(`ERROR: tests.json is not valid JSON: ${e.message}`);
    process.exit(2);
  }
  if (!Array.isArray(tests) || tests.length === 0) {
    console.error("ERROR: tests.json must be a non-empty array of test cases");
    process.exit(2);
  }

  console.log(`SQL grade_check — ${path.relative(process.cwd(), exerciseDir) || exerciseDir}`);
  console.log(`node ${process.version} · sql.js @ ${path.relative(process.cwd(), LOADER_PATH)}`);
  console.log(`${tests.length} test case(s)`);

  const SQL = await initSqlJs({ locateFile: () => WASM_PATH });

  const sol = grade(SQL, schemaSql, solutionSql, tests);
  report("SOLUTION (expect: all pass)", sol, verbose);
  const solOk = sol.length > 0 && sol.every(([, p]) => p);

  let starterOk = true;
  if (starterSql !== null) {
    const st = grade(SQL, schemaSql, starterSql, tests);
    report("STARTER (expect: >= 1 fail)", st, verbose);
    starterOk = st.some(([, p]) => !p);
  }

  console.log("\n--- summary ---");
  console.log(`  solution passes all cases : ${solOk}`);
  if (starterSql !== null) console.log(`  starter fails >= 1 case   : ${starterOk}`);
  const ok = solOk && starterOk;
  console.log(`  RESULT: ${ok ? "OK" : "PROBLEM - fix before checkpoint"}`);
  process.exit(ok ? 0 : 1);
}

main().catch((e) => {
  console.error("grade_check CRASHED:", e);
  process.exit(2);
});
