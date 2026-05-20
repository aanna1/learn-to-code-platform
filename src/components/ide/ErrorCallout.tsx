import type { ErrorExplanation, RuntimeError } from "@/lib/languages/types";

interface ErrorCalloutProps {
  error: RuntimeError;
  explanation: ErrorExplanation | null;
}

/**
 * Shows a runtime error's traceback plus a beginner-friendly explanation when
 * one is known. All fields are rendered as escaped text (never as HTML), since
 * tracebacks contain user-controlled content.
 */
export function ErrorCallout({ error, explanation }: ErrorCalloutProps) {
  return (
    <div role="alert" className="rounded-md border border-danger/40 bg-danger/10 p-4 text-sm">
      <p className="font-semibold text-danger">
        {explanation?.title ?? (error.type ? `${error.type}` : "Something went wrong")}
      </p>

      <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap rounded bg-surface-raised p-3 font-mono text-xs text-text">
        {error.traceback}
      </pre>

      {explanation ? (
        <div className="mt-3 space-y-1.5 text-text">
          <p>{explanation.explanation}</p>
          <p>
            <span className="font-semibold">How to fix it: </span>
            {explanation.fix}
          </p>
        </div>
      ) : null}
    </div>
  );
}
