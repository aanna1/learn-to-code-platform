"use client";

import { Modal } from "@/components/ui/Modal";

function modKey(): string {
  if (typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.platform)) {
    return "⌘";
  }
  return "Ctrl";
}

export function ShortcutsOverlay({ open, onClose }: { open: boolean; onClose: () => void }) {
  const mod = modKey();
  const shortcuts: [string, string][] = [
    [`${mod} + Enter`, "Run your code"],
    [`${mod} + Shift + Enter`, "Submit (run the checks)"],
    [`${mod} + /`, "Toggle line comment"],
    ["Esc", "Close this and other dialogs"],
  ];

  return (
    <Modal open={open} onClose={onClose} title="Keyboard shortcuts" widthClass="max-w-md">
      <dl className="divide-y divide-border">
        {shortcuts.map(([keys, description]) => (
          <div key={keys} className="flex items-center justify-between gap-4 py-2.5">
            <dt className="text-text">{description}</dt>
            <dd>
              <kbd className="rounded border border-border bg-surface-raised px-2 py-1 font-mono text-xs text-muted">
                {keys}
              </kbd>
            </dd>
          </div>
        ))}
      </dl>
    </Modal>
  );
}
