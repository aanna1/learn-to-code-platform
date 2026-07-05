import type { QueryResultSet } from "@/lib/languages/types";

interface ResultsGridProps {
  /** null = nothing run yet (idle). An array = the last run's result sets. */
  results: QueryResultSet[] | null;
  /** True while a query is executing, for a lightweight in-pane hint. */
  running?: boolean;
}

/**
 * The grid output surface for `outputMode: "grid"` languages (SQL). Renders each
 * QueryResultSet as a plain HTML table — sticky header, monospace cells, NULL
 * styling, right-aligned numeric columns, a "N rows" footer — with idle, running,
 * empty-set, and summary-only (DDL/DML) states. Each table's bordered box
 * scrolls horizontally (overflow-x-auto) so wide result sets stay usable on
 * narrow screens instead of being clipped. No dependency, no browser APIs.
 *
 * Note: below `md` the whole IDE (and this grid) is hidden by <ExercisePane>,
 * which shows a "read this lesson on a wider screen" message on phones — so this
 * component only needs to stay usable from the md breakpoint up.
 *
 * The IDE's `<Terminal>` analogue: `<Ide>` mounts one or the other based on
 * `language.config.outputMode`. Errors are shown by `<ErrorCallout>` in the
 * feedback pane, not here, so this component only ever renders successful output.
 */
export function ResultsGrid({ results, running }: ResultsGridProps) {
  return (
    <div
      className="h-full w-full overflow-auto bg-surface p-3"
      role="region"
      aria-label="Query results"
      aria-live="polite"
    >
      {running ? (
        <p className="p-2 text-sm text-muted">Running…</p>
      ) : results === null ? (
        <p className="p-2 text-sm text-muted">
          Press <span className="font-medium text-text">Run</span> to execute your SQL and see the
          results here.
        </p>
      ) : results.length === 0 ? (
        <p className="p-2 text-sm text-muted">No results.</p>
      ) : (
        <div className="space-y-4">
          {results.map((rs, index) => (
            <ResultSetTable key={index} rs={rs} label={results.length > 1 ? index + 1 : null} />
          ))}
        </div>
      )}
    </div>
  );
}

function ResultSetTable({ rs, label }: { rs: QueryResultSet; label: number | null }) {
  // A summary-only result set (no columns): a DDL/DML statement that returned no rows.
  if (rs.columns.length === 0) {
    return (
      <div className="text-sm text-muted">
        {label !== null ? <p className="mb-1 text-xs font-medium uppercase tracking-wide">Statement {label}</p> : null}
        <p>{rs.summary ?? "Statement executed successfully."}</p>
      </div>
    );
  }

  const numericColumns = rs.columns.map((_col, colIndex) =>
    rs.rows.length > 0 &&
    rs.rows.every((row) => {
      const cell = row[colIndex];
      return cell === null || cell === undefined || typeof cell === "number";
    }),
  );

  return (
    <div>
      {label !== null ? (
        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted">Result {label}</p>
      ) : null}
      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full border-collapse font-mono text-sm">
          <thead>
            <tr className="bg-surface-raised">
              {rs.columns.map((col, colIndex) => (
                <th
                  key={colIndex}
                  scope="col"
                  className={`sticky top-0 whitespace-nowrap border-b border-border bg-surface-raised px-3 py-2 font-semibold text-text ${
                    numericColumns[colIndex] ? "text-right" : "text-left"
                  }`}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rs.rows.length === 0 ? (
              <tr>
                <td colSpan={rs.columns.length} className="px-3 py-3 text-center text-muted">
                  No rows.
                </td>
              </tr>
            ) : (
              rs.rows.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b border-border/60 last:border-b-0">
                  {rs.columns.map((_col, colIndex) => (
                    <td
                      key={colIndex}
                      className={`whitespace-nowrap px-3 py-1.5 text-text ${
                        numericColumns[colIndex] ? "text-right" : "text-left"
                      }`}
                    >
                      <Cell value={row[colIndex]} />
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <p className="mt-1.5 text-xs text-muted">
        {rs.rows.length} row{rs.rows.length === 1 ? "" : "s"}
      </p>
    </div>
  );
}

function Cell({ value }: { value: unknown }) {
  if (value === null || value === undefined) {
    return <span className="italic text-muted">NULL</span>;
  }
  if (value instanceof Uint8Array) {
    return <span className="italic text-muted">{`«blob, ${value.length} bytes»`}</span>;
  }
  return <>{String(value)}</>;
}
