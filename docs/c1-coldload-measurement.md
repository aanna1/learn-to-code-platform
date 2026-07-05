# C1 Cold-Load Measurement — clang-wasm vs TinyCC

The one number the C0 spike said it still owed: the cold-load weight of a real in-browser Clang
bundle, to lock the C1 engine choice. Status: **DONE — static sizes + live browser pass both
measured.** Verdict: clang-wasm cold-loads **19.4 MB over the wire** (one-time, cached), and
compilation is not the bottleneck. The "tens of MB, first-visit-only" cost the spike predicted is
confirmed and is comfortably acceptable.

## Live browser pass (`binji.github.io/wasm-clang`, DevTools Network, cache disabled)

Measured in Chrome with "Disable cache" on, full reload, then a hello-world compile:

| Metric | Value |
|---|---|
| **Total transferred (whole page, 32 requests)** | **19.4 MB** |
| `clang` (transferred / on-disk) | **10.7 MB** / 31.2 MB (gzip ~34%) |
| `lld` (transferred / on-disk) | **6.8 MB** / 19.5 MB (gzip ~35%) |
| `sysroot.tar` (transferred / on-disk) | **1.87 MB** / 9.3 MB |
| `clang` fetch + instantiate | ~1.3 s |
| `lld` fetch + instantiate | ~0.8 s |
| First hello-world compile → link → run | completed cleanly, sub-second compile after fetch |

So GitHub Pages **does** gzip the extensionless wasm binaries (~34% of uncompressed), making the
real cold-load **19.4 MB**, below the 25–35 MB upper-bound estimate. The DevTools "**121 MB
resources**" figure is a measurement artifact, **not** the real footprint: the demo fetches each
artifact twice (once via `worker.js`, once re-served by its `service_worker.js`), so the decoded
total double-counts (~2 × the true ~60 MB). Compilation latency is dominated by the one-time
toolchain fetch/instantiate; the actual translation of learner-sized C is sub-second.

## Static sizes — `binji/wasm-clang` (the reference Clang-WASM bundle)

Read from the GitHub tree API (`binji/wasm-clang@master`), so these are **uncompressed** blob
sizes — what the toolchain weighs on disk and the upper bound on transfer:

| Artifact | Bytes | ≈ |
|---|---:|---|
| `clang` (clang→wasm) | 31,214,472 | **31.2 MB** |
| `lld` (linker→wasm) | 19,490,094 | **19.5 MB** |
| `sysroot.tar` (headers + libc archives) | 9,297,920 | **9.3 MB** |
| `memfs` (WASI memfs→wasm) | 345,442 | 0.34 MB |
| JS glue (`shared.js`+`worker.js`+`web.js`+`shared_web.js`) | ~37,000 | 0.04 MB |
| **Core toolchain total** | | **≈ 60.4 MB uncompressed** |

Over the wire this compresses (wasm gzips to roughly 40–55%), so expect **~25–35 MB transferred**
on a cold visit — the exact figure depends on whether the host serves gzip/brotli for these
extensionless binaries, which is what the live pass below pins down. Note `binji`'s prebuilt is an
older LLVM (~v8, 2019); a current Clang would be somewhat larger, but the order of magnitude —
**tens of MB, one-time** — is exactly what the C0 spike predicted.

## What this means for the engine decision

- **Clang-WASM:** ~60 MB uncompressed / ~25–35 MB transferred, **once**, then service-worker
  cached so it's a first-visit-only cost. Buys real Clang diagnostics + working UBSan (the C0
  spike's friendly-error win).
- **TinyCC-WASM:** ~1–2 MB, near-instant cold load. **No sanitizers (no UBSan)**, weaker
  diagnostics — the grading/error story the C2 contract is built around degrades.

The tradeoff is now concrete: the only reason to pick TinyCC is if a ~30 MB first-visit download
(cached thereafter) is unacceptable for the target audience. This is a product call, not a
technical unknown anymore.

## Reproduce the live pass (for the record)

How the numbers above were taken: open `https://binji.github.io/wasm-clang/`, DevTools → Network,
check **Disable cache**, reload, wait for the toolchain to finish, then read the status-bar
*transferred* total and the `clang`/`lld`/`sysroot.tar` rows (use the `service_worker.js`-served
row for the real network transfer). For a scripted version, paste into the console (note: the demo
fetches the toolchain **inside a worker**, so main-thread `performance` entries may not capture
those — the Network panel is the source of truth):

```js
// 1) Cold-load transfer: sum encoded (over-the-wire) bytes for the toolchain artifacts.
const res = performance.getEntriesByType("resource")
  .filter(r => /\/(clang|lld|memfs|sysroot\.tar)(\?|$)/.test(r.name));
const transferred = res.reduce((a, r) => a + (r.transferSize || 0), 0);
const decoded = res.reduce((a, r) => a + (r.decodedBodySize || 0), 0);
({
  files: res.map(r => ({ name: r.name.split("/").pop(),
                         transferKB: Math.round(r.transferSize/1024),
                         decodedKB: Math.round(r.decodedBodySize/1024) })),
  totalTransferredMB: +(transferred/1048576).toFixed(1),
  totalDecodedMB: +(decoded/1048576).toFixed(1),
});
```

For first-compile latency, type a small program into the demo's editor, then time the
compile+run button (or instrument the page's compile call) and record wall-clock ms. Capture the
network HAR or the `transferSize` table above for the record, then update this doc + the C0/CLAUDE
"🌐 owed" notes to closed.
