import type { Metadata } from "next";
import "@/app/globals.css";
import { ThemeProvider } from "@/lib/theme/ThemeProvider";
import { themeInitScript } from "@/lib/theme/script";

export const metadata: Metadata = {
  title: "Learn to Code",
  description:
    "A free, friendly place to learn programming from zero — read a lesson, then run real code right in your browser.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Sets the theme class before first paint to avoid a flash of the wrong theme. */}
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="min-h-screen bg-bg text-text">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
