"use client";

import { useCallback, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorCallout } from "@/components/ide/ErrorCallout";
import { getLanguage } from "@/lib/languages/registry";
import { useLessonLanguage } from "@/components/lesson/LessonLanguageProvider";
import type { RuntimeError } from "@/lib/languages/types";

interface RunnableProps {
  /** Initial source shown in the editor. */
  code: string;
  /** Overrides the lesson language; defaults to the surrounding lesson's language. */
  languageId?: string;
}

type Status = "idle" | "loading" | "ready";

const TAB = "    ";

/**
 * Inline, editable, runnable code block for lectures. It uses the same runtime as
 * the full IDE (so Python actually executes in the browser) but has no tests,
 * linting, or submission — just edit and run. Kept deliberately small and visually
 * distinct from static code blocks via the accent stripe.
 */
export function Runnable({ code, languageId }: RunnableProps) {
  const contextLanguage = useLessonLanguage();
  const resolvedId = languageId ?? contextLanguage ?? "";
  const language = getLanguage(resolvedId);

  const initial = useMemo(() => code.replace(/\n+$/, ""), [code]);
  const [source, setSource] = useState(initial);
  const [output, setOutput] = useState("");
  const [hasRun, setHasRun] = useState(false);
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [loadMessage, setLoadMessage] = useState("");
  const [error, setError] = useState<RuntimeError | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const busyRef = useRef(false);

  const handleRun = useCallback(async () => {
    if (!language || busyRef.current) return;
    busyRef.current = true;
    setRunning(true);
    setHasRun(true);
    setOutput("");
    setError(null);
    try {
      if (!language.runtime.isLoaded()) {
        setStatus("loading");
        await language.runtime.load((message) => setLoadMessage(message));
      }
      setStatus("ready");
      const controller = new AbortController();
      abortRef.current = controller;
      const result = await language.runtime.run({
        code: source,
        onStdout: (text) => setOutput((prev) => prev + text),
        onStderr: (text) => setOutput((prev) => prev + text),
        onInput: (prompt) => Promise.resolve(window.prompt(prompt) ?? ""),
        signal: controller.signal,
      });
      if (!result.ok && result.error) setError(result.error);
    } catch (err) {
      setOutput((prev) => prev + `\n${String((err as Error)?.message ?? err)}\n`);
    } finally {
      abortRef.current = null;
      busyRef.current = false;
      setRunning(false);
    }
  }, [language, source]);

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const handleReset = useCallback(() => {
    setSource(initial);
    setOutput("");
    setError(null);
    setHasRun(false);
  }, [initial]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        void handleRun();
        return;
      }
      if (event.key === "Tab") {
        event.preventDefault();
        const target = event.currentTarget;
        const { selectionStart, selectionEnd } = target;
        const next = source.slice(0, selectionStart) + TAB + source.slice(selectionEnd);
        setSource(next);
        requestAnimationFrame(() => {
          target.selectionStart = target.selectionEnd = selectionStart + TAB.length;
        });
      }
    },
    [handleRun, source],
  );

  if (!language) {
    return (
      <p className="my-4 rounded-md border border-danger/40 bg-danger/10 p-3 text-sm text-danger">
        Runnable block has no language to run with.
      </p>
    );
  }

  const explanation = error ? language.errorExplainer.explain(error) : null;
  const rows = Math.min(Math.max(source.split("\n").length, 3), 20);

  return (
    <div className="my-5 overflow-hidden rounded-md border border-border border-l-4 border-l-accent bg-surface">
      <div className="flex items-center gap-2 border-b border-border bg-surface-raised px-3 py-1.5">
        <span className="text-xs font-semibold uppercase tracking-wide text-accent-strong">
          Try it
        </span>
        <span className="text-xs text-muted">{language.config.displayName}</span>
        <div className="ml-auto flex items-center gap-2">
          {status === "loading" ? (
            <span className="flex items-center gap-1.5 text-xs text-muted">
              <Spinner /> {loadMessage || "Loading…"}
            </span>
          ) : null}
          {running ? (
            <Button variant="danger" size="sm" onClick={handleStop}>
              Stop
            </Button>
          ) : null}
          {hasRun && !running ? (
            <Button variant="ghost" size="sm" onClick={handleReset}>
              Reset
            </Button>
          ) : null}
          <Button variant="primary" size="sm" onClick={handleRun} loading={running}>
            Run
          </Button>
        </div>
      </div>

      <textarea
        value={source}
        onChange={(event) => setSource(event.target.value)}
        onKeyDown={handleKeyDown}
        rows={rows}
        spellCheck={false}
        autoCapitalize="off"
        autoCorrect="off"
        aria-label={`Editable ${language.config.displayName} code`}
        className="block w-full resize-y bg-surface p-3 font-mono text-sm leading-relaxed text-text outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent"
      />

      {hasRun ? (
        <div className="border-t border-border p-3">
          <pre className="max-h-56 overflow-auto whitespace-pre-wrap font-mono text-sm text-text">
            {output || <span className="text-muted">(no output)</span>}
          </pre>
          {error ? (
            <div className="mt-3">
              <ErrorCallout error={error} explanation={explanation} />
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
