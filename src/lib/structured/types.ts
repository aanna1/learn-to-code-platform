/**
 * Track-2 "structured" exercise model — the non-query grading format for modeling
 * and normalization lessons (Modules 03–04, Checkpoint A, the Capstone design
 * stage). See docs/sql-test-harness-contract.md for the canonical contract.
 *
 * A structured exercise constrains the learner's answer to a handful of typed
 * fields so grading is exact, deterministic, canonical-form comparison — never
 * NLP, never a backend, never the runtime engine. Every field maps to exactly one
 * pure comparator in ./grade.ts, and the SAME comparators run in the browser
 * (<StructuredExercise>) and in scripts/sql/grade_check_structured.mjs, so
 * "passes grade_check" ⟺ "passes Submit in the browser."
 *
 * On disk (sibling of the query bundle, same folder position):
 *   <lessonId>/exercise/
 *     prompt.mdx        # scenario + task; may reference the ungraded draft area
 *     question.json     # StructuredQuestion — the interactive field spec
 *     answer.json       # StructuredAnswer — canonical value per field id
 *     hints.json        # same shape as every other bundle
 *     wrong.json        # optional authored wrong answer (grader discriminator)
 */

export type StructuredFieldType =
  | "single-select"
  | "multi-select"
  | "token-set"
  | "matching"
  | "partition"
  | "erd-spec";

interface FieldBase {
  /** Stable id; the key into answer.json / the learner's answer map. */
  id: string;
  type: StructuredFieldType;
  /** Shown above the field; also the TestCaseResult name for this field. */
  label: string;
  /** Optional helper text under the label. */
  help?: string;
}

/** Pick exactly one option. Graded by exact (case-folded) match. */
export interface SingleSelectField extends FieldBase {
  type: "single-select";
  options: string[];
}

/** Check all that apply. Graded by set equality. */
export interface MultiSelectField extends FieldBase {
  type: "multi-select";
  options: string[];
}

/**
 * Type items, one per line. Graded by set equality after normalization.
 * `grammar: "fd"` parses each line as a functional dependency `a, b -> c`:
 * the LHS is order-insensitive, and a composite RHS `-> c, d` splits into
 * separate atoms so `a -> b, c` equals `a -> c` + `a -> b`.
 */
export interface TokenSetField extends FieldBase {
  type: "token-set";
  grammar?: "plain" | "fd";
  placeholder?: string;
}

/** Pair each left item with one option. Graded per-pair against the canonical map. */
export interface MatchingField extends FieldBase {
  type: "matching";
  left: string[];
  options: string[];
}

/**
 * Drop each item into one of the named targets. Graded by comparing the
 * collection of resulting groups (each a set of items). By default target
 * labels are ignored (only the grouping matters); set `matchLabels` to require
 * the canonical label per group.
 */
export interface PartitionField extends FieldBase {
  type: "partition";
  items: string[];
  targets: string[];
  matchLabels?: boolean;
}

/** Structured ERD editor. Graded by structural equality (see grade.ts). */
export interface ErdSpecField extends FieldBase {
  type: "erd-spec";
  /** Optional fixed cardinality vocabulary for the relationship editor. */
  cardinalities?: string[];
}

export type StructuredField =
  | SingleSelectField
  | MultiSelectField
  | TokenSetField
  | MatchingField
  | PartitionField
  | ErdSpecField;

export interface StructuredQuestion {
  /** Ungraded "draft it on paper / in this box first" prompt (handwritten-exam practice). */
  draft?: string;
  fields: StructuredField[];
}

// ---- ERD value shape (erd-spec fields) -----------------------------------

export interface ErdAttribute {
  name: string;
  pk?: boolean;
}
export interface ErdEntity {
  name: string;
  attributes: ErdAttribute[];
}
export interface ErdRelationship {
  from: string;
  to: string;
  /** e.g. "1:N", "N:M", "1:1". */
  cardinality: string;
  identifying?: boolean;
}
export interface ErdValue {
  entities: ErdEntity[];
  relationships: ErdRelationship[];
}

/**
 * A learner's (or canonical) answer to one field. The concrete shape depends on
 * the field type:
 *   single-select → string
 *   multi-select  → string[]
 *   token-set     → string[]                       (raw lines)
 *   matching      → Record<leftItem, option>
 *   partition     → Record<targetName, string[]>
 *   erd-spec      → ErdValue
 */
export type FieldValue =
  | string
  | string[]
  | Record<string, string>
  | Record<string, string[]>
  | ErdValue
  | null
  | undefined;

/** answer.json / wrong.json / the learner's live answers: field id → value. */
export type StructuredAnswer = Record<string, FieldValue>;
