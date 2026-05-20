"use client";

import { useEffect, useRef } from "react";
import Editor, { loader, type Monaco, type OnMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import type { Diagnostic } from "@/lib/languages/types";
import type { Theme } from "@/lib/theme";

// Pin Monaco to a specific version on jsDelivr. jsDelivr serves the
// cross-origin-resource-policy header our COEP require-corp policy needs, so the
// editor and its worker load cleanly under cross-origin isolation.
loader.config({
  paths: { vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs" },
});

const LIGHT_THEME = "ltcp-light";
const DARK_THEME = "ltcp-dark";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  languageId: string;
  theme: Theme;
  diagnostics: Diagnostic[];
  onRun?: () => void;
  onSubmit?: () => void;
  readOnly?: boolean;
  ariaLabel?: string;
}

export function CodeEditor({
  value,
  onChange,
  languageId,
  theme,
  diagnostics,
  onRun,
  onSubmit,
  readOnly = false,
  ariaLabel = "Code editor",
}: CodeEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);

  // Keep shortcut handlers fresh without re-registering Monaco commands.
  const onRunRef = useRef(onRun);
  const onSubmitRef = useRef(onSubmit);
  useEffect(() => {
    onRunRef.current = onRun;
    onSubmitRef.current = onSubmit;
  }, [onRun, onSubmit]);

  const handleMount: OnMount = (editorInstance, monaco) => {
    editorRef.current = editorInstance;
    monacoRef.current = monaco;

    monaco.editor.defineTheme(LIGHT_THEME, {
      base: "vs",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#FCFAF5",
        "editor.foreground": "#29323C",
        "editorLineNumber.foreground": "#9aa39f",
        "editorCursor.foreground": "#4E968A",
        "editor.selectionBackground": "#dfeae6",
        "editor.lineHighlightBackground": "#f0ece2",
      },
    });
    monaco.editor.defineTheme(DARK_THEME, {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#212632",
        "editor.foreground": "#EDE8DE",
        "editorLineNumber.foreground": "#6b7280",
        "editorCursor.foreground": "#7AB8AC",
        "editor.selectionBackground": "#3a3f4f",
        "editor.lineHighlightBackground": "#272d3a",
      },
    });
    monaco.editor.setTheme(theme === "dark" ? DARK_THEME : LIGHT_THEME);

    // Ctrl/Cmd+Enter = Run, Ctrl/Cmd+Shift+Enter = Submit. (Ctrl/Cmd+/ toggles
    // line comment via Monaco's built-in keybinding.)
    editorInstance.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onRunRef.current?.();
    });
    editorInstance.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter,
      () => {
        onSubmitRef.current?.();
      },
    );
  };

  // Apply theme changes.
  useEffect(() => {
    monacoRef.current?.editor.setTheme(theme === "dark" ? DARK_THEME : LIGHT_THEME);
  }, [theme]);

  // Surface linter diagnostics as gutter markers.
  useEffect(() => {
    const monaco = monacoRef.current;
    const model = editorRef.current?.getModel();
    if (!monaco || !model) return;
    const markers: editor.IMarkerData[] = diagnostics.map((d) => ({
      startLineNumber: d.line,
      startColumn: d.column,
      endLineNumber: d.endLine ?? d.line,
      endColumn: d.endColumn ?? d.column + 1,
      message: d.code ? `${d.message} (${d.code})` : d.message,
      severity:
        d.severity === "error"
          ? monaco.MarkerSeverity.Error
          : d.severity === "warning"
            ? monaco.MarkerSeverity.Warning
            : monaco.MarkerSeverity.Info,
    }));
    monaco.editor.setModelMarkers(model, "ruff", markers);
  }, [diagnostics]);

  return (
    <Editor
      language={languageId}
      value={value}
      onChange={(next) => onChange(next ?? "")}
      onMount={handleMount}
      theme={theme === "dark" ? DARK_THEME : LIGHT_THEME}
      loading={
        <div className="flex h-full items-center justify-center text-sm text-muted">
          Loading editor…
        </div>
      }
      options={{
        ariaLabel,
        readOnly,
        fontSize: 14,
        fontFamily: 'ui-monospace, "SF Mono", "Cascadia Code", "Fira Code", monospace',
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        tabSize: 4,
        insertSpaces: true,
        automaticLayout: true,
        padding: { top: 12, bottom: 12 },
        renderLineHighlight: "line",
        smoothScrolling: true,
        scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10 },
      }}
    />
  );
}
