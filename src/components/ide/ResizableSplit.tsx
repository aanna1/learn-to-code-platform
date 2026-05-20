"use client";

import { useCallback, useRef, useState, type ReactNode } from "react";

type Orientation = "horizontal" | "vertical";

interface ResizableSplitProps {
  /** "horizontal" = panes side by side; "vertical" = stacked top/bottom. */
  orientation?: Orientation;
  first: ReactNode;
  second: ReactNode;
  /** Initial fraction (0..1) of the first pane. */
  initialRatio?: number;
  minRatio?: number;
  maxRatio?: number;
  className?: string;
}

const KEYBOARD_STEP = 0.025;

export function ResizableSplit({
  orientation = "vertical",
  first,
  second,
  initialRatio = 0.6,
  minRatio = 0.2,
  maxRatio = 0.85,
  className = "",
}: ResizableSplitProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [ratio, setRatio] = useState(initialRatio);
  const isHorizontal = orientation === "horizontal";

  const clamp = useCallback(
    (value: number) => Math.min(maxRatio, Math.max(minRatio, value)),
    [minRatio, maxRatio],
  );

  const updateFromPointer = useCallback(
    (clientX: number, clientY: number) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      const next = isHorizontal
        ? (clientX - rect.left) / rect.width
        : (clientY - rect.top) / rect.height;
      setRatio(clamp(next));
    },
    [isHorizontal, clamp],
  );

  const onPointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    const divider = event.currentTarget;
    divider.setPointerCapture(event.pointerId);
    const onMove = (e: PointerEvent) => updateFromPointer(e.clientX, e.clientY);
    const onUp = (e: PointerEvent) => {
      divider.releasePointerCapture(e.pointerId);
      divider.removeEventListener("pointermove", onMove);
      divider.removeEventListener("pointerup", onUp);
    };
    divider.addEventListener("pointermove", onMove);
    divider.addEventListener("pointerup", onUp);
  };

  const onKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const decrease = isHorizontal ? "ArrowLeft" : "ArrowUp";
    const increase = isHorizontal ? "ArrowRight" : "ArrowDown";
    if (event.key === decrease) {
      event.preventDefault();
      setRatio((r) => clamp(r - KEYBOARD_STEP));
    } else if (event.key === increase) {
      event.preventDefault();
      setRatio((r) => clamp(r + KEYBOARD_STEP));
    }
  };

  return (
    <div
      ref={containerRef}
      className={`flex ${isHorizontal ? "flex-row" : "flex-col"} ${className}`}
    >
      <div className="min-h-0 min-w-0 overflow-hidden" style={{ flexBasis: `${ratio * 100}%` }}>
        {first}
      </div>
      <div
        role="separator"
        tabIndex={0}
        aria-label="Resize panels"
        aria-orientation={isHorizontal ? "vertical" : "horizontal"}
        aria-valuenow={Math.round(ratio * 100)}
        aria-valuemin={Math.round(minRatio * 100)}
        aria-valuemax={Math.round(maxRatio * 100)}
        onPointerDown={onPointerDown}
        onKeyDown={onKeyDown}
        className={`group flex shrink-0 items-center justify-center bg-border transition-colors hover:bg-accent focus-visible:bg-accent focus-visible:outline-none ${
          isHorizontal ? "w-1.5 cursor-col-resize" : "h-1.5 cursor-row-resize"
        }`}
      >
        <span
          aria-hidden="true"
          className={`rounded-full bg-bg/40 group-hover:bg-bg/0 ${
            isHorizontal ? "h-8 w-0.5" : "h-0.5 w-8"
          }`}
        />
      </div>
      <div className="min-h-0 min-w-0 flex-1 overflow-hidden">{second}</div>
    </div>
  );
}
