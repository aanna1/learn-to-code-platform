/**
 * C runtime Web Worker — Phase-C1 (dev bundle = binji/wasm-clang).
 *
 * Loads clang + lld (+ wasi sysroot) from a CDN, compiles the learner's C in-browser,
 * links to wasm, runs it under binji's WASI-ish `App`, and streams stdio. The C analogue
 * of `python/pyodide.worker.ts`.
 *
 * It drives binji's `API` (from shared.js). We fetch+eval shared.js and capture the
 * top-level `const API` onto `self` (importScripts wouldn't expose a block-scoped const to
 * this bundled module), then call the LOW-LEVEL `api.run(module, ...argv)` so we control
 * the exact `clang -cc1 -x c` flags (the C2 contract) instead of binji's C++/-O2 default.
 *
 * Bundle caveats (see runtimeProtocol.ts C_SUPPORTS_UBSAN and docs/c1-runtime-notes.md):
 * the binji dev bundle ships clang 8, no compiler-rt UBSan (so UBSan flags are gated off),
 * and reads stdin from a preset string (no interactive blocking yet). The prod bundle flips
 * those on; the code here is written so only constants change.
 *
 * NOT browser-verified in this environment (no browser). Mirrors the headless, verified
 * scripts/c/grade_check.py compile/run/parse model so browser ⟺ grade_check stay in step.
 */

import {
  C_CC1_BASE_ARGS,
  C_NEUTRALIZE_MAIN,
  C_SUPPORTS_UBSAN,
  C_TOOLCHAIN_CDN_BASE,
  C_UBSAN_ARGS,
  INPUT_DATA_OFFSET,
} from "@/lib/languages/c/runtimeProtocol";
import type { WorkerInbound, WorkerOutbound } from "@/lib/languages/c/runtimeProtocol";
import type { RuntimeError, TestCaseResult } from "@/lib/languages/types";

const ctx: any = self;

function post(message: WorkerOutbound): void {
  ctx.postMessage(message);
}

// SAB views (provided by main thread). Reserved for the interactive-stdin upgrade; the
// dev bundle reads stdin from a preset string, so these are not yet consumed.
let inputControl: Int32Array | null = null;
let inputData: Uint8Array | null = null;

// binji link line, tuned to its sysroot (crt1.o + libc/libc++ archives live in
// lib/wasm32-wasi). Centralized so the prod bundle can swap it.
const LINK_ARGS = [
  "wasm-ld",
  "--no-threads",
  "--export-dynamic",
  "-z",
  "stack-size=1048576",
  "-Llib/wasm32-wasi",
  "lib/wasm32-wasi/crt1.o",
];
const LINK_LIBS = ["-lc", "-lc++", "-lc++abi", "-lcanvas"];

let api: any = null;
let loadPromise: Promise<void> | null = null;

// Where the current phase's hostWrite output goes. In "run" we stream stdout live; in
// "capture" (compile/link/load) we buffer it as diagnostics and keep it off the terminal.
let mode: "run" | "capture" = "capture";
let captureBuf = "";

function hostWrite(text: string): void {
  if (mode === "run") {
    post({ type: "stdout", text });
  } else {
    captureBuf += text;
  }
}

const ANSI = /\x1b\[[0-9;]*m/g;
function clean(s: string): string {
  return s.replace(ANSI, "");
}

/**
 * Keep only real compiler diagnostics from a captured compile/link phase, dropping binji's
 * own chatter: the `> clang -cc1 …` / `> wasm-ld …` command echoes (and "Fetching…/Untarring…"
 * status), plus the "N warning(s) generated." summary. Source-context and caret lines (which
 * don't start with ">") are kept so a diagnostic stays readable.
 */
function extractDiagnostics(raw: string): string {
  return clean(raw)
    .split("\n")
    .filter((line) => {
      const t = line.trim();
      if (!t) return false;
      if (t.startsWith(">")) return false;
      if (/^\d+ (warning|error)s? generated\.?$/.test(t)) return false;
      return true;
    })
    .join("\n");
}

async function compileModule(name: string): Promise<WebAssembly.Module> {
  // Use compile (not compileStreaming): CDN may not serve application/wasm MIME.
  const resp = await fetch(C_TOOLCHAIN_CDN_BASE + name);
  if (!resp.ok) throw new Error(`Failed to fetch ${name}: ${resp.status}`);
  return WebAssembly.compile(await resp.arrayBuffer());
}

async function readBuffer(name: string): Promise<ArrayBuffer> {
  const resp = await fetch(C_TOOLCHAIN_CDN_BASE + name);
  if (!resp.ok) throw new Error(`Failed to fetch ${name}: ${resp.status}`);
  return resp.arrayBuffer();
}

async function ensureLoaded(): Promise<void> {
  if (api) return;
  if (!loadPromise) {
    loadPromise = (async () => {
      post({ type: "loadProgress", message: "Loading the C compiler (one-time)…" });
      // Fetch + eval shared.js, capturing binji's top-level `const API` onto self.
      const srcResp = await fetch(C_TOOLCHAIN_CDN_BASE + "shared.js");
      if (!srcResp.ok) throw new Error(`Failed to fetch shared.js: ${srcResp.status}`);
      const src = await srcResp.text();
      (0, eval)(`${src}\n;self.__CLANG_API__ = API;`);
      const API = ctx.__CLANG_API__;
      if (!API) throw new Error("Could not load the C toolchain driver (API missing).");

      mode = "capture";
      captureBuf = "";
      api = new API({ hostWrite, readBuffer, compileStreaming: compileModule });
      await api.ready; // memfs instantiated + sysroot.tar untarred

      post({ type: "loadProgress", message: "Warming up clang + lld…" });
      // Pre-fetch/compile clang and lld so the first Run isn't slowed by the download.
      await api.getModule("clang");
      await api.getModule("lld");
    })();
  }
  await loadPromise;
}

/** Compile one C translation unit to an object file. Throws with diagnostics on failure. */
async function compileTU(srcName: string, objName: string, extraArgs: string[] = []): Promise<void> {
  const ubsan = C_SUPPORTS_UBSAN ? [...C_UBSAN_ARGS] : [];
  const clang = await api.getModule("clang");
  await api.run(
    clang,
    "clang",
    "-cc1",
    ...C_CC1_BASE_ARGS,
    ...ubsan,
    ...extraArgs,
    "-o",
    objName,
    srcName,
  );
}

async function link(objNames: string[], wasmName: string): Promise<void> {
  const lld = await api.getModule("lld");
  await api.run(lld, ...LINK_ARGS, ...objNames, ...LINK_LIBS, "-o", wasmName);
}

/** Map a thrown run/compile failure to a RuntimeError type the errorExplainer knows. */
function classify(phase: "compile" | "run", diag: string, exn: any): RuntimeError {
  const text = clean(diag);
  if (phase === "compile") {
    const line = text.split("\n").find((l) => l.includes("error:")) ?? "Compilation failed.";
    return { type: "CompileError", message: line.trim(), traceback: text.trim() };
  }
  const lower = text.toLowerCase();
  let type = "NonZeroExit";
  if (/runtime error:|signed integer overflow|out of bounds|undefined behavior/.test(lower)) {
    type = "UndefinedBehavior";
  } else if (/divide|division by zero/.test(lower)) {
    type = "FloatingPointError";
  } else if (/stack/.test(lower) && /overflow|exhaust/.test(lower)) {
    type = "StackOverflow";
  } else if (/memory access out of bounds|unreachable|null/.test(lower)) {
    type = "SegmentationFault";
  }
  const message =
    typeof exn?.code === "number" ? `Program exited with code ${exn.code}.` : String(exn?.message ?? "Program crashed.");
  return { type, message, traceback: text.trim() || message };
}

function resetMemfsStdin(): void {
  // Dev bundle: non-interactive stdin (EOF). The interactive SAB-backed host_read goes here.
  api.memfs?.setStdinStr?.("");
}

async function handleRun(code: string): Promise<void> {
  try {
    mode = "capture";
    captureBuf = "";
    api.memfs.addFile("main.c", code);
    try {
      await compileTU("main.c", "main.o");
      await link(["main.o"], "main.wasm");
    } catch (exn) {
      const diag = extractDiagnostics(captureBuf);
      if (diag) post({ type: "stderr", text: `${diag}\n` });
      post({ type: "runResult", ok: false, error: classify("compile", diag, exn) });
      return;
    }
    // Surface any compile warnings even on success.
    const warnings = extractDiagnostics(captureBuf).trim();
    if (warnings) post({ type: "stderr", text: `${warnings}\n` });

    const wasm = api.memfs.getFileContents("main.wasm");
    const mod = await WebAssembly.compile(wasm);
    resetMemfsStdin();
    mode = "run";
    captureBuf = "";
    try {
      await api.run(mod, "main.wasm");
      post({ type: "runResult", ok: true });
    } catch (exn: any) {
      if (exn && exn.code === 0) {
        post({ type: "runResult", ok: true });
      } else {
        post({ type: "runResult", ok: false, error: classify("run", captureBuf, exn) });
      }
    }
  } catch (exn: any) {
    post({ type: "runResult", ok: false, error: { type: "", message: String(exn?.message ?? exn), traceback: "" } });
  }
}

const T_LINE = /^__T__\|([^|]*)\|(PASS|FAIL)(?:\|(.*))?$/;

function parseTestLines(stdout: string): TestCaseResult[] {
  const results: TestCaseResult[] = [];
  for (const raw of clean(stdout).split("\n")) {
    const m = T_LINE.exec(raw.trim());
    if (m) results.push({ name: m[1] ?? "", passed: m[2] === "PASS", message: m[3] || undefined });
  }
  return results;
}

async function handleRunTests(code: string, tests: string): Promise<void> {
  mode = "capture";
  captureBuf = "";
  try {
    api.memfs.addFile("submission.c", code);
    api.memfs.addFile("tests.c", tests);
    try {
      // Separate-compile per the C2 contract: neutralize the student main() on the
      // submission TU only, then link with the harness's main().
      await compileTU("submission.c", "submission.o", [C_NEUTRALIZE_MAIN]);
      await compileTU("tests.c", "tests.o");
      await link(["submission.o", "tests.o"], "tests.wasm");
    } catch (exn) {
      post({
        type: "testResult",
        results: [],
        allPassed: false,
        error: classify("compile", extractDiagnostics(captureBuf), exn),
      });
      return;
    }
    const wasm = api.memfs.getFileContents("tests.wasm");
    const mod = await WebAssembly.compile(wasm);
    resetMemfsStdin();
    mode = "run";
    captureBuf = "";
    let crashed: RuntimeError | undefined;
    try {
      await api.run(mod, "tests.wasm");
    } catch (exn: any) {
      if (!(exn && exn.code === 0)) crashed = classify("run", captureBuf, exn);
    }
    const results = parseTestLines(captureBuf);
    if (crashed) {
      results.push({ name: "(program crashed)", passed: false, message: crashed.message });
    }
    if (results.length === 0) {
      post({
        type: "testResult",
        results: [],
        allPassed: false,
        error: crashed ?? { type: "", message: "The tests produced no output.", traceback: "" },
      });
      return;
    }
    post({ type: "testResult", results, allPassed: results.every((r) => r.passed) });
  } catch (exn: any) {
    post({ type: "testResult", results: [], allPassed: false, error: { type: "", message: String(exn?.message ?? exn), traceback: "" } });
  }
}

ctx.onmessage = async (event: MessageEvent<WorkerInbound>) => {
  const msg = event.data;
  switch (msg.type) {
    case "init":
      if (msg.inputSab) {
        inputControl = new Int32Array(msg.inputSab, 0, 2);
        inputData = new Uint8Array(msg.inputSab, INPUT_DATA_OFFSET);
        void inputControl;
        void inputData;
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

export {};
