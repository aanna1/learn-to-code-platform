"use client";

import "@xterm/xterm/css/xterm.css";
import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
} from "react";
import type { Terminal as XTerm } from "@xterm/xterm";
import type { FitAddon } from "@xterm/addon-fit";
import type { Theme } from "@/lib/theme";

export interface TerminalHandle {
  write: (text: string) => void;
  writeError: (text: string) => void;
  clear: () => void;
  /** Resolves with one line when the user presses Enter; rejects if cancelled. */
  readLine: () => Promise<string>;
  /** Abort a pending readLine (e.g. the program was stopped). */
  cancelInput: () => void;
  focus: () => void;
}

interface TerminalProps {
  theme: Theme;
}

function xtermTheme(theme: Theme) {
  return theme === "dark"
    ? { background: "#212632", foreground: "#EDE8DE", cursor: "#7AB8AC", selectionBackground: "#3a3f4f" }
    : { background: "#FCFAF5", foreground: "#29323C", cursor: "#4E968A", selectionBackground: "#dfeae6" };
}

const RED = "\x1b[31m";
const RESET = "\x1b[0m";

export const Terminal = forwardRef<TerminalHandle, TerminalProps>(function Terminal(
  { theme },
  ref,
) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const termRef = useRef<XTerm | null>(null);
  const fitRef = useRef<FitAddon | null>(null);

  // Interactive input state.
  const inputModeRef = useRef(false);
  const bufferRef = useRef("");
  const resolveRef = useRef<((line: string) => void) | null>(null);
  const rejectRef = useRef<((reason?: unknown) => void) | null>(null);

  useEffect(() => {
    let disposed = false;
    let resizeObserver: ResizeObserver | null = null;

    (async () => {
      const [{ Terminal: XTermCtor }, { FitAddon: FitAddonCtor }] = await Promise.all([
        import("@xterm/xterm"),
        import("@xterm/addon-fit"),
      ]);
      if (disposed || !containerRef.current) return;

      const term = new XTermCtor({
        convertEol: true,
        cursorBlink: true,
        fontFamily: 'ui-monospace, "SF Mono", "Cascadia Code", "Fira Code", monospace',
        fontSize: 13,
        theme: xtermTheme(theme),
        scrollback: 2000,
      });
      const fit = new FitAddonCtor();
      term.loadAddon(fit);
      term.open(containerRef.current);
      fit.fit();

      term.onData((data) => handleData(data, term));

      termRef.current = term;
      fitRef.current = fit;

      resizeObserver = new ResizeObserver(() => {
        try {
          fit.fit();
        } catch {
          // container momentarily zero-sized during layout — ignore.
        }
      });
      resizeObserver.observe(containerRef.current);
    })();

    return () => {
      disposed = true;
      resizeObserver?.disconnect();
      rejectRef.current?.(new Error("Terminal unmounted"));
      termRef.current?.dispose();
      termRef.current = null;
      fitRef.current = null;
    };
    // Mount once; theme updates handled in a separate effect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Live theme updates without recreating the terminal.
  useEffect(() => {
    if (termRef.current) termRef.current.options.theme = xtermTheme(theme);
  }, [theme]);

  function endInput(term: XTerm) {
    inputModeRef.current = false;
    const line = bufferRef.current;
    bufferRef.current = "";
    term.write("\r\n");
    const resolve = resolveRef.current;
    resolveRef.current = null;
    rejectRef.current = null;
    resolve?.(line);
  }

  function handleData(data: string, term: XTerm) {
    if (!inputModeRef.current) return;
    for (const ch of data) {
      if (ch === "\r" || ch === "\n") {
        endInput(term);
        return;
      }
      if (ch === "\x7f" || ch === "\b") {
        if (bufferRef.current.length > 0) {
          bufferRef.current = bufferRef.current.slice(0, -1);
          term.write("\b \b");
        }
        continue;
      }
      // Skip other control characters; echo printable input.
      if (ch >= " ") {
        bufferRef.current += ch;
        term.write(ch);
      }
    }
  }

  useImperativeHandle(ref, () => ({
    write: (text: string) => termRef.current?.write(text),
    writeError: (text: string) => termRef.current?.write(`${RED}${text}${RESET}`),
    clear: () => termRef.current?.clear(),
    readLine: () =>
      new Promise<string>((resolve, reject) => {
        if (!termRef.current) {
          reject(new Error("Terminal not ready"));
          return;
        }
        inputModeRef.current = true;
        bufferRef.current = "";
        resolveRef.current = resolve;
        rejectRef.current = reject;
        termRef.current.focus();
      }),
    cancelInput: () => {
      if (inputModeRef.current) {
        inputModeRef.current = false;
        bufferRef.current = "";
        const reject = rejectRef.current;
        resolveRef.current = null;
        rejectRef.current = null;
        reject?.(new Error("Input cancelled"));
      }
    },
    focus: () => termRef.current?.focus(),
  }));

  return (
    <div className="h-full w-full overflow-hidden bg-surface p-2">
      <div ref={containerRef} className="h-full w-full" aria-label="Program output terminal" />
    </div>
  );
});
