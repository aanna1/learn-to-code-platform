import type { RuntimeError, TestCaseResult } from "@/lib/languages/types";

/**
 * Pinned engine for the in-browser C toolchain. The runtime worker loads the compiler
 * + linker + sysroot from a CDN (same COOP/COEP + cross-origin-resource-policy story as
 * Pyodide), then compiles/links/runs entirely client-side.
 *
 * DECISION (locked Phase C1): **clang+lld → WASM**. The C0 spike proved clang buys real
 * diagnostics + working UBSan over TinyCC, and the C1 cold-load measurement
 * (docs/c1-coldload-measurement.md) showed ~19 MB transferred, one-time + service-worker
 * cached — acceptable.
 *
 * BUNDLE SUB-DECISION (open — see docs/c1-runtime-notes.md). Two layers:
 *   - DEV/SPIKE bundle = `binji/wasm-clang` (the bundle the cold-load was measured on,
 *     loaded below). It proves the worker plumbing end-to-end in a real browser, BUT it
 *     does NOT satisfy the C2 contract out of the box: its `compile()` defaults to C++
 *     (we bypass it and drive `clang -cc1 -x c` directly), it ships clang 8.0.1, its
 *     `App` reads stdin from a preset string (no interactive blocking), leaves
 *     `clock_time_get` unimplemented, and its sysroot almost certainly lacks the
 *     compiler-rt UBSan runtime — so `-fsanitize=undefined` links will fail on it.
 *   - PROD bundle = a purpose-built clang+lld + wasi-libc + **compiler-rt (UBSan)**
 *     sysroot, plus an interactive SAB-backed stdin shim. Building it is an offline LLVM
 *     task (the C1 engineering gate). When ready, only the constants here + the CDN base
 *     change; the worker/runtime code below is written to that target.
 */
export const C_ENGINE = "clang-wasm" as const;
/** Clang version in the currently-loaded bundle (binji dev bundle = 8.0.1). */
export const C_CLANG_VERSION = "8.0.1";
/**
 * Base URL for the compiler (`clang`), linker (`lld`), `memfs`, `sysroot.tar`, and the
 * `shared.js` driver. **Self-hosted same-origin** from `public/c-toolchain/`.
 *
 * WHY SAME-ORIGIN (browser-verified 2026-06-07): jsDelivr **403s the ~31 MB `clang` blob**
 * — it exceeds jsDelivr's ~20 MB per-file limit (memfs + sysroot.tar are smaller and load
 * fine, which is the giveaway). binji's own GitHub Pages serves it (that's what the
 * cold-load was measured on) but sets no CORP header, so it can't load under our COEP
 * `require-corp`. Same-origin assets are exempt from COEP/CORP **and** have no size cap, so
 * self-hosting is the robust path for both dev and prod. Root-relative + basePath so it
 * resolves under GitHub Pages' `/learn-to-code-platform/` prefix too.
 *
 * Populate the folder once (gitignored — ~60 MB) from binji's Pages host:
 *   mkdir -p public/c-toolchain && cd public/c-toolchain
 *   for f in clang lld memfs sysroot.tar shared.js; do curl -fL -o "$f" "https://binji.github.io/wasm-clang/$f"; done
 * Prod will swap this for the purpose-built clang+lld+wasi-libc+compiler-rt bundle (still
 * self-hosted) + a service-worker cache (C4).
 */
export const C_TOOLCHAIN_CDN_BASE = `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/c-toolchain/`;

/**
 * `clang -cc1` args for compiling one C TU to an object file, per the C2 contract
 * (docs/c-test-harness-contract.md). `{clangInclude}` is interpolated from C_CLANG_VERSION.
 * UBSan flags are included for the PROD bundle; on the dev bundle (no compiler-rt) they are
 * dropped by the worker (see C_SUPPORTS_UBSAN) so basic C still runs.
 */
export const C_CC1_BASE_ARGS = [
  "-emit-obj",
  "-disable-free",
  "-isysroot",
  "/",
  "-internal-isystem",
  "/include",
  "-internal-isystem",
  `/lib/clang/${C_CLANG_VERSION}/include`,
  "-ferror-limit",
  "19",
  "-fmessage-length",
  "80",
  "-fcolor-diagnostics",
  "-Wall",
  "-Wextra",
  "-std=c11",
  "-O0",
  "-x",
  "c",
] as const;
/** UBSan (non-trap) flags — readable UB message → errorExplainer. Requires compiler-rt in the sysroot. */
export const C_UBSAN_ARGS = ["-fsanitize=undefined", "-fno-sanitize-trap=undefined"] as const;
/**
 * Whether the loaded bundle's sysroot has the compiler-rt UBSan runtime to link against.
 * FALSE for the binji dev bundle; flip to TRUE with the prod bundle. Gates C_UBSAN_ARGS.
 */
export const C_SUPPORTS_UBSAN = false;
/** Define applied to the SUBMISSION TU only, to neutralize a student main() (C2 contract). */
export const C_NEUTRALIZE_MAIN = "-Dmain=__student_main__";

// ---------------------------------------------------------------------------
// SharedArrayBuffer layout for passing one line of stdin from main -> worker.
// Identical to the Python runtime's layout so the Terminal/Ide plumbing is reused
// unchanged. Used to make scanf()/fgets()/getchar() block on the worker until the
// main thread writes a line, exactly like Python's input().
// ---------------------------------------------------------------------------
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

/**
 * Cancellation. Unlike Pyodide (which exposes a SIGINT interrupt buffer), a compiled
 * WASM program can't be interrupted cooperatively, so a CPU-bound run is cancelled by
 * terminating the worker. When the page IS cross-origin isolated, input waits are
 * cancelled via STATUS_CANCELLED first (graceful) before any terminate.
 */

export type WorkerInbound =
  // The input SAB is omitted when the page isn't cross-origin isolated; interactive
  // stdin (scanf/fgets) is then unavailable and reads hit EOF.
  | { type: "init"; inputSab?: SharedArrayBuffer }
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
  | {
      type: "testResult";
      results: TestCaseResult[];
      allPassed: boolean;
      error?: RuntimeError;
    };
