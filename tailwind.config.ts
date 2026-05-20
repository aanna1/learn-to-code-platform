import type { Config } from "tailwindcss";

/**
 * Colors are defined as CSS custom properties (see src/app/globals.css) and
 * referenced here via rgb(var(--token) / <alpha-value>). This keeps the palette
 * theme-driven: flipping the `dark` class on <html> swaps every token at once,
 * and components never hardcode a hex value.
 */
const config: Config = {
  darkMode: "class",
  content: [
    "./src/app/**/*.{ts,tsx,md,mdx}",
    "./src/components/**/*.{ts,tsx,md,mdx}",
    "./src/content/**/*.{md,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "rgb(var(--color-bg) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        "surface-raised": "rgb(var(--color-surface-raised) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",
        text: "rgb(var(--color-text) / <alpha-value>)",
        muted: "rgb(var(--color-muted) / <alpha-value>)",
        accent: "rgb(var(--color-accent) / <alpha-value>)",
        "accent-strong": "rgb(var(--color-accent-strong) / <alpha-value>)",
        highlight: "rgb(var(--color-highlight) / <alpha-value>)",
        "highlight-strong": "rgb(var(--color-highlight-strong) / <alpha-value>)",
        danger: "rgb(var(--color-danger) / <alpha-value>)",
        success: "rgb(var(--color-success) / <alpha-value>)",
      },
      borderRadius: {
        lg: "var(--radius-lg)",
        md: "var(--radius-md)",
        sm: "var(--radius-sm)",
      },
      boxShadow: {
        soft: "var(--shadow-soft)",
        lift: "var(--shadow-lift)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
