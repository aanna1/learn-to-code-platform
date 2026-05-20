import type { LanguageDisplayConfig } from "@/lib/languages/types";

export const pythonConfig: LanguageDisplayConfig = {
  id: "python",
  displayName: "Python",
  tagline: "A friendly first language. Clear to read, quick to run, and used everywhere.",
  monacoLanguageId: "python",
  fileExtension: ".py",
  // Python's brand blue/yellow, warmed slightly to fit the palette.
  accentRgb: "78 150 138",
  icon: "Py",
};
