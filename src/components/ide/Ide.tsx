"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { CodeEditor } from "@/components/ide/CodeEditor";
import { Terminal, type TerminalHandle } from "@/components/ide/Terminal";
import { ResizableSplit } from "@/components/ide/ResizableSplit";
import { ErrorCallout } from "@/components/ide/ErrorCallout";
import { TestResults } from "@/components/ide/TestResults";
import { ShortcutsOverlay } from "@/components/ide/ShortcutsOverlay";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { Modal } from "@/components/ui/Modal";
import { getLanguage } from "@/lib/languages/registry";
import { useTheme } from "@/lib/theme";
import { clearCode, loadCode, saveCode } from "@/lib/progress";
import type { Diagnostic, RuntimeError, SubmitResult } from "@/lib/languages/types";

export interface IdeExercise {
  starter: string;
  solution: string;
  tests: string;
  hints: string[];
}

interface IdeProps {
  languageId: string;
  exercise: IdeExercise;
  /** When provided, code is autosaved/restored per lesson. */
  autosave?: { moduleId: string; lessonId: string };
  /** Called once when all hidden tests pass. */
  onAllTestsPassed?: () => void;
}

type RuntimeStatus = "idle" | "loading" | "ready";

export function Ide({ languageId, exercise, autosave, onAllTestsPassed }: IdeProps) {
  const language = getLanguage(languageId);
  const { theme } = useTheme();

  const [code, setCode] = useState(exercise.starter);
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [status, setStatus] = useState<RuntimeStatus>("idle");
  const [loadMessage, setLoadMessage] = useState("");
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runtimeError, setRuntimeError] = useState<RuntimeError | null>(null);
  const [testResult, setTestResult] = useState<SubmitResult | null>(null);
  const [hintsRevealed, setHintsRevealed] = useState(0);
  const [solved, setSolved] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  const terminalRef = useRef<TerminalHandle>(null);
  const abortRef = useRef<AbortController | null>(null);
  const busyRef = useRef(false);

  const busy = running || submitting;

  // Restore autosaved code on mount (client only, to avoid hydration mismatch).
  useEffect(() => {
    if (!autosave) return;
    const saved = loadCode(languageId, autosave.moduleId, autosave.lessonId);
    if (saved !== null) setCode(saved);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Debounced autosave.
  useEffect(() => {
    if (!autosave) return;
    const handle = window.setTimeout(
      () => saveCode(languageId, autosave.moduleId, autosave.lessonId, code),
      500,
    );
    return () => window.clearTimeout(handle);
  }, [code, autosave, languageId]);

  // Debounced real-time linting.
  useEffect(() => {
    if (!language) return;
    const handle = window.setTimeout(async () => {
      try {
        setDiagnostics(await language.linter.lint(code));
      } catch {
        // linter failures must not interrupt editing
      }
    }, 400);
    return () => window.clearTimeout(handle);
  }, [code, language]);

  const ensureReady = useCallback(async () => {
    if (!language || language.runtime.isLoaded()) {
      setStatus("ready");
      return;
    }
    setStatus("loading");
    await language.runtime.load((message) => setLoadMessage(message));
    setStatus("ready");
  }, [language]);

  const handleRun = useCallback(async () => {
    if (!language || busyRef.current) return;
    busyRef.current = true;
    setRunning(true);
    setRuntimeError(null);
    setTestResult(null);
    try {
      await ensureReady();
      terminalRef.current?.write("\x1b[2m— Running —\x1b[0m\n");
      const controller = new AbortController();
      abortRef.current = controller;
      const result = await language.runtime.run({
        code,
        onStdout: (text) => terminalRef.current?.write(text),
        onStderr: (text) => terminalRef.current?.writeError(text),
        onInput: () =>
          terminalRef.current?.readLine() ?? Promise.reject(new Error("Terminal not ready")),
        signal: controller.signal,
      });
      if (!result.ok && result.error) setRuntimeError(result.error);
    } catch (error) {
      terminalRef.current?.writeError(`\n${String((error as Error)?.message ?? error)}\n`);
    } finally {
      abortRef.current = null;
      busyRef.current = false;
      setRunning(false);
    }
  }, [code, language, ensureReady]);

  const handleSubmit = useCallback(async () => {
    if (!language || busyRef.current) return;
    busyRef.current = true;
    setSubmitting(true);
    setRuntimeError(null);
    setTestResult(null);
    try {
      await ensureReady();
      terminalRef.current?.write("\x1b[2m— Checking your work —\x1b[0m\n");
      const controller = new AbortController();
      abortRef.current = controller;
      const result = await language.runtime.runTests({
        code,
        tests: exercise.tests,
        onStdout: (text) => terminalRef.current?.write(text),
        onStderr: (text) => terminalRef.current?.writeError(text),
        signal: controller.signal,
      });
      setTestResult(result);
      if (result.error) setRuntimeError(result.error);
      if (result.allPassed) {
        setSolved(true);
        onAllTestsPassed?.();
      }
    } catch (error) {
      terminalRef.current?.writeError(`\n${String((error as Error)?.message ?? error)}\n`);
    } finally {
      abortRef.current = null;
      busyRef.current = false;
      setSubmitting(false);
    }
  }, [code, exercise.tests, language, ensureReady, onAllTestsPassed]);

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
    terminalRef.current?.cancelInput();
  }, []);

  const doReset = useCallback(() => {
    setCode(exercise.starter);
    if (autosave) clearCode(languageId, autosave.moduleId, autosave.lessonId);
    setDiagnostics([]);
    setRuntimeError(null);
    setTestResult(null);
    terminalRef.current?.clear();
    setShowResetConfirm(false);
  }, [exercise.starter, autosave, languageId]);

  // Global Run/Submit shortcuts (also work when focus is in the terminal).
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        if (event.shiftKey) void handleSubmit();
        else void handleRun();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [handleRun, handleSubmit]);

  if (!language) {
    return <p className="p-4 text-danger">Unknown language: {languageId}</p>;
  }

  const hints = exercise.hints;
  const allHintsShown = hintsRevealed >= hints.length;
  const solutionAvailable = solved || (hints.length > 0 && allHintsShown);
  const explanation = runtimeError ? language.errorExplainer.explain(runtimeError) : null;
  const hasFeedback = hintsRevealed > 0 || runtimeError !== null || testResult !== null;

  return (
    <div className="flex h-full min-h-0 flex-col rounded-lg border border-border bg-surface">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2 border-b border-border p-2.5">
        <Button variant="primary" onClick={handleRun} loading={running} disabled={submitting}>
          Run
        </Button>
        <Button variant="secondary" onClick={handleSubmit} loading={submitting} disabled={running}>
          Submit
        </Button>
        {busy ? (
          <Button variant="danger" onClick={handleStop}>
            Stop
          </Button>
        ) : null}

        <div className="ml-auto flex flex-wrap items-center gap-2">
          {status === "loading" ? (
            <span className="flex items-center gap-2 text-sm text-muted">
              <Spinner /> {loadMessage || "Loading…"}
            </span>
          ) : null}
          {hints.length > 0 && !allHintsShown ? (
            <Button variant="ghost" size="sm" onClick={() => setHintsRevealed((n) => n + 1)}>
              {hintsRevealed === 0 ? "Stuck? Show a hint" : "Show another hint"}
            </Button>
          ) : null}
          {solutionAvailable ? (
            <Button variant="ghost" size="sm" onClick={() => setShowSolution(true)}>
              Show solution
            </Button>
          ) : null}
          <Button variant="ghost" size="sm" onClick={() => setShowResetConfirm(true)}>
            Reset
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowShortcuts(true)}
            aria-label="Keyboard shortcuts"
            title="Keyboard shortcuts"
          >
            ⌨
          </Button>
          <a
            href={`/cheatsheet/${languageId}`}
            className="rounded-md px-3 py-1.5 text-sm text-muted transition hover:bg-surface-raised hover:text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            Cheat sheet
          </a>
        </div>
      </div>

      {/* Editor + terminal split */}
      <div className="min-h-0 flex-1">
        <ResizableSplit
          orientation="vertical"
          initialRatio={0.62}
          className="h-full"
          first={
            <CodeEditor
              value={code}
              onChange={setCode}
              languageId={language.config.monacoLanguageId}
              theme={theme}
              diagnostics={diagnostics}
              onRun={handleRun}
              onSubmit={handleSubmit}
              ariaLabel={`${language.config.displayName} code editor`}
            />
          }
          second={<Terminal ref={terminalRef} theme={theme} />}
        />
      </div>

      {/* Feedback: hints, friendly errors, test results */}
      {hasFeedback ? (
        <div className="max-h-64 shrink-0 space-y-3 overflow-auto border-t border-border p-3">
          {hintsRevealed > 0 ? (
            <div className="rounded-md border border-highlight/40 bg-highlight/10 p-3 text-sm">
              <p className="font-semibold text-highlight-strong">Hints</p>
              <ol className="mt-1.5 list-decimal space-y-1 pl-5">
                {hints.slice(0, hintsRevealed).map((hint, index) => (
                  <li key={index}>{hint}</li>
                ))}
              </ol>
            </div>
          ) : null}
          {testResult ? <TestResults result={testResult} /> : null}
          {runtimeError ? <ErrorCallout error={runtimeError} explanation={explanation} /> : null}
        </div>
      ) : null}

      <ShortcutsOverlay open={showShortcuts} onClose={() => setShowShortcuts(false)} />

      <Modal
        open={showSolution}
        onClose={() => setShowSolution(false)}
        title="Solution"
        widthClass="max-w-2xl"
      >
        <p className="mb-3 text-sm text-muted">
          Try to understand each line rather than copying it — that&apos;s where the learning sticks.
        </p>
        <pre className="max-h-[60vh] overflow-auto rounded-md bg-surface-raised p-4 font-mono text-sm">
          {exercise.solution}
        </pre>
      </Modal>

      <Modal
        open={showResetConfirm}
        onClose={() => setShowResetConfirm(false)}
        title="Reset to starter code?"
        widthClass="max-w-md"
      >
        <p className="text-sm text-muted">
          This discards your current code and restores the original starter code. This can&apos;t be
          undone.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setShowResetConfirm(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={doReset}>
            Reset code
          </Button>
        </div>
      </Modal>
    </div>
  );
}
