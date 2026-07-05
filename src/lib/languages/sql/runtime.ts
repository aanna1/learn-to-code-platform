import type {
  RunOptions,
  RunResult,
  RunTestsOptions,
  RuntimeAdapter,
  SubmitResult,
} from "@/lib/languages/types";
import type { WorkerInbound, WorkerOutbound } from "@/lib/languages/sql/runtimeProtocol";

/**
 * Main-thread SQL runtime adapter. Owns the worker (`sql.worker.ts`, which loads
 * sql.js and runs SQLite in-browser) and serializes operations — one program at a
 * time — matching the IDE disabling Run/Submit while busy.
 *
 * Structurally a slimmed-down port of src/lib/languages/c/runtime.ts. SQL is
 * simpler than Python/C in two ways:
 *   - No SharedArrayBuffer / interactive stdin: queries return tables, so `run()`
 *     resolves with `resultSets` and never calls `onStdout`/`onInput`.
 *   - Cancellation TERMINATES the worker (SQLite has no cooperative interrupt) —
 *     the same approach C uses for a CPU-bound run.
 *
 * All browser APIs (Worker) are touched only inside methods, so this module is
 * import-safe from server components (the registry can import it).
 */
class SqlRuntime implements RuntimeAdapter {
  private worker: Worker | null = null;
  private loaded = false;
  private loadingPromise: Promise<void> | null = null;
  private handler: ((msg: WorkerOutbound) => void) | null = null;
  private opLock: Promise<unknown> = Promise.resolve();

  isLoaded(): boolean {
    return this.loaded;
  }

  private ensureWorker(): void {
    if (this.worker) return;
    const worker = new Worker(new URL("./sql.worker.ts", import.meta.url));
    worker.onmessage = (event: MessageEvent<WorkerOutbound>) => {
      this.handler?.(event.data);
    };
    this.worker = worker;
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
            if (msg.type === "runResult") {
              options.signal?.removeEventListener("abort", onAbort);
              this.handler = null;
              resolve({ ok: msg.ok, error: msg.error, resultSets: msg.resultSets });
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
            if (msg.type === "testResult") {
              options.signal?.removeEventListener("abort", onAbort);
              this.handler = null;
              resolve({ results: msg.results, allPassed: msg.allPassed, error: msg.error });
            }
          };
          this.send({ type: "runTests", code: options.code, tests: options.tests });
        }),
    );
  }

  /** Stop a running query. SQLite can't be interrupted cooperatively, so terminate the worker. */
  private cancel(): void {
    this.terminate();
  }

  private terminate(): void {
    this.worker?.terminate();
    this.worker = null;
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

export const sqlRuntime: RuntimeAdapter = new SqlRuntime();
