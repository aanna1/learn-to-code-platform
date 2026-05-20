"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { recordQuizResult } from "@/lib/progress";
import type { Quiz } from "@/lib/content/types";

interface LessonQuizProps {
  languageId: string;
  moduleId: string;
  lessonId: string;
  quiz: Quiz;
  /** Fired once when every question is answered correctly. */
  onPassed?: () => void;
}

/**
 * End-of-lecture multiple-choice quiz built from quiz.json. Selecting an option
 * gives instant feedback (correct/incorrect + that option's explanation). Once
 * every question is answered the attempt is recorded via the progress module; a
 * perfect score reports completion through onPassed. Users can retry freely.
 */
export function LessonQuiz({ languageId, moduleId, lessonId, quiz, onPassed }: LessonQuizProps) {
  const questions = quiz.questions;
  const total = questions.length;

  const [selected, setSelected] = useState<(number | null)[]>(() => questions.map(() => null));
  const recordedRef = useRef(false);
  const passedRef = useRef(false);

  const answeredCount = selected.filter((s) => s !== null).length;
  const allAnswered = answeredCount === total && total > 0;
  const score = selected.reduce<number>((acc, sel, i) => {
    const option = sel === null ? undefined : questions[i]?.options[sel];
    return acc + (option?.correct ? 1 : 0);
  }, 0);

  useEffect(() => {
    if (!allAnswered) return;
    if (!recordedRef.current) {
      recordQuizResult(languageId, moduleId, lessonId, score, total);
      recordedRef.current = true;
    }
    if (score === total && !passedRef.current) {
      passedRef.current = true;
      onPassed?.();
    }
  }, [allAnswered, score, total, languageId, moduleId, lessonId, onPassed]);

  const handleSelect = useCallback((questionIndex: number, optionIndex: number) => {
    setSelected((prev) => prev.map((s, i) => (i === questionIndex ? optionIndex : s)));
  }, []);

  const handleRetry = useCallback(() => {
    recordedRef.current = false;
    setSelected(questions.map(() => null));
  }, [questions]);

  if (total === 0) return null;

  return (
    <section aria-labelledby="quiz-heading" className="mt-10 border-t border-border pt-8">
      <h2 id="quiz-heading" className="text-xl font-semibold tracking-tight">
        Quick check
      </h2>
      <p className="mt-1 text-sm text-muted">
        Answer all {total} to see how it went. You can retry as many times as you like.
      </p>

      <ol className="mt-6 space-y-7">
        {questions.map((question, qi) => {
          const chosen = selected[qi] ?? null;
          return (
            <li key={qi}>
              <fieldset>
                <legend className="font-medium">{question.question}</legend>
                <div className="mt-3 space-y-2">
                  {question.options.map((option, oi) => {
                    const isChosen = chosen === oi;
                    const state = !isChosen
                      ? "border-border bg-surface hover:border-accent"
                      : option.correct
                        ? "border-success bg-success/10"
                        : "border-danger bg-danger/10";
                    return (
                      <label
                        key={oi}
                        className={`flex cursor-pointer items-start gap-3 rounded-md border p-3 text-sm transition ${state}`}
                      >
                        <input
                          type="radio"
                          name={`q-${qi}`}
                          checked={isChosen}
                          onChange={() => handleSelect(qi, oi)}
                          className="sr-only"
                        />
                        <span
                          aria-hidden
                          className={`mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded-full border ${
                            isChosen
                              ? option.correct
                                ? "border-success bg-success text-white"
                                : "border-danger bg-danger text-white"
                              : "border-muted"
                          }`}
                        >
                          {isChosen ? (option.correct ? "✓" : "✕") : null}
                        </span>
                        <span>
                          <span className="block">{option.text}</span>
                          {isChosen ? (
                            <span className="mt-1 block text-muted">{option.explanation}</span>
                          ) : null}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </fieldset>
            </li>
          );
        })}
      </ol>

      {allAnswered ? (
        <div
          className={`mt-6 rounded-md border p-4 text-sm ${
            score === total ? "border-success/40 bg-success/10" : "border-highlight/40 bg-highlight/10"
          }`}
        >
          <p className="font-semibold">
            You scored {score} of {total}.
          </p>
          <p className="mt-1 text-muted">
            {score === total
              ? "Perfect — this lesson is marked complete."
              : "Review the explanations above, then give it another go."}
          </p>
          <div className="mt-3">
            <Button variant="secondary" size="sm" onClick={handleRetry}>
              Try again
            </Button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
