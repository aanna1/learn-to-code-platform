"use client";

import { useCallback, useEffect, useState } from "react";
import { Ide, type IdeExercise } from "@/components/ide/Ide";
import { isLessonComplete, setLastVisited, setLessonComplete } from "@/lib/progress";

interface ExercisePaneProps {
  languageId: string;
  moduleId: string;
  lessonId: string;
  exercise: IdeExercise;
}

/**
 * Client wrapper that mounts the full IDE for an exercise lesson. It records the
 * lesson as last-visited, marks it complete when all hidden tests pass, and hides
 * the IDE below the md breakpoint (the brief: coding needs a wider screen) with a
 * friendly message in its place. The instructions/prompt are rendered separately
 * by the page and remain readable on mobile.
 */
export function ExercisePane({ languageId, moduleId, lessonId, exercise }: ExercisePaneProps) {
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    setLastVisited(languageId, moduleId, lessonId);
    setCompleted(isLessonComplete(languageId, moduleId, lessonId));
  }, [languageId, moduleId, lessonId]);

  const handleAllTestsPassed = useCallback(() => {
    setLessonComplete(languageId, moduleId, lessonId, true);
    setCompleted(true);
  }, [languageId, moduleId, lessonId]);

  return (
    <div className="flex h-full min-h-0 flex-col">
      {completed ? (
        <div className="mb-2 shrink-0 rounded-md border border-success/40 bg-success/10 px-3 py-1.5 text-sm font-medium text-success">
          ✓ You&apos;ve completed this exercise. Feel free to keep experimenting.
        </div>
      ) : null}

      {/* Full IDE on wider screens */}
      <div className="hidden min-h-0 flex-1 md:block">
        <Ide
          languageId={languageId}
          exercise={exercise}
          autosave={{ moduleId, lessonId }}
          onAllTestsPassed={handleAllTestsPassed}
        />
      </div>

      {/* Reading-only fallback on small screens */}
      <div className="rounded-lg border border-border bg-surface p-6 text-sm text-muted md:hidden">
        <p className="font-medium text-text">This exercise needs a wider screen.</p>
        <p className="mt-2">
          Open this lesson on a laptop or desktop to write and run the code. The instructions above
          are fully readable here on mobile.
        </p>
      </div>
    </div>
  );
}
