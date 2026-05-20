import type {
  Diagnostic,
  DiagnosticSeverity,
  LinterAdapter,
} from "@/lib/languages/types";
import type { Diagnostic as RuffDiagnostic } from "@astral-sh/ruff-wasm-web";

/**
 * Ruff-backed linter adapter (via @astral-sh/ruff-wasm-web). The WASM module and
 * Workspace are loaded lazily on first lint() and cached. The package is loaded
 * with a dynamic import so it never enters the server bundle; webpack emits its
 * .wasm as a same-origin asset, which is safe under COEP require-corp.
 *
 * Ruff reports 1-based row/column; Monaco markers are also 1-based, so positions
 * map directly (clamped to >= 1).
 */

// Loaded lazily; `Workspace` instance from the dynamically imported module.
type WorkspaceInstance = { check(contents: string): unknown };

let workspace: WorkspaceInstance | null = null;
let loadPromise: Promise<void> | null = null;

function severityFor(code: string | null): DiagnosticSeverity {
  // No rule code = a parse/syntax error; E9xx are syntax errors too.
  if (!code) return "error";
  if (code.startsWith("E9")) return "error";
  return "warning";
}

function clamp1(n: number): number {
  return n >= 1 ? n : 1;
}

export const pythonLinter: LinterAdapter = {
  isLoaded() {
    return workspace !== null;
  },

  async load() {
    if (workspace) return;
    if (!loadPromise) {
      loadPromise = (async () => {
        const ruff = await import("@astral-sh/ruff-wasm-web");
        await ruff.default();
        workspace = new ruff.Workspace(
          ruff.Workspace.defaultSettings(),
          ruff.PositionEncoding.Utf16,
        ) as unknown as WorkspaceInstance;
      })();
    }
    await loadPromise;
  },

  async lint(code: string): Promise<Diagnostic[]> {
    await this.load();
    if (!workspace) return [];
    let raw: RuffDiagnostic[];
    try {
      raw = workspace.check(code) as RuffDiagnostic[];
    } catch {
      // A linter crash must never break editing.
      return [];
    }
    return raw.map((d) => ({
      line: clamp1(d.start_location.row),
      column: clamp1(d.start_location.column),
      endLine: clamp1(d.end_location.row),
      endColumn: clamp1(d.end_location.column),
      message: d.message,
      severity: severityFor(d.code),
      code: d.code ?? undefined,
    }));
  },
};
