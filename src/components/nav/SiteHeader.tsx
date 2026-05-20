import Link from "next/link";
import { getAllLanguages } from "@/lib/languages/registry";
import { ThemeToggle } from "@/components/nav/ThemeToggle";
import { MobileNav, type MobileNavLink } from "@/components/nav/MobileNav";

/**
 * Global top nav, shown on every page. The links are driven entirely by the
 * language registry — no language is named here, so adding one to the registry
 * adds it to the nav automatically. The cheat-sheet link only appears while a
 * single language is registered (it's per-language; with several, each course's
 * outline links its own). Fixed height (h-14) so full-height pages like the
 * exercise IDE can size themselves with calc(100vh - 3.5rem). Below md the links
 * collapse into a hamburger (MobileNav); the theme toggle stays visible.
 */
export function SiteHeader() {
  const languages = getAllLanguages();
  const soleLanguage = languages.length === 1 ? languages[0] : undefined;

  const navLinks: MobileNavLink[] = [
    { href: "/", label: "Home" },
    ...languages.map((language) => ({
      href: `/learn/${language.config.id}`,
      label: language.config.displayName,
    })),
    ...(soleLanguage
      ? [{ href: `/cheatsheet/${soleLanguage.config.id}`, label: "Cheat sheet" }]
      : []),
  ];

  return (
    <header className="sticky top-0 z-40 h-14 border-b border-border bg-bg/80 backdrop-blur">
      <nav className="mx-auto flex h-full max-w-6xl items-center gap-1 px-4 sm:px-6">
        <Link
          href="/"
          className="mr-2 rounded-md px-2 py-1.5 font-semibold tracking-tight transition hover:text-accent-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
        >
          Learn to Code
        </Link>

        {/* Desktop links */}
        <div className="hidden items-center gap-0.5 md:flex">
          {languages.map((language) => (
            <Link
              key={language.config.id}
              href={`/learn/${language.config.id}`}
              className="rounded-md px-3 py-1.5 text-sm text-muted transition hover:bg-surface-raised hover:text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              {language.config.displayName}
            </Link>
          ))}
          {soleLanguage ? (
            <Link
              href={`/cheatsheet/${soleLanguage.config.id}`}
              className="rounded-md px-3 py-1.5 text-sm text-muted transition hover:bg-surface-raised hover:text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              Cheat sheet
            </Link>
          ) : null}
        </div>

        <div className="ml-auto flex items-center gap-1">
          <ThemeToggle />
          <MobileNav links={navLinks} />
        </div>
      </nav>
    </header>
  );
}
