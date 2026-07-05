import type { Diagnostic, LinterAdapter } from "@/lib/languages/types";

/**
 * C linter adapter — Phase-C1 SHELL.
 *
 * Returns no diagnostics for now. It is intentionally graceful (never throws) so that
 * if C is registered before the real linter lands, editing still works — same rule the
 * Python linter follows ("a linter crash must never break editing").
 *
 * INTENDED DESIGN:
 *   Option A (cheap, ships first): reuse the compiler. On lint(), ask the runtime worker
 *   to run clang in syntax-only mode (`-fsyntax-only -Wall -Wextra`) and map each
 *   diagnostic's {line, column, message, severity} to Diagnostic[]. clang emits
 *   structured, 1-based positions, so this maps directly (clamped to >= 1), like Ruff.
 *   Option B (later): a dedicated clang-tidy-in-WASM pass for richer lints.
 *
 *   Debounce in the editor layer (already done for Python). Severity: clang "error" ->
 *   "error", "warning" -> "warning", "note" -> "info".
 */

export const cLinter: LinterAdapter = {
  isLoaded(): boolean {
    return true;
  },

  async load(): Promise<void> {
    // No-op until the real compiler-backed linter is wired in.
  },

  async lint(_code: string): Promise<Diagnostic[]> {
    void _code;
    return [];
  },
};
