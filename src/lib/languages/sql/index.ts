import type { Language } from "@/lib/languages/types";
import { sqlConfig } from "@/lib/languages/sql/config";
import { sqlRuntime } from "@/lib/languages/sql/runtime";
import { sqlLinter } from "@/lib/languages/sql/linter";
import { sqlErrorExplainer } from "@/lib/languages/sql/errorExplainer";

/**
 * The concrete SQL language, assembled from its adapters.
 *
 * REGISTERED (S3): `sql` is in src/lib/languages/registry.ts, so the homepage card,
 * nav, course outline, `/cheatsheet/sql`, and inline `<Runnable>` all surface it. The
 * temporary `/dev/ide-sql` harness that proved the results-grid runtime (the way
 * Python's IDE was proven on `/dev/ide` and C's on `/dev/ide-c`) was removed in S4.
 * See docs/sql-integration-plan.md.
 */
export const sql: Language = {
  config: sqlConfig,
  runtime: sqlRuntime,
  linter: sqlLinter,
  errorExplainer: sqlErrorExplainer,
};
