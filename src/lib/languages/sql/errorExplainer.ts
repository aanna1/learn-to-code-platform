import type {
  ErrorExplainer,
  ErrorExplanation,
  RuntimeError,
} from "@/lib/languages/types";

/**
 * Beginner-friendly translations of the error "types" the SQL runtime worker emits.
 *
 * SQLite reports its own errors as clean, stable message text (verified in the S0
 * spike, docs/sql0-spike-report.md). `sql.worker.ts` normalizes each thrown message
 * into one of the stable `RuntimeError.type` strings below (see its `classify()`),
 * so this map stays simple and the interface stays language-agnostic. Keep this set
 * in sync with the types produced in `sql.worker.ts`.
 *
 * Emitted types (the contract):
 *   - "NoSuchTable"        queried a table that doesn't exist (typo / not created / not seeded)
 *   - "NoSuchColumn"       referenced a column that doesn't exist on the table
 *   - "SyntaxError"        the SQL couldn't be parsed (misspelled keyword, missing comma/quote)
 *   - "UniqueConstraint"   an INSERT/UPDATE duplicated a value in a UNIQUE / PRIMARY KEY column
 *   - "NotNullConstraint"  wrote NULL into a NOT NULL column (or left a required column out)
 *   - "ForeignKeyConstraint" a row referenced a parent row that isn't there
 *   - "CheckConstraint"    a value violated a CHECK rule on the column
 *   - "DatatypeMismatch"   a value's type didn't fit where it was used
 *   - "SqlError"           any other database error (message passed through)
 */
const EXPLANATIONS: Record<string, ErrorExplanation> = {
  NoSuchTable: {
    title: "The database has no table by that name",
    explanation:
      "Your query named a table SQLite couldn't find. Usually the name is misspelled, has different capitalization, or the table simply hasn't been created (or seeded) yet in this database.",
    fix: "Check the table name against the schema for this exercise — spelling and singular/plural both matter. If you're creating the table yourself, make sure the CREATE TABLE runs before the query that uses it.",
  },
  NoSuchColumn: {
    title: "That column isn't on the table",
    explanation:
      "You referenced a column name the table doesn't have. This is often a typo, a column that lives on a different table, or an alias used before it's defined.",
    fix: "List the table's real columns (the CREATE TABLE shows them) and match the name exactly. If the column is on another table, join to that table first.",
  },
  SyntaxError: {
    title: "SQL couldn't understand your statement",
    explanation:
      "The database parser hit something it couldn't read — commonly a misspelled keyword (SELECT/FROM/WHERE), a missing comma between columns, an unclosed quote or parenthesis, or a missing semicolon between statements.",
    fix: "Read the snippet the error shows after 'near' — the problem is usually right there or just before it. Check keyword spelling, commas between listed columns, and that every quote and parenthesis is closed.",
  },
  UniqueConstraint: {
    title: "That value has to be unique, and it's already taken",
    explanation:
      "A column marked UNIQUE (a PRIMARY KEY counts) can't hold the same value twice. Your INSERT or UPDATE tried to store a value that already exists in another row.",
    fix: "Use a value that isn't already in that column, or update the existing row instead of inserting a new one. The error names the exact table.column that clashed.",
  },
  NotNullConstraint: {
    title: "A required column was left empty",
    explanation:
      "A column marked NOT NULL must always have a value. Your statement tried to store NULL there — often because the column was omitted from an INSERT and has no default.",
    fix: "Provide a value for the column the error names. If you're inserting, include it in the column list with a real value.",
  },
  ForeignKeyConstraint: {
    title: "A row pointed at a parent that doesn't exist",
    explanation:
      "A foreign key links a row to a row in another table. This failed because the referenced parent row isn't there — or you tried to delete a parent row that still has children pointing at it.",
    fix: "Insert the parent row first (or reference one that already exists). When deleting, remove or reassign the child rows before the parent.",
  },
  CheckConstraint: {
    title: "A value broke one of the table's rules",
    explanation:
      "A CHECK constraint enforces a rule on a column's values (for example, price must be >= 0). The value you wrote didn't satisfy that rule.",
    fix: "Look at the CHECK rule in the table definition and adjust the value so it passes.",
  },
  DatatypeMismatch: {
    title: "A value didn't fit where you used it",
    explanation:
      "A value's type didn't match what the column or expression expected — for instance putting text where a number belongs.",
    fix: "Check the column's declared type and make sure the value you supply matches it.",
  },
};

export const sqlErrorExplainer: ErrorExplainer = {
  explain(error: RuntimeError): ErrorExplanation | null {
    if (!error.type) return null;
    return EXPLANATIONS[error.type] ?? null;
  },
};
