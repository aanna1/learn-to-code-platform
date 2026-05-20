"use client";

import { createContext, useContext, type ReactNode } from "react";

/**
 * Carries the current lesson's language id down to inline MDX components like
 * <Runnable>, so an MDX author never has to repeat `languageId="python"` on every
 * runnable block. The lesson page wraps its rendered MDX in this provider; the
 * server-rendered MDX passes straight through as children.
 */
const LessonLanguageContext = createContext<string | null>(null);

export function LessonLanguageProvider({
  languageId,
  children,
}: {
  languageId: string;
  children: ReactNode;
}) {
  return (
    <LessonLanguageContext.Provider value={languageId}>{children}</LessonLanguageContext.Provider>
  );
}

/** The language id from the nearest provider, or null outside a lesson. */
export function useLessonLanguage(): string | null {
  return useContext(LessonLanguageContext);
}
