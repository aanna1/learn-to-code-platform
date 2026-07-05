import type {
  RunOptions,
  RunResult,
  RunTestsOptions,
  RuntimeAdapter,
  SubmitResult,
} from "@/lib/languages/types";
import {
  INPUT_CAPACITY,
  INPUT_DATA_OFFSET,
  INPUT_SAB_BYTES,
  SAB_LEN,
  SAB_STATUS,
  STATUS_CANCELLED,
  STATUS_READY,
  STATUS_WAITING,
  type WorkerInbound,
  type WorkerOutbound,
} from "@/lib/languages/c/runtimeProtocol";

/**
 * Main-thread C runtime adapter. Owns the worker (`c.worker.ts`, which loads clang+lld
 * and compiles/links/runs C in-browser) and the SharedArrayBuffer used to feed one line
 * of stdin to a blocked `scanf`/`fgets`/`getchar`. Operations are serialized — one program
 * at a time — matching the IDE disabling Run/Submit while busy.
 *
 * Structurally a port of src/lib/languages/python/runtime.ts, with one deliberate
 * difference: a compiled WASM program can't be interrupted cooperatively (no SIGINT/
 * interrupt buffer like Pyodide), so cancellation of a CPU-bound run TERMINATES and
 * recreates the worker. An input wait is released first via STATUS_CANCELLED when isolated.
 *
 * All browser APIs (Worker, SharedArrayBuffer) are touched only inside methods, so this
 * module is import-safe from server components (the registry can import it).
 */
class CRuntime implements RuntimeAdapter {
  private worker: Worker | null = null;
  private inputControl: Int32Array | null = null;
  private inputData: Uint8Array | null = null;
  private loaded = false;
  private loadingPromise: Promise<void> | null = null;
  private handler: ((msg: WorkerOutbound) => void) | null = null;
  private opLock: Promise<unknown> = Promise.resolve();

  isLoaded(): boolean {
    return this.loaded;
  }

  /** Whether interactive stdin is available (needs cross-origin isolation for the SAB). */
  get isInteractive(): boolean {
    return this.inputControl !== null;
  }

  private ensureWorker(): void {
    if (this.worker) return;

    const worker = new Worker(new URL("./c.worker.ts", import.meta.url));
    worker.onmessage = (event: MessageEvent<WorkerOutbound>) => {
      this.handler?.(event.data);
    };
    this.worker = worker;

    let inputSab: SharedArrayBuffer | undefined;
    if (typeof SharedArrayBuffer !== "undefined" && globalThis.crossOriginIsolated) {
      inputSab = new SharedArrayBuffer(INPUT_SAB_BYTES);
      this.inputControl = new Int32Array(inputSab, 0, 2);
      this.inputData = new Uint8Array(inputSab, INPUT_DATA_OFFSET);
    }
    this.send({ type: "init", inputSab });
  }

  private send(message: WorkerInbound): void {
    this.worker?.postMessage(message);
  }

  load(onProgress?: (message: string) => void): Promise<void> {
    if (this.loaded) return Promise.resolve();
    if (this.loadingPromise) return this.loadingPromise;

    this.loadingPromise = new Promise<void>((resolve, reject) => {
      this.ensureWorker();
      this.handler = (msg) => {
        if (msg.type === "loadProgress") {
          onProgress?.(msg.message);
        } else if (msg.type === "loaded") {
          this.loaded = true;
          this.handler = null;
          resolve();
        } else if (msg.type === "loadError") {
          this.handler = null;
          this.loadingPromise = null;
          reject(new Error(msg.message));
        }
      };
      this.send({ type: "load" });
    });
    return this.loadingPromise;
  }

  async run(options: RunOptions): Promise<RunResult> {
    await this.load();
    return this.enqueue(
      () =>
        new Promise<RunResult>((resolve) => {
          const onAbort = () => this.cancel();
          options.signal?.addEventListener("abort", onAbort, { once: true });

          this.handler = (msg) => {
            switch (msg.type) {
              case "stdout":
                options.onStdout(msg.text);
                break;
              case "stderr":
                options.onStderr(msg.text);
                break;
              case "awaitingInput":
                this.provideInput(options);
                break;
              case "runResult":
                options.signal?.removeEventListener("abort", onAbort);
                this.handler = null;
                resolve({ ok: msg.ok, error: msg.error });
                break;
            }
          };
          this.send({ type: "run", code: options.code });
        }),
    );
  }

  async runTests(options: RunTestsOptions): Promise<SubmitResult> {
    await this.load();
    return this.enqueue(
      () =>
        new Promise<SubmitResult>((resolve) => {
          const onAbort = () => this.cancel();
          options.signal?.addEventListener("abort", onAbort, { once: true });

          this.handler = (msg) => {
            switch (msg.type) {
              case "stdout":
                options.onStdout?.(msg.text);
                break;
              case "stderr":
                options.onStderr?.(msg.text);
                break;
              case "testResult":
                options.signal?.removeEventListener("abort", onAbort);
                this.handler = null;
                resolve({ results: msg.results, allPassed: msg.allPassed, error: msg.error });
                break;
            }
          };
          this.send({ type: "runTests", code: options.code, tests: options.tests });
        }),
    );
  }

  /** Resolve the program's stdin request with a line from the caller (or EOF on failure). */
  private provideInput(options: RunOptions): void {
    if (!options.onInput) {
      this.writeInput(null);
      return;
    }
    options.onInput("").then(
      (line) => this.writeInput(line),
      () => this.writeInput(null),
    );
  }

  private writeInput(line: string | null): void {
    if (!this.inputControl || !this.inputData) return;
    if (line === null) {
      Atomics.store(this.inputControl, SAB_STATUS, STATUS_CANCELLED);
    } else {
      const bytes = new TextEncoder().encode(`${line}\n`);
      const n = Math.min(bytes.length, INPUT_CAPACITY);
      this.inputData.set(bytes.subarray(0, n));
      Atomics.store(this.inputControl, SAB_LEN, n);
      Atomics.store(this.inputControl, SAB_STATUS, STATUS_READY);
    }
    Atomics.notify(this.inputControl, SAB_STATUS);
  }

  /** Stop a running program. No cooperative interrupt for WASM, so terminate the worker. */
  private cancel(): void {
    if (this.inputControl && Atomics.load(this.inputControl, SAB_STATUS) === STATUS_WAITING) {
      // Release a blocked stdin read gracefully before tearing the worker down.
      Atomics.store(this.inputControl, SAB_STATUS, STATUS_CANCELLED);
      Atomics.notify(this.inputControl, SAB_STATUS);
    }
    this.terminate();
  }

  private terminate(): void {
    this.worker?.terminate();
    this.worker = null;
    this.inputControl = null;
    this.inputData = null;
    this.loaded = false;
    this.loadingPromise = null;
    this.handler = null;
  }

  /** Run operations strictly one after another. */
  private enqueue<T>(op: () => Promise<T>): Promise<T> {
    const result = this.opLock.then(op, op);
    this.opLock = result.then(
      () => undefined,
      () => undefined,
    );
    return result;
  }
}

export const cRuntime: RuntimeAdapter = new CRuntime();
