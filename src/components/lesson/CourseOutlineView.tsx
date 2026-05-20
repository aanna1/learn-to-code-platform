"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getCompletedLessonKeys, getLastVisited, type LessonLocation } from "@/lib/progress";
import type { Course, ModuleManifest } from "@/lib/content/types";

interface CourseOutlineViewProps {
  languageId: string;
  course: Course;
  modules: ModuleManifest[];
}

function lessonHref(languageId: string, moduleId: string, lessonId: string): string {
  return `/learn/${languageId}/${moduleId}/${lessonId}`;
}

/**
 * Interactive course outline. The module/lesson tree is static (server-provided),
 * while completion checkmarks and the "continue where you left off" button come
 * from localStorage — read after mount so the server and first client render match.
 */
export function CourseOutlineView({ languageId, course, modules }: CourseOutlineViewProps) {
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  const [lastVisited, setLastVisited] = useState<LessonLocation | null>(null);

  useEffect(() => {
    setCompleted(new Set(getCompletedLessonKeys(languageId)));
    setLastVisited(getLastVisited(languageId) ?? null);
  }, [languageId]);

  const continueTitle = (() => {
    if (!lastVisited) return null;
    const lesson = modules
      .find((m) => m.id === lastVisited.moduleId)
      ?.lessons.find((l) => l.id === lastVisited.lessonId);
    return lesson?.title ?? null;
  })();

  let lessonNumber = 0;

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-muted hover:text-text">
        ← All languages
      </Link>

      <h1 className="mt-4 text-3xl font-bold tracking-tight">{course.displayName}</h1>
      <p className="mt-2 max-w-prose text-muted">{course.tagline}</p>

      {lastVisited && continueTitle ? (
        <Link
          href={lessonHref(languageId, lastVisited.moduleId, lastVisited.lessonId)}
          className="mt-6 inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white shadow-soft transition hover:bg-accent-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
        >
          Continue where you left off: {continueTitle}
        </Link>
      ) : null}

      <div className="mt-10 space-y-10">
        {modules.map((module) => (
          <section key={module.id}>
            <h2 className="text-xl font-semibold tracking-tight">{module.title}</h2>
            {module.description ? (
              <p className="mt-1 text-sm text-muted">{module.description}</p>
            ) : null}

            <ul className="mt-4 divide-y divide-border overflow-hidden rounded-lg border border-border bg-surface">
              {module.lessons.map((lesson) => {
                lessonNumber += 1;
                const isDone = completed.has(`${module.id}/${lesson.id}`);
                return (
                  <li key={lesson.id}>
                    <Link
                      href={lessonHref(languageId, module.id, lesson.id)}
                      className="flex items-center gap-4 px-4 py-3 transition hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent"
                    >
                      <span
                        aria-hidden
                        className={`grid h-6 w-6 shrink-0 place-items-center rounded-full border text-xs ${
                          isDone
                            ? "border-success bg-success text-white"
                            : "border-border text-muted"
                        }`}
                      >
                        {isDone ? "✓" : lessonNumber}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block font-medium">{lesson.title}</span>
                      </span>
                      <span className="shrink-0 rounded-full border border-border px-2.5 py-0.5 text-xs capitalize text-muted">
                        {lesson.type}
                      </span>
                      {isDone ? <span className="sr-only">Completed</span> : null}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </section>
        ))}
      </div>
    </main>
  );
}
