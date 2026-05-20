/**
 * Pyodide web worker. Runs Python off the main thread so that synchronous
 * input() can block the worker (via Atomics.wait on a SharedArrayBuffer) while
 * the main thread collects a line from the terminal — giving a real interactive
 * shell feel. Requires cross-origin isolation (COOP/COEP), configured in
 * next.config.mjs (dev) and vercel.json (prod).
 *
 * Pyodide itself is loaded from the jsDelivr CDN (per the brief), which serves
 * the needed `access-control-allow-origin` and `cross-origin-resource-policy:
 * cross-origin` headers, so importScripts works under COEP require-corp.
 *
 * The worker is loosely typed at the boundary on purpose: pulling in the
 * "webworker" lib alongside "dom" causes global type conflicts, so we treat the
 * worker scope as `any` and keep strong types on the message payloads only.
 */

import { PYODIDE_VERSION, SAB_STATUS, SAB_LEN, INPUT_DATA_OFFSET } from "@/lib/languages/python/runtimeProtocol";
import type { WorkerInbound, WorkerOutbound } from "@/lib/languages/python/runtimeProtocol";

const ctx: any = self;

const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// SharedArrayBuffer views, provided by the main thread via the "init" message.
let inputControl: Int32Array | null = null;
let inputData: Uint8Array | null = null;
let interrupt: Uint8Array | null = null;

let pyodide: any = null;
let loadPromise: Promise<void> | null = null;

function post(message: WorkerOutbound): void {
  ctx.postMessage(message);
}

/** The Python harness that runs every `test_*` function and reports per-case results as JSON. */
const TEST_RUNNER = `
import json as _json, traceback as _traceback
def _run_tests(_ns):
    _results = []
    for _name, _fn in list(_ns.items()):
        if _name.startswith("test_") and callable(_fn):
            _label = (_fn.__doc__ or _name).strip().splitlines()[0] if (_fn.__doc__ or _name).strip() else _name
            try:
                _fn()
                _results.append({"name": _label, "passed": True})
            except AssertionError as _e:
                _msg = str(_e) or "Expected something different from what your code produced."
                _results.append({"name": _label, "passed": False, "message": _msg})
            except Exception as _e:
                _results.append({"name": _label, "passed": False, "message": f"{type(_e).__name__}: {_e}"})
    return _json.dumps(_results)
`;

function makeStreamingDecoder(): (bytes: Uint8Array) => string {
  const decoder = new TextDecoder();
  return (bytes: Uint8Array) => decoder.decode(bytes, { stream: true });
}

/**
 * Synchronous stdin used by Python's input(). Signals the main thread, then
 * blocks the worker until the main thread writes a line into the shared buffer.
 * Returns "" (EOF) when input isn't available or the run is cancelled.
 */
function blockingStdin(): string {
  if (!inputControl || !inputData) return "";
  Atomics.store(inputControl, SAB_STATUS, 1 /* WAITING */);
  post({ type: "awaitingInput" });
  Atomics.wait(inputControl, SAB_STATUS, 1 /* WAITING */);
  const status = Atomics.load(inputControl, SAB_STATUS);
  if (status === 3 /* CANCELLED */) {
    Atomics.store(inputControl, SAB_STATUS, 0 /* IDLE */);
    return "";
  }
  const len = Atomics.load(inputControl, SAB_LEN);
  const bytes = inputData.slice(0, len);
  Atomics.store(inputControl, SAB_STATUS, 0 /* IDLE */);
  return new TextDecoder().decode(bytes);
}

function configureStreams(interactive: boolean): void {
  const outDecode = makeStreamingDecoder();
  const errDecode = makeStreamingDecoder();
  pyodide.setStdout({
    write: (buf: Uint8Array) => {
      post({ type: "stdout", text: outDecode(buf) });
      return buf.length;
    },
  });
  pyodide.setStderr({
    write: (buf: Uint8Array) => {
      post({ type: "stderr", text: errDecode(buf) });
      return buf.length;
    },
  });
  pyodide.setStdin({
    stdin: interactive ? blockingStdin : () => "",
    isatty: false,
  });
}

function resetInterrupt(): void {
  if (interrupt) interrupt[0] = 0;
}

interface ParsedError {
  type: string;
  message: string;
  traceback: string;
}

function parseError(error: any): ParsedError {
  // Pyodide PythonError exposes `.type` (the Python class name) and puts the
  // full formatted traceback in `.message`.
  const traceback = String(error?.message ?? error ?? "Unknown error");
  const type =
    typeof error?.type === "string" && error.type
      ? error.type
      : (error?.name ?? "");
  // The human message is the last non-empty traceback line ("NameError: ...").
  const lines = traceback.split("\n").filter((l) => l.trim().length > 0);
  const lastLine = lines[lines.length - 1] ?? traceback;
  const message =
    type && lastLine.startsWith(`${type}:`)
      ? lastLine.slice(type.length + 1).trim()
      : lastLine;
  return { type, message, traceback };
}

async function ensureLoaded(): Promise<void> {
  if (pyodide) return;
  if (!loadPromise) {
    loadPromise = (async () => {
      post({ type: "loadProgress", message: "Downloading the Python runtime…" });
      ctx.importScripts(`${PYODIDE_INDEX_URL}pyodide.js`);
      post({ type: "loadProgress", message: "Starting Python…" });
      pyodide = await ctx.loadPyodide({ indexURL: PYODIDE_INDEX_URL });
      if (interrupt) pyodide.setInterruptBuffer(interrupt);
    })();
  }
  await loadPromise;
}

async function handleRun(code: string): Promise<void> {
  resetInterrupt();
  configureStreams(true);
  try {
    await pyodide.runPythonAsync(code);
    post({ type: "runResult", ok: true });
  } catch (error) {
    post({ type: "runResult", ok: false, error: parseError(error) });
  }
}

async function handleRunTests(code: string, tests: string): Promise<void> {
  resetInterrupt();
  configureStreams(false);
  // Fresh namespace so one submission can't leak state into the next. __name__ is
  // set to a non-"__main__" value so any `if __name__ == "__main__":` block (used
  // by exercises for interactive demo code) is skipped during testing.
  const ns = pyodide.toPy({ __name__: "__tests__" });
  try {
    pyodide.runPython(code, { globals: ns });
  } catch (error) {
    ns.destroy?.();
    post({ type: "testResult", results: [], allPassed: false, error: parseError(error) });
    return;
  }
  try {
    pyodide.runPython(tests, { globals: ns });
    pyodide.runPython(TEST_RUNNER, { globals: ns });
    const runner = ns.get("_run_tests");
    const json: string = runner(ns);
    runner.destroy?.();
    const results = JSON.parse(json) as { name: string; passed: boolean; message?: string }[];
    post({
      type: "testResult",
      results,
      allPassed: results.length > 0 && results.every((r) => r.passed),
    });
  } catch (error) {
    post({ type: "testResult", results: [], allPassed: false, error: parseError(error) });
  } finally {
    ns.destroy?.();
  }
}

ctx.onmessage = async (event: MessageEvent<WorkerInbound>) => {
  const msg = event.data;
  switch (msg.type) {
    case "init":
      if (msg.inputSab) {
        inputControl = new Int32Array(msg.inputSab, 0, 2);
        inputData = new Uint8Array(msg.inputSab, INPUT_DATA_OFFSET);
      }
      if (msg.interruptSab) {
        interrupt = new Uint8Array(msg.interruptSab);
        if (pyodide) pyodide.setInterruptBuffer(interrupt);
      }
      break;
    case "load":
      try {
        await ensureLoaded();
        post({ type: "loaded" });
      } catch (error) {
        post({ type: "loadError", message: String((error as Error)?.message ?? error) });
      }
      break;
    case "run":
      await handleRun(msg.code);
      break;
    case "runTests":
      await handleRunTests(msg.code, msg.tests);
      break;
  }
};
