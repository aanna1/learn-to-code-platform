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
  INTERRUPT_SIGINT,
  SAB_LEN,
  SAB_STATUS,
  STATUS_CANCELLED,
  STATUS_READY,
  STATUS_WAITING,
  type WorkerInbound,
  type WorkerOutbound,
} from "@/lib/languages/python/runtimeProtocol";

/**
 * Main-thread Pyodide adapter. Owns the worker and the SharedArrayBuffers used
 * to pass input lines (and an interrupt signal) into the worker. Operations are
 * serialized — one program runs at a time — which matches the IDE disabling
 * Run/Submit while busy. All browser APIs (Worker, SharedArrayBuffer) are touched
 * only inside methods, so this module is safe to import from server components.
 */
class PythonRuntime implements RuntimeAdapter {
  private worker: Worker | null = null;
  private inputControl: Int32Array | null = null;
  private inputData: Uint8Array | null = null;
  private interrupt: Uint8Array | null = null;
  private loaded = false;
  private loadingPromise: Promise<void> | null = null;
  private handler: ((msg: WorkerOutbound) => void) | null = null;
  private opLock: Promise<unknown> = Promise.resolve();

  isLoaded(): boolean {
    return this.loaded;
  }

  /** Whether interactive input() and mid-run interrupt are available (needs isolation). */
  get isInteractive(): boolean {
    return this.inputControl !== null;
  }

  private ensureWorker(): void {
    if (this.worker) return;

    const worker = new Worker(new URL("./pyodide.worker.ts", import.meta.url));
    worker.onmessage = (event: MessageEvent<WorkerOutbound>) => {
      this.handler?.(event.data);
    };
    this.worker = worker;

    let inputSab: SharedArrayBuffer | undefined;
    let interruptSab: SharedArrayBuffer | undefined;
    if (typeof SharedArrayBuffer !== "undefined" && globalThis.crossOriginIsolated) {
      inputSab = new SharedArrayBuffer(INPUT_SAB_BYTES);
      interruptSab = new SharedArrayBuffer(1);
      this.inputControl = new Int32Array(inputSab, 0, 2);
      this.inputData = new Uint8Array(inputSab, INPUT_DATA_OFFSET);
      this.interrupt = new Uint8Array(interruptSab);
    }
    this.send({ type: "init", inputSab, interruptSab });
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
                resolve({
                  results: msg.results,
                  allPassed: msg.allPassed,
                  error: msg.error,
                });
                break;
            }
          };
          this.send({ type: "runTests", code: options.code, tests: options.tests });
        }),
    );
  }

  /** Resolve the program's input() request with a line from the caller (or EOF on failure). */
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

  /** Stop a running program: interrupt CPU-bound code, and unblock any input wait. */
  private cancel(): void {
    if (this.interrupt) {
      this.interrupt[0] = INTERRUPT_SIGINT;
    }
    if (this.inputControl && Atomics.load(this.inputControl, SAB_STATUS) === STATUS_WAITING) {
      Atomics.store(this.inputControl, SAB_STATUS, STATUS_CANCELLED);
      Atomics.notify(this.inputControl, SAB_STATUS);
    }
    if (!this.interrupt) {
      // No isolation: the only reliable kill switch is terminating the worker.
      this.terminate();
    }
  }

  private terminate(): void {
    this.worker?.terminate();
    this.worker = null;
    this.inputControl = null;
    this.inputData = null;
    this.interrupt = null;
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

export const pythonRuntime = new PythonRuntime();
