import type { SubmitResult } from "@/lib/languages/types";

interface TestResultsProps {
  result: SubmitResult;
}

/** Per-test pass/fail summary. Announced to assistive tech via aria-live. */
export function TestResults({ result }: TestResultsProps) {
  const passed = result.results.filter((r) => r.passed).length;
  const total = result.results.length;

  return (
    <div role="status" aria-live="polite" className="rounded-md border border-border bg-surface p-4 text-sm">
      {result.error ? (
        <p className="font-semibold text-danger">
          Your code couldn&apos;t run, so the checks didn&apos;t complete. See the error below.
        </p>
      ) : (
        <p className={`font-semibold ${result.allPassed ? "text-success" : "text-text"}`}>
          {result.allPassed
            ? `All checks passed (${passed}/${total}). Nicely done!`
            : `${passed} of ${total} checks passed. Keep going!`}
        </p>
      )}

      {total > 0 ? (
        <ul className="mt-3 space-y-2">
          {result.results.map((test, index) => (
            <li key={index} className="flex gap-2">
              <span aria-hidden="true" className={test.passed ? "text-success" : "text-danger"}>
                {test.passed ? "✓" : "✗"}
              </span>
              <span>
                <span className="text-text">{test.name}</span>
                {!test.passed && test.message ? (
                  <span className="mt-0.5 block text-muted">{test.message}</span>
                ) : null}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
