import type { Diagnostic, LinterAdapter } from "@/lib/languages/types";

/**
 * SQL linter adapter — S1 SHELL.
 *
 * Returns no diagnostics for now. It is intentionally graceful (never throws) so
 * editing always works even before a real linter lands — the same rule the Python
 * and C linters follow ("a linter crash must never break editing").
 *
 * INTENDED DESIGN (later): a light client-side pass is enough for a beginner SQL
 * course — flag an empty statement, an obviously unbalanced quote/paren, or a
 * missing trailing semicolon. A heavier option is to `EXPLAIN` the statement under
 * sql.js against the fixture and surface SQLite's parse error as a gutter marker;
 * that reuses the runtime the worker already loads. Map any finding's
 * {line, column, message, severity} to Diagnostic[] (1-based), debounced in the
 * editor layer (already done for every language).
 */
export const sqlLinter: LinterAdapter = {
  isLoaded(): boolean {
    return true;
  },

  async load(): Promise<void> {
    // No-op until a real SQL linter is wired in.
  },

  async lint(_code: string): Promise<Diagnostic[]> {
    void _code;
    return [];
  },
};
