import type { RuntimeError, TestCaseResult } from "@/lib/languages/types";

/** Pyodide version. The CDN index URL and the dev-dependency types are pinned to match. */
export const PYODIDE_VERSION = "0.26.4";

// SharedArrayBuffer layout for passing one line of input from main -> worker.
// [0..7]   two Int32s: [SAB_STATUS, SAB_LEN]
// [8..]    UTF-8 bytes of the input line
export const SAB_STATUS = 0;
export const SAB_LEN = 1;
export const INPUT_DATA_OFFSET = 8;
/** Max bytes for a single input line. */
export const INPUT_CAPACITY = 64 * 1024;
export const INPUT_SAB_BYTES = INPUT_DATA_OFFSET + INPUT_CAPACITY;

// Status values stored at SAB_STATUS.
export const STATUS_IDLE = 0;
export const STATUS_WAITING = 1; // worker is blocked waiting for a line
export const STATUS_READY = 2; // main has written a line
export const STATUS_CANCELLED = 3; // run cancelled while waiting for input

// Interrupt buffer: 1 byte. Writing 2 (SIGINT) makes Pyodide raise KeyboardInterrupt.
export const INTERRUPT_SIGINT = 2;

export type WorkerInbound =
  // SABs are omitted when the page isn't cross-origin isolated; interactive
  // input() and mid-run interrupt are then unavailable (input() yields EOF).
  | { type: "init"; inputSab?: SharedArrayBuffer; interruptSab?: SharedArrayBuffer }
  | { type: "load" }
  | { type: "run"; code: string }
  | { type: "runTests"; code: string; tests: string };

export type WorkerOutbound =
  | { type: "loadProgress"; message: string }
  | { type: "loaded" }
  | { type: "loadError"; message: string }
  | { type: "stdout"; text: string }
  | { type: "stderr"; text: string }
  | { type: "awaitingInput" }
  | { type: "runResult"; ok: boolean; error?: RuntimeError }
  | { type: "testResult"; results: TestCaseResult[]; allPassed: boolean; error?: RuntimeError };
