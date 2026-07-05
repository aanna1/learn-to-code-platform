#!/usr/bin/env node
/*
 * Headless grader-discrimination check for Track-2 "structured" (modeling)
 * exercises — the non-query format used by Modules 03–04, Checkpoint A, and the
 * Capstone design stage. See docs/sql-test-harness-contract.md (Track-2 section).
 *
 * Usage:
 *     node grade_check_structured.mjs [<exercise-dir>] [--verbose]
 *
 * <exercise-dir> defaults to the co-located ./example-structured. It must contain:
 *
 *     question.json   the interactive field spec (StructuredQuestion)
 *     answer.json     canonical answer, keyed by field id  — must PASS every field
 *     wrong.json      optional authored wrong answer        — must FAIL >= 1 field
 *
 * LOCK-STEP INVARIANT ("passes grade_check" <=> "passes Submit in the browser").
 * The comparator functions below are a VERBATIM PORT of src/lib/structured/grade.ts,
 * which is what <StructuredExercise> runs in the browser. Grading is pure — no
 * sql.js, no worker, no network. If you edit a comparator in grade.ts, edit it here
 * too and re-run this script. grade.ts is the source of truth.
 *
 * Exit 0 only if the canonical answer passes every field AND (no wrong.json OR the
 * wrong answer fails >= 1 field). Anything else exits non-zero — fix before shipping.
 */

import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ===========================================================================
// PORT OF src/lib/structured/grade.ts  (keep byte-for-byte equivalent)
// ===========================================================================

function norm(s) {
  return String(s ?? "").trim().toLowerCase().replace(/\s+/g, " ");
}

function setEqual(a, b) {
  if (a.length !== b.length) return false;
  const sa = [...a].sort();
  const sb = [...b].sort();
  return sa.every((v, i) => v === sb[i]);
}

function uniq(xs) {
  return [...new Set(xs)];
}

function canonMulti(value) {
  if (!Array.isArray(value)) return [];
  return uniq(value.map(norm).filter((s) => s.length > 0));
}

function canonFdLine(line) {
  const parts = line.split(/->|→/);
  if (parts.length < 2) return [];
  const lhs = uniq((parts[0] ?? "").split(",").map(norm).filter((s) => s.length > 0)).sort();
  if (lhs.length === 0) return [];
  const lhsKey = lhs.join("+");
  const rhs = (parts[1] ?? "").split(",").map(norm).filter((s) => s.length > 0);
  return rhs.map((r) => `${lhsKey}>${r}`);
}

function canonTokenSet(value, grammar) {
  if (!Array.isArray(value)) return [];
  const lines = value.map((v) => String(v ?? ""));
  if (grammar === "fd") return uniq(lines.flatMap(canonFdLine));
  return uniq(lines.map(norm).filter((s) => s.length > 0));
}

function canonPartition(value, matchLabels) {
  if (!value || typeof value !== "object") return [];
  const groups = [];
  for (const [label, items] of Object.entries(value)) {
    if (!Array.isArray(items)) continue;
    const members = uniq(items.map(norm).filter((s) => s.length > 0)).sort();
    if (members.length === 0) continue;
    groups.push(matchLabels ? `${norm(label)}::${members.join(",")}` : members.join(","));
  }
  return groups.sort();
}

function normCardinality(c) {
  const s = norm(c).replace(/[\s_-]/g, "");
  if (["1:1", "11", "onetoone", "oneone"].includes(s)) return "1:1";
  if (["n:m", "m:n", "n:n", "m:m", "manytomany", "nm", "mn"].includes(s)) return "n:n";
  if (["1:n", "n:1", "1:m", "m:1", "onetomany", "manytoone", "1n", "n1", "1m", "m1"].includes(s)) {
    return "1:n";
  }
  return s.replace("m", "n");
}

function reverseCardinality(c) {
  if (c === "1:n") return "n:1";
  if (c === "n:1") return "1:n";
  return c;
}

function canonEntity(e) {
  if (!e || typeof e !== "object") return "";
  const attrs = Array.isArray(e.attributes) ? e.attributes : [];
  const attrSig = uniq(
    attrs
      .map((a) => {
        const at = a ?? {};
        return `${norm(at.name)}${at.pk ? "*" : ""}`;
      })
      .filter((s) => s.replace("*", "").length > 0),
  ).sort();
  return `${norm(e.name)}|${attrSig.join(",")}`;
}

function canonRelationship(r) {
  if (!r || typeof r !== "object") return "";
  let a = norm(r.from);
  let b = norm(r.to);
  let card = normCardinality(r.cardinality);
  if (a > b) {
    [a, b] = [b, a];
    card = reverseCardinality(card);
  }
  return `${a}~${b}|${card}|${r.identifying ? "1" : "0"}`;
}

function canonErd(value) {
  const v = value ?? {};
  const entities = uniq((Array.isArray(v.entities) ? v.entities : []).map(canonEntity).filter(Boolean)).sort();
  const relationships = uniq(
    (Array.isArray(v.relationships) ? v.relationships : []).map(canonRelationship).filter(Boolean),
  ).sort();
  return { entities, relationships };
}

function gradeField(field, submitted, expected) {
  switch (field.type) {
    case "single-select":
      return norm(submitted) === norm(expected) && norm(expected).length > 0;
    case "multi-select":
      return setEqual(canonMulti(submitted), canonMulti(expected));
    case "token-set":
      return setEqual(canonTokenSet(submitted, field.grammar), canonTokenSet(expected, field.grammar));
    case "matching": {
      const exp = expected ?? {};
      const sub = submitted ?? {};
      const keys = Object.keys(exp);
      if (keys.length === 0) return false;
      return keys.every((k) => norm(sub[k]) === norm(exp[k]) && norm(exp[k]).length > 0);
    }
    case "partition":
      return setEqual(
        canonPartition(submitted, field.matchLabels === true),
        canonPartition(expected, field.matchLabels === true),
      );
    case "erd-spec": {
      const s = canonErd(submitted);
      const e = canonErd(expected);
      return setEqual(s.entities, e.entities) && setEqual(s.relationships, e.relationships);
    }
    default:
      return false;
  }
}

function gradeStructured(question, canonical, submitted) {
  const results = question.fields.map((field) => ({
    name: field.label,
    passed: gradeField(field, submitted[field.id], canonical[field.id]),
  }));
  return { results, allPassed: results.length > 0 && results.every((r) => r.passed) };
}

// ===========================================================================
// CLI
// ===========================================================================

function readJson(p) {
  return JSON.parse(readFileSync(p, "utf8"));
}

function report(title, res, verbose) {
  console.log(`\n=== ${title} ===`);
  for (const r of res.results) {
    console.log(`  [${r.passed ? "PASS" : "FAIL"}] ${r.name}`);
  }
  const n = res.results.filter((r) => r.passed).length;
  console.log(`  (${n}/${res.results.length} passed)`);
  if (verbose) console.log(`  allPassed=${res.allPassed}`);
}

function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose");
  const positional = args.filter((a) => !a.startsWith("--"));
  const dir = path.resolve(positional[0] || path.join(__dirname, "example-structured"));

  const questionPath = path.join(dir, "question.json");
  const answerPath = path.join(dir, "answer.json");
  const wrongPath = path.join(dir, "wrong.json");

  for (const [label, p] of [["question.json", questionPath], ["answer.json", answerPath]]) {
    if (!existsSync(p)) {
      console.error(`ERROR: required file ${label} not found in ${dir}`);
      process.exit(2);
    }
  }

  const question = readJson(questionPath);
  const answer = readJson(answerPath);
  if (!question || !Array.isArray(question.fields) || question.fields.length === 0) {
    console.error("ERROR: question.json must have a non-empty `fields` array");
    process.exit(2);
  }

  console.log(`structured grade_check — ${path.relative(process.cwd(), dir) || dir}`);
  console.log(`node ${process.version} · ${question.fields.length} field(s)`);

  const canon = gradeStructured(question, answer, answer);
  report("CANONICAL (expect: all pass)", canon, verbose);
  const canonOk = canon.allPassed;

  let wrongOk = true;
  if (existsSync(wrongPath)) {
    const wrong = readJson(wrongPath);
    const wr = gradeStructured(question, answer, wrong);
    report("WRONG ANSWER (expect: >= 1 fail)", wr, verbose);
    wrongOk = wr.results.some((r) => !r.passed);
  }

  console.log("\n--- summary ---");
  console.log(`  canonical passes all fields : ${canonOk}`);
  if (existsSync(wrongPath)) console.log(`  wrong answer fails >= 1     : ${wrongOk}`);
  const ok = canonOk && wrongOk;
  console.log(`  RESULT: ${ok ? "OK" : "PROBLEM - fix before shipping"}`);
  process.exit(ok ? 0 : 1);
}

main();
