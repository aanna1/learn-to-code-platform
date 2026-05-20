import Link from "next/link";
import { getAllLanguages } from "@/lib/languages/registry";

/**
 * Landing page. Everything that mentions a language is driven by the registry —
 * the hero CTA points at the first registered language and the card grid maps
 * over all of them, so adding a language needs no change here. Aim per the brief:
 * warm and welcoming for absolute beginners, a little playful, never corporate.
 */
export default function HomePage() {
  const languages = getAllLanguages();
  const firstLanguage = languages[0];

  return (
    <main>
      {/* Hero */}
      <section className="mx-auto max-w-3xl px-6 pb-12 pt-16 text-center sm:pt-24">
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium text-muted">
          Free · runs in your browser · no sign-up
        </span>
        <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-5xl">
          Learn to code, from zero.
        </h1>
        <p className="mx-auto mt-4 max-w-prose text-lg leading-relaxed text-muted">
          Read a short, friendly lesson, then write and run real code right here — no
          installs, no accounts, nothing to set up. Just you and a blinking cursor.
        </p>
        {firstLanguage ? (
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              href={`/learn/${firstLanguage.config.id}`}
              className="inline-flex items-center gap-2 rounded-md bg-accent px-5 py-2.5 font-medium text-white shadow-soft transition hover:bg-accent-strong hover:shadow-lift focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
            >
              Start with {firstLanguage.config.displayName}
            </Link>
            <Link
              href={`/cheatsheet/${firstLanguage.config.id}`}
              className="inline-flex items-center gap-2 rounded-md px-5 py-2.5 font-medium text-text transition hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              Browse the cheat sheet
            </Link>
          </div>
        ) : null}
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-4xl px-6 py-8">
        <ol className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[
            {
              step: "1",
              title: "Read a lesson",
              body: "Plain-English explanations built for people who've never coded.",
            },
            {
              step: "2",
              title: "Run real code",
              body: "An in-browser editor and terminal. Edit, run, and see output instantly.",
            },
            {
              step: "3",
              title: "Check your work",
              body: "Exercises grade themselves, with hints when you get stuck.",
            },
          ].map((item) => (
            <li
              key={item.step}
              className="rounded-lg border border-border bg-surface p-5 shadow-soft"
            >
              <span className="grid h-8 w-8 place-items-center rounded-full bg-highlight/20 font-semibold text-highlight-strong">
                {item.step}
              </span>
              <h3 className="mt-3 font-semibold">{item.title}</h3>
              <p className="mt-1 text-sm text-muted">{item.body}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* Language picker */}
      <section className="mx-auto max-w-4xl px-6 py-10">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
          Choose a language
        </h2>
        <ul className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {languages.map((language) => (
            <li key={language.config.id}>
              <Link
                href={`/learn/${language.config.id}`}
                className="group block rounded-lg border border-border bg-surface p-5 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
              >
                <div className="flex items-center gap-3">
                  <span
                    className="grid h-10 w-10 place-items-center rounded-md font-mono text-sm font-bold text-white"
                    style={{ backgroundColor: `rgb(${language.config.accentRgb})` }}
                  >
                    {language.config.icon}
                  </span>
                  <span className="text-lg font-semibold">{language.config.displayName}</span>
                  <span className="ml-auto text-muted transition group-hover:translate-x-0.5 group-hover:text-accent-strong">
                    →
                  </span>
                </div>
                <p className="mt-3 text-sm text-muted">{language.config.tagline}</p>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
