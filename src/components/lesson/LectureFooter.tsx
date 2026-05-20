"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { LessonQuiz } from "@/components/lesson/LessonQuiz";
import { isLessonComplete, setLastVisited, setLessonComplete } from "@/lib/progress";
import type { Quiz } from "@/lib/content/types";

interface LectureFooterProps {
  languageId: string;
  moduleId: string;
  lessonId: string;
  quiz: Quiz | null;
}

/**
 * Client footer for lecture lessons: the end-of-lecture quiz plus the
 * mark-as-complete control, sharing one source of truth for completion so that
 * acing the quiz and clicking the button stay in sync. Also records this lesson
 * as last-visited on mount. Completion is read on the client to avoid a
 * hydration mismatch (the server can't see localStorage).
 */
export function LectureFooter({ languageId, moduleId, lessonId, quiz }: LectureFooterProps) {
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    setLastVisited(languageId, moduleId, lessonId);
    setCompleted(isLessonComplete(languageId, moduleId, lessonId));
  }, [languageId, moduleId, lessonId]);

  const mark = useCallback(
    (value: boolean) => {
      setLessonComplete(languageId, moduleId, lessonId, value);
      setCompleted(value);
    },
    [languageId, moduleId, lessonId],
  );

  return (
    <>
      {quiz ? (
        <LessonQuiz
          languageId={languageId}
          moduleId={moduleId}
          lessonId={lessonId}
          quiz={quiz}
          onPassed={() => mark(true)}
        />
      ) : null}

      <div className="mt-10 flex flex-wrap items-center gap-3 border-t border-border pt-6">
        {completed ? (
          <>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-success/40 bg-success/10 px-3 py-1.5 text-sm font-medium text-success">
              ✓ Completed
            </span>
            <Button variant="ghost" size="sm" onClick={() => mark(false)}>
              Mark as not complete
            </Button>
          </>
        ) : (
          <Button variant="primary" onClick={() => mark(true)}>
            Mark as complete
          </Button>
        )}
      </div>
    </>
  );
}
