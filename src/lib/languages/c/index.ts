import type { Language } from "@/lib/languages/types";
import { cConfig } from "@/lib/languages/c/config";
import { cRuntime } from "@/lib/languages/c/runtime";
import { cLinter } from "@/lib/languages/c/linter";
import { cErrorExplainer } from "@/lib/languages/c/errorExplainer";

/**
 * The concrete C language, assembled from its adapters.
 *
 * NOT YET REGISTERED. Because the homepage, nav, and course routes are registry-driven,
 * adding `c` to src/lib/languages/registry.ts would immediately surface a C card whose
 * Run/Submit throw (the runtime is a Phase-C1 shell). Register it only once the runtime
 * works — or behind a temporary `/dev/ide-c` harness route, the way Python's IDE was
 * proven on `/dev/ide` before going live. See docs/c-integration-plan.md.
 */
export const c: Language = {
  config: cConfig,
  runtime: cRuntime,
  linter: cLinter,
  errorExplainer: cErrorExplainer,
};
