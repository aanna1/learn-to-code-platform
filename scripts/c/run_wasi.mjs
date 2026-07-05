// Minimal WASI runner used by the C grader to execute a compiled wasm32-wasi
// module headlessly, the same way the browser worker runs it under a WASI shim.
//
//   node --no-warnings run_wasi.mjs <module.wasm> [stdinFile]
//
// stdout/stderr stream straight through; the process exit code mirrors the
// program's exit/trap (a trap exits 134, matching a SIGABRT-style failure).
import { readFile } from "node:fs/promises";
import { WASI } from "node:wasi";

const wasmPath = process.argv[2];
const stdinPath = process.argv[3];

const opts = { version: "preview1", args: ["prog"], env: {} };
if (stdinPath) {
  // Map fd 0 to the provided file so scanf()/fgets()/getchar() read it.
  opts.stdin = 0;
  opts.preopens = {};
}

const wasi = new WASI(opts);
try {
  const bytes = await readFile(wasmPath);
  const mod = await WebAssembly.compile(bytes);
  const inst = await WebAssembly.instantiate(mod, wasi.getImportObject());
  const code = wasi.start(inst);
  process.exit(typeof code === "number" ? code : 0);
} catch (err) {
  // A WASM trap (UBSan trap, unreachable, OOB, div-by-zero) lands here.
  process.stderr.write(`__TRAP__ ${err && err.message ? err.message : String(err)}\n`);
  process.exit(134);
}
