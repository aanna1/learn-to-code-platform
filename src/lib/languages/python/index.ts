import type { Language } from "@/lib/languages/types";
import { pythonConfig } from "@/lib/languages/python/config";
import { pythonRuntime } from "@/lib/languages/python/runtime";
import { pythonLinter } from "@/lib/languages/python/linter";
import { pythonErrorExplainer } from "@/lib/languages/python/errorExplainer";

/** The concrete Python language, assembled from its adapters. */
export const python: Language = {
  config: pythonConfig,
  runtime: pythonRuntime,
  linter: pythonLinter,
  errorExplainer: pythonErrorExplainer,
};
