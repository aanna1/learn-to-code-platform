"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export interface MobileNavLink {
  href: string;
  label: string;
}

/**
 * Hamburger menu for narrow screens (the desktop links are hidden below md). It's
 * a client island so it can manage open/closed state, close on Esc, on outside
 * click, and after navigating. Links are passed in as plain data so this bundle
 * never imports the language modules.
 */
export function MobileNav({ links }: { links: MobileNavLink[] }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <div className="md:hidden">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label="Menu"
        aria-expanded={open}
        aria-controls="mobile-menu"
        className="grid h-9 w-9 place-items-center rounded-md text-muted transition hover:bg-surface-raised hover:text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
      >
        <svg
          viewBox="0 0 24 24"
          className="h-5 w-5"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          aria-hidden
        >
          {open ? (
            <path d="M6 6l12 12M18 6L6 18" />
          ) : (
            <path d="M3 6h18M3 12h18M3 18h18" />
          )}
        </svg>
      </button>

      {open ? (
        <>
          {/* Outside-click backdrop */}
          <button
            type="button"
            aria-hidden
            tabIndex={-1}
            onClick={() => setOpen(false)}
            className="fixed inset-0 z-40 cursor-default"
          />
          <div
            id="mobile-menu"
            className="absolute right-2 top-14 z-50 w-52 rounded-lg border border-border bg-surface p-1.5 shadow-lift"
          >
            <nav className="flex flex-col">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="rounded-md px-3 py-2 text-sm text-text transition hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>
        </>
      ) : null}
    </div>
  );
}
