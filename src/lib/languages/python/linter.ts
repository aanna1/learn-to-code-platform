import type { LinterAdapter } from "@/lib/languages/types";

/**
 * Ruff-backed linter adapter for Python (via @astral-sh/ruff-wasm-web, or the
 * closest working equivalent).
 *
 * PHASE 1: interface-conformant shell. Phase 2 wires the real WASM linter and
 * maps its output onto our Diagnostic shape for the Monaco gutter.
 *
 * Phase 2 plan:
 *   - load(): initialize the ruff-wasm module once (cache the init promise).
 *   - lint(): run Ruff over the source and translate each finding into a
 *     Diagnostic { line, column, message, severity, code }. Debouncing on the
 *     editor side keeps it responsive as the user types.
 */

const PHASE_2_MARKER =
  "Python linter is implemented in Phase 2 (Ruff WASM adapter). This is a Phase 1 shell.";

export const pythonLinter: LinterAdapter = {
  isLoaded() {
    return false;
  },
  async load() {
    throw new Error(PHASE_2_MARKER);
  },
  async lint() {
    throw new Error(PHASE_2_MARKER);
  },
};
