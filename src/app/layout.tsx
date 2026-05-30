import type { Metadata } from "next";
import Script from "next/script";
import "@/app/globals.css";
import { ThemeProvider } from "@/lib/theme/ThemeProvider";
import { themeInitScript } from "@/lib/theme/script";
import { SiteHeader } from "@/components/nav/SiteHeader";

export const metadata: Metadata = {
  title: "Learn to Code",
  description:
    "A free, friendly place to learn programming from zero — read a lesson, then run real code right in your browser.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // GitHub Pages can't set COOP/COEP headers, so register the coi-serviceworker
  // shim from the static asset path. NEXT_PUBLIC_BASE_PATH is set in
  // next.config.mjs so the same path works under and without basePath.
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Sets the theme class before first paint to avoid a flash of the wrong theme. */}
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        {/* Enables cross-origin isolation on hosts (like GitHub Pages) that
            can't send COOP/COEP headers — required for SharedArrayBuffer in
            interactive Pyodide input(). Must run before page scripts so the
            service worker is installed and the page reloads cross-origin
            isolated on first visit. */}
        <Script src={`${basePath}/coi-serviceworker.js`} strategy="beforeInteractive" />
      </head>
      <body className="min-h-screen bg-bg text-text">
        <ThemeProvider>
          <SiteHeader />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
