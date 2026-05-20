/**
 * Theme constants and the pre-paint init script. Kept in a plain (non-client)
 * module so the server root layout can import the script string without pulling
 * in a client boundary.
 */

/** localStorage key for the saved theme preference. */
export const THEME_STORAGE_KEY = "ltcp:v1:theme";

/**
 * Inline script that runs before first paint to set the theme class, preventing
 * a flash of the wrong theme. Injected as a raw <script> in the root layout.
 * Mirrors the logic in ThemeProvider; keep the storage key in sync.
 */
export const themeInitScript = `(function(){try{var k='${THEME_STORAGE_KEY}';var s=localStorage.getItem(k);var d=s?s==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;var r=document.documentElement;r.classList.toggle('dark',d);r.style.colorScheme=d?'dark':'light';}catch(e){}})();`;
