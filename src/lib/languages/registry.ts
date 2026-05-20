import type { Language } from "@/lib/languages/types";
import { python } from "@/lib/languages/python";

/**
 * The language registry. This is the ONLY place languages are listed. The
 * homepage, nav, course routes, and static-param generation all read from here,
 * so adding a language is: implement the Language interface, import it, add it to
 * this array. No component or route changes.
 */
const LANGUAGES: readonly Language[] = [python];

const BY_ID: ReadonlyMap<string, Language> = new Map(
  LANGUAGES.map((language) => [language.config.id, language]),
);

/** Every registered language, in display order. */
export function getAllLanguages(): readonly Language[] {
  return LANGUAGES;
}

/** Look up a language by its id (the `[language]` URL segment). */
export function getLanguage(id: string): Language | undefined {
  return BY_ID.get(id);
}

/** Whether a language id is registered. */
export function hasLanguage(id: string): boolean {
  return BY_ID.has(id);
}

/** All registered language ids — used to pre-render `[language]` routes. */
export function getLanguageIds(): string[] {
  return LANGUAGES.map((language) => language.config.id);
}
