/**
 * Pure, deterministic grader for Track-2 "structured" exercises. No engine, no
 * worker, no network — just canonical-form comparison over the field values.
 *
 * LOCK-STEP INVARIANT: scripts/sql/grade_check_structured.mjs is a hand-kept
 * verbatim port of the functions below (same rule the SQL/C query graders follow
 * for their diff logic). If you change a comparator here, change it there too and
 * re-run the discriminator. docs/sql-test-harness-contract.md is the source of truth.
 */

import type { SubmitResult, TestCaseResult } from "@/lib/languages/types";
import type {
  ErdValue,
  StructuredAnswer,
  StructuredField,
  StructuredQuestion,
} from "@/lib/structured/types";

// ---------------------------------------------------------------------------
// primitives
// ---------------------------------------------------------------------------

/** Trim + case-fold + collapse internal whitespace — the identifier normalizer. */
function norm(s: unknown): string {
  return String(s ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

function setEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  const sa = [...a].sort();
  const sb = [...b].sort();
  return sa.every((v, i) => v === sb[i]);
}

function uniq(xs: string[]): string[] {
  return [...new Set(xs)];
}

// ---------------------------------------------------------------------------
// per-type canonicalizers → string[] (compared by setEqual) or a scalar
// ---------------------------------------------------------------------------

function canonMulti(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return uniq(value.map(norm).filter((s) => s.length > 0));
}

/** A functional dependency line "a, b -> c, d" → atoms ["a+b>c","a+b>d"]. */
function canonFdLine(line: string): string[] {
  const parts = line.split(/->|→/);
  if (parts.length < 2) return [];
  const lhs = uniq(
    (parts[0] ?? "")
      .split(",")
      .map(norm)
      .filter((s) => s.length > 0),
  ).sort();
  if (lhs.length === 0) return [];
  const lhsKey = lhs.join("+");
  const rhs = (parts[1] ?? "")
    .split(",")
    .map(norm)
    .filter((s) => s.length > 0);
  return rhs.map((r) => `${lhsKey}>${r}`);
}

function canonTokenSet(value: unknown, grammar: string | undefined): string[] {
  if (!Array.isArray(value)) return [];
  const lines = (value as unknown[]).map((v) => String(v ?? ""));
  if (grammar === "fd") {
    return uniq(lines.flatMap(canonFdLine));
  }
  return uniq(lines.map(norm).filter((s) => s.length > 0));
}

/** Partition → sorted list of group signatures (each group = sorted item set). */
function canonPartition(
  value: unknown,
  matchLabels: boolean,
): string[] {
  if (!value || typeof value !== "object") return [];
  const map = value as Record<string, unknown>;
  const groups: string[] = [];
  for (const [label, items] of Object.entries(map)) {
    if (!Array.isArray(items)) continue;
    const members = uniq(items.map(norm).filter((s) => s.length > 0)).sort();
    if (members.length === 0) continue;
    groups.push(matchLabels ? `${norm(label)}::${members.join(",")}` : members.join(","));
  }
  return groups.sort();
}

// ---- ERD canonicalization -------------------------------------------------

/** Normalize a cardinality token to one of: "1:1", "1:n", "n:n". */
function normCardinality(c: unknown): string {
  const s = norm(c).replace(/[\s_-]/g, "");
  if (["1:1", "11", "onetoone", "oneone"].includes(s)) return "1:1";
  if (["n:m", "m:n", "n:n", "m:m", "manytomany", "nm", "mn"].includes(s)) return "n:n";
  if (["1:n", "n:1", "1:m", "m:1", "onetomany", "manytoone", "1n", "n1", "1m", "m1"].includes(s)) {
    return "1:n";
  }
  // Fall back to a colon-normalized form so unknown-but-consistent tokens still compare.
  return s.replace("m", "n");
}

function reverseCardinality(c: string): string {
  if (c === "1:n") return "n:1";
  if (c === "n:1") return "1:n";
  return c; // symmetric (1:1, n:n)
}

function canonEntity(e: unknown): string {
  if (!e || typeof e !== "object") return "";
  const ent = e as { name?: unknown; attributes?: unknown };
  const attrs = Array.isArray(ent.attributes) ? ent.attributes : [];
  const attrSig = uniq(
    attrs.map((a) => {
      const at = (a ?? {}) as { name?: unknown; pk?: unknown };
      return `${norm(at.name)}${at.pk ? "*" : ""}`;
    }).filter((s) => s.replace("*", "").length > 0),
  ).sort();
  return `${norm(ent.name)}|${attrSig.join(",")}`;
}

function canonRelationship(r: unknown): string {
  if (!r || typeof r !== "object") return "";
  const rel = r as { from?: unknown; to?: unknown; cardinality?: unknown; identifying?: unknown };
  let a = norm(rel.from);
  let b = norm(rel.to);
  let card = normCardinality(rel.cardinality);
  // Order endpoints canonically; if we swap them, swap the cardinality direction too.
  if (a > b) {
    [a, b] = [b, a];
    card = reverseCardinality(card);
  }
  return `${a}~${b}|${card}|${rel.identifying ? "1" : "0"}`;
}

function canonErd(value: unknown): { entities: string[]; relationships: string[] } {
  const v = (value ?? {}) as Partial<ErdValue>;
  const entities = uniq((Array.isArray(v.entities) ? v.entities : []).map(canonEntity).filter(Boolean)).sort();
  const relationships = uniq(
    (Array.isArray(v.relationships) ? v.relationships : []).map(canonRelationship).filter(Boolean),
  ).sort();
  return { entities, relationships };
}

// ---------------------------------------------------------------------------
// grade one field
// ---------------------------------------------------------------------------

/** True ⇔ the learner's value for `field` matches the canonical `expected`. */
export function gradeField(
  field: StructuredField,
  submitted: unknown,
  expected: unknown,
): boolean {
  switch (field.type) {
    case "single-select":
      return norm(submitted) === norm(expected) && norm(expected).length > 0;

    case "multi-select":
      return setEqual(canonMulti(submitted), canonMulti(expected));

    case "token-set":
      return setEqual(
        canonTokenSet(submitted, field.grammar),
        canonTokenSet(expected, field.grammar),
      );

    case "matching": {
      const exp = (expected ?? {}) as Record<string, unknown>;
      const sub = (submitted ?? {}) as Record<string, unknown>;
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

// ---------------------------------------------------------------------------
// grade the whole exercise → SubmitResult (reuses the query/Python test shape)
// ---------------------------------------------------------------------------

export function gradeStructured(
  question: StructuredQuestion,
  canonical: StructuredAnswer,
  submitted: StructuredAnswer,
): SubmitResult {
  const results: TestCaseResult[] = question.fields.map((field) => {
    const passed = gradeField(field, submitted[field.id], canonical[field.id]);
    const result: TestCaseResult = { name: field.label, passed };
    if (!passed) {
      result.message = "Not quite — review this part and try again.";
    }
    return result;
  });

  return { results, allPassed: results.length > 0 && results.every((r) => r.passed) };
}
