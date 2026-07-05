import type { LanguageDisplayConfig } from "@/lib/languages/types";

export const sqlConfig: LanguageDisplayConfig = {
  id: "sql",
  displayName: "SQL",
  tagline:
    "The language of data. Ask a database precise questions — and learn why the same questions, asked carelessly, are how systems get breached.",
  // Monaco ships SQL highlighting out of the box.
  monacoLanguageId: "sql",
  fileExtension: ".sql",
  // A database blue-teal, tuned to read against the palette.
  accentRgb: "56 139 168",
  icon: "≡",
  // SQL is the first language whose programs return a *table*, not a text stream,
  // so the IDE shows a results grid instead of the terminal. See <Ide> + <ResultsGrid>.
  outputMode: "grid",
};
