/**
 * The Language interface is the single seam through which every language-specific
 * behavior flows. Components and routes operate against this interface ONLY — there
 * must never be an `if (language === "python")` branch anywhere in the app. Adding a
 * new language means implementing this interface and registering it; zero component
 * or route changes.
 *
 * A concrete Language bundles four things:
 *   - config:         static display metadata (name, color, Monaco id, file extension)
 *   - runtime:        executes user code in the browser (Pyodide for Python)
 *   - linter:         produces editor diagnostics (Ruff for Python)
 *   - errorExplainer: turns a runtime error into a beginner-friendly explanation
 */

// ---------------------------------------------------------------------------
// Display config
// ---------------------------------------------------------------------------

export interface LanguageDisplayConfig {
  /** Stable id; also the `[language]` URL segment. e.g. "python" */
  id: string;
  /** Human-facing name. e.g. "Python" */
  displayName: string;
  /** One-line pitch shown on the homepage card and course outline. */
  tagline: string;
  /** Monaco editor language id used for syntax highlighting. e.g. "python" */
  monacoLanguageId: string;
  /** Source file extension, including the dot. e.g. ".py" */
  fileExtension: string;
  /**
   * Accent color for this language's card/badges, as an "R G B" triple so it can
   * be dropped into rgb(... / <alpha>) just like the theme tokens.
   */
  accentRgb: string;
  /** Short glyph (emoji or letters) used as the card icon until we have real art. */
  icon: string;
}

// ---------------------------------------------------------------------------
// Runtime
// ---------------------------------------------------------------------------

/** A structured, language-agnostic representation of an uncaught runtime error. */
export interface RuntimeError {
  /** Error class/type name, e.g. "NameError". Empty string if it couldn't be parsed. */
  type: string;
  /** The error's own message line. */
  message: string;
  /** Full traceback text as the runtime produced it. */
  traceback: string;
}

export interface RunResult {
  /** True when the program finished without an uncaught error. */
  ok: boolean;
  /** Present when `ok` is false. */
  error?: RuntimeError;
}

export interface RunOptions {
  /** The user's source code. */
  code: string;
  /** Called with each chunk of stdout as it is produced. */
  onStdout: (text: string) => void;
  /** Called with each chunk of stderr as it is produced. */
  onStderr: (text: string) => void;
  /**
   * Called when the program asks for interactive input (Python's input()). The
   * adapter pauses execution until the returned promise resolves with one line.
   * If omitted, input() should resolve as if EOF was reached.
   */
  onInput?: (prompt: string) => Promise<string>;
  /** Allows the caller to abort a long-running or runaway program. */
  signal?: AbortSignal;
}

/** Result of one hidden test case, surfaced to the learner without revealing the test source. */
export interface TestCaseResult {
  /** Display name of the test, e.g. "greet returns a greeting". */
  name: string;
  passed: boolean;
  /** Short, friendly explanation shown only when the test fails. */
  message?: string;
}

export interface SubmitResult {
  results: TestCaseResult[];
  allPassed: boolean;
  /** Set when an error prevented the test suite from running at all. */
  error?: RuntimeError;
}

export interface RunTestsOptions {
  /** The user's source code under test. */
  code: string;
  /** The hidden test program (contents of tests.py for Python). */
  tests: string;
  onStdout?: (text: string) => void;
  onStderr?: (text: string) => void;
  signal?: AbortSignal;
}

/**
 * Executes code for one language. Implementations are expected to be lazily
 * loaded — `load()` pulls down the heavy engine (e.g. Pyodide from CDN) and must
 * be idempotent so callers can await it freely.
 */
export interface RuntimeAdapter {
  /** Load/initialize the engine. Idempotent. `onProgress` reports human-readable steps. */
  load(onProgress?: (message: string) => void): Promise<void>;
  /** Whether `load()` has completed successfully. */
  isLoaded(): boolean;
  /** Run user code, streaming output. Resolves when the program ends. */
  run(options: RunOptions): Promise<RunResult>;
  /** Run hidden tests against user code and report per-case results. */
  runTests(options: RunTestsOptions): Promise<SubmitResult>;
}

// ---------------------------------------------------------------------------
// Linter
// ---------------------------------------------------------------------------

export type DiagnosticSeverity = "error" | "warning" | "info";

/** A single editor diagnostic. Positions are 1-based to match editor conventions. */
export interface Diagnostic {
  line: number;
  column: number;
  endLine?: number;
  endColumn?: number;
  message: string;
  severity: DiagnosticSeverity;
  /** Linter rule code, e.g. "F821". */
  code?: string;
}

export interface LinterAdapter {
  /** Load/initialize the linter engine. Idempotent. */
  load(): Promise<void>;
  isLoaded(): boolean;
  /** Analyze source and return diagnostics for the editor gutter. */
  lint(code: string): Promise<Diagnostic[]>;
}

// ---------------------------------------------------------------------------
// Error explainer
// ---------------------------------------------------------------------------

export interface ErrorExplanation {
  /** Friendly one-line title, e.g. "Python doesn't recognize a name you used". */
  title: string;
  /** Plain-English description of what this error usually means. */
  explanation: string;
  /** Concrete, beginner-oriented suggestion for fixing it. */
  fix: string;
}

export interface ErrorExplainer {
  /** Return a friendly explanation for a runtime error, or null if the type is unknown. */
  explain(error: RuntimeError): ErrorExplanation | null;
}

// ---------------------------------------------------------------------------
// Language
// ---------------------------------------------------------------------------

export interface Language {
  config: LanguageDisplayConfig;
  runtime: RuntimeAdapter;
  linter: LinterAdapter;
  errorExplainer: ErrorExplainer;
}
