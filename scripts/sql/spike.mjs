// SQL S0 spike — prove sql.js end-to-end headlessly in Node.
// Mirrors the C0 spike: load engine -> seed -> run -> read {columns, rows} ->
// diff against expected -> multi-statement -> INSERT/UPDATE round-trips ->
// isolation -> error surface -> size/latency numbers.
//
// Run: node spike.mjs
// Exits non-zero if any assertion fails (so re-run == reproducibility check).

import { createRequire } from "node:module";
import { performance } from "node:perf_hooks";
import { readFileSync, statSync } from "node:fs";
import { gzipSync } from "node:zlib";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const initSqlJs = require("sql.js");
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// sql.js blocks package.json subpath access via "exports", so derive the wasm
// path from the resolved loader (dist/sql-wasm.js) instead.
const LOADER_PATH = require.resolve("sql.js");
const DIST_DIR = path.dirname(LOADER_PATH);
const WASM_PATH = path.join(DIST_DIR, "sql-wasm.wasm");

// ---------------------------------------------------------------------------
// tiny assert harness
// ---------------------------------------------------------------------------
let pass = 0;
let fail = 0;
const failures = [];
function check(name, cond, detail = "") {
  if (cond) {
    pass++;
    console.log(`  PASS  ${name}`);
  } else {
    fail++;
    failures.push(name + (detail ? ` — ${detail}` : ""));
    console.log(`  FAIL  ${name}${detail ? ` — ${detail}` : ""}`);
  }
}
function section(t) {
  console.log(`\n=== ${t} ===`);
}

// ---------------------------------------------------------------------------
// result-set normalization + comparison (the future grade_check diff logic)
// ---------------------------------------------------------------------------
// sql.js exec() returns [{ columns:[...], values:[[...]] }, ...] — one entry per
// statement that returns rows. Normalize to the plan's { columns, rows } shape.
function toResultSet(execEntry) {
  if (!execEntry) return { columns: [], rows: [] };
  return { columns: execEntry.columns, rows: execEntry.values };
}

function colsEqual(a, b, { caseLenient = false } = {}) {
  if (a.length !== b.length) return false;
  const norm = (s) => (caseLenient ? String(s).toLowerCase() : String(s));
  return a.every((c, i) => norm(c) === norm(b[i]));
}

// Compare two result sets. orderMatters=true => ordered deep-equal on rows.
// orderMatters=false => multiset (set) equality on rows.
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

// ---------------------------------------------------------------------------
// fixture (the S3 exercise-bundle "schema.sql" analogue)
// ---------------------------------------------------------------------------
const SCHEMA_SQL = `
CREATE TABLE products (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL UNIQUE,
  price INTEGER NOT NULL,
  category TEXT
);
INSERT INTO products (id, name, price, category) VALUES
  (1, 'Lamp',  40,  'home'),
  (2, 'Chair', 95,  'home'),
  (3, 'Desk',  210, 'home'),
  (4, 'Pen',   3,   'office'),
  (5, 'Mug',   12,  'office');
`;

function freshDb(SQL) {
  const db = new SQL.Database();
  db.run(SCHEMA_SQL); // seed: runs before the "learner" SQL, re-seeded per case
  return db;
}

// ===========================================================================
async function main() {
  console.log("SQL S0 spike — sql.js headless proof");
  console.log(`node ${process.version}`);
  console.log(`sql.js loader: ${LOADER_PATH}`);

  // -- Section 1: load WASM (cold-load timing + asset size) -----------------
  section("1. Load WASM engine (cold-load)");
  const wasmBytes = readFileSync(WASM_PATH);
  const wasmRaw = wasmBytes.length;
  const wasmGz = gzipSync(wasmBytes).length;
  const loaderRaw = statSync(LOADER_PATH).size;
  const loaderGz = gzipSync(readFileSync(LOADER_PATH)).length;

  const tLoad0 = performance.now();
  const SQL = await initSqlJs({ locateFile: () => WASM_PATH });
  const tLoad1 = performance.now();
  const coldLoadMs = tLoad1 - tLoad0;
  check("initSqlJs resolved (engine loaded)", typeof SQL?.Database === "function");
  console.log(`  sql-wasm.wasm : ${wasmRaw} B raw  /  ${wasmGz} B gzip`);
  console.log(`  sql-wasm.js   : ${loaderRaw} B raw  /  ${loaderGz} B gzip`);
  console.log(`  cold init     : ${coldLoadMs.toFixed(1)} ms (wasm compile + instantiate)`);

  // -- Section 2: seed schema, run a query, read {columns, rows}, diff ------
  section("2. Seed schema -> query -> read {columns, rows} -> diff");
  let db = freshDb(SQL);
  const q1 = "SELECT name, price FROM products ORDER BY price DESC LIMIT 3;";
  const rs1 = toResultSet(db.exec(q1)[0]);
  console.log(`  columns: ${JSON.stringify(rs1.columns)}`);
  console.log(`  rows   : ${JSON.stringify(rs1.rows)}`);
  const expected1 = {
    columns: ["name", "price"],
    rows: [["Desk", 210], ["Chair", 95], ["Lamp", 40]],
  };
  check("read back correct {columns, rows}", resultSetsEqual(rs1, expected1, { orderMatters: true }));

  // discriminator: a wrong expected must be rejected by the same diff
  const wrongExpected = { columns: ["name", "price"], rows: [["Desk", 210], ["Lamp", 40], ["Chair", 95]] };
  check("diff REJECTS a wrong result set (discriminator)",
    resultSetsEqual(rs1, wrongExpected, { orderMatters: true }) === false);

  // -- Section 3: ordered vs set comparison --------------------------------
  section("3. orderMatters: ordered vs set comparison");
  const rsUnordered = toResultSet(db.exec("SELECT name FROM products WHERE category='office';")[0]);
  const expOfficeSet = { columns: ["name"], rows: [["Mug"], ["Pen"]] }; // different order
  check("set comparison ignores row order (orderMatters=false)",
    resultSetsEqual(rsUnordered, expOfficeSet, { orderMatters: false }));
  check("ordered comparison catches wrong order (orderMatters=true)",
    resultSetsEqual(rsUnordered, expOfficeSet, { orderMatters: true }) === false);

  // -- Section 4: multi-statement scripts ----------------------------------
  section("4. Multi-statement scripts");
  // 4a: one exec() with several SELECTs => several result sets (resultSets[])
  const multi = db.exec("SELECT COUNT(*) AS n FROM products; SELECT MAX(price) AS top FROM products;");
  check("exec() returns one result set per returning statement", multi.length === 2,
    `got ${multi.length}`);
  check("multi-stmt result set #1 correct", resultSetsEqual(toResultSet(multi[0]), { columns: ["n"], rows: [[5]] }));
  check("multi-stmt result set #2 correct", resultSetsEqual(toResultSet(multi[1]), { columns: ["top"], rows: [[210]] }));

  // 4b: a DDL+DML script in a single run() call, then read it back
  const db2 = new SQL.Database();
  db2.run(`
    CREATE TABLE t (k TEXT, v INTEGER);
    INSERT INTO t VALUES ('a', 1);
    INSERT INTO t VALUES ('b', 2);
    INSERT INTO t VALUES ('c', 3);
  `);
  const sum = toResultSet(db2.exec("SELECT SUM(v) AS s FROM t;")[0]);
  check("multi-stmt CREATE+INSERT script persisted", resultSetsEqual(sum, { columns: ["s"], rows: [[6]] }));
  db2.close();

  // -- Section 5: INSERT / UPDATE / DELETE round-trips (probe pattern) ------
  section("5. DML round-trips via post-mutation probe (+ rows-affected summary)");
  // UPDATE
  db.run("UPDATE products SET price = price * 2 WHERE name = 'Lamp';");
  const updAffected = db.getRowsModified();
  const lampPrice = toResultSet(db.exec("SELECT price FROM products WHERE name='Lamp';")[0]);
  check("UPDATE rows-affected = 1", updAffected === 1, `got ${updAffected}`);
  check("UPDATE visible via probe (40 -> 80)", resultSetsEqual(lampPrice, { columns: ["price"], rows: [[80]] }));

  // INSERT
  db.run("INSERT INTO products (id, name, price, category) VALUES (6, 'Rug', 150, 'home');");
  const insAffected = db.getRowsModified();
  const cnt = toResultSet(db.exec("SELECT COUNT(*) AS n FROM products;")[0]);
  check("INSERT rows-affected = 1", insAffected === 1, `got ${insAffected}`);
  check("INSERT visible via probe (5 -> 6 rows)", resultSetsEqual(cnt, { columns: ["n"], rows: [[6]] }));

  // DELETE
  db.run("DELETE FROM products WHERE category = 'office';");
  const delAffected = db.getRowsModified();
  const cnt2 = toResultSet(db.exec("SELECT COUNT(*) AS n FROM products;")[0]);
  check("DELETE rows-affected = 2", delAffected === 2, `got ${delAffected}`);
  check("DELETE visible via probe (6 -> 4 rows)", resultSetsEqual(cnt2, { columns: ["n"], rows: [[4]] }));

  // -- Section 6: per-case isolation (fresh re-seeded DB) -------------------
  section("6. Per-case isolation (mutations do not leak between DBs)");
  const dbA = freshDb(SQL);
  dbA.run("DELETE FROM products;"); // nuke everything in A
  const dbB = freshDb(SQL); // fresh seed
  const bCount = toResultSet(dbB.exec("SELECT COUNT(*) AS n FROM products;")[0]);
  check("fresh DB unaffected by another DB's mutations", resultSetsEqual(bCount, { columns: ["n"], rows: [[5]] }));
  dbA.close();
  dbB.close();

  // -- Section 7: error surface (feeds errorExplainer) ---------------------
  section("7. Error surface (messages sql.js throws -> errorExplainer inputs)");
  const errDb = freshDb(SQL);
  const errorCases = [
    ["no such table", "SELECT * FROM nope;"],
    ["no such column", "SELECT nope FROM products;"],
    ["syntax error", "SELEKT * FROM products;"],
    ["UNIQUE constraint", "INSERT INTO products (id, name, price) VALUES (99, 'Lamp', 1);"],
    ["NOT NULL constraint", "INSERT INTO products (id, name, price) VALUES (98, NULL, 1);"],
  ];
  for (const [label, sql] of errorCases) {
    let msg = null;
    try { errDb.run(sql); } catch (e) { msg = e.message; }
    check(`throws on: ${label}`, msg !== null, "no error thrown");
    if (msg) console.log(`     -> "${msg}"`);
  }
  errDb.close();

  // -- Section 8: warm-run latency -----------------------------------------
  section("8. Warm-run latency");
  const warmDb = freshDb(SQL);
  const N = 2000;
  const tW0 = performance.now();
  for (let i = 0; i < N; i++) {
    const r = warmDb.exec("SELECT name, price FROM products WHERE price > 10 ORDER BY price DESC;");
    void r;
  }
  const tW1 = performance.now();
  const perQuery = (tW1 - tW0) / N;
  console.log(`  ${N} queries in ${(tW1 - tW0).toFixed(1)} ms  =>  ${perQuery.toFixed(4)} ms/query`);

  // per-test-case setup cost = new Database() + re-seed schema (isolation cost)
  const M = 500;
  const tS0 = performance.now();
  for (let i = 0; i < M; i++) {
    const d = new SQL.Database();
    d.run(SCHEMA_SQL);
    d.close();
  }
  const tS1 = performance.now();
  const perSeed = (tS1 - tS0) / M;
  console.log(`  ${M} fresh-DB + re-seed cycles in ${(tS1 - tS0).toFixed(1)} ms  =>  ${perSeed.toFixed(4)} ms/case`);
  warmDb.close();
  db.close();

  // -- summary --------------------------------------------------------------
  section("SUMMARY");
  console.log(`  asserts: ${pass} passed, ${fail} failed`);
  console.log("  --- numbers for the report ---");
  console.log(`  sqljs_version       : 1.14.1`);
  console.log(`  wasm_raw_bytes      : ${wasmRaw}`);
  console.log(`  wasm_gzip_bytes     : ${wasmGz}`);
  console.log(`  loader_raw_bytes    : ${loaderRaw}`);
  console.log(`  loader_gzip_bytes   : ${loaderGz}`);
  console.log(`  coldload_raw_bytes  : ${wasmRaw + loaderRaw}`);
  console.log(`  coldload_gzip_bytes : ${wasmGz + loaderGz}`);
  console.log(`  cold_init_ms        : ${coldLoadMs.toFixed(1)}`);
  console.log(`  warm_ms_per_query   : ${perQuery.toFixed(4)}`);
  console.log(`  reseed_ms_per_case  : ${perSeed.toFixed(4)}`);

  if (fail > 0) {
    console.log("\nFAILURES:");
    for (const f of failures) console.log(`  - ${f}`);
    console.log("\nRESULT: FAIL");
    process.exit(1);
  }
  console.log("\nRESULT: OK — sql.js pipeline validated end to end");
}

main().catch((e) => {
  console.error("SPIKE CRASHED:", e);
  process.exit(2);
});
