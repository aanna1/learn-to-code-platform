import Link from "next/link";
import { getAllLanguages } from "@/lib/languages/registry";

/**
 * Homepage. This is a Phase 1 placeholder that proves the page is driven by the
 * language registry — the card grid maps over getAllLanguages() with zero
 * hardcoded language references. The polished landing page (hero copy, nav, theme
 * toggle) lands in Phase 5; the registry-driven structure here is what carries
 * forward. The /learn/<id> links resolve once those routes exist (Phase 3/5).
 */
export default function HomePage() {
  const languages = getAllLanguages();

  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Learn to Code</h1>
      <p className="mt-3 max-w-prose text-muted">
        A free, friendly place to start programming from zero. Read a short lesson,
        then run real code right here in your browser — no installs, no accounts.
      </p>

      <h2 className="mt-12 text-sm font-semibold uppercase tracking-wide text-muted">
        Choose a language
      </h2>
      <ul className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {languages.map((language) => (
          <li key={language.config.id}>
            <Link
              href={`/learn/${language.config.id}`}
              className="block rounded-lg border border-border bg-surface p-5 shadow-soft transition hover:shadow-lift hover:-translate-y-0.5"
            >
              <div className="flex items-center gap-3">
                <span
                  className="grid h-10 w-10 place-items-center rounded-md font-mono text-sm font-bold text-white"
                  style={{ backgroundColor: `rgb(${language.config.accentRgb})` }}
                >
                  {language.config.icon}
                </span>
                <span className="text-lg font-semibold">
                  {language.config.displayName}
                </span>
              </div>
              <p className="mt-3 text-sm text-muted">{language.config.tagline}</p>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
