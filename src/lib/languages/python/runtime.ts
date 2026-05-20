import type { RuntimeAdapter } from "@/lib/languages/types";

/**
 * Pyodide-backed runtime adapter for Python.
 *
 * PHASE 1: this is an interface-conformant shell. The actual engine — loading
 * Pyodide from CDN, capturing stdout/stderr, pausing on input(), and running the
 * hidden test harness — is implemented in Phase 2 when the IDE is built on
 * /dev/ide. Until then every method throws a clear marker error so nothing fails
 * silently. No page calls these in Phase 1; the homepage only reads `config`.
 *
 * Phase 2 plan (recorded here so the next session has the design in hand):
 *   - load(): inject the Pyodide loader script from the CDN, await loadPyodide(),
 *     cache the instance at module scope (idempotent via a load promise).
 *   - run(): redirect sys.stdout/sys.stderr to the onStdout/onStderr callbacks;
 *     override builtins.input to await onInput(prompt). The interactive pause
 *     likely uses a web worker + SharedArrayBuffer (hence the COOP/COEP headers
 *     in next.config.mjs and vercel.json), or an equivalent that yields the
 *     cleanest terminal feel.
 *   - runTests(): exec the user code then the tests.py harness in a fresh
 *     namespace, collecting per-case results as structured data.
 */

const PHASE_2_MARKER =
  "Python runtime is implemented in Phase 2 (Pyodide adapter). This is a Phase 1 shell.";

export const pythonRuntime: RuntimeAdapter = {
  isLoaded() {
    return false;
  },
  async load() {
    throw new Error(PHASE_2_MARKER);
  },
  async run() {
    throw new Error(PHASE_2_MARKER);
  },
  async runTests() {
    throw new Error(PHASE_2_MARKER);
  },
};
